## 0. Phase 0: Current State Scan And Module-Chain Capability Confirmation

Goal: Confirm prerequisites and prevent work from starting on the wrong base.
Allowed scope: OpenSpec files, current skill configs, existing SkillEditor / Skill Test Arena / SkillEvent / AI report references.
Forbidden scope: Runtime edits, WebApp edits, `active_fungal_petards/skill.yaml`, `skill.yaml` creation, or config migration.
Acceptance: `migrate-active-lightning-chain-to-chain` archive is confirmed; usable `damage_zone` template is confirmed; active changes are listed; migrated packages and old Fungal Petards path are confirmed.
Recommended verification command: `cmd /c openspec list --json`

- [x] 0.1 Confirm `migrate-active-lightning-chain-to-chain` is archived under `openspec/changes/archive`.
- [x] 0.2 Confirm `damage_zone` is available through archived change history or `configs/skills/behavior_templates/damage_zone.yaml`.
- [x] 0.3 List current active changes and note completed but unarchived work.
- [x] 0.4 Confirm migrated Skill Packages include `active_fire_bolt`, `active_ice_shards`, `active_penetrating_shot`, `active_frost_nova`, `active_puncture`, and `active_lightning_chain`.
- [x] 0.5 Confirm `active_fungal_petards` still uses `configs/skills/skill_templates.toml`.
- [x] 0.6 Confirm existing SkillEditor, Skill Test Arena, SkillEvent timeline, and AI self-test report capabilities remain reusable migration templates.

## 1. Phase 1: Skill Package Module-Chain Schema Design

Goal: Add an ordered module-chain model to one Skill Package.
Allowed scope: Skill schema, schema validation utilities, OpenSpec requirements, module-chain validation tests.
Forbidden scope: Node editors, script DSL, expression interpreters, undeclared module fields, runtime special branches.
Acceptance: `modules` supports ordered entries, module ids, whitelisted types, marker / trigger links, and unresolved trigger rejection.
Recommended verification command: `python tools\\validate_skill_packages.py`

- [x] 1.1 Extend Skill Package schema to support `modules`.
- [x] 1.2 Require stable unique module ids within one Skill Package.
- [x] 1.3 Validate module type against declared behavior/module templates.
- [x] 1.4 Validate `impact_marker_id` uniqueness and `trigger_marker_id` references.
- [x] 1.5 Reject unresolved triggers, duplicate marker ids, undeclared fields, scripts, and expression-like values.

## 2. Phase 2: Projectile Ballistic / Impact Marker Extension

Goal: Extend the reusable projectile module for thrown ballistic projectiles.
Allowed scope: Projectile behavior template, projectile schema validation, runtime projectile module implementation, event payload tests.
Forbidden scope: Fungal Petards-only projectile code, Combat Runtime skill-id branches, target-point instant damage.
Acceptance: `trajectory = ballistic`, `travel_time_ms`, `arc_height`, `target_policy`, and `impact_marker_id` are validated and emitted in real events.
Recommended verification command: `python tools\\validate_skill_packages.py`

- [x] 2.1 Add `trajectory` enum with `linear` and `ballistic`.
- [x] 2.2 Add positive `travel_time_ms` validation.
- [x] 2.3 Add non-negative `arc_height` validation.
- [x] 2.4 Add `target_policy` enum with `nearest_enemy`, `locked_target`, and `target_position`.
- [x] 2.5 Add `impact_marker_id` validation and event payload propagation.
- [x] 2.6 Emit `projectile_spawn` and `projectile_impact` with ballistic timing and marker data.

## 3. Phase 3: Triggered Damage Zone Extension

Goal: Allow existing damage zones to be triggered from markers.
Allowed scope: Damage zone behavior template, damage zone schema validation, runtime damage zone trigger scheduling, event payload tests.
Forbidden scope: New `delayed_area` template, static fake damage zones, unmatched trigger success.
Acceptance: Triggered damage zone uses projectile impact position as origin and waits `trigger_delay_ms` before applying damage.
Recommended verification command: `python tools\\validate_skill_packages.py`

- [x] 3.1 Add `trigger_marker_id` validation.
- [x] 3.2 Add non-negative `trigger_delay_ms` validation.
- [x] 3.3 Add `origin_policy = trigger_position`.
- [x] 3.4 Define and validate the relationship between `hit_at_ms` and `trigger_delay_ms`.
- [x] 3.5 Emit `damage_zone_prime` before the actual `damage_zone`.
- [x] 3.6 Ensure `damage` is emitted only after the triggered damage zone resolves.

