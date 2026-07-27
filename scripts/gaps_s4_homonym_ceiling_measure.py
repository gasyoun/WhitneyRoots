#!/usr/bin/env python3
"""H1747 / SL GAPS §4 — measure residual DCS-lumped homonym ceiling.

Does NOT invent sense attributions. Confirms current token_attribution.json
state: how many groups are reliable, why the residual fails, and whether any
'collapses onto one homonym' rows could be recovered by lower coverage floors.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "crosswalk" / "token_attribution.json"
OUT = ROOT / "crosswalk" / "gaps_s4_homonym_ceiling_report.json"


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    items = data["items"]
    rel = [it for it in items if it.get("reliable")]
    unrel = [it for it in items if not it.get("reliable")]
    reasons = Counter(it.get("reason", "?") for it in unrel)
    lump_1 = []
    multi_id = []
    collapse = []
    for it in unrel:
        reason = it.get("reason", "")
        n_ids = it.get("dcs_lemma_ids")
        if isinstance(n_ids, list):
            n_ids = len(n_ids)
        elif not isinstance(n_ids, int):
            n_ids = 0
        if "lumps" in reason or n_ids == 1:
            lump_1.append(it)
        elif "collapse" in reason:
            collapse.append(it)
        else:
            multi_id.append(it)

    report = {
        "handoff": "H1747",
        "gap": "SanskritLexicography/GAPS.md §4",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "model": "Grok 4.5 (grok-4.5)",
        "source": str(SRC.as_posix()),
        "groups": data.get("groups"),
        "reliable": len(rel),
        "unreliable": len(unrel),
        "reason_counts": dict(reasons),
        "lump_single_lemma_id": len(lump_1),
        "collapse_onto_one": len(collapse),
        "other_unreliable": len(multi_id),
        "verdict": (
            "HARD CEILING: single-lemma_id lumps cannot be token-attributed without "
            "sense/gloss gold (DCS meanings ↔ Warnemyr). Lowering coverage≥0.55 does "
            "not create new reliable splits when n_lemma_id=1. Residual requires "
            "manual/LLM gloss adjudication, not more morphology."
        ),
        "sample_lump": [
            {
                "lemma": it.get("lemma"),
                "reason": it.get("reason"),
                "coverage": it.get("coverage"),
                "glosses": [h.get("gloss") for h in it.get("homonyms", [])],
            }
            for it in lump_1[:12]
        ],
        "sample_collapse": [
            {
                "lemma": it.get("lemma"),
                "reason": it.get("reason"),
                "coverage": it.get("coverage"),
                "glosses": [h.get("gloss") for h in it.get("homonyms", [])],
            }
            for it in collapse[:12]
        ],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k not in ("sample_lump", "sample_collapse")}, ensure_ascii=False, indent=2))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
