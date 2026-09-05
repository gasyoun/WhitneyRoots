_Created: 10-06-2026 · Last updated: 05-09-2026_

# PPP Correction Plan

> **Historical (June 2026) — kept for provenance.** This analysis seeded the PPP
> correction track; execution has since moved on. The apparatus-bleed arm is
> **fully drained** (`python scripts/dcs/scan_ppp_apparatus.py` reports
> `0 apparatus-bleed records` as of 18-07-2026) via the idempotent
> `scripts/dcs/fix_ppp_*` family; current operator guidance lives in
> [docs/BUILD_MANUAL.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/BUILD_MANUAL.md)
> and the live queues in
> [docs/DECISIONS_NEEDED.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md).
> The verdict counts below describe the June snapshot, not today's data.

_Based on validation of 208 Whitney Roots PPP entries against DCS corpus._

## Executive Summary

**Of 208 PPP entries in Whitney Roots:**
- **50 ATTESTED** (24%) — Present in corpus, valid ✓
- **76 LIKELY_ERROR** (37%) — Morphologically suspect, recommend removal/correction ⚠️
- **12 SUSPICIOUS** (6%) — High-frequency roots with missing forms, probable errors ⚠️
- **27 UNCERTAIN** (13%) — Moderate frequency, needs linguistic review
- **88 PLAUSIBLE_GAP** (42%) — Low-frequency roots where absence is plausible ✓

**Action items: 88 entries (76 likely errors + 12 suspicious) require correction or removal**

---

## Category 1: LIKELY_ERROR (76 entries) — Recommend Removal/Correction

These 76 entries have morphological problems:

### INVALID_MORPH (95% error likelihood) — Remove immediately
- **śak (767)**: `saktave` (ends -ve after -ta, impossible)
- **vastave** pattern: ta+ve is not valid Sanskrit morphology
- **Recommendation**: Remove these entries from Roots source

### UNCERTAIN_ENDING (50% error likelihood) — Investigate & Correct
- **jan (249)**: `janitos, janitvi` — these endings (-tos, -tvi) are not standard PPP
  - Correct form should be: `janita` (from √jan + -ta)
  
- **labh (673)**: `labdhva, labhya` — -va and -ya endings after -ta are suspicious
  - Correct form should be: `labdha` (from √labh + -ta)
  
- **bhuj (524-525)**: `bhugna 1` — ends -na, but notation "1" appended suggests data error
  - Correct form should be: `bhagna` (from √bhuj + -ta)

- **Recommendation**: Correct these to standard -ta/-na PPP forms (likely extraction errors from source)

---

## Category 2: SUSPICIOUS (12 entries) — Very High Frequency, Unattested Forms

These roots appear 1000+ times in corpus but listed PPP never appears:

| Root | Tokens | Listed PPP | Issue |
|------|--------|-----------|-------|
| dā (×3) | 12,008 | `tta` | **PARTIAL STEM** — should be `dātta` not `tta` alone |
| han | 8,744 | `ghata` | Not attested despite 8.7K tokens; likely Vedic-only or error |
| vad | 3,914 | `vadita` | Not attested despite 3.9K tokens; check if form is correct |
| kṣip | 2,461 | `ksipita` | Not attested; may be poetic/rare |
| tyaj | 2,417 | `tyajita` | Not attested; may be poetic/rare |
| tap | 2,065 | `tapita` | Not attested; may be poetic/rare |
| pṛ | 1,512 | `prta, purita` | Not attested; check both forms |

### dā (349-351) — Highest Priority

**Current entry**: `tta`
**Problem**: This is clearly a **partial stem**. The suffix "-tta" was extracted without the root.
**Expected form**: `dātta` (from √dā + -ta)
**Action**: Replace `tta` with `dātta` across all 3 entries (1 dā, 2 dā, 3 dā)

### han, vad, kṣip, tyaj, tap — Medium Priority

These forms are morphologically clean (standard -ta ending) but never attested in 1000+ token sample. Possibilities:
1. **Real but Vedic/rare**: form exists but only in Vedic texts (excluded from DCS)
2. **Source error**: form was incorrectly listed in Whitney Roots
3. **Undiscovered variant**: form exists but masked by sandhi in corpus

**Recommendation**: Cross-check against Whitney Grammar §-chapters for PPP formation. User to validate with Zalizniak authority.

---

## Category 3: UNCERTAIN (27 entries) — Moderate Frequency, Morphologically Sound

These are morphologically valid but low-frequency roots (100-1000 tokens) with unattested PPP.

**Recommendation**: Lower priority. Plausible that PPP is simply rare in corpus. Validate linguistically if needed.

---

## Category 4: PLAUSIBLE_GAP (88 entries) — Acceptable

Low-frequency roots (<100 tokens) where absence of PPP in corpus is plausible.

**Recommendation**: Accept as-is. These roots may simply have no PPP forms in DCS corpus.

---

## Immediate Actions Required

### Phase A: Data Correction (High Confidence)

1. **dā entries (349, 350, 351)**: Replace `tta` → `dātta`
   - Fixes the partial stem extraction error
   
2. **INVALID_MORPH entries (~5-10)**: Remove forms ending in impossible patterns
   - e.g., `vastave`, `saktave`, forms ending in -ve or -os after -ta

### Phase B: Linguistic Review (Needs Authority)

Use Whitney Grammar (§ chapters on PPP formation) to validate:
- han's `ghata`: Check if this is the attested form or if it should be `hata`
- vad's `vadita`: Check PPP formation for class-I roots
- kṣip's `ksipita`: Check class-VI root PPP patterns
- Other high-frequency suspicious forms (pṛ, tap, tyaj, kṣubh, etc.)

### Phase C: Source Cleanup (Later)

Correct the UNCERTAIN_ENDING entries (50% error likelihood):
- Standardize janitos → janita
- Standardize labdhva → labdha
- etc.

---

## Summary of Changes

| Category | Count | Action | Priority |
|----------|-------|--------|----------|
| ATTESTED | 50 | Keep ✓ | — |
| INVALID_MORPH | ~5-10 | Remove | HIGH |
| dā partial stem | 3 | Replace tta→dātta | HIGH |
| SUSPICIOUS high-freq | 9 | Validate vs. Grammar | MEDIUM |
| UNCERTAIN_ENDING | ~50-60 | Correct to standard form | MEDIUM |
| PLAUSIBLE_GAP | 88 | Keep (low-freq OK) | — |

**Net result**: ~88 entries require correction or removal (42% of list)

_Dr. Mārcis Gasūns_
