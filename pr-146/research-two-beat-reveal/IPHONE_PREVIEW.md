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
2. Confirm the first screen shows the line 「夜の森で、静かな物音がする。」 followed by three small clue cards (shapes only — footprints, swaying grass, a faint glow — with **no visible name or label under any of them**) and the question 「どうする？」.
3. Before choosing, look only at the three shapes and try to name what each one is meant to represent, without reading anything else on the screen (there is nothing else to read — the names are not shown yet). Note what you guessed for each.
4. Confirm three choice buttons are visible: 「音をよく聞く」「高い場所へ登る」「光を追いかける」, each large enough to tap comfortably with a thumb.
5. Tap one choice.
6. Confirm the screen now shows a small clue name (e.g. 「揺れている草」) directly above a short reveal sentence connected to that specific choice, with no score, no "正解"/"不正解" label, and no counter. Compare the revealed clue name against what you guessed in step 3.
7. Tap 「もう一度試す」and confirm the screen returns to the clue/choice screen, again with no labels visible on the shapes.
8. Repeat with a different choice and confirm it produces a different clue name and a different, but equally sensible, reveal sentence.
9. Reload the page and confirm it returns cleanly to the first screen (shapes unlabeled again) with no leftover state.

Review Points:

- Without any label, could you tell what each of the three shapes was meant to represent — footprints, grass, or a light — before choosing? Which ones were more or less legible?
- Does the scene ("夜の森で、次に必要なものは？") read clearly without any instruction beyond the on-screen text?
- After choosing, does the revealed clue name feel like the right match for the shape you had guessed, or a surprise?
- Does the reveal feel like a small "なるほど" connected to that specific choice, rather than an arbitrary or disconnected outcome?
- Does any choice feel implicitly "wrong" compared to the others, even without an explicit incorrect label?
- Does the whole loop (read → guess the shapes → choose → reveal → optionally retry) feel like it takes about 30-60 seconds, without feeling rushed or dragging?
- Do the tap targets and text feel comfortable one-handed on an actual iPhone?

Expected Feeling:

> 「手がかりを読んで、自分で選んだ。どれを選んでも、ちゃんと森が応えてくれた。」

Expected result:

- the complete scene appears without login, download, or setup
- three clue shapes and three choice buttons are visible on first load, with no visible name/label under any of the three shapes
- tapping any one of the three choices produces a small clue name plus a reveal sentence specific to that choice, with no visible score, correct/incorrect label, or counter
- "もう一度試す" returns to the first screen without any leftover state, and the shapes are unlabeled again
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
