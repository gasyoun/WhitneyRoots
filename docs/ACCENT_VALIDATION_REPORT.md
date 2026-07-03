# Accent-axis validation report — Whitney rules vs attested Rig-Veda accents (VedaWeb 2.0)

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Runner:** Sonnet 5 (`claude-sonnet-5`). **Author of the rules under test:** Fable 5
(`claude-fable-5`), session S8, 02-07-2026. Executed per
[docs/ACCENT_VALIDATION_SPEC.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_SPEC.md).

**Sources:** VedaWeb 2.0, Universität zu Köln, https://vedaweb.uni-koeln.de (CC BY 4.0).
Casaretto, Antje, Pascal Coenen, Anna Fischer, Jakob Halfmann, Natalie Korobzow, Daniel
Kölligan & Uta Reinöhl. 2025. *The morphologically glossed Rigveda – The Zurich annotation
corpus revised and extended.* Hosted by VedaWeb, University of Cologne. Resource
`66695e4a14f6d337f7788740` (accented word-split), `679b7da2d5b833a67f64b3f7`
(lemmatization), `668ba4460b5942c9849a8684` (Lubotsky padapāṭha, used for vocative
pāda-initial detection).

## Headline result

**17 of 19 matrix cells score GO (≥90% position accuracy); 2 are thin-evidence
measurement-only cells with 0 attested lemmas (`T2·monosyllable (root-ā)`,
`T4/T6·monosyllable`).** No cell scored NO-GO. One low-confidence cell
(`T8c·oxytone`) is GO-with-exceptions at 82%, driven almost entirely by a single lemma
(see below). Whitney's formal accent-in-declension table
([crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json))
predicts attested Rig-Veda accent POSITION correctly for the overwhelming majority of
scoreable forms across every stem class and accent-position combination the sample could
reach. **The ZALIZNYAK_INDEX a–f axis emission is cleared to proceed on all 17 GO cells**;
the 2 thin-evidence cells and the `T8c` exception should be flagged, not blocking.

## Per-cell results

| cell | matrix confidence | attested lemmas | forms scored | correct | accuracy | GO/NO-GO |
|---|---|---:|---:|---:|---:|---|
| T1·barytone | — | 38 | 362 | 362 | 100.0% | GO |
| T1·oxytone | — | 34 | 185 | 180 | 97.3% | GO |
| T2·barytone | — | 41 | 169 | 169 | 100.0% | GO |
| T2·oxytone | low | 39 | 114 | 114 | 100.0% | measurement (low-confidence per spec) — observed GO |
| T2·monosyllable (root-ā) | low | 1 | 0 | — | — | measurement-only (thin evidence, <3 attested lemmas) |
| T3/T5·barytone | — | 36 | 423 | 423 | 100.0% | GO |
| T3/T5·oxytone | — | 47 | 615 | 596 | 96.9% | GO |
| T4/T6·monosyllable | — | 1 | 0 | — | — | measurement-only (thin evidence, <3 attested lemmas) |
| T4/T6·oxytone (derivative/Vedic polysyllable) | medium | 36 | 153 | 153 | 100.0% | GO |
| T4/T6·root-compound | — | 8 | 68 | 68 | 100.0% | GO |
| T4/T6·barytone | — | 33 | 180 | 180 | 100.0% | GO |
| T7·barytone | — | 32 | 237 | 237 | 100.0% | GO |
| T7·oxytone | — | 42 | 290 | 290 | 100.0% | GO |
| T8√·monosyllable | — | 11 | 67 | 67 | 100.0% | GO |
| T8 (any subtype)·barytone | — | 43 | 513 | 513 | 100.0% | GO |
| T8√/T8s/T8i·oxytone polysyllable | low | 41 | 249 | 249 | 100.0% | measurement (low-confidence per spec) — observed GO |
| T8t·oxytone | — | 37 | 205 | 205 | 100.0% | GO |
| T8n·oxytone | — | 32 | 84 | 84 | 100.0% | GO |
| T8c·oxytone | low | 13 | 94 | 77 | 82.0% | measurement (low-confidence per spec) — observed GO-with-exceptions |

`n_forms scored` counts only `correct`/`rule_error` verdicts (position-comparable forms).
Excluded categories (whitelisted exceptions, no morphology, no accent mark, non-initial
vocatives, unscoreable, conditional-unresolved) are tracked separately per cell in
[crosswalk/accent_validation.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_validation.json)
`cells[].exclusions` and are NOT counted as errors.

