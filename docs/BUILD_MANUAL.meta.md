# BUILD_MANUAL.meta.md — metadoc for the operator manual

_Created: 10-07-2026 · Last updated: 10-07-2026_

Companion record for [docs/BUILD_MANUAL.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.md), per the org metadoc convention (a document *about* the document: purpose, provenance, improvement backlog, revision history — never a duplicate of the subject's content).

## Purpose

Give a new operator/contributor a single document from which the whole repo can be run end-to-end — regenerate every derived data file (Track A, the Python crosswalk pipeline) and build/serve/deploy the JS lexicon app (Track B) — without reading the source code.

## Audience

- A **new operator** re-running the pipeline or refreshing a deliverable (primary).
- A **maintainer** touching a stage script (Part II: invariants, per-script traps, the Phase-8 revert history).
- An **AI session** picking up a WhitneyRoots handoff (the Symptom→Cause→Cure table encodes the recorded failure modes).

## Provenance

- Authored 10-07-2026 by Fable 5 (`claude-fable-5`) under handoff [H503](https://github.com/gasyoun/Uprava/blob/main/handoffs/H503-Fable_WhitneyRoots_pipeline_and_app_build_manual_10.07.26.md) (manual-coverage census batch H501–H531, 79 active repos surveyed 10-07-2026).
- Method: four parallel Explore-agent surveys (Python pipeline map with exact I/O per script; JS app + deploy map; data-file provenance + glossary; gold-standard template skeleton from [RussianRamayana Litpam-Indexator MANUAL.md](https://github.com/gasyoun/RussianRamayana/blob/main/Litpam-Indexator/docs/indesign-pipeline/MANUAL.md)), synthesized against repo state at commit `37fb894`.
- The manual supersedes the intent of [Whitney_Transition_Runbook.md](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_Transition_Runbook.md) (a 2-byte stub that never held content).

## Ranked improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | **Pin the environment**: add a `requirements.txt` (or `pyproject.toml`) capturing `vidyut`, `rdflib` and the `sanskrit-util` editable install, so the manual's Environment section becomes one `pip install -r` line | open |
| 2 | **De-hardcode Stage 0**: `scratch/phase0/parse_warnemyr.py` carries an absolute `BASE` path; make it repo-relative so the bootstrap runs on any clone unchanged | open |
| 3 | **Bundle-freshness CI gate**: CI does not detect a stale `v3_app.js`; add a job that re-runs `node scripts/bundle.js` and fails on a non-timestamp diff (or retire the bundle — the deployed `index.html` doesn't reference it) | open |
| 4 | **Decide the `v3_app.js` question**: the deployed HTML loads ES modules directly, so the bundle ships unused in the Pages artifact — either wire it as the production script or document it as the embeddable single-file build and drop it from `_site` | open |
| 5 | **`1885/` mirror acquisition recipe**: the manual says "copy it from an existing machine or re-mirror" — script the re-mirror (`curl -k` + the `wn_index.tsv` URL map) so a fresh clone can bootstrap unattended | open |
| 6 | **One-command pipeline driver**: stages 0–5 are hand-ordered; a `run_pipeline.py` (or make-style) driver with per-stage skip flags would eliminate order mistakes the asserts currently catch late | open |
| 7 | **Time budget table**: the gold standard carries measured per-stage timings; measure a full pipeline run and add one (only `extract_dcs.py` ≈1 min is recorded so far) | open |

## Known limitations

- Command flags were transcribed from source at commit `37fb894`; the scripts' own `--help` wins if they drift.
- The accent-validation runner (`scratch/accent_validation/`) is gitignored and not on disk — that track is documented as archival, not reproducible.
- The manual does not cover the human-adjudication *content* workflow (Queues A–E) — that is [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md)'s job.

## Related documents

- [DESIGN.md](https://github.com/gasyoun/WhitneyRoots/blob/main/DESIGN.md) — schema, authority order, layer model.
- [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md) + [docs/DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) — adjudication.
- [CLAUDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/CLAUDE.md) — AI-session conventions (subset of the manual's traps).
- [docs/PPP_APPARATUS_BLEED_WORKLIST.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/PPP_APPARATUS_BLEED_WORKLIST.md) — the apparatus-bleed record.

## Revision history

| Date | Change | By |
|---|---|---|
| 10-07-2026 | Initial version: cheat-sheet, data-flow diagram, stages 0–5 + branch tracks, Track B (app/bundle/serve/deploy), 16-row Symptom→Cause→Cure, glossary, maintainer appendix (invariants, per-script traps, Phase-8 archive) | Fable 5 (`claude-fable-5`), H503 |

_Dr. Mārcis Gasūns_
