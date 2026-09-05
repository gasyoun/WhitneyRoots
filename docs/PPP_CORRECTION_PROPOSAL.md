_Created: 15-06-2026 · Last updated: 05-09-2026_

# PPP Correction Proposal — Queue B/C residual (Whitney-§-cited)

_Generated 2026-06-15 by the `ppp-correction-proposal` workflow (39 agents: per-form **verify** + **adversarial refute**), grounded in Whitney's *Sanskrit Grammar* §§952–993 (Wikisource-verified this session, see [DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) §3). **Nothing here is applied** — this is a proposal over the `ppp` arrays in [src/app_data.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/app_data.json), to apply once the external actor's in-flight apparatus/infinitive PRs (the #12/#13 line) settle._

**Scope:** the suspect PPP forms still present on `origin/main` *after* PRs #12 (apparatus bleed) and #13 (infinitives) — i.e. the residual the mechanical scripts missed (re-derived live from `origin/main:src/app_data.json`, not the stale `ppp_source_validation.md`).

**Headline — 19 forms judged across 17 records:**
- **14 to drop** — 12 infinitive/gerund bleed (`-tos`/`-tum`/`-tvī`, §§968/970/989) + `han ghata` (not a PPP) + `dā dātta` (a manufactured long-ā form). In every case the genuine PPP is already present, so nothing is invented.
- **4 KEEP** — Whitney-attested seṭ `-ita` doublets the stale `-tos/-tum/-tvī` heuristic over-flagged (`kṣip`, `tap`, `tyaj`, `vad`); no edit.
- **1 HOLD** — `pṛ purita`: the adversarial reviewer **overturned** an over-eager "correct→purta" (it is a genuine spine-head PPP) → human review.

18 of 19 verdicts were unanimous (verify + skeptic agree); the 1 dispute is §5.

---

### A. REMOVE — infinitive / gerund bleed (not PPPs)

Forms ending `-tos`/`-tum`/`-tvī` (§§968/970/989–991) that slipped past PR #13. In every case the genuine PPP is already present in the array and is retained.

| id(s) | root | remove | current ppp → corrected ppp | Whitney § | conf |
|---|---|---|---|---|---|
| 69 | √ṛ | `artos` | `["rta","arna","artos"]` → `["rta","arna"]` | §970 (gen. `-tos` of tu-noun = datival inf.) | high |
| 249 | √jan | `janitos` | `["jata","janitos","janitvi"]` → `["jata"]` | §970 (Whitney's own `-tos` example) | high |
| 249 | √jan | `janitvi` | (same array) | §989–991 / §993 (Vedic gerund `-tvī`) | high |
| 262 | √juṣ | `justvi` | `["justa","justa","justvi"]` → `["justa"]`\* | §989–991 / §993b (`-tvī`) | high |
| 545 | √mad | `maditos` | `["matta","madita","maditos"]` → `["matta","madita"]` | §970 (`maditos B.` = inf. gen.) | high |
| 561 | √mī | `metos` | `["mita","metos"]` → `["mita"]` | §970 (`me-tos`, gen. of `me-tu`) | high |
| 735 | √viṣ | `vistvi` | `["vista","vistvi"]` → `["vista"]` | §989–991 (`viṣṭvī`) | high |
| 743 | √vṛj | `vrktvi` | `["vrkta","vrktvi","vrjya"]` → `["vrkta"]`† | §989–991 (`vṛktvī`) | high |
| 846 | √su | `tos` | `["suta","tos"]` → `["suta"]` | §970 (truncated `-tos` fragment of `sotos`) | high |
| 878 | √spand | `spanditum` | `["spandita","spanditum"]` → `["spandita"]` | §968 (Whitney's own model inf. `spanditum`) | high |
| 921 | √hū | `hvayitum` | `["huta","hvayitum"]` → `["huta"]` | §968 (`hvay-i-tum`, inf. of √hve) | high |
| 936 | √hval | `hvalitos` | `["hvalita","hvalitos"]` → `["hvalita"]` | §970 (`hválitos ŚB.`, root-accent inf.) | high |
| 908 | √han | `ghata` | `["hata","ghata"]` → `["hata"]` | §954 (PPP is `hatá`; `ghata` is not a √han PPP) | high |

\* §262 also carries a **duplicate `justa`** — out of scope for these verdicts; flag for a dedup pass (final should be `["justa"]`).
† §743 `vrjya` (= `vṛjya`, the `-ya` gerund §989–991) is also a non-PPP but was not the adjudicated suspect; flag for follow-up (likely → `["vrkta"]`).

---

### B. KEEP — Whitney-attested seṭ / variant (the stale heuristic over-flagged these)

`-ita` forms the `-tos/-tum/-tvī` heuristic should never have touched; each is an explicit Whitney seṭ doublet or later-language variant. **No edit.**

| id | root | form | Whitney § + quote |
|---|---|---|---|
| 143 | √kṣip | `ksipita` (= kṣipita) | §956b.4 — "occasionally kṣip, gup, tap, dṛp, vap, çap"; spine: "PPP : kṣiptá V.+ , kṣipita S." |
| 296 | √tap | `tapita` | §956b.4 — "occasionally kṣip, gup, tap, dṛp, vap, çap"; spine: "PPP : taptá V.+ , tapita C." |
| 324 | √tyaj | `tyajita` | §956b.2 — "also tyaj and mṛj in late texts (usually tyaktá and mṛṣṭá)"; spine: "PPP : tyaktá B.+ , tyajita C." |
| 704 | √vad | `vadita` | §956d — "uditá (also vadita in the later language)" |
| 545 | √mad | `madita` | §956b.3 — "mad has both mattá and maditá" (retained in the §A row above) |

---

### C. CORRECT / genuine issues

| id(s) | root | form | recommendation | Whitney § | open question |
|---|---|---|---|---|---|
| 349/350/351 | √dā | `dātta` | **DROP** (delete, not string-rewrite) → `["data","datta"]` | §955f / §952 / §957a | Long-ā double-`tt` `dātta` is non-attested in Whitney (the string occurs only in `udātta`/`anudātta`, §81). Canonical `datta` (§952) is already at index 1, so a rewrite would **duplicate**. The original `tta` was Whitney's genuine abbreviated compounding form (`ā́tta`, `prátta`, §955f/§957a); `scripts/dcs/apply_ppp_corrections.py:76-86` manufactured the spurious `dātta` from it. Matches [DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) §3c. **Faithful action = drop `dātta`.** (If a long-ā Vedic form is ever wanted, the real one is `dāta`, single t.) |
| 469/470/471 | √pṛ "fill" | `purita` | **HOLD — human review** (see §5) | §957b | adversarial dispute below |

---

### 5. Adversarial dispute (the one non-unanimous verdict) — human review required

**√pṛ `purita` (ids 469/470/471).** The verifier proposed **CORRECT `purita` → `purta`** (reasoning: §957b "pūrṇá (√pṛ fill: also pūrtá and pṛta)" looks exhaustive; no seṭ `-ita` for √pṛ; `purita` = apparatus-garbled `pūrtá`). The skeptic **refuted this (counter-verdict KEEP):**

- The warnemyr spine head (`1885/root_1_p_r.html`) reads verbatim: **"PPP : pūrṇá V.+ , pṛta S 1 . pūrita ; Inf : pūritum R. ; Abs : pūrtvā"** — so `pūrita` is a **genuine spine-head PPP**, listed separately from the inf. `pūritum` and abs. `pūrtvā`.
- The apparatus marker `S1` was **already attached to `prta`** (`ppp_attestation {"prta":["S1"]}`), leaving `purita` clean — it is **not** the contaminant.
- warnemyr lists **no `pūrta` at all**, so the "correction" would **delete a real spine-head PPP and add one the spine never lists**.
- `docs/PPP_APPARATUS_BLEED_WORKLIST.md:115` independently classifies 469/470/471 as "`S1.` + real form `purita`"; MW corroborates a later-language `-pūrita` (`pari-/prati-/pra-/sam-pūrita`).

**Resolution needed:** KEEP `purita` (skeptic) vs CORRECT→`purta` (verifier). The skeptic's case is stronger (spine-head attestation + worklist + the marker already stripped). **Provisional disposition: KEEP `purita`**; separately consider *adding* the Whitney-grammar `pūrta` (§957b) as an additive, not a correction. **Do not auto-apply** — escalate to maintainer ([DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) §3).

---

### 6. How to apply

- All edits target the **`ppp` arrays in [src/app_data.json](https://github.com/gasyoun/WhitneyRoots/blob/main/src/app_data.json)** only. No source-table, grammar, or crosswalk edits (those are audit-trail, judged separately).
- **§A (13 removals) + `dā dātta` drop:** mechanical array-element deletions; the retained PPP is already present in every case, so no form is invented.
- **§B (4 KEEPs):** no-ops; recorded so the stale `-tos/-tum/-tvī` heuristic does not re-flag them.
- **§C `pṛ purita`:** **hold** pending the §5 dispute.
- **Coordination:** the external actor has **in-flight apparatus/infinitive PRs (the #12/#13 line)**. **Hold these edits until those settle** to avoid array-index collisions / re-flagging churn; re-verify each array against `origin/main` immediately before applying (some forms may already be removed upstream).
- **Follow-ups flagged (out of scope here):** duplicate `justa` in id 262; `-ya` gerund `vrjya` in id 743 — a separate dedup/gerund pass.

_Dr. Mārcis Gasūns_
