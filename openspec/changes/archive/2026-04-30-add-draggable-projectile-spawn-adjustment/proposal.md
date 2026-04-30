## Why

Projectile spawn offsets are currently edited through numeric inputs, while the useful feedback is visible in the battle preview scene. This makes tuning the launch point slow because the editor must repeatedly type values, inspect the scene, and adjust again.

## What Changes

- Add a SkillEditor "direct adjust" flow for projectile launch position.
- Allow the editor panel to temporarily hide while the user drags the projectile launch point in the scene.
- Show a scene-level draggable launch-point handle and minimal confirm/cancel controls during adjustment.
- Convert the dragged scene position back into `behavior.params.spawn_offset` for the current draft.
- Keep the adjustment as draft-only until the existing "save skill package" flow is used.
- Preserve existing validation, behavior-template whitelists, and Chinese UI requirements.
- Do not change projectile runtime trajectory, damage, target selection, or SkillEvent semantics.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: SkillEditor projectile launch-position editing gains a scene drag adjustment flow that updates the editable draft spawn offset without bypassing existing save validation.

## Impact

- Affected frontend files:
  - `webapp/App.tsx`
  - `webapp/styles.css`
  - `webapp/smoke-test.mjs`
- Possible test files:
  - `tests/test_skill_editor.py` only if backend/editor metadata needs a test assertion.
- No expected schema, runtime, combat, loot, inventory, gem board, or skill damage logic changes.
- No new dependencies.
