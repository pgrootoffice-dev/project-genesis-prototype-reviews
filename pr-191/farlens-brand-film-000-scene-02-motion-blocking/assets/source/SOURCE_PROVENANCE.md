# Source Provenance

Status: **WORKING TEST / NON-CANONICAL**

## Adopted Scene 2 inputs

Source: Draft PR #190, branch `claude/scene-2-static-sequence-pd7vm3`, commit `86b4f098d8d3a8dbefe5495dd53fd34f1af1d8ec`.

The five PNGs under `docs/farlens/brand-film/assets/scene-02/` are read directly by the renderer. They are not regenerated, edited, overwritten, or reordered.

| Frame | SHA-256 |
| --- | --- |
| A1 | `6c4d3f3896889db7a8e16802c92b8d739a4bc5342bdbfaeb12851523606fbc8d` |
| A2 | `c4f16462dbe58888a5072a6d023e39db877c57811b5041a444eeb8cc07e57122` |
| A3 | `dbc4f9c4449d23c72fca7d649b5d54112c2ecd00828c0ddf11598d78e6e23cac` |
| A4 | `b909d73c727d937ee8acf63ceee247214cecd46f888ceecabde50fdd227b7274` |
| A5 | `8ce4ad337213db9b99e0b75f973266494abb5d1fbcfe6d7f9468e1f59071dcc1` |

## Scene 1 transition input

`scene-01-terminal-review.png` is a review-only frame extracted at 9.95 seconds from PR #188's master MP4 (`f684be2e...d1b79`). It is used only for the Scene 1→2 transition sheet and pre-roll review clip. It is never inserted into the 13.000-second Scene 2 master.

- Extracted PNG SHA-256: `32b9a74ea1ee1a01386671726abb47201bdcbc7c3ff4dd2f59a51cd157258c1c`
- Reference implementation: Draft PR #188, commit `0c78afc7ff7205df70c43723439a33fd68904196`

## Compass revision baseline

`revision-01/scene-02-motion-blocking-before-revision.mp4` is the exact Master reviewed from Workflow Run `31072498229` / Artifact `8956156501`. It is retained only to build the requested same-time before/after sheet and quantitative revision evidence.

- Baseline SHA-256: `9667cfef2be62c8fa7b00713daa13bcdcda6e0c6d96b28785498b91b2536bfc2`
- It is not used as a visual source in the revised Master.

## Authority boundary

- PR #190 and PR #188 remain unchanged.
- Static Sequence adoption, script, Beat structure, and Genesis OS are unchanged.
- This prototype is Pipeline Stage 3 Motion Blocking, not Final Motion or Canonical Motion Grammar.
