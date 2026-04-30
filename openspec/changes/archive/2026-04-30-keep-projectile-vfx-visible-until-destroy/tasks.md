## 1. Inspect Current Projectile Presentation

- [x] 1.1 Inspect `webapp/App.tsx` projectile VFX state, TTL updates, travel progress, body opacity, trail opacity, and sprite-frame looping.
- [x] 1.2 Verify how `projectile_spawn` payload fields such as `lifetime_ms`, `expire_time_ms`, `expire_world_position`, and `end_position` are currently consumed.
- [x] 1.3 Confirm existing runtime tests already cover projectile lifetime and expiry payloads, and identify whether any assertion needs to be added.

## 2. Implement Alive And Fade Presentation Phases

- [x] 2.1 Extend the WebApp projectile VFX state to distinguish runtime alive duration from visual exit fade duration without changing runtime combat data.
- [x] 2.2 Update projectile TTL decrement/removal so body VFX stays mounted through alive duration plus the short exit fade phase.
- [x] 2.3 Update projectile body opacity so it remains visible during the alive phase and only fades during the exit phase.
- [x] 2.4 Keep projectile body frame selection looping during the alive phase and avoid one-shot playback semantics for projectile loop sheets.
- [x] 2.5 Lock or clamp projectile position to the runtime end/expiry position during exit fade.
- [x] 2.6 Keep trail visibility consistent with the body during alive flight, while allowing the trail to fade during the exit phase.

## 3. Preserve Runtime Authority

- [x] 3.1 Ensure projectile VFX direction continues to use runtime velocity first and runtime direction as fallback.
- [x] 3.2 Ensure body VFX position continues to derive from runtime spawn/end/lifetime data and does not recalculate hit or target logic.
- [x] 3.3 Ensure impact VFX remains driven only by `hit_vfx` events and is not triggered by body fade completion.
- [x] 3.4 Verify no skill YAML, projectile speed, max distance, collision, hit policy, damage, cooldown, or target selection values are changed.

## 4. Verification

- [x] 4.1 Add or update a focused WebApp test/smoke check for a long-flight projectile whose sprite-loop duration is shorter than runtime lifetime.
- [x] 4.2 Verify the long-flight projectile body remains visible after the first sprite-loop cycle and before runtime expiry.
- [x] 4.3 Verify the body enters fade only after runtime expiry and is removed after fade completion.
- [x] 4.4 Verify multi-projectile skills keep independent projectile body instances through their own lifetime/fade phases.
- [x] 4.5 Run `npm run build`.
- [x] 4.6 Run relevant existing tests for skill runtime and WebApp smoke coverage. `python -m unittest tests.test_skill_runtime` passed; `npm.cmd test` ran and failed on pre-existing unit animation manifest/frame-count state outside this change.
