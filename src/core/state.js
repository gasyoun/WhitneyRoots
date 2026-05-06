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
