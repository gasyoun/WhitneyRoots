# Changelog

All notable changes to the Whitney Roots data and tooling.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).
Authority order for all linguistic decisions: **Grammar > Roots > DCS corpus > Zalizniak (tiebreaker).**

## [Unreleased]

## [1.5.0] - 2026-07-17
### Added
- **Full alternation-type classification over Whitney's 930 roots — authorial ingest (H1065).** [crosswalk/alternation_type.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type.csv): 794 roots classified from Tolchelnikov's own Приложение 1 ([talmud_appendix1.json](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/data/talmud_appendix1.json), manual 2.1.6) instead of algorithmic induction — the ISCLS-2024 paper's "unpublished" backbone turned out to be the manual's Таблица 5 types I–IV (MG's source ruling in-session). regular 711 · under-strong 71 · over-strong 12; exception rate 10.5% (paper ≈13%); 136 explicitly unclassifiable with reasons. Gold seed: 7/7 high-confidence rows reproduce, svar's "uncertain" resolved (tip II), the low-confidence tan row exposed as a tāy misattribution (erratum in the seed README). Method + validation: [ALTERNATION_TYPE_TALMUD_INGEST_2026.md](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/ALTERNATION_TYPE_TALMUD_INGEST_2026.md); inducer replaced by [scripts/ingest_talmud_alternation.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/ingest_talmud_alternation.py). Fable 5 (`claude-fable-5`).
### Added
- **Alternation-type seed (`crosswalk/alternation_type_seed.csv` + `.README.md`, 16-07-2026, Opus 4.8 `claude-opus-4-8[1m]`)** —
  per-root morphological-position × alternation-type data from Tolchelnikov & Shirobokov's *Non-Paninian
  Approach to Sanskrit Morphonology* (ISCLS 2024). **Seed only** — the ~9 roots the paper's slides
  document (kṛ, ji, bhū, vac, dhāv, tan, hiṃs, jṛmbh, svar), keyed on `whitney_no`, with the 2MP
  future-stem grade + `alternation_class` (regular/over-strong/under-strong). **NOT** the full ~820-root
  classification: that data backbone is not in the paper's slides or this repo; source it from the
  in-house authors or re-implement the paper's induction over Whitney's forms (README documents the
  prerequisite). No values fabricated.

### Changed
- **Reader + linguistics JS now delegate to `sanskrit-util` instead of carrying inline copies**
  (H922 momentum-axis track; SHARED_CODE.md §1-2 item 6). `reader/reader.js`'s inline
  `deva2iast`/`norm`/`nfold` and `src/utils/linguistics.js`'s inline `normalizeSanskrit`/
  `iastToDevanagari` now delegate to the canonical [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util)
  package (the same package `scripts/sanskrit_util.py` has re-exported on the Python side since
  its extraction) — `reader/` loads the vendored IIFE/global build
  (`reader/vendor/sanskrit-util.global.js`, `window.SanskritUtil`), `src/` loads a vendored ESM
  copy (`src/vendor/sanskrit-util.js`, byte-identical to `sanskrit-util/js/index.mjs`, saved
  `.js` not `.mjs`). Both vendored copies are re-copied whole, never hand-edited. `scripts/bundle.js`
  gained the vendor file in `FILES_ORDER` (ahead of `utils/linguistics.js`) plus a multi-line
  `export default {...}` strip (mirroring `sanskrit-util/js/build-global.mjs`'s own strip) so
  `v3_app.js` keeps regenerating cleanly. **No behavior change** — verified via (1) a Node
  parity check of every swapped function against the pre-migration implementation over 43 real
  IAST/Devanāgarī words (0 mismatches, including confirming `iastToDevanagari`'s known display
  bug is reproduced bug-for-bug, not newly introduced — see SHARED_CODE.md's
  "iast_to_devanagari is BROKEN" note), and (2) a Playwright load of `reader/index.html` (not
  Observable-based — plain static `<script>` tags, no dev-server `.mjs` gotcha) showing zero
  console errors and byte-identical analysis-panel output for both the IAST and Devanāgarī
  example passages, before vs. after. `BookIndex`'s copy of `linguistics.js` is unaffected —
  it remains a separate, un-scoped follow-up.

## [1.4.0] - 2026-07-10
### Added
- **Operator & build manual** (`docs/BUILD_MANUAL.md`, H503): end-to-end runbook for both
  halves of the repo — the Python crosswalk pipeline (spine bootstrap from the Warnemyr
  mirror through the FAIR crosswalk + reader-data emitters, with the exact command,
  inputs and outputs per stage) and the JS app (edit → `node scripts/bundle.js` → serve →
  Pages deploy). Includes a one-screen cheat-sheet, data-flow diagram, environment/sibling-repo
  prerequisites, a 16-row symptom→cause→cure table, glossary, and a maintainer appendix
  (invariants, per-script traps, the Phase-8 revert archive). Companion metadoc
  `docs/BUILD_MANUAL.meta.md` (backlog + revision history); linked from the README's new
  Documentation index. Authored by Fable 5 (`claude-fable-5`).

## [1.3.0] - 2026-07-05
### Fixed
- **`T8c·oxytone` samyaYc/anvaYc/SvityaYc exception, resolved as a rule gap** (H115):
  Whitney §407b + §409b/c + §410 (read in full, previously outside the cell's cited
  scope) show añc-compounds split into a prā́ñc-type (stem accent retained under
  contraction) and a pratyáñc-type (accent shifts to the ending under contraction,
  §410's own examples include `samīcī́`) sub-class; the missing rule was that the
  feminine declension (§407b: "accented like" the weakest-case stem) inherits the
  weakest-slot accent in ANY case/number, not just the cell's generic `weakest` slot.
  Patched `crosswalk/accent_rules.json` (new `lexical_exceptions[]` lemma_group entry)
  and re-scored `crosswalk/accent_validation.json`: `T8c·oxytone` 82.0% (77/94) →
  **100.0% (94/94)**; `R10` rollup 95.6% (366/383) → **100.0% (383/383)**. 18/19 matrix
  cells now score unconditional GO.
- **D3 G.pl split (`T4/T6·oxytone`) relabeling correction**: the 2 attested forms
  (`rathī́nām`, `vadhū́nām`) were mislabeled `ending` (`-īnā́m`, §319a) in the original
  run; both carry the acute on the ī/ū vowel itself, which is the `-ī́nām` `stem_final`
  pattern (§356) — relabeled in `crosswalk/accent_validation.json`. A wider pull to grow
  n past 2 was attempted (uncapped full-corpus search vs. the original run's
  `max_locations` browse cap) but blocked mid-run by a `vedaweb.uni-koeln.de` outage
  (logged in `Uprava/SERVER_OUTAGES.md`); n remains 2, split still unresolved.

## [1.2.0] - 2026-07-03
### Added
- **Accent-axis validation results** (`crosswalk/accent_validation.json` +
  `docs/ACCENT_VALIDATION_REPORT.md`): scored the 18-rule/19-cell Whitney accent-in-declension
  table against attested Rig-Veda accents from VedaWeb 2.0 (CC BY 4.0) + Casaretto et al.
  (2025), joined on PWG `key2` udātta positions. **17 of 19 matrix cells GO (≥90% position
  accuracy), 1 GO-with-exceptions (T8c·oxytone, 82%, driven by the `samyaYc` lemma), 2
  measurement-only (thin evidence, 0-1 attested lemmas), 0 NO-GO.** D3 empirical split
  (G.pl `-īnā́m` vs `-ī́nām`) measured at 2/2 `ending` — too thin to resolve Whitney's own
  §319a/§356 self-contradiction, flagged for a wider pull. Executed per
  `docs/ACCENT_VALIDATION_SPEC.md` by Sonnet 5 (`claude-sonnet-5`); fixed a case/number
  override-lookup bug in the scoring pipeline mid-run (9 of 19 cells had `G.pl`/`N.A.du.n`
  overrides silently falling back to the generic slot rule) and re-scored all 19 cells from
  the cached VedaWeb data.

## [1.1.0] - 2026-07-02
### Added
- **Zaliznyak accent-axis rule table** (`crosswalk/accent_rules.json` + flat
  `crosswalk/accent_rules.tsv` via `scripts/emit_accent_rules_tsv.py`): Whitney's
  accent-in-declension prose (§§314–319 + per-class §§350/372/390/423/446, with §§311/316/
  348–356/361/371–373/389–391/421–427/444–448 context) encoded as 18 formal rules, a 19-cell
  (stem-class × accent-position) → per-case accent matrix, and a 16-entry lexical-exception
  registry. Every interpretive cell records the decision AND the rejected alternative (D1–D11),
  including Whitney's own §319a-vs-§320/§356 contradiction on derivative ī-stem gen. plurals
  (encoded as a per-lemma variant cell). Encoded by Fable 5 (`claude-fable-5`), 2026-07-02.
- **Validation spec** (`docs/ACCENT_VALIDATION_SPEC.md`): Sonnet-runnable brief scoring the
  rule table against attested accented Rig-Veda forms via VedaWeb 2.0 (CC BY 4.0), joined on
  PWG `key2` udātta positions (`headword_index.tsv`). Advisory-only guardrails baked in.

## [1.0.0] - 2026-06-13
### Added
- **Whitney Grammar §-citations for all 935 roots.**
  `scripts/dcs/grammar_ref_builder.py` extracts every Grammar §-reference for each root from
  the Grammar PDF (cached as `src/wg_text.txt`), classifies each as *generic* (regular class
  member), *specific* (own paragraph), or *exception* (deviates from the rule), and writes:
  - `Whitney_Grammar_Citations.md` — human-readable §-table (935 rows).
  - `src/grammar_refs.json` — machine-readable per-root citations + snippets.
  - a `grammar_ref` field on each `app_data.json` entry.
- **DCS corpus verification** (`scripts/dcs/corpus_verify_classes.py`) — present-stem signal per
  root vs. Whitney class; verdicts in `corpus_class_verdicts.json`.
- **PPP source validation** (`scripts/dcs/ppp_source_validation.py`,
  `ppp_source_validation.md`, `PPP_CORRECTION_PLAN.md`) — every Whitney PPP checked against
  381k corpus forms and classified ATTESTED / LIKELY_ERROR / SUSPICIOUS / PLAUSIBLE_GAP.
- **Bilingual reviewer guide** (`REVIEWER_GUIDE.md`, EN + RU) with a per-item algorithm and
  five prioritized review queues.
- `review_queue.json` — the 19 class additions kept pending human + Zalizniak review.

### Fixed
- **PPP data-quality corrections** (`scripts/dcs/apply_ppp_corrections.py`):
  - `dā` (349/350/351): partial stem `tta` → full **`dātta`**.
  - Removed 12 morphologically impossible PPP forms (`vastave`, `saktave`, `ratave`,
    `tamitos`, `ksaradhyai`, …) — `-tave`/`-tos`/`-dhyai` are infinitive/sandhi fragments,
    not participles.

### Changed / Reverted — **important**
- **Reverted 120 of 139 automated verb-class additions.** A critical review
  (`scripts/dcs/revert_collapse_additions.py`) established that the corpus present-stem
  heuristic **cannot distinguish class I from class VI** (they differ only by accent, which the
  DCS forms lack). The pipeline had therefore added a spurious complementary class to ~117
  thematic roots, plus 2 invalid `IV|PASS` labels leaked from the script's ambiguity marker.
  - 117 I/VI accent-collapse additions → reverted to the pure Whitney Roots class set.
  - 2 invalid `IV|PASS` labels (`rā` 635/636) → removed.
  - 1 Section-B `yam +VI` → reverted (same I/VI artifact).
  - **No Whitney Roots class was ever removed** — only corpus-added classes were withdrawn.
  - 19 additions that add a *genuinely distinct* class (III/IV/VII/…) were **kept but flagged**
    in `review_queue.json` for Grammar + Zalizniak adjudication.

### Known limitations / methodology notes
- The DCS corpus is unaccented; class **I vs VI** and **IV vs passive (yá-stem)** are not
  decidable from surface present-stems alone. Treat the corpus signal as a *prompt to look*,
  never as proof. See `REVIEWER_GUIDE.md` → "How to tell class I from class VI."
- Short roots (`as`, `i`, `ṛ`…) match English words and stray text in the Grammar extract,
  so auto-detected `specific`/`exception` tags for them can be false (Queue D).

### Superseded
- `detailed_conflict_triage.md` and `candidates_for_addition.md` describe the pre-revert
  proposal set and are retained for history only; the reviewer guide supersedes them.
