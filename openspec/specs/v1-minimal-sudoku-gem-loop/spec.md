# v1-minimal-sudoku-gem-loop Specification

## Purpose
TBD - created by archiving change implement-v1-minimal-sudoku-gem-loop. Update Purpose after archive.
## Requirements
### Requirement: V1 正式最小循环

V1 SHALL be the first formal minimal loop version of the project, not a Demo, and SHALL validate the loop "刷宝石 -> 看词缀 -> 调盘面 -> 技能表现变化 -> 再刷宝石".

#### Scenario: 完成刷宝闭环
- **WHEN** 玩家通过战斗获得宝石、拾取入库、查看词缀、调整 9x9 数独盘并重新进入战斗
- **THEN** 系统 SHALL 使用新盘面和宝石词缀重新计算技能最终效果，并在战斗中体现技能表现变化

#### Scenario: 禁止 V1 外系统
- **WHEN** V1 规格、配置或 UI 被审查
- **THEN** 系统 SHALL NOT include 装备系统、装备随机词缀、地图词缀、腐化系统、复杂货币系统、法力系统、力量 / 敏捷 / 智力成长系统、完整元素抗性系统、完整护甲 / 闪避 / 能量护盾系统、赛季系统、复杂技能树或多角色职业

### Requirement: 模块边界

V1 SHALL define and preserve module boundaries for Core Foundation, Content Rule Data, Gem Board Runtime, Skill Runtime, Combat Runtime, Loot Runtime, Inventory / Storage, and Presentation UX.

#### Scenario: 模块职责清晰
- **WHEN** 后续实现任务被拆分
- **THEN** 每个任务 SHALL map to one or more of the eight V1 modules and SHALL respect the forbidden responsibilities documented in the design

#### Scenario: 运行时不承担内容规则
- **WHEN** Gem Board Runtime, Skill Runtime, Combat Runtime, Loot Runtime, Inventory / Storage, or Presentation UX needs content definitions
- **THEN** they SHALL consume validated Content Rule Data rather than embedding static content tables directly in runtime logic

### Requirement: 配置拆分与校验

V1 SHALL split configuration into focused files under `configs/` and SHALL NOT use `all.xxx.toml` style aggregate configuration files.

#### Scenario: 配置目录结构
- **WHEN** V1 configuration files are created
- **THEN** they SHALL be split across `configs/core/`, `configs/player/`, `configs/combat/`, `configs/gems/`, `configs/sudoku_board/`, `configs/skills/`, `configs/affixes/`, `configs/loot/`, and `configs/localization/`

#### Scenario: 必需配置文件
- **WHEN** V1 configuration completeness is validated
- **THEN** the system SHALL require the planned files `id_rules.toml`, `random_rules.toml`, `player_base_stats.toml`, `player_stat_defs.toml`, `damage_types.toml`, `hit_rules.toml`, `status_effects.toml`, `gem_type_defs.toml`, `active_skill_gems.toml`, `support_gems.toml`, `gem_tag_defs.toml`, `gem_instance_schema.toml`, `board_layout.toml`, `placement_rules.toml`, `relation_rules.toml`, `effect_routing_rules.toml`, `skill_templates.toml`, `skill_scaling_rules.toml`, `affix_defs.toml`, `affix_spawn_rules.toml`, `affix_groups.toml`, `affix_tiers.toml`, `gem_drop_pools.toml`, `drop_weight_rules.toml`, and `zh_cn.toml`

#### Scenario: 配置引用校验
- **WHEN** V1 configuration validation runs
- **THEN** it SHALL validate unique IDs, existing references, legal tags, legal stats, legal `gem_type`, legal affix groups, legal value ranges, and required Chinese localization keys

### Requirement: 玩家属性定义

V1 SHALL define the minimal player stats required for combat, skill calculation, gem affixes, pickup, and active skill slots.

#### Scenario: 属性集合完整
- **WHEN** `player_stat_defs.toml` is validated
- **THEN** it SHALL include `max_life`, `current_life`, `move_speed`, `pickup_radius`, `skill_slots_active`, `damage_add_percent`, `damage_final_percent`, `attack_speed_add_percent`, `cast_speed_add_percent`, `skill_speed_final_percent`, `cooldown_reduction_percent`, `added_cooldown_ms`, `area_add_percent`, `projectile_count_add`, `projectile_speed_add_percent`, `crit_chance_add_percent`, `crit_damage_add_percent`, `status_chance_add_percent`, `physical_damage_add_percent`, `fire_damage_add_percent`, `cold_damage_add_percent`, and `lightning_damage_add_percent`

