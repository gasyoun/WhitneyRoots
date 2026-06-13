# -*- coding: utf-8 -*-
"""Emit the FAIR crosswalk dataset (Layer-1 root hub) from the Phase-0 spine.

Reads  scratch/phase0/root_spine.json  (warnemyr-derived, 939 records, 930 keyed)
Writes crosswalk/:
  roots.csv               flat table, one row per Whitney root-sense (keyed on whitney_no)
  root_class.csv          long/normalized: (whitney_no, gana, certainty)
  roots.sqlite            same two tables, queryable
  roots.ttl               OntoLex-Lemon + thin wr: namespace (Turtle/RDF)
  roots.csv-metadata.json CSVW descriptor bridging roots.csv <-> RDF
  _unmatched.csv          the records with no whitney_no (alias-resolution debt)

Per DESIGN.md §4/§7. CC BY-SA 4.0. No network. UTF-8, never utf-8-sig (no BOM).
"""
import sys, os, re, json, csv, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPINE = os.path.join(BASE, 'scratch', 'phase0', 'root_spine.json')
OUT   = os.path.join(BASE, 'crosswalk')
URI   = 'https://w3id.org/whitneyroots/'          # persistent base (to be registered)

from sanskrit_util import to_slp1   # shared IAST→SLP1 transcoder (single source of truth)

ROMAN_ORDER = {r:i for i,r in enumerate(['I','II','III','IV','V','VI','VII','VIII','IX','X'])}

def forms_str(c):
    return '|'.join('%s:%s' % (x.get('form',''), x.get('n','')) for x in (c.get('attested_forms') or []))

def sect_str(r):
    return '|'.join('%s:%d-%d' % (e['category'], e['section_lo'], e['section_hi'])
                    for e in (r.get('whitney_sections') or []))

def load():
    recs = json.load(open(SPINE, encoding='utf-8'))
    keyed   = [r for r in recs if 'whitney_no' in r]
    unkeyed = [r for r in recs if 'whitney_no' not in r]
    keyed.sort(key=lambda r: r['whitney_no'])
    return keyed, unkeyed

def write_utf8(path):
    return open(path, 'w', encoding='utf-8', newline='')

def emit_csv(keyed):
    cols = ['whitney_no','root_iast','root_slp1','homonym','class','class_uncertain',
            'gloss_short','ppp','period_tags','grouped','warnemyr_url',
            'dcs_freq','dcs_rank','dcs_class_tag','attested_forms',
            'mw_id','apte_id','senses','section_refs']
    with write_utf8(os.path.join(OUT,'roots.csv')) as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in keyed:
            c = r.get('corpus') or {}
            d = r.get('dict') or {}
            w.writerow([
                r['whitney_no'], r['root_iast'], (r.get('root_slp1') or to_slp1(r['root_iast'])), r.get('homonym') or '',
                '|'.join(r.get('class',[])), '|'.join(r.get('class_uncertain',[])),
                r.get('gloss_short',''), r.get('ppp',''), '|'.join(r.get('period_tags',[])),
                '1' if r.get('grouped') else '0', r.get('warnemyr_url',''),
                c.get('dcs_freq',''), c.get('dcs_rank') or '',
                '|'.join(str(x) for x in (c.get('dcs_class_tag') or [])), forms_str(c),
                d.get('mw_id') or '', d.get('apte_id') or '', ' / '.join(d.get('senses') or []),
                sect_str(r),
            ])
    # long/normalized class table
    with write_utf8(os.path.join(OUT,'root_class.csv')) as f:
        w = csv.writer(f); w.writerow(['whitney_no','gana','certainty'])
        for r in keyed:
            for g in r.get('class',[]):            w.writerow([r['whitney_no'], g, 'certain'])
            for g in r.get('class_uncertain',[]):  w.writerow([r['whitney_no'], g, 'uncertain'])

