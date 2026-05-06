/**
 * WhitneyRoots v3 Bundle
 * Generated: 2026-05-06T21:40:49.852Z
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
  isLoading: true
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
    const response = await fetch('src/app_data.json');
    const data = await response.json();
    const migrated = migrateAppDataSchema(data);
    updateState({ data: migrated, isLoading: false });
  } catch (error) {
    console.error('Failed to load app data:', error);
    updateState({ isLoading: false });
  }
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

const whitneyQuiz = {
  levels: [
    {
      id: 1,
      title: "Basic Roots",
      questions: [
        {
          question: "What is the meaning of the root √ad?",
          options: ["go", "eat", "praise", "be"],
          answer: "eat"
        },
        {
          question: "Which root means 'to breathe'?",
          options: ["√an", "√as", "√ah", "√am"],
          answer: "√an"
        }
      ]
    }
  ]
};

function startQuiz(levelId) {
  const level = whitneyQuiz.levels.find(l => l.id === levelId);
  if (!level) return null;
  
  return {
    ...level,
    currentQuestion: 0,
    score: 0
  };
}


// --- FILE: core/analytics.js ---
/**
 * @file analytics.js
 * @description Topic clustering and centrality analysis
 */

function buildTopicClusters(data) {
  console.log('Analyzing root clusters...');
  return []; // Placeholder
}

function calculateCentrality(data) {
  console.log('Calculating root centrality...');
  return {}; // Placeholder
}


// --- FILE: core/achievements.js ---
/**
 * @file achievements.js
 * @description Achievement tracking for WhitneyRoots
 */

const achievements = [
  { id: 'first_root', title: 'First Root', description: 'View your first Sanskrit root' },
  { id: 'quiz_master', title: 'Quiz Master', description: 'Complete a quiz with 100% accuracy' }
];

function checkAchievements(state) {
  // Logic to unlock achievements
}


// --- FILE: core/ai.js ---
/**
 * @file ai.js
 * @description AI Insights and heuristic suggestions
 */

function getAIInsights(rootItem) {
  // Heuristic logic to suggest related roots or prefixes
  return `Insight for ${rootItem.root}: This root often appears with the prefix 'pra-'.`;
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


// --- FILE: renderers/lists.js ---
/**
 * @file lists.js
 * @description List rendering for WhitneyRoots
 */




function renderRootList(roots) {
  const listContainer = createElement('div', { class: 'root-list' });
  
  roots.forEach(root => {
    const item = createElement('div', { class: 'list-item' }, [
      renderRootCard(root)
    ]);
    listContainer.appendChild(item);
  });
  
  return listContainer;
}


// --- FILE: renderers/quiz.js ---
/**
 * @file quiz.js
 * @description Quiz renderer for WhitneyRoots
 */





function renderQuiz() {
  const quizState = startQuiz(1); // Default to level 1
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

      createElement('section', {}, [
        createElement('h3', {}, ['Meaning']),
        createElement('p', { class: 'detail-meaning' }, [rootItem.meaning])
      ]),

      createElement('section', { class: 'ai-insights-section' }, [
        createElement('h3', {}, ['AI Insights']),
        createElement('p', {}, [aiInsight])
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
      updateState({ searchQuery: e.target.value });
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

  if (currentState.view === 'quiz') {
    appContainer.appendChild(renderQuiz());
    return;
  }

  if (currentState.view === 'detail') {
    appContainer.appendChild(renderDetailView(currentState.selectedItem, currentState.data));
    return;
  }

  const filteredData = performSearch(currentState.data, currentState.searchQuery);
  
  appContainer.appendChild(renderRootList(filteredData));
}

// Start the app
document.addEventListener('DOMContentLoaded', initApp);

