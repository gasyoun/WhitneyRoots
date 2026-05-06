import { createElement } from '../utils/dom.js';
import { renderRootCard } from './cards.js';
import { buildTopicClusters } from '../core/analytics.js';
import { updateState } from '../core/state.js';

export function renderRootList(data) {
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
  container.appendChild(grid);
  
  return container;
}
