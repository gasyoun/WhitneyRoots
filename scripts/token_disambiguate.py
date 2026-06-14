# -*- coding: utf-8 -*-
"""Phase 1b (token-level): split a shared DCS lemma's verb tokens across Whitney homonyms by using
DCS's OWN homonym separation — its multiple verb `lemma_id`s, each with its own gaṇa — rather than
fragile stem-matching.

Background: extract_dcs joined Whitney roots to DCS by lemma STRING, so homonyms that DCS actually
keeps apart as distinct lemma_ids (e.g. as = lemma_id 156122 'be' cl.2 vs 156123 'throw' cl.4) got
collapsed and all shared the summed lemma freq. Here we recover the split: for each DCS verb lemma_id
we map it to the single Whitney homonym whose class matches its gaṇa, and attribute that lemma_id's
token count there.

Reliability guard (conservative — the project never asserts a corpus split it can't defend):
  - DCS must keep ≥2 verb lemma_ids for the lemma (it separated the homonyms), AND
  - each lemma_id maps to exactly ONE Whitney homonym by gaṇa, AND
  - the resulting attribution lands on ≥2 distinct homonyms (it really separated them, didn't collapse
    everything onto one — which catches cases like aś where DCS split by pada, not by Whitney's sense), AND
  - coverage ≥ COV_MIN.
Groups DCS lumps under one lemma_id (38 of 72) — or whose lemma_ids don't cleanly map — are left with
the shared lemma-level dcs_freq UNCHANGED. Writes crosswalk/token_attribution.json and, for reliable
groups only, corpus.dcs_freq_token on the spine (never touches class or dcs_freq). UTF-8, no BOM.
"""
import sys, os, re, json, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
DCS   = os.path.join(BASE, os.pardir, 'VisualDCS', 'src', 'DCS-data-2026', 'dcs_full.sqlite')
OUT   = os.path.join(BASE, 'crosswalk', 'token_attribution.json')
R2A = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10}
COV_MIN = 0.55

def homonym_arabic(r):
    return {R2A[c] for c in (r.get('class') or []) if c in R2A}

def verb_lemma_ids(con, lemma):
    """[(lemma_id, {arabic gaṇa}, verb_token_count)] for a lemma string, verb rows only."""
    out = []
    for lid, g in con.execute("SELECT lemma_id, grammar FROM lemma WHERE lemma=?", (lemma,)):
        n = con.execute("SELECT COUNT(*) FROM token WHERE lemma_id=? AND upos='VERB'", (lid,)).fetchone()[0]
        if n:
            cls = {int(x) for x in re.findall(r'\b(\d{1,2})\b', g or '') if 1 <= int(x) <= 10}
            out.append((lid, cls, n))
    return out

def main():
    spine = json.load(open(SPINE, encoding='utf-8'))
    by_lemma = {}
    for r in spine:
        c = r.get('corpus') or {}
        if c.get('dcs_status') == 'homonym_shared' and c.get('dcs_lemma'):
            by_lemma.setdefault(c['dcs_lemma'], []).append(r)
    groups = {lem: rs for lem, rs in by_lemma.items() if len(rs) >= 2}

    con = sqlite3.connect(DCS)
    report, fold = [], {}
    tot_r = attr_r = 0
    for lem, group in sorted(groups.items()):
        lids = verb_lemma_ids(con, lem)
        counts = {r['whitney_no']: 0 for r in group}
        total = unattr = 0
        for lid, acls, n in lids:
            total += n
            matches = [r['whitney_no'] for r in group if homonym_arabic(r) & acls]
            if len(matches) == 1:
                counts[matches[0]] += n
            else:
                unattr += n                      # lemma_id maps to 0 or >1 homonyms → ambiguous
        attr = total - unattr
        cov = attr / total if total else 0.0
        n_dist = sum(1 for v in counts.values() if v > 0)
        reliable = (len(lids) >= 2) and (n_dist >= 2) and (cov >= COV_MIN)
        if reliable:
            for no, c in counts.items():
                fold[no] = c
            tot_r += total; attr_r += attr
        reason = ('ok' if reliable else
                  ('DCS lumps (1 verb lemma_id)' if len(lids) < 2 else
                   'collapses onto one homonym' if n_dist < 2 else 'low coverage'))
        report.append({'lemma': lem, 'reliable': reliable, 'dcs_lemma_ids': len(lids),
                       'total': total, 'coverage': round(cov, 3), 'reason': reason,
                       'homonyms': [{'whitney_no': r['whitney_no'], 'gloss': r.get('gloss_short', ''),
                                     'class': r.get('class', []), 'attributed': counts[r['whitney_no']]}
                                    for r in sorted(group, key=lambda x: x['whitney_no'])],
                       'unattributed': unattr})
    con.close()

    for r in spine:                              # idempotent: clear stale token fields
        if r.get('corpus'):
            r['corpus'].pop('dcs_freq_token', None)
            r['corpus'].pop('dcs_token_method', None)
    for r in spine:
        no = r.get('whitney_no')
        if no in fold and r.get('corpus'):
            r['corpus']['dcs_freq_token'] = fold[no]
            r['corpus']['dcs_token_method'] = 'DCS lemma_id → homonym by gaṇa (guard-passed; see token_attribution.json)'
    json.dump(spine, open(SPINE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    report.sort(key=lambda x: (-x['reliable'], -x['total']))
    n_rel = sum(1 for x in report if x['reliable'])
    json.dump({'note': "Per-homonym DCS token freq, recovered from DCS's own verb lemma_id separation "
                       "(each lemma_id mapped to the Whitney homonym whose gaṇa matches). Folded to "
                       "spine corpus.dcs_freq_token only for `reliable` groups (DCS keeps ≥2 lemma_ids, "
                       "they map 1:1 to ≥2 distinct homonyms, coverage ≥ %.2f). Groups DCS lumps under "
                       "one lemma_id stay shared/unsplit. Never replaces lemma-level dcs_freq." % COV_MIN,
               'groups': len(report), 'reliable': n_rel, 'unreliable': len(report) - n_rel,
               'items': report}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(OUT, 'rb') as fb:
        assert fb.read(3).hex() != 'efbbbf'

    print(f'groups={len(report)}  reliable={n_rel}  unreliable={len(report)-n_rel}  '
          f'(folded {len(fold)} homonyms across {n_rel} lemmas)')
    print('\nRELIABLE splits (DCS-lemma_id-separated, folded):')
    for it in [x for x in report if x['reliable']]:
        hs = ', '.join(f"#{h['whitney_no']} {h['gloss'][:11]!r}={h['attributed']}" for h in it['homonyms'])
        print(f"  {it['lemma']:<6} tot={it['total']:<6} cov={it['coverage']:<5} | {hs}")
    print(f"\n{len(report)-n_rel} unreliable groups left shared (38 DCS-lumped + ambiguous mappings).")

if __name__ == '__main__':
    main()
