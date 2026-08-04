# Changelog

All notable changes to the Whitney Roots data and tooling.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).
Authority order for all linguistic decisions: **Grammar > Roots > DCS corpus > Zalizniak (tiebreaker).**

## [Unreleased]

## [1.6.0] - 2026-07-31
### Added
- **Queue C/D/E agent-verdict pre-resolve** (H1686, 28-07-2026, Sonnet 5 `claude-sonnet-5`):
  [`scripts/dcs/queue_cde_agent_verdicts.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dcs/queue_cde_agent_verdicts.py)
  reads the H975 candidate-prefill files (`docs/queue_candidates/queue_{c,d,e}.json`) plus
  live `src/app_data.json`, `src/grammar_refs.json`, `src/wg_text.txt`, and the
  SanskritLexicography `SCH-accents-IAST-20247.txt` accented headword list, and writes a
  cited agent verdict for every one of the 295 pending rows across queue C (76 malformed-PPP),
  D (101 grammar-exception tags), and E (118 reverted I/VI pairs) — see
  `docs/queue_verdicts/SUMMARY.json` and the per-queue `queue_{c,d,e}_verdicts.json` /
  `queue_{c,d,e}_human_residue.md`. 144/295 resolved by agent verdict (already-fixed by a
  prior pass, a classifier parse artifact, a cited Whitney infinitive/gerund-bleed pattern,
  a literal grammar-text citation, a confirmed exception citation, a contamination-cleared
  false tag, or zero accented-source citability); 151/295 remain genuine human residue.
  Read-only — no write to `app_data.json`/`grammar_refs.json`/`review_queue.json` (gated on
  the human residue vote per [H1686](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1686-Sonnet_WhitneyRoots_queues-cde-pattern-preresolve_26.07.26.md)'s DoD). Mandate: [VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md).
- **Homonym token-attribution ceiling report** (H1747, 27-07-2026, Grok 4.5): crosswalk/gaps_s4_homonym_ceiling_report.json — 26 reliable / 46 unreliable (38 DCS single-lemma_id lumps).


## [1.5.2] - 2026-07-18

### Changed
- **`docs/BUILD_MANUAL.md` estate refresh (H1245, 18-07-2026, Fable 5 `claude-fable-5`).**
  Drift-refresh against the 8 commits since 12-07 (new branch-track row for
  [`scripts/ingest_talmud_alternation.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/ingest_talmud_alternation.py);
  Track B rewritten for the sanskrit-util re-vendor; bundle is 17 modules; Stage 0b
  committed-outputs-lag-inputs warning with measured verdict drift; version bookkeeping to
  1.5.1) + six commands spot-run with real output recorded in the manual and in
  [`docs/BUILD_MANUAL.meta.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.meta.md)'s
  new `LAST_VERIFIED` block. Consolidation: `Whitney_Transition_Runbook.md` (empty stub)
  now a pointer to the manual; `PPP_CORRECTION_PLAN.md` carries a historical banner
  (apparatus-bleed arm measured drained — scanner reports 0 records). Metadoc backlog
  reconciled; item 8 (refresh stale `extract_dcs.py` projections) added.

## [1.5.1] - 2026-07-17
### Fixed
- **`alternation_type.csv` asserted the author's Тип for 16 roots he never classified — homonym smear (H1065).** v1.5.0's ingest re-joined [`talmud_appendix1.json`](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/data/talmud_appendix1.json) against [`roots.csv`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv) itself, binding an entry whenever its Whitney spelling was unique **without checking the homonym the author had indexed**. One authorial entry therefore smeared across several of Whitney's homonyms — 15 entries onto 31 records — every row still labelled `grade_confidence=authorial`: the author wrote «2 iṣ» and it was asserted of both `iṣ¹` and `iṣ²`; his single «1 śṛ» was asserted of `śṛ¹`, `śṛ²` **and** `śṛ³`. Also affected `paś²` (DCS rank 24), `pat²` (38), `stu²` (62), `vṛ²` (65), `rudh¹` (184), `tan²` (229). Same shape as the Warnemyr union-smear ([FINDINGS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)). **Fixed by retiring this repo's duplicate join**: [`scripts/ingest_talmud_alternation.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/ingest_talmud_alternation.py) now reads the one canonical Приложение-1 × Whitney join, [`whitney_talmud.json`](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/data/whitney_talmud.json) ([SanskritGrammar PRs #348](https://github.com/gasyoun/SanskritGrammar/pull/348), [#352](https://github.com/gasyoun/SanskritGrammar/pull/352), [#353](https://github.com/gasyoun/SanskritGrammar/pull/353), [#354](https://github.com/gasyoun/SanskritGrammar/pull/354)), which abstains on homonym divergence and carries its own audit trail (`talmud_root`/`talmud_ref`/`talmud_match`). Classified **794 → 787**, homonym smears **15 → 0**, **0** tip-value disagreements on roots classified by both; 15 over-assertions withdrawn, 8 spelling-alt recoveries gained (`gach`, DCS rank 5, keeps its Тип). Exception rate **unchanged at 10.5%** — the paper-level finding never depended on the defect. Gold seed still 7/7 high-confidence + `svar` resolved + the `tan`/`tāy` erratum. 19 unbound roots are homonym divergences parked for Tolchelnikov's ruling. (Opus 4.8 `claude-opus-4-8`)

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
