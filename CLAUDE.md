# CLAUDE.md

_Created: 03-07-2026 · Last updated: 16-08-2026_

WhitneyRoots digitizes William Dwight Whitney's *The Roots, Verb-forms and
Primary Derivatives of the Sanskrit Language* into structured data and a
state-driven web app ([live](https://gasyoun.github.io/WhitneyRoots/)). Two
halves: a Python pipeline under `scripts/` (DCS root-class verification,
PPP validation, Whitney §-citation extraction, MW↔Whitney crosswalk) and a
vanilla-JS front end under `src/`. Most active work is the pipeline.

Org conventions live in [`../CLAUDE.md`](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md).
Before encodings or corpus data, read the
[Sanskrit context primer](https://github.com/gasyoun/github-spine/blob/main/SANSKRIT_CONTEXT_PRIMER.md).
[`scripts/sanskrit_util.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/sanskrit_util.py)
is the **canonical donor** other repos' `sanskrit_util.py` shims re-export —
read [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)
before changing its behaviour.

## How to run

```bash
node scripts/bundle.js              # REQUIRED after any edit under src/
python scripts/sanskrit_util.py
python scripts/build_decisions_doc.py
python scripts/build_form_section_edges.py
python scripts/build_reader_data.py
python scripts/dict_align.py
python scripts/emit_crosswalk.py
python scripts/extract_dict_roots.py
python scripts/fold_corpus.py
python scripts/token_disambiguate.py
python scripts/vidyut_paradigms.py
python scripts/vidyut_validate_ppp.py
```

No single test command covers the repo. Pipeline stage order lives in
[.ai_state.md](https://github.com/gasyoun/WhitneyRoots/blob/main/.ai_state.md).
CI (`ci.yml`) is the generic satellite baseline (markdown/YAML lint; ruff
when `.py` exists). Pages deploy: `pages.yml`.

## Key paths

| Path | Purpose |
|---|---|
| `src/core/` | JS state, hash router (`#v1/roots/list`), search, data load |
| `src/utils/linguistics.js` | JS-side IAST/Devanagari helpers |
| `src/app_data.json` | Primary lexicon (root, meaning, gaṇa) |
| `v3_app.js` | **Generated** bundle — never hand-edit |
| `scripts/dcs/` · `scripts/wikisource/` | Verification / fetch families |
| `crosswalk/` | MW↔Whitney outputs |
| `docs/DECISIONS_NEEDED.md` · `docs/PPP_APPARATUS_BLEED_WORKLIST.md` | Live queues |
| `Whitney_Transition_Runbook.md` | Pointer stub → `docs/BUILD_MANUAL.md` |

## Conventions

- **Bundle after every `src/` edit.** Nothing in CI enforces this.
- Root-class labels are revert-prone (Phase 8 reverted 120/139 empirical
  adds). Do not hand-edit `app_data.json` class fields without DCS
  cross-check.
- Residual homonym groups are a lexical-semantic problem
  (`token_disambiguate.py`), not a morphology-tool gap. Do not re-pilot
  vidyut / ND-SWSMP without new evidence.
- `sanskrit-util iast_to_devanagari` is broken — compose `to_slp1()` →
  `slp1_to_devanagari()`.

## Do not touch

- `v3_app.js` — regenerate with `node scripts/bundle.js`.
- `Whitney_Transition_Runbook.md` — extend `docs/BUILD_MANUAL.md` instead.
- Historical-only files: `detailed_conflict_triage.md`,
  `candidates_for_addition.md` (Phase 1–6 / Phase 8 revert audit).
- `Tolchelnikov/` — authored educational guides, not generated.

Danger facts:
[Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md)
and the generated block of
[AGENTS.md](https://github.com/gasyoun/WhitneyRoots/blob/main/AGENTS.md).

_Dr. Mārcis Gasūns_
