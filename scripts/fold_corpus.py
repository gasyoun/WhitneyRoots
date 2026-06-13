# -*- coding: utf-8 -*-
"""Phase 1: fold DCS corpus freq/forms into the spine record.

FREQ + ATTESTED FORMS ONLY — this NEVER writes a class. Everything corpus-derived lives under
a dedicated `corpus` key (lowest authority; DCS `grammar_class` is lexicon metadata, not corpus
proof — see scripts/dcs/README.md). Run AFTER parse_warnemyr.py (which builds the warnemyr spine);
idempotent — re-running just overwrites the `corpus` key. Reads src/dcs_freq.json (from
scripts/dcs/extract_dcs.py). UTF-8, no BOM.
"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
FREQ  = os.path.join(BASE, 'src', 'dcs_freq.json')
TOPN  = 8

spine   = json.load(open(SPINE, encoding='utf-8'))
entries = json.load(open(FREQ, encoding='utf-8'))['entries']

# snapshot class fields to prove the fold is class-safe
before = {r.get('whitney_no'): (tuple(r.get('class', [])), tuple(r.get('class_uncertain', [])))
          for r in spine if 'whitney_no' in r}

folded = tokens = 0
for r in spine:
    no = r.get('whitney_no')
    if no is None:
        r.pop('corpus', None)
        continue
    e = entries.get(str(no))
    if not e:
        r['corpus'] = {'dcs_status': 'no_entry'}
        continue
    r['corpus'] = {
        'dcs_lemma':      e.get('dcs_lemma'),
        'dcs_status':     e.get('dcs_status'),
        'dcs_freq':       e.get('total', 0),
        'dcs_rank':       e.get('rank'),
        'dcs_class_tag':  e.get('grammar_class', []),   # DCS lexicon metadata — NOT an asserted class
        'attested_forms': e.get('top_forms', [])[:TOPN],
        'attested_ppp':   e.get('ppp', []),
        'preverbs':       e.get('preverbs', []),
    }
    folded += 1
    if r['corpus']['dcs_freq']:
        tokens += 1

# hard guard: no class / class_uncertain may have changed
after = {r.get('whitney_no'): (tuple(r.get('class', [])), tuple(r.get('class_uncertain', [])))
         for r in spine if 'whitney_no' in r}
changed = [k for k in before if before[k] != after[k]]
assert not changed, f'FOLD ALTERED CLASS for {changed[:10]} — aborting'

json.dump(spine, open(SPINE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(SPINE, 'rb') as fb:
    assert fb.read(3).hex() != 'efbbbf', 'BOM written'
print(f'folded corpus into {folded} keyed records · {tokens} with >0 DCS tokens · class untouched ✓')
matched = sum(1 for r in spine if r.get('corpus', {}).get('dcs_status') in ('matched', 'homonym_shared'))
print(f'dcs_status matched/homonym_shared: {matched}  (freq>0: {tokens})')
