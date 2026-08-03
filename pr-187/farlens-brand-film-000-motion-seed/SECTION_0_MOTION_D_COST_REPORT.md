# Section 0 Motion D — Cost Report

Status: WORKING ESTIMATE / NON-CANONICAL
Measurement basis: Codex implementation wall-clock plus human-production planning estimate

## Recorded implementation pass

| Work | Elapsed |
| --- | ---: |
| Material separation | 6 min |
| Layer reconstruction / underlay tuning | 9 min |
| Motion implementation and eight video encodes | 9 min |
| Visual adjustment, evidence, Review Bridge, and PR QA | 26 min |
| Total | 50 min |

The elapsed values measure this deterministic prototype pass, including automated renders. They are not a claim that a human motion designer can complete a visually approved scene in 50 minutes.

## Complexity

- Layer count: 9
- Manual semantic masks: 8
- Locked path coordinates: 36
- Reused from C: path coordinates, arc-length interpolation, additive trail convention, H.264/iPhone encodes, A/B/C SHA lock, Review Bridge
- D-specific: layer extractor, source-derived cloud/window underlays, cloud sublayers, tree deformation, hill warmth, house response, window settlement, role-handoff and continuity evidence, layer-breakdown render
- Section-specific: all spatial masks, cloud group boxes, tree pivots, house/window regions, response timing

## Planning estimate

- Next scene of the same visual complexity: 2–3.5 human hours after the reusable harness exists
- Full 12-screen expansion: 28–48 human hours for first-pass separation, motion, and QA, before stakeholder revision
- Templateable share: roughly 55–65% of renderer, evidence, comparison, and Review Bridge mechanics
- Section-specific share: roughly 35–45%, dominated by semantic masks, hidden-area treatment, paths, pivots, and timing

## Compared with C

- Quality: D adds perceptible layer depth and a clear Earth → Clouds → Light → Family handoff. It offers more motion density and stronger semantic staging while preserving the source composition.
- Cost: the PR #186 planning model estimates D at 2–3.5 human hours versus C at 1.5–2.5 hours: +0.5–1.0 hour, approximately +20–67% depending on scene complexity.
- Decision: use D only where independent roles materially improve the script meaning. C remains preferable where a single path hero is sufficient.
