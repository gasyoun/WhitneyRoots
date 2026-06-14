/* Whitney Reader — a pure view over the crosswalk (DESIGN §8). No new data. */
'use strict';

const DEFAULT_PASSAGE = 'sañjaya uvāca | dharmaṃ kṛtvā arjunaḥ gacchati | sukhaṃ bhavati ||';
const DEVA_PASSAGE = 'सञ्जय उवाच । धर्मं कृत्वा अर्जुनः गच्छति । सुखं भवति ॥';
let DATA = null;
let PARADIGMS = {};   // whitney_no -> {root, paradigms:[…]} from src/paradigms.json (vidyut, optional)

const $ = (id) => document.getElementById(id);
function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}
// --- Devanagari → IAST, so Devanagari passages resolve through the same (IAST-built) index ---
const DV_VOWEL = { 'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au' };
const DV_MATRA = { 'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ', 'ॢ': 'ḷ', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au' };
const DV_CONS = { 'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ', 'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'ñ', 'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'ś', 'ष': 'ṣ', 'स': 's', 'ह': 'h', 'ळ': 'ḷ' };
const DV_MARK = { 'ं': 'ṃ', 'ः': 'ḥ', 'ँ': 'ṃ' };
const VIRAMA = '्';
function deva2iast(s) {
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (DV_CONS[ch] != null) {
      out += DV_CONS[ch];
      const nx = s[i + 1];
      if (nx === VIRAMA) { i++; }                         // bare consonant (conjunct)
      else if (DV_MATRA[nx] != null) { out += DV_MATRA[nx]; i++; }
      else { out += 'a'; }                                // inherent vowel
    } else if (DV_VOWEL[ch] != null) { out += DV_VOWEL[ch]; }
    else if (DV_MARK[ch] != null) { out += DV_MARK[ch]; }
    else if (ch === 'ऽ') { /* avagraha — drop */ }
    else { out += ch; }
  }
  return out;
}
const DEVA_RE = /[ऀ-ॿ]/;
// Mirror of scripts/sanskrit_util.py norm()/nfold(). norm() = EXACT key (transliterate Devanagari,
// NFD, drop marks, NFC, lower). nfold() additionally folds every nasal → 'n' for the recall fallback.
function norm(s) {
  s = s || '';
  if (DEVA_RE.test(s)) s = deva2iast(s);
  return s.normalize('NFD').replace(/\p{Mn}/gu, '').normalize('NFC').toLowerCase().trim();
}
function nfold(s) {
  return norm(s).replace(/[mn]/g, 'n');
}
const isWord = (s) => /\p{L}/u.test(s);

// Two-tier: exact form_index first (keeps am/an, kram/kṛ distinct), then the nasal-folded
// fold_alias as a fallback so anusvāra spellings (kāṃkṣ-) still reach homorganic forms (kāṅkṣ-).
function candidatesFor(word) {
  const ex = DATA.form_index[norm(word)];
  if (Array.isArray(ex) && ex.length) return ex.map(String);
  const keys = DATA.fold_alias[nfold(word)];
  if (!Array.isArray(keys)) return [];
  const seen = {}, out = [];
  keys.forEach((k) => (DATA.form_index[k] || []).forEach((n) => {
    if (!seen[n]) { seen[n] = 1; out.push(n); }
  }));
  out.sort((a, b) => ((DATA.roots[b] || {}).freq || 0) - ((DATA.roots[a] || {}).freq || 0));
  return out.map(String);
}

/* ---------- passage rendering ---------- */
let selectedEl = null;

function renderTokens() {
  const text = $('passage').value;
  const box = $('tokens');
  box.textContent = '';
  const parts = text.split(/([^\p{L}\p{M}]+)/u).filter((p) => p.length);
  let firstResolved = null;
  parts.forEach((part) => {
    if (!isWord(part)) { box.appendChild(el('span', 'sep', part)); return; }
    const cands = candidatesFor(part);
    const cls = cands.length === 0 ? 'unresolved' : cands.length === 1 ? 'resolved' : 'multi';
    const span = el('span', 'tok ' + cls, part);
    span.tabIndex = 0;
    const pick = () => selectToken(span, part, cands);
    span.addEventListener('click', pick);
    span.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') pick(); });
    box.appendChild(span);
    if (!firstResolved && cands.length) firstResolved = span;
  });
  if (firstResolved) firstResolved.click();
}

