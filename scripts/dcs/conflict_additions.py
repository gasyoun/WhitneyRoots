"""
conflict_additions.py
====================
For HIGH priority conflicts where Grammar confirms corpus signal,
identify which classes could be added to Whitney.

Logic:
  - If corpus signal is [I, VI] and Grammar cites only one:
    - If Grammar cites I but not VI: consider adding VI (corpus shows both)
    - If Grammar cites VI but not I: consider adding I (corpus shows both)
  - If both are in Grammar: definitely add
  - If neither: Grammar-unsupported, skip

Output: candidates_for_addition.md
"""

import sys, json, pathlib
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
GRAMMAR_REFS = ROOT / 'src' / 'grammar_refs.json'
VERDICT_JSON = ROOT / 'corpus_class_verdicts.json'
OUT_MD = ROOT / 'candidates_for_addition.md'

ROMAN_ORDER = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
               'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}

# ── 1. Load data ──────────────────────────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

with open(GRAMMAR_REFS, encoding='utf-8') as f:
    gram_refs = json.load(f)

with open(VERDICT_JSON, encoding='utf-8') as f:
    verdicts = json.load(f)

root_to_entry = {}
for entry in app_data['lexicon']:
    root = entry['root'].lstrip('0123456789 ').strip()
    root_to_entry[root] = entry

# ── 2. Analyze HIGH priority conflicts ──────────────────────────────────────

candidates = []  # list of (root, id, whitney, corpus_signal, to_add, grammar_status)

for root, verdict in verdicts.items():
    if verdict.get('verdict') != 'conflict':
        continue

    eid = verdict['id']
    entry = root_to_entry.get(root)
    if not entry:
        continue

    whitney_classes = set(entry.get('classes', []))
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

    # Check if Grammar confirms any corpus class
    corpus_in_grammar = corpus_classes & grammar_classes

    if not corpus_in_grammar:
        # Grammar doesn't confirm corpus signal
        continue

    # This is HIGH priority; now determine what to add
    classes_to_add = corpus_classes - whitney_classes

    if not classes_to_add:
        # All corpus classes are already in Whitney
        continue

    # Check which classes to add are in Grammar
    add_in_grammar = classes_to_add & grammar_classes

    if add_in_grammar:
        status = 'GRAMMAR_CONFIRMED'
    else:
        # Classes to add are corpus-suggested but not in Grammar
        # Still valid if Grammar cites at least one corpus class
        status = 'CORPUS_INFERRED'

    tokens = len(verdict.get('corpus_forms', []))

    candidates.append({
        'root': root,
        'id': eid,
        'whitney': sorted(whitney_classes),
        'corpus': sorted(corpus_classes),
        'grammar': sorted(grammar_classes),
        'to_add': sorted(classes_to_add),
        'add_in_grammar': sorted(add_in_grammar),
        'status': status,
        'tokens': tokens,
    })

# ── 3. Sort by status and token count ──────────────────────────────────────

status_order = {'GRAMMAR_CONFIRMED': 0, 'CORPUS_INFERRED': 1}
candidates.sort(key=lambda x: (status_order.get(x['status'], 99), -x['tokens']))

# ── 4. Write output ───────────────────────────────────────────────────────

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('# Candidates for Addition from Conflicts\n\n')
    f.write('_HIGH priority conflict cases where Grammar/corpus support adding classes._\n\n')

    status_counts = defaultdict(int)
    for c in candidates:
        status_counts[c['status']] += 1

    f.write('## Summary\n\n')
    f.write(f'- **GRAMMAR_CONFIRMED**: {status_counts["GRAMMAR_CONFIRMED"]} (Grammar cites all classes to add)\n')
    f.write(f'- **CORPUS_INFERRED**: {status_counts["CORPUS_INFERRED"]} (Corpus shows class, Grammar confirms at least one)\n')
    f.write(f'- **Total candidates**: {len(candidates)}\n\n')

    # GRAMMAR_CONFIRMED (highest priority)
    confirmed = [c for c in candidates if c['status'] == 'GRAMMAR_CONFIRMED']
    if confirmed:
        f.write(f'## GRAMMAR_CONFIRMED ({len(confirmed)})\n\n')
        f.write('Grammar explicitly cites all classes to add. These are high-confidence.\n\n')

        for c in confirmed:
            f.write(f"### [{c['id']}] {c['root']}\n\n")
            f.write(f"**Proposal:** {' + '.join(c['to_add'])} → {', '.join(sorted(set(c['whitney']) | set(c['to_add'])))}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Whitney | {', '.join(c['whitney'])} |\n")
            f.write(f"| Corpus | {', '.join(c['corpus'])} |\n")
            f.write(f"| Grammar | {', '.join(c['grammar'])} |\n")
            f.write(f"| To add | {', '.join(c['to_add'])} |\n")
            f.write(f"| Tokens | {c['tokens']} |\n\n")

    # CORPUS_INFERRED
    inferred = [c for c in candidates if c['status'] == 'CORPUS_INFERRED']
    if inferred:
        f.write(f'## CORPUS_INFERRED ({len(inferred)})\n\n')
        f.write('Corpus shows these classes; Grammar confirms at least one. Consider review.\n\n')

        for c in inferred[:20]:  # Show top 20
            f.write(f"### [{c['id']}] {c['root']}\n\n")
            f.write(f"**Proposal:** {' + '.join(c['to_add'])} → {', '.join(sorted(set(c['whitney']) | set(c['to_add'])))}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Whitney | {', '.join(c['whitney'])} |\n")
            f.write(f"| Corpus | {', '.join(c['corpus'])} |\n")
            f.write(f"| Grammar | {', '.join(c['grammar'])} |\n")
            f.write(f"| To add | {', '.join(c['to_add'])} |\n")
            f.write(f"| Tokens | {c['tokens']} |\n\n")

print(f'Wrote {OUT_MD}', file=sys.stderr)

# ── 5. Summary ──────────────────────────────────────────────────────────

print(f'\nConflict Addition Candidates:')
print(f'  GRAMMAR_CONFIRMED: {status_counts["GRAMMAR_CONFIRMED"]}')
print(f'  CORPUS_INFERRED: {status_counts["CORPUS_INFERRED"]}')
print(f'  Total: {len(candidates)}')

if confirmed:
    print(f'\nTop GRAMMAR_CONFIRMED (by frequency):')
    for c in confirmed[:10]:
        old = ', '.join(c['whitney'])
        new = ', '.join(sorted(set(c['whitney']) | set(c['to_add'])))
        print(f"  {c['id']:3s} {c['root']:15s}: {old:15s} → {new:15s} ({c['tokens']:4d} tokens)")
