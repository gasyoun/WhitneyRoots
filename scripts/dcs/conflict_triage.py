"""
conflict_triage.py
==================
Detailed analysis of 231 CONFLICT roots: corpus stem signals diverge from Whitney.

Strategy: For each conflict, show:
  - Whitney classes
  - Corpus signal (what present-stems suggest)
  - Grammar citations (if any for the corpus-suggested class)
  - Recommendation: is the corpus-suggested class valid per Grammar?

Output: detailed_conflict_triage.md with priorities:
  1. HIGH_PRIORITY: Corpus signal matches Grammar citation (Grammar confirms corpus)
  2. GRAMMAR_SILENT: Corpus signal is valid per Grammar but not Whitney
  3. UNCERTAIN: Grammar unclear or corpus signal weakly supported
"""

import sys, json, pathlib, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]  # WhitneyRoots/
APP_DATA    = ROOT / 'src' / 'app_data.json'
GRAMMAR_REFS = ROOT / 'src' / 'grammar_refs.json'
VERDICT_JSON = ROOT / 'corpus_class_verdicts.json'
OUT_MD      = ROOT / 'detailed_conflict_triage.md'

NUM_TO_ROMAN = {
    '1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V',
    '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X'
}

ROMAN_ORDER = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
               'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}

def normalize_class(class_str):
    """Convert class number to Roman numeral"""
    s = class_str.strip()
    if s in NUM_TO_ROMAN:
        return NUM_TO_ROMAN[s]
    return s

# ── 1. Load data ─────────────────────────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

with open(GRAMMAR_REFS, encoding='utf-8') as f:
    gram_refs = json.load(f)

with open(VERDICT_JSON, encoding='utf-8') as f:
    verdicts = json.load(f)

# Build lookups
root_to_entry = {}
for entry in app_data['lexicon']:
    root = entry['root'].lstrip('0123456789 ').strip()
    root_to_entry[root] = entry

# ── 2. Extract CONFLICT verdicts ─────────────────────────────────────────

conflicts = {}  # root → verdict
for root, verdict in verdicts.items():
    if verdict.get('verdict') == 'conflict':
        conflicts[root] = verdict

print(f'Found {len(conflicts)} conflict cases', file=sys.stderr)

# ── 3. Analyze each conflict against Grammar ──────────────────────────────

analysis = []

for root, verdict in conflicts.items():
    eid = verdict['id']
    entry = root_to_entry.get(root)

    if not entry:
        continue

    whitney_classes = set(entry.get('classes', []))
    corpus_gana = verdict.get('corpus_gana')  # e.g., "I, VI"

    # Parse corpus signal
    corpus_classes = set()
    if corpus_gana:
        for c in corpus_gana.split(','):
            corpus_classes.add(c.strip())

    # Get Grammar citations
    gram_for_root = gram_refs.get(eid, {})
    gram_refs_list = gram_for_root.get('grammar_refs', [])

    grammar_classes = set()
    for ref in gram_refs_list:
        if ref.get('class_chapter'):
            grammar_classes.add(str(ref['class_chapter']))

    # Determine recommendation
    # If corpus signal matches Grammar, it's high-priority
    corpus_in_grammar = corpus_classes & grammar_classes

    if corpus_in_grammar:
        # Grammar confirms corpus signal (even if different from Whitney)
        priority = 'HIGH'
        reasoning = f"Grammar cites {sorted(corpus_in_grammar)}, corpus signals {sorted(corpus_classes)}. Consider adding."
    elif not grammar_classes:
        # No Grammar class-chapter refs; uncertain
        priority = 'UNCERTAIN'
        reasoning = f"No Grammar class-chapter refs. Corpus signals {sorted(corpus_classes)} vs Whitney {sorted(whitney_classes)}."
    else:
        # Grammar cites different classes than corpus
        priority = 'GRAMMAR_CONFLICT'
        reasoning = f"Grammar cites {sorted(grammar_classes)}, corpus signals {sorted(corpus_classes)}, Whitney has {sorted(whitney_classes)}."

    tokens = len(verdict.get('corpus_forms', []))

    analysis.append({
        'root': root,
        'id': eid,
        'whitney': sorted(whitney_classes),
        'corpus_signal': sorted(corpus_classes) if corpus_classes else None,
        'grammar_classes': sorted(grammar_classes),
        'corpus_in_grammar': sorted(corpus_in_grammar),
        'tokens': tokens,
        'priority': priority,
        'note': reasoning,
    })

