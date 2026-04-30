---
name: make-iso-map-tiles
description: Use when generating, correcting, previewing, confirming, slicing, and saving 128x64 isometric map tile raw sheets for this POE project. Enforces a user-confirmed split-line preview before any cropped tiles are written into assest/battle/tiles.
---

# Make Iso Map Tiles

## Purpose

Create production-ready isometric map tiles for this repo. The default target is:

- raw sheets: `assest/battle/tiles/raw/`
- cropped tiles: `assest/battle/tiles/cropped/`
- QA previews and manifests: `assest/battle/tiles/manifests/`
- tile crop size: `128x64`
- safe visible content box: at most `104x48`, centered inside the `128x64` crop
- tile layout: centered tile artwork inside larger cells, usually `4x4`

## Non-Negotiable Confirmation Gate

Do not slice or save cropped tiles into the project asset folders until the user has explicitly approved the split-line preview.

Required approval sequence:

1. Generate or repair the raw sheet.
2. Create a split-line preview that shows:
   - the large sheet cell boundaries
   - the exact `128x64` crop box for every tile
   - the center point of every crop box
   - no extra inner crop frame; slicing is based on the outer `128x64` crop box only
3. Show the preview image to the user.
4. Ask for confirmation if approval is not already explicit.
5. Only after confirmation, run slicing and write cropped assets.

If any tile is not centered, touches the `128x64` crop frame, overlaps another tile, or sits too close to a neighboring tile, fix the raw sheet and repeat the preview/confirmation step.

## Workflow

Plan before editing:

```text
Plan:
1. Inspect tile asset folders and current raw sheet -> verify: destination and dimensions are clear
2. Generate split-line preview -> verify: every tile is centered in a 128x64 box
3. Wait for user confirmation -> verify: explicit approval before saving cropped tiles
4. Slice approved raw into cropped assets -> verify: every output is 128x64 RGBA and non-empty
5. Save manifest/contact sheet -> verify: paths and metadata parse correctly
```

## Raw Sheet Requirements

When prompting image generation or repairing generated output:

- Use a solid `#FF00FF` background outside tile art when possible.
- Keep each tile in its own large cell with generous spacing.
- Keep the visible tile art fully inside a centered safe box within the `128x64` crop. Default safe box: `104x48`.
- Do not allow tile corners or outlines to touch the `128x64` crop border. The crop must include visible transparent padding around the whole tile.
- Do not draw the safe box as a second frame in previews. The visible preview frame should be the actual `128x64` crop only.
- If generated tiles are oversized and must be repaired, rebuild from the original full raw image, not from already-cropped outputs.
- When shrinking detailed painted tiles into `128x64`, apply sharpening after resize so the final cropped tiles remain readable.
- Use low, flat ground art only for `128x64` ground tiles. Avoid tall props, trees, cliffs, pillars, labels, UI, or shadows that exceed the crop box.
- Preserve the requested art style, but prioritize deterministic slicing over visual density.

## Script

Use `scripts/slice_iso_tiles.py` for preview and slicing.

Optional adjustable HTML preview before final confirmation:

```powershell
python .codex\skills\make-iso-map-tiles\scripts\make_adjustable_crop_preview.py `
  --raw assest\battle\tiles\raw\example.png `
  --out assest\battle\tiles\manifests\example-adjust-crop.html `
  --cols 2 `
  --rows 2 `
  --cell-size 896x560 `
  --tile-size 704x448
```

Use the HTML page to tune the blue crop frame. This does not write cropped
tiles. After the user confirms a crop size, pass the same `--tile-size`,
`--cols`, `--rows`, and `--cell-size` values to `slice_iso_tiles.py`.

Preview only:

```powershell
python .codex\skills\make-iso-map-tiles\scripts\slice_iso_tiles.py `
  --raw assest\battle\tiles\raw\example.png `
  --mode preview `
  --preview assest\battle\tiles\manifests\example-split-preview.png `
  --safe-size 104x48
```

Slice only after user approval:

```powershell
python .codex\skills\make-iso-map-tiles\scripts\slice_iso_tiles.py `
  --raw assest\battle\tiles\raw\example.png `
  --mode slice `
  --confirmed `
  --out assest\battle\tiles\cropped `
  --manifest assest\battle\tiles\manifests\example-manifest.json `
  --contact assest\battle\tiles\manifests\example-contact-sheet.png `
  --prefix example_tile `
  --safe-size 104x48
```

Use `--names` with a comma-separated list when the user or current pack has meaningful tile IDs.

## Validation

After slicing, report:

- raw path
- split preview path
- cropped output directory
- manifest path
- contact sheet path
- output count
- validation result

Every accepted cropped tile must be:

- exactly `128x64`
- PNG with alpha (`RGBA`)
- non-empty after magenta chroma key
- visible content fully inside the centered safe content box, default `104x48`
- no visible pixel touching the `128x64` crop border
- derived from a centered crop box that was previously shown to the user

If validation fails, do not present the outputs as finished. Fix the raw sheet or crop settings and repeat the confirmation gate.