def emit_unmatched(unkeyed):
    with write_utf8(os.path.join(OUT,'_unmatched.csv')) as f:
        w = csv.writer(f); w.writerow(['root_iast_raw','warnemyr_url','class'])
        for r in unkeyed:
            w.writerow([r.get('root_iast',''), r.get('warnemyr_url',''), '|'.join(r.get('class',[]))])

def emit_sqlite(keyed):
    p = os.path.join(OUT,'roots.sqlite')
    if os.path.exists(p): os.remove(p)
    con = sqlite3.connect(p); cur = con.cursor()
    cur.execute("""CREATE TABLE root(
        whitney_no INTEGER PRIMARY KEY, root_iast TEXT, root_slp1 TEXT, homonym TEXT,
        class TEXT, class_uncertain TEXT, gloss_short TEXT, ppp TEXT,
        period_tags TEXT, grouped INTEGER, warnemyr_url TEXT,
        dcs_freq INTEGER, dcs_rank INTEGER, dcs_class_tag TEXT, attested_forms TEXT,
        mw_id TEXT, apte_id TEXT, senses TEXT, section_refs TEXT)""")
    cur.execute("CREATE TABLE root_class(whitney_no INTEGER, gana TEXT, certainty TEXT)")
    cur.execute("""CREATE TABLE root_section(whitney_no INTEGER, category TEXT,
        section_lo INTEGER, section_hi INTEGER, chapter TEXT, wikisource_url TEXT)""")
    for r in keyed:
        c = r.get('corpus') or {}
        d = r.get('dict') or {}
        cur.execute("INSERT INTO root VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            r['whitney_no'], r['root_iast'], (r.get('root_slp1') or to_slp1(r['root_iast'])), r.get('homonym') or '',
            '|'.join(r.get('class',[])), '|'.join(r.get('class_uncertain',[])),
            r.get('gloss_short',''), r.get('ppp',''), '|'.join(r.get('period_tags',[])),
            1 if r.get('grouped') else 0, r.get('warnemyr_url',''),
            c.get('dcs_freq'), c.get('dcs_rank'),
            '|'.join(str(x) for x in (c.get('dcs_class_tag') or [])), forms_str(c),
            d.get('mw_id'), d.get('apte_id'), ' / '.join(d.get('senses') or []), sect_str(r)))
        for e in (r.get('whitney_sections') or []):
            cur.execute("INSERT INTO root_section VALUES(?,?,?,?,?,?)",
                        (r['whitney_no'], e['category'], e['section_lo'], e['section_hi'], e['chapter'], e['url']))
        for g in r.get('class',[]):           cur.execute("INSERT INTO root_class VALUES(?,?,?)", (r['whitney_no'], g, 'certain'))
        for g in r.get('class_uncertain',[]): cur.execute("INSERT INTO root_class VALUES(?,?,?)", (r['whitney_no'], g, 'uncertain'))
    con.commit(); con.close()

def ttl_esc(s):
    return s.replace('\\','\\\\').replace('"','\\"')

