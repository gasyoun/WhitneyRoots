# PPP Cleanup Worklist — apparatus bleed + verbal-noun (infinitive) bleed

> Normalizing two contaminants in the `ppp` (past-passive-participle) arrays of [`src/app_data.json`](../src/app_data.json): **(A) Whitney's scholarly apparatus** (39 records) and **(B) datival infinitives** captured along with the PPP (9 records, 3 overlapping A). **STATUS: implemented** — apparatus pass = [`scripts/dcs/fix_ppp_apparatus_bleed.py`](../scripts/dcs/fix_ppp_apparatus_bleed.py); infinitive pass = [`scripts/dcs/fix_ppp_infinitives.py`](../scripts/dcs/fix_ppp_infinitives.py). All five original decisions plus (f) are resolved (§4). This doc is the record of what was done and why.

---

## 1. Summary & scope

### The source over-captured Whitney's "Verbal Nouns" column

Each lexicon record has a `ppp` array, extracted from the fixed-width column in [`Whitney_roots_class-PP.txt`](../Whitney_roots_class-PP.txt). That column reproduces Whitney's **"Verbal Nouns"** section, which contains the PPP **and** apparatus **and** (for some roots) **datival infinitives** — all of which bled into the array when the column was split on commas.

**(A) Scholarly apparatus**

| Apparatus kind | Looks like | Meaning |
|---|---|---|
| Period / text-of-attestation markers | `RV1`, `RV2`, `E1`, `C1`, `S1`, `B1`, `K`, `R`, `AA` | Text/period of attestation. **Provenance, not stem.** A bare trailing digit (`danta 1`) is a period-figure of the same family. |
| Uncertainty marker | `?` | Whitney's doubt about the form (`ajita ?`). |
| Alternate-form joiners | `&` (`turta & turna`), bare space (`vrdha brdha`) | Two genuine variant participles → **separate** elements. |
| Cross-reference / usage notes | `=`, `= seq. abhi`, `adj` | Cross-ref or "used adjectivally". |

**(B) Datival infinitives** (NOT apparatus, NOT OCR — genuine Sanskrit forms in the wrong field). Whitney lists datival infinitives (`-e`, `-aye`, `-vane`) in the same "Verbal Nouns" section, so they sit in `ppp`. Example — id **649 √riṣ**: warnemyr (following Whitney) records **"PPP : riṣṭá V.+ ; riṣé riṣés RV"**. ASCII-stripped that is exactly the source's `rista, rise rises`: `rista` = riṣṭá (PPP), **`rise` = riṣé, `rises` = riṣés** (RV datival infinitives). The earlier `apply_ppp_corrections.py` already removed a few `-tave`/`-dhyai` infinitives; this completes that work for the `-e`/`-aye`/`-vane` type (9 records, §2b).

### Distinct from the already-fixed "gloss bleed"

English **gloss** bleed was fixed for **6 records** by [`scripts/dcs/fix_ppp_gloss_bleed.py`](../scripts/dcs/fix_ppp_gloss_bleed.py) (19, 100, 182, 184, 347, 831). Those stay **untouched** here.

### Why it matters (two consumers)

1. **False ✗ chips** — [`src/renderers/detail.js`](../src/renderers/detail.js) `fold()` (lines 291–299) compares each `ppp` to the DCS corpus; `fold("kupita RV1")` and infinitives like `riṣé` never match the PPP corpus → false red ✗. Clean stems restore ✓.
2. **Inflated scoring** — [`src/core/analytics.js`](../src/core/analytics.js) line 23 `score += item.ppp.length * 2`; length must count only real PPP forms.

### Scope

- **45 distinct records**: **39** apparatus (§2) + **9** infinitive (§2b), **3 overlapping** (227, 472, 649). File: [`src/app_data.json`](../src/app_data.json), `lexicon` (935 entries).
- Apparatus records classified + adversarially verified (workflow `wf_75c62a06-764`). The infinitive set was found by [`scripts/dcs/scan_ppp_apparatus.py`](../scripts/dcs/scan_ppp_apparatus.py) (now detects `-e/-aye/-vane`) after the maintainer flagged that `rise rises` is not an error. Re-running that scanner on the fixed file reports **0** remaining.

---

## 2. Apparatus correction table (39 records)

`final ppp` = apparatus stripped, alternates split, **infinitives moved out** (rows 227, 472, 649 → §2b). Stripped markers/uncertainty/notes preserved per §4(a)/(b)/(d) in `ppp_attestation` / `ppp_uncertain` / `ppp_note`.