#### Scenario: V1 外成长属性不进入实现
- **WHEN** player stats are exposed to V1 gameplay or UI
- **THEN** mana, strength, dexterity, intelligence, full resistance stats, armor, evasion, and energy shield SHALL remain out of V1 implemented gameplay

### Requirement: 宝石定义与宝石实例

V1 SHALL separate base gem definitions from player-owned gem instances.

#### Scenario: 宝石实例引用基础定义
- **WHEN** a gem drops and is saved to inventory
- **THEN** the saved instance SHALL include an `instance_id`, `base_gem_id`, `gem_type`, `rarity`, `level`, affix lists, and lock state while referencing the base definition by ID

#### Scenario: 主动技能宝石清单
- **WHEN** active skill gem content is validated
- **THEN** it SHALL include exactly the V1 active skill IDs `active_fire_bolt`, `active_ice_shards`, `active_lightning_chain`, `active_frost_nova`, `active_puncture`, `active_penetrating_shot`, `active_lava_orb`, and `active_fungal_petards`

#### Scenario: 辅助宝石结构
- **WHEN** support gem content is validated
- **THEN** it SHALL include 24 support gem structures split into 8 general skill modifiers, 4 damage type enhancers, 4 projectile / area specialists, 3 high-risk high-reward supports, 2 skill level supports, and 3 row / column / box conduits

#### Scenario: 辅助宝石适用条件
- **WHEN** a support gem definition is validated
- **THEN** it SHALL declare explicit apply filters using tags and SHALL NOT rely only on stat field names to imply affected targets

### Requirement: 数独宝石盘

V1 SHALL provide a 9x9 sudoku gem board with row, column, box, and orthogonal adjacency relationships.

#### Scenario: gem_type 合法性检查
- **WHEN** a gem is placed on the board
- **THEN** the board SHALL validate that its `gem_type` is between `gem_type_1` and `gem_type_9`

#### Scenario: 同行同列同宫不重复
- **WHEN** the board contains two placed gems with the same `gem_type` in the same row, column, or 3x3 box
- **THEN** the placement SHALL be invalid

#### Scenario: 空盘不可进入战斗
- **WHEN** the board has no active skill gem
- **THEN** the system SHALL prevent entering combat

#### Scenario: 关系计算
- **WHEN** two gems are placed on the board
- **THEN** Gem Board Runtime SHALL calculate whether they are in the same row, same column, same 3x3 box, or orthogonally adjacent

### Requirement: 随机词缀

V1 SHALL include random gem affixes as a required part of the loop rather than a deferred feature.

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

#### Scenario: 词缀生成流程
- **WHEN** Loot Runtime generates a gem instance
- **THEN** it SHALL select base gem type, select rarity, determine affix count, filter affixes by gem tags, apply affix weights, enforce mutual exclusion groups, roll value ranges, and save the result as a gem instance

### Requirement: 掉落与库存

V1 SHALL support gem drops, pickup, inventory storage, and board mount / unmount state.

#### Scenario: 只掉落宝石
- **WHEN** a combat reward drop is generated
- **THEN** Loot Runtime SHALL generate only active skill gems or support gems and SHALL NOT generate equipment, currency, maps, fragments, or materials

#### Scenario: 拾取入库
- **WHEN** the player picks up a dropped gem within pickup range
- **THEN** the gem instance SHALL be added to Inventory / Storage with its base gem reference, rarity, affixes, and board state preserved

#### Scenario: 上盘下盘
- **WHEN** a player mounts or unmounts a gem
- **THEN** Inventory / Storage SHALL update the gem's board occupancy state and Gem Board Runtime SHALL recalculate legality and relationships

### Requirement: 数独盘效果路由

V1 SHALL route gem effects through Source, Target, Relation, and Power using fixed enumerated rules.

