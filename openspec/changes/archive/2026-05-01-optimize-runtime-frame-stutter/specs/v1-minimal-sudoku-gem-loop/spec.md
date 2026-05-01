## ADDED Requirements

### Requirement: WebApp Runtime Performance Observability
V1 WebApp SHALL provide low-overhead runtime performance observability for battle and SkillEditor test-arena runtime without changing gameplay behavior.

#### Scenario: Record frame performance summary
- **WHEN** WebApp runtime is playing
- **THEN** it SHALL record recent frame time, logic step time, active visual object counts, scheduled SkillEvent count, consumed SkillEvent count, and dropped-frame count

#### Scenario: Performance observability does not cause high-frequency UI renders
- **WHEN** performance data is updated every animation frame
- **THEN** high-frequency samples SHALL be stored outside React state, and any visible summary SHALL update at a lower frequency

#### Scenario: Show Chinese performance summary in development context
- **WHEN** the SkillEditor or development runtime performance summary is visible
- **THEN** all visible labels and warnings SHALL be Chinese

### Requirement: Batched SkillEvent Consumption
WebApp runtime SHALL consume same-frame SkillEvents in batches to reduce React state churn while preserving event order and gameplay results.

#### Scenario: Consume ready scheduled events as an ordered batch
- **WHEN** multiple scheduled SkillEvents become ready in the same animation frame
- **THEN** WebApp SHALL collect them in existing timeline order and consume them through a batch path

#### Scenario: Batch projectile visual updates
- **WHEN** a batch contains multiple `projectile_spawn` events
- **THEN** WebApp SHALL append their projectile body visuals with a single state update for that visual collection

#### Scenario: Batch impact and floating text visual updates
- **WHEN** a batch contains multiple `projectile_impact`, `hit_vfx`, or `floating_text` events
- **THEN** WebApp SHALL append their corresponding visual objects with batched state updates

#### Scenario: Batch damage application without changing results
- **WHEN** a batch contains multiple `damage` events
- **THEN** WebApp SHALL apply all damage events in event order and produce the same enemy HP, death count, and combat log result as individual consumption

#### Scenario: Preserve SkillEvent semantics
- **WHEN** SkillEvent batching is enabled
- **THEN** event count, event ordering, event payloads, damage timing, target selection, projectile lifetime, cooldown behavior, and visible SkillEvent timeline data SHALL remain unchanged

### Requirement: Runtime Visual Object Budget
WebApp runtime SHALL cap front-end-only visual object counts to avoid DOM growth causing frame drops without dropping logic events.

#### Scenario: Cap projectile and impact visuals
- **WHEN** active projectile bodies or impact VFX exceed the configured visual budget
- **THEN** WebApp SHALL remove older or near-expired visual objects while keeping underlying SkillEvents and damage results intact

#### Scenario: Cap floating text visuals
- **WHEN** active floating text objects exceed the configured visual budget
- **THEN** WebApp SHALL remove older or near-expired floating text objects without changing damage events or enemy HP

#### Scenario: Cap area, chain, and melee visuals
- **WHEN** active area, chain, damage-zone, or melee-arc visual objects exceed the configured visual budget
- **THEN** WebApp SHALL limit only front-end presentation objects and SHALL NOT alter Skill Runtime output

#### Scenario: Do not use budget for gameplay logic
- **WHEN** visual budgets are applied
- **THEN** budgets SHALL NOT be used to skip SkillEvent generation, target selection, damage calculation, cooldown updates, enemy HP updates, or test-arena results

### Requirement: SkillEditor Debug Layer Performance
SkillEditor runtime debug layers SHALL avoid excessive render and layout work while preserving projectile and damage-zone debugging visibility.

#### Scenario: Render debug layers only when relevant
- **WHEN** SkillEditor debug options are disabled or the user is outside SkillEditor debug context
- **THEN** launch points, target points, direction lines, collision radii, and search ranges SHALL NOT render unnecessary DOM nodes

#### Scenario: Reuse projected guide calculations
- **WHEN** debug guide positions are rendered for projectile, chain, melee, or damage-zone previews
- **THEN** WebApp SHALL reuse or memoize world-to-screen projection results where practical instead of recalculating equivalent guide positions repeatedly during the same render

#### Scenario: Limit event timeline rendering cost
- **WHEN** SkillEditor test-arena event timeline contains many events
- **THEN** the timeline SHALL limit initially rendered rows or keep large payload text collapsed until needed, while still allowing the user to inspect the real event details

#### Scenario: Preserve debug correctness
- **WHEN** debug-layer optimizations are applied
- **THEN** launch point, target point, direction line, collision radius, search range, and event payload displays SHALL remain derived from SkillEvent data or current editor draft data

### Requirement: Runtime Optimization Scope Guard
Runtime performance optimization SHALL NOT change formal runtime rules, skill configuration, or unrelated V1 systems.

#### Scenario: Do not change Skill Runtime behavior
- **WHEN** this change is applied
- **THEN** `src/liufang/skill_runtime.py` behavior semantics, event ordering, damage timing, projectile trajectories, target selection, cooldown events, and payload meanings SHALL remain unchanged

#### Scenario: Do not change formal skill configuration
- **WHEN** this change is applied
- **THEN** formal `configs/skills/**` values, skill schema, behavior template whitelist, and saved `skill.yaml` contents SHALL remain unchanged unless a later explicit change requests it

#### Scenario: Do not affect non-runtime systems
- **WHEN** this change is applied
- **THEN** gem board, sudoku legality, loot, affixes, inventory, localization content, and formal combat module behavior SHALL remain unchanged

#### Scenario: Build and tests pass
- **WHEN** runtime performance optimization is complete
- **THEN** WebApp build, WebApp smoke test, and relevant Python runtime tests SHALL pass
