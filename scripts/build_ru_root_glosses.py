"""Derive a corpus-attested RU gloss layer for WhitneyRoots' crosswalk roots (H347).

Joins crosswalk/roots.csv (930 Whitney roots, SLP1-keyed) against the sibling
SanskritRussian repo's root_glossary.jsonl (corpus_lexicon Sa->Ru alignments,
2,021 roots) on the exact root_slp1 key -- both sides already use the same
length-preserving SLP1 encoding, so no lemma-hop or NFD normalization is
needed. Additive only: writes crosswalk/ru_root_glosses.tsv, never touches
roots.csv or any other reviewed crosswalk file. Machine-derived, unreviewed --
candidate layer only (see the TSV's own header comment).
"""
import csv
import io
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOTS_CSV = REPO_ROOT / "crosswalk" / "roots.csv"
GLOSSARY_JSONL = REPO_ROOT.parent / "SanskritRussian" / "root_glossary.jsonl"
OUT_TSV = REPO_ROOT / "crosswalk" / "ru_root_glosses.tsv"
TOP_N = 3
LOW_ATTESTATION_THRESHOLD = 3  # root_freq_n below this counts as "low-attestation" residue


def sibling_repo_commit(repo_dir: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%H %ad", "--date=short",
             "--", "root_glossary.jsonl"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_glossary(path: Path) -> dict:
    index = {}
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            index[rec["root_slp1"]] = rec
    return index


def top_glosses(rec: dict, n: int):
    translations = sorted(rec.get("translations", []), key=lambda t: -t.get("n", 0))
    return translations[:n]


def main() -> int:
    glossary = load_glossary(GLOSSARY_JSONL)
    glossary_commit = sibling_repo_commit(GLOSSARY_JSONL.parent)

    rows = []
    with io.open(ROOTS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        crosswalk_rows = list(reader)

    n_total = len(crosswalk_rows)
    n_hit = 0
    n_absent = 0
    n_low_attestation = 0
    homonym_shared_slp1 = {
        slp1 for slp1, count in
        defaultdict(int, {}).items()
    }
    # count how many crosswalk rows share each root_slp1 (homonym groups)
    slp1_counts = defaultdict(int)
    for row in crosswalk_rows:
        slp1_counts[row["root_slp1"]] += 1

    for row in crosswalk_rows:
        slp1 = row["root_slp1"]
        rec = glossary.get(slp1)
        homonym_shared = slp1_counts[slp1] > 1
        if rec is None:
            n_absent += 1
            rows.append({
                "whitney_no": row["whitney_no"],
                "root_slp1": slp1,
                "root_iast": row["root_iast"],
                "gloss_ru_1": "", "count_1": "",
                "gloss_ru_2": "", "count_2": "",
                "gloss_ru_3": "", "count_3": "",
                "root_freq_n": "0",
                "root_n_forms": "0",
                "homonym_shared": "1" if homonym_shared else "0",
            })
            continue
        n_hit += 1
        freq_n = rec.get("n", 0)
        if freq_n < LOW_ATTESTATION_THRESHOLD:
            n_low_attestation += 1
        top = top_glosses(rec, TOP_N)
        out_row = {
            "whitney_no": row["whitney_no"],
            "root_slp1": slp1,
            "root_iast": row["root_iast"],
            "root_freq_n": str(freq_n),
            "root_n_forms": str(rec.get("n_forms", 0)),
            "homonym_shared": "1" if homonym_shared else "0",
        }
        for i in range(TOP_N):
            if i < len(top):
                out_row[f"gloss_ru_{i+1}"] = top[i].get("ru", "")
                out_row[f"count_{i+1}"] = str(top[i].get("n", 0))
            else:
                out_row[f"gloss_ru_{i+1}"] = ""
                out_row[f"count_{i+1}"] = ""
        rows.append(out_row)

    today = datetime.now().strftime("%d-%m-%Y")
    header_comment = (
        f"# ru_root_glosses.tsv -- machine-derived, UNREVIEWED candidate layer (H347, {today})\n"
        f"# Source: SanskritRussian root_glossary.jsonl (corpus_lexicon Sa->Ru alignments), "
        f"commit {glossary_commit}\n"
        f"# Join: exact root_slp1 match against crosswalk/roots.csv, no lemma-hop, no NFD "
        f"normalization (length-preserving SLP1 both sides)\n"
        f"# Coverage: {n_hit}/{n_total} roots have >=1 corpus-attested RU gloss "
        f"({n_hit/n_total:.1%}); {n_absent} absent from corpus_lexicon; "
        f"{n_low_attestation} present but low-attestation (root_freq_n < {LOW_ATTESTATION_THRESHOLD})\n"
        f"# Promotion into any reviewed artifact is a separate human-gated step -- gaps stay gaps, "
        f"no LLM-invented glosses.\n"
    )

    fieldnames = [
        "whitney_no", "root_slp1", "root_iast",
        "gloss_ru_1", "count_1", "gloss_ru_2", "count_2", "gloss_ru_3", "count_3",
        "root_freq_n", "root_n_forms", "homonym_shared",
    ]
    with io.open(OUT_TSV, "w", encoding="utf-8", newline="") as f:
        f.write(header_comment)
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {OUT_TSV} ({n_total} rows)")
    print(f"coverage: {n_hit}/{n_total} ({n_hit/n_total:.1%}) roots have >=1 corpus RU gloss")
    print(f"residue: {n_absent} absent from corpus_lexicon, {n_low_attestation} low-attestation (n<{LOW_ATTESTATION_THRESHOLD})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