| id | root | current `ppp` | final `ppp` | treatment |
|---|---|---|---|---|
| 6 | aj | `["ajita ?"]` | `["ajita"]` | mechanical |
| 74 | ṛd | `["ardita ="]` | `["ardita"]` | editorial |
| 99 | kup | `["kupita RV1"]` | `["kupita"]` | mechanical |
| 140 | kṣā | `["ksana ?"]` | `["ksana"]` | mechanical |
| 168 | gadh | `["gadhita RV2"]` | `["gadhita"]` | mechanical |
| 227 | cit | `["citta", "cite ?", "citaye"]` | `["citta"]` → §2b | editorial |
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
| 472 | pṛc | `["prkta", "prgna ? RV1", "prce"]` | `["prkta", "prgna"]` → §2b | editorial |
| 524 | 1 bhuj | `["bhugna 1"]` | `["bhugna"]` | mechanical |
| 525 | 2 bhuj | `["bhugna 1"]` | `["bhugna"]` | mechanical |
| 573 | mṛkṣ | `["mraksita = seq. abhi"]` | `["mraksita"]` | editorial |
| 580 | mṛdh | `["mrddha 1"]` | `["mrddha"]` | mechanical |
| 632 | raś | `["rasita 1"]` | `["rasita"]` | mechanical |
| 633 | ras | `["rasita 1"]` | `["rasita"]` | mechanical |
| 649 | riṣ | `["rista", "rise rises"]` | `["rista"]` → §2b | editorial |
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

**`?`-uncertain forms** → `ppp_uncertain`: 6 `ajita`, 140 `ksana`, 322 `trsta`, 365 `duta`, 472 `prgna`, 668 `lagna`, 718 `vodha`, 790 `sukta`, 797/798/799 `surta`, 877 `snuta`; plus 227 `cite` (now an infinitive — the `?` flag is retained against that form).

**Non-collapse rule:** id 747 `vrdha brdha` is a genuine v-/b- variant PPP pair → split into two PPPs. Most space-separated tokens are apparatus — no blanket "split on space".

---

## 2b. Datival infinitive table (9 records)

Whitney's datival infinitives moved **out of `ppp`** into the new additive **`infinitives`** field (§4f). Source-literal ASCII; the true PPP stays in `ppp`. (3 records — 227, 472, 649 — are also in §2.)

| id | root | original `ppp` | final `ppp` | `infinitives` | also §2? |
|---|---|---|---|---|---|
| 227 | cit | `["citta", "cite ?", "citaye"]` | `["citta"]` | `["cite", "citaye"]` (`cite` `?`) | yes |
| 333 | tviṣ | `["tvisita", "tvise"]` | `["tvisita"]` | `["tvise"]` | no |
| 409 | dhvṛ | `["dhurta", "dhruta", "dhurvane"]` | `["dhurta", "dhruta"]` | `["dhurvane"]` | no |
| 472 | pṛc | `["prkta", "prgna ? RV1", "prce"]` | `["prkta", "prgna"]` | `["prce"]` | yes |
| 560 | mih | `["midha", "mihe"]` | `["midha"]` | `["mihe"]` | no |
| 568 | muh | `["mugdha", "mudha", "muhe"]` | `["mugdha", "mudha"]` | `["muhe"]` | no |
| 649 | riṣ | `["rista", "rise rises"]` | `["rista"]` | `["rise", "rises"]` | yes |
| 793 | śubh | `["subhita", "sumbhita", "subhe"]` | `["subhita", "sumbhita"]` | `["subhe"]` | no |
| 914 | hi | `["hita", "hye"]` | `["hita"]` | `["hye"]` | no |

IAST: cité/citáye, tviṣé, dhúrvaṇe, pṛcé, mihé, muhé, riṣé/riṣés, śubhé, hyé — all datival infinitives. `tvise/mihe/muhe/subhe/hye/dhurvane` look "clean", so only the `-e`/`-vane` ending betrays them.

---

## 3. Mechanical / editorial / infinitive split

- **Mechanical (24)**: 6, 99, 140, 168, 306, 326, 332, 343, 371, 372, 452, 524, 525, 580, 632, 633, 706, 708, 709, 718, 737, 790, 877, 892.
- **Editorial — apparatus (9)**: 74 (dangling `=`), 322 (`? adj`), 365 (`AA. ? C1`), 469, 470, 471 (`S1.` + real form `purita`), 573 (`= seq. abhi`), 668 (`B1.?` + `?`), 747 (`brdha` real alternate).
- **Infinitive move (9, incl. 3 overlap)**: 227, 333, 409, 472, 560, 568, 649, 793, 914.

