/**
 * WhitneyRoots v3 Bundle
 * Generated: 2026-07-14T11:12:50.651Z
 */

// --- FILE: core/state.js ---
/**
 * @file state.js
 * @description Global state management for WhitneyRoots
 */

const state = {
  view: 'lexicon',
  searchQuery: '',
  selectedItem: null,
  data: null,
  isLoading: true,
  sortBy: 'default',        // 'default' | 'freq-desc' | 'freq-asc'
  attestedOnly: false,      // show only roots attested in the DCS corpus
  stats: {
    rootsViewed: 0,
    perfectQuizzes: 0,
    searches: 0
  },
  unlockedAchievements: []
};

function updateState(newState) {
  Object.assign(state, newState);
  document.dispatchEvent(new CustomEvent('statechange', { detail: state }));
}


// --- FILE: core/data.js ---
/**
 * @file data.js
 * @description Data loading and schema migration logic
 */



export async function loadAppData() {
  try {
    const [appResp, freqResp, pidxResp, paraResp, afxResp] = await Promise.all([
      fetch('src/app_data.json'),
      fetch('src/dcs_freq.json').catch(() => null),
      fetch('src/participle_index.json').catch(() => null),
      fetch('src/paradigms.json').catch(() => null),
      fetch('src/affix_data.json').catch(() => null)
    ]);
    const data = await appResp.json();
    const migrated = migrateAppDataSchema(data);

    // Optional DCS corpus enrichment (sidecar; app works without it)
    if (freqResp && freqResp.ok) {
      try {
        const freq = await freqResp.json();
        mergeDcsFreq(migrated, freq);
      } catch (e) {
        console.warn('DCS frequency sidecar present but unreadable:', e);
      }
    }

    // Optional participle -> root lookup index
    if (pidxResp && pidxResp.ok) {
      try {
        const pidx = await pidxResp.json();
        migrated.participleIndex = pidx.index || {};
        migrated.participleLabels = (pidx.metadata && pidx.metadata.labels) || {};
      } catch (e) {
        console.warn('Participle index present but unreadable:', e);
      }
    }

    // Optional vidyut-prakriya generated paradigms (sidecar; app works without it)
    if (paraResp && paraResp.ok) {
      try {
        const para = await paraResp.json();
        mergeParadigms(migrated, para);
      } catch (e) {
        console.warn('Paradigm sidecar present but unreadable:', e);
      }
    }

    // Optional affix-explorer dataset (sidecar; app works without it)
    if (afxResp && afxResp.ok) {
      try {
        migrated.affixes = await afxResp.json();
      } catch (e) {
        console.warn('Affix dataset present but unreadable:', e);
      }
    }

    updateState({ data: migrated, isLoading: false });
  } catch (error) {
    console.error('Failed to load app data:', error);
    updateState({ isLoading: false });
  }
}

function mergeDcsFreq(data, freq) {
  if (!freq || !freq.entries) return data;
  data.dcsMeta = freq.metadata || null;
  data.lexicon.forEach(item => {
    const d = freq.entries[item.id];
    if (d) item.dcs = d;
  });
  return data;
}

function mergeParadigms(data, para) {
  if (!para || !para.roots) return data;
  data.paradigmMeta = para._meta || null;
  data.lexicon.forEach(item => {
    const p = para.roots[item.id];
    if (p) item.paradigm = p;   // { root, whitney_class, paradigms: [...] }
  });
  return data;
}

function migrateAppDataSchema(data) {
  // Logic from Zalizniakiada v17.6
  if (!data.lexicon) data.lexicon = [];
  if (!data.indices) data.indices = { subjects: [], languages: [], names: [] };
  
  // Ensure every item has a unique ID
  data.lexicon.forEach((item, index) => {
    if (!item.id) item.id = `root_${index}`;
  });

  return data;
}


// --- FILE: core/search.js ---


function performSearch(data, query) {
  if (!query) return data.lexicon;

  const normalizedQuery = normalizeSanskrit(query);
  return data.lexicon.filter(item => {
    return normalizeSanskrit(item.root).includes(normalizedQuery) ||
           normalizeSanskrit(item.meaning).includes(normalizedQuery);
  });
}

/**
 * Look up a (possibly inflected) participle surface form in the DCS index and
 * return the roots it belongs to. Diacritic-insensitive so users can paste
 * either IAST or plain ASCII (kriyamāṇe / kriyamane).
 */
function findParticipleMatches(index, query, limit = 60) {
  if (!index || !query) return [];
  const nq = normalizeSanskrit(query);
  if (nq.length < 2) return [];
  const exact = [];
  const prefix = [];
  for (const form in index) {
    const nf = normalizeSanskrit(form);
    if (nf === nq) {
      index[form].forEach(hit => exact.push({ form, ...hit }));
    } else if (nf.startsWith(nq)) {
      index[form].forEach(hit => prefix.push({ form, ...hit }));
    }
    if (exact.length + prefix.length > limit * 3) break;
  }
  return exact.concat(prefix).slice(0, limit);
}


// --- FILE: core/router.js ---
/**
 * @file router.js
 * @description Hash-based routing for WhitneyRoots
 */



function initRouter() {
  window.addEventListener('hashchange', handleRoute);
  handleRoute();
}

function handleRoute() {
  const hash = window.location.hash || '#v1/roots/list';
  const parts = hash.slice(1).split('/');
  
  // Example: #v1/roots/list or #v1/roots/item/1
  if (parts[1] === 'roots') {
    if (parts[2] === 'list') {
      updateState({ view: 'lexicon', selectedItem: null });
    } else if (parts[2] === 'item' && parts[3]) {
      updateState({ view: 'detail', selectedItem: parts[3] });
    }
  } else if (parts[1] === 'quiz') {
    updateState({ view: 'quiz' });
  } else if (parts[1] === 'affixes') {
    updateState({ view: 'affixes', selectedItem: null });
  }
}

function navigateTo(route) {
  window.location.hash = route;
}


// --- FILE: core/quiz.js ---
/**
 * @file quiz.js
 * @description Quiz engine for WhitneyRoots
 */

function startQuiz(data, count = 10) {
  if (!data || !data.lexicon || data.lexicon.length === 0) return null;
  
  const questions = [];
  const lexicon = data.lexicon;
  
  for (let i = 0; i < count; i++) {
    const target = lexicon[Math.floor(Math.random() * lexicon.length)];
    const type = Math.random() > 0.5 ? 'ROOT_TO_MEANING' : 'MEANING_TO_ROOT';
    
    // Get 3 random decoys
    const decoys = [];
    while (decoys.length < 3) {
      const decoy = lexicon[Math.floor(Math.random() * lexicon.length)];
      if (decoy.id !== target.id && !decoys.includes(decoy)) {
        decoys.push(decoy);
      }
    }
    
    if (type === 'ROOT_TO_MEANING') {
      questions.push({
        question: `What is the meaning of the root √${target.root}?`,
        options: shuffle([target.meaning, ...decoys.map(d => d.meaning)]),
        answer: target.meaning
      });
    } else {
      questions.push({
        question: `Which root means '${target.meaning}'?`,
        options: shuffle([`√${target.root}`, ...decoys.map(d => `√${d.root}`)]),
        answer: `√${target.root}`
      });
    }
  }
  
  return {
    title: "Dynamic Root Challenge",
    questions,
    score: 0
  };
}

function shuffle(array) {
  return array.sort(() => Math.random() - 0.5);
}


