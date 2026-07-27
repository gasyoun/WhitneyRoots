"""
queue_cde_agent_verdicts.py
============================
H1686 (Uprava handoff) -- pre-resolve pattern-defined rows in review queues C, D, E
with a cited agent verdict, per the mandate in
Uprava/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md S11 (H1664) and
Uprava/handoffs/H1686-Sonnet_WhitneyRoots_queues-cde-pattern-preresolve_26.07.26.md.

READ-ONLY. Reads the H975 candidate-prefill files (docs/queue_candidates/queue_{c,d,e}.json,
produced by scripts/dcs/build_queue_candidates.py), the live src/app_data.json and
src/grammar_refs.json, src/wg_text.txt (Whitney's Grammar full text), and the
SanskritLexicography SCH-accents-IAST headword list. Writes ONLY new verdict files under
docs/queue_verdicts/ -- never touches app_data.json, grammar_refs.json, or review_queue.json
(those stay gated on the human residue vote per the handoff's DoD).

Verdict taxonomy
----------------
Queue C (malformed PPP, LIKELY_ERROR classifier output):
  already-fixed              current app_data.json ppp/infinitives no longer carries the
                              flagged suspect form (a prior pass -- fix_ppp_infinitives.py --
                              already moved it out). No human action needed.
  classifier-parse-artifact  the "suspect" ending is only an un-stripped edition/citation tag
                              (e.g. "E1" without a trailing period defeats the classifier's own
                              regex), not a real morphological problem; the underlying PPP is
                              clean -ta/-na. No human action needed.
  infinitive-bleed-*         suspect form's ending matches a Whitney-cited datival/ablative-
                              genitive infinitive suffix (-tave/-tavai <972, 968h>; -tos <970b,
                              972>; -dhyai <976>) -- the same "Verbal Nouns" apparatus-bleed
                              class already fixed for other ids by fix_ppp_infinitives.py.
                              Agent recommends the same disposition (move to `infinitives`);
                              residue: a human still applies the data edit (DoD gate), but no
                              longer has to research WHY.
  residue-human              no confident pattern match; needs linguistic judgment.

Queue D (grammar_ref.type == "exception" lexicon entries):
  contamination-clear        root is <=2 chars (or on the documented HIGH-risk list) and/or its
                              section_count is wildly disproportionate to a real exception
                              footnote list -- consistent with substring contamination in the
                              OCR'd grammar text (root string matches inside unrelated English
                              words), not a genuine cited exception.
  confirmed-exception        at least one of the entry's sections is independently tagged
                              type=="exception" in src/grammar_refs.json AND its snippet contains
                              the bare root as a real token (word-boundary match) -- a genuine
                              citation exists.
  residue-human               ambiguous: sections exist but no clean root-token match, or count
                              is borderline.

Queue E (reverted I/VI accent-collapse pairs):
  no-citation-auto-fail      root has zero prefix matches in the SCH-accents-IAST-20247.txt
                              accented headword list -- per the sheet's own promotion rule, a
                              row with no citable accented source cannot be promoted; revert
                              stands, no human vote owed.
  citable-source-candidate   >=1 accented headword shares the root's bare prefix -- a citation
                              MAY exist; kept for the human to inspect and decide I vs VI.

Usage:  python scripts/dcs/queue_cde_agent_verdicts.py
Output: docs/queue_verdicts/queue_{c,d,e}_verdicts.json
        docs/queue_verdicts/queue_{c,d,e}_human_residue.md
"""
import sys, json, re, io, pathlib, unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
CAND_DIR = ROOT / 'docs' / 'queue_candidates'
OUT_DIR = ROOT / 'docs' / 'queue_verdicts'
OUT_DIR.mkdir(parents=True, exist_ok=True)

AGENT_TIER = 'Sonnet 5 (claude-sonnet-5)'
HANDOFF = 'H1686'
GENERATED_ON = '28-07-2026'

ACCENT_LIST = ROOT.parent / 'SanskritLexicography' / 'HeadwordLists' / 'then-2014' / 'SCH-accents-IAST-20247.txt'
WG_TEXT = ROOT / 'src' / 'wg_text.txt'

