## ADDED Requirements

### Requirement: Skill Module Chain
V1 Skill Packages SHALL support ordered modules inside one Skill Package for skills that require composition of reusable behavior modules.

#### Scenario: Ordered modules are declared
- **WHEN** a Skill Package declares `modules`
- **THEN** each module SHALL have a stable `id`, a whitelisted `type`, and declared fields only

#### Scenario: Module ids are unique
- **WHEN** a Skill Package declares multiple modules
- **THEN** validation SHALL reject duplicate module ids within that Skill Package

#### Scenario: Marker trigger links are declared
- **WHEN** one module declares an output marker and a later module declares a trigger
- **THEN** the trigger SHALL reference the marker by id through declared marker / trigger fields

#### Scenario: Unresolved triggers are rejected
- **WHEN** a module declares `trigger_marker_id` that does not match a preceding declared marker id
- **THEN** validation SHALL reject the Skill Package and SHALL NOT silently execute the triggered module

#### Scenario: Module chain is not scripting
- **WHEN** a Skill Package declares modules
- **THEN** validation SHALL reject arbitrary scripts, node graph data, complex expression interpreter fields, function-call strings, and undeclared fields

### Requirement: Projectile Ballistic Extension
The projectile module SHALL support ballistic projectile timing and marker emission for thrown skills.

#### Scenario: Ballistic trajectory is supported
- **WHEN** a projectile module declares `trajectory = ballistic`
- **THEN** validation SHALL accept it as a legal projectile trajectory enum value

#### Scenario: Ballistic timing fields are validated
- **WHEN** a projectile module declares `travel_time_ms` and `arc_height`
- **THEN** `travel_time_ms` SHALL be positive and `arc_height` SHALL be non-negative

#### Scenario: Projectile target policy is validated
- **WHEN** a projectile module declares `target_policy`
- **THEN** validation SHALL accept only `nearest_enemy`, `locked_target`, or `target_position`

#### Scenario: Impact marker is emitted
- **WHEN** a projectile with `impact_marker_id` reaches its impact point
- **THEN** Skill Runtime SHALL emit `projectile_impact` with `marker_id` and `impact_position`

#### Scenario: Projectile spawn payload includes ballistic data
- **WHEN** Skill Runtime emits `projectile_spawn` for a ballistic projectile
- **THEN** the payload SHALL include `trajectory`, `start_position`, `target_position`, `travel_time_ms`, `arc_height`, and `impact_marker_id`

### Requirement: Triggered Damage Zone
The `damage_zone` module SHALL support marker-triggered execution and trigger-position origin for composed skills.

#### Scenario: Trigger marker is validated
- **WHEN** a damage zone module declares `trigger_marker_id`
- **THEN** validation SHALL require it to match a preceding module marker such as `projectile.impact_marker_id`

#### Scenario: Trigger delay is validated
- **WHEN** a damage zone module declares `trigger_delay_ms`
- **THEN** validation SHALL require it to be non-negative

#### Scenario: Trigger position origin is supported
- **WHEN** a damage zone module declares `origin_policy = trigger_position`
- **THEN** Skill Runtime SHALL use the matched `projectile_impact.impact_position` as the damage zone origin

#### Scenario: Warning event is emitted before triggered hit
- **WHEN** a triggered damage zone is primed by a projectile impact marker
- **THEN** Skill Runtime SHALL emit `damage_zone_prime` with `trigger_marker_id`, `origin`, `delay_ms`, `radius`, and `vfx_key`

#### Scenario: Triggered damage zone does not silently execute without source
- **WHEN** no matching trigger marker is emitted
- **THEN** Skill Runtime SHALL NOT emit the triggered `damage_zone` or `damage` events as if the trigger succeeded

### Requirement: Fungal Petards Skill Package
V1 SHALL migrate `active_fungal_petards / 真菌爆弹` from the old `skill_templates.toml` path into a Skill Package using a projectile plus triggered damage zone module chain.

#### Scenario: Fungal Petards uses module chain
- **WHEN** `active_fungal_petards` is migrated
- **THEN** its Skill Package SHALL use a `projectile` module followed by a `damage_zone` module linked by marker / trigger ids

