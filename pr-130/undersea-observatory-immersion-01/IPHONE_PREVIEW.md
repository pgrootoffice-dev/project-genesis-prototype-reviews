# Prototype 01 Immersion Test — iPhone Review

Status: OFFICIAL PERSISTENT FOUNDER REVIEW WORKFLOW
Date: 2026-07-23

## Supported Review Path

GitHub Pages is the only official Founder review route. The Prototype PR automatically publishes this directory to:

`https://pgrootoffice-dev.github.io/project-genesis-prototype-reviews/pr-<PR number>/undersea-observatory-immersion-01/`

Founder does not need to run a server, find a LAN address, download an artifact, enable a service, or discover a URL.

## Prototype Review

Device:
iPhone Safari

Review URL:
Use the exact verified PR-numbered GitHub Pages URL from the workflow result.

Review Steps:

1. Open the exact HTTPS URL in the `Prototype Review` section of the Compass report or PR handoff.
2. Watch without touching anything for the first several seconds. Confirm the screen starts almost fully dark, with a low water sound and a soft blue light slowly arriving.
3. Around 4 seconds, confirm a large window appears showing deep water, drifting particles, and slow-moving shapes outside.
4. Around 8–12 seconds, confirm small floor lights turn on one after another, as if the world is waking up because you arrived.
5. Around 12 seconds, confirm three different-looking spots appear below the window — one rippling with water, one almost fully dark, one with a tiny distant blinking point. Confirm you can tell them apart by sight alone, without reading anything.
6. Around 18 seconds, confirm the single sentence "どこを見にいく？" appears, and the three spots each briefly brighten in turn.
7. Tap any one of the three spots. Confirm the screen responds immediately, the other two spots fade away, and the view "travels" toward the one you tapped.
8. Confirm the choice ends in a short, positive discovery line — never an "incorrect" or empty result.
9. Repeat from the start (reload the page) and pick a different one of the three. Confirm it also ends positively, with a different discovery line.

Review Points:

- Did you understand where you were within about 10 seconds, without reading anything?
- Within about 30 seconds, did you want to touch something yourself?
- Was there ever a moment (10+ seconds) where you didn't know what to do?
- Could you tell the three spots apart by sight alone?
- Did tapping feel immediate, not laggy or delayed?
- Did your first choice feel like a "win" rather than a wrong answer?
- Did it feel like the world responded because you were there, not like you were watching a video?
- Did anything feel cheap, generic, or AI-generated-looking?
- Did anything feel like a school worksheet or an educational app?
- Do you want to see what happens next?

Expected Feeling:

> 「暗闇の向こうに、静かに生きている海の底の街があった。触れたら、世界が少しだけ応えてくれた。」

Expected result:

- the complete opening sequence plays automatically from a dark screen with no explanation text
- the underwater facility reads as a real place within the first several seconds, by sight alone
- three visually distinct choices appear and remain tappable
- the one sentence "どこを見にいく？" appears around 18 seconds
- tapping any of the three choices always leads to a small, positive discovery — never a dead end or a wrong-answer feeling
- no login, backend, score, correct/incorrect UI, or stored personal data appears
- sound is quiet, underwater, and never a continuous loud BGM; it becomes audible after the first tap due to iOS/browser autoplay restrictions (see `README.md`'s Sound section)

## Builder Publication Rule

Before reporting the review URL, Codex / Builder must:

1. open or update the Prototype PR
2. confirm the `Founder Prototype Review` workflow succeeds
3. confirm the exact GitHub Pages URL opens over public HTTPS
4. verify the public root, stylesheet, and script
5. verify the page at an iPhone-sized viewport
6. verify the opening sequence autoplays through darkness, window reveal, light wake-up, and the three choices without any tap required
7. verify all three choices are tappable, visually distinct, and each produce a positive discovery
8. verify no login, backend, score, correct/incorrect UI, or stored state appears
9. put the exact verified URL in the required `Prototype Review` report format

The handoff ends after reporting the verified URL. Do not keep a process alive, wait for Founder Evidence, or start monitoring.

## Builder-Only Debugging

Localhost, Mac LAN preview, and a temporary Cloudflare Quick Tunnel may be used only for short-lived Builder debugging. They must never be presented as Founder review routes.

## Safety Boundary

The GitHub Pages preview is a persistent public copy of the static Prototype 01 directory. It adds no account, backend, login, payment, analytics, persistent storage, or paid runtime service. Sound is synthesized locally in the browser via the Web Audio API; no audio files are shipped and no external audio/AI service is called.
