/**
 * @file detail.js
 * @description Detail view renderer for a single Whitney root
 */

import { createElement } from '../utils/dom.js';
import { updateState } from '../core/state.js';
import { iastToDevanagari } from '../utils/linguistics.js';
import { getAIInsights, getPrefixSuggestions } from '../core/ai.js';

export function renderDetailView(rootId, data) {
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
