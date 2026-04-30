## Why

Current projectile VFX fades across the whole flight lifetime, so long-range or slow projectiles can become nearly invisible before reaching their runtime destroy condition. Projectile visuals should stay readable while the runtime projectile exists, loop their in-flight frames, and only fade after the projectile reaches hit or expiry.

## What Changes

- Keep projectile body VFX visible during the runtime projectile lifetime instead of tying body opacity to remaining travel time.
- Loop the projectile in-flight frame segment for as long as the runtime projectile remains active.
- Add a short visual exit/fade phase after the projectile reaches its hit or max-distance expiry condition.
- Preserve runtime projectile data as the source of truth for spawn position, direction, current position, hit position, max-distance expiry, and projectile identity.
- Ensure hit VFX remains triggered by runtime `hit_vfx` events, not by presentation code guessing hits.
- Add focused verification for long-flight projectiles so body VFX remains visible until the destroy transition.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: Update projectile presentation requirements so projectile body VFX loops and remains visible until runtime hit or expiry, then fades out.

## Impact

- Affected implementation scope should be limited to WebApp projectile presentation and tests:
  - `webapp/App.tsx`
  - `webapp/smoke-test.mjs` or another existing focused WebApp test if more appropriate
  - `tests/test_skill_runtime.py` only if existing runtime event payload assertions need to cover already-emitted lifetime/expiry fields
- Runtime projectile logic, combat damage, hit selection, cooldowns, skill balance values, skill YAML content, VFX PNG assets, and non-projectile skills should not change.
