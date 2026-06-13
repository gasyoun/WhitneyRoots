// run-whitneyroots driver — serve the static site with `python -m http.server` and drive it in
// headless Chrome via playwright-core (uses the system Chrome; no browser download).
//
//   node driver.mjs            # drive the reader/ (Phase-5 "Why this form?" view) — default
//   node driver.mjs explorer   # drive index.html (the v3 root-explorer app)
//   PORT=8750 node driver.mjs  # override the port
//
// Spawns the server, drives one real flow, asserts, writes a PNG to ./screenshots/, cleans up.
// Exits 0 on success, non-zero (with the failing detail) otherwise.
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SKILL_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(SKILL_DIR, '..', '..', '..');          // .../WhitneyRoots
const PORT = Number(process.env.PORT) || 8733;
const PAGE = (process.argv[2] || 'reader').toLowerCase();
const URLPATH = PAGE === 'explorer' ? '/index.html' : '/reader/';
const URL = `http://127.0.0.1:${PORT}${URLPATH}`;
const SHOTDIR = path.join(SKILL_DIR, 'screenshots');
const SHOT = path.join(SHOTDIR, `${PAGE}.png`);
const PY = process.platform === 'win32' ? 'python' : 'python3';
mkdirSync(SHOTDIR, { recursive: true });
const log = (...a) => console.log('[driver]', ...a);

const server = spawn(PY, ['-m', 'http.server', String(PORT), '--directory', REPO], { stdio: 'ignore' });
let browser, failed = null;
try {
  for (let i = 0; ; i++) {                                       // wait for the server
    try { await fetch(`http://127.0.0.1:${PORT}/`); break; } catch { /* not up yet */ }
    if (i > 50) throw new Error(`http.server never came up on :${PORT} (port in use? PORT=NNNN to change)`);
    await sleep(200);
  }
  log(`server up on :${PORT}`);
  browser = await chromium.launch({ channel: 'chrome' });        // installed Chrome; no download
  const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push('JS: ' + e));                       // real JS exceptions
  page.on('response', (r) => {                                                // real missing resources (with URL)
    if (r.status() >= 400 && !r.url().endsWith('/favicon.ico')) errors.push(`HTTP ${r.status()} ${r.url()}`);
  });
  page.on('console', (m) => {                                                 // other console errors (skip the
    if (m.type() === 'error' && !/favicon|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text());
  });                                                                         // generic favicon-404 noise)
  await page.goto(URL, { waitUntil: 'networkidle' });

  if (PAGE === 'reader') {
    const probe = await page.evaluate(() => {
      const names = (a) => a.map((n) => DATA.roots[n].root + '#' + n);
      return {
        roots: DATA._meta.roots,
        form_index: DATA._meta.form_index_keys,
        tokens: document.querySelectorAll('.tok').length,
        uvaca: names(candidatesFor('uvāca')),         // exact single root
        am: names(candidatesFor('am')),               // exact precision (must NOT include √an)
        deva: names(candidatesFor('कांक्षति')),         // Devanagari anusvāra via fold fallback
      };
    });
    log('probe', JSON.stringify(probe));
    await page.click('.tok.multi');                              // a homonym-chooser token (kṛtvā / gacchati)
    const panel = await page.evaluate(() => ({
      root: (document.querySelector('.root-head .rt') || {}).textContent,
      why: document.querySelectorAll('.why a').length,
      chips: document.querySelectorAll('.chooser .chip').length,
    }));
    log('clicked homonym token -> panel', JSON.stringify(panel));
    const checks = {
      'data loaded (930 roots)': probe.roots === 930,
      'tokens rendered': probe.tokens >= 8,
      'uvāca -> √vac': probe.uvaca.join() === 'vac#699',
      'am exact (no √an merge)': probe.am.join() === 'am#13',
      'Devanagari kāṅkṣ via fold': probe.deva.some((x) => x.startsWith('kāṅkṣ')),
      'homonym panel has §§ + chooser': panel.why > 0 && panel.chips >= 2,
    };
    const bad = Object.entries(checks).filter(([, v]) => !v).map(([k]) => k);
    if (bad.length) failed = 'reader assertions failed: ' + bad.join('; ');
  } else {
    const probe = await page.evaluate(() => ({
      title: document.title,
      app: !!document.querySelector('#app, .app, main, body > *'),
    }));
    log('explorer probe', JSON.stringify(probe));
    if (!probe.app) failed = 'explorer did not render any app content';
  }

  await page.screenshot({ path: SHOT });
  log('screenshot ->', SHOT);
  if (errors.length) { log('CONSOLE ERRORS:', errors); failed ||= 'page had console errors'; }
} catch (e) {
  failed = e.message || String(e);
} finally {
  if (browser) await browser.close().catch(() => {});
  server.kill();
}

if (failed) { console.error('[driver] FAIL:', failed); process.exit(1); }
log('OK — all checks passed');
