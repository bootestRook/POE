## ADDED Requirements

### Requirement: SkillEditor projectile launch point direct adjustment
SkillEditor SHALL provide a direct scene adjustment flow for editable projectile launch positions that updates the current draft `behavior.params.spawn_offset` without bypassing existing save validation.

#### Scenario: Enter direct adjustment from launch position section
- **WHEN** the user opens an editable Skill Package whose behavior template supports persisted `spawn_offset`
- **THEN** the "发射位置" section SHALL provide a Chinese "直接调整" action that enters scene adjustment mode

#### Scenario: Ice shards uses generic projectile spread
- **WHEN** `active_ice_shards` is editable in SkillEditor
- **THEN** it SHALL use the generic `projectile` behavior template with projectile count and spread-angle params rather than requiring a separate fan-projectile template

#### Scenario: Hide editor shell during adjustment
- **WHEN** scene adjustment mode is active
- **THEN** the full SkillEditor panel SHALL be temporarily hidden while the editor draft remains mounted and available

#### Scenario: Drag launch point in battle scene
- **WHEN** the user drags the launch-point handle in the battle scene
- **THEN** SkillEditor SHALL convert the dragged scene position into `behavior.params.spawn_offset.x` and `behavior.params.spawn_offset.y` relative to the current cast source in the editor draft

#### Scenario: Confirm adjusted position
- **WHEN** the user confirms the adjusted launch position
- **THEN** SkillEditor SHALL return to the full editor panel with the numeric launch offset fields and read-only launch-point preview reflecting the adjusted draft value

#### Scenario: Cancel adjusted position
- **WHEN** the user cancels scene adjustment mode
- **THEN** SkillEditor SHALL restore the launch offset values that existed before entering adjustment mode and return to the full editor panel

#### Scenario: Save still uses existing validation
- **WHEN** the user saves after confirming a directly adjusted launch position
- **THEN** SkillEditor SHALL use the existing save flow, schema validation, and behavior-template whitelist before writing the Skill Package

#### Scenario: Do not expose unsupported templates
- **WHEN** the current Skill Package behavior template does not allow persisted `spawn_offset`
- **THEN** SkillEditor SHALL NOT enable direct launch-position adjustment for that package

#### Scenario: No runtime behavior change
- **WHEN** Skill Runtime executes a projectile skill after this editor change is applied
- **THEN** projectile spawning, targeting, trajectory, damage, and SkillEvent semantics SHALL remain determined by existing runtime logic and the saved `spawn_offset` value
