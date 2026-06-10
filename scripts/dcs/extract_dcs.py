#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_dcs.py — Link & verify Whitney Roots against the DCS corpus.

Reads WhitneyRoots/src/app_data.json and the DCS CoNLL-U SQLite
(dcs_full.sqlite, in the sibling VisualDCS repo), then writes:

  * src/dcs_freq.json        — frequency / morphology sidecar, keyed by Whitney id
  * Whitney_DCS_audit.json   — machine-readable per-root verdicts
  * Whitney_DCS_audit.md     — human summary + top discrepancies

The join key is the root = DCS lemma (IAST). Frequencies come ONLY from the
token table (upos='VERB'); Gaṇa class is read from the lemma.grammar field
(asserted) AND inferred from corpus present-stem forms (heuristic). Nothing in
app_data.json or the runtime app is modified.

Usage:
  python scripts/dcs/extract_dcs.py [--db PATH] [--app-data PATH]
                                    [--out-freq PATH] [--out-audit-md PATH]
                                    [--out-audit-json PATH]

Note (Windows): absent token features are SQL NULL (not the string 'None').
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_DB = os.path.abspath(
    os.path.join(REPO, "..", "VisualDCS", "src", "DCS-data-2026", "dcs_full.sqlite")
)
DEFAULT_APP_DATA = os.path.join(REPO, "src", "app_data.json")
DEFAULT_OUT_FREQ = os.path.join(REPO, "src", "dcs_freq.json")
DEFAULT_OUT_AUDIT_JSON = os.path.join(REPO, "Whitney_DCS_audit.json")
DEFAULT_OUT_AUDIT_MD = os.path.join(REPO, "Whitney_DCS_audit.md")
DEFAULT_OUT_PINDEX = os.path.join(REPO, "src", "participle_index.json")
DEFAULT_OUT_PINDEX_DCS = os.path.join(REPO, "src", "participle_index_dcs.json")
DEFAULT_OUT_WORKLIST_MD = os.path.join(REPO, "Whitney_DCS_worklist.md")
DEFAULT_OUT_WORKLIST_CSV = os.path.join(REPO, "Whitney_DCS_worklist.csv")

DCS_SNAPSHOT = "2026 CoNLL-U"

# --------------------------------------------------------------------------
# Step 1 — Normalizer (auto-only). Deliberately conservative: it must NOT fold
# vowel length or retroflex/sibilant distinctions (that would collapse distinct
# roots). Mirrors the JS dcsKey() to be added later when wiring the UI.
# --------------------------------------------------------------------------
_HOMONYM_PREFIX = re.compile(r"^\d+\s+")


def strip_prefix(root: str) -> str:
    """Remove Whitney's leading homonym number (e.g. '1 akṣ' -> 'akṣ')."""
    return _HOMONYM_PREFIX.sub("", (root or "").strip()).strip()


_FOLD_MAP = {
    "ā": "a", "ī": "i", "ū": "u", "ṛ": "r", "ṝ": "r", "ḷ": "l", "ḹ": "l",
    "ṅ": "n", "ñ": "n", "ṭ": "t", "ḍ": "d", "ṇ": "n", "ś": "s", "ṣ": "s",
    "ḥ": "h", "ṃ": "m", "ṁ": "m",
}


