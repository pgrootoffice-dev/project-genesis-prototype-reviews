# Research Prototype iPhone Review

Status: OFFICIAL PERSISTENT FOUNDER REVIEW WORKFLOW
Date: 2026-07-28

## Supported Review Path

GitHub Pages is the only official Founder review route. The Prototype PR automatically publishes this directory to:

`https://pgrootoffice-dev.github.io/project-genesis-prototype-reviews/pr-<PR number>/research-two-beat-reveal/`

Founder does not need to run a server, find a LAN address, download an artifact, enable a service, or discover a URL.

## Prototype Review

Device:
iPhone Safari

Review URL:
Use the exact verified PR-numbered GitHub Pages URL from the workflow result.

Review Steps:

1. Open the exact HTTPS URL in the `Prototype Review` section of the PR handoff.
2. Confirm the first screen shows the line 「夜の森で、静かな物音がする。」 followed by three small clue cards (footprints, swaying grass, a faint glow) and the question 「どうする？」.
3. Confirm three choice buttons are visible: 「音をよく聞く」「高い場所へ登る」「光を追いかける」, each large enough to tap comfortably with a thumb.
4. Tap one choice.
5. Confirm the screen changes to a short reveal sentence connected to that specific choice, with no score, no "正解"/"不正解" label, and no counter.
6. Tap 「もう一度試す」and confirm the screen returns to the clue/choice screen.
7. Repeat with a different choice and confirm it produces a different, but equally sensible, reveal sentence.
8. Reload the page and confirm it returns cleanly to the first screen with no leftover state.

Review Points:

- Does the scene ("夜の森で、次に必要なものは？") read clearly without any instruction beyond the on-screen text?
- Do the three clues (footprints, grass, light) feel visually distinct and legible as simple shapes, without needing color realism or detail?
- After choosing, does the reveal feel like a small "なるほど" connected to that specific choice, rather than an arbitrary or disconnected outcome?
- Does any choice feel implicitly "wrong" compared to the others, even without an explicit incorrect label?
- Does the whole loop (read → choose → reveal → optionally retry) feel like it takes about 30-60 seconds, without feeling rushed or dragging?
- Do the tap targets and text feel comfortable one-handed on an actual iPhone?

Expected Feeling:

> 「手がかりを読んで、自分で選んだ。どれを選んでも、ちゃんと森が応えてくれた。」

Expected result:

- the complete scene appears without login, download, or setup
- three clue shapes and three choice buttons are visible and legible on first load
- tapping any one of the three choices produces a reveal sentence specific to that choice, with no visible score, correct/incorrect label, or counter
- "もう一度試す" returns to the first screen without any leftover state
- reloading the page also returns cleanly to the first screen
- no network request, login, analytics, sound requirement, or stored personal data is involved anywhere in the experience

## Builder Publication Rule

Before reporting the review URL, Codex / Builder must:

1. open or update the Prototype PR
2. confirm the `Founder Prototype Review` workflow succeeds
3. confirm the exact GitHub Pages URL opens over public HTTPS
4. verify the public root, stylesheet, and script load correctly
5. verify the page at an iPhone-sized viewport
6. verify all three choices each produce their own distinct, connected reveal
7. verify no console error, no login, backend, score, or stored state appears
8. put the exact verified URL in the required `Prototype Review` report format

The handoff ends after reporting the verified URL. Do not keep a process alive, wait for Founder Evidence, or start monitoring.

## Builder-Only Debugging

Localhost and a temporary local HTTP server may be used only for short-lived Builder debugging. They must never be presented as Founder review routes.

## Safety Boundary

The GitHub Pages preview is a persistent public copy of the static Prototype directory. It adds no account, backend, login, payment, analytics, persistent storage, or paid runtime service.
