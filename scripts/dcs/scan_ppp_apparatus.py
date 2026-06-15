"""
scan_ppp_apparatus.py
=====================
Read-only enumerator for "apparatus bleed" in src/app_data.json ppp arrays:
records whose ppp elements carry Whitney's scholarly apparatus (period/source
markers like RV1/E1/C1/S1/B1/K/R/AA, footnote/period digits, uncertainty "?",
"&"/space-joined alternates, "= seq." cross-refs, "adj" usage notes) instead of
a clean participle stem.

This is the deterministic ground-truth scan behind docs/PPP_APPARATUS_BLEED_WORKLIST.md.
It does NOT modify anything. Run it to (re)produce the 39-record catalog; pipe to
a file for the cleanup task:

    python scripts/dcs/scan_ppp_apparatus.py            # human summary
    python scripts/dcs/scan_ppp_apparatus.py --json     # full JSON catalog

NB: this flags ONLY apparatus bleed. The distinct *gloss* bleed (English meaning
words) was already fixed by scripts/dcs/fix_ppp_gloss_bleed.py and is not re-flagged.
"""
import json, sys, re, pathlib

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DATA = ROOT / 'src' / 'app_data.json'
SOURCE = ROOT / 'Whitney_roots_class-PP.txt'

# A "clean form" = transliteration letters only (incl. common IAST diacritics),
# no spaces, digits, or apparatus punctuation.
_CLEAN = re.compile(r"[a-zA-Zāīūṛṝḷḹṅñṭḍṇśṣṃḥ'~-]+")


def is_clean(form):
    f = form.strip()
    return bool(f) and _CLEAN.fullmatch(f) is not None


# Datival infinitives (-e / -aye / -vane) bled into the PPP column along with the
# participle; they pass is_clean() but are NOT past-passive-participles. See
# docs/PPP_APPARATUS_BLEED_WORKLIST.md §2b.
def is_infinitive(form):
    tok = form.split(' ')[0].strip()
    return tok.endswith(('aye', 'vane')) or (tok.endswith('e') and len(tok) > 2)


def categorize(form):
    cats = []
    if is_infinitive(form):
        cats.append('datival-infinitive')
    if ' ' in form:
        cats.append('space-multiword')
    if re.search(r'\d', form):
        cats.append('digit')
    if '?' in form:
        cats.append('uncertainty(?)')
    if '=' in form:
        cats.append('equals(=)')
    if '&' in form:
        cats.append('ampersand(&)')
    if re.search(r'\b[A-Z]{1,3}\d?\b', form) and form not in ('I', 'II', 'III'):
        cats.append('upper-ref(RV/R/K/E/C/S/AA...)')
    if '.' in form:
        cats.append('dot')
    return cats or ['other']


def build_catalog():
    data = json.load(open(APP_DATA, encoding='utf-8'))

    # source line per id (parsed by the leading "N." prefix, not id+9 arithmetic)
    src = {}
    for line in open(SOURCE, encoding='utf-8'):
        m = re.match(r'\s*(\d+)\.\s', line)
        if m:
            src[m.group(1)] = line.rstrip('\n').rstrip('\r')

    catalog = []
    for e in data['lexicon']:
        flagged = [p for p in (e.get('ppp') or []) if not is_clean(p) or is_infinitive(p)]
        if flagged:
            catalog.append({
                'id': e['id'],
                'root': e.get('root'),
                'meaning': e.get('meaning'),
                'ppp': e.get('ppp'),
                'flagged': flagged,
                'categories': sorted({c for p in flagged for c in categorize(p)}),
                'source_line': src.get(e['id'], '<<NOT FOUND>>'),
            })
    return catalog


def main():
    catalog = build_catalog()
    if '--json' in sys.argv:
        by_cat = {}
        for rec in catalog:
            for c in rec['categories']:
                by_cat[c] = by_cat.get(c, 0) + 1
        print(json.dumps({'count': len(catalog), 'by_category': by_cat, 'records': catalog},
                         ensure_ascii=False, indent=1))
        return
    print(f'{len(catalog)} apparatus-bleed records in {APP_DATA.relative_to(ROOT)}\n')
    for r in catalog:
        print(f"{r['id']:>3} {r['root']:<9} {str(r['flagged']):<44} {','.join(r['categories'])}")


if __name__ == '__main__':
    main()
