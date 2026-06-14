# -*- coding: utf-8 -*-
"""vidyut-prakriya paradigm generator (DISPLAY use only — never touches the authoritative spine
class/freq).  The pilot synthesis (2026-06-14) concluded vidyut's right role here is paradigm
*display* and form *validation*, not gaṇa attribution.  This is the display half.

For each Whitney keyed root we find its Dhātupāṭha entry/entries in vidyut by an it-stripped clean
root key — obtained from vidyut's OWN derivation history (`result[0]` at the LAST it-lopa, rule 1.3.9,
BEFORE the present lakāra is inserted at 3.2.123), NOT a hand-rolled anubandha stripper.  Taking 1.3.9
rather than 3.2.123 avoids the num-augment (7.1.58 idito num) that would otherwise nasalise idit roots
(skud not skund).  The match is exact-then-nasal-folded (Y/N/R/M → n) so the spine's homorganic SLP1
(aYj, kANkz, hiMs) reaches vidyut's dental-n clean root.  We then generate a representative paradigm
(present 3×3, the other lakāras 3sg/3pl, a set of kṛdantas) and render every form SLP1→IAST.

TWO GATES bind the RIGHT dhātu to each Whitney homonym (a bare-string + gaṇa match alone wrongly
attached the reap-root dāti to √dā 'give', the kill-root jñāti to √jñā 'know', etc.):
  1. gaṇa — the dhātu's Pāṇinian gaṇa must be one Whitney lists for the root (Whitney's class numbers
     from warnemyr ≠ Pāṇini's gaṇa for many roots; e.g. √i I/IV/V/IX vs adādi=II — those are withheld).
  2. corroboration — where the spine/corpus records present-system forms, the dhātu's generated PRESENT
     must match one (the present stem is the gaṇa identity, so it picks the right homonym; the PPP is
     built on the bare root and is shared, so it can't bind a gaṇa).  If a homonym group has present
     evidence, only present-matched dhātus survive; if the corpus is too sparse to attest any present,
     we fall back to PPP-match; with no recorded form at all, gaṇa-only.  Each emitted paradigm carries
     `attested` (corpus/warnemyr confirms ≥1 form).

Conservative throughout: where nothing corroborates, abstain.  Writes src/paradigms.json (UTF-8, no BOM).
"""
import sys, os, json, collections, time
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import re
from sanskrit_util import from_slp1, to_roman, form_key

from vidyut import prakriya as P

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VDATA = os.path.join(BASE, 'scratch', 'vidyut_data', 'prakriya')
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
OUT   = os.path.join(BASE, 'src', 'paradigms.json')

WH2G = {'I': P.Gana.Bhvadi, 'II': P.Gana.Adadi, 'III': P.Gana.Juhotyadi, 'IV': P.Gana.Divadi,
        'V': P.Gana.Svadi, 'VI': P.Gana.Tudadi, 'VII': P.Gana.Rudhadi, 'VIII': P.Gana.Tanadi,
        'IX': P.Gana.Kryadi, 'X': P.Gana.Curadi}
G2ARABIC = {P.Gana.Bhvadi: 1, P.Gana.Adadi: 2, P.Gana.Juhotyadi: 3, P.Gana.Divadi: 4,
            P.Gana.Svadi: 5, P.Gana.Tudadi: 6, P.Gana.Rudhadi: 7, P.Gana.Tanadi: 8,
            P.Gana.Kryadi: 9, P.Gana.Curadi: 10}

PUR = [('3', P.Purusha.Prathama), ('2', P.Purusha.Madhyama), ('1', P.Purusha.Uttama)]
VAC = [('sg', P.Vacana.Eka), ('du', P.Vacana.Dvi), ('pl', P.Vacana.Bahu)]
# secondary lakāras shown as 3sg+3pl (label -> Lakara)
SECONDARY = [('imperfect', P.Lakara.Lan), ('imperative', P.Lakara.Lot),
             ('optative', P.Lakara.VidhiLin), ('perfect', P.Lakara.Lit),
             ('aorist', P.Lakara.Lun), ('future', P.Lakara.Lrt)]
# kṛdantas shown as nominative-sg citation (participles/PPP/agent) or the indeclinable itself
KRT_NOM = [('ppp', 'kta'), ('past_active', 'ktavatu'), ('pres_act_ptcp', 'Satf'),
           ('pres_mid_ptcp', 'SAnac'), ('gerundive', 'tavya'), ('agent', 'tfc'),
           ('perf_act_ptcp', 'kvasu')]
