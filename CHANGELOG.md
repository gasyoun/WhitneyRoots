# Changelog

All notable changes to the Whitney Roots data and tooling.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).
Authority order for all linguistic decisions: **Grammar > Roots > DCS corpus > Zalizniak (tiebreaker).**

## [Unreleased] — 2026-06-10

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
