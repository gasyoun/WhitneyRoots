// sanskrit_util — shared Sanskrit string helpers for the CDSL / Sanskrit-Lexicon repos.
//
// Behaviour-identical port of py/sanskrit_util/__init__.py (proved by ../vectors/vectors.json).
// Consolidated from WhitneyRoots reader.js (deva2iast/norm/nfold), linguistics.js
// (normalizeSanskrit/iastToDevanagari) and scripts/sanskrit_util.py (to_slp1/from_slp1/
// to_roman/form_key). See README for which key to use when.

// ---- IAST -> SLP1 (longest-key-first; aspirates + diphthongs are digraphs) ----
const SLP1 = {
  ai: 'E', au: 'O', kh: 'K', gh: 'G', ch: 'C', jh: 'J', 'ṭh': 'W', 'ḍh': 'Q',
  th: 'T', dh: 'D', ph: 'P', bh: 'B',
  'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṛ': 'f', 'ṝ': 'F', 'ḷ': 'x', 'ḹ': 'X',
  'ṃ': 'M', 'ṁ': 'M', 'ḥ': 'H', 'ṅ': 'N', 'ñ': 'Y', 'ṭ': 'w', 'ḍ': 'q', 'ṇ': 'R',
  'ś': 'S', 'ṣ': 'z', 'ḻ': 'L',
  a: 'a', i: 'i', u: 'u', e: 'e', o: 'o', k: 'k', g: 'g', c: 'c', j: 'j',
  t: 't', d: 'd', n: 'n', p: 'p', b: 'b', m: 'm', y: 'y', r: 'r', l: 'l',
  v: 'v', s: 's', h: 'h',
};

export function to_slp1(iast) {
  const s = iast || '';
  let out = '', i = 0;
  while (i < s.length) {
    const two = s.slice(i, i + 2);
    if (SLP1[two] !== undefined) { out += SLP1[two]; i += 2; continue; }
    const one = s[i];
    out += (SLP1[one] !== undefined ? SLP1[one] : one); i += 1;
  }
  return out;
}

const ROMAN = { 1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X' };

export function to_roman(nums) {
  return (nums || []).filter((n) => ROMAN[n] !== undefined).map((n) => ROMAN[n]);
}

// ---- SLP1 -> IAST ----
const FROM_SLP1 = {
  A: 'ā', I: 'ī', U: 'ū', f: 'ṛ', F: 'ṝ', x: 'ḷ', X: 'ḹ',
  E: 'ai', O: 'au', M: 'ṃ', H: 'ḥ',
  K: 'kh', G: 'gh', N: 'ṅ', C: 'ch', J: 'jh', Y: 'ñ',
  w: 'ṭ', W: 'ṭh', q: 'ḍ', Q: 'ḍh', R: 'ṇ',
  T: 'th', D: 'dh', P: 'ph', B: 'bh',
  S: 'ś', z: 'ṣ', L: 'ḻ',
};

export function from_slp1(slp1) {
  let out = '';
  for (const ch of (slp1 || '')) out += (FROM_SLP1[ch] !== undefined ? FROM_SLP1[ch] : ch);
  return out;
}

// ---- Devanāgarī -> IAST (inherent-'a' + virāma aware) ----
const DV_VOWEL = { 'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au' };
const DV_MATRA = { 'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ', 'ॢ': 'ḷ', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au' };
const DV_CONS = { 'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ', 'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'ñ', 'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'ś', 'ष': 'ṣ', 'स': 's', 'ह': 'h', 'ळ': 'ḷ' };
const DV_MARK = { 'ं': 'ṃ', 'ः': 'ḥ', 'ँ': 'ṃ' };
const VIRAMA = '्';

export function deva_to_iast(s) {
  s = s || '';
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (DV_CONS[ch] != null) {
      out += DV_CONS[ch];
      const nx = s[i + 1];
      if (nx === VIRAMA) { i++; }
      else if (DV_MATRA[nx] != null) { out += DV_MATRA[nx]; i++; }
      else { out += 'a'; }
    } else if (DV_VOWEL[ch] != null) { out += DV_VOWEL[ch]; }
    else if (DV_MARK[ch] != null) { out += DV_MARK[ch]; }
    else if (ch === 'ऽ') { /* avagraha — drop */ }
    else { out += ch; }
  }
  return out;
}

// ---- Devanāgarī -> SLP1 (direct; the ळ→L vs x decision is made HERE) ----
// deva_to_iast collapses ळ (U+0933, retroflex ḻa) onto vocalic ḷ (both render as IAST ḷ/U+1E37),
// so to_slp1(deva_to_iast('ळ')) would yield 'x' (vocalic ḷ) instead of 'L'. SLP1 keeps them apart
// and that can't be recovered after the IAST step, so we transcode Devanāgarī → SLP1 directly:
// derive the maps from the IAST maps (tracking to_slp1) and override ळ → 'L'. Round-trip partner
// of from_slp1 ('L' → ḻ), where to_slp1∘deva_to_iast is not. Mirror of the Python deva_to_slp1.
const mapVals = (m) => Object.fromEntries(Object.entries(m).map(([k, v]) => [k, to_slp1(v)]));
const DV_VOWEL_SLP1 = mapVals(DV_VOWEL);
const DV_MATRA_SLP1 = mapVals(DV_MATRA);
const DV_CONS_SLP1 = mapVals(DV_CONS);
DV_CONS_SLP1['ळ'] = 'L';        // retroflex ḻa — NOT 'x' (vocalic ḷ, from ऌ); see note above
const DV_MARK_SLP1 = mapVals(DV_MARK);

export function deva_to_slp1(s) {
  s = s || '';
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (DV_CONS_SLP1[ch] != null) {
      out += DV_CONS_SLP1[ch];
      const nx = s[i + 1];
      if (nx === VIRAMA) { i++; }
      else if (DV_MATRA_SLP1[nx] != null) { out += DV_MATRA_SLP1[nx]; i++; }
      else { out += 'a'; }
    } else if (DV_VOWEL_SLP1[ch] != null) { out += DV_VOWEL_SLP1[ch]; }
    else if (DV_MARK_SLP1[ch] != null) { out += DV_MARK_SLP1[ch]; }
    else if (ch === 'ऽ') { /* avagraha — drop */ }
    else { out += ch; }
  }
  return out;
}