KRT_IND = [('gerund', 'ktvA'), ('infinitive', 'tumun')]

v = P.Vyakarana()


def _texts(pada):
    return sorted({p.text for p in v.derive(pada)})


def tin(d, lakara, pur, vac):
    return _texts(P.Pada.Tinanta(dhatu=d, prayoga=P.Prayoga.Kartari, lakara=lakara,
                                 purusha=pur, vacana=vac))


def clean_root(d):
    """It-stripped SLP1 root from vidyut's OWN derivation. We take result[0] at the LAST it-lopa step
    (rule 1.3.9 lopo'nubandhasya) BEFORE the present lakāra is inserted (3.2.123) — NOT result[0] at
    3.2.123 itself, because for idit roots the num-augment (7.1.58 idito num dhātoḥ) fires in between
    and would nasalise the stem (skudi~ → 'skund' instead of the bare 'skud'). If no 1.3.9 fired (a
    vowel-final root with no consonant anubandha, e.g. BU), fall back to result[0] at 3.2.123."""
    prks = v.derive(P.Pada.Tinanta(dhatu=d, prayoga=P.Prayoga.Kartari, lakara=P.Lakara.Lat,
                                   purusha=P.Purusha.Prathama, vacana=P.Vacana.Eka))
    if not prks:
        return None
    last_itlopa = None
    for st in prks[0].history:
        if st.code == '1.3.9':
            last_itlopa = st.result[0]
        elif st.code == '3.2.123':
            return last_itlopa if last_itlopa is not None else st.result[0]
    return last_itlopa


def nasal_key(slp1):
    """Fold the class/anusvāra nasals (ñ Y, ṅ N, ṇ R, anusvāra M) → dental n, for cross-matching the
    spine's homorganic SLP1 (aYj, kANkz, hiMs) against vidyut's clean root, which renders them as n."""
    return re.sub('[YNRM]', 'n', slp1 or '')


def krt_nom(d, krt_name):
    """Nominative sg masc of a kṛdanta (citation form: gataḥ, gacchan, gantā…)."""
    if not hasattr(P.Krt, krt_name):
        return []
    pp = P.Pratipadika.krdanta(dhatu=d, krt=getattr(P.Krt, krt_name))
    return _texts(P.Pada.Subanta(pratipadika=pp, linga=P.Linga.Pum,
                                 vibhakti=P.Vibhakti.Prathama, vacana=P.Vacana.Eka))


def krt_ind(d, krt_name):
    """Indeclinable kṛdanta (gerund gatvā, infinitive gantum) — the avyaya form."""
    if not hasattr(P.Krt, krt_name):
        return []
    pp = P.Pratipadika.krdanta(dhatu=d, krt=getattr(P.Krt, krt_name))
    out = _texts(P.Pada.Subanta(pratipadika=pp, linga=P.Linga.Pum,
                                vibhakti=P.Vibhakti.Prathama, vacana=P.Vacana.Eka))
    if not out:                                   # avyayas may not inflect; try first/seventh
        for vib in (P.Vibhakti.Dvitiya, P.Vibhakti.Saptami):
            out = _texts(P.Pada.Subanta(pratipadika=pp, linga=P.Linga.Pum,
                                        vibhakti=vib, vacana=P.Vacana.Eka))
            if out:
                break
    return out


def iast_list(forms):
    return [from_slp1(f) for f in forms]


def gen_paradigm(en):
    """Full structured paradigm (IAST) for one Dhātupāṭha entry."""
    d = en.dhatu
    present = {}
    for pn, pu in PUR:
        for vn, va in VAC:
            present['%s%s' % (pn, vn)] = iast_list(tin(d, P.Lakara.Lat, pu, va))
    secondary = {}
    for label, lak in SECONDARY:
        cell = {'3sg': iast_list(tin(d, lak, P.Purusha.Prathama, P.Vacana.Eka)),
                '3pl': iast_list(tin(d, lak, P.Purusha.Prathama, P.Vacana.Bahu))}
        if cell['3sg'] or cell['3pl']:
            secondary[label] = cell
    krt = {}
    for label, kn in KRT_NOM:
        forms = iast_list(krt_nom(d, kn))
        if forms:
            krt[label] = forms
    for label, kn in KRT_IND:
        forms = iast_list(krt_ind(d, kn))
        if forms:
            krt[label] = forms
    pada = 'parasmaipada' if present.get('3sg') and any(f.endswith('ti') for f in present['3sg']) else ''
    if present.get('3sg') and any(f.endswith('te') for f in present['3sg']):
        pada = (pada + '+atmanepada').strip('+') if pada else 'atmanepada'
    return {'dhatu_code': en.code, 'gana': to_roman([G2ARABIC[d.gana]])[0],
            'gana_arabic': G2ARABIC[d.gana], 'artha': from_slp1(en.artha or ''), 'pada': pada,
            'present': present, 'secondary': secondary, 'krt': krt}


