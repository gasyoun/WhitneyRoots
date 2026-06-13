# -*- coding: utf-8 -*-
"""Phase 0 engine: parse cached warnemyr root pages -> structured records + class-gap audit.

Reads whatever is present in wn_cache/ (so it works on a pilot subset or the full 937),
joins each page to the local Whitney numbering by (root, homonym), and flags where the
local class disagrees with warnemyr (capture gaps like kḷp, union-smears like 2 as / kṛ).
"""
import sys, re, html, json, os, glob
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
from sanskrit_util import to_slp1

BASE  = r'C:/Users/user/Documents/GitHub/WhitneyRoots'
# Phase 0 source-of-truth = the full local warnemyr mirror in 1885/ (939 root pages),
# not the partial scratch harvest. Glob restricts to root_*.html (skips index/jpg/css).
CACHE = BASE + '/1885'
INDEX = BASE + '/scratch/phase0/wn_index.tsv'
LOCAL = BASE + '/Whitney_roots_class-PP.txt'
OUT_SPINE = BASE + '/scratch/phase0/root_spine.json'
OUT_AUDIT = BASE + '/scratch/phase0/audit.md'

ROMAN = r'(?:X|IX|VI{0,3}|IV|V|I{1,3})'   # Gaṇa I–X, longest-match order

def clean(s):
    s = re.sub(r'(?is)<head.*?</head>', ' ', s)
    s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?is)<[^>]+>', ' ', s)
    s = html.unescape(s).replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def norm(root):
    return re.sub(r'[√\s]', '', root).strip()

def load_index():
    idx = {}
    for line in open(INDEX, encoding='utf-8'):
        if '\t' in line:
            u, a = line.rstrip('\n').split('\t', 1)
            idx[u] = a
    return idx

def load_local():
    """Parse Whitney_roots_class-PP.txt -> {(root,homonym): {no, class_local, gloss}}."""
    loc = {}
    for line in open(LOCAL, encoding='utf-8'):
        m = re.match(r'\s*(\d+)\.\s+(.*\S)\s*$', line)
        if not m:
            continue
        no, rest = m.group(1), m.group(2)
        hm = re.match(r'([1-9])\s+(.*)$', rest)
        homonym = hm.group(1) if hm else None
        if hm:
            rest = hm.group(2)
        rm = re.match(r'√?\s*(\S+)\s+(.*)$', rest)
        if not rm:
            continue
        root, after = norm(rm.group(1)), rm.group(2)
        cm = re.match(r'(\S+)\s+(.*)$', after)
        ctok = cm.group(1) if cm else '—'
        cls = [] if ctok in ('—', '-', '?') else [c for c in ctok.split('/') if re.fullmatch(ROMAN, c)]
        loc[(root, homonym)] = {'no': int(no), 'class_local': cls, 'class_local_raw': ctok}
    return loc

def parse_classes(txt):
    """Gaṇa(s) = romans written 'I .' inside the Present section. The space BEFORE the period
    distinguishes a class ('V . akṣṇoti') from a period tag ('V.+', 'V.B.S.' — no space)."""
    m = re.search(r'\bPresent\b', txt)
    if not m:
        return [], []
    seg = txt[m.end():]
    for nl in ('Future', 'Aorist', 'Perfect', 'Causative', 'Desiderative',
               'Intensive', 'Verbal Nouns', 'Derivatives', 'Meanings'):
        k = seg.find(nl)
        if k >= 0:
            seg = seg[:k]
    out, seen = [], set()
    for c in re.findall(r'\b(' + ROMAN + r')\s+\.', seg):
        if c not in seen:
            seen.add(c)
            out.append(c)
    # warnemyr marks an UNCERTAIN gaṇa as 'IV ?' (question mark, no period). Keep these
    # out of `class` (conservative — never assert an uncertain class) but don't lose them.
    unc = []
    for c in re.findall(r'\b(' + ROMAN + r')\s+\?', seg):
        if c not in seen and c not in unc:
            unc.append(c)
    return out, unc

def section(txt, label, nexts):
    i = txt.find(label)
    if i < 0:
        return ''
    j = len(txt)
    for nl in nexts:
        k = txt.find(nl, i + len(label))
        if k >= 0:
            j = min(j, k)
    return re.sub(r'\s+', ' ', txt[i + len(label):j]).strip(' :,')

NX = {'Present': ['Future', 'Aorist', 'Perfect'], 'Future': ['Aorist', 'Perfect', 'Causative'],
      'Aorist': ['Perfect', 'Causative'], 'Perfect': ['Causative', 'Desiderative', 'Verbal'],
      'Causative': ['Desiderative', 'Intensive', 'Verbal'], 'Desiderative': ['Intensive', 'Verbal'],
      'Intensive': ['Verbal', 'Derivatives'], 'Verbal Nouns': ['Derivatives', 'Meanings'],
      'Derivatives': ['Meanings']}

# Aorist sub-type tokens, matched space-insensitively (warnemyr writes '-sa- Ao' but '-s-Ao').
AOR_SUB = [('√-Ao', 'aor_root'), ('ThAo', 'aor_a'), ('RAo', 'aor_redup'),
           ('-siṣ-Ao', 'aor_sis'), ('-iṣ-Ao', 'aor_is'), ('-sa-Ao', 'aor_sa'), ('-s-Ao', 'aor_s')]