// --- FILE: core/analytics.js ---
function buildTopicClusters(data) {
  const clusters = {};
  const commonKeywords = ['move', 'speak', 'shine', 'eat', 'go', 'sound', 'be', 'do', 'strike', 'cut'];
  
  data.lexicon.forEach(item => {
    const meaning = item.meaning.toLowerCase();
    commonKeywords.forEach(keyword => {
      if (meaning.includes(keyword)) {
        if (!clusters[keyword]) clusters[keyword] = [];
        clusters[keyword].push(item.id);
      }
    });
  });
  
  return Object.entries(clusters).map(([name, roots]) => ({ name, roots }));
}

function calculateCentrality(data) {
  // Simple centrality: roots with many PPP forms or multiple classes are "influential"
  const centrality = {};
  data.lexicon.forEach(item => {
    let score = 0;
    if (item.ppp) score += item.ppp.length * 2;
    if (item.classes) score += item.classes.length * 1.5;
    if (item.meaning.length < 15) score += 1; // Short core meanings are often fundamental
    centrality[item.id] = score;
  });
  return centrality;
}


// --- FILE: core/achievements.js ---
const ACHIEVEMENTS_LIST = [
  { id: 'first_view', title: 'Curious Scholar', description: 'Viewed your first root detail.', condition: (stats) => stats.rootsViewed >= 1 },
  { id: 'lexicon_master', title: 'Lexicon Master', description: 'Viewed 5 roots.', condition: (stats) => stats.rootsViewed >= 5 }, // Smaller for testing
  { id: 'quiz_pro', title: 'Quiz Pro', description: 'Passed a quiz with 100% score.', condition: (stats) => stats.perfectQuizzes >= 1 }
];

function trackProgress(currentState, eventType) {
  const stats = currentState.stats || { rootsViewed: 0, perfectQuizzes: 0, searches: 0 };
  const unlocked = currentState.unlockedAchievements || [];

  if (eventType === 'VIEW_ROOT') stats.rootsViewed++;
  if (eventType === 'PERFECT_QUIZ') stats.perfectQuizzes++;
  if (eventType === 'SEARCH') stats.searches++;

  const newlyUnlocked = ACHIEVEMENTS_LIST.filter(a => a.condition(stats) && !unlocked.includes(a.id));
  
  return {
    stats,
    unlocked: [...unlocked, ...newlyUnlocked.map(a => a.id)],
    newlyUnlocked: newlyUnlocked
  };
}

function getUnlockedAchievements(unlockedIds) {
  return ACHIEVEMENTS_LIST.filter(a => unlockedIds.includes(a.id));
}


// --- FILE: core/ai.js ---
function getAIInsights(rootItem) {
  const insights = [];
  
  if (rootItem.classes && rootItem.classes.length > 1) {
    insights.push(`Note: This root belongs to multiple classes (${rootItem.classes.join(', ')}), indicating high morphological versatility.`);
  }
  
  if (rootItem.ppp && rootItem.ppp.length > 2) {
    insights.push(`Philological Tip: Multiple PPP forms suggest varied usage in different Vedic or Classical periods.`);
  }

  if (rootItem.meaning && rootItem.meaning.toLowerCase().includes('go')) {
    insights.push("Comparative Insight: Roots of 'going' often develop abstract meanings like 'knowing' or 'attaining' in Sanskrit.");
  }
  
  return insights.length > 0 ? insights.join(' ') : "Focus on mastering the primary meaning and class first.";
}

function getPrefixSuggestions(rootItem) {
  // Common Sanskrit prefixes (Upasargas)
  const upasargas = ['pra', 'apa', 'sam', 'anu', 'vi', 'upa', 'ni', 'ati'];
  return upasargas.slice(0, 3).map(u => `${u}-${rootItem.root}`);
}


// --- FILE: utils/dom.js ---
/**
 * @file dom.js
 * @description WhitneyRoots DOM Utilities
 */

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[m]);
}

function bindActionWithKeyboard(element, callback) {
  if (!element) return;
  element.addEventListener('click', callback);
  element.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      callback(e);
    }
  });
}

function safeUrl(path) {
  return path.startsWith('http') ? path : `#${path}`;
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('visible'), 100);
  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 500);
  }, 3000);
}

function createElement(tag, props = {}, children = []) {
  const element = document.createElement(tag);
  
  Object.entries(props).forEach(([key, value]) => {
    if (key === 'class') {
      element.className = value;
    } else if (key.startsWith('on') && typeof value === 'function') {
      element.addEventListener(key.substring(2).toLowerCase(), value);
    } else {
      element.setAttribute(key, value);
    }
  });

  children.forEach(child => {
    if (typeof child === 'string') {
      element.appendChild(document.createTextNode(child));
    } else if (child instanceof HTMLElement) {
      element.appendChild(child);
    }
  });

  return element;
}


// --- FILE: vendor/sanskrit-util.js ---
// sanskrit_util — shared Sanskrit string helpers for the CDSL / Sanskrit-Lexicon repos.
//
// Behaviour-identical port of py/sanskrit_util/__init__.py (proved by ../vectors/vectors.json).
// Consolidated from WhitneyRoots reader.js (deva2iast/norm/nfold), linguistics.js
// (normalizeSanskrit/iastToDevanagari) and scripts/sanskrit_util.py (to_slp1/from_slp1/
// to_roman/form_key). See README for which key to use when.

// ---- IAST -> SLP1 (longest-key-first; aspirates + diphthongs are digraphs) ----
const SLP1 = {
  ai: 'E', au: 'O', kh: 'K', gh: 'G', ch: 'C', jh: 'J', 'ṭh': 'W', 'ḍh': 'Q',
  th: 'T', dh: 'D', ph: 'P', bh: 'B',
  'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṛ': 'f', 'ṝ': 'F', 'ḷ': 'x', 'ḹ': 'X',
  'ṃ': 'M', 'ṁ': 'M', 'ḥ': 'H', 'ṅ': 'N', 'ñ': 'Y', 'ṭ': 'w', 'ḍ': 'q', 'ṇ': 'R',
  'ś': 'S', 'ṣ': 'z', 'ḻ': 'L',
  a: 'a', i: 'i', u: 'u', e: 'e', o: 'o', k: 'k', g: 'g', c: 'c', j: 'j',
  t: 't', d: 'd', n: 'n', p: 'p', b: 'b', m: 'm', y: 'y', r: 'r', l: 'l',
  v: 'v', s: 's', h: 'h',
};

function to_slp1(iast) {
  const s = iast || '';
  let out = '', i = 0;
  while (i < s.length) {
    const two = s.slice(i, i + 2);
    if (SLP1[two] !== undefined) { out += SLP1[two]; i += 2; continue; }
    const one = s[i];
    out += (SLP1[one] !== undefined ? SLP1[one] : one); i += 1;
  }
  return out;
}

