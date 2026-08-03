# Section 0 Motion C — Design, Evidence, and Cost Notes

Status: WORKING TEST / NON-CANONICAL

Scope: Section 0 C only. A, B, Section 4, and Final are byte-locked and unchanged.

Design authority: PR #186, commit `6cfde74041e7a64e791bac31b15d61db772521cc`, `docs/farlens/brand-film/SECTION_00_MOTION_C_DESIGN_REVIEW.md`.

## Semantic contract

- Motion-level Meaning Verb: `届く`
- Section-level arc: `つながる`
- Hero: the Traveling Light that follows the locked orange connection line
- Duration: 5.4 seconds
- Camera: fixed
- Hold: 4.30–5.40 seconds (1.10 seconds)

Motion Order:

1. 0.00–1.10s — background color presence and two cloud regions wake at different rates; Earth itself stays fixed.
2. 1.10–3.90s — one compact warm light travels from the Earth origin to home at constant distance along the locked source path. Only an additive passed-segment trail and a weak local color-plane response accompany it.
3. 3.88–4.30s — the traveler yields to a warmer home/window/hill response, then all operations freeze for the hold.

## Layer construction

Six semantic layers are implemented: Background; Earth plus two cloud source regions; locked Connection Line; Traveling Light plus additive trail; Home plus Window Light; local Background Reactive Glow. They map to the nine design roles without unnecessary independent cutouts.

Every frame begins from the complete locked JPEG. Three feathered source-region masks are hand-defined: Cloud 1, Cloud 2, and Home. No missing background is synthesized. The line path uses 36 measured coordinates sampled from orange source pixels; its shape is neither redrawn nor replaced. The light core is part of the single Traveling Light hero, not a star or particle system.

## A/B/C review

- A: restrained Base Motion; progression is subtle.
- B: separates world, connection, and family semantically, but progression is mainly a spatial reaction around an already-visible line.
- C: makes direction literal by moving one source-path-following light from world to home, then holding the received warmth.

Self-review: the traveler is legible in the 540×960 encode, the camera and Earth remain fixed, the locked composition stays underneath all overlays, and no generative deformation is possible. C increases perceived animation and `届く` clarity without changing the source route. The main risk is taste, not integrity: the CEO/Compass should decide whether the compact light is still restrained enough for FARLENS.

## Cost record

Observed Codex wall clock: the existing-file lock was recorded at 13:48 JST; the first passing C render completed at 13:54; path visibility and maximum-change acceptance completed at 13:56 (8 minutes for the C implementation/tuning pass). Local Bridge and 390×844 browser acceptance concluded at 15:45 after an extended browser-environment wait; that wait, publication, and CI are excluded from the implementation estimate. This elapsed time benefits from the existing B renderer and Bridge harness and is not a human production estimate.

Planning estimate inherited from the PR #186 design review: approximately 60–90 minutes incremental over B, or 1.5–2.5 engineering hours for a standalone Section 0 C pass including mapping, tuning, evidence, and device review. Against the prior B Section 0 allocation of 18 minutes, the section-specific increment is approximately +330–500%; when shared render, comparison, evidence, and Bridge work is included, the expected total-work increase is approximately +55–85%.

- Semantic layers: 6
- Manual masks: 3
- Path coordinates: 36
- Reused from B: locked-JPEG base, phase/easing helpers, additive glow/path helpers, source-region duplicate, H.264 packaging, checksum lock, Review Bridge
- C-specific: constant-distance polyline follow, traveler-to-arrival handoff, passed-segment trail, distinct origin/home reactions, A/B/C packaging
- Reusable primitives: Source-Path Traveling Light; Arrival → Settle → Hold; low-amplitude local color-plane reaction
- Section 4 transfer: the constant-distance follower can traverse its locked flows, but would change the semantic emphasis and therefore needs a separate design decision; do not apply automatically
- Other-Section transfer: suitable only for a locked composition whose meaning is transmission, guidance, handoff, or arrival and whose path already exists

Full-film estimate: do not apply C to all 11 Sections indiscriminately. For an eligible 3–5 Sections, allow roughly 0.5–1.0 hour per Section after the primitive is stable, plus semantic/path QA. Applying bespoke path mapping and evidence to all 11 would add approximately 8–14 engineering hours to the existing layered-motion estimate, excluding review revisions and any section that cannot be separated without reconstruction.

## Evidence

`section-0-c-technical-evidence.json` records codec, duration, dimensions, hold difference, 36 path coordinates, deterministic method, existing A/B/Section 4/Final locks, and maximum-change timestamp. `section-0-c-checksums.sha256` locks every new C/comparison output. The Review Bridge additionally generates timeline frames, Contact Sheets, source comparison, manifest, public verification, and the Actions Artifact.
