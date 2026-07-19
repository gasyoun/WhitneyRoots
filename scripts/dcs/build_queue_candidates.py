"""
build_queue_candidates.py
==========================
H975 (Uprava handoff) -- produce-not-decide candidate pre-fill for the five
human-adjudication queues A-E described in `.ai_state.md` / `REVIEWER_GUIDE.md`.

READ-ONLY. This script never writes to `src/app_data.json`, `review_queue.json`,
or any other file a human may already have reviewed. It only *reads* existing
live data + existing analysis artifacts and emits fresh candidate JSON (decision
cells always null/PENDING_REVIEW) under `docs/queue_candidates/`.

Deliberately does NOT call `scripts/dcs/revert_collapse_additions.py` -- that
script WRITES `src/app_data.json` + `review_queue.json` unconditionally and is
exactly the "seeder that can wipe human-reviewed overlays" the H975 handoff
guardrail warns about. Queue E below reproduces its read-only diff logic only
(no write path copied), against a git blob, not the working tree.

Usage:  python scripts/dcs/build_queue_candidates.py
Output: docs/queue_candidates/queue_{a,b,c,d,e}.json
"""
import sys, json, re, pathlib, subprocess, sqlite3
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / 'docs' / 'queue_candidates'
OUT_DIR.mkdir(parents=True, exist_ok=True)

GENERATED_BY = 'Sonnet 5 (claude-sonnet-5), H975'
GENERATED_ON = '19-07-2026'

def write_queue(letter, source, items, extra=None):
    payload = {
        'queue': letter,
        'generated': GENERATED_ON,
        'generated_by': GENERATED_BY,
        'source': source,
        'produce_not_decide': True,
        'note': 'Candidate pre-fill only. No item below has been adjudicated; '
                'decision/verdict fields are intentionally null for a human '
                '(then Zalizniak as tiebreaker) to fill in.',
        'count': len(items),
        'items': items,
    }
    if extra:
        payload.update(extra)
    out = OUT_DIR / f'queue_{letter.lower()}.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f'  queue {letter}: {len(items)} candidates -> {out.relative_to(ROOT)}')
    return out


# -- Queue A -- kept class additions (review_queue.json + DECISIONS_NEEDED.md S1) --

def build_queue_a():
    rq = json.load(open(ROOT / 'review_queue.json', encoding='utf-8'))
    kept = {e['id']: e for e in rq['kept_pending_review']}

    dn_text = (ROOT / 'docs' / 'DECISIONS_NEEDED.md').read_text(encoding='utf-8')
    m = re.search(r'## 1\. Queue A.*?\n\n(\|.*?)\n\n---', dn_text, re.S)
    evidence = {}
    if m:
        for line in m.group(1).splitlines():
            if not line.startswith('|') or line.startswith('|--'):
                continue
            cols = [c.strip() for c in line.strip('|').split('|')]
            if len(cols) >= 7 and cols[0].strip('*').isdigit():
                eid = cols[0].strip('*')
                evidence[eid] = {
                    'whitney_classes_doc': cols[2],
                    'added_doc': cols[3],
                    'warnemyr_doc': cols[4],
                    'grammar_support_for_added': cols[5],
                    'proposal': cols[6],
                }

    items = []
    for eid, e in kept.items():
        row = dict(e)
        ev = evidence.get(eid, {})
        row['grammar_support_for_added'] = ev.get('grammar_support_for_added')
        row['proposal'] = ev.get('proposal')
        row['decision'] = None
        row['decision_note'] = None
        items.append(row)
    items.sort(key=lambda r: int(r['id']))
    write_queue('A', 'review_queue.json + docs/DECISIONS_NEEDED.md S1 (merged, read-only)', items)


# -- Queue B -- 12 suspicious high-frequency PPP (ppp_source_validation.md) --

