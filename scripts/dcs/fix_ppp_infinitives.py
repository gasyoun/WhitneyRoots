"""
fix_ppp_infinitives.py
======================
Second-pass correction on top of fix_ppp_apparatus_bleed.py.

The source "PPP column" in Whitney_roots_class-PP.txt reproduces Whitney's whole
"Verbal Nouns" section, which contains the PPP AND datival infinitives (-e/-aye/
-vane). Those infinitives bled into the `ppp` arrays. They are real Sanskrit
forms but NOT past-passive-participles, so per the maintainer's decision (f) they
move OUT of `ppp` into a new additive `infinitives` field; the true PPP stays.

This also corrects id 649 √riṣ: the apparatus pass dropped "rises" as a presumed
OCR duplicate — it is NOT. warnemyr (following Whitney) records
"PPP : riṣṭá V.+ ; riṣé riṣés RV", so `rise`=riṣé and `rises`=riṣés are both
datival infinitives. Both are restored into `infinitives`.

Surgical, CRLF/BOM-preserving, idempotent — same pattern as the apparatus/gloss
scripts. See docs/PPP_APPARATUS_BLEED_WORKLIST.md §2b/§4(e)/§4(f).
"""
import sys, json, pathlib

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'

NL = '\r\n'

# id : (ppp currently on file, final ppp, infinitives to move out)
RECORDS = {
    '227': (['citta', 'cite', 'citaye'],        ['citta'],              ['cite', 'citaye']),
    '333': (['tvisita', 'tvise'],               ['tvisita'],            ['tvise']),
    '409': (['dhurta', 'dhruta', 'dhurvane'],   ['dhurta', 'dhruta'],   ['dhurvane']),
    '472': (['prkta', 'prgna', 'prce'],         ['prkta', 'prgna'],     ['prce']),
    '560': (['midha', 'mihe'],                  ['midha'],              ['mihe']),
    '568': (['mugdha', 'mudha', 'muhe'],        ['mugdha', 'mudha'],    ['muhe']),
    '649': (['rista', 'rise'],                  ['rista'],              ['rise', 'rises']),  # restore "rises"
    '793': (['subhita', 'sumbhita', 'subhe'],   ['subhita', 'sumbhita'],['subhe']),
    '914': (['hita', 'hye'],                    ['hita'],               ['hye']),
}


def arr_block(forms, key):
    inner = (',' + NL).join('        ' + json.dumps(f, ensure_ascii=False) for f in forms)
    return f'"{key}": [{NL}{inner}{NL}      ]'


def main():
    with open(APP_DATA, 'r', encoding='utf-8', newline='') as f:
        text = f.read()
    if text.startswith('﻿'):
        raise SystemExit('ERROR: file starts with a BOM')

    changed = 0
    for rid, (old_ppp, new_ppp, inf) in RECORDS.items():
        anchor = f'"id": "{rid}"'
        ai = text.find(anchor)
        if ai == -1:
            raise SystemExit(f'ERROR: record id {rid} not found')
        nxt = text.find('"id":', ai + len(anchor))
        end = nxt if nxt != -1 else len(text)
        region = text[ai:end]

        old_block = arr_block(old_ppp, 'ppp')
        new_block = arr_block(new_ppp, 'ppp') + ',' + NL + '      ' + arr_block(inf, 'infinitives')

        if old_block not in region:
            print(f'  skip  {rid}: already corrected (ppp pattern not found)')
            continue
        if region.count(old_block) != 1:
            raise SystemExit(f'ERROR: id {rid} ppp block matched {region.count(old_block)}x in record')
        pos = ai + region.find(old_block)
        text = text[:pos] + new_block + text[pos + len(old_block):]
        print(f'  fix   {rid}: ppp {old_ppp} -> {new_ppp} ; infinitives {inf}')
        changed += 1

    if changed:
        with open(APP_DATA, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    else:
        print('Nothing to change. Already correct.')

    # ── verify ───────────────────────────────────────────────────────────
    with open(APP_DATA, 'rb') as f:
        raw = f.read()
    assert raw[:3].hex() != 'efbbbf', 'BOM introduced!'
    data = json.loads(raw.decode('utf-8'))
    assert len(data['lexicon']) == 935, f"entry count {len(data['lexicon'])} != 935"
    by = {e['id']: e for e in data['lexicon']}
    for rid, (_old, new_ppp, inf) in RECORDS.items():
        e = by[rid]
        assert e.get('ppp') == new_ppp, f"id {rid} ppp = {e.get('ppp')}, expected {new_ppp}"
        assert e.get('infinitives') == inf, f"id {rid} infinitives = {e.get('infinitives')}, expected {inf}"
    # no datival-infinitive ending left anywhere in any ppp
    bad = []
    for e in data['lexicon']:
        for p in (e.get('ppp') or []):
            tok = p.split(' ')[0]
            if tok.endswith(('aye', 'vane')) or (tok.endswith('e') and len(tok) > 2):
                bad.append((e['id'], p))
    assert not bad, f'infinitive-ending forms still in ppp: {bad}'
    print(f'\n{changed} record(s) corrected. JSON valid, BOM-free, {len(data["lexicon"])} entries; '
          f'no infinitive endings remain in any ppp.')


if __name__ == '__main__':
    main()