## 4. Phase 4: Active Fungal Petards Skill Package Creation

Goal: Migrate only `active_fungal_petards` into a module-chain Skill Package.
Allowed scope: `configs/skills/active/active_fungal_petards/skill.yaml`, Chinese localization keys, skill package validation fixtures.
Forbidden scope: `active_lava_orb`, formal drops, inventory, gem board behavior, random affix restoration, `delayed_area`.
Acceptance: Fungal Petards declares projectile and damage zone modules linked by `fungal_impact`, physical damage, circle radius, delayed trigger, and localized Chinese text keys.
Recommended verification command: `python tools\\validate_skill_packages.py`

- [x] 4.1 Create `configs/skills/active/active_fungal_petards/skill.yaml`.
- [x] 4.2 Define `fungal_projectile` as `projectile` with `trajectory = ballistic`.
- [x] 4.3 Define `fungal_explosion_zone` as `damage_zone` triggered by `fungal_impact`.
- [x] 4.4 Ensure `damage_type = physical`.
- [x] 4.5 Remove runtime dependency on the old `skill_templates.toml` path for Fungal Petards only after package validation passes.

## 5. Phase 5: SkillEditor Module-Chain Panel

Goal: Let SkillEditor inspect and edit the Fungal Petards module chain safely.
Allowed scope: SkillEditor module-chain UI, validation messages, test modifier preview plumbing.
Forbidden scope: Node editor, script DSL, arbitrary expressions, writing test modifiers to real `skill.yaml`, restoring random affix editing.
Acceptance: UI shows projectile module fields, damage zone module fields, and the marker / trigger link; save rejects inconsistent links.
Recommended verification command: `npm test -- --runInBand SkillEditor`

- [x] 5.1 Add 鈥滄妧鑳芥ā鍧楅摼鈥?panel for module-chain Skill Packages.
- [x] 5.2 Show projectile fields: `trajectory`, `travel_time_ms`, `arc_height`, `target_policy`, `impact_marker_id`, `projectile_speed`, `projectile_width`, `projectile_height`, and `vfx_key`.
- [x] 5.3 Show damage zone fields: `trigger_marker_id`, `trigger_delay_ms`, `shape`, `origin_policy`, `radius`, `hit_at_ms`, `max_targets`, `damage_type`, and `vfx_key`.
- [x] 5.4 Show `projectile.impact_marker_id -> damage_zone.trigger_marker_id`.
- [x] 5.5 Use dropdown or controlled input for marker ids and prefer existing marker dropdowns for triggers.
- [x] 5.6 Validate marker / trigger consistency before save.

## 6. Phase 6: SkillRuntime Module-Chain Execution

Goal: Execute module chains with real projectile impact and triggered damage zone events.
Allowed scope: SkillRuntime module-chain executor, projectile module runtime, damage zone module runtime, SkillEvent types, focused tests.
Forbidden scope: Combat Runtime `active_fungal_petards` branch, cast-start damage, target-point instant explosion, static fake events.
Acceptance: Runtime emits ballistic projectile, impact marker, warning, explosion, physical damage, VFX, floating text, and cooldown events in the correct order.
Recommended verification command: `python -m pytest tests`

- [x] 6.1 Execute ordered modules from one Skill Package.
- [x] 6.2 Generate ballistic projectile using player and target positions.
- [x] 6.3 Emit `projectile_impact` after `travel_time_ms`.
- [x] 6.4 Resolve damage zone trigger from `impact_marker_id`.
- [x] 6.5 Use `impact_position` as damage zone origin.
- [x] 6.6 Delay explosion and damage by `trigger_delay_ms`.
- [x] 6.7 Apply HP changes only through `damage` events after the damage zone hit.

## 7. Phase 7: WebApp Module-Chain SkillEvent Consumption

Goal: Render the full Fungal Petards sequence from events.
Allowed scope: WebApp SkillEvent renderer, projectile presentation, damage zone warning/explosion presentation, tests or screenshots.
Forbidden scope: Skill id guessing, old `behavior_type` guessing, VFX key behavior guessing, fake frontend events.
Acceptance: WebApp renders ballistic projectile, landing, warning circle, explosion zone, HP change, hit VFX, and floating text from payloads.
Recommended verification command: `npm test -- --runInBand`

