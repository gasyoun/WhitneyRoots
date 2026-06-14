"""
fix_ppp_apparatus_bleed.py
==========================
Fix the PPP *apparatus*-bleed bug in src/app_data.json.

ROOT CAUSE
----------
Each lexicon record carries a `ppp` array — the past-passive-participle form(s)
Whitney lists for that root, extracted from the fixed-width PPP column in
Whitney_roots_class-PP.txt. That column does NOT contain only clean stems:
Whitney interleaves his scholarly *apparatus* directly into the cell, and it bled
into the arrays verbatim when the column was split on commas. The contaminants:

  * period / text-of-attestation markers — RV1 RV2 E1 C1 S1 B1 K R AA, and bare
    trailing period-figures (`danta 1`, `bhugna 1`). Provenance, not stem.
  * uncertainty marker `?`  (`ajita ?`, `snuta ?`) — Whitney's doubt.
  * alternate-form joiners — `&` (`turta & turna`) and, where source+validation
    confirm a genuine variant pair, a bare space (`vrdha brdha`). Each real
    alternate must be its OWN array element.
  * cross-reference notes — `=`, `= seq. abhi`.
  * usage note `adj`.
  * an OCR doubling — id 649 `rise rises` (`rises` is a spurious dup of `rise`).

This is DISTINCT from the already-fixed *gloss* bleed (English meaning words),
handled for 6 records by scripts/dcs/fix_ppp_gloss_bleed.py (ids 19, 100, 182,
184, 347, 831). Those 6 are NOT touched here.

EDITORIAL POLICY (see docs/PPP_APPARATUS_BLEED_WORKLIST.md §4, resolved 2026-06-14)
----------------------------------------------------------------------------------
Decision: PRESERVE the stripped apparatus as additive, consumer-safe sidecar
fields rather than discard it. For each affected record we strip the apparatus
OUT of the `ppp` string (so the form is clean for detail.js `fold()` matching
and analytics.js length-counting) and capture it in new fields:

  * "ppp_attestation": { form: [markers] }   — period/source markers + period digits
  * "ppp_uncertain":   [ forms ]             — forms Whitney flagged with `?`
  * "ppp_note":        { form: "note" }       — `=`/`= seq.`/`adj` editorial notes

These fields are additive: current consumers (detail.js, analytics.js) ignore
unknown keys, so nothing regresses. id 74 `ardita =` keeps a DANGLING-`=` note
flagging that the cross-ref target was truncated at the column boundary and needs
a human to recover it from Whitney's print.

CANONICAL FORMS ARE SOURCE-LITERAL: the source PPP column is ASCII without
macrons/dots (`ksana`, `vita`, `danta`). We do NOT "upgrade" to accented
warnemyr/vidyut spellings — that is a separate, larger decision, out of scope.

EDIT STRATEGY
-------------
Mirror fix_ppp_gloss_bleed.py: surgical TEXT replacement (NOT json.dump — a
round-trip would rewrite every line and corrupt CRLF/indent/no-BOM/no-trailing
-newline). For each record we anchor on its UNIQUE `"id"` first, then replace the
`"ppp": [ ... ]` block within that record's slice — because several records share
identical ppp text (371/372, 469/470/471, 708/709, 797/798/799), a global
count==1 would be wrong for them. The clean ppp block plus any additive metadata
fields are emitted in one replacement, injected before the trailing comma so the
following `"grammar_ref"` field is untouched.

Idempotent: the replacement is keyed on the DIRTY old ppp block; after a
successful pass that block is gone, so a second run finds nothing and is a no-op.
An audit record (every before/after + every stripped marker) is written to
docs/ppp_apparatus_bleed_audit.json so provenance stays recoverable independent
of the data fields.
"""

import sys, json, pathlib

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
AUDIT = ROOT / 'docs' / 'ppp_apparatus_bleed_audit.json'

NL = '\r\n'
I6 = '      '          # field / closing-bracket indent inside a record
I8 = '        '        # ppp / nested-object-key indent
I10 = '          '     # marker-array element indent

