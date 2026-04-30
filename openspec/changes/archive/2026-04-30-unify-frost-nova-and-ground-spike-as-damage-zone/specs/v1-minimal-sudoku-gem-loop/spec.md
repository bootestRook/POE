## ADDED Requirements

### Requirement: Damage Zone Behavior Template
V1 SHALL provide a declarative `damage_zone` behavior template for non-projectile damage settlement areas / hit zones.

#### Scenario: Declare supported damage zone shapes
- **WHEN** `configs/skills/behavior_templates/damage_zone.yaml` is validated
- **THEN** it SHALL declare supported shapes including `circle` and `rectangle`

#### Scenario: Reject scripts and undeclared params
- **WHEN** a Skill Package declares `behavior.template = damage_zone`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, frontend-only fake params, and params not declared by the `damage_zone` template

#### Scenario: Validate common damage zone params
- **WHEN** a Skill Package declares `behavior.template = damage_zone`
- **THEN** validation SHALL require legal `shape`, `origin_policy`, `facing_policy`, non-negative `hit_at_ms`, positive integer or explicitly declared unlimited `max_targets`, legal `status_chance_scale`, and key-only `zone_vfx_key`

#### Scenario: Validate circle params
- **WHEN** a `damage_zone` Skill Package declares `shape = circle`
- **THEN** validation SHALL require positive `radius` and SHALL treat the effective angle as 360 degrees

#### Scenario: Validate rectangle params
- **WHEN** a `damage_zone` Skill Package declares `shape = rectangle`
- **THEN** validation SHALL require positive `length`, positive `width`, and legal `angle_offset_deg` or equivalent declared angle field

### Requirement: Frost Nova Damage Zone
V1 SHALL represent `active_frost_nova` / `冰霜新星` as a circular `damage_zone`.

#### Scenario: Load frost nova as circle damage zone
- **WHEN** `active_frost_nova` Skill Package is loaded
- **THEN** it SHALL declare `behavior.template = damage_zone` and `shape = circle`

#### Scenario: Frost nova keeps circular hit semantics
- **WHEN** Skill Runtime executes `active_frost_nova`
- **THEN** targets inside the configured circle radius SHALL be eligible for damage and targets outside the radius SHALL NOT be hit

#### Scenario: Frost nova timing remains event based
- **WHEN** Skill Runtime executes `active_frost_nova`
- **THEN** target life SHALL NOT be reduced before `hit_at_ms`, and life reduction SHALL occur through `damage` events at or after `hit_at_ms`

#### Scenario: Frost nova keeps Chinese player-facing text
- **WHEN** `active_frost_nova` name, description, damage reason, VFX feedback, or floating text is shown
- **THEN** the player-visible text SHALL remain Chinese and SHALL come from localization keys

### Requirement: Ground Spike Damage Zone
V1 SHALL rework `active_puncture` / `穿刺` into player-facing `地刺`, represented as a rectangular `damage_zone`.

#### Scenario: Load ground spike as rectangle damage zone
- **WHEN** `active_puncture` Skill Package is loaded after this change
- **THEN** it SHALL declare `behavior.template = damage_zone`, `shape = rectangle`, and `classification.damage_type = physical`

#### Scenario: Show ground spike Chinese text
- **WHEN** the skill name, description, damage reason, VFX feedback, or floating text for `active_puncture` is shown
- **THEN** the player-visible Chinese text SHALL describe `地刺` rather than a melee slash or ranged instant puncture

#### Scenario: Fire a rectangular spike line toward target direction
- **WHEN** Skill Runtime executes the ground spike skill
- **THEN** it SHALL create a rectangular damage zone from the player or cast source position toward the locked target direction, or nearest target direction when no explicit locked target is available

#### Scenario: Ground spike rectangle hit testing
- **WHEN** ground spike resolves targets
- **THEN** targets inside the rectangle defined by origin, facing direction, `length`, `width`, and angle offset SHALL be eligible for hit, while targets beyond length or outside width SHALL NOT be hit

#### Scenario: Ground spike timing and damage events
- **WHEN** ground spike is cast
- **THEN** target life SHALL NOT be reduced at release time or before `hit_at_ms`, and life reduction SHALL occur through `damage` events at or after `hit_at_ms`

#### Scenario: Ground spike physical presentation events
- **WHEN** a target is hit by ground spike
- **THEN** Skill Runtime SHALL output `damage`, `hit_vfx`, and `floating_text` events with `damage_type = physical`

### Requirement: Damage Zone SkillEvent
V1 SHALL express circular and rectangular hit zones through real `damage_zone` SkillEvents.

#### Scenario: Emit damage zone event
- **WHEN** Skill Runtime executes a skill using `damage_zone`
- **THEN** it SHALL emit a `damage_zone` event containing `shape`, `origin`, `origin_world_position`, `facing_policy`, `facing_direction`, `facing_angle_deg`, `hit_at_ms`, `max_targets`, `damage_type`, `vfx_key`, and payload data

#### Scenario: Include circle geometry
- **WHEN** the emitted `damage_zone` event has `shape = circle`
- **THEN** its payload SHALL include `radius` and effective angle information of 360 degrees

#### Scenario: Include rectangle geometry
- **WHEN** the emitted `damage_zone` event has `shape = rectangle`
- **THEN** its payload SHALL include `length`, `width`, angle offset or equivalent angle field, and the runtime facing direction

