## Context

The skill system now has a working Skill Package path for `active_fire_bolt`, `active_ice_shards`, and `active_penetrating_shot`. Those migrations established the reusable pieces this change should copy: schema-based package validation, behavior-template parameter whitelists, SkillEditor modules, Skill Test Arena scenarios, real SkillEvent timelines, and Chinese AI self-test reports.

`active_frost_nova` still comes from the old active gem plus `skill_templates.toml` path:

- `configs/gems/active_skill_gems.toml` declares `active_frost_nova` with `skill_template = "skill_frost_nova"`.
- `configs/skills/skill_templates.toml` declares `skill_frost_nova` with `behavior_type = "area"`, `damage_type = "cold"`, `base_damage = 14`, and `base_cooldown_ms = 1200`.
- `configs/skills/active/active_frost_nova/skill.yaml` does not exist yet.

The important design distinction is center ownership. Frost Nova is a player-centered nova, not a target-point explosion. The runtime, test arena, WebApp, and report must all treat the player or cast source position as the authoritative center.

## Goals / Non-Goals

**Goals:**

- Define the future `active_frost_nova` Skill Package at `configs/skills/active/active_frost_nova/skill.yaml`.
- Define the future `player_nova` behavior template at `configs/skills/behavior_templates/player_nova.yaml`.
- Make `player_nova` a low-risk area extension after projectile-family migrations: no script hooks, no DSL, no arbitrary expressions, only declared fields.
- Ensure SkillRuntime emits real `area_spawn`, `damage`, `hit_vfx`, and `floating_text` events with damage delayed until `hit_at_ms`.
- Ensure SkillEditor exposes and validates every declared `player_nova` field before the skill is considered migrated.
- Ensure Skill Test Arena and AI self-test report can validate player-centered area behavior with real event results.

**Non-Goals:**

- Do not write runtime code during Propose.
- Do not create `configs/skills/active/active_frost_nova/skill.yaml` during Propose.
- Do not implement `player_nova` during Propose.
- Do not migrate `active_lightning_chain`, `active_puncture`, `active_lava_orb`, `active_fungal_petards`, or any other active skill.
- Do not modify already migrated skills except for shared compatibility checks required during Apply.
- Do not modify formal loot, inventory, gem board, or random affix generation.
- Do not create a node editor, script DSL, or complex expression interpreter.
- Do not let the frontend guess behavior from skill id, `behavior_type`, or `visual_effect`.
- Do not use static fake SkillEvents or English player-visible copy.

## Decisions

### 1. `active_frost_nova` Skill Package structure

Future path:

`configs/skills/active/active_frost_nova/skill.yaml`

The package must include:

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
- `behavior.template = player_nova`
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

Rationale: this mirrors the existing package contract used by fire bolt, ice shards, and penetrating shot while making the nova-specific behavior explicit.

### 2. `player_nova` Behavior Template

Future path:

`configs/skills/behavior_templates/player_nova.yaml`

Allowed params must include at least:

- `radius`
- `expand_duration_ms`
- `hit_at_ms`
- `max_targets`
- `center_policy`
- `damage_falloff_by_distance`
- `ring_width`
- `status_chance_scale`

Validation rules:

- `radius` must be a positive number.
- `expand_duration_ms` must be a non-negative number.
- `hit_at_ms` must be a non-negative number and must not be greater than `expand_duration_ms`.
- `max_targets` must be a positive integer, or a clearly declared `unlimited` enum value if the schema supports it.
- `center_policy` must be an enum; the first version only allows `player_center`.
- `damage_falloff_by_distance` must be either a legal enum or a legal numeric rule declared by the template.
- `ring_width` must be a positive number.
- `status_chance_scale` must have a legal numeric range.
- Scripts, expression DSL fields, function-call strings, complex expression interpreter fields, and undeclared params must be rejected.

Rationale: `player_nova` is an area template, but keeping it declarative and whitelisted preserves the safety model already used by `projectile` and `fan_projectile`.

### 3. SkillEditor `player_nova` module

SkillEditor must add a range nova module for `behavior.template = player_nova` with:

- `radius`
- `expand_duration_ms`
- `hit_at_ms`
- `max_targets`
- `center_policy`
- `damage_falloff_by_distance`
- `ring_width`
- `status_chance_scale`
- read-only range summary
- read-only hit timing summary

The editor must use schema and behavior-template whitelist validation on save. It must reject undeclared fields, illegal enum values, invalid numeric ranges, and invalid `hit_at_ms > expand_duration_ms` with Chinese error text. Range fields must remain real behavior params, not frontend-only fake params.

Rationale: migration is not complete unless designers can edit all behavior fields in the same editor surface used by previous migrated skills.

### 4. SkillRuntime `player_nova` behavior

Runtime behavior must:

