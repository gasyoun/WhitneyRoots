"""
grammar_ref_builder.py
======================
Builds Whitney Grammar §-citations for every root in app_data.json.

Outputs
-------
src/grammar_refs.json         — machine-readable per-root citations
Whitney_Grammar_Citations.md  — human metadocument (§ refs + DCS class)

Grammar authority order: Whitney Grammar (PDF) > Whitney Roots (app_data) > DCS corpus

Citation types
--------------
  generic    — root mentioned as a member-example in the opening of its class chapter
               (light-grey in UI: expected, unremarkable)
  specific   — root has a dedicated irregular paragraph in the Grammar
  exception  — root is explicitly called out as deviating from the normal rule
               ("except", "irregular", "anomalous", "but", "contrary", etc.)

Usage
-----
  cd WhitneyRoots
  python scripts/dcs/grammar_ref_builder.py
"""

import sys, re, json, sqlite3, pathlib

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]  # WhitneyRoots/
GRAMMAR_TXT = ROOT / 'src' / 'wg_text.txt'
APP_DATA    = ROOT / 'src' / 'app_data.json'
DCS_DB      = ROOT.parent / 'VisualDCS' / 'src' / 'DCS-data-2026' / 'dcs_full.sqlite'
OUT_JSON    = ROOT / 'src' / 'grammar_refs.json'
OUT_MD      = ROOT / 'Whitney_Grammar_Citations.md'

# ── 1. Load Grammar text (extract from PDF if not yet cached) ────────────────

GRAMMAR_PDF = ROOT / 'src' / 'Whitney-Grammar_Wikisource_2023.pdf'

if not GRAMMAR_TXT.exists():
    print(f'Extracting Grammar text from PDF...', file=sys.stderr)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(GRAMMAR_PDF))
        pages = [page.get_text() for page in doc]
        GRAMMAR_TXT.write_text('\n'.join(pages), encoding='utf-8')
        print(f'Saved to {GRAMMAR_TXT}', file=sys.stderr)
    except ImportError:
        raise RuntimeError('PyMuPDF (fitz) required: pip install pymupdf')

with open(GRAMMAR_TXT, encoding='utf-8') as f:
    GTEXT = f.read()

# ── 2. Build §-number index: sec_num → (char_pos, subsec_at_pos) ─────────────
#
# Pattern: "NNN." at the beginning of a paragraph.
# Subsection letter comes right after the §-number on a new line: "a. ", "b. "

SEC_RE = re.compile(r'(?:^|\n)(\d{3,4})\.')
SUBSEC_RE = re.compile(r'\n([a-h])\.\s')

sec_positions = {}  # num → list of char positions (there may be multiples; keep the largest that's > 500k)
for m in SEC_RE.finditer(GTEXT):
    n = int(m.group(1))
    pos = m.start()
    sec_positions.setdefault(n, []).append(pos)

# For each §, pick the "in-body" occurrence (after char 500000, where verb chapters live)
# If none after 500000, use the first
sec_pos = {}
for n, positions in sec_positions.items():
    body = [p for p in positions if p > 400000]
    sec_pos[n] = body[0] if body else positions[0]

# Sorted list of (position, sec_num) for quick nearest-§ lookup
sec_list = sorted((pos, n) for n, pos in sec_pos.items())

def nearest_sec(char_pos):
    """Return (sec_num, sec_start_pos) for the §-number most recently before char_pos."""
    lo, hi = 0, len(sec_list) - 1
    result = (0, 0)
    while lo <= hi:
        mid = (lo + hi) // 2
        if sec_list[mid][0] <= char_pos:
            result = (sec_list[mid][1], sec_list[mid][0])
            lo = mid + 1
        else:
            hi = mid - 1
    return result

def subsec_at(sec_start, hit_pos):
    """
    Find the active subsection letter (a/b/c/...) for a hit that falls between
    sec_start and the next §.
    Returns the letter string or '' if no subsection precedes the hit.
    """
    segment = GTEXT[sec_start:hit_pos]
    matches = list(SUBSEC_RE.finditer(segment))
    if matches:
        return matches[-1].group(1)
    return ''

