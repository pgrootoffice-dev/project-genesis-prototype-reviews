# Research Prototype — Setup → Guess → Reveal (「夜の森で、次に必要なものは？」)

Status: NON-CANONICAL RESEARCH PROTOTYPE
Date: 2026-07-28
Prototype ID: `FRL-P-0001` (new convention, informal — not yet confirmed as the permanent Research-Lab-linked Prototype ID scheme; parallels `FRL-R-NNNN`)

Related records:

- `../../docs/genesis-os/education-adventure-ip/research/FRL-R-0001-taro-miura-tools.md` — the Research Entry this Prototype tests
- `../../docs/genesis-os/education-adventure-ip/research/README.md` — FARLENS Research Lab (Promotion Path)
- `../../docs/genesis-os/education-adventure-ip/FARLENS_VISUAL_SYSTEM_BLUEPRINT.md`
- `../../docs/genesis-os/education-adventure-ip/FARLENS_VISUAL_DESIGN_RULEBOOK.md`
- `../../docs/genesis-os/education-adventure-ip/ADVENTURE_QUIZ_EXPERIENCE_WORKING_STRATEGY.md`
- `../living-storybook-prototype4/README.md` — the existing `prototypes/` placement and GitHub Pages review convention this Prototype reuses

## Purpose

This Prototype is a Research Entry verification, not a finished work, official UI, or Canonical rule. It tests whether FRL-R-0001's extracted Production Grammar — a **Setup → Guess → Reveal** two-beat structure, built from a small set of silhouette-legible clues — can carry a small FARLENS-original judgment moment for a child, entirely in FARLENS's own world and visual language, with no copied subject matter, characters, or artwork from the source (Taro Miura's *Tools*).

## Research Question Tested

Can 3-5 silhouette/shape-legible clues, followed by a 3-way choice with no visible correct/incorrect outcome, produce a small experience that (a) invites a child to read the scene and choose, rather than guess a hidden right answer, and (b) always resolves into a meaningful, connected discovery regardless of which choice is made?

## FARLENS Transformation

The scene ("夜の森で、次に必要なものは？" — a night forest, three quiet clues: small footprints, swaying grass, a faint distant light) is original to this Prototype. It does not reuse Taro Miura's tools/professions subject matter, silhouette style, or page-turn mechanic literally — only the abstract two-beat structure and the "legible silhouette, no color/detail needed" shape discipline from FRL-R-0001's Section 5 (Production grammar extracted) were carried forward.

**Improvement over the task brief's original example**: the brief's example had one clue ("音をよく聞く" / listening) as the "real" path to the reveal, with the other two choices implicitly not leading anywhere. This Prototype instead gives **all three choices their own complete, connected reveal** (listening → the grass sound gets closer; climbing → the footprints continue into the distance; following the light → a small lantern is found). No choice is privileged as "correct," which more fully satisfies the task's own requirement that no choice should read as wrong — the earlier one-real-answer structure risked feeling like a guess with two silent failures even without a visible "incorrect" label.

## What Was Built

- A single static HTML page (`index.html`) with two screens: Setup (3 clue shapes, shown with **no visible name/label** — only the shape — + 3-choice prompt) and Reveal (the connected clue's name + a short 1-2 sentence explanation + a "もう一度試す" / try again button). The clue names are visually-hidden on Setup (kept as screen-reader-only text for accessibility) so a reviewer must read the shapes themselves, not a text label, before choosing — this was a P1 fix from Codex review; the initial version incorrectly showed the names on Setup, which let a viewer read the answer as text instead of the shape.
- All 3 choices lead to their own reveal text; none is marked correct or incorrect, no score, no counter, no timer.
- All clue and reveal art is CSS/inline SVG only — no external images, fonts, or audio.
- Portrait-first layout, minimum 56px-tall tap targets, no horizontal scroll, `prefers-reduced-motion` respected for the ambient grass-sway and light-pulse animations.
- No network requests, no storage (`localStorage`/cookies), no analytics, no personal data of any kind. Reloading the page always returns to the Setup screen — there is no state to reset.

## What Was Not Built

- No sound design (silent by design; the task requires the experience to work without audio).
- No connection to a real FARLENS Adventure Experience, World Map, or Evidence system — this is an isolated, standalone test, not integrated with `../../docs/genesis-os/education-adventure-ip/PROTOTYPE_01_PRODUCTION_SPECIFICATION.md` or any production pipeline.
- No child, parent, or production testing — see Evidence Status below.
- No animation beyond the two ambient CSS loops (grass sway, light pulse); no transition animation between Setup and Reveal beyond an instant screen swap (a smoother transition is a candidate next step, not built here).
- No Rulebook, Blueprint, or Decision Log changes of any kind.

## Observe (what a reviewer should watch for)

- Before choosing: how did you read/name each of the 3 unlabeled shapes? Record what you guessed for each, so it can be compared against the clue name that appears on Reveal.
- Does the reveal text for each of the 3 choices genuinely feel connected to that choice's clue, or does it feel arbitrary?
- Does the absence of a "correct" answer read as calm and exploratory, or as unclear/pointless?
- Does the whole loop (read scene → choose → read reveal → optionally retry) complete in roughly 30-60 seconds without feeling rushed or dragging?
- Do the tap targets and text read comfortably on an actual iPhone screen (portrait, one-handed reach)?

## Success Criteria

- A reviewer can complete Setup → choice → Reveal without instructions, and the reveal text reads as a small "なるほど" rather than confusion.
- All three choices, tried independently, each produce a distinct, sensible reveal tied to their own clue.
- No visible failure/incorrect state appears for any choice.
- The full loop takes about 30-60 seconds.
- No console errors; page reload returns cleanly to Setup.

## Failure Criteria

- A reveal text reads as disconnected from the clue/choice that produced it.
- Any choice implicitly reads as "wrong" (e.g. through tone, layout emphasis, or ordering).
- Tap targets are too small or layout requires horizontal scrolling on a narrow phone width.
- Any console error, broken transition, or state that survives a reload.

## Evidence Status

Per `../../docs/genesis-os/education-adventure-ip/research/FRL-R-0001-taro-miura-tools.md`'s Section 10 vocabulary:

- [x] Prototype built (this Prototype exists and is locally/CI-testable)
- [ ] Prototype tested by a human reviewer (pending — this Prototype has been built and self-reviewed by Claude Code in this pass; no separate CEO/Compass/other human review has occurred yet)
- [ ] Child evidence — not collected; no child has used this Prototype
- [ ] Parent evidence — not collected
- [ ] Production evidence — not collected

This Prototype does not itself claim "Prototype tested" status in FRL-R-0001 until an actual human reviewer (CEO/Compass or other) has gone through it — see `../../docs/genesis-os/education-adventure-ip/research/FRL-R-0001-taro-miura-tools.md`'s updated Evidence Status for exactly what is and is not claimed.

## Rulebook / Blueprint Impact

No impact yet. This Prototype does not modify, and does not by itself justify modifying, `../../docs/genesis-os/education-adventure-ip/FARLENS_VISUAL_SYSTEM_BLUEPRINT.md`, `../../docs/genesis-os/education-adventure-ip/FARLENS_VISUAL_DESIGN_RULEBOOK.md`, or `../../DECISION_LOG.md`. Any future promotion would require its own separate PR/Decision after real review evidence exists.

## Scope

Included:

- one static, self-contained HTML/CSS/JS experience testing the Setup → Guess → Reveal structure
- an original FARLENS night-forest scene, built from scratch for this Prototype
- iPhone Safari-first responsive layout
- reduced-motion support

Not included:

- new visual art beyond simple CSS/SVG shapes
- sound, animation transitions beyond ambient loops
- any backend, login, analytics, or persistence
- integration with any real FARLENS world, Adventure Experience, or Evidence system
- Canonical promotion of any kind, or a decision about whether this pattern should become a Rulebook/Blueprint rule

## Development Check

From the repository root:

```sh
python3 -m http.server 4177 --bind 127.0.0.1 --directory prototypes/research-two-beat-reveal
```

Then open `http://127.0.0.1:4177/` in a browser and resize to a mobile width (e.g. 375px), or use browser devtools' device emulation for an iPhone viewport. The local route is for Builder checks only.

`IPHONE_PREVIEW.md` defines the one supported Founder review path and requires a verified HTTPS URL in the final handoff, per `../../docs/os/COMPASS_OPERATING_CHARTER.md`'s Prototype Review Rule.
