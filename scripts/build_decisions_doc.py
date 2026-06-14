# -*- coding: utf-8 -*-
"""Assemble docs/DECISIONS_NEEDED.md — the consolidated human-decision register.

Pre-gathers Grammar §-evidence for every open class decision so a reviewer (and then
Zalizniak) only has to confirm, not hunt. Reads (never writes) the data sources:
  review_queue.json            19 kept class additions (Queue A)
  src/grammar_refs.json        per-root Whitney §-citations, tagged by class_chapter
  scratch/phase0/root_spine.json   warnemyr-authoritative class per homonym (+ uncertain)
  scratch/phase0/audit.md      the 23 Phase-0 GAP/SMEAR flags

Authority order: Grammar > Whitney Roots > DCS corpus > Zalizniak. Nothing here is applied;
every row is EVIDENCE + a PROPOSAL. The human decides. UTF-8, no BOM.
"""
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(BASE, *a)

queue  = json.load(open(P('review_queue.json'), encoding='utf-8'))['kept_pending_review']
grefs  = json.load(open(P('src','grammar_refs.json'), encoding='utf-8'))
spine  = json.load(open(P('scratch','phase0','root_spine.json'), encoding='utf-8'))
by_no  = {r['whitney_no']: r for r in spine if 'whitney_no' in r}

ppp_val_p = P('crosswalk', 'ppp_validation.json')
ppp_val = json.load(open(ppp_val_p, encoding='utf-8')) if os.path.exists(ppp_val_p) else None

URGENT = {'473','578','890'}   # [I,VI]-onto-empty: the collapse the revert predicate can't catch

# The corpus-corroborated PPP "mismatches" from scripts/vidyut_validate_ppp.py — each verified by a
# 3-verifier Sanskritist panel (wf_0225d753, 2026-06-14, 13/13 unanimous). FINDING: NONE is a warnemyr
# error. 8 are homonym artifacts (warnemyr records the PPP of the GLOSSED homonym; vidyut/DCS surface
# the corpus-DOMINANT same-spelled root's PPP because the DCS lemma lumps them) → KEEP warnemyr. 5 are
# aniṭ/seṭ (or -ta/-na) doublets of one root → editorial, both valid. So `corpus_backs_vidyut` is, on a
# root with homonyms or a PPP doublet, a homonym/variant detector — NOT a correction signal.
PPP_NOTES = {   # whitney_no: (kind, warnemyr's form belongs to, the corpus form belongs to)
    43:  ('homonym', '√iṣ "send" — seṭ (iṣ-i-tá)',           '√iṣ "desire" #42 — aniṭ (iṣ+ta→iṣṭá)'),
    259: ('homonym', '√ji/jinv "quicken" — seṭ',             '√ji "conquer" #258 — jitá'),
    350: ('homonym', '√dā "divide/cut" — dyáti-root',        '√dā "give" #349 — dadā́ti-root, datta'),
    395: ('homonym', '√dhāv "run" — seṭ',                    '√dhāv "wash/cleanse" — aniṭ vṛddhi, dhauta'),
    572: ('homonym', '√mṛ "crush" #2 — mṛṇáti, mūrṇá',       '√mṛ "die" #1 — mriyáte, mṛtá'),
    729: ('homonym', '√vid "find/obtain" #729 — vittá',      '√vid "know" #728 — viditá'),
    773: ('homonym', '√śam "labor/toil" #773 — śamitá',      '√śam "be quiet/cease" #774 — śāntá'),
    912: ('homonym', '√hā "go forth/move" — hāna',           '√hā "abandon/quit" #911 — jáhāti, hīná'),
    148: ('variant', 'kṣubdha — aniṭ -ta',                   'kṣubhita — seṭ -ita (one √kṣubh, §956b)'),
    183: ('variant', 'gupitá — seṭ',                         'gupta — aniṭ (one √gup, §956b)'),
    197: ('variant', 'grasitá — seṭ',                        'grasta — aniṭ (one √gras)'),
    455: ('variant', 'piṣṭá — aniṭ (piś+ta→piṣṭa)',          'piśita — seṭ (one √piś "adorn")'),
    727: ('variant', 'vikta — -ta allomorph (Rigvedic)',     'vigna — -na allomorph (one √vij "tremble")'),
}

def chapter_set(eid):
    """Whitney grammar chapters (gaṇas) under which this root is actually discussed."""
    out = {}
    for ref in grefs.get(eid, {}).get('grammar_refs', []):
        cc = ref.get('class_chapter')
        if cc:
            for part in str(cc).split('_'):
                out.setdefault(part, []).append((ref['label'], ref.get('type',''), ref.get('snippet','')[:160]))
    return out