// ---- SLP1 -> Devanāgarī (real transcode: virāma conjuncts + mātrās) ----
// Round-trip partner of deva_to_slp1: for canonical SLP1, deva_to_slp1(slp1_to_devanagari(s)) == s
// (proved on the full alphabet + 1000 real MW headwords). Unlike iast_to_devanagari (a display-only
// replace), this supplies the virāma between clustered consonants and picks independent-vowel vs
// mātrā by position. The vowel/mātrā/consonant maps are INVERTED from the same Devanāgarī→SLP1 maps
// deva_to_slp1 uses (kept in lock-step); only the 3 marks are explicit (M→anusvāra, H→visarga,
// ~→candrabindu) since anusvāra and candrabindu both map back to 'M' and can't be inverted. Not
// round-trip stable (matching deva_to_slp1): candrabindu (~→ँ→'M') and avagraha ('→ऽ, dropped).
const invert = (m) => Object.fromEntries(Object.entries(m).map(([k, v]) => [v, k]));
const SLP1_TO_DV_VOWEL = invert(DV_VOWEL_SLP1);
const SLP1_TO_DV_MATRA = invert(DV_MATRA_SLP1);
SLP1_TO_DV_MATRA['a'] = '';        // inherent 'a' takes no sign
const SLP1_TO_DV_CONS = invert(DV_CONS_SLP1);
const SLP1_TO_DV_MARK = { M: 'ं', H: 'ः', '~': 'ँ' }; // anusvāra / visarga / candrabindu

export function slp1_to_devanagari(slp1) {
  const s = slp1 || '';
  let out = '';
  let pendingCons = false;         // a consonant sign was emitted, still awaits its vowel/virāma
  for (const ch of s) {
    if (SLP1_TO_DV_CONS[ch] != null) {
      if (pendingCons) out += VIRAMA;               // previous consonant had no vowel -> conjunct
      out += SLP1_TO_DV_CONS[ch];
      pendingCons = true;
    } else if (SLP1_TO_DV_VOWEL[ch] != null) {
      if (pendingCons) { out += SLP1_TO_DV_MATRA[ch]; pendingCons = false; } // mātrā ('' for 'a')
      else out += SLP1_TO_DV_VOWEL[ch];             // independent vowel sign
    } else {                                        // mark, avagraha, accent, digit, space, other
      if (pendingCons) { out += VIRAMA; pendingCons = false; }
      if (ch === "'") out += 'ऽ';                   // avagraha
      else out += (SLP1_TO_DV_MARK[ch] != null ? SLP1_TO_DV_MARK[ch] : ch);
    }
  }
  if (pendingCons) out += VIRAMA;                   // trailing bare consonant
  return out;
}