- Use the player position or cast source position as the nova center.
- Emit `cast_start`.
- Emit `area_spawn` with center, radius, ring width, expand duration, hit timing, and relevant VFX payload.
- Select targets by distance from the player-centered nova radius.
- Exclude targets outside `radius`.
- Respect `max_targets`.
- Emit `damage` at or after `hit_at_ms`.
- Emit `hit_vfx` and `floating_text` after or with `damage`.
- Use `damage_type = cold`.
- Avoid target-point explosion semantics.
- Avoid release-time instant HP removal.
- Avoid static fake events.
- Avoid a Combat Runtime branch specific to `active_frost_nova`.

Rationale: SkillEvent is the shared contract. The WebApp and Combat Runtime must consume event facts, not infer area behavior from skill identity.

### 5. WebApp SkillEvent consumption

WebApp must render the nova from `area_spawn` event data. It must use event payload fields such as center, radius, duration, `vfx_key`, and timing, then render `damage`, `hit_vfx`, and `floating_text` from their corresponding events.

It must not guess behavior from `active_frost_nova`, old `behavior_type = area`, or VFX names.

### 6. Skill Test Arena acceptance

Required scenarios:

- Dense small monsters: verifies multiple targets inside radius are hit and outside targets are excluded.
- Single dummy: verifies basic damage timing and player-centered radius.
- Three-target horizontal row: verifies radius boundary behavior.

Required checks:

- Nova center equals player or cast source position.
- Multiple in-range enemies can be hit.
- Out-of-range enemies are not hit.
- HP is unchanged before `hit_at_ms`.
- HP changes only through `damage` events at or after `hit_at_ms`.
- Changing `radius` changes hit target coverage.
- Changing `expand_duration_ms` changes presentation timing.
- Changing `hit_at_ms` changes damage timing.
- Modifier Test Stack affects final damage or range params without writing production data.

### 7. SkillEvent timeline acceptance

Timeline must display real events for `active_frost_nova`, including:

- `cast_start`
- `area_spawn`
- `damage`
- `hit_vfx`
- `floating_text`
- `cooldown_update` when present

Each displayed event must include:

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

### 8. AI self-test report acceptance

Expected player-facing description:

"自动以玩家自身为中心释放一圈向外扩散的冰霜新星，命中范围内敌人后造成冰霜伤害，并显示冰霜范围爆发特效与伤害浮字。"

The report must check:

- `area_spawn` exists.
- `area_spawn` is centered on the player.
- `damage` exists.
- `hit_vfx` exists.
- `floating_text` exists.
- `damage` is not earlier than `hit_at_ms`.
- HP is not reduced before `hit_at_ms`.
- In-range targets are hit.
- Out-of-range targets are not hit.
- `damage_type = cold`.
- Changing `radius` changes target coverage.
- The conclusion is `通过`, `部分通过`, or `不通过`.
- Inconsistencies and suggested fixes are Chinese.

## Risks / Trade-offs

- Area behavior could accidentally become target-centered because previous projectile templates aim at nearest enemies. Mitigation: require `center_policy = player_center`, arena center assertions, and report checks.
- Damage timing could drift from presentation timing. Mitigation: `area_spawn.duration_ms` expresses visual expansion, while `damage.delay_ms` must respect `hit_at_ms`; tests must verify both.
- `max_targets` can be ambiguous if unlimited is allowed. Mitigation: first Apply should choose one explicit representation and enforce it in schema, template, editor, and runtime.
- Frontend could be tempted to special-case frost nova visuals. Mitigation: acceptance requires rendering from `area_spawn` event payload and forbids skill-id guessing.
- Existing area modifiers may affect radius without visible validation. Mitigation: Modifier Test Stack must prove damage or radius params affect real SkillEvents.

## Migration Plan

1. Add `player_nova` schema/template validation.
2. Create the `active_frost_nova` Skill Package.
3. Add SkillEditor fields and validation.
4. Implement SkillRuntime `player_nova` event generation.
5. Consume `area_spawn` in WebApp.
6. Add Skill Test Arena and timeline/report support.
7. Run strict OpenSpec validation, config validation, Python tests, WebApp build/test, and AI report generation.

Rollback strategy: because this migration introduces a new Skill Package path, rollback can remove or disable `active_frost_nova/skill.yaml` and keep the old `skill_templates.toml` path for non-migrated skills. Apply must not migrate any other active skill as part of this change.

## Open Questions

- Should `max_targets` use a positive integer only, or should the first Apply allow a literal `unlimited` enum?
- Should `damage_falloff_by_distance` start as `none` only, or include a simple first-version enum such as `linear_outer_ring`?
- Which VFX keys should be introduced for `area_spawn` versus `hit_vfx` while keeping all player-facing text Chinese?
