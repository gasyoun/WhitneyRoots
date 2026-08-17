"""
corpus_verify_classes.py
========================
Verify Whitney Grammar class assignments against DCS corpus present-tense forms.

Strategy: extract all present-tense finite forms for each root, derive the
present-stem pattern, and map it back to a gaṇa (class I–X). Compare against
the Grammar class assignment.

Present-stem signatures (what each gaṇa looks like):
  I   (bhū)   → stem = root + a  (e.g., bhav-a, bhav-anti)
  II  (ad)    → stem = root      (e.g., ad-mi, ad-anti)
  III (hu)    → stem = redup+root (e.g., juhū, juhv-anti)
  IV  (div)   → stem = root + ya  (e.g., div-ya, div-yanti)
  V   (su)    → stem = root + nu (strong: -nó)  (e.g., sunómi, sunv-anti)
  VI  (tud)   → stem = root + á  (accented; root unstrengthened)  (e.g., tudá)
  VII (rudh)  → stem = root + nasal + a  (e.g., ruṇaddhi, ruṇad-mi)
  VIII(tan)   → stem = root + u  (weak: tan-u)  (e.g., tan-u, tan-ū-anti)
  IX  (krī)   → stem = root + nā (strong: nā́)  (e.g., krīṇā, krīṇ-anti)
  X   (cur)   → stem = root + aya (strengthened)  (e.g., cúraya)
  Pass → stem = root + yá (accented; passive voice)

Output: `corpus_class_verdicts.json` with per-root present-stem evidence.
"""

# H2892 — refuse-by-default writer lock over the human-reviewed overlays.
# Must stay the first executable statement: nothing below it may open a
# reviewed file. Set ALLOW_OVERLAY_WIPE=1 only for a deliberate, re-pinned
# rewrite (scripts/overlay_guard.py).
import pathlib as _pathlib, sys as _sys
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))
from overlay_guard import refuse_unless_hatched as _refuse_unless_hatched
_refuse_unless_hatched(__file__, targets=('src/app_data.json',), rewrites=False)

import sys, re, json, sqlite3, pathlib
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]  # WhitneyRoots/
APP_DATA    = ROOT / 'src' / 'app_data.json'
GRAMMAR_REFS = ROOT / 'src' / 'grammar_refs.json'
DCS_DB      = ROOT.parent / 'VisualDCS' / 'src' / 'DCS-data-2026' / 'dcs_full.sqlite'
OUT_JSON    = ROOT / 'corpus_class_verdicts.json'

# ── 1. Load Whitney/Grammar assignments ────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

with open(GRAMMAR_REFS, encoding='utf-8') as f:
    gram_refs = json.load(f)

# Build root → (classes, grammar_type)
root_assignments = {}  # bare_root → {classes, grammar_type, id, root_raw}
for entry in app_data['lexicon']:
    eid = entry['id']
    root_raw = entry['root']
    root = re.sub(r'^\d+\s+', '', root_raw.strip())
    classes = entry.get('classes', [])

    gram = gram_refs.get(eid, {})
    gram_type = 'none'
    if gram.get('grammar_refs'):
        class_refs = [r for r in gram['grammar_refs'] if r.get('class_chapter')]
        if class_refs:
            gram_type = class_refs[0]['type']

    root_assignments[root] = {
        'id': eid,
        'root_raw': root_raw,
        'root': root,
        'classes': classes,
        'grammar_type': gram_type,
    }

# ── 2. Query DCS for present-tense forms per root ──────────────────────────

