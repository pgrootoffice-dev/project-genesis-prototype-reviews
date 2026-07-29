# AI Confidence Question — A/B Visual Test (Explanation-led vs. Question-led Choice)

Status: NON-CANONICAL WORKING PROTOTYPE
Date: 2026-07-29
Prototype ID: `FRL-P-0002` (informal, parallels `FRL-P-0001`/`FRL-R-NNNN` convention)

Related records:

- `../../docs/genesis-os/education-adventure-ip/research/FRL-R-0004-kurzgesagt-one-screen-one-meaning.md` — the Research Entry whose candidate Production Grammar hypotheses this Prototype tests
- `../../docs/genesis-os/education-adventure-ip/research/README.md` — FARLENS Research Lab (Promotion Path)
- `../../docs/genesis-os/ACTIVE_DIRECTION.md` — Creator Intelligence, Reference Diversity Rule, "Next Content Prototype" conditions
- `../../docs/genesis-os/DO_NOT_RESTORE.md` — retired directions this Prototype does not touch
- `../../docs/genesis-os/education-adventure-ip/FARLENS_VISUAL_DESIGN_RULEBOOK.md`, `FARLENS_VISUAL_SYSTEM_BLUEPRINT.md`
- `../research-two-beat-reveal/` — the existing `prototypes/` placement and GitHub Pages review convention this Prototype reuses (no new mechanism introduced)

## Purpose

This is **not a finished product**. It is a small, disposable Visual Test comparing two structural approaches to the same 10-15 second educational Short, so the CEO can react to a real, playable comparison rather than a description. It exists to test candidate Production Grammar from `FRL-R-0004` (itself still Preliminary/unconfirmed by direct video observation) against FARLENS's own original material — the Prototype does not depend on `FRL-R-0004`'s hypotheses being true; it is a fresh, first-hand test of the same underlying ideas using FARLENS's own Visual Core.

## Educational Theme

Central question: 「AIが『100％正しい』と言ったら、信じる？」

Capability exercised: Evidence checking, critical thinking, separating Confidence from Correctness, suspending judgment, thinking for oneself while using AI as a tool.

**This is explicitly not "AI is untrustworthy."** Both variants teach: AI is a powerful tool; a confident answer can still be wrong; checking evidence is a habit worth building; a person makes the final judgment. No claim about grades, exam outcomes, school admission, or intelligence increase appears anywhere in either variant — enforced by an automated check, see "What Was Built" below.

## What Was Built

Two ~10-15 second, silent-by-default, vertical (9:16) HTML/CSS/JS "Short" simulations sharing one Color Set, font stack, and scene-timeline engine — same medium and mechanism as the existing `research-two-beat-reveal` Prototype (static, self-contained, no server, no build step).

