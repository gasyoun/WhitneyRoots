# Alternation-type classification over Whitney's roots — authorial ingest from the Talmud (H1065)

_Created: 17-07-2026 · Last updated: 17-07-2026_

## What happened to the induction plan

[H1065](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1065-Opus_WhitneyRoots_alternation-type-induction-nonpaninian_16.07.26.md)
planned to *re-implement* the ISCLS-2024 Non-Paninian paper's induction (Tolchelnikov &
Shirobokov), because its per-root alternation-type backbone was "not published and not in
the repo". Per the handoff's own gate question, MG was asked first — and pointed at the
Talmud manual's own root catalog. That closed the case: **the backbone is authorial,
in-house, and already machine-parsed** —
[TolchelnikovTalmud_2026/data/talmud_appendix1.json](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/data/talmud_appendix1.json)
(Приложение 1 of manual 2.1.6, 745 roots) carries `tip` = **Таблица 5 alternation type
I–IV** per root, plus ablaut series (`ryad`), seṭ/aniṭ and pada. So this deliverable is an
**ingest + validation**, not an induction — cheaper and authoritative, exactly as the
handoff's alternative branch prescribed.

## The mapping (Таблица 5 → the paper's classes)

Таблица 5 gives each type its grade at the three morphological positions; the paper's
classes are keyed to the 2MP (guṇa-expecting) position:

| Тип | 1MP | 2MP | 3MP | `alternation_class` |
|---|---|---|---|---|
| I (полноизменяемые) | слабая | guṇa | vṛddhi | regular |
| II (неполноизменяемые) | guṇa | guṇa | vṛddhi | regular at 2MP (`mp1_deviation=guna_for_basic`) |
| III (неполноизменяемые) | слабая | **слабая** | vṛddhi | **under-strong** |
| IV (неизменяемые) | **vṛddhi** | **vṛddhi** | vṛddhi | **over-strong** |

## Results ([alternation_type.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type.csv) · [stats](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type_stats.json))

| Metric | Value |
|---|---|
| Whitney roots ([roots.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv)) | 930 |
| Classified from Приложение 1 | **787 (84.6%)** — tip I 428 · II 276 · III 71 · IV 12 |
| `alternation_class` | regular 704 · under-strong 71 · over-strong 12 |
| Exception rate (under+over) | **10.5%** — goal window 8–18%; paper's own figure ~110/820 ≈ 13% |
| Unclassifiable | 143 (15.4%, stop-gate was 30%) — all `no_authorial_binding` |
| Match kinds | 617 root-uniq · 112 ref+hom · 57 spelling-alt · 1 manualroot · 143 unbound |

Generated deterministically by
[scripts/ingest_talmud_alternation.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/ingest_talmud_alternation.py)
**over the canonical join** —
[whitney_talmud.json](https://github.com/gasyoun/SanskritGrammar/blob/main/TolchelnikovTalmud_2026/data/whitney_talmud.json)
(SanskritGrammar). This file does **not** join the catalog itself; see next section.

## Correction 17-07-2026 — the join is read, not re-derived (794 → 787)

The first cut re-joined `talmud_appendix1.json` against `roots.csv` here, binding an entry
whenever its Whitney spelling was unique — **without checking the homonym the author had
indexed**. One authorial entry then smeared across several of Whitney's homonyms: 15 entries
onto 31 records, **16 excess assertions**, each still labelled `grade_confidence=authorial`.
The author wrote «2 iṣ»; it was asserted of both `iṣ¹` and `iṣ²`. He wrote one «1 śṛ»; it was
asserted of `śṛ¹`, `śṛ²` **and** `śṛ³`. Also affected: `paś²` (DCS rank 24), `pat²` (38),
`stu²` (62), `vṛ²` (65), `rudh¹` (184), `tan²` (229). Same shape as the Warnemyr
union-smear ([FINDINGS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).

Fixed by deleting this join and reading the one canonical Приложение-1 × Whitney join, which
abstains on homonym divergence and carries its own audit trail (`talmud_root`, `talmud_ref`,
`talmud_match`). Net effect:

| | first cut | now |
|---|---:|---:|
| classified | 794 | **787** |
| authorial entries smeared across homonyms of one spelling | 15 | **0** |
| tip-value disagreements on roots classified by both | — | **0** |
| over-assertions withdrawn / recoveries gained | — | 15 / 8 |

The exception rate is unchanged at **10.5%**, so the paper-level finding never depended on
the defect. The withdrawn 15 are now `unclassifiable`; **19 of the unbound roots are homonym
divergences awaiting Tolchelnikov's ruling** (Whitney's `pā³` vs his `pā¹`/`pā²`, his
«1 paś, spaś» vs Whitney's `paś²`) — an editorial numbering question, not one induction can
settle.

**Do not "fix" a wrong Тип in this CSV** — fix the join upstream and regenerate. This file is
a projection, not a source.

## Gold-seed validation (9 paper-verified roots)

| Root | Seed class (confidence) | Talmud tip → ingested | Verdict |
|---|---|---|---|
| kṛ, ji, bhū, vac | regular (high ×4) | I → regular | ✅ 4/4 |
| dhāv | over-strong (high) | IV → over-strong | ✅ |
| hiṃs, jṛmbh | under-strong (high ×2) | III → under-strong | ✅ 2/2 |
| svar | **uncertain** (2MP grade not stated in slides) | II → regular | ✅ **resolved by the authorial data** |
| tan | over-strong (**low**; "paper OCR 'tai'; root id uncertain") | I → regular | ⚠️ **seed erratum exposed** |

**All 7 high-confidence seed rows reproduce exactly.** The single mismatch is the seed's
own flagged low-confidence row: the paper slide reads `tai`, which in Приложение 1 is the
root **tāy** (`tai`, tip II, ряд I) — a different root than tan (`tn̥`, tip I). The seed
misattributed the slide row to tan; erratum recorded in
[alternation_type_seed.README.md](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type_seed.README.md),
the seed CSV left untouched as the historical extraction record. (Residual: the slide
called the `tai` row's 2MP vṛddhi, while tip II predicts guṇa at 2MP — with the root-id
confusion this is a slide-vs-manual question for Tolchelnikov, parked, not adjudicated.)

## Honest limits

1. 2MP/3MP **grades here are type-derived** (Таблица 5), not per-form attested: the CSV
   asserts the authorial classification, not a corpus measurement. A form-level check of
   future/aorist stems (vidyut or DCS attestations) against the type-predicted grades is
   the natural v2 — it would measure how often usage deviates from the author's system.
2. The 143 `no_authorial_binding` roots are Whitney entries the canonical join bound no
   catalog entry to — mostly rare/secondary roots outside the manual's 745-root catalog,
   plus the 19 homonym divergences parked for the author. All explicitly `unclassifiable`,
   never guessed.
3. **The 2MP grade is type-derived for every root, including the 19 parked ones** — so the
   "regular 704" figure is a count of the author's *system*, not of attested usage. The v2
   form-level check in limit 1 is what would turn it into a measurement.

_Fable 5 (`claude-fable-5`), H1065, per MG's authorization on the Opus-tier row; source
ruling per MG in-session 17-07-2026 (samskrtam.ru/z data is older than the manual — the
Talmud file is the source of truth). Join re-pointed at the canonical feed + homonym-smear
correction 17-07-2026 by Opus 4.8 (`claude-opus-4-8`)._

_Dr. Mārcis Gasūns_
