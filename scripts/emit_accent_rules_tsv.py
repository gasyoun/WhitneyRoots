"""Emit crosswalk/accent_rules.tsv from crosswalk/accent_rules.json.

The JSON is the hand-curated source of truth (one object per Whitney rule,
with citations, per-case encoding, and recorded interpretive decisions);
the TSV is a flat, spreadsheet-friendly view: one row per rule.

Usage:  python scripts/emit_accent_rules_tsv.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'crosswalk', 'accent_rules.json')
DST = os.path.join(ROOT, 'crosswalk', 'accent_rules.tsv')

COLS = [
    'rule_id', 'name', 'whitney', 'stem_classes', 'accent_position',
    'strong', 'middle', 'weakest', 'vocative', 'overrides', 'scheme',
    'examples', 'decision', 'rejected_alternative', 'exceptions',
]


def flat(v):
    """Render a JSON value as a single TSV-safe cell."""
    if v is None:
        return ''
    if isinstance(v, list):
        return ' | '.join(flat(x) for x in v)
    if isinstance(v, dict):
        return ' | '.join(f'{k}: {flat(x)}' for k, x in v.items())
    return str(v).replace('\t', ' ').replace('\n', ' ')


def main():
    with open(SRC, encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    for r in data['rules']:
        acc = r.get('accent', {})
        interp = r.get('interpretation') or {}
        overrides = dict(acc.get('overrides', {}))
        if r.get('condition'):
            overrides['condition'] = r['condition']
        rows.append({
            'rule_id': r['rule_id'],
            'name': r['name'],
            'whitney': flat(r['whitney']),
            'stem_classes': flat(r['applies_to'].get('stem_classes')),
            'accent_position': flat(r['applies_to'].get('accent_position')),
            'strong': flat(acc.get('strong')),
            'middle': flat(acc.get('middle')),
            'weakest': flat(acc.get('weakest')),
            'vocative': flat(acc.get('vocative')),
            'overrides': flat(overrides),
            'scheme': flat(r.get('scheme')),
            'examples': flat(r.get('examples')),
            'decision': flat(interp.get('decision')),
            'rejected_alternative': flat(interp.get('rejected_alternative')),
            'exceptions': flat(r.get('exceptions')),
        })

    with open(DST, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(COLS) + '\n')
        for row in rows:
            f.write('\t'.join(row[c] for c in COLS) + '\n')

    print(f'wrote {DST}: {len(rows)} rules')
    # sanity: no BOM
    with open(DST, 'rb') as f:
        head = f.read(3)
    assert head != b'\xef\xbb\xbf', 'BOM leaked into TSV'
    # sanity: rule ids unique and matrix references resolve
    ids = [r['rule_id'] for r in data['rules']]
    assert len(ids) == len(set(ids)), 'duplicate rule_id'
    for cell in data['matrix']:
        for rid in cell['rule_ids']:
            assert rid in ids, f'matrix cell {cell["cell"]} references unknown {rid}'
    print(f'sanity OK: {len(ids)} unique rules, '
          f'{len(data["matrix"])} matrix cells all resolve, '
          f'{len(data["lexical_exceptions"])} lexical-exception entries')


if __name__ == '__main__':
    main()
