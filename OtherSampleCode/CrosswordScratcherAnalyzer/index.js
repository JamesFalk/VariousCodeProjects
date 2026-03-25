#!/usr/bin/env node
// === CROSSWORD SCRATCHER ANALYZER v2 ===
// Node.js 24+ | Termux | 1.5M sims | Progress bar
const fs = require('fs');
const path = require('path');

// === CONFIG: EDIT WORDS FROM TICKET ===
const WORDS = {
  3: ["RAT", "TEA", "RED", "ICE"],
  4: ["BEAN", "TWO", "NEED", "BOOK", "BEST"],
  5: ["CHEF", "CHESS", "BATHS"],
  6: ["EATING", "ACROSS", "BATTLE"],
  7: ["CLEANER"],
  8: ["EXCESSIVE", "ENGINEER"],
  9: ["BACTERIA"]
};

const PRIZE_MULTIPLIER = {
  0: 0, 1: 1, 2: 2, 3: 3, 4: 5, 5: 10, 6: 15, 7: 20, 8: 40, 9: 50,
  10: 100, 11: 500, 12: 1000, 13: 5000, 14: 10000
};

const SIMULATIONS = 1_500_000;
const CALL_LETTERS = 18;
const PROGRESS_INTERVAL = 100_000;

// Pre-process words
function wordToReq(w) {
  const req = {};
  for (const c of w) {
    const n = c.charCodeAt(0) - 64;
    req[n] = (req[n] || 0) + 1;
  }
  return req;
}
const ALL_REQS = Object.values(WORDS).flat().map(wordToReq);

// Shuffle 1-26, take 18
const fullDeck = Array.from({length: 26}, (_,i) => i+1);
function draw18() {
  const deck = fullDeck.slice();
  for (let i = deck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }
  return deck.slice(0, CALL_LETTERS).reduce((a,n) => (a[n] = (a[n]||0)+1, a), {});
}

// Main
console.log(`\nStarting ${SIMULATIONS.toLocaleString()} simulations...`);
const hits = {};
let nextLog = PROGRESS_INTERVAL;

for (let i = 0; i < SIMULATIONS; i++) {
  const available = draw18();
  let completed = 0;
  for (const req of ALL_REQS) {
    if (Object.entries(req).every(([n,need]) => (available[n]||0) >= need)) {
      completed++;
    }
  }
  const mult = PRIZE_MULTIPLIER[completed] || 0;
  hits[mult] = (hits[mult] || 0) + 1;

  if (i + 1 === nextLog) {
    console.log(`Progress: ${((i+1)/SIMULATIONS*100).toFixed(1)}%`);
    nextLog += PROGRESS_INTERVAL;
  }
}

// === RESULTS ===
const results = [];
results.push("=== CROSSWORD SCRATCHER PROBABILITIES ===");
results.push(`Simulations: ${SIMULATIONS.toLocaleString()}`);
results.push(`Call Letters: ${CALL_LETTERS}`);
results.push("");
results.push("Prize    % of Tickets    Hits");
results.push("--------------------------------");

for (const mult of Object.keys(hits).map(Number).sort((a,b)=>a-b)) {
  const pct = (hits[mult] / SIMULATIONS * 100).toFixed(4);
  results.push(`${mult.toString().padStart(4)}x    ${pct.padStart(8)}%    ${hits[mult].toLocaleString().padStart(8)}`);
}

const output = results.join('\n') + '\n';
console.log('\n' + output);

// Save to file
const outFile = path.join(process.cwd(), 'results.txt');
fs.writeFileSync(outFile, output);
console.log(`Results saved to: ${outFile}`);
console.log(`Open with any text app!`);
