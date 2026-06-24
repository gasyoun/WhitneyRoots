/**
 * @file affixes.js
 * @description Affix explorer view — Sanskrit suffixes grouped by what they FORM, sized by
 * Apte productivity, with click-to-expand anubandha decoding + example derivatives.
 * Data: src/affix_data.json (built by SanskritLexicography/.../affix_pedagogy.py).
 */

import { createElement } from '../utils/dom.js';

const KIND_CLASS = {
  'kṛt': 'affix-kind-krt',
  'taddhita': 'affix-kind-tad',
  'strī': 'affix-kind-stri',
  'taddhita/kṛt': 'affix-kind-tad'
};

export function renderAffixes(data) {
  const payload = data && data.affixes;
  const affixes = (payload && payload.affixes) || [];
  if (!affixes.length) {
    return createElement('div', { class: 'affix-explorer' }, [
      createElement('h2', {}, ['Sanskrit affixes']),
      createElement('p', { class: 'affix-intro' }, ['Affix data not loaded (src/affix_data.json).'])
    ]);
  }

  const maxR = Math.max(...affixes.map(a => a.apte_roots || 0)) || 1;
  const groups = {};
  affixes.forEach(a => { (groups[a.group] = groups[a.group] || []).push(a); });
  const sum = arr => arr.reduce((s, a) => s + (a.apte_roots || 0), 0);
  const order = Object.keys(groups).sort((x, y) => sum(groups[y]) - sum(groups[x]));

  const listWrap = createElement('div', { class: 'affix-list' }, []);
  const filter = createElement('input', {
    class: 'affix-filter', type: 'text',
    placeholder: 'filter by suffix, function, or pratyaya…'
  });
  filter.addEventListener('input', e => renderList(e.target.value));

  function renderList(q) {
    listWrap.replaceChildren();
    const f = (q || '').toLowerCase();
    order.forEach(g => {
      const items = groups[g]
        .filter(a => !f || (a.surface + a.pratyaya + a.function + a.group).toLowerCase().includes(f))
        .sort((a, b) => (b.apte_roots || 0) - (a.apte_roots || 0));
      if (!items.length) return;
      listWrap.appendChild(createElement('div', { class: 'affix-group' }, [
        createElement('h3', { class: 'affix-group-title' }, [g]),
        ...items.map(affixCard)
      ]));
    });
  }

  function affixCard(a) {
    const pct = Math.round(100 * (a.apte_roots || 0) / maxR);
    const card = createElement('div', { class: 'affix-card', tabindex: '0', role: 'button' }, [
      createElement('div', { class: 'affix-card-head' }, [
        createElement('span', { class: 'affix-surface' }, ['-' + a.surface]),
        createElement('span', { class: 'affix-pill ' + (KIND_CLASS[a.kind] || '') },
          [a.pratyaya_deva + '  ' + a.pratyaya]),
        createElement('span', { class: 'affix-func' }, [a.function]),
        createElement('span', { class: 'affix-count' }, [(a.apte_roots || 0) + ' roots'])
      ]),
      createElement('div', { class: 'affix-bar' }, [
        createElement('div', { class: 'affix-bar-fill', style: 'width:' + pct + '%' }, [])
      ])
    ]);
    let detail = null;
    const toggle = () => {
      if (detail) { detail.remove(); detail = null; return; }
      const steps = (a.anubandha || []).map(s =>
        createElement('span', { class: 'affix-step' }, [s]));
      const exs = (a.examples || []).map(e => createElement('span', { class: 'affix-ex' }, [
        createElement('span', { class: 'affix-ex-root' }, [e.root]),
        ' → ',
        createElement('span', { class: 'affix-ex-word' }, [e.word_iast])
      ]));
      const meta = a.kind + (a.mw_count ? '  ·  MW surface-suffix headwords: ' + a.mw_count : '');
      detail = createElement('div', { class: 'affix-detail' }, [
        createElement('div', { class: 'affix-detail-row' },
          [createElement('span', { class: 'affix-detail-label' }, ['Anubandha → surface: ']), ...steps]),
        createElement('div', { class: 'affix-detail-row' },
          [createElement('span', { class: 'affix-detail-label' }, ['Examples: ']),
           ...(exs.length ? exs : [createElement('span', { class: 'affix-ex' }, ['—'])])]),
        createElement('div', { class: 'affix-detail-meta' }, [meta])
      ]);
      detail.addEventListener('click', e => e.stopPropagation());
      card.appendChild(detail);
    };
    card.addEventListener('click', toggle);
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
    });
    return card;
  }

  renderList('');
  return createElement('div', { class: 'affix-explorer' }, [
    createElement('h2', {}, ['Sanskrit affixes — what forms what']),
    createElement('p', { class: 'affix-intro' }, [
      'Affixes grouped by what they form, sized by Apte productivity (number of distinct roots taking the affix). ' +
      'Click an affix for its anubandha (it-marker) decoding and example derivatives. ' +
      'kṛt = from verb roots · taddhita = from nominal stems · strī = feminine.'
    ]),
    filter,
    listWrap
  ]);
}
