# -*- coding: utf-8 -*-
"""vidyut-prakriya form-validation (the second half of vidyut's role per the 2026-06-14 pilot
synthesis).  ADVISORY ONLY — never edits the spine; emits a flag report a human adjudicates.

For each Whitney root that has a vidyut paradigm (its Pāṇinian gaṇa matches a Whitney class), we
take vidyut's canonical past-passive-participle (kta) and cross-check it against:
  - warnemyr's recorded PPP (`ppp` on the spine), and
  - the DCS corpus's most-frequent attested PPP stem (`corpus.attested_ppp[0]`).

Verdicts:
  match           warnemyr PPP is among vidyut's generated kta stems (or no warnemyr PPP but the
                  DCS top PPP stem matches vidyut) — the recorded form is Pāṇinianly sound.
  mismatch        warnemyr records a PPP and it is NOT among vidyut's kta stems → flagged for REVIEW
                  (NOT auto-correction — see the corroboration caveat below).
  fill_candidate  warnemyr has no PPP, AND the DCS corpus's top PPP MATCHES vidyut's kta → corpus-backed
                  safe add (genuinely corroborated; this is the only "fill" we vouch for).
  vidyut_only     warnemyr has no PPP, and the corpus's top PPP does NOT match vidyut's kta → vidyut has
                  a form but neither warnemyr nor the corpus's commonest PPP confirms it (don't auto-add).

A mismatch is `corpus_backs_vidyut` when the DCS corpus's attested PPP agrees with vidyut and disagrees
with warnemyr.  ⚠️ This is NOT a "warnemyr is wrong" signal.  A 3-verifier Sanskritist panel (2026-06-14,
13/13 unanimous) found that ALL 13 corpus-corroborated mismatches are either a HOMONYM ARTIFACT (warnemyr
records the PPP of the glossed homonym, e.g. √mṛ "crush"→mūrṇá, √vid "find"→vittá; the corpus surfaces the
lumped dominant root's PPP, mṛta/vidita) or an aniṭ/seṭ DOUBLET of one root (kṣubdha/kṣubhita) — none is a
warnemyr error.  Treat corroborated mismatches as a HOMONYM/VARIANT detector, dispositioned in
docs/DECISIONS_NEEDED.md §3, NOT a correction list.  Writes crosswalk/ppp_validation.json (UTF-8, no BOM).
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sanskrit_util import form_key as ppp_key   # shared length-preserving, nasal-folding form key

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
PARA  = os.path.join(BASE, 'src', 'paradigms.json')
OUT   = os.path.join(BASE, 'crosswalk', 'ppp_validation.json')


def ppp_stem(iast_nom_sg):
    """kta nom.sg.masc (gataḥ, kṛtaḥ, krāntaḥ) → length-preserving stem key (gata, kṛta, krānta)."""
    return ppp_key(iast_nom_sg)


def main():
    spine = json.load(open(SPINE, encoding='utf-8'))
    para = json.load(open(PARA, encoding='utf-8'))['roots']
    by_no = {str(r['whitney_no']): r for r in spine if r.get('whitney_no') is not None}

    items = []
    counts = {'match': 0, 'mismatch': 0, 'fill_candidate': 0, 'vidyut_only': 0}
    for no, pdata in para.items():
        r = by_no.get(no)
        if not r:
            continue
        # vidyut kta stems across this root's agreeing paradigms (every emitted paradigm carries one)
        vstems = set()
        for pg in pdata['paradigms']:
            for f in (pg.get('krt', {}).get('ppp') or []):
                vstems.add(ppp_stem(f))
        if not vstems:
            continue                                # can't validate without a generated kta (never seen)
        wn_ppp = ppp_key(r.get('ppp') or '')
        c = r.get('corpus') or {}
        dcs_ppp = ppp_key((c.get('attested_ppp') or [{}])[0].get('stem', '')) if c.get('attested_ppp') else ''

        if wn_ppp:
            verdict = 'match' if wn_ppp in vstems else 'mismatch'
        elif dcs_ppp and dcs_ppp in vstems:
            verdict = 'fill_candidate'              # warnemyr blank; corpus DOES confirm vidyut → safe add
        elif dcs_ppp:
            verdict = 'vidyut_only'                 # warnemyr blank; corpus's top PPP does NOT match vidyut
        else:
            continue                                # nothing to compare — skip silently
        counts[verdict] += 1
        # corroboration = warnemyr recorded a form, it is genuinely absent from vidyut's kta set, and
        # the corpus independently attests vidyut's form (i.e. the corpus backs vidyut against warnemyr).
        corpus_backs_vidyut = (verdict == 'mismatch' and bool(dcs_ppp)
                               and dcs_ppp in vstems and wn_ppp not in vstems)
        items.append({'whitney_no': int(no), 'root': pdata['root'],
                      'class': pdata.get('whitney_class', []),
                      'warnemyr_ppp': r.get('ppp') or '', 'vidyut_ppp': sorted(vstems),
                      'dcs_top_ppp': (c.get('attested_ppp') or [{}])[0].get('stem', '') if c.get('attested_ppp') else '',
                      'verdict': verdict, 'corpus_backs_vidyut': corpus_backs_vidyut})

    # mismatches first (most actionable), corpus-corroborated ones at the very top
    order = {'mismatch': 0, 'fill_candidate': 1, 'vidyut_only': 2, 'match': 3}
    items.sort(key=lambda x: (order[x['verdict']], not x['corpus_backs_vidyut'], x['whitney_no']))
    payload = {
        '_meta': {'what': 'vidyut-prakriya PPP (kta) form-validation against warnemyr + DCS. Advisory.',
                  'generated_by': 'vidyut-prakriya; compares spine.ppp & corpus.attested_ppp vs generated kta',
                  'note': 'Advisory; never edits the spine. corpus_backs_vidyut is a HOMONYM/VARIANT detector, '
                          'NOT a correction signal — all 13 such cases are warnemyr-correct (panel-verified); '
                          'see docs/DECISIONS_NEEDED.md §3.',
                  'counts': counts, 'roots_checked': len(items)},
        'items': items}
    json.dump(payload, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(OUT, 'rb') as fb:
        assert fb.read(3).hex() != 'efbbbf'

    print('wrote crosswalk/ppp_validation.json — %d roots checked' % len(items))
    print('  counts:', counts)
    print('\nmismatches (warnemyr PPP ∉ vidyut kta) — corpus-corroborated first:')
    for it in [x for x in items if x['verdict'] == 'mismatch'][:25]:
        flag = '  ⟸ corpus backs vidyut' if it['corpus_backs_vidyut'] else ''
        print('  √%-9s %-6s warnemyr=%-12s vidyut=%-22s dcs=%-10s%s'
              % (it['root'], '/'.join(it['class']), it['warnemyr_ppp'],
                 ','.join(it['vidyut_ppp']), it['dcs_top_ppp'], flag))


if __name__ == '__main__':
    main()
