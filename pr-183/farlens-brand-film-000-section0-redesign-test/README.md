# FARLENS Brand Film #000 — Section 0 Redesign Test

Status: WORKING TASTE TEST — NON-CANONICAL

Section 0 only. Six 9:16 studies: A1/A2, B1/B2, C1/C2. Section 1/2, Motion, and the 55-second film are intentionally excluded.

- `composites/`: six 1080 × 1920 PNG masters and SVG counterparts.
- `source/variants/`: editable deterministic SVG sources.
- `source/shared/atmosphere/`: built-in ImageGen background plates and lightweight derivatives.
- `previews/`: iPhone list JPEGs and contact sheet.
- `index.html`: iPhone-first comparison page; JPEG list, full PNG on tap.

Run `node record-render.mjs` for the complete reproducible path: it rebuilds SVGs, renders six 1080 × 1920 PNGs through Chrome/Chromium, refreshes JPEGs and the contact sheet, records hashes for every direct input/output, and clears its temporary browser profile. `node verify.mjs` is read-only and refuses stale render lineage.
