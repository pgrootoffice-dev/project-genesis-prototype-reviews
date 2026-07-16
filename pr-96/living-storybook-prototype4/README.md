# Living Storybook Prototype 4 — The World Chooses Silence

Status: NON-CANONICAL INTERACTIVE PROTOTYPE
Date: 2026-07-16
Built from: refined Prototype 3 commit `bbb04bd`

Related records:

- `../../docs/genesis-os/education-adventure-ip/DESIGN_PRINCIPLES.md`
- `../../docs/genesis-os/education-adventure-ip/WORLD_EXISTENCE_GUIDELINES.md`
- `../../docs/genesis-os/education-adventure-ip/FIRST_WONDER_WORKING_STRATEGY.md`
- `../../docs/genesis-os/education-adventure-ip/EMOTIONAL_GRAMMAR.md`
- `../../docs/genesis-os/education-adventure-ip/PROTOTYPE_1_EXPERIENCE.md`
- `../../docs/genesis-os/education-adventure-ip/PROTOTYPE_1_INTERACTION.md`
- `../../docs/genesis-os/education-adventure-ip/CURRENT_STATE.md`

## Purpose

Prototype 4 tests whether the refined Prototype 3 world can remain emotionally meaningful when touch does not always produce a visible response.

It does not test a new visual language, feature, interface, story, reward, or game rule.

## Controlled Inheritance

Prototype 4 preserves from refined Prototype 3:

- the same illustrated world asset
- the same CSS visual language
- the same composition, atmosphere, text hierarchy, and quiet motion
- the same single full-world touch, pointer, and keyboard surface
- the same destination-first curved answer
- the same 2.8-second return to the living baseline
- the same absence of navigation, sound, reward, progress, and accumulated state

`styles.css` and `assets/world-threshold-v2.png` are byte-identical to refined Prototype 3. The asset SHA-256 is:

```text
a693d5504936df38e4fc9c81f89a36d22cc2a8d68039543b6412859afedb747b
```

No image was generated or modified for Prototype 4.

## The One Rule

> The world answers at most once per breath.

The world uses the existing eight-second threshold rhythm as its response interval:

1. the first eligible touch receives the refined Prototype 3 destination-first answer
2. the answer disappears into the living baseline after 2.8 seconds
3. any further touch within the same eight-second world breath produces no visible response
4. mist, water, small lights, and the observatory continue exactly as they already were
5. after the next world breath begins, touch may receive the same answer again

Touch does not create, restart, accelerate, or visibly acknowledge the silent state.

The interval is deterministic rather than random. This makes silence reproducible for review and prevents an unpredictable failure from being mistaken for intentional world behavior.

The eight-second interval is an implementation hypothesis for this prototype only. It is not a permanent Genesis timing rule.

## What Silence Means

During a silent choice:

- no reply light is launched
- no local atmosphere bloom appears
- no tap ring, pulse, text, message, counter, vibration, or substitute feedback appears
- no ambient animation pauses or restarts
- no progress, score, memory, reward, or hidden collection state changes
- the world remains visually complete and quietly alive

The temporary `data-rule-phase="silence"` and `data-last-choice="silence"` values exist only for Builder verification. They have no visible style, user-facing message, stored history, or product meaning.

## Emotional Test

- World autonomy: does the continuing ambient rhythm make silence feel chosen rather than broken?
- Safe curiosity: does the child remain interested without being trained to tap repeatedly for a response?
- Calm trust: does the absence of feedback remain composed, legible, and free from manipulation?
- Free continuity: does the world feel complete without needing to acknowledge every visitor action?
- Emotional meaning: does a later answer feel like part of the world's time rather than a delayed reward?

## Scope

Included:

- the complete refined Prototype 3 visual surface and ambient life
- the existing destination-first response
- one deterministic world-breath interval
- intentional visible response and intentional silence states
- the existing single touch, pointer, and keyboard surface
- reduced-motion support
- iPhone Safari-first layout

Not included:

- new visual art, image generation, or visual polish
- new UI, control, route, instruction, or visible status
- score, reward, progression, collection, achievement, or game mechanics
- backend, login, payment, analytics, audio, vibration, full 3D, or production deployment
- personal recognition, child data, persistence, or emotional profiling
- Prototype 3 validation or Canonical promotion
- final approval of silence, timing, image, world, or product direction

## Development Check

From the repository root:

```sh
python3 -m http.server 4176 --bind 127.0.0.1 --directory prototypes/living-storybook-prototype4
node prototypes/living-storybook-prototype4/prototype4.behavior.test.mjs
```

The local route is for Builder checks only.

`IPHONE_PREVIEW.md` defines the one supported Founder review path and requires a verified HTTPS URL in the final handoff.
