"""
ppp_priority.py
===============
Generate a prioritized review list for 109 UNATTESTED_VALID PPP forms.

Strategy:
  1. Group by root
  2. Sort by root frequency (token count descending)
  3. Show which PPP forms are unattested for each root
  4. Flag for potential errors (partial stems, morphological issues)

Output: ppp_priority_review.md for manual examination
"""

import sys, json, pathlib, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
GRAMMAR_REFS = ROOT / 'src' / 'grammar_refs.json'
WORKLIST = ROOT / 'Whitney_DCS_worklist.md'
OUT_MD = ROOT / 'ppp_priority_review.md'

# ── 1. Load app_data ──────────────────────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

root_to_entry = {}
for entry in app_data['lexicon']:
    root = entry['root'].lstrip('0123456789 ').strip()
    if root not in root_to_entry:
        root_to_entry[root] = []
    root_to_entry[root].append(entry)

# ── 2. Parse Section C and classify PPP forms ──────────────────────────────

def classify_ppp(ppp_str):
    """Classify PPP form for red flags."""
    ppp_forms = [f.strip() for f in ppp_str.split(',')]
    results = []

    for form in ppp_forms:
        form = re.split(r'\s+[A-Z]\d\.\s*', form)[0]
        form = form.split('?')[0].strip()

        flags = []
        if len(form) <= 2:
            flags.append('PARTIAL')
        if form.endswith('ve') and 'ta' in form:
            flags.append('INVALID_ve')
        if form.endswith(('os', 'iḥ')) and 'ta' in form and form.endswith(('tos', 'tiḥ')):
            flags.append('SANDHI')
        if not form.endswith(('ta', 'na')):
            if not any('|' in form or '?' in form for c in form):
                flags.append('UNCERTAIN_ENDING')

        results.append({
            'form': form,
            'flags': flags,
            'is_suspect': len(flags) > 0
        })

    return results

ppp_section = defaultdict(list)  # root → list of (id, ppp_str, tokens, classifications)

with open(WORKLIST, encoding='utf-8') as f:
    in_section_c = False
    for line in f:
        if '## C. Whitney PPP' in line:
            in_section_c = True
            continue
        if in_section_c and line.startswith('## '):
            break
        if in_section_c and line.startswith('|') and '---' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4 and parts[1] and parts[1].isdigit():
                try:
                    eid = parts[1]
                    root = parts[2]
                    ppp_str = parts[3]
                    tokens = int(parts[4]) if len(parts) > 4 else 0

                    root_bare = root.lstrip('0123456789 ').strip()
                    classifications = classify_ppp(ppp_str)

                    ppp_section[root_bare].append({
                        'id': eid,
                        'root_raw': root,
                        'ppp_str': ppp_str,
                        'tokens': tokens,
                        'classifications': classifications
                    })
                except (ValueError, IndexError):
                    pass

# ── 3. Build review data by root frequency ────────────────────────────────

review_items = []

for root_bare, entries in ppp_section.items():
    # Get total tokens for this root
    entries = sorted(entries, key=lambda x: -x['tokens'])
    total_tokens = entries[0]['tokens']  # Same for all variants

    # Collect unattested valid forms (from last phase)
    for entry in entries:
        ppp_str = entry['ppp_str']
        classifications = entry['classifications']

        # Identify unattested forms (we'll cross-ref with grammar later)
        for ppp_class in classifications:
            form = ppp_class['form']
            is_suspect = ppp_class['is_suspect']

            review_items.append({
                'root': root_bare,
                'root_raw': entry['root_raw'],
                'id': entry['id'],
                'ppp_form': form,
                'ppp_str': ppp_str,
                'tokens': total_tokens,
                'flags': ppp_class['flags'],
                'is_suspect': is_suspect,
            })

# ── 4. Sort by token count (descending) ────────────────────────────────────

review_items.sort(key=lambda x: (-x['tokens'], x['root']))

# ── 5. Write output ───────────────────────────────────────────────────────

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('# PPP Priority Review\n\n')
    f.write('_Unattested PPP forms prioritized by root frequency (highest first)._\n\n')

    # Group by token bucket
    by_frequency = defaultdict(list)
    for item in review_items:
        if item['tokens'] >= 10000:
            bucket = '10K+'
        elif item['tokens'] >= 1000:
            bucket = '1K-10K'
        elif item['tokens'] >= 100:
            bucket = '100-1K'
        else:
            bucket = '<100'
        by_frequency[bucket].append(item)

    for bucket in ['10K+', '1K-10K', '100-1K', '<100']:
        items = by_frequency[bucket]
        if not items:
            continue

        f.write(f'## {bucket} tokens ({len(items)} PPP forms)\n\n')

        for item in items:
            flags_str = ', '.join(item['flags']) if item['flags'] else 'clean'
            flag_marker = '⚠️' if item['is_suspect'] else '✓'

            f.write(f"### [{item['id']}] {item['root_raw']:20s}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Root frequency | {item['tokens']} tokens |\n")
            f.write(f"| PPP forms listed | {item['ppp_str']} |\n")
            f.write(f"| Unattested form | {item['ppp_form']} |\n")
            f.write(f"| Morphology | {flags_str} {flag_marker} |\n\n")

print(f'Wrote {OUT_MD}', file=sys.stderr)

# ── 6. Summary ────────────────────────────────────────────────────────────

total = len(review_items)
suspect_count = sum(1 for item in review_items if item['is_suspect'])
clean_count = total - suspect_count

print(f'\nPPP Priority Review Summary:')
print(f'  Total unattested PPP forms: {total}')
print(f'  Suspect forms (morphological flags): {suspect_count}')
print(f'  Clean forms (standard morphology): {clean_count}')
print(f'\n  10K+ tokens: {len(by_frequency["10K+"])}')
print(f'  1K-10K tokens: {len(by_frequency["1K-10K"])}')
print(f'  100-1K tokens: {len(by_frequency["100-1K"])}')
print(f'  <100 tokens: {len(by_frequency["<100"])}')

# Top 10 by frequency
print(f'\nTop 10 high-frequency unattested PPP forms:')
for item in review_items[:10]:
    flags_str = f" [{', '.join(item['flags'])}]" if item['flags'] else ""
    print(f"  {item['root']:15s}: {item['ppp_form']:15s} ({item['tokens']:5d} tokens){flags_str}")
