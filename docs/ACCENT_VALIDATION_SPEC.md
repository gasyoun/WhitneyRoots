# Accent-axis validation spec — Whitney rules vs attested Rig-Veda accents (VedaWeb 2.0)

_Created: 02-07-2026 · Last updated: 02-07-2026_

**Status:** ready to run. **Runner tier:** Sonnet (state tier + exact version from the run
environment in every log/commit, e.g. "Sonnet 4.6 (`claude-sonnet-4-6`)" — never a bare tier).
**Author of the rules under test:** Fable 5 (`claude-fable-5`), session S8, 02-07-2026.

## Objective

Score the formal Whitney accent-in-declension table
[crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json)
(flat view: [crosswalk/accent_rules.tsv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.tsv))
against attested, accented Rig-Veda word-forms from VedaWeb 2.0, and report **per-rule and
per-matrix-cell accuracy**. The result decides which cells of the Zaliznyak-style accent axis
([ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md))
can be trusted, and surfaces per-lemma exception candidates.

## Inputs (all on disk / live, nothing to build first)

1. **Rules under test** —
   [crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json).
   Use `rules[]` (18 rules), `matrix[]` (19 cells), `lexical_exceptions[]` (whitelists and
   override lists), `case_slots` (incl. the **§311b neuter remap** — mandatory before scoring).
2. **Lemma pool with accent position + stem class** —
   [RussianTranslation/src/headword_index.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv)
   (columns: `k1` SLP1 headword · `hom` · `lex` · `accented` SLP1 key2 with udātta `/` ·
   `index_token` `G·T S F` · `stem_class` · `compound_members` · `irregularities`).
   Only rows whose `accented` contains `/` participate (~20.5k of the PWG key2 list carry the
   mark). `accent_position` = `oxytone` if `/` follows the LAST stem vowel, else `barytone`;
   `monosyllable` if `k1` has exactly one vowel/diphthong. The `S` letter already in
   `index_token` (`a`/`b`) encodes the same split — cross-check, prefer recomputing from `/`.
3. **Validation corpus** — **VedaWeb 2.0**, `https://vedaweb.uni-koeln.de/api`
   (FastAPI; OpenAPI at `/api/openapi.json` — consult it first; the legacy
   `/rigveda/api/search` is superseded). Probed + confirmed 2026-06-29
   ([FINDINGS.md §1](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)):
   - `POST /api/search` `{"type":"quick","q":"<lemma>"}` → hits with per-resource highlights.
     Check the OpenAPI schema for a grammar/morphology search mode (lemma + case/number
     filters); prefer it over quick-search when present.
   - **Casaretto et al. (2025) accented word-split annotation** — resource
     `66695e4a14f6d337f7788740`: udātta-marked, position-aligned per-word forms
     (e.g. RV 6.59.3 `… índrā; nú; agnī́; ávasā; ihá; vajríṇā; vayám; devā́`).
   - **Lemmatization layer** — resource `679b7da2d5b833a67f64b3f7` (same positions).
   - **Accented text (Scarlata–Widmer/Lubotsky)** — resource `66695c4b14f6d337f778873f`;
     **Lubotsky padapāṭha** — resource `668ba4460b5942c9849a8684` (use to detect pāda-initial
     position for the vocative rule).
   - **Bulk**: `GET /api/resources/{id}/export` — prefer ONE bulk export per resource over
     per-lemma searches; cache everything under `scratch/accent_validation/` (gitignored).
   - License CC BY 4.0 — cite "VedaWeb 2.0, Universität zu Köln" + the Casaretto et al. (2025)
     annotation resource in the report.
4. **Shared utilities** —
   [scripts/sanskrit_util.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/sanskrit_util.py):
   `from_slp1()` for SLP1→IAST, and reuse `form_key()`'s accent-handling logic. ⚠️ IAST accent
   pitfalls are REAL and already solved there
   ([FINDINGS.md §36](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)):
   `ś` decomposes to `s`+U+0301 (an acute that is NOT a pitch accent); the udātta on vocalic
   `ṛ́`/`ṝ́` needs a walk-back past all combining marks; never NFD+strip-Mn. Do not re-derive —
   adapt `form_key()`.

## Method

### 1. Sample

For each of the 19 `matrix[]` cells: select up to **25 lemmas** from `headword_index.tsv`
matching (stem_class, accent_position), ranked by RV attestation count (probe VedaWeb once per
lemma, or rank by hits in the bulk lemmatization export). Skip cells with <3 attested lemmas and
say so in the report (expected for `T2·monosyllable`). Exclude: compounds (`compound_members`
non-empty) except for the `T4/T6·root-compound` cell, numerals (§315a/§483), pronominals.

