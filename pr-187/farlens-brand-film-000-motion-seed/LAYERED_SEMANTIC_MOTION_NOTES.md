# Layered Semantic Motion A/B — Design & Cost Notes

Status: WORKING TEST / NON-CANONICAL

Scope: Section 0 and Section 4 only

A: existing Base Motion, byte-locked

B: deterministic Layered Semantic Motion

## Shared grammar under test

1. One Section has one Meaning Verb and one Hero Element.
2. Motion Order has no more than three semantic stages.
3. The complete locked still remains the base of every frame.
4. Regions move or react at different times; the background does not become a camera move.
5. Every motion resolves into a stable hold.

This is a candidate for evaluation only. It does not promote a Motion Grammar or either B test to Canonical.

## Section 0 B

- Meaning Verb: `つながる`
- Hero Element: 世界から家族へ届く既存のオレンジ接続線
- Duration / Hold: 5.4s / approximately 0.98s after 4.42s
- Main layers (5): Background, World, Connection Line, Family/Home, Light/Glow
- Manual region masks (2): feathered World ellipse; feathered Family/Home ellipse
- Existing-path definitions (1): locked orange connection trajectory

Motion Order:

1. 0.45–1.30s: World wakes through a one-pixel, low-opacity source-region depth separation; the world-side point appears.
2. 1.20–3.70s: the existing path gains a broad, weak spatial wake before a restrained path accent advances toward home.
3. 3.45–4.42s: the source-defined home region separates by one pixel and receives local warmth; the frame then holds.

Review:

- Meaning gain: world, connection, and family have separate entrances; this is clearer than A's mostly continuous point/path treatment.
- Still preservation: PASS in maximum-change inspection. Full locked JPEG remains under every overlay; no hole or invented plate exists.
- Quietness: retained. No globe rotation, global zoom, flare, or home movement.
- Limitation: because the orange line is already visible in the source, progression is communicated by spatial response rather than literal line reveal.

## Section 4 B

- Meaning Verb: `整理される`
- Hero Element: 複数の情報が確認を経て一つの意味核へ整う流れ
- Duration / Hold: 5.6s / approximately 1.12s after 4.48s
- Main layers (5): Background, Flow Group A, Flow Group B, Verification Points, Meaning Core
- Manual raster masks (0): no background cutout or inpainting
- Existing-path definitions (5): the same five restrained routes used by the Base Motion

Motion Order:

1. 0.42–2.85s: Flow A and B gather with five staggered starts, two corridor depths, and slightly different tail behavior.
2. 1.84–3.22s: each route passes its own verification point; unverified heads retain a sub-pixel-feeling normal variation while confirmed segments settle on the locked route.
3. 3.55–4.48s: confirmed routes receive a uniform core-side accent; the Meaning Core responds once and settles into the hold.

Review:

- Meaning gain: gather / verify / interpret are temporally separated rather than reading as five equivalent moving points.
- Still preservation: PASS in maximum-change inspection. No flow is deleted, redrawn as a new trajectory, or pulled into a suction effect.
- Quietness: retained. The core response is one non-oscillating change, not a pulse loop.
- Limitation: the locked still already contains strong converging ribbons, so layer depth is intentionally local and may require playback—not a single still—to judge.

## Cost record

Observed Codex wall-clock log: A/Final lock confirmed at 13:04 JST; the joint Section 0/4 renderer and first passing render completed at approximately 13:07; local Bridge, artifact, and 390×844 page acceptance completed at 13:15. Because both Sections were authored in one joint patch, a truthful independent per-Section wall-clock split is not available. CI/publication time is excluded.

The table below records Section-specific engineering-equivalent allocation for planning (implementation, semantic mapping, and one tuning pass), not elapsed Codex wall time:

| Item | Section 0 | Section 4 |
|---|---:|---:|
| Section-specific implementation and tuning | 18 min | 24 min |
| Main layers | 5 | 5 |
| Manual region/raster masks | 2 | 0 |
| Existing path definitions | 1 | 5 |
| Base Motion complexity increase (estimate) | +65% | +80% |

Shared production-equivalent allocation for the A/B renderer, comparison encoding, evidence, page, Bridge configuration, and QA: 42 min. Shared work is reusable and should not be charged again in full per Section.

Reusable:

- locked-source base-frame contract
- three-stage timing functions and mandatory hold
- soft source-region depth layer without background completion
- staggered existing-path flow groups and sequential checkpoints
- A hash lock, side-by-side/sequence encoders, technical evidence, Review Bridge bundle

Section-specific:

- semantic region coordinates and mask boundaries
- existing path coordinates, verification locations, colors, and timing
- visually acceptable light strength for each composition
- CEO judgment of whether the meaning gain is sufficient

11-Section expansion estimate: 11–18 engineering hours for first-pass layer mapping, render, device QA, and evidence, assuming locked stills already exist. Review revisions are excluded. Sections requiring clean occlusion separation or missing-background repair should fall back to fewer layers rather than add inpainting. Relative to applying Base Motion at the same fidelity, the expected production increase is approximately 65–85% before template reuse, declining toward 35–55% after two or three additional Sections validate the shared helpers.

Templateable range: timing/hold, source-safe regional depth, path staging, checkpoint staging, one-shot core settlement, A/B packaging, and Bridge publication. Non-templateable range: semantic selection, masks/paths, visibility tuning, and the decision that a particular image can be safely separated at all.