#### Scenario: Timeline displays damage zone events
- **WHEN** SkillEvent timeline displays a damage zone skill run
- **THEN** it SHALL show `cast_start`, `damage_zone`, `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when present

#### Scenario: Timeline event fields
- **WHEN** SkillEvent timeline displays a `damage_zone` related event
- **THEN** it SHALL include `timestamp_ms`, `delay_ms`, `duration_ms`, `source_entity`, `target_entity`, `amount`, `damage_type`, `vfx_key`, `reason_key`, and `payload`

### Requirement: SkillEditor Damage Zone Module
SkillEditor SHALL expose one shared damage zone module for skills whose `behavior.template` is `damage_zone`.

#### Scenario: Show common damage zone fields
- **WHEN** SkillEditor opens a `damage_zone` Skill Package
- **THEN** it SHALL expose editable common fields for zone shape, origin policy, facing policy, hit timing, max targets, status chance scale, and VFX key

#### Scenario: Show circle fields
- **WHEN** SkillEditor edits a `damage_zone` package with `shape = circle`
- **THEN** it SHALL show `radius` and SHALL hide angle or show it read-only as 360 degrees

#### Scenario: Show rectangle fields
- **WHEN** SkillEditor edits a `damage_zone` package with `shape = rectangle`
- **THEN** it SHALL show `length`, `width`, and angle offset or equivalent angle field

#### Scenario: Save only whitelisted fields
- **WHEN** SkillEditor saves a `damage_zone` Skill Package
- **THEN** it SHALL validate through the skill schema and behavior-template whitelist and SHALL NOT write undeclared fields or frontend-only fake params

#### Scenario: Chinese validation errors
- **WHEN** SkillEditor rejects invalid `damage_zone` values
- **THEN** it SHALL display Chinese error text and SHALL NOT persist invalid skill data

### Requirement: WebApp Damage Zone Consumption
WebApp SHALL render damage zone visuals from `damage_zone` SkillEvent payloads.

#### Scenario: Render circle damage zone from event
- **WHEN** WebApp receives a `damage_zone` event with `shape = circle`
- **THEN** it SHALL render a circular damage zone using event-provided origin, radius, timing, and VFX key

#### Scenario: Render rectangle damage zone from event
- **WHEN** WebApp receives a `damage_zone` event with `shape = rectangle`
- **THEN** it SHALL render a rectangular ground spike line using event-provided origin, facing direction, length, width, angle, timing, and VFX key

#### Scenario: Do not guess damage zone behavior
- **WHEN** WebApp renders frost nova or ground spike
- **THEN** it SHALL NOT infer behavior from skill id, legacy skill template id, behavior type, visual effect name, or VFX key

#### Scenario: Render presentation events from events
- **WHEN** WebApp receives `damage`, `hit_vfx`, or `floating_text`
- **THEN** it SHALL render damage, hit effects, and floating text from those events rather than from static fake events

### Requirement: Damage Zone Test Arena Acceptance
Skill Test Arena SHALL validate both circular frost nova and rectangular ground spike using real SkillEvents.

#### Scenario: Validate circle radius behavior
- **WHEN** Skill Test Arena runs `active_frost_nova`
- **THEN** it SHALL verify circular in-radius targets are hit, out-of-radius targets are not hit, and changing `radius` changes hit coverage

#### Scenario: Validate rectangle length behavior
- **WHEN** Skill Test Arena runs ground spike
- **THEN** it SHALL verify targets within rectangle length are hit, targets beyond length are not hit, and changing `length` changes hit coverage

#### Scenario: Validate rectangle width behavior
- **WHEN** Skill Test Arena runs ground spike
- **THEN** it SHALL verify targets within rectangle width are hit, targets outside width are not hit, and changing `width` changes lateral hit coverage

#### Scenario: Validate rectangle angle behavior
- **WHEN** Skill Test Arena runs ground spike
- **THEN** it SHALL verify changing angle offset or equivalent angle field changes the rectangle hit direction

#### Scenario: Validate damage timing
- **WHEN** Skill Test Arena observes a `damage_zone` skill before `hit_at_ms`
- **THEN** it SHALL verify target life is unchanged until `damage` events occur at or after `hit_at_ms`

#### Scenario: Validate modifier stack effect
- **WHEN** Skill Test Arena runs a `damage_zone` skill with the test Modifier Stack
- **THEN** the stack SHALL affect final damage, zone geometry, or status chance runtime parameters used by actual SkillEvents without writing production inventory, gem instances, or Skill Package data

### Requirement: Damage Zone AI Self-Test Report
The AI self-test report SHALL evaluate `damage_zone` skills from real Skill Test Arena results.

#### Scenario: Report frost nova circle checks
- **WHEN** an AI self-test report is generated for `active_frost_nova`
- **THEN** it SHALL check for `damage_zone`, `shape = circle`, circle origin, radius hit coverage, damage timing, cold damage, hit VFX, floating text, and radius parameter effects

#### Scenario: Report ground spike rectangle checks
- **WHEN** an AI self-test report is generated for ground spike
- **THEN** it SHALL check for `damage_zone`, `shape = rectangle`, origin, facing toward locked or nearest target, length/width/angle hit coverage, damage timing, physical damage, hit VFX, floating text, and geometry parameter effects

#### Scenario: Report Chinese conclusion and fixes
- **WHEN** a `damage_zone` AI self-test report finishes evaluation
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes
