## MODIFIED Requirements

### Requirement: 玩家属性定义

V1 SHALL define the player stats required for character display, combat, skill calculation, gem affixes, and sudoku-board stat routing, with explicit V1 status metadata that prevents non-effective stats from affecting runtime.

#### Scenario: 属性定义包含状态元数据
- **WHEN** `player_stat_defs.toml` is validated
- **THEN** every stat SHALL declare an id, Chinese localization key, category, value type, `v1_status`, `runtime_effective`, and `affix_spawn_enabled_v1`

#### Scenario: V1 生效属性集合完整
- **WHEN** `player_stat_defs.toml` is validated for V1 runtime-effective stats
- **THEN** it SHALL include `max_life`, `current_life`, `move_speed`, `support_link_limit`, `damage_add_percent`, `damage_final_percent`, `hit_damage_add_percent`, `hit_damage_final_percent`, `physical_damage_add_percent`, `fire_damage_add_percent`, `cold_damage_add_percent`, `lightning_damage_add_percent`, `elemental_damage_add_percent`, `attack_damage_add_percent`, `spell_damage_add_percent`, `melee_damage_add_percent`, `ranged_damage_add_percent`, `projectile_damage_add_percent`, `area_damage_add_percent`, `attack_speed_add_percent`, `cast_speed_add_percent`, `skill_speed_final_percent`, `cooldown_reduction_percent`, `added_cooldown_ms`, `projectile_speed_add_percent`, `base_crit_chance_percent`, `crit_chance_add_percent`, `crit_damage_add_percent`, `cannot_crit`, `area_add_percent`, `projectile_count_add`, `chain_count_add`, `pierce_count_add`, `status_chance_add_percent`, `active_gem_level_add`, `gem_level`, `source_power_row`, `source_power_column`, `source_power_box`, `target_power_row`, `target_power_column`, `target_power_box`, `conduit_power_row`, `conduit_power_column`, and `conduit_power_box`

#### Scenario: 多余玩家属性被清理
- **WHEN** player stat definitions, base stats, API state, UI type contracts, tests, or validation rules are inspected
- **THEN** they SHALL NOT define or reference `pickup_radius`, `active_skill_slots`, `passive_skill_slots`, or `skill_slots_active` as player stats

#### Scenario: V1 外属性可定义但不可误生效
- **WHEN** a stat has `v1_status` equal to `V1_DISPLAY_ONLY`, `V1_RESERVED`, or `V2_PLUS`
- **THEN** runtime calculation SHALL NOT apply it to combat, skill results, movement, drops, or board routing unless a later spec changes that status

#### Scenario: 基础值与属性定义一致
- **WHEN** `player_base_stats.toml` is validated
- **THEN** every base value key SHALL reference an existing player stat and every runtime-effective player stat that requires a default SHALL have a defined base value

#### Scenario: 状态元数据约束词缀生成
- **WHEN** player stat definitions are validated
- **THEN** any stat whose `v1_status` is not `V1_ACTIVE` SHALL have `affix_spawn_enabled_v1 = false`

### Requirement: 配置拆分与校验

V1 SHALL split configuration into focused files under `configs/` and SHALL NOT use `all.xxx.toml` style aggregate configuration files.

#### Scenario: 配置目录结构
- **WHEN** V1 configuration files are created
- **THEN** they SHALL be split across `configs/core/`, `configs/player/`, `configs/combat/`, `configs/gems/`, `configs/sudoku_board/`, `configs/skills/`, `configs/affixes/`, `configs/loot/`, and `configs/localization/`

#### Scenario: 必需配置文件
- **WHEN** V1 configuration completeness is validated
- **THEN** the system SHALL require the planned files `id_rules.toml`, `random_rules.toml`, `player_base_stats.toml`, `player_stat_defs.toml`, a left character panel display configuration under `configs/player/`, `damage_types.toml`, `hit_rules.toml`, `status_effects.toml`, `gem_type_defs.toml`, `gem_tag_defs.toml`, `gem_instance_schema.toml`, active/passive/support Skill Package files under `configs/skills/`, `board_layout.toml`, `placement_rules.toml`, `relation_rules.toml`, `effect_routing_rules.toml`, `skill_scaling_rules.toml`, `affix_defs.toml`, `affix_spawn_rules.toml`, `affix_groups.toml`, `affix_tiers.toml`, `gem_drop_pools.toml`, `drop_weight_rules.toml`, and `zh_cn.toml`

