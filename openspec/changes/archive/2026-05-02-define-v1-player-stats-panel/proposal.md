## Why

The left character panel currently mixes a few real values with many hardcoded placeholder labels, icons, and numbers, so it cannot be trusted as a true character stat view. The V1 stat design document now establishes the authoritative player stat dictionary and needs to be reflected in configuration, validation, runtime exposure, and the configurable left-side UI.

## What Changes

- Expand the player stat dictionary from the current minimal set into the V1-defined character stat set, with explicit `v1_status`, `runtime_effective`, and `affix_spawn_enabled_v1` metadata.
- Correct and clean the V1 player-stat scope: `pickup_radius`, `active_skill_slots`, `passive_skill_slots`, and legacy `skill_slots_active` SHALL NOT exist as player stats after this change.
- Keep non-effective and future stats definable for display or reservation while preventing them from affecting V1 runtime or random affix generation.
- Add a configuration-driven left character panel model so panel groups, order, icons, labels, formatting, and bound stat values can be adjusted without hardcoding display rows in the frontend.
- Expose real calculated player stat values through the backend state API for the left character panel, including base values and V1-active contributions.
- Replace hardcoded left-panel placeholder values with configured entries backed by real stat values or explicitly display-only/reserved values.
- Add validation so player stat definitions, base values, localization keys, panel bindings, and V1 affix-spawn flags stay consistent.
- Remove obsolete stat references from configuration, validation, API serialization, tests, and UI data contracts instead of leaving unused aliases.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: Update V1 player stat requirements, runtime scope, affix-generation limits, and WebApp character panel presentation requirements.

## Impact

- Affected configuration: `configs/player/player_stat_defs.toml`, `configs/player/player_base_stats.toml`, new left character panel display configuration, and `configs/localization/zh_cn.toml`.
- Affected backend: config loading/validation, player stat calculation, API state serialization, and affix validation rules.
- Affected frontend: `CharacterInfoPanel` in `webapp/App.tsx` and related styles/types so the left panel renders configured stat entries from real API state.
- Affected tests: config validation tests, skill/stat calculation tests, API state tests, and WebApp smoke or component-level checks for configured character panel rendering.
