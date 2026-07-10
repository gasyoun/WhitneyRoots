# -*- coding: utf-8 -*-
"""
Canonical MW <-> Whitney hub <-> DCS three-way verbal-root triangulation join.

SHARED_CODE.md §16 (was duplicated: MWS/root_crosswalk/root_crosswalk.py built this
join by re-scanning mw.txt itself; this module is the one place it happens now).
Reads the canonical MW root inventory (csl-orig/v02/mw/mw_roots.tsv, SHARED_CODE.md
§11) instead of re-parsing mw.txt, joins it against the Whitney hub (935 roots,
src/app_data.json) and the DCS corpus fold (src/dcs_freq.json) on the
homonym-normalised bare root string.

Public API: triangulate() -> (rows, summary, mw_unmatched)
  rows          list of dict: whitney_id, root, in_MW, mw_L, mw_classes, dcs_status, dcs_freq
  summary       dict: n_hub, n_mw_genuine, n_mw_anchored, n_westergaard,
                       in_mw, in_dcs, in_both, n_unmatched
  mw_unmatched  list of (mw_root_iast_bare, mw_L, whitney_page) — MW anchors with no hub match

Caveat carried from the original join: matching is on the homonym-collapsed bare
root string, so "in MW" does not assert the MW and hub records mean the same
homonym — homonym-level alignment is a separate, more precise join
(dict_align.py -> crosswalk/root_alignment.csv, SLP1 + gaṇa-disambiguated).
"""
import os
import re
import json

HERE = os.path.dirname(os.path.abspath(__file__))          # WhitneyRoots/scripts
WR = os.path.dirname(HERE)                                 # WhitneyRoots/
GH = os.path.dirname(WR)                                   # GitHub/
MW_ROOTS_TSV = os.path.join(GH, 'csl-orig', 'v02', 'mw', 'mw_roots.tsv')
HUB_PATH = os.path.join(WR, 'src', 'app_data.json')
DCS_FREQ_PATH = os.path.join(WR, 'src', 'dcs_freq.json')

_S2I = {'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ', 'E': 'ai', 'O': 'au',
        'M': 'ṃ', 'H': 'ḥ', 'K': 'kh', 'G': 'gh', 'N': 'ṅ', 'C': 'ch', 'J': 'jh', 'Y': 'ñ',
        'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ', 'T': 'th', 'D': 'dh', 'P': 'ph',
        'B': 'bh', 'S': 'ś', 'z': 'ṣ', 'L': 'ḻ'}


def s2i(s):
    return ''.join(_S2I.get(c, c) for c in s)


def bare(r):
    """Strip homonym markers: leading 'N ' (hub) or trailing digit (MW)."""
    r = re.sub(r'^\d+\s+', '', r.strip())
    r = re.sub(r'\d+$', '', r)
    return r


def load_mw_roots(tsv_path=MW_ROOTS_TSV):
    """Read the canonical MW verbal-root inventory. Returns list of dict rows."""
    rows = []
    with open(tsv_path, encoding='utf-8') as f:
        header = f.readline().rstrip('\n').split('\t')
        for line in f:
            vals = line.rstrip('\n').split('\t')
            rows.append(dict(zip(header, vals)))
    return rows


def load_hub(hub_path=HUB_PATH):
    return json.load(open(hub_path, encoding='utf-8'))['lexicon']


def load_dcs(dcs_path=DCS_FREQ_PATH):
    return json.load(open(dcs_path, encoding='utf-8'))['entries']


def _mw_anchor_bares(mw_rows):
    """whitney_anchor column ('root,page;root,page;...' in SLP1) -> {bare_iast: (mw_L, page, classes)}."""
    mw_anchor_bare = {}
    for r in mw_rows:
        anchor = r.get('whitney_anchor', '')
        if not anchor:
            continue
        for part in anchor.split(';'):
            if ',' not in part:
                continue
            root, page = part.rsplit(',', 1)
            b = bare(s2i(root))
            mw_anchor_bare.setdefault(b, (r['mw_L'], page, r.get('classes', '')))
    return mw_anchor_bare


def triangulate(mw_roots_tsv=MW_ROOTS_TSV, hub_path=HUB_PATH, dcs_path=DCS_FREQ_PATH):
    mw_rows = load_mw_roots(mw_roots_tsv)
    hub = load_hub(hub_path)
    dcs = load_dcs(dcs_path)

    bare2ids = {}
    hub_by_id = {}
    for r in hub:
        b = bare(r['root'])
        hub_by_id[r['id']] = {'root': r['root'], 'bare': b}
        bare2ids.setdefault(b, []).append(r['id'])

    mw_anchor_bare = _mw_anchor_bares(mw_rows)

    mw_unmatched = []
    for b, (mw_L, page, _classes) in mw_anchor_bare.items():
        if b not in bare2ids:
            mw_unmatched.append((b, mw_L, page))

    rows = []
    in_mw = in_dcs = in_both = 0
    for r in hub:
        hid = r['id']
        b = hub_by_id[hid]['bare']
        mw = mw_anchor_bare.get(b)
        d = dcs.get(hid, {})
        dstat = d.get('dcs_status', '')
        dfreq = d.get('total', '')
        dflag = (dstat == 'matched')
        if mw:
            in_mw += 1
        if dflag:
            in_dcs += 1
        if mw and dflag:
            in_both += 1
        rows.append({
            'whitney_id': hid, 'root': r['root'],
            'in_MW': 'yes' if mw else 'no',
            'mw_L': mw[0] if mw else '', 'mw_classes': mw[2] if mw else '',
            'dcs_status': dstat, 'dcs_freq': dfreq,
        })

    n_genuine = sum(1 for r in mw_rows if r.get('verb_type') == 'genuineroot')
    n_anchored = sum(1 for r in mw_rows if r.get('whitney_anchor'))
    n_westergaard = sum(1 for r in mw_rows if r.get('westergaard'))
    summary = {
        'n_hub': len(hub), 'n_mw_total': len(mw_rows), 'n_mw_genuine': n_genuine,
        'n_mw_anchored': n_anchored, 'n_westergaard': n_westergaard,
        'in_mw': in_mw, 'in_dcs': in_dcs, 'in_both': in_both,
        'n_unmatched': len(mw_unmatched),
    }
    return rows, summary, mw_unmatched


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    rows, summary, unmatched = triangulate()
    print(f"MW verbal-root records {summary['n_mw_total']} "
          f"(genuineroot {summary['n_mw_genuine']}) | whitney-anchored {summary['n_mw_anchored']} "
          f"| westergaard {summary['n_westergaard']}")
    print(f"hub {summary['n_hub']}: in_MW {summary['in_mw']}, in_DCS {summary['in_dcs']}, "
          f"in_both {summary['in_both']}")
    print(f"MW anchors unmatched to hub: {summary['n_unmatched']}")
