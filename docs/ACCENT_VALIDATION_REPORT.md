# Accent-axis validation report — Whitney rules vs attested Rig-Veda accents (VedaWeb 2.0)

_Created: 03-07-2026 · Last updated: 26-08-2026_

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

**18 of 19 matrix cells score GO (≥90% position accuracy); 2 are thin-evidence
measurement-only cells with 0 attested lemmas (`T2·monosyllable (root-ā)`,
`T4/T6·monosyllable`).** No cell scored NO-GO. `T8c·oxytone` — originally
GO-with-exceptions at 82%, driven almost entirely by `samyaYc` — was resolved to a clean
100% GO by
[H115](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H115-Sonnet_WhitneyRoots_samyanc_exception_d3_split_03.07.26.md)
(05-07-2026): the "errors" were a genuine rule gap (feminine/contracted-stem forms of a
pratyáñc-type añc-compound take the weakest-slot accent, not the strong-slot value),
not lemma-level noise — see the updated exception section below. Whitney's formal
accent-in-declension table
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
| T8c·oxytone | low | 13 | 94 | 94 | 100.0% | measurement (low-confidence per spec) — observed GO (resolved by H115, was 82.0%/GO-with-exceptions) |

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
| R10 | 383 | 383 | 100.0% (was 366/95.6% before the H115 T8c fix) |
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
combination): `raTI` (rathī́ 'charioteer') and `vaDU` (vadhū́ 'bride').

**H115 correction (05-07-2026):** the original run's `observed_variant: "ending"` label
for both forms was a mislabeling, not a genuine `ending`-variant observation. Re-querying
VedaWeb directly (`POST /api/search`, advanced, resource `66695e4a14f6d337f7788740`,
`lemma_vedaweb`+`case=GEN`+`number=PL`) reproduces the exact same two RV locations
(1.11.1, 8.19.36) and forms (`rathī́nām`, `vadhū́nām`) already in the cache — so this is not
a different attestation, just a re-read of the diacritics. Both forms carry the acute on
the **ī/ū vowel itself** (ra-**thī́**-nām, va-**dhū́**-nām, `accent_syll_idx=1` of 3), which
is the `-ī́nām` **`stem_final`** pattern (§356, noun-type) — **not** the `-īnā́m` `ending`
pattern (§319a, bahvī́-type adjectives), which would require the acute on `-nām`. Both
lemmas are nouns (rathī́- 'charioteer', vadhū́- 'bride'), consistent with taking the
noun-type §356 variant rather than the bahvī́-type adjective variant. **Corrected raw
counts:** `{"raTI|stem_final": 1, "vaDU|stem_final": 1}` (previously mislabeled as
`ending`).

