/**
 * @file cards.js
 * @description Card rendering for WhitneyRoots
 */

import { createElement } from '../utils/dom.js';
import { iastToDevanagari } from '../utils/linguistics.js';
import { updateState } from '../core/state.js';

export function renderRootCard(rootItem) {
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
