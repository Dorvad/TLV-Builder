#!/usr/bin/env node
/**
 * TLV Builder smoke tests (source-level invariants)
 * - funds baseline
 * - unlock baseline
 * - milestone baseline
 * - reset behavior guard
 */
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
  console.error('❌ Could not find inline <script> in index.html');
  process.exit(1);
}
const script = scriptMatch[1];

function extract(re, label) {
  const m = script.match(re);
  if (!m) throw new Error(`Missing ${label}`);
  return m[0];
}

const BUILDINGS_SRC = extract(/const BUILDINGS = {[\s\S]*?^};/m, 'BUILDINGS');
const MILESTONES_SRC = extract(/const MILESTONES = \[[\s\S]*?^\];/m, 'MILESTONES');
const CREATE_STATE_SRC = extract(/function createState\(\) {[\s\S]*?^}/m, 'createState');

const harness = `
${BUILDINGS_SRC}
${MILESTONES_SRC}
${CREATE_STATE_SRC}
this.__exports = { BUILDINGS, MILESTONES, createState };
`;

const context = { console };
vm.createContext(context);
vm.runInContext(harness, context, { filename: 'smoke-harness.js' });

const { BUILDINGS, MILESTONES, createState } = context.__exports;
const state = createState();

const failures = [];

if (state.funds !== 800) failures.push(`Expected starting funds=800, got ${state.funds}`);
if (state.totalEarned !== 0) failures.push(`Expected totalEarned=0, got ${state.totalEarned}`);

const expectedUnlocked = ['bauhaus_block', 'hipster_loft', 'cafe', 'falafel_stand', 'park'];
for (const key of expectedUnlocked) {
  if (!state.unlocked.has(key)) failures.push(`Missing initial unlock: ${key}`);
}

for (const [key, def] of Object.entries(BUILDINGS)) {
  if (def.unlocked === true && !state.unlocked.has(key)) {
    failures.push(`Definition says unlocked=true but missing in state.unlocked: ${key}`);
  }
}

const funds500 = MILESTONES.find(m => m.id === 'funds_500');
if (!funds500) {
  failures.push('Missing milestone funds_500');
} else if (funds500.check(state) !== false) {
  failures.push('funds_500 should be false at initial state (totalEarned baseline)');
}

if (!script.includes('prevUnlockedSize=STATE.unlocked.size;')) {
  failures.push('Reset behavior missing prevUnlockedSize synchronization');
}

if (failures.length > 0) {
  console.error('❌ Smoke tests failed:');
  for (const f of failures) console.error(` - ${f}`);
  process.exit(1);
}

console.log('✅ Smoke tests passed');
console.log(' - Starting funds baseline is correct');
console.log(' - Earned-funds baseline is correct');
console.log(' - Initial unlocks are consistent with definitions');
console.log(' - funds_500 milestone baseline is correct');
console.log(' - Reset handler keeps unlock notifier baseline in sync');