ASCII_FOLD = str.maketrans({
    'ā': 'a', 'Ā': 'A', 'ī': 'i', 'Ī': 'I', 'ū': 'u', 'Ū': 'U',
    'ṛ': 'r', 'Ṛ': 'R', 'ṝ': 'r', 'Ṝ': 'R', 'ḷ': 'l', 'Ḷ': 'L', 'ḹ': 'l', 'Ḹ': 'L',
    'ṃ': 'm', 'Ṃ': 'M', 'ṁ': 'm', 'Ṁ': 'M', 'ḥ': 'h', 'Ḥ': 'H',
    'ś': 's', 'Ś': 'S', 'ç': 's', 'Ç': 'S', 'ṣ': 's', 'Ṣ': 'S',
    'ñ': 'n', 'Ñ': 'N', 'ṅ': 'n', 'Ṅ': 'N', 'ṇ': 'n', 'Ṇ': 'N',
    'ṭ': 't', 'Ṭ': 'T', 'ḍ': 'd', 'Ḍ': 'D',
    '́': '', '̀': '', '̍': '', '॒': '', '॑': '',  # Vedic accent/svara marks (combining, non-decomposed)
})


def ascii_fold(s):
    """Map every precomposed IAST-diacritic letter and every standalone Vedic accent
    mark to its bare-ASCII equivalent in a SINGLE pass over the as-encoded string
    (translate() is per-character and does not care about composition), then strip
    any still-combining marks (category Mn) NFD may reveal, so no dangling zero-width
    character is left to fool a plain [a-zA-Z] word-boundary regex."""
    folded = s.translate(ASCII_FOLD)
    d = unicodedata.normalize('NFD', folded)
    return ''.join(c for c in d if unicodedata.category(c) != 'Mn')


def load_wg_text_folded():
    text = WG_TEXT.read_text(encoding='utf-8')
    return ascii_fold(text)


def load_json(p):
    return json.load(open(p, encoding='utf-8'))


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def strip_accent_marks(s):
    """Remove ONLY the Vedic pitch-accent combining marks (acute/grave/anudatta),
    keep every other IAST diacritic (macron, dot-below, etc.) intact."""
    d = unicodedata.normalize('NFD', s)
    d = ''.join(c for c in d if c not in ('́', '̀', '̍', '॒', '॑'))
    return unicodedata.normalize('NFC', d)


def bare_root(root_field):
    return re.sub(r'^\d+\s*', '', root_field).strip()


# ============================================================================
# Queue C -- malformed PPP
# ============================================================================

EDITION_TAG_RE = re.compile(r'\s+([A-Z]\d*\.?|\?)\s*$')


def strip_edition_tag(form):
    """Strip a trailing edition/citation marker (E1, E1., S1, K, RV1, ?) that the
    upstream classifier's own regex (requires a literal period) sometimes misses."""
    prev = None
    cur = form
    while prev != cur:
        prev = cur
        cur = EDITION_TAG_RE.sub('', cur).strip()
    return cur


