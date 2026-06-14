# PPP Apparatus-Bleed Cleanup Worklist

> Self-contained worklist for normalizing **Whitney scholarly apparatus** that has bled into the `ppp` (past-passive-participle) arrays of 39 records in [`src/app_data.json`](../src/app_data.json). Written for an engineer with **no prior context** on this work. Read it top to bottom before touching data.

---

## 1. Summary & scope

### What is "apparatus bleed"?

Each lexicon record in [`src/app_data.json`](../src/app_data.json) has a `ppp` array — the past-passive-participle form(s) Whitney lists for that root. The PPP forms were extracted from the fixed-width source column in [`Whitney_roots_class-PP.txt`](../Whitney_roots_class-PP.txt). That source column does **not** contain only clean stems: Whitney interleaves his **scholarly apparatus** directly into the PPP cell. When the column was split (on commas), the apparatus tokens were carried into the array verbatim. Examples of the apparatus that bled in:

| Apparatus kind | Looks like | Meaning |
|---|---|---|
| Period / text-of-attestation markers | `RV1`, `RV2`, `E1`, `C1`, `S1`, `B1`, `K`, `R`, `AA` | The text/period where the form is attested (Rig-Veda, Epic, Classical, Sutra, Brahmana, Kāṭhaka, Rāmāyaṇa, Aitareya-Āraṇyaka). **Provenance, not part of the stem.** A trailing bare digit (`danta 1`, `bhugna 1`) is a period-figure of the same family. |
| Uncertainty marker | `?` | Whitney's doubt about the form (`ajita ?`, `snuta ?`). |
| Alternate-form joiners | `&` (`turta & turna`), bare space between two stems (`vrdha brdha`) | Two genuine variant participles that should be **separate** array elements. |
| Cross-reference notes | `=`, `= seq. abhi` | "behaves like / is attested following" another entry. |
| Usage note | `adj` | Form used adjectivally, not a verbal participle proper. |
| OCR doubling | `rise rises` (id 649) | A real form (`rise`) plus a spurious duplicate (`rises`). |

So a record like id **99 √kup** ships `ppp: ["kupita RV1"]` when the canonical participle is `kupita` and `RV1` is provenance metadata.

### How this differs from the already-fixed "gloss bleed"

A **sibling** bug — English **gloss** text bleeding into `ppp` — was already fixed for **6 records** by [`scripts/dcs/fix_ppp_gloss_bleed.py`](../scripts/dcs/fix_ppp_gloss_bleed.py) (ids 19, 100, 182, 184, 347, 831; e.g. `"gunthita veil", "conceal", "hide"` → `["gunthita"]`). That was **English meaning words** spilling into the PPP column. **This task is distinct**: the contaminant here is Whitney's **Sanskrit-philological apparatus** (period markers, `?`, `&`, cross-refs), not English glosses. Those 39 records were **intentionally left untouched** by the gloss fix and are the entire scope of this worklist. Do **not** re-touch the 6 gloss records.

### Why it matters (the two downstream consumers it breaks)

1. **False ✗ validation chips** — [`src/renderers/detail.js`](../src/renderers/detail.js) (lines 133–149) renders a "Whitney PPP vs corpus" row. For each `ppp` string it computes a diacritic-folded key via `fold()` (lines 291–299) and checks `attested.some(a => a === pf || a.startsWith(pf))`. With apparatus attached, `fold("kupita RV1") === "kupita rv1"`, which **fails** both `===` and `startsWith` against the corpus stem `kupita` — so a correctly-attested form renders a **red ✗ "miss" chip** (`dcs-chip miss`). Stripping the apparatus restores the true ✓.
2. **Inflated "fundamentalness" scoring** — [`src/core/analytics.js`](../src/core/analytics.js) line 23: `if (item.ppp) score += item.ppp.length * 2;`. Centrality counts **array length**. Unsplit `&`/space alternates (e.g. id 332 `["tvarita", "turta & turna"]` = length 2 instead of the true 3) and any future split changes the count and therefore the centrality score. The count must reflect **real** participle forms only.

### Scope

- **39 records**, ids listed in §2. File: [`src/app_data.json`](../src/app_data.json), `lexicon` array (935 entries total).
- These were classified per-record and **adversarially verified** (every verdict `agree: true`). Verifier corrections to the canonical form are folded into §2 below.

---

## 2. Correction table

Every column is the **verified** canonical `ppp` (verifier corrections applied where any verdict raised severity). All 39 verdicts came back `agree: true`; the two `minor` flags (ids 227, 332) were **citation/metadata nits only** — the shipped canonical forms were already correct, so no canonical value changed. The two `minor` flags on ids 737 and 747 likewise concern provenance reconciliation, not the shipped form.

