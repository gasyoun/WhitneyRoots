"""
fix_ppp_gloss_bleed.py
======================
Fix the PPP column-bleed bug in src/app_data.json.

ROOT CAUSE
----------
The source file Whitney_roots_class-PP.txt is fixed-width with five columns:

    №   √root            Class(es)        PPP-form(s)                    Meaning

For a handful of roots the source PPP column *also* carries an English gloss
(and, for one root, mirrored HTML/HTTrack junk) sitting between the actual
participle form and the meaning column, e.g.:

    182. √guṇṭh   —   gunthita veil, conceal, hide   cover
    184. √guph    I   gumphita string together, wreathe, wind. Copyright © 2005 ... twine

The extraction that built app_data.json split the PPP cell on commas, so the
trailing gloss became extra `ppp` array elements (gunthita veil / conceal /
hide), or — when the cell was polluted with HTTrack junk (guph) — the form was
dropped entirely (ppp = []). This is NOT a column-position problem: the gloss
lives inside the PPP column in the source, so it cannot be separated by a
fixed-width parse. It requires the curated, per-record correction below.

The canonical meaning already lives in each record's `meaning` field (from
Whitney), so the dropped gloss text is not lost information.

This script is idempotent: re-running it after a successful pass is a no-op
(the old substrings will no longer be found and each correction is skipped).
It edits the file as text with surgical string replacement so the original
CRLF line endings, 2-space indent, and absence of a BOM/trailing newline are
preserved exactly — a json.dump round-trip would rewrite every line.
"""

import sys, json, pathlib

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'

NL = '\r\n'
I8 = '        '   # 8-space indent for ppp array elements

# (label, old_block, new_block)
# old_block targets only the array-element content (unique in the file), so the
# `"ppp": [ ... ]` wrapper and its indentation are left untouched.
CORRECTIONS = [
    ('19  √av',    f'"uta favour",{NL}{I8}"like",{NL}{I8}"delight in"',        '"uta"'),
    ('100 √kuṣ',   f'"kusita pinch",{NL}{I8}"tear",{NL}{I8}"gnaw"',            '"kusita"'),
    ('182 √guṇṭh', f'"gunthita veil",{NL}{I8}"conceal",{NL}{I8}"hide"',        '"gunthita"'),
    ('347 √das',   f'"dasta suffer want",{NL}{I8}"languish"',                  '"dasta"'),
    ('831 √san',   f'"sata win",{NL}{I8}"conquer",{NL}{I8}"acquire"',          '"sata"'),
]

# guph (184): the form "gumphita" was lost (ppp == []) to HTTrack/Copyright junk.
# Recover it by anchoring on the unique guph record, then replacing its empty
# ppp array. The empty `"ppp": []` is NOT unique, so anchor on the root first.
GUPH_ANCHOR = '"root": "guph",'
GUPH_OLD = '"ppp": []'
GUPH_NEW = f'"ppp": [{NL}{I8}"gumphita"{NL}      ]'


def main():
    # Read preserving CRLF exactly (newline='' => no translation).
    with open(APP_DATA, 'r', encoding='utf-8', newline='') as f:
        text = f.read()

    if text.startswith('﻿'):
        raise SystemExit('ERROR: file unexpectedly starts with a BOM')

    changed = 0

    for label, old, new in CORRECTIONS:
        wrapped_old = f'"ppp": [{NL}{I8}{old}{NL}      ]'
        wrapped_new = f'"ppp": [{NL}{I8}{new}{NL}      ]'
        n = text.count(wrapped_old)
        if n == 0:
            print(f'  skip  {label}: already corrected (pattern not found)')
            continue
        if n > 1:
            raise SystemExit(f'ERROR: pattern for {label} matched {n} times (expected 1)')
        text = text.replace(wrapped_old, wrapped_new)
        print(f'  fix   {label}: {old.splitlines()[0]} ...  ->  {new}')
        changed += 1

    # guph special case
    a = text.find(GUPH_ANCHOR)
    if a == -1:
        raise SystemExit('ERROR: could not locate the guph record')
    p = text.find(GUPH_OLD, a)
    nextrec = text.find('"id":', a + 1)
    if p != -1 and (nextrec == -1 or p < nextrec):
        text = text[:p] + GUPH_NEW + text[p + len(GUPH_OLD):]
        print('  fix   184 √guph: ppp [] (form lost to HTML junk)  ->  ["gumphita"]')
        changed += 1
    else:
        print('  skip  184 √guph: already corrected (empty ppp not found in record)')

    if changed == 0:
        print('Nothing to change. File already correct.')
        return

    # Write back preserving CRLF, no BOM, no added trailing newline.
    with open(APP_DATA, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

    # ── Verify ────────────────────────────────────────────────────────────
    with open(APP_DATA, 'rb') as f:
        raw = f.read()
    assert raw[:3].hex() != 'efbbbf', 'BOM was introduced!'
    data = json.loads(raw.decode('utf-8'))  # raises if invalid JSON
    expect = {'19': ['uta'], '100': ['kusita'], '182': ['gunthita'],
              '347': ['dasta'], '831': ['sata'], '184': ['gumphita']}
    by_id = {e['id']: e for e in data['lexicon']}
    for rid, want in expect.items():
        got = by_id[rid].get('ppp')
        assert got == want, f'id {rid}: expected {want}, got {got}'
    print(f'\n{changed} record(s) fixed. JSON valid, BOM-free, {len(data["lexicon"])} entries.')


if __name__ == '__main__':
    main()
