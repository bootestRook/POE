## Context

The current skill migration framework already supports schema-backed Skill Packages, whitelisted behavior templates, SkillEditor modules, Skill Test Arena runs, SkillEvent timelines, WebApp event consumption, and Chinese AI self-test reports.

`active_frost_nova` currently represents an area damage skill through `player_nova`. `active_puncture` has just been migrated as a physical short-range skill, but the desired direction has changed: the player-facing skill should become `地刺`, firing a line of ground spikes toward the locked or nearest enemy. Both skills are better described by the same semantic primitive: a damage settlement area / hit zone.

The change should consolidate this concept without turning skill behavior into scripts. Designers should choose the settlement zone shape and edit only schema-declared fields. Runtime should emit real SkillEvents and resolve hits from event-backed geometry.

## Goals / Non-Goals

**Goals:**

- Introduce a declarative `damage_zone` behavior template.
- Represent `active_frost_nova` as `damage_zone` with `shape = circle`.
- Rework `active_puncture` visible behavior and text into `地刺`, represented as `damage_zone` with `shape = rectangle`.
- Merge SkillEditor area-skill controls into one damage zone module.
- Let the editor conditionally show fields by zone shape:
  - rectangle: length, width, angle;
  - circle: radius, angle fixed or shown read-only as 360 degrees.
- Resolve runtime hits through one damage zone resolver for circle and rectangle shapes.
- Emit `damage_zone`, `damage`, `hit_vfx`, and `floating_text` SkillEvents that drive WebApp rendering, timeline display, arena validation, and AI reports.
- Keep all player-visible text Chinese.

**Non-Goals:**

- Do not migrate `active_lightning_chain`, `active_lava_orb`, or `active_fungal_petards`.
- Do not restore random affix UI or random affix generation.
- Do not create a node editor, scripting DSL, expression interpreter, or arbitrary formula system.
- Do not let WebApp infer behavior from skill id, legacy template id, behavior type, or VFX key.
- Do not keep `active_puncture` as a melee arc slash after this change.
- Do not keep separate editor modules for frost nova and ground spike once `damage_zone` is implemented.

## Decisions

### 1. Use `damage_zone` as the shared behavior template

`damage_zone` is the canonical template for non-projectile damage settlement areas. It describes where damage will be checked, when damage is applied, and how the hit zone is visualized.

The first version supports:

- `shape = circle`
- `shape = rectangle`

Rejected alternative: keep `player_nova` and `melee_arc` as separate public templates. That preserves existing behavior names, but duplicates timing, target cap, hit testing, editor validation, report checks, and WebApp rendering.

### 2. Keep skill identity, change player-facing puncture semantics

The internal id may remain `active_puncture` for compatibility with inventory and saved references, but player-visible Chinese text should become `地刺`. The behavior should be a ground spike line, not a melee slash.

Expected player-facing behavior:

`自动朝锁定敌人或最近敌人方向发出一列地刺，命中矩形范围内敌人后造成物理伤害，并显示地刺命中特效与伤害浮字。`

Rejected alternative: create a new `active_ground_spike` skill id immediately. That is cleaner semantically, but it widens migration scope into inventory/drop compatibility and is not necessary for this design pass.

### 3. `damage_zone` SkillEvent is the shared event surface

Runtime should emit:

- `cast_start`
- `damage_zone`
- `damage`
- `hit_vfx`
- `floating_text`
- `cooldown_update` when present

`damage_zone.payload` must include enough real geometry for consumers:

- common:
  - `zone_id`
  - `skill_id`
  - `shape`
  - `origin`
  - `origin_world_position`
  - `facing_policy`
  - `facing_direction`
  - `facing_angle_deg`
  - `angle_offset_deg`
  - `hit_at_ms`
  - `max_targets`
  - `damage_type`
  - `vfx_key`
  - `payload`
- circle:
  - `radius`
  - `angle_deg = 360`
- rectangle:
  - `length`
  - `width`
  - `angle_deg`

Rejected alternative: emit separate `area_spawn` and `ground_spike` events forever. That keeps very specific names, but the timeline and report would still need to understand duplicated geometry systems.

### 4. Shape-specific hit testing lives in one resolver

