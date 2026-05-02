# Asset and Generated File Layout

This repository uses `assets/` as the only root-level game asset directory.
Do not recreate the legacy misspelled asset root.

## Runtime Assets

- `assets/battle/maps/<map_id>/`
  Baked battle map images, masks, and `map_meta.json`.
- `assets/battle/units/sheets/`
  Runtime unit animation sprite sheets imported by the web app.
- `assets/battle/units/manifests/`
  Runtime unit animation manifests. Manifests should point to sheet assets only.
- `assets/battle/vfx/<skill_id>/`
  Runtime skill VFX sprite sheets and VFX manifests.
- `webapp/assets/`
  Web-app-only UI images referenced directly by CSS or React code.

## Generated Outputs

- `dist/`
  Vite build output. Do not commit generated bundles.
- `logs/`
  Local run logs and visual verification captures. Do not put logs in the repo root.
- `reports/`
  Human-readable analysis reports.
- `tmp/`
  Scratch files and throwaway generation intermediates.

## Hygiene Checks

Run this before committing asset or root-layout changes:

```powershell
npm run check:hygiene
```

The check rejects:

- The legacy misspelled root-level asset directory.
- Root-level `.log` or `.err.log` files.
- Unexpected new files in the repository root.
- Legacy asset-root references in project text files.