# ── 3. Class chapter character ranges ────────────────────────────────────────
#
# Tuples: (start_char, end_char, hindu_class_roman, class_intro_§, whitney_name)
# Positions derived from the actual chapter-header text locations in the PDF extract.
#
# Whitney's numbering (I–IX) differs from Hindu gaṇa numbers (1–10).
# We store Hindu gaṇa numbers (matching app_data.json "classes" field).
#
# "intro_sec" is the §-number used for default generic citations.

CLASS_CHAPTERS = [
    # Gaṇa II = root/ad-class     §611–641  char 563482–586063
    (563482, 586063,  'II',   611, 'root/ad-class'),
    # Gaṇa III = hu/reduplication §642–682  char 586063–604611
    (586063, 604611,  'III',  642, 'hu-class/reduplication'),
    # Gaṇa VII = rudh/nasal       §683–696  char 604611–610471
    (604611, 610471,  'VII',  683, 'rudh/nasal-class'),
    # Gaṇa V+VIII = su+tan/nu+u   §697–716  char 610471–622450
    (610471, 622450,  'V_VIII', 697, 'su/tan-class (V & VIII)'),
    # Gaṇa IX = krī/nā            §717–733  char 622450–629925
    (622450, 629925,  'IX',   717, 'nā/krī-class'),
    # Gaṇa I  = bhū/a-unaccented  §734–750  char 629925–638796
    (629925, 638796,  'I',    734, 'bhū-class'),
    # Gaṇa VI = tud/á-accented    §751–760  char 638796–645862
    (638796, 645862,  'VI',   751, 'tud-class'),
    # Gaṇa IV = div/ya            §761–773  char 645862–654811
    (645862, 654811,  'IV',   761, 'div/ya-class'),
    # Passive yá-class            §774–784  char 654811–660000
    (654811, 660000,  'PASS', 774, 'passive/yá-class'),
    # Gaṇa X  = cur-class         §1041+    char 895184–920000
    (895184, 920000,  'X',    1041, 'cur-class'),
]

# Map Hindu gaṇa number (as string matching app_data "classes" field) to chapter entry
GANA_TO_CHAPTER = {}
for start, end, cls, intro_sec, name in CLASS_CHAPTERS:
    for label in cls.split('_'):   # 'V_VIII' → 'V', 'VIII'
        GANA_TO_CHAPTER[label] = (start, end, cls, intro_sec, name)

# Gaṇa number → intro §-label (used for default generic citations)
GANA_INTRO_SEC = {
    'I':   '§734', 'II':  '§611', 'III': '§642',
    'IV':  '§761', 'V':   '§697', 'VI':  '§751',
    'VII': '§683', 'VIII':'§697b','IX':  '§717', 'X': '§1041',
}

# The opening-paragraph boundary of each class chapter (where generic members are listed).
GENERIC_WINDOW = 1800  # chars from chapter start = "intro zone"

def chapter_for_pos(pos):
    """Return (class_roman, class_name, is_in_generic_zone) for a character position."""
    for start, end, cls, intro_sec, name in CLASS_CHAPTERS:
        if start <= pos < end:
            return cls, name, (pos - start) < GENERIC_WINDOW
    return None, None, False

# ── 4. Exception-keyword detection ───────────────────────────────────────────

EXCEPTION_KEYWORDS = re.compile(
    r'\b(irregular|anomalous?|defect(?:ive)?|supplet|supplied by|no present|'
    r'absent\b|does not .{0,20}follow|not .{0,15}form|contrary|'
    r'except(?:ing|ion)?\b|retain[s]? .{0,20}unchanged|'
    r'peculiar|transfers? to|treated .{0,15}as)',
    re.IGNORECASE
)

def is_exception_context(hit_pos):
    """Narrow window: 100 chars before and after the root mention only."""
    snippet = GTEXT[max(0, hit_pos - 100) : min(len(GTEXT), hit_pos + 100)]
    return bool(EXCEPTION_KEYWORDS.search(snippet))

# ── 5. Load app_data.json ─────────────────────────────────────────────────────

with open(APP_DATA, encoding='utf-8') as f:
    app_data = json.load(f)

entries = app_data['lexicon']

# ── 6. Load DCS class data ────────────────────────────────────────────────────
#
# DCS lemma.grammar format: "4. Ā."  means class 4, ātmanepada
# We store all class values for a given lemma string.

