/**
 * @file router.js
 * @description Hash-based routing for WhitneyRoots
 */

import { updateState } from './state.js';

export function initRouter() {
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

export function navigateTo(route) {
  window.location.hash = route;
}
