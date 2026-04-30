## ADDED Requirements

### Requirement: Projectile Body VFX Stays Visible Until Runtime Destroy
WebApp projectile presentation SHALL keep projectile body VFX visible while the runtime projectile is alive, loop the in-flight body frames during that lifetime, and fade the body only after the runtime projectile reaches hit-driven destruction or max-distance expiry.

#### Scenario: Long flight keeps projectile body visible
- **WHEN** WebApp renders a `projectile_spawn` event whose runtime lifetime is longer than the projectile body sprite sheet duration
- **THEN** the projectile body VFX SHALL remain visible during the runtime lifetime and SHALL loop its in-flight frames instead of fading out across the full flight

#### Scenario: Projectile body follows runtime position during flight
- **WHEN** a projectile body VFX is rendered before the runtime lifetime has ended
- **THEN** its current visual position SHALL be derived from the runtime spawn position, direction, velocity or end position, and event lifetime data from the `projectile_spawn` event

#### Scenario: Projectile body fades only after runtime expiry
- **WHEN** the runtime projectile reaches the expiry time or end position supplied by the `projectile_spawn` event
- **THEN** the projectile body VFX SHALL enter a short visual fade-out phase and SHALL NOT start that fade earlier during normal flight

#### Scenario: Hit impact remains event driven
- **WHEN** a projectile hits a target and Skill Runtime emits `projectile_hit` and `hit_vfx` events
- **THEN** WebApp SHALL render impact VFX from the `hit_vfx` event and SHALL NOT infer or trigger impact VFX from the projectile body fade transition

#### Scenario: Projectile logic and combat values are unchanged
- **WHEN** this presentation behavior is applied
- **THEN** projectile speed, max distance, collision, pierce, target selection, damage, cooldown, skill YAML values, and runtime hit rules SHALL remain unchanged

#### Scenario: Multi-projectile bodies fade independently
- **WHEN** a skill emits multiple `projectile_spawn` events for a fan or burst projectile skill
- **THEN** each projectile body VFX SHALL loop, remain visible, reach expiry, and fade independently according to its own runtime event identity and lifetime data
