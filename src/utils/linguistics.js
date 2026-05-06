/**
 * @file linguistics.js
 * @description Linguistic utilities for Sanskrit (Whitney Roots)
 */

export function normalizeSanskrit(text) {
  if (!text) return '';
  // Basic normalization: remove accents and lowercase
  return text.normalize('NFD')
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[āīūṛṝḷḹṅñṭḍṇśṣḥṃ]/g, (match) => {
      const map = {
        'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
        'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
        'ḥ': 'h', 'ṃ': 'm'
      };
      return map[match] || match;
    })
    .toLowerCase();
}

const IAST_TO_DEVANAGARI_MAP = {
  'a': 'अ', 'ā': 'आ', 'i': 'इ', 'ī': 'ई', 'u': 'उ', 'ū': 'ऊ', 'ṛ': 'ऋ', 'ṝ': 'ॠ', 'ḷ': 'ऌ', 'ḹ': 'ॡ',
  'e': 'ए', 'ai': 'ऐ', 'o': 'ओ', 'au': 'औ', 'ṃ': 'ं', 'ḥ': 'ः',
  'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ', 'ṅ': 'ङ',
  'c': 'च', 'ch': 'छ', 'j': 'ज', 'jh': 'झ', 'ñ': 'ञ',
  'ṭ': 'ट', 'ṭh': 'ठ', 'ḍ': 'ड', 'ḍh': 'ढ', 'ṇ': 'ण',
  't': 'त', 'th': 'थ', 'd': 'द', 'dh': 'ध', 'n': 'न',
  'p': 'प', 'ph': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
  'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व',
  'ś': 'श', 'ṣ': 'ष', 's': 'स', 'h': 'ह'
};

export function iastToDevanagari(text) {
  // Simple replacement logic (not full phonological rules, but useful for basic display)
  let result = text.toLowerCase();
  Object.keys(IAST_TO_DEVANAGARI_MAP).sort((a, b) => b.length - a.length).forEach(key => {
    const regex = new RegExp(key, 'g');
    result = result.replace(regex, IAST_TO_DEVANAGARI_MAP[key]);
  });
  return result;
}
