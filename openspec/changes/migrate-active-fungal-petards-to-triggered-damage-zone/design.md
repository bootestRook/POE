## Context

The current Skill Package framework already has migrated active skill packages for `active_fire_bolt`, `active_ice_shards`, `active_penetrating_shot`, `active_frost_nova`, `active_puncture`, and `active_lightning_chain`. The `damage_zone` behavior template exists and is used by migrated damage-zone skills. `active_fungal_petards` remains in `configs/skills/skill_templates.toml` with `behavior_type = "trap_or_mine"`, so it cannot yet be validated through the same Skill Package, SkillEditor, Skill Test Arena, SkillEvent timeline, and AI self-test report loop.

This design captures the first modular-composition skill. The skill is not a new `delayed_area` behavior. It is an ordered module chain:

```text
projectile(ballistic)
  -> projectile_impact(marker)
  -> triggered damage_zone(circle)
  -> delayed damage
  -> hit_vfx / floating_text
```

## Goals / Non-Goals

**Goals:**

- Define `active_fungal_petards` as a future Skill Package composed from reusable modules.
- Define module ids and marker / trigger links as a general mechanism, not a Fungal Petards special branch.
- Extend projectile semantics with ballistic flight parameters.
- Extend damage zone semantics so it can be triggered from a projectile impact marker and use the impact position as origin.
- Keep WebApp rendering fully driven by SkillEvents.
- Keep AI self-test reports based on real projectile impact and damage zone events.

**Non-Goals:**

- Do not write runtime code in this round.
- Do not modify WebApp in this round.
- Do not create `configs/skills/active/active_fungal_petards/skill.yaml` in this round.
- Do not migrate `active_lava_orb`.
- Do not create `delayed_area`.
- Do not create a node editor, script DSL, complex expression interpreter, static fake event system, or skill-id based frontend behavior.
- Do not modify formal drops, inventory, or gem board behavior.

## Decisions

### Decision 1: Skill Package module-chain structure

Future path:

```text
configs/skills/active/active_fungal_petards/skill.yaml
```

Suggested structure:

```yaml
modules:
  - id: fungal_projectile
    type: projectile
    params:
      trajectory: ballistic
      travel_time_ms: 520
      arc_height: 120
      target_policy: target_position
      impact_marker_id: fungal_impact

  - id: fungal_explosion_zone
    type: damage_zone
    trigger:
      trigger_marker_id: fungal_impact
      trigger_delay_ms: 420
    params:
      shape: circle
      origin_policy: trigger_position
      radius: 180
      hit_at_ms: 420
      max_targets: 999
      vfx_key: skill_event.fungal_petards.explode
```

`modules` is the ordered internal module chain for one skill. Each module has a stable `id`, a whitelisted `type`, and declared fields only. The projectile module emits the declared `impact_marker_id`. The damage zone module listens to the matching `trigger_marker_id`. This is declarative linking, not arbitrary script execution.

The schema and validators must reject undeclared fields, unresolved trigger ids, duplicate marker ids, and trigger declarations with no valid source marker. No node graph is introduced; the initial chain is an ordered list.

### Decision 2: Projectile module ballistic extension

The projectile module adds or extends these fields:

- `trajectory`: enum `linear | ballistic`
- `travel_time_ms`: positive number
- `arc_height`: non-negative number
- `target_policy`: enum `nearest_enemy | locked_target | target_position`
- `impact_marker_id`: unique marker id within the Skill Package

`trajectory = ballistic` describes presentation and event timing for the thrown petard. `travel_time_ms` controls impact timing. `arc_height` controls the visual arc. `target_policy = target_position` allows the module to lock the target area selected from nearest-enemy targeting at cast time. `impact_marker_id` becomes the source marker referenced by later modules.

Player-visible text must remain Chinese and must come from localization keys. These fields are technical config and event payload values, not player-facing English copy.

### Decision 3: Triggered damage zone extension

The damage zone module adds or extends these trigger fields:

- `trigger_marker_id`
- `trigger_delay_ms`
- `origin_policy = trigger_position`

`trigger_marker_id` must match a preceding module's `impact_marker_id`. `trigger_delay_ms` is non-negative. When `origin_policy = trigger_position`, the damage zone origin is the `projectile_impact.impact_position`. `hit_at_ms` may equal `trigger_delay_ms`; if both are present, the runtime must define whether `hit_at_ms` is relative to cast start or to trigger time and validate the relation consistently.

The system must not silently accept unmatched triggers. A damage zone with a trigger must not execute without a real source marker.

### Decision 4: SkillEvent sequence

Fungal Petards must output at least:

- `cast_start`
- `projectile_spawn`
- `projectile_impact`
- `damage_zone_prime`
- `damage_zone`
- `damage`
- `hit_vfx`
- `floating_text`
- `cooldown_update`, when present

`projectile_spawn` expresses the ballistic projectile and includes `trajectory`, `start_position`, `target_position`, `travel_time_ms`, `arc_height`, and `impact_marker_id`.

`projectile_impact` expresses landing and includes `marker_id` and `impact_position`.

`damage_zone_prime` expresses the post-landing warning and includes `trigger_marker_id`, `origin`, `delay_ms`, `radius`, and `vfx_key`.

`damage_zone` expresses the real circular explosion hit area and includes `shape = circle`, `origin`, `radius`, `hit_at_ms`, `damage_type`, and `vfx_key`.