def grammar_supports(eid, gana):
    chs = chapter_set(eid)
    return chs.get(gana, [])

def proposal(item):
    eid, added = item['id'], item['added']
    supported = {g: grammar_supports(eid, g) for g in added}
    n_sup = sum(1 for g in added if supported[g])
    # True only when the delta is *purely* I and/or VI onto an empty Whitney baseline — the
    # unaccented-corpus collapse. (A delta like [I,III] must NOT be labelled an I/VI artifact.)
    iv_pair = bool(added) and set(added) <= {'I', 'VI'} and not item['whitney_roots_classes']
    if n_sup == len(added) and added:
        verdict = 'LEAN KEEP — Grammar cites this root under the added chapter(s). Confirm sense w/ Zalizniak.'
    elif n_sup == 0 and iv_pair:
        verdict = 'LEAN REVERT — no Grammar chapter cites the added class; I/VI is the unaccented-corpus artifact.'
    elif n_sup == 0:
        verdict = 'NEEDS ZALIZNIAK — added class has no Grammar chapter; corpus-only signal.'
    else:
        verdict = 'MIXED — part Grammar-supported; review each added class below.'
    return supported, verdict

def fmt_supported(supported):
    rows = []
    for g, hits in supported.items():
        if hits:
            labs = ', '.join(sorted({h[0] for h in hits}))
            rows.append(f'    - **+{g}**: Grammar **{labs}** ✓  _“{hits[0][2].strip()}…”_')
        else:
            rows.append(f'    - **+{g}**: ✗ no Grammar chapter cites class {g} for this root.')
    return '\n'.join(rows)

def wn_evidence(item):
    no = int(re.sub(r'\D','', item['id']))
    r = by_no.get(no)
    if not r: return '_(no warnemyr record)_'
    bits = [f"warnemyr class **{'/'.join(r['class']) or '—'}**"]
    if r.get('class_uncertain'): bits.append(f"uncertain {'/'.join(r['class_uncertain'])}")
    if r.get('gloss_short'):     bits.append(f"“{r['gloss_short']}”")
    return ' · '.join(bits)

out = []
out.append('# DECISIONS NEEDED — Whitney-root class & PPP curation\n')
out.append('Open decisions that require a Sanskritist (then **Zalizniak** as tiebreaker). '
           'Authority order: **Grammar > Whitney Roots > DCS corpus > Zalizniak**. '
           'Everything below is **evidence + a proposal** — nothing is applied. '
           'Companion to [REVIEWER_GUIDE.md](../REVIEWER_GUIDE.md) (full per-item algorithm, EN/RU) '
           'and [review_queue.json](../review_queue.json).\n')
out.append('Generated by `scripts/build_decisions_doc.py` from the data sources — regenerable, do not hand-edit.\n')
out.append('---\n')

# ---- Section 0: the 3 urgent I/VI-onto-empty ----
urgent_items = [q for q in queue if q['id'] in URGENT]
out.append('## 0. ⚠️ Highest priority — I/VI added together onto an empty baseline\n')
if not urgent_items:
    out.append('✓ **Resolved.** The I/VI-onto-empty additions (pṛṇ 473, mṛṇ 578, sphur 890) were reverted '
               'to an empty class baseline (PR #9) — a corpus-only class must not be written into '
               '`app_data.json`, and the +VI "support" was only a passing §-mention (§753a/§756 discuss '
               'these as root *transfers/relations*, not a clean class-VI present). Re-add VI from Grammar '
               'cleanly if ever warranted; nothing is live here now.\n')
else:
    out.append('Flagged by code review: these were added **[I, VI] together** where Whitney lists **no** class. '
               'The revert predicate only catches a *single*-class I↔VI delta, so these slipped through and sit '
               '**live in `app_data.json`** as unaccented-corpus-derived classes with (check below) no Whitney support. '
               'The corpus *cannot* distinguish I from VI. Decide explicitly before treating as authoritative.\n')
    for item in urgent_items:
        supported, verdict = proposal(item)
        out.append(f"### [{item['id']}] {item['root']} — added {item['added']}")
        out.append(f"- {wn_evidence(item)}")
        out.append(fmt_supported(supported))
        out.append(f"- **Proposal:** {verdict}\n")

# ---- Section 1: Queue A (the rest of the 19) ----
out.append('---\n')
out.append('## 1. Queue A — kept class additions (Grammar-§ checked)\n')
out.append('Each adds a *distinct* gaṇa on a corpus prompt. Grammar-chapter evidence pre-pulled from '
           '`src/grammar_refs.json`; confirm against the cited §, then Zalizniak.\n')