def emit_ttl(keyed):
    PER = {'RV':'rigvedic','AV':'atharvavedic','V':'vedic','B':'brahmana','S':'sutra','E':'epic','C':'classical'}
    lines = [
        '@prefix wr:       <%sns#> .' % URI,
        '@prefix root:     <%sroot/> .' % URI,
        '@prefix ontolex:  <http://www.w3.org/ns/lemon/ontolex#> .',
        '@prefix lexinfo:  <http://www.lexinfo.net/ontology/3.0/lexinfo#> .',
        '@prefix dct:      <http://purl.org/dc/terms/> .',
        '@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .',
        '@prefix skos:     <http://www.w3.org/2004/02/skos/core#> .',
        '@prefix cito:     <http://purl.org/spar/cito/> .',
        '@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .',
        '',
        '# Whitney-Root crosswalk, Layer-1 hub. Source: Whitney Roots via L. Warnemyr (warnemyr.com/skrgram).',
        '# Vocabulary: OntoLex-Lemon + thin wr: namespace (gana, period, uncertainty). CC BY-SA 4.0.',
        'wr:Root rdfs:subClassOf ontolex:LexicalEntry .',
        'wr:gana a rdfs:Property ; rdfs:comment "Sanskrit present-system class (gaṇa), Roman I–X." .',
        'wr:ganaUncertain a rdfs:Property ; rdfs:comment "Gaṇa marked uncertain (warnemyr ‘?’)." .',
        'wr:period a rdfs:Property ; rdfs:comment "Diachronic attestation tag (RV/AV/V/B/S/E/C)." .',
        'wr:dcsFreq a rdfs:Property ; rdfs:comment "DCS corpus token frequency (lemma-level)." .',
        'wr:dcsClassTag a rdfs:Property ; rdfs:comment "DCS lexicon class tag — METADATA, not an asserted gaṇa." .',
        '',
    ]
    for r in keyed:
        u = 'root:%d' % r['whitney_no']
        iast, slp1 = ttl_esc(r['root_iast']), ttl_esc((r.get('root_slp1') or to_slp1(r['root_iast'])))
        lines.append('%s a wr:Root ;' % u)
        lines.append('  rdfs:label "%s"@sa-Latn ;' % iast)
        lines.append('  ontolex:canonicalForm [ ontolex:writtenRep "%s"@sa-Latn, "%s"^^wr:slp1 ] ;' % (iast, slp1))
        if r.get('homonym'): lines.append('  wr:homonym "%s" ;' % ttl_esc(str(r['homonym'])))
        for g in r.get('class',[]):           lines.append('  wr:gana "%s" ;' % g)
        for g in r.get('class_uncertain',[]): lines.append('  wr:ganaUncertain "%s" ;' % g)
        if r.get('gloss_short'): lines.append('  rdfs:comment "%s"@en ;' % ttl_esc(r['gloss_short']))
        if r.get('ppp'):         lines.append('  wr:ppp "%s"@sa-Latn ;' % ttl_esc(r['ppp']))
        for p in r.get('period_tags',[]):
            if p in PER: lines.append('  wr:period "%s" ;' % PER[p])
        c = r.get('corpus') or {}
        if c.get('dcs_lemma') and c.get('dcs_status') in ('matched','homonym_shared'):
            lines.append('  wr:dcsLemma "%s"@sa-Latn ;' % ttl_esc(c['dcs_lemma']))
            lines.append('  wr:dcsFreq %d ;' % (c.get('dcs_freq') or 0))
            if c.get('dcs_rank'): lines.append('  wr:dcsRank %d ;' % c['dcs_rank'])
            for t in (c.get('dcs_class_tag') or []):
                lines.append('  wr:dcsClassTag "%s" ;' % ttl_esc(str(t)))
        d = r.get('dict') or {}
        if d.get('mw_id'):   lines.append('  wr:mwId "%s" ;' % ttl_esc(str(d['mw_id'])))
        if d.get('apte_id'): lines.append('  wr:apteId "%s" ;' % ttl_esc(str(d['apte_id'])))
        for sense in (d.get('senses') or []):
            lines.append('  skos:definition "%s"@en ;' % ttl_esc(sense))
        for e in (r.get('whitney_sections') or []):   # root -> form-category -> § (Layer 2)
            lines.append('  cito:isExplainedBy <%s> ;' % e['url'])
        lines.append('  dct:source <https://warnemyr.com/skrgram/%s> .' % r.get('warnemyr_url',''))
        lines.append('')
    with open(os.path.join(OUT,'roots.ttl'),'w',encoding='utf-8') as f:
        f.write('\n'.join(lines))

