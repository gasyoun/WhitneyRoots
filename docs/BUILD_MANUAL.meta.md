# BUILD_MANUAL.meta.md — metadoc for the operator manual

_Created: 10-07-2026 · Last updated: 18-07-2026_

Companion record for [docs/BUILD_MANUAL.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.md), per the org metadoc convention (a document *about* the document: purpose, provenance, improvement backlog, revision history — never a duplicate of the subject's content).

## Purpose

Give a new operator/contributor a single document from which the whole repo can be run end-to-end — regenerate every derived data file (Track A, the Python crosswalk pipeline) and build/serve/deploy the JS lexicon app (Track B) — without reading the source code.

## Audience

- A **new operator** re-running the pipeline or refreshing a deliverable (primary).
- A **maintainer** touching a stage script (Part II: invariants, per-script traps, the Phase-8 revert history).
- An **AI session** picking up a WhitneyRoots handoff (the Symptom→Cause→Cure table encodes the recorded failure modes).

## Provenance

- Authored 10-07-2026 by Fable 5 (`claude-fable-5`) under handoff [H503](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H503-Fable_WhitneyRoots_pipeline_and_app_build_manual_10.07.26.md) (manual-coverage census batch H501–H531, 79 active repos surveyed 10-07-2026).
- Method: four parallel Explore-agent surveys (Python pipeline map with exact I/O per script; JS app + deploy map; data-file provenance + glossary; gold-standard template skeleton from [RussianRamayana Litpam-Indexator MANUAL.md](https://github.com/gasyoun/RussianRamayana/blob/main/Litpam-Indexator/docs/indesign-pipeline/MANUAL.md)), synthesized against repo state at commit `37fb894`.
- The manual supersedes the intent of [Whitney_Transition_Runbook.md](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_Transition_Runbook.md) — an empty stub until 18-07-2026, when H1245 gave it a pointer body to this manual.

## Verification

```
LAST_VERIFIED: 18-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1245
COMMANDS_SPOT_RUN: 6
```

Spot-run 18-07-2026 from a fresh worktree (no gitignored spine/mirror): `node
scripts/bundle.js` (committed bundle proven fresh — timestamp-only diff),
`python scripts/emit_accent_rules_tsv.py` (sanity OK, TSV in sync),
`python scripts/dcs/scan_ppp_apparatus.py` (0 records — backlog drained),
`python scripts/dcs/audit_class_changes.py` (clean),
`python scripts/ingest_talmud_alternation.py` (idempotent, gold seed reproduced),
`python scripts/dcs/extract_dcs.py` (runs; surfaced committed-outputs staleness —
regenerated data discarded, docs-only pass). **Not** spot-run: stages 0–5 proper
(need the spine/mirror), `vidyut`-dependent scripts, the JS smoke-test checklist.

## Ranked improvement backlog

All seven items remain **open** — every one is a code/CI/data change, and the
18-07-2026 pass (H1245) was docs-fenced by design. Reconciled statuses:

| # | Item | Status |
|---|---|---|
| 1 | **Pin the environment**: add a `requirements.txt` (or `pyproject.toml`) capturing `vidyut`, `rdflib` and the `sanskrit-util` editable install, so the manual's Environment section becomes one `pip install -r` line | open (code — out of docs-pass scope) |
| 2 | **De-hardcode Stage 0**: `scratch/phase0/parse_warnemyr.py` carries an absolute `BASE` path; make it repo-relative so the bootstrap runs on any clone unchanged | open (code) |
| 3 | **Bundle-freshness CI gate**: CI does not detect a stale `v3_app.js`; add a job that re-runs `node scripts/bundle.js` and fails on a non-timestamp diff (or retire the bundle — the deployed `index.html` doesn't reference it) | open (CI). 18-07-2026: bundle verified fresh by hand — the gap is the gate, not the current state |
| 4 | **Decide the `v3_app.js` question**: the deployed HTML loads ES modules directly, so the bundle ships unused in the Pages artifact — either wire it as the production script or document it as the embeddable single-file build and drop it from `_site` | open (@DECIDE-shaped) |
| 5 | **`1885/` mirror acquisition recipe**: the manual says "copy it from an existing machine or re-mirror" — script the re-mirror (`curl -k` + the `wn_index.tsv` URL map) so a fresh clone can bootstrap unattended | open (code) |
| 6 | **One-command pipeline driver**: stages 0–5 are hand-ordered; a `run_pipeline.py` (or make-style) driver with per-stage skip flags would eliminate order mistakes the asserts currently catch late | open (code) |
| 7 | **Time budget table**: the gold standard carries measured per-stage timings; measure a full pipeline run and add one (only `extract_dcs.py` ≈1 min is recorded so far — re-confirmed 18-07-2026) | open (needs a full spine run) |
| 8 | **Refresh the committed `extract_dcs.py` projections**: they were generated 10-06-2026 and now lag `src/app_data.json` (measured verdict drift 18-07-2026: agree 322→321, conflict 103→97) — a data-refresh PR, deliberately not folded into H1245 | open (data; added 18-07-2026) |

## Known limitations

- Command flags were transcribed from source at commit `37fb894`; the scripts' own `--help` wins if they drift.
- The accent-validation runner (`scratch/accent_validation/`) is gitignored and not on disk — that track is documented as archival, not reproducible.
- The manual does not cover the human-adjudication *content* workflow (Queues A–E) — that is [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md)'s job.

## Intended use / known misuse

- **For**: an operator or AI session that needs to regenerate a specific derived file (crosswalk CSV, reader dataset, DCS frequency table) or bring up/deploy the Lexicon Explorer app, working from the manual alone without reading pipeline source. Also the first stop when a stage script fails — the [Symptom → Cause → Cure](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.md#symptom--cause--cure) table encodes 16 recorded failure modes.
- **Known/likely misuse**:
  - Treating it as documentation of *what the data means* — schema, authority order, and layer model live in [DESIGN.md](https://github.com/gasyoun/WhitneyRoots/blob/main/DESIGN.md), not here.
  - Running stages out of the canonical 0→5 order on the assumption idempotent guards make order irrelevant — the guards make *re-running a single stage* safe, they do not make *skipping ahead* safe; several stages assert fields only an earlier stage populates.
  - Copy-pasting the transcribed CLI flags without checking `--help` after the repo has moved past commit `37fb894` — flags were transcribed from source at that commit and the scripts' own `--help` wins on drift (see Known limitations).
  - Using it to adjudicate a root-class or PPP question — that workflow (Queues A–E) is explicitly out of scope; use [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md) instead.
  - Assuming the accent-validation runner (`scratch/accent_validation/`) is reproducible from the manual — it is documented as archival only, and the runner itself is gitignored and absent from disk.

## Maintenance & sunset plan

- **Owner**: no dedicated maintainer process — the manual is kept current by whichever human or AI session next changes a stage script's CLI surface or the data-flow diagram's shape; there is no scheduled review cadence.
- **Keeps it alive**: WhitneyRoots' own pipeline and app code (`scripts/`, `scratch/phase0/`, `src/`) — the manual tracks that surface, not an external feed. CI (YAML lint + `ruff`) gates merges to `main` but does not verify the manual's content against the scripts (see backlog item 3, a bundle-freshness gate, for the nearest analogue).
- **Sunset trigger**: the manual is retired only if Track A (the Python crosswalk pipeline) or Track B (the JS app) is itself retired or replaced by a different build system: if that happens, this file and [docs/BUILD_MANUAL.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.md) move to an `archive/` folder (per the org's `/handoff-archive` convention) with a pointer to the successor manual.
- **What "archived" looks like**: file moved under `docs/archive/`, this metadoc's Deprecation status flipped to `superseded by [X]` or `retired`, and any live cross-references (`CLAUDE.md`, repo README) repointed in the same commit.

## Deprecation status

`active`

## Related documents

- [DESIGN.md](https://github.com/gasyoun/WhitneyRoots/blob/main/DESIGN.md) — schema, authority order, layer model.
- [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md) + [docs/DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) — adjudication.
- [CLAUDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/CLAUDE.md) — AI-session conventions (subset of the manual's traps).
- [docs/PPP_APPARATUS_BLEED_WORKLIST.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/PPP_APPARATUS_BLEED_WORKLIST.md) — the apparatus-bleed record.

## Revision history

| Date | Change | By |
|---|---|---|
| 10-07-2026 | Initial version: cheat-sheet, data-flow diagram, stages 0–5 + branch tracks, Track B (app/bundle/serve/deploy), 16-row Symptom→Cause→Cure, glossary, maintainer appendix (invariants, per-script traps, Phase-8 archive) | Fable 5 (`claude-fable-5`), H503 |
| 11-07-2026 | template v2 backfill (H663) | Sonnet 5 (`claude-sonnet-5`) |
| 18-07-2026 | H1245 estate refresh: drift-refresh vs 8 commits (new `ingest_talmud_alternation.py` branch-track row; Track B rewritten for the sanskrit-util re-vendor; bundle 16→17 modules; Stage 0b staleness warning; version bookkeeping to 1.5.1), deepen (six-command spot-run evidence block, two new symptom rows), consolidate (Transition-Runbook stub → pointer body; PPP_CORRECTION_PLAN historical banner), `LAST_VERIFIED` block, backlog reconciled + item 8 added | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