# ── The 39 corrections ────────────────────────────────────────────────────────
# old : the EXACT current ppp array (apparatus-bleed text), as it sits in the file
# new : clean ppp (apparatus stripped, alternates split, OCR dup dropped)
# att : ppp_attestation  {form: [markers]}   (period/source markers + period digits)
# unc : ppp_uncertain    [forms]             (Whitney's `?`)
# note: ppp_note         {form: "note"}      (`=` / `= seq.` / `adj`)
CORRECTIONS = [
    dict(rid='6',   label='6   √aj',     old=['ajita ?'],                       new=['ajita'],                       unc=['ajita']),
    dict(rid='74',  label='74  √ṛd',     old=['ardita ='],                      new=['ardita'],                      note={'ardita': '= (cross-ref target unrecovered)'}),
    dict(rid='99',  label='99  √kup',    old=['kupita RV1'],                    new=['kupita'],                      att={'kupita': ['RV1']}),
    dict(rid='140', label='140 √kṣā',    old=['ksana ?'],                       new=['ksana'],                       unc=['ksana']),
    dict(rid='168', label='168 √gadh',   old=['gadhita RV2'],                   new=['gadhita'],                     att={'gadhita': ['RV2']}),
    dict(rid='227', label='227 √cit',    old=['citta', 'cite ?', 'citaye'],     new=['citta', 'cite', 'citaye'],     unc=['cite']),
    dict(rid='306', label='306 √tim',    old=['timita R'],                      new=['timita'],                      att={'timita': ['R']}),
    dict(rid='322', label='322 √tṛṣ',    old=['trsita', 'trsta ? adj'],         new=['trsita', 'trsta'],             unc=['trsta'], note={'trsta': 'adj (adjectival usage)'}),
    dict(rid='326', label='326 √tras',   old=['trasta', 'trasas K'],            new=['trasta', 'trasas'],            att={'trasas': ['K']}),
    dict(rid='332', label='332 √tvar',   old=['tvarita', 'turta & turna'],      new=['tvarita', 'turta', 'turna']),
    dict(rid='343', label='343 √dam',    old=['danta 1'],                       new=['danta'],                       att={'danta': ['1']}),
    dict(rid='365', label='365 √du',     old=['duna', 'duta AA. ? C1'],         new=['duna', 'duta'],                att={'duta': ['AA', 'C1']}, unc=['duta']),
    dict(rid='371', label='371 √1 dṛ',   old=['dirna', 'drta R'],               new=['dirna', 'drta'],               att={'drta': ['R']}),
    dict(rid='372', label='372 √2 dṛ',   old=['dirna', 'drta R'],               new=['dirna', 'drta'],               att={'drta': ['R']}),
    dict(rid='452', label='452 √pi',     old=['pina 1 & pipivas'],              new=['pina', 'pipivas'],             att={'pina': ['1']}),
    dict(rid='469', label='469 √1 pṛ',   old=['purna', 'prta S1. purita'],      new=['purna', 'prta', 'purita'],     att={'prta': ['S1']}),
    dict(rid='470', label='470 √2 pṛ',   old=['purna', 'prta S1. purita'],      new=['purna', 'prta', 'purita'],     att={'prta': ['S1']}),
    dict(rid='471', label='471 √3 pṛ',   old=['purna', 'prta S1. purita'],      new=['purna', 'prta', 'purita'],     att={'prta': ['S1']}),
    dict(rid='472', label='472 √pṛc',    old=['prkta', 'prgna ? RV1', 'prce'],  new=['prkta', 'prgna', 'prce'],      att={'prgna': ['RV1']}, unc=['prgna']),
    dict(rid='524', label='524 √1 bhuj', old=['bhugna 1'],                      new=['bhugna'],                      att={'bhugna': ['1']}),
    dict(rid='525', label='525 √2 bhuj', old=['bhugna 1'],                      new=['bhugna'],                      att={'bhugna': ['1']}),
    dict(rid='573', label='573 √mṛkṣ',   old=['mraksita = seq. abhi'],          new=['mraksita'],                    note={'mraksita': '= seq. abhi (cf. abhi-mṛkṣ)'}),
    dict(rid='580', label='580 √mṛdh',   old=['mrddha 1'],                      new=['mrddha'],                      att={'mrddha': ['1']}),
    dict(rid='632', label='632 √raś',    old=['rasita 1'],                      new=['rasita'],                      att={'rasita': ['1']}),
    dict(rid='633', label='633 √ras',    old=['rasita 1'],                      new=['rasita'],                      att={'rasita': ['1']}),
    dict(rid='649', label='649 √riṣ',    old=['rista', 'rise rises'],           new=['rista', 'rise']),  # rises = OCR dup, dropped (audit-recorded)
    dict(rid='668', label='668 √lag',    old=['lagna B1.?'],                    new=['lagna'],                       att={'lagna': ['B1']}, unc=['lagna']),
    dict(rid='706', label='706 √van',    old=['vata 1'],                        new=['vata'],                        att={'vata': ['1']}),
    dict(rid='708', label='708 √1 vap',  old=['upta', 'upita E1', 'vapta E1'],  new=['upta', 'upita', 'vapta'],      att={'upita': ['E1'], 'vapta': ['E1']}),
    dict(rid='709', label='709 √2 vap',  old=['upta', 'upita E1', 'vapta E1'],  new=['upta', 'upita', 'vapta'],      att={'upita': ['E1'], 'vapta': ['E1']}),
    dict(rid='718', label='718 √vah',    old=['udha', 'vodha ? E1'],            new=['udha', 'vodha'],               att={'vodha': ['E1']}, unc=['vodha']),
    dict(rid='737', label='737 √vī',     old=['vita 1'],                        new=['vita'],                        att={'vita': ['1']}),
    dict(rid='747', label='747 √vṛh',    old=['vrdha brdha'],                   new=['vrdha', 'brdha']),  # genuine v-/b- variant pair → split, keep both
    dict(rid='790', label='790 √śuc',    old=['sukta ?'],                       new=['sukta'],                       unc=['sukta']),
    dict(rid='797', label='797 √1 śṛ',   old=['sirna', 'sirta', 'surta ? RV1'], new=['sirna', 'sirta', 'surta'],     att={'surta': ['RV1']}, unc=['surta']),
    dict(rid='798', label='798 √2 śṛ',   old=['sirna', 'sirta', 'surta ? RV1'], new=['sirna', 'sirta', 'surta'],     att={'surta': ['RV1']}, unc=['surta']),
    dict(rid='799', label='799 √3 śṛ',   old=['sirna', 'sirta', 'surta ? RV1'], new=['sirna', 'sirta', 'surta'],     att={'surta': ['RV1']}, unc=['surta']),
    dict(rid='877', label='877 √snu',    old=['snuta ?'],                       new=['snuta'],                       unc=['snuta']),
    dict(rid='892', label='892 √sphṛ',   old=['sphurita', 'sphulita C1'],       new=['sphurita', 'sphulita'],        att={'sphulita': ['C1']}),
]

