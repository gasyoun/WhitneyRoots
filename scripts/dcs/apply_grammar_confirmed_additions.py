"""
apply_grammar_confirmed_additions.py
====================================
Apply the 11 GRAMMAR_CONFIRMED conflict additions to app_data.json.

These are HIGH-confidence cases where Grammar explicitly cites
the classes that the corpus signal suggests adding.
"""

# H2892 — refuse-by-default writer lock over the human-reviewed overlays.
# Must stay the first executable statement: nothing below it may open a
# reviewed file. Set ALLOW_OVERLAY_WIPE=1 only for a deliberate, re-pinned
# rewrite (scripts/overlay_guard.py).
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
from overlay_guard import refuse_unless_hatched as _refuse_unless_hatched
_refuse_unless_hatched(__file__, targets=('src/app_data.json',))

import sys, json, pathlib
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
VERDICT_JSON = ROOT / 'corpus_class_verdicts.json'
GRAMMAR_REFS = ROOT / 'src' / 'grammar_refs.json'

ROMAN_ORDER = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
               'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}

# ── 1. Load data ──────────────────────────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

with open(VERDICT_JSON, encoding='utf-8') as f:
    verdicts = json.load(f)

with open(GRAMMAR_REFS, encoding='utf-8') as f:
    gram_refs = json.load(f)

root_to_entry_idx = {}  # bare_root → list of (idx, entry) tuples
for idx, entry in enumerate(app_data['lexicon']):
    root = entry['root'].lstrip('0123456789 ').strip()
    if root not in root_to_entry_idx:
        root_to_entry_idx[root] = []
    root_to_entry_idx[root].append((idx, entry))

# ── 2. Identify GRAMMAR_CONFIRMED additions ───────────────────────────────

additions = []  # list of (root, bare_root, classes_to_add, entry_indices)

for root, verdict in verdicts.items():
    if verdict.get('verdict') != 'conflict':
        continue

    eid = verdict['id']
    corpus_gana = verdict.get('corpus_gana')

    if not corpus_gana:
        continue

    corpus_classes = set(c.strip() for c in corpus_gana.split(','))

    # Get Grammar citations
    gram_for_root = gram_refs.get(eid, {})
    gram_refs_list = gram_for_root.get('grammar_refs', [])

    grammar_classes = set()
    for ref in gram_refs_list:
        if ref.get('class_chapter'):
            grammar_classes.add(str(ref['class_chapter']))

    # Check if Grammar confirms corpus AND grammar cites ALL classes to add
    if not grammar_classes:
        continue

    corpus_in_grammar = corpus_classes & grammar_classes
    if not corpus_in_grammar:
        continue

    # Find entries for this root
    entry_indices = root_to_entry_idx.get(root, [])
    if not entry_indices:
        continue

    # Get classes to add (what corpus suggests but Whitney doesn't have)
    for idx, entry in entry_indices:
        whitney_classes = set(entry.get('classes', []))
        classes_to_add = corpus_classes - whitney_classes

        # Check if Grammar cites ALL classes to add
        if classes_to_add <= grammar_classes:
            # All classes to add are in Grammar: GRAMMAR_CONFIRMED
            if classes_to_add:
                additions.append({
                    'root': entry['root'],
                    'bare_root': root,
                    'id': entry['id'],
                    'whitney': sorted(whitney_classes),
                    'corpus': sorted(corpus_classes),
                    'grammar': sorted(grammar_classes),
                    'to_add': sorted(classes_to_add),
                    'entry_idx': idx,
                    'entry': entry,
                    'tokens': len(verdict.get('corpus_forms', []))
                })

print(f'Found {len(additions)} GRAMMAR_CONFIRMED additions', file=sys.stderr)

# ── 3. Apply additions ──────────────────────────────────────────────────────

changes = []

for add in sorted(additions, key=lambda x: -x['tokens']):
    idx = add['entry_idx']
    entry = app_data['lexicon'][idx]
    old_classes = entry.get('classes', [])
    new_classes = sorted(set(old_classes) | set(add['to_add']),
                         key=lambda x: ROMAN_ORDER.get(x, 999))

    entry['classes'] = new_classes
    changes.append({
        'id': entry['id'],
        'root': entry['root'],
        'old': old_classes,
        'new': new_classes,
        'to_add': add['to_add'],
        'tokens': add['tokens']
    })

print(f'Applying {len(changes)} changes:\n', file=sys.stderr)
for change in changes:
    old_str = ', '.join(change['old']) if change['old'] else '(none)'
    new_str = ', '.join(change['new'])
    print(f"  [{change['id']}] {change['root']:20s}: {old_str:15s} + {', '.join(change['to_add'])} → {new_str:15s} ({change['tokens']:5d} tokens)")

# ── 4. Write updated app_data.json ──────────────────────────────────────────

with open(APP_DATA, 'w', encoding='utf-8') as f:
    json.dump(app_data, f, ensure_ascii=False, indent=2)

print(f'\nWrote {APP_DATA}', file=sys.stderr)
print(f'Total additions applied: {len(changes)}', file=sys.stderr)
