"""
section_b_resolver.py
======================
Process Section B conflicts: use Grammar citations to decide whether to
add DCS classes without removing Whitney classes.

Strategy: For each Section B conflict, check if Grammar has a class-chapter
citation matching the DCS class. If yes, flag for addition (with user review).
If no, leave unchanged (Whitney is authority, but we note the discrepancy).

Output: detailed_b_analysis.md with one entry per conflict, showing:
  - Root / ids
  - Whitney classes (current)
  - DCS class (proposed)
  - Grammar citations for all classes
  - Recommendation: ADD or NO_CHANGE
  - Reasoning
"""

import sys, json, pathlib
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]  # WhitneyRoots/
APP_DATA    = ROOT / 'src' / 'app_data.json'
GRAMMAR_REFS = ROOT / 'src' / 'grammar_refs.json'
WORKLIST    = ROOT / 'Whitney_DCS_worklist.md'
OUT_MD      = ROOT / 'detailed_b_analysis.md'

# ── Roman numeral conversion ────────────────────────────────────────────
NUM_TO_ROMAN = {
    '1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V',
    '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X'
}

def normalize_class(class_str):
    """Convert class number to Roman numeral (1→I, 4→IV, etc.)"""
    s = class_str.strip()
    if s in NUM_TO_ROMAN:
        return NUM_TO_ROMAN[s]
    return s  # Already Roman or unknown

# ── 1. Parse Section B from worklist ────────────────────────────────────

section_b = []  # list of (id, root, whitney, dcs, corpus_signal, tokens)

with open(WORKLIST, encoding='utf-8') as f:
    in_section_b = False
    for line in f:
        if '## B. Other class conflicts' in line:
            in_section_b = True
            continue
        if in_section_b and line.startswith('## C.'):
            break
        if in_section_b and line.startswith('|') and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6 and parts[1] and parts[1].isdigit():
                try:
                    eid = parts[1]
                    root = parts[2]
                    whitney = parts[3]
                    dcs = parts[4]
                    corpus = parts[5]
                    tokens = int(parts[6]) if len(parts) > 6 else 0
                    section_b.append({
                        'id': eid,
                        'root': root,
                        'whitney': whitney,
                        'dcs': dcs,
                        'corpus': corpus,
                        'tokens': tokens,
                    })
                except (ValueError, IndexError):
                    pass

print(f'Loaded {len(section_b)} Section B conflicts', file=sys.stderr)

# ── 2. Load app_data and grammar_refs ───────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

with open(GRAMMAR_REFS, encoding='utf-8') as f:
    gram_refs = json.load(f)

# Build lookup tables
root_to_entry = {}  # root_bare → entry
for entry in app_data['lexicon']:
    eid = entry['id']
    root = entry['root'].lstrip('0123456789 ').strip()
    root_to_entry[root] = entry

# ── 3. For each Section B conflict, analyze Grammar support ──────────────

analysis = []

for conflict in section_b:
    eid = conflict['id']
    root = conflict['root']
    whitney_str = conflict['whitney']
    dcs_str = conflict['dcs']

    # Parse classes (normalize DCS to Roman numerals)
    whitney_classes = set(c.strip() for c in whitney_str.split(',') if c.strip())
    dcs_classes = set(normalize_class(c.strip()) for c in dcs_str.split(',') if c.strip())

    # Look up entry (try exact match first, then with numbers stripped)
    entry = root_to_entry.get(root)
    if not entry:
        # Try stripping any number prefix (e.g., "1 akṣ" → "akṣ")
        root_bare = root.lstrip('0123456789 ').strip()
        entry = root_to_entry.get(root_bare)

    if not entry:
        analysis.append({
            'id': eid,
            'root': root,
            'status': 'NOT_FOUND',
            'whitney_classes': sorted(whitney_classes),
            'dcs_classes': sorted(dcs_classes),
            'grammar_classes': [],
            'dcs_in_grammar': [],
            'tokens': conflict['tokens'],
            'corpus_signal': conflict['corpus'],
            'grammar_refs_count': 0,
            'recommendation': 'ERROR',
            'note': 'Root not found in app_data.json'
        })
        continue

    # Get grammar refs for this root
    gram_for_root = gram_refs.get(eid, {})
    gram_refs_list = gram_for_root.get('grammar_refs', [])

    # Extract class-chapter refs
    class_chapters_in_grammar = set()
    for ref in gram_refs_list:
        if ref.get('class_chapter'):
            gana = ref['class_chapter']
            class_chapters_in_grammar.add(str(gana))

    # Check if DCS classes appear in Grammar
    dcs_in_grammar = dcs_classes & class_chapters_in_grammar

    # Recommendation logic
    if dcs_in_grammar:
        recommendation = 'ADD'
        reasoning = f"Grammar cites class(es) {sorted(dcs_in_grammar)} matching DCS. "
        reasoning += "Add to Whitney classes without removing existing."
    elif not class_chapters_in_grammar:
        recommendation = 'GRAMMAR_UNCLEAR'
        reasoning = "No class-chapter citations in Grammar for this root. Cannot decide."
    else:
        recommendation = 'NO_CHANGE'
        reasoning = f"Grammar cites {sorted(class_chapters_in_grammar)} only. "
        reasoning += "DCS class not in Grammar. Whitney is authority; leave unchanged."

    analysis.append({
        'id': eid,
        'root': root,
        'status': 'OK',
        'whitney_classes': sorted(whitney_classes),
        'dcs_classes': sorted(dcs_classes),
        'grammar_classes': sorted(class_chapters_in_grammar),
        'dcs_in_grammar': sorted(dcs_in_grammar),
        'tokens': conflict['tokens'],
        'corpus_signal': conflict['corpus'],
        'grammar_refs_count': len(gram_refs_list),
        'recommendation': recommendation,
        'note': reasoning,
    })