def spine_evidence(r):
    """The forms the spine + corpus actually record for this root, as form_key sets, used to bind a
    vidyut dhātu to the RIGHT homonym (not just one sharing root_slp1 + gaṇa).  Returns (ppp_ev, form_ev)."""
    c = r.get('corpus') or {}
    ppp_ev = {form_key(r.get('ppp') or '')}
    for p in (c.get('attested_ppp') or []):
        ppp_ev.add(form_key(p.get('stem', '')))
    form_ev = {form_key(f.get('form', '')) for f in (c.get('attested_forms') or [])}
    ppp_ev.discard(''); form_ev.discard('')
    return ppp_ev, form_ev


def paradigm_form_keys(pg):
    """(ppp_keys, present_keys) for corroboration.  ONLY the present system + PPP — these are the
    gaṇa-distinguishing forms.  The perfect/aorist/future are built on the bare root and are shared
    across all homonyms of a root_slp1 (every √dā homonym has perfect dadau), so including them would
    let a wrong-present intruder (dā-reap dāti) corroborate via the shared dadau.  Excluding them lets
    corroboration actually separate gaṇa homonyms."""
    ppp = {form_key(x) for x in pg.get('krt', {}).get('ppp', [])}
    present = {form_key(x) for cell in pg.get('present', {}).values() for x in cell}
    return ppp, present


