"""
revert_collapse_additions.py
============================
Revert the unsound corpus-driven class additions, keeping the defensible ones.

REVERT (restore to pure Whitney Roots class set, baseline = commit 18b51b1):
  - 117 I/VI accent-collapse additions (corpus cannot distinguish I from VI)
  - 2 invalid 'IV|PASS' labels (script ambiguity marker leaked into `classes`)

KEEP (leave the addition in place, but record in review queue):
  - 12 "genuinely distinct class" additions (dā→III, du/dhi/hi→VII, vā→I, etc.)
  - 8 Section B additions (DCS-metadata method: jñā, bandh, dhṛ, kṣi, yam, krī, cit)

Only the `classes` field is touched for reverted entries; grammar_ref / ppp / etc. untouched.
Writes review_queue.json describing the 20 kept additions for the human reviewer.
"""
import json, subprocess, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
REVIEW_Q = ROOT / 'review_queue.json'

# Pure Whitney Roots baseline (grammar-citation commit; did not change classes)
raw = subprocess.run(['git', 'show', '18b51b1:src/app_data.json'],
                     cwd=str(ROOT), capture_output=True, encoding='utf-8')
base = json.loads(raw.stdout)
base_cls = {e['id']: list(e.get('classes', [])) for e in base['lexicon']}

curr = json.load(open(APP_DATA, encoding='utf-8'))

# Section B ids (DCS-metadata method) — keep, flag for review
SECTION_B_IDS = {'269', '494', '402', '141', '142', '600', '120', '227'}

reverted, kept = [], []

for e in curr['lexicon']:
    eid = e['id']; root = e['root']
    cnow = set(e.get('classes', []))
    cold = set(base_cls.get(eid, []))
    added = cnow - cold
    if not added:
        continue

    has_invalid = any('|' in c for c in cnow)            # 'IV|PASS'
    # I/VI accent-collapse: the unaccented corpus cannot tell class I from VI.
    # The collapse shows up either as a single {VI}/{I} added against the other,
    # OR as the *pair* {I, VI} added together from an empty Whitney baseline
    # (pṛṇ, mṛṇ, sphur) — the pair form was missed by the original single-class
    # patterns and left corpus-only classes live in app_data.json.
    is_iv_collapse = (
        (added == {'VI'} and 'I' in cold)
        or (added == {'I'} and 'VI' in cold)
        or ({'I', 'VI'} <= added)
    )

    if has_invalid or is_iv_collapse:
        # REVERT: restore Whitney Roots classes exactly
        e['classes'] = list(base_cls.get(eid, []))
        reverted.append({
            'id': eid, 'root': root,
            'reverted_from': sorted(cnow),
            'restored_to': base_cls.get(eid, []),
            'reason': 'invalid_label' if has_invalid else 'IV/VI accent-collapse (corpus cannot distinguish I from VI)',
        })
    else:
        # KEEP, but record provenance for the reviewer
        method = 'section-B (DCS metadata ∩ Grammar text)' if eid in SECTION_B_IDS \
                 else 'conflict pipeline (distinct class)'
        kept.append({
            'id': eid, 'root': root,
            'whitney_roots_classes': base_cls.get(eid, []),
            'current_classes': sorted(cnow),
            'added': sorted(added),
            'method': method,
            'status': 'PENDING_REVIEW',
            'check_against': 'Whitney Grammar §-chapter for the added class; then Zalizniak.',
        })

with open(APP_DATA, 'w', encoding='utf-8') as f:
    json.dump(curr, f, ensure_ascii=False, indent=2)

with open(REVIEW_Q, 'w', encoding='utf-8') as f:
    json.dump({'kept_pending_review': kept}, f, ensure_ascii=False, indent=2)

print(f'Reverted {len(reverted)} entries to pure Whitney Roots classes.')
print(f'Kept {len(kept)} entries (flagged PENDING_REVIEW in review_queue.json).')
print()
print('KEPT (need human + Zalizniak review):')
for k in sorted(kept, key=lambda x: int(x['id'])):
    wr = ','.join(k['whitney_roots_classes']) or '∅'
    print(f"   [{k['id']:>3}] {k['root']:10s} Whitney={wr:10s} +{','.join(k['added']):8s} ({k['method']})")

print()
print('Sanity: invalid labels remaining?')
bad = [(e['id'], e['root'], e['classes']) for e in curr['lexicon']
       if any('|' in c for c in e.get('classes', []))]
print('   ', bad if bad else 'none — clean.')
