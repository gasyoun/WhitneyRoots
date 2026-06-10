"""
ppp_source_validation.py
=========================
Validate whether unattested PPP forms represent genuine corpus gaps or source data errors.

Strategy:
  1. For suspect morphology (PARTIAL, INVALID_ve, SANDHI): flag as probable errors
  2. For clean forms on high-frequency roots: check if it's likely a real gap or error
     - If root has 1000+ tokens but PPP never appears: likely error or very rare
     - If root has <100 tokens: PPP gap is plausible (low frequency)
  3. For each high-frequency root: suggest validation or correction needed

Output: ppp_source_validation.md with action recommendations
"""

import sys, json, pathlib, re, sqlite3
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
WORKLIST = ROOT / 'Whitney_DCS_worklist.md'
DCS_DB = ROOT.parent / 'VisualDCS' / 'src' / 'DCS-data-2026' / 'dcs_full.sqlite'
OUT_MD = ROOT / 'ppp_source_validation.md'

# ── 1. Load corpus to check for related forms ──────────────────────────────

con = sqlite3.connect(str(DCS_DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute("SELECT DISTINCT form FROM token")
corpus_forms = {row[0] for row in cur.fetchall()}

# Also get lemma forms to check if root appears
cur.execute("SELECT DISTINCT lemma FROM token")
corpus_lemmas = {row[0] for row in cur.fetchall()}

con.close()

print(f'Loaded {len(corpus_forms)} unique corpus forms', file=sys.stderr)
print(f'Loaded {len(corpus_lemmas)} unique corpus lemmas', file=sys.stderr)

# ── 2. Parse Section C with morphological classification ──────────────────

def classify_ppp_detailed(ppp_str):
    """Detailed PPP classification with error likelihood."""
    ppp_forms = [f.strip() for f in ppp_str.split(',')]
    results = []

    for form in ppp_forms:
        original = form
        form = re.split(r'\s+[A-Z]\d\.\s*', form)[0]
        form = form.split('?')[0].strip()

        # Classify
        classification = 'CLEAN'
        error_likelihood = 0.1  # Base: 10% chance of error

        if len(form) <= 2:
            classification = 'PARTIAL'
            error_likelihood = 0.95  # 95% likely error
        elif form.endswith('ve') and 'ta' in form:
            classification = 'INVALID_MORPH'
            error_likelihood = 0.95
        elif form.endswith(('os', 'iḥ')) and 'ta' in form:
            classification = 'SANDHI_ARTIFACT'
            error_likelihood = 0.85
        elif not form.endswith(('ta', 'na')):
            if 'samskṛta' not in form and 'samskṛt' not in form:
                classification = 'UNCERTAIN_ENDING'
                error_likelihood = 0.50

        results.append({
            'form': form,
            'original': original,
            'classification': classification,
            'error_likelihood': error_likelihood,
        })

    return results

ppp_entries = []  # (root, id, ppp_str, tokens, classifications)

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
                    classifications = classify_ppp_detailed(ppp_str)

                    ppp_entries.append({
                        'id': eid,
                        'root': root,
                        'root_bare': root_bare,
                        'ppp_str': ppp_str,
                        'tokens': tokens,
                        'classifications': classifications,
                    })
                except (ValueError, IndexError):
                    pass

print(f'Loaded {len(ppp_entries)} PPP entries', file=sys.stderr)

# ── 3. Validate each PPP entry ─────────────────────────────────────────────

validations = []  # (root, id, tokens, ppp_form, validation_verdict, reasoning)

for entry in ppp_entries:
    root_bare = entry['root_bare']
    tokens = entry['tokens']

    for ppp_class in entry['classifications']:
        form = ppp_class['form']
        classification = ppp_class['classification']
        error_likelihood = ppp_class['error_likelihood']

        # Check if form exists in corpus
        exists_in_corpus = form in corpus_forms

        if exists_in_corpus:
            verdict = 'ATTESTED'
            reasoning = f'PPP form found in corpus'
        elif classification != 'CLEAN':
            verdict = 'LIKELY_ERROR'
            reasoning = f'Morphologically suspect ({classification}). Likely source data error.'
        elif tokens >= 1000:
            # High-frequency root with missing PPP
            verdict = 'SUSPICIOUS'
            reasoning = f'Root appears {tokens}+ times but PPP "{form}" never attested. Either: (1) very rare/poetic form, (2) source data error, or (3) sandhi variation hides form.'
        elif tokens >= 100:
            verdict = 'UNCERTAIN'
            reasoning = f'Root appears {tokens}+ times. PPP might be rare or error. Needs review.'
        else:
            verdict = 'PLAUSIBLE_GAP'
            reasoning = f'Low-frequency root ({tokens} tokens). PPP absence may be plausible but worth checking.'

        validations.append({
            'root': entry['root'],
            'root_bare': root_bare,
            'id': entry['id'],
            'tokens': tokens,
            'ppp_form': form,
            'ppp_str': entry['ppp_str'],
            'classification': classification,
            'verdict': verdict,
            'reasoning': reasoning,
            'error_likelihood': error_likelihood,
        })

# ── 4. Sort by priority: LIKELY_ERROR > SUSPICIOUS > high frequency ────────

verdict_order = {'LIKELY_ERROR': 0, 'SUSPICIOUS': 1, 'UNCERTAIN': 2, 'PLAUSIBLE_GAP': 3, 'ATTESTED': 4}
validations.sort(key=lambda x: (verdict_order.get(x['verdict'], 99), -x['tokens'], x['root_bare']))

# ── 5. Write output ───────────────────────────────────────────────────────

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('# PPP Source Validation\n\n')
    f.write('_Assess whether unattested PPP forms are genuine corpus gaps or source data errors._\n\n')

    verdict_counts = defaultdict(int)
    for v in validations:
        verdict_counts[v['verdict']] += 1

    f.write('## Summary by Verdict\n\n')
    for verdict in ['ATTESTED', 'LIKELY_ERROR', 'SUSPICIOUS', 'UNCERTAIN', 'PLAUSIBLE_GAP']:
        count = verdict_counts[verdict]
        if count > 0:
            f.write(f'- **{verdict}**: {count}\n')
    f.write('\n')

    # LIKELY_ERROR (highest priority for correction)
    likely_errors = [v for v in validations if v['verdict'] == 'LIKELY_ERROR']
    if likely_errors:
        f.write(f'## LIKELY_ERROR ({len(likely_errors)})\n\n')
        f.write('Morphologically suspect forms. Recommend removing or correcting in source.\n\n')

        for v in likely_errors[:30]:
            f.write(f"### [{v['id']}] {v['root']:20s}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Root frequency | {v['tokens']} tokens |\n")
            f.write(f"| PPP forms listed | {v['ppp_str']} |\n")
            f.write(f"| Suspect form | {v['ppp_form']} ({v['classification']}) |\n")
            f.write(f"| Error likelihood | {int(v['error_likelihood']*100)}% |\n\n")
            f.write(f"{v['reasoning']}\n\n")

    # SUSPICIOUS (high-frequency roots with missing PPP)
    suspicious = [v for v in validations if v['verdict'] == 'SUSPICIOUS']
    if suspicious:
        f.write(f'## SUSPICIOUS ({len(suspicious)})\n\n')
        f.write('High-frequency roots with unattested PPP forms. Check if entries are correct.\n\n')

        for v in suspicious[:30]:
            f.write(f"### [{v['id']}] {v['root']:20s}\n\n")
            f.write(f"| Field | Value |\n")
            f.write(f"|-------|-------|\n")
            f.write(f"| Root frequency | {v['tokens']} tokens |\n")
            f.write(f"| PPP forms listed | {v['ppp_str']} |\n")
            f.write(f"| Unattested form | {v['ppp_form']} |\n")
            f.write(f"| Morphology | {v['classification']} |\n\n")
            f.write(f"{v['reasoning']}\n\n")

print(f'Wrote {OUT_MD}', file=sys.stderr)

# ── 6. Summary stats ───────────────────────────────────────────────────────

print(f'\nPPP Source Validation Summary:')
for verdict in ['ATTESTED', 'LIKELY_ERROR', 'SUSPICIOUS', 'UNCERTAIN', 'PLAUSIBLE_GAP']:
    count = verdict_counts[verdict]
    if count > 0:
        print(f'  {verdict:20s}: {count:3d}')

# Show top suspects
print(f'\nTop 10 HIGH-FREQUENCY suspicious forms:')
for v in suspicious[:10]:
    print(f"  {v['id']:3s} {v['root']:20s}: {v['ppp_form']:15s} ({v['tokens']:5d} tokens)")
