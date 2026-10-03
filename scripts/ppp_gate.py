# -*- coding: utf-8 -*-
"""ppp_gate.py — G87 (H5778): the pass/fail gate around the PPP validation
REPORT WRITER that H1668 said could not be a goal ("vidyut_validate_ppp is a
report writer — mismatches expected, not pass/fail").

The distinction this gate locks: the VALIDATOR is advisory (mismatches are
expected, adjudicated by humans — never a red), but the RUN itself has hard,
deterministic facts:
  1. the validator exits 0 and rewrites crosswalk/ppp_validation.json;
  2. every item carries a verdict from the closed set
     {match, mismatch, fill_candidate, vidyut_only} plus the provenance trio
     (matched_form / matched_against / match_basis) that makes it revisable;
  3. the verdict arithmetic sums: Σ verdict buckets == len(items) — a report
     that loses or double-counts a root is a broken run, not an opinion.

Usage: python3 scripts/ppp_gate.py   (from a checkout that has
scratch/phase0/root_spine.json — the gate runs the validator itself).
Exit 0 = GATE PASS (counts printed); exit 1 = GATE FAIL (first cause named).
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(BASE, "scripts", "vidyut_validate_ppp.py")
OUT = os.path.join(BASE, "crosswalk", "ppp_validation.json")
VERDICTS = ("match", "mismatch", "fill_candidate", "vidyut_only")
PROVENANCE = ("matched_form", "matched_against", "match_basis")


def fail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def main():
    if not os.path.isfile(VALIDATOR):
        fail(f"validator missing: {VALIDATOR}")
    proc = subprocess.run([sys.executable, VALIDATOR], capture_output=True,
                          text=True)
    if proc.returncode != 0:
        fail(f"vidyut_validate_ppp.py exited {proc.returncode}: "
             f"{(proc.stderr or proc.stdout)[-400:]}")
    try:
        with open(OUT, encoding="utf-8") as fb:
            report = json.load(fb)
    except (OSError, ValueError) as exc:
        fail(f"report unreadable after run: {exc}")
    items = report.get("items")
    if not isinstance(items, list) or not items:
        fail("report has no items[]")
    if "_meta" not in report:
        fail("report lost its _meta block")

    counts = {v: 0 for v in VERDICTS}
    for idx, item in enumerate(items):
        verdict = item.get("verdict")
        if verdict not in counts:
            fail(f"item[{idx}] verdict {verdict!r} outside the closed set")
        counts[verdict] += 1
        for field in PROVENANCE:
            if field not in item:
                fail(f"item[{idx}] missing provenance field {field!r}")
    total = sum(counts.values())
    if total != len(items):
        fail(f"verdict arithmetic broken: Σ buckets {total} != items "
             f"{len(items)}")

    print(f"GATE PASS: {len(items)} roots · match={counts['match']} "
          f"mismatch={counts['mismatch']} "
          f"fill_candidate={counts['fill_candidate']} "
          f"vidyut_only={counts['vidyut_only']} · provenance + arithmetic OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
