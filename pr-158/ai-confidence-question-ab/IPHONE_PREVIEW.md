# Oxygen Short A/B — iPhone Review

Status: OFFICIAL PERSISTENT FOUNDER REVIEW WORKFLOW
Date: 2026-07-30

## Supported Review Path

GitHub Pages is the only official Founder review route. The Prototype PR automatically publishes this directory to:

`https://pgrootoffice-dev.github.io/project-genesis-prototype-reviews/pr-<PR number>/ai-confidence-question-ab/`

Founder does not need to run a server, find a LAN address, download an artifact, enable a service, or discover a URL.

## Prototype Review

Device:
iPhone Safari

Review URL:
Use the exact verified PR-numbered GitHub Pages URL from the workflow result. It opens directly to the A/B comparison page (`index.html`).

Review Steps:

1. Open the exact HTTPS URL in the `Prototype Review` section of the PR handoff.
2. Confirm the comparison page shows the shared question — 「もし、空気中の酸素が5秒だけ消えたら？」 — above two phone-shaped frames labeled A and B.
3. Confirm both A and B open with the exact same Opening (two scenes: a brief world shot with a small "空気中の酸素だけ" note, then the shared question).
4. Watch A (Question-led Short) play through once, start to finish (~15 seconds), without tapping anything. Confirm it never shows a choice, never states a resolved "answer," and ends on an open question ("他には、何が変わると思う？").
5. Tap A's "▶ 再生する" to replay it if you want a second look.
6. Watch B (Quiz-led Short) play through once, start to finish (~14.5 seconds), without tapping anything.
7. Notice the moment in B where three candidate outcomes appear together (engine / flame / sky) with none highlighted, held for a genuine pause of a couple of seconds, before the correct one quietly gains a soft outline (color only — no checkmark, no score sound, no "correct!" text), followed by the same event actually playing out, and a closing line: 「火が消えたのは、酸素が届かなかったから。」
8. Optionally tap each 🔇 button once to confirm an unmute control exists — sound is muted by default and entirely optional (a few short, synthesized tones only, no music/SE file of any kind).

Review Points: (this 4-question set only)

1. 問い先行（A）とクイズ先行（B）、どちらが構成として強いか
2. 続きを見たいと思うか
3. 親として、自分の子どもに見せたいと思うか
4. アニメーションとして視覚的に魅力があるか

Expected Feeling:

> 「たった5秒のことなのに、火のような『いつも起きていること』が、実は空気中の酸素に支えられていたんだ、と気づく。」

Expected result:

- the complete comparison page appears without login, download, or setup
- both A and B autoplay their own ~14-15 second sequence with no tap required to progress
- neither variant ever shows a score, a correct/incorrect label, or a game-style reward effect
- no network request, login, analytics, sound requirement, or stored personal data is involved anywhere in the experience

## Builder Publication Rule

Before reporting the review URL, Codex / Builder must:

1. open or update the Prototype PR
2. confirm the `Founder Prototype Review` workflow succeeds
3. confirm the exact GitHub Pages URL opens over public HTTPS
4. verify the public root, stylesheet, and script load correctly
5. verify the page at an iPhone-sized viewport
6. verify both A and B play their full sequence with no console error
7. verify no login, backend, score, or stored state appears
8. put the exact verified URL in the required `Prototype Review` report format

The handoff ends after reporting the verified URL. Do not keep a process alive, wait for Founder Evidence, or start monitoring.

## Builder-Only Debugging

Localhost and a temporary local HTTP server may be used only for short-lived Builder debugging. They must never be presented as Founder review routes.

## Safety Boundary

The GitHub Pages preview is a persistent public copy of the static Prototype directory. It adds no account, backend, login, payment, analytics, persistent storage, or paid runtime service.
