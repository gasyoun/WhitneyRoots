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
    renderDcsBadge(rootItem),
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

/**
 * Compact DCS corpus-frequency badge for a card.
 * Attested roots get a token count + corpus rank; unmatched / zero-attestation
 * roots get a neutral "not in DCS corpus" tag (no judgement implied).
 */
export function renderDcsBadge(rootItem) {
  const dcs = rootItem.dcs;
  if (!dcs) return null;
  if (dcs.total > 0) {
    return createElement('div', { class: 'dcs-badge', title: 'Digital Corpus of Sanskrit attestations' }, [
      createElement('span', { class: 'dcs-freq' }, [`${dcs.total.toLocaleString()}×`]),
      dcs.rank ? createElement('span', { class: 'dcs-rank' }, [`#${dcs.rank}`]) : null
    ]);
  }
  return createElement('span', { class: 'dcs-tag-none' }, ['not in DCS corpus']);
}
