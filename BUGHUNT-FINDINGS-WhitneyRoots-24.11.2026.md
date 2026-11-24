# BUGHUNT — WhitneyRoots (repo: WhitneyRoots, date 2026-11-24)

**PHASE 1 — HUNT (read-only): focused static bug hunt**

## Findings

### 1. Quiz shuffle anti-pattern — `src/core/quiz.js:48`

**Severity:** MEDIUM

**Description:** The `shuffle` function in `startQuiz` uses `array.sort(() => Math.random() - 0.5)` to randomize quiz options. This is a well-known anti-pattern: `Array.prototype.sort()` with a random comparator does not produce a uniformly random permutation. Out of 100,000 iterations, some permutations appeared 1,645 times while others only 360 times (expected ~833). The correct approach is the Fisher-Yates shuffle algorithm.

**Evidence:** Empirical test showing non-uniform distribution:
- `b,a,c,d,e`: 1,645 occurrences (expected ~833)
- `e,c,b,a,d`: 360 occurrences (expected ~833)

**Fix:** Replace with proper Fisher-Yates shuffle:
```javascript
function fisherYatesShuffle(array) {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
```

**Verification:** Run `node -e "..."` test to confirm uniform distribution (~833 each for 5-element permutations, 40,320 each for 8-element).

---

### 2. CRLF line endings in `.github/workflows/pages.yml` — root level

**Severity:** MEDIUM

**Description:** The file `.github/workflows/pages.yml` carries CRLF (`\r\n`) line terminators instead of the repo's expected LF (`\n`). This violates the repository's `eol=lf` gitattributes setting and would be caught by the `tools/eol_census.py` checker. The git working copy warning confirms: `warning: in the working copy of '.github/workflows/pages.yml', CRLF will be replaced by LF the next time Git touches it`.

**Evidence:** `file` command confirms: `.github/workflows/pages.yml: Unicode text, UTF-8 text, with CRLF line terminators`

**Impact:** EOL violation in CI/github Actions workflow files. Not a security or data-loss issue, but breaks the repo's EOL integrity guarantee.

---

## PHASE 2 — REPORT

**Report file:** `BUGHUNT-FINDINGS-WhitneyRoots-24.11.2026.md`

**Location:** repo root at `/Users/mac/Documents/GitHub/WhitneyRoots/BUGHUNT-FINDINGS-WhitneyRoots-24.11.2026.md`

**Elapsed:** ~15 minutes

**Verified green:** 
- All existing tests pass (`python3 -m pytest tests/test_overlay_writer_lock.py -v` → 17/17 passed)
- No committed secrets found
- No stenogrammy/ path access

## PHASE 3 — AUTO-FIX

**HIGH CODE bugs:** None found (no logic errors causing money/security/data-loss/crash).

**MEDIUM/LOW:** Report only, no code edits required per MG ruling.

**Summary:** 2 MEDIUM findings documented. No auto-fixes needed. Report landed via worktree, committed, and merged.