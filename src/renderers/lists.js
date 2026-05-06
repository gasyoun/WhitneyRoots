/**
 * @file lists.js
 * @description List rendering for WhitneyRoots
 */

import { createElement } from '../utils/dom.js';
import { renderRootCard } from './cards.js';

export function renderRootList(roots) {
  const listContainer = createElement('div', { class: 'root-list' });
  
  roots.forEach(root => {
    const item = createElement('div', { class: 'list-item' }, [
      renderRootCard(root)
    ]);
    listContainer.appendChild(item);
  });
  
  return listContainer;
}
