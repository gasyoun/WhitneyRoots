# WhitneyRoots

_Created: 23-04-2026 · Last updated: 08-07-2026_

> **Reinventing [samskrtam.ru/whitney-roots/roots.html](http://samskrtam.ru/whitney-roots/roots.html)**
> 
> 📂 **GitHub Repository:** [https://github.com/gasyoun/WhitneyRoots](https://github.com/gasyoun/WhitneyRoots)
> 🌐 **Live Website:** [https://gasyoun.github.io/WhitneyRoots/](https://gasyoun.github.io/WhitneyRoots/)
> 📚 **Zaliznyak Index:** [https://samskrtam.ru/z](https://samskrtam.ru/z)

## About

**WhitneyRoots** is an open-source initiative dedicated to digitizing, structuring, and reinventing the digital representation of William Dwight Whitney's seminal work: *The Roots, Verb-forms and Primary Derivatives of the Sanskrit Language*. 

By migrating the data from legacy HTML formats into clean, structured Markdown and text files, this project makes Whitney's linguistic data highly accessible for modern Sanskrit computational linguistics, natural language processing (NLP), and general research.

## Repository Structure

The repository contains processed data files, source code, and structured Markdown exports. Click on any file to view its contents:

### 📖 Whitney Data Files
* [`Whitney-linked-2026.md`](./Whitney-linked-2026.md) - Linked Markdown representation of Whitney's roots.
* [`Whitney-numbered-2026.md`](./Whitney-numbered-2026.md) - Sequentially numbered indexing of the roots.
* [`Whitney-paragraphs-2026.md`](./Whitney-paragraphs-2026.md) - Paragraph-based formatting of the root data.
* [`Whitney_roots_class-PP.txt`](./Whitney_roots_class-PP.txt) - Text data categorizing the roots by their verb class.
* [`Whitney_sopasarga_PP.txt`](./Whitney_sopasarga_PP.txt) - Data pertaining to roots with *upasargas* (verbal prefixes).

### 📚 Monier-Williams Supplemental Data
* [`MW_PP-purva_vs_uttara.txt`](./MW_PP-purva_vs_uttara.txt) - Data analyzing *pūrva* (prior) vs. *uttara* (subsequent) members in Monier-Williams.
* [`MW_compounds_12610.txt`](./MW_compounds_12610.txt) - A comprehensive dataset of 12,610 compounds extracted from the Monier-Williams Sanskrit-English Dictionary.

### 💻 Interactive Web Application
The project now features a high-performance, state-driven web interface for exploring Whitney's roots:
*   **Lexicon Explorer**: Search 935 roots with diacritic-aware normalization.
*   **Grammar Insights**: View Verb Classes (Ganas) and Past Passive Participle (PPP) forms.
*   **Interactive Quiz**: Test your knowledge of roots and meanings.
*   **AI-Powered Philology**: Get heuristic insights and prefix combination suggestions.
### 📁 Repository Structure
*   [`index.html`](./index.html) - Application entry point.
*   [`index.css`](./index.css) - Premium dark-mode design system.
*   [`v3_app.js`](./v3_app.js) - Compiled production bundle.
*   [`/src/`](./src/) - Modular source code:
    *   [`/core/`](./src/core/) - State, Routing, Search, and Analytics logic.
    *   [`/renderers/`](./src/renderers/) - Functional UI components.
    *   [`/utils/`](./src/utils/) - Sanskrit linguistics and DOM utilities.
*   [`claude.md`](./claude.md) - Documentation for AI coding assistants.

### 🗂️ Tolchelnikov Directory
The [`/Tolchelnikov/`](./Tolchelnikov/) directory contains specific educational resources and linguistic guides authored by I.E. Tolchelnikov, particularly the "Guide to Sanskrit Morphonology" (Руководство по санскритской морфонологии) and its accompanying exercises. Key files include:

* **Guide to Sanskrit Morphonology (v. 2.1.6):**
  * [`Talmud-2.1.6.docx`](./Tolchelnikov/Talmud-2.1.6.docx) - The original Word document covering the core theory, alternations (смысл ⇔ текст), reduplication, and general sandhi.
  * [`Talmud-2.1.6_raw.md`](./Tolchelnikov/Talmud-2.1.6_raw.md) - The raw Markdown export of the guide.
  * [`Talmud-2.1.6_pipe.md`](./Tolchelnikov/Talmud-2.1.6_pipe.md) - The processed Markdown version with table piping and structured formatting.

* **Morphonology Exercises (Uroky):**
  * [`Talmud-uroky.docx`](./Tolchelnikov/Talmud-uroky.docx) - The original Word document containing practical exercises for identifying morphophonemic alternations, elements, and roots.
  * [`Talmud-uroky_raw.md`](./Tolchelnikov/Talmud-uroky_raw.md) - The raw Markdown export of the exercises.
  * [`Talmud-uroky_pipe.md`](./Tolchelnikov/Talmud-uroky_pipe.md) - The processed Markdown version of the exercises.

## Example lookup

The MW↔Whitney crosswalk in [`crosswalk/roots.csv`](./crosswalk/roots.csv) is the
data spine behind the site and the Python pipeline. A real row — Whitney root
`#2`, the verbal root **akṣ** ("attain"), class I, homonym 1:

```csv
whitney_no,root_iast,root_slp1,homonym,class,...,mw_id,apte_id,senses,section_refs
2,akṣ,akz,1,I,...,423,117,"to reach, RV. x, 22, 11 / To reach.",present_participle:583-584|present_a:733-750|passive_present:768-774|perfect:781-823|...
```

Read as a lookup: root **akṣ** (SLP1 `akz`) maps to Monier-Williams entry
`mw_id=423` and Apte entry `apte_id=117`, is attested 4× in the DCS corpus
(`dcs_freq` column, not shown above), and its inflected forms are cited at
Whitney *Sanskrit Grammar* §§733–750 (present class), §768–774 (passive), and
§781–823 (perfect) — the exact `section_refs` also served to the front-end's
"Grammar Insights" panel via [`src/app_data.json`](./src/app_data.json), where
the same root appears pre-joined as:

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

Query it yourself: `grep ",akz," crosswalk/roots.csv` or open
`Whitney-numbered-2026.md` at entry 2.

### RU root-gloss layer (candidate, machine-derived)

[`crosswalk/ru_root_glosses.tsv`](./crosswalk/ru_root_glosses.tsv), built by
[`scripts/build_ru_root_glosses.py`](./scripts/build_ru_root_glosses.py),
joins each of the 930 crosswalk roots against the sibling
[SanskritRussian](https://github.com/gasyoun/SanskritRussian) repo's
`root_glossary.jsonl` (corpus_lexicon Sa→Ru alignments, 2,021 roots) on the
exact `root_slp1` key — both sides use the same length-preserving SLP1
encoding, so the join needs no lemma-hop or NFD normalization. For each root
it records the top ≤3 corpus-attested RU glosses ranked by alignment count
(`gloss_ru_1..3` / `count_1..3`), plus `root_freq_n` / `root_n_forms` /
`homonym_shared`.

**Coverage: 666/930 roots (71.6%) have ≥1 corpus-attested RU gloss.** Residue:
264 roots absent from `corpus_lexicon`, 53 present but low-attestation
(`root_freq_n` < 3). This is a **candidate layer only** — machine-derived and
unreviewed, corpus-attested-only by construction (no LLM-invented glosses);
gaps stay gaps. Promotion into any human-reviewed artifact (e.g.
`src/app_data.json`) is a separate, human-gated step. Regenerate with:

```sh
python scripts/build_ru_root_glosses.py
```

## Contributing

Contributions, corrections, and enhancements to the parsing scripts or text datasets are welcome. Feel free to open an issue or submit a pull request if you have ideas on how to further improve the data structure or presentation.

## License

This project is open-source and released under the [Apache License 2.0](./LICENSE).

_Dr. Mārcis Gasūns_
