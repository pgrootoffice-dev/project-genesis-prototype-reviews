# Living Storybook Prototype 1

Status: NON-CANONICAL INTERACTIVE PROTOTYPE
Date: 2026-07-16
Related records:
- `../../docs/genesis-os/education-adventure-ip/DESIGN_PRINCIPLES.md`
- `../../docs/genesis-os/education-adventure-ip/PROTOTYPE_1_EXPERIENCE.md`
- `../../docs/genesis-os/education-adventure-ip/PROTOTYPE_1_INTERACTION.md`
- `../../docs/genesis-os/education-adventure-ip/VISUAL_LANGUAGE.md`
- `../../docs/genesis-os/education-adventure-ip/PLATFORM_AND_DISTRIBUTION.md`
- `../../docs/genesis-os/source-events/2026-07-15_living-storybook-infinite-atlas.md`

## Purpose

This prototype extends the Living Storybook Prototype 0 first Web screen into the minimum interactive Prototype 1.

It asks whether the entrance can feel like a quiet living illustrated page that notices the viewer, rather than a normal website hero, game UI, or generic AI fantasy image.

## Scope

Included:

- one no-build HTML page
- CSS-only layered placeholder world
- a visually central shoreline threshold and quiet light source
- local pointer, touch, and keyboard response through light, atmosphere, and depth
- automatic return to calm after each response
- reduced-motion support
- iPhone Safari-friendly viewport settings
- replaceable structure for a future high-quality world image

Not included:

- final visual style
- final world bible
- login
- payment
- map system
- learning system
- backend
- Cloudflare deployment
- generated production image assets

## Interaction

The complete world surface is the single interaction area. Touch or click anywhere to create a small local response; mouse or pen presence adds only restrained layer depth. The stable composition and text do not move, and the response settles without navigation, reward, sound, or accumulated state.

## Development Check

From the repository root:

```sh
python -m http.server 4173 --directory prototypes/living-storybook-first-screen
```

Then open:

```text
http://localhost:4173/
```

This localhost route is for Builder development checks only. It is not a supported Founder review entry point.

`IPHONE_PREVIEW.md` defines the one supported Founder review path and requires Codex / Builder to provide the verified HTTPS URL directly.

## Next Image Asset Need

The next visual step is a high-quality 16:9 or 4:5 world illustration designed for layer separation.

Minimum useful layers:

- background sky / atmosphere
- distant architecture or landform
- water or reflective surface
- mist / light / particles
- foreground framing
- optional small guide or scale element

The image should avoid generic AI fantasy, typical RPG UI, heavy game HUD, and luxury-only fantasy.
