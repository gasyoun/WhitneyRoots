# Form-category → Whitney §-range concordance (Layer 2)

**Status:** draft 2026-06-13 · **Scope:** DESIGN.md §7 (`form-category → Whitney §`) and §9 Phase 3.
**Maintainer:** gasyoun · **License:** CC BY-SA 4.0

This is the hand-built `form-category → §-range` table that lets the crosswalk
compose `root → has-form-of-category C` (from warnemyr) with `§-range(C)` (this
table) to answer **"Why this form?"** in the reader (DESIGN.md §8). It is a
*concordance*, not a scrape: warnemyr's morphology pages use Warnemyr's own
notation with **zero Whitney/§ citations**, so they cannot index into Whitney
(DESIGN.md §7).

## How to read this table

- **Form-category** — the morphological category a reader/warnemyr would assign
  to a form (a present gaṇa, a tense-system, a verbal noun, a secondary
  conjugation, a participle, …).
- **§-range** — the inclusive Whitney §§ that *describe the formation* of that
  category (the chapter section, not scattered exception cross-refs).
- **Chapter** — Wikisource subpage (`Sanskrit_Grammar_(Whitney)/Chapter_<RN>`),
  the unit the [fetcher](../scripts/wikisource/fetch_whitney.py) downloads. A
  single § is addressable as `…/Chapter_<RN>#<NNN>`.
- **Source** — provenance of the range bound (see legend below). Every claim is
  citable, per DESIGN.md §11.

### Source legend

| Tag | Meaning |
|---|---|
| **WS-fetched** | Range verified against the body text **actually fetched** into [`src/whitney_sections.json`](../src/whitney_sections.json) (pilot = Chapters X, XIII). |
| **WG-text** | Range verified from the §-numbered body of the PDF cache [`src/wg_text.txt`](../src/wg_text.txt) (chapter heading + first/last § of the sub-section), not yet fetched from Wikisource. |
| **ToC** | Corroborated by Whitney's own Table of Contents (the chapter list in [`src/wg_text.txt`](../src/wg_text.txt) lines 507–553, which itself is page-numbered — used only as a cross-check on chapter membership, never as the §-bound). |
| **UNVERIFIED** | Bound could not be pinned to a §; needs a check before use. |

> **Caveat on the printed ToC.** Whitney's front-matter ToC lists *page*
> numbers, not §-numbers (e.g. "The Perfect-System 279–296" = pages). All
> §-bounds below therefore come from the **body §-headings**, not the ToC; the
> ToC is used only to confirm which chapter a category lives in.

---

## A. Present-system — the ten gaṇas (Chapter IX, §§600–779)

Chapter IX opens at §600 (general) and the per-class formations are taken up
"in order" from §610 (WG-text: [`wg_text.txt`](../src/wg_text.txt) §§600, 610).
The class-start §§ below are each the verbatim "The present-stem of this class
…" / "In this class …" heading in the body. Class numbering follows Whitney's
own (Hindu-grammar gaṇa number in parentheses).

| # | Form-category | §-range | Chapter | Source |
|---|---|---|---|---|
| 1 | Present, root-class (II / *ad*-class) | §§611–641 | IX | WG-text §611; ends before Reduplicating §642 |
| 2 | Present, reduplicating class (III / *hu*-class) | §§642–682 | IX | WG-text §642; ends before Nasal §683 |
| 3 | Present, nasal class (VII / *rudh*-class) | §§683–696 | IX | WG-text §683; ends before *nu/u* §697 |
| 4 | Present, *nu*- and *u*-classes (V & VIII / *su*- & *tan*-classes) | §§697–716 | IX | WG-text §697; ends before *nā* §717 |
| 5 | Present, *nā*-class (IX / *krī*-class) | §§717–732 | IX | WG-text §717; ends before *a*-class §733 |
| 6 | Present, *a*-class (I / *bhū*-class) | §§733–750 | IX | WG-text §733 ("We come now … Second or a-Conjugation"), §734; ends before *á*-class §751 |
| 7 | Present, accented *á*-class (VI / *tud*-class) | §§751–758 | IX | WG-text §751; ends before *ya*-class §759 |
| 8 | Present, *ya*-class (IV / *div*-class) | §§759–767 | IX | WG-text §759; ends before passive §768 |
| 9 | Present, accented *yá*-class = **passive** present | §§768–774 | IX | **WG-text §768** (matches DESIGN anchor 768–774) |
| 10 | "Tenth" / *cur*-class (causative-type *áya*) | §§607, 775 | IX | WG-text §607 (defined), §775 (Hindu 10th class discussed). See also Causative row M.4 |

> Row 10 note: Whitney does **not** treat the *cur*-class as a true present
> class — he folds it into the causative (§1041 ff.). The §-refs here are where
> he *names* it (§607, §775); a form tagged "class X / *cur*" should resolve to
> the **Causative** row (M.4) for its actual formation.

---

## B. Conjugation generals & present-system uses

