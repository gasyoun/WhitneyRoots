"""H1065 — alternation-type classification over Whitney's roots, ingested from the
AUTHORIAL source instead of induced.

The ISCLS-2024 Non-Paninian paper's data backbone (per-root alternation type) turned out
to be published in-house all along: Tolchelnikov's own Приложение 1 of the Talmud manual
(2.1.6), machine-parsed at SanskritGrammar/TolchelnikovTalmud_2026/data/talmud_appendix1.json
(745 roots, `tip` = Таблица 5 alternation type I..IV, `ryad` = ablaut series, seṭ, pada,
Whitney join key). MG pointed at this source when asked per the handoff's gate question.

Таблица 5 semantics (grades at morphological positions 1/2/3):
  I   (полноизменяемые)    : слабая / guṇa   / vṛddhi   -> 2MP guṇa    -> regular
  II  (неполноизменяемые)  : guṇa   / guṇa   / vṛddhi   -> 2MP guṇa    -> regular (1MP deviates)
  III (неполноизменяемые)  : слабая / слабая / vṛddhi   -> 2MP слабая  -> under-strong
  IV  (неизменяемые)       : vṛddhi / vṛddhi / vṛddhi   -> 2MP vṛddhi  -> over-strong

The paper's ~110/820 (~13%) exceptions = 2MP-grade deviants = tips III+IV; in Приложение 1
that is 84/745 = 11.3%.

Deterministic; UTF-8 stdout. Fable 5 (claude-fable-5), 17-07-2026, per MG's authorization
on the Opus-tier row.
"""

import csv
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
APPENDIX1 = REPO.parent / "SanskritGrammar" / "TolchelnikovTalmud_2026" / "data" / "talmud_appendix1.json"
ROOTS_CSV = REPO / "crosswalk" / "roots.csv"
SEED_CSV = REPO / "crosswalk" / "alternation_type_seed.csv"
OUT_CSV = REPO / "crosswalk" / "alternation_type.csv"
OUT_JSON = REPO / "crosswalk" / "alternation_type_stats.json"

TIP_GRADES = {
    "I": ("basic", "guna", "vrddhi"),
    "II": ("guna", "guna", "vrddhi"),
    "III": ("basic", "basic", "vrddhi"),
    "IV": ("vrddhi", "vrddhi", "vrddhi"),
}
TIP_CLASS = {"I": "regular", "II": "regular", "III": "under-strong", "IV": "over-strong"}


def nfc(s):
    return unicodedata.normalize("NFC", (s or "").strip())


def main():
    app = json.load(open(APPENDIX1, encoding="utf-8"))
    entries = app["roots"]

    # index appendix entries by every whitney spelling (NFC), keeping homonym number
    by_spelling = {}
    for e in entries:
        for sp in (e.get("whitney_spellings") or []):
            by_spelling.setdefault(nfc(sp), []).append(e)

    rows_out = []
    match_kind = Counter()
    with open(ROOTS_CSV, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            w_no = row["whitney_no"]
            iast = nfc(row["root_iast"])
            hom = nfc(row.get("homonym") or "")
            cands = by_spelling.get(iast, [])
            chosen, kind = None, None
            if len(cands) == 1:
                chosen, kind = cands[0], "unique_spelling"
            elif len(cands) > 1:
                by_hom = [e for e in cands if nfc(e.get("whitney_num") or "") == hom]
                if len(by_hom) == 1:
                    chosen, kind = by_hom[0], "spelling+homonym"
                else:
                    same_tip = {e.get("tip") for e in cands}
                    if len(same_tip) == 1 and None not in same_tip:
                        chosen, kind = cands[0], "ambiguous_same_tip"
                    else:
                        kind = "ambiguous_conflicting"
            else:
                kind = "no_appendix1_entry"
            match_kind[kind] += 1

            if chosen is not None and chosen.get("tip") in TIP_GRADES:
                tip = chosen["tip"]
                g1, g2, g3 = TIP_GRADES[tip]
                rows_out.append({
                    "whitney_no": w_no, "root_iast": row["root_iast"],
                    "homonym": row.get("homonym") or "",
                    "talmud_root": chosen.get("root") or "",
                    "talmud_whitney_ref": chosen.get("whitney_ref") or "",
                    "talmud_tip": tip,
                    "talmud_ryad": chosen.get("ryad") or "",
                    "talmud_set": chosen.get("set") or "",
                    "mp1_grade": g1, "mp2_grade": g2, "mp3_grade": g3,
                    "alternation_class": TIP_CLASS[tip],
                    "mp1_deviation": "guna_for_basic" if tip == "II" else "",
                    "derivation_method": "talmud_appendix1",
                    "grade_confidence": "authorial",
                    "match_kind": kind, "unclassifiable_reason": "",
                })
            else:
                reason = kind if kind != "unique_spelling" else "appendix1_entry_without_tip"
                rows_out.append({
                    "whitney_no": w_no, "root_iast": row["root_iast"],
                    "homonym": row.get("homonym") or "",
                    "talmud_root": "", "talmud_whitney_ref": "", "talmud_tip": "",
                    "talmud_ryad": "", "talmud_set": "",
                    "mp1_grade": "", "mp2_grade": "", "mp3_grade": "",
                    "alternation_class": "unclassifiable",
                    "mp1_deviation": "", "derivation_method": "",
                    "grade_confidence": "", "match_kind": kind or "",
                    "unclassifiable_reason": reason,
                })

    fieldnames = list(rows_out[0].keys())
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_out)

    # ── gold-seed validation ──
    seed = list(csv.DictReader(open(SEED_CSV, encoding="utf-8", newline="")))
    by_no = {r["whitney_no"]: r for r in rows_out}
    gold = []
    for s in seed:
        got = by_no.get(s["whitney_no"], {})
        expected = s["alternation_class"]
        actual = got.get("alternation_class", "MISSING")
        verdict = ("MATCH" if actual == expected
                   else "RESOLVES_UNCERTAIN" if expected == "uncertain" and actual != "unclassifiable"
                   else "MISMATCH")
        gold.append({"whitney_no": s["whitney_no"], "root": s["root_iast"],
                     "seed_class": expected, "seed_confidence": s["root_match_confidence"],
                     "talmud_tip": got.get("talmud_tip", ""), "ingested_class": actual,
                     "verdict": verdict})

    classified = [r for r in rows_out if r["alternation_class"] != "unclassifiable"]
    cls = Counter(r["alternation_class"] for r in classified)
    exc = cls["under-strong"] + cls["over-strong"]
    stats = {
        "instrument": "ingest_talmud_alternation.py over talmud_appendix1.json (manual 2.1.6) x crosswalk/roots.csv",
        "total_whitney_roots": len(rows_out),
        "classified": len(classified),
        "class_counts": dict(cls),
        "tip_counts": dict(Counter(r["talmud_tip"] for r in classified)),
        "exception_rate_pct": round(100 * exc / len(classified), 1) if classified else None,
        "paper_reference_rate": "~110/820 = ~13% (ISCLS 2024 slides)",
        "match_kinds": dict(match_kind),
        "gold_seed_validation": gold,
    }
    OUT_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "gold_seed_validation"},
                     ensure_ascii=False, indent=1))
    print("\ngold seed:")
    for g in gold:
        print(f"  {g['root']}: seed={g['seed_class']} ({g['seed_confidence']}) "
              f"tip={g['talmud_tip']} -> {g['ingested_class']} [{g['verdict']}]")
    print("->", OUT_CSV)


if __name__ == "__main__":
    main()