| id | root | current `ppp` | canonical `ppp` (verified) | treatment |
|---|---|---|---|---|
| 6 | aj | `["ajita ?"]` | `["ajita"]` | mechanical |
| 74 | ṛd | `["ardita ="]` | `["ardita"]` | editorial |
| 99 | kup | `["kupita RV1"]` | `["kupita"]` | mechanical |
| 140 | kṣā | `["ksana ?"]` | `["ksana"]` | mechanical |
| 168 | gadh | `["gadhita RV2"]` | `["gadhita"]` | mechanical |
| 227 | cit | `["citta", "cite ?", "citaye"]` | `["citta", "cite", "citaye"]` | mechanical |
| 306 | tim | `["timita R"]` | `["timita"]` | mechanical |
| 322 | tṛṣ | `["trsita", "trsta ? adj"]` | `["trsita", "trsta"]` | editorial |
| 326 | tras | `["trasta", "trasas K"]` | `["trasta", "trasas"]` | mechanical |
| 332 | tvar | `["tvarita", "turta & turna"]` | `["tvarita", "turta", "turna"]` | mechanical |
| 343 | dam | `["danta 1"]` | `["danta"]` | mechanical |
| 365 | du | `["duna", "duta AA. ? C1"]` | `["duna", "duta"]` | editorial |
| 371 | 1 dṛ | `["dirna", "drta R"]` | `["dirna", "drta"]` | mechanical |
| 372 | 2 dṛ | `["dirna", "drta R"]` | `["dirna", "drta"]` | mechanical |
| 452 | pi | `["pina 1 & pipivas"]` | `["pina", "pipivas"]` | mechanical |
| 469 | 1 pṛ | `["purna", "prta S1. purita"]` | `["purna", "prta", "purita"]` | editorial |
| 470 | 2 pṛ | `["purna", "prta S1. purita"]` | `["purna", "prta", "purita"]` | editorial |
| 471 | 3 pṛ | `["purna", "prta S1. purita"]` | `["purna", "prta", "purita"]` | editorial |
| 472 | pṛc | `["prkta", "prgna ? RV1", "prce"]` | `["prkta", "prgna", "prce"]` | mechanical |
| 524 | 1 bhuj | `["bhugna 1"]` | `["bhugna"]` | mechanical |
| 525 | 2 bhuj | `["bhugna 1"]` | `["bhugna"]` | mechanical |
| 573 | mṛkṣ | `["mraksita = seq. abhi"]` | `["mraksita"]` | editorial |
| 580 | mṛdh | `["mrddha 1"]` | `["mrddha"]` | mechanical |
| 632 | raś | `["rasita 1"]` | `["rasita"]` | mechanical |
| 633 | ras | `["rasita 1"]` | `["rasita"]` | mechanical |
| 649 | riṣ | `["rista", "rise rises"]` | `["rista", "rise"]` | investigate |
| 668 | lag | `["lagna B1.?"]` | `["lagna"]` | editorial |
| 706 | van | `["vata 1"]` | `["vata"]` | mechanical |
| 708 | 1 vap | `["upta", "upita E1", "vapta E1"]` | `["upta", "upita", "vapta"]` | mechanical |
| 709 | 2 vap | `["upta", "upita E1", "vapta E1"]` | `["upta", "upita", "vapta"]` | mechanical |
| 718 | vah | `["udha", "vodha ? E1"]` | `["udha", "vodha"]` | mechanical |
| 737 | vī | `["vita 1"]` | `["vita"]` | mechanical |
| 747 | vṛh | `["vrdha brdha"]` | `["vrdha", "brdha"]` | editorial |
| 790 | śuc | `["sukta ?"]` | `["sukta"]` | mechanical |
| 797 | 1 śṛ | `["sirna", "sirta", "surta ? RV1"]` | `["sirna", "sirta", "surta"]` | mechanical |
| 798 | 2 śṛ | `["sirna", "sirta", "surta ? RV1"]` | `["sirna", "sirta", "surta"]` | mechanical |
| 799 | 3 śṛ | `["sirna", "sirta", "surta ? RV1"]` | `["sirna", "sirta", "surta"]` | mechanical |
| 877 | snu | `["snuta ?"]` | `["snuta"]` | mechanical |
| 892 | sphṛ | `["sphurita", "sphulita C1"]` | `["sphurita", "sphulita"]` | mechanical |