# ── 4. Sort by priority and token count ───────────────────────────────────

priority_order = {'HIGH': 0, 'GRAMMAR_CONFLICT': 1, 'UNCERTAIN': 2}
analysis.sort(key=lambda x: (priority_order.get(x['priority'], 99), -x['tokens']))

# ── 5. Write output ──────────────────────────────────────────────────────

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('# Conflict Triage (231 cases)\n\n')
    f.write('_Corpus present-stem signals diverge from Whitney class assignments._\n\n')

    # Summary
    priority_counts = defaultdict(int)
    for a in analysis:
        priority_counts[a['priority']] += 1

    f.write('## Summary by Priority\n\n')
    f.write(f'- **HIGH** (Grammar confirms corpus): {priority_counts["HIGH"]}\n')
    f.write(f'- **GRAMMAR_CONFLICT** (Grammar vs corpus): {priority_counts["GRAMMAR_CONFLICT"]}\n')
    f.write(f'- **UNCERTAIN** (No Grammar refs): {priority_counts["UNCERTAIN"]}\n')
    f.write(f'\n')

    # Top HIGH priority (10 most frequent)
    high_priority = [a for a in analysis if a['priority'] == 'HIGH']
    if high_priority:
        f.write(f'## HIGH Priority ({len(high_priority)})\n\n')
        f.write(f'Grammar confirms corpus signal. Consider adding to Whitney classes.\n\n')

        for a in high_priority[:20]:  # Show top 20
            f.write(f"### [{a['id']}] {a['root']}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Whitney | {', '.join(a['whitney'])} |\n")
            f.write(f"| Corpus signal | {', '.join(a['corpus_signal']) if a['corpus_signal'] else '—'} |\n")
            f.write(f"| Grammar classes | {', '.join(a['grammar_classes']) if a['grammar_classes'] else '(no refs)'} |\n")
            f.write(f"| Corpus in Grammar | {', '.join(a['corpus_in_grammar']) if a['corpus_in_grammar'] else '—'} |\n")
            f.write(f"| Tokens | {a['tokens']} |\n\n")
            f.write(f"{a['note']}\n\n")

    # GRAMMAR_CONFLICT (show a sample)
    grammar_conflict = [a for a in analysis if a['priority'] == 'GRAMMAR_CONFLICT']
    if grammar_conflict:
        f.write(f'## GRAMMAR_CONFLICT ({len(grammar_conflict)})\n\n')
        f.write(f'Grammar and corpus both differ from Whitney. Manual review needed.\n\n')

        for a in grammar_conflict[:20]:
            f.write(f"### [{a['id']}] {a['root']}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Whitney | {', '.join(a['whitney'])} |\n")
            f.write(f"| Corpus signal | {', '.join(a['corpus_signal']) if a['corpus_signal'] else '—'} |\n")
            f.write(f"| Grammar classes | {', '.join(a['grammar_classes']) if a['grammar_classes'] else '(no refs)'} |\n")
            f.write(f"| Tokens | {a['tokens']} |\n\n")
            f.write(f"{a['note']}\n\n")

print(f'Wrote {OUT_MD}', file=sys.stderr)

# ── 6. Print summary ─────────────────────────────────────────────────────

print(f'\nConflict Triage Summary:')
print(f'  Total conflicts: {len(analysis)}')
print(f'  HIGH priority: {priority_counts["HIGH"]} (Grammar confirms corpus)')
print(f'  GRAMMAR_CONFLICT: {priority_counts["GRAMMAR_CONFLICT"]} (both diverge from Whitney)')
print(f'  UNCERTAIN: {priority_counts["UNCERTAIN"]} (no Grammar class refs)')

if high_priority:
    print(f'\nTop HIGH priority (by frequency):')
    for a in high_priority[:10]:
        print(f"  {a['id']:3s} {a['root']:15s}: Whitney {a['whitney']} + corpus {a['corpus_signal']} ({a['tokens']:4d} tokens)")
