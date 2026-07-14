/**
 * @file linguistics.js
 * @description Linguistic utilities for Sanskrit (Whitney Roots)
 *
 * Thin re-export over the canonical sanskrit-util package — see
 * ../vendor/sanskrit-util.js (a byte-identical copy of sanskrit-util/js/index.mjs, re-copied
 * whole on every package update, never hand-edited) and github-spine/SHARED_CODE.md §1-2. This
 * file used to carry its own inline normalizeSanskrit/iastToDevanagari implementations; those
 * were the donor for sanskrit-util's normalize_sanskrit/iast_to_devanagari (folded in verbatim),
 * so this swap is behaviour-identical, not a rewrite. Do not re-add inline transcode/normalize
 * logic here — extend sanskrit-util instead.
 *
 * Note (parity, not a regression): sanskrit-util's iast_to_devanagari uses the SAME simple
 * character-replace algorithm this file's old iastToDevanagari used (no virama/matra
 * construction) — see SHARED_CODE.md's "iast_to_devanagari is BROKEN" note. Output here is
 * unchanged from before this migration; fixing that display bug is a separate, un-scoped change.
 */
import { normalize_sanskrit, iast_to_devanagari } from '../vendor/sanskrit-util.js';

export function normalizeSanskrit(text) {
  return normalize_sanskrit(text);
}

export function iastToDevanagari(text) {
  return iast_to_devanagari(text);
}
