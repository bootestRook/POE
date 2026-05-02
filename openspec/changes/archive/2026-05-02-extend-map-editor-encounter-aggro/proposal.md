## Why

Authored monster and boss points currently define where enemies are placed, but they do not let designers control when a whole pack becomes aggressive or how many monsters a point actually rolls for a run. This causes encounter pacing to feel abrupt, especially when enemies appear only after the player approaches, and makes map authoring harder once many encounter points exist.

## What Changes

- Add adjustable aggro/search ranges to monster spawn points and boss groups in the map editor.
- Trigger group-wide aggro when the player enters an encounter point's search range; every monster from that point locks onto the player.
- Preserve aggro once triggered so monsters keep chasing the player instead of returning to dormant behavior after the player leaves the range.
- Add per-monster-point random count multiplier ranges; actual spawned count becomes `floor(configured count * random(min, max))`, with decimal multiplier support.
- Add an encounter selection dropdown/list in the map editor that jumps the editor view to the selected monster point or boss group.
- Improve authored encounter runtime presentation so enemies are logically created at battle start, visible enemies do not pop into existence near the player, and distant enemies remain performance-friendly.

## Capabilities

### New Capabilities
- `map-editor-encounter-aggro`: Covers map editor authoring for encounter aggro range, random monster count multipliers, encounter navigation, and saved encounter data compatibility.

### Modified Capabilities
- `v1-minimal-sudoku-gem-loop`: V1 WebApp battle runtime consumes authored encounter aggro ranges, group aggro lock, random count multipliers, and start-of-battle encounter visibility/performance behavior.

## Impact

- Affected code: `webapp/App.tsx`, `webapp/styles.css`, `webapp/smoke-test.mjs`, and map editor JSON normalization/persistence.
- Affected data: `map/*.json` saved `spawnPlans` gain optional aggro and count multiplier fields with backward-compatible defaults.
- Affected runtime: authored enemy initialization, enemy activation tiers, aggro state, render selection, and spatial-index queries.
- No new external dependencies are expected.
