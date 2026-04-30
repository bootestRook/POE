## 1. State and Scope

- [x] 1.1 Inspect current SkillEditor draft ownership, preview guide data flow, and `spawn_offset` edit constraints.
- [x] 1.2 Add UI-only adjustment state for active/inactive mode, pending drag value, and pre-adjustment snapshot.
- [x] 1.3 Ensure adjustment is only enabled for editable packages whose behavior template can persist `spawn_offset`.

## 2. Editor Entry and Mode Flow

- [x] 2.1 Add a Chinese "直接调整" action to the "发射位置" section.
- [x] 2.2 Enter adjustment mode without unmounting the SkillEditor draft.
- [x] 2.3 Hide the full editor shell while adjustment mode is active.
- [x] 2.4 Add minimal Chinese confirm/cancel controls for adjustment mode.
- [x] 2.5 On confirm, return to the full editor with the adjusted draft value.
- [x] 2.6 On cancel, restore the snapshot values from before adjustment mode.

## 3. Scene Drag Adjustment

- [x] 3.1 Add a battle-scene launch-point drag handle that reuses the current projectile guide spawn position.
- [x] 3.2 Convert pointer position from viewport coordinates into terrain-local projected coordinates using the current battle camera transform.
- [x] 3.3 Convert terrain-local projected coordinates back into world coordinates.
- [x] 3.4 Convert dragged world coordinates into `spawn_offset` relative to the current player/cast source.
- [x] 3.5 Update the current SkillEditor draft during drag so existing guide overlays move immediately.

## 4. Styling and UX

- [x] 4.1 Style the drag handle so it is visible above the battle scene and clearly associated with the launch point.
- [x] 4.2 Style the adjustment toolbar without obscuring the dragged launch point.
- [x] 4.3 Keep all new labels, hints, status text, and button text in Chinese.
- [x] 4.4 Ensure adjustment UI state is never included in the save payload.

## 5. Verification

- [x] 5.1 Add or update WebApp smoke coverage for opening the editor and entering direct adjustment mode.
- [x] 5.2 Verify cancel restores the previous `spawn_offset` draft values.
- [x] 5.3 Verify confirm updates the editor fields and existing save validation still controls persistence.
- [x] 5.4 Run the WebApp build.
- [x] 5.5 Run relevant existing SkillEditor/runtime tests if touched by implementation.
- [x] 5.6 Run `openspec validate add-draggable-projectile-spawn-adjustment --strict`.

## 6. Ice Shards Projectile Unification

- [x] 6.1 Migrate `active_ice_shards` from `fan_projectile` to generic `projectile`.
- [x] 6.2 Represent the fan spread through `projectile_count`, `spread_angle_deg`, and `angle_step`.
- [x] 6.3 Do not add `spawn_offset` support to the redundant `fan_projectile` template.
- [x] 6.4 Update tests and reports to expect generic projectile spread for ice shards.