out.append('| # | root | Whitney | added | warnemyr | Grammar support for added | proposal |')
out.append('|--:|---|:-:|:-:|:-:|---|---|')
for item in [q for q in queue if q['id'] not in URGENT]:
    supported, verdict = proposal(item)
    sup = '; '.join(f"+{g}: {', '.join(sorted({h[0] for h in hits})) if hits else '✗'}"
                    for g, hits in supported.items())
    r = by_no.get(int(re.sub(r'\D','', item['id'])))
    wn = '/'.join(r['class']) if r and r['class'] else '—'
    tag = verdict.split(' — ')[0]
    out.append(f"| {item['id']} | {item['root']} | {'/'.join(item['whitney_roots_classes']) or '—'} "
               f"| {','.join(item['added'])} | {wn} | {sup} | {tag} |")
out.append('')

# ---- Section 2: Phase-0 GAP/SMEAR ----
out.append('---\n')
out.append('## 2. Phase-0 audit — warnemyr vs local class (23 flags)\n')
out.append('From `scratch/phase0/audit.md` (full warnemyr re-harvest of `1885/`). **GAP** = local `—` but '
           'warnemyr has a class (usually a safe capture-gap fix, e.g. kḷp → I). **SMEAR** = the classes '
           'disagree. ⚠️ **Caveat (DESIGN §6):** these are matched by *homonym number*, which is unreliable '
           'across sources — a SMEAR may be a homonym mis-alignment, not a real class change. Verify by '
           '*feature* (present-stem) before adopting warnemyr.\n')
gaps, smears = [], []
for line in open(P('scratch','phase0','audit.md'), encoding='utf-8'):
    m = re.match(r'\|\s*(\d+)\s*\|\s*(\S+)\s*\|\s*([1-9]?)\s*\|\s*(GAP|SMEAR)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', line)
    if m:
        no, root, hom, typ, loc, wn = m.groups()
        (gaps if typ=='GAP' else smears).append((no, root, hom, loc, wn))
out.append(f'**GAP ({len(gaps)})** — local `—`, warnemyr supplies a class (lean adopt, verify not truly defective):\n')
out.append('| # | root | hom | warnemyr |')
out.append('|--:|---|:-:|:-:|')
for no, root, hom, loc, wn in gaps:
    out.append(f'| {no} | {root} | {hom} | {wn} |')
out.append(f'\n**SMEAR ({len(smears)})** — classes disagree; check homonym alignment + feature first:\n')
out.append('| # | root | hom | local | warnemyr |')
out.append('|--:|---|:-:|:-:|:-:|')
for no, root, hom, loc, wn in smears:
    out.append(f'| {no} | {root} | {hom} | {loc} | {wn} |')
out.append('')

# ---- Section 3: PPP + Section 4: unmatched ----
out.append('---\n')
out.append('## 3. PPP validation — vidyut + corpus vs warnemyr\n')
out.append('`scripts/vidyut_validate_ppp.py` compares vidyut-prakriya\'s generated `kta` against warnemyr\'s '
           'recorded PPP and the DCS corpus. Where warnemyr **disagrees** and the **corpus backs vidyut**, the '
           'naive read is "warnemyr is wrong — correct it." **It is not.** A 3-verifier Sanskritist panel '
           '(13/13 unanimous) found that of the corpus-corroborated mismatches, **none is a warnemyr error**: '
           'every one is either a **homonym artifact** (warnemyr records the PPP of the *glossed* homonym, while '
           'vidyut/DCS surface the *corpus-dominant* same-spelled root because the DCS lemma lumps them) or an '
           '**aniṭ/seṭ doublet** of a single root. So this signal is a homonym/variant detector, **not** a '
           'correction list. **Do not auto-apply it.**\n')

