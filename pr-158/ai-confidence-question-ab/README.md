# Oxygen Short — A/B Visual Test (Question-led Short vs. Quiz-led Short)

Status: NON-CANONICAL WORKING PROTOTYPE
Date: 2026-07-30
Prototype ID: `FRL-P-0002` (same ID/branch/PR as before — this is a full content
revision of the existing Prototype, not a new one)

Related records:

- `../../docs/genesis-os/education-adventure-ip/research/FRL-R-0004-kurzgesagt-one-screen-one-meaning.md` — the Research Entry whose candidate Production Grammar hypotheses this Prototype tests
- `../../docs/genesis-os/education-adventure-ip/research/README.md` — FARLENS Research Lab (Promotion Path)
- `../../docs/genesis-os/ACTIVE_DIRECTION.md` — Creator Intelligence, Reference Diversity Rule, "Next Content Prototype" conditions
- `../../docs/genesis-os/DO_NOT_RESTORE.md` — retired directions this Prototype does not touch
- `../../docs/genesis-os/education-adventure-ip/FARLENS_VISUAL_DESIGN_RULEBOOK.md`, `FARLENS_VISUAL_SYSTEM_BLUEPRINT.md`
- `../research-two-beat-reveal/` — the existing `prototypes/` placement and GitHub Pages review convention this Prototype reuses (no new mechanism introduced)

## Revision note (2026-07-30) — why this exists