A wider pull to grow past n=2 (the original mandate of this section) was attempted against
the same 13 lemmas already sampled in this cell (`asU`, `raTI`, `camU`, `juhU`, `ABU`,
`vaDU`, `prasU`, `ADI`, `ApaTI`, `nAndI`, `AhU`, `uhU`, `KArI`), querying `case=GEN`+
`number=PL` directly (an uncapped full-corpus search, not a `max_locations`-limited
browse). `raTI` returned before `vedaweb.uni-koeln.de` went down mid-session (the same
flapping host documented in
[SanskritLexicography/FINDINGS.md §48](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
and [Uprava/SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md));
the remaining 12 lemmas could not be queried. **n is still 2 — the D3 split remains
unresolved (measurement-only) — but both attested points are now correctly read as
`stem_final`, not `ending`,** which is directionally the opposite lean from what the
original report claimed. Given n=2 either way, this does not settle Whitney's §319a/§356
contradiction; it only corrects the sign of the (still too-thin) existing evidence. The
outage-blocked lemma expansion is filed as a follow-up (see Definition of done /
`.ai_state.md`).

**H3555 resolution (26-08-2026, Fable 5 `claude-fable-5`): the D3 split is RESOLVED —
n grew 2 → 71.** The blocked lemma expansion was completed not through the still-WAF-blocked
API host (HTTP 418, re-probed 26-08-2026) but through the public
[VedaWebProject/vedaweb-data](https://github.com/VedaWebProject/vedaweb-data) GitHub mirror
(`rigveda/versions/zurich.xlsx`, Casaretto et al. 2025, CC BY 4.0 — the same dataset as API
resource `66695e4a14f6d337f7788740`): a full-corpus census of all 2,159 Rigveda gen.pl
tokens, 477 in long-ī/ū + `nām` shape, run by
[scripts/d3_genpl_probe.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/d3_genpl_probe.py).
Verdict: **§319a and §320/§356 are both correct — their scopes are disjoint**, and the
recorded self-contradiction dissolves under word-class control. Oxytone derivative ī/ū-stem
*nouns* are **44/44 `stem_final`** with zero exceptions (nadī́- ×20, tanū́- ×15, rathī́- ×2,
yātujū́- ×2, ahī́-, hiraṇyavī́-, puruṣī́-, pūrvasū́-, vadhū́- ×1 each) — the n=2 lean above was
the right sign. The vacillation Whitney's §319a describes is real but lives entirely in the
devī́-declension adjective/participle class (bahvīnā́m ×2 — his own example — plus present
participles, mixed roughly 9 ending : 11 stem-final); monosyllables follow the separate
§355 rule (8/8 ending); barytones never move (62/62); máh- is the one mixed lemma (4:1).
Consequence for this repo: the D3 cell now emits `stem_final` as a **RULE** for derivative
ī/ū-stem noun lemmas (per-lemma variant reserved for the devī́-class and máh-), recorded in
[crosswalk/accent_validation.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_validation.json)
under `d3_genitive_plural_split`. Verdict of record with full per-lemma tables:
[SanskritLexicography docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/D3_GENPL_ACCENT_PROBE_26-08-2026.md);
residue [SanskritLexicography FINDINGS §587/§588](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md);
shipped via SL [PR #1895](https://github.com/gasyoun/SanskritLexicography/pull/1895).

The two other `variant` cells in the matrix: `T4/T6·monosyllable` G.pl (dhiyā́m/dhīnā́m)
had 0 attested lemmas in the sample (thin-evidence, not reached). `T8√·monosyllable` A.pl
(§390a lists override D1) had strong attestation — 80 `variant_observed` forms across its
11 lemmas, all scoring as `variant_observed` (not counted as errors either way, per spec:
"BOTH listed positions score as correct").

## Exception candidate — `samyaYc` (samyañc) in `T8c·oxytone` — RESOLVED (H115, 05-07-2026)

The automated per-lemma exception-candidate detector (accuracy < 0.4 AND < cell accuracy
− 0.3) did not fire here — `samyaYc`'s per-lemma accuracy of 0.44 narrowly misses the 0.4
absolute floor — but the manual per-lemma breakdown for `T8c·oxytone` originally showed
the cell's 82% accuracy almost entirely attributable to one lemma:

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

**Verdict: (b) — the `T8c·oxytone` rule was incomplete for a documented Whitney
sub-class, not a lexical exception limited to `samyaYc`.** Whitney §407–410 (read in full
for this pass, all previously OUTSIDE the cell's cited sections) splits añc-compounds into
two accentual sub-types:

- **§409a, prā́ñc-type** (ápāñc, ávāñc, párāñc, arvā́ñc, adharā́ñc — and, per this sample,
  satrāñc/dadhyañc/devadryañc/kadryañc pattern the same way): accent is **retained on the
  stem** even when the stem contracts to ī/ū (§410: "thus, prā́cā, arvā́cā, adharā́cas").
  These are exactly the lemmas that scored 100% in the original run.
- **§409b/c, pratyáñc-type** (pratyáñc itself, nyàñc, samyáñc, údañc, víṣvañc, anváñc):
  accent **shifts to the ending** whenever the surface form is built from the contracted
  ī/ū allomorph — §410 states this explicitly and names `pratīcā́`, `anūcás`, **`samīcī́`**
  as its own attested RV examples (samīcī́ is Whitney's own citation, not a corpus
  artifact). `samyaYc`, `anvaYc`, and `SvityaYc` are all §409b/c-type lemmas.

The missing piece was **§407b**: "the feminine is made by adding ī to the stem-form used
in the *weakest* cases, **and is accented like them**." Cross-checking every one of the
17 `T8c·oxytone` rule-error forms against `crosswalk/accent_validation.json`'s raw
per-form data confirms this exactly: all 17 (14 `samyaYc`, 2 `anvaYc`, 1 `SvityaYc`) are
feminine-gender forms built from the contracted stem (`samīcī́` NOM/ACC.du, `samīcī́ḥ`
NOM.pl, `śvitīcī́` NOM.sg, `anūcáḥ`) that the pipeline scored against the generic
`strong`/`middle`-slot `stem_final` prediction — but §407b says the feminine paradigm is
accented like the **weakest**-slot form, which for these lemmas is `ending` per §410. Every
form the pipeline *did* route to the `weakest` slot for these same three lemmas
(`samīcī́ḥ` ACC.pl, `samīcyóḥ` LOC.du, `śvitīcé` DAT.sg) already scored correct — the bug
was purely that feminine strong/middle-slot cases weren't being recognized as sharing the
weakest slot's contracted allomorph and its accent behavior.

**Patch applied**, per the spec's citation guardrail: a new `lexical_exceptions[]`
lemma_group entry ("§409b/c añc-compounds: pratyáñc-type accent-shift-on-contraction")
in [crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json),
citing §407b + §409b + §409c + §410, documenting that feminine-gender forms of this
sub-group take the weakest-slot accent regardless of case/number. The `T8c·oxytone` cell
`notes` field cross-references it. `crosswalk/accent_validation.json`'s 17 affected
`per_form_verdicts` entries were updated from `rule_error` to `correct` (each carrying a
`resolved_by` citation), and the cell/rollup summaries were recomputed: `T8c·oxytone`
94/94 = 100.0%, `R10` 383/383 = 100.0%.

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
- **GO, resolved by H115 (1 cell):** T8c·oxytone — was 82%/GO-with-exceptions, now 100%
  after the `samyaYc`/`anvaYc`/`SvityaYc` rule-gap fix (see the exception section above);
  moves into the unconditional-GO set alongside the low-confidence-but-clean group.
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
