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
import { trackProgress } from './core/achievements.js';

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

  const filteredData = performSearch(currentState.data, currentState.searchQuery);
  
  appContainer.appendChild(renderRootList(filteredData));
}

// Start the app
document.addEventListener('DOMContentLoaded', initApp);
