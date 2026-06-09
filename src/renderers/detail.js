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

      buildDcsSection(rootItem),

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

const ROMAN_TO_ARABIC = {
  I: '1', II: '2', III: '3', IV: '4', V: '5',
  VI: '6', VII: '7', VIII: '8', IX: '9', X: '10'
};

function chip(text, cls) {
  return createElement('span', { class: cls || 'dcs-chip' }, [text]);
}

/**
 * The DCS corpus section: frequency/rank, class comparison + verdict,
 * PPP confirmation, the 9 participle categories, top forms and preverbs.
 * Falls back to a neutral note when the root is not in the corpus.
 */
function buildDcsSection(rootItem) {
  const dcs = rootItem.dcs;
  if (!dcs || dcs.total === 0) {
    return createElement('section', { class: 'dcs-section' }, [
      createElement('h3', {}, ['DCS Corpus']),
      createElement('p', { class: 'dcs-none-note' }, [
        'Not attested in the Digital Corpus of Sanskrit. ' +
        'This root is listed by Whitney but the corpus offers no usage evidence.'
      ])
    ]);
  }

  // ---- class comparison + verdict ----
  const wClasses = (rootItem.classes || []).map(c => ROMAN_TO_ARABIC[c] || c);
  const dClasses = dcs.grammar_class || [];
  const wset = new Set(wClasses);
  const dset = new Set(dClasses);
  let verdict = 'no DCS class', vcls = 'neutral';
  if (dClasses.length) {
    const inter = [...wset].filter(x => dset.has(x));
    const same = wset.size === dset.size && inter.length === wset.size;
    if (same) { verdict = 'agree'; vcls = 'agree'; }
    else if (inter.length) { verdict = 'partial overlap'; vcls = 'partial'; }
    else { verdict = 'differ'; vcls = 'differ'; }
  }
  const signal = dcs.present_stem_signal && dcs.present_stem_signal.dominant;

  const classRow = createElement('div', { class: 'dcs-class-compare' }, [
    createElement('div', { class: 'dcs-cc-col' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['Whitney']),
      createElement('span', {}, [wClasses.join(', ') || '—'])
    ]),
    createElement('div', { class: 'dcs-cc-col' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['DCS grammar']),
      createElement('span', {}, [dClasses.join(', ') || '—'])
    ]),
    createElement('div', { class: 'dcs-cc-col' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['Corpus signal']),
      createElement('span', {}, [signal || '—'])
    ]),
    createElement('span', { class: `dcs-verdict ${vcls}` }, [verdict])
  ]);

  // ---- PPP confirmation (Whitney's listed PPP vs attested) ----
  let pppRow = null;
  const wppp = (rootItem.ppp || []).filter(Boolean);
  if (wppp.length) {
    const attested = new Set((dcs.participles && dcs.participles['past-passive']
      ? dcs.participles['past-passive'].top : []).map(t => fold(t.form)));
    // also fold the derived ppp stems for a broader confirm set
    (dcs.ppp || []).forEach(s => attested.add(fold(s.stem)));
    pppRow = createElement('div', { class: 'dcs-ppp-check' }, [
      createElement('span', { class: 'dcs-cc-label' }, ['Whitney PPP vs corpus: ']),
      ...wppp.map(p => {
        const pf = fold(p);
        const ok = [...attested].some(a => a === pf || a.startsWith(pf));
        return chip(`${p} ${ok ? '✓' : '✗'}`, `dcs-chip ${ok ? 'ok' : 'miss'}`);
      })
    ]);
  }

  // ---- participles (the 9 categories) ----
  let partBlock = null;
  const parts = dcs.participles || {};
  const cats = Object.keys(parts);
  if (cats.length) {
    partBlock = createElement('div', { class: 'dcs-participles' },
      cats.map(cat => {
        const info = parts[cat];
        return createElement('div', { class: 'dcs-part-cat' }, [
          createElement('div', { class: 'dcs-part-head' }, [
            createElement('span', { class: 'dcs-part-label' }, [info.label || cat]),
            createElement('span', { class: 'dcs-part-n' }, [`${info.total.toLocaleString()}`])
          ]),
          createElement('div', { class: 'dcs-part-forms' },
            (info.top || []).slice(0, 5).map(t => chip(t.form))
          )
        ]);
      })
    );
  }

  // ---- top forms + preverbs ----
  const topForms = (dcs.top_forms || []).slice(0, 12);
  const preverbs = (dcs.preverbs || []).slice(0, 10);

  return createElement('section', { class: 'dcs-section' }, [
    createElement('h3', {}, ['DCS Corpus']),
    createElement('div', { class: 'dcs-freq-line' }, [
      createElement('span', { class: 'dcs-freq-big' }, [dcs.total.toLocaleString()]),
      createElement('span', { class: 'dcs-freq-unit' }, ['attestations']),
      dcs.rank ? createElement('span', { class: 'dcs-rank-pill' }, [`rank #${dcs.rank}`]) : null
    ]),

    createElement('h4', {}, ['Verb class — Whitney vs corpus']),
    classRow,
    createElement('p', { class: 'dcs-foot' }, [
      'DCS grammar is itself lexicon metadata; the corpus signal is a coarse ' +
      'present-stem heuristic. Disagreement is not proof Whitney is wrong.'
    ]),

    pppRow,

    partBlock ? createElement('h4', {}, ['Participles attested in the corpus']) : null,
    partBlock,

    topForms.length ? createElement('h4', {}, ['Most frequent forms']) : null,
    topForms.length ? createElement('div', { class: 'dcs-chips' },
      topForms.map(t => chip(`${t.form} (${t.n})`))) : null,

    preverbs.length ? createElement('h4', {}, ['Preverb compounds']) : null,
    preverbs.length ? createElement('div', { class: 'dcs-chips' },
      preverbs.map(p => chip(`${p.form} (${p.n.toLocaleString()})`))) : null
  ]);
}

/** Diacritic fold to match Whitney's ASCII PPP against DCS IAST forms. */
function fold(s) {
  if (!s) return '';
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[āīūṛṝḷḹṅñṭḍṇśṣḥṃṁ]/g, m => ({
      'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
      'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
      'ḥ': 'h', 'ṃ': 'm', 'ṁ': 'm'
    }[m] || m)).toLowerCase();
}