- **`a.html` — A: Explanation-led** (~14.3s). Narration-style captions explain in order: AI declares confidently → even confidence can be wrong → so check the evidence → Ending. Fully passive viewing; no pause, no choice.
- **`b.html` — B: Question-led Choice** (~13.4s). Same opening line, then a real question is posed to the viewer, then two candidate judgments ("すぐ信じる" / "確かめる") appear together with neither highlighted and are held on screen for a genuine ~2.9-second pause — the "one-moment judgment" beat — before the meaning quietly lands on "確かめる" (a soft outline, never a score or a red/green correct-incorrect mark) and the Ending appears.
- **`index.html`** — the CEO-facing comparison page: both variants embedded side by side (stacked on narrow viewports), a one-line description of what differs, and links to open each standalone.
- **`shared.css`** — the Prototype-only Color Set, typography, phone-frame chrome, and every shape used by both variants (see "Visual System" below).
- **`scene-engine.js`** — a small, dependency-free timeline runner: every scene is pre-authored as static HTML (`<section class="scene" data-start="…" data-end="…">`), and the engine only toggles which one is `.is-active` at the current playhead time, drives the progress bar, and (muted by default) triggers short synthesized tones via the Web Audio API. Nothing is built dynamically — the entire script and its timing is directly readable from `a.html`/`b.html`'s own source.
- **`ai-confidence-ab.behavior.test.mjs`** — an automated, dependency-free Node check (run by `.github/workflows/living-storybook-preview.yml`, same as every other Prototype's `*.behavior.test.mjs`) asserting: each variant's total duration is 10-15.5s, scenes are contiguous with no gap/overlap, both variants share the exact same opening line and exact same Ending line, B contains no score/correct-incorrect label, none of the three pages contain a banned promotional phrase (ハーバード/東大/合格/頭が良くなる/偏差値/IQ), and none of the three pages or `shared.css`/`scene-engine.js` reference any external network resource.

### Explicitly not interactive / not a branching prototype

Both `a.html` and `b.html` autoplay linearly from start to end. The only buttons are Play/Replay and an optional sound toggle — there is no click-to-choose, no branching path, and no state that depends on a viewer's tap. B's "choice" is something the viewer experiences by watching (a held pause showing two options, then the meaning lands), the same way an actual YouTube Short poses a question without requiring the viewer to tap anything. This is a deliberate design constraint, not an oversight: `DO_NOT_RESTORE.md` item 5/9 retires browser choice-branching interaction as FARLENS's production medium; this Prototype tests a **video-medium** structural difference instead, consistent with `ACTIVE_DIRECTION.md`'s YouTube-premised direction.

## Visual System (Prototype-only hypothesis)

### Color Set — NOT Canonical, NOT Kurzgesagt's palette

| Role | Hex | Meaning |
| --- | --- | --- |
| Background | `#17262c` | calm, dark, non-alarming base |
| Background (soft) | `#1f343c` | cards, one step lighter |
| Subject | `#f5efe3` | AI core, child silhouette — one consistent warm tone |
| Accent | `#e8a33d` | AI's confident assertion (amber, not red) |
| Signal | `#4fb0a5` | evidence / verification (muted teal-green) |
| Caution | `#d97a4e` | uncertainty only — a muted coral, never a saturated alarm red, never paired with black |

Deliberately different from Kurzgesagt's widely-reported general palette (deep blues/purples with bright reds/oranges/yellow): this set uses a teal-navy base rather than blue-purple, no saturated red anywhere, and every color is assigned exactly one meaning role rather than used decoratively (`FARLENS_VISUAL_DESIGN_RULEBOOK.md` Section 3). **This Color Set is a Prototype-limited hypothesis and does not become FARLENS's Canonical Palette from this Prototype alone.**

### Shapes (Semantic Geometry) — original, not references to any specific work

- **AI** — a rounded-square "core" with a pulsing outline ring (computation), containing only the text "AI". No face, no eyes, no bird/creature form.
- **Child / viewer** — an intentionally minimal circle-head + rounded-body silhouette, a single flat tone, no limbs, no face — deliberately not Kurzgesagt's specific round-body/stick-limb/eye-dot character construction.
- **Confident assertion** — a speech bubble (rounded rectangle + tail).
- **Evidence / verify** — a rounded card with a stroke-drawn checkmark (generic UI language, not a magnifying glass or any distinctive icon).
- **Uncertainty** — a small, softened caution triangle (rounded joins, not a sharp alarm form).
- **Judgment candidates** — two plain pill shapes, no icon, no character.

### Typography

System font stack only (`-apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Noto Sans JP", system-ui, sans-serif`) — no bundled or CDN-loaded font of any kind, so there is no font-license question and no possibility of matching a specific reference's typeface. Bold weight for the AI declaration and Ending lines; medium weight for supporting captions; both variants share the exact same font stack so the A/B comparison is never confounded by a typography difference.

### Sound

Silent by default (matches the existing `research-two-beat-reveal` precedent and the task's own "無音でもよい" allowance). A muted-by-default 🔇 toggle exists on both variants and, if unmuted, plays a small number of short, purely synthesized sine-wave tones generated at runtime via the Web Audio API (`scene-engine.js`'s `createTonePlayer`) — no audio file of any kind is loaded, recorded, sourced, or copied from anywhere. This was chosen specifically because (a) no licensed music/SE source is available in this environment, (b) adding a new paid audio service or API is explicitly forbidden (`CLAUDE.md` Decision Level 3 / Section 6), and (c) iOS Safari generally cannot autoplay unmuted audio without a user gesture regardless, so a default-muted state is the correct behavior, not a workaround.

## Production Grammar Tested (from `FRL-R-0004`, treated here as untested hypotheses re-tested fresh)

- **One Moment, One Cognitive Focus** — each scene in both variants carries exactly one idea.
- **Static-first, Motion-selective** — only meaningful elements move (AI core pulse, checkmark draw-in, pill emphasis); no whole-screen motion.
- **Progressive Visual Disclosure** — B's two choice pills, then the landing caption, appear in sequence, never all at once; A's four beats replace each other one at a time.
- **Semantic Geometry** — every shape (see above) exists to carry a specific meaning, not decoration.
- **Emotionally Safe Complexity** — no red/black alarm pairing, no "AI is scary" framing; the caution beat in A is a single small, softened icon, not a screen-wide warning.
- **Typography as Visual System** — captions are sized/weighted by role (declaration vs. supporting caption vs. Ending), not uniform body text.

## What Was Fixed After Visual Self-Review (real findings, not assumed-correct on first attempt)

Two genuine bugs were found by actually taking timestamped screenshots via headless Chromium at a mobile viewport (not by reading the HTML/CSS source alone) and are recorded here because they directly bear on the Production Grammar being tested:

1. **Scene crossfade double-exposure.** The original CSS let an outgoing scene's caption still be mid-fade-out while the incoming scene's caption was already fading in, so for roughly half a second two different captions were both partially legible at once — the opposite of "one concept fully clears before the next appears," which is exactly one of the candidate principles this Prototype exists to test. Fixed by giving the "leaving" state a fast, undelayed fade-out and the "entering" state a `transition-delay` long enough to only start once the previous scene has fully cleared (verified directly: a screenshot mid-transition now shows only the incoming scene's content).
2. **B's choice pills never appeared at all.** A CSS rule was missing entirely (`.scene.is-active .choice-pill` had no matching activation rule), so "すぐ信じる"/"確かめる" silently stayed at `opacity: 0` for the whole scene — caught only by screenshot, not by reading the CSS, since the file looked complete on inspection. Fixed by adding the missing rule.
3. **B's emphasis timing was firing before the scene was even visible.** The emphasis used a CSS `animation` on a class present in the static markup from page load, so its `animation-delay` counted from page load, not from when the B3 scene actually became active — the "held pause before the meaning lands" was landing during an earlier, invisible scene, so by the time B3 appeared the emphasis had already resolved. Fixed by using the correct absolute time (`data-start` + intended in-scene delay) and documented inline in `b.html` with the underlying `animation-delay`-is-absolute vs. `transition-delay`-is-relative distinction, so a future edit doesn't reintroduce the same class of bug.

All three were verified fixed by re-running the same screenshot check at the same and additional timestamps — see the PR body for the verification method.

## Copy-Risk Guardrail / What FARLENS Must Not Copy

Never used anywhere in this Prototype: Kurzgesagt's bird or any other specific character; their logo; their specific color-set; their specific icon set; their specific Shape Language as a whole; any specific composition, Visual metaphor, or Motion Sequence from any Kurzgesagt video; their narration wording, music, or SE; their world-view; any starfield/cosmic background treatment; or any combined look that would read as "trying to look like Kurzgesagt." This Prototype uses only the abstract structural ideas named in `FRL-R-0004` (screen-time budgeting, progressive disclosure, a companion-evidence pattern), re-implemented from scratch in FARLENS's own Visual Core language.

## Evidence Status

- [x] Prototype built (both variants exist, are automatically tested, and were verified by direct screenshot at multiple timestamps in this pass)
- [ ] Prototype tested by a human reviewer — pending (this Prototype has been built and self-reviewed by Claude Code only; no CEO/Compass review has occurred yet)
- [ ] Child evidence — not collected
- [ ] Parent evidence — not collected
- [ ] Production evidence — not collected

## Rulebook / Blueprint Impact

No impact yet, and none is claimed by this Prototype's existence. The Color Set above is explicitly Prototype-limited (see "Visual System"). Any future promotion of any idea tested here into `FARLENS_VISUAL_DESIGN_RULEBOOK.md`, `FARLENS_VISUAL_SYSTEM_BLUEPRINT.md`, or a Canonical Palette requires its own separate PR/Decision after real CEO/Compass review evidence exists — this Prototype does not perform or imply that promotion.

## Production Cost / AI Automation / Human Judgment

- **Estimated production cost**: low — both variants are code-generated static HTML/CSS/SVG plus a shared ~150-line JS timeline engine; no external assets, no rendering pipeline, no paid tooling. Built and verified (screenshots + automated test) in a single pass.
- **AI reproducibility**: high for this class of artifact — the scene-timeline structure, shape library, and Color Set are all reusable for a future Quiz-format piece (the engine already supports an arbitrary number of timed scenes; a Reveal-branch structure would be the next natural extension, not built here).
- **Human review needs**: a person must judge the actual felt experience (attraction, "which do I want to watch again," which reads as more FARLENS) — this is exactly what the CEO Review Points in `IPHONE_PREVIEW.md` ask for, and cannot be automated. A design/production reviewer should also independently confirm neither variant visually converges on Kurzgesagt's reported look before any wider showing.

## Development Check

From the repository root:

```sh
python3 -m http.server 4177 --bind 127.0.0.1 --directory prototypes/ai-confidence-question-ab
```

Then open `http://127.0.0.1:4177/` (the A/B comparison page) in a browser, or `.../a.html` / `.../b.html` directly, and resize to a mobile width (e.g. 390px), or use browser devtools' device emulation for an iPhone viewport. The local route is for Builder checks only — `IPHONE_PREVIEW.md` defines the one supported Founder review path.

```sh
node prototypes/ai-confidence-question-ab/ai-confidence-ab.behavior.test.mjs
node --check prototypes/ai-confidence-question-ab/scene-engine.js
```