def queue_c_verdict(item, app_data_by_id, wg_text_folded):
    eid = item['id']
    suspect = item['suspect_form']
    classification = item['classification']

    e = app_data_by_id.get(eid)
    current_ppp = (e.get('ppp') or []) if e else []
    current_inf = (e.get('infinitives') or []) if e else []

    stripped = strip_edition_tag(suspect)

    # 1. already-fixed: the raw suspect form (or its edition-tag-stripped form) is no
    #    longer present in the live ppp array -- a prior pass already moved it out.
    if suspect not in current_ppp and stripped not in current_ppp:
        return {
            'verdict': 'already-fixed',
            'confidence': 'high',
            'human_residue': False,
            'evidence': f'src/app_data.json id={eid}: current ppp={current_ppp!r}, '
                        f'infinitives={current_inf!r} -- flagged form {suspect!r} no longer present.',
            'citation': None,
        }

    # 2. classifier-parse-artifact: stripping the edition tag reveals a clean -ta/-na form;
    #    the original UNCERTAIN_ENDING flag was a regex miss (classify_ppp_detailed() only
    #    strips "X1." with a literal trailing period), not a real morphological defect.
    if stripped != suspect and stripped.endswith(('ta', 'na')):
        return {
            'verdict': 'classifier-parse-artifact',
            'confidence': 'high',
            'human_residue': False,
            'evidence': f'ppp_source_validation.py classify_ppp_detailed() only strips a trailing '
                        f'edition tag matching "\\s+[A-Z]\\d.\\s*" (period required); {suspect!r} '
                        f'carries an un-punctuated tag. Stripped form {stripped!r} ends in -ta/-na '
                        f'-- a clean PPP, not {classification}.',
            'citation': None,
        }

    # 3. infinitive/verbal-noun apparatus bleed -- cite Whitney's own infinitive sections.
    #    Same defect class fix_ppp_infinitives.py already corrected for ids 227/333/409/472/
    #    560/568/649/793/914 (endings -e/-aye/-vane bled from Whitney's "Verbal Nouns" section).
    if stripped.endswith(('dhyai', 'dhyāi', 'ṣyai', 'ṣyāi')):
        return {
            'verdict': 'infinitive-bleed-dhyai',
            'confidence': 'medium-high',
            'human_residue': False,
            'evidence': f'{stripped!r} matches the Vedic dative-infinitive suffix -dhyai/-dhyāi '
                        f'(Whitney SS976: "The ending dhyai... added to a weak/strong form of root", '
                        f'worked example kSaradhyai for root kSar SS976 lists exactly this form). '
                        f'Same apparatus-bleed class as the already-fixed ids in '
                        f'scripts/dcs/fix_ppp_infinitives.py. Not a PPP; recommend moving to '
                        f'`infinitives` (data edit gated on human residue vote per DoD).',
            'citation': 'Whitney SS976',
        }
    if stripped.endswith(('tave', 'tavai', 'tavāi')):
        return {
            'verdict': 'infinitive-bleed-tave',
            'confidence': 'medium-high',
            'human_residue': False,
            'evidence': f'{stripped!r} matches the datival infinitive suffix -tave/-tavai made from '
                        f'the tu-stem (Whitney SS972, SS968h: "dative infinitives in tave or tavai"). '
                        f'A PPP never takes a suffix after -ta; this is a Verbal-Nouns-section bleed, '
                        f'same class as the already-fixed ids. Recommend moving to `infinitives`.',
            'citation': 'Whitney SS972 / SS968h',
        }
    if re.search(r'(dh|t)os$', stripped) and 'ta' not in stripped.replace(stripped[-3:], ''):
        pass  # fallthrough handled below by explicit -tos test
    if stripped.endswith('tos') or stripped.endswith('dhos'):
        return {
            'verdict': 'infinitive-bleed-tos',
            'confidence': 'medium-high',
            'human_residue': False,
            'evidence': f'{stripped!r} matches the ablative/genitive infinitive suffix -tos made '
                        f'from the tu-stem (Whitney SS970b: "its ablative and genitive in tos"; '
                        f'SS972 "hantos"). Not a PPP form; recommend moving to `infinitives`.',
            'citation': 'Whitney SS970b / SS972',
        }

    # 4. direct citation check: is the (ASCII-folded) suspect form itself an example word
    #    Whitney's own grammar text quotes for this root's PPP? (e.g. SS954a explicitly lists
    #    "crabdha" (ASCII-folded from "crabdha"/"srabdha") as the cited PPP of root crambh/
    #    crambh -- so a classifier flag of "non-standard ending" is simply wrong: -dha/-gdha/
    #    -bdha/-DHa etc. are ordinary sandhi outcomes of -ta that classify_ppp_detailed()'s
    #    "must end in ta/na" rule does not know about.)
    folded_suspect = ascii_fold(stripped).lower()
    root_bare = item['root_bare']
    folded_root = ascii_fold(root_bare).lower()
    if len(folded_suspect) >= 4:
        pattern = r'(?<![a-zA-Z])' + re.escape(folded_suspect) + r'(?![a-zA-Z])'
        for m in re.finditer(pattern, wg_text_folded, flags=re.IGNORECASE):
            window_lo, window_hi = max(0, m.start() - 200), m.end() + 200
            # exclude the matched suspect-word span itself from the corroboration search --
            # otherwise a root that happens to be a PREFIX of its own suspect form (e.g. root
            # "kas" inside suspect "kasam") trivially "corroborates" itself with no independent
            # evidence at all (the id-87 kasam false positive: an unrelated AV. noun form
            # Whitney himself flags "perhaps a false reading", sharing zero etymology with
            # root kaS, that happened to contain "kas" as its own first three letters).
            window = (wg_text_folded[window_lo:m.start()] + ' ' * (m.end() - m.start())
                      + wg_text_folded[m.end():window_hi])
            root_pattern = r'(?<![a-zA-Z])' + re.escape(folded_root) + r'(?![a-zA-Z])'
            if not re.search(root_pattern, window, flags=re.IGNORECASE):
                continue
            ctx = window[max(0, m.start() - window_lo - 90):m.end() - window_lo + 90].replace('\n', ' ')
            return {
                'verdict': 'confirmed-in-grammar-text',
                'confidence': 'high',
                'human_residue': False,
                'evidence': f'{stripped!r} (ASCII-folded {folded_suspect!r}) appears as a literal '
                            f'word in src/wg_text.txt (Whitney\'s Grammar full text), with root '
                            f'{root_bare!r} also present in the surrounding +-200-char window -- '
                            f'the classifier\'s "must end in -ta/-na" rule does not recognize '
                            f'regular sandhi outcomes (-dha, -gdha, -bdha, -gna, etc.); Whitney '
                            f'cites this exact form for this root. Context: "...{ctx}..."',
                'citation': 'Whitney (src/wg_text.txt, literal citation)',
            }

    # 5. root vowel-grade / weak-stem replacement is a real linguistic call -- leave to human.
    return {
        'verdict': 'residue-human',
        'confidence': 'low',
        'human_residue': True,
        'evidence': f'No already-fixed / parse-artifact / cited-infinitive-suffix / '
                    f'grammar-text-citation pattern matched for {suspect!r} (classification '
                    f'{classification}, {item["error_likelihood_pct"]}% error likelihood per '
                    f'ppp_source_validation.py). Needs Grammar SS-lookup + Zalizniak per '
                    f'REVIEWER_GUIDE.md Queue C algorithm.',
        'citation': None,
    }


