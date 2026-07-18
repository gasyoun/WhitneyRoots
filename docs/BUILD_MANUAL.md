# WhitneyRoots — Operator & Build Manual

_Created: 10-07-2026 · Last updated: 18-07-2026_

This is the end-to-end operator manual for [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots): how to regenerate every derived data file, run the Python crosswalk pipeline, build and serve the JS lexicon app, and ship a deploy — **from the manual alone, without reading the source code**. It is modelled on the org's gold-standard operator manual ([RussianRamayana Litpam-Indexator MANUAL.md](https://github.com/gasyoun/RussianRamayana/blob/main/Litpam-Indexator/docs/indesign-pipeline/MANUAL.md)).

The repo has **two halves**:

- **Track A — the Python data pipeline**: parses a local mirror of Warnemyr's digitization of Whitney's *Roots* into a per-root "spine", folds in the DCS corpus, Monier-Williams/Apte dictionaries and Whitney *Grammar* §§, and emits the FAIR crosswalk (`crosswalk/roots.csv` and friends) plus the reader dataset.
- **Track B — the vanilla-JS web app**: the Lexicon Explorer at [gasyoun.github.io/WhitneyRoots/](https://gasyoun.github.io/WhitneyRoots/) plus the standalone passage Reader, deployed by GitHub Pages with **no build step** (one optional bundling script).

> **Which document to open:**
> - *Run/regenerate something* → this manual.
> - *What the data means, schema, authority order* → [DESIGN.md](https://github.com/gasyoun/WhitneyRoots/blob/main/DESIGN.md).
> - *Adjudicate a root-class or PPP question* → [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md) (EN/RU) + [docs/DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md).
> - *AI-assistant conventions* → [CLAUDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/CLAUDE.md).
> - [Whitney_Transition_Runbook.md](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_Transition_Runbook.md) is a **pointer stub to this manual** (empty from creation until 18-07-2026, when H1245 gave it a pointer body) — this manual is the document that name promised.

---

## Cheat-sheet: the whole pipeline on one screen

Run from the repo root. Steps 1–2 are one-time bootstrap; 3–10 regenerate everything; 11–12 are the app.

1. **[Prerequisites](#environment--prerequisites)** — Python 3.7+, Node, sibling repos `sanskrit-util` + `VisualDCS` + `csl-orig`, the local `1885/` mirror, `pip install vidyut rdflib`.
2. **Spine bootstrap** — `python scratch/phase0/parse_warnemyr.py` → `scratch/phase0/root_spine.json` (the hub every later stage mutates). [Stage 0](#stage-0--bootstrap-the-spine-from-the-warnemyr-mirror)
3. **DCS extraction** — `python scripts/dcs/extract_dcs.py` → `src/dcs_freq.json` + audits/worklists. [Stage 0b](#stage-0b--dcs-corpus-extraction)
4. **Corpus fold** — `python scripts/fold_corpus.py`, then `python scripts/token_disambiguate.py`. [Stage 1](#stage-1--fold-the-corpus-into-the-spine)
5. **Dictionary arm** — `python scripts/extract_dict_roots.py`, then `python scripts/dict_align.py`. [Stage 2](#stage-2--dictionary-arm-mw--apte)
6. **Grammar §§ ingest** — `python scripts/wikisource/fetch_whitney.py --full` → `src/whitney_sections.json`. [Stage 3](#stage-3--whitney-grammar--ingest-wikisource)
7. **Form→§ edges** — `python scripts/build_form_section_edges.py`. [Stage 4](#stage-4--form-section-edges)
8. **Emit deliverables** — `python scripts/emit_crosswalk.py` (FAIR crosswalk) and `python scripts/build_reader_data.py` (reader dataset). [Stage 5](#stage-5--emit-the-crosswalk-and-reader-data)
9. **Branch tracks (as needed)** — vidyut paradigms + PPP validation, MW derivations, accent-rules TSV, decisions register. [Branch tracks](#branch-tracks)
10. **Data fixes** — the idempotent `scripts/dcs/fix_ppp_*` / `apply_ppp_corrections.py` editors of `src/app_data.json`. [Maintainer appendix](#part-ii--maintainer-appendix)
11. **JS app** — edit under `src/`, run `node scripts/bundle.js`, serve with `python -m http.server 8000`, test at `http://localhost:8000/`. [Track B](#track-b--the-js-web-app)
12. **Ship** — commit → PR (YAML lint + `ruff` error-codes are the only hard CI gates) → merge to `main` → Pages deploys automatically. [Deploy](#deployment-github-pages)

Something broke? Jump to [Symptom → Cause → Cure](#symptom--cause--cure).

---

## Data flow

```
                      TRACK A — Python pipeline
                      =========================

 1885/  (local HTTrack mirror          Whitney_roots_class-PP.txt
  of warnemyr.com, gitignored)          + scratch/phase0/wn_index.tsv
        │                                       │
        ▼                                       ▼
 [0] scratch/phase0/parse_warnemyr.py ──► scratch/phase0/root_spine.json   (+ audit.md)
                                                │ (the mutable hub, gitignored)
 src/app_data.json ──► [0b] scripts/dcs/extract_dcs.py ◄── ../VisualDCS/src/DCS-data-2026/dcs_full.sqlite
                                │
                                ▼
                        src/dcs_freq.json ──► [1] scripts/fold_corpus.py ──► spine (+corpus)
                        dcs_full.sqlite  ──► [1b] scripts/token_disambiguate.py ──► spine (+dcs_freq_token)
                                                                                  + crosswalk/token_attribution.json
 ../csl-orig/v02/{mw,ap90} ──► [2a] scripts/extract_dict_roots.py ──► crosswalk/{mw,apte}_roots.json
                                                │
                                                ▼
                               [2b] scripts/dict_align.py ──► spine (+dict) + crosswalk/root_alignment.csv
 en.wikisource.org ──► [3] scripts/wikisource/fetch_whitney.py --full ──► src/whitney_sections.json
                                                │
                                                ▼
 src/form_section_concordance.json ──► [4] scripts/build_form_section_edges.py ──► spine (+whitney_sections)
                                                │                                 + crosswalk/root_section_edges.csv
                ┌───────────────────────────────┴───────────────────────┐
                ▼                                                       ▼
 [5] scripts/emit_crosswalk.py                            [5] scripts/build_reader_data.py
     ──► crosswalk/roots.csv, root_class.csv,                 ──► src/reader_data.json
         roots.sqlite, roots.ttl, _unmatched.csv                  (consumed by reader/)

                      TRACK B — JS app
                      ================

 src/{core,utils,renderers}/*.js + src/entry.js ──► node scripts/bundle.js ──► v3_app.js
 index.html ──loads──► src/entry.js (ES modules) ──fetches──► src/app_data.json (+ optional sidecars)
 push to main ──► .github/workflows/pages.yml ──► gasyoun.github.io/WhitneyRoots/
```

Two different files are "the data", one per half — do not confuse them:

| File | Role | Producer |
|---|---|---|
| `scratch/phase0/root_spine.json` | Crosswalk hub (Track A). Gitignored — exists only after Stage 0. | [scratch/phase0/parse_warnemyr.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scratch/phase0/parse_warnemyr.py), then mutated by stages 1–4 |
| [src/app_data.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/app_data.json) | The JS app's lexicon (Track B; also read by `extract_dcs.py`). Committed. | No single generator — curated incrementally by the `scripts/dcs/*` fix/apply scripts |

[src/dcs_freq.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/dcs_freq.json) is the bridge: extracted against `app_data.json`, folded into the spine.

---

## Environment & prerequisites

- **OS**: Windows-first (every script forces UTF-8 stdio), but nothing is Windows-only.
- **Python 3.7+** (no venv, no `requirements.txt` — dependencies are implicit). Third-party packages actually needed:
  - `pip install vidyut` — only for [scripts/vidyut_paradigms.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/vidyut_paradigms.py).
  - `pip install rdflib` — optional; [scripts/emit_crosswalk.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/emit_crosswalk.py) skips Turtle validation without it.
  - Everything else is stdlib (`sqlite3`, `json`, `csv`, `re`, `urllib`).
- **Node.js** (any modern version) — only for `node scripts/bundle.js`.
- **Sibling repos** cloned next to this one under the same parent directory:

| Sibling | Needed for | What is read |
|---|---|---|
| [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util) | almost every Python script | [scripts/sanskrit_util.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/sanskrit_util.py) is a shim that loads `../sanskrit-util/py/sanskrit_util/__init__.py` — **missing sibling = ImportError everywhere** |
| [VisualDCS](https://github.com/gasyoun/VisualDCS) | Stages 0b, 1b; optional in Stage 5 | `../VisualDCS/src/DCS-data-2026/dcs_full.sqlite` (the **full** DB, not the 31 MB `dcs.sqlite` sample) + `derived-data/.../dcs_ppp_verified.tsv` |
| [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) | Stage 2a; MW derivations | `v02/mw/mw.txt`, `v02/ap90/ap90.txt`, `v02/mw/mw_etymology.tsv` |

- **The `1885/` mirror** (gitignored, ~13 MB, © 2005 L. Warnemyr — not redistributed): a local HTTrack mirror of `warnemyr.com/skrgram`, 939 `root_*.html` pages + the full grammar mirror. Stage 0 cannot run without it. If you must re-fetch: the site's HTTPS certificate is invalid — use `curl -k`, and **never guess page filenames** (the encoding is irregular: `ś→z`, `ā→aa`, `ṣ→_s`, `ḷ→_l`); resolve URLs through the `{sense→URL}` map in `scratch/phase0/wn_index.tsv`.
- **Network** (read-only, no credentials anywhere in the repo): English Wikisource (Stage 3), VedaWeb 2.0 (accent validation — archival), warnemyr.com (only if re-mirroring).
- **Encoding discipline** (org-wide, enforced by asserts in the scripts): UTF-8 everywhere, **never UTF-8-BOM**; every script calls `sys.stdout.reconfigure(encoding='utf-8')`; several stages assert the files they touch carry no BOM.

---

# Part I — Operator walkthrough

Each stage: the exact command, what it consumes, what it produces. All commands run from the repo root. Stages 1–4 **mutate the spine in place** — re-running a stage is safe (idempotent guards + class-field asserts), but the canonical order below is what the asserts expect.

## Stage 0 — bootstrap the spine from the Warnemyr mirror

```
python scratch/phase0/parse_warnemyr.py
```

- **Consumes**: `1885/root_*.html` (all 939), `scratch/phase0/wn_index.tsv`, [Whitney_roots_class-PP.txt](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_roots_class-PP.txt).
- **Produces**: `scratch/phase0/root_spine.json` (930 keyed root-senses; 35 flagged `class_uncertain`) + `scratch/phase0/audit.md` (23 GAP/SMEAR flags).
- **Notes**: paths are hardcoded inside the script (including an absolute `BASE` — adjust if your clone lives elsewhere). This is the **only** producer of the spine; every downstream stage asserts the spine (and its `root_slp1` field) exists and tells you to run this first if not.

## Stage 0b — DCS corpus extraction

```
python scripts/dcs/extract_dcs.py
```

- **Consumes**: [src/app_data.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/app_data.json), `../VisualDCS/src/DCS-data-2026/dcs_full.sqlite` (override with `--db PATH`).
- **Produces**: [src/dcs_freq.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/dcs_freq.json), [Whitney_DCS_audit.json](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_DCS_audit.json)/[.md](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_DCS_audit.md), [Whitney_DCS_worklist.md](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_DCS_worklist.md)/[.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_DCS_worklist.csv), [src/participle_index.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/participle_index.json), [src/participle_index_dcs.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/participle_index_dcs.json).
- **Notes**: ~1 min full scan; every output path has a `--out-*` override flag. Links Whitney roots to DCS by `root = lemma` (IAST). Read the audit's "Honesty rules": corpus absence ≠ Whitney wrong.
- ⚠️ **The committed outputs lag their inputs.** They were generated 10-06-2026; `src/app_data.json` has taken PPP/class fixes since, so a fresh run produces *real* verdict drift (18-07-2026 check: agree 322→321, conflict 103→97, partial-overlap 254→262), not just a new date stamp. Before quoting any audit/worklist count, check the `generated` date in `Whitney_DCS_audit.md` and re-run this stage if it trails `app_data.json`'s last data commit. (A refresh of the committed outputs is queued as its own data task — deliberately not bundled into doc passes.)

## Stage 1 — fold the corpus into the spine

```
python scripts/fold_corpus.py
python scripts/token_disambiguate.py
```

- [scripts/fold_corpus.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/fold_corpus.py) folds `src/dcs_freq.json` into the spine under a `corpus` key (frequency only — class fields are hard-guarded by asserts).
- [scripts/token_disambiguate.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/token_disambiguate.py) splits a shared DCS lemma's verb tokens across Whitney homonyms via DCS's own `lemma_id`s (gloss-first, gaṇa fallback); writes [crosswalk/token_attribution.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/token_attribution.json) and adds `corpus.dcs_freq_token` to reliable groups only. Needs `dcs_full.sqlite`.

## Stage 2 — dictionary arm (MW + Apte)

```
python scripts/extract_dict_roots.py
python scripts/dict_align.py
```

- [scripts/extract_dict_roots.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/extract_dict_roots.py) extracts verbal-root entries from `../csl-orig/v02/mw/mw.txt` and `../csl-orig/v02/ap90/ap90.txt` → [crosswalk/mw_roots.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/mw_roots.json), [crosswalk/apte_roots.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/apte_roots.json).
- [scripts/dict_align.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dict_align.py) aligns them onto the spine by SLP1 + class (conservative; class hard-guarded) → spine gains `dict`; also writes [crosswalk/root_alignment.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/root_alignment.csv) + [crosswalk/alignment_review.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alignment_review.json).

## Stage 3 — Whitney *Grammar* §§ ingest (Wikisource)

```
python scripts/wikisource/fetch_whitney.py --full
```

- **Consumes**: the MediaWiki API at `en.wikisource.org` (page base *Sanskrit Grammar (Whitney)*). Raw HTML is cached under `scratch/wikisource/Chapter_<RN>.html` (gitignored) and reused unless `--refresh`.
- **Produces**: [src/whitney_sections.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/whitney_sections.json).
- **Mode flags** (mutually exclusive): `--pilot` (chapters X + XIII, the default) · `--full` (verb-system chapters IX–XV — the live-build choice) · `--all` (every chapter I–XVIII) · `--chapters X,XIII,XI` (explicit comma-separated Roman numerals).

## Stage 4 — form→section edges

```
python scripts/build_form_section_edges.py
```

- **Consumes**: the spine, [src/form_section_concordance.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/form_section_concordance.json) (the hand-built form-category → §-range table; authored from Whitney's ToC, never scraped), [src/whitney_sections.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/whitney_sections.json).
- **Produces**: spine gains `whitney_sections` edge lists; writes [crosswalk/root_section_edges.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/root_section_edges.csv). Validates edges against the fetched §§ (IX–XV); class-guarded.

## Stage 5 — emit the crosswalk and reader data

```
python scripts/emit_crosswalk.py
python scripts/build_reader_data.py
```

- [scripts/emit_crosswalk.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/emit_crosswalk.py) emits the FAIR Layer-1 dataset from the spine: [crosswalk/roots.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv), [crosswalk/root_class.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/root_class.csv), `crosswalk/roots.sqlite`, [crosswalk/roots.ttl](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.ttl), [crosswalk/roots.csv-metadata.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv-metadata.json), [crosswalk/_unmatched.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/_unmatched.csv). Self-validates row counts and no-BOM; validates the TTL if `rdflib` is installed.
- [scripts/build_reader_data.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/build_reader_data.py) reshapes the spine into [src/reader_data.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/reader_data.json) (~3.3 MB: per-root records + a normalized `form_index` + nasal-fold aliases). If `dcs_full.sqlite` is reachable it also indexes every attested VERB surface form; if the sibling is absent it prints "DCS sqlite not found" and skips gracefully.

## Branch tracks

Run only what you need; each hangs off the products above.

| Command | Consumes | Produces |
|---|---|---|
| `python scripts/vidyut_paradigms.py` | spine + the `vidyut` package's bundled Dhātupāṭha | [src/paradigms.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/paradigms.json) (454 roots / 503 paradigms; display only — never touches class/freq) |
| `python scripts/vidyut_validate_ppp.py` | spine + `src/paradigms.json` + [Whitney_roots_class-PP.txt](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_roots_class-PP.txt) | [crosswalk/ppp_validation.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/ppp_validation.json) (advisory; never edits the spine). Run **after** `vidyut_paradigms.py` |
| `python scripts/build_mw_derivations.py [--sample N] [--mw-etym PATH]` | [crosswalk/roots.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv) + `../csl-orig/v02/mw/mw_etymology.tsv` | [crosswalk/mw_derivations.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/mw_derivations.json). Run **after** `emit_crosswalk.py` (the one script that still needs `roots.csv` first); `--sample` = max headwords per root (default 12), TSV path also via env `WHITNEY_MW_ETYM` |
| `python scripts/emit_accent_rules_tsv.py` | [crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json) (**hand-curated source of truth** — rules R01–R18 + 19-cell matrix; edit the JSON, never the TSV) | [crosswalk/accent_rules.tsv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.tsv) |
| `python scripts/ingest_talmud_alternation.py` | the canonical Приложение-1 × Whitney join `../SanskritGrammar/TolchelnikovTalmud_2026/data/whitney_talmud.json` ([SanskritGrammar](https://github.com/gasyoun/SanskritGrammar) sibling required — since v1.5.1 the script deliberately does **not** re-join against `roots.csv` itself, the source of the retired homonym-smear defect) + the gold seed [crosswalk/alternation_type_seed.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type_seed.csv) | [crosswalk/alternation_type.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type.csv) (930 rows: 787 authorially classified — regular/under-strong/over-strong — 19 homonym-divergence abstentions, rest unclassifiable-with-reason) + [crosswalk/alternation_type_stats.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type_stats.json). Idempotent; re-verifies the 7-row gold seed on every run (`tan` MISMATCH is the recorded seed erratum, `svar` RESOLVES_UNCERTAIN). Method + validation: [crosswalk/ALTERNATION_TYPE_TALMUD_INGEST_2026.md](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/ALTERNATION_TYPE_TALMUD_INGEST_2026.md) (H1065, v1.4.0–1.5.1) |
| `python scripts/build_decisions_doc.py` | [review_queue.json](https://github.com/gasyoun/WhitneyRoots/blob/main/review_queue.json) + [src/grammar_refs.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/grammar_refs.json) + spine + `crosswalk/ppp_validation.json` (+ VisualDCS `dcs_ppp_verified.tsv`, optional) | [docs/DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) (regenerable — do not hand-edit) |

> [crosswalk/accent_validation.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_validation.json) + [docs/ACCENT_VALIDATION_REPORT.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_REPORT.md) are the archived deliverables of a one-off validation run against VedaWeb 2.0 / Casaretto accents; the runner lived in gitignored `scratch/accent_validation/` and is **not** part of the reproducible pipeline.

## Track B — the JS web app

The app is vanilla ES modules — **no framework, no npm, no build step**. [index.html](https://github.com/gasyoun/WhitneyRoots/blob/main/index.html) loads [src/entry.js](https://github.com/gasyoun/WhitneyRoots/blob/main/src/entry.js) directly as a module; on `DOMContentLoaded` it wires the `statechange` event → render, starts the hash router, and fetches the data.

1. **Edit** modules under [src/](https://github.com/gasyoun/WhitneyRoots/tree/main/src): `core/` (state, data loading, search, router, quiz, analytics, achievements, AI-insight heuristics), `renderers/` (pure DOM-returning functions), `utils/` (`dom.js`, `linguistics.js`). Since 14-07-2026 (PR [#41](https://github.com/gasyoun/WhitneyRoots/pull/41)) the Sanskrit normalization/transcode logic is **no longer inline**: this repo was the original donor to [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util), and both JS consumers now delegate back to vendored builds of that canonical package — `src/vendor/sanskrit-util.js` (ESM copy, byte-identical to `sanskrit-util/js/index.mjs`) for `utils/linguistics.js`, and `reader/vendor/sanskrit-util.global.js` (IIFE, `window.SanskritUtil`) for the Reader. Vendored copies are **re-copied whole from sanskrit-util, never hand-edited**.
2. **Bundle** after every `src/` edit:

   ```
   node scripts/bundle.js
   ```

   [scripts/bundle.js](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/bundle.js) concatenates the **17** modules in a hardcoded order (`vendor/sanskrit-util.js` deliberately precedes `utils/linguistics.js` so the stripped import resolves) into [v3_app.js](https://github.com/gasyoun/WhitneyRoots/blob/main/v3_app.js) — strips `import`/`export` by regex including sanskrit-util's multi-line `export default {...}` block, prepends a timestamp banner. **No CI gate checks bundle freshness** — a forgotten run silently ships a stale bundle. Verify: re-run it and `git diff v3_app.js` (only the `Generated:` timestamp line should change if fresh — confirmed clean 18-07-2026). Never hand-edit `v3_app.js`.
3. **Serve** — `fetch()` of local JSON is blocked under `file://`, so use any static server from the repo root:

   ```
   python -m http.server 8000
   ```

   Explorer: `http://localhost:8000/` · Reader: `http://localhost:8000/reader/index.html`.
4. **Data contract** — `loadAppData()` in [src/core/data.js](https://github.com/gasyoun/WhitneyRoots/blob/main/src/core/data.js) fetches `src/app_data.json` (**required**) plus four optional sidecars, each merged only if present: `src/dcs_freq.json`, `src/participle_index.json`, `src/paradigms.json`, `src/affix_data.json` (built externally by SanskritLexicography's `affix_pedagogy.py`). The app runs with the sidecars missing.
5. **Routes** (hash-based, [src/core/router.js](https://github.com/gasyoun/WhitneyRoots/blob/main/src/core/router.js)): `#v1/roots/list` (default) · `#v1/roots/item/<id>` · `#v1/quiz` · `#v1/affixes`; the Reader is a plain link to `reader/index.html`.
6. **The Reader** ([reader/](https://github.com/gasyoun/WhitneyRoots/tree/main/reader)) is a separate self-contained app (classic script, not a module): paste an IAST/Devanagari passage, click a word → root, Whitney §§, MW/Apte sense, DCS frequency. It loads [src/reader_data.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/reader_data.json) — regenerate that with `python scripts/build_reader_data.py` (Stage 5) after spine changes.

### Manual smoke-test checklist (no JS test suite exists)

- Explorer loads with the root list; search finds `bhū` and a diacritic-free form (`bhu`).
- A root card opens the detail view (`#v1/roots/item/<id>`), showing classes, PPP, grammar §§.
- Quiz and Affixes views render; Reader resolves a pasted word to a root.
- DevTools console shows no fetch 404 on `src/app_data.json`.

## Deployment (GitHub Pages)

Deploy is automatic: **push to `main`** triggers [.github/workflows/pages.yml](https://github.com/gasyoun/WhitneyRoots/blob/main/.github/workflows/pages.yml) (also runnable via *workflow_dispatch*). There is no build — the workflow assembles `_site/` by copying exactly: `index.html`, `index.css`, `v3_app.js`, `.nojekyll`, and the whole `src/` + `reader/` directories, then uploads to Pages. `scripts/`, `docs/`, `crosswalk/`, `scratch/` are deliberately excluded. Published at [gasyoun.github.io/WhitneyRoots/](https://gasyoun.github.io/WhitneyRoots/) (relative paths make the `/WhitneyRoots/` base path just work).

> Known quirk: the shipped `index.html` loads `src/entry.js` (ES modules) — `v3_app.js` is copied into the artifact but **not referenced** by the deployed HTML. The bundle currently matters only as an embeddable single-file build.

### CI gates on a PR ([.github/workflows/ci.yml](https://github.com/gasyoun/WhitneyRoots/blob/main/.github/workflows/ci.yml))

| Job | Blocking? | What it checks |
|---|---|---|
| yaml-lint | **yes** | `yaml.safe_load` over every `*.yml`/`*.yaml` |
| python-lint | **yes** | `ruff check --select=E9,F63,F7,F82` (syntax/undefined-name class only) |
| markdown-lint | no (warn-only) | `markdownlint-cli2` |
| link-check | no (`continue-on-error`) | markdown link checker |
| js-lint | never runs | requires a root `package.json`, which does not exist |

Plus [dependabot-auto-merge.yml](https://github.com/gasyoun/WhitneyRoots/blob/main/.github/workflows/dependabot-auto-merge.yml) auto-merges dependency bumps.

---

## Symptom → Cause → Cure

| Symptom | Cause | Cure |
|---|---|---|
| `ImportError` from `sanskrit_util` in any script | The [scripts/sanskrit_util.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/sanskrit_util.py) shim can't find the sibling package | Clone [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util) next to this repo, or `pip install -e <path>/sanskrit-util/py` |
| Downstream stage aborts "run parse_warnemyr.py first" / missing `root_slp1` | `scratch/phase0/root_spine.json` absent or from a stale schema | Run [Stage 0](#stage-0--bootstrap-the-spine-from-the-warnemyr-mirror); it needs the local `1885/` mirror |
| Stage 0 can't find `1885/` pages | The mirror is gitignored — a fresh clone doesn't have it | Copy it from an existing machine, or re-mirror `warnemyr.com/skrgram` with `curl -k` (invalid cert) via the URL map in `scratch/phase0/wn_index.tsv` — never guess filenames (`ś→z`, `ā→aa`, `ṣ→_s`, `ḷ→_l`) |
| DCS-reading scripts return near-empty results | Pointed at the 31 MB `dcs.sqlite` **sample** instead of the full DB | Use `../VisualDCS/src/DCS-data-2026/dcs_full.sqlite` (the default; `--db` to override) |
| Corpus says a thematic root is "class I, VI" | **Accent-collapse**: DCS is unaccented; I (`cárati`) and VI (`tudáti`) are identical without accents. Same trap: `root+ya` passives masquerade as class IV | Never trust corpus-inferred class labels; decide by root-vowel grade per [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md). This exact trap caused the Phase-8 revert of 120 additions |
| App shows the eternal "loading" spinner locally | Opened via `file://` — `fetch()` of local JSON is blocked | Serve over HTTP: `python -m http.server 8000` from the repo root |
| Site works locally but the deployed app behaves stale | Edited `src/` without re-bundling, or Pages cached | `node scripts/bundle.js` + hard-refresh; remember no CI gate catches a stale `v3_app.js` |
| `emit_crosswalk.py` skips TTL validation | `rdflib` not installed (optional dep) | `pip install rdflib` — or ignore; the TTL is still written |
| `vidyut_paradigms.py` fails to import | `vidyut` not installed | `pip install vidyut` |
| A root's PPP looks like apparatus junk (`-tave`, `= seq.`, `RV1`…) | **Apparatus bleed** — Whitney's citation apparatus leaked into the `ppp` field | See [docs/PPP_APPARATUS_BLEED_WORKLIST.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/PPP_APPARATUS_BLEED_WORKLIST.md); enumerate with `python scripts/dcs/scan_ppp_apparatus.py`, fix with the `fix_ppp_*` scripts (idempotent). The historical 39-record backlog is fully drained — the scanner reports `0 apparatus-bleed records` as of 18-07-2026 — so any hit now is a **new** bleed, worth its own worklist entry |
| `extract_dcs.py` output wildly differs from the committed audit/worklist files | The committed projections lag `src/app_data.json` — they carry a `generated` date (10-06-2026 as of this writing) and the app data has taken fixes since | Not an extractor bug: trust the fresh run, check the date stamp, and land a data-refresh PR separately from doc work (see Stage 0b note) |
| A blank class/PPP (`—`) treated as "defective root" | `—` in the Warnemyr scrape usually means a **capture gap**, not a defective root (e.g. `kḷp` is really class I, PPP `kḷptá`) | Audit against the actual Warnemyr page before concluding anything |
| Wikisource fetch re-downloads everything | `--refresh` passed, or the `scratch/wikisource/` cache was deleted | Drop `--refresh`; the cache is reused by default |
| `build_mw_derivations.py` exits with an error about a missing TSV | `../csl-orig/v02/mw/mw_etymology.tsv` absent | Generate it in the csl-orig sibling (`v02/mw/analyze_mw_etymology.py`) or pass `--mw-etym PATH` |
| Your uncommitted edits vanish / `CHANGELOG.md` differs from what you wrote | An **external actor** (another session/watcher) has edited this repo mid-session before | `git log -p CHANGELOG.md` before trusting its head; land risky changes from a fresh worktree off `origin/main` |
| Edits to `v3_app.js` disappear | It is a **generated** bundle | Edit `src/`, then `node scripts/bundle.js` |

---

## Glossary

| Term | Meaning here |
|---|---|
| **gaṇa / verb class (I–X)** | Whitney's present-system conjugation class; Roman numerals in `classes` / `class` fields. The primary homonym discriminator |
| **spine / hub** | The per-root-sense record set keyed on `whitney_no` (`scratch/phase0/root_spine.json`); the join point of the lexical crosswalk and the grammar-§ graph |
| **whitney_no** | Canonical sense id (#1–938); other sources' homonym numbers are local labels mapped many-to-many onto it |
| **PPP** | Past Passive Participle (`-ta`/`-na`); a first-class data field, corpus-validated (ATTESTED / LIKELY_ERROR / SUSPICIOUS / PLAUSIBLE_GAP) |
| **seṭ vs aniṭ** | Whether the root takes connecting *i* in the PPP (`-ita` vs `-ta`); the §956 test for triaging suspicious PPPs |
| **accent-collapse** | The I/VI (and IV/passive) indistinguishability in the unaccented DCS corpus — the false signal behind the Phase-8 revert |
| **class-smear / union-smear** | Warnemyr-mirror defect: a root's homonyms show the *union* of their classes; Stage 0 re-derives class per homonym |
| **`—` (capture gap)** | A blank in the scrape — usually missing data, **not** a defective root |
| **apparatus bleed** | Whitney's citation apparatus (period markers, alt-joiners, datival infinitives) leaked into `ppp` fields; cleaned by the `fix_ppp_*` family |
| **SLP1 / IAST** | ASCII-safe encoding (crosswalk key, e.g. `kxp`) vs diacritic Roman for display (`kḷp`); transcoded by `sanskrit_util` |
| **DCS** | Digital Corpus of Sanskrit (Hellwig), read from the VisualDCS sibling; the **lowest** authority — "can only suggest, never decide" |
| **Zaliznyak** | The Russian grammatical index ([samskrtam.ru/z](https://samskrtam.ru/z)); tie-breaker when Whitney's Grammar is silent |
| **Authority order** | Whitney *Grammar* (§§) > Whitney *Roots* > DCS corpus > Zaliznyak |
| **generic / specific / exception** | §-citation tags: regular class member / own paragraph / deviates from rule. The `exception` auto-tag is false-positive-prone on short roots |
| **Section B** | The ~131 corpus-conflict class additions of Phases 5–6 — the batch mostly reverted in Phase 8 |
| **Queues A–E** | The human-adjudication queues in [docs/DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) / [REVIEWER_GUIDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md) (kept class-adds, SUSPICIOUS PPPs, LIKELY_ERROR PPPs, exception-tag audit, …) |

---

# Part II — Maintainer appendix

## Invariants & contracts

- **Class fields are sacred.** `fold_corpus.py`, `dict_align.py`, `build_form_section_edges.py`, `token_disambiguate.py` all assert class values before/after — a stage that changes a class is a bug. All class *decisions* go through the human queues, never through pipeline runs.
- **No BOM, ever.** Emitters assert `read(3).hex() != 'efbbbf'`; write UTF-8, never `utf-8-sig`.
- **The spine mutates in place**; the committed deliverables (`crosswalk/*`, `src/reader_data.json`, `src/whitney_sections.json`, `src/dcs_freq.json`) are regenerable projections of it. `src/app_data.json` is the *other* source of truth (Track B) and is edited only by the `scripts/dcs/*` fixers, each idempotent, CRLF/BOM-preserving and self-verifying.
- **`scripts/sanskrit_util.py` is the org-canonical donor** re-exported by other repos' shims (see [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) and [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util)) — behavior changes ripple across the org; check before altering `norm`/`nfold`/`form_key` semantics. Since 14-07-2026 the **JS side consumes the same package back** via the two vendored builds (`src/vendor/`, `reader/vendor/`); to change JS-side normalization, change `sanskrit-util` itself and re-copy the builds whole — never patch the vendored files or reintroduce inline copies.
- **DCS SQL conventions**: token features are SQL `NULL` when absent (not the string `'None'`); count verbs via `upos='VERB'`.
- **Grammar text quirks**: the PDF-derived `src/wg_text.txt` uses `ç` (U+00E7) for IAST `ś` (2665 vs 2 occurrences) — builders normalize via `to_grammar_conv()`; Whitney's chapter numbers ≠ Hindu gaṇa numbers — builders use the Hindu numbering matching `app_data.json`.

## Per-script breakdown

### Live pipeline (see Part I for I/O detail)

| Script | Role | Trap notes |
|---|---|---|
| `scratch/phase0/parse_warnemyr.py` | Stage-0 spine builder | Hardcoded absolute `BASE` path; 35 `class_uncertain` flags are expected output, not errors |
| [scripts/dcs/extract_dcs.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/extract_dcs.py) | Whitney↔DCS linker + audit/worklist/participle-index emitter | The only `scripts/dcs/*` member that is a *pipeline* stage, not an editorial tool |
| [scripts/fold_corpus.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/fold_corpus.py) | Corpus freq → spine | Freq only; class-guarded |
| [scripts/token_disambiguate.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/token_disambiguate.py) | Homonym token attribution via DCS `lemma_id`s | Writes `dcs_freq_token` only for groups it can attribute reliably; the residual ~33 DCS-lumped homonym groups are a *lexical-semantic* problem — morphology tools were piloted (vidyut, ND-SWSMP) and don't help; don't re-pilot without new evidence |
| [scripts/extract_dict_roots.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/extract_dict_roots.py) + [scripts/dict_align.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dict_align.py) | MW/Apte arm | Deliberately decoupled from `emit_crosswalk.py` (they read `root_slp1` off the spine, breaking a former ordering cycle) |
| [scripts/wikisource/fetch_whitney.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/wikisource/fetch_whitney.py) | Grammar §§ ingest | stdlib `urllib` only; cache-first |
| [scripts/build_form_section_edges.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/build_form_section_edges.py) | Root→form-category→§ edges | The concordance is hand-authored — extend it in `src/form_section_concordance.json`, don't scrape |
| [scripts/emit_crosswalk.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/emit_crosswalk.py) | FAIR emitter (CSV/SQLite/TTL/CSVW) | `rdflib` optional; self-validates row counts |
| [scripts/build_reader_data.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/build_reader_data.py) | Reader dataset | Graceful DCS-absent fallback; compact separators, no BOM |
| [scripts/vidyut_paradigms.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/vidyut_paradigms.py) | vidyut-prakriya paradigm generator (display only) | Clean-root key must be taken at the **last it-lopa (rule 1.3.9) before laṭ-insertion (3.2.123)** or the num-augment (7.1.58) nasalizes idit roots (`skud→skund`); two gates (gaṇa ∈ Whitney classes + present-form corroboration) reject 168 wrong-homonym intruders; `pat` cl. 4 'rule' is absent from vidyut's Dhātupāṭha (coverage gap, not a panic) |
| [scripts/vidyut_validate_ppp.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/vidyut_validate_ppp.py) | PPP validation vs vidyut (advisory) | Parses **all** comma-separated PPP doublets from `Whitney_roots_class-PP.txt` (the spine keeps only the first — √gup `gupita, gupta` was a false mismatch); the source column is ASCII-romanized, and `WHITNEY_RESTORE` diacritic-restores only the two Grammar-confirmed single-root doublets (kṣubh §956b.4, piś §956b.5) — homonym cases (mṛ/iṣ/hā) deliberately stay ASCII and flagged |
| [scripts/build_mw_derivations.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/build_mw_derivations.py) | MW derivation oracle (read-only sidecar) | Needs `roots.csv` + csl-orig's `mw_etymology.tsv` |
| [scripts/emit_accent_rules_tsv.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/emit_accent_rules_tsv.py) | Accent-rules TSV view | JSON is the source of truth; sanity-checks rule-id uniqueness + matrix refs |
| [scripts/build_decisions_doc.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/build_decisions_doc.py) | Human-decision register assembler | Pre-pulls Grammar-§ evidence; graceful "—" fallbacks for optional inputs |
| [scripts/bundle.js](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/bundle.js) | JS bundle concatenator (Node) | Hardcoded 16-file order; missing files warn + skip, not fail |

### Editorial fixers of `src/app_data.json` (all idempotent, self-verifying)

| Script | Fix |
|---|---|
| [scripts/dcs/scan_ppp_apparatus.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/scan_ppp_apparatus.py) | Read-only enumerator of apparatus-bleed records (`--json` → machine catalog behind the worklist) |
| [scripts/dcs/fix_ppp_apparatus_bleed.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/fix_ppp_apparatus_bleed.py) | Cleans the 39 apparatus-bleed `ppp` records (adds `ppp_attestation`/`ppp_uncertain`/`ppp_note`) |
| [scripts/dcs/fix_ppp_gloss_bleed.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/fix_ppp_gloss_bleed.py) | The earlier 6 English-gloss-bleed records |
| [scripts/dcs/fix_ppp_infinitives.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/fix_ppp_infinitives.py) | Moves datival infinitives (`-e/-aye/-vane`) out of `ppp` into an `infinitives` field |
| [scripts/dcs/apply_ppp_corrections.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/apply_ppp_corrections.py) | High-confidence PPP fixes (dā `tta→dātta`; removes impossible `-tave`/`-tos`/`-dhyai`) |
| [scripts/dcs/audit_class_changes.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/audit_class_changes.py) | Diffs `classes` vs a git baseline (default `18b51b1` — the pure pre-additions state); run after any class-touching change |

### Archived / superseded (Phase 6–8 history — do not re-run against live data)

The corpus-inferred class-addition family is retained as an audit trail of the **Phase-8 revert** (2026-06-10): the present-stem heuristic hit the I/VI accent-collapse and 120 of 139 empirically-added class labels were reverted (117 collapse + 2 invalid `IV|PASS` + 1 Section-B); 19 genuinely-distinct-class additions were kept and parked in [review_queue.json](https://github.com/gasyoun/WhitneyRoots/blob/main/review_queue.json) for human adjudication. No original Whitney class was ever removed.

- [scripts/dcs/corpus_verify_classes.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/corpus_verify_classes.py) → [corpus_class_verdicts.json](https://github.com/gasyoun/WhitneyRoots/blob/main/corpus_class_verdicts.json) (the rejected method), [scripts/dcs/conflict_triage.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/conflict_triage.py), [scripts/dcs/conflict_additions.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/conflict_additions.py), [scripts/dcs/section_b_resolver.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/section_b_resolver.py), the three `apply_*_additions.py` scripts, and the PPP-review trio (`ppp_priority.py`, `ppp_review.py`, `ppp_source_validation.py`).
- [scripts/dcs/revert_collapse_additions.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/revert_collapse_additions.py) — the revert itself; [scripts/dcs/verify_iv_collapse.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/verify_iv_collapse.py) reproduces the collapse evidence (the "why" demo).
- [scripts/dcs/grammar_ref_builder.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/grammar_ref_builder.py) → [src/grammar_refs.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/grammar_refs.json) + [Whitney_Grammar_Citations.md](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_Grammar_Citations.md) — still the producer of its outputs but superseded as an active stage; its short-root false-positive problem (root `as` matches English "as" 2482× in `wg_text.txt`) is Queue D.
- **`scripts/parse_whitney.js` is dead code** — it is *not* the producer of `src/app_data.json` (wrong output path `../app_data.json`, wrong schema, CRLF-incompatible regex). Never cite it as the build step.
- Superseded analysis docs (banner-marked, history only): [candidates_for_addition.md](https://github.com/gasyoun/WhitneyRoots/blob/main/candidates_for_addition.md), [detailed_conflict_triage.md](https://github.com/gasyoun/WhitneyRoots/blob/main/detailed_conflict_triage.md), [detailed_b_analysis.md](https://github.com/gasyoun/WhitneyRoots/blob/main/detailed_b_analysis.md).

## Version bookkeeping

Two numbering systems coexist: [CHANGELOG.md](https://github.com/gasyoun/WhitneyRoots/blob/main/CHANGELOG.md) carries public **semantic versions** (1.0.0 = the pipeline + revert story; 1.1.0/1.2.0 = the accent-rule table + VedaWeb validation; 1.4.0–1.5.1 = the alternation-type authorial ingest, its homonym-smear fix, and the sanskrit-util JS re-vendor), while [.ai_state.md](https://github.com/gasyoun/WhitneyRoots/blob/main/.ai_state.md) tracks internal **Phase numbers** (the Phase-8 revert lives there and in [CLAUDE.md](https://github.com/gasyoun/WhitneyRoots/blob/main/CLAUDE.md), *not* in the changelog). Org-wide `H###` handoff ids referenced in commit messages resolve in the external [Uprava handoffs registry](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md), not in this repo.

## Known external-actor hazard

This repo has a recorded history of **mid-session external edits** (`CHANGELOG.md` changed by another actor mid-run; a PPP fix had to land from a worktree off `origin/main` because an actor was mid-flight on the branches). Before trusting the head state of a file you edited earlier, `git log` it; land risky changes from a fresh worktree.

---

## Provenance & caveats

- Authored 10-07-2026 by Fable 5 (`claude-fable-5`) under handoff [H503](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H503-Fable_WhitneyRoots_pipeline_and_app_build_manual_10.07.26.md), from a four-agent survey of the repo (pipeline, app, data provenance, gold-standard template) — see the companion metadoc [docs/BUILD_MANUAL.meta.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.meta.md) for the improvement backlog and revision history.
- Commands were transcribed from the scripts' own argparse/paths as of commit `37fb894`; if a script's flags drift, its `--help` and source win over this manual.
- **Spot-verified live 18-07-2026 (H1245, from a fresh worktree without the gitignored spine/mirror)** — six commands executed with real output: `node scripts/bundle.js` (17 modules; `git diff v3_app.js` showed only the timestamp line — the committed bundle is fresh); `python scripts/emit_accent_rules_tsv.py` (`sanity OK: 18 unique rules, 19 matrix cells all resolve, 17 lexical-exception entries`; committed TSV in sync); `python scripts/dcs/scan_ppp_apparatus.py` (`0 apparatus-bleed records`); `python scripts/dcs/audit_class_changes.py` (`Clean: no invalid labels, no Whitney Roots classes removed`); `python scripts/ingest_talmud_alternation.py` (idempotent — committed `alternation_type.csv` reproduced byte-identically, gold seed 7/7 with the recorded `tan` erratum and `svar` resolution); `python scripts/dcs/extract_dcs.py` (runs ~1 min against the VisualDCS sibling; surfaced the committed-outputs staleness documented at Stage 0b — regenerated data discarded, not committed, this being a docs-only pass). Everything needing the spine (`1885/`, stages 0–5 proper) or `pip install vidyut` was **not** re-run this pass and keeps its transcribed-from-source status.
- The `1885/` mirror and `scratch/phase0/root_spine.json` are **gitignored** — a fresh clone cannot run Stage 0 without obtaining the mirror first; everything downstream of the committed deliverables (the app, the reader, the crosswalk CSVs) works from a plain clone.

_Dr. Mārcis Gasūns_
