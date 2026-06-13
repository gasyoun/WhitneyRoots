# -*- coding: utf-8 -*-
"""Phase 4: build root -> form-category -> Whitney § edges (the "Why this form?" graph).

Composition (DESIGN §7): root has-form-of-category C (from the warnemyr spine: gaṇa class +
paradigm inventory) THEN section_range(C) (from src/form_section_concordance.json). Folds a
`whitney_sections` edge list into each spine record and writes crosswalk/root_section_edges.csv.
Validates every edge whose chapter was fetched (IX–XV) against src/whitney_sections.json.
NEVER touches `class` (hard-guarded). Idempotent. UTF-8, no BOM.
"""
import sys, os, json, csv
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
CONC  = os.path.join(BASE, 'src', 'form_section_concordance.json')
SECS  = os.path.join(BASE, 'src', 'whitney_sections.json')
OUT   = os.path.join(BASE, 'crosswalk')

conc  = json.load(open(CONC, encoding='utf-8'))
CAT   = conc['categories']
GANA  = conc['gana_present']         # gaṇa → present-class category; aorist/other categories come
PAGE  = conc['_meta']['page_base']   # pre-detected from full text in parse_warnemyr.detect_forms
spine = json.load(open(SPINE, encoding='utf-8'))
secs  = json.load(open(SECS, encoding='utf-8'))
fetched_nums  = {s['section_number'] for s in secs['sections']}
fetched_chaps = {c['chapter'] for c in secs['_meta']['chapters_fetched']}

def categories_for(r):
    """Concordance category-keys this root has a form of: present gaṇa(s) from the asserted
    `class` (via gana_present) + the parse-time `forms_present` (detected on FULL paradigm text
    in parse_warnemyr — fixes both the 240-char truncation loss and the spaced sa-aorist token)."""
    cats = [GANA[g] for g in r.get('class', []) if g in GANA]
    cats += r.get('forms_present', [])
    seen, out = set(), []
    for c in cats:
        if c in CAT and c not in seen:
            seen.add(c); out.append(c)
    return out

before = {r['whitney_no']: (tuple(r.get('class', [])), tuple(r.get('class_uncertain', [])))
          for r in spine if 'whitney_no' in r}

edge_rows, n_edges, n_validated, n_unfetched, with_edges = [], 0, 0, 0, 0
for r in spine:
    no = r.get('whitney_no')
    if no is None:
        r.pop('whitney_sections', None); continue
    edges = []
    for c in categories_for(r):
        meta = CAT[c]
        url = '%s/Chapter_%s#%d' % (PAGE, meta['chapter'], meta['lo'])
        edges.append({'category': c, 'label': meta['label'], 'section_lo': meta['lo'],
                      'section_hi': meta['hi'], 'chapter': meta['chapter'], 'url': url})
        edge_rows.append([no, c, meta['lo'], meta['hi'], meta['chapter'], url])
        n_edges += 1
        if meta['chapter'] in fetched_chaps:
            assert meta['lo'] in fetched_nums, f"edge §{meta['lo']} ({c}) not in fetched sections"
            n_validated += 1
        else:
            n_unfetched += 1
    edges.sort(key=lambda e: e['section_lo'])
    r['whitney_sections'] = edges
    if edges: with_edges += 1

after = {r['whitney_no']: (tuple(r.get('class', [])), tuple(r.get('class_uncertain', [])))
         for r in spine if 'whitney_no' in r}
changed = [k for k in before if before[k] != after[k]]
assert not changed, f'PHASE 4 ALTERED CLASS for {changed[:10]} — aborting'

json.dump(spine, open(SPINE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(os.path.join(OUT, 'root_section_edges.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['whitney_no', 'category', 'section_lo', 'section_hi', 'chapter', 'wikisource_url'])
    w.writerows(edge_rows)
for p in (SPINE, os.path.join(OUT, 'root_section_edges.csv')):
    with open(p, 'rb') as fb:
        assert fb.read(3).hex() != 'efbbbf'

print(f'roots with §-edges: {with_edges}/{len(before)}  ·  total edges: {n_edges}  ·  class untouched ✓')
print(f'edges validated against fetched §§ (IX–XV): {n_validated}  ·  into unfetched chapters: {n_unfetched}')
# show one worked example
ex = next(r for r in spine if r.get('whitney_no') == 528)  # bhū
print(f"\nexample #{ex['whitney_no']} {ex['root_iast']} (class {ex['class']}):")
for e in ex['whitney_sections']:
    print(f"  {e['category']:<20} §§{e['section_lo']}-{e['section_hi']}  {e['url']}")
