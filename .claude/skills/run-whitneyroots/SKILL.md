---
name: run-whitneyroots
description: >-
  Run, launch, serve, build, or screenshot the WhitneyRoots Sanskrit-root web apps headlessly —
  the Phase-5 "Why this form?" reader (reader/) and the v3 root explorer (index.html). Use when
  asked to run/start/preview/screenshot/smoke-test/drive WhitneyRoots or its reader in a browser.
---

# Run WhitneyRoots

WhitneyRoots is a **static, client-side web app** (no server, no build step, no deps at runtime):
a `python -m http.server` serves the repo and the browser does everything. Two surfaces share the
static root:

- **`reader/`** — the "Why this form?" reader: type/click a Sanskrit word → its Whitney root, gaṇa,
  grammar §§ (Wikisource links), MW/Apte sense, and DCS frequency. Loads `src/reader_data.json`.
- **`index.html` + `v3_app.js`** — the older v3 root-explorer (cards/list/quiz over `src/app_data.json`).

You drive it with **[.claude/skills/run-whitneyroots/driver.mjs](.claude/skills/run-whitneyroots/driver.mjs)**
— a Node + `playwright-core` harness that spawns the server, launches the **installed Chrome**
headless, runs a real flow (resolve tokens, click a homonym, screenshot), asserts, and cleans up.
(Paths below are relative to the repo root, `WhitneyRoots/`.)

## Prerequisites

- **Python 3** and **Node ≥ 18** on `PATH` (verified with Python 3.14, Node 24 on Windows).
- **Google Chrome** installed (the driver launches it via `channel: 'chrome'` — no browser download).
- Install the driver's one dependency (`playwright-core`, no bundled browser) **once**:

```bash
cd .claude/skills/run-whitneyroots
npm install
```

## Build

**None.** The site is static and the data it serves (`src/reader_data.json`, `crosswalk/`) is already
generated and committed. *Rebuilding the data from sources* is a separate offline pipeline
(`scratch/phase0/parse_warnemyr.py` → `fold_corpus` → `extract_dict_roots` → `dict_align` →
`build_form_section_edges` → `emit_crosswalk` → `build_reader_data.py`; needs the local `1885/`
warnemyr mirror and the `../VisualDCS` DCS sqlite) — **not needed to run the app**. See `.ai_state.md`.

## Run — agent path (use this)

From the skill directory, after `npm install`:

```bash
node driver.mjs            # drive reader/ : assert data + resolution, click a homonym, screenshot
node driver.mjs explorer   # drive index.html (the v3 explorer)
PORT=8751 node driver.mjs   # override the port (default 8733) if it's busy
```

It prints a probe line and writes a PNG to `.claude/skills/run-whitneyroots/screenshots/<page>.png`,
then exits `0` (all checks passed) or `1` (with the failing detail). The reader run asserts: 930 roots
loaded, `uvāca → vac#699`, `am → am#13` (exact — **not** merged with `√an`), `कांक्षति → kāṅkṣ#90`
(Devanagari anusvāra via the fold fallback), and that clicking a homonym token raises the chooser +
§§ panel. Verified output this session:

```
[driver] probe {"roots":930,"form_index":31451,"tokens":8,"uvaca":["vac#699"],"am":["am#13"],"deva":["kāṅkṣ#90"]}
[driver] clicked homonym token -> panel {"root":"kṛ","why":22,"chips":4}
[driver] OK — all checks passed
```

To poke it interactively, edit the `page.evaluate(...)` blocks in `driver.mjs` — the reader's
`candidatesFor(word)`, `norm()`, `nfold()`, and the `DATA` object are page globals (see Gotchas).

## Run — human path

Serve the repo root and open the reader in a browser (useless headless; for eyeballing only):

```bash
python -m http.server 8733 --directory .
# then open http://localhost:8733/reader/   (or /index.html for the explorer)
```

Stop with Ctrl-C. The server **must be rooted at the repo**, not at `reader/` — the reader fetches
`../src/reader_data.json`.

## Gotchas

- **`favicon.ico` 404 is benign** — the apps have no favicon, so the browser's automatic request
  404s. The driver filters it; do **not** broaden the error filter to treat it as a failure.
- **`reader.js` is a classic `<script>`, not a module** — so `candidatesFor`, `norm`, `nfold`, and
  `DATA` are real page globals, reachable from `page.evaluate(() => candidatesFor('am'))`. If it's
  ever switched to `type="module"`, that breaks and the driver must read them another way.
- **Two-tier lookup — don't "simplify" it.** `candidatesFor` tries the **exact** `form_index` first
  (`am → am#13`), then falls back to `fold_alias` (nasal-folded: m/n/ṅ/ñ/ṇ/anusvāra → n) only on a
  miss (`कांक्षति → kāṅkṣ`). Folding the exact index re-merges distinct roots (am/an, kram/kṛ).
- **Devanagari works only client-side**: `reader.js` transliterates it (`deva2iast`) before lookup;
  the Python-built index is IAST-only, so a Python-side lookup of Devanagari won't match.
- **`channel: 'chrome'` needs Google Chrome.** On a Chromium-/Edge-only machine, change it in
  `driver.mjs` to `'chromium'` / `'msedge'`, or pass `executablePath`.
- **Default port 8733** matches the repo's preview config. A stale server holding it makes the driver
  fail to bind — free it or use `PORT=`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Cannot find package 'playwright-core'` | `cd .claude/skills/run-whitneyroots && npm install` |
| `http.server never came up on :8733 (port in use?)` | A stale server holds the port: `PORT=8750 node driver.mjs`, or kill the process on 8733 |
| `Chromium distribution 'chrome' is not found` | Install Google Chrome, or edit `driver.mjs` `channel:'chrome'` → `'msedge'`/`'chromium'` or set `executablePath` |
| Driver "FAIL: page had console errors" | A *real* resource 404 or JS error (favicon is already excluded) — the message names the URL/exception |
| Reader shows "Could not load reader_data.json" | Server isn't rooted at the repo, or `src/reader_data.json` is missing — serve with `--directory .` and rebuild data if needed |
