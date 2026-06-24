// One-off: verify the #v1/affixes view (cards grouped by function, productivity bars,
// click-to-expand anubandha + examples). Reuses the driver's server+Chrome boilerplate.
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SKILL_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(SKILL_DIR, '..', '..', '..');
const PORT = Number(process.env.PORT) || 8744;
const URL = `http://127.0.0.1:${PORT}/index.html#v1/affixes`;
const SHOT = path.join(SKILL_DIR, 'screenshots', 'affixes.png');
const PY = process.platform === 'win32' ? 'python' : 'python3';
mkdirSync(path.dirname(SHOT), { recursive: true });
const log = (...a) => console.log('[affix]', ...a);

const server = spawn(PY, ['-m', 'http.server', String(PORT), '--directory', REPO], { stdio: 'ignore' });
let browser, failed = null;
try {
  for (let i = 0; ; i++) {
    try { await fetch(`http://127.0.0.1:${PORT}/`); break; } catch {}
    if (i > 50) throw new Error(`http.server never came up on :${PORT}`);
    await sleep(200);
  }
  browser = await chromium.launch({ channel: 'chrome' });
  const page = await browser.newPage({ viewport: { width: 1000, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push('JS: ' + e));
  page.on('response', r => { if (r.status() >= 400 && !r.url().endsWith('/favicon.ico')) errors.push(`HTTP ${r.status()} ${r.url()}`); });
  page.on('console', m => { if (m.type() === 'error' && !/favicon|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForSelector('.affix-card', { timeout: 5000 });
  const before = await page.evaluate(() => ({
    groups: document.querySelectorAll('.affix-group').length,
    cards: document.querySelectorAll('.affix-card').length,
    firstGroup: (document.querySelector('.affix-group-title') || {}).textContent,
    firstSurface: (document.querySelector('.affix-surface') || {}).textContent,
    hasBar: !!document.querySelector('.affix-bar-fill'),
  }));
  log('rendered', JSON.stringify(before));
  await page.click('.affix-card');                          // expand the first card
  await sleep(150);
  const after = await page.evaluate(() => ({
    details: document.querySelectorAll('.affix-detail').length,
    steps: document.querySelectorAll('.affix-step').length,
    examples: document.querySelectorAll('.affix-ex').length,
  }));
  log('after click', JSON.stringify(after));
  await page.screenshot({ path: SHOT, fullPage: true });
  log('screenshot ->', SHOT);

  const checks = {
    'groups rendered': before.groups >= 8,
    'cards rendered': before.cards >= 20,
    'productivity bar present': before.hasBar,
    'click expands detail': after.details === 1,
    'anubandha steps shown': after.steps >= 1,
    'examples shown': after.examples >= 1,
  };
  const bad = Object.entries(checks).filter(([, v]) => !v).map(([k]) => k);
  if (bad.length) failed = 'affix assertions failed: ' + bad.join('; ');
  if (errors.length) { log('CONSOLE ERRORS:', errors); failed ||= 'page had console errors'; }
} catch (e) {
  failed = e.message || String(e);
} finally {
  if (browser) await browser.close().catch(() => {});
  server.kill();
}
if (failed) { console.error('[affix] FAIL:', failed); process.exit(1); }
log('OK — all affix-view checks passed');
