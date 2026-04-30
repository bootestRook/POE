## Context

`refactor-skill-system-runtime-and-skill-package` is archived, and the current migrated active skill surface is centered on `active_fire_bolt`: one package under `configs/skills/active/active_fire_bolt/skill.yaml`, a `projectile` behavior template, SkillEditor editing support, Skill Test Arena validation, SkillEvent timeline viewing, and AI self-test report generation.

`active_ice_shards` still exists in the old `configs/skills/skill_templates.toml` path as `skill_ice_shards`, with `damage_type = "cold"`, `behavior_type = "projectile"`, and projectile-related scaling. That makes it a good second migration because it is close enough to reuse the fire bolt vertical slice, but different enough to prove that the behavior template system supports a real fan-shaped multi-projectile skill rather than a visual-only reskin.

The player-facing target after migration is: "自动向最近敌人方向射出多枚冰霜冰棱，冰棱以扇形展开飞行，命中后造成冰霜伤害，并显示冰霜命中特效与伤害浮字。"

## Goals / Non-Goals

**Goals:**
- Specify `active_ice_shards` as the second active Skill Package migration.
- Specify a deterministic, whitelisted `fan_projectile` behavior template.
- Require real multi-projectile fan SkillEvents rather than release-time damage or static fake events.
- Require SkillEditor support for every `fan_projectile` field before the skill is considered migrated.
- Require Skill Test Arena, SkillEvent timeline, and AI self-test report coverage for the actual fan behavior.
- Preserve Chinese player-visible text through localization keys and report text.

**Non-Goals:**
- Do not migrate the other six active skills in this change.
- Do not implement runtime code, WebApp code, or the real `active_ice_shards/skill.yaml` during this propose-only round.
- Do not change the completed `active_fire_bolt` behavior except to keep it as a regression template.
- Do not modify formal loot drops, inventory/storage, or the sudoku gem board.
- Do not add a node editor, arbitrary scripts, script DSL, complex expression interpreter, or frontend-side behavior guessing.
- Do not use static fake events to satisfy SkillEvent, arena, or AI report requirements.

## Decisions

### Decision: migrate ice shards second

`active_ice_shards` is the best second migrated active skill because the old content already classifies it as a cold projectile skill, the localization and VFX assets already exist, and its current problem is concrete: the base behavior is still effectively a normal projectile shape. Migrating it next validates the Skill Package system against a nearby but meaningfully different behavior without taking on chain, nova, melee, orbit, or delayed-area complexity.

Alternative considered: migrate `active_lightning_chain` next. That would test a new behavior family, but it adds target chaining rules and would be a larger runtime jump than needed immediately after `projectile`.

### Decision: `fan_projectile` is a low-risk extension of `projectile`

`fan_projectile` SHALL reuse the known projectile event vocabulary: `projectile_spawn`, `projectile_hit`, `damage`, `hit_vfx`, and `floating_text`. Its new responsibility is deterministic fan geometry: compute a base direction toward the selected target, derive one independent direction per projectile, emit one spawn event per projectile, and resolve hits from each projectile's flight/collision rule.

Alternative considered: reuse `projectile` with `spread_angle_deg`. That keeps the template count small, but it does not make the migration contract explicit enough for SkillEditor, arena acceptance, and AI report checks that require fan-specific fields like `angle_step`, `spawn_pattern`, and `per_projectile_damage_scale`.

### Decision: Skill Package structure for `active_ice_shards`

The migrated package SHALL live at the future path:

```text
configs/skills/active/active_ice_shards/skill.yaml
```

The package SHALL contain at least:

- `id`
- `version`
- `display.name_key`
- `display.description_key`
- `classification.tags`
- `classification.damage_type = cold`
- `classification.damage_form`
- `cast.mode`
- `cast.target_selector`
- `cast.search_range`
- `cast.cooldown_ms`
- `cast.windup_ms`
- `cast.recovery_ms`
- `behavior.template = fan_projectile`
- `behavior.params`
- `hit.base_damage`
- `hit.can_crit`
- `hit.can_apply_status`
- `scaling.additive_stats`
- `scaling.final_stats`
- `scaling.runtime_params`
- `presentation.vfx`
- `presentation.sfx`
- `presentation.floating_text`
- `presentation.screen_feedback`
- `preview.show_fields`