const ROMAN = { 1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X' };

function to_roman(nums) {
  return (nums || []).filter((n) => ROMAN[n] !== undefined).map((n) => ROMAN[n]);
}

// ---- SLP1 -> IAST ----
const FROM_SLP1 = {
  A: 'ā', I: 'ī', U: 'ū', f: 'ṛ', F: 'ṝ', x: 'ḷ', X: 'ḹ',
  E: 'ai', O: 'au', M: 'ṃ', H: 'ḥ',
  K: 'kh', G: 'gh', N: 'ṅ', C: 'ch', J: 'jh', Y: 'ñ',
  w: 'ṭ', W: 'ṭh', q: 'ḍ', Q: 'ḍh', R: 'ṇ',
  T: 'th', D: 'dh', P: 'ph', B: 'bh',
  S: 'ś', z: 'ṣ', L: 'ḻ',
};

function from_slp1(slp1) {
  let out = '';
  for (const ch of (slp1 || '')) out += (FROM_SLP1[ch] !== undefined ? FROM_SLP1[ch] : ch);
  return out;
}

// ---- Devanāgarī -> IAST (inherent-'a' + virāma aware) ----
const DV_VOWEL = { 'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au' };
const DV_MATRA = { 'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ', 'ॢ': 'ḷ', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au' };
const DV_CONS = { 'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ', 'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'ñ', 'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'ś', 'ष': 'ṣ', 'स': 's', 'ह': 'h', 'ळ': 'ḷ' };
const DV_MARK = { 'ं': 'ṃ', 'ः': 'ḥ', 'ँ': 'ṃ' };
const VIRAMA = '्';

function deva_to_iast(s) {
  s = s || '';
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (DV_CONS[ch] != null) {
      out += DV_CONS[ch];
      const nx = s[i + 1];
      if (nx === VIRAMA) { i++; }
      else if (DV_MATRA[nx] != null) { out += DV_MATRA[nx]; i++; }
      else { out += 'a'; }
    } else if (DV_VOWEL[ch] != null) { out += DV_VOWEL[ch]; }
    else if (DV_MARK[ch] != null) { out += DV_MARK[ch]; }
    else if (ch === 'ऽ') { /* avagraha — drop */ }
    else { out += ch; }
  }
  return out;
}

// ---- Devanāgarī -> SLP1 (direct; the ळ→L vs x decision is made HERE) ----
// deva_to_iast collapses ळ (U+0933, retroflex ḻa) onto vocalic ḷ (both render as IAST ḷ/U+1E37),
// so to_slp1(deva_to_iast('ळ')) would yield 'x' (vocalic ḷ) instead of 'L'. SLP1 keeps them apart
// and that can't be recovered after the IAST step, so we transcode Devanāgarī → SLP1 directly:
// derive the maps from the IAST maps (tracking to_slp1) and override ळ → 'L'. Round-trip partner
// of from_slp1 ('L' → ḻ), where to_slp1∘deva_to_iast is not. Mirror of the Python deva_to_slp1.
const mapVals = (m) => Object.fromEntries(Object.entries(m).map(([k, v]) => [k, to_slp1(v)]));
const DV_VOWEL_SLP1 = mapVals(DV_VOWEL);
const DV_MATRA_SLP1 = mapVals(DV_MATRA);
const DV_CONS_SLP1 = mapVals(DV_CONS);
DV_CONS_SLP1['ळ'] = 'L';        // retroflex ḻa — NOT 'x' (vocalic ḷ, from ऌ); see note above
const DV_MARK_SLP1 = mapVals(DV_MARK);

function deva_to_slp1(s) {
  s = s || '';
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (DV_CONS_SLP1[ch] != null) {
      out += DV_CONS_SLP1[ch];
      const nx = s[i + 1];
      if (nx === VIRAMA) { i++; }
      else if (DV_MATRA_SLP1[nx] != null) { out += DV_MATRA_SLP1[nx]; i++; }
      else { out += 'a'; }
    } else if (DV_VOWEL_SLP1[ch] != null) { out += DV_VOWEL_SLP1[ch]; }
    else if (DV_MARK_SLP1[ch] != null) { out += DV_MARK_SLP1[ch]; }
    else if (ch === 'ऽ') { /* avagraha — drop */ }
    else { out += ch; }
  }
  return out;
}

// ---- SLP1 -> Devanāgarī (real transcode: virāma conjuncts + mātrās) ----
// Round-trip partner of deva_to_slp1: for canonical SLP1, deva_to_slp1(slp1_to_devanagari(s)) == s
// (proved on the full alphabet + 1000 real MW headwords). Unlike iast_to_devanagari (a display-only
// replace), this supplies the virāma between clustered consonants and picks independent-vowel vs
// mātrā by position. The vowel/mātrā/consonant maps are INVERTED from the same Devanāgarī→SLP1 maps
// deva_to_slp1 uses (kept in lock-step); only the 3 marks are explicit (M→anusvāra, H→visarga,
// ~→candrabindu) since anusvāra and candrabindu both map back to 'M' and can't be inverted. Not
// round-trip stable (matching deva_to_slp1): candrabindu (~→ँ→'M') and avagraha ('→ऽ, dropped).
const invert = (m) => Object.fromEntries(Object.entries(m).map(([k, v]) => [v, k]));
const SLP1_TO_DV_VOWEL = invert(DV_VOWEL_SLP1);
const SLP1_TO_DV_MATRA = invert(DV_MATRA_SLP1);
SLP1_TO_DV_MATRA['a'] = '';        // inherent 'a' takes no sign
const SLP1_TO_DV_CONS = invert(DV_CONS_SLP1);
const SLP1_TO_DV_MARK = { M: 'ं', H: 'ः', '~': 'ँ' }; // anusvāra / visarga / candrabindu

function slp1_to_devanagari(slp1) {
  const s = slp1 || '';
  let out = '';
  let pendingCons = false;         // a consonant sign was emitted, still awaits its vowel/virāma
  for (const ch of s) {
    if (SLP1_TO_DV_CONS[ch] != null) {
      if (pendingCons) out += VIRAMA;               // previous consonant had no vowel -> conjunct
      out += SLP1_TO_DV_CONS[ch];
      pendingCons = true;
    } else if (SLP1_TO_DV_VOWEL[ch] != null) {
      if (pendingCons) { out += SLP1_TO_DV_MATRA[ch]; pendingCons = false; } // mātrā ('' for 'a')
      else out += SLP1_TO_DV_VOWEL[ch];             // independent vowel sign
    } else {                                        // mark, avagraha, accent, digit, space, other
      if (pendingCons) { out += VIRAMA; pendingCons = false; }
      if (ch === "'") out += 'ऽ';                   // avagraha
      else out += (SLP1_TO_DV_MARK[ch] != null ? SLP1_TO_DV_MARK[ch] : ch);
    }
  }
  if (pendingCons) out += VIRAMA;                   // trailing bare consonant
  return out;
}

// ---- IAST -> Devanāgarī (approximate display transcode) ----
const IAST_TO_DEVA = {
  a: 'अ', 'ā': 'आ', i: 'इ', 'ī': 'ई', u: 'उ', 'ū': 'ऊ', 'ṛ': 'ऋ', 'ṝ': 'ॠ', 'ḷ': 'ऌ', 'ḹ': 'ॡ',
  e: 'ए', ai: 'ऐ', o: 'ओ', au: 'औ', 'ṃ': 'ं', 'ḥ': 'ः',
  k: 'क', kh: 'ख', g: 'ग', gh: 'घ', 'ṅ': 'ङ',
  c: 'च', ch: 'छ', j: 'ज', jh: 'झ', 'ñ': 'ञ',
  'ṭ': 'ट', 'ṭh': 'ठ', 'ḍ': 'ड', 'ḍh': 'ढ', 'ṇ': 'ण',
  t: 'त', th: 'थ', d: 'द', dh: 'ध', n: 'न',
  p: 'प', ph: 'फ', b: 'ब', bh: 'भ', m: 'म',
  y: 'य', r: 'र', l: 'ल', v: 'व',
  'ś': 'श', 'ṣ': 'ष', s: 'स', h: 'ह',
};
const IAST_TO_DEVA_KEYS = Object.keys(IAST_TO_DEVA).sort((a, b) => b.length - a.length);

function iast_to_devanagari(text) {
  let result = (text || '').toLowerCase();
  for (const key of IAST_TO_DEVA_KEYS) {
    result = result.split(key).join(IAST_TO_DEVA[key]);
  }
  return result;
}