def detect_forms(full):
    """Concordance category-keys this root has a form of, detected on the FULL (untruncated)
    section text. Conservative: only categories warnemyr's paradigm reliably marks (no guessing
    of precative/conditional/pluperfect, which warnemyr does not flag). Present-gaṇa categories
    are NOT here — they come from `class` via gana_present in build_form_section_edges."""
    out = []
    P = full.get('Present', '')
    if P:
        out.append('present_participle')                 # participles are made from every present-stem
    if 'Passive' in P:
        out.append('passive_present')
    if full.get('Perfect', '').strip():
        out += ['perfect', 'perfect_participle']
    ao = full.get('Aorist', '')
    if ao.strip():
        out.append('aor_class')
        aon = re.sub(r'\s+', '', ao)                     # '-sa- Ao' -> '-sa-Ao'; 'Th Ao' -> 'ThAo'
        for tok, cat in AOR_SUB:
            if tok in aon:
                out.append(cat)
    fut = full.get('Future', '')
    if fut.strip():
        out += ['future_participle', 's_future']
        if 'Periphrastic' in fut:
            out.append('periphrastic_future')
    if full.get('Causative', '').strip():
        out.append('causative')
    if full.get('Desiderative', '').strip():
        out.append('desiderative')
    if full.get('Intensive', '').strip():
        out.append('intensive')
    vn = full.get('Verbal Nouns', '')
    if 'PPP' in vn:
        out += ['ppp', 'past_active_participle']         # past active ptcp (-tavant) is made from the PPP (§959)
    if re.search(r'\bInf\b', vn):
        out.append('infinitive')
    if re.search(r'\b2 Abs\b', vn):
        out.append('adverbial_gerund')
    if re.search(r'\b(1 Abs|Abs|Ger)\b', vn):
        out.append('gerund')
    if re.search(r'(tavya|anīya)', vn):
        out.append('gerundive')
    seen, res = set(), []
    for c in out:
        if c not in seen:
            seen.add(c); res.append(c)
    return res

def parse_page(txt):
    cls, cls_unc = parse_classes(txt)
    rec = {'class': cls}
    if cls_unc:
        rec['class_uncertain'] = cls_unc
    head = txt.split('Present')[0]
    gm = re.search(r'[“‘"\']([^”’"\']{2,60})[”’"\']', head)
    rec['gloss_short'] = gm.group(1) if gm else ''
    full = {}
    for lab, nxs in NX.items():
        v = section(txt, lab, nxs)
        if v:
            full[lab] = v
    rec['paradigm_raw'] = {lab: v[:240] for lab, v in full.items()}   # truncated for storage/display only
    rec['forms_present'] = detect_forms(full)                         # detection runs on FULL text
    # period tags only from the paradigm region (Present..Meanings), never the English gloss/Meanings prose
    pstart, mend = txt.find('Present'), txt.find('Meanings')
    region = txt[(pstart if pstart >= 0 else 0):(mend if mend >= 0 else len(txt))]
    rec['period_tags'] = sorted(set(re.findall(r'\b(RV|AV|V|B|S|E|C)\.', region)))
    vn = section(txt, 'Verbal Nouns', ['Derivatives', 'Meanings'])
    pm = re.search(r'PPP\s*:?\s*(\S+)', vn)
    rec['ppp'] = pm.group(1) if pm else ''
    return rec

def main():
    idx, loc = load_index(), load_local()
    pages = sorted(glob.glob(CACHE + '/root_*.html'))
    recs, audit = [], []
    matched = 0
    for path in pages:
        url = os.path.basename(path)
        anchor = idx.get(url, '')
        hm = re.match(r'\s*([1-9])\s+(.*)', anchor)
        homonym = hm.group(1) if hm else None
        rest = hm.group(2) if hm else anchor
        primary = norm(re.sub(r'\(.*?\)', '', rest.split(',')[0]))
        try:
            raw = open(path, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        if len(raw) < 400:
            continue  # empty/failed fetch
        rec = parse_page(clean(raw))
        rec.update({'root_iast': primary, 'root_slp1': to_slp1(primary), 'homonym': homonym,
                    'warnemyr_url': url, 'grouped': ',' in anchor})
        l = loc.get((primary, homonym))
        if l:
            matched += 1
            rec['whitney_no'] = l['no']
            lc, wc = l['class_local'], rec['class']
            if not lc and wc:
                audit.append((l['no'], primary, homonym, 'GAP', '—', '/'.join(wc)))
            elif lc and wc and not (set(lc) & set(wc)):
                audit.append((l['no'], primary, homonym, 'SMEAR', '/'.join(lc), '/'.join(wc)))
        recs.append(rec)
    recs.sort(key=lambda r: r.get('whitney_no', 9999))
    json.dump(recs, open(OUT_SPINE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    audit.sort()
    with open(OUT_AUDIT, 'w', encoding='utf-8') as f:
        f.write('# Phase 0 — class-gap audit (local Whitney vs warnemyr)\n\n')
        f.write(f'Pages parsed: {len(recs)} · matched to numbering: {matched} · flags: {len(audit)}\n\n')
        f.write('| # | root | hom | type | local | warnemyr |\n|--:|---|:-:|---|:-:|:-:|\n')
        for no, r, h, t, lc, wc in audit:
            f.write(f'| {no} | {r} | {h or ""} | {t} | {lc} | {wc} |\n')
    print(f'parsed={len(recs)} matched={matched} flags={len(audit)}')
    for no, r, h, t, lc, wc in audit[:25]:
        print(f'  #{no} {r}{("/"+h) if h else ""}: {t}  local={lc} -> warnemyr={wc}')

if __name__ == '__main__':
    main()