def emit_csvw():
    desc = {
        "@context": "http://www.w3.org/ns/csvw",
        "url": "roots.csv",
        "dc:title": "Whitney Sanskrit verbal roots — Layer-1 crosswalk hub",
        "dc:license": {"@id": "https://creativecommons.org/licenses/by-sa/4.0/"},
        "dc:source": "W. D. Whitney, The Roots…, digitised by L. Warnemyr (warnemyr.com/skrgram)",
        "tableSchema": {
            "aboutUrl": URI + "root/{whitney_no}",
            "primaryKey": "whitney_no",
            "columns": [
                {"name":"whitney_no","datatype":"integer","titles":"Whitney root-sense number"},
                {"name":"root_iast","datatype":"string","titles":"Root (IAST)"},
                {"name":"root_slp1","datatype":"string","titles":"Root (SLP1)"},
                {"name":"homonym","datatype":"string","titles":"Homonym index"},
                {"name":"class","datatype":"string","separator":"|","titles":"Gaṇa(s), certain"},
                {"name":"class_uncertain","datatype":"string","separator":"|","titles":"Gaṇa(s), uncertain"},
                {"name":"gloss_short","datatype":"string","titles":"Short gloss"},
                {"name":"ppp","datatype":"string","titles":"Past passive participle"},
                {"name":"period_tags","datatype":"string","separator":"|","titles":"Diachronic tags"},
                {"name":"grouped","datatype":"boolean","titles":"Shared a warnemyr page"},
                {"name":"warnemyr_url","datatype":"string","titles":"Source page"},
                {"name":"dcs_freq","datatype":"integer","titles":"DCS corpus frequency"},
                {"name":"dcs_rank","datatype":"integer","titles":"DCS frequency rank"},
                {"name":"dcs_class_tag","datatype":"string","separator":"|","titles":"DCS lexicon class tag (metadata, not asserted)"},
                {"name":"attested_forms","datatype":"string","titles":"Top attested forms (form:count)"},
                {"name":"mw_id","datatype":"string","titles":"Monier-Williams entry id (Cologne L-number)"},
                {"name":"apte_id","datatype":"string","titles":"Apte (AP90) entry id (Cologne L-number)"},
                {"name":"senses","datatype":"string","titles":"Short senses from MW / Apte"},
                {"name":"section_refs","datatype":"string","titles":"Form-category -> Whitney §-range (category:lo-hi)"},
            ],
        },
    }
    with open(os.path.join(OUT,'roots.csv-metadata.json'),'w',encoding='utf-8') as f:
        json.dump(desc, f, ensure_ascii=False, indent=2)

def main():
    os.makedirs(OUT, exist_ok=True)
    keyed, unkeyed = load()
    emit_csv(keyed); emit_unmatched(unkeyed); emit_sqlite(keyed); emit_ttl(keyed); emit_csvw()
    # ---- self-validation ----
    with open(os.path.join(OUT,'roots.csv'), encoding='utf-8') as f:
        csv_rows = sum(1 for _ in f) - 1
    con = sqlite3.connect(os.path.join(OUT,'roots.sqlite'))
    sq_rows = con.execute("SELECT COUNT(*) FROM root").fetchone()[0]
    cls_rows = con.execute("SELECT COUNT(*) FROM root_class").fetchone()[0]
    con.close()
    assert csv_rows == len(keyed) == sq_rows, (csv_rows, len(keyed), sq_rows)
    for path in ('roots.csv','roots.sqlite','roots.ttl','roots.csv-metadata.json'):
        with open(os.path.join(OUT,path),'rb') as fb:
            assert fb.read(3).hex() != 'efbbbf', 'BOM in '+path
    print(f'keyed={len(keyed)}  unmatched={len(unkeyed)}  csv_rows={csv_rows}  sqlite_rows={sq_rows}  class_rows={cls_rows}')
    print('spot SLP1:', [(w, to_slp1(w)) for w in ('kḷp','kṛ','aṃh','śī','bhū','hṛ')])
    # optional rdflib validation
    try:
        import rdflib
        g = rdflib.Graph(); g.parse(os.path.join(OUT,'roots.ttl'), format='turtle')
        print('rdflib: parsed OK, triples =', len(g))
    except ImportError:
        print('rdflib: not installed — skipped Turtle validation (syntax written by template)')

if __name__ == '__main__':
    main()
