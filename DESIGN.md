# Whitney-Root Crosswalk — DESIGN

**Status:** design locked 2026-06-10 / -12 · **Phase 0 in progress**
**Maintainer:** gasyoun · **License:** CC BY-SA 4.0 (matches DCS)

Link the three Sanskrit resources — **grammar** (Whitney), **corpus** (DCS), **dictionaries** (Cologne) — into one FAIR, citable dataset, keyed on the Whitney root, consumable by a Sanskrit **student**.

---

## 1. The problem

Three siloed resources, each keyed on a *different* identifier:

| Resource | What | Key |
|---|---|---|
| **Grammar — Whitney** | 938 verbal roots (the *Roots* appendix) + the full grammar §§ 1–1340 | IAST root + homonym no. |
| **Corpus — DCS / VisualDCS** | ~4.57M tokens, 55k lemmas, per-form frequency, CoNLL-U | DCS lemma id |
| **Dictionaries — Cologne** | MW, Apte, PW, PWG … headwords, senses, `<ls>` sources | SLP1 headword + homonym no. |

The natural pin is the root/lemma, but nothing shares an ID. The whole project is **one crosswalk** — `Whitney root ↔ DCS lemma ↔ Cologne headword` — reconciled across IAST↔SLP1 and across each scheme's independent homonym numbering. Whitney's *Roots* is a **supplement** to the grammar, so the root list ≠ the whole grammar layer; the §§ are a second graph.

---

## 2. Architecture — two layers joined at the Whitney root

```
            WhitneyRoots          VisualDCS (DCS)        Cologne (MW/Apte)
                 |                      |                       |
   class·PPP·paradigm·gloss     lemma·freq·forms          headword·senses
                 \                      |                       /
                  \                     v                      /
   LAYER 1 ───────►  √ HUB — Whitney root-sense #1–938  ◄──────
   (lexical            key = SLP1 + homonym index
    crosswalk)                         │  roots ⇄ §§
   LAYER 2 ───────►  Whitney Grammar §§ 1–1340  (Wikisource)
   (grammar graph)    root → form-category → § (concordance)
                                        │
                          Sanskrit student / reader
                    passage → word → root + §§ + gloss
```

- **Layer 1 — lexical crosswalk (root-keyed):** ships first. Hub = Whitney root-sense; `whitney_no` is already unique per homonym, so it *is* the canonical sense id.
- **Layer 2 — grammar graph:** Whitney §§ from Wikisource; `root → form-category → §` edges via a hand-built concordance (warnemyr cannot index into Whitney — see §7).

---

## 3. Locked decisions

| Decision | Choice |
|---|---|
| Hub / key | Whitney root-sense #1–938 · `SLP1 + homonym index` (IAST for display) |
| Deliverable | FAIR crosswalk **dataset first** — normalized tables (CSV/SQLite) **+ RDF** |
| Grammar depth | **full §§ cross-linking** (Layer 2) |
| §§ body source | **Wikisource** |
| Root source-of-truth | **full re-scrape of warnemyr** (local files are a lossy derivative) |
| First dictionaries | **MW + Apte** (both English; MW seeded by `Whitney_sopasarga_PP.txt`) |
| Corpus attachment | **lemma-level now, token-level next** |
| Whitney-root link | **warnemyr canonical + samskrtam.ru mirror** (both stored) |
| Consumer | **Sanskrit student / reader** |
| Home repo | **WhitneyRoots** (spine + §§ + crosswalk) |

---

## 4. Data model — spine record (per root-sense)

```jsonc
{
  "whitney_no": 114, "root_iast": "kḷp", "root_slp1": "kxp", "homonym": null,
  "class": ["I"], "gloss_short": "be adapted", "gloss_full": "be in order, succeed; …",
  "paradigm": { "present":"kálpate", "future":"kalpsyate; kalpiṣyate",
    "aorist":"acīkḷpat", "perfect":"cakḷpé", "caus":"kalpáyati",
    "desid":"cikḷpsa-", "inten":"cāklp-",
    "verbal_nouns": { "ppp":"kḷptá", "inf":"kalpitum", "ger":"kḷptvā; -kḷpya" } },
  "period_tags": ["V","B","S","E","C"], "derivatives": ["kḷpti","kálpa","kalpana"],
  "preverbs": ["abhi","ava","upa","pari","pra","vi","sam","upasam"],
  "warnemyr_url": "root_k_lp.html", "samskrtam_url": "root_k_lp.html",
  // resolved in later phases:
  "dcs_lemma": null, "dcs_freq": null, "dcs_class_tag": null, "attested_forms": [],
  "mw_id": null, "mw_homonym": null, "apte_id": null, "senses": [],
  "whitney_sections": []   // form-category → § via the concordance (Layer 2)
}
```

Serialized as **CSV/SQLite + Turtle (RDF)**, bridged by **CSVW**; persistent **w3id.org** URIs.

---

## 5. Source of truth — warnemyr, and the data-quality findings

`warnemyr.com/skrgram` (Lennart Warnemyr © 2005) is the **rich source of truth** for the root layer: each page has the full paradigm, diachronic period tags (V/B/S/E/C), derivatives, upasarga senses, and intra-grammar hyperlinks. The local WhitneyRoots files are a **lossy HTTrack scrape**:

