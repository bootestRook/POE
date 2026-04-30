## ADDED Requirements

### Requirement: Lightning Chain Skill Package
V1 SHALL migrate `active_lightning_chain / 连锁闪电` from the old skill template path into a Skill Package.

#### Scenario: Load lightning chain Skill Package
- **WHEN** `active_lightning_chain` is migrated
- **THEN** the system SHALL load it from `configs/skills/active/active_lightning_chain/skill.yaml`

#### Scenario: Use chain behavior template
- **WHEN** the `active_lightning_chain` Skill Package is loaded
- **THEN** it SHALL declare `behavior.template = chain`

#### Scenario: Use lightning damage type
- **WHEN** the `active_lightning_chain` Skill Package is validated
- **THEN** it SHALL declare `classification.damage_type = lightning`

#### Scenario: Keep Chinese player-facing text
- **WHEN** `active_lightning_chain` name, description, damage reason, VFX feedback, screen feedback, or floating text is shown
- **THEN** the player-visible text SHALL be Chinese and SHALL come from localization keys

#### Scenario: Do not migrate other active skills
- **WHEN** this change is applied
- **THEN** it SHALL NOT create Skill Packages for `active_lava_orb`, `active_fungal_petards`, or any other active skill outside this change

### Requirement: Chain Behavior Template
V1 SHALL provide a declarative `chain` behavior template for real multi-target lightning jumps.

#### Scenario: Declare chain template fields
- **WHEN** `configs/skills/behavior_templates/chain.yaml` is validated
- **THEN** it SHALL declare a whitelist including `chain_count`, `chain_radius`, `chain_delay_ms`, `damage_falloff_per_chain`, `target_policy`, `allow_repeat_target`, `max_targets`, and `segment_vfx_key`

#### Scenario: Validate numeric chain fields
- **WHEN** a Skill Package declares `behavior.template = chain`
- **THEN** validation SHALL require positive integer `chain_count`, positive `chain_radius`, non-negative `chain_delay_ms`, and legal numeric-range `damage_falloff_per_chain`

#### Scenario: Validate target selection fields
- **WHEN** a Skill Package declares `behavior.template = chain`
- **THEN** validation SHALL require enum `target_policy` with first-version support for `nearest_not_hit`, boolean `allow_repeat_target` defaulting to `false`, and positive integer or explicitly declared `unlimited` `max_targets`

#### Scenario: Validate key-only segment VFX
- **WHEN** a Skill Package declares `segment_vfx_key`
- **THEN** validation SHALL treat it as a key-only field and SHALL NOT use it as player-visible text

#### Scenario: Reject undeclared chain params
- **WHEN** a Skill Package declares `behavior.template = chain`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, frontend-only fake params, and params not declared by the `chain` template

#### Scenario: Generate real chain segments
- **WHEN** Skill Runtime executes a `chain` skill
- **THEN** it SHALL generate one or more `chain_segment` SkillEvents from the initial target through subsequent chained targets according to `chain_count`, `chain_radius`, `target_policy`, `allow_repeat_target`, and `max_targets`

### Requirement: SkillEditor Chain Field Support
SkillEditor SHALL expose a dedicated `chain` module before the lightning chain migration is considered complete.

#### Scenario: Show all editable chain fields
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template = chain`
- **THEN** it SHALL expose editable fields for `chain_count`, `chain_radius`, `chain_delay_ms`, `damage_falloff_per_chain`, `target_policy`, `allow_repeat_target`, `max_targets`, and `segment_vfx_key`

#### Scenario: Show read-only chain summaries
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template = chain`
- **THEN** it SHALL show a read-only maximum chain segment summary and a read-only estimated total chain duration summary

#### Scenario: Validate chain editor fields
- **WHEN** SkillEditor saves `chain` behavior params
- **THEN** it SHALL validate integer fields, numeric ranges, enum fields, boolean fields, key-only `segment_vfx_key`, and unknown fields through the skill schema and behavior-template whitelist

#### Scenario: Reject invalid chain values in Chinese
- **WHEN** SkillEditor rejects invalid `chain_count`, `chain_radius`, `chain_delay_ms`, `damage_falloff_per_chain`, `target_policy`, `allow_repeat_target`, `max_targets`, `segment_vfx_key`, or undeclared fields
- **THEN** it SHALL display Chinese error text and SHALL NOT persist invalid skill data

#### Scenario: Do not save frontend-only chain params
- **WHEN** SkillEditor saves a `chain` Skill Package
- **THEN** it SHALL NOT write frontend-only fake params or any field not declared by the `chain` behavior template

### Requirement: Lightning Chain SkillEvent
V1 SHALL express `active_lightning_chain` through real SkillEvents for chain segments, damage, and presentation.

