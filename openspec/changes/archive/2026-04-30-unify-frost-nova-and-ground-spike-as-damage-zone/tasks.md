## 1. Phase 0: Current State And Scope Guard

- [x] 1.1 Confirm `migrate-active-puncture-to-melee-arc` is complete and decide whether it must be archived before Apply; verify active changes with `cmd /c openspec list --json`
- [x] 1.2 Confirm current migrated Skill Packages include `active_fire_bolt`, `active_ice_shards`, `active_penetrating_shot`, `active_frost_nova`, and `active_puncture`
- [x] 1.3 Confirm `active_lightning_chain`, `active_lava_orb`, and `active_fungal_petards` still have no Skill Package directory and remain out of scope
- [x] 1.4 Confirm no changes are needed to formal drops, inventory, gem board, random affix UI, or random affix generation

## 2. Phase 1: Damage Zone Schema And Template

- [x] 2.1 Add `configs/skills/behavior_templates/damage_zone.yaml` with a strict whitelist for common, circle, and rectangle params
- [x] 2.2 Extend `configs/skills/schema/skill.schema.json` and config validation so `damage_zone` rejects undeclared params, scripts, expression DSL fields, and frontend-only fake params
- [x] 2.3 Validate common fields: `shape`, `origin_policy`, `facing_policy`, `hit_at_ms`, `max_targets`, `status_chance_scale`, and `zone_vfx_key`
- [x] 2.4 Validate circle fields: positive `radius` and effective angle of 360 degrees
- [x] 2.5 Validate rectangle fields: positive `length`, positive `width`, and legal `angle_offset_deg` or equivalent declared angle field
- [x] 2.6 Add config validation tests for valid and invalid `damage_zone` circle and rectangle packages

## 3. Phase 2: Frost Nova Circle Migration

- [x] 3.1 Convert `configs/skills/active/active_frost_nova/skill.yaml` to `behavior.template = damage_zone` with `shape = circle`
- [x] 3.2 Preserve frost nova Chinese player-facing text, cold damage type, timing, radius semantics, presentation keys, and modifier behavior
- [x] 3.3 Add regression tests proving frost nova circle radius hit coverage, `hit_at_ms` timing, `damage` event life reduction, hit VFX, floating text, and AI report support

## 4. Phase 3: Puncture To Ground Spike Rectangle Migration

- [x] 4.1 Rework `configs/skills/active/active_puncture/skill.yaml` to represent player-facing `鍦板埡` with `behavior.template = damage_zone` and `shape = rectangle`
- [x] 4.2 Update Chinese localization so player-visible name, description, reason text, screen feedback, VFX feedback, and floating text describe `鍦板埡`
- [x] 4.3 Preserve internal compatibility where needed for `active_puncture` id while ensuring visible behavior is ground spike, not melee slash
- [x] 4.4 Add package/config tests proving ground spike uses physical damage, rectangle damage zone params, and Chinese visible text

## 5. Phase 4: SkillEditor Damage Zone Module

- [x] 5.1 Replace separate frost nova / melee arc editor modules with one shared `浼ゅ缁撶畻鍖哄煙` module for `damage_zone`
- [x] 5.2 Show common fields for shape, origin policy, facing policy, hit timing, max targets, status chance scale, and VFX key
- [x] 5.3 Show circle-only fields for radius and read-only or hidden 360-degree angle
- [x] 5.4 Show rectangle-only fields for length, width, and angle offset or equivalent angle field
- [x] 5.5 Add editor validation and Chinese error tests for invalid shape, radius, length, width, angle, hit timing, max targets, VFX key, and unknown params

## 6. Phase 5: SkillRuntime Damage Zone Resolver

- [x] 6.1 Implement a shared runtime `damage_zone` resolver that emits `cast_start`, `damage_zone`, `damage`, `hit_vfx`, and `floating_text`
- [x] 6.2 Implement circle hit testing by origin and radius for frost nova
- [x] 6.3 Implement rectangle hit testing by origin, facing direction, length, width, and angle offset for ground spike
- [x] 6.4 Ensure `hit_at_ms` gates all life reduction and only `damage` events reduce life
- [x] 6.5 Ensure `max_targets`, damage type, status chance scale, and modifier-adjusted runtime params are respected
- [x] 6.6 Add runtime tests for circle radius, rectangle length, rectangle width, rectangle angle, timing, max targets, and modifier effects

## 7. Phase 6: WebApp Damage Zone Rendering

- [x] 7.1 Update WebApp SkillEvent pipeline to consume `damage_zone` events
- [x] 7.2 Render `shape = circle` from event origin, radius, timing, and VFX key
- [x] 7.3 Render `shape = rectangle` as a ground spike line from event origin, facing direction, length, width, angle, timing, and VFX key
- [x] 7.4 Keep `damage`, `hit_vfx`, and `floating_text` rendering event-driven
- [x] 7.5 Add smoke checks proving WebApp does not infer behavior from skill id, legacy template id, behavior type, visual effect, or VFX key

## 8. Phase 7: Skill Test Arena, Timeline, And AI Reports

- [x] 8.1 Update Skill Test Arena to validate frost nova circle behavior and ground spike rectangle behavior
- [x] 8.2 Add arena scenarios or assertions for circle radius, rectangle length, rectangle width, rectangle angle, and `hit_at_ms`
- [x] 8.3 Update SkillEvent timeline supported types and checks to display `damage_zone` with required event fields
- [x] 8.4 Update AI self-test report for frost nova `shape = circle` checks
- [x] 8.5 Update AI self-test report for ground spike `shape = rectangle` checks and Chinese conclusion / inconsistency / suggestion output

## 9. Phase 8: Verification And Regression

- [x] 9.1 Run `python tools\validate_v1_configs.py`
- [x] 9.2 Run `python -m unittest discover tests`
- [x] 9.3 Run `cmd /c openspec validate unify-frost-nova-and-ground-spike-as-damage-zone --strict`
- [x] 9.4 Run `cmd /c npm run build`
- [x] 9.5 Run `cmd /c npm test`
- [x] 9.6 Run `python tools\generate_skill_test_report.py --skill active_frost_nova --scenario dense_pack`
- [x] 9.7 Run `python tools\generate_skill_test_report.py --skill active_puncture --scenario dense_pack`
- [x] 9.8 Confirm projectile skills `active_fire_bolt`, `active_ice_shards`, and `active_penetrating_shot` have no regression
- [x] 9.9 Confirm unmigrated skills remain unmigrated and no random affix UI/generation returns