#### Scenario: 配置引用校验
- **WHEN** V1 configuration validation runs
- **THEN** it SHALL validate unique IDs, existing references, legal tags, legal stats, legal `gem_type`, legal affix groups, legal value ranges, required Chinese localization keys, player stat V1 status metadata, player base stat coverage, and left character panel stat bindings

#### Scenario: 多余属性引用校验失败
- **WHEN** V1 configuration validation finds `pickup_radius`, `active_skill_slots`, `passive_skill_slots`, or `skill_slots_active` referenced as a player stat
- **THEN** validation SHALL fail instead of treating the reference as an alias or ignored field

### Requirement: 随机词缀

V1 SHALL include random gem affixes as a required part of the loop rather than a deferred feature, and SHALL only generate affixes whose stats are explicitly V1 affix-spawn enabled.

#### Scenario: 稀有度决定词缀数量
- **WHEN** a gem instance is generated
- **THEN** `normal` / 普通 SHALL have 0 random affixes, `magic` / 魔法 SHALL have 1 random affix, and `rare` / 稀有 SHALL have 2 random affixes

#### Scenario: 词缀类型覆盖
- **WHEN** affix definitions are validated
- **THEN** they SHALL cover `prefix`, `suffix`, and `implicit` affixes

#### Scenario: 词缀大类覆盖
- **WHEN** V1 affix pools are validated
- **THEN** they SHALL cover skill numeric affixes, tag strengthening affixes, board source affixes, board target affixes, high-risk cost affixes, and affix mutual exclusion groups

#### Scenario: 盘面词缀方向
- **WHEN** board-related affixes are validated
- **THEN** they SHALL include `source_power_row`, `source_power_column`, `source_power_box`, `target_power_row`, `target_power_column`, and `target_power_box`

#### Scenario: 禁止非 V1 生效词缀生成
- **WHEN** affix definitions or affix spawn pools are validated
- **THEN** every randomly spawnable affix stat SHALL reference a player stat with `v1_status = "V1_ACTIVE"` and `affix_spawn_enabled_v1 = true`

#### Scenario: 词缀生成流程
- **WHEN** Loot Runtime generates a gem instance
- **THEN** it SHALL select base gem type, select rarity, determine affix count, filter affixes by gem tags, filter affixes by V1 stat spawn eligibility, apply affix weights, enforce mutual exclusion groups, roll value ranges, and save the result as a gem instance

### Requirement: WebApp 可操作入口

V1 SHALL provide a browser-openable WebApp entry for the minimal loop, including a configurable left character panel backed by real player stat data.

#### Scenario: 浏览器打开 WebApp
- **WHEN** 玩家启动 V1 WebApp
- **THEN** WebApp SHALL open in a browser page with the Chinese title `数独宝石流放like V1`

#### Scenario: WebApp 完成最小循环操作
- **WHEN** 玩家使用 WebApp
- **THEN** WebApp SHALL allow player to view inventory, inspect gems, mount/unmount gems on the 9x9 board, preview final skill effects, start minimal combat, see drops, and pick up drops

#### Scenario: WebApp 中文玩家可见文本
- **WHEN** WebApp displays buttons, titles, prompts, errors, HUD, logs, inventory, board, skill preview, combat, drops, pickup feedback, or character panel text
- **THEN** WebApp SHALL display all player-visible text in Chinese

#### Scenario: WebApp 复用 V1 规则层
- **WHEN** WebApp needs sudoku legality, board relationships, skill final effects, combat results, loot drops, inventory updates, or calculated player stats
- **THEN** WebApp SHALL call or reuse the current V1 rules capability through an API or adapter layer and SHALL NOT reimplement a divergent rule set in frontend code

#### Scenario: 左侧人物面板读取真实属性值
- **WHEN** the inventory overlay left character panel is rendered
- **THEN** its stat values SHALL come from backend-provided player stat values and SHALL NOT use hardcoded gameplay-looking placeholder values for configured stat rows

#### Scenario: 左侧人物面板展示可配置
- **WHEN** left character panel display configuration is changed for a stat row's group, order, icon, label, formatter, or bound stat id
- **THEN** the WebApp SHALL render the panel according to that configuration without requiring a frontend code change for that row

#### Scenario: 左侧人物面板拒绝无效绑定
- **WHEN** left character panel display configuration references a missing stat id, missing localization key, or obsolete player stat id
- **THEN** validation SHALL fail before the WebApp renders an inconsistent character panel
