# -*- coding: utf-8 -*-
"""Phase 2b: align MW + Apte root entries onto the Whitney-root hub (conservative, DESIGN §6).

Hub-side join keyed on SLP1, then disambiguate Whitney homonyms by class (Gaṇa):
  - dict root unique for this SLP1            -> auto-accept (basis 'unique-slp1')
  - several Whitney homonyms share the SLP1   -> the one whose class overlaps the dict class
      * exactly one overlaps                  -> accept (basis 'class')
      * zero or >1 overlap                    -> AMBIGUOUS -> alignment_review.json (human + Zalizniak)
Folds mw_id / apte_id (+ homonym, class, gloss) into the spine under a `dict` key. NEVER touches
`class` (hard-guarded). Writes crosswalk/root_alignment.csv + crosswalk/alignment_review.json.
Idempotent. UTF-8, no BOM.
"""
import sys, os, re, json, csv
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT   = os.path.join(BASE, 'crosswalk')
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')

mw   = json.load(open(os.path.join(OUT,'mw_roots.json'), encoding='utf-8'))
ap   = json.load(open(os.path.join(OUT,'apte_roots.json'), encoding='utf-8'))
spine= json.load(open(SPINE, encoding='utf-8'))

# slp1 per spine record — read from the spine itself (parse_warnemyr stores root_slp1). No roots.csv
# dependency, so this no longer requires emit_crosswalk to have run first (breaks the ordering cycle).
slp1_by_no = {r['whitney_no']: r.get('root_slp1', '') for r in spine if 'whitney_no' in r}
hub_share = {}                                    # how many Whitney homonyms share each SLP1
for v in slp1_by_no.values():
    hub_share[v] = hub_share.get(v, 0) + 1

def index(dict_roots):
    by = {}
    for d in dict_roots:
        by.setdefault(d['slp1'], []).append(d)
    return by
MW, AP = index(mw), index(ap)

before = {r['whitney_no']: (tuple(r.get('class',[])), tuple(r.get('class_uncertain',[])))
          for r in spine if 'whitney_no' in r}

align_rows, review = [], []

def pick(cands, hub_class, no, root, source):
    """Return (chosen_dict_root, basis) or (None, None); log ambiguity to review."""
    if not cands:
        return None, None
    if len(cands) == 1:
        return cands[0], 'unique-slp1'
    hc = set(hub_class)
    byclass = [d for d in cands if set(d['class']) & hc] if hc else []
    if len(byclass) == 1:
        return byclass[0], 'class'
    review.append({'whitney_no': no, 'root': root, 'source': source,
                   'hub_class': hub_class,
                   'candidates': [{'L': d.get('mw_L') or d.get('ap_L'), 'homonym': d['homonym'],
                                   'class': d['class'], 'gloss': d['gloss']} for d in cands]})
    return None, 'AMBIGUOUS'

acc = {'mw': 0, 'apte': 0}
for r in spine:
    no = r.get('whitney_no')
    if no is None:
        r.pop('dict', None); continue
    s = slp1_by_no.get(no, '')
    hub_class = r.get('class', [])
    d = {}
    m, mb = pick(MW.get(s, []), hub_class, no, r['root_iast'], 'mw')
    if m:
        if mb == 'unique-slp1' and hub_share.get(s, 0) > 1: mb = 'slp1-shared'   # 1 MW entry ↔ ≥2 Whitney homonyms
        d.update(mw_id=m['mw_L'], mw_homonym=m['homonym'], mw_class=m['class'], mw_gloss=m['gloss'], mw_basis=mb)
        align_rows.append([no, s, 'mw', m['mw_L'], m['homonym'] or '', '|'.join(m['class']), mb]); acc['mw'] += 1
    a, ab = pick(AP.get(s, []), hub_class, no, r['root_iast'], 'apte')
    if a:
        if ab == 'unique-slp1' and hub_share.get(s, 0) > 1: ab = 'slp1-shared'
        d.update(apte_id=a['ap_L'], apte_homonym=a['homonym'], apte_class=a['class'], apte_gloss=a['gloss'], apte_basis=ab)
        align_rows.append([no, s, 'apte', a['ap_L'], a['homonym'] or '', '|'.join(a['class']), ab]); acc['apte'] += 1
    d['senses'] = [g for g in (d.get('mw_gloss'), d.get('apte_gloss')) if g]
    r['dict'] = d

after = {r['whitney_no']: (tuple(r.get('class',[])), tuple(r.get('class_uncertain',[])))
         for r in spine if 'whitney_no' in r}
changed = [k for k in before if before[k] != after[k]]
assert not changed, f'ALIGN ALTERED CLASS for {changed[:10]} — aborting'

json.dump(spine, open(SPINE,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
with open(os.path.join(OUT,'root_alignment.csv'),'w',encoding='utf-8',newline='') as f:
    w = csv.writer(f); w.writerow(['whitney_no','root_slp1','source','dict_L','dict_homonym','dict_class','basis'])
    w.writerows(align_rows)
json.dump({'note': 'Whitney roots whose MW/Apte homonym is ambiguous (SLP1 shared, class cannot '
                   'disambiguate). Resolve by present-stem/gloss, then Zalizniak. DESIGN §6.',
           'count': len(review), 'items': review},
          open(os.path.join(OUT,'alignment_review.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
for p in ('root_alignment.csv','alignment_review.json'):
    with open(os.path.join(OUT,p),'rb') as fb:
        assert fb.read(3).hex() != 'efbbbf'

linked_mw  = sum(1 for r in spine if r.get('dict',{}).get('mw_id'))
linked_ap  = sum(1 for r in spine if r.get('dict',{}).get('apte_id'))
linked_any = sum(1 for r in spine if r.get('dict',{}).get('mw_id') or r.get('dict',{}).get('apte_id'))
print(f'aligned (class-safe ✓): MW {acc["mw"]} (unique+class)  Apte {acc["apte"]}')
print(f'hub roots with mw_id {linked_mw} · apte_id {linked_ap} · either {linked_any} / {len(before)}')
print(f'ambiguous -> alignment_review.json: {len(review)} groups')
basis = {}
for row in align_rows: basis[(row[2],row[6])] = basis.get((row[2],row[6]),0)+1
print('basis breakdown:', dict(sorted(basis.items())))