The package SHALL use Chinese localization keys for player-visible name, description, floating text, reason, and feedback. It SHALL NOT embed English player-visible text.

### Decision: `fan_projectile` behavior template schema

The new behavior template SHALL live at the future path:

```text
configs/skills/behavior_templates/fan_projectile.yaml
```

The template SHALL declare an allowed parameter whitelist that includes at least:

- `projectile_count`
- `projectile_speed`
- `projectile_width`
- `projectile_height`
- `spread_angle`
- `angle_step`
- `max_distance`
- `hit_policy`
- `collision_radius`
- `spawn_pattern`
- `per_projectile_damage_scale`

Validation rules:

- `projectile_count` SHALL be a positive integer.
- `spread_angle` SHALL have a bounded numeric range suitable for a fan and MUST reject invalid angles.
- `angle_step` SHALL have a bounded numeric range and MUST reject invalid angles.
- `projectile_speed`, `projectile_width`, `projectile_height`, `max_distance`, and `collision_radius` SHALL be legal positive numbers.
- `hit_policy` SHALL be an enum, initially constrained to values such as `first_hit`, `pierce`, or other explicitly declared policies.
- `spawn_pattern` SHALL be an enum, initially constrained to values such as `centered_fan`, `edge_to_edge`, or other explicitly declared patterns.
- `per_projectile_damage_scale` SHALL be numeric with a declared valid range.
- Schema/template validation SHALL reject params not declared by `fan_projectile`.
- The template SHALL NOT permit scripts, function calls, expression strings, arbitrary DSL fields, or complex expression interpreters.

### Decision: SkillEditor `fan_projectile` field module

SkillEditor SHALL add a `fan_projectile` projectile module and expose all fields before migration is complete:

- `projectile_count`
- `projectile_speed`
- `projectile_width`
- `projectile_height`
- `spread_angle`
- `angle_step`
- `max_distance`
- `hit_policy`
- `collision_radius`
- `spawn_pattern`
- `per_projectile_damage_scale`
- read-only flight time or per-projectile flight time summary

The editor SHALL use schema and behavior-template whitelist validation. It SHALL reject unknown template fields and invalid values before save. Enum fields SHALL use enum controls, numeric fields SHALL use bounded numeric validation, and the read-only flight-time summary SHALL derive from actual speed/distance params rather than being saved as behavior data.

### Decision: SkillRuntime `fan_projectile` behavior

`fan_projectile` SHALL generate projectiles from the player position or declared cast source position. It SHALL select the target direction from the nearest enemy or configured target selector, then expand multiple projectile directions across the fan.

Runtime event order SHALL represent actual behavior:

```text
cast_start
projectile_spawn x projectile_count
projectile_hit for actual collisions / hit rules
damage after hit timing
hit_vfx and floating_text after or with damage
cooldown_update when applicable
```

Each projectile SHALL have an independent direction and independent `projectile_spawn` event. Hit resolution SHALL use real projectile travel and collision/hit rules. Damage SHALL be applied by `damage` events, not by cast start or release-time shortcuts. Presentation events SHALL be derived from real hit/damage outcomes, not static fake events.

### Decision: Skill Test Arena acceptance coverage

The arena SHALL support `active_ice_shards` in at least these scenarios:

- 三目标横排
- 密集小怪
- 单体木桩 as a baseline damage timing regression

Acceptance checks:

- Multiple ice shard projectile spawns are generated.
- Fan angles are visible in event data and presentation.
- Hit targets come from real collision or hit policy resolution.
- No life is reduced while projectiles are in flight.
- Life is reduced only after hit/damage timing.
- Changing `projectile_count` changes the number of projectiles/events.
- Changing `spread_angle` changes projectile direction distribution.
- Changing `projectile_speed` changes flight time.
- The Modifier test stack can affect final damage or projectile parameters.