def main():
    t0 = time.time()
    entries = P.Data(VDATA).load_dhatu_entries()
    by_root = collections.defaultdict(list)        # clean_root -> [entry]
    by_root_nasal = collections.defaultdict(list)  # nasal-folded clean_root -> [entry]
    for en in entries:
        try:
            cr = clean_root(en.dhatu)
        except Exception:
            cr = None
        if cr:
            by_root[cr].append(en)
            by_root_nasal[nasal_key(cr)].append(en)
    print('indexed %d dhātu entries under %d clean roots (%.1fs)'
          % (len(entries), len(by_root), time.time() - t0))

    spine = json.load(open(SPINE, encoding='utf-8'))
    out = {}
    n_roots = n_para = n_attested = 0
    withheld_divergent, uncorroborated = [], []
    for r in spine:
        no = r.get('whitney_no')
        rs = r.get('root_slp1')
        if no is None or not rs:
            continue
        wh_classes = r.get('class') or []
        wh_ganas = {WH2G[c] for c in wh_classes if c in WH2G}
        # exact clean-root match first; fall back to nasal-folded (recovers añj, kāṅkṣ, hiṃs, śaṃs…)
        cands = by_root.get(rs) or by_root_nasal.get(nasal_key(rs), [])
        if not cands:
            continue
        ppp_ev, form_ev = spine_evidence(r)
        # Gate 1 (gaṇa): the dhātu's Pāṇinian gaṇa must be one Whitney lists.  Then build every
        # gaṇa-agreeing candidate and score it: pres_match (its generated present is attested) and
        # ppp_match (its PPP is recorded).  The present stem IS the gaṇa identity, so it disambiguates
        # competing homonyms; the PPP is built on the bare root and is shared, so it only confirms
        # existence, it cannot bind a gaṇa.
        seen, cand_pgs, had_divergent = set(), [], False
        for en in cands:
            if en.code in seen:
                continue
            seen.add(en.code)
            g = en.dhatu.gana
            if g not in wh_ganas:
                had_divergent = True
                continue
            pg = gen_paradigm(en)
            vppp, vpres = paradigm_form_keys(pg)
            cand_pgs.append((en, pg, g, bool(vppp & ppp_ev), bool(vpres & form_ev)))

        # Gate 2 (corroboration), tiered: if ANY candidate's present is attested, the present
        # disambiguates — keep only present-matched ones (rejects √dā-give's reap intruder dāti and
        # √jñā-know's kill intruder jñāti, whose presents are unattested, even though a corpus-lumped
        # PPP stem like 'dāta' would otherwise leak them in).  If NO candidate's present is attested
        # (sparse corpus), fall back to PPP-match so a genuine root isn't dropped for lack of an
        # attested present.  If the root has no recorded form at all → gaṇa-only.
        any_present = any(prm for *_, prm in cand_pgs)
        per_gana, paradigms = collections.Counter(), []
        for en, pg, g, ppm, prm in cand_pgs:
            if form_ev or ppp_ev:
                keep = prm if any_present else ppm
            else:
                keep = True                      # no evidence — gaṇa-only fallback
            if not keep:
                uncorroborated.append('%s#%s:%s(%s)' % (r['root_iast'], no, en.code, en.artha))
                continue
            if per_gana[g] >= 4:                 # cap homonymous arthas in one gaṇa (√van keeps all 4)
                continue
            per_gana[g] += 1
            pg['attested'] = prm or ppm          # corpus/warnemyr confirms ≥1 form
            pg['_ppp_match'] = ppm
            paradigms.append(pg)
        if not paradigms:
            if had_divergent and wh_classes:
                withheld_divergent.append('%s/%s' % (rs, '·'.join(wh_classes)))
            continue
        # PPP-attested blocks first (so √budh shows aniṭ buddha before seṭ budhita), then any attested,
        # then by gaṇa number.
        paradigms.sort(key=lambda p: (not p.pop('_ppp_match'), not p['attested'], p['gana_arabic']))
        out[str(no)] = {'root': r['root_iast'], 'whitney_class': wh_classes, 'paradigms': paradigms}
        n_roots += 1
        n_para += len(paradigms)
        n_attested += sum(1 for p in paradigms if p['attested'])

    payload = {
        '_meta': {
            'what': 'vidyut-prakriya generated verb paradigms for Whitney roots (DISPLAY only).',
            'generated_by': 'vidyut-prakriya %s (ambuda-org, MIT); Dhātupāṭha %d entries'
                            % (getattr(__import__('vidyut'), '__version__', '?'), len(entries)),
            'method': "clean root = result[0] at the last it-lopa (rule 1.3.9) before laṭ-insertion "
                      "(3.2.123) — pre-num-augment, so idit roots stay bare (skud not skund); matched "
                      "exact then nasal-folded (Y/N/R/M→n). paradigm = Laṭ 3×3 + Laṅ/Loṭ/VidhiLiṅ/Liṭ/"
                      "Luṅ/Lṛṭ 3sg+3pl + kṛdantas.",
            'caveat': "Two gates: (1) the dhātu's Pāṇinian gaṇa must be a Whitney class; (2) where the "
                      "spine/corpus records any form, the dhātu's generated PPP or a finite form must "
                      "match it — binding the right homonym and rejecting same-(slp1,gaṇa) intruders "
                      "(jñā≠jñāti, dā give≠dāp reap, vid know/find unswapped). `attested`=corpus/warnemyr "
                      "confirms ≥1 form; roots with no recorded form fall back to gaṇa-only. Authoritative "
                      "class/freq live in the spine and are NOT derived from this file.",
            'roots': n_roots, 'paradigms': n_para, 'attested_paradigms': n_attested,
            'withheld_gana_divergent': len(withheld_divergent),
            'rejected_uncorroborated': len(uncorroborated),
            'license_data': 'CC BY-SA 4.0; generator MIT'},
        'roots': out}
    json.dump(payload, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    with open(OUT, 'rb') as fb:
        assert fb.read(3).hex() != 'efbbbf'

    sz = os.path.getsize(OUT)
    print('wrote src/paradigms.json — %d roots, %d paradigms (%d corpus-attested), %d KB (%.1fs)'
          % (n_roots, n_para, n_attested, sz // 1024, time.time() - t0))
    print('withheld (vidyut has root only in a non-Whitney gaṇa): %d  e.g. %s'
          % (len(withheld_divergent), withheld_divergent[:8]))
    print('rejected (gaṇa-ok but no spine/corpus form corroborates → wrong homonym): %d  e.g. %s'
          % (len(uncorroborated), uncorroborated[:8]))
    print('\ndemo:')
    demo_nos = [k for k, vv in out.items() if vv['root'] in ('gam', 'bhū', 'kṛ', 'vac', 'as')]
    for k in demo_nos:
        d = out[k]
        for pg in d['paradigms']:
            print('  #%s √%s [%s · %s] pres3sg=%s ppp=%s ger=%s inf=%s'
                  % (k, d['root'], pg['gana'], pg['artha'],
                     pg['present'].get('3sg'), pg['krt'].get('ppp'),
                     pg['krt'].get('gerund'), pg['krt'].get('infinitive')))


if __name__ == '__main__':
    main()
