"""
audit_class_changes.py
======================
Audit every `classes` change in src/app_data.json against a baseline git revision
(default = 18b51b1, the grammar-citation commit, which holds pure Whitney Roots classes).

Reports additions, removals, and any invalid (non I–X) class labels.
Use this after any class edit to confirm the data stays defensible.

  python scripts/dcs/audit_class_changes.py [baseline_rev]
"""
import json, subprocess, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]   # WhitneyRoots/
BASELINE = sys.argv[1] if len(sys.argv) > 1 else '18b51b1'
VALID = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'}

def load_rev(rev):
    r = subprocess.run(['git', 'show', f'{rev}:src/app_data.json'],
                       cwd=str(ROOT), capture_output=True, encoding='utf-8')
    if r.returncode != 0:
        sys.exit(f'git show {rev} failed: {r.stderr.strip()}')
    return json.loads(r.stdout)

base = load_rev(BASELINE)
curr = json.load(open(ROOT / 'src' / 'app_data.json', encoding='utf-8'))
base_cls = {e['id']: set(e.get('classes', [])) for e in base['lexicon']}

added = removed = invalid = 0
inv_list, rem_list = [], []
for e in curr['lexicon']:
    cnow = set(e.get('classes', []))
    cold = base_cls.get(e['id'], set())
    if cnow - cold:
        added += 1
    if cold - cnow:
        removed += 1
        rem_list.append((e['id'], e['root'], sorted(cold), sorted(cnow)))
    if cnow - VALID:
        invalid += 1
        inv_list.append((e['id'], e['root'], sorted(cnow - VALID)))

print(f'Baseline: {BASELINE}')
print(f'Entries with ADDED classes:   {added}')
print(f'Entries with REMOVED classes: {removed}')
print(f'Entries with INVALID labels:  {invalid}')
if inv_list:
    print('\nINVALID labels (data bug):')
    for eid, root, bad in inv_list:
        print(f'   [{eid}] {root}: {bad}')
if rem_list:
    print('\nREMOVALS (Whitney Roots classes should never be removed):')
    for eid, root, cold, cnow in rem_list:
        print(f'   [{eid}] {root}: {cold} -> {cnow}')
if not inv_list and not rem_list:
    print('\nClean: no invalid labels, no Whitney Roots classes removed.')