# The 6 gloss-bleed records — must stay exactly as fix_ppp_gloss_bleed.py left them.
GLOSS_UNTOUCHED = {'19': ['uta'], '100': ['kusita'], '182': ['gunthita'],
                   '184': ['gumphita'], '347': ['dasta'], '831': ['sata']}

# Tokens that must never survive inside a cleaned ppp string.
FORBIDDEN = ['RV1', 'RV2', 'E1', 'C1', 'S1', 'B1', 'AA', '?', '&', '=', 'adj', 'seq.']


def jq(s):
    """JSON-quote a scalar string exactly as the file does (no ASCII escaping)."""
    return json.dumps(s, ensure_ascii=False)


def ppp_array_block(elements):
    inner = (',' + NL).join(I8 + jq(e) for e in elements)
    return '"ppp": [' + NL + inner + NL + I6 + ']'


def attestation_block(d):
    rows = []
    for form, marks in d.items():
        mk = (',' + NL).join(I10 + jq(m) for m in marks)
        rows.append(I8 + jq(form) + ': [' + NL + mk + NL + I8 + ']')
    return '"ppp_attestation": {' + NL + (',' + NL).join(rows) + NL + I6 + '}'


def uncertain_block(forms):
    inner = (',' + NL).join(I8 + jq(f) for f in forms)
    return '"ppp_uncertain": [' + NL + inner + NL + I6 + ']'


def note_block(d):
    rows = [I8 + jq(form) + ': ' + jq(text) for form, text in d.items()]
    return '"ppp_note": {' + NL + (',' + NL).join(rows) + NL + I6 + '}'


def build_new(c):
    """Clean ppp block + any additive metadata fields, joined as record fields."""
    parts = [ppp_array_block(c['new'])]
    if c.get('att'):
        parts.append(attestation_block(c['att']))
    if c.get('unc'):
        parts.append(uncertain_block(c['unc']))
    if c.get('note'):
        parts.append(note_block(c['note']))
    return (',' + NL + I6).join(parts)


