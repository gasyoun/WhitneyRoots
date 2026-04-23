# WhitneyRoots

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

### 💻 Code & Resources
* [`/src/`](./src/) - Source code and scripts used for parsing, processing, and generating the markdown/text files.

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

## Contributing

Contributions, corrections, and enhancements to the parsing scripts or text datasets are welcome. Feel free to open an issue or submit a pull request if you have ideas on how to further improve the data structure or presentation.

## License

This project is open-source and released under the [Apache License 2.0](./LICENSE).