**Forms carrying a Whitney `?` uncertainty** (to be recorded as metadata, see §4b): id 6 `ajita`, 140 `ksana`, 227 `cite`, 322 `trsta`, 365 `duta`, 472 `prgna`, 668 `lagna`, 718 `vodha`, 790 `sukta`, 797/798/799 `surta`, 877 `snuta`.

**Important non-collapse rule:** id 747 `vrdha brdha` is a **genuine v-/b- variant pair** (vṛh~bṛh alternation) and **must be split**, whereas id 649 `rise rises` is a real form plus an **OCR duplicate** and the duplicate must be **dropped**. Both involve a bare space — the source/validation evidence is what distinguishes them (see §4c, §4e). Do not write a blanket "split on space" rule.

---

## 3. Mechanical vs editorial split

### Mechanical (26 records) — deterministic apparatus strip / alternate split, no policy judgment

Strip trailing period markers (`RV1`/`RV2`/`E1`/`C1`/`S1`/`K`/`R`/`AA`/bare digit) and/or `?`; split `&`-joined and (where evidence confirms a variant pair) space-joined alternates. No preserve-vs-drop decision.

> 6, 99, 140, 168, 227, 306, 326, 332, 343, 371, 372, 452, 472, 524, 525, 580, 632, 633, 706, 708, 709, 718, 737, 790, 877, 892

### Editorial (12 records) — needs a human policy decision before/while editing

These carry a token whose **keep-vs-drop** or **parse** is a judgment call (a dangling/cross-ref `=`, an `adj` usage note, a `?` on a form whose retention is debatable, or a `.`-terminated abbreviation that must be parsed off without eating a following real form):

> 74 (dangling `=`), 322 (`? adj`), 365 (`AA. ? C1` cluster), 469, 470, 471 (`S1.` abbreviation + following real form `purita`), 573 (`= seq. abhi` cross-ref), 668 (`B1.?` artifact + `?`), 747 (`brdha` is a real alternate **not** in the warnemyr validation list — preserve-vs-drop)

### Investigate (1 record)

> 649 (`rise rises` — OCR doubling; see §4e)

---

## 4. Cross-cutting editorial decisions (for [`docs/DECISIONS_NEEDED.md`](DECISIONS_NEEDED.md))

Each is phrased as a question with a **recommended default**. These are policy calls that determine the destination of the stripped apparatus; settle them before the bulk edit so metadata is captured, not discarded.

### (a) Do we DROP period/source provenance markers, or preserve them?

Markers affected: `RV1 RV2 E1 C1 S1 B1 K R AA` and bare trailing digits.

> **Recommended default:** **Preserve, do not discard.** Strip the marker out of the `ppp` string (so the form is clean for `fold()`/scoring), but capture it in a **new sibling field** `ppp_attestation` (or `ppp_provenance`) keyed by form, e.g.
> ```json
> "ppp": ["kupita"],
> "ppp_attestation": { "kupita": ["RV1"] }
> ```
> Rationale: the markers are genuine Whitney scholarship (text/period of first attestation) and are reconstructable for a `<ls>`-style link later; dropping them is lossy and irreversible. The new field is **additive** and ignored by current consumers, so it cannot regress detail.js/analytics.js. If product decides metadata is out of scope for now, the fallback is to drop the markers but **record them in the audit change file** (§5) so they are recoverable.

### (b) Do we preserve Whitney's `?` uncertainty as a flag?

> **Recommended default:** **Yes, preserve as a per-form flag** in a `ppp_uncertain` array (the 13 forms enumerated at the end of §2), separate from the clean `ppp` string. Rationale: `?` is a substantive editorial signal (Whitney doubts the form); collapsing it silently loses information that downstream review (and the validation crosswalk) cares about. Like (a), additive and consumer-safe.

### (c) Policy for splitting `&` / space alternates into separate `ppp` elements

> **Recommended default:** **Split into separate array elements** so each real participle is one element (correct for `analytics.js` length-counting and `detail.js` per-form chips). Specifically:
> - `&` (id 332 `turta & turna`, id 452 `pina 1 & pipivas`): **always split** — `&` unambiguously joins alternates per the source legend.
> - **Bare space** (id 747 `vrdha brdha`): split **only when** source + validation confirm a genuine variant pair. Do **not** generalize a "split on whitespace" rule, because most space-separated tokens in this column are apparatus (`vata 1`, `surta ? RV1`), not second forms.
> Never collapse two real alternates into one element, and never silently drop one.

### (d) Handling of `= seq.` cross-references and the `adj` usage note