// ---- normalization keys ----
const DEVA_RE = /[ऀ-ॿ]/;

// Whitespace pinned to match the Python port's _WS_CHARS exactly. JS String.trim()/\s strip the
// BOM/ZWNBSP U+FEFF (which sneaks in when a file is read without a BOM-aware decoder) while Python
// str.strip()/\s do not (and conversely Python strips U+0085 NEL) — list the class explicitly so
// norm()/form_key()/slp1_norm() yield identical keys in both languages.
const WS = '\\t\\n\\x0b\\f\\r \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000\\ufeff';
const WS_TRIM_RE = new RegExp('^[' + WS + ']+|[' + WS + ']+$', 'g');
const WS_RUN_RE = new RegExp('[' + WS + ']+', 'g');
const wstrim = (s) => s.replace(WS_TRIM_RE, '');

function norm(s) {
  s = s || '';
  if (DEVA_RE.test(s)) s = deva_to_iast(s);
  return wstrim(s.normalize('NFD').replace(/\p{Mn}/gu, '').normalize('NFC').toLowerCase());
}

function nfold(s) {
  return norm(s).replace(/[mn]/g, 'n');
}

// ---- length-preserving comparison key ----
const FK_ACCENT = new Set(['́', '̀', '॑', '॒']); // acute, grave, Vedic svarita/anudātta
const FK_VOWELS = new Set([...'aāiīuūṛṝḷḹeēoō']);
const COMBINING_RE = /\p{Mn}/u;

function form_key(s) {
  s = wstrim(s || '').toLowerCase();
  if (s === '-' || s === '–' || s === '—') return '';
  s = s.replace(/ḥ$/, '');
  s = s.replace(/[ṃṁṅñṇ]/g, 'n');
  const out = [];
  for (const ch of s.normalize('NFD')) {
    if (FK_ACCENT.has(ch)) {
      let j = out.length - 1;
      while (j >= 0 && COMBINING_RE.test(out[j])) j -= 1;
      const base = j >= 0 ? out.slice(j).join('').normalize('NFC') : '';
      if (FK_VOWELS.has(base)) continue;
    }
    out.push(ch);
  }
  return out.join('').normalize('NFC');
}

// ---- lossy ASCII-folding search key (v3-explorer normalizeSanskrit) ----
const NS_MAP = {
  'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
  'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
  'ḥ': 'h', 'ṃ': 'm',
};

function normalize_sanskrit(text) {
  if (!text) return '';
  return text.normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[āīūṛṝḷḹṅñṭḍṇśṣḥṃ]/g, (m) => NS_MAP[m] || m)
    .toLowerCase();
}

// ---- SLP1-side API ----
// The CDSL dictionaries store headwords in SLP1, where case is PHONEMIC (S=ś≠s) — so the
// IAST helpers above can't key them without a transcode, and every CDSL repo re-rolled its own
// SLP1 alphabet + headword normalizer. Behaviour-identical port of the Python additions.
const SLP1_VOWELS = 'aAiIuUfFxXeEoO';                          // f/F=ṛ/ṝ, x/X=ḷ/ḹ, E=ai, O=au
const SLP1_MARKS = 'MH~';                                     // anusvāra, visarga, candrabindu
const SLP1_CONSONANTS = 'kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL'; // L = Vedic retroflex ḻa
const SLP1_ALPHABET = SLP1_VOWELS + SLP1_MARKS + SLP1_CONSONANTS; // valid SLP1 letters (no avagraha)

const SLP1_ACCENTS_RE = /[/\\^~]/g; // udātta / anudātta / svarita / candrabindu

function strip_slp1_accents(slp1) {
  return (slp1 ?? '').replace(SLP1_ACCENTS_RE, '');
}

function slp1_norm(slp1) {
  let s = strip_slp1_accents(slp1 ?? '');
  s = s.replace(/\d+$/, '');
  return wstrim(s.replace(WS_RUN_RE, ' '));
}

function slp1_form_key(slp1) {
  return form_key(from_slp1(strip_slp1_accents(slp1 ?? '')));
}

// Fuzzy-match key: fold ALL SLP1 distinctions to plain ASCII — the lossy extreme of the SLP1 key
// family. For building/querying MW headword indexes (mw_en_tm.json); index and query sides agree
// because both use standard SLP1 (R=ṇ). ⚠️ guṇa = 'guRa' in MW — forgetting R→n maps it to 'gūna'.
function slp1_simplify(slp1) {
  let s = slp1 || '';
  s = s.replace(/K/g, 'kh').replace(/G/g, 'gh')
    .replace(/C/g, 'ch').replace(/J/g, 'jh')
    .replace(/T/g, 'th').replace(/D/g, 'dh')
    .replace(/P/g, 'ph').replace(/B/g, 'bh');
  s = s.replace(/S/g, 's').replace(/z/g, 's');
  s = s.replace(/Y/g, 'n').replace(/N/g, 'n').replace(/R/g, 'n');   // R=ṇ is the critical case
  s = s.replace(/A/g, 'a').replace(/I/g, 'i').replace(/U/g, 'u');
  s = s.replace(/E/g, 'ai').replace(/O/g, 'au');
  s = s.replace(/f/g, 'r').replace(/F/g, 'r').replace(/x/g, 'l').replace(/X/g, 'l');
  s = s.replace(/M/g, 'm').replace(/H/g, '');
  s = s.replace(/W/g, 'th').replace(/Q/g, 'dh');
  s = s.replace(/w/g, 't').replace(/q/g, 'd');
  s = s.replace(/L/g, 'l');                                         // Vedic retroflex ḻa
  return s.toLowerCase();
}

// ---- CDSL raw source line -> readable IAST (display layer over from_slp1) ----
// A raw csl-orig line is SLP1 inside CDSL markup, unreadable to a human. These
// render it to IAST honoring each dictionary's encoding: MW <s>…</s>;
// PW/PWG/AP/WIL {#…#} (with the meaning language in {%…%}, left as-is);
// VCP/SKD whole-line SLP1 prose. The markup shell (tags, [Page…] markers, the ¦
// headword separator) is stripped. `code` is the csl-orig dict code
// (mw, ap, pwg, pw, wil, vcp, skd). Non-SLP1 spans — glosses, <ls> citations,
// grammar abbreviations like "f." — are preserved.
const _PROSE_SLP1_DICTS = new Set(['vcp', 'skd']);

function _stripCdslMarkup(text) {
  return text
    .replace(/<info[^>]*\/?>/gi, '')   // metadata self-closing tags
    .replace(/\[Page[^\]]*\]/g, '')    // VCP/SKD page markers
    .replace(/<[^>]+>/g, '');          // any remaining tag shell
}

function _cleanCdsl(text) {
  return text
    .replace(/¦/g, ' ')                // ¦ headword/body separator
    .replace(/\s+([,.;:!?])/g, '$1')   // pull punctuation back
    .replace(/\s+/g, ' ')
    .trim();
}

