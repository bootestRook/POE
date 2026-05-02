## Context

The map editor already authors monster spawn points and boss groups through `spawnPlans`, and the WebApp runtime initializes authored encounters at battle start as lightweight enemy records. Runtime performance is currently protected by spatial chunk queries, activation tiers, and render limits, but encounter behavior is still distance-tier driven: nearby enemies move toward the player, distant enemies become dormant again, and enemies outside the render range are not shown.

The new requirements add designer-authored aggro ranges, persistent group aggro, random count multipliers, and an editor jump list. The key constraint is to make authored enemies feel present at battle start without simulating or rendering every monster every frame.

## Goals / Non-Goals

**Goals:**

- Let designers adjust a separate aggro/search radius for every monster spawn point and boss group.
- Make the runtime trigger all monsters from a point or boss group when the player enters that point's aggro radius.
- Keep triggered enemies locked onto the player until death or battle reset.
- Roll actual monster counts from decimal multiplier ranges at battle start using floor rounding.
- Add map editor navigation for quickly selecting and jumping to authored monster/BOSS points.
- Improve visual presentation so enemies inside or near the camera can appear before aggro while distant enemies remain lightweight.

**Non-Goals:**

- Add full patrol, leash, stealth, faction, or multi-target threat systems.
- Add formal monster database/content tables.
- Change skill targeting, damage, loot, inventory, or gem board rules beyond consuming the updated enemy records.
- Replace the current React/DOM renderer with canvas or WebGL.
- Persist runtime aggro state back into map JSON.

## Decisions

### Store Aggro And Count Multiplier Data On Authored Points

Add optional fields to saved `spawnPlans` entries:

```ts
type MapEditorMonsterSpawnPoint = {
  aggroRadius: number;
  countMultiplierMin: number;
  countMultiplierMax: number;
};

type MapEditorBossGroup = {
  aggroRadius: number;
};
```

`radius` remains the spawn sampling range. `aggroRadius` is a separate search range. Count multipliers apply only to monster spawn points; boss groups keep explicit `bossCount` and `bossIds` so boss encounters remain deliberate.

Default normalization should keep old maps valid:

- Monster aggro radius defaults to `max(radius * 3, 6)` cells.
- Boss aggro radius defaults to `max(radius * 4, 8)` cells.
- Monster multiplier defaults to `[1, 1]`.
- If min is greater than max, normalization swaps or clamps to a valid ordered range.

Alternative considered: reuse `radius` for both spawn placement and aggro. That would make compact monster packs aggro too late and large spawn circles aggro too early.

### Render Separate Editor Rings For Spawn And Aggro

The editor overlay should draw the spawn radius and aggro radius distinctly. The selected encounter can expose two resize handles or a clear mode-specific handle so designers can adjust aggro without accidentally changing spawn placement.

Alternative considered: numeric-only aggro editing. It is simple, but hard to tune spatially on large maps.

### Add Encounter Jump Navigation

The encounter panel should list monster spawn points and boss groups in a dropdown or compact select list. Choosing an entry selects it and pans the editor camera to that point. This is editor-only state and should not alter saved encounter data.

Alternative considered: search by ID only. IDs are useful internally, but a list with type and coordinates is faster for level authoring.

### Treat Aggro As Runtime Source State

Runtime enemies should carry their `spawnPlanSourceId`, and the runtime should track triggered source IDs for the current battle. When the player enters a source aggro range, every living enemy with that source ID becomes `aggroLocked`.

`aggroLocked` is monotonic for the battle: once true, the enemy continues chasing while alive. It is reset only by starting a new battle or recreating enemies.

Alternative considered: recompute aggro purely by current player distance every frame. That recreates leash behavior and contradicts persistent chase.

### Separate Logical Presence From Visual Rendering

Authored enemies should still be created at battle start. To prevent pop-in, enemies inside or near the camera can render as idle/visible even before aggro, while distant enemies remain lightweight records. Aggro should decide pursuit; visibility should decide presentation.

Implementation can keep the current render budget and spatial index, but selection should consider camera/viewport proximity rather than only player proximity where practical. Triggered enemies can be updated at a reduced cadence when far away and promoted to full active movement near the player.

Alternative considered: eagerly render every authored enemy after battle start. That makes presence obvious but risks frame drops on large maps.

## Risks / Trade-offs

- High monster counts still exceed DOM budget -> Keep visible enemy rendering capped and prioritize camera-visible or nearby enemies.
- Aggro range checks scan all source points every frame -> Use low-frequency checks or source spatial lookup if point counts become large.
- Triggered distant packs chase through long routes too cheaply or too expensively -> Use reduced-frequency movement for far aggro-locked enemies and full updates near the player.
- Existing saved maps lack new fields -> Normalize missing values to defaults and write the expanded shape only when saving.
- Designers confuse spawn radius and aggro radius -> Use distinct labels, colors, and handles in the editor.

## Migration Plan

No file migration is required. Existing map JSON remains loadable because new fields are optional and normalized at load time. Saving a map after this change writes the normalized aggro and multiplier fields.

Rollback can ignore `aggroRadius`, `countMultiplierMin`, `countMultiplierMax`, and runtime `aggroLocked` fields while preserving existing spawn placement data.

## Open Questions

- Should the encounter jump list display designer-friendly aliases later, once formal monster/BOSS content tables exist?
- Should future boss groups get count multipliers too, or remain explicitly authored for encounter control?