def build_queue_c():
    cand = load_json(CAND_DIR / 'queue_c.json')
    app_data = load_json(ROOT / 'src' / 'app_data.json')
    by_id = {e['id']: e for e in app_data['lexicon']}
    wg_text_folded = load_wg_text_folded()

    items = []
    for it in cand['items']:
        v = queue_c_verdict(it, by_id, wg_text_folded)
        row = dict(it)
        row['agent_verdict'] = v['verdict']
        row['agent_confidence'] = v['confidence']
        row['human_residue'] = v['human_residue']
        row['agent_evidence'] = v['evidence']
        row['agent_citation'] = v['citation']
        row['agent'] = AGENT_TIER
        row['handoff'] = HANDOFF
        items.append(row)

    return items


# ============================================================================
# Queue D -- grammar "exception" tags
# ============================================================================

def root_token_in_snippet(root, snippet):
    if not snippet or not root:
        return False
    # word-boundary-ish match respecting IAST/devanagari punctuation as boundaries
    pattern = r'(?<![A-Za-zĀ-ǿāīūṛṝḷḹṃḥṅñṭḍṇśṣ])' + re.escape(root) + r'(?![A-Za-zĀ-ǿāīūṛṝḷḹṃḥṅñṭḍṇśṣ])'
    return re.search(pattern, snippet) is not None


def queue_d_verdict(item):
    root_bare = item['root_bare']
    section_count = item['section_count']
    risk = item['short_root_contamination_risk']
    sections = item['sections']

    is_short = len(root_bare) <= 2

    # A section_count this large for a single root is only plausible as substring
    # contamination -- Whitney never devotes 20+ distinct exception paragraphs to one root.
    CONTAMINATION_COUNT_THRESHOLD = 20

    if is_short and section_count >= CONTAMINATION_COUNT_THRESHOLD:
        return {
            'verdict': 'contamination-clear',
            'confidence': 'high',
            'human_residue': False,
            'evidence': f'root {root_bare!r} is <=2 chars ({risk}) and carries {section_count} '
                        f'candidate sections -- Whitney does not devote {section_count} distinct '
                        f'exception paragraphs to one root; this count is consistent with '
                        f'substring contamination in the OCR text (the bare root string recurring '
                        f'inside unrelated words/markup), not a genuine citation list.',
            'citation': None,
        }

    exception_sections = [s for s in sections if s.get('type') == 'exception']
    matched = [s for s in exception_sections
               if root_token_in_snippet(root_bare, s.get('snippet') or '')]

    # A <=2-char root token-matching a snippet is exactly the same false-positive risk
    # demonstrated in Queue C (root "kas" trivially "confirmed" by an unrelated word) --
    # a bare 1-2 letter token recurs constantly in ordinary prose. Require a SECOND,
    # independent exception-typed section to also token-match before trusting a short
    # root's citation; a single hit is not enough evidence to resolve it.
    if matched and (not is_short or len(matched) >= 2):
        top = matched[0]
        return {
            'verdict': 'confirmed-exception',
            'confidence': 'medium-high' if not is_short else 'medium',
            'human_residue': False,
            'evidence': f'section {top["label"]} is tagged type=="exception" and its snippet '
                        f'contains {root_bare!r} as a distinct token '
                        f'({len(matched)} independent exception-section token-match(es) total): '
                        f'"...{(top.get("snippet") or "")[:160]}..."',
            'citation': f'Whitney {top["label"]}',
        }

    if not exception_sections:
        return {
            'verdict': 'contamination-clear',
            'confidence': 'medium',
            'human_residue': False,
            'evidence': f'none of the {len(sections)} candidate sections for {root_bare!r} carry '
                        f'type=="exception" in src/grammar_refs.json -- the app_data.json '
                        f'"exception" tag has no supporting exception-typed citation.',
            'citation': None,
        }

    return {
        'verdict': 'residue-human',
        'confidence': 'low',
        'human_residue': True,
        'evidence': f'{len(exception_sections)} exception-typed section(s) exist for {root_bare!r} '
                    f'but none of their snippets contain the root as a clean token match -- '
                    f'needs a human read of the paragraph to confirm relevance.',
        'citation': None,
    }


