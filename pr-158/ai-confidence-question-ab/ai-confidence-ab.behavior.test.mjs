import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const aHtml = fs.readFileSync(path.join(dir, 'a.html'), 'utf8');
const bHtml = fs.readFileSync(path.join(dir, 'b.html'), 'utf8');
const indexHtml = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
const readmeMd = fs.readFileSync(path.join(dir, 'README.md'), 'utf8');
const iphonePreviewMd = fs.readFileSync(path.join(dir, 'IPHONE_PREVIEW.md'), 'utf8');
const sharedCss = fs.readFileSync(path.join(dir, 'shared.css'), 'utf8');
const engineJs = fs.readFileSync(path.join(dir, 'scene-engine.js'), 'utf8');

function extractSceneBlock(html, id) {
  const marker = `data-id="${id}"`;
  const start = html.indexOf(marker);
  assert.ok(start !== -1, `could not find scene block with ${marker}`);
  const sectionStart = html.lastIndexOf('<section', start);
  const sectionEnd = html.indexOf('</section>', start) + '</section>'.length;
  return html.slice(sectionStart, sectionEnd);
}

// HTML comments in this project frequently *describe* a banned/absent
// pattern in prose (e.g. "no score/correct-answer sound") -- a bare
// substring match against the raw file would false-positive on that
// documentation, not on real rendered content. Strip comments before any
// "must not contain phrase X" check.
function stripHtmlComments(html) {
  return html.replace(/<!--[\s\S]*?-->/g, '');
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
  assert.ok(scenes.length >= 5, `${name}: expected at least 5 scenes (Opening + 4 content beats), found ${scenes.length}`);

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

// --- Shared Opening: A and B must share the exact same first two scenes
// (same markup, same timing) -- this is the one thing kept identical;
// everything after it is free to diverge structurally ---
assert.ok(aHtml.includes('空気中の酸素だけ'), 'A: missing the brief, small scientific-scope caption');
assert.ok(bHtml.includes('空気中の酸素だけ'), 'B: missing the brief, small scientific-scope caption');
assert.ok(aHtml.includes('もし、空気中の酸素が'), 'A: missing the shared subject question');
assert.ok(bHtml.includes('もし、空気中の酸素が'), 'B: missing the shared subject question');

for (const id of ['open-world', 'open-question']) {
  const aBlock = extractSceneBlock(aHtml, id).replace(/data-id="[^"]+"/, 'data-id="X"');
  const bBlock = extractSceneBlock(bHtml, id).replace(/data-id="[^"]+"/, 'data-id="X"');
  assert.equal(aBlock, bBlock, `A and B must share byte-identical "${id}" Opening scene content/timing`);
}

// --- A: Question-led Short -- no choices, ends on an open question, never
// asserts a resolved answer ---
assert.ok(!aHtml.includes('choice-stack'), 'A: must not contain a choice-stack (no choices allowed in A)');
assert.ok(!aHtml.includes('choice-pill'), 'A: must not contain any choice-pill (no choices allowed in A)');
assert.ok(aHtml.includes('何が') && aHtml.includes('？'), 'A: missing an open-ended closing question');

// --- B: Quiz-led Short -- 2-3 grounded choices, a genuine judgment pause
// before a quiet, color-only Reveal, and a causal-insight closing line
// (never just "the answer is X") ---
assert.ok(bHtml.includes('choice-stack'), 'B: missing choice-stack');
const choicePillCount = (bHtml.match(/class="choice-pill/g) || []).length;
assert.ok(choicePillCount >= 2 && choicePillCount <= 3, `B: expected 2-3 choice-pill elements, found ${choicePillCount}`);

// Check each choice-pill's own OPENING TAG only (not its whole nested
// subtree, which would make a naive "next </div>" search land on an inner
// nested div instead of the pill's own close) for data-reveal-at.
const choicePillOpenTags = bHtml.match(/<div class="choice-pill"[^>]*>/g) || [];
assert.equal(
  choicePillOpenTags.length,
  choicePillCount,
  'B: choice-pill opening-tag count does not match choice-pill class-attribute count (unexpected markup shape)'
);
const revealAttrsInChoices = choicePillOpenTags.filter((tag) => /data-reveal-at="[\d.]+"/.test(tag));
assert.equal(
  revealAttrsInChoices.length,
  1,
  `B: exactly one choice-pill may carry data-reveal-at (the correct answer) -- found ${revealAttrsInChoices.length}, so either no Reveal exists or the answer is pre-marked on more than one option`
);

const revealMatch = revealAttrsInChoices[0].match(/data-reveal-at="([\d.]+)"/);
assert.ok(revealMatch, 'B: missing data-reveal-at on the Reveal target (no Reveal mechanism found)');
const revealAt = parseFloat(revealMatch[1]);
const bChoiceScene = extractScenes(bHtml).find((s) => s.id === 'b4-choice');
assert.ok(bChoiceScene, 'B: missing the b4-choice scene');
assert.ok(
  revealAt - bChoiceScene.start >= 2,
  `B: Reveal must land at least 2s into the choice scene (a genuine 判断の間), found ${revealAt - bChoiceScene.start}s`
);
assert.ok(
  revealAt < bChoiceScene.end,
  'B: Reveal must land before the choice scene ends, so the reveal is actually visible'
);

// The Reveal must be a quiet class-toggle only -- no textual "correct/
// incorrect" label anywhere, and the closing line must be a causal sentence,
// not a bare "answer is X" statement.
assert.ok(bHtml.includes('から。'), 'B: missing a causal-insight closing sentence (expected a "...から。" causal clause)');
const bHtmlNoComments = stripHtmlComments(bHtml);
for (const forbidden of ['正解', '不正解', 'スコア', 'Score', 'ポイント', '報酬', '得点']) {
  assert.ok(!bHtmlNoComments.includes(forbidden), `B: must not contain score/correctness/reward label "${forbidden}" in rendered content (comments are exempt)`);
}

// --- Old theme must not linger as *live content* in the playable variants.
// index.html is allowed one brief historical mention (why the theme
// changed, recorded per CLAUDE.md Section 9 "Memory") -- that is a record,
// not a lingering old theme. ---
for (const [name, html] of [['A', aHtml], ['B', bHtml]]) {
  assert.ok(!html.includes('これは100％正しいです'), `${name}: old "AI confidence" theme declaration line must not remain`);
  assert.ok(!html.includes('AI Confidence'), `${name}: old theme name "AI Confidence" must not remain`);
}
assert.ok(!indexHtml.includes('これは100％正しいです'), 'index: old "AI confidence" theme declaration line must not remain');

// --- Retired review vocabulary must never appear in the CEO-facing review
// surfaces (index.html, IPHONE_PREVIEW.md) ---
for (const [name, text] of [['index.html', stripHtmlComments(indexHtml)], ['IPHONE_PREVIEW.md', iphonePreviewMd]]) {
  for (const retired of ['違和感', 'FARLENSらしい', '世界観']) {
    assert.ok(!text.includes(retired), `${name}: retired review vocabulary "${retired}" must not appear`);
  }
}

// --- CEO Review must be reduced to exactly the 4 specified questions ---
const REQUIRED_REVIEW_QUESTIONS = [
  '問い先行',
  '続きを見たい',
  '親として',
  '視覚的に魅力',
];
for (const q of REQUIRED_REVIEW_QUESTIONS) {
  assert.ok(indexHtml.includes(q), `index.html: missing required CEO review question containing "${q}"`);
}
// A crude upper bound: the review-questions list itself should contain
// exactly 4 <li> items, so no extra question silently crept back in.
const reviewListMatch = indexHtml.match(/<ol>([\s\S]*?)<\/ol>/);
assert.ok(reviewListMatch, 'index.html: missing the review questions <ol> list');
const reviewListItemCount = (reviewListMatch[1].match(/<li>/g) || []).length;
assert.equal(reviewListItemCount, 4, `index.html: review questions list must contain exactly 4 items, found ${reviewListItemCount}`);

// --- Shared major Asset set: both variants must reference every required
// visual-density category from the CEO spec ---
const REQUIRED_ASSET_CLASSES = [
  'ground',
  'city-skyline',
  'air-layer',
  'o2-particle',
  'person-figure',
  'animal-figure',
  'vehicle',
  'flame',
  'time-dial',
  'bg-decoration',
  'layer-back',
  'layer-mid',
  'layer-front',
];
for (const [name, html] of [['A', aHtml], ['B', bHtml]]) {
  for (const cls of REQUIRED_ASSET_CLASSES) {
    assert.ok(html.includes(cls), `${name}: missing required shared asset class "${cls}"`);
  }
}

// --- At least one scene per variant must co-present >= 3 of the "actor"
// object types (person/animal/vehicle/flame) together ---
for (const [name, html] of [['A', aHtml], ['B', bHtml]]) {
  const sceneBodies = html.split('<section class="scene"').slice(1);
  const hasCoPresentScene = sceneBodies.some((body) => {
    const types = ['person-figure', 'animal-figure', 'vehicle', 'flame'];
    return types.filter((t) => body.includes(t)).length >= 3;
  });
  assert.ok(hasCoPresentScene, `${name}: no single scene co-presents >= 3 of person/animal/vehicle/flame`);
}

// --- Shared Color/Font/Sound conditions: both variants load the same
// shared.css and scene-engine.js, and neither hardcodes a divergent font ---
for (const [name, html] of [['A', aHtml], ['B', bHtml]]) {
  assert.ok(html.includes('href="shared.css"'), `${name}: must load the shared Color/Font stylesheet`);
  assert.ok(html.includes('src="scene-engine.js"'), `${name}: must load the shared timeline/sound engine`);
  assert.ok(!/font-family\s*:/.test(html), `${name}: must not declare its own font-family (must rely solely on shared.css)`);
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
for (const [name, html] of [['A', aHtml], ['B', bHtml], ['index', indexHtml], ['README', readmeMd]]) {
  const clean = stripHtmlComments(html);
  for (const phrase of BANNED_PHRASES) {
    assert.ok(!clean.includes(phrase), `${name}: must not contain banned promotional phrase "${phrase}" in rendered content (comments are exempt)`);
  }
}

// --- No external network dependency anywhere ---
for (const [name, html] of [['A', aHtml], ['B', bHtml], ['index', indexHtml]]) {
  assert.ok(!/\s(src|href)\s*=\s*"https?:\/\//.test(html), `${name}: must not reference any external http(s) resource`);
  assert.ok(!/@import/.test(html), `${name}: must not @import any external stylesheet/font`);
}
assert.ok(!/@import/.test(sharedCss), 'shared.css: must not @import anything external');
assert.ok(!/url\(\s*["']?https?:\/\//.test(sharedCss), 'shared.css: must not reference an external url() asset');
assert.ok(!/https?:\/\//.test(engineJs), 'scene-engine.js: must not reference any external URL');
assert.ok(!/\bfetch\(/.test(engineJs), 'scene-engine.js: must not perform any network fetch');

// --- Engine mechanisms this revision depends on must actually exist ---
assert.ok(/data-hide-from/.test(engineJs) && /data-hide-until/.test(engineJs), 'scene-engine.js: missing the data-hide-from/-until (is-hidden-now) mechanism');
assert.ok(/sweep\s*:\s*function/.test(engineJs), 'scene-engine.js: missing the sweep() tone method used for the O2-vanish sound cue');
assert.ok(/item\.tone/.test(engineJs), 'scene-engine.js: missing the per-reveal data-tone chime mechanism used for the quiz Reveal');

// --- README.md: research must be recorded with Confirmed / Reasonable
// inference / Not confirmed tiers and real Source URLs, per topic ---
for (const tier of ['Confirmed', 'Reasonable inference', 'Not confirmed']) {
  assert.ok(readmeMd.includes(tier), `README.md: missing evidence tier "${tier}"`);
}
const sourceUrlCount = (readmeMd.match(/https:\/\/(www\.)?(nasa|noaa|scied\.ucar|pmc\.ncbi\.nlm\.nih|sandiego)\.[a-z.]+/g) || []).length;
assert.ok(sourceUrlCount >= 4, `README.md: expected at least 4 institutional source URLs (NASA/NOAA/UCAR/NCBI/public institution), found ${sourceUrlCount}`);
for (const requiredTopic of ['atmospheric', 'combustion', 'engine', '空の色', '5 second']) {
  assert.ok(readmeMd.toLowerCase().includes(requiredTopic.toLowerCase()), `README.md: missing required research topic reference "${requiredTopic}"`);
}
assert.ok(/not\s+promoted?\s+to\s+Canonical|not\s+promoted\s+by\s+this\s+Prototype|not become FARLENS's Canonical/i.test(readmeMd), 'README.md: missing explicit "not yet Canonical" statement for the Production Grammar hypothesis');

console.log('ai-confidence-question-ab behavior: ok');