function source_line_to_iast(text, code) {
  if (text == null) return '';
  const c = String(code || '').toLowerCase();
  if (_PROSE_SLP1_DICTS.has(c)) {
    const s = String(text).replace(/[A-Za-z~']+/g, (m) => from_slp1(m));
    return _cleanCdsl(_stripCdslMarkup(s));
  }
  let s = String(text);
  s = s.replace(/\{[#@]([^#@]*)[#@]\}/g, (_, x) => from_slp1(x));   // {#…#}, {@…@}
  s = s.replace(/<s\d?>([^<]*)<\/s\d?>/gi, (_, x) => from_slp1(x)); // MW <s>…</s>
  s = s.replace(/\{%([^%]*)%\}/g, (_, x) => x);                    // meaning: unwrap, keep
  return _cleanCdsl(_stripCdslMarkup(s));
}

function source_text_to_iast(text, code) {
  if (text == null) return '';
  return String(text).split('\n').map((l) => source_line_to_iast(l, code)).join('\n');
}



// --- FILE: utils/linguistics.js ---
/**
 * @file linguistics.js
 * @description Linguistic utilities for Sanskrit (Whitney Roots)
 *
 * Thin re-export over the canonical sanskrit-util package — see
 * ../vendor/sanskrit-util.js (a byte-identical copy of sanskrit-util/js/index.mjs, re-copied
 * whole on every package update, never hand-edited) and github-spine/SHARED_CODE.md §1-2. This
 * file used to carry its own inline normalizeSanskrit/iastToDevanagari implementations; those
 * were the donor for sanskrit-util's normalize_sanskrit/iast_to_devanagari (folded in verbatim),
 * so this swap is behaviour-identical, not a rewrite. Do not re-add inline transcode/normalize
 * logic here — extend sanskrit-util instead.
 *
 * Note (parity, not a regression): sanskrit-util's iast_to_devanagari uses the SAME simple
 * character-replace algorithm this file's old iastToDevanagari used (no virama/matra
 * construction) — see SHARED_CODE.md's "iast_to_devanagari is BROKEN" note. Output here is
 * unchanged from before this migration; fixing that display bug is a separate, un-scoped change.
 */


function normalizeSanskrit(text) {
  return normalize_sanskrit(text);
}

function iastToDevanagari(text) {
  return iast_to_devanagari(text);
}


// --- FILE: renderers/cards.js ---
/**
 * @file cards.js
 * @description Card rendering for WhitneyRoots
 */





function renderRootCard(rootItem) {
  const devanagari = iastToDevanagari(rootItem.root);
  
  return createElement('div', { 
    class: 'root-card clickable',
    onclick: () => {
      window.location.hash = `#v1/roots/item/${rootItem.id}`;
    }
  }, [
    createElement('div', { class: 'root-header' }, [
      createElement('h3', {}, [rootItem.root]),
      createElement('span', { class: 'devanagari' }, [devanagari])
    ]),
    renderDcsBadge(rootItem),
    rootItem.classes && rootItem.classes.length > 0 ?
      createElement('div', { class: 'classes' }, rootItem.classes.map(c => createElement('span', { class: 'class-badge' }, [c]))) : 
      null,
    rootItem.ppp && rootItem.ppp.length > 0 ?
      createElement('p', { class: 'ppp-forms' }, [
        createElement('strong', {}, ['PPP: ']),
        rootItem.ppp.join(', ')
      ]) : null,
    createElement('p', { class: 'meaning' }, [rootItem.meaning]),
    createElement('a', { href: rootItem.link, target: '_blank', class: 'external-link' }, ['View on samskrtam.ru'])
  ]);
}

/**
 * Compact DCS corpus-frequency badge for a card.
 * Attested roots get a token count + corpus rank; unmatched / zero-attestation
 * roots get a neutral "not in DCS corpus" tag (no judgement implied).
 */
function renderDcsBadge(rootItem) {
  const dcs = rootItem.dcs;
  if (!dcs) return null;
  if (dcs.total > 0) {
    return createElement('div', { class: 'dcs-badge', title: 'Digital Corpus of Sanskrit attestations' }, [
      createElement('span', { class: 'dcs-freq' }, [`${dcs.total.toLocaleString()}×`]),
      dcs.rank ? createElement('span', { class: 'dcs-rank' }, [`#${dcs.rank}`]) : null
    ]);
  }
  return createElement('span', { class: 'dcs-tag-none' }, ['not in DCS corpus']);
}


// --- FILE: renderers/lists.js ---





/**
 * Results panel for a participle form-lookup: each hit links to its root and
 * names the participle category. Shown above the grid when the search query
 * matches attested participle forms in the DCS index.
 */
function renderParticipleMatches(matches, labels) {
  const panel = createElement('div', { class: 'participle-lookup' });
  panel.appendChild(createElement('div', { class: 'plk-head' }, [
    `Participle forms (${matches.length}) — corpus forms matching your search`
  ]));
  const grid = createElement('div', { class: 'plk-grid' });
  matches.forEach(m => {
    const label = (labels && labels[m.category]) || m.category;
    const row = createElement('div', { class: 'plk-hit clickable' }, [
      createElement('span', { class: 'plk-form' }, [m.form]),
      createElement('span', { class: 'plk-arrow' }, ['→']),
      createElement('span', { class: 'plk-root' }, [m.root]),
      createElement('span', { class: 'plk-cat' }, [label])
    ]);
    row.onclick = () => { window.location.hash = `#v1/roots/item/${m.id}`; };
    grid.appendChild(row);
  });
  panel.appendChild(grid);
  return panel;
}

/** DCS sort + filter controls for the list view. */
function renderDcsControls() {
  const bar = createElement('div', { class: 'dcs-controls' });

  const sortLabel = createElement('label', { class: 'dcs-ctrl-label' }, ['Sort: ']);
  const select = document.createElement('select');
  select.className = 'dcs-select';
  [['default', 'Whitney order'],
   ['freq-desc', 'Most frequent (DCS)'],
   ['freq-asc', 'Least frequent (DCS)']].forEach(([val, txt]) => {
    const opt = document.createElement('option');
    opt.value = val; opt.textContent = txt;
    if (state.sortBy === val) opt.selected = true;
    select.appendChild(opt);
  });
  select.onchange = () => updateState({ sortBy: select.value });
  sortLabel.appendChild(select);

  const filterLabel = createElement('label', { class: 'dcs-ctrl-label' });
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = !!state.attestedOnly;
  cb.onchange = () => updateState({ attestedOnly: cb.checked });
  filterLabel.appendChild(cb);
  filterLabel.appendChild(document.createTextNode(' Corpus-attested only'));

  bar.appendChild(sortLabel);
  bar.appendChild(filterLabel);
  return bar;
}

function renderRootList(data) {
  // We need the full data for clusters, but only use 'data' (filtered) for the grid
  // Actually, let's just use the current filtered list for clusters too, or the whole app data?
  // The runbook suggests analyzing the corpus. Let's use the full data for clusters.
  // Wait, 'data' passed here is the filtered result from performSearch.
  // I should probably pass the full state.data to buildTopicClusters.
  
  const clusters = buildTopicClusters({ lexicon: data }); // Simple version for now
  
  const container = createElement('div', { class: 'root-list-view' });
  
  const clustersBar = createElement('div', { class: 'clusters-bar' }, [
    createElement('span', { class: 'cluster-label' }, ['Topic Filters: ']),
    ...clusters.map(c => {
      const btn = createElement('button', { class: 'cluster-btn' }, [`${c.name} (${c.roots.length})`]);
      btn.onclick = () => {
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
          searchInput.value = c.name;
          updateState({ searchQuery: c.name });
        }
      };
      return btn;
    })
  ]);
  
  const grid = createElement('div', { class: 'root-grid' });
  data.forEach(root => {
    grid.appendChild(renderRootCard(root));
  });
  
  container.appendChild(clustersBar);
  container.appendChild(renderDcsControls());
  container.appendChild(grid);

  return container;
}


// --- FILE: renderers/quiz.js ---
/**
 * @file quiz.js
 * @description Quiz renderer for WhitneyRoots
 */





function renderQuiz() {
  const quizState = startQuiz(state.data, 10); 
  const container = createElement('div', { class: 'quiz-container' });
  
  function renderQuestion(questionIndex) {
    container.innerHTML = '';
    const q = quizState.questions[questionIndex];
    
    const questionEl = createElement('div', { class: 'quiz-question' }, [
      createElement('h2', {}, [`Question ${questionIndex + 1}`]),
      createElement('p', { class: 'question-text' }, [q.question]),
      createElement('div', { class: 'options' }, q.options.map(opt => {
        const btn = createElement('button', { class: 'option-btn' }, [opt]);
        btn.onclick = () => {
          if (opt === q.answer) {
            quizState.score++;
            btn.classList.add('correct');
          } else {
            btn.classList.add('wrong');
          }
          
          setTimeout(() => {
            if (questionIndex + 1 < quizState.questions.length) {
              renderQuestion(questionIndex + 1);
            } else {
              renderResult();
            }
          }, 1000);
        };
        return btn;
      }))
    ]);
    
    container.appendChild(questionEl);
  }

  function renderResult() {
    container.innerHTML = '';
    
    // Tracking perfect scores
    if (quizState.score === quizState.questions.length) {
      updateState({ stats: { ...state.stats, perfectQuizzes: state.stats.perfectQuizzes + 1 } });
    }

    container.appendChild(createElement('div', { class: 'quiz-result' }, [
      createElement('h2', {}, ['Quiz Complete!']),
      createElement('p', {}, [`Your score: ${quizState.score} / ${quizState.questions.length}`]),
      createElement('button', { 
        class: 'back-btn', 
        onclick: () => updateState({ view: 'lexicon' }) 
      }, ['Back to Roots'])
    ]));
  }

  renderQuestion(0);
  return container;
}


// --- FILE: renderers/detail.js ---
/**
 * @file detail.js
 * @description Detail view renderer for a single Whitney root
 */






function renderDetailView(rootId, data) {
  const rootItem = data.lexicon.find(r => r.id === rootId);
  if (!rootItem) return createElement('div', {}, ['Root not found']);

  const devanagari = iastToDevanagari(rootItem.root);
  const aiInsight = getAIInsights(rootItem);
  const prefixSuggestions = getPrefixSuggestions(rootItem);

  return createElement('div', { class: 'detail-view' }, [
    createElement('button', { 
      class: 'back-link', 
      onclick: () => updateState({ view: 'lexicon', selectedItem: null }) 
    }, ['← Back to Lexicon']),
    
    createElement('div', { class: 'detail-header' }, [
      createElement('h1', {}, [rootItem.root]),
      createElement('div', { class: 'detail-devanagari' }, [devanagari])
    ]),

    createElement('div', { class: 'detail-content' }, [
      createElement('section', {}, [
        createElement('h3', {}, ['Grammar']),
        createElement('div', { class: 'detail-classes' }, [
          createElement('strong', {}, ['Verb Class: ']),
          ...(rootItem.classes.length > 0 ? rootItem.classes : ['N/A']).map(c => 
            createElement('span', { class: 'class-badge' }, [c])
          )
        ]),
        rootItem.ppp && rootItem.ppp.length > 0 ?
          createElement('div', { class: 'detail-ppp' }, [
            createElement('strong', {}, ['PPP Forms: ']),
            rootItem.ppp.join(', ')
          ]) : null
      ]),

      buildParadigmSection(rootItem),

      buildDcsSection(rootItem),

      createElement('section', {}, [
        createElement('h3', {}, ['Meaning']),
        createElement('p', { class: 'detail-meaning' }, [rootItem.meaning])
      ]),

      createElement('section', { class: 'ai-insights-section' }, [
        createElement('h3', {}, ['AI Insights']),
        createElement('p', {}, [aiInsight]),
        createElement('div', { class: 'prefix-suggestions' }, [
          createElement('strong', {}, ['Common Prefix Combinations: ']),
          ...prefixSuggestions.map(p => createElement('span', { class: 'prefix-badge' }, [p]))
        ])
      ]),

      createElement('section', {}, [
        createElement('h3', {}, ['References']),
        createElement('a', {
          href: rootItem.link,
          target: '_blank',
          class: 'external-link large'
        }, ['View full entry on samskrtam.ru'])
      ])
    ])
  ]);
}

const ROMAN_TO_ARABIC = {
  I: '1', II: '2', III: '3', IV: '4', V: '5',
  VI: '6', VII: '7', VIII: '8', IX: '9', X: '10'
};

function chip(text, cls) {
  return createElement('span', { class: cls || 'dcs-chip' }, [text]);
}

/**
 * The DCS corpus section: frequency/rank, class comparison + verdict,
 * PPP confirmation, the 9 participle categories, top forms and preverbs.
 * Falls back to a neutral note when the root is not in the corpus.
 */
function buildDcsSection(rootItem) {
  const dcs = rootItem.dcs;
  if (!dcs || dcs.total === 0) {
    return createElement('section', { class: 'dcs-section' }, [
      createElement('h3', {}, ['DCS Corpus']),
      createElement('p', { class: 'dcs-none-note' }, [
        'Not attested in the Digital Corpus of Sanskrit. ' +
        'This root is listed by Whitney but the corpus offers no usage evidence.'
      ])
    ]);
  }

  // ---- class comparison + verdict ----
  const wClasses = (rootItem.classes || []).map(c => ROMAN_TO_ARABIC[c] || c);
  const dClasses = dcs.grammar_class || [];
  const wset = new Set(wClasses);
  const dset = new Set(dClasses);
  let verdict = 'no DCS class', vcls = 'neutral';
  if (dClasses.length) {
    const inter = [...wset].filter(x => dset.has(x));
    const same = wset.size === dset.size && inter.length === wset.size;
    if (same) { verdict = 'agree'; vcls = 'agree'; }
    else if (inter.length) { verdict = 'partial overlap'; vcls = 'partial'; }
    else { verdict = 'differ'; vcls = 'differ'; }
  }
  const signal = dcs.present_stem_signal && dcs.present_stem_signal.dominant;

  const classRow = createElement('div', { class: 'dcs-class-compare' }, [
    createElement('div', { class: 'dcs-cc-col' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['Whitney']),
      createElement('span', {}, [wClasses.join(', ') || '—'])
    ]),
    createElement('div', { class: 'dcs-cc-col' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['DCS grammar']),
      createElement('span', {}, [dClasses.join(', ') || '—'])
    ]),
    createElement('div', { class: 'dcs-cc-col' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['Corpus signal']),
      createElement('span', {}, [signal || '—'])
    ]),
    createElement('span', { class: `dcs-verdict ${vcls}` }, [verdict])
  ]);

  // ---- PPP confirmation (Whitney's listed PPP vs attested) ----
  let pppRow = null;
  const wppp = (rootItem.ppp || []).filter(Boolean);
  if (wppp.length) {
    const attested = new Set((dcs.participles && dcs.participles['past-passive']
      ? dcs.participles['past-passive'].top : []).map(t => fold(t.form)));
    // also fold the derived ppp stems for a broader confirm set
    (dcs.ppp || []).forEach(s => attested.add(fold(s.stem)));
    pppRow = createElement('div', { class: 'dcs-ppp-check' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['Whitney PPP vs corpus: ']),
      ...wppp.map(p => {
        const pf = fold(p);
        const ok = [...attested].some(a => a === pf || a.startsWith(pf));
        return chip(`${p} ${ok ? '✓' : '✗'}`, `dcs-chip ${ok ? 'ok' : 'miss'}`);
      })
    ]);
  }

  // ---- participles (the 9 categories) ----
  let partBlock = null;
  const parts = dcs.participles || {};
  const cats = Object.keys(parts);
  if (cats.length) {
    partBlock = createElement('div', { class: 'dcs-participles' },
      cats.map(cat => {
        const info = parts[cat];
        return createElement('div', { class: 'dcs-part-cat' }, [
          createElement('div', { class: 'dcs-part-head' }, [
            createElement('span', { class: 'dcs-part-label' }, [info.label || cat]),
            createElement('span', { class: 'dcs-part-n' }, [`${info.total.toLocaleString()}`])
          ]),
          createElement('div', { class: 'dcs-part-forms' },
            (info.top || []).slice(0, 5).map(t => chip(t.form))
          )
        ]);
      })
    );
  }

  // ---- top forms + preverbs ----
  const topForms = (dcs.top_forms || []).slice(0, 12);
  const preverbs = (dcs.preverbs || []).slice(0, 10);

  return createElement('section', { class: 'dcs-section' }, [
    createElement('h3', {}, ['DCS Corpus']),
    createElement('div', { class: 'dcs-freq-line' }, [
      createElement('span', { class: 'dcs-freq-big' }, [dcs.total.toLocaleString()]),
      createElement('span', { class: 'dcs-freq-unit' }, ['attestations']),
      dcs.rank ? createElement('span', { class: 'dcs-rank-pill' }, [`rank #${dcs.rank}`]) : null
    ]),

    createElement('h4', {}, ['Verb class — Whitney vs corpus']),
    classRow,
    createElement('p', { class: 'dcs-foot' }, [
      'DCS grammar is itself lexicon metadata; the corpus signal is a coarse ' +
      'present-stem heuristic. Disagreement is not proof Whitney is wrong.'
    ]),

    pppRow,

    partBlock ? createElement('h4', {}, ['Participles attested in the corpus']) : null,
    partBlock,

    topForms.length ? createElement('h4', {}, ['Most frequent forms']) : null,
    topForms.length ? createElement('div', { class: 'dcs-chips' },
      topForms.map(t => chip(`${t.form} (${t.n})`))) : null,

    preverbs.length ? createElement('h4', {}, ['Preverb compounds']) : null,
    preverbs.length ? createElement('div', { class: 'dcs-chips' },
      preverbs.map(p => chip(`${p.form} (${p.n.toLocaleString()})`))) : null
  ]);
}