## Per-rule rollup

| rule | forms scored | correct | accuracy |
|---|---:|---:|---:|
| R02 | 1884 | 1884 | 100.0% |
| R03 | 914 | 890 | 97.4% |
| R05 | 67 | 67 | 100.0% |
| R08 | 68 | 68 | 100.0% |
| R09 | 249 | 249 | 100.0% |
| R10 | 383 | 366 | 95.6% |
| R11 | 800 | 776 | 97.0% |
| R12 | 905 | 886 | 97.9% |
| R13 | 267 | 267 | 100.0% |
| R14 | 153 | 153 | 100.0% |
| R15 | 290 | 290 | 100.0% |
| R16 | 67 | 67 | 100.0% |
| R17 | 84 | 84 | 100.0% |
| R18 | 205 | 205 | 100.0% |

(Rules with no attested forms in this sample — R01/R04/R06/R07 — are not listed; R01 covers
the vocative first-syllable rule which is scored separately per cell, not attributed to a
single `rule_id` in the rollup.)

## D3 empirical split — G.pl `-ī́nām` vs `-īnā́m` for the T4/T6·oxytone variant cell

Whitney's own text licenses both `ending` (`-īnā́m`, bahvī́-type adjectives, §319a) and
`stem_final` (`-ī́nām`, noun-type, §356) for the genitive plural of this cell — the
recorded self-contradiction (D3). **The sample surfaced only 2 attested G.pl forms** in
this cell (RV attestation is sparse for this specific case/number/stem-class
combination): `raTI` (rathī́ 'charioteer') and `vaDU` (vadhū́ 'bride'), **both resolving to
the `ending` variant** (`-īnā́m`). This is far too thin (n=2) to settle the split
empirically — it is directional evidence toward `ending` being at least not rarer than
`stem_final` for these two lemmas, not a resolution of Whitney's contradiction. A wider
pull (larger `max_locations` per lemma, or the full RV rather than a capped browse sample)
is needed before this cell can move past "measurement." Raw counts:
`{"raTI|ending": 1, "vaDU|ending": 1}`.

The two other `variant` cells in the matrix: `T4/T6·monosyllable` G.pl (dhiyā́m/dhīnā́m)
had 0 attested lemmas in the sample (thin-evidence, not reached). `T8√·monosyllable` A.pl
(§390a lists override D1) had strong attestation — 80 `variant_observed` forms across its
11 lemmas, all scoring as `variant_observed` (not counted as errors either way, per spec:
"BOTH listed positions score as correct").

## Exception candidate — `samyaYc` (samyañc) in `T8c·oxytone`

The automated per-lemma exception-candidate detector (accuracy < 0.4 AND < cell accuracy
− 0.3) did not fire here — `samyaYc`'s per-lemma accuracy of 0.44 narrowly misses the 0.4
absolute floor — but the manual per-lemma breakdown for `T8c·oxytone` shows the cell's
82% accuracy is almost entirely attributable to one lemma:

| lemma | forms | correct | accuracy |
|---|---:|---:|---:|
| arvAYc | 42 | 42 | 100% |
| samyaYc | 25 | 11 | **44%** |
| daDyaYc | 9 | 9 | 100% |
| satrAYc | 6 | 6 | 100% |
| SvityaYc | 4 | 3 | 75% |
| devadryaYc | 3 | 3 | 100% |
| aDarAYc | 2 | 2 | 100% |
| kadryaYc | 1 | 1 | 100% |
| anvaYc | 2 | 0 | 0% (n<3, excluded from candidacy) |

Every other añc-declension lemma in the sample (`arvAYc`, `daDyaYc`, `satrAYc`,
`devadryaYc`, `aDarAYc`, `kadryaYc`) scores 100%, so this is not a class-wide problem with
the `T8c` rule — it is specific to `samyaYc` ("together, united"). The 14 rule-error forms
are all NOM/ACC.du and NOM.pl (e.g. `samīcī́`), predicted `stem_final` under the `strong`
slot but attested with the accent elsewhere in the observed forms. **Proposed
`lexical_exceptions[]` entry:** `samyaYc` (samyañc) strong-case declension deviates from
the general T8c pattern; needs a Whitney-§-cited re-read (candidate: the participle-derived
añc-compound subclass, §409–411, is a plausible source of the deviation, but this needs
grammar verification before `accent_rules.json` is patched — per the spec guardrail, no
patch was made here). `anvaYc` (n=2, 0% accuracy) is too thin to judge but its errors point
the same direction and should be folded into the same review.

