import { normalizeSanskrit } from '../utils/linguistics.js';

export function performSearch(data, query) {
  if (!query) return data.lexicon;

  const normalizedQuery = normalizeSanskrit(query);
  return data.lexicon.filter(item => {
    return normalizeSanskrit(item.root).includes(normalizedQuery) ||
           normalizeSanskrit(item.meaning).includes(normalizedQuery);
  });
}

/**
 * Look up a (possibly inflected) participle surface form in the DCS index and
 * return the roots it belongs to. Diacritic-insensitive so users can paste
 * either IAST or plain ASCII (kriyamāṇe / kriyamane).
 */
export function findParticipleMatches(index, query, limit = 60) {
  if (!index || !query) return [];
  const nq = normalizeSanskrit(query);
  if (nq.length < 2) return [];
  const exact = [];
  const prefix = [];
  for (const form in index) {
    const nf = normalizeSanskrit(form);
    if (nf === nq) {
      index[form].forEach(hit => exact.push({ form, ...hit }));
    } else if (nf.startsWith(nq)) {
      index[form].forEach(hit => prefix.push({ form, ...hit }));
    }
    if (exact.length + prefix.length > limit * 3) break;
  }
  return exact.concat(prefix).slice(0, limit);
}