dcs_classes = {}   # lemma_str → list of (class_num_str, voice, grammar_raw)
con = sqlite3.connect(str(DCS_DB))
cur = con.cursor()
# Grammar field looks like "4. Ā." or "1. P." or "4. P.Ā." or just "m" (noun)
cur.execute("SELECT lemma, grammar FROM lemma WHERE grammar GLOB '[0-9]*'")
for lemma, grammar in cur.fetchall():
    m = re.match(r'(\d+)\.\s*([PĀ\.]+)', grammar)
    if m:
        cls_num = m.group(1)
        voice = m.group(2).strip('.')
        dcs_classes.setdefault(lemma, []).append((cls_num, voice, grammar))
con.close()

# ── 7. Build IAST root search patterns ───────────────────────────────────────
#
# The Grammar PDF text uses ç (U+00E7) for IAST ś (U+015B).
# All other IAST diacritics are identical.
#
# Word-boundary approximation: a root is a standalone token when not preceded
# or followed by a letter that could continue a Sanskrit word.

WORD_CHARS = r'a-zāīūṛḷṃḥṭḍṇśṣḻṁḥñçṅṃḫǵŕÇ'   # covers both IAST and Grammar conventions

def bare_root(root_str):
    """Strip '1 ', '2 ' etc. prefix."""
    return re.sub(r'^\d+\s+', '', root_str.strip())

def to_grammar_conv(root):
    """Convert IAST root to Grammar-text convention (ś → ç)."""
    return root.replace('ś', 'ç')

def build_search_pattern(root):
    """
    Pattern matching the root as a standalone token in Grammar text.
    Handles:
      - √root  (root cited after the √ symbol — need word-end check after root)
      - standalone root without √
    """
    gram_root = to_grammar_conv(root)
    escaped   = re.escape(gram_root)
    wb_after  = rf'(?![{WORD_CHARS}])'   # nothing letter-like follows
    wb_before = rf'(?<![{WORD_CHARS}])'  # nothing letter-like precedes
    return re.compile(
        rf'√{escaped}{wb_after}|{wb_before}{escaped}{wb_after}',
        re.UNICODE
    )

# ── 8. For each entry, find Grammar mentions ──────────────────────────────────

QUOTE_LEN = 200   # chars of context to quote

all_refs = {}     # id → citation list

for entry in entries:
    eid = entry['id']
    root_raw = entry['root']
    root = bare_root(root_raw)
    current_classes = entry.get('classes', [])
    ppp = entry.get('ppp', [])

    pat = build_search_pattern(root)
    refs = []

    for m in pat.finditer(GTEXT):
        pos = m.start()

        sec_num, sec_start = nearest_sec(pos)
        if sec_num == 0:
            continue

        subsec = subsec_at(sec_start, pos)

        cls, cls_name, is_generic = chapter_for_pos(pos)

        # Snippet for quote + exception detection
        snip_start = max(0, pos - 80)
        snip_end   = min(len(GTEXT), pos + QUOTE_LEN)
        snippet = GTEXT[snip_start:snip_end].replace('\n', ' ').strip()

        is_exc = is_exception_context(pos)

        if is_exc:
            cite_type = 'exception'
        elif is_generic:
            cite_type = 'generic'
        else:
            cite_type = 'specific'

        sec_label = f'§{sec_num}' + (f'{subsec}' if subsec else '')

        refs.append({
            'section': sec_num,
            'subsection': subsec if subsec else None,
            'label': sec_label,
            'class_chapter': cls,          # None if outside class chapters
            'class_chapter_name': cls_name,
            'type': cite_type,
            'is_exception': is_exc,
            'is_generic': is_generic,
            'snippet': snippet,
            'char_pos': pos,
        })

    # De-duplicate by label (keep first occurrence)
    seen = set()
    deduped = []
    for r in refs:
        if r['label'] not in seen:
            seen.add(r['label'])
            deduped.append(r)

    # Sort: class-chapter refs first, then others; exceptions before generics
    def sort_key(r):
        in_class = 0 if r['class_chapter'] else 1
        exc_order = 0 if r['is_exception'] else (1 if not r['is_generic'] else 2)
        return (in_class, exc_order, r['section'])

    deduped.sort(key=sort_key)

    # DCS data
    dcs_data = dcs_classes.get(root, [])
    dcs_class_labels = list({f"class {c} ({v})" for c, v, _ in dcs_data}) if dcs_data else ['—']

    # Add default generic citation for each class the Roots assigns,
    # if no Grammar class-chapter ref already covers that class.
    covered_chapters = {r['class_chapter'] for r in deduped if r['class_chapter']}
    default_generics = []
    for gana in current_classes:
        entry_ch = GANA_TO_CHAPTER.get(gana)
        if not entry_ch:
            continue
        _, _, ch_label, intro_sec, ch_name = entry_ch
        if ch_label not in covered_chapters:
            intro_label = GANA_INTRO_SEC.get(gana, f'§{intro_sec}')
            default_generics.append({
                'section': intro_sec,
                'subsection': None,
                'label': intro_label,
                'class_chapter': ch_label,
                'class_chapter_name': ch_name,
                'type': 'generic',
                'is_exception': False,
                'is_generic': True,
                'snippet': f'Default: {root_raw} is a regular member of the {ch_name}.',
                'char_pos': -1,
            })

    # Merge: grammar-specific refs first, then defaults
    all_grammar_refs = deduped + default_generics

    all_refs[eid] = {
        'id': eid,
        'root': root_raw,
        'root_bare': root,
        'classes_roots': current_classes,
        'ppp': ppp,
        'grammar_refs': all_grammar_refs,
        'dcs_classes': dcs_class_labels,
    }