/* ---- vidyut-prakriya generated paradigm (DISPLAY only; merged from src/paradigms.json) ---- */
const SEC_ORDER = ['imperfect', 'imperative', 'optative', 'perfect', 'aorist', 'future'];
const SEC_LABELS = {
  imperfect: 'Imperfect', imperative: 'Imperative', optative: 'Optative',
  perfect: 'Perfect', aorist: 'Aorist', future: 'Future'
};
const KRT_ORDER = ['ppp', 'ppp_caus', 'past_active', 'gerund', 'infinitive', 'pres_act_ptcp',
  'pres_mid_ptcp', 'gerundive', 'agent', 'perf_act_ptcp'];
const KRT_LABELS = {
  ppp: 'Past pass. ptcp.', ppp_caus: 'Caus. PPP', past_active: 'Past act. ptcp.', gerund: 'Gerund (abs.)',
  infinitive: 'Infinitive', pres_act_ptcp: 'Pres. act. ptcp.', pres_mid_ptcp: 'Pres. mid. ptcp.',
  gerundive: 'Gerundive', agent: 'Agent noun', perf_act_ptcp: 'Perf. act. ptcp.'
};
const NUMS = ['sg', 'du', 'pl'];

function presentTable(present) {
  const rows = [createElement('tr', {}, [
    createElement('th', {}, ['']),
    ...NUMS.map(n => createElement('th', {}, [n]))
  ])];
  ['3', '2', '1'].forEach(p => {
    rows.push(createElement('tr', {}, [
      createElement('td', { class: 'para-pn' }, [p]),
      ...NUMS.map(n => createElement('td', {}, [(present[p + n] || []).join(' / ') || '—']))
    ]));
  });
  return createElement('table', { class: 'para-pres' }, rows);
}