#### Scenario: 基础路由公式
- **WHEN** a source gem effect is routed to a target gem
- **THEN** the routed effect SHALL be calculated from source effect, source power, target receiving power, and relation coefficient

#### Scenario: 关系系数
- **WHEN** relation coefficients are applied
- **THEN** V1 SHALL support adjacent coefficient, same row coefficient, same column coefficient, and same box coefficient

#### Scenario: 相邻关系优先
- **WHEN** two gems are both orthogonally adjacent and in the same row or column
- **THEN** the system SHALL calculate the relation once using the adjacent relationship and SHALL NOT add a second row or column calculation

#### Scenario: 防重复和防递归
- **WHEN** source / target routing is evaluated
- **THEN** the same source gem SHALL affect the same target gem for the same stat at most once, the system SHALL NOT perform infinite recursive propagation, and conduit gems SHALL only amplify without creating new secondary propagation chains

### Requirement: 技能最终效果计算

V1 SHALL calculate final skill effects from active skill definitions, gem affixes, support effects, board routing, conduit amplification, additive modifiers, and final modifiers.

#### Scenario: 固定计算顺序
- **WHEN** the final effect of an active skill is calculated
- **THEN** the system SHALL read the active skill base definition, apply the active gem's own random affixes, find support gems that can affect it, apply support base effects, apply support random affixes, apply row / column / box conduit amplification, aggregate additive modifiers, aggregate final modifiers, and output the final skill instance

#### Scenario: 战斗中使用最终技能实例
- **WHEN** combat automatically releases an activated skill
- **THEN** Skill Runtime SHALL use the final skill instance calculated from the current valid board and inventory state

### Requirement: 最小战斗循环

V1 SHALL include a minimal combat loop that supports automatic active skill release, monster kills, gem drops, gem pickup, and returning to board adjustment.

#### Scenario: 自动释放已激活技能
- **WHEN** combat is running and the board has valid activated active skill gems
- **THEN** Combat Runtime SHALL trigger Skill Runtime to automatically release those skills according to their final cooldown and speed values

#### Scenario: 击杀触发掉落
- **WHEN** monsters are killed in combat
- **THEN** Combat Runtime SHALL trigger Loot Runtime to roll gem drops

### Requirement: 中文 UI

V1 SHALL display all player-visible text in Chinese.

#### Scenario: 宝石详情展示
- **WHEN** the player views a gem
- **THEN** Presentation UX SHALL show Chinese name, gem type / number / color identity, active or support category, tags, base skill or support effect, random affixes, affix values, affected target rules, and current effective targets on the board

#### Scenario: 数独盘展示
- **WHEN** the player edits the board
- **THEN** Presentation UX SHALL show the 9x9 grid, 3x3 box sections, invalid placement prompts, same row / same column / same box highlights, gem influence preview, and final skill effect preview in Chinese

#### Scenario: 战斗与掉落展示
- **WHEN** combat or loot feedback is displayed
- **THEN** combat HUD, drop prompts, invalid placement prompts, and skill final effect descriptions SHALL use Chinese player-visible text

### Requirement: WebApp 可操作入口

V1 SHALL provide a browser-openable WebApp entry for the minimal loop.

#### Scenario: 浏览器打开 WebApp
- **WHEN** 玩家启动 V1 WebApp
- **THEN** WebApp SHALL open in a browser page with the Chinese title `数独宝石流放like V1`

#### Scenario: WebApp 完成最小循环操作
- **WHEN** 玩家使用 WebApp
- **THEN** WebApp SHALL allow player to view inventory, inspect gems, mount/unmount gems on the 9x9 board, preview final skill effects, start minimal combat, see drops, and pick up drops

#### Scenario: WebApp 中文玩家可见文本
- **WHEN** WebApp displays buttons, titles, prompts, errors, HUD, logs, inventory, board, skill preview, combat, drops, or pickup feedback
- **THEN** WebApp SHALL display all player-visible text in Chinese

#### Scenario: WebApp 复用 V1 规则层
- **WHEN** WebApp needs sudoku legality, board relationships, skill final effects, combat results, loot drops, or inventory updates
- **THEN** WebApp SHALL call or reuse the current V1 rules capability through an API or adapter layer and SHALL NOT reimplement a divergent rule set in frontend code