> **Recommended default:** **Strip out of `ppp`; record the note in metadata** (`ppp_note` keyed by form), do not keep it inside the participle string.
> - id 573 `mraksita = seq. abhi` → `["mraksita"]`, note `{"mraksita": "= seq. abhi (cf. abhi-mṛkṣ)"}`.
> - id 74 `ardita =` → `["ardita"]`, but the `=` is **dangling** (target truncated at the column boundary). **Flag for a human** to recover the intended cross-ref target from Whitney's print. Until recovered, record `{"ardita": "= (cross-ref target unrecovered)"}`.
> - id 322 `trsta adj` → `["trsta"]`, note `{"trsta": "adj (adjectival usage)"}`.

### (e) The `rise rises` anomaly (id 649)

> **What the source actually shows:** [`Whitney_roots_class-PP.txt`](../Whitney_roots_class-PP.txt) line 658 literally reads `rista, rise rises`. The validation crosswalk ([`crosswalk/ppp_validation.json`](../crosswalk/ppp_validation.json), whitney_no 649) lists `warnemyr_ppp_forms = ["riṣṭá", "rista", "rise"]` (verdict `match`). So `rista` and `rise` are **genuine** recorded participles; **`rises` is NOT** — it is an OCR/parse doubling of `rise` (an English-plural-looking corruption).
> **Recommended resolution:** ship `["rista", "rise"]` — split the two real forms, **drop** `rises`. This is the one record flagged `investigate`; do not silently keep `rises`. (Contrast id 747 in §4c, a real variant pair that must be kept.)

---

## 5. Recommended implementation

**Mirror [`scripts/dcs/fix_ppp_gloss_bleed.py`](../scripts/dcs/fix_ppp_gloss_bleed.py) exactly.** That script is the proven, reviewed pattern for surgically editing this file. Create a new sibling, e.g. `scripts/dcs/fix_ppp_apparatus_bleed.py`. Do **not** `json.dump()` the whole structure — a round-trip would rewrite every line and corrupt the formatting.

### File invariants (verified against the live file — preserve all of them)

- **No BOM** — first 3 bytes are `7b 0d 0a` (`{\r\n`), not `ef bb bf`.
- **CRLF line endings** throughout (17601 `\r\n`, zero bare `\n`). Open with `newline=''` to disable translation.
- **2-space base indent**; `ppp` **array elements at 8-space indent**; the closing `]` of a `ppp` array at **6-space indent** (`      ]`), matching the wrappers in the gloss-fix script.
- **No trailing newline** — the file ends `...\r\n  }\r\n}` with no final newline.
- **935 entries** in `lexicon`.

### Edit strategy