#### Scenario: Emit chain event timeline
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** it SHALL output `cast_start`, one or more `chain_segment`, one or more `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when present

#### Scenario: Include required event fields
- **WHEN** SkillEvent timeline displays `active_lightning_chain` events
- **THEN** each relevant event SHALL include `timestamp_ms`, `delay_ms`, `duration_ms`, `source_entity`, `target_entity`, `amount`, `damage_type`, `vfx_key`, `reason_key`, and `payload`

#### Scenario: Include chain segment payload
- **WHEN** Skill Runtime outputs a `chain_segment`
- **THEN** its payload SHALL include `segment_index`, `from_target`, `to_target`, `start_position`, `end_position`, `chain_radius`, `chain_delay_ms`, `damage_scale`, and `vfx_key`

#### Scenario: Select initial and subsequent targets
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** it SHALL select the nearest enemy as the initial target and then choose subsequent targets within `chain_radius` according to `target_policy`

#### Scenario: Do not repeat targets by default
- **WHEN** `allow_repeat_target = false`
- **THEN** Skill Runtime SHALL NOT choose an already-hit target for a later chain segment

#### Scenario: Apply chain count and target limits
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** `chain_count` SHALL limit the maximum number of `chain_segment` events and `max_targets` SHALL limit the maximum number of damaged targets

#### Scenario: Delay damage by chain segment timing
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** target life SHALL NOT be reduced at `cast_start`, and life reduction SHALL occur only through `damage` events at or after the corresponding `chain_segment`

#### Scenario: Apply lightning damage and falloff
- **WHEN** a target is damaged by `active_lightning_chain`
- **THEN** the `damage` event SHALL use `damage_type = lightning`, and later chain segments SHALL apply damage according to `damage_falloff_per_chain`

#### Scenario: Emit presentation events from real hits
- **WHEN** a target is hit by `active_lightning_chain`
- **THEN** Skill Runtime SHALL emit `hit_vfx` and `floating_text` aligned with the corresponding `damage` event

#### Scenario: Do not fake chain behavior
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** it SHALL NOT resolve the skill as a single visual line, a release-time instant damage batch, a static fake event list, or an `active_lightning_chain` special branch in Combat Runtime

### Requirement: Lightning Chain Test Arena Acceptance
Skill Test Arena SHALL validate `active_lightning_chain` using real `chain_segment` and `damage` results.

#### Scenario: Validate three target row chain behavior
- **WHEN** Skill Test Arena runs `active_lightning_chain` in the three-target-row scenario
- **THEN** it SHALL verify the initial target is hit, subsequent targets are selected by `chain_radius`, and chain segment order is visible

#### Scenario: Validate dense pack chain behavior
- **WHEN** Skill Test Arena runs `active_lightning_chain` in the dense-pack scenario
- **THEN** it SHALL verify real multi-target jumps and SHALL verify targets are not repeated by default

#### Scenario: Validate single dummy timing
- **WHEN** Skill Test Arena runs `active_lightning_chain` in the single-dummy scenario
- **THEN** it SHALL verify the base cast, chain segment, damage, hit VFX, floating text, and no life reduction before the relevant damage event

#### Scenario: Validate chain count parameter
- **WHEN** Skill Test Arena changes `chain_count`
- **THEN** the number of emitted `chain_segment` events SHALL change according to the configured limit

#### Scenario: Validate chain radius parameter
- **WHEN** Skill Test Arena changes `chain_radius`
- **THEN** the set of reachable chained targets SHALL change according to the configured radius

#### Scenario: Validate chain delay parameter
- **WHEN** Skill Test Arena changes `chain_delay_ms`
- **THEN** the time interval between chain segments and corresponding damage events SHALL change

#### Scenario: Validate damage falloff parameter
- **WHEN** Skill Test Arena changes `damage_falloff_per_chain`
- **THEN** later chain segment damage amounts SHALL change according to the configured falloff

#### Scenario: Validate modifier stack effects
- **WHEN** Skill Test Arena runs `active_lightning_chain` with the test Modifier Stack
- **THEN** the stack SHALL affect final damage or chain runtime parameters used by actual SkillEvents without writing production inventory, gem instances, or Skill Package data

### Requirement: Lightning Chain AI Self-Test Report
The AI self-test report SHALL evaluate `active_lightning_chain` from real Skill Test Arena results.

#### Scenario: Generate lightning chain report
- **WHEN** `python tools\generate_skill_test_report.py --skill active_lightning_chain --scenario dense_pack` is run
- **THEN** it SHALL generate a Chinese AI self-test report based on real test results

#### Scenario: Check required chain events
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether `chain_segment`, multiple `chain_segment` events, `damage`, `hit_vfx`, and `floating_text` exist

#### Scenario: Check chain timing and damage type
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether damage is not earlier than the corresponding `chain_segment`, no HP is reduced at `cast_start`, and `damage_type = lightning`

#### Scenario: Check target selection behavior
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether multiple targets are hit, whether the default behavior avoids repeated targets, and whether out-of-radius targets are not chained

#### Scenario: Check chain parameter effects
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether changing `chain_count`, `chain_radius`, `chain_delay_ms`, and `damage_falloff_per_chain` changes real chain results

#### Scenario: Report Chinese conclusion and fixes
- **WHEN** the AI self-test report finishes evaluating `active_lightning_chain`
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes
