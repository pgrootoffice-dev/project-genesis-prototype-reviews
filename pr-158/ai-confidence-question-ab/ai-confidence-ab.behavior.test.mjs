import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const aHtml = fs.readFileSync(path.join(dir, 'a.html'), 'utf8');
const bHtml = fs.readFileSync(path.join(dir, 'b.html'), 'utf8');
const indexHtml = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');

function extractSceneBlock(html, id) {
  const marker = `data-id="${id}"`;
  const start = html.indexOf(marker);
  assert.ok(start !== -1, `could not find scene block with ${marker}`);
  const sectionStart = html.lastIndexOf('<section', start);
  const sectionEnd = html.indexOf('</section>', start) + '</section>'.length;
  return html.slice(sectionStart, sectionEnd);
}

function extractScenes(html) {
  const scenes = [];
  const sceneRegex = /<section class="scene"[^>]*data-id="([^"]+)"[^>]*data-start="([\d.]+)"[^>]*data-end="([\d.]+)"/g;
  let match;
  while ((match = sceneRegex.exec(html)) !== null) {
    scenes.push({ id: match[1], start: parseFloat(match[2]), end: parseFloat(match[3]) });
  }
  return scenes;
}

// --- Duration: each variant must land inside the required 10-15.5s window,
// with contiguous (no gap, no overlap) scene timing ---
for (const [name, html] of [['A', aHtml], ['B', bHtml]]) {
  const scenes = extractScenes(html);
  assert.ok(scenes.length >= 3, `${name}: expected at least 3 scenes, found ${scenes.length}`);

  const total = Math.max(...scenes.map((s) => s.end));
  assert.ok(total >= 10 && total <= 15.5, `${name}: total duration ${total}s must be within 10-15.5s`);

  const sorted = [...scenes].sort((a, b) => a.start - b.start);
  for (let i = 1; i < sorted.length; i += 1) {
    assert.equal(
      sorted[i].start,
      sorted[i - 1].end,
      `${name}: scene ${i} must start exactly where scene ${i - 1} ends (found gap/overlap)`
    );
  }
  assert.equal(sorted[0].start, 0, `${name}: first scene must start at 0`);
}

// --- Shared opening condition: A and B must share the exact same first
// scene markup (same declaration line, same timing) -- this is the one
// thing kept identical; everything after it is free to diverge structurally ---
assert.ok(aHtml.includes('これは100％正しいです。'), 'A: missing shared AI declaration line');
assert.ok(bHtml.includes('これは100％正しいです。'), 'B: missing shared AI declaration line');
const aOpeningBlock = extractSceneBlock(aHtml, 'a1-declare');
const bOpeningBlock = extractSceneBlock(bHtml, 'b1-declare');
assert.equal(
  aOpeningBlock.replace(/data-id="a1-declare"/, 'data-id="X"'),
  bOpeningBlock.replace(/data-id="b1-declare"/, 'data-id="X"'),
  'A and B must share byte-identical opening scene content/timing (only the data-id differs)'
);

// --- A: Question-led Short -- no choices, no explanation-style conclusion,
// ends on an open prompt, never asserts a resolved answer ---
assert.ok(!aHtml.includes('choice-row'), 'A: must not contain a choice-row (no choices allowed in A)');
assert.ok(!aHtml.includes('choice-pill'), 'A: must not contain any choice-pill (no choices allowed in A)');
assert.ok(aHtml.includes('君なら'), 'A: missing the open prompt "君なら、どう確かめる？"');
for (const explanatoryPhrase of ['だから、根拠を確かめよう', '未来をつくるのは', '確かめよう。']) {
  assert.ok(!aHtml.includes(explanatoryPhrase), `A: must not contain explanation-style conclusion phrase "${explanatoryPhrase}"`);
}