1. Read with `open(path, 'r', encoding='utf-8', newline='')`; assert it does **not** start with `'﻿'`.
2. For each of the 39 records build a `wrapped_old`/`wrapped_new` pair targeting the **exact** `"ppp": [ ... ]` block (same approach as the gloss script's `CORRECTIONS` loop — anchor on the unique array-element content so the wrapper/indentation is untouched). Because several records share identical `ppp` text (e.g. 371/372 `["dirna", "drta R"]`; 469/470/471 `["purna", "prta S1. purita"]`; 708/709; 797/798/799), **anchor on the unique `"id"` of each record first**, then replace the `ppp` block within that record's slice (mirror the script's `guph` special-case, which anchors on a unique field before replacing a non-unique substring). Do **not** rely on a global `count == 1` for the shared-text records — it will be > 1 and must be handled per-id.
3. Make every replacement **idempotent**: if `wrapped_old` is not found, print `skip` and continue (re-running after success is a no-op). Never error on "not found".
4. If §4 decisions (a)/(b)/(d) are accepted, also inject the additive `ppp_attestation` / `ppp_uncertain` / `ppp_note` fields in the same surgical pass (or, simpler, generate them in a second idempotent pass). Keep them additive so no consumer regresses.
5. Write back with `open(path, 'w', encoding='utf-8', newline='')` — preserves CRLF, adds no BOM, adds no trailing newline.

### Post-edit verification (bake into the script, like the gloss fix's verify block)

- Re-read raw bytes: assert `raw[:3].hex() != 'efbbbf'` (no BOM introduced).
- `json.loads(raw.decode('utf-8'))` succeeds (valid JSON).
- `len(data['lexicon']) == 935`.
- Every one of the 39 ids has its **canonical** `ppp` from §2 (assert each `by_id[rid]['ppp'] == expected`).
- Re-confirm CRLF preserved (`raw.count(b'\r\n')` unchanged outside the edited spans; zero bare `\n`) and no trailing newline added.

### Consumer cross-checks (no consumer should break)

- [`src/renderers/detail.js`](../src/renderers/detail.js) `fold()` (lines 291–299): with clean stems, `fold("kupita")` now `startsWith`-matches the corpus stem → ✓ chip instead of false ✗. Spot-check a handful of the 39 in the running app via the `/run-whitneyroots` reader/v3 app to confirm chips flip green.
- [`src/core/analytics.js`](../src/core/analytics.js) line 23: `score += item.ppp.length * 2` — confirm the records whose array length **changed** (332, 452, 469, 470, 471, 747 grew; 649 shrank) get the intended new centrality. This is expected and correct (counts now reflect real forms).
- **Bundle:** per [`CLAUDE.md`](../CLAUDE.md), any `src/` change requires `node scripts/bundle.js` to regenerate [`v3_app.js`](../v3_app.js). `app_data.json` is data, not a bundled module — but re-run the bundle if you touch any `src/*.js`, and re-smoke the app.
- **Sidecars:** the canonical-form change is confined to `app_data.json`. The validation crosswalk [`crosswalk/ppp_validation.json`](../crosswalk/ppp_validation.json) is the **source of truth used to verify** the corrections, not a consumer to rewrite — leave it untouched. Other ppp sidecars ([`src/participle_index.json`](../src/participle_index.json), [`src/participle_index_dcs.json`](../src/participle_index_dcs.json), [`src/reader_data.json`](../src/reader_data.json)) are DCS/corpus-derived and do **not** mirror Whitney's `ppp` strings; confirm none of them ingest the raw apparatus strings before assuming they're unaffected.

### Audit trail

Per the org [`CLAUDE.md`](../../CLAUDE.md) correction conventions, capture the before/after as a change record (and, if decision (a) lands as "drop", record every stripped marker there so provenance is recoverable). Commit the script + the corrected `app_data.json` + this worklist; reference the decisions added to [`docs/DECISIONS_NEEDED.md`](DECISIONS_NEEDED.md).

---

## 6. Acceptance criteria & out-of-scope notes

### Acceptance criteria

- [ ] All **39** ids in §2 carry their **verified canonical** `ppp` (apparatus stripped, alternates split, `rises` dropped).
- [ ] No `ppp` string in any of the 39 contains: a period/source marker (`RV1 RV2 E1 C1 S1 B1 K R AA` or a trailing bare digit), `?`, `&`, `=`, `adj`, or `seq.`.
- [ ] id 332 → length 3; id 452 → length 2; ids 469/470/471 → length 3; id 747 → length 2; id 649 → length 2. (Length changes are intentional; analytics centrality updates accordingly.)
- [ ] [`src/app_data.json`](../src/app_data.json) is valid JSON, **BOM-free**, **CRLF**, **935 entries**, **no trailing newline** — byte-format identical to before outside the edited spans.
- [ ] Script is **idempotent** (second run = "Nothing to change").
- [ ] If decisions §4(a)/(b)/(d) accepted: `ppp_attestation` / `ppp_uncertain` / `ppp_note` populated and additive (no consumer regression).
- [ ] detail.js "Whitney PPP vs corpus" chips for the affected roots no longer show false ✗ caused by apparatus suffixes (verified in the running app).
- [ ] The 6 **gloss-bleed** records (19, 100, 182, 184, 347, 831) are **untouched**.

### Out of scope

- The 6 gloss-bleed records — already fixed by [`scripts/dcs/fix_ppp_gloss_bleed.py`](../scripts/dcs/fix_ppp_gloss_bleed.py). Do not re-run or re-edit them.
- **Diacritic / vowel-length normalization** of the canonical forms. The source PPP column is romanized **without** macrons/dots (`ksana` for kṣāṇa, `vita` for vīta, `danta` for dānta, `mrddha` for mṛddha). Ship the **source-literal** unaccented form as the canonical anchor; do **not** "upgrade" to the accented warnemyr/vidyut spine (`tṛṣitá`, `vīta`, `dānta`). Reconciling source-literal vs accented spine is a separate, larger decision (ids 737 `vita`/`vīta` and 227 `citta`/`cittá` were flagged `minor` precisely for this — noted, not actioned here).
- Recovering the **dangling cross-ref target** for id 74 `ardita =` from Whitney's print — flagged for a human (§4d); not a code change.
- Inventing warnemyr "spine head" forms (e.g. `bhukta` for 525, `pṛta` for 471) into `ppp` — those are **not** in Whitney's PPP column for those lines and must not be added.
- Editing [`crosswalk/ppp_validation.json`](../crosswalk/ppp_validation.json) or any DCS sidecar — they are validation inputs, not targets.