function paraRow(label, valueStr) {
  if (!valueStr) return null;
  return createElement('div', { class: 'para-row' }, [
    createElement('span', { class: 'para-lab' }, [label]),
    createElement('span', { class: 'para-val' }, [valueStr])
  ]);
}

function paraBlock(pg) {
  const head = createElement('div', { class: 'para-head' }, [
    createElement('span', { class: 'para-gana' }, ['class ' + (pg.gana || '?')]),
    pg.artha ? createElement('span', { class: 'para-artha' }, [pg.artha]) : null,
    pg.pada ? createElement('span', { class: 'para-pada' }, [pg.pada]) : null,
    pg.attested === false
      ? createElement('span', { class: 'para-unatt', title: 'generated form; no DCS/Whitney attestation for this root' }, ['not in corpus'])
      : null
  ]);
  const sec = pg.secondary || {};
  const krt = pg.krt || {};
  const secRows = SEC_ORDER.map(k => {
    if (!sec[k]) return null;
    const sg = (sec[k]['3sg'] || []).join(' / ');
    const pl = (sec[k]['3pl'] || []).join(' / ');
    return paraRow(SEC_LABELS[k], [sg, pl].filter(Boolean).join('   ·   '));
  });
  const krtRows = KRT_ORDER.map(k => paraRow(KRT_LABELS[k], (krt[k] || []).join('  /  ')));
  return createElement('div', { class: 'para-block' }, [
    head,
    pg.present ? presentTable(pg.present) : null,
    secRows.some(Boolean) ? createElement('div', { class: 'para-sub' }, ['Other tenses (3rd person sg · pl)']) : null,
    ...secRows,
    krtRows.some(Boolean) ? createElement('div', { class: 'para-sub' }, ['Primary derivatives']) : null,
    ...krtRows
  ]);
}

/**
 * Generated conjugation from vidyut-prakriya (Pāṇinian), merged from src/paradigms.json.
 * One block per gaṇa-homonym; present system in full, other tenses 3sg/3pl, then kṛdantas.
 * Display only — never part of the authoritative class/frequency data. Absent for ~half the
 * roots (vidyut coverage + the conservative present-corroboration gate), so this section is
 * simply omitted when there is no paradigm.
 */
function buildParadigmSection(rootItem) {
  const pdata = rootItem.paradigm;
  if (!pdata || !pdata.paradigms || !pdata.paradigms.length) return null;
  return createElement('section', { class: 'para-section' }, [
    createElement('h3', {}, ['Paradigm']),
    createElement('p', { class: 'para-foot' }, [
      'Conjugation generated by vidyut-prakriya (Pāṇinian). Display only — not part of the ' +
      'authoritative class/frequency data.'
    ]),
    ...pdata.paradigms.map(paraBlock)
  ]);
}

/** Diacritic fold to match Whitney's ASCII PPP against DCS IAST forms. */
function fold(s) {
  if (!s) return '';
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[āīūṛṝḷḹṅñṭḍṇśṣḥṃṁ]/g, m => ({
      'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
      'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
      'ḥ': 'h', 'ṃ': 'm', 'ṁ': 'm'
    }[m] || m)).toLowerCase();
}