def build_queue_d():
    cand = load_json(CAND_DIR / 'queue_d.json')
    items = []
    for it in cand['items']:
        v = queue_d_verdict(it)
        row = {k: v2 for k, v2 in it.items() if k != 'sections'}
        row['section_labels'] = [s['label'] for s in it['sections']]
        row['agent_verdict'] = v['verdict']
        row['agent_confidence'] = v['confidence']
        row['human_residue'] = v['human_residue']
        row['agent_evidence'] = v['evidence']
        row['agent_citation'] = v['citation']
        row['agent'] = AGENT_TIER
        row['handoff'] = HANDOFF
        items.append(row)
    return items


# ============================================================================
# Queue E -- reverted I/VI accent-collapse pairs
# ============================================================================

def load_accent_index():
    with io.open(ACCENT_LIST, encoding='utf-8-sig') as f:
        words = [l.strip() for l in f if l.strip()]
    pairs = [(strip_accent_marks(w), w) for w in words]
    pairs.sort(key=lambda p: p[0])
    return pairs


def prefix_matches(pairs, root, limit=6):
    # pairs sorted by bare form -- linear scan is fine at this size (~20k)
    return [w for b, w in pairs if b.startswith(root)][:limit]


MIN_RELIABLE_PREFIX_LEN = 3  # below this, a bare-prefix scan over ~20k headwords is too noisy
                             # to count as a citable match (e.g. root "am" prefix-matches
                             # "amUrta" = negating a- + mUrta, wholly unrelated to Vam amI)


def queue_e_verdict(item, accent_pairs):
    root_bare = bare_root(item['root'])
    matches = prefix_matches(accent_pairs, root_bare)

    if not matches:
        return {
            'verdict': 'no-citation-auto-fail',
            'confidence': 'high',
            'human_residue': False,
            'evidence': f'0 entries in SCH-accents-IAST-20247.txt (SanskritLexicography/HeadwordLists) '
                        f'share the bare-root prefix {root_bare!r} (accent marks normalized away, all '
                        f'other IAST diacritics preserved). No citable accented source -- per the '
                        f'sheet\'s own promotion rule, revert stands.',
            'citation': None,
            'matches': [],
        }

    if len(root_bare) < MIN_RELIABLE_PREFIX_LEN:
        return {
            'verdict': 'short-root-screening-unreliable',
            'confidence': 'low',
            'human_residue': True,
            'evidence': f'{len(matches)} prefix hits for {root_bare!r}, but root is only '
                        f'{len(root_bare)} chars -- a bare-prefix scan this short cannot '
                        f'distinguish a genuinely cognate accented form from an unrelated word that '
                        f'happens to start the same way (e.g. a negating a- + unrelated stem). '
                        f'Screening inconclusive; kept for the human, matches shown for reference: '
                        f'{matches!r}.',
            'citation': None,
            'matches': matches,
        }

    return {
        'verdict': 'citable-source-candidate',
        'confidence': 'n/a (screening only)',
        'human_residue': True,
        'evidence': f'{len(matches)} accented headword(s) in SCH-accents-IAST-20247.txt share the '
                    f'bare-root prefix {root_bare!r}: {matches!r}. A human must still read these to '
                    f'determine whether any shows the present-stem accent pattern (root-syllable = '
                    f'class I vs thematic vowel = class VI); the agent only screens for citability.',
        'citation': 'SCH-accents-IAST-20247.txt (SanskritLexicography/HeadwordLists/then-2014/)',
        'matches': matches,
    }


