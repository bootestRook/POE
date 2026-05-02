## Why

`active_fungal_petards / 真菌爆弹` is still on the old `skill_templates.toml` path and can collapse into target-point instant damage. It should prove the next step of the completed Skill Package framework: one active skill assembled from reusable modules rather than a new one-off behavior template.

Fungal Petards is not a `delayed_area` template because its player-facing behavior has two distinct runtime phases: a ballistic projectile lands at a target position, then that landing marker triggers a delayed circular damage zone. Modeling that as `projectile + damage_zone` keeps trajectory, impact, warning, explosion, damage, VFX, floating text, SkillEditor fields, Skill Test Arena checks, and AI report checks event-driven and reusable for later skills.

## What Changes

- Plan migration of only `active_fungal_petards / 真菌爆弹` from `configs/skills/skill_templates.toml` to a future Skill Package at `configs/skills/active/active_fungal_petards/skill.yaml`.
- Introduce the Skill Package module-chain concept with ordered `modules`, module ids, and declared module links.
- Define a generic marker / trigger mechanism where `projectile.impact_marker_id` emits a marker at `projectile_impact`, and `damage_zone.trigger_marker_id` listens to that marker.
- Extend the `projectile` module capability to support `trajectory = ballistic`, `travel_time_ms`, `arc_height`, `target_policy`, and `impact_marker_id`.
- Extend the `damage_zone` module capability to support `trigger_marker_id`, `trigger_delay_ms`, and `origin_policy = trigger_position`.
- Require the migrated player-side effect: “自动向最近敌人位置投掷一枚真菌爆弹，爆弹以抛物线飞行到目标区域，落地后出现短暂预警，随后在落点产生圆形孢子爆炸，对范围内敌人造成物理伤害，并显示爆炸特效与伤害浮字。”
- Require real SkillEvents for `cast_start`, `projectile_spawn`, `projectile_impact`, `damage_zone_prime`, `damage_zone`, `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when present.
- Require SkillEditor to add a “技能模块链” panel that exposes the projectile module, damage zone module, and `projectile.impact_marker_id -> damage_zone.trigger_marker_id` link.
- Require Skill Test Arena acceptance for single dummy, dense small monsters, and three-target horizontal row scenarios.
- Require the AI self-test report to validate real `projectile_impact` and `damage_zone` events rather than static descriptions.
- Do not migrate `active_lava_orb / 熔岩球` in this change.
- Do not create `delayed_area`, a node editor, script DSL, complex expression interpreter, static fake events, frontend behavior guessing, or English player-visible text.
- This round only creates OpenSpec Explore / Propose artifacts. It does not write runtime code, modify WebApp, or create `active_fungal_petards/skill.yaml`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: Add requirements for Skill Package module chains, marker / trigger links, ballistic projectile extension, triggered damage zone, Fungal Petards migration, SkillEditor module-chain support, WebApp event-driven rendering, Skill Test Arena acceptance, and AI report validation.

## Impact

- Future config scope: `configs/skills/schema/skill.schema.json`, `configs/skills/behavior_templates/projectile.yaml`, `configs/skills/behavior_templates/damage_zone.yaml`, future `configs/skills/active/active_fungal_petards/skill.yaml`, Chinese localization keys, and validation tools.
- Future runtime scope: SkillRuntime module-chain execution, projectile ballistic timing, marker emission, triggered damage zone scheduling, delayed damage, physical damage events, VFX events, and floating text events.
- Future editor/testing/report scope: SkillEditor module-chain panel, marker / trigger validation UI, Skill Test Arena scenarios and parameter mutations, SkillEvent timeline display, and AI self-test report checks.
- Future WebApp scope: render projectile, impact, warning, explosion, damage, hit VFX, and floating text from SkillEvent payloads only.
- Explicitly out of scope for this round: runtime code, WebApp code, `skill.yaml` creation, `active_lava_orb` migration, formal drop/inventory/gem board changes, `delayed_area`, node graph editing, script DSL, complex expression interpretation, static fake events, skill-id based frontend behavior, and English player-visible copy.

