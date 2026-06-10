"""
verify_iv_collapse.py
=====================
Reproduces the empirical evidence behind the Phase-8 revert. Run it to see why the
corpus present-stem heuristic was rejected for class assignment.

  H1: The DCS corpus cannot distinguish class I from class VI (accent collapse).
      Both are thematic root+a; they differ only by accent, which DCS forms lack —
      so `carati` (I) and `tudati` (VI) are written identically.
  H2: Short roots match promiscuously in the Grammar text (English words / substrings),
      producing spurious "Grammar confirms class X" signals.

  python scripts/dcs/verify_iv_collapse.py
"""
import sys, re, sqlite3, pathlib
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[2]   # WhitneyRoots/
DCS_DB = ROOT.parent / 'VisualDCS' / 'src' / 'DCS-data-2026' / 'dcs_full.sqlite'
GTEXT = (ROOT / 'src' / 'wg_text.txt').read_text(encoding='utf-8')

print('=' * 70)
print('H1: present forms of known class-I (car/jīv/nam) vs class-VI (tud/viś/diś)')
print('    If I and VI look identical, the corpus cannot assign the class.')
print('=' * 70)
con = sqlite3.connect(str(DCS_DB))
cur = con.cursor()
for lemma in ['car', 'jīv', 'nam', 'tud', 'viś', 'diś', 'likh', 'kṣip']:
    cur.execute("""SELECT DISTINCT form FROM token
                   WHERE lemma=? AND feat_tense='Pres' AND feat_verbform IS NULL LIMIT 8""",
                (lemma,))
    forms = [r[0] for r in cur.fetchall()]
    print(f'  {lemma:6s}: {forms}')

print()
print('=' * 70)
print('H2: short-root match counts in the Grammar text (and in the VI chapter)')
print('    VI chapter char range: 638796–645862')
print('=' * 70)
WORD_CHARS = r'a-zāīūṛḷṃḥṭḍṇśṣḻṁḥñçṅṃḫǵŕÇ'
def pat_for(root):
    esc = re.escape(root.replace('ś', 'ç'))
    return re.compile(rf'√{esc}(?![{WORD_CHARS}])|(?<![{WORD_CHARS}]){esc}(?![{WORD_CHARS}])', re.UNICODE)

VI_START, VI_END = 638796, 645862
for root in ['car', 'jīv', 'nam', 'as', 'i', 'labh']:
    hits = list(pat_for(root).finditer(GTEXT))
    hits_vi = [m for m in hits if VI_START <= m.start() < VI_END]
    print(f'\n  root {root!r}: {len(hits)} total hits, {len(hits_vi)} in VI chapter')
    for m in hits_vi[:3]:
        s = GTEXT[max(0, m.start() - 40):m.start() + 40].replace('\n', ' ')
        print(f'      …{s}…')
con.close()

print('\nConclusion: I and VI surface-forms coincide (H1); short roots match English '
      'words and stray text (H2). Corpus class signal is a prompt to look, not proof.')
