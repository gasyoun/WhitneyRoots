"""
apply_ppp_corrections.py
========================
Apply high-confidence PPP corrections to app_data.json:

1. dā (entries 349, 350, 351): Replace "tta" → "dātta"
2. INVALID_MORPH forms: Remove impossible forms (vastave, saktave, etc.)

These are data quality fixes based on morphological validation.
"""

import sys, json, pathlib, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
WORKLIST = ROOT / 'Whitney_DCS_worklist.md'

# ── 1. Load app_data ──────────────────────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

# ── 2. Parse INVALID_MORPH entries from worklist ───────────────────────────
#       (need to extract which forms have morphological issues)

invalid_morph_patterns = {
    'vastave', 'saktave',  # ta+ve combinations (impossible)
    'ksaradhyai', 'stha',  # Other suspicious patterns
}

# Additional invalid patterns to detect
def is_invalid_morph(ppp_str):
    """Check if PPP form has invalid morphology."""
    forms = [f.strip() for f in ppp_str.split(',')]

    for form in forms:
        # Remove notes
        form = re.split(r'\s+[A-Z]\d\.\s*', form)[0]
        form = form.split('?')[0].strip()

        # Check for ta+ve (impossible)
        if form.endswith('ve') and 'ta' in form:
            return True, form, 'INVALID_MORPH_ve'

        # Check for ta+os (sandhi artifact)
        if form.endswith('os') and 'ta' in form and form.endswith('tos'):
            return True, form, 'SANDHI_tos'

        # Check for explicit patterns
        if form in invalid_morph_patterns:
            return True, form, 'KNOWN_INVALID'

    return False, None, None

# ── 3. Apply corrections ──────────────────────────────────────────────────

corrections_applied = []

for entry in app_data['lexicon']:
    eid = entry['id']
    root = entry['root']
    ppp_list = entry.get('ppp', [])

    if not ppp_list:
        continue

    new_ppp = []
    entry_changed = False

    for ppp_form in ppp_list:
        # Correction 1: dā entries (349, 350, 351)
        if eid in ['349', '350', '351'] and ppp_form == 'tta':
            new_ppp.append('dātta')
            corrections_applied.append({
                'id': eid,
                'root': root,
                'type': 'PARTIAL_STEM_FIX',
                'old': ppp_form,
                'new': 'dātta',
                'reason': 'Partial stem extraction error; should include root'
            })
            entry_changed = True

        # Correction 2: INVALID_MORPH forms
        else:
            is_invalid, invalid_form, invalid_type = is_invalid_morph(ppp_form)
            if is_invalid:
                corrections_applied.append({
                    'id': eid,
                    'root': root,
                    'type': f'INVALID_MORPH_{invalid_type}',
                    'old': ppp_form,
                    'new': '(removed)',
                    'reason': f'Invalid morphology: {invalid_type}'
                })
                entry_changed = True
                # Skip this form (remove it)
                continue

            new_ppp.append(ppp_form)

    if entry_changed:
        entry['ppp'] = new_ppp

# ── 4. Write updated app_data.json ───────────────────────────────────────

with open(APP_DATA, 'w', encoding='utf-8') as f:
    json.dump(app_data, f, ensure_ascii=False, indent=2)

print(f'Applied {len(corrections_applied)} PPP corrections:\n')

by_type = defaultdict(list)
for corr in corrections_applied:
    by_type[corr['type']].append(corr)

for corr_type in sorted(by_type.keys()):
    corrs = by_type[corr_type]
    print(f'\n{corr_type} ({len(corrs)} entries):')
    for corr in corrs:
        print(f"  [{corr['id']}] {corr['root']:20s}: {corr['old']:20s} → {corr['new']:20s}")
        print(f"       {corr['reason']}")

print(f'\n\nWrote {APP_DATA}')
print(f'Total corrections: {len(corrections_applied)}')

# ── 5. Summary ──────────────────────────────────────────────────────────

partial_stem = len([c for c in corrections_applied if c['type'] == 'PARTIAL_STEM_FIX'])
invalid_morph = len([c for c in corrections_applied if 'INVALID_MORPH' in c['type']])

print(f'\nSummary:')
print(f'  Partial stem fixes: {partial_stem} (dā entries)')
print(f'  Invalid morphology removals: {invalid_morph}')
print(f'  Total: {len(corrections_applied)}')
