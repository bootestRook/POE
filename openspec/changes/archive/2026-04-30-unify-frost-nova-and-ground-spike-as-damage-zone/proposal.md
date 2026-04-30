## Why

`active_frost_nova` and the planned replacement for `active_puncture` are both non-projectile skills whose real behavior is a damage settlement area / hit zone. Keeping one as `player_nova` and the other as `melee_arc` splits the same semantic concept into separate editor, runtime, timeline, and report modules.

This change unifies those skills under a declarative `damage_zone` model, and changes `active_puncture` / `穿刺` into `地刺`: a rectangular line of ground spikes fired toward the locked or nearest enemy direction.

## What Changes

- Introduce a `damage_zone` behavior template for area-based damage settlement.
- Migrate `active_frost_nova` from `player_nova` semantics to `damage_zone` with `shape = circle`.
- Rework `active_puncture` player behavior into `地刺`, using `damage_zone` with `shape = rectangle`.
- Replace the prior puncture `melee_arc` target behavior with a rectangular hit zone:
  - origin from player or cast source;
  - direction toward locked target or nearest target;
  - rectangle geometry defined by length, width, and angle offset;
  - damage only through delayed `damage` SkillEvents.
- Update SkillEditor so one "damage zone" module edits the common fields and conditionally shows:
  - circle fields: radius, angle display fixed or hidden as 360 degrees;
  - rectangle fields: length, width, angle;
  - shared fields: hit timing, max targets, facing policy, status chance scale, VFX key.
- Update SkillRuntime, Skill Test Arena, SkillEvent timeline, WebApp rendering, and AI self-test report to consume `damage_zone` events rather than separate nova and melee-specific behavior paths.
- Preserve projectile skills and already migrated projectile behavior.
- Do not migrate `active_lightning_chain`, `active_lava_orb`, or `active_fungal_petards`.
- Do not introduce a node editor, script DSL, expression interpreter, frontend-only fake behavior params, or static fake events.
- Do not restore random affix UI or random affix generation.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: Add `damage_zone` behavior semantics for circular and rectangular damage settlement areas, migrate frost nova and puncture/ground spike to that model, and update editor/runtime/test/timeline/report requirements.

## Impact

- Skill config/schema:
  - `configs/skills/behavior_templates/damage_zone.yaml`
  - `configs/skills/active/active_frost_nova/skill.yaml`
  - `configs/skills/active/active_puncture/skill.yaml`
  - `configs/skills/schema/skill.schema.json`
  - `configs/localization/zh_cn.toml`
- Python runtime and tooling:
  - `src/liufang/config.py`
  - `src/liufang/skill_effects.py`
  - `src/liufang/skill_runtime.py`
  - `src/liufang/skill_editor.py`
  - `src/liufang/skill_test_report.py`
  - `tools/validate_v1_configs.py`
  - `tools/generate_skill_test_report.py`
  - `tools/webapp_server.py`
- WebApp:
  - `webapp/App.tsx`
  - `webapp/styles.css`
  - `webapp/smoke-test.mjs`
- Tests:
  - runtime, editor, effects/config validation, combat regression, AI report, and WebApp smoke tests.