---

## 4. Editorial decisions — RESOLVED (implemented)

- **(a) Period/source markers → PRESERVE** ✅ in additive `ppp_attestation` keyed by form (`"ppp_attestation": {"kupita": ["RV1"]}`).
- **(b) `?` uncertainty → PRESERVE** ✅ in `ppp_uncertain` (forms in §2; for 227 the `?` is on the infinitive `cite`).
- **(c) `&`/space alternates → SPLIT** ✅ (`&` always; bare space only for confirmed pairs, 747).
- **(d) `= seq.`/`adj` → METADATA** ✅ in `ppp_note`. **id 74 `ardita =`** has a **dangling** `=` (target truncated) → `ppp_note: {"ardita": "= (cross-ref target unrecovered)"}`; **NEEDS human print recovery** (Whitney print / Scharf digitization). Only open item.
- **(e) `rise rises` (id 649) → NOT OCR; they are infinitives** ✅ `rista` = riṣṭá (PPP); `rise`/`rises` = riṣé/riṣés → `infinitives` (not dropped). Confirmed against warnemyr "PPP : riṣṭá V.+ ; riṣé riṣés RV" and Scharf's Whitney digitization.
- **(f) Datival infinitives → MOVE to new additive `infinitives` field** ✅ (`"ppp": ["rista"], "infinitives": ["rise", "rises"]`). Consumer-safe.

---

## 5. Implementation (as built)

Two surgical, CRLF/BOM-preserving, idempotent passes (mirror [`fix_ppp_gloss_bleed.py`](../scripts/dcs/fix_ppp_gloss_bleed.py)):
1. [`scripts/dcs/fix_ppp_apparatus_bleed.py`](../scripts/dcs/fix_ppp_apparatus_bleed.py) — 39 apparatus records + `ppp_attestation`/`ppp_uncertain`/`ppp_note`.
2. [`scripts/dcs/fix_ppp_infinitives.py`](../scripts/dcs/fix_ppp_infinitives.py) — 9 infinitive records: move infinitives to `infinitives`, restore `rises` (649).

**File invariants preserved:** no BOM, CRLF, `ppp` elements at 8-space indent / closing `]` at 6-space, no trailing newline, **935** entries. Shared `ppp` text across records (371/372; 469/470/471; 708/709; 797/798/799) is disambiguated by anchoring on the unique `"id"` first.

**Verification (baked into both scripts):** no BOM; `json.loads` OK; 935 entries; each target id has its expected `ppp` (+ `infinitives`); **no `ppp` string anywhere ends in `-e`/`-aye`/`-vane`**; both scripts idempotent (second run = "Nothing to change"). [`scripts/dcs/scan_ppp_apparatus.py`](../scripts/dcs/scan_ppp_apparatus.py) reports **0** remaining.

**Consumers:** detail.js chips flip ✓ for affected roots; analytics.js `ppp.length` now counts only real PPPs. No `src/*.js` touched → no `node scripts/bundle.js` needed (app_data.json is fetched at runtime). Sidecars (`crosswalk/ppp_validation.json`, `src/participle_index*.json`, `src/reader_data.json`) untouched and unaffected.

---

## 6. Acceptance & out-of-scope

### Acceptance ✅
- [x] 45 records carry their final `ppp` (apparatus stripped, alternates split, infinitives moved).
- [x] No `ppp` string in the 45 contains a marker / `?` / `&` / `=` / `adj` / `seq.` or a datival-infinitive ending.
- [x] `ppp_attestation` / `ppp_uncertain` / `ppp_note` / `infinitives` populated and additive.
- [x] `infinitives` on the 9 §2b records (incl. 649 `["rise","rises"]` — `rises` restored).
- [x] `app_data.json` valid JSON, BOM-free, CRLF, 935 entries, no trailing newline.
- [x] Both scripts idempotent; scan reports 0.
- [x] The 6 gloss-bleed records untouched.

### Out of scope
- The 6 gloss-bleed records (already fixed).
- **Diacritic / vowel-length normalization** — source is ASCII (`ksana`, `vita`, `danta`); shipped source-literal, not the accented spine. Separate decision.
- **id 74's dangling `=` target** — needs Whitney print (§4d). Only open item.
- Inventing warnemyr "spine head" forms not in Whitney's column.
- Editing `crosswalk/ppp_validation.json` or any DCS sidecar.