The CEO reviewed the previous revision of this Prototype (the "AI Confidence"
theme) directly on iPhone and found both variants too content-poor to fairly
judge Question-led vs. Quiz-led as structures: neither variant made the CEO
want to keep watching, and the thin asset/motion density made the comparison
close to meaningless. The CEO also retired the old "違和感" review axis
permanently — it is not used anywhere in this revision (see "CEO Review
Points" below and `IPHONE_PREVIEW.md`).

**This revision keeps the same branch, same Draft PR, and the same directory
and file names** (`a.html`, `b.html`, `index.html`, `shared.css`,
`scene-engine.js`, `ai-confidence-ab.behavior.test.mjs`) even though the
subject matter changed completely, specifically so the GitHub Pages preview
workflow (`.github/workflows/living-storybook-preview.yml`) — which detects
and publishes prototype directories by name — does not leave a stale,
orphaned directory on the external `project-genesis-prototype-reviews` Pages
repo. No new branch, PR, or publishing infrastructure was created.

What changed in this revision:

- **New subject**: 「もし、空気中の酸素が5秒だけ消えたら？」 (see "Scope of
  the Scenario" and "Research" below), replacing the previous "AI confidence"
  theme entirely.
- **Full visual rebuild**: `shared.css` and `scene-engine.js` were rewritten
  with a much larger semantic-geometry component library (ground, sky,
  atmosphere/O2 particles, city skyline, person, animal, vehicle, flame,
  time-dial, causal-line, camera push/pull/pan + real parallax) and both
  `a.html`/`b.html` were rewritten scene-by-scene at meaningfully higher
  asset and motion density than the previous revision.
- **CEO Review reduced to exactly 4 questions** (down from a longer, looser
  list that included the retired "違和感"/"FARLENSらしいか"/"世界観" axes) —
  see `IPHONE_PREVIEW.md`.

## Scope of the Scenario (must be read before the Research table)

The scenario is precisely: **only the free O2 molecules currently in the
atmosphere vanish, for exactly 5 seconds, then return.** It explicitly does
**not** mean:

- oxygen bound in water (H2O), rock/minerals, living tissue, or building
  materials disappearing
- "all of Earth's oxygen" disappearing permanently
- any change to non-oxygen atmospheric gases (nitrogen ~78%, argon, CO2, etc.)

This framing is shown once, briefly, in small text ("空気中の酸素だけ") in
the shared Opening of both variants, and is never explained at length inside
either video — the precision lives here in the README, not on screen.

## Research (institutional/peer-reviewed sources only)

Every claim used in either variant is classified below. **Confirmed** =
directly stated by a NASA/NOAA/university/peer-reviewed/public-institution
source. **Reasonable inference** = a straightforward, undisputed application
of confirmed general physics/chemistry to this specific hypothetical (no
institution has studied "atmospheric O2 vanishing for 5 seconds" directly,
because it is not a real phenomenon). **Not confirmed / excluded** = no
qualifying source was found; the claim is not used anywhere in either
variant.

| # | Topic | Status | Source | Representation adopted in the Prototype | Child-facing simplification |
| --- | --- | --- | --- | --- | --- |
| 1 | Atmospheric O2 is ~20.9-20.95% of dry air by volume; N2 is ~78.08% | Confirmed | [NASA Science — The Atmosphere: Getting a Handle on Carbon Dioxide](https://science.nasa.gov/earth/climate-change/greenhouse-gases/the-atmosphere-getting-a-handle-on-carbon-dioxide/); [NOAA JetStream — The Atmosphere](https://www.noaa.gov/jetstream/atmosphere); [UCAR Center for Science Education — What's in the Air?](https://scied.ucar.edu/learning-zone/air-quality/whats-in-the-air) | Air is shown as a cluster of small two-circle "O2 glyph" particles among (implicitly) far more numerous other air content — O2 is drawn as present but a minority share, never as "most of the air" | "空気中の酸素だけ" caption; the O2 glyphs are deliberately sparse (5 particles), not filling the whole air layer |
| 2 | Total atmospheric pressure is the sum of each gas's partial pressure (Dalton's Law is a confirmed physical law) | Confirmed (the law itself) | General physics/chemistry (Dalton's Law of Partial Pressures) — not scenario-specific | Not directly dramatized (no pressure gauge/ring asset used in either variant this revision) | n/a |
| 2b | Applying Dalton's Law to "what would total pressure do if only O2 vanished for 5s" | Reasonable inference | Derived from #2 — removing ~21% of the gas mixture's molecules would reduce local total pressure by a comparable fraction while it's gone, as a simple closed-system approximation, not a rigorously modeled result (real air is not a closed system; wind/mixing complicate this) | Not shown as a specific numeric or gauge effect in either variant — flagged as a simplification we chose not to visualize this revision, to avoid overstating a modeled-but-unverified number | n/a |
| 3 | Flaming combustion generally cannot be sustained once ambient oxygen drops below roughly 15% (varies by fuel, ~14-17% for common organic materials) | Confirmed | [San Diego Fire-Rescue Department training manual — Fire Dynamics](https://www.sandiego.gov/sites/default/files/2025-03/fire-rescue-drill-manual-chapter-07.pdf) (public fire-service institution); general combustion chemistry (fuel + O2 -> CO2 + H2O + energy) | A's `a4-vanish`/B's `b5-vanish`: the `.flame` element visibly shrinks/dims (`.is-hidden-now`) in sync with the O2 particles vanishing, and recovers once O2 returns | "酸素が消えると、火は小さくなる。" — stated as "gets smaller," not "goes out entirely," since a full extinguish is a stronger claim than the general 14-17% threshold guarantees for a *brief* 5-second dip |
| 4 | A resting adult can voluntarily hold their breath for an average of roughly 30 seconds without ambient air, without harm | Confirmed | [Factors Affecting Voluntary Breath-Holding Duration and Breaking Point in Young Adults — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12110200/) | Neither variant shows a person in visible distress — the `.person-figure`/`.animal-figure` remain calm throughout both variants | n/a (deliberately *not* dramatized — see #5) |
| 5 | A person already breathing normally would not be expected to suffer meaningful harm from 5 seconds of ambient O2 absence | Reasonable inference | Derived from #4 — 5 seconds is far inside the ~30-second average voluntary breath-hold tolerance most people already have without training | Person/animal figures are drawn calm and unaffected in every scene of both variants; the video never claims or implies a person is harmed | n/a |
| 6 | Internal combustion requires an oxidizer (ambient O2); an excessively lean air-fuel mixture causes rough running/misfire, not necessarily a full stall | Reasonable inference (general combustion chemistry extended to any combustion engine; no institutional source studying this exact 5-second scenario was found) | Same combustion-chemistry basis as #3; general automotive engineering references describe lean-mixture misfire as roughing/stumbling, not automatic failure | A3/A4 (and B4's choice icon / B5): `.vehicle` gets a brief `vehicle-sputter` motion when O2 is gone — never drawn stopping, crashing, or failing | B's choice label reads "エンジンの調子が悪くなる" (runs rough) — deliberately not "止まる"/"stops," to avoid overclaiming beyond what #6's evidence tier supports |
| 7 | Aircraft jet engines also require ambient O2 for combustion (same general principle as #3/#6) | Reasonable inference | Same general combustion-chemistry basis; no institutional source was found studying a 5-second ambient O2 loss on an aircraft specifically | **Not used** — no aircraft/vehicle-in-flight asset appears in either variant, specifically to avoid dramatizing an unverified catastrophic claim (engine flameout, crash) | n/a |
| 8 | Sky color/appearance changes measurably within 5 seconds from a 21%-of-molecules removal | Not confirmed / excluded | No NASA/NOAA/university/peer-reviewed source addressing this specific hypothetical was found | **Not used as a real event.** Appears only as B's third quiz choice ("空の色が変わる"), explicitly as the *incorrect* option — used to test recognition of a plausible-sounding but unsupported claim, never depicted as actually happening | The choice-icon's `.sky-swatch.is-shifted` purple tint is the *hypothesis being asked about*, not a depiction of a real outcome — the Reveal never colors it as correct |
| 9 | Building/structural collapse, oceans vanishing, crust cracking, or any Earth-scale catastrophic claim from a 5-second atmospheric O2 loss | Not confirmed / excluded | No qualifying source found; these are the exaggerated claims already circulating in unreliable "viral" versions of this scenario online, which this Prototype explicitly does not adopt | **Not used anywhere.** The `.city-skyline`/`.building` assets are present as ordinary background scenery in every scene and never animate, crack, or react to the O2 event | n/a |
| 10 | Immediate human collapse/unconsciousness from a single 5-second event | Not confirmed / excluded (contradicted by #4/#5) | See #4 | **Not used** — see #5 | n/a |

## What Was Built

Two ~14.5-15.0 second, silent-by-default, vertical (9:16) HTML/CSS/JS "Short"
simulations sharing one Color Set, font stack, semantic-geometry asset
library, and scene-timeline engine — same medium and mechanism as the
existing `research-two-beat-reveal` Prototype (static, self-contained, no
server, no build step, all assets code-generated). **A and B share a
byte-identical Opening** (the same two scenes, same markup, same timing,
enforced by an automated test) — everything after that point is where the
two educational structures diverge; the subject, the scientific facts, the
Visual Asset set, Color Set, Font, and Sound conditions are otherwise the
same between them.

- **`a.html` — A: Question-led Short** (15.0s, 6 scenes: `open-world` /
  `open-question` / `a3-street` / `a4-vanish` / `a5-causal` / `a6-linger`). A
  straight event-progression: the street scene is established, the O2 event
  unfolds and its effects (flame, vehicle) are shown, a brief causal
  observation is made ("酸素が消えると、火は小さくなる。"), and the video
  ends on a lingering shot with an **open question** ("他には、何が変わると
  思う？") — never a resolving statement, never a choice.
- **`b.html` — B: Quiz-led Short** (14.5s, 6 scenes: `open-world` /
  `open-question` / `b3-prompt` / `b4-choice` / `b5-vanish` / `b6-insight`).
  Same Opening, then "先に起きるのは、どっち？", then **3** scientifically
  grounded choices (engine roughens / flame shrinks / sky color changes) each
  with its own small animated icon, held through a genuine ~2.6s judgment
  pause with no auto-highlight and no game-show gimmick, a quiet **color-only**
  Reveal on the correct pill (`エンジンの調子が悪くなる` and `空の色が変わる`
  never receive any highlight, before or after Reveal), then the same visual
  event as A plays out, ending on a short **causal-insight sentence** (「火が
  消えたのは、酸素が届かなかったから。」) — not merely "the answer was X."
- **`index.html`** — the CEO-facing comparison page: both variants embedded
  side by side, a one-line description of each, and the 4 review questions
  (see "CEO Review Points" below).
- **`shared.css`** — the Prototype-only Color Set, typography, phone-frame
  chrome, camera/parallax keyframe system, and every semantic-geometry shape
  used by both variants (see "Visual System" below).
- **`scene-engine.js`** — the dependency-free timeline runner. Every scene is
  pre-authored as static HTML; the engine only toggles which one is
  `.is-active` at the current playhead time, drives the progress bar, toggles
  `.is-revealed` on any `[data-reveal-at]` element once its own threshold is
  passed (optionally firing a short synthesized chime the instant that
  happens, via a paired `data-tone`), toggles `.is-hidden-now` on any
  `[data-hide-from]`/`[data-hide-until]` element for exactly that time
  window (used for the O2 particles and the flame, so cause and effect share
  one timing source), and (muted by default) plays short, fully-synthesized
  Web Audio tones/sweeps. Nothing is built dynamically.
- **`ai-confidence-ab.behavior.test.mjs`** — rewritten for the new theme; see
  "Automated Test Coverage" below.

### Explicitly not interactive / not a branching prototype

Both `a.html` and `b.html` autoplay linearly from start to end. The only
buttons are Play/Replay and an optional sound toggle — there is no
click-to-choose, no branching path, and no state that depends on a viewer's
tap. B's "choice" is something the viewer experiences by watching (three
options held on screen, then a quiet Reveal), the same way an actual YouTube
Short poses a question without requiring a tap. This is a deliberate design
constraint, consistent with `DO_NOT_RESTORE.md` item 5/9 (browser
choice-branching interaction is retired as FARLENS's production medium) and
`ACTIVE_DIRECTION.md`'s YouTube-premised direction.

## Visual System (Prototype-only hypothesis, judged directly this revision)

### Color Set — NOT Canonical, NOT Kurzgesagt's palette, NOT required to
match the previous revision

The CEO did not rate the previous Color Set highly, so this revision was
free to choose colors on their own visual merit rather than inherit the
prior set.

| Role | Hex | Meaning |
| --- | --- | --- |
| Background | `#14232b` | calm, dark-enough-for-contrast, not black |
| Background (soft) | `#1e343d` | one step lighter (choice cards) |
| Subject | `#f7f1e4` | person, animal — one consistent warm tone |
| Oxygen | `#5fd6c8` | the O2 glyph, progress bar, Reveal outline — the one "evidence" color |
| Fire / energy | `#f2965a` | flame, engine warmth |
| Structure | `#93a8ae` | ground, city silhouette, vehicle body |
| Sky | `#3f5c74` | sky band backdrop |

No red+black "danger" pairing anywhere. The "not confirmed" quiz option
(sky-color-changes) is never colored as wrong, before or after Reveal — see
Research row #8. Deliberately not Kurzgesagt's reported palette (deep
blues/purples with bright reds/oranges/yellow): this set uses a cool
teal-navy base, no saturated red, and each color has exactly one meaning
role (`FARLENS_VISUAL_DESIGN_RULEBOOK.md` Section 3). **This Color Set is a
Prototype-limited hypothesis and does not become FARLENS's Canonical Palette
from this Prototype alone.**

### Shapes (Semantic Geometry) — original, not references to any specific work

- **Oxygen** — an original two-circles-joined molecule glyph (`.o2-particle`,
  drawn via `::before`/`::after`), not any existing chemistry-kit or
  Kurzgesagt icon.
- **Air / atmosphere** — a loose cluster of the above glyphs inside a
  translucent band (`.air-layer`).
- **Disappearance** — shrink + fade (`.is-hidden-now`), never a hard cut.
- **Fire** — 3 overlapping soft lobes (`.flame`), gently alive at idle,
  visibly shrinking/dimming when O2 is gone.
- **Causality** — a drawn SVG connector (`.causal-line`) linking the air
  layer to the flame, using a stroke-dasharray "draw-in" technique.
- **Time (5 seconds)** — 5 discrete arc "beats" (`.time-dial`/`.dial-tick`)
  lighting up in sequence, not a literal running numeral.
- **Person / animal** — abstract single-tone silhouettes, no face, no named
  character.
- **Vehicle** — a plain rounded body + two wheels, no brand or specific
  real-vehicle silhouette.
- **City / building** — plain rectangles of varying height, purely
  geometric.

None of this imitates Kurzgesagt's specific Shape Language (their
round-body/stick-limb/eye-dot character construction, their icon set, or
their specific composition style) — see "Copy-Risk Guardrail" below.

### Typography

System font stack only (`-apple-system, BlinkMacSystemFont, "Hiragino Sans",
"Yu Gothic", "Noto Sans JP", system-ui, sans-serif`) — no bundled or
CDN-loaded font. Identical stack across A and B. 1-2 short lines per screen,
never a stacked paragraph; captions carry a built-in ~0.3s entrance delay
after a scene becomes active, which structurally helps keep "visual change
shown before text confirms it" true without extra bookkeeping.

### Sound

Silent by default. A muted-by-default 🔇 toggle exists on both variants and,
if unmuted, plays short, fully self-synthesized Web Audio tones — a blip for
scene transitions, a descending sweep specifically for the O2-vanish moment,
and a distinct blip fired once at the quiz's Reveal instant. No audio file,
no external library, no new paid service.

## Educational Structures Compared (both share subject/facts/Opening/assets)

- **A — Question-led**: progression through events, no choices, no early
  "answer" framing, ends on an open question.
- **B — Quiz-led**: "which happens first?" question, 3 grounded choices each
  with a small animated icon, a genuine judgment pause, a quiet color-only
  Reveal (no score, no correct/incorrect sound, no game-show gimmick), a
  final scene stating a short causal insight rather than just naming the
  answer.

## CEO Review Points (this revision — see `IPHONE_PREVIEW.md`)

Reduced to exactly 4 questions per explicit CEO instruction. The retired
"違和感" axis, "FARLENSらしいか," "世界観," and any Taste sub-category split
are not used anywhere in this revision's review UI:

1. 問い先行（A）とクイズ先行（B）、どちらが構成として強いか
2. 続きを見たいと思うか
3. 親として、自分の子どもに見せたいと思うか
4. アニメーションとして視覚的に魅力があるか

## Automated Test Coverage (`ai-confidence-ab.behavior.test.mjs`)

- research facts referenced in this README carry a Source URL and an
  explicit Confirmed / Reasonable inference / Not confirmed tier
- A contains zero `choice-pill`/`choice-stack` elements
- B contains exactly 3 `choice-pill` elements, a Reveal (`data-reveal-at`)
  landing at least 2s into the choice scene (a genuine pause) and before
  that scene ends, and no pre-Reveal styling distinguishing the correct pill
- the correct answer is never named/highlighted before the Reveal instant
- A and B's Opening (first two scenes) is byte-identical
- A and B both reference the full shared major-asset set (ground, air/O2,
  person, animal, vehicle, flame, city, time representation, background
  decoration, fg/mid/bg layering)
- A and B share the same Color/Font/Sound conditions (same `shared.css`,
  `scene-engine.js`, font stack)
- no external network reference anywhere (`http(s)://` src/href, `@import`,
  `fetch(`)
- no banned promotional phrase anywhere
- the retired term "違和感" does not appear anywhere in the CEO Review UI
  (`index.html`, `IPHONE_PREVIEW.md`)
- each variant's total duration is 10-15.5s with contiguous, gap-free,
  overlap-free scene timing

## What Was Fixed This Revision (real findings, not assumed-correct on first attempt)

While building the new camera-motion system, a real instance of the exact
bug class this codebase already guards against (see `scene-engine.js`'s
top-of-file comment) was found and fixed: `.cam-push`/`.cam-pull`/`.cam-pan`
and `.is-focus` were originally written as CSS `animation`s tied to a
**static** class present in the HTML from page load. Because a scene's own
`.is-active` class is what actually reveals it (via `opacity`), a bare
`animation` on a statically-present class would start counting from page
load and finish — freezing at its own end-state — long before that scene
ever became visible, exactly like the `animation-delay`-from-load bug this
project has already fixed once before. **Fix:** every such rule is now
scoped to `.scene.is-active .cam-push` (etc.) so the browser starts the
animation fresh only when the engine's own JS toggles `.is-active` at that
scene's real start time. The `prefers-reduced-motion` override block was
then updated to use the same selector shape (not just `!important` alone),
since two `!important` rules resolve by specificity — a lower-specificity
override would otherwise have silently lost to the new, more specific normal
rule and let motion leak through under reduced-motion. The vehicle's
"sputter" motion had the same static-class problem and was fixed the same
way, keyed to `data-reveal-at` (`.is-revealed`) instead of a static class.

Separately, the quiz Reveal needed a sound cue at its own sub-scene instant
(not just at a scene's start) — `scene-engine.js`'s `[data-reveal-at]`
handling was extended to optionally accept a paired `data-tone`, fired once,
the instant that one element's own reveal threshold is crossed, reusing the
same one-directional-toggle principle as the existing per-scene tone.

## Copy-Risk Guardrail / What FARLENS Must Not Copy

Never used anywhere in this Prototype: Kurzgesagt's bird or any other
specific character; their logo; their specific color set; their specific
icon set; their specific Shape Language as a whole; any specific
composition, Visual metaphor, or Motion Sequence from any Kurzgesagt video;
their narration wording, music, or SE; their world-view; any starfield/
cosmic background treatment; or any combined look that would read as "trying
to look like Kurzgesagt." This Prototype uses only the abstract structural
ideas named in `FRL-R-0004` (screen-time budgeting, progressive disclosure,
a companion-evidence pattern), re-implemented from scratch in FARLENS's own
Visual Core language, on FARLENS's own original subject matter.

## Evidence Status

- [x] Previous revision (AI-confidence theme) built, self-reviewed, and
  reviewed by the CEO directly on iPhone.
- [x] CEO Review result (previous revision): A was provisionally stronger
  than B, but **neither variant made the CEO want to keep watching**; the
  content was too thin to fairly judge Question-led vs. Quiz-led as
  structures, and the previous subject matter may not have suited video —
  asset count and animation richness needed to increase.
- [x] This revision: subject matter replaced, Visual/Motion density
  substantially increased, CEO Review reduced to exactly 4 questions, the
  "違和感" axis retired permanently, on the same branch/Draft PR.
- [ ] Prototype tested by a human reviewer this revision — pending (built
  and self-reviewed by Claude Code only so far; see PR body for the Artifact
  Review pass results).
- [ ] Child evidence — not collected.
- [ ] Parent evidence — not collected.
- [ ] Production evidence — not collected.
- **The underlying Production Grammar hypothesis (`FRL-R-0004`) is not
  promoted to Canonical by this Prototype's existence, this revision, or any
  future revision on its own** — that requires its own separate PR/Decision
  after real CEO/Compass review evidence exists.

## Rulebook / Blueprint Impact

No impact yet, and none is claimed by this Prototype's existence. The Color
Set above is explicitly Prototype-limited (see "Visual System"). Any future
promotion of any idea tested here into `FARLENS_VISUAL_DESIGN_RULEBOOK.md`,
`FARLENS_VISUAL_SYSTEM_BLUEPRINT.md`, or a Canonical Palette requires its own
separate PR/Decision after real CEO/Compass review evidence exists — this
Prototype does not perform or imply that promotion.

## Production Cost / AI Automation / Human Judgment

- **Estimated production cost**: low — both variants are code-generated
  static HTML/CSS/SVG plus a shared, dependency-free JS timeline engine; no
  external assets, no rendering pipeline, no paid tooling, no new API/
  subscription of any kind (see `CLAUDE.md` Section 6 cost ceiling). This
  full content rewrite was a same-day, same-branch, same-Draft-PR edit — no
  new infrastructure.
- **AI reproducibility**: high for this class of artifact — the
  scene-timeline structure, the semantic-geometry component library, the
  camera/parallax keyframe system, and the `data-hide-from`/`data-hide-until`
  cause-effect mechanism are all reusable for a future Short on a different
  factual subject.
- **What is/isn't automatable**: scene timing/gap checks, asset-set parity,
  Reveal-timing rules, and banned-phrase checks are fully automated (see
  "Automated Test Coverage"). What a human must judge — whether the story is
  actually engaging, whether A's open ending feels satisfying-open or just
  incomplete, whether B's pause feels genuine, whether either looks visually
  appealing as animation, whether a parent would want to show it to their
  child — is exactly what the 4 CEO Review Points ask for and cannot be
  automated.

## Development Check

From the repository root:

```sh
python3 -m http.server 4177 --bind 127.0.0.1 --directory prototypes/ai-confidence-question-ab
```

Then open `http://127.0.0.1:4177/` (the A/B comparison page) in a browser, or
`.../a.html` / `.../b.html` directly, and resize to a mobile width (e.g.
390px), or use browser devtools' device emulation for an iPhone viewport.
The local route is for Builder checks only — `IPHONE_PREVIEW.md` defines the
one supported Founder review path.

```sh
node prototypes/ai-confidence-question-ab/ai-confidence-ab.behavior.test.mjs
node --check prototypes/ai-confidence-question-ab/scene-engine.js
```
