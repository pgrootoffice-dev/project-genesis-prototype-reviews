# Prototype 01 — Immersion Test v0.1: 沈んだ海底観測都市

Status: NON-CANONICAL INTERACTIVE PROTOTYPE
Date: 2026-07-23

Related records:

- `../../docs/genesis-os/education-adventure-ip/VISUAL_LANGUAGE.md`
- `../../docs/genesis-os/education-adventure-ip/EMOTIONAL_GRAMMAR.md`
- `../../docs/genesis-os/education-adventure-ip/EDUCATION_PRINCIPLES.md`
- `../../docs/genesis-os/education-adventure-ip/PROTOTYPE_1_EXPERIENCE.md`
- `../../docs/genesis-os/education-adventure-ip/PROTOTYPE_1_INTERACTION.md`
- `../../docs/os/ARTIFACT_REVIEW_LOOP.md`

## Purpose

This prototype tests only the first 0–30 seconds of "沈んだ海底観測都市" (a sunken undersea observation city) — one candidate "Infinite Atlas" place (`VISUAL_LANGUAGE.md` lists "undersea museum" as an example place type).

It tests whether an initial 8-year-old viewer can, without any explanation screen:

- understand where they are within 10 seconds
- want to touch/choose within 30 seconds
- never hit an "I don't know what to do" moment for more than 10 seconds
- receive a guaranteed positive discovery on their first choice, regardless of which of the three they pick

It does not test full gameplay, correct/incorrect answers, scoring, a mission-complete state, a Victory Theme, or the World Map. Those are explicitly out of scope for v0.1 (see Scope below).

## Experience Timeline (autoplay, no tap required to begin)

| Time | What happens |
| --- | --- |
| 0–4s | Near darkness. A low underwater ambient tone (see Sound) and a soft blue light slowly arriving. No text. |
| 4–8s | A large window fades/scales into view, showing deep water, drifting particles, and two slow-moving creature silhouettes outside — establishes "we are inside an undersea facility" by sight alone. |
| 8–12s | The camera reads as advancing: floor lights along the room wake up one by one in sequence. |
| 12–18s | Three doorway-shaped thresholds fade in below the window, each already visually distinct (rippling water / near-total darkness / a faint distant blink) — no labels, nothing to read. They are tappable from this moment. |
| 18–22s | The only sentence in the whole experience appears: "どこを見にいく？". The three thresholds each briefly brighten in turn (順番にわずかに反応) to draw attention if the viewer hasn't already tapped. |
| 22–30s+ | Tapping any threshold locks in that choice, fades the other two, and "travels" toward it (the window scales/zooms toward the chosen spot). Every choice ends in a small, positive discovery caption — there is no wrong answer. |

Because the child may take longer than 30 seconds to choose, the three thresholds and the question remain tappable indefinitely after 18s — nothing times out or disappears on them.

## The Three Choices (all rewarding, none a "wrong answer")

| Choice | Visual difference | Discovery caption |
| --- | --- | --- |
| 水がゆれる場所 (water) | Rippling horizontal shimmer, pale cyan | 「きらきら……」 |
| 真っ暗な場所 (dark) | Near-total darkness, faint outline only | 「ひかった……」 |
| 遠くで光る場所 (light) | A tiny distant point blinking slowly | 「ピカ……ピカ……ピカ」 rhythm, then 「あれ……？」 |

The "light" choice's blink rhythm and closing line follow the exact example given in the source task spec. The other two captions were written to match the same short, trailing-ellipsis tone, since the spec did not fix exact wording for them.

## Sound

Fully synthesized with the Web Audio API (`script.js`) — no audio files, no new dependency, no paid service:

- a very low, quiet ambient hum (two slightly detuned sine oscillators through a lowpass filter) for the underwater environment
- a short, quiet tone on choosing a threshold
- a soft three-note chime on discovery

**Platform constraint, stated honestly:** iOS Safari (and most modern browsers) block any audio from starting before a user gesture. The experience's own visual timeline still autoplays from 0s with no tap required, exactly as specified, but the ambient hum only becomes audible from the very first tap/keypress anywhere on the screen (`unlockAudioOnce` in `script.js`) rather than from 0s as an ideal spec would want. This is a genuine platform limitation, not a design shortcut, and is the same reason no other Genesis prototype in this repository autoplays audio either. No BGM loops continuously; the ambient hum is the only sustained sound, and silence is otherwise used exactly as the spec asks.

## Visual Implementation Note

Following the same precedent as Prototype 0 (`VISUAL_LANGUAGE.md`, "The CSS-only placeholder world should be kept as Prototype 0"), this v0.1 uses no generated or external image assets — the entire scene (window, water, particles, creature silhouettes, floor lights, three doorways) is built from CSS gradients, shapes, and animation only. This keeps the palette restrained (deep blue / near-black / pale blue-white only, no warm colors before any "achievement" moment, per the task's Visual DNA) and avoids the "AI-generated flashy fantasy" look the task explicitly asks to avoid.

The "three directions" are simplified from full 3D corridor navigation to three adjacent doorway thresholds within one continuous composed scene, directly below the main window. This keeps the v0.1 implementation legible in 2D CSS for the target age within the stated 0–30s scope, rather than building navigable 3D space.

## Scope

Included:

- the 0–30s opening sequence described above
- three visually distinct, guaranteed-positive first choices
- synthesized ambient/interaction sound
- reduced-motion support
- iPhone Safari-first layout

Not included (explicitly out of scope for this pass):

- Q1/Q2 main content, correct/incorrect answer judgment, Mission Complete
- Victory Theme (structure left connectable for later, per the task's own instruction, but not implemented)
- World Map implementation
- Future Skills parent-facing explanation
- SNS sharing
- backend, login, payment, analytics, or any stored/child-personal data
- generated image assets

## Development Check

From the repository root:

```sh
python3 -m http.server 4177 --bind 127.0.0.1 --directory prototypes/undersea-observatory-immersion-01
node prototypes/undersea-observatory-immersion-01/prototype1-immersion.behavior.test.mjs
```

The local route is for Builder checks only.

`IPHONE_PREVIEW.md` defines the one supported Founder review path and requires a verified HTTPS URL in the final handoff.