if ppp_val:
    corro = [x for x in ppp_val.get('items', []) if x.get('corpus_backs_vidyut')]
    hom = [x for x in corro if PPP_NOTES.get(x['whitney_no'], ('',))[0] == 'homonym']
    var = [x for x in corro if PPP_NOTES.get(x['whitney_no'], ('',))[0] == 'variant']

    out.append('### 3a. KEEP warnemyr — corpus reflects a *different* homonym (%d)\n' % len(hom))
    out.append('warnemyr is **correct** for the glossed sense; the corpus form belongs to a same-spelled root '
               'the DCS lemma conflates (the √vid know/find, √mṛ die/crush pattern). **Action: do not change** — '
               'and treat each as positive evidence for the homonym split (cf. `crosswalk/token_attribution.json`).\n')
    out.append('| # | root | Whitney | gloss | warnemyr PPP ✓ | corpus PPP | warnemyr = | corpus = |')
    out.append('|--:|---|:-:|---|:-:|:-:|---|---|')
    for x in sorted(hom, key=lambda z: z['whitney_no']):
        no = x['whitney_no']; g = (by_no.get(no, {}) or {}).get('gloss_short', '')
        _, wsrc, ssrc = PPP_NOTES[no]
        out.append('| %s | %s | %s | %s | `%s` | `%s` | %s | %s |'
                   % (no, x['root'], '/'.join(x['class']) or '—', g, x['warnemyr_ppp'],
                      x['dcs_top_ppp'] or ','.join(x['vidyut_ppp']), wsrc, ssrc))
    out.append('')

    out.append('### 3b. Editorial — legitimate aniṭ/seṭ (or -ta/-na) doublet, one root (%d)\n' % len(var))
    out.append('Both forms are valid PPPs of the **same** root and sense; warnemyr\'s is not wrong, just the '
               'alternant the corpus under-represents. **Action: keep warnemyr, or list both** — editorial, '
               'not a correction.\n')
    out.append('| # | root | gloss | warnemyr PPP | corpus PPP | both are |')
    out.append('|--:|---|---|:-:|:-:|---|')
    for x in sorted(var, key=lambda z: z['whitney_no']):
        no = x['whitney_no']; g = (by_no.get(no, {}) or {}).get('gloss_short', '')
        _, wsrc, ssrc = PPP_NOTES[no]
        out.append('| %s | %s | %s | `%s` | `%s` | %s · %s |'
                   % (no, x['root'], g, x['warnemyr_ppp'], x['dcs_top_ppp'] or ','.join(x['vidyut_ppp']), wsrc, ssrc))
    out.append('')
    cc = ppp_val['_meta'].get('counts', {})
    out.append('_Full validator output (%d match · %d mismatch · %d corpus-corroborated, all dispositioned above): '
               '`crosswalk/ppp_validation.json`. The remaining non-corroborated mismatches are warnemyr-only '
               'variants the corpus does not weigh in on._\n'
               % (cc.get('match', 0), cc.get('mismatch', 0), len(corro)))
else:
    out.append('_`crosswalk/ppp_validation.json` not present — run `python scripts/vidyut_validate_ppp.py`._\n')

out.append('### 3c. Open editorial call — √dā `dātta`\n')
out.append('Ids **349/350/351 (√dā)** carry `ppp = [data, datta, dātta]` — the script added **`dātta`** while '
           'canonical **`datta`** was already present. `dātta` (long ā) is a non-standard PPP rendering. '
           '**Decide:** keep `dātta`, or collapse to canonical `datta`.\n')
out.append('---\n')
out.append('## 4. Alias-resolution debt — 9 warnemyr pages unmatched to Whitney numbering\n')
out.append('Vowel-length / bracketed-gloss cases from Phase 0 (see `crosswalk/_unmatched.csv`): '
           '`ṛj, mi, vā(in, dīv, dvar?, hru, hur, med[mid], modṣ`. Need a curated alias to bind each to its '
           'Whitney `whitney_no` (IAST↔SLP1 edge cases, DESIGN §10). Mechanical once the alias is chosen.\n')

# ---- Section 5: MW/Apte homonym alignment ambiguities (Phase 2) ----
align_p = P('crosswalk', 'alignment_review.json')
n_align = 0
if os.path.exists(align_p):
    items = json.load(open(align_p, encoding='utf-8')).get('items', [])
    n_align = len(items)
    out.append('---\n')
    out.append(f'## 5. Phase-2 dictionary alignment — {n_align} ambiguous homonym links\n')
    out.append('MW/Apte share the SLP1 key with several Whitney homonyms and **class cannot disambiguate** '
               'which dict homonym maps to which Whitney sense (DESIGN §6). Resolve by present-stem / gloss, '
               'then Zalizniak. Full data: `crosswalk/alignment_review.json`.\n')
    out.append('| # | root | hub class | src | candidates (L·hom·class·gloss) |')
    out.append('|--:|---|:-:|:-:|---|')
    for it in items:
        cands = '; '.join("L%s·%s·%s·%s" % (c['L'], c['homonym'], '/'.join(c['class']) or '—', c['gloss'][:22])
                          for c in it['candidates'][:3])
        out.append("| %s | %s | %s | %s | %s |" %
                   (it['whitney_no'], it['root'], '/'.join(it['hub_class']) or '—', it['source'], cands))
    out.append('')

with open(P('docs','DECISIONS_NEEDED.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('wrote docs/DECISIONS_NEEDED.md  ·  queue items:', len(queue),
      '· urgent:', len(urgent_items), '· gaps:', len(gaps), '· smears:', len(smears), '· align-ambig:', n_align)