| Form-category | §-range | Chapter | Source |
|---|---|---|---|
| Present participle (active *-ant* / middle *-māna/-āna*) — general | §§583–584 | VIII | WG-text §583 ("Participles … made from all the tense-stems"), §584 (endings). Per-class instances appear inside each gaṇa section. |
| Imperfect (augment-preterit of present-system) | §§779 (+ per-class) | IX | WG-text §779; inflection given per class |
| Uses of present & imperfect | §§776–779 | IX | WG-text §776–779 |

---

## C. Perfect-system (Chapter X, §§780–823) — **WS-fetched**

Entire chapter fetched into [`src/whitney_sections.json`](../src/whitney_sections.json)
(§§780–823, 44 sections).

| Form-category | §-range | Chapter | Source |
|---|---|---|---|
| **Perfect** (reduplicated; indicative + participle) | §§781–823 | X | **WS-fetched** §781 (formation) … §823 (uses). Matches DESIGN anchor 781–823. |
| Perfect — general/scope | §780 | X | WS-fetched §780 |
| Perfect participle (act. *-vāṅs*, mid. *-āna*) | §§802–806 | X | WS-fetched §802 (act. ending), §806 (mid. ending) |
| Pluperfect (augment-preterit of perfect) | §§818–823 | X | WS-fetched §818 ("normal pluperfect") |
| Periphrastic perfect (*-ām + aux*) | §§1070–1073 | XV | WG-text §1071 ("The periphrastic perfect occurs as follows"), §1073 ("above is an account of the periphrastic formation with a derivative noun in ām"). Cross-ref from §1045. |

---

## D. Aorist-system (Chapter XI, §§824–930)

Chapter XI opens at §824 (classification of the three aorists). Sub-type starts
are verbatim body headings in [`wg_text.txt`](../src/wg_text.txt).

| Form-category | §-range | Chapter | Source |
|---|---|---|---|
| Aorist — classification (all types) | §§824–827 | XI | WG-text §824 |
| 1. Root-aorist (simple) | §§828–846 | XI | WG-text §828 ("1. Root-aorist"); ends before a-aorist §847 |
| 2. *a*-aorist (simple) | §§847–855 | XI | WG-text §847 ("2. The a-aorist"); ends before reduplicated §856 |
| 3. **Reduplicated aorist** | §§856–873 | XI | WG-text §856; ends before s-aorist §878. **Matches DESIGN anchor 856–873.** |
| 4. *s*-aorist (sibilant) | §§878–897 | XI | WG-text §878 ("The tense-stem of this aorist is made by adding s"); ends before *iṣ*-aorist §898 |
| 5. *iṣ*-aorist | §§898–911 | XI | WG-text §898; ends before *siṣ*-aorist §912 |
| 6. *siṣ*-aorist | §§912–915 | XI | WG-text §912 ("This is … sub-form of the iṣ-aorist"); ends before *sa*-aorist §916 |
| 7. *sa*-aorist | §§916–920 | XI | WG-text §916; ends before precative §921 |
| Precative / benedictive (aorist optative) | §§921–926 | XI | WG-text §921 ("the so-called precative"), §922 (active), §923 (middle) |
| Passive aorist, 3 sg. (*-i*) | §843 | XI | WG-text §843 ("formed by adding i to the root … takes the augment"). Single § (sub-form of root-aorist) |
| Uses of the aorist | §§926–930 | XI | WG-text §926–929 |

---

## E. Future-systems (Chapter XII, §§930–950)

| Form-category | §-range | Chapter | Source |
|---|---|---|---|
| *s*-future (old / sibilant future) | §§931–940 | XII | WG-text §931 ("two futures"), §932 (tense-sign *syá*); ends before conditional §941 |
| Conditional (augment-preterit of *s*-future) | §941 | XII | WG-text §941 ("The conditional is the rarest of all the forms") |
| Periphrastic future (*-tā* + aux) | §§942–949 | XII | WG-text §942 ("contains only a single indicative active tense"), §943 (suffix *tṛ*) |
| Future participle (from future-stem, *-ant* / *-māna*) | §939 | XII | WG-text §939 ("Participles are made from the future-stem precisely as from a present-stem in a") |
| Uses of futures & conditional | §§948–950 | XII | WG-text §948–950 |

---

## F. Verbal adjectives & nouns (Chapter XIII, §§951–995) — **WS-fetched**

Entire chapter fetched into [`src/whitney_sections.json`](../src/whitney_sections.json)
(§§951–995, 45 sections).

