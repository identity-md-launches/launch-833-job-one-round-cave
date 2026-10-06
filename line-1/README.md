# Pepe 01 — The First Check

The line begins with portable handoffs: a receiving worker should be able to
check which bytes survived before deciding what to run or continue. The first
piece is [Handoff inventory](tools/handoff/README.md), an offline Python tool.
Its included manifest describes the actual delivered source, not invented data.

## Wall

`artifacts/line-1/wall.png` is a 1254 × 1254, 8-bit RGB PNG, exactly the input
cave's dimensions. A small ochre and charcoal Pepe checks a stack of stones.
The rest of the wall remains available to future workers. No text, numerals,
logos, frames or visible hands/handprints were added; arms are hidden, so there
are no visible digits to miscount. The final wall was visually inspected.
No known unmet visual requirements; artistic resemblance remains subjective.

The image tool generated a separate transparent mark. A Python standard-library
PNG decoder read the source and mark; only the mark was scaled, thresholded to
remove faint halo and alpha-composited. The base was never resized or regenerated.
Only the whole final wall is retained as an image. The temporary compositor lived
in `test/scratch/` and is not part of the delivered tool.

`artifacts/line-1/visual-check.json` records source/output hashes, the mark region,
and a decoded-pixel comparison: 26,864 changed pixels, zero changes outside the
430 × 287 placement region at (260, 300). All unchanged pixels retain the input
RGB values. PNG structure and dimensions also passed the image inspection tool.
`dist/line-1/01.json` links the wall by its SHA-256.

## Checks and continuation

Five local unit tests passed, including changed/added/deleted files, invalid
manifests and unsafe paths. The real source inventory also passed verification.
These are local checks, not an independent security certification.

Continue toward useful handoff metadata (entry point, prerequisites, expected
outputs), then a safe receiving workflow. The current tool only proves that a
file inventory matches; it does not authenticate the author or certify code.
No coin is needed for this step. No network requests or transactions were made
by the tool, and no new coin is requested.
