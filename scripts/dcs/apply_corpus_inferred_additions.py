"""
apply_corpus_inferred_additions.py
==================================
Apply 110 CORPUS_INFERRED conflict additions to app_data.json.

These are medium-confidence cases where:
  - Corpus signal suggests a class
  - Grammar confirms at least one corpus class (even if not all)
  - The class to add is not yet in Grammar refs

Strategy: Add corpus-suggested classes where Grammar validates at least
one of them, indicating the root is genuinely multi-class.
"""

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

root_to_entry_idx = {}
for idx, entry in enumerate(app_data['lexicon']):
    root = entry['root'].lstrip('0123456789 ').strip()
    if root not in root_to_entry_idx:
        root_to_entry_idx[root] = []
    root_to_entry_idx[root].append((idx, entry))

# ── 2. Identify CORPUS_INFERRED additions ──────────────────────────────────

additions = []  # list of (root, classes_to_add, tokens, entry_indices)

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

    # Check if Grammar confirms ANY corpus class
    corpus_in_grammar = corpus_classes & grammar_classes

    if not corpus_in_grammar:
        # Grammar doesn't confirm ANY corpus class: skip
        continue

    # Check if some (but not all) classes to add are in Grammar
    entry_indices = root_to_entry_idx.get(root, [])
    if not entry_indices:
        continue

    for idx, entry in entry_indices:
        whitney_classes = set(entry.get('classes', []))
        classes_to_add = corpus_classes - whitney_classes

        if not classes_to_add:
            continue

        # Check: are ALL classes to add in Grammar?
        all_in_grammar = classes_to_add <= grammar_classes
        if all_in_grammar:
            # This is GRAMMAR_CONFIRMED, skip it (already handled)
            continue

        # CORPUS_INFERRED: at least one corpus class in Grammar,
        # but not all classes to add
        if corpus_in_grammar:
            tokens = len(verdict.get('corpus_forms', []))
            additions.append({
                'root': entry['root'],
                'bare_root': root,
                'id': entry['id'],
                'whitney': sorted(whitney_classes),
                'corpus': sorted(corpus_classes),
                'grammar': sorted(grammar_classes),
                'to_add': sorted(classes_to_add),
                'corpus_in_grammar': sorted(corpus_in_grammar),
                'entry_idx': idx,
                'entry': entry,
                'tokens': tokens,
            })

print(f'Found {len(additions)} CORPUS_INFERRED additions', file=sys.stderr)

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
        'tokens': add['tokens'],
        'grammar_backs': add['corpus_in_grammar']
    })

print(f'Applying {len(changes)} CORPUS_INFERRED changes:\n', file=sys.stderr)

by_root = defaultdict(list)
for change in changes:
    by_root[change['root']].append(change)

for root in sorted(by_root.keys()):
    root_changes = by_root[root]
    for change in root_changes:
        old_str = ', '.join(change['old']) if change['old'] else '(none)'
        new_str = ', '.join(change['new'])
        backing = ', '.join(change['grammar_backs']) if change['grammar_backs'] else '?'
        print(f"  [{change['id']:3s}] {root:20s}: {old_str:15s} + {', '.join(change['to_add'])} "
              f"→ {new_str:15s} (Grammar cites {backing}, {change['tokens']:5d} tokens)")

# ── 4. Write updated app_data.json ──────────────────────────────────────────

with open(APP_DATA, 'w', encoding='utf-8') as f:
    json.dump(app_data, f, ensure_ascii=False, indent=2)

print(f'\nWrote {APP_DATA}', file=sys.stderr)
print(f'Total CORPUS_INFERRED additions applied: {len(changes)}', file=sys.stderr)

# ── 5. Summary ──────────────────────────────────────────────────────────

unique_roots = len(set(c['root'] for c in changes))
print(f'Unique roots updated: {unique_roots}', file=sys.stderr)
print(f'Total entries modified: {len(changes)}', file=sys.stderr)
