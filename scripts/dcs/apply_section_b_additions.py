"""
apply_section_b_additions.py
============================
Apply Section B ADD recommendations to app_data.json.

Strategy:
  For each ADD case: add the DCS class to Whitney classes without removing existing.
  (If Whitney has [I, IX] and DCS suggests IV, result is [I, IV, IX].)

Input: detailed_b_analysis.md (generated from section_b_resolver.py)
Output: updated app_data.json

Before writing, print a summary of changes for user review.
"""

# H2892 — refuse-by-default writer lock over the human-reviewed overlays.
# Must stay the first executable statement: nothing below it may open a
# reviewed file. Set ALLOW_OVERLAY_WIPE=1 only for a deliberate, re-pinned
# rewrite (scripts/overlay_guard.py).
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
from overlay_guard import refuse_unless_hatched as _refuse_unless_hatched
_refuse_unless_hatched(__file__, targets=('src/app_data.json',))

import sys, json, pathlib, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]  # WhitneyRoots/
APP_DATA    = ROOT / 'src' / 'app_data.json'
ANALYSIS_MD = ROOT / 'detailed_b_analysis.md'

# Roman numeral ordering for sorting
ROMAN_ORDER = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
               'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}

# ── 1. Parse ADD recommendations from detailed_b_analysis.md ────────────

additions = {}  # id → dcs_class_to_add

with open(ANALYSIS_MD, encoding='utf-8') as f:
    in_add_section = False
    current_id = None
    current_root = None
    for line in f:
        if '## ADD (' in line:
            in_add_section = True
            continue
        if in_add_section and line.startswith('## NO_CHANGE'):
            break
        if in_add_section and line.startswith('### ['):
            # Extract id and root
            match = re.match(r'### \[(\d+)\] (.+)', line)
            if match:
                current_id = match.group(1)
                current_root = match.group(2).strip()
        if in_add_section and '| DCS in Grammar |' in line:
            # Extract the class to add
            match = re.search(r'\| DCS in Grammar \| (.+) \|', line)
            if match:
                dcs_class = match.group(1).strip()
                if dcs_class and dcs_class != '(no match)':
                    additions[current_id] = {
                        'root': current_root,
                        'class_to_add': dcs_class
                    }

print(f'Found {len(additions)} ADD recommendations:', file=sys.stderr)
for eid, info in sorted(additions.items()):
    print(f"  [{eid}] {info['root']}: add {info['class_to_add']}", file=sys.stderr)

# ── 2. Load app_data.json ──────────────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

# ── 3. Apply additions ─────────────────────────────────────────────────

changes = []  # List of (id, root, old_classes, new_classes)

for entry in app_data['lexicon']:
    eid = entry['id']
    if eid not in additions:
        continue

    info = additions[eid]
    class_to_add = info['class_to_add']

    old_classes = entry.get('classes', [])
    new_classes = list(set(old_classes) | {class_to_add})
    new_classes.sort(key=lambda x: ROMAN_ORDER.get(x, 999))

    entry['classes'] = new_classes
    changes.append({
        'id': eid,
        'root': entry['root'],
        'old': old_classes,
        'new': new_classes
    })

# ── 4. Print summary of changes for review ─────────────────────────────

print(f'\nChanges to apply ({len(changes)} entries):')
print()
for change in changes:
    old_str = ', '.join(change['old'])
    new_str = ', '.join(change['new'])
    print(f"  [{change['id']}] {change['root']:20s} | {old_str:15s} → {new_str}")

# ── 5. Write updated app_data.json ─────────────────────────────────────

with open(APP_DATA, 'w', encoding='utf-8') as f:
    json.dump(app_data, f, ensure_ascii=False, indent=2)

print(f'\nWrote {APP_DATA}', file=sys.stderr)

# ── 6. Summary ─────────────────────────────────────────────────────────

print(f'\nSummary:')
print(f'  Total entries modified: {len(changes)}')
print(f'  Total entries in lexicon: {len(app_data["lexicon"])}')