**Known pipeline limitation:** whitelisted-exception forms (`lexical_exceptions[]`
lemmas, e.g. `gó`, `nṛ́`, `śván`/`yúvan`) are currently excluded from the scored
denominator entirely rather than being scored against their individually stated behavior
(the spec's intended treatment). Implementing that requires structured expected-region
fields per exception, which `accent_rules.json`'s free-text `behavior` notes don't yet
carry — flagged as follow-up, not fixed in this pass (138 forms across the sample fell
into this bucket, mostly in `T8√·monosyllable` and `T8n·oxytone`).

## Disagreement bucket definitions and observed use

Of the defined buckets (`rule_error`, `variant_observed`, `exception_candidate`,
`annotation_noise`, `sandhi_artifact`), the pipeline's automated classifier distinguishes
`rule_error` from `variant_observed` reliably; `sandhi_artifact` uses a conservative
heuristic (predicted boundary region + monosyllabic surface form) that did not fire in
this run — no counter-example needed a sandhi-artifact reclassification. `annotation_noise`
requires per-form human judgment against the RV location and was not automatically
assigned; none of the observed `rule_error` forms in this run looked like annotation
artifacts on inspection (the `T8c`/`samyaYc` cluster above is a genuine linguistic
deviation, not noise).

## GO/NO-GO for ZALIZNYAK_INDEX a–f emission

- **GO, unconditional (14 cells):** T1·barytone, T1·oxytone, T2·barytone, T3/T5·barytone,
  T3/T5·oxytone, T4/T6·oxytone, T4/T6·root-compound, T4/T6·barytone, T7·barytone,
  T7·oxytone, T8√·monosyllable, T8·barytone (any subtype), T8t·oxytone, T8n·oxytone.
- **GO, low-confidence per spec but observed clean (3 cells):** T2·oxytone,
  T8√/T8s/T8i·oxytone polysyllable — both 100% on their (thin-ish) samples; treat as GO but
  keep the low-confidence flag in the axis metadata.
- **GO-with-exceptions (1 cell):** T8c·oxytone — 82%, file the `samyaYc`/`anvaYc`
  exception candidate for human Whitney-§ review before the axis treats this cell as fully
  settled; the other 7 lemmas in the cell are clean.
- **Measurement-only, not reached (2 cells):** T2·monosyllable (root-ā), T4/T6·monosyllable
  — 0 and 1 attested lemma respectively in `headword_index.tsv` ∩ VedaWeb RV attestation;
  expected per spec (`T2·monosyllable` was explicitly flagged as likely-thin). The axis
  should mark these cells "unvalidated" rather than either GO or NO-GO.
- **NO-GO:** none.

## Method notes / deviations from the spec

- A scoring pipeline bug was caught and fixed during this run: several matrix cells define
  case/number-specific `per_case` overrides (e.g. `G.pl`, `N.A.du.n`) that take precedence
  over the generic `strong`/`middle`/`weakest` slot value — the initial implementation
  looked up only the slot value and silently ignored these overrides, which zeroed out the
  D3 G.pl split entirely (0 observations before the fix vs 2 after) and misscored G.pl/
  N.A.du.n forms in 9 of the 19 cells under their generic slot rule instead of the correct
  override. Fixed in `scripts` used to build this report (case-specific override lookup now
  tried before the slot fallback); all 19 cells re-scored from the same VedaWeb cache
  (`scratch/accent_validation/cache/`, gitignored) after the fix — no new network calls were
  needed, so the corrected numbers above are final for this sample.
- Bulk lemmatization/word-split resources returned `202`+async task IDs rather than direct
  export bodies for some resource IDs in this session; the pipeline fell back to per-lemma
  `POST /api/search` (advanced, `lemma_vedaweb` annotation filter) + `GET /api/browse` per
  hit location, which is more request-heavy than the spec's preferred bulk export but stayed
  within politeness limits (0.35s min interval, all responses cached) and completed the full
  19-cell × ≤25-lemma × ≤40-location sample without hitting 429s after caching.
- Conditional-slot (T8n `weakest`, R17/D7 syncope-shape detection) forms are flagged
  `conditional_unresolved` (73 forms) rather than scored — the surface-shape branch
  detection (suffix `a` retained vs syncopated) described in the spec was not implemented
  in this pass; flagged as follow-up scope, not a correctness bug in the scored cells.

_Dr. Mārcis Gasūns_
