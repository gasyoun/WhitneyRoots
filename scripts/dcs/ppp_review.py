"""
ppp_review.py
=============
Review Section C unattested PPP forms.

Note: PPP entries sometimes have issues:
  - Partial stems (e.g., "tta" instead of full form "dātta")
  - Impossible morphology (e.g., "vastave" = ta + ve, but ta is final)
  - Sandhi artifacts (e.g., "maditos" = ta + os, sandhi product)

Filter for morphologically plausible forms and check if they appear in corpus.

Output: ppp_analysis.md with categorized PPP cases
"""

import sys, json, pathlib, re, sqlite3
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
GRAMMAR_REFS = ROOT / 'src' / 'grammar_refs.json'
WORKLIST = ROOT / 'Whitney_DCS_worklist.md'
DCS_DB = ROOT.parent / 'VisualDCS' / 'src' / 'DCS-data-2026' / 'dcs_full.sqlite'
OUT_MD = ROOT / 'ppp_analysis.md'

# ── 1. Parse Section C from worklist ────────────────────────────────────

section_c = []  # list of (id, root, ppp_forms, tokens)

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
                    section_c.append({
                        'id': eid,
                        'root': root,
                        'ppp_forms': ppp_str,
                        'tokens': tokens,
                    })
                except (ValueError, IndexError):
                    pass

print(f'Loaded {len(section_c)} Section C PPP entries', file=sys.stderr)

# ── 2. Load app_data and grammar_refs ───────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

with open(GRAMMAR_REFS, encoding='utf-8') as f:
    gram_refs = json.load(f)

root_to_entry = {}
for entry in app_data['lexicon']:
    root = entry['root'].lstrip('0123456789 ').strip()
    root_to_entry[root] = entry

# ── 3. Classify PPP forms by morphological plausibility ─────────────────

def classify_ppp(ppp_str):
    """
    Classify PPP form as:
    - VALID: looks morphologically sound (full stem, no obvious sandhi)
    - PARTIAL: incomplete stem (e.g., "tta" instead of "dātta")
    - INVALID: morphologically impossible (e.g., "ta + ve", "ta + os")
    - UNCERTAIN: ambiguous
    """
    ppp_forms = [f.strip() for f in ppp_str.split(',')]
    results = []

    for form in ppp_forms:
        # Remove inline notes (e.g., "purta S1. purita" → keep both)
        # Split on common markers
        form = re.split(r'\s+[A-Z]\d\.\s*', form)[0]  # Remove "S1. " style notes
        form = form.split('?')[0].strip()  # Remove uncertain marker

        # Check for obvious issues
        if len(form) <= 2:
            # Very short (probably partial)
            results.append(('PARTIAL', form))
        elif form.endswith('ve') and 'ta' in form:
            # ta + ve = impossible
            results.append(('INVALID', form))
        elif form.endswith(('os', 'iḥ')) and form.endswith('tos'):
            # Sandhi artifact (e.g., tos = ta + os)
            results.append(('INVALID', form))
        elif form.endswith('ta') or form.endswith('na'):
            # Standard -ta or -na PPP ending
            results.append(('VALID', form))
        else:
            results.append(('UNCERTAIN', form))

    return results

# ── 4. Check corpus for PPP forms ──────────────────────────────────────────

con = sqlite3.connect(str(DCS_DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

# Get all forms in corpus
cur.execute("SELECT DISTINCT form FROM token")
corpus_forms = {row[0] for row in cur.fetchall()}
con.close()

print(f'Loaded {len(corpus_forms)} unique corpus forms', file=sys.stderr)

# ── 5. Analyze each PPP entry ──────────────────────────────────────────────

analysis = []

for ppp_entry in section_c:
    eid = ppp_entry['id']
    root = ppp_entry['root']
    ppp_str = ppp_entry['ppp_forms']
    tokens = ppp_entry['tokens']

    entry = root_to_entry.get(root.lstrip('0123456789 ').strip())
    if not entry:
        continue

    # Classify forms
    ppp_classifications = classify_ppp(ppp_str)

    # Check corpus
    attested_forms = []
    unattested_forms = []

    for ppp_class, form in ppp_classifications:
        if form in corpus_forms:
            attested_forms.append((ppp_class, form))
        else:
            unattested_forms.append((ppp_class, form))

    # Determine overall status
    if attested_forms and not unattested_forms:
        status = 'ATTESTED'
    elif attested_forms and unattested_forms:
        status = 'PARTIAL'
    else:
        # All unattested; classify by type
        invalid_count = sum(1 for c, _ in unattested_forms if c == 'INVALID')
        partial_count = sum(1 for c, _ in unattested_forms if c == 'PARTIAL')
        valid_count = sum(1 for c, _ in unattested_forms if c == 'VALID')

        if invalid_count == len(unattested_forms):
            status = 'INVALID_FORMS'
        elif partial_count == len(unattested_forms):
            status = 'PARTIAL_FORMS'
        elif valid_count > 0:
            status = 'UNATTESTED_VALID'
        else:
            status = 'UNATTESTED_UNCERTAIN'

    analysis.append({
        'id': eid,
        'root': root,
        'ppp_str': ppp_str,
        'tokens': tokens,
        'ppp_classifications': ppp_classifications,
        'attested': attested_forms,
        'unattested': unattested_forms,
        'status': status,
    })

# ── 6. Sort by status and frequency ──────────────────────────────────────

status_order = {'ATTESTED': 0, 'PARTIAL': 1, 'UNATTESTED_VALID': 2,
                'UNATTESTED_UNCERTAIN': 3, 'PARTIAL_FORMS': 4, 'INVALID_FORMS': 5}
analysis.sort(key=lambda x: (status_order.get(x['status'], 99), -x['tokens']))

# ── 7. Write output ──────────────────────────────────────────────────────

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('# PPP Analysis (Section C)\n\n')
    f.write('_Unattested PPP forms from Whitney Roots._\n\n')

    status_counts = defaultdict(int)
    for a in analysis:
        status_counts[a['status']] += 1

    f.write('## Summary by Status\n\n')
    for status in ['ATTESTED', 'PARTIAL', 'UNATTESTED_VALID', 'UNATTESTED_UNCERTAIN', 'PARTIAL_FORMS', 'INVALID_FORMS']:
        count = status_counts[status]
        if count > 0:
            f.write(f'- **{status}**: {count}\n')
    f.write(f'\n')

    # Show UNATTESTED_VALID (high priority for investigation)
    unatt_valid = [a for a in analysis if a['status'] == 'UNATTESTED_VALID']
    if unatt_valid:
        f.write(f'## UNATTESTED_VALID ({len(unatt_valid)})\n\n')
        f.write('Valid PPP forms that appear nowhere in corpus. High frequency cases are priorities.\n\n')

        for a in unatt_valid[:30]:
            f.write(f"### [{a['id']}] {a['root']}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| PPP forms listed | {a['ppp_str']} |\n")
            f.write(f"| Tokens (root) | {a['tokens']} |\n")

            if a['attested']:
                f.write(f"| Attested | {', '.join([f'{f} ({c})' for c, f in a['attested']])} |\n")
            if a['unattested']:
                f.write(f"| Unattested (valid) | {', '.join([f'{f} ({c})' for c, f in a['unattested']])} |\n")
            f.write(f"\n")

print(f'Wrote {OUT_MD}', file=sys.stderr)

# ── 8. Summary ──────────────────────────────────────────────────────────

print(f'\nPPP Analysis Summary:')
for status, count in sorted(status_counts.items()):
    print(f'  {status:25s}: {count:3d}')