// --- B: Quiz-led Short -- exactly two choices, a genuine judgment pause
// before the Reveal, and a Reveal that lands on "根拠を確かめる" ---
assert.ok(bHtml.includes('choice-row'), 'B: missing choice-row');
const choicePillCount = (bHtml.match(/class="choice-pill/g) || []).length;
assert.equal(choicePillCount, 2, `B: expected exactly 2 choice-pill elements, found ${choicePillCount}`);
assert.ok(bHtml.includes('すぐ信じる'), 'B: missing first choice candidate');
assert.ok(bHtml.includes('根拠を確かめる'), 'B: missing second choice candidate / Reveal target');

const revealMatch = bHtml.match(/data-reveal-at="([\d.]+)"/);
assert.ok(revealMatch, 'B: missing data-reveal-at on the Reveal target (no Reveal mechanism found)');
const revealAt = parseFloat(revealMatch[1]);
const bChoiceScene = extractScenes(bHtml).find((s) => s.id === 'b3-choice');
assert.ok(bChoiceScene, 'B: missing the b3-choice scene');
assert.ok(
  revealAt - bChoiceScene.start >= 2.5,
  `B: Reveal must land at least 2.5s into the choice scene (a genuine 判断の間), found ${revealAt - bChoiceScene.start}s`
);
assert.ok(
  revealAt < bChoiceScene.end,
  'B: Reveal must land before the choice scene ends, so the reveal is actually visible'
);

assert.ok(bHtml.includes('自信と正しさは'), 'B: missing the closing Reveal insight line');
for (const forbidden of ['正解', '不正解', 'スコア', 'Score', 'ポイント', '報酬']) {
  assert.ok(!bHtml.includes(forbidden), `B: must not contain score/correctness/reward label "${forbidden}"`);
}

// --- Old variant names must not linger anywhere ---
for (const [name, html] of [['A', aHtml], ['B', bHtml], ['index', indexHtml]]) {
  assert.ok(!html.includes('Explanation-led'), `${name}: old variant name "Explanation-led" must not remain`);
  assert.ok(!html.includes('Question-led Choice'), `${name}: old variant name "Question-led Choice" must not remain`);
}

// --- Banned promotional / outcome-guarantee phrases (any file) ---
const BANNED_PHRASES = [
  'ハーバード',
  '東大',
  '合格',
  '頭が良くな',
  '偏差値',
  'IQ',
];
for (const [name, html] of [['A', aHtml], ['B', bHtml], ['index', indexHtml]]) {
  for (const phrase of BANNED_PHRASES) {
    assert.ok(!html.includes(phrase), `${name}: must not contain banned promotional phrase "${phrase}"`);
  }
}

// --- No external network dependency: no http(s):// src/href anywhere in the
// three pages (fonts, images, audio, scripts must all be local/self-contained) ---
for (const [name, html] of [['A', aHtml], ['B', bHtml], ['index', indexHtml]]) {
  assert.ok(!/\s(src|href)\s*=\s*"https?:\/\//.test(html), `${name}: must not reference any external http(s) resource`);
  assert.ok(!/@import/.test(html), `${name}: must not @import any external stylesheet/font`);
}

// --- shared.css must not @import or url() an external font/asset either ---
const sharedCss = fs.readFileSync(path.join(dir, 'shared.css'), 'utf8');
assert.ok(!/@import/.test(sharedCss), 'shared.css: must not @import anything external');
assert.ok(!/url\(\s*["']?https?:\/\//.test(sharedCss), 'shared.css: must not reference an external url() asset');

// --- scene-engine.js must not fetch or load any external resource ---
const engineJs = fs.readFileSync(path.join(dir, 'scene-engine.js'), 'utf8');
assert.ok(!/https?:\/\//.test(engineJs), 'scene-engine.js: must not reference any external URL');
assert.ok(!/\bfetch\(/.test(engineJs), 'scene-engine.js: must not perform any network fetch');

console.log('ai-confidence-question-ab behavior: ok');
