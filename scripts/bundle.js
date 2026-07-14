/**
 * @file bundle.js
 * @description WhitneyRoots Modular Build Script
 */

const fs = require('fs');
const path = require('path');

const VERSION = "1.0.0-whitney";
const OUTPUT_FILE = path.join(__dirname, '../v3_app.js');

const FILES_ORDER = [
  'core/state.js',
  'core/data.js',
  'core/search.js',
  'core/router.js',
  'core/quiz.js',
  'core/analytics.js',
  'core/achievements.js',
  'core/ai.js',
  'utils/dom.js',
  // Vendored sanskrit-util (js/index.mjs re-copied verbatim, see ../SHARED_CODE.md §1-2) — must
  // precede utils/linguistics.js so its plain functions/consts are already in bundle scope by the
  // time linguistics.js's stripped import line would otherwise leave them undefined.
  'vendor/sanskrit-util.js',
  'utils/linguistics.js',
  'renderers/cards.js',
  'renderers/lists.js',
  'renderers/quiz.js',
  'renderers/detail.js',
  'renderers/affixes.js',
  'entry.js'
];

console.log(`📦 Bundling WhitneyRoots ${VERSION}...`);

let combinedContent = `/**
 * WhitneyRoots v3 Bundle
 * Generated: ${new Date().toISOString()}
 */
`;

FILES_ORDER.forEach(file => {
  const filePath = path.join(__dirname, '../src', file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    // Remove imports/exports for bundle
    const cleaned = content
      .replace(/import\s+.*?\s+from\s+['"].*?['"];?/g, '')
      .replace(/export\s+default\s+\{[\s\S]*?\};\s*$/m, '')  // drop multi-line default-export objects (e.g. vendor/sanskrit-util.js) — mirrors sanskrit-util/js/build-global.mjs's own strip
      .replace(/export\s+const\s+/g, 'const ')
      .replace(/export\s+function\s+/g, 'function ')
      .replace(/export\s+default\s+/g, '');
      
    combinedContent += `\n// --- FILE: ${file} ---\n${cleaned}\n`;
    console.log(`  + ${file}`);
  } else {
    console.warn(`  ! Missing: ${file}`);
  }
});

fs.writeFileSync(OUTPUT_FILE, combinedContent);
console.log(`✅ Successfully bundled to ${OUTPUT_FILE}`);