def parse_ppp_md_section(text, header_pat):
    m = re.search(header_pat + r'.*?\n\n(.*?)(\n## |\Z)', text, re.S)
    if not m:
        return
    body = m.group(1)
    for rec in re.split(r'\n(?=### )', body):
        rec = rec.strip()
        if not rec.startswith('###'):
            continue
        hm = re.match(r'### \[(\S+)\]\s*(.+)', rec.splitlines()[0])
        if not hm:
            continue
        eid, root = hm.group(1), hm.group(2).strip()
        fields = dict(re.findall(r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|', rec))
        fields.pop('Field', None)
        fields = {k: v for k, v in fields.items() if not re.fullmatch(r'-+', k)}
        reasoning_m = re.search(r'\n\n([^\n#|].+?)\s*$', rec, re.S)
        reasoning = reasoning_m.group(1).strip() if reasoning_m else None
        yield {'id': eid, 'root': root, **fields, 'reasoning': reasoning}


def build_queue_b():
    text = (ROOT / 'ppp_source_validation.md').read_text(encoding='utf-8')
    items = []
    for rec in parse_ppp_md_section(text, r'## SUSPICIOUS \(\d+\)'):
        rec['status'] = 'PENDING_REVIEW'
        rec['decision'] = None
        rec['decision_note'] = None
        items.append(rec)
    write_queue('B', 'ppp_source_validation.md -> SUSPICIOUS (already-complete section, no truncation)', items)


# -- Queue C -- 76 malformed PPP, LIKELY_ERROR (regenerate FULL list, read-only) --

def classify_ppp_detailed(ppp_str):
    ppp_forms = [f.strip() for f in ppp_str.split(',')]
    results = []
    for form in ppp_forms:
        original = form
        form = re.split(r'\s+[A-Z]\d\.\s*', form)[0]
        form = form.split('?')[0].strip()
        classification = 'CLEAN'
        error_likelihood = 0.1
        if len(form) <= 2:
            classification = 'PARTIAL'
            error_likelihood = 0.95
        elif form.endswith('ve') and 'ta' in form:
            classification = 'INVALID_MORPH'
            error_likelihood = 0.95
        elif form.endswith(('os', 'ih')) and 'ta' in form:
            classification = 'SANDHI_ARTIFACT'
            error_likelihood = 0.85
        elif not form.endswith(('ta', 'na')):
            if 'samskrta' not in form and 'samskrt' not in form:
                classification = 'UNCERTAIN_ENDING'
                error_likelihood = 0.50
        results.append({'form': form, 'original': original,
                         'classification': classification, 'error_likelihood': error_likelihood})
    return results


def build_queue_c():
    dcs_db = ROOT.parent / 'VisualDCS' / 'src' / 'DCS-data-2026' / 'dcs_full.sqlite'
    if not dcs_db.exists():
        print(f'  queue C: SKIPPED -- {dcs_db} not found', file=sys.stderr)
        return
    con = sqlite3.connect(str(dcs_db))
    cur = con.cursor()
    cur.execute("SELECT DISTINCT form FROM token")
    corpus_forms = {row[0] for row in cur.fetchall()}
    con.close()

    worklist = ROOT / 'Whitney_DCS_worklist.md'
    ppp_entries = []
    in_section_c = False
    with open(worklist, encoding='utf-8') as f:
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
                        eid = parts[1]; root = parts[2]; ppp_str = parts[3]
                        tokens = int(parts[4]) if len(parts) > 4 else 0
                        root_bare = root.lstrip('0123456789 ').strip()
                        ppp_entries.append({'id': eid, 'root': root, 'root_bare': root_bare,
                                             'ppp_str': ppp_str, 'tokens': tokens,
                                             'classifications': classify_ppp_detailed(ppp_str)})
                    except (ValueError, IndexError):
                        pass

    likely_errors = []
    for entry in ppp_entries:
        for ppp_class in entry['classifications']:
            form = ppp_class['form']; classification = ppp_class['classification']
            if form in corpus_forms:
                continue
            if classification == 'CLEAN':
                continue
            likely_errors.append({
                'id': entry['id'], 'root': entry['root'], 'root_bare': entry['root_bare'],
                'tokens': entry['tokens'], 'ppp_str': entry['ppp_str'],
                'suspect_form': form, 'classification': classification,
                'error_likelihood_pct': int(ppp_class['error_likelihood'] * 100),
                'reasoning': f"Morphologically suspect ({classification}). Likely source data error.",
                'status': 'PENDING_REVIEW', 'decision': None, 'decision_note': None,
            })
    likely_errors.sort(key=lambda x: (-x['tokens'], x['root_bare']))
    write_queue('C', 'Whitney_DCS_worklist.md SecC + dcs_full.sqlite, classify_ppp_detailed() '
                      '(same logic as scripts/dcs/ppp_source_validation.py, FULL list, no [:30] cap)',
                items=likely_errors,
                extra={'note_truncation': 'ppp_source_validation.md itself shows only the first 30 of '
                                           'these under LIKELY_ERROR (its own [:30] cap); this file has all.'})


# -- Queue D -- 101 grammar "exception" tags (src/app_data.json lexicon) --

SHORT_ROOT_CONTAMINATION_RISK = {
    'as': 'HIGH (matches English "as", 2482x in wg_text.txt per .ai_state.md)',
    'i': 'HIGH (matches English "i", 598x in wg_text.txt per .ai_state.md)',
}

def build_queue_d():
    app_data = json.load(open(ROOT / 'src' / 'app_data.json', encoding='utf-8'))
    raw_refs = json.load(open(ROOT / 'src' / 'grammar_refs.json', encoding='utf-8'))

    exc_entries = [e for e in app_data['lexicon'] if (e.get('grammar_ref') or {}).get('type') == 'exception']

    items = []
    for e in exc_entries:
        eid = e['id']
        root = e['root']
        root_bare = re.sub(r'^\d+\s*', '', root).strip()
        sections = e['grammar_ref'].get('sections', [])

        raw = raw_refs.get(eid, {})
        label_to_ref = {r['label']: r for r in raw.get('grammar_refs', [])}
        section_detail = []
        for label in sections:
            r = label_to_ref.get(label)
            if r:
                section_detail.append({
                    'label': label, 'type': r.get('type'),
                    'is_exception': r.get('is_exception'),
                    'snippet': r.get('snippet'),
                })
            else:
                section_detail.append({'label': label, 'type': None, 'is_exception': None, 'snippet': None})

        n_short = len(root_bare)
        if root_bare in SHORT_ROOT_CONTAMINATION_RISK:
            risk = SHORT_ROOT_CONTAMINATION_RISK[root_bare]
        elif n_short <= 2:
            risk = 'HIGH (bare root <=2 chars, per REVIEWER_GUIDE.md Queue D short-root caveat)'
        elif n_short <= 3:
            risk = 'MEDIUM (bare root <=3 chars)'
        else:
            risk = 'LOW'

        items.append({
            'id': eid, 'root': root, 'root_bare': root_bare, 'meaning': e.get('meaning'),
            'classes': e.get('classes'), 'ppp': e.get('ppp'),
            'section_count': len(sections),
            'sections': section_detail,
            'short_root_contamination_risk': risk,
            'status': 'PENDING_REVIEW', 'decision': None, 'decision_note': None,
        })
    risk_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    items.sort(key=lambda r: (risk_order.get(r['short_root_contamination_risk'].split(' ')[0], 3),
                               -r['section_count']))
    write_queue('D', 'src/app_data.json (grammar_ref.type=="exception") + src/grammar_refs.json '
                      '(per-section snippet lookup, read-only)', items)


# -- Queue E -- 117 reverted I/VI pairs (optional; read-only diff vs commit 18b51b1) --

def build_queue_e():
    raw = subprocess.run(['git', 'show', '18b51b1:src/app_data.json'], cwd=str(ROOT),
                          capture_output=True, encoding='utf-8')
    if raw.returncode != 0:
        print(f'  queue E: SKIPPED -- could not read commit 18b51b1 ({raw.stderr.strip()})', file=sys.stderr)
        return
    base = json.loads(raw.stdout)
    base_cls = {e['id']: list(e.get('classes', [])) for e in base['lexicon']}

    curr = json.load(open(ROOT / 'src' / 'app_data.json', encoding='utf-8'))

    items = []
    for e in curr['lexicon']:
        eid = e['id']; root = e['root']
        cnow = set(e.get('classes', []))
        cold = set(base_cls.get(eid, []))
        added = cnow - cold
        if not added:
            continue
        is_iv_collapse = ((added == {'VI'} and 'I' in cold) or (added == {'I'} and 'VI' in cold)
                           or ({'I', 'VI'} <= added))
        if is_iv_collapse:
            items.append({'id': eid, 'root': root, 'reverted_from_would_be': sorted(cnow),
                          'whitney_roots_baseline': base_cls.get(eid, []),
                          'reason': 'IV/VI accent-collapse (corpus cannot distinguish I from VI)'})

    if not items:
        log = subprocess.run(['git', 'log', '--all', '--format=%H', '--grep',
                               'revert.*unsound class additions', '-i'],
                              cwd=str(ROOT), capture_output=True, encoding='utf-8')
        commits = [c for c in log.stdout.split() if c]
        commit_sha = commits[-1] if commits else None  # oldest match = the original revert commit
        if commit_sha:
            parent = subprocess.run(['git', 'rev-parse', f'{commit_sha}^'], cwd=str(ROOT),
                                     capture_output=True, encoding='utf-8').stdout.strip()
            before = subprocess.run(['git', 'show', f'{parent}:src/app_data.json'], cwd=str(ROOT),
                                     capture_output=True, encoding='utf-8')
            after = subprocess.run(['git', 'show', f'{commit_sha}:src/app_data.json'], cwd=str(ROOT),
                                    capture_output=True, encoding='utf-8')
            if before.returncode == 0 and after.returncode == 0:
                b = {e['id']: (e['root'], set(e.get('classes', []))) for e in json.loads(before.stdout)['lexicon']}
                a = {e['id']: (e['root'], set(e.get('classes', []))) for e in json.loads(after.stdout)['lexicon']}
                for eid, (root, cls_before) in b.items():
                    _, cls_after = a.get(eid, (root, cls_before))
                    removed = cls_before - cls_after
                    if not removed:
                        continue
                    is_iv_collapse = ((removed == {'VI'} and 'I' in cls_after)
                                       or (removed == {'I'} and 'VI' in cls_after)
                                       or ({'I', 'VI'} <= removed))
                    if is_iv_collapse:
                        items.append({'id': eid, 'root': root, 'reverted_from': sorted(cls_before),
                                      'restored_to': sorted(cls_after),
                                      'reason': 'IV/VI accent-collapse (corpus cannot distinguish I from VI)',
                                      'source_commit': commit_sha})
        if not items:
            print('  queue E: could not recover the historical 117-pair list from git history '
                  '(no matching commit found) -- see REVIEWER_GUIDE.md Queue E for the manual '
                  'git show <commit> recipe instead.', file=sys.stderr)
            return

    for it in items:
        it['status'] = 'PENDING_REVIEW'
        it['decision'] = None
        it['decision_note'] = None
        it['optional'] = True
        it['adjudicable_by'] = ('Only an accented source (e.g. VedaWeb) or Zalizniak can split I vs VI here '
                                 '-- not errors in Whitney, cases the unaccented corpus cannot speak to.')
    items.sort(key=lambda r: int(r['id']))
    write_queue('E', ('read-only diff vs git commit 18b51b1:src/app_data.json, reproducing (never '
                       'executing) the classification logic of scripts/dcs/revert_collapse_additions.py'),
                items, extra={'priority': 'LOWEST of the batch -- optional re-check per .ai_state.md'})


if __name__ == '__main__':
    print('Building H975 queue candidates (read-only)...')
    build_queue_a()
    build_queue_b()
    build_queue_c()
    build_queue_d()
    build_queue_e()
    print('Done.')
