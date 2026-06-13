# -*- coding: utf-8 -*-
"""Phase 5: derive src/reader_data.json — a compact, browser-loadable view over the crosswalk.

The reader introduces NO new data (DESIGN §8): this only reshapes the spine into
  roots[whitney_no] = {root, class, gloss, senses, freq, forms, sections, ...}
plus a form_index (normalised DCS-attested surface form -> [whitney_no]) for passage
token resolution. Read-only on the spine. UTF-8, no BOM.
"""
import sys, os, re, json, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
OUT   = os.path.join(BASE, 'src', 'reader_data.json')

def norm(s):
    """Lookup key: NFC, lowercased, strip combining accents (DCS is unaccented anyway)."""
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn' or c in 'ँंः')
    return unicodedata.normalize('NFC', s).strip().lower()

spine = json.load(open(SPINE, encoding='utf-8'))
roots, form_index = {}, {}

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
        'freq': c.get('dcs_freq'), 'rank': c.get('dcs_rank'), 'ppp': r.get('ppp', ''),
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

out = {
    '_meta': {'what': 'Browser view over the Whitney-root crosswalk (DESIGN §8 reader).',
              'source': 'scratch/phase0/root_spine.json — no new data added.',
              'roots': len(roots), 'form_index_keys': len(form_index),
              'license': 'CC BY-SA 4.0'},
    'roots': roots, 'form_index': form_index,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
with open(OUT, 'rb') as fb:
    assert fb.read(3).hex() != 'efbbbf'

sz = os.path.getsize(OUT)
print(f'wrote src/reader_data.json — roots {len(roots)}, form_index {len(form_index)} keys, {sz//1024} KB')
print('demo-token resolution check:')
for tok in ['uvāca', 'gacchati', 'bhavati', 'gatvā', 'kṛtvā', 'bhūtvā', 'gataḥ', 'avocat', 'vakṣyati', 'jagāma']:
    hits = form_index.get(norm(tok), [])
    names = ['%s#%s' % (roots[str(h)]['root'], h) for h in hits]
    print(f"  {tok:<10} -> {names or '— (unresolved)'}")
