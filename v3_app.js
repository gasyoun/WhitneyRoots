/**
 * WhitneyRoots v3 Bundle
 * Generated: 2026-06-10T02:46:17.785Z
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
    const [appResp, freqResp, pidxResp] = await Promise.all([
      fetch('src/app_data.json'),
      fetch('src/dcs_freq.json').catch(() => null),
      fetch('src/participle_index.json').catch(() => null)
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


// --- FILE: utils/linguistics.js ---
/**
 * @file linguistics.js
 * @description Linguistic utilities for Sanskrit (Whitney Roots)
 */

function normalizeSanskrit(text) {
  if (!text) return '';
  // Basic normalization: remove accents and lowercase
  return text.normalize('NFD')
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[āīūṛṝḷḹṅñṭḍṇśṣḥṃ]/g, (match) => {
      const map = {
        'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
        'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
        'ḥ': 'h', 'ṃ': 'm'
      };
      return map[match] || match;
    })
    .toLowerCase();
}

const IAST_TO_DEVANAGARI_MAP = {
  'a': 'अ', 'ā': 'आ', 'i': 'इ', 'ī': 'ई', 'u': 'उ', 'ū': 'ऊ', 'ṛ': 'ऋ', 'ṝ': 'ॠ', 'ḷ': 'ऌ', 'ḹ': 'ॡ',
  'e': 'ए', 'ai': 'ऐ', 'o': 'ओ', 'au': 'औ', 'ṃ': 'ं', 'ḥ': 'ः',
  'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ', 'ṅ': 'ङ',
  'c': 'च', 'ch': 'छ', 'j': 'ज', 'jh': 'झ', 'ñ': 'ञ',
  'ṭ': 'ट', 'ṭh': 'ठ', 'ḍ': 'ड', 'ḍh': 'ढ', 'ṇ': 'ण',
  't': 'त', 'th': 'थ', 'd': 'द', 'dh': 'ध', 'n': 'न',
  'p': 'प', 'ph': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
  'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व',
  'ś': 'श', 'ṣ': 'ष', 's': 'स', 'h': 'ह'
};

function iastToDevanagari(text) {
  // Simple replacement logic (not full phonological rules, but useful for basic display)
  let result = text.toLowerCase();
  Object.keys(IAST_TO_DEVANAGARI_MAP).sort((a, b) => b.length - a.length).forEach(key => {
    const regex = new RegExp(key, 'g');
    result = result.replace(regex, IAST_TO_DEVANAGARI_MAP[key]);
  });
  return result;
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