function selectToken(span, word, cands) {
  if (selectedEl) selectedEl.classList.remove('sel');
  selectedEl = span;
  span.classList.add('sel');
  renderPanel(word, cands, cands[0]);
}

/* ---------- analysis panel ---------- */
function renderPanel(word, cands, chosenNo) {
  const panel = $('panel');
  panel.textContent = '';

  const line = el('div', 'tok-line');
  line.appendChild(document.createTextNode('Token '));
  line.appendChild(el('b', null, word));
  panel.appendChild(line);

  if (!cands.length) {
    panel.appendChild(degrade('No verbal root resolved. Likely a noun, name, or indeclinable, '
      + 'or a finite form not among this root’s DCS-attested top forms.'));
    return;
  }
  if (cands.length > 1) {
    const ch = el('div', 'chooser');
    cands.forEach((no) => {
      const r = DATA.roots[no];
      const chip = el('span', 'chip' + (no === chosenNo ? ' on' : ''),
        '√' + r.root + (r.class.length ? ' · ' + r.class.join('/') : ''));
      chip.title = r.gloss || '';
      chip.addEventListener('click', () => renderPanel(word, cands, no));
      ch.appendChild(chip);
    });
    panel.appendChild(ch);
  }
  panel.appendChild(rootCard(DATA.roots[chosenNo], chosenNo));
}

function rootCard(r, no) {
  const card = document.createDocumentFragment();

  const head = el('div', 'root-head');
  head.appendChild(el('span', 'rt', r.root));
  head.appendChild(el('span', 'wn', '#' + no));
  (r.class || []).forEach((g) => head.appendChild(el('span', 'gana', g)));
  (r.unc || []).forEach((g) => { const c = el('span', 'gana unc', g + ' ?'); c.title = 'uncertain gaṇa (warnemyr)'; head.appendChild(c); });
  card.appendChild(head);
  if (r.gloss) card.appendChild(el('p', 'gloss', r.gloss));

  // HERO — Why this form?
  const why = el('div', 'sect hero');
  why.appendChild(el('h3', null, 'Why this form? — Whitney §§'));
  if (r.sections && r.sections.length) {
    const list = el('div', 'why');
    r.sections.forEach((s) => {
      const a = el('a');
      a.href = s.url; a.target = '_blank'; a.rel = 'noopener';
      a.appendChild(el('span', 'lab', s.label));
      a.appendChild(el('span', 'ss', '§§' + s.lo + '–' + s.hi));
      list.appendChild(a);
    });
    why.appendChild(list);
  } else {
    why.appendChild(degrade('§ not yet mapped for this root.'));
  }
  card.appendChild(why);

  // Paradigm (vidyut-generated, display-only) — collapsed; absent if no agreeing-gaṇa paradigm
  const pdata = PARADIGMS[no];
  if (pdata && pdata.paradigms && pdata.paradigms.length) card.appendChild(paradigmSection(pdata));

  // Dictionary
  const dic = el('div', 'sect');
  dic.appendChild(el('h3', null, 'Dictionary'));
  if (r.senses && r.senses.length) {
    dic.appendChild(el('p', 'senses', r.senses.join('  ·  ')));
  } else {
    dic.appendChild(el('p', 'gloss', '— no linked MW/Apte sense'));
  }
  const ids = [];
  if (r.mw_id) ids.push('MW L' + r.mw_id);
  if (r.apte_id) ids.push('Apte L' + r.apte_id);
  if (ids.length) dic.appendChild(el('p', 'prov', ids.join('  ·  ')));
  card.appendChild(dic);

  // Corpus — collapsed
  const det = el('details', 'corpus');
  det.appendChild(el('summary', null, 'Corpus (DCS)'));
  let freq;
  if (r.freq == null) freq = 'not attested as a verb in DCS';
  else if (r.freq_sense != null)   // per-sense count recovered from DCS lemma_id separation
    freq = r.freq_sense.toLocaleString() + ' tokens (this sense)  ·  ' + r.freq.toLocaleString() + ' for the lemma';
  else freq = r.freq.toLocaleString() + ' tokens' + (r.rank ? '  ·  rank #' + r.rank : '');
  det.appendChild(el('div', 'freq', freq));
  if (r.forms && r.forms.length) {
    const fb = el('div', 'forms');
    r.forms.forEach((f) => { const x = el('span', 'f'); x.appendChild(el('b', null, f.form)); x.appendChild(document.createTextNode(' ×' + f.n)); fb.appendChild(x); });
    det.appendChild(fb);
  }
  card.appendChild(det);
  return card;
}

