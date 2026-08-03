# Section 0 Motion D — Layer-first Motion Notes

Status: WORKING TEST / NON-CANONICAL
Scope: Section 0 only
Source of Truth: PR #186, `docs/farlens/brand-film/SECTION_00_MOTION_D_LAYER_MANIFEST_AND_SPEC.md` at `fb671a9427fd19c15867ad082701433d664c4973`

## Intent

- Script: 「世界の変化を、家族の未来へ。」
- Meaning: `世界の変化が、家族へ届く`
- Motion Level: `Lv2 Semantic Motion`
- Hero Element: `Traveling Light`
- Camera: fixed

D tests whether independently registered layers can exchange the visual lead while the locked composition remains intact. It does not promote a Motion Grammar and it does not change A, B, C, Section 4, or Final.

## Nine registered layers

1. Background
2. Earth
3. Clouds
4. Connection Line
5. Traveling Light
6. Hill
7. House
8. Trees
9. Window Glow

All files use the source's 720×1280 canvas. Background is necessarily opaque; the other eight PNGs have transparent surroundings. Recomposition is pixel-exact against `section-0-working-lock.jpg`: MAE 0.0, maximum channel error 0, changed channel values 0.

The masks are deterministic and source-derived. Cloud and window motion expose small source-derived local underlays. No AI fill, image generation, external upload, new star, particle, object, or camera movement is used.

## Beat and role handoff

| Time | Lead | Action |
| --- | --- | --- |
| 0.00–0.30 | Background | Restrained moving color field prevents a dead opening. |
| 0.05–0.80 | Earth | A local wake at the existing departure point suggests the world awakening; the globe stays fixed. |
| 0.30–4.30 | Clouds | Two cloud groups drift at different speeds and directions. |
| 1.10–1.50 | Traveling Light | The source-derived light clearly departs. |
| 1.50–2.60 | Traveling Light | It follows all 36 locked path coordinates toward the home, with a short additive trail. |
| 2.60–3.30 | Trees | Two tree groups react with a small timing offset. |
| 3.30–3.90 | Hill / House | Local warmth rises; the house responds by at most one pixel. |
| 3.90–4.30 | Window Glow | Existing window light rises to the stable arrival state. |
| 4.30–5.40 | Hold | The complete arrived state freezes for 1.1 seconds. |

Only the lead and its immediate support move at any one beat. The motion uses layer depth rather than a global zoom.

## A/B/C/D distinction

- A: base motion; broad, restrained post-process response.
- B: layered semantic timing; connection is still read mainly through spatial response.
- C: source JPEG post-process with one path-following traveling light.
- D: source-registered asset layers plus traveling light, cloud depth, delayed tree reaction, hill/house warmth, and window settlement.

D is more continuously animated and makes the semantic relay visible. C remains the cheaper and simpler benchmark. D's principal risk is that layer separation can become visible if amplitudes are increased beyond this prototype.

## Self-review

- Meaning strengthened: yes; direction, transit, receipt, and settlement have separate beats.
- Still-image strength: retained; fixed camera and pixel-exact zero-motion recomposition.
- Motion density: materially higher than C without simultaneous whole-frame movement.
- Boundary quality: no unintended gap or halo was observed in inspected key frames at 0.2, 1.2, 2.2, 2.9, 3.6, 4.1, and 4.6 seconds.
- iPhone legibility: the light uses the source light itself, a small warm core, and a restrained 7 px glow; it remains readable in the 540×960 encode.
- Hold: stable from 4.3–5.4 seconds.
- AI-video feel: absent; geometry is never regenerated or interpolated.

## Reusable primitives

- Same-canvas registered RGBA layer contract
- Deterministic semantic masks with pixel-exact recomposition evidence
- Multi-rate source-layer drift over a local source-derived underlay
- Locked polyline arc-length traversal
- Arrival-triggered dependent-layer response
- Lead-role timeline with a fail-closed pre-Hold continuity test
- Frozen-state Hold contract

Section 4 can reuse verification points, arc-length traversal, staggered layer groups, and arrival-triggered core response. Its actual masks and path logic remain Section-specific.

## Known limitations

- The Background layer is opaque by definition; only foreground semantic layers are transparent.
- Under-cloud and under-window areas are conservative local source reconstructions, not hidden source artwork.
- The layer-breakdown video intentionally exposes incomplete cumulative stages; missing later layers are not defects in the final composite.
- Device testing performed by the workflow and browser automation is a compatibility check, not a Founder/Compass aesthetic decision.