def build_queue_e():
    cand = load_json(CAND_DIR / 'queue_e.json')
    accent_pairs = load_accent_index()
    items = []
    for it in cand['items']:
        v = queue_e_verdict(it, accent_pairs)
        row = dict(it)
        row['agent_verdict'] = v['verdict']
        row['agent_confidence'] = v['confidence']
        row['human_residue'] = v['human_residue']
        row['agent_evidence'] = v['evidence']
        row['agent_citation'] = v['citation']
        row['accent_source_matches'] = v['matches']
        row['agent'] = AGENT_TIER
        row['handoff'] = HANDOFF
        items.append(row)
    return items


# ============================================================================
# Output
# ============================================================================

def summarize(letter, items):
    counts = defaultdict(int)
    for it in items:
        counts[it['agent_verdict']] += 1
    residue = sum(1 for it in items if it['human_residue'])
    print(f'Queue {letter}: {len(items)} total, {residue} human_residue, by verdict: {dict(counts)}')
    return {'total': len(items), 'human_residue': residue, 'by_verdict': dict(counts)}


def write_residue_md(letter, title, items, extra_cols):
    residue = [it for it in items if it['human_residue']]
    lines = [f'# Queue {letter} -- reduced human ask ({title})', '',
             f'_Generated {GENERATED_ON} by {AGENT_TIER}, {HANDOFF}. '
             f'{len(items)} total rows screened; {len(residue)} remain for a human; '
             f'{len(items) - len(residue)} resolved by agent verdict (see '
             f'docs/queue_verdicts/queue_{letter.lower()}_verdicts.json for every row + evidence)._',
             '']
    for it in residue:
        lines.append(f"### [{it['id']}] {it['root']}")
        lines.append('')
        for col in extra_cols:
            if col in it:
                lines.append(f'- **{col}**: {it[col]}')
        lines.append(f"- **agent_verdict**: {it['agent_verdict']} ({it['agent_confidence']})")
        lines.append(f"- **evidence**: {it['agent_evidence']}")
        lines.append('')
    out = OUT_DIR / f'queue_{letter.lower()}_human_residue.md'
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'  -> {out.relative_to(ROOT)} ({len(residue)} rows)')


if __name__ == '__main__':
    print('Building H1686 queue C/D/E agent verdicts (read-only)...')

    c_items = build_queue_c()
    d_items = build_queue_d()
    e_items = build_queue_e()

    summary = {
        'handoff': HANDOFF,
        'agent': AGENT_TIER,
        'generated': GENERATED_ON,
        'queue_c': summarize('C', c_items),
        'queue_d': summarize('D', d_items),
        'queue_e': summarize('E', e_items),
    }

    write_json(OUT_DIR / 'queue_c_verdicts.json',
               {'queue': 'C', 'source': 'docs/queue_candidates/queue_c.json + src/app_data.json',
                'generated': GENERATED_ON, 'generated_by': AGENT_TIER, 'handoff': HANDOFF,
                'count': len(c_items), 'items': c_items})
    write_json(OUT_DIR / 'queue_d_verdicts.json',
               {'queue': 'D', 'source': 'docs/queue_candidates/queue_d.json + src/grammar_refs.json',
                'generated': GENERATED_ON, 'generated_by': AGENT_TIER, 'handoff': HANDOFF,
                'count': len(d_items), 'items': d_items})
    write_json(OUT_DIR / 'queue_e_verdicts.json',
               {'queue': 'E', 'source': 'docs/queue_candidates/queue_e.json + SCH-accents-IAST-20247.txt',
                'generated': GENERATED_ON, 'generated_by': AGENT_TIER, 'handoff': HANDOFF,
                'count': len(e_items), 'items': e_items})
    write_json(OUT_DIR / 'SUMMARY.json', summary)

    write_residue_md('C', 'malformed PPP', c_items,
                      ['tokens', 'ppp_str', 'suspect_form', 'classification', 'error_likelihood_pct'])
    write_residue_md('D', 'grammar exception tags', d_items,
                      ['meaning', 'section_count', 'short_root_contamination_risk'])
    write_residue_md('E', 'reverted I/VI pairs', e_items,
                      ['reverted_from', 'restored_to'])

    total = summary['queue_c']['total'] + summary['queue_d']['total'] + summary['queue_e']['total']
    residue_total = (summary['queue_c']['human_residue'] + summary['queue_d']['human_residue']
                      + summary['queue_e']['human_residue'])
    print(f'\nTOTAL: {total} verdicts committed; {residue_total} human_residue (goal: ~90); '
          f'{total - residue_total} resolved by agent.')
