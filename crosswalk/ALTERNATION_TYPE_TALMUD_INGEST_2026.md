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
| Classified from Приложение 1 | **794 (85.4%)** — tip I 436 · II 275 · III 71 · IV 12 |
| `alternation_class` | regular 711 · under-strong 71 · over-strong 12 |
| Exception rate (under+over) | **10.5%** — goal window 8–18%; paper's own figure ~110/820 ≈ 13% |
| Unclassifiable | 136 (14.6%, stop-gate was 30%): 125 `no_appendix1_entry` + 11 `ambiguous_conflicting` |
| Match kinds | 679 unique spelling · 101 spelling+homonym · 14 ambiguous-but-same-tip |

Generated deterministically by
[scripts/ingest_talmud_alternation.py](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/ingest_talmud_alternation.py);
join on the appendix's `whitney_spellings` + homonym number against `roots.csv`.

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
2. The 125 `no_appendix1_entry` roots are Whitney entries outside the manual's 745-root
   catalog (mostly rare/secondary roots); they are explicitly `unclassifiable`, never guessed.
3. 11 `ambiguous_conflicting` spellings match multiple appendix entries with different
   types and no homonym-number resolution — listed in the CSV with reasons.

_Fable 5 (`claude-fable-5`), H1065, per MG's authorization on the Opus-tier row; source
ruling per MG in-session 17-07-2026 (samskrtam.ru/z data is older than the manual — the
Talmud file is the source of truth)._

_Dr. Mārcis Gasūns_