### Decision: SkillEvent timeline acceptance

The timeline SHALL display the real event sequence for ice shards and include:

- `cast_start`
- multiple `projectile_spawn`
- `projectile_hit`
- `damage`
- `hit_vfx`
- `floating_text`
- `cooldown_update` when present

Each event display SHALL include:

- `timestamp_ms`
- `delay_ms`
- `duration_ms`
- `source_entity`
- `target_entity`
- `amount`
- `damage_type`
- `vfx_key`
- `reason_key`
- `payload`

### Decision: AI self-test report acceptance

The report SHALL evaluate actual Skill Test Arena results against this expected description:

```text
自动向最近敌人方向射出多枚冰霜冰棱，冰棱以扇形展开飞行，命中后造成冰霜伤害，并显示冰霜命中特效与伤害浮字。
```

The report SHALL check:

- Whether multiple `projectile_spawn` events are generated.
- Whether projectile directions form a fan.
- Whether `projectile_hit` exists.
- Whether `damage` exists.
- Whether `hit_vfx` exists.
- Whether `floating_text` exists.
- Whether `damage` is not earlier than `projectile_spawn`.
- Whether no life is reduced during projectile flight.
- Whether `damage_type` is `cold`.
- Whether changing `projectile_count` changes event count.
- Whether changing `spread_angle` changes projectile directions.
- Whether the conclusion is `通过`, `部分通过`, or `不通过`.
- Whether Chinese inconsistencies and suggested fixes are output.

## Risks / Trade-offs

- [Risk] `fan_projectile` could accidentally become a generic scripting hook. → Mitigation: keep it as a strict behavior template with an explicit field whitelist, enum constraints, and no script/expression fields.
- [Risk] The WebApp could visually fan out projectiles while runtime still resolves single-target damage. → Mitigation: require SkillEvent and AI report checks to prove multiple spawn, hit, and damage events come from real runtime output.
- [Risk] Damage timing could regress to release-time deduction. → Mitigation: require single dummy timing regression and timeline checks that damage occurs after projectile travel/hit timing.
- [Risk] Field naming could drift from existing `projectile` params. → Mitigation: keep common names aligned where practical, and explicitly document `spread_angle` and `angle_step` for the fan template.
- [Risk] Modifier tests could only affect display values. → Mitigation: require Modifier test stack effects to appear in final damage or projectile params used by actual arena events.

## Migration Plan

1. Confirm `active_fire_bolt` remains the working Skill Package template and that `configs/skills/active/` still contains only `active_fire_bolt/skill.yaml`.
2. Add `fan_projectile` schema/template definitions without wiring any skill to it.
3. Create `active_ice_shards` Skill Package using `behavior.template = fan_projectile`.
4. Add SkillEditor `fan_projectile` field module and validation.
5. Implement SkillRuntime `fan_projectile` event generation and damage timing.
6. Teach WebApp presentation to consume `fan_projectile` SkillEvents without guessing behavior.
7. Add Skill Test Arena scenarios and AI self-test report checks for ice shards.
8. Run strict OpenSpec validation, backend tests, WebApp build/tests, and targeted arena/report verification.

Rollback strategy: if `fan_projectile` implementation is incomplete, keep `active_ice_shards` on the old `skill_templates.toml` path and do not expose it as an editable migrated Skill Package until all editor, runtime, arena, timeline, and report acceptance criteria pass.

## Open Questions

- Exact enum values for `hit_policy` and `spawn_pattern` should be finalized during apply based on existing validation helpers.
- Exact numeric bounds for `spread_angle`, `angle_step`, and `per_projectile_damage_scale` should be chosen to match current UI validation patterns and gameplay tuning.
- Whether `angle_step` is explicitly authored or derived when absent should be resolved in schema design; either way, saved params must remain whitelisted and deterministic.