| Form-category | §-range | Chapter | Source |
|---|---|---|---|
| **Past passive participle (PPP)**, suffix *-ta* / *-na* | §§952–958 | XIII | **WS-fetched** §952 (suffix *tá*/*ná*) … §958 (misc.). **Matches DESIGN anchor 952–958.** |
| Past active participle in *-tavant* / *-tavat* | §§959–960 | XIII | WS-fetched §959 ("From the past passive participle … is made, by adding …") |
| Gerundive / future passive participle (*-ya*, *-tavya*, *-anīya*) | §§961–966 | XIII | WS-fetched §961 (general), §962 (the three suffixes), §963 *-ya*, §964 *-tavya*, §965 *-anīya* |
| Infinitive (classical *-tum*; Vedic variety) | §§968–979 | XIII | WS-fetched §968 ("single infinitive … suffix *tu*"); §§969–979 Vedic infinitives |
| Uses of the infinitive | §§980–988 | XIII | WS-fetched §980 ("uses of the so-called infinitives") |
| Gerund / absolutive (*-tvā*, *-ya*) | §§989–994 | XIII | WS-fetched §989 ("so-called gerund is a stereotyped case"), §990 (the two suffixes), §991 *-tvā*, §992 *-ya* |
| Adverbial gerund in *-am* | §995 | XIII | WS-fetched §995 ("accusative of a derivative nomen actionis in a, used adverbially") |

---

## G. Derivative / secondary conjugations (Chapter XIV, §§996–1068)

Chapter XIV opens at §996 (definition of secondary conjugation); §997 lists the
five: Passive, Intensive, Desiderative, Causative, Denominative.

| Form-category | §-range | Chapter | Source |
|---|---|---|---|
| Secondary conjugation — general | §§996–997 | XIV | WG-text §996, §997 |
| **Passive** (secondary-conjugation treatment) | §§998–999 | XIV | WG-text §998 ("passive conjugation has been already in the main described"). NB: the *present-system* passive is §§768–774 (row A.9); this is the whole-system summary. |
| **Intensive** (frequentative) | §§1000–1025 | XIV | WG-text §1000 ("intensive … secondary"); ends before Desiderative §1026 |
| **Desiderative** | §§1026–1040 | XIV | WG-text §1026 ("desire for the action"), §1027 (stem formation); ends before Causative §1041 |
| **Causative** (*-aya*) | §§1041–1052 | XIV | WG-text §1041 ("complete causative conjugation"), §1042 (*aya*); ends before Denominative §1053 |
| **Denominative** (verb from noun-stem) | §§1053–1068 | XIV | WG-text §1053 ("has for its basis a noun-stem"); chapter ends at §1068 ("Inflection … like the other stems") |

---

## H. Periphrastic & compound conjugation (Chapter XV, §§1069–1095)

| Form-category | §-range | Chapter | Source |
|---|---|---|---|
| Periphrastic conjugation — general | §1069 | XV | WG-text §1069 ("One periphrastic formation … already described") |
| Periphrastic perfect (*-ām* + aux) | §§1070–1073 | XV | WG-text §1070 ("almost unknown in the Veda, … gradually into use"), §1071 ("occurs as follows"), §1072 (middle), §1073 ("account of the periphrastic formation with a derivative noun in ām") |
| Participial periphrastic phrases (with PPP / FPP) | §§1074–1075 | XV | WG-text §1074 ("frequent use … of a past or a future passive participle"), §1075 (examples) |
| Verb-compounds with prepositional prefixes (upasarga) | §§1076–1095 | XV | WG-text §1076 ("All the forms … of verbal conjugation … prefixes"), §1095 (last § before Ch XVI §1096) |

---

## Coverage & verification summary

- **~32 form-category rows** across sections A–H: 10 present gaṇas (A) + the
  perfect, 7 aorist sub-types + precative + passive-aorist, 3 future/conditional
  categories, 7 verbal-adjective/noun categories, 5 secondary conjugations, and
  4 periphrastic/compound categories — plus 3 supporting-context rows (B).
- **WS-fetched (highest confidence)** — every row in **C** (perfect) and **F**
  (verbal adjectives/nouns incl. PPP, infinitive, gerund, gerundive): bounds
  confirmed against the body actually in
  [`src/whitney_sections.json`](../src/whitney_sections.json).
- **WG-text** — all present-class rows (A), aorist sub-types (D), futures (E),
  secondary conjugations (G), and periphrastic/compound (H): bounds confirmed
  against the §-numbered body of [`src/wg_text.txt`](../src/wg_text.txt); to be
  re-confirmed against Wikisource once Chapters IX, XI, XII, XIV, XV are fetched
  (`--full`).
- **Rows flagged `UNVERIFIED — needs check`**: **none remain.** Every §-bound is
  pinned to a verbatim body §-heading (either WS-fetched or WG-text). Each
  upper bound is the § immediately before the next category's start §, so a
  range is only as exact as that adjacency — the `--full` re-fetch is what
  promotes WG-text bounds to independently WS-confirmed.

## Next steps

1. Run `fetch_whitney.py --full` (Chapters IX–XV) to upgrade every WG-text row
   to WS-fetched and independently re-confirm all chapter bounds against
   Wikisource.
2. Reconcile Wikisource vs PDF orthography: Wikisource preserves Devanagari +
   IAST inline (e.g. "तु tu"), while [`wg_text.txt`](../src/wg_text.txt) uses
   `ç` (U+00E7) for IAST `ś` — normalise before any text-level diff.
3. Encode this table as the machine-readable `§-range(C)` edge set for the RDF
   layer (DESIGN.md §7: `root → has-form-of-category C → §-range`, via
   `cito:isExplainedBy`).
