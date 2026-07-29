# AI Confidence Question — A/B iPhone Review

Status: OFFICIAL PERSISTENT FOUNDER REVIEW WORKFLOW
Date: 2026-07-29

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
2. Confirm the comparison page shows the shared question — 「AIが『100％正しい』と言ったら、信じる？」 — above two phone-shaped frames labeled A and B.
3. Watch A (Explanation-led) play through once, start to finish (~14 seconds), without tapping anything.
4. Tap A's "▶ 再生する" to replay it if you want a second look.
5. Watch B (Question-led Choice) play through once, start to finish (~13.4 seconds), without tapping anything.
6. Notice the moment in B where two candidate judgments appear side by side ("すぐ信じる" / "確かめる") with neither highlighted, held for a couple of seconds, before one quietly gains a soft outline and the closing line lands.
7. Confirm both A and B end on the exact same line: 「未来をつくるのは、答えを知る人ではなく、確かめられる人。」
8. Optionally tap each 🔇 button once to confirm an unmute control exists — sound is muted by default and entirely optional (a few short, synthesized tones only, no music/SE file of any kind).

Review Points:

- どちらに惹かれるか
- どちらを最後まで見たいか
- どちらが子どもに考えさせるか
- どちらを親として見せたいか
- どちらがFARLENSらしいか
- 違和感がある場所
- また見たいか

Expected Feeling:

> 「AIが自信満々に言い切っても、それだけで信じていいわけじゃない。確かめる人になりたい。」

Expected result:

- the complete comparison page appears without login, download, or setup
- both A and B autoplay their own ~10-15 second sequence with no tap required to progress
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
