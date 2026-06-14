# -*- coding: utf-8 -*-
"""Phase 5: derive src/reader_data.json — a compact, browser-loadable view over the crosswalk.

The reader introduces NO new data (DESIGN §8): this only reshapes the spine into
  roots[whitney_no] = {root, class, gloss, senses, freq, forms, sections, ...}
plus a form_index (normalised DCS-attested surface form -> [whitney_no]) for passage
token resolution. Read-only on the spine. UTF-8, no BOM.
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
OUT   = os.path.join(BASE, 'src', 'reader_data.json')

from sanskrit_util import norm, nfold   # exact + nasal-folded lookup keys; mirror of reader.js

DCS   = os.path.join(BASE, os.pardir, 'VisualDCS', 'src', 'DCS-data-2026', 'dcs_full.sqlite')
spine = json.load(open(SPINE, encoding='utf-8'))
roots, form_index, fold_alias, lemma2no = {}, {}, {}, {}

def add_form(form, no):
    k = norm(form)
    if not k:
        return
    form_index.setdefault(k, [])
    if no not in form_index[k]:
        form_index[k].append(no)

for r in spine:
    no = r.get('whitney_no')
    if no is None:
        continue
    c = r.get('corpus') or {}
    d = r.get('dict') or {}
    forms = [{'form': f.get('form'), 'n': f.get('n')} for f in (c.get('attested_forms') or [])]
    roots[str(no)] = {
        'root': r['root_iast'], 'slp1_hom': r.get('homonym'),
        'class': r.get('class', []), 'unc': r.get('class_uncertain', []),
        'gloss': r.get('gloss_short', ''), 'senses': d.get('senses', []),
        'mw_id': d.get('mw_id'), 'apte_id': d.get('apte_id'),
        'freq': c.get('dcs_freq'), 'freq_sense': c.get('dcs_freq_token'),
        'rank': c.get('dcs_rank'), 'ppp': r.get('ppp', ''),
        'forms': forms,
        'sections': [{'cat': e['category'], 'label': e['label'], 'lo': e['section_lo'],
                      'hi': e['section_hi'], 'ch': e['chapter'], 'url': e['url']}
                     for e in (r.get('whitney_sections') or [])],
    }
    # form_index sources: DCS attested surface forms, the PPP, and the bare root
    for f in forms:
        add_form(f['form'], no)
    add_form(r.get('ppp'), no)
    for p in (c.get('attested_ppp') or []):
        add_form(p.get('stem'), no)
    add_form(r['root_iast'], no)
    lem = c.get('dcs_lemma')
    if lem:
        lemma2no.setdefault(lem, []).append(no)

# Enrich the index with EVERY attested verb form (finite + participle + infinitive) for each
# Whitney-linked DCS lemma — straight from the corpus. Homonyms sharing a lemma all become
# candidates (the reader's chooser then disambiguates). Skipped if VisualDCS isn't a sibling.
dcs_added = 0
if os.path.exists(DCS):
    import sqlite3
    before = len(form_index)
    con = sqlite3.connect(DCS)
    for lemma, form, mu in con.execute(
            "SELECT DISTINCT lemma, form, m_unsandhied FROM token WHERE upos='VERB'"):
        nos = lemma2no.get(lemma)
        if not nos:
            continue
        for surf in (form, mu):
            if not surf or ' ' in surf or '-' in surf:   # passage tokens are single, unbound words
                continue
            for no in nos:
                add_form(surf, no)
    con.close()
    dcs_added = len(form_index) - before
    print(f'DCS verb-form enrichment: +{dcs_added} surface-form keys from {len(lemma2no)} linked lemmas')
else:
    print('DCS sqlite not found — form index limited to spine top-forms (no finite-form enrichment)')

# Rank each form's candidate roots by DCS frequency so the likeliest root is the chooser
# default and rare mis-tags sort last.
for k in form_index:
    form_index[k].sort(key=lambda no: -(roots[str(no)].get('freq') or 0))

# Two-tier resolution: form_index is keyed by the EXACT norm (so am/an, kram/kṛ stay distinct);
# fold_alias maps each nasal-folded key -> the exact keys that fold to it, consulted ONLY when the
# exact lookup misses. This keeps precision for non-nasal tokens while recovering anusvāra recall
# (kāṃkṣ- → kāṅkṣ-) against the corpus's inconsistent ṃ-vs-homorganic spellings.
for k in form_index:
    fa = nfold(k)
    fold_alias.setdefault(fa, [])
    if k not in fold_alias[fa]:
        fold_alias[fa].append(k)

out = {
    '_meta': {'what': 'Browser view over the Whitney-root crosswalk (DESIGN §8 reader).',
              'source': 'scratch/phase0/root_spine.json — no new data added.',
              'roots': len(roots), 'form_index_keys': len(form_index), 'fold_alias_keys': len(fold_alias),
              'license': 'CC BY-SA 4.0'},
    'roots': roots, 'form_index': form_index, 'fold_alias': fold_alias,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
with open(OUT, 'rb') as fb:
    assert fb.read(3).hex() != 'efbbbf'

sz = os.path.getsize(OUT)
print(f'wrote src/reader_data.json — roots {len(roots)}, form_index {len(form_index)} keys, '
      f'fold_alias {len(fold_alias)} keys, {sz//1024} KB')

def resolve(tok):
    ex = form_index.get(norm(tok))
    if ex:
        return ex, 'exact'
    out2 = []
    for k in fold_alias.get(nfold(tok), []):
        out2 += [n for n in form_index.get(k, []) if n not in out2]
    return out2, 'fold'

print('demo-token resolution check (exact→fold fallback):')
for tok in ['uvāca', 'bhavati', 'kṛtvā', 'am', 'kāṃkṣati', 'avocat', 'jagāma']:
    hits, via = resolve(tok)
    names = ['%s#%s' % (roots[str(h)]['root'], h) for h in hits]
    print(f"  {tok:<10} [{via:5}] -> {names or '— (unresolved)'}")