// --- FILE: renderers/affixes.js ---
/**
 * @file affixes.js
 * @description Affix explorer view — Sanskrit suffixes grouped by what they FORM, sized by
 * Apte productivity, with click-to-expand anubandha decoding + example derivatives.
 * Data: src/affix_data.json (built by SanskritLexicography/.../affix_pedagogy.py).
 */



const KIND_CLASS = {
  'kṛt': 'affix-kind-krt',
  'taddhita': 'affix-kind-tad',
  'strī': 'affix-kind-stri',
  'taddhita/kṛt': 'affix-kind-tad'
};

function renderAffixes(data) {
  const payload = data && data.affixes;
  const affixes = (payload && payload.affixes) || [];
  if (!affixes.length) {
    return createElement('div', { class: 'affix-explorer' }, [
      createElement('h2', {}, ['Sanskrit affixes']),
      createElement('p', { class: 'affix-intro' }, ['Affix data not loaded (src/affix_data.json).'])
    ]);
  }

  const maxR = Math.max(...affixes.map(a => a.apte_roots || 0)) || 1;
  const groups = {};
  affixes.forEach(a => { (groups[a.group] = groups[a.group] || []).push(a); });
  const sum = arr => arr.reduce((s, a) => s + (a.apte_roots || 0), 0);
  const order = Object.keys(groups).sort((x, y) => sum(groups[y]) - sum(groups[x]));

  const listWrap = createElement('div', { class: 'affix-list' }, []);
  const filter = createElement('input', {
    class: 'affix-filter', type: 'text',
    placeholder: 'filter by suffix, function, or pratyaya…'
  });
  filter.addEventListener('input', e => renderList(e.target.value));

  function renderList(q) {
    listWrap.replaceChildren();
    const f = (q || '').toLowerCase();
    order.forEach(g => {
      const items = groups[g]
        .filter(a => !f || (a.surface + a.pratyaya + a.function + a.group).toLowerCase().includes(f))
        .sort((a, b) => (b.apte_roots || 0) - (a.apte_roots || 0));
      if (!items.length) return;
      listWrap.appendChild(createElement('div', { class: 'affix-group' }, [
        createElement('h3', { class: 'affix-group-title' }, [g]),
        ...items.map(affixCard)
      ]));
    });
  }

  function affixCard(a) {
    const pct = Math.round(100 * (a.apte_roots || 0) / maxR);
    const card = createElement('div', { class: 'affix-card', tabindex: '0', role: 'button' }, [
      createElement('div', { class: 'affix-card-head' }, [
        createElement('span', { class: 'affix-surface' }, ['-' + a.surface]),
        createElement('span', { class: 'affix-pill ' + (KIND_CLASS[a.kind] || '') },
          [a.pratyaya_deva + '  ' + a.pratyaya]),
        createElement('span', { class: 'affix-func' }, [a.function]),
        createElement('span', { class: 'affix-count' }, [(a.apte_roots || 0) + ' roots'])
      ]),
      createElement('div', { class: 'affix-bar' }, [
        createElement('div', { class: 'affix-bar-fill', style: 'width:' + pct + '%' }, [])
      ])
    ]);
    let detail = null;
    const toggle = () => {
      if (detail) { detail.remove(); detail = null; return; }
      const steps = (a.anubandha || []).map(s =>
        createElement('span', { class: 'affix-step' }, [s]));
      const exs = (a.examples || []).map(e => createElement('span', { class: 'affix-ex' }, [
        createElement('span', { class: 'affix-ex-root' }, [e.root]),
        ' → ',
        createElement('span', { class: 'affix-ex-word' }, [e.word_iast])
      ]));
      const meta = a.kind + (a.mw_count ? '  ·  MW surface-suffix headwords: ' + a.mw_count : '');
      detail = createElement('div', { class: 'affix-detail' }, [
        createElement('div', { class: 'affix-detail-row' },
          [createElement('span', { class: 'affix-detail-label' }, ['Anubandha → surface: ']), ...steps]),
        createElement('div', { class: 'affix-detail-row' },
          [createElement('span', { class: 'affix-detail-label' }, ['Examples: ']),
           ...(exs.length ? exs : [createElement('span', { class: 'affix-ex' }, ['—'])])]),
        createElement('div', { class: 'affix-detail-meta' }, [meta])
      ]);
      detail.addEventListener('click', e => e.stopPropagation());
      card.appendChild(detail);
    };
    card.addEventListener('click', toggle);
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
    });
    return card;
  }

  renderList('');
  return createElement('div', { class: 'affix-explorer' }, [
    createElement('h2', {}, ['Sanskrit affixes — what forms what']),
    createElement('p', { class: 'affix-intro' }, [
      'Affixes grouped by what they form, sized by Apte productivity (number of distinct roots taking the affix). ' +
      'Click an affix for its anubandha (it-marker) decoding and example derivatives. ' +
      'kṛt = from verb roots · taddhita = from nominal stems · strī = feminine.'
    ]),
    filter,
    listWrap
  ]);
}


// --- FILE: entry.js ---
/**
 * @file entry.js
 * @description Application entry point
 */











async function initApp() {
  console.log('🚀 WhitneyRoots Initializing...');
  
  // Setup listeners
  document.addEventListener('statechange', (e) => {
    renderApp(e.detail);
  });

  const searchInput = document.getElementById('global-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value;
      const progress = trackProgress(state, 'SEARCH');
      updateState({ 
        searchQuery: query, 
        stats: progress.stats, 
        unlockedAchievements: progress.unlocked 
      });
    });
  }

  // Init router
  initRouter();

  // Load data
  await loadAppData();
}

function renderApp(currentState) {
  const appContainer = document.getElementById('app');
  if (!appContainer) return;

  if (currentState.isLoading) {
    appContainer.innerHTML = '<div class="loading">Loading Whitney Roots...</div>';
    return;
  }

  // Clear previous render before re-rendering (statechange fires on every
  // search / sort / filter toggle; otherwise renders stack up).
  appContainer.innerHTML = '';

  if (currentState.view === 'quiz') {
    appContainer.appendChild(renderQuiz());
    return;
  }

  if (currentState.view === 'affixes') {
    appContainer.appendChild(renderAffixes(currentState.data));
    return;
  }

  if (currentState.view === 'detail') {
    // Tracking
    const progress = trackProgress(currentState, 'VIEW_ROOT');
    if (progress.newlyUnlocked.length > 0) {
      console.log('🏆 New Achievement:', progress.newlyUnlocked[0].title);
      Object.assign(currentState, { stats: progress.stats, unlockedAchievements: progress.unlocked });
    }
    appContainer.appendChild(renderDetailView(currentState.selectedItem, currentState.data));
    return;
  }

  let filteredData = performSearch(currentState.data, currentState.searchQuery);

  // DCS attested-only filter + frequency sort
  if (currentState.attestedOnly) {
    filteredData = filteredData.filter(r => r.dcs && r.dcs.total > 0);
  }
  const freq = r => (r.dcs && r.dcs.total) || 0;
  if (currentState.sortBy === 'freq-desc') {
    filteredData = [...filteredData].sort((a, b) => freq(b) - freq(a));
  } else if (currentState.sortBy === 'freq-asc') {
    filteredData = [...filteredData].sort((a, b) => freq(a) - freq(b));
  }

  // Participle form-lookup: surface corpus participle forms matching the query
  const pMatches = findParticipleMatches(
    currentState.data.participleIndex, currentState.searchQuery);
  if (pMatches.length) {
    appContainer.appendChild(
      renderParticipleMatches(pMatches, currentState.data.participleLabels));
  }

  appContainer.appendChild(renderRootList(filteredData));
}

// Start the app
document.addEventListener('DOMContentLoaded', initApp);

