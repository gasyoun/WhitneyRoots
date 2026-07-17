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

The paper's ~110/820 (~13%) exceptions = 2MP-grade deviants = tips III+IV.

WE DO NOT JOIN THE CATALOG OURSELVES — we read the canonical join
================================================================
The first cut of this script re-joined `talmud_appendix1.json` against `roots.csv` itself,
matching on the Whitney spelling. It bound a catalog entry whenever that spelling was
unique **without checking the homonym the author had indexed**, so ONE authorial entry
smeared across SEVERAL of Whitney's homonyms — 15 entries onto 31 records, 16 excess
assertions. The author's «2 iṣ» was asserted of BOTH iṣ¹ and iṣ²; his single «1 śṛ» of
śṛ¹ AND śṛ² AND śṛ³ — every one still labelled `grade_confidence=authorial`. Same shape
as the Warnemyr union-smear (FINDINGS §3).

`whitney_talmud.json` (SanskritGrammar, H1065) is the ONE canonical Приложение-1 × Whitney
join and carries its own audit trail — `talmud_root`, `talmud_ref`, `talmud_match` — so
this script now **reads** the binding instead of repeating it. That join abstains wherever
the author's homonym index disagrees with Whitney's (iṣ¹, śṛ², śṛ³, paś², stu², pat², pā³
…), leaving those roots unclassified pending his ruling rather than guessing.

Consequence: never "fix" a wrong Тип here — fix the join upstream and regenerate. This
file is a projection, not a source.

Deterministic; UTF-8 stdout. Originally Fable 5 (claude-fable-5) 17-07-2026 over its own
join; re-pointed at the canonical feed by Opus 4.8 (claude-opus-4-8) the same day.
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
FEED = (REPO.parent / "SanskritGrammar" / "TolchelnikovTalmud_2026"
        / "data" / "whitney_talmud.json")
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


def main():
    if not FEED.exists():
        sys.exit(f"canonical join feed not found: {FEED}\n"
                 "Needs a SanskritGrammar sibling clone (H1065).")
    records = json.load(open(FEED, encoding="utf-8"))["verbal_roots"]

    rows_out = []
    match_kind = Counter()
    for r in records:
        tip = r.get("tip")
        # `talmud_match` is set iff the canonical join bound an entry to this root. It
        # abstains on homonym divergence, so a null here means the author asserted NOTHING
        # about this root — never a licence to fall back on a neighbouring homonym.
        bound = r.get("talmud_match")
        match_kind[bound or "no_authorial_binding"] += 1

        base = {
            "whitney_no": str(r["whitney_no"]),
            "root_iast": r["root_iast"],
            "homonym": r.get("homonym") or "",
            "talmud_root": r.get("talmud_root") or "",
            "talmud_whitney_ref": r.get("talmud_ref") or "",
            "match_kind": bound or "",
        }
        if tip in TIP_GRADES:
            g1, g2, g3 = TIP_GRADES[tip]
            rows_out.append({
                **base,
                "talmud_tip": tip,
                "talmud_ryad": r.get("ryad") or "",
                "talmud_set": r.get("set") or "",
                "mp1_grade": g1, "mp2_grade": g2, "mp3_grade": g3,
                "alternation_class": TIP_CLASS[tip],
                "mp1_deviation": "guna_for_basic" if tip == "II" else "",
                "derivation_method": "talmud_appendix1_via_whitney_talmud",
                "grade_confidence": "authorial",
                "unclassifiable_reason": "",
            })
        else:
            rows_out.append({
                **base,
                "talmud_tip": "", "talmud_ryad": "", "talmud_set": "",
                "mp1_grade": "", "mp2_grade": "", "mp3_grade": "",
                "alternation_class": "unclassifiable",
                "mp1_deviation": "", "derivation_method": "", "grade_confidence": "",
                # bound-but-tipless = the author catalogs the root yet gives no Тип;
                # unbound = absent from his catalog OR a homonym divergence he must rule on.
                "unclassifiable_reason": ("authorial_entry_without_tip" if bound
                                          else "no_authorial_binding"),
            })

    rows_out.sort(key=lambda x: int(x["whitney_no"]))
    order = ["whitney_no", "root_iast", "homonym", "talmud_root", "talmud_whitney_ref",
             "talmud_tip", "talmud_ryad", "talmud_set", "mp1_grade", "mp2_grade",
             "mp3_grade", "alternation_class", "mp1_deviation", "derivation_method",
             "grade_confidence", "match_kind", "unclassifiable_reason"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=order)
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
        "instrument": "ingest_talmud_alternation.py over whitney_talmud.json "
                      "(SanskritGrammar H1065 canonical Приложение-1 × Whitney join)",
        "source_of_truth": "SanskritGrammar/TolchelnikovTalmud_2026/data/whitney_talmud.json",
        "join_owner": "build_whitney_talmud.py — NOT re-derived here (see module docstring)",
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