// ---- IAST -> Devanāgarī (real transcode via to_slp1 -> slp1_to_devanagari composition;
// virāma + mātrā aware. Previously a naive longest-key-first character substitution that
// never applied virāma/mātrā and emitted an independent vowel sign after every consonant
// (wrong on 9 of 9 basic words, e.g. 'ka' -> कअ instead of क). Fixed per H1394.) ----

export function iast_to_devanagari(text) {
  return slp1_to_devanagari(to_slp1((text || '').toLowerCase()));
}

// ---- normalization keys ----
const DEVA_RE = /[ऀ-ॿ]/;

// Whitespace pinned to match the Python port's _WS_CHARS exactly. JS String.trim()/\s strip the
// BOM/ZWNBSP U+FEFF (which sneaks in when a file is read without a BOM-aware decoder) while Python
// str.strip()/\s do not (and conversely Python strips U+0085 NEL) — list the class explicitly so
// norm()/form_key()/slp1_norm() yield identical keys in both languages.
const WS = '\\t\\n\\x0b\\f\\r \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000\\ufeff';
const WS_TRIM_RE = new RegExp('^[' + WS + ']+|[' + WS + ']+$', 'g');
const WS_RUN_RE = new RegExp('[' + WS + ']+', 'g');
const wstrim = (s) => s.replace(WS_TRIM_RE, '');

export function norm(s) {
  s = s || '';
  if (DEVA_RE.test(s)) s = deva_to_iast(s);
  return wstrim(s.normalize('NFD').replace(/\p{Mn}/gu, '').normalize('NFC').toLowerCase());
}

export function nfold(s) {
  return norm(s).replace(/[mn]/g, 'n');
}

// ---- length-preserving comparison key ----
const FK_ACCENT = new Set(['́', '̀', '॑', '॒']); // acute, grave, Vedic svarita/anudātta
const FK_VOWELS = new Set([...'aāiīuūṛṝḷḹeēoō']);
const COMBINING_RE = /\p{Mn}/u;

export function form_key(s) {
  s = wstrim(s || '').toLowerCase();
  if (s === '-' || s === '–' || s === '—') return '';
  s = s.replace(/ḥ$/, '');
  // WORD-FINAL anusvāra is underlyingly /m/: Sanskrit writes final -m as anusvāra before a
  // consonant and as -m in pausa or before a vowel, so `rasaṃ` and `rasam` are one word in
  // two spellings. Must run BEFORE the general fold below, which would otherwise send the
  // anusvāra to `n` and leave the real `m` alone — the two spellings then never collide, and
  // every anusvāra-final attestation reads as un-generated. Deliberately does NOT touch
  // final `n`: `rājan` and a hypothetical `rājam` stay distinct keys.
  s = s.replace(/[ṃṁ]$/, 'm');            // final anusvāra -> m (H3911)
  s = s.replace(/[ṃṁṅñṇ]/g, 'n');
  const out = [];
  for (const ch of s.normalize('NFD')) {
    if (FK_ACCENT.has(ch)) {
      let j = out.length - 1;
      while (j >= 0 && COMBINING_RE.test(out[j])) j -= 1;
      const base = j >= 0 ? out.slice(j).join('').normalize('NFC') : '';
      if (FK_VOWELS.has(base)) continue;
    }
    out.push(ch);
  }
  return out.join('').normalize('NFC');
}

// ---- lossy ASCII-folding search key (v3-explorer normalizeSanskrit) ----
const NS_MAP = {
  'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
  'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
  'ḥ': 'h', 'ṃ': 'm',
};

export function normalize_sanskrit(text) {
  if (!text) return '';
  return text.normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[āīūṛṝḷḹṅñṭḍṇśṣḥṃ]/g, (m) => NS_MAP[m] || m)
    .toLowerCase();
}

