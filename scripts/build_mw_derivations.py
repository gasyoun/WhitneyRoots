# -*- coding: utf-8 -*-
"""Derivation oracle: attach MW derivational productivity to each Whitney root.

Consumes csl-orig's pre-built `mw_etymology.tsv` (9,378 MW headwords with an
identified root, ~90% coverage) instead of re-extracting MW derivations here.
That TSV is the canonical derivation extract owned by csl-orig
(`v02/mw/analyze_mw_etymology.py`); this script only *reads* it and joins it
onto the Whitney root spine by root SLP1.

For each Whitney root it reports which MW headwords are derived from it -- i.e.
the root's derivational productivity in Monier-Williams -- with a breakdown by
deriv_type and a sample of headwords.

Output is a NEW read-only sidecar, `crosswalk/mw_derivations.json`. It does NOT
touch app_data.json, the crosswalk class fields, PPP overlays, homonym splits,
or any human-reviewed file. Load it like dcs_freq (optional enrichment).

    python scripts/build_mw_derivations.py [--sample N]

Join caveat: mw_etymology references a root by surface SLP1 (e.g. "kf"), not by
its own L-number, so homonymous roots that share a surface form are pooled
together. The per-root counts are therefore by surface form; this is recorded
in the output meta. UTF-8, no BOM.
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH = os.path.dirname(BASE)
MW_ETYM = os.path.join(GH, "csl-orig", "v02", "mw", "mw_etymology.tsv")
ROOTS_CSV = os.path.join(BASE, "crosswalk", "roots.csv")
OUT = os.path.join(BASE, "crosswalk", "mw_derivations.json")


def load_mw_etymology(path):
    """Group MW derivations by root surface SLP1.

    Returns {root_slp1: {"count": int, "deriv_types": {type: n}, "headwords": [slp1,...]}}.
    """
    by_root = defaultdict(lambda: {"count": 0, "deriv_types": defaultdict(int), "headwords": []})
    rows = 0
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            rows += 1
            root = (r.get("root_slp1") or "").strip()
            if not root:
                continue  # ~10% of MW headwords have no identified root
            hw = (r.get("headword_slp1") or "").strip()
            dt = (r.get("deriv_type") or "").strip() or "unspecified"
            bucket = by_root[root]
            bucket["count"] += 1
            bucket["deriv_types"][dt] += 1
            bucket["headwords"].append(hw)
    return by_root, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", type=int, default=12, help="max headwords sampled per root")
    ap.add_argument("--mw-etym", default=os.environ.get("WHITNEY_MW_ETYM", MW_ETYM),
                    help="path to csl-orig mw_etymology.tsv (default: sibling csl-orig)")
    args = ap.parse_args()

    if not os.path.exists(args.mw_etym):
        print("Error: MW etymology TSV not found at {}".format(args.mw_etym))
        print("It is produced by csl-orig/v02/mw/analyze_mw_etymology.py.")
        print("Pass --mw-etym PATH or set WHITNEY_MW_ETYM.")
        sys.exit(1)

    by_root, total_rows = load_mw_etymology(args.mw_etym)

    out = {}
    matched_roots = 0
    sum_over_roots = 0
    matched_surfaces = set()
    with open(ROOTS_CSV, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            slp1 = (r.get("root_slp1") or "").strip()
            wno = (r.get("whitney_no") or "").strip()
            if not slp1 or slp1 not in by_root:
                continue
            b = by_root[slp1]
            sample = sorted(set(b["headwords"]))[: args.sample]
            out[wno] = {
                "root_slp1": slp1,
                "mw_derived_count": b["count"],
                "deriv_types": dict(sorted(b["deriv_types"].items(), key=lambda x: -x[1])),
                "sample_headwords": sample,
            }
            matched_roots += 1
            sum_over_roots += b["count"]
            matched_surfaces.add(slp1)
    # Unique MW derivations covered (a surface form pooled across homonyms counts once).
    unique_derivations = sum(by_root[s]["count"] for s in matched_surfaces)

    payload = {
        "_meta": {
            "description": "MW derivational productivity per Whitney root, joined from "
            "csl-orig mw_etymology.tsv by root surface SLP1.",
            "source": "csl-orig/v02/mw/mw_etymology.tsv",
            "provenance": "derivation-oracle (read-only consume; no re-extraction)",
            "join_key": "root_slp1 surface form (homonyms sharing a surface form are pooled)",
            "mw_etymology_rows": total_rows,
            "whitney_roots_matched": matched_roots,
            "matched_root_surfaces": len(matched_surfaces),
            "unique_mw_derivations_covered": unique_derivations,
            "sum_over_roots": sum_over_roots,
            "note": "sum_over_roots > unique_mw_derivations_covered because homonymous "
            "Whitney roots sharing a surface SLP1 each receive that surface's full derivation set.",
        },
        "by_whitney_no": dict(sorted(out.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)),
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("MW etymology rows read    : {}".format(total_rows))
    print("Whitney roots matched     : {}".format(matched_roots))
    print("Unique MW derivations cover: {}".format(unique_derivations))
    print("Wrote {}".format(os.path.relpath(OUT, BASE)))


if __name__ == "__main__":
    main()
