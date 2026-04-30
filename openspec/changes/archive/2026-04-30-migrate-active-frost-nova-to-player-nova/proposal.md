## Why

`active_frost_nova` / `冰霜新星` is the next low-risk migration because it exercises the first player-centered area behavior after projectile, fan projectile, and pierce projectile skills have proved the Skill Package, SkillEditor, Skill Test Arena, SkillEvent timeline, and AI self-test report pipeline. The current old template only says `behavior_type = area`, which is too vague to guarantee a player-centered expanding nova rather than a target-point explosion.

This change makes the player-facing behavior explicit: "自动以玩家自身为中心释放一圈向外扩散的冰霜新星，命中范围内敌人后造成冰霜伤害，并显示冰霜范围爆发特效与伤害浮字。"

## What Changes

- Migrate only `active_frost_nova` from the old `skill_templates.toml` path to a future Skill Package at `configs/skills/active/active_frost_nova/skill.yaml`.
- Introduce a whitelisted `player_nova` behavior template for player-centered expanding area skills.
- Require `player_nova` to use the player position as the area center; it must not be implemented as a target-point AoE with frost visuals.
- Require SkillRuntime to emit real SkillEvents for `cast_start`, `area_spawn`, `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when present.
- Require damage to occur through `damage` events at or after `hit_at_ms`; release-time instant HP removal is forbidden.
- Extend SkillEditor with a `player_nova` area module exposing every declared field and read-only range/timing summaries.
- Extend Skill Test Arena and AI self-test report acceptance for dense monsters, single dummy, and three-target row boundary verification.
- Keep `active_fire_bolt`, `active_ice_shards`, and `active_penetrating_shot` behavior intact.
- Do not migrate `active_lightning_chain`, `active_puncture`, `active_lava_orb`, `active_fungal_petards`, or any other active skill in this change.
- Do not create a node editor, script DSL, complex expression interpreter, static fake events, or English player-visible copy.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `v1-minimal-sudoku-gem-loop`: Add requirements for the `active_frost_nova` Skill Package migration, `player_nova` behavior template, SkillEditor field support, SkillEvent output, Skill Test Arena acceptance, and AI self-test report acceptance.

## Impact

- Future config scope: `configs/skills/active/active_frost_nova/skill.yaml`, `configs/skills/behavior_templates/player_nova.yaml`, skill schema, and Chinese localization keys.
- Future runtime scope: SkillRuntime behavior template dispatch, area target resolution, SkillEvent generation, and damage timing.
- Future editor/testing/report scope: SkillEditor module fields and validation, Skill Test Arena scenarios, SkillEvent timeline display, AI self-test report checks.
- Future WebApp scope: consume `player_nova` SkillEvents without guessing behavior from skill id, `behavior_type`, or visual effect.
- Current preconditions: `migrate-active-ice-shards-to-fan-projectile` is archived; `active_fire_bolt`, `active_ice_shards`, and `active_penetrating_shot` Skill Packages exist; `active_frost_nova/skill.yaml` does not exist and `active_frost_nova` still references `skill_frost_nova` in old active gem/template data. `active_penetrating_shot` is migrated in the current codebase, but no standalone `migrate-active-penetrating-shot...` OpenSpec change was found in active or archive lists.
