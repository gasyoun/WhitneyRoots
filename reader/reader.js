/* Whitney Reader — a pure view over the crosswalk (DESIGN §8). No new data. */
'use strict';

const DEFAULT_PASSAGE = 'sañjaya uvāca | dharmaṃ kṛtvā arjunaḥ gacchati | sukhaṃ bhavati ||';
let DATA = null;

const $ = (id) => document.getElementById(id);
function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}
// Match scripts/build_reader_data.py norm(): NFD, drop combining marks, NFC, lower.
function norm(s) {
  return (s || '').normalize('NFD').replace(/\p{Mn}/gu, '').normalize('NFC').toLowerCase().trim();
}
const WORD_RE = /[\p{L}ऀ-ॿ]/u;
const isWord = (s) => WORD_RE.test(s);

function candidatesFor(word) {
  const hit = DATA.form_index[norm(word)];
  return Array.isArray(hit) ? hit.map(String) : [];
}

/* ---------- passage rendering ---------- */
let selectedEl = null;

function renderTokens() {
  const text = $('passage').value;
  const box = $('tokens');
  box.textContent = '';
  const parts = text.split(/([^\p{L}ऀ-ॿ]+)/u).filter((p) => p.length);
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
  const freq = (r.freq == null) ? 'not attested as a verb in DCS'
    : r.freq.toLocaleString() + ' tokens' + (r.rank ? '  ·  rank #' + r.rank : '');
  det.appendChild(el('div', 'freq', freq));
  if (r.forms && r.forms.length) {
    const fb = el('div', 'forms');
    r.forms.forEach((f) => { const x = el('span', 'f'); x.innerHTML = ''; x.appendChild(el('b', null, f.form)); x.appendChild(document.createTextNode(' ×' + f.n)); fb.appendChild(x); });
    det.appendChild(fb);
  }
  card.appendChild(det);
  return card;
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
  $('meta').textContent = DATA._meta.roots + ' roots · ' + DATA._meta.form_index_keys + ' indexed forms';
  $('analyze').addEventListener('click', renderTokens);
  renderTokens();
}
document.addEventListener('DOMContentLoaded', boot);