Runtime should use one `damage_zone` resolver:

- circle: target is eligible when distance from origin is within `radius`;
- rectangle: project target position into the local forward/right axes and require:
  - forward distance between `0` and `length`;
  - lateral distance within `width / 2`;
  - direction derived from locked target or nearest target plus `angle_offset_deg`.

Both shapes share:

- `max_targets`;
- `hit_at_ms`;
- no HP reduction before hit timing;
- damage applied only through `damage` events;
- `hit_vfx` and `floating_text` after or with damage.

Rejected alternative: encode rectangle hit logic in WebApp. WebApp must render real SkillEvents; it must not own combat geometry.

### 5. SkillEditor merges area controls into a damage zone module

SkillEditor should show a single "伤害结算区域" module for `damage_zone`. It should not show separate "范围新星" and "近战扇形" modules for frost nova and ground spike.

Common editable fields:

- `shape`
- `origin_policy`
- `facing_policy`
- `hit_at_ms`
- `max_targets`
- `status_chance_scale`
- `zone_vfx_key`

Circle fields:

- `radius`
- `angle_deg` hidden or read-only as 360

Rectangle fields:

- `length`
- `width`
- `angle_deg` or `angle_offset_deg`

Validation must use schema and behavior-template whitelist. Unknown params and frontend-only fake params must be rejected.

### 6. WebApp renders from `damage_zone`

WebApp must render:

- a circular zone for `shape = circle`;
- a rectangular ground spike line for `shape = rectangle`.

Rendering must use `damage_zone` payload geometry. `damage`, `hit_vfx`, and `floating_text` must continue to come from their own events. WebApp must not infer ground spike from `active_puncture`, `skill_puncture`, or VFX names.

### 7. Tests and AI reports treat shape as the acceptance axis

Skill Test Arena and AI reports should check the shared `damage_zone` contract first, then shape-specific expectations:

- frost nova: circle radius controls hit coverage;
- ground spike: rectangle length/width/angle controls hit coverage.

This keeps tests focused on behavior semantics instead of implementation names.

## Risks / Trade-offs

- Existing `player_nova` and `melee_arc` tests may become stale -> Update tests to assert `damage_zone` and shape-specific geometry instead of old event names.
- Renaming player-facing puncture to ground spike can confuse saved ids -> Keep internal `active_puncture` id for compatibility and change Chinese display text/description only.
- Rectangle hit testing can be off by orientation or coordinate projection -> Add tests for length boundary, width boundary, and angle rotation.
- WebApp could accidentally special-case skill ids -> Smoke tests and code review should require `damage_zone` event-driven rendering.
- A generic template can become too broad -> First version only supports declared circle and rectangle schemas, no scripts, no expression DSL, and no arbitrary shapes.

## Migration Plan

1. Add `damage_zone` schema and behavior template with circle and rectangle field constraints.
2. Convert `active_frost_nova` Skill Package to `behavior.template = damage_zone`, `shape = circle`.
3. Convert `active_puncture` Skill Package player-visible text and behavior to `地刺`, `behavior.template = damage_zone`, `shape = rectangle`.
4. Replace frost nova / puncture-specific SkillEditor modules with one damage zone module.
5. Implement shared runtime damage zone hit testing and SkillEvent emission.
6. Update WebApp to consume and render `damage_zone` events for circle and rectangle.
7. Update Skill Test Arena scenarios for circle and rectangle validation.
8. Update SkillEvent timeline and AI self-test reports for shape-specific checks.
9. Run config validation, Python tests, OpenSpec strict validation, npm build/test, and AI reports for both frost nova and ground spike.

Rollback strategy: keep existing Skill Package ids and localization keys. If the shared resolver fails, revert the packages to their previous behavior templates and retain the old runtime paths until the resolver is corrected.

## Open Questions

- Should the config field be named `angle_deg` or `angle_offset_deg` for rectangle zones? Recommended: `angle_offset_deg`, because runtime facing direction is derived from target selection.
- Should `active_puncture` display name become exactly `地刺`, or `穿刺地刺` for continuity? Recommended: `地刺`.
- Should `area_spawn` remain as a compatibility alias for old timelines during transition? Recommended: no new alias unless tests or tooling require it.