# ── 9. Write grammar_refs.json ────────────────────────────────────────────────

with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(all_refs, f, ensure_ascii=False, indent=2)

print(f'Wrote {OUT_JSON}', file=sys.stderr)

# ── 10. Write Whitney_Grammar_Citations.md ────────────────────────────────────
#
# Table columns:
#   id | root | Roots classes | Grammar §§ [type] | DCS classes | notes
#
# Citation type markers:
#   (no marker)   = generic, regular — rendered light-grey in doc
#   ✦             = specific (root-specific § in a class chapter)
#   ⚠             = exception (root deviates from the normal rule)
#   ✦⚠            = specific AND exception

MAX_NONCLASS_REFS = 3   # max non-class-chapter refs to show in table

def format_refs(refs):
    """
    Format Grammar refs for the markdown table cell.

    Class-chapter refs first (all shown), then up to MAX_NONCLASS_REFS
    non-class refs in a lighter italic style.
    """
    class_parts = []
    nonclass_parts = []

    seen = set()
    for r in refs:
        label = r['label']
        if label in seen:
            continue
        seen.add(label)

        if r['class_chapter']:
            if r['is_exception']:
                class_parts.append(f'`{label}` ⚠')
            elif r['is_generic']:
                # default generics (char_pos == -1) get a slightly different marker
                if r.get('char_pos', 0) == -1:
                    class_parts.append(f'_{label}_')
                else:
                    class_parts.append(f'_{label}_')
            else:
                class_parts.append(f'**{label}** ✦')
        else:
            if r.get('char_pos', 0) != -1:   # skip default entries
                nonclass_parts.append(f'{label}')

    all_parts = class_parts + nonclass_parts[:MAX_NONCLASS_REFS]
    if len(nonclass_parts) > MAX_NONCLASS_REFS:
        all_parts.append(f'…+{len(nonclass_parts)-MAX_NONCLASS_REFS}')

    return ' · '.join(all_parts) if all_parts else '—'

lines = [
    '# Whitney Grammar Citations',
    '',
    '_Source: Whitney, Sanskrit Grammar (Harvard 1950 repr.) extracted from PDF._',
    '',
    '## Legend',
    '',
    '| Marker | Meaning |',
    '|--------|---------|',
    '| _§NNN_ | **Generic** — root is a regular member of its class; §-ref points to class-chapter introduction. (Display light grey — no conflict.) |',
    '| **§NNN** ✦ | **Specific** — root has a dedicated paragraph in the Grammar (irregular or noteworthy but still within its class). |',
    '| `§NNN` ⚠ | **Exception** — Grammar explicitly calls this root out as deviating from the normal rule. |',
    '| **§NNN** ✦⚠ | Specific AND exception. |',
    '',
    '## Citations table',
    '',
    '| id | root | Roots classes | Grammar §§ | DCS classes | notes |',
    '|---|---|---|---|---|---|',
]

