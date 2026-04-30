## Context

The SkillEditor already exposes projectile launch position through `behavior.params.spawn_offset.x` and `behavior.params.spawn_offset.y`. The battle preview also renders launch-point, target, direction, collision, and search-range debug overlays from the current editor draft.

The missing workflow is direct manipulation. Editors need to tune where the projectile appears relative to the player by looking at the scene, but currently must type numeric offsets in the right parameter panel and visually compare the result.

The existing editor draft and save validation should remain the source of truth. This change should add an editing mode around the current draft rather than adding a separate runtime coordinate system or bypassing `save skill package`.

## Goals / Non-Goals

**Goals:**

- Add a projectile launch-position adjustment mode entered from the "发射位置" section.
- Temporarily hide the full editor shell while adjustment is active, so the battle scene can be inspected and dragged.
- Show a draggable launch-point handle in the battle scene using the same projection and camera transform as existing runtime guide overlays.
- Convert the dragged world position into `spawn_offset` relative to the current player/cast source.
- Support confirm and cancel before returning to the full editor.
- Keep the result as editor draft data until the normal save action persists it.
- Keep all user-visible text in Chinese.

**Non-Goals:**

- Do not change Skill Runtime projectile spawning, trajectory, targeting, damage, or event order.
- Do not add new skill schema fields.
- Do not persist UI-only adjustment state to `skill.yaml`.
- Do not expand `fan_projectile`; fan-shaped projectile patterns should be represented by the generic `projectile` template using projectile count and spread-angle params.
- Do not modify gem board, loot, inventory, combat, or non-SkillEditor UI.

## Decisions

### Keep Adjustment as Draft-Only Until Existing Save

The direct adjust flow SHALL update the same draft object used by numeric inputs. Confirmation returns to the editor with updated draft values, and persistence still requires the existing "保存技能包" action.

Alternative considered: make confirm immediately save `skill.yaml`. That would make the scene tool faster but would bypass the editor's visible save step and make cancel/validation behavior harder to reason about.

### Hide, Do Not Unmount, the Editor Shell

The adjustment mode SHALL keep `SkillEditorPanel` mounted and hide the full shell visually. The component owns unsaved draft state; unmounting or closing it would risk losing the draft.

Alternative considered: close the editor and reopen after adjustment. That would require lifting all draft state into `GameApp` or backend state, increasing scope.

### Use Existing Projection Math

The drag handle SHALL use the battle scene projection and camera transform already used by runtime guide overlays. Pointer coordinates should be converted from viewport space back into terrain-local projected screen space and then world coordinates.

Alternative considered: approximate offsets from raw mouse deltas. That would drift when camera zoom, projection bounds, or terrain transform changes.

### Use Generic Projectile for Fan Spread

The adjustment flow SHALL be enabled for the generic `projectile` template. `active_ice_shards` should use `projectile` with `projectile_count`, `spread_angle_deg`, and `angle_step` instead of relying on a separate `fan_projectile` behavior template.

Alternative considered: add `spawn_offset` to `fan_projectile`. That would preserve the old split but would keep growing a redundant template for behavior that the generic projectile params can already express.

## Risks / Trade-offs

- Pointer-to-world conversion can be wrong if it ignores the battle camera transform -> Use the same constants and inverse transform path as the visible terrain.
- Adjustment could accidentally persist UI-only state -> Store only the resulting `spawn_offset` in the draft; keep mode/drag state in React UI state.
- Users may expect confirm to write the file -> Use Chinese copy that distinguishes "确认位置" from "保存技能包".
- Dirty worktree already contains unrelated changes -> Implementation should touch only the scoped SkillEditor/WebApp files and avoid reverting unrelated files.
