# -*- coding: utf-8 -*-
"""vidyut-prakriya form-validation (the second half of vidyut's role per the 2026-06-14 pilot
synthesis).  ADVISORY ONLY — never edits the spine; emits a flag report a human adjudicates.

For each Whitney root that has a vidyut paradigm (its Pāṇinian gaṇa matches a Whitney class), we
take vidyut's canonical past-passive-participle (kta) and cross-check it against:
  - warnemyr's recorded PPP(s) — the accented `ppp` on the spine PLUS any doublet forms warnemyr
    lists comma-separated in the numbered source `Whitney_roots_class-PP.txt` (e.g. √gup records
    BOTH 'gupita, gupta'); we honour ALL of them, not just the first, and
  - the DCS corpus's most-frequent attested PPP stem (`corpus.attested_ppp[0]`).

DOUBLETS: the spine's `ppp` keeps only the first form warnemyr's HTML page prints, so a root whose
second recorded form (gupta) is the one vidyut generates used to be a FALSE 'mismatch'.  We now read
the full comma-separated PPP list from Whitney_roots_class-PP.txt and treat the root as a match if
ANY recorded form matches.  (That source column is ASCII-romanised — 'ksubhita' for kṣubhita — so a
doublet carrying ṛ/ṣ/ś only registers when length-preserving form_key() can equate it; we never
coerce an ambiguous ASCII fold.  EXCEPTION: WHITNEY_RESTORE diacritic-restores the two source forms
that Whitney's Grammar confirms as a single-root aniṭ/seṭ doublet — kṣubh §956b.4, piś §956b.5 — so
they match; the genuine HOMONYM cases mṛ/iṣ/hā are left ASCII and correctly stay flagged.)

CAUSATIVE: vidyut's kta is generated on BOTH the primary stem (krt.ppp → gata, gupta) and the
causative ṇic stem (krt.ppp_caus → gamita, gopita, śamita).  Many warnemyr -ita PPPs are causative-
stem forms (√śam → śamita), so we check a warnemyr form against the primary kta first, then the
causative kta, then the DCS top form.  Each item records WHICH set cleared it (matched_against ∈
{vidyut, vidyut_caus, dcs}) and WHICH warnemyr form (match_basis ∈ {spine, doublet, source_alt,
corpus_fill}), so any class of match is revisable later.

Verdicts:
  match           SOME warnemyr PPP (any doublet form) is among vidyut's generated PRIMARY or
                  CAUSATIVE kta stems, or equals the DCS top PPP stem (or no warnemyr PPP but the
                  DCS top PPP matches vidyut) — the recorded form is Pāṇinianly sound / corroborated.
  mismatch        warnemyr records PPP(s) and NONE is among vidyut's primary/causative kta stems
                  (nor equals the DCS top PPP) → flagged for REVIEW (NOT auto-correction).
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
import sys, os, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sanskrit_util import form_key as ppp_key   # shared length-preserving, nasal-folding form key

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
PARA  = os.path.join(BASE, 'src', 'paradigms.json')
LOCAL = os.path.join(BASE, 'Whitney_roots_class-PP.txt')   # numbered source — doublet PPP forms
OUT   = os.path.join(BASE, 'crosswalk', 'ppp_validation.json')

# Diacritic restoration of the ASCII-romanised source PPP column, applied ONLY to single-root doublets
# that Whitney's Grammar confirms as ONE root taking BOTH the aniṭ and the seṭ form (so the seṭ alternant
# vidyut generates is genuinely warnemyr's too).  Without this, form_key (which keeps ṣ/ś/ṛ distinct)
# cannot equate the source's ASCII 'ksubhita' with vidyut's 'kṣubhita'.  DELIBERATELY NOT applied to the
# §3a homonym KEEP cases (mṛ #572, iṣ #43, hā #912), where the alternant belongs to a DIFFERENT root and
# the ASCII form *correctly* fails to match.  Cited verbatim against en.wikisource.org Sanskrit_Grammar_(Whitney):
WHITNEY_RESTORE = {
    '148': {'ksubhita': 'kṣubhita'},   # √kṣubh — §956b.4 "kṣubh ... have both forms" (kṣubdha / kṣubhita)
    '455': {'pisita': 'piśita'},        # √piś   — §956b.5 "piç has both forms"        (piṣṭá / piśita)
}


def ppp_stem(iast_nom_sg):
    """kta nom.sg.masc (gataḥ, kṛtaḥ, krāntaḥ) → length-preserving stem key (gata, kṛta, krānta)."""
    return ppp_key(iast_nom_sg)


def load_warnemyr_forms(path):
    """Whitney_roots_class-PP.txt → {whitney_no(str): [ppp_form, ...]}.  Column 4 ('PPP-форма(ы)')
    is comma-separated when a root has a doublet (√gup → 'gupita, gupta'); columns are run-of-≥2-space
    delimited, so a doublet's internal ', ' stays inside one column.  We take the first whitespace
    token of each comma segment (drops trailing gloss-bleed / '? adj' / period tags) and keep only
    lowercase, letter-bearing tokens.  NB this column is ASCII-romanised (no ṛ/ṣ/ś/retroflex dots),
    so form_key() equates a form with vidyut/DCS only when the form carries no such diacritic."""
    by_no = {}
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*(\d+)\.\s', line)
        if not m:
            continue
        cols = re.split(r'\s{2,}', line.strip())          # [num+root, class, PPP, gloss]
        ppp = cols[2].strip() if len(cols) > 2 else ''
        if ppp in ('—', '-', '?', ''):
            by_no[m.group(1)] = []
            continue
        forms = []
        for seg in ppp.split(','):
            tok = seg.strip().split()
            if tok and not tok[0].isupper() and re.search(r'[a-zāīūṛṝḷḹ]', tok[0]):
                forms.append(tok[0])
        sub = WHITNEY_RESTORE.get(m.group(1), {})        # diacritic restoration for confirmed doublets
        by_no[m.group(1)] = [sub.get(f, f) for f in forms]
    return by_no


def _basis_tally(items):
    """How many matches were cleared by each warnemyr-form class (spine/doublet/source_alt/corpus_fill)."""
    return dict(sorted(collections.Counter(x['match_basis'] for x in items if x['match_basis']).items()))


def _against_tally(items):
    """What each match was cleared against (vidyut primary / vidyut_caus / dcs)."""
    return dict(sorted(collections.Counter(x['matched_against'] for x in items if x['matched_against']).items()))


def merge_forms(primary, extra):
    """Ordered, form_key-deduped warnemyr PPP list with `primary` (the accented spine PPP) FIRST for
    back-compat (== warnemyr_ppp), followed by any additional doublet forms from the romanised source."""
    out, seen = [], set()
    for f in [primary] + (extra or []):
        f = (f or '').strip()
        if not f:
            continue
        k = ppp_key(f)
        if k and k not in seen:
            seen.add(k)
            out.append(f)
    return out


def main():
    spine = json.load(open(SPINE, encoding='utf-8'))
    para = json.load(open(PARA, encoding='utf-8'))['roots']
    by_no = {str(r['whitney_no']): r for r in spine if r.get('whitney_no') is not None}
    wn_extra = load_warnemyr_forms(LOCAL)           # whitney_no → full comma-separated PPP doublet list

    items = []
    counts = {'match': 0, 'mismatch': 0, 'fill_candidate': 0, 'vidyut_only': 0}
    for no, pdata in para.items():
        r = by_no.get(no)
        if not r:
            continue
        # vidyut kta stems across this root's agreeing paradigms — PRIMARY kta (krt.ppp) and the
        # CAUSATIVE (ṇic) kta (krt.ppp_caus), kept apart so a causative-only match is auditable.
        vstems, vstems_caus = set(), set()
        for pg in pdata['paradigms']:
            krt = pg.get('krt', {})
            for f in (krt.get('ppp') or []):
                vstems.add(ppp_stem(f))
            for f in (krt.get('ppp_caus') or []):
                vstems_caus.add(ppp_stem(f))
        if not vstems:
            continue                                # can't validate without a generated primary kta
        spine_ppp = r.get('ppp') or ''
        wn_ppp = ppp_key(spine_ppp)                 # primary (accented) form key — back-compat
        c = r.get('corpus') or {}
        dcs_ppp = ppp_key((c.get('attested_ppp') or [{}])[0].get('stem', '')) if c.get('attested_ppp') else ''

        # honour DOUBLETS: warnemyr may record >1 PPP (√gup 'gupita, gupta'); a root is sound if ANY
        # recorded form is generated by vidyut (primary OR causative kta) OR equals the DCS top form.
        # wn_forms keeps the accented spine PPP first (== warnemyr_ppp), then the romanised-source
        # doublets, deduped by key.
        wn_forms = merge_forms(spine_ppp, wn_extra.get(no)) if wn_ppp else []
        wn_keys = {ppp_key(f) for f in wn_forms}

        # PROVENANCE (recorded so the verdict is revisable):
        #   matched_form     which warnemyr form cleared the flag ('' if mismatch)
        #   matched_against  what it matched: vidyut | vidyut_caus | dcs
        #   match_basis      which warnemyr form it was: spine | doublet | source_alt | corpus_fill
        matched_form = matched_against = match_basis = ''
        if wn_ppp:
            txt_multi = len(wn_extra.get(no) or []) >= 2     # the source listed a true comma-doublet
            for tier, pool in (('vidyut', vstems), ('vidyut_caus', vstems_caus)):
                for f in wn_forms:
                    if ppp_key(f) in pool:
                        matched_form, matched_against = f, tier
                        break
                if matched_form:
                    break
            if not matched_form and dcs_ppp:                 # warnemyr form == DCS corpus top
                for f in wn_forms:
                    if ppp_key(f) == dcs_ppp:
                        matched_form, matched_against = f, 'dcs'
                        break
            if matched_form:
                match_basis = ('spine' if ppp_key(matched_form) == wn_ppp
                               else ('doublet' if txt_multi else 'source_alt'))
            verdict = 'match' if matched_form else 'mismatch'
        elif dcs_ppp and (dcs_ppp in vstems or dcs_ppp in vstems_caus):
            verdict = 'fill_candidate'              # warnemyr blank; corpus DOES confirm vidyut → safe add
            match_basis = 'corpus_fill'
            matched_against = 'vidyut' if dcs_ppp in vstems else 'vidyut_caus'
        elif dcs_ppp:
            verdict = 'vidyut_only'                 # warnemyr blank; corpus's top PPP does NOT match vidyut
        else:
            continue                                # nothing to compare — skip silently
        counts[verdict] += 1
        # corroboration = NONE of warnemyr's recorded forms is in vidyut's kta set, yet the corpus's top
        # PPP independently attests vidyut's PRIMARY kta (i.e. the corpus backs vidyut against warnemyr).
        corpus_backs_vidyut = (verdict == 'mismatch' and bool(dcs_ppp)
                               and dcs_ppp in vstems and not (wn_keys & vstems))
        items.append({'whitney_no': int(no), 'root': pdata['root'],
                      'class': pdata.get('whitney_class', []),
                      'warnemyr_ppp': spine_ppp, 'warnemyr_ppp_forms': wn_forms,
                      'vidyut_ppp': sorted(vstems), 'vidyut_ppp_caus': sorted(vstems_caus),
                      'dcs_top_ppp': (c.get('attested_ppp') or [{}])[0].get('stem', '') if c.get('attested_ppp') else '',
                      'verdict': verdict, 'match_basis': match_basis, 'matched_form': matched_form,
                      'matched_against': matched_against, 'corpus_backs_vidyut': corpus_backs_vidyut})

    # mismatches first (most actionable), corpus-corroborated ones at the very top
    order = {'mismatch': 0, 'fill_candidate': 1, 'vidyut_only': 2, 'match': 3}
    items.sort(key=lambda x: (order[x['verdict']], not x['corpus_backs_vidyut'], x['whitney_no']))
    payload = {
        '_meta': {'what': 'vidyut-prakriya PPP (kta) form-validation against warnemyr (all doublet forms) + DCS. Advisory.',
                  'generated_by': 'vidyut-prakriya; compares spine.ppp + Whitney_roots_class-PP.txt doublets '
                                  '& corpus.attested_ppp vs generated PRIMARY (krt.ppp) and CAUSATIVE (krt.ppp_caus) kta',
                  'note': 'Advisory; never edits the spine. warnemyr_ppp_forms lists ALL of warnemyr\'s recorded '
                          'PPP doublets (spine accented form first, then romanised-source forms); a match needs '
                          'only ONE of them in vidyut PRIMARY or CAUSATIVE kta, or the DCS top form. Per item, '
                          'match_basis/matched_form/matched_against record WHY it matched so any class of match '
                          '(doublet | source_alt | causative=vidyut_caus | dcs) can be revised later. '
                          'corpus_backs_vidyut (surviving mismatches) is a HOMONYM/VARIANT detector, NOT a '
                          'correction signal — see docs/DECISIONS_NEEDED.md §3.',
                  'counts': counts, 'roots_checked': len(items),
                  'match_basis_counts': dict(_basis_tally(items)),
                  'matched_against_counts': dict(_against_tally(items))},
        'items': items}
    json.dump(payload, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(OUT, 'rb') as fb:
        assert fb.read(3).hex() != 'efbbbf'

    print('wrote crosswalk/ppp_validation.json — %d roots checked' % len(items))
    print('  counts:', counts)
    print('  matched_against:', dict(_against_tally(items)), '| match_basis:', dict(_basis_tally(items)))
    caus = [x for x in items if x['matched_against'] == 'vidyut_caus']
    print('\nmatches cleared by the CAUSATIVE (ṇic) kta (%d):' % len(caus))
    for it in sorted(caus, key=lambda x: x['whitney_no']):
        print('  √%-9s %-6s warnemyr=%-8s == caus %s' % (it['root'], '/'.join(it['class']),
              it['matched_form'], ','.join(it['vidyut_ppp_caus'])))
    print('\nmismatches (NO warnemyr PPP form ∈ vidyut primary/caus kta / DCS) — corpus-corroborated first:')
    for it in [x for x in items if x['verdict'] == 'mismatch'][:25]:
        flag = '  ⟸ corpus backs vidyut' if it['corpus_backs_vidyut'] else ''
        print('  √%-9s %-6s warnemyr=%-22s vidyut=%-18s caus=%-14s dcs=%-10s%s'
              % (it['root'], '/'.join(it['class']), ','.join(it['warnemyr_ppp_forms']) or it['warnemyr_ppp'],
                 ','.join(it['vidyut_ppp']), ','.join(it['vidyut_ppp_caus']), it['dcs_top_ppp'], flag))


if __name__ == '__main__':
    main()
