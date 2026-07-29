# AI Confidence Question — A/B Visual Test (Question-led Short vs. Quiz-led Short)

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

**Revision note (2026-07-29):** the comparison axis was redefined to the current **"Question-led Short vs. Quiz-led Short"** — i.e. a passive-question-with-lingering-effect structure vs. a choice-pause-Reveal participatory structure, both sharing the identical opening line/timing so only the structure downstream of it differs. The underlying technical foundation (Color Set, Font, Scene Engine, GitHub Pages review mechanism) is unchanged; only the two variants' content and structure were redesigned.

## Educational Theme

Central question: 「AIが『100％正しい』と言ったら、信じる？」

Capability exercised: Evidence checking, critical thinking, separating Confidence from Correctness, suspending judgment, thinking for oneself while using AI as a tool.

**This is explicitly not "AI is untrustworthy."** Both variants teach: AI is a powerful tool; a confident answer can still be wrong; checking evidence is a habit worth building; a person makes the final judgment. No claim about grades, exam outcomes, school admission, or intelligence increase appears anywhere in either variant — enforced by an automated check, see "What Was Built" below.

## What Was Built

Two ~13-14 second, silent-by-default, vertical (9:16) HTML/CSS/JS "Short" simulations sharing one Color Set, font stack, and scene-timeline engine — same medium and mechanism as the existing `research-two-beat-reveal` Prototype (static, self-contained, no server, no build step). **A and B share a byte-identical opening scene** (same AI declaration line, same 0-2.5s timing, enforced by an automated test) — everything after that point is where the two structures diverge.

