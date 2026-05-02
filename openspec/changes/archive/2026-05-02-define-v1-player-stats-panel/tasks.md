## 1. Stat Scope And Configuration

- [x] 1.1 Expand `configs/player/player_stat_defs.toml` with V1 status metadata, runtime effectiveness, affix-spawn eligibility, categories, value types, and localization keys for the scoped V1 player stat dictionary.
- [x] 1.2 Update `configs/player/player_base_stats.toml` so every required runtime-effective stat has a default value and every key references an existing stat definition.
- [x] 1.3 Remove `pickup_radius`, `active_skill_slots`, `passive_skill_slots`, and `skill_slots_active` from player stat definitions, base values, tests, API contracts, and UI contracts.
- [x] 1.4 Add or update Chinese localization keys for all player stats and left character panel labels that will be visible in V1.

## 2. Validation And Affix Gates

- [x] 2.1 Extend config loading/validation to require player stat `v1_status`, `runtime_effective`, and `affix_spawn_enabled_v1`.
- [x] 2.2 Validate that non-`V1_ACTIVE` stats cannot set `affix_spawn_enabled_v1 = true`.
- [x] 2.3 Validate that random affix definitions and spawn pools only reference stats with V1 affix spawning enabled.
- [x] 2.4 Add validation failures for obsolete player stat ids: `pickup_radius`, `active_skill_slots`, `passive_skill_slots`, and `skill_slots_active`.

## 3. Player Stat Calculation And API

- [x] 3.1 Update backend player stat calculation to initialize from configured base stats and apply only runtime-effective V1 contributions.
- [x] 3.2 Update passive/self-stat contribution handling to work with the expanded stat dictionary without applying display-only or reserved stats.
- [x] 3.3 Update API state serialization so `player_stats` exposes calculated stat values, labels, value types, categories, and V1 status needed by the WebApp.
- [x] 3.4 Remove hardcoded API serialization limited to `max_life` and `move_speed`.

## 4. Left Character Panel Configuration

- [x] 4.1 Add a left character panel display configuration under `configs/player/` that defines panel groups, order, icons, labels, formatters, and bound `stat_id` values.
- [x] 4.2 Validate that each panel row binds to an existing non-obsolete stat id and references existing Chinese localization keys.
- [x] 4.3 Add backend view-model shaping for the configured left character panel sections and rows.

## 5. WebApp Rendering

- [x] 5.1 Update `AppState` types to accept the expanded player stat payload and configured left character panel sections.
- [x] 5.2 Replace `CharacterInfoPanel` hardcoded core cards, attributes, resistance rows, and detail groups with rendering from the configured panel payload.
- [x] 5.3 Preserve current runtime uses of real stats such as `max_life` and `move_speed` while avoiding frontend-only stat total calculations.
- [x] 5.4 Adjust CSS only as needed so configured panel rows remain readable in the existing left-panel layout.

## 6. Verification

- [x] 6.1 Add or update Python tests for stat definition coverage, obsolete stat cleanup, base stat consistency, and affix spawn eligibility.
- [x] 6.2 Add or update API tests proving the state payload includes configured real player stats and panel sections.
- [x] 6.3 Add or update WebApp smoke coverage for the left character panel rendering configured values instead of hardcoded placeholders.
- [x] 6.4 Run config validation, relevant Python tests, WebApp build, and WebApp smoke test.
