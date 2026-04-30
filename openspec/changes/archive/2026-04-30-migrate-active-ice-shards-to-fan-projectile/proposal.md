## Why

`active_fire_bolt` has completed the first Skill Package vertical slice, including SkillEditor, Skill Test Arena, SkillEvent timeline, and AI self-test report coverage. The next safest migration target is `active_ice_shards` because it is already a cold projectile skill in the old `skill_templates.toml` path, but its current behavior still reads like a near single-target projectile instead of the player-facing fantasy of scattered ice shards.

Choosing ice shards second validates that the new skill system can extend from a straight `projectile` template to a constrained `fan_projectile` template without opening the door to arbitrary scripts, node graphs, expression DSLs, or frontend behavior guessing. This is a low-risk expansion because it reuses the existing projectile concepts of spawn, travel, collision, hit, damage, VFX, floating text, and modifier-driven runtime params, while only adding deterministic multi-projectile fan geometry.

## What Changes

- Migrate only `active_ice_shards` / `冰棱散射` from the old centralized skill template into a Skill Package at the future path `configs/skills/active/active_ice_shards/skill.yaml`.
- Add the `fan_projectile` behavior template contract at the future path `configs/skills/behavior_templates/fan_projectile.yaml`.
- Define `fan_projectile` as a whitelisted behavior template with explicit declared parameters for projectile count, speed, size, fan spread, collision, spawn pattern, hit policy, and per-projectile damage scale.
- Extend SkillEditor requirements so a `fan_projectile` sub-projectile module exposes all editable fields with schema and template whitelist validation before the skill is considered migrated.
- Extend SkillRuntime requirements so ice shards generate real multi-projectile SkillEvents: `cast_start`, multiple `projectile_spawn`, `projectile_hit`, `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when applicable.
- Extend Skill Test Arena requirements so ice shards can be validated in a single dummy regression, three-target horizontal row, and dense small monster scenarios.
- Extend SkillEvent timeline and AI self-test report requirements so the migration can prove the actual result matches: "自动向最近敌人方向射出多枚冰霜冰棱，冰棱以扇形展开飞行，命中后造成冰霜伤害，并显示冰霜命中特效与伤害浮字。"
- Keep the other six non-migrated active skills on their existing behavior; this change does not migrate `active_lightning_chain`, `active_frost_nova`, `active_puncture`, `active_penetrating_shot`, `active_lava_orb`, or `active_fungal_petards`.
- Do not modify the completed `active_fire_bolt` capability except where shared tests or acceptance criteria need to ensure it remains a working template.
- Do not create runtime code, WebApp code, or `configs/skills/active/active_ice_shards/skill.yaml` during this propose-only change.
- Do not introduce a node editor, script DSL, complex expression interpreter, static fake events, frontend-guessed skill behavior, production drop changes, inventory changes, or gem board changes.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `v1-minimal-sudoku-gem-loop`: Adds requirements for migrating `active_ice_shards` to a Skill Package, defining `fan_projectile`, exposing its SkillEditor fields, validating real fan-projectile SkillEvents in Skill Test Arena, and generating an AI self-test report from real test results.

## Impact

- Future configuration scope: `configs/skills/active/active_ice_shards/skill.yaml`, `configs/skills/behavior_templates/fan_projectile.yaml`, and related schema/template validation.
- Future runtime scope: Skill Package loading, FinalSkillInstance parameter aggregation, SkillRuntime `fan_projectile` event generation, damage timing, and collision/hit rules.
- Future WebApp scope: SkillEditor field modules, Skill Test Arena scenarios, SkillEvent timeline rendering, projectile presentation, hit VFX, floating text, and AI self-test report generation.
- Explicitly out of scope for this change proposal: runtime implementation, WebApp implementation, creating the actual ice shards `skill.yaml`, migrating other active skills, modifying production loot/inventory/board behavior, and adding any scripting or node-graph systems.
