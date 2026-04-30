## Context

Projectile skills already emit `projectile_spawn`, `projectile_hit`, `damage`, `hit_vfx`, and `floating_text` events. The projectile spawn event carries runtime-authored spawn position, direction, velocity, lifetime, expiry time, and expiry/end position data.

The current WebApp projectile renderer uses the projectile event duration both for travel progress and body opacity. This makes the projectile body and trail fade continuously during normal flight. For long-distance or slow projectiles, the body can become visually unreadable before the runtime projectile reaches its hit or expiry condition, even though the frame animation itself already loops.

## Goals / Non-Goals

**Goals:**

- Keep projectile body VFX readable while the runtime projectile is alive.
- Continue looping in-flight projectile frames during the alive phase.
- Add a short fade-out phase only after hit or max-distance expiry.
- Preserve runtime projectile data as the single source of truth for position, direction, lifetime, hit, and expiry.
- Keep hit and impact presentation driven by runtime `hit_vfx` events.
- Add focused verification for long-flight projectile visibility.

**Non-Goals:**

- Do not change projectile speed, max distance, collision, hit policy, pierce, damage, cooldown, or target selection.
- Do not add new VFX PNG frames or regenerate VFX assets.
- Do not add skill YAML fields unless a later change explicitly needs configurable fade duration.
- Do not make WebApp infer hits or expiry from target positions independently of runtime event data.
- Do not refactor unrelated area, melee, damage-zone, inventory, board, loot, or combat systems.

## Decisions

### Separate Alive Visual State From Exit Fade State

Projectile body VFX SHALL have two presentation phases:

- Alive phase: from `projectile_spawn` until runtime lifetime/end position is reached.
- Exit phase: a short visual-only fade after the alive phase ends.

Rationale: the runtime projectile's lifetime already expresses how long the projectile exists. Body opacity should not encode travel progress. Travel progress should continue to control world position only.

Alternative considered: extend the sprite sheet with more frames. This would only hide the symptom for some distances and would still fade if opacity remains tied to travel lifetime.

### Keep Runtime Event Data Authoritative

The WebApp SHALL use `projectile_spawn.duration_ms`, payload `lifetime_ms`, `end_position`, and `expire_world_position` when available to determine the alive phase and final visual point.

Rationale: this follows the projectile VFX standard. The renderer should consume runtime data, not derive independent projectile logic.

Alternative considered: calculate fade start from current target distance in the WebApp. That risks diverging from runtime pierce, fan, max-distance, and future projectile rules.

### Loop Body Frames Independently From Fade

Projectile body frame selection SHALL continue looping during alive and exit phases. The fade phase may keep looping or hold a frame, but it MUST NOT make the projectile body vanish during normal alive flight.

Rationale: existing 4-frame projectile-loop sheets are designed as loopable in-flight assets, not one-shot lifetime assets.

### Leave Impact VFX Event-Driven

`hit_vfx` SHALL remain the only source for hit/impact burst visuals. The projectile body exit fade is only a disappearance transition for the body layer.

Rationale: impact timing and position belong to runtime events. Presentation fade should not create a second hit interpretation.

## Risks / Trade-offs

- Risk: keeping body opacity constant can make very long projectiles visually persistent after a hit event for piercing skills. Mitigation: keep one body instance per runtime projectile and end it only at runtime expiry, while impact bursts remain separate per hit event.
- Risk: adding a fade phase by extending local TTL could desync data attributes that report current projectile position. Mitigation: lock current position to `end_position` / `expire_world_position` during exit fade and keep runtime identity fields unchanged.
- Risk: tests might only validate event creation, not visual lifetime. Mitigation: add a WebApp-focused check that advances a long-flight projectile past the sprite sheet frame duration and confirms the projectile body is still rendered with visible opacity before expiry.