for entry in entries:
    eid = entry['id']
    data = all_refs.get(eid, {})
    root_raw = entry['root']
    roots_cls = ', '.join(data.get('classes_roots', [])) or '—'
    gram_refs = format_refs(data.get('grammar_refs', []))
    dcs_cls   = ', '.join(data.get('dcs_classes', ['—']))
    notes     = ''
    refs_list = data.get('grammar_refs', [])

    # Detect special scholarly cases
    class_refs = [r for r in refs_list if r['class_chapter']]
    has_text_class_ref = any(r['class_chapter'] and r.get('char_pos',-1) != -1 for r in refs_list)

    # mṛ: §773 says mriyáte is passive, not ya-class
    if '§773' in [r['label'] for r in refs_list]:
        notes = '§773: mriyáte is a passive (yá-stem), not a class-IV intransitive. Whitney class I (§731: mṛṇá á-stem) is correct.'
    # vadh: no present class in Grammar; present supplied by han
    elif root_raw in ('vadh',) and not any(r['class_chapter'] in ('I','II','III','IV','V','VI','VII','VIII','IX') and r.get('char_pos',-1) != -1 for r in refs_list):
        notes = 'Defective root: present supplied by √han. Grammar cites only aorist (§904a) and denominative (§1042g). Class I is nominal (from Roots).'
    # cūṣ: no Grammar class mention
    elif root_raw == 'cūṣ':
        notes = '§240b phonological note only. Class IV from Whitney Roots; Grammar does not confirm independently.'
    elif not has_text_class_ref and roots_cls != '—':
        notes = 'Class from Roots only; not mentioned in Grammar class chapters.'
    elif not refs_list:
        notes = 'Not found in Grammar text.'

    lines.append(f'| {eid} | {root_raw} | {roots_cls} | {gram_refs} | {dcs_cls} | {notes} |')

lines += [
    '',
    '---',
    '_Generated by scripts/dcs/grammar_ref_builder.py_',
    '',
]

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Wrote {OUT_MD}', file=sys.stderr)

# ── 11. Update app_data.json with grammar_ref field ──────────────────────────
#
# Adds "grammar_ref": { "sections": ["§731", "§773a"], "type": "specific/generic/exception" }

for entry in app_data['lexicon']:
    eid = entry['id']
    data = all_refs.get(eid, {})
    refs_list = data.get('grammar_refs', [])

    # Only include class-chapter refs in app_data (non-class refs are too noisy)
    class_refs = [r for r in refs_list if r['class_chapter']]

    if class_refs:
        # Highest-priority type
        types = {r['type'] for r in class_refs}
        if 'exception' in types:
            top_type = 'exception'
        elif 'specific' in types:
            top_type = 'specific'
        else:
            top_type = 'generic'

        entry['grammar_ref'] = {
            'sections': [r['label'] for r in class_refs],
            'type': top_type,
        }
    else:
        entry['grammar_ref'] = None

with open(APP_DATA, 'w', encoding='utf-8') as f:
    json.dump(app_data, f, ensure_ascii=False, indent=2)

print(f'Updated {APP_DATA}', file=sys.stderr)

# ── 12. Summary stats ─────────────────────────────────────────────────────────

total = len(entries)
has_any    = sum(1 for e in entries if e.get('grammar_ref'))
generic    = sum(1 for e in entries if (e.get('grammar_ref') or {}).get('type') == 'generic')
specific   = sum(1 for e in entries if (e.get('grammar_ref') or {}).get('type') == 'specific')
exception  = sum(1 for e in entries if (e.get('grammar_ref') or {}).get('type') == 'exception')
not_found  = total - has_any

print(f'\nSummary ({total} entries):')
print(f'  with Grammar class-chapter ref: {has_any}')
print(f'    generic  (regular member):    {generic}')
print(f'    specific (own §-paragraph):   {specific}')
print(f'    exception (deviates):         {exception}')
print(f'  no Grammar class-ref (Roots only): {not_found}')