// ---- SLP1-side API ----
// The CDSL dictionaries store headwords in SLP1, where case is PHONEMIC (S=ś≠s) — so the
// IAST helpers above can't key them without a transcode, and every CDSL repo re-rolled its own
// SLP1 alphabet + headword normalizer. Behaviour-identical port of the Python additions.
export const SLP1_VOWELS = 'aAiIuUfFxXeEoO';                          // f/F=ṛ/ṝ, x/X=ḷ/ḹ, E=ai, O=au
export const SLP1_MARKS = 'MH~';                                     // anusvāra, visarga, candrabindu
export const SLP1_CONSONANTS = 'kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL'; // L = Vedic retroflex ḻa
export const SLP1_ALPHABET = SLP1_VOWELS + SLP1_MARKS + SLP1_CONSONANTS; // valid SLP1 letters (no avagraha)

const SLP1_ACCENTS_RE = /[/\\^~]/g; // udātta / anudātta / svarita / candrabindu

export function strip_slp1_accents(slp1) {
  return (slp1 ?? '').replace(SLP1_ACCENTS_RE, '');
}

export function slp1_norm(slp1) {
  let s = strip_slp1_accents(slp1 ?? '');
  s = s.replace(/\d+$/, '');
  return wstrim(s.replace(WS_RUN_RE, ' '));
}

export function slp1_form_key(slp1) {
  return form_key(from_slp1(strip_slp1_accents(slp1 ?? '')));
}

// Fuzzy-match key: fold ALL SLP1 distinctions to plain ASCII — the lossy extreme of the SLP1 key
// family. For building/querying MW headword indexes (mw_en_tm.json); index and query sides agree
// because both use standard SLP1 (R=ṇ). ⚠️ guṇa = 'guRa' in MW — forgetting R→n maps it to 'gūna'.
export function slp1_simplify(slp1) {
  let s = slp1 || '';
  s = s.replace(/K/g, 'kh').replace(/G/g, 'gh')
    .replace(/C/g, 'ch').replace(/J/g, 'jh')
    .replace(/T/g, 'th').replace(/D/g, 'dh')
    .replace(/P/g, 'ph').replace(/B/g, 'bh');
  s = s.replace(/S/g, 's').replace(/z/g, 's');
  s = s.replace(/Y/g, 'n').replace(/N/g, 'n').replace(/R/g, 'n');   // R=ṇ is the critical case
  s = s.replace(/A/g, 'a').replace(/I/g, 'i').replace(/U/g, 'u');
  s = s.replace(/E/g, 'ai').replace(/O/g, 'au');
  s = s.replace(/f/g, 'r').replace(/F/g, 'r').replace(/x/g, 'l').replace(/X/g, 'l');
  s = s.replace(/M/g, 'm').replace(/H/g, '');
  s = s.replace(/W/g, 'th').replace(/Q/g, 'dh');
  s = s.replace(/w/g, 't').replace(/q/g, 'd');
  s = s.replace(/L/g, 'l');                                         // Vedic retroflex ḻa
  return s.toLowerCase();
}

// ---- CDSL raw source line -> readable IAST (display layer over from_slp1) ----
// A raw csl-orig line is SLP1 inside CDSL markup, unreadable to a human. These
// render it to IAST honoring each dictionary's encoding: MW <s>…</s>;
// PW/PWG/AP/WIL {#…#} (with the meaning language in {%…%}, left as-is);
// VCP/SKD whole-line SLP1 prose. The markup shell (tags, [Page…] markers, the ¦
// headword separator) is stripped. `code` is the csl-orig dict code
// (mw, ap, pwg, pw, wil, vcp, skd). Non-SLP1 spans — glosses, <ls> citations,
// grammar abbreviations like "f." — are preserved.
const _PROSE_SLP1_DICTS = new Set(['vcp', 'skd']);

function _stripCdslMarkup(text) {
  return text
    .replace(/<info[^>]*\/?>/gi, '')   // metadata self-closing tags
    .replace(/\[Page[^\]]*\]/g, '')    // VCP/SKD page markers
    .replace(/<[^>]+>/g, '');          // any remaining tag shell
}

function _cleanCdsl(text) {
  return text
    .replace(/¦/g, ' ')                // ¦ headword/body separator
    .replace(/\s+([,.;:!?])/g, '$1')   // pull punctuation back
    .replace(/\s+/g, ' ')
    .trim();
}