- [x] 7.1 Render ballistic projectile from `projectile_spawn`.
- [x] 7.2 Use `travel_time_ms` and `arc_height` for projectile path shape.
- [x] 7.3 Render landing from `projectile_impact`.
- [x] 7.4 Render warning circle from `damage_zone_prime`.
- [x] 7.5 Render explosion range from `damage_zone`.
- [x] 7.6 Render HP deltas, hit VFX, and floating text from `damage`, `hit_vfx`, and `floating_text`.

## 8. Phase 8: Skill Test Arena Fungal Petards Acceptance

Goal: Prove the player-side behavior with controlled scenarios and parameter mutations.
Allowed scope: Skill Test Arena scenarios, test modifier stack, event assertions, HP/range/timing checks.
Forbidden scope: Static fake reports, writing test modifiers to production data, formal inventory or drop changes.
Acceptance: Single dummy, dense pack, and three-target row prove projectile impact, warning, delayed circular physical damage, in-range hits, out-of-range misses, and parameter effects.
Recommended verification command: `python tools\\run_skill_test_arena.py --skill active_fungal_petards`

- [x] 8.1 Add single dummy acceptance for projectile, impact, warning, explosion, and damage order.
- [x] 8.2 Add dense small monster acceptance for multi-target circle hits.
- [x] 8.3 Add three-target row acceptance for radius boundary behavior.
- [x] 8.4 Verify no target HP changes before explosion damage.
- [x] 8.5 Verify `travel_time_ms`, `arc_height`, `trigger_delay_ms`, and `radius` mutations change real results or event payloads.
- [x] 8.6 Verify Modifier Stack affects final damage or range parameters without writing production data.

## 9. Phase 9: SkillEvent Timeline And AI Self-Test Report

Goal: Make Fungal Petards debuggable through the existing timeline and AI report loop.
Allowed scope: Timeline display, report generator checks, Chinese report output, event comparison utilities.
Forbidden scope: Static fake timeline, static fake report, English natural-language player-facing report content.
Acceptance: Timeline shows real module-chain events; AI report checks projectile impact, marker / trigger, damage zone origin, delayed damage, physical damage, parameter effects, and Chinese conclusion/fix items.
Recommended verification command: `python tools\\generate_skill_test_report.py --skill active_fungal_petards --scenario dense_pack`

- [x] 9.1 Add timeline support for `projectile_impact` and `damage_zone_prime`.
- [x] 9.2 Ensure timeline displays marker ids, trigger ids, origin, radius, delay, damage type, VFX key, and payload data.
- [x] 9.3 Add AI report checks for ballistic projectile and impact marker.
- [x] 9.4 Add AI report checks for triggered circle damage zone origin and timing.
- [x] 9.5 Add AI report checks for pre-explosion no-damage and post-damage HP loss.
- [x] 9.6 Add AI report checks for radius, travel time, arc height, and trigger delay parameter effects.
- [x] 9.7 Output Chinese conclusion as `閫氳繃`, `閮ㄥ垎閫氳繃`, or `涓嶉€氳繃`, with Chinese inconsistency items and suggested fixes.

## 10. Phase 10: Verification And Regression

Goal: Confirm the migration is complete without broadening scope.
Allowed scope: Validation commands, focused runtime/editor/WebApp tests, OpenSpec task updates.
Forbidden scope: Unrelated refactors, unrelated active skill migration, lava orb migration, formal drops/inventory/gem board changes.
Acceptance: OpenSpec strict validation passes; skill package validation passes; focused runtime/editor/WebApp/test-arena/report checks pass; no forbidden files were changed.
Recommended verification command: `cmd /c openspec validate migrate-active-fungal-petards-to-triggered-damage-zone --strict`

- [x] 10.1 Run OpenSpec strict validation.
- [x] 10.2 Run Skill Package validation.
- [x] 10.3 Run focused runtime tests for module-chain projectile and triggered damage zone behavior.
- [x] 10.4 Run focused SkillEditor tests for module-chain fields and marker / trigger validation.
- [x] 10.5 Run focused WebApp tests for SkillEvent-driven rendering.
- [x] 10.6 Run Skill Test Arena and AI self-test report for `active_fungal_petards`.
- [x] 10.7 Confirm no runtime, WebApp, formal drop, inventory, gem board, lava orb, or unrelated migration files changed outside the apply scope.


