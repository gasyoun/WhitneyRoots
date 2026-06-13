# -*- coding: utf-8 -*-
"""Shared Sanskrit helpers for the crosswalk pipeline (single source of truth).

Retires the copies of these functions that had drifted across the scripts:
  - to_slp1   : IAST → SLP1 (was duplicated in emit_crosswalk.py)
  - to_roman  : Arabic gaṇa → Roman (was duplicated in extract_dict_roots.py + dcs/)
  - norm      : lookup-key normaliser (was duplicated in build_reader_data.py + reader.js)

norm() MUST stay byte-identical to reader/reader.js norm() or reader token lookups silently miss.
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

def norm(s):
    """Lookup key: (caller transliterates Devanagari first,) NFD, drop ALL combining marks,
    NFC, lower, then fold every nasal (m/n/ṅ/ñ/ṇ/anusvāra) to 'n'. The nasal fold lets an
    anusvāra spelling (saṃ-, kāṃkṣ-) match the corpus's homorganic-nasal spelling (kāṅkṣ-).
    Mirror of reader/reader.js norm()."""
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = unicodedata.normalize('NFC', s).lower().strip()
    return re.sub('[mn]', 'n', s)