# ── 4. Sort by recommendation priority (ADD > GRAMMAR_UNCLEAR > NO_CHANGE) ──
recommendation_order = {'ADD': 0, 'GRAMMAR_UNCLEAR': 1, 'NO_CHANGE': 2, 'ERROR': 3}
analysis.sort(key=lambda x: (recommendation_order.get(x['recommendation'], 99), -x.get('tokens', 0)))

# ── 5. Write output markdown ────────────────────────────────────────────

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('# Section B Detailed Analysis\n\n')
    f.write('_Use Grammar citations to decide whether to add DCS classes._\n\n')
    f.write(f'**Total:** {len(analysis)} conflicts analyzed.\n\n')

    # Summary by recommendation
    rec_counts = defaultdict(int)
    for a in analysis:
        rec_counts[a['recommendation']] += 1

    f.write('## Summary by Recommendation\n\n')
    for rec in ['ADD', 'GRAMMAR_UNCLEAR', 'NO_CHANGE', 'ERROR']:
        count = rec_counts[rec]
        if count > 0:
            f.write(f'- **{rec}**: {count}\n')
    f.write('\n')

    # Detailed entries grouped by recommendation
    for rec_type in ['ADD', 'GRAMMAR_UNCLEAR', 'NO_CHANGE', 'ERROR']:
        entries = [a for a in analysis if a['recommendation'] == rec_type]
        if not entries:
            continue

        f.write(f'## {rec_type} ({len(entries)})\n\n')

        for a in entries:
            f.write(f"### [{a['id']}] {a['root']}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Whitney classes | {', '.join(a['whitney_classes'])} |\n")
            f.write(f"| DCS classes | {', '.join(a['dcs_classes'])} |\n")
            f.write(f"| Grammar classes | {', '.join(a['grammar_classes']) if a['grammar_classes'] else '(none)'} |\n")
            f.write(f"| DCS in Grammar | {', '.join(a['dcs_in_grammar']) if a['dcs_in_grammar'] else '(no match)'} |\n")
            f.write(f"| Corpus signal | {a.get('corpus_signal', '?')} |\n")
            f.write(f"| Tokens | {a.get('tokens', 0)} |\n")
            f.write(f"| Grammar refs | {a['grammar_refs_count']} |\n\n")
            f.write(f"**Recommendation:** {a['recommendation']}\n\n")
            f.write(f"{a['note']}\n\n")

print(f'Wrote {OUT_MD}', file=sys.stderr)

# ── 6. Summary stats ─────────────────────────────────────────────────────

adds = [a for a in analysis if a['recommendation'] == 'ADD']
high_freq_adds = [a for a in adds if a.get('tokens', 0) >= 100]

print(f'\nSection B Analysis Summary:')
print(f'  Total conflicts: {len(analysis)}')
print(f'  ADD (Grammar supports DCS): {len(adds)}')
print(f'    High-frequency (≥100 tokens): {len(high_freq_adds)}')
print(f'  GRAMMAR_UNCLEAR: {rec_counts["GRAMMAR_UNCLEAR"]}')
print(f'  NO_CHANGE (Whitney only): {rec_counts["NO_CHANGE"]}')
print(f'  ERROR: {rec_counts["ERROR"]}')

if high_freq_adds:
    print(f'\nHigh-frequency ADD candidates:')
    for a in high_freq_adds[:10]:
        print(f"  {a['id']:3s} {a['root']:15s}: Whitney {a['whitney_classes']} + DCS {a['dcs_classes']} "
              f"({a['tokens']} tokens)")
