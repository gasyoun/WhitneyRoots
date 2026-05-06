/**
 * @file entry.js
 * @description Application entry point
 */

import { state, updateState } from './core/state.js';
import { loadAppData } from './core/data.js';
import { initRouter } from './core/router.js';
import { renderRootList } from './renderers/lists.js';
import { renderQuiz } from './renderers/quiz.js';
import { renderDetailView } from './renderers/detail.js';
import { performSearch } from './core/search.js';

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