- **`kḷp` (#114)** is `—`/`—` (class/PPP) locally but really **class I, PPP kḷptá** — a *capture gap*, so **`—` ≠ defective**; every `—` root is audited against warnemyr.
- **Homonym class/PPP is union-smeared**: `2 √as` shows cl. II but is really **IV** (*ásyati*); all three `√kṛ` show VI but "make" is **VIII**. So Whitney-side classes are **re-derived per-homonym from warnemyr first**.

**Mechanics:** warnemyr keys each homonym in its URL (`root_1_zad.html` = 1 √śad), with an **irregular** encoding (ś→`z`, ā→`aa`, ṣ→`_s`, ḷ→`_l`, homonym-number prefix) — so the `{sense → URL}` map is **harvested from the root index**, never generated (this was the "linked wrong before" bug). warnemyr's HTTPS cert is invalid → `WebFetch` fails; fetch with **`curl -k`**. Some pages group roots (`root_arc.html` = "arc, ṛc") → warnemyr-page → whitney_no is **many-to-one** in places.

---

## 6. Homonym alignment (Whitney ↔ MW ↔ DCS)

Homonym *numbers* across sources are independent labels — **match by feature, never by number**. `whitney_no` is the canonical sense id; MW / Apte / DCS map **onto** it as a **many-to-many** `root_alignment` table (cardinality can disagree — Whitney's 4× `√dā` may ≠ MW's split).

- **Discriminators**, in order: **class (Gaṇa) → present-stem → gloss**. Class resolves many (`as` II vs IV; `vid` II/VI/IV); a minority collide (`akṣ`, `dī`, `paś`, `phal`, `pat`) or mismatch in count (`dā`, `vā`, `pā`).
- **Policy (default): conservative** — auto-accept only on a unique class+stem match; everything else → a human review queue (~25–35 groups), stored as an audit-trailed alignment file in the `csl-corrections` paired-line idiom.
- **Sizing:** ~55 homonym groups / ~120 senses.

---

## 7. LOD / RDF + the form→§ concordance

**form-category → Whitney § is a hand-built ~30-row concordance**, not a scrape: warnemyr's morphology pages use Warnemyr's *own* formal notation with **zero Whitney/§ citations**, so they cannot index into Whitney. The concordance is sourced from Whitney's own ToC (Perfect → ≈ §§ 781–823, Reduplicated aorist → ≈ §§ 856–873, PPP → ≈ §§ 952–958, …). Composition: `root → has-form-of-category C` (warnemyr) → `§-range(C)` (concordance).

**RDF vocabulary** — OntoLex-Lemon, modeled on **LiLa (Linking Latin)** (a lemma hub interlinking corpora + lexica + morphology):

- Hub root-sense = `ontolex:LexicalEntry` (`wr:Root`), URI `…/root/{whitney_no}`; `canonicalForm → writtenRep` in SLP1 / IAST / Devanagari.
- Forms = `ontolex:otherForm`; morpho-features in **UD** (matches DCS CoNLL-U) → **OLiA**; Gaṇa = `wr:gana`.
- Senses/dicts = `ontolex:LexicalSense`; MW/Apte entries linked by `rdfs:seeAlso` / `vartrans`.
- Corpus = DCS token `ontolex:isFormOf` hub (LiLa/CoNLL-RDF pattern).
- Grammar = Whitney § as `wr:Section` (+ Wikisource `foaf:page`); root→§ via **CITO** `cito:isExplainedBy`.
- Diachrony = V/B/E/C as SKOS aligned to **PeriodO** URIs.

Mint a **thin `wr:` namespace** for only the ~5 Sanskrit-specific predicates (Gaṇa, §, period); reuse standards for the rest.

---

## 8. Reader UX

Two-pane (passage left, sticky analysis panel right — Perseus/Logeion pattern, **not** a popover). **Progressive disclosure** matching `token → root + §§ + gloss`: Analysis + **"Why this form?"** (the §-link — the accent **hero**, the thing a plain dictionary can't do) + Root + Dictionary visible; Corpus collapsed. §-resolution spans **verb / participle / nominal**. Homonym chip → a **√A-or-√B chooser** for unresolved cases; panel **degrades gracefully** on gaps (`unresolved` / `§ not yet mapped`, never guess). The reader introduces **no new data** — it is a pure view over the crosswalk + concordance.

---

## 9. Build order

| # | Phase | Output |
|---|---|---|
| **0** | **Harvest warnemyr** — 937 pages → structured records **+ `—`/smear audit** | spine + Layer-2 form data |
| 1 | Corpus arm (lemma) | DCS freq/forms + class-tag cross-check |
| 2 | Dict arm (MW + Apte) | senses; homonym alignment (curated) |
| 3 | §§ ingest (Wikisource) | §§ 1–1340 nodes; build the form→§ concordance |
| 4 | Grammar cross-link | root→form→§, morph-cat→§, corpus-form→§ |
| 5 | Token reader (v2) | passage word → root → {§§, gloss} |

---

## 10. Open curation questions

- **Homonym alignment** review queue (the ~25–35 class-collision / cardinality-mismatch groups).
- **`—` audit** outcomes — which are truly defective vs capture gaps.
- Exact **§-range bounds** for the form→§ concordance (pinned during Wikisource ingest).
- IAST→SLP1 transcoding edge cases (vocalic ḷ/ḹ, accents, the DCS `?`-damaged words).

---

## 11. Provenance & licensing

| Source | Author / project | License |
|---|---|---|
| Whitney roots + grammar | W. D. Whitney; digitised by **L. Warnemyr** (warnemyr.com/skrgram, © 2005) + Wikisource | per source |
| Corpus | **DCS** — O. Hellwig (Digital Corpus of Sanskrit) | CC BY-SA 4.0 |
| Dictionaries | **Cologne** Digital Sanskrit Dictionaries (MW, Apte, …) | per CDSL |

Output dataset: **CC BY-SA 4.0**. Every crosswalk claim links to its source (form rule → Whitney §§ / Wikisource; root + paradigm → warnemyr; senses → Cologne; attestation → DCS).