### 2. Collect attested forms

Per lemma, via the lemmatization layer: all RV tokens of that lemma; join each token position to
the Casaretto accented word-split for the surface accented form and its morphological annotation
(case, number, gender). Verify the annotation field names against a sample export before coding
the join. Drop tokens with no morphology or no accent mark (but see vocative handling below).

### 3. Predict

For each attested (lemma, case, number, gender):

- Map to slot via `case_slots`, applying the **neuter remap** (§311b) when gender=n.
- Find the governing matrix cell → per_case value → predicted accent REGION:
  - `stem` — the syllable bearing `/` in key2;
  - `stem_final` — last stem syllable **in whatever ablaut grade** (align by de-accented
    longest-common-prefix between stem and attested form; the graded syllable counts as stem);
  - `ending` — any syllable after the stem region;
  - `fused` — the boundary syllable (stem-final + ending coalesced) — count as correct if the
    accent sits on that syllable, whatever its tone;
  - `first_syllable` — vocatives only;
  - `conditional` (T8n weakest) — detect the surface shape first (suffix `a` retained vs
    syncopated) and apply the matching branch (R17/D7);
  - `variant` — BOTH listed positions score as correct, and the chosen one is COUNTED per
    lemma (R05/R16 A.pl via D1; R13 G.pl via D3 — this cell is a measurement target: report
    the empirical split between `-īnā́m` and `-ī́nām` by lemma type).
- **Vocatives:** score only pāda-initial ones (padapāṭha/metrical position from the Lubotsky
  resource); expect first-syllable accent (R01). Non-initial vocatives are EXCLUDED, not failed.
- **Svarita equivalence (D5):** an independent svarita on a semivowelized syllable
  (`nadyàs`-type) is the SAME position as the acute of the dissyllabic reading — score by
  position, not tone (R03, R08, R14).
- **Whitelists:** any form/lemma in `lexical_exceptions[]` scores against its OWN stated
  behavior (gó, nṛ́, śván/yúvan, the §390a A.pl lists, the §448 participle anomalies), never
  against the class rule.

### 4. Score and report

Per rule and per matrix cell: `n_forms`, `n_correct`, accuracy, plus a disagreement breakdown:

| bucket | meaning |
|---|---|
| `rule_error` | clean counter-example — Whitney encoding wrong or incomplete |
| `variant_observed` | a `variant` cell resolved one way for this lemma (not an error) |
| `exception_candidate` | one lemma consistently deviates → propose a lexical_exceptions entry |
| `annotation_noise` | accent/morphology annotation implausible (cite the RV location) |
| `sandhi_artifact` | accent moved/lost by saṁhitā sandhi — retry against the padapāṭha |

Outputs (PR to WhitneyRoots, branch + auto-merge; **never** push to main directly):

- `crosswalk/accent_validation.json` — machine-readable per-form verdicts + per-rule rollup;
- `docs/ACCENT_VALIDATION_REPORT.md` — accuracy tables, the D3 empirical split, proposed
  exception candidates, and the go/no-go per matrix cell for the ZALIZNYAK_INDEX a–f emission
  (dated header + byline per the global doc contract).

### 5. Acceptance thresholds

- **≥90 %** per high-confidence cell → cell is GO for the axis.
- **70–90 %** → GO with the misses filed as exception candidates for human review.
- **<70 %** → NO-GO; the cell's rule needs re-reading against Whitney — file the counter-examples,
  do NOT patch `accent_rules.json` without citing the § that justifies the change.
- Low-confidence cells (`T2·monosyllable`, `T8c·oxytone`, `T2·oxytone`, `T8s/T8i`) are
  measurements, not tests — report whatever they show.

## Guardrails (binding)

- **Advisory only.** Never write rule-predicted or corpus-derived accent/class into
  `src/app_data.json`, `headword_index.tsv`, the spine, or any reviewed data — the I/VI
  accent-collapse lesson. The validation output is a report.
- The `apply_*` / `corpus_verify` scripts in this repo are do-not-rerun overlay-wipers.
- Vedic-only: no predictions for unaccented (Classical) headwords.
- Be polite to the API: bulk exports over per-form queries; cache; back off on 429.
- Every log/commit states model tier + exact version per step.

_Dr. Mārcis Gasūns_
