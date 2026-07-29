import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const aHtml = fs.readFileSync(path.join(dir, 'a.html'), 'utf8');
const bHtml = fs.readFileSync(path.join(dir, 'b.html'), 'utf8');
const indexHtml = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');

const ENDING_LINE = '未来をつくるのは、<br />答えを知る人ではなく、<br />確かめられる人。';

function extractScenes(html) {
  const scenes = [];
  const sceneRegex = /<section class="scene"[^>]*data-start="([\d.]+)"[^>]*data-end="([\d.]+)"/g;
  let match;
  while ((match = sceneRegex.exec(html)) !== null) {
    scenes.push({ start: parseFloat(match[1]), end: parseFloat(match[2]) });
  }
  return scenes;
}

// --- Duration: each variant must land inside the required 10-15s window ---
for (const [name, html] of [['A', aHtml], ['B', bHtml]]) {
  const scenes = extractScenes(html);
  assert.ok(scenes.length >= 3, `${name}: expected at least 3 scenes, found ${scenes.length}`);

  const total = Math.max(...scenes.map((s) => s.end));
  assert.ok(total >= 10 && total <= 15.5, `${name}: total duration ${total}s must be within 10-15s (small overrun tolerance to 15.5s)`);

  // Scenes must be contiguous (no gap, no overlap) so the whole timeline is
  // always covered by exactly one active scene.
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

// --- Shared script elements: both variants open with the same AI line and
// close with the exact same Ending line, per the task's common-script rule ---
for (const [name, html] of [['A', aHtml], ['B', bHtml]]) {
  assert.ok(html.includes('これは100％正しいです。'), `${name}: missing shared AI declaration line`);
  assert.ok(html.includes(ENDING_LINE), `${name}: missing exact shared Ending line`);
}

// --- B-specific: two choice candidates present, no score/correctness label ---
assert.ok(bHtml.includes('すぐ信じる'), 'B: missing first choice candidate');
assert.ok(bHtml.includes('確かめる'), 'B: missing second choice candidate');
for (const forbidden of ['正解', '不正解', 'スコア', 'Score', 'ポイント']) {
  assert.ok(!bHtml.includes(forbidden), `B: must not contain score/correctness label "${forbidden}"`);
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
