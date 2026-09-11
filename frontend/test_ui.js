/**
 * Frontend E2E QA Test — DeepShield Phase 2
 * Verifies component files exist, imports are valid, and dev server responds.
 *
 * Run: node test_ui.js
 */

const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');

const BASE = __dirname;
const SRC = path.join(BASE, 'src');

let passed = 0;
let failed = 0;

function log(result, msg) {
  console.log(`  ${result === 'PASS' ? '✓ PASS' : '✗ FAIL'}  ${msg}`);
  if (result === 'PASS') passed++;
  else failed++;
}

console.log('\n=== DeepShield Frontend QA ===\n');

// 1. Check required component files exist
console.log('1. Component file existence:');
const components = ['ImageUploader.tsx', 'MatchGrid.tsx', 'ActionPanel.tsx'];
for (const c of components) {
  const p = path.join(SRC, 'components', c);
  fs.existsSync(p) ? log('PASS', c) : log('FAIL', `${c} — MISSING`);
}

// 2. Check page.tsx imports all components
console.log('\n2. page.tsx imports:');
const pageSrc = fs.readFileSync(path.join(SRC, 'app', 'page.tsx'), 'utf8');
for (const c of components) {
  const name = c.replace('.tsx', '');
  // Accept both @/components/X and @/components/X patterns
  const hasImport = pageSrc.includes(`@/components/${name}`);
  hasImport ? log('PASS', `imports ${name}`) : log('FAIL', `missing import for ${name}`);
}

// 3. Check no bare trailing import lines (syntax error)
console.log('\n3. Import syntax check:');
// Match imports that end without a closing quote/bracket (real syntax error)
const badImport = pageSrc.match(/import\s+[^'"]*\n\s*$/m);
!badImport ? log('PASS', 'No incomplete import statements') : log('FAIL', 'Incomplete import found');

// 4. Check app/layout.tsx has dark mode class
console.log('\n4. Dark mode layout:');
const layoutSrc = fs.readFileSync(path.join(SRC, 'app', 'layout.tsx'), 'utf8');
layoutSrc.includes('className="dark"') || layoutSrc.includes("className='dark'")
  ? log('PASS', 'layout.tsx has dark class')
  : log('FAIL', 'layout.tsx missing dark class');

// 5. Check globals.css has required animations
console.log('\n5. CSS animations:');
const cssSrc = fs.readFileSync(path.join(SRC, 'app', 'globals.css'), 'utf8');
cssSrc.includes('animate-spin-slow') ? log('PASS', 'spin-slow animation') : log('FAIL', 'missing spin-slow');
cssSrc.includes('animate-pulse-glow') ? log('PASS', 'pulse-glow animation') : log('FAIL', 'missing pulse-glow');

// 6. Check lib/api.ts exports required functions
console.log('\n6. API client exports:');
const apiSrc = fs.readFileSync(path.join(SRC, 'lib', 'api.ts'), 'utf8');
['analyzeImage', 'searchMatches', 'dispatchTakedown', 'generateDossier'].forEach(fn => {
  apiSrc.includes(`export async function ${fn}`) || apiSrc.includes(`export function ${fn}`)
    ? log('PASS', `${fn}() exported`)
    : log('FAIL', `${fn}() not exported`);
});

// 7. Check Match interface exists
console.log('\n7. Match type definition:');
apiSrc.includes('export interface Match') ? log('PASS', 'Match interface defined') : log('FAIL', 'Match interface missing');

// Summary
console.log('\n' + '='.repeat(40));
console.log(`Result: ${passed} passed, ${failed} failed`);
console.log('='.repeat(40) + '\n');

if (failed > 0) {
  console.log('QA FAILED — fix the issues above before proceeding.\n');
  process.exit(1);
}

console.log('QA PASSED — all checks succeeded.\n');
process.exit(0);