- **`a.html` — A: Question-led Short** (~13.7s). AI declares confidently → a real question is posed ("自信があることと、正しいことは同じ？") → a short, silent thinking pause (no new text, no new visual — the point of this beat is that nothing new arrives) → a second open prompt ("君なら、どう確かめる？") → the video ends on a lingering visual with no caption at all. **No choice is ever shown, no answer is ever asserted, and the video never reverts to an explanation-style conclusion.** The aim is a question that keeps working in the viewer's head after the video ends.
- **`b.html` — B: Quiz-led Short** (~13.0s). Same opening line, then "どうする？", then two candidate judgments appear together ("すぐ信じる" / "根拠を確かめる") with neither highlighted, held on screen for a genuine ~3.3-second pause — a real judgment beat, not a rushed transition — before "根拠を確かめる" quietly gains a soft outline (never a score, never a red/green correct-incorrect mark) and a final scene lands the insight: 「自信と正しさは、同じとは限らない。」
- **`index.html`** — the CEO-facing comparison page: both variants embedded side by side (stacked on narrow viewports), a one-line description of what differs, and links to open each standalone.
- **`shared.css`** — the Prototype-only Color Set, typography, phone-frame chrome, and every shape used by both variants (see "Visual System" below).
- **`scene-engine.js`** — a small, dependency-free timeline runner: every scene is pre-authored as static HTML (`<section class="scene" data-start="…" data-end="…">`), and the engine only toggles which one is `.is-active` at the current playhead time, drives the progress bar, toggles an `.is-revealed` class on any `[data-reveal-at]` element once the playhead passes its own timestamp (used by B's Reveal), and (muted by default) triggers short synthesized tones via the Web Audio API. Nothing is built dynamically — the entire script and its timing is directly readable from `a.html`/`b.html`'s own source.
- **`ai-confidence-ab.behavior.test.mjs`** — an automated, dependency-free Node check (run by `.github/workflows/living-storybook-preview.yml`, same as every other Prototype's `*.behavior.test.mjs`) asserting: each variant's total duration is 10-15.5s with contiguous scene timing; A and B's opening scene is byte-identical; A contains no `choice-row`/`choice-pill` and no explanation-style conclusion phrase, and does contain the open prompt "君なら"; B contains exactly two choice pills, a Reveal mechanism (`data-reveal-at`) that lands at least 2.5s into the choice scene (a genuine pause, not an instant reveal) and before that scene ends, the closing insight line, and no score/correctness/reward label; neither old variant name ("Explanation-led" / "Question-led Choice") remains anywhere; no banned promotional phrase (Harvard/Todai/pass exam/head-gets-smarter/hensachi/IQ) anywhere; and no external network reference anywhere.

### Explicitly not interactive / not a branching prototype

Both `a.html` and `b.html` autoplay linearly from start to end. The only buttons are Play/Replay and an optional sound toggle — there is no click-to-choose, no branching path, and no state that depends on a viewer's tap. B's "choice" is something the viewer experiences by watching (a held pause showing two options, then the meaning lands), the same way an actual YouTube Short poses a question without requiring the viewer to tap anything. This is a deliberate design constraint, not an oversight: `DO_NOT_RESTORE.md` item 5/9 retires browser choice-branching interaction as FARLENS's production medium; this Prototype tests a **video-medium** structural difference instead, consistent with `ACTIVE_DIRECTION.md`'s YouTube-premised direction.

## Visual System (Prototype-only hypothesis) — unchanged by this revision

### Color Set — NOT Canonical, NOT Kurzgesagt's palette

| Role | Hex | Meaning |
| --- | --- | --- |
| Background | `#17262c` | calm, dark, non-alarming base |
| Background (soft) | `#1f343c` | cards, one step lighter |
| Subject | `#f5efe3` | AI core, child silhouette — one consistent warm tone |
| Accent | `#e8a33d` | AI's confident assertion (amber, not red) |
| Signal | `#4fb0a5` | evidence / verification / Reveal outline (muted teal-green) |
| Caution | `#d97a4e` | reserved for uncertainty in a future variant — a muted coral, never a saturated alarm red, never paired with black |

Deliberately different from Kurzgesagt's widely-reported general palette (deep blues/purples with bright reds/oranges/yellow): this set uses a teal-navy base rather than blue-purple, no saturated red anywhere, and every color is assigned exactly one meaning role rather than used decoratively (`FARLENS_VISUAL_DESIGN_RULEBOOK.md` Section 3). **This Color Set is a Prototype-limited hypothesis and does not become FARLENS's Canonical Palette from this Prototype alone.**

### Shapes (Semantic Geometry) — original, not references to any specific work

- **AI** — a rounded-square "core" with a pulsing outline ring (computation), containing only the text "AI". No face, no eyes, no bird/creature form.
- **Child / viewer** — an intentionally minimal circle-head + rounded-body silhouette, a single flat tone, no limbs, no face — deliberately not Kurzgesagt's specific round-body/stick-limb/eye-dot character construction. Used only in A's lingering ending in this revision.
- **Confident assertion** — a speech bubble (rounded rectangle + tail).
- **Evidence / verify** — a rounded card with a stroke-drawn checkmark (generic UI language, not a magnifying glass or any distinctive icon). Used in B's Reveal scene.
- **Uncertainty** — a small, softened caution triangle (rounded joins, not a sharp alarm form). Part of the shared shape library in `shared.css`; not used by either variant in this revision (A no longer explains "even confidence can be wrong" in words — the caution-mark shape remains available for a future variant).
- **Judgment candidates** — two plain pill shapes, no icon, no character.

### Typography

System font stack only (`-apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Noto Sans JP", system-ui, sans-serif`) — no bundled or CDN-loaded font of any kind, so there is no font-license question and no possibility of matching a specific reference's typeface. Both variants share the exact same font stack so the A/B comparison is never confounded by a typography difference.

### Sound

Silent by default (matches the existing `research-two-beat-reveal` precedent and the task's own "無音でもよい" allowance). A muted-by-default 🔇 toggle exists on both variants and, if unmuted, plays a small number of short, purely synthesized sine-wave tones generated at runtime via the Web Audio API (`scene-engine.js`'s `createTonePlayer`) — no audio file of any kind is loaded, recorded, sourced, or copied from anywhere.

## Production Grammar Tested (from `FRL-R-0004`, treated here as untested hypotheses re-tested fresh)

- **One Moment, One Cognitive Focus** — each scene in both variants carries exactly one idea; A's "思考の間" scene deliberately carries *no* new idea at all, testing whether an empty beat can itself be meaningful.
- **Static-first, Motion-selective** — only meaningful elements move (AI core pulse, checkmark draw-in, pill Reveal outline); no whole-screen motion.
- **Progressive Visual Disclosure** — B's Reveal (pause → outline → new scene with the insight line) never shows everything at once; A's beats replace each other one at a time, ending on an intentionally empty visual rather than a resolved statement.
- **Semantic Geometry** — every shape (see above) exists to carry a specific meaning, not decoration.
- **Emotionally Safe Complexity** — no red/black alarm pairing, no "AI is scary" framing anywhere in either structure.
- **Typography as Visual System** — captions are sized/weighted by role (declaration vs. supporting caption), not uniform body text.

**New in this revision — two structural hypotheses being directly compared for the first time:** (1) does an unresolved, lingering question (A) hold attention and provoke continued thinking better than an explicit structural payoff (B)? (2) does a real, held judgment pause before a Reveal (B) make a quiz-style participatory beat feel earned rather than rushed, compared to a purely reflective beat with no payoff at all (A)? Neither question is answered by this Prototype's existence — that is exactly what the CEO Review Points in `IPHONE_PREVIEW.md` ask a human to judge.

## What Was Fixed After Visual Self-Review (real findings, not assumed-correct on first attempt)

Findings from the first draft's self-review (scene crossfade double-exposure; B's choice pills never rendering due to a missing CSS activation rule; B's emphasis timing firing before its scene was even visible because a CSS `animation-delay` on a statically-present class counts from page load, not scene-activation time) were already fixed before that draft's PR and remain fixed here — the underlying transition-timing model (fast/undelayed leaving, delayed entering) is unchanged by this revision.

**This revision's own engineering change, made specifically to avoid reintroducing the `animation-delay` class of bug:** B's Reveal no longer uses a CSS `animation` on a static class at all. `scene-engine.js` now supports a generic `[data-reveal-at="<seconds>"]` attribute: the engine itself toggles a `.is-revealed` class via JavaScript once the playhead passes that absolute timestamp, and `shared.css` responds to that class change with an ordinary CSS *transition* (which is always relative to the moment the class is actually toggled, unlike an `animation-delay` on a class present since page load). This was verified directly by screenshot at t=6/7.5/8.2/8.5s (see PR body): the two choice pills stay neutral through the held pause and the outline appears only once the playhead genuinely reaches `data-reveal-at`, with the pill visibly neutral in earlier frames and visibly outlined in later ones from the *same* running instance — not inferred from source alone.

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

- **Estimated production cost**: low — both variants are code-generated static HTML/CSS/SVG plus a shared ~150-line JS timeline engine; no external assets, no rendering pipeline, no paid tooling. Restructuring both variants for this revision was a same-day, same-branch edit — no new infrastructure.
- **AI reproducibility**: high for this class of artifact — the scene-timeline structure, shape library, Color Set, and the new `data-reveal-at` mechanism are all reusable for a future Quiz-format piece with more than one Reveal beat.
- **Human review needs**: a person must judge the actual felt experience (attraction, "which do I want to watch again," which reads as more FARLENS, whether A's unresolved ending feels satisfying-open or just incomplete, whether B's pause feels genuine or slow) — this is exactly what the CEO Review Points in `IPHONE_PREVIEW.md` ask for, and cannot be automated. A design/production reviewer should also independently confirm neither variant visually converges on Kurzgesagt's reported look before any wider showing.

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
