# FARLENS Brand Film #000 — Section 0 Zero-base Taste Test

Status: WORKING TASTE TEST — NON-CANONICAL

Section 0 only. The previous six directions, Section 0→1 connection work, Motion, Section 1/2, and the 55-second film are stopped. The review surface contains three new 9:16 studies only.

- `source/directions/`: six editable SVG layers per direction (Background, Main subject, Supporting elements, Atmosphere, Typography, Transition candidate).
- `composites/`: three 1080 × 1920 PNG masters and reproducible SVG composites.
- `previews/`: lightweight iPhone JPEGs and a three-up contact sheet.
- `index.html`: iPhone-first comparison page with full-resolution tap enlargement.

No ImageGen, external image, reference image, old logo asset, or raster input is used. `node record-render.mjs` composes the existing editable SVG layers without regenerating them, renders masters, refreshes previews, and records the complete lineage. `node verify.mjs` is read-only and rejects stale lineage, embedded images, old direction names, and old-logo references. `node build.mjs --initialize` is an explicit destructive reset to the initial vector study and is not part of the normal render workflow.
