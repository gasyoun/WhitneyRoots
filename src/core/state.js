/**
 * @file state.js
 * @description Global state management for WhitneyRoots
 */

export const state = {
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

export function updateState(newState) {
  Object.assign(state, newState);
  document.dispatchEvent(new CustomEvent('statechange', { detail: state }));
}