con = sqlite3.connect(str(DCS_DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

# Present tense = feat_tense='Pres', finite = feat_verbform='Fin'
# We want: lemma, form (surface), feat_person, feat_voice
# Group by lemma to avoid duplicates

lemma_tokens = defaultdict(list)  # lemma → [(form, person, voice), ...]

cur.execute("""
    SELECT DISTINCT t.lemma, t.form, t.feat_person, t.feat_voice
    FROM token t
    WHERE t.feat_tense = 'Pres'
      AND t.feat_verbform IS NULL
    ORDER BY t.lemma, t.form
""")

for row in cur.fetchall():
    lemma = row[0]
    form = row[1]
    person = row[2] or ''
    voice = row[3] or 'Act'
    lemma_tokens[lemma].append((form, person, voice))

con.close()

# ── 3. Derive present-stem patterns ────────────────────────────────────────
#
# For each lemma, extract the present-stem by removing personal endings.
# Strategy: collect all forms, find the common root, then identify the stem marker.

def extract_present_stems(forms):
    """
    Extract the attested present-stem from a set of forms.

    Strategy: remove personal/modal endings from each form, collect the stems,
    and return the most frequent stems.

    Returns: list of (stem, count, example_forms) tuples, sorted by frequency.
    """
    if not forms:
        return []

    # Personal + modal endings (comprehensive list)
    # Active: 1s -mi, 2s -si, 3s -ti, 1d -vas, 2d -thaḥ, 3d -tus, 1p -mas, 2p -tha, 3p -anti
    # Subjunctive: 1s -āni, 2s -āsi, 3s -āt, 1p -āma, 2p -āta, 3p -ān
    # Optative: 1s -yām, 2s -yāḥ, 3s -yāt, 1p -yāma, 2p -yāta, 3p -yur
    # Imperative: 2s often shortened form, 2d -tam, 3d -tām, 2p -ta, 3p -antu
    # Middle: similar but -te, -dhve, -mahe, -āte, -ante

    endings = [
        # Sorted by length (longest first) to avoid partial matches
        'āmahe', 'dhve', 'ante', 'anti', 'thaḥ', 'tām',  # 4+ chars
        'āmi', 'yum', 'tus', 'mas', 'tha', 'yur',  # 3 chars
        'mi', 'ti', 'si', 'ni', 'te', 'se', 'ḥ',  # 1-2 chars
        'ati', 'ate', 'ita', 'ete', 'et', 'an', 'ām', 'āt', 'yāḥ',
    ]

    stems = defaultdict(lambda: {'count': 0, 'examples': []})

    for form in forms:
        matched = False
        for ending in sorted(endings, key=len, reverse=True):
            if form.endswith(ending) and len(form) > len(ending):
                stem = form[:-len(ending)]
                stems[stem]['count'] += 1
                if form not in stems[stem]['examples']:
                    stems[stem]['examples'].append(form)
                matched = True
                break
        if not matched:
            # Couldn't remove an ending; treat whole form as stem
            stems[form]['count'] += 1
            stems[form]['examples'].append(form)

    # Return stems sorted by frequency
    result = [(stem, data['count'], data['examples'])
              for stem, data in stems.items()]
    result.sort(key=lambda x: -x[1])
    return result

# ── 4. Map stems to gaṇa signatures ───────────────────────────────────────
#
# Given a present-stem and root, identify which gaṇa class it signals.

GANA_MARKERS = {
    # Signature: regex pattern → (gaṇa_class, description)
    # Pattern uses $R for root, $S for stem
    'I':     (r'^$R[ao]?$',              'bhū: stem = root+a or root'),
    'II':    (r'^$R$',                   'ad: stem = root (no marker)'),
    'III':   (r'^[a-z]+$R',              'hu: reduplication prefix'),
    'IV':    (r'^$Rya',                  'div: stem = root+ya'),
    'V':     (r'^$Rnu',                  'su: stem = root+nu (strong: -nó)'),
    'VI':    (r'^$R[aā]',                'tud: stem = root+á (accented)'),
    'VII':   (r'^$R[aāiī]?[ṇn]',        'rudh: stem = root+nasal+a'),
    'VIII':  (r'^$Ru',                   'tan: stem = root+u'),
    'IX':    (r'^$Rn[aā]',               'krī: stem = root+nā'),
    'X':     (r'^$Raya',                 'cur: stem = root+aya'),
    'PASS':  (r'^$Rya',                  'passive: stem = root+yá (indistinguishable from IV without voice)'),
}

def infer_gana(root, stem):
    """
    Given root and stem, infer which gaṇa (class) this signals.
    Returns: (gaṇa, confidence, reason)
    gaṇa: 'I', 'II', ..., 'IV|PASS' (if ambiguous), or None
    confidence: 'high', 'med', 'low'
    """
    if not stem or not root:
        return None, 'low', 'no stem or root'

    # Normalize root: remove diacritics variations for initial matching
    # Use the exact characters from the corpus

    # Try to find a gana that matches
    matches = []
    for gana, (pattern, desc) in GANA_MARKERS.items():
        # Build the pattern: replace $R with root
        pat = pattern.replace('$R', re.escape(root))
        if re.match(pat, stem):
            matches.append((gana, desc))

    if not matches:
        return None, 'low', f'no pattern match (stem={stem!r}, root={root!r})'

    if len(matches) == 1:
        return matches[0][0], 'high', matches[0][1]

    # Ambiguity: IV and PASS both have +ya marker
    ganas = [m[0] for m in matches]
    if ganas == ['IV', 'PASS'] or ganas == ['PASS', 'IV']:
        return 'IV|PASS', 'med', 'stem=root+ya (class IV or passive)'

    return ganas[0], 'med', f'multiple matches: {ganas}'

# ── 5. Build verdict for each root ────────────────────────────────────────

verdicts = {}  # root → verdict dict

for root, assignment in root_assignments.items():
    forms = lemma_tokens.get(root, [])
    forms_list = [f[0] for f in forms]

    if not forms_list:
        verdicts[root] = {
            'id': assignment['id'],
            'root_raw': assignment['root_raw'],
            'classes': assignment['classes'],
            'grammar_type': assignment['grammar_type'],
            'corpus_forms': [],
            'corpus_stems': [],
            'corpus_gana': None,
            'corpus_confidence': 'none',
            'verdict': 'not_attested',
            'note': 'No present-tense tokens in DCS corpus.',
        }
        continue

    # Extract stems (list of (stem, count, example_forms))
    stem_list = extract_present_stems(forms_list)

    # Infer gana from the most frequent stems
    inferred_ganas = set()
    confidences = []
    reasons = []

    for stem, count, examples in stem_list[:3]:  # check top 3 stems by frequency
        gana, conf, reason = infer_gana(root, stem)
        if gana:
            inferred_ganas.add(gana)
            confidences.append(conf)
            reasons.append(f'{stem} ({count}x) → {gana} ({reason})')
            # Stop after first match if confidence is high
            if conf == 'high':
                break

    # Summarize
    corpus_gana = ', '.join(sorted(inferred_ganas)) if inferred_ganas else None
    corpus_conf = 'high' if 'high' in confidences else ('med' if 'med' in confidences else 'low')

    # Compare vs. Whitney
    verdict_label = 'agree'
    note = ''

    if not corpus_gana:
        verdict_label = 'unclear'
        note = 'Could not infer gaṇa from present-stem.'
    elif corpus_gana in assignment['classes']:
        verdict_label = 'agree'
        note = f"Corpus signal ({corpus_gana}) matches Whitney class."
    elif '|' in corpus_gana:
        # Ambiguous (IV vs PASS)
        if 'IV' in assignment['classes']:
            verdict_label = 'agree_ambig'
            note = f"Corpus signal ({corpus_gana}) is ambiguous; Whitney has IV."
        else:
            verdict_label = 'conflict'
            note = f"Corpus signal ({corpus_gana}) but Whitney has {assignment['classes']}."
    else:
        verdict_label = 'conflict'
        note = f"Corpus signals {corpus_gana} but Whitney has {assignment['classes']}."

    verdicts[root] = {
        'id': assignment['id'],
        'root_raw': assignment['root_raw'],
        'classes': assignment['classes'],
        'grammar_type': assignment['grammar_type'],
        'corpus_forms': forms_list[:10],  # cap to 10 examples
        'corpus_stems': [(s, c) for s, c, _ in stem_list[:5]],  # (stem, count)
        'corpus_gana': corpus_gana,
        'corpus_confidence': corpus_conf,
        'stem_derivation': reasons,
        'verdict': verdict_label,
        'note': note,
    }

# ── 6. Write output ─────────────────────────────────────────────────────────

with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(verdicts, f, ensure_ascii=False, indent=2)

print(f'Wrote {OUT_JSON}', file=sys.stderr)

# ── 7. Summary ──────────────────────────────────────────────────────────────

verdict_counts = defaultdict(int)
for v in verdicts.values():
    verdict_counts[v['verdict']] += 1

print(f'\nSummary ({len(verdicts)} roots checked):')
for vtype, count in sorted(verdict_counts.items()):
    print(f'  {vtype:20s}: {count:3d}')

# Show conflicts
conflicts = {r: v for r, v in verdicts.items() if v['verdict'] == 'conflict'}
if conflicts:
    print(f'\nConflicts ({len(conflicts)}):')
    for root, v in sorted(conflicts.items(), key=lambda x: -len(x[1]['corpus_forms']))[:10]:
        print(f"  {root:15s}: Whitney {v['classes']} vs. corpus {v['corpus_gana']} "
              f"({len(v['corpus_forms'])} tokens)")
