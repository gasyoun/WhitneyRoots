# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

WhitneyRoots digitizes and re-engineers William Dwight Whitney's *The Roots,
Verb-forms and Primary Derivatives of the Sanskrit Language* into structured
data, plus builds a state-driven web app (`v3_app.js`, [live
site](https://gasyoun.github.io/WhitneyRoots/)) to explore it. The repo has
**two distinct halves that this file previously undersold** — a Python data
pipeline (root-class verification against the DCS corpus, PPP validation,
Whitney §-citation extraction, a MW↔Whitney crosswalk, morphology
disambiguation) under `scripts/`, and a small vanilla-JS front-end under
`src/`. Most active engineering right now is the Python pipeline (see
`.ai_state.md` for the current phase); the front-end is comparatively stable.
`scripts/sanskrit_util.py` is also the **canonical donor** other repos'
`sanskrit_util.py` shims re-export from — see
[`../sanskrit-util/CLAUDE.md`](../sanskrit-util/CLAUDE.md) — changes here can
ripple across the org; check `../SHARED_CODE.md` before altering its behavior.

## Common commands

```bash
node scripts/bundle.js              # REQUIRED after any edit under src/ — concatenates modules into v3_app.js
python scripts/sanskrit_util.py     # canonical Sanskrit string-helper donor (see Conventions)
python scripts/build_decisions_doc.py     # regenerate docs/DECISIONS_NEEDED.md (Grammar-§ evidence for queued root-class adds)
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

No single test/build command covers the whole repo — the Python pipeline is a
chain of standalone stage scripts (see `.ai_state.md` "Dev Notes" for the
current phase's actual invocation order; it changes as phases complete/revert).

## Key directories / files

| Path | Purpose |
|---|---|
| `src/core/` | JS app state (`state.js`), routing (`router.js`, hash-based: `#v1/roots/list`), search (`search.js`), data loading (`data.js`), plus `ai.js`, `achievements.js`, `analytics.js`, `quiz.js` |
| `src/utils/linguistics.js` | JS-side Sanskrit normalization/IAST transliteration — donor for `deva_to_iast`/`iast_to_devanagari`/`normalize_sanskrit` in `sanskrit-util` |
| `src/renderers/` | Pure functions returning DOM elements from state |
| `src/app_data.json` | Primary lexicon data source (root, meaning, gaṇa class, links) |
| `v3_app.js` | **Generated** production bundle — never hand-edit, regenerate via `scripts/bundle.js` |
| `scripts/sanskrit_util.py` | Canonical Python Sanskrit string-helper implementation (see `../sanskrit-util/CLAUDE.md`) |
| `scripts/dcs/`, `scripts/wikisource/` | DCS-corpus verification and Wikisource-fetch subtool families |
| `docs/DECISIONS_NEEDED.md`, `docs/PPP_APPARATUS_BLEED_WORKLIST.md` | Live decision queues — check before assuming a root-class or PPP question is settled |
| `PPP_CORRECTION_PLAN.md`, `REVIEWER_GUIDE.md` | Current correction-pass plan and reviewer instructions (EN/RU) |
| `crosswalk/` | MW↔Whitney root crosswalk outputs |
| `review_queue.json` | Pending human-review items from the root-class revert/add pipeline |
| `Tolchelnikov/` | Educational morphonology guides (Talmud series) authored by I.E. Tolchelnikov — reference material, not generated |
| `Whitney_Transition_Runbook.md` | **Stub only (2 bytes)** — despite the name, do not expect migration instructions here |

## CI workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | push/PR to `master`/`main` | Generic satellite-repo baseline: markdown lint (warn-only), markdown link-check (continue-on-error), YAML lint (hard fail), conditional Python lint (`ruff`, error-codes only) and JS lint (`npm test --if-present`) if `package.json`/`.py` files exist |
| `dependabot-auto-merge.yml` | Dependabot PRs | Auto-merges dependency bumps once checks pass |
| `pages.yml` | (GitHub Pages deploy) | Publishes the static site to `gasyoun.github.io/WhitneyRoots/` |

## Conventions

- **Bundle after every `src/` edit** — `node scripts/bundle.js` regenerates
  `v3_app.js`; nothing enforces this in CI (no JS build-freshness gate), so a
  forgotten bundle silently ships stale JS.
- **Root-class changes are historically revert-prone.** Phase 8
  (`.ai_state.md`) reverted 120 of 139 empirically-added class labels after
  they were found unsound (I/VI accent-collapse contamination). Treat any new
  class addition as provisional until corpus-verified — don't hand-edit
  `app_data.json` class fields without the same DCS cross-check discipline.
- **Morphology is effectively mined out** for the remaining homonym-class
  ambiguities (per `.ai_state.md`): vidyut and ND-SWSMP were both piloted and
  neither resolves the residual ~33 DCS-lumped homonym groups beyond the 5 a
  gaṇa-distinct signal already covers — remaining disambiguation is
  lexical-semantic (`token_disambiguate.py`'s job), not a morphology-tool gap.
  Don't re-pilot a morphology library expecting a different answer without
  new evidence.
- **`CHANGELOG.md` has been externally edited mid-session before** (noted in
  `.ai_state.md`) — check `git log` on it before assuming your last edit is
  the latest state.
- Windows/UTF-8 conventions from the org-root `../CLAUDE.md` apply to every
  new Python script here (`sys.stdout.reconfigure(encoding='utf-8')`, etc.).

## What not to touch

- `v3_app.js` — generated by `scripts/bundle.js` from `src/`; edits are lost
  on the next bundle run.
- `Whitney_Transition_Runbook.md` — a 2-byte stub; don't treat it as a real
  spec (nothing currently points serious documentation there).
- Data files superseded-but-retained for history: `detailed_conflict_triage.md`,
  `candidates_for_addition.md` (Phase 1–6 analysis, subject of the Phase 8
  revert — kept for audit trail only, not current guidance).
