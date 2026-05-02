## ADDED Requirements

### Requirement: Authored encounter aggro runtime
V1 WebApp battle runtime SHALL use authored encounter aggro ranges to trigger group-wide enemy aggression.

#### Scenario: Trigger monster point aggro
- **WHEN** the player enters a monster spawn point's authored aggro range during battle
- **THEN** every living enemy spawned from that monster spawn point SHALL lock onto the player

#### Scenario: Trigger boss group aggro
- **WHEN** the player enters a chosen boss group's authored aggro range during battle
- **THEN** every living boss spawned from that boss group SHALL lock onto the player

#### Scenario: Aggro persists after leaving range
- **WHEN** an enemy has locked onto the player because its authored encounter source was triggered
- **THEN** that enemy SHALL continue pursuing the player until death or battle reset even if the player leaves the original aggro range

#### Scenario: Untriggered distant enemies stay lightweight
- **WHEN** authored enemies have not been triggered and are far from the player and camera
- **THEN** runtime SHALL keep them as lightweight records without full per-frame AI or DOM rendering

### Requirement: Authored encounter random count multiplier runtime
V1 WebApp battle runtime SHALL apply authored monster count multiplier ranges when initializing monster spawn points.

#### Scenario: Roll actual monster count
- **WHEN** a battle starts on a map with a monster spawn point that defines a count multiplier interval
- **THEN** runtime SHALL calculate that point's actual monster count as `floor(configured count * random(min, max))`

#### Scenario: Decimal multipliers are supported
- **WHEN** a monster spawn point defines decimal multiplier bounds
- **THEN** runtime SHALL use those decimal values when rolling the actual monster count

#### Scenario: Default multiplier preserves existing maps
- **WHEN** a monster spawn point has no multiplier interval fields
- **THEN** runtime SHALL treat the interval as `[1, 1]` and preserve the existing configured count behavior

#### Scenario: Boss explicit counts are preserved
- **WHEN** a battle starts with an authored boss group
- **THEN** runtime SHALL spawn bosses according to the chosen boss group's explicit boss count and boss selections rather than applying the monster count multiplier

### Requirement: Authored encounter start presence
V1 WebApp battle runtime SHALL keep authored enemies logically present from battle start while avoiding close-range pop-in and frame drops.

#### Scenario: Initialize authored enemies at battle start
- **WHEN** a battle starts on a map with authored monster spawn points or boss groups
- **THEN** runtime SHALL create enemy records for the rolled authored encounter enemies at battle start

#### Scenario: Visible untriggered enemies can render before aggro
- **WHEN** an untriggered authored enemy is inside or near the current camera view
- **THEN** runtime SHALL allow that enemy to render as present without requiring it to start chasing the player

#### Scenario: Distant authored enemies avoid render cost
- **WHEN** authored enemies are outside the visible or near-visible area
- **THEN** runtime SHALL avoid rendering individual DOM nodes for those enemies

#### Scenario: Performance optimizations preserve encounter logic
- **WHEN** authored enemies move between dormant, visible, triggered, active, or dead runtime states
- **THEN** enemy HP, death, drops, skill targeting, damage results, and aggro lock state SHALL remain consistent with the enemies logically present on the map