#### Scenario: Fungal Petards does not use delayed area
- **WHEN** `active_fungal_petards` is migrated
- **THEN** it SHALL NOT use or create a `delayed_area` behavior template

#### Scenario: Fungal Petards uses physical circular explosion
- **WHEN** the triggered damage zone resolves for `active_fungal_petards`
- **THEN** the `damage_zone` SHALL have `shape = circle`, `damage_type = physical`, and origin from the projectile impact position

#### Scenario: Fungal Petards remains localized
- **WHEN** Fungal Petards name, description, damage reason, VFX feedback, screen feedback, or floating text is shown
- **THEN** player-visible text SHALL be Chinese and SHALL come from localization keys

#### Scenario: Lava orb is not migrated
- **WHEN** this change is applied
- **THEN** it SHALL NOT migrate `active_lava_orb` or create a Lava Orb Skill Package

### Requirement: Fungal Petards SkillEvent
V1 SHALL express `active_fungal_petards` through real SkillEvents for cast, ballistic projectile, impact marker, warning, explosion, damage, and presentation.

#### Scenario: Full event timeline is emitted
- **WHEN** Skill Runtime executes `active_fungal_petards`
- **THEN** it SHALL output `cast_start`, `projectile_spawn`, `projectile_impact`, `damage_zone_prime`, `damage_zone`, `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when present

#### Scenario: Damage zone payload is circular
- **WHEN** Skill Runtime emits `damage_zone` for `active_fungal_petards`
- **THEN** the payload SHALL include `shape = circle`, `origin`, `radius`, `hit_at_ms`, `damage_type`, and `vfx_key`

#### Scenario: Damage occurs only after explosion hit
- **WHEN** `active_fungal_petards` is cast
- **THEN** target life SHALL NOT be reduced at `cast_start`, before `projectile_impact`, or before the triggered damage zone hit resolves

#### Scenario: Damage is the only HP-changing event
- **WHEN** targets are hit by `active_fungal_petards`
- **THEN** HP reduction SHALL occur only through `damage` events emitted after the `damage_zone`

#### Scenario: No fake fungal events
- **WHEN** Skill Runtime executes `active_fungal_petards`
- **THEN** it SHALL NOT emit static fake event lists or resolve the skill as target-point instant damage

### Requirement: SkillEditor Module Chain Support
SkillEditor SHALL expose module-chain Skill Packages through a controlled “技能模块链” panel.

#### Scenario: Projectile module fields are shown
- **WHEN** SkillEditor opens `active_fungal_petards`
- **THEN** it SHALL show projectile module fields for `trajectory`, `travel_time_ms`, `arc_height`, `target_policy`, `impact_marker_id`, `projectile_speed`, `projectile_width`, `projectile_height`, and `vfx_key`

#### Scenario: Damage zone module fields are shown
- **WHEN** SkillEditor opens `active_fungal_petards`
- **THEN** it SHALL show damage zone module fields for `trigger_marker_id`, `trigger_delay_ms`, `shape`, `origin_policy`, `radius`, `hit_at_ms`, `max_targets`, `damage_type`, and `vfx_key`

#### Scenario: Marker trigger link is shown
- **WHEN** SkillEditor displays the module chain
- **THEN** it SHALL show `projectile.impact_marker_id -> damage_zone.trigger_marker_id`

#### Scenario: Trigger input is controlled
- **WHEN** SkillEditor edits `trigger_marker_id`
- **THEN** it SHALL prefer selecting from existing declared marker ids and SHALL NOT allow saving a trigger that references a missing marker

#### Scenario: Test modifiers do not persist
- **WHEN** SkillEditor runs Fungal Petards with a test Modifier Stack
- **THEN** it SHALL NOT write test modifier values into the real Skill Package YAML and SHALL NOT restore random affix editing

### Requirement: WebApp Module Chain Rendering
WebApp SHALL render Fungal Petards from SkillEvent payloads instead of skill identity or legacy behavior guesses.

#### Scenario: Render ballistic projectile from event
- **WHEN** WebApp receives `projectile_spawn` with `trajectory = ballistic`
- **THEN** it SHALL render the projectile path using event-provided `start_position`, `target_position`, `travel_time_ms`, and `arc_height`

#### Scenario: Render impact and warning from events
- **WHEN** WebApp receives `projectile_impact` and `damage_zone_prime`
- **THEN** it SHALL render the landing and warning circle from event-provided marker, origin, delay, radius, and VFX payload data

#### Scenario: Render explosion from damage zone event
- **WHEN** WebApp receives `damage_zone` with `shape = circle`
- **THEN** it SHALL render the explosion range from event-provided origin, radius, timing, damage type, and VFX key

#### Scenario: Render presentation events from real events
- **WHEN** WebApp receives `damage`, `hit_vfx`, or `floating_text`
- **THEN** it SHALL render HP changes, hit effects, and floating text from those events

#### Scenario: Do not guess Fungal Petards behavior
- **WHEN** WebApp renders `active_fungal_petards`
- **THEN** it SHALL NOT infer behavior from skill id, old `behavior_type`, `visual_effect`, VFX key, or hardcoded Fungal Petards branches

### Requirement: Fungal Petards Skill Test Arena Acceptance
Skill Test Arena SHALL validate `active_fungal_petards` using real projectile impact, triggered damage zone, damage, and presentation events.

#### Scenario: Validate single dummy timing
- **WHEN** Skill Test Arena runs `active_fungal_petards` against one dummy
- **THEN** it SHALL verify `projectile_spawn`, `projectile_impact`, `damage_zone_prime`, `damage_zone`, no HP loss before explosion, HP loss after `damage`, hit VFX, and floating text

#### Scenario: Validate dense pack area behavior
- **WHEN** Skill Test Arena runs `active_fungal_petards` against dense small monsters
- **THEN** it SHALL verify targets inside the circular radius are hit and targets outside the radius are not hit

#### Scenario: Validate three target row radius behavior
- **WHEN** Skill Test Arena runs `active_fungal_petards` against three horizontal targets
- **THEN** it SHALL verify hit selection changes according to circular radius and impact position

#### Scenario: Validate timing and geometry parameter effects
- **WHEN** Skill Test Arena changes `travel_time_ms`, `arc_height`, `trigger_delay_ms`, or `radius`
- **THEN** projectile impact timing, projectile arc payload or rendering, explosion timing, or hit coverage SHALL change according to the modified parameter

#### Scenario: Validate modifier stack effects
- **WHEN** Skill Test Arena runs `active_fungal_petards` with a test Modifier Stack
- **THEN** the stack SHALL affect final damage or range parameters used by actual SkillEvents without writing production inventory, gem instances, or Skill Package data

### Requirement: AI Report Module Chain Validation
The AI self-test report SHALL evaluate Fungal Petards module-chain behavior from real Skill Test Arena events and HP results.

#### Scenario: Check projectile impact chain
- **WHEN** the AI self-test report evaluates `active_fungal_petards`
- **THEN** it SHALL check whether `projectile_spawn` exists, `trajectory = ballistic`, `projectile_impact` exists, and `projectile_impact` carries `marker_id`

#### Scenario: Check triggered damage zone chain
- **WHEN** the AI self-test report evaluates `active_fungal_petards`
- **THEN** it SHALL check whether `damage_zone_prime` exists, references `trigger_marker_id`, `damage_zone` exists, `shape = circle`, and damage zone origin equals projectile impact position

#### Scenario: Check damage timing and damage type
- **WHEN** the AI self-test report evaluates `active_fungal_petards`
- **THEN** it SHALL check that damage is not earlier than `projectile_impact + trigger_delay_ms`, no HP is reduced before explosion, HP is reduced after `damage`, and `damage_type = physical`

#### Scenario: Check parameter mutation effects
- **WHEN** the AI self-test report evaluates changed Fungal Petards parameters
- **THEN** it SHALL check that radius changes hit targets, `travel_time_ms` changes landing timing, `arc_height` changes ballistic presentation parameters, and `trigger_delay_ms` changes explosion timing

#### Scenario: Report Chinese conclusion and fixes
- **WHEN** the AI self-test report finishes evaluating `active_fungal_petards`
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes

