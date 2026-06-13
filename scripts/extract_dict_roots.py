# -*- coding: utf-8 -*-
"""Phase 2a: extract verbal-root entries from MW and Apte (AP90) -> root inventories.

MW   roots: Cologne entries tagged <info verb="genuineroot"/>; SLP1 = <k1>, homonym = <h>,
            class = '<ab>cl.</ab> N.' (Arabic). Records run <L>...<LEND>.
AP90 roots: Apte entries whose body carries a class marker '{cNc}'; SLP1 = <k1>; homonyms are
            positional (consecutive <L> with the same k1); class from '{cNc}'; gloss from '{@1@}'.

Writes crosswalk/mw_roots.json and crosswalk/apte_roots.json + a parse report. No alignment here.
Reads csl-orig siblings (read-only). UTF-8, no BOM.
"""
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH   = os.path.dirname(BASE)
MW   = os.path.join(GH, 'csl-orig', 'v02', 'mw', 'mw.txt')
AP90 = os.path.join(GH, 'csl-orig', 'v02', 'ap90', 'ap90.txt')
OUT  = os.path.join(BASE, 'crosswalk')

from sanskrit_util import to_roman

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)              # MW <..> tags
    s = re.sub(r'\{[#%@][^}]*[#%@]\}', lambda m: m.group(0)[2:-2], s)  # Apte {#..#}/{%..%}/{@..@}
    s = re.sub(r'\{[^}]*\}', '', s)            # leftover Apte {..}
    s = re.sub(r'[¦|]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip(' ,;:')

def parse_mw():
    raw = open(MW, encoding='utf-8', errors='replace').read()
    roots = []
    for block in raw.split('<LEND>'):
        if 'verb="genuineroot"' not in block:
            continue
        k1 = re.search(r'<k1>([^<]*)<', block)
        if not k1:
            continue
        L  = re.search(r'<L>([^<]*)<', block)
        h  = re.search(r'<h>(\d+)', block)
        # class: digits between 'cl.' and the first Sanskrit form / citation / info tag, so numerals
        # inside <ls> citations (Dhātup./Pāṇ. line numbers) are NOT mis-read as gaṇas.
        cls = []
        m = re.search(r'\bcl\.\s*</ab>(.*)', block) or re.search(r'\bcl\.(.*)', block)
        if m:
            stop = re.search(r'(<s>|<ls\b|<info|<lex|<hom)', m.group(1))
            clause = m.group(1)[:stop.start()] if stop else m.group(1)[:30]
            cls = sorted({int(x) for x in re.findall(r'\b(\d{1,2})\b', clause) if 1 <= int(x) <= 10})
        # gloss: first 'to ...' clause in the body, else snippet after the headword bar
        body = block.split('¦', 1)[1] if '¦' in block else block
        gm = re.search(r'\bto\b[^;]{2,70}', strip_tags(body))
        gloss = gm.group(0).strip() if gm else strip_tags(body)[:60]
        roots.append({'mw_L': L.group(1) if L else None, 'slp1': k1.group(1),
                      'homonym': h.group(1) if h else None,
                      'class': to_roman(cls), 'class_arabic': cls, 'gloss': gloss})
    return roots

def parse_ap90():
    raw = open(AP90, encoding='utf-8', errors='replace').read()
    roots, seen = [], {}
    for block in raw.split('<LEND>'):
        cm = re.search(r'\{c(\d+)c\}', block)      # class marker = root entry
        if not cm:
            continue
        k1 = re.search(r'<k1>([^<]*)<', block)
        if not k1:
            continue
        L  = re.search(r'<L>([^<]*)<', block)
        slp1 = k1.group(1)
        seen[slp1] = seen.get(slp1, 0) + 1         # positional homonym
        cls = sorted({int(x) for x in re.findall(r'\{c(\d+)c\}', block) if 1 <= int(x) <= 10})
        gm = re.search(r'\{@1@\}\s*(.{2,70}?)[;{]', block)
        gloss = strip_tags(gm.group(1)) if gm else ''
        roots.append({'ap_L': L.group(1) if L else None, 'slp1': slp1,
                      'homonym': str(seen[slp1]), 'class': to_roman(cls),
                      'class_arabic': cls, 'gloss': gloss})
    return roots

def main():
    os.makedirs(OUT, exist_ok=True)
    mw, ap = parse_mw(), parse_ap90()
    json.dump(mw, open(os.path.join(OUT,'mw_roots.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(ap, open(os.path.join(OUT,'apte_roots.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    spine = json.load(open(os.path.join(BASE,'scratch','phase0','root_spine.json'), encoding='utf-8'))
    spine_slp1 = {r['root_slp1'] for r in spine if r.get('root_slp1')}   # from the spine; no roots.csv dependency
    mw_slp1, ap_slp1 = {r['slp1'] for r in mw}, {r['slp1'] for r in ap}
    print(f'MW genuine roots : {len(mw)}  (distinct slp1 {len(mw_slp1)})  with class: {sum(1 for r in mw if r["class"])}')
    print(f'AP90 root entries: {len(ap)}  (distinct slp1 {len(ap_slp1)})  with class: {sum(1 for r in ap if r["class"])}')
    print(f'hub slp1 keys    : {len(spine_slp1)}')
    print(f'hub ∩ MW slp1    : {len(spine_slp1 & mw_slp1)}')
    print(f'hub ∩ AP90 slp1  : {len(spine_slp1 & ap_slp1)}')
    print('\nMW samples:')
    for r in mw[:5]: print('  ', r)
    print('AP90 samples:')
    for r in ap[:5]: print('  ', r)

if __name__ == '__main__':
    main()