/* ---------- vidyut paradigm (display only) ---------- */
function presentTable(present) {
  const tbl = el('table', 'para-pres');
  const head = el('tr');
  head.appendChild(el('th', null, 'pres.'));
  ['sg', 'du', 'pl'].forEach((v) => head.appendChild(el('th', null, v)));
  tbl.appendChild(head);
  ['3', '2', '1'].forEach((p) => {
    const tr = el('tr');
    tr.appendChild(el('td', 'pn', p));
    ['sg', 'du', 'pl'].forEach((v) => {
      const cell = present[p + v] || [];
      tr.appendChild(el('td', null, cell.join(' / ') || '—'));
    });
    tbl.appendChild(tr);
  });
  return tbl;
}

function paradigmSection(pdata) {
  const det = el('details', 'paradigm');
  det.appendChild(el('summary', null, 'Paradigm — generated'));
  pdata.paradigms.forEach((pg) => {
    const blk = el('div', 'para-blk');
    const h = el('div', 'para-head');
    h.appendChild(el('span', 'para-gana', 'class ' + (pg.gana || '?')));
    if (pg.artha) h.appendChild(el('span', 'para-artha', pg.artha));
    if (pg.pada) h.appendChild(el('span', 'para-pada', pg.pada));
    if (pg.attested === false) {        // gaṇa-only fallback — no corpus/warnemyr form confirms it
      const u = el('span', 'para-unatt', 'not in corpus');
      u.title = 'generated form; no DCS/Whitney attestation for this root';
      h.appendChild(u);
    }
    blk.appendChild(h);
    if (pg.present) blk.appendChild(presentTable(pg.present));

    const more = el('div', 'para-more');
    const addRow = (label, val) => {
      if (!val || !val.length) return;
      const row = el('div', 'para-row');
      row.appendChild(el('span', 'para-lab', label));
      row.appendChild(el('span', 'para-val', val.join('  /  ')));
      more.appendChild(row);
    };
    const sec = pg.secondary || {};
    [['imperfect', 'imperfect'], ['imperative', 'imperative'], ['optative', 'optative'],
     ['perfect', 'perfect'], ['aorist', 'aorist'], ['future', 'future']].forEach(([k, lab]) => {
      if (sec[k]) addRow(lab + ' 3sg', sec[k]['3sg']);
    });
    const krt = pg.krt || {};
    [['ppp', 'PPP'], ['gerund', 'gerund (–tvā)'], ['infinitive', 'infinitive'],
     ['pres_act_ptcp', 'pres. part.'], ['gerundive', 'gerundive'], ['agent', 'agent']]
      .forEach(([k, lab]) => addRow(lab, krt[k]));
    blk.appendChild(more);
    det.appendChild(blk);
  });
  det.appendChild(el('p', 'para-prov', 'generated by vidyut-prakriya (Pāṇinian) — for display; '
    + 'not part of the authoritative crosswalk'));
  return det;
}

function degrade(msg) { return el('div', 'degrade', msg); }

/* ---------- boot ---------- */
async function boot() {
  $('passage').value = DEFAULT_PASSAGE;
  try {
    const res = await fetch('../src/reader_data.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    DATA = await res.json();
  } catch (e) {
    $('panel').innerHTML = '';
    $('panel').appendChild(degrade('Could not load reader_data.json (' + e.message
      + '). Run: python scripts/build_reader_data.py'));
    return;
  }
  try {                                  // vidyut paradigms are optional enrichment — never fatal
    const pr = await fetch('../src/paradigms.json');
    if (pr.ok) PARADIGMS = (await pr.json()).roots || {};
  } catch (e) { /* paradigm section simply absent */ }
  $('meta').textContent = DATA._meta.roots + ' roots · ' + DATA._meta.form_index_keys + ' indexed forms';
  $('analyze').addEventListener('click', renderTokens);
  $('exIast').addEventListener('click', () => { $('passage').value = DEFAULT_PASSAGE; renderTokens(); });
  $('exDeva').addEventListener('click', () => { $('passage').value = DEVA_PASSAGE; renderTokens(); });
  renderTokens();
}
document.addEventListener('DOMContentLoaded', boot);