export function source_line_to_iast(text, code) {
  if (text == null) return '';
  const c = String(code || '').toLowerCase();
  if (_PROSE_SLP1_DICTS.has(c)) {
    const s = String(text).replace(/[A-Za-z~']+/g, (m) => from_slp1(m));
    return _cleanCdsl(_stripCdslMarkup(s));
  }
  let s = String(text);
  s = s.replace(/\{[#@]([^#@]*)[#@]\}/g, (_, x) => from_slp1(x));   // {#…#}, {@…@}
  s = s.replace(/<s\d?>([^<]*)<\/s\d?>/gi, (_, x) => from_slp1(x)); // MW <s>…</s>
  s = s.replace(/\{%([^%]*)%\}/g, (_, x) => x);                    // meaning: unwrap, keep
  return _cleanCdsl(_stripCdslMarkup(s));
}

export function source_text_to_iast(text, code) {
  if (text == null) return '';
  return String(text).split('\n').map((l) => source_line_to_iast(l, code)).join('\n');
}

// ---- German lexicographic-apparatus (metalanguage) detection -----------------
// Behaviour-identical port of the Python classify_german_metalanguage — see the
// Python module for the full harvest provenance (pwg_tm_fragmentize GRAMMAR_AB /
// FORMULA_AB / FORMULA_PHRASES, compile_translatable GRAM, microstructure FUNC_DE
// ∪ pwg_mask DE_FUNCTION, H2684 extras, H2787 defect formulae). PWG/PW apparatus
// spans ("eines", "im Comp. vorangehend", "adj.") must never be translated as
// ordinary gloss prose; 'uncertain' (bare "so" / "Ergänzung") is the consumer's
// treat-as-not-gloss-and-log case.
export const GERMAN_GRAMMAR_AB = new Set([
  'adj.', 'adv.', 'm.', 'f.', 'n.', 'm. n.', 'f. n.', 'm. f.', 'm. f. n.',
  'partic.', 'part.', 'caus.', 'desid.', 'intens.', 'pass.', 'med.', 'act.',
  'nom.', 'acc.', 'instr.', 'dat.', 'abl.', 'gen.', 'loc.', 'voc.',
  'sg.', 'du.', 'pl.', 'inf.', 'abs.', 'ger.', 'impf.', 'perf.', 'aor.',
  'opt.', 'impv.', 'fut.', 'cond.', 'ppp.', 'pp.', 'subst.', 'interj.',
  'pron.', 'num.', 'indecl.', 'comp.', 'superl.', 'denomin.', 'desid',
  'partic', 'caus',
]);
export const GERMAN_GRAMMAR_BARE = new Set([
  'Subst', 'Adj', 'Adv', 'Indekl', 'PostP', 'mfn', 'ifc', 'NPr',
  'Pl', 'Sg', 'Du', 'Akk', 'Lok', 'Dat', 'Gen', 'Instr', 'Nom', 'Vok',
]);
export const GERMAN_FORMULA_AB = new Set([
  'vgl.', 's. u.', 's. d.', 's. v.', 's. u. d.', 'fgg.', 'fg.', 'dass.',
  'ebend.', 'u.s.w.', 'desgl.', 'dgl.', 'sc.', 'scil.', 's. u. d. W.',
  // H2684 one-bounded-repair extras
  'demin.', 'personif.', 'uebertr.',
]);
// Pattern STRINGS (compiled case-insensitive); identical to the Python tuple.
export const GERMAN_FORMULA_PHRASES = [
  'am Anf(?:ange|\\.) eines Comp(?:ositums?|\\.)?',
  'am Ende eines Comp(?:ositums?|\\.)?',
  'an der Spitze eines Comp(?:ositums?|\\.)?',
  'mit Ergänzung von',
  'im Comp\\.(?:,? vorangehend[a-z]*)?',
  'in Verbindung mit',
  's\\.\\s*u\\.\\s*d\\.\\s*W\\.',
];
export const GERMAN_FUNCTION_WORDS = new Set(
  ('der die das den dem des ein eine einen einem eines einer und oder aber auf '
   + 'in an zu von mit bei nach für so als wie am im zum zur ist sind war wird '
   + 'auch nur noch nicht wo wenn dass vor über unter durch ohne um bis').split(' '));
export const GERMAN_AMBIGUOUS_TOKENS = new Set(['so', 'ergänzung']);

// Guards: no German letter directly before/after (explicit classes — \b mishandles
// umlauts and would diverge from the Python port).
const GM_L = '(?<![A-Za-zäöüßÄÖÜ])';
const GM_R = '(?![A-Za-zäöüßÄÖÜ])';
const GM_PHRASE_RES = GERMAN_FORMULA_PHRASES.map((p) => new RegExp(GM_L + p + GM_R, 'gi'));

// '.' is literal; a single space matches a plain-whitespace run ([ \t\n\r]+, NOT \s+,
// because Python and JS disagree on the \s class edges).  Backslashes are escaped
// first so a literal '\' in a token can never act as a regex metachar (CodeQL
// incomplete-string-escaping; inputs today are compile-time constants - hardened
// so a future dynamic token cannot turn the class into an injection surface).
function gmTokenPattern(tok) {
  return tok.replace(/\\/g, '\\\\').replace(/\./g, '\\.').replace(/ /g, '[ \t\n\r]+');
}

// Module-scope Set construction avoids iterable spread (`[...set]`): bundler
// loose-mode transforms compile it to `[].concat(set, …)` which does NOT
// flatten Sets — a consumer (csl-guides, H3488) crashed at module eval with
// `TypeError: a.replace is not a function` when the Set objects reached
// gmTokenPattern. Array.from is spread-free and transform-safe.
const gmSortTokens = (set) =>
  Array.from(set).sort((a, b) => (b.length - a.length) || (a < b ? -1 : a > b ? 1 : 0));
const GM_DOTTED_RE = new RegExp(
  GM_L + '(?:' +
  gmSortTokens(new Set(Array.from(GERMAN_GRAMMAR_AB).concat(Array.from(GERMAN_FORMULA_AB))))
    .map(gmTokenPattern).join('|') + ')' + GM_R,
  'gi');
const GM_BARE_RE = new RegExp(
  GM_L + '(?:' + gmSortTokens(GERMAN_GRAMMAR_BARE).join('|') + ')' + GM_R,
  'g');   // case-SENSITIVE: NWS-layer labels, exact form
const GM_WORD_RE = /[A-Za-zäöüßÄÖÜ]+/g;
const gmEnsureDot = (t) => (t.endsWith('.') ? t : t + '.');
const GM_FORMULA_NORM = new Set(Array.from(GERMAN_FORMULA_AB).map(gmEnsureDot));

// Detect German lexicographic-apparatus spans; returns [{start, end, text, category}]
// sorted by position. Categories: 'grammar_label' | 'recurring_formula' |
// 'function_word' (whole text is bare function words) | 'uncertain' (whole text is
// an ambiguous token — consumer treats as not-gloss and logs). Mid-text function
// words ("Name eines Baumes") are NOT flagged; ordinary gloss prose returns [].
// Offsets are code-unit-identical to the Python port for BMP text.
export function classify_german_metalanguage(text) {
  const s = text || '';
  const spans = [];
  const keep = (start, end, txt, category) => {
    for (const sp of spans) if (start < sp.end && sp.start < end) return;
    spans.push({ start, end, text: txt, category });
  };
  for (const rx of GM_PHRASE_RES) {
    rx.lastIndex = 0;
    for (const m of s.matchAll(rx)) keep(m.index, m.index + m[0].length, m[0], 'recurring_formula');
  }
  GM_DOTTED_RE.lastIndex = 0;
  for (const m of s.matchAll(GM_DOTTED_RE)) {
    const tok = gmEnsureDot(m[0].replace(/[ \t\n\r]+/g, ' ').toLowerCase());
    const cat = GM_FORMULA_NORM.has(tok) ? 'recurring_formula' : 'grammar_label';
    keep(m.index, m.index + m[0].length, m[0], cat);
  }
  GM_BARE_RE.lastIndex = 0;
  for (const m of s.matchAll(GM_BARE_RE)) keep(m.index, m.index + m[0].length, m[0], 'grammar_label');
  if (spans.length) {
    spans.sort((a, b) => (a.start - b.start) || (a.end - b.end));
    return spans;
  }

  // nothing matched: is the WHOLE text an apparatus placeholder / ambiguous token?
  GM_WORD_RE.lastIndex = 0;
  const words = (s.match(GM_WORD_RE) || []).map((w) => w.toLowerCase());
  if (words.length
      && words.every((w) => GERMAN_FUNCTION_WORDS.has(w) || GERMAN_AMBIGUOUS_TOKENS.has(w))) {
    GM_WORD_RE.lastIndex = 0;
    const first = GM_WORD_RE.exec(s);
    const start = first.index;
    let end = s.length;
    while (end > start && ' \t\n\r'.includes(s[end - 1])) end -= 1;
    const cat = words.every((w) => GERMAN_AMBIGUOUS_TOKENS.has(w)) ? 'uncertain' : 'function_word';
    return [{ start, end, text: s.slice(start, end), category: cat }];
  }
  return [];
}

// ---- linkid: TYPED_LINK_ID_GRAMMAR.md builders/parsers/validators ----------
// Cross-repo Type-D (grammar <-> non-grammar) link-ID grammar, per the concordance
// roadmap's @DECIDE D2 spec: Uprava/TYPED_LINK_ID_GRAMMAR.md. Every anchor id and
// target-locus id is '<prefix>:<tail>' where the tail is copied VERBATIM from that
// source's own stable id (spec section 0 "reuse, don't mint" — never a fresh
// synthetic key, never a URL host). The prefixes/patterns/tiers below are locked
// verbatim against the spec's canonical validator, kosha/scripts/typed_link_lint.py
// (ANCHOR_PATTERNS / TARGET_PATTERNS / ANCHOR_TYPE_TO_PREFIX) and
// kosha/scripts/concordance_core.py (TYPE_D_LINK_TYPES / TIER_CONFIDENCE) — behaviour-
// identical port of the linkid_* section in py/sanskrit_util/__init__.py (proved by
// ../vectors/vectors.json). JS `\w` is already ASCII-only (unlike Python's
// Unicode-aware default), so no extra flag is needed here — see the Python port's
// note on this cross-language parity trap.
export const LINKID_ANCHOR_PREFIXES = ['gra', 'whitney-root', 'whitney-sec', 'root', 'sutra'];
export const LINKID_TARGET_PREFIXES = ['dcs', 'vedaweb', 'commentary', 'subject'];
export const LINKID_LINK_TYPES = ['translation-witness', 'commentary-citation', 'thematic'];
export const LINKID_MATCH_METHODS = ['id-link', 'xref', 'curated', 'exact', 'floor', 'relaxed', 'fuzzy'];

const LINKID_ANCHOR_RE = {
  'gra': /^\d+(\.\d+)?$/,
  'whitney-root': /^\d+$/,
  'whitney-sec': /^\d+(-\d+)?$/,
  'root': /^[A-Za-z]+$/,
  'sutra': /^\d+\.\d+\.\d+$/,
};
const LINKID_TARGET_RE = {
  'dcs': /^.+$/,
  'vedaweb': /^\d+(\.\d+)*:[0-9a-fA-F]{24}$/,
  'commentary': /^[\w-]+:.+$/,
  'subject': /^[\w-]+:[\w.-]+$/,
};
const LINKID_ANCHOR_TYPE_TO_PREFIX = {
  'id-gra': 'gra',
  'whitney-root': 'whitney-root',
  'whitney-sec': 'whitney-sec',
  'root': 'root',
  'panini-sutra': 'sutra',
};
const LINKID_DATE_RE = /^\d{2}-\d{2}-\d{4}$/;
const LINKID_MATCH_METHOD_SET = new Set(LINKID_MATCH_METHODS);

export function linkid_build_anchor_id(spec) {
  if (spec === null || typeof spec !== 'object') return null;
  const t = spec.type;
  const tail = spec.tail;
  const rx = LINKID_ANCHOR_RE[t];
  if (!rx || typeof tail !== 'string' || !rx.test(tail)) return null;
  return `${t}:${tail}`;
}

export function linkid_parse_anchor_id(anchorId) {
  if (typeof anchorId !== 'string' || !anchorId.includes(':')) return null;
  const i = anchorId.indexOf(':');
  const prefix = anchorId.slice(0, i);
  const tail = anchorId.slice(i + 1);
  const rx = LINKID_ANCHOR_RE[prefix];
  if (!rx) return null;
  return { type: prefix, tail, valid: rx.test(tail) };
}

export function linkid_build_target_locus(spec) {
  if (spec === null || typeof spec !== 'object') return null;
  const t = spec.type;
  const tail = spec.tail;
  const rx = LINKID_TARGET_RE[t];
  if (!rx || typeof tail !== 'string' || !rx.test(tail)) return null;
  return `${t}:${tail}`;
}

export function linkid_parse_target_locus(targetLocus) {
  if (typeof targetLocus !== 'string' || !targetLocus.includes(':')) return null;
  const i = targetLocus.indexOf(':');
  const prefix = targetLocus.slice(0, i);
  const tail = targetLocus.slice(i + 1);
  const rx = LINKID_TARGET_RE[prefix];
  if (!rx) return null;
  return { type: prefix, tail, valid: rx.test(tail) };
}

export function linkid_validate_link_record(record) {
  const errors = [];
  if (record === null || typeof record !== 'object') {
    return { valid: false, errors: ['record is not an object'] };
  }

  const anchorType = record.anchor_type || '';
  const anchorId = record.anchor_id || '';
  const expectedPrefix = LINKID_ANCHOR_TYPE_TO_PREFIX[anchorType];
  if (!expectedPrefix) {
    errors.push(`unknown anchor_type '${anchorType}'`);
  } else {
    const parsed = linkid_parse_anchor_id(anchorId);
    if (parsed === null) {
      errors.push(`anchor_id '${anchorId}' has no known prefix (expected '${expectedPrefix}:...')`);
    } else if (parsed.type !== expectedPrefix) {
      errors.push(`anchor_id '${anchorId}' prefix '${parsed.type}' does not match anchor_type '${anchorType}' (expected '${expectedPrefix}:...')`);
    } else if (!parsed.valid) {
      errors.push(`anchor_id '${anchorId}': tail '${parsed.tail}' fails '${parsed.type}' syntax`);
    }
  }

  const targetLocus = record.target_locus || '';
  const parsedT = linkid_parse_target_locus(targetLocus);
  if (parsedT === null) {
    errors.push(`target_locus '${targetLocus}' has no known prefix`);
  } else if (!parsedT.valid) {
    errors.push(`target_locus '${targetLocus}': tail '${parsedT.tail}' fails '${parsedT.type}' syntax`);
  }
  if (typeof targetLocus === 'string'
      && (targetLocus.startsWith('http://') || targetLocus.startsWith('https://') || targetLocus.startsWith('www.'))) {
    errors.push(`target_locus '${targetLocus}' looks like a URL host — reuse the source's own stable id (spec section 0)`);
  }

  const linkType = record.link_type || '';
  if (!LINKID_LINK_TYPES.includes(linkType)) {
    errors.push(`link_type '${linkType}' not in [${LINKID_LINK_TYPES.join(', ')}]`);
  }

  const matchMethod = record.match_method || '';
  if (!LINKID_MATCH_METHOD_SET.has(matchMethod)) {
    errors.push(`match_method '${matchMethod}' not in [${LINKID_MATCH_METHODS.join(', ')}]`);
  }

  const date = record.date || '';
  if (!date) {
    errors.push('date is missing');
  } else if (!LINKID_DATE_RE.test(String(date))) {
    errors.push(`date '${date}' is not DD-MM-YYYY`);
  }

  return { valid: errors.length === 0, errors };
}

export default {
  to_slp1, from_slp1, to_roman, deva_to_iast, deva_to_slp1, iast_to_devanagari,
  norm, nfold, form_key, normalize_sanskrit,
  SLP1_VOWELS, SLP1_MARKS, SLP1_CONSONANTS, SLP1_ALPHABET,
  strip_slp1_accents, slp1_norm, slp1_form_key, slp1_to_devanagari, slp1_simplify,
  source_line_to_iast, source_text_to_iast,
  classify_german_metalanguage,
  GERMAN_GRAMMAR_AB, GERMAN_GRAMMAR_BARE, GERMAN_FORMULA_AB, GERMAN_FORMULA_PHRASES,
  GERMAN_FUNCTION_WORDS, GERMAN_AMBIGUOUS_TOKENS,
  LINKID_ANCHOR_PREFIXES, LINKID_TARGET_PREFIXES, LINKID_LINK_TYPES, LINKID_MATCH_METHODS,
  linkid_build_anchor_id, linkid_parse_anchor_id,
  linkid_build_target_locus, linkid_parse_target_locus, linkid_validate_link_record,
};
