# WhitneyRoots

_Created: 23-04-2026 · Last updated: 11-07-2026_

> **Reinventing [samskrtam.ru/whitney-roots/roots.html](http://samskrtam.ru/whitney-roots/roots.html)**
>
> 📂 **GitHub Repository:** [https://github.com/gasyoun/WhitneyRoots](https://github.com/gasyoun/WhitneyRoots)
> 🌐 **Live Website:** [https://gasyoun.github.io/WhitneyRoots/](https://gasyoun.github.io/WhitneyRoots/)
> 📚 **Zaliznyak Index:** [https://samskrtam.ru/z](https://samskrtam.ru/z)

## About

**WhitneyRoots** is an open-source initiative dedicated to digitizing, structuring, and reinventing the digital representation of William Dwight Whitney's seminal work: *The Roots, Verb-forms and Primary Derivatives of the Sanskrit Language*.

By migrating the data from legacy HTML formats into clean, structured Markdown and text files, this project makes Whitney's linguistic data highly accessible for modern Sanskrit computational linguistics, natural language processing (NLP), and general research. Beyond the raw text it builds a **root crosswalk** — a per-root join of Whitney against Monier-Williams, Apte, and the Digital Corpus of Sanskrit (DCS) — and ships a self-contained web app for exploring it.

> **Not to be confused with [`csl-whitroot`](https://github.com/sanskrit-lexicon/csl-whitroot).** That sibling repo is a scanned-book *display* of Whitney's Roots (page images + a reader interface) in the Cologne `sanskrit-lexicon` org. **This** repo (`gasyoun/WhitneyRoots`) is the structured-data + crosswalk + interactive-app workspace; the two are complementary, not duplicates.

## Documentation

* [`docs/BUILD_MANUAL.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.md) — **the operator & build manual**: regenerate every derived file, run the Python crosswalk pipeline end-to-end, build/serve/deploy the JS app, plus a symptom→cause→cure table and maintainer appendix. Start here to run the repo.
* [`DESIGN.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/DESIGN.md) — data model: schema, layers, authority order.
* [`REVIEWER_GUIDE.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/REVIEWER_GUIDE.md) + [`docs/DECISIONS_NEEDED.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) — human adjudication of root-class and PPP questions.
* [`CLAUDE.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/CLAUDE.md) — conventions for AI coding sessions.

## Repository Structure

The repository contains processed data files, source code, and structured Markdown exports.

### 📖 Whitney Data Files

* [`Whitney-linked-2026.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney-linked-2026.md) — Linked Markdown representation of Whitney's roots.
* [`Whitney-numbered-2026.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney-numbered-2026.md) — Sequentially numbered indexing of the roots.
* [`Whitney-paragraphs-2026.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney-paragraphs-2026.md) — Paragraph-based formatting of the root data.
* [`Whitney_roots_class-PP.txt`](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_roots_class-PP.txt) — Text data categorizing the roots by their verb class.
* [`Whitney_sopasarga_PP.txt`](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney_sopasarga_PP.txt) — Data pertaining to roots with *upasargas* (verbal prefixes).

### 📚 Monier-Williams Supplemental Data

* [`MW_PP-purva_vs_uttara.txt`](https://github.com/gasyoun/WhitneyRoots/blob/main/MW_PP-purva_vs_uttara.txt) — Data analyzing *pūrva* (prior) vs. *uttara* (subsequent) members in Monier-Williams.
* [`MW_compounds_12610.txt`](https://github.com/gasyoun/WhitneyRoots/blob/main/MW_compounds_12610.txt) — A dataset of 12,610 compounds extracted from the Monier-Williams Sanskrit–English Dictionary.

### 🔗 Root Crosswalk (data spine)

The [`crosswalk/`](https://github.com/gasyoun/WhitneyRoots/tree/main/crosswalk) directory holds the machine-built join tables that link Whitney's roots to the other dictionaries and to the DCS corpus:

* [`crosswalk/roots.csv`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv) — the canonical **930-root** crosswalk (one row per Whitney root/homonym) with MW, Apte, DCS-frequency, PPP, and Whitney-grammar section columns; also mirrored as [`roots.sqlite`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.sqlite) and [`roots.ttl`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.ttl).
* [`scripts/root_triangulation.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/root_triangulation.py) — the canonical **MW↔Whitney↔DCS root-triangulation join** (`triangulate()`), registered org-wide as [`SHARED_CODE.md` §17](https://github.com/gasyoun/SHARED_CODE.md); it locks the MW-coverage stat at **809 of the 935-root hub** attested in MW. Downstream consumer: [`MWS/root_crosswalk/`](https://github.com/sanskrit-lexicon/MWS). This is distinct from the per-homonym [`scripts/dict_align.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/dict_align.py) alignment and does not supersede it.

### 💻 Interactive Web Application

The project features a state-driven web interface for exploring Whitney's roots:

* **Lexicon Explorer** — search 935 roots with diacritic-aware normalization.
* **Grammar Insights** — view Verb Classes (Ganas) and Past Passive Participle (PPP) forms.
* **Interactive Quiz** — test your knowledge of roots and meanings.
* **Prefix suggestions** — heuristic *upasarga* combination hints.

Source layout:

* [`index.html`](https://github.com/gasyoun/WhitneyRoots/blob/main/index.html) — application entry point.
* [`index.css`](https://github.com/gasyoun/WhitneyRoots/blob/main/index.css) — dark-mode design system.
* [`v3_app.js`](https://github.com/gasyoun/WhitneyRoots/blob/main/v3_app.js) — compiled production bundle.
* [`src/`](https://github.com/gasyoun/WhitneyRoots/tree/main/src) — modular source code:
  * [`src/core/`](https://github.com/gasyoun/WhitneyRoots/tree/main/src/core) — state, routing, search, and analytics logic.
  * [`src/renderers/`](https://github.com/gasyoun/WhitneyRoots/tree/main/src/renderers) — functional UI components.
  * [`src/utils/`](https://github.com/gasyoun/WhitneyRoots/tree/main/src/utils) — Sanskrit-linguistics and DOM utilities.
  * [`src/app_data.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/src/app_data.json) — the 935-root lexicon the front end reads (pre-joined from the crosswalk).

### 🗂️ Tolchelnikov Directory

The [`Tolchelnikov/`](https://github.com/gasyoun/WhitneyRoots/tree/main/Tolchelnikov) directory contains educational resources and linguistic guides authored by I.E. Tolchelnikov, particularly the "Guide to Sanskrit Morphonology" (Руководство по санскритской морфонологии) and its accompanying exercises:

* **Guide to Sanskrit Morphonology (v. 2.1.6):**
  * [`Talmud-2.1.6.docx`](https://github.com/gasyoun/WhitneyRoots/blob/main/Tolchelnikov/Talmud-2.1.6.docx) — the original Word document covering the core theory, alternations (смысл ⇔ текст), reduplication, and general sandhi.
  * [`Talmud-2.1.6_raw.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Tolchelnikov/Talmud-2.1.6_raw.md) — the raw Markdown export of the guide.
  * [`Talmud-2.1.6_pipe.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Tolchelnikov/Talmud-2.1.6_pipe.md) — the processed Markdown version with table piping and structured formatting.
* **Morphonology Exercises (Uroky):**
  * [`Talmud-uroky.docx`](https://github.com/gasyoun/WhitneyRoots/blob/main/Tolchelnikov/Talmud-uroky.docx) — the original Word document containing practical exercises for identifying morphophonemic alternations, elements, and roots.
  * [`Talmud-uroky_raw.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Tolchelnikov/Talmud-uroky_raw.md) — the raw Markdown export of the exercises.
  * [`Talmud-uroky_pipe.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Tolchelnikov/Talmud-uroky_pipe.md) — the processed Markdown version of the exercises.

## Example lookup

The MW↔Whitney crosswalk in [`crosswalk/roots.csv`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/roots.csv) is the data spine behind the site and the Python pipeline. A real row — Whitney root `#2`, the verbal root **akṣ** ("attain"), class I, homonym 1:

```csv
whitney_no,root_iast,root_slp1,homonym,class,...,mw_id,apte_id,senses,section_refs
2,akṣ,akz,1,I,...,423,117,"to reach, RV. x, 22, 11 / To reach.",present_participle:583-584|present_a:733-750|passive_present:768-774|perfect:781-823|...
```

Read as a lookup: root **akṣ** (SLP1 `akz`) maps to Monier-Williams entry `mw_id=423` and Apte entry `apte_id=117`, is attested 4× in the DCS corpus (`dcs_freq` column), and its inflected forms are cited at Whitney *Sanskrit Grammar* §§733–750 (present class), §768–774 (passive), and §781–823 (perfect) — the same `section_refs` also served to the front-end's "Grammar Insights" panel via [`src/app_data.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/src/app_data.json), where the same root appears pre-joined as:

```json
{
  "id": "2",
  "root": "1 akṣ",
  "meaning": "attain",
  "classes": ["I"],
  "ppp": ["asta"],
  "grammar_ref": { "sections": ["§734"], "type": "generic" }
}
```

Query it yourself: `grep ",akz," crosswalk/roots.csv` or open [`Whitney-numbered-2026.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/Whitney-numbered-2026.md) at entry 2.

### RU root-gloss layer (candidate, machine-derived)

[`crosswalk/ru_root_glosses.tsv`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/ru_root_glosses.tsv), built by [`scripts/build_ru_root_glosses.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/build_ru_root_glosses.py), joins each of the 930 crosswalk roots against the sibling [SanskritRussian](https://github.com/gasyoun/SanskritRussian) repo's `root_glossary.jsonl` (corpus_lexicon Sa→Ru alignments, 2,021 roots) on the exact `root_slp1` key — both sides use the same length-preserving SLP1 encoding, so the join needs no lemma-hop or NFD normalization. For each root it records the top ≤3 corpus-attested RU glosses ranked by alignment count (`gloss_ru_1..3` / `count_1..3`), plus `root_freq_n` / `root_n_forms` / `homonym_shared`.

**Coverage: 666/930 roots (71.6%) have ≥1 corpus-attested RU gloss.** Residue: 264 roots absent from `corpus_lexicon`, 53 present but low-attestation (`root_freq_n` < 3). This is a **candidate layer only** — machine-derived and unreviewed, corpus-attested-only by construction (no LLM-invented glosses); gaps stay gaps. Promotion into any human-reviewed artifact (e.g. `src/app_data.json`) is a separate, human-gated step. Regenerate with:

```sh
python scripts/build_ru_root_glosses.py
```

## Contributing

Contributions, corrections, and enhancements to the parsing scripts or text datasets are welcome. Feel free to open an issue or submit a pull request if you have ideas on how to further improve the data structure or presentation.

## License

This project is open-source and released under the [Apache License 2.0](https://github.com/gasyoun/WhitneyRoots/blob/main/LICENSE).

_Dr. Mārcis Gasūns_
