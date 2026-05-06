import { normalizeSanskrit } from '../utils/linguistics.js';

export function performSearch(data, query) {
  if (!query) return data.lexicon;
  
  const normalizedQuery = normalizeSanskrit(query);
  return data.lexicon.filter(item => {
    return normalizeSanskrit(item.root).includes(normalizedQuery) ||
           normalizeSanskrit(item.meaning).includes(normalizedQuery);
  });
}
