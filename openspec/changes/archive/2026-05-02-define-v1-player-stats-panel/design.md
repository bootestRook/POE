## Context

The project currently has a small `configs/player/player_stat_defs.toml` and `player_base_stats.toml` set that only partially overlaps the V1 stat design document. The left character panel in `webapp/App.tsx` reads real values for `max_life` and `move_speed`, but most labels, icons, groups, and numbers are hardcoded placeholders.

The V1 stat design document establishes a broader dictionary with status metadata: V1-active stats may affect runtime and affix generation, display-only stats may appear without affecting combat, reserved stats may exist but must not spawn as random affixes, and V2+ stats stay outside V1 content. The user clarified that pickup range and active/passive skill slot stats do not exist in this version and must be cleaned up rather than retained as unused fields.

## Goals / Non-Goals

**Goals:**

- Make the player stat dictionary authoritative, status-tagged, and validated.
- Remove obsolete player stat entries and references for `pickup_radius`, `active_skill_slots`, `passive_skill_slots`, and `skill_slots_active`.
- Keep V1 runtime strict: only stats marked runtime-effective may affect combat, skill calculation, or random affix generation.
- Make the left character panel configuration-driven for groups, ordering, icons, labels, formatting, and stat bindings.
- Ensure the left character panel reads real backend stat values rather than hardcoded gameplay-looking placeholders.
- Preserve display-only and reserved stats as visible configuration concepts without accidentally making them effective.

**Non-Goals:**

- Do not implement pickup range, active/passive skill slot stats, character classes, or attribute growth.
- Do not implement full mana, armor, evasion, resistance, energy shield, minion, trap, conversion, or V2+ systems.
- Do not make the frontend calculate player stat totals independently from backend/runtime rules.
- Do not generate random affixes for display-only, reserved, or V2+ stats.

## Decisions

1. **Use one authoritative stat definition table with V1 metadata.**

   `player_stat_defs.toml` remains the canonical stat dictionary, but each stat gains explicit metadata such as `v1_status`, `runtime_effective`, and `affix_spawn_enabled_v1`. This is preferable to splitting active and inactive stats across multiple files because validation can reason about all defined stats in one place and prevent accidental affix/runtime leakage.

2. **Keep base values separate from display layout.**

   `player_base_stats.toml` stores numeric defaults for defined player stats. A separate left-panel display configuration stores presentation concerns such as group, order, icon, label key, value formatting, and `stat_id` binding. This keeps stat math stable while letting the panel be tuned without editing React constants.

3. **Backend owns stat calculation and panel data shaping.**

   The API should return both calculated stat values and a panel-ready view model. The frontend renders that model and does not infer hidden meanings from stat ids except for narrowly necessary runtime integrations such as movement speed already used by battle movement.

4. **Obsolete stats are removed, not aliased.**

   `skill_slots_active` and the clarified non-existent pickup/slot stats should fail validation if referenced after the change. Aliases would reduce migration friction but risk silently preserving the exact ambiguity this change is meant to remove.

5. **Affix validation uses V1 status gates.**

   Random affix definitions and spawn pools must only reference stats whose definition permits V1 affix spawning. This catches the case where a stat is visible or reserved but would mislead players if rolled as a random affix.

## Risks / Trade-offs

- **Risk: Large stat dictionary creates noisy UI.** -> Mitigation: The left panel uses display configuration, so only selected groups and rows render in the main character panel.
- **Risk: Reserved stats look effective to players.** -> Mitigation: Display config must be explicit, and reserved/display-only stats must not be marked runtime-effective or affix-spawn-enabled.
- **Risk: Existing tests or code still reference `skill_slots_active`.** -> Mitigation: Add validation/tests that fail on obsolete stat ids, then update callers instead of preserving aliases.
- **Risk: Frontend and backend view models drift.** -> Mitigation: Type the `player_stats` and character panel payload broadly by stat id and add smoke coverage for rendered configured values.

## Migration Plan

1. Update stat definitions and base values to match the V1 scoped dictionary, excluding clarified non-existent pickup and active/passive slot stats.
2. Remove `skill_slots_active` from configs, API typing, tests, and any UI references.
3. Add panel display configuration and localization keys for panel rows/icons/groups.
4. Load and validate stat definitions, base values, panel bindings, localization references, and affix spawn eligibility together.
5. Update backend state serialization to expose calculated stat values and configured left-panel sections.
6. Update `CharacterInfoPanel` to render the panel payload and remove hardcoded placeholder rows.
7. Run Python tests, config validation, WebApp build, and smoke checks.

## Open Questions

- Whether `support_link_limit` should be treated as a player stat or moved into board/rules configuration later. For this proposal it remains in scope because only pickup range and active/passive slot stats were clarified as non-existent.
