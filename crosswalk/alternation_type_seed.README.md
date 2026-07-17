# Alternation-type seed (Non-Paninian morphonology)

_Created: 16-07-2026 · Last updated: 16-07-2026_

Seed data for a per-root **alternation-type** classification of Whitney's verbal roots, from
Tolchelnikov & Shirobokov, *A Non-Paninian Approach to Sanskrit Morphonology (Based on the works of
A. Zaliznyak)*, 7th International Sanskrit Computational Linguistics Symposium (ISCLS), 2024
(http://sanskrit.anshir.ru/). Companion to [`roots.csv`](roots.csv), keyed on `whitney_no`.

## The framework

The paper separates two orthogonal notions:

- **Morphological Position (MP)** — the grade a slot *expects*:
  - **1MP → basic** (past participle `-ta-`: `kṛta`, `bhūta`, …)
  - **2MP → guṇa** (future stem `-sya-`: `kariṣyati`, `dhāsyati`, …)
  - **3MP → vṛddhi** (4th-aorist `-s-`: `akārṣīt`, `anaiṣīt`, …)
- **Alternation type** — the grade a *specific root* actually takes at each MP. Whitney's rule-based
  account treats any deviation as an exception; the paper's headline is that **~110 of ~820 roots** are
  2MP-exceptions (future-stem grade ≠ guṇa). Reframing them by alternation type turns the exceptions into
  a finite set of classes.

`alternation_class` here summarises the **2MP (future-stem) behaviour**, the paper's clearest signal:

| class | 2MP grade | meaning |
|---|---|---|
| `regular` | guṇa | matches the rule (the ~87%) |
| `over-strong` | vṛddhi | stronger than expected (exception) |
| `under-strong` | basic | weaker than expected (exception) |

## ⚠️ Scope — this is a SEED, not the full classification

`alternation_type_seed.csv` contains **only the ~9 roots the paper's slides actually document** as worked
examples (kṛ, ji, bhū, vac, dhāv, tan, hiṃs, jṛmbh, svar). It is **not** the full ~820-root classification.

The paper is a symposium presentation; its full per-root alternation-type table (the "data backbone",
built over Whitney's *Roots, Verb-Forms and Primary Derivatives*) is **not** in the extracted slide text
and is **not** present anywhere in this repo (checked: `roots.csv`, `crosswalk/`, `Tolchelnikov/` — the
latter holds teaching material, not this dataset). Populating the full column requires one of:

1. **Source the authors' table** — Tolchelnikov & Shirobokov are in-house (advisor MG); the full
   classification, if it exists as data, should come from them rather than be re-derived or guessed.
2. **Re-implement the paper's induction** — derive alternation type per root algorithmically from
   Whitney's attested `-ta-` / `-sya-` / `-s-` forms (the paper's actual method). This is a real
   research task, not a data-entry pass — track it as a handoff if pursued.

**No values were fabricated.** OCR-garbled root names in the slides were resolved against `roots.csv`
by gloss (`uøc`→`vac`/speak, `dhau`→`dhāv`/run, `tai`→`tan`/stretch — the last flagged
`root_match_confidence: low`). `svar`'s 2MP grade is left `uncertain` because the slide does not state it.

## Columns

`whitney_no` · `root_iast` · `gloss` · `mp2_future_form` · `mp2_future_grade` · `alternation_class` ·
`mp1_ppp_form` · `mp3_aorist_form` · `root_match_confidence` · `source`.

_Dr. Mārcis Gasūns_

## Superseded by the full authorial classification (17-07-2026, H1065)

The full 930-root classification now lives at
[alternation_type.csv](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alternation_type.csv) —
ingested from the AUTHORIAL source (Talmud manual 2.1.6, Приложение 1, per MG's ruling that
the manual is newer than samskrtam.ru/z), not induced. Method + validation:
[ALTERNATION_TYPE_TALMUD_INGEST_2026.md](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/ALTERNATION_TYPE_TALMUD_INGEST_2026.md).
All 7 high-confidence seed rows reproduce; svar's "uncertain" resolves to type II (guṇa at 2MP).

**Erratum:** the seed row `whitney_no=293 tan` was a misattribution — the paper slide's
`tai` is the root **tāy** (Приложение 1: `tai`, tip II), not tan. The row is kept as the
historical extraction record; consumers should prefer alternation_type.csv.