def main():
    with open(APP_DATA, 'r', encoding='utf-8', newline='') as f:
        text = f.read()

    if text.startswith('﻿'):
        raise SystemExit('ERROR: file unexpectedly starts with a BOM')

    changed = 0
    audit = []

    for c in CORRECTIONS:
        wrapped_old = ppp_array_block(c['old'])
        wrapped_new = build_new(c)

        anchor = f'"id": "{c["rid"]}"'
        ai = text.find(anchor)
        if ai == -1:
            raise SystemExit(f'ERROR: record id {c["rid"]} not found')
        nxt = text.find('"id":', ai + len(anchor))
        end = nxt if nxt != -1 else len(text)
        region = text[ai:end]

        n = region.count(wrapped_old)
        if n == 0:
            print(f'  skip  {c["label"]}: already corrected (pattern not in record)')
            continue
        if n > 1:
            raise SystemExit(f'ERROR: ppp block for id {c["rid"]} matched {n}x in its own record')

        pos = text.find(wrapped_old, ai, end)
        text = text[:pos] + wrapped_new + text[pos + len(wrapped_old):]
        print(f'  fix   {c["label"]}: {c["old"]}  ->  {c["new"]}')
        audit.append({
            'id': c['rid'], 'label': c['label'].strip(),
            'ppp_before': c['old'], 'ppp_after': c['new'],
            'ppp_attestation': c.get('att'), 'ppp_uncertain': c.get('unc'),
            'ppp_note': c.get('note'),
        })
        changed += 1

    if changed == 0:
        print('Nothing to change. File already correct.')
    else:
        with open(APP_DATA, 'w', encoding='utf-8', newline='') as f:
            f.write(text)

    verify()

    # Audit trail — only (re)written when this pass actually edited records, so a
    # no-op re-run does not clobber the committed combined audit (which also covers
    # the second, infinitive pass). Note: 227/472/649 are finalized downstream by
    # fix_ppp_infinitives.py, so the `ppp_after` below is this pass's intermediate.
    if changed:
        with open(AUDIT, 'w', encoding='utf-8', newline='') as f:
            json.dump({
                'description': 'PPP apparatus-bleed cleanup (stage 1 of 2): before/after + stripped '
                               'apparatus for 39 records. Stage 2 = fix_ppp_infinitives.py.',
                'source_column': 'Whitney_roots_class-PP.txt',
                'records': [{'id': c['rid'], 'root': c['label'].split('√')[-1].strip(),
                             'ppp_before': c['old'], 'ppp_after': c['new'],
                             'attestation': c.get('att'), 'uncertain': c.get('unc'),
                             'note': c.get('note')}
                            for c in CORRECTIONS],
            }, f, ensure_ascii=False, indent=2)
        print(f'\n{changed} record(s) changed. Audit -> {AUDIT.relative_to(ROOT)}')
    else:
        print(f'\n{changed} record(s) changed (audit left as committed combined view).')


def verify():
    with open(APP_DATA, 'rb') as f:
        raw = f.read()
    assert raw[:3].hex() != 'efbbbf', 'BOM was introduced!'
    assert raw.count(b'\n') == raw.count(b'\r\n'), 'bare LF found — CRLF not preserved!'
    assert not raw.endswith(b'\n'), 'trailing newline was added!'

    data = json.loads(raw.decode('utf-8'))
    assert len(data['lexicon']) == 935, f"expected 935 entries, got {len(data['lexicon'])}"
    by_id = {e['id']: e for e in data['lexicon']}

    # 227, 472, 649 are finalized by the second pass fix_ppp_infinitives.py
    # (datival infinitives moved out of ppp), so THIS stage's exact `new` ppp is
    # only intermediate for them — assert the apparatus-stripped invariant, not
    # exact equality, so verify() holds both right after this pass and after the
    # infinitive pass.
    PIPELINED = {'227', '472', '649'}
    for c in CORRECTIONS:
        e = by_id[c['rid']]
        if c['rid'] not in PIPELINED:
            assert e['ppp'] == c['new'], f"id {c['rid']}: ppp {e['ppp']} != {c['new']}"
        # no apparatus survives in any cleaned ppp string
        for p in e['ppp']:
            for bad in FORBIDDEN:
                assert bad not in p, f"id {c['rid']}: forbidden token {bad!r} in {p!r}"
            assert not any(ch.isdigit() for ch in p), f"id {c['rid']}: digit in {p!r}"
        # additive metadata present and correct
        assert e.get('ppp_attestation') == c.get('att'), f"id {c['rid']}: ppp_attestation mismatch"
        assert e.get('ppp_uncertain') == c.get('unc'), f"id {c['rid']}: ppp_uncertain mismatch"
        assert e.get('ppp_note') == c.get('note'), f"id {c['rid']}: ppp_note mismatch"

    # expected length changes
    assert len(by_id['332']['ppp']) == 3
    assert len(by_id['452']['ppp']) == 2
    assert len(by_id['469']['ppp']) == 3 and len(by_id['470']['ppp']) == 3 and len(by_id['471']['ppp']) == 3
    assert len(by_id['747']['ppp']) == 2
    # 649's final ppp length is set by fix_ppp_infinitives.py (rise/rises moved
    # to `infinitives`), so it is not asserted here.

    # the 6 gloss records untouched (no apparatus fields, original ppp)
    for rid, want in GLOSS_UNTOUCHED.items():
        e = by_id[rid]
        assert e['ppp'] == want, f"gloss id {rid}: ppp {e['ppp']} != {want} (must stay untouched)"
        assert 'ppp_attestation' not in e and 'ppp_uncertain' not in e and 'ppp_note' not in e, \
            f"gloss id {rid}: unexpected apparatus field added"

    print(f'\nVERIFY ok — JSON valid, BOM-free, CRLF preserved, {len(data["lexicon"])} entries; '
          f'{len(CORRECTIONS)} canonical ppp + metadata confirmed; 6 gloss records untouched.')


if __name__ == '__main__':
    main()