`damage` is emitted only after the damage zone hit resolves and is the only HP-changing event.

### Decision 5: Runtime behavior

Runtime must generate a ballistic projectile from player position to the chosen target position. After `travel_time_ms`, the projectile emits `projectile_impact` with `marker_id = impact_marker_id`. The triggered damage zone listens for `trigger_marker_id`, uses `impact_position` as origin, emits `damage_zone_prime`, then emits `damage_zone` and `damage` after `trigger_delay_ms`.

The runtime must not apply damage before the explosion. No HP changes at `cast_start`, no target-point instant explosion, no static fake events, and no `active_fungal_petards` special branch in Combat Runtime are allowed. Damage type is `physical`.

### Decision 6: WebApp event-driven rendering

WebApp must consume SkillEvents only:

- Render ballistic projectile from `projectile_spawn`.
- Use `travel_time_ms` and `arc_height` to shape the projectile path.
- Render landing from `projectile_impact`.
- Render warning circle from `damage_zone_prime`.
- Render explosion range from `damage_zone`.
- Render HP changes, hit VFX, and floating text from `damage`, `hit_vfx`, and `floating_text`.

WebApp must not infer behavior from skill id, old `behavior_type`, `visual_effect`, or VFX key.

### Decision 7: SkillEditor module-chain panel

SkillEditor adds a “技能模块链” panel.

Projectile module fields:

- `trajectory`
- `travel_time_ms`
- `arc_height`
- `target_policy`
- `impact_marker_id`
- `projectile_speed`, if still retained, as read-only or mutually exclusive with `travel_time_ms`
- `projectile_width`
- `projectile_height`
- `vfx_key`

Damage zone module fields:

- `trigger_marker_id`
- `trigger_delay_ms`
- `shape = circle`
- `origin_policy = trigger_position`
- `radius`
- `hit_at_ms`
- `max_targets`
- `damage_type`
- `vfx_key`

The panel shows the link:

```text
projectile.impact_marker_id -> damage_zone.trigger_marker_id
```

`impact_marker_id` should be selected from controlled input or generated options. `trigger_marker_id` should prefer a dropdown of existing markers. Saving must validate marker / trigger consistency. Test modifiers must not write into real `skill.yaml`, and random affix editing must not be restored.

### Decision 8: Skill Test Arena acceptance

Required scenes:

- Single dummy.
- Dense small monsters.
- Three targets in a horizontal row.

Acceptance checks include `projectile_spawn`, `projectile_impact`, correct impact position, `damage_zone_prime`, `damage_zone`, no HP loss before explosion, HP loss after `damage`, in-radius hits, out-of-radius misses, timing changes from `travel_time_ms`, arc-height changes from `arc_height`, explosion timing changes from `trigger_delay_ms`, range changes from `radius`, and Modifier Stack effects on final damage or range parameters.

### Decision 9: AI self-test report

Expected player-side description:

```text
自动向最近敌人位置投掷一枚真菌爆弹，爆弹以抛物线飞行到目标区域，落地后出现短暂预警，随后在落点产生圆形孢子爆炸，对范围内敌人造成物理伤害，并显示爆炸特效与伤害浮字。
```

The report must check real results for `projectile_spawn`, ballistic trajectory, `projectile_impact`, marker id, `damage_zone_prime`, trigger marker id, `damage_zone`, circle shape, origin equality with impact position, damage timing no earlier than impact plus trigger delay, no pre-explosion HP loss, post-damage HP loss, `damage_type = physical`, radius mutation effects, `travel_time_ms` mutation effects, `arc_height` mutation effects, `trigger_delay_ms` mutation effects, and Chinese conclusion / inconsistency / suggested fix output.

## Risks / Trade-offs

- [Risk] Module chains could become a hidden scripting system. -> Mitigation: allow only ordered modules, declared module ids, whitelisted module types, declared fields, and marker / trigger references.
- [Risk] `hit_at_ms` and `trigger_delay_ms` can be interpreted inconsistently. -> Mitigation: validators and design docs must define their relation before implementation.
- [Risk] WebApp may be tempted to special-case Fungal Petards for visuals. -> Mitigation: require rendering from `projectile_spawn`, `projectile_impact`, `damage_zone_prime`, and `damage_zone` payloads only.
- [Risk] AI reports may become static explanations. -> Mitigation: report checks must be based on real Skill Test Arena event timelines and HP deltas.

## Migration Plan

1. Confirm current module-chain prerequisites and old Fungal Petards path.
2. Extend schema and behavior-template validation for modules, markers, projectile ballistic fields, and triggered damage zone fields.
3. Create the future Fungal Petards Skill Package in the apply phase.
4. Implement runtime module-chain execution without Combat Runtime skill-id branches.
5. Extend SkillEditor, WebApp rendering, Skill Test Arena, SkillEvent timeline, AI report, and regression tests.

Rollback is limited to the apply phase: keep the old `skill_templates.toml` entry until the new package passes validation, tests, and report acceptance.

## Open Questions

- Should `hit_at_ms` be relative to cast start or relative to trigger time when a damage zone is triggered?
- Should `projectile_speed` remain as read-only derived output when `travel_time_ms` is authoritative?
- Should marker ids be globally unique per skill package or scoped to one cast instance with runtime event identity added by SkillRuntime?

