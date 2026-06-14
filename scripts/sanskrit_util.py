# -*- coding: utf-8 -*-
"""Shared Sanskrit helpers for the crosswalk pipeline.

Single source of truth for the spine/crosswalk scripts:
  - to_slp1    : IAST → SLP1 (consolidated from emit_crosswalk.py)
  - to_roman   : Arabic gaṇa → Roman (consolidated from extract_dict_roots.py)
  - norm/nfold : lookup-key normalisers, mirrored in reader/reader.js

Note: scripts/dcs/ keep their OWN Roman↔Arabic + fold helpers (a separate corpus-class
pipeline, intentionally not consolidated here). norm()/nfold() must stay in sync with
reader/reader.js norm()/nfold() (for IAST input) or reader token lookups silently miss.
"""
import re
import unicodedata

# ---- IAST → SLP1 (longest-key-first; aspirates + diphthongs are digraphs) ----
_SLP1 = {
    'ai': 'E', 'au': 'O', 'kh': 'K', 'gh': 'G', 'ch': 'C', 'jh': 'J', 'ṭh': 'W', 'ḍh': 'Q',
    'th': 'T', 'dh': 'D', 'ph': 'P', 'bh': 'B',
    'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṛ': 'f', 'ṝ': 'F', 'ḷ': 'x', 'ḹ': 'X',
    'ṃ': 'M', 'ṁ': 'M', 'ḥ': 'H', 'ṅ': 'N', 'ñ': 'Y', 'ṭ': 'w', 'ḍ': 'q', 'ṇ': 'R',
    'ś': 'S', 'ṣ': 'z', 'ḻ': 'L',
    'a': 'a', 'i': 'i', 'u': 'u', 'e': 'e', 'o': 'o', 'k': 'k', 'g': 'g', 'c': 'c', 'j': 'j',
    't': 't', 'd': 'd', 'n': 'n', 'p': 'p', 'b': 'b', 'm': 'm', 'y': 'y', 'r': 'r', 'l': 'l',
    'v': 'v', 's': 's', 'h': 'h',
}

def to_slp1(iast):
    out, i, s = [], 0, (iast or '')
    while i < len(s):
        two = s[i:i + 2]
        if two in _SLP1:
            out.append(_SLP1[two]); i += 2; continue
        out.append(_SLP1.get(s[i], s[i])); i += 1
    return ''.join(out)

_ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X'}

def to_roman(nums):
    return [_ROMAN[n] for n in nums if n in _ROMAN]

# ---- SLP1 → IAST (inverse of _SLP1; SLP1 is one ASCII char per phoneme) ----
_FROM_SLP1 = {
    'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ',
    'E': 'ai', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ',
    'K': 'kh', 'G': 'gh', 'N': 'ṅ', 'C': 'ch', 'J': 'jh', 'Y': 'ñ',
    'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ',
    'T': 'th', 'D': 'dh', 'P': 'ph', 'B': 'bh',
    'S': 'ś', 'z': 'ṣ', 'L': 'ḻ',
}

def from_slp1(slp1):
    """SLP1 → IAST. Used to render vidyut-prakriya output (SLP1) for the reader."""
    return ''.join(_FROM_SLP1.get(ch, ch) for ch in (slp1 or ''))

# ---- length-preserving comparison key for verb forms / PPP stems (vidyut↔warnemyr↔DCS) ----
# Unlike norm()/nfold() (which collapse vowel length for the reader's diacritic-insensitive search),
# form_key() PRESERVES length (ā≠a): it is used to compare *generated* forms against *recorded* forms,
# where kranta vs krānta is a real difference. It folds anusvāra + homorganic nasals → n (krāṃta ==
# krānta), strips the nom-sg visarga, and drops PITCH accents that sit on a vowel — but keeps the
# letter ś (= s + U+0301, same codepoint as the acute accent) and the retroflex/vocalic dots.
_FK_ACCENT = {'́', '̀', '॑', '॒'}     # acute, grave, Vedic svarita/anudātta
_FK_VOWELS = set('aāiīuūṛṝḷḹeēoō')

def form_key(s):
    s = (s or '').strip().lower()
    if s in ('-', '–', '—'):                    # warnemyr 'no recorded form' placeholder → blank
        return ''
    s = re.sub('ḥ$', '', s)                     # nom-sg visarga
    s = re.sub('[ṃṁṅñṇ]', 'n', s)              # anusvāra + ṅ/ñ/ṇ → n (precomposed, before NFD)
    out = []
    for ch in unicodedata.normalize('NFD', s):
        if ch in _FK_ACCENT:
            j = len(out) - 1                    # walk back past ALL combining marks to the base letter
            while j >= 0 and unicodedata.combining(out[j]):
                j -= 1
            base = unicodedata.normalize('NFC', ''.join(out[j:])) if j >= 0 else ''
            if base in _FK_VOWELS:              # accent on a (long/vocalic) vowel → drop; on s (→ś) → keep
                continue
        out.append(ch)
    return unicodedata.normalize('NFC', ''.join(out))

def norm(s):
    """EXACT lookup key: NFD, drop all combining marks, NFC, lower. Mirror of reader.js norm()
    for IAST input (reader.js additionally transliterates Devanagari first via deva2iast)."""
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return unicodedata.normalize('NFC', s).lower().strip()

def nfold(s):
    """NASAL-FOLDED recall key: norm() then fold every nasal (m/n/ṅ/ñ/ṇ/anusvāra) to 'n'. Used
    only as a FALLBACK index, so an anusvāra spelling (saṃ-, kāṃkṣ-) matches the corpus's
    homorganic spelling (kāṅkṣ-) WITHOUT merging genuinely distinct roots (am/an) on the exact
    key. Mirror of reader/reader.js nfold()."""
    return re.sub('[mn]', 'n', norm(s))