def fold(s: str) -> str:
    """Strip diacritics to ASCII-ish form. Whitney's `ppp` field is stored this
    way (bhūta -> 'bhuta'); DCS m_unsandhied is full IAST. Used ONLY for the
    within-root PPP confirmation test, never for the cross-root join key."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return "".join(_FOLD_MAP.get(c, c) for c in s).lower()


def dcs_key(root: str) -> str:
    """Conservative join key: prefix-strip, NFC, unify anusvāra, drop avagraha."""
    s = strip_prefix(root)
    s = unicodedata.normalize("NFC", s)
    s = s.replace("ṁ", "ṃ")          # unify the two anusvāra code points
    s = s.replace("'", "").replace("’", "").replace("ʼ", "")  # avagraha
    return s.strip()


# Curated aliases: Whitney citation/sandhi spelling -> DCS lemma. Hand-verified
# against dcs_full.sqlite (each target is an attested verbal lemma). Covers what
# auto-normalization cannot bridge: present-stem citations (gach=gam, yach=yam,
# prach=pracch, ich=iṣ), guṇa/vṛddhi citations (har=hṛ, vāh=vah), vowel-length
# and retroflex/dental variants (path=paṭh, pis=piṣ, khad=khād, iḍ=īḍ, div=dīv,
# dū=du, rī=ri, turv=tūrv, kṣvid=kṣviḍ), and vyā=vye. Wrong proximity matches
# were rejected (e.g. hū≠hu 'sacrifice', nṛ≠nṛt 'dance').
ALIASES = {
    "gach": "gam", "yach": "yam", "prach": "pracch", "ich": "iṣ",
    "har": "hṛ", "vāh": "vah",
    "path": "paṭh", "khad": "khād", "iḍ": "īḍ",
    "div": "dīv", "dū": "du", "rī": "ri", "turv": "tūrv",
    "kṣvid": "kṣviḍ", "vyā": "vye",
    # NB: pis ("stretch/extend") is NOT piṣ ("grind", class 7) — distinct roots;
    # that alias was removed after it produced a spurious class conflict.
}


# --------------------------------------------------------------------------
# Gaṇa class from lemma.grammar  (e.g. "1.P.,4.P.,4.Ā." / "8.P.,5.Ā." / "Desid. P.")
# --------------------------------------------------------------------------
_ROMAN_TO_ARABIC = {
    "I": "1", "II": "2", "III": "3", "IV": "4", "V": "5",
    "VI": "6", "VII": "7", "VIII": "8", "IX": "9", "X": "10",
}


def to_arabic(cls: str) -> str:
    """Whitney classes are Roman numerals; DCS grammar is Arabic. Normalize."""
    c = (cls or "").strip().upper()
    return _ROMAN_TO_ARABIC.get(c, c)


_CLASS_PART = re.compile(r"(\d{1,2})\s*\.\s*[PĀ]")
_VERBAL_GRAMMAR = re.compile(r"(\d{1,2}\s*\.\s*[PĀ])|Desid\.|Denom\.|Int\.")
_DERIVED = re.compile(r"Desid\.|Denom\.|Int\.")


def is_verbal_grammar(grammar: str) -> bool:
    return bool(grammar) and bool(_VERBAL_GRAMMAR.search(grammar))


def parse_classes(grammars):
    """Return (sorted class list, derived-type list, raw joined) from grammar strings."""
    classes, derived, raws = set(), set(), []
    for g in grammars:
        if not g:
            continue
        raws.append(g.strip())
        for m in _CLASS_PART.finditer(g):
            classes.add(m.group(1))
        for m in _DERIVED.finditer(g):
            derived.add(m.group(0).rstrip("."))
    cl = sorted(classes, key=lambda x: int(x))
    return cl, sorted(derived), "; ".join(sorted(set(raws)))


# --------------------------------------------------------------------------
# PPP stemming (for aggregation only; Whitney-confirmation uses a prefix test,
# so verdicts never depend on this approximate stemmer).
# --------------------------------------------------------------------------
_A_ENDINGS = sorted(
    ["asya", "ānām", "ābhiḥ", "ābhyaḥ", "āyāḥ", "āyām", "eṣu", "ayoḥ", "ais",
     "aiḥ", "āni", "ena", "āya", "āt", "ām", "āḥ", "ān", "au", "aḥ", "am",
     "ā", "e", "o", "ḥ", "m"],
    key=len, reverse=True,
)
_VOWELS = "aāiīuūṛṝḷeoaiau"


def ppp_stem(form: str) -> str:
    if not form:
        return form
    for e in _A_ENDINGS:
        if form.endswith(e) and len(form) > len(e) + 1:
            base = form[: -len(e)]
            if base and base[-1] not in _VOWELS:
                base += "a"
            return base
    return form


# --------------------------------------------------------------------------
# Present-stem class signal (Step 3) — coarse, documented heuristic.
# Classifies finite present-active forms by ending of the unsandhied form.
# --------------------------------------------------------------------------
def present_class_bucket(form: str) -> str:
    """Classify a present form by its visible class marker. ONLY 3rd-person
    forms (-ti/-te/-nti/-nte) are diagnostic — the stem marker (-ya-, -aya-,
    -no-, -nā-, …) sits right before the ending. 1st/2nd-person forms (manye,
    manyase, manyāmi) carry no visible marker, so they are skipped ('?');
    classifying them by their personal ending was what mislabeled class-IV
    roots (man, kṛś) as I/VI."""
    f = form
    if not f.endswith(("ti", "te", "nti", "nte")):
        return "?"
    if f.endswith(("ayati", "ayate", "ayanti", "ayante")):
        return "X/caus-denom"
    if f.endswith(("nāti", "nīte", "nanti", "nānti", "nāte")):
        return "IX"
    if f.endswith(("noti", "nute", "nvanti", "nvate", "nuvanti")):
        return "V"
    if f.endswith(("oti", "ute", "vate")):
        return "VIII"
    if f.endswith(("yati", "yate", "yanti", "yante")):
        return "IV"
    if f.endswith(("ayati", "ayate")):
        return "X/caus-denom"
    if f.endswith(("ati", "ate", "anti", "ante")):
        return "I/VI"  # thematic; guṇa (I) vs no-guṇa (VI) not separable cheaply
    # remaining -ti/-te/-nti/-nte with no thematic vowel = athematic
    # (root / reduplicating / nasal-infix): classes 2/3/7
    return "II/III (athematic)"


# --------------------------------------------------------------------------
def load_lexicon(path):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("lexicon", [])


def build_lemma_indexes(conn):
    """Return:
       grammar_by_lemma: lemma_str -> set(grammar strings)
       verbal_lemmas:    set(lemma_str having >=1 verbal grammar)
       preverb_forms:    list of (lemma_str, preverb) for prefixed verbal lemmas
    """
    grammar_by_lemma = defaultdict(set)
    preverb_forms = []
    for lemma, grammar, preverbs in conn.execute(
        "SELECT lemma, grammar, preverbs FROM lemma"
    ):
        if grammar:
            grammar_by_lemma[lemma].add(grammar)
        if preverbs and is_verbal_grammar(grammar or ""):
            preverb_forms.append((lemma, preverbs))
    verbal_lemmas = {
        lem for lem, gs in grammar_by_lemma.items() if any(is_verbal_grammar(g) for g in gs)
    }
    return grammar_by_lemma, verbal_lemmas, preverb_forms


def verb_totals(conn):
    """lemma_str -> total VERB token count (for rank)."""
    totals = {}
    for lemma, n in conn.execute(
        "SELECT lemma, COUNT(*) FROM token WHERE upos='VERB' GROUP BY lemma"
    ):
        totals[lemma] = n
    return totals


def stream_detail(conn, wanted):
    """Single scan over VERB tokens; accumulate detail only for `wanted` lemmas."""
    det = {
        k: {
            "forms": Counter(),
            "verbforms": Counter(),
            "tenses": Counter(),
            "voices": Counter(),
            "present_signal": Counter(),
        }
        for k in wanted
    }
    q = (
        "SELECT lemma, form, m_unsandhied, feat_verbform, feat_tense, feat_voice "
        "FROM token WHERE upos='VERB'"
    )
    for lemma, form, muns, vf, tense, voice in conn.execute(q):
        if lemma not in det:
            continue
        d = det[lemma]
        surf = form or muns or ""
        d["forms"][surf] += 1
        d["verbforms"][vf or "Finite"] += 1
        d["tenses"][tense or "—"] += 1
        d["voices"][voice or "Active"] += 1
        stem = muns or form or ""
        # present-stem signal: finite (vf NULL), Pres, active (voice NULL)
        if vf is None and tense == "Pres" and voice is None:
            d["present_signal"][present_class_bucket(stem)] += 1
    return det


def derive_ppp_stems(ppp_forms: Counter, top=12):
    agg = Counter()
    for form, n in ppp_forms.items():
        agg[ppp_stem(form)] += n
    return [{"stem": s, "n": n} for s, n in agg.most_common(top)]


def present_signal(sig: Counter):
    if not sig:
        return {"dominant": None, "evidence": []}
    ev = [{"bucket": b, "n": n} for b, n in sig.most_common()]
    dom = next((e["bucket"] for e in ev if e["bucket"] != "?"), ev[0]["bucket"])
    return {"dominant": dom, "evidence": ev}


# --------------------------------------------------------------------------
# Participle system — the classical 9, as far as DCS tagging + endings allow.
# DCS natively tags ~6 buckets (verbform Part/Gdv × tense × voice); the
# active/middle split and the perfect participle are inferred from the form
# ending (heuristic). Absolutive (Conv) and infinitive (Inf) are NOT
# participles and are excluded.
# --------------------------------------------------------------------------
PARTICIPLE_ORDER = [
    "present-active", "present-middle", "present-passive",
    "past-passive", "past-active", "perfect-active",
    "future-active", "future-middle", "gerundive",
]
PARTICIPLE_LABELS = {
    "present-active": "Present active (-at/-ant)",
    "present-middle": "Present middle (-māna/-āna)",
    "present-passive": "Present passive (-yamāna)",
    "past-passive": "Past passive — PPP (-ta/-na)",
    "past-active": "Past active (-tavant)",
    "perfect-active": "Perfect active (-vas/-vāṃs)",
    "future-active": "Future active (-syant)",
    "future-middle": "Future middle (-syamāna)",
    "gerundive": "Gerundive / FPP (-tavya/-anīya/-ya)",
}
_MIDDLE_END = ("māna", "māne", "mānaḥ", "mānam", "mānā", "mānau", "mānāḥ", "mānāt",
               "āna", "āṇa", "ānaḥ", "āṇaḥ", "ānam", "āṇam", "ānā", "āṇā", "ānāḥ", "āṇāḥ")
_PERFECT_END = ("vāṃs", "vāṃsam", "vān", "vānam", "vuṣaḥ", "vuṣā", "ivān", "ivāṃs",
                "uṣīm", "uṣī", "uṣaḥ")
_TAVANT = re.compile(r"tav(ant|ān|at|atī|antam|atā)?$")


def _is_middle(f: str) -> bool:
    return f.endswith(_MIDDLE_END)


def participle_category(vf, tense, voice, form):
    """Return one of PARTICIPLE_ORDER, or None if not a participle."""
    f = form or ""
    if vf == "Gdv":
        return "gerundive"
    if vf != "Part":
        return None
    # -tavant past active participle (kṛtavān) — check before perfect (-vān clash)
    if _TAVANT.search(f) or "tavant" in f:
        return "past-active"
    # perfect active participle (cakṛvān, vidvāṃs) — -vas/-vāṃs without 'tav'
    if f.endswith(_PERFECT_END):
        return "perfect-active"
    if voice == "Pass":
        return "present-passive"
    if tense == "Pres":
        return "present-middle" if _is_middle(f) else "present-active"
    if tense == "Fut":
        return "future-middle" if _is_middle(f) else "future-active"
    # tense Past/None, non-tavant → PPP
    return "past-passive"


def scan_participles(conn, linked):
    """One scan over participle/gerundive tokens across ALL verbal lemmas.

    linked: lemma_str -> list of (whitney_id, root) for linked entries.
    Returns:
      part_by_lemma: lemma -> category -> Counter(surface form)
      whitney_index: surface form -> list[{id, root, category}]  (linked roots)
      dcs_index:     surface form -> list[{lemma, category}]      (all roots)
    """
    part_by_lemma = defaultdict(lambda: defaultdict(Counter))
    dcs_pairs = defaultdict(set)  # form -> set((lemma, category))
    q = (
        "SELECT lemma, form, m_unsandhied, feat_verbform, feat_tense, feat_voice "
        "FROM token WHERE upos='VERB' AND feat_verbform IN ('Part','Gdv')"
    )
    for lemma, form, muns, vf, tense, voice in conn.execute(q):
        cat = participle_category(vf, tense, voice, muns or form or "")
        if not cat:
            continue
        surf = form or muns or ""
        if not surf:
            continue
        part_by_lemma[lemma][cat][surf] += 1
        dcs_pairs[surf].add((lemma, cat))

    whitney_index = {}
    dcs_index = {}
    for surf, pairs in dcs_pairs.items():
        dcs_index[surf] = sorted(
            ({"lemma": lem, "category": cat} for lem, cat in pairs),
            key=lambda x: (x["lemma"], x["category"]),
        )
        wlist = [
            {"id": wid, "root": root, "category": cat}
            for lem, cat in pairs
            for (wid, root) in linked.get(lem, [])
        ]
        if wlist:
            whitney_index[surf] = sorted(wlist, key=lambda x: (x["root"], x["category"]))
    return part_by_lemma, whitney_index, dcs_index


def build_participles_field(parts):
    """parts: category -> Counter(form). Returns ordered dict for the sidecar."""
    out = {}
    for cat in PARTICIPLE_ORDER:
        c = parts.get(cat)
        if c:
            out[cat] = {
                "label": PARTICIPLE_LABELS[cat],
                "total": sum(c.values()),
                "top": [{"form": f, "n": n} for f, n in c.most_common(8)],
            }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--app-data", default=DEFAULT_APP_DATA)
    ap.add_argument("--out-freq", default=DEFAULT_OUT_FREQ)
    ap.add_argument("--out-audit-json", default=DEFAULT_OUT_AUDIT_JSON)
    ap.add_argument("--out-audit-md", default=DEFAULT_OUT_AUDIT_MD)
    ap.add_argument("--out-pindex", default=DEFAULT_OUT_PINDEX)
    ap.add_argument("--out-pindex-dcs", default=DEFAULT_OUT_PINDEX_DCS)
    ap.add_argument("--out-worklist-md", default=DEFAULT_OUT_WORKLIST_MD)
    ap.add_argument("--out-worklist-csv", default=DEFAULT_OUT_WORKLIST_CSV)
    args = ap.parse_args()

    if not os.path.exists(args.db):
        sys.exit(f"DB not found: {args.db}")
    print(f"DB:        {args.db}")
    print(f"app_data:  {args.app_data}")

    lexicon = load_lexicon(args.app_data)
    print(f"Whitney entries: {len(lexicon)}")

    conn = sqlite3.connect(args.db)
    print("Indexing lemma table ...")
    grammar_by_lemma, verbal_lemmas, preverb_forms = build_lemma_indexes(conn)
    print(f"  verbal lemmas: {len(verbal_lemmas)}")
    print("Computing verb-token totals (rank) ...")
    totals = verb_totals(conn)
    # corpus-wide rank among lemmas that actually appear as verbs
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    rank_of = {lem: i + 1 for i, (lem, _) in enumerate(ranked)}

    # preverb forms grouped by base root (heuristic: prefixed lemma endswith root)
    preverbs_by_root = defaultdict(list)
    for lem, pv in preverb_forms:
        preverbs_by_root[lem] = pv  # lem -> its own preverb string

    # ---- resolve each Whitney entry to a DCS lemma key ----
    resolved = []  # (entry, key, status)
    dcs_lemma_users = Counter()
    for e in lexicon:
        raw = strip_prefix(e["root"])
        key = dcs_key(e["root"])
        in_db_raw = raw in verbal_lemmas or raw in totals
        in_db_norm = key in verbal_lemmas or key in totals
        alias = ALIASES.get(raw) or ALIASES.get(key)
        if in_db_raw:
            status, used = "matched", raw
        elif in_db_norm:
            status, used = "normalized", key
        elif alias and (alias in verbal_lemmas or alias in totals):
            status, used = "aliased", alias
        else:
            status, used = "unmatched", None
        if used:
            dcs_lemma_users[used] += 1
        resolved.append((e, used, status))

    print("Streaming verb tokens for matched roots ...")
    wanted = {used for (_, used, _) in resolved if used}
    detail = stream_detail(conn, wanted)

    print("Scanning participles (all 9 categories) + building indexes ...")
    linked = defaultdict(list)
    for e, used, _ in resolved:
        if used:
            linked[used].append((str(e["id"]), e["root"]))
    part_by_lemma, whitney_index, dcs_index = scan_participles(conn, linked)
    conn.close()

    # ---- build sidecar + audit ----
    freq_entries = {}
    audit_rows = []
    counts = Counter()

    for e, used, status in resolved:
        eid = str(e["id"])
        w_classes = [to_arabic(str(c)) for c in (e.get("classes") or [])]
        w_ppp = [p for p in (e.get("ppp") or []) if p]

        if used is None:
            counts["unmatched"] += 1
            freq_entries[eid] = {
                "root": e["root"], "dcs_lemma": None, "dcs_status": "unmatched",
                "total": 0, "rank": None, "grammar_class": [], "grammar_derived": [],
                "grammar_raw": "", "verbforms": {}, "tenses": {}, "voices": {},
                "top_forms": [], "ppp": [], "participles": {}, "preverbs": [],
                "present_stem_signal": {},
            }
            audit_rows.append({
                "id": eid, "root": e["root"], "dcs_lemma": None, "status": "unmatched",
                "whitney_classes": w_classes, "dcs_classes": [], "present_signal": None,
                "class_verdict": "no-dcs-match",
                "whitney_ppp": w_ppp, "ppp_results": [], "existence": "no-dcs-match",
            })
            continue

        if dcs_lemma_users[used] > 1:
            status = "homonym_shared"
        counts[status] += 1

        d = detail.get(used, {})
        total = totals.get(used, 0)
        gl, derived, raw = parse_classes(grammar_by_lemma.get(used, []))
        parts = part_by_lemma.get(used, {})
        ppp_counter = parts.get("past-passive", Counter())
        ppp_stems = derive_ppp_stems(ppp_counter)
        participles = build_participles_field(parts)
        sig = present_signal(d.get("present_signal", Counter())) if d else {"dominant": None, "evidence": []}
        top_forms = [{"form": f, "n": n} for f, n in d.get("forms", Counter()).most_common(15)] if d else []
        # Prefixed forms: lemma must end in the root AND its leading part must
        # equal the recorded preverb(s) — rejects look-alikes like ācakṣ/rakṣ
        # for root akṣ (no sandhi-junction handling; precision over recall).
        pv = []
        for lem in verbal_lemmas:
            if lem == used or lem not in preverbs_by_root or not lem.endswith(used):
                continue
            prefix = lem[: -len(used)]
            pvfield = (preverbs_by_root[lem] or "").replace("-", "").replace(" ", "")
            if prefix and prefix == pvfield:
                pv.append({"form": lem, "preverb": preverbs_by_root[lem], "n": totals.get(lem, 0)})
        pv = sorted(pv, key=lambda x: x["n"], reverse=True)[:12]

        freq_entries[eid] = {
            "root": e["root"], "dcs_lemma": used, "dcs_status": status,
            "total": total, "rank": rank_of.get(used),
            "grammar_class": gl, "grammar_derived": derived, "grammar_raw": raw,
            "verbforms": dict(d.get("verbforms", Counter())) if d else {},
            "tenses": dict(d.get("tenses", Counter())) if d else {},
            "voices": dict(d.get("voices", Counter())) if d else {},
            "top_forms": top_forms,
            "ppp": ppp_stems,
            "participles": participles,
            "preverbs": pv,
            "present_stem_signal": sig,
        }

        # ---- verdicts ----
        # class: compare Whitney vs DCS asserted grammar classes
        wset, dset = set(w_classes), set(gl)
        if not gl and total == 0:
            class_verdict = "no-corpus-evidence"
        elif not gl:
            class_verdict = "dcs-has-no-class"
        elif wset == dset:
            class_verdict = "agree"
        elif wset & dset:
            class_verdict = "partial-overlap"
        elif not wset:
            class_verdict = "whitney-missing"
        else:
            class_verdict = "conflict"

        # ppp: prefix test against attested PPP forms (robust)
        # PPP confirmation: fold diacritics on both sides (Whitney ppp is ASCII)
        ppp_folded = [fold(f) for f in ppp_counter.keys()]
        ppp_results = []
        for p in w_ppp:
            pf = fold(p)
            hit = bool(pf) and any(f == pf or f.startswith(pf) for f in ppp_folded)
            ppp_results.append({"stem": p, "verdict": "confirmed" if hit else "unattested"})
        w_ppp_folded = [fold(p) for p in w_ppp]
        dcs_extra = [s["stem"] for s in ppp_stems
                     if not any(fold(s["stem"]).startswith(p) or p.startswith(fold(s["stem"]))
                                for p in w_ppp_folded)]

        existence = "attested" if total > 0 else "lexicon-only"

        audit_rows.append({
            "id": eid, "root": e["root"], "dcs_lemma": used, "status": status,
            "total": total,
            "whitney_classes": w_classes, "dcs_classes": gl, "dcs_derived": derived,
            "present_signal": sig["dominant"], "class_verdict": class_verdict,
            "whitney_ppp": w_ppp, "ppp_results": ppp_results, "dcs_extra_ppp": dcs_extra[:6],
            "existence": existence,
        })

    meta = {
        "source": os.path.basename(args.db), "dcs_snapshot": DCS_SNAPSHOT,
        "generated": str(date.today()), "total": len(lexicon),
        "matched": counts["matched"], "normalized": counts["normalized"],
        "aliased": counts["aliased"], "homonym_shared": counts["homonym_shared"],
        "unmatched": counts["unmatched"],
    }

    with open(args.out_freq, "w", encoding="utf-8") as fh:
        json.dump({"metadata": meta, "entries": freq_entries}, fh, ensure_ascii=False, indent=1)
    with open(args.out_audit_json, "w", encoding="utf-8") as fh:
        json.dump({"metadata": meta, "rows": audit_rows}, fh, ensure_ascii=False, indent=1)

    write_audit_md(args.out_audit_md, meta, audit_rows)
    wl_a, wl_b, wl_ppp = write_worklist(
        args.out_worklist_md, args.out_worklist_csv, meta, audit_rows)

    # ---- participle reverse indexes (surface form -> root/lemma + category) ----
    pmeta = {
        "source": os.path.basename(args.db), "dcs_snapshot": DCS_SNAPSHOT,
        "generated": str(date.today()), "categories": PARTICIPLE_ORDER,
        "labels": PARTICIPLE_LABELS,
    }
    with open(args.out_pindex, "w", encoding="utf-8") as fh:
        json.dump({"metadata": {**pmeta, "scope": "Whitney-linked roots",
                                "forms": len(whitney_index)},
                   "index": whitney_index}, fh, ensure_ascii=False, indent=1)
    with open(args.out_pindex_dcs, "w", encoding="utf-8") as fh:
        json.dump({"metadata": {**pmeta, "scope": "all DCS verbal roots",
                                "forms": len(dcs_index)},
                   "index": dcs_index}, fh, ensure_ascii=False, indent=1)

    print("\n=== summary ===")
    for k in ("matched", "normalized", "aliased", "homonym_shared", "unmatched"):
        print(f"  {k:15s} {counts[k]}")
    linked_n = (counts["matched"] + counts["normalized"]
                + counts["aliased"] + counts["homonym_shared"])
    print(f"  {'linked total':15s} {linked_n} / {len(lexicon)}")
    print(f"  participle forms: whitney={len(whitney_index)}  dcs-all={len(dcs_index)}")
    print(f"  worklist: class-backs-DCS={wl_a}  other-conflicts={wl_b}  ppp-unattested={wl_ppp}")
    print(f"\nWrote:\n  {args.out_freq}\n  {args.out_audit_json}\n  {args.out_audit_md}"
          f"\n  {args.out_pindex}\n  {args.out_pindex_dcs}"
          f"\n  {args.out_worklist_md}\n  {args.out_worklist_csv}")


_ROMAN_RE = re.compile(r"\b(I{1,3}|IV|VI{0,3}|IX|X)\b")


def sig_classes(signal):
    """Arabic class set implied by a present-stem signal string (e.g. 'I/VI'
    -> {1,6}, 'X/caus-denom' -> {10}). The 'athematic' bucket is a catch-all
    (classes 2/3/5/7/8/9 all look athematic) so it corroborates NOTHING
    specific — return empty rather than falsely pointing at 2/3."""
    if not signal or "athematic" in signal:
        return set()
    return {_ROMAN_TO_ARABIC[m.group(0)] for m in _ROMAN_RE.finditer(signal)
            if m.group(0) in _ROMAN_TO_ARABIC}


def write_worklist(path_md, path_csv, meta, rows):
    """Editorial worklist for correcting app_data.json: class conflicts the
    corpus corroborates against Whitney, plus PPP stems the corpus never shows.
    Prioritised by corpus frequency."""
    linked = [r for r in rows if r["dcs_lemma"]]

    # ---- class conflicts, with which side the corpus signal backs ----
    conf = []
    for r in linked:
        if r["class_verdict"] != "conflict":
            continue
        w, d = set(r["whitney_classes"]), set(r["dcs_classes"])
        sc = sig_classes(r.get("present_signal"))
        if sc & d and not (sc & w):
            backs = "DCS"        # corpus corroborates DCS -> Whitney correction candidate
        elif sc & w and not (sc & d):
            backs = "Whitney"    # corpus corroborates Whitney -> DCS is the outlier
        else:
            backs = "ambiguous"
        conf.append((r, backs))
    conf.sort(key=lambda rb: -rb[0]["total"])
    backs_dcs = [rb for rb in conf if rb[1] == "DCS"]
    backs_other = [rb for rb in conf if rb[1] != "DCS"]

    # ---- Whitney PPP stems unattested in corpus ----
    ppp = []
    for r in linked:
        miss = [x["stem"] for x in r.get("ppp_results", []) if x["verdict"] == "unattested"]
        if miss:
            ppp.append((r, miss))
    ppp.sort(key=lambda rm: -rm[0]["total"])

    def md_tbl(header, rb_list, kind):
        L = ["| id | root | Whitney | DCS | corpus signal | tokens |",
             "|---|---|---|---|---|---|"]
        for r, _ in rb_list:
            L.append(f"| {r['id']} | {r['root']} | {','.join(r['whitney_classes']) or '—'} "
                     f"| {','.join(r['dcs_classes']) or '—'} | {r.get('present_signal') or '—'} "
                     f"| {r['total']} |")
        return "\n".join(L)

    L = [f"# Whitney ↔ DCS editorial worklist\n",
         f"_Source: `{meta['source']}` ({meta['dcs_snapshot']}); generated {meta['generated']}._\n",
         "Actionable discrepancies for correcting `src/app_data.json`. The `id` is the lexicon "
         "entry id. **This is a review aid, not an oracle** — DCS's grammar field is itself "
         "lexicon metadata and the corpus signal is a coarse heuristic; confirm before editing.\n",
         f"## A. Class conflicts the corpus backs AGAINST Whitney ({len(backs_dcs)})\n",
         "Highest-priority: Whitney's class set is disjoint from DCS **and** the corpus "
         "present-stem signal points to the DCS class. Consider adding/adjusting the class.\n",
         md_tbl(None, backs_dcs, "class"), "",
         f"## B. Other class conflicts — review ({len(backs_other)})\n",
         "Disjoint class sets where the corpus signal does not corroborate DCS (sometimes it "
         "backs Whitney, meaning DCS's grammar field is the outlier — do not 'correct' these).\n",
         md_tbl(None, backs_other, "class"), "",
         f"## C. Whitney PPP stems unattested in the corpus ({len(ppp)})\n",
         "PPP forms Whitney lists that never appear in DCS. High-frequency roots first (a missing "
         "PPP on a common root is more suspect; rare/Vedic roots may simply be unattested).\n",
         "| id | root | unattested PPP | tokens |", "|---|---|---|---|"]
    for r, miss in ppp:
        L.append(f"| {r['id']} | {r['root']} | {', '.join(miss)} | {r['total']} |")
    L.append("")
    with open(path_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    # ---- CSV (machine-readable) ----
    import csv
    with open(path_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "root", "type", "whitney", "dcs", "corpus_signal",
                    "corpus_backs", "tokens"])
        for r, backs in conf:
            w.writerow([r["id"], r["root"], "class", "|".join(r["whitney_classes"]),
                        "|".join(r["dcs_classes"]), r.get("present_signal") or "",
                        backs, r["total"]])
        for r, miss in ppp:
            w.writerow([r["id"], r["root"], "ppp_unattested", "|".join(miss),
                        "", "", "", r["total"]])
    return len(backs_dcs), len(backs_other), len(ppp)


def write_audit_md(path, meta, rows):
    linked = [r for r in rows if r["dcs_lemma"]]
    cv = Counter(r["class_verdict"] for r in linked)
    conflicts = [r for r in linked if r["class_verdict"] == "conflict"]
    partial = [r for r in linked if r["class_verdict"] == "partial-overlap"]
    unattested_ppp = [
        (r, [x["stem"] for x in r["ppp_results"] if x["verdict"] == "unattested"])
        for r in linked
    ]
    unattested_ppp = [(r, lst) for r, lst in unattested_ppp if lst]
    lexicon_only = [r for r in linked if r["existence"] == "lexicon-only"]

    def tbl(rs, cols, fmt):
        out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
        out += [fmt(r) for r in rs]
        return "\n".join(out)

    L = []
    L.append("# Whitney ↔ DCS audit\n")
    L.append(f"_Source: `{meta['source']}` ({meta['dcs_snapshot']}); "
             f"generated {meta['generated']}._\n")
    L.append("**Honesty rules:** DCS `grammar` is itself lexicon metadata, so a class "
             "disagreement there is *lexicon-vs-lexicon*, not corpus proof. Absence of a "
             "finite class in the corpus is *no evidence*, never \"Whitney is wrong.\" The "
             "present-stem signal is a coarse heuristic shown for context only.\n")
    L.append("## Coverage\n")
    L.append(f"- Whitney entries: **{meta['total']}**")
    linked_total = (meta['matched'] + meta['normalized']
                    + meta.get('aliased', 0) + meta['homonym_shared'])
    L.append(f"- Linked to DCS: **{linked_total}** "
             f"(matched {meta['matched']}, normalized {meta['normalized']}, "
             f"aliased {meta.get('aliased', 0)}, homonym-shared {meta['homonym_shared']})")
    L.append(f"- Unmatched (no DCS lemma; citation-form/Vedic): **{meta['unmatched']}**")
    L.append(f"- Lexicon-only (DCS lemma but 0 corpus tokens): **{len(lexicon_only)}**\n")
    L.append("## Class verdicts (Whitney vs DCS grammar field)\n")
    L.append(tbl(
        [{"k": k, "n": n} for k, n in cv.most_common()],
        ["verdict", "count"], lambda r: f"| {r['k']} | {r['n']} |"))
    L.append("")
    L.append(f"### Conflicts ({len(conflicts)}) — disjoint class sets\n")
    L.append(tbl(
        sorted(conflicts, key=lambda r: -r["total"])[:60],
        ["root", "DCS lemma", "Whitney", "DCS grammar", "corpus signal", "tokens"],
        lambda r: f"| {r['root']} | {r['dcs_lemma']} | {','.join(r['whitney_classes']) or '—'} "
                  f"| {','.join(r['dcs_classes']) or '—'} | {r['present_signal'] or '—'} | {r['total']} |"))
    L.append("")
    L.append(f"### Partial overlap ({len(partial)})\n")
    L.append(tbl(
        sorted(partial, key=lambda r: -r["total"])[:40],
        ["root", "Whitney", "DCS grammar", "tokens"],
        lambda r: f"| {r['root']} | {','.join(r['whitney_classes'])} | {','.join(r['dcs_classes'])} | {r['total']} |"))
    L.append("")
    L.append(f"## PPP: Whitney stems unattested in corpus ({len(unattested_ppp)} roots)\n")
    L.append(tbl(
        sorted(unattested_ppp, key=lambda rl: -rl[0]["total"])[:60],
        ["root", "DCS lemma", "unattested PPP", "tokens"],
        lambda rl: f"| {rl[0]['root']} | {rl[0]['dcs_lemma']} | {', '.join(rl[1])} | {rl[0]['total']} |"))
    L.append("")
    L.append(f"## Lexicon-only roots ({len(lexicon_only)}) — DCS lists, corpus never attests\n")
    L.append(", ".join(sorted(r["root"] for r in lexicon_only)) or "_none_")
    L.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
