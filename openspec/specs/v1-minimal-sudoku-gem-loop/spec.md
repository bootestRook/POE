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

### Requirement: 技能定义 Skill Package
V1 技能系统 SHALL 将主动技能定义从集中式 `skill_templates` 迁移为 Skill Package 结构，每个主动技能 SHALL 拥有独立目录和独立 `skill.yaml`。

#### Scenario: 主动技能独立 skill.yaml
- **WHEN** 主动技能定义被加载
- **THEN** 系统 SHALL 从 `configs/skills/active/<skill_id>/skill.yaml` 读取对应主动技能定义，并 SHALL NOT 依赖单一集中大表表达所有主动技能语义

#### Scenario: 火焰弹 package 路径
- **WHEN** 第一轮 Apply 加载火焰弹技能定义
- **THEN** 系统 SHALL 从 `configs/skills/active/active_fire_bolt/skill.yaml` 加载 `active_fire_bolt`

#### Scenario: 技能字段完整性
- **WHEN** `skill.yaml` 被校验
- **THEN** 技能定义 SHALL 至少声明 `id`、`version`、`display.name_key`、`display.description_key`、`classification.tags`、`classification.damage_type`、`classification.damage_form`、`cast.mode`、`cast.target_selector`、`cast.search_range`、`cast.cooldown_ms`、`cast.windup_ms`、`cast.recovery_ms`、`behavior.template`、`behavior.params`、`hit.base_damage`、`hit.can_crit`、`hit.can_apply_status`、`scaling.additive_stats`、`scaling.final_stats`、`scaling.runtime_params`、`presentation.vfx`、`presentation.sfx`、`presentation.floating_text`、`presentation.screen_feedback` 和 `preview.show_fields`

### Requirement: skill.schema.json 校验
V1 技能系统 SHALL 使用统一 `configs/skills/schema/skill.schema.json` 校验 Skill Package 定义。

#### Scenario: schema 校验技能定义
- **WHEN** 技能 package 被加载
- **THEN** 系统 SHALL 使用 `skill.schema.json` 校验 `skill.yaml` 的必需字段、枚举、类型、模板引用和参数边界

#### Scenario: schema 不执行技能行为
- **WHEN** `skill.schema.json` 校验 `behavior.params`
- **THEN** schema SHALL 只校验结构和允许字段，并 SHALL NOT 执行脚本、解释表达式或计算技能效果

#### Scenario: 玩家可见文本使用本地化 key
- **WHEN** 技能 package 声明名称、描述、浮字、原因或反馈文案
- **THEN** 技能 package SHALL 使用中文本地化 key，并 SHALL NOT 写入英文玩家可见文案

### Requirement: 白名单 Behavior Template
V1 技能行为 SHALL 只能通过白名单 Behavior Template 执行，技能 YAML SHALL NOT 包含任意脚本、复杂 DSL 或复杂表达式解释器。

#### Scenario: 只允许白名单模板
- **WHEN** 技能定义声明 `behavior.template`
- **THEN** 系统 SHALL 只接受 `projectile`、`fan_projectile`、`chain`、`player_nova`、`melee_arc`、`line_pierce`、`orbit` 或 `delayed_area`

#### Scenario: 模板参数受控
- **WHEN** 技能定义声明 `behavior.params`
- **THEN** 系统 SHALL 只接受对应 Behavior Template 白名单中定义的参数，并 MUST reject 任意脚本、函数调用、表达式字符串或未声明参数

#### Scenario: V1 主动技能模板映射
- **WHEN** 后续迁移 8 个主动技能
- **THEN** `active_fire_bolt` SHALL use `projectile`，`active_ice_shards` SHALL use `fan_projectile`，`active_lightning_chain` SHALL use `chain`，`active_frost_nova` SHALL use `player_nova`，`active_puncture` SHALL use `melee_arc`，`active_penetrating_shot` SHALL use `line_pierce`，`active_lava_orb` SHALL use `orbit`，`active_fungal_petards` SHALL use `delayed_area`

### Requirement: FinalSkillInstance 最终技能参数
V1 技能系统 SHALL 使用 `FinalSkillInstance` 承接主动宝石、被动、辅助、数独关系和 modifier 聚合后的最终技能参数。

#### Scenario: FinalSkillInstance 输入来源
- **WHEN** 主动技能进入 Skill Runtime
- **THEN** `FinalSkillInstance` SHALL 包含来自主动技能 package、主动宝石实例、被动贡献、辅助贡献、数独关系、additive modifier、final modifier 和 runtime 参数 modifier 的最终结果

#### Scenario: FinalSkillInstance 兼容三类宝石字段
- **WHEN** `FinalSkillInstance` 记录来源信息
- **THEN** 来源信息 SHALL 兼容 `gem_kind` / `sudoku_digit` 字段模型，并 SHALL NOT 从旧 `gem_type` 推断宝石大类或数独数字

#### Scenario: FinalSkillInstance 不执行行为
- **WHEN** `FinalSkillInstance` 被创建
- **THEN** 它 SHALL 表示最终参数和来源上下文，并 SHALL NOT 包含任意脚本或直接执行技能行为

### Requirement: SkillEvent 事件接口
V1 技能系统 SHALL 使用 `SkillEvent[]` 作为技能表现与伤害结算的事件接口，并作为 Runtime 和 WebApp 的共同语言。

#### Scenario: SkillEvent 类型覆盖
- **WHEN** Skill Runtime 输出技能事件
- **THEN** `SkillEvent` SHALL 至少预留 `cast_start`、`projectile_spawn`、`projectile_hit`、`chain_segment`、`area_spawn`、`melee_arc`、`orbit_spawn`、`orbit_tick`、`delayed_area_prime`、`delayed_area_explode`、`damage`、`hit_vfx`、`floating_text` 和 `cooldown_update`

#### Scenario: SkillEvent 字段覆盖
- **WHEN** 任一 `SkillEvent` 被序列化给 Combat Runtime 或 WebApp
- **THEN** 事件 SHALL 能表达 `source_entity`、`target_entity`、`position`、`direction`、`delay_ms`、`duration_ms`、`amount`、`damage_type`、`skill_instance_id`、`vfx_key`、`sfx_key` 和 `reason_key`

#### Scenario: damage 事件代表真实结算点
- **WHEN** 技能造成伤害
- **THEN** 伤害结算 SHALL 由 `damage` 事件表达，Combat Runtime SHALL NOT 在技能释放瞬间提前扣除需要等待命中的伤害

### Requirement: Combat Runtime 与 Skill Runtime 分层
V1 Combat Runtime SHALL 管理战斗流程和实体结算，Skill Runtime SHALL 根据 `FinalSkillInstance` 与白名单 Behavior Template 生成 `SkillEvent[]`。

#### Scenario: Combat Runtime 不写具体技能分支
- **WHEN** Combat Runtime 自动释放主动技能
- **THEN** Combat Runtime SHALL 调用 Skill Runtime 执行技能，并 SHALL NOT 编写 `active_fire_bolt`、`active_lightning_chain`、`active_frost_nova` 等具体技能分支

#### Scenario: Skill Runtime 生成事件
- **WHEN** Skill Runtime 执行 `FinalSkillInstance`
- **THEN** Skill Runtime SHALL 根据 `behavior.template` 调用白名单行为模板，并输出真实 `SkillEvent[]`

#### Scenario: 火焰弹伤害时机
- **WHEN** `active_fire_bolt` 使用 `projectile` 行为模板命中目标
- **THEN** `damage` 事件 SHALL 与投射物命中时机一致，并 SHALL NOT 在 `cast_start` 时提前结算

### Requirement: WebApp 消费 SkillEvent
V1 WebApp SHALL 消费 `SkillEvent[]` 渲染技能表现，并 SHALL NOT 根据 `behavior_type + visual_effect` 猜测技能行为。

#### Scenario: WebApp 渲染投射物
- **WHEN** WebApp 收到 `projectile_spawn` 事件
- **THEN** WebApp SHALL 根据事件中的位置、方向、持续时间、`skill_instance_id` 和 `vfx_key` 渲染投射物表现

#### Scenario: WebApp 渲染命中与浮字
- **WHEN** WebApp 收到 `damage`、`hit_vfx` 或 `floating_text` 事件
- **THEN** WebApp SHALL 根据事件中的目标、位置、数值、伤害类型、`vfx_key` 和 `reason_key` 渲染命中表现与中文浮字

#### Scenario: 前端不猜技能行为
- **WHEN** WebApp 需要展示技能表现
- **THEN** WebApp SHALL 使用 `SkillEvent[]`，并 SHALL NOT 通过 `behavior_type`、`visual_effect` 或技能 ID 在前端反推伤害时机、目标选择或技能路径

### Requirement: 火焰弹第一轮垂直切片
V1 第一轮 Apply SHALL 只实现 `active_fire_bolt` 的 Skill Package、schema、FinalSkillInstance、SkillEvent、Combat Runtime 和 WebApp 消费垂直切片。

#### Scenario: 火焰弹加载和校验
- **WHEN** 第一轮 Apply 验收火焰弹
- **THEN** `active_fire_bolt` SHALL 从 `configs/skills/active/active_fire_bolt/skill.yaml` 加载，并 SHALL 通过 `skill.schema.json` 校验

#### Scenario: 火焰弹生成最终实例
- **WHEN** 火焰弹主动宝石在有效盘面中进入战斗
- **THEN** 系统 SHALL 生成包含最终参数的 `FinalSkillInstance`

#### Scenario: 火焰弹输出事件
- **WHEN** 火焰弹释放并命中目标
- **THEN** 系统 SHALL 输出至少包含 `projectile_spawn`、`damage`、`hit_vfx` 和 `floating_text` 的 `SkillEvent[]`

#### Scenario: 其他 7 个技能保持旧行为
- **WHEN** 第一轮 Apply 完成
- **THEN** `active_ice_shards`、`active_lightning_chain`、`active_frost_nova`、`active_puncture`、`active_penetrating_shot`、`active_lava_orb` 和 `active_fungal_petards` SHALL 保持旧行为，并 SHALL NOT 被半迁移、禁用或破坏

#### Scenario: 火焰弹完整验收更新
- **WHEN** `active_fire_bolt` 垂直切片被标记为完整完成
- **THEN** SkillEditor SHALL 能打开它，Skill Test Arena SHALL 能运行它，AI 自测报告 SHALL 能基于真实测试结果评估它

### Requirement: SkillEditor V0
V1 WebApp SHALL provide a browser-openable SkillEditor V0 for Skill Package editing.

#### Scenario: 打开已迁移 Skill Package
- **WHEN** SkillEditor V0 打开技能列表
- **THEN** SkillEditor SHALL list migrated active skill packages from `configs/skills/active/` and SHALL allow opening at least `configs/skills/active/active_fire_bolt/skill.yaml`

#### Scenario: 不打开未迁移旧技能
- **WHEN** SkillEditor V0 displays the existing 8 active skills
- **THEN** SkillEditor SHALL NOT allow the 7 non-migrated old skills to be opened as editable Skill Packages

#### Scenario: 显示基础 package 信息
- **WHEN** SkillEditor V0 opens `active_fire_bolt`
- **THEN** SkillEditor SHALL display the Chinese skill name, `skill.yaml` path, `behavior.template`, and current schema validation status

#### Scenario: 只编辑 schema 允许字段
- **WHEN** SkillEditor saves a Skill Package
- **THEN** SkillEditor SHALL edit only fields allowed by `skill.schema.json` and the referenced behavior template whitelist

#### Scenario: 保存失败中文错误
- **WHEN** SkillEditor validation fails before saving
- **THEN** SkillEditor SHALL display Chinese error text and SHALL NOT write invalid skill data

#### Scenario: 禁止脚本和复杂表达式
- **WHEN** SkillEditor edits or saves a Skill Package
- **THEN** SkillEditor SHALL NOT write arbitrary scripts, expression DSL, complex expression interpreters, or script-like fields

### Requirement: SkillEditor 模块化字段
SkillEditor SHALL organize editable fields by modules, and each implemented `behavior_template` SHALL expose all editable fields for that template before a skill is considered migrated.

#### Scenario: 基础信息模块
- **WHEN** SkillEditor opens `active_fire_bolt`
- **THEN** SkillEditor SHALL expose an information module with read-only `id`, editable `version`, `display.name_key`, `display.description_key`, `classification.tags`, `classification.damage_type`, and `classification.damage_form`

#### Scenario: 释放参数模块
- **WHEN** SkillEditor opens `active_fire_bolt`
- **THEN** SkillEditor SHALL expose a cast module with `cast.mode`, `cast.target_selector`, `cast.search_range`, `cast.cooldown_ms`, `cast.windup_ms`, and `cast.recovery_ms`

#### Scenario: projectile 子弹模块
- **WHEN** SkillEditor opens a `projectile` behavior template
- **THEN** SkillEditor SHALL expose `projectile_count`, `projectile_speed`, `projectile_width`, `projectile_height`, `max_distance`, `hit_policy`, `pierce_count`, `collision_radius`, `spawn_offset`, and `travel_duration` or a read-only flight time derived from speed and distance

#### Scenario: 伤害点模块
- **WHEN** SkillEditor opens `active_fire_bolt`
- **THEN** SkillEditor SHALL expose `hit.base_damage`, `hit.can_crit`, `hit.can_apply_status`, `damage_type`, `damage_form`, `damage_timing`, `hit_delay_ms`, `hit_radius`, and `target_policy`

#### Scenario: 表现模块
- **WHEN** SkillEditor opens `active_fire_bolt`
- **THEN** SkillEditor SHALL expose `cast_vfx_key`, `projectile_vfx_key`, `hit_vfx_key`, `sfx_key`, `floating_text_style`, `hit_stop_ms`, and `camera_shake`

#### Scenario: 预览字段模块
- **WHEN** SkillEditor opens `active_fire_bolt`
- **THEN** SkillEditor SHALL expose `preview.show_fields`

#### Scenario: behavior template 字段支持是迁移前置条件
- **WHEN** a behavior template is implemented for migration
- **THEN** SkillEditor SHALL expose all editable fields for that template before any skill using it is considered migrated

### Requirement: Modifier 测试栈
SkillEditor SHALL allow selecting support gem effects or scaling modifiers for test-only modifier stacks.

#### Scenario: 读取可测试 modifier
- **WHEN** SkillEditor builds a test Modifier Stack
- **THEN** it SHALL read testable modifiers from current support gem configuration or `skill_scaling_rules`

#### Scenario: 选择多个测试 modifier
- **WHEN** a user configures a test run
- **THEN** SkillEditor SHALL allow selecting one or more test modifiers

#### Scenario: 模拟关系与 power 参数
- **WHEN** a test Modifier Stack is configured
- **THEN** SkillEditor SHALL allow simulated relation selection for adjacent, same row, same column, and same box, and SHALL allow setting `source_power`, `target_power`, and conduit test parameters

#### Scenario: 测试 modifier 不写真实数据
- **WHEN** a test Modifier Stack is applied
- **THEN** it SHALL affect only the test run and SHALL NOT write real gem instances, real Skill Package files, or production inventory data

#### Scenario: 不恢复随机词缀
- **WHEN** test modifiers are used
- **THEN** test modifier stacks SHALL NOT write random affixes, real gem instance affixes, random affix generated values, random affix UI sections, or random affix fields into real skill files

### Requirement: Skill Test Arena
V1 WebApp SHALL provide a dedicated skill test arena for controlled skill behavior verification.

#### Scenario: 受控测试场景
- **WHEN** Skill Test Arena is opened
- **THEN** it SHALL provide single dummy, three-target horizontal row, vertical queue, and dense small monster scenarios

#### Scenario: 测试场操作
- **WHEN** Skill Test Arena runs a test
- **THEN** it SHALL support selecting a skill, applying or disabling the test Modifier Stack, run, pause, single-step, reset, viewing monster life, viewing hit targets, viewing actual damage results, and viewing the SkillEvent timeline

#### Scenario: 第一版支持火焰弹
- **WHEN** Skill Test Arena first ships
- **THEN** it SHALL support at least `active_fire_bolt`

#### Scenario: 火焰弹测试时序
- **WHEN** Skill Test Arena runs `active_fire_bolt`
- **THEN** it SHALL generate `projectile_spawn`, SHALL NOT reduce life while the projectile is flying, SHALL generate `damage` after arrival, and SHALL generate `hit_vfx` and `floating_text` after or with `damage`

#### Scenario: 火焰弹测试数值变化
- **WHEN** projectile speed, base damage, or test Modifier Stack changes for `active_fire_bolt`
- **THEN** Skill Test Arena SHALL show changed flight time, changed damage, and changed `FinalSkillInstance` or SkillEvent values

### Requirement: SkillEvent 时间线查看器
SkillEditor and Skill Test Arena SHALL expose a timeline viewer for real SkillEvent sequences.

#### Scenario: 时间线事件类型
- **WHEN** a SkillEvent timeline is displayed
- **THEN** it SHALL show `cast_start`, `projectile_spawn`, `projectile_hit`, `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` event types when present

#### Scenario: 时间线事件字段
- **WHEN** a SkillEvent is shown in the timeline
- **THEN** the timeline SHALL display `timestamp_ms`, `delay_ms`, `duration_ms`, `source_entity`, `target_entity`, `amount`, `damage_type`, `vfx_key`, `reason_key`, and `payload`

#### Scenario: 时间线来源真实
- **WHEN** the timeline is used for validation
- **THEN** it SHALL display actual SkillEvent data from a test or runtime execution and SHALL NOT use static fake events

### Requirement: AI 自测报告
System SHALL generate a Chinese self-test report from actual skill test results.

#### Scenario: 报告基于真实结果
- **WHEN** an AI self-test report is generated
- **THEN** the report SHALL be based on actual Skill Test Arena results, actual SkillEvent sequences, actual damage results, and actual hit targets

#### Scenario: 报告格式
- **WHEN** an AI self-test report is exported
- **THEN** it SHALL be Markdown or JSON, and all natural-language report text SHALL be Chinese

#### Scenario: 报告内容
- **WHEN** an AI self-test report is generated
- **THEN** it SHALL include test skill ID, Chinese skill name, `skill.yaml` path, `behavior_template`, test scenario, test Modifier Stack, expected player-facing description, actual SkillEvent sequence, actual damage result, actual hit targets, presentation event completeness, whether damage timing matches presentation, whether actual behavior matches description, inconsistencies, and suggested fixes

#### Scenario: 对比期望与实际
- **WHEN** report evaluation runs
- **THEN** it SHALL compare the expected player-facing description with actual SkillEvent and damage outcomes

### Requirement: 技能系统与三类宝石字段兼容
V1 技能系统重构 SHALL 兼容三类宝石字段模型，并 SHALL NOT 破坏 `refactor-three-gem-kinds-v1-phase2` 的 active / passive / support 宝石重构方向。

#### Scenario: Apply 前确认字段模型
- **WHEN** 技能系统重构进入 Apply 阶段
- **THEN** 实现 SHALL 先确认 `gem_kind` / `sudoku_digit` 字段模型状态，并 SHALL 在三类宝石字段迁移完成后进行，或至少兼容该字段模型

#### Scenario: 不覆盖既有 active change
- **WHEN** `refactor-three-gem-kinds-v1-phase2` 仍为 active change
- **THEN** 本 change SHALL NOT 修改该 change 的 artifacts，也 SHALL NOT 设计成覆盖其字段迁移结果

### Requirement: 技能系统玩家可见文本中文
V1 技能系统 SHALL 保持所有玩家可见文本为中文。

#### Scenario: 技能 package 玩家文本
- **WHEN** 技能 package、presentation key、浮字或屏幕反馈被展示给玩家
- **THEN** 玩家可见文本 SHALL 来自中文本地化内容，并 SHALL NOT 引入英文玩家可见文案

#### Scenario: WebApp 事件反馈中文
- **WHEN** WebApp 渲染 SkillEvent 产生的 HUD、浮字、命中特效说明、冷却反馈或错误提示
- **THEN** 所有玩家可见文本 SHALL 使用中文

### Requirement: 冰棱散射 Skill Package
V1 SHALL migrate `active_ice_shards` / `冰棱散射` from the old centralized skill template path into an active Skill Package after the `active_fire_bolt` vertical slice is complete.

#### Scenario: 从 active Skill Package 加载冰棱散射
- **WHEN** `active_ice_shards` is considered migrated
- **THEN** the system SHALL load it from `configs/skills/active/active_ice_shards/skill.yaml`

#### Scenario: 使用 fan_projectile 行为模板
- **WHEN** the migrated `active_ice_shards` Skill Package is validated
- **THEN** it SHALL declare `behavior.template = fan_projectile`

#### Scenario: 保持中文玩家可见文本
- **WHEN** `active_ice_shards` name, description, hit reason, floating text, VFX feedback, or screen feedback is shown to the player
- **THEN** the player-visible text SHALL be Chinese and SHALL come from localization keys rather than embedded English text

#### Scenario: 不迁移其他主动技能
- **WHEN** this migration is applied
- **THEN** `active_lightning_chain`, `active_frost_nova`, `active_puncture`, `active_penetrating_shot`, `active_lava_orb`, and `active_fungal_petards` SHALL remain on their existing behavior paths unless a later change migrates them explicitly

### Requirement: fan_projectile Behavior Template
V1 SHALL provide a whitelisted `fan_projectile` Behavior Template for deterministic fan-shaped multi-projectile skills.

#### Scenario: 生成扇形多投射 SkillEvent
- **WHEN** Skill Runtime executes a skill using `fan_projectile`
- **THEN** it SHALL generate multiple projectile SkillEvents spread across a fan based on target direction, projectile count, spread angle, angle step, speed, distance, spawn pattern, and hit policy

#### Scenario: 声明 fan_projectile 参数白名单
- **WHEN** `configs/skills/behavior_templates/fan_projectile.yaml` is validated
- **THEN** it SHALL declare allowed params including `projectile_count`, `projectile_speed`, `projectile_width`, `projectile_height`, `spread_angle`, `angle_step`, `max_distance`, `hit_policy`, `collision_radius`, `spawn_pattern`, and `per_projectile_damage_scale`

#### Scenario: 禁止脚本和未声明参数
- **WHEN** a Skill Package declares `behavior.template = fan_projectile`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, and any params not declared by the `fan_projectile` template

### Requirement: SkillEditor fan_projectile 字段支持
SkillEditor SHALL expose and validate every editable `fan_projectile` field before any skill using `fan_projectile` is considered migrated.

#### Scenario: 暴露 fan_projectile 子弹模块字段
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template` is `fan_projectile`
- **THEN** it SHALL expose editable fields for `projectile_count`, `projectile_speed`, `projectile_width`, `projectile_height`, `spread_angle`, `angle_step`, `max_distance`, `hit_policy`, `collision_radius`, `spawn_pattern`, and `per_projectile_damage_scale`, plus a read-only flight time or per-projectile flight time summary

#### Scenario: 使用 schema 和模板白名单校验
- **WHEN** SkillEditor edits or saves a `fan_projectile` Skill Package
- **THEN** it SHALL validate values through both the skill schema and behavior template whitelist and SHALL NOT write fields that the template does not declare

#### Scenario: 校验 fan_projectile 数值和枚举
- **WHEN** SkillEditor validates `fan_projectile` params
- **THEN** `projectile_count` SHALL be a positive integer, `spread_angle` and `angle_step` SHALL respect declared ranges, `projectile_speed`, `projectile_width`, `projectile_height`, `max_distance`, and `collision_radius` SHALL be legal positive numbers, `hit_policy` and `spawn_pattern` SHALL use declared enum values, and `per_projectile_damage_scale` SHALL respect its declared numeric range

### Requirement: 冰棱散射 SkillEvent
`active_ice_shards` SHALL express projectile generation, hit, damage, and presentation through real SkillEvents.

#### Scenario: 输出多条 projectile_spawn
- **WHEN** migrated `active_ice_shards` is cast with `projectile_count` greater than one
- **THEN** Skill Runtime SHALL output one `projectile_spawn` event per generated ice shard with independent direction data

#### Scenario: 命中后输出结算和表现事件
- **WHEN** an ice shard hits a target according to real collision or hit policy resolution
- **THEN** Skill Runtime SHALL output `projectile_hit`, `damage`, `hit_vfx`, and `floating_text` events for that hit

#### Scenario: damage 事件负责扣血
- **WHEN** `active_ice_shards` is cast
- **THEN** target life SHALL NOT be reduced at release time, and life reduction SHALL be caused by `damage` events after projectile travel and hit timing

#### Scenario: 冰霜伤害类型
- **WHEN** `active_ice_shards` emits a `damage` event
- **THEN** the event SHALL declare `damage_type = cold`

### Requirement: 冰棱散射测试场验收
Skill Test Arena SHALL validate migrated `active_ice_shards` through controlled scenarios that prove fan-shaped multi-projectile behavior.

#### Scenario: 三目标横排验证扇形多投射
- **WHEN** Skill Test Arena runs migrated `active_ice_shards` in the three-target horizontal row scenario
- **THEN** it SHALL verify multiple ice shard spawns, visible fan angle distribution, real hit targets, and damage only after projectile hit timing

#### Scenario: 密集小怪验证多目标覆盖
- **WHEN** Skill Test Arena runs migrated `active_ice_shards` in the dense small monster scenario
- **THEN** it SHALL verify that hit targets come from real projectile collision or hit policy resolution and that multiple projectiles can affect the result

#### Scenario: 单体木桩验证基础伤害时序
- **WHEN** Skill Test Arena runs migrated `active_ice_shards` against a single dummy
- **THEN** it SHALL verify no life is reduced during projectile flight and life is reduced only after `projectile_hit` and `damage`

#### Scenario: 参数修改影响实际事件
- **WHEN** SkillEditor or the arena test stack changes `projectile_count`, `spread_angle`, or `projectile_speed`
- **THEN** Skill Test Arena SHALL show changed projectile event count, changed fan direction distribution, or changed flight time respectively

#### Scenario: Modifier 测试栈影响结果
- **WHEN** Skill Test Arena runs `active_ice_shards` with a test Modifier Stack
- **THEN** the stack SHALL affect final damage or projectile runtime parameters used by actual SkillEvents without writing real inventory, gem instance, or Skill Package data

### Requirement: 冰棱散射 AI 自测报告
The AI self-test report SHALL evaluate migrated `active_ice_shards` against real Skill Test Arena results and the expected Chinese player-facing behavior.

#### Scenario: 基于真实结果判断玩家侧描述
- **WHEN** an AI self-test report is generated for migrated `active_ice_shards`
- **THEN** it SHALL compare actual SkillEvent sequences, damage results, hit targets, and presentation events against the expected description "自动向最近敌人方向射出多枚冰霜冰棱，冰棱以扇形展开飞行，命中后造成冰霜伤害，并显示冰霜命中特效与伤害浮字。"

#### Scenario: 检查关键事件和时序
- **WHEN** the report evaluates `active_ice_shards`
- **THEN** it SHALL check whether multiple `projectile_spawn` events exist, projectile directions form a fan, `projectile_hit` exists, `damage` exists, `hit_vfx` exists, `floating_text` exists, `damage` is not earlier than `projectile_spawn`, no life is reduced during projectile flight, and `damage_type` is `cold`

#### Scenario: 检查参数修改效果
- **WHEN** the report compares baseline and modified arena runs
- **THEN** it SHALL check whether changing `projectile_count` changes projectile event count and whether changing `spread_angle` changes projectile directions

#### Scenario: 输出中文结论和修复建议
- **WHEN** the report finishes evaluation
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes

### Requirement: 冰霜新星 Skill Package
V1 SHALL migrate `active_frost_nova` / `冰霜新星` from the old centralized skill template path into an active Skill Package.

#### Scenario: 从 active Skill Package 加载冰霜新星
- **WHEN** `active_frost_nova` is considered migrated
- **THEN** the system SHALL load it from `configs/skills/active/active_frost_nova/skill.yaml`

#### Scenario: 使用 player_nova 行为模板
- **WHEN** the migrated `active_frost_nova` Skill Package is validated
- **THEN** it SHALL declare `behavior.template = player_nova`

#### Scenario: 保持中文玩家可见文本
- **WHEN** `active_frost_nova` name, description, damage reason, floating text, VFX feedback, or screen feedback is shown to the player
- **THEN** the player-visible text SHALL be Chinese and SHALL come from localization keys rather than embedded English text

#### Scenario: 不迁移其他主动技能
- **WHEN** this migration is applied
- **THEN** `active_lightning_chain`, `active_puncture`, `active_lava_orb`, and `active_fungal_petards` SHALL remain on their existing behavior paths unless a later change migrates them explicitly

### Requirement: player_nova Behavior Template
V1 SHALL provide a whitelisted `player_nova` Behavior Template for deterministic player-centered expanding nova skills.

#### Scenario: 以玩家为中心生成范围新星 SkillEvent
- **WHEN** Skill Runtime executes a skill using `player_nova`
- **THEN** it SHALL generate an `area_spawn` SkillEvent centered on the player or cast source position using declared radius, ring width, expansion duration, hit timing, target cap, damage falloff, and presentation params

#### Scenario: 声明 player_nova 参数白名单
- **WHEN** `configs/skills/behavior_templates/player_nova.yaml` is validated
- **THEN** it SHALL declare allowed params including `radius`, `expand_duration_ms`, `hit_at_ms`, `max_targets`, `center_policy`, `damage_falloff_by_distance`, `ring_width`, and `status_chance_scale`

#### Scenario: 校验 player_nova 参数约束
- **WHEN** a Skill Package declares `behavior.template = player_nova`
- **THEN** validation SHALL require positive `radius`, non-negative `expand_duration_ms`, non-negative `hit_at_ms`, `hit_at_ms` not greater than `expand_duration_ms`, positive integer or explicitly declared unlimited `max_targets`, `center_policy = player_center`, legal `damage_falloff_by_distance`, positive `ring_width`, and ranged `status_chance_scale`

#### Scenario: 禁止脚本和未声明参数
- **WHEN** a Skill Package declares `behavior.template = player_nova`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, frontend-only fake params, and any params not declared by the `player_nova` template

### Requirement: SkillEditor player_nova 字段支持
SkillEditor SHALL expose and validate every editable `player_nova` field before `active_frost_nova` is considered migrated.

#### Scenario: 暴露 player_nova 范围新星模块字段
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template` is `player_nova`
- **THEN** it SHALL expose editable fields for `radius`, `expand_duration_ms`, `hit_at_ms`, `max_targets`, `center_policy`, `damage_falloff_by_distance`, `ring_width`, and `status_chance_scale`, plus read-only range summary and hit timing summary

#### Scenario: 使用枚举和范围校验
- **WHEN** SkillEditor edits or saves a `player_nova` Skill Package
- **THEN** `center_policy` SHALL use an enum limited to player center in the first version, `radius`, `expand_duration_ms`, `hit_at_ms`, `ring_width`, and `status_chance_scale` SHALL use declared range validation, and `max_targets` SHALL use integer validation or an explicitly declared unlimited enum

#### Scenario: 使用 schema 和模板白名单校验
- **WHEN** SkillEditor saves a `player_nova` Skill Package
- **THEN** it SHALL validate through both the skill schema and behavior template whitelist and SHALL NOT write undeclared fields or frontend-only fake params

#### Scenario: 输出中文校验错误
- **WHEN** SkillEditor rejects invalid `player_nova` values such as `hit_at_ms > expand_duration_ms`, invalid enum values, or invalid numeric ranges
- **THEN** it SHALL display Chinese error text and SHALL NOT write invalid skill data

### Requirement: 冰霜新星 SkillEvent
`active_frost_nova` SHALL express area generation, hit timing, damage, and presentation through real SkillEvents.

#### Scenario: 输出 area_spawn
- **WHEN** migrated `active_frost_nova` is cast
- **THEN** Skill Runtime SHALL output an `area_spawn` event centered on the player or cast source position with radius, ring width, duration, hit timing, damage type, VFX key, and payload data

#### Scenario: 按玩家中心半径判断命中
- **WHEN** `active_frost_nova` resolves targets
- **THEN** targets inside the player-centered radius SHALL be eligible for hit and targets outside the radius SHALL NOT be hit

#### Scenario: damage 事件负责扣血
- **WHEN** `active_frost_nova` is cast
- **THEN** target life SHALL NOT be reduced at release time or before `hit_at_ms`, and life reduction SHALL be caused by `damage` events at or after `hit_at_ms`

#### Scenario: 输出伤害和表现事件
- **WHEN** an in-range target is hit by `active_frost_nova`
- **THEN** Skill Runtime SHALL output `damage`, `hit_vfx`, and `floating_text` events for that target after or with the hit timing

#### Scenario: 冰霜伤害类型
- **WHEN** `active_frost_nova` emits a `damage` event
- **THEN** the event SHALL declare `damage_type = cold`

#### Scenario: 禁止目标点爆炸和静态假事件
- **WHEN** Skill Runtime executes `active_frost_nova`
- **THEN** it SHALL NOT use target-point explosion semantics, static fake events, or a Combat Runtime branch specific to `active_frost_nova`

### Requirement: 冰霜新星测试场验收
Skill Test Arena SHALL validate migrated `active_frost_nova` through controlled scenarios that prove player-centered area behavior.

#### Scenario: 密集小怪验证范围多目标命中
- **WHEN** Skill Test Arena runs migrated `active_frost_nova` in the dense small monster scenario
- **THEN** it SHALL verify the nova is centered on the player, multiple in-range enemies can be hit, and out-of-range enemies are not hit

#### Scenario: 单体木桩验证伤害时序
- **WHEN** Skill Test Arena runs migrated `active_frost_nova` against a single dummy
- **THEN** it SHALL verify no life is reduced before `hit_at_ms` and life is reduced only by `damage` events at or after `hit_at_ms`

#### Scenario: 三目标横排验证范围边界
- **WHEN** Skill Test Arena runs migrated `active_frost_nova` in the three-target horizontal row scenario
- **THEN** it SHALL verify that targets inside the configured radius are hit and targets outside the configured radius are not hit

#### Scenario: 参数修改影响真实测试结果
- **WHEN** SkillEditor or the arena test stack changes `radius`, `expand_duration_ms`, or `hit_at_ms`
- **THEN** Skill Test Arena SHALL show changed target coverage, changed presentation timing, or changed damage timing respectively

#### Scenario: Modifier 测试栈影响结果
- **WHEN** Skill Test Arena runs `active_frost_nova` with a test Modifier Stack
- **THEN** the stack SHALL affect final damage or range runtime parameters used by actual SkillEvents without writing real inventory, gem instance, or Skill Package data

### Requirement: 冰霜新星 AI 自测报告
The AI self-test report SHALL evaluate migrated `active_frost_nova` against real Skill Test Arena results and the expected Chinese player-facing behavior.

#### Scenario: 基于真实结果判断玩家侧描述
- **WHEN** an AI self-test report is generated for migrated `active_frost_nova`
- **THEN** it SHALL compare actual SkillEvent sequences, damage results, hit targets, and presentation events against the expected description "自动以玩家自身为中心释放一圈向外扩散的冰霜新星，命中范围内敌人后造成冰霜伤害，并显示冰霜范围爆发特效与伤害浮字。"

#### Scenario: 检查 area_spawn 和玩家中心
- **WHEN** the report evaluates `active_frost_nova`
- **THEN** it SHALL check whether `area_spawn` exists and whether its center is the player or cast source position

#### Scenario: 检查关键事件和时序
- **WHEN** the report evaluates `active_frost_nova`
- **THEN** it SHALL check whether `damage`, `hit_vfx`, and `floating_text` exist, whether `damage` is not earlier than `hit_at_ms`, whether no life is reduced before `hit_at_ms`, and whether `damage_type` is `cold`

#### Scenario: 检查范围命中规则
- **WHEN** the report evaluates `active_frost_nova`
- **THEN** it SHALL check whether in-range targets are hit, out-of-range targets are not hit, and changing `radius` changes hit target coverage

#### Scenario: 输出中文结论和修复建议
- **WHEN** the report finishes evaluation
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes

### Requirement: Damage Zone Behavior Template
V1 SHALL provide a declarative `damage_zone` behavior template for non-projectile damage settlement areas / hit zones.

#### Scenario: Declare supported damage zone shapes
- **WHEN** `configs/skills/behavior_templates/damage_zone.yaml` is validated
- **THEN** it SHALL declare supported shapes including `circle` and `rectangle`

#### Scenario: Reject scripts and undeclared params
- **WHEN** a Skill Package declares `behavior.template = damage_zone`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, frontend-only fake params, and params not declared by the `damage_zone` template

#### Scenario: Validate common damage zone params
- **WHEN** a Skill Package declares `behavior.template = damage_zone`
- **THEN** validation SHALL require legal `shape`, `origin_policy`, `facing_policy`, non-negative `hit_at_ms`, positive integer or explicitly declared unlimited `max_targets`, legal `status_chance_scale`, and key-only `zone_vfx_key`

#### Scenario: Validate circle params
- **WHEN** a `damage_zone` Skill Package declares `shape = circle`
- **THEN** validation SHALL require positive `radius` and SHALL treat the effective angle as 360 degrees

#### Scenario: Validate rectangle params
- **WHEN** a `damage_zone` Skill Package declares `shape = rectangle`
- **THEN** validation SHALL require positive `length`, positive `width`, and legal `angle_offset_deg` or equivalent declared angle field

### Requirement: Frost Nova Damage Zone
V1 SHALL represent `active_frost_nova` / `冰霜新星` as a circular `damage_zone`.

#### Scenario: Load frost nova as circle damage zone
- **WHEN** `active_frost_nova` Skill Package is loaded
- **THEN** it SHALL declare `behavior.template = damage_zone` and `shape = circle`

#### Scenario: Frost nova keeps circular hit semantics
- **WHEN** Skill Runtime executes `active_frost_nova`
- **THEN** targets inside the configured circle radius SHALL be eligible for damage and targets outside the radius SHALL NOT be hit

#### Scenario: Frost nova timing remains event based
- **WHEN** Skill Runtime executes `active_frost_nova`
- **THEN** target life SHALL NOT be reduced before `hit_at_ms`, and life reduction SHALL occur through `damage` events at or after `hit_at_ms`

#### Scenario: Frost nova keeps Chinese player-facing text
- **WHEN** `active_frost_nova` name, description, damage reason, VFX feedback, or floating text is shown
- **THEN** the player-visible text SHALL remain Chinese and SHALL come from localization keys

### Requirement: Ground Spike Damage Zone
V1 SHALL rework `active_puncture` / `穿刺` into player-facing `地刺`, represented as a rectangular `damage_zone`.

#### Scenario: Load ground spike as rectangle damage zone
- **WHEN** `active_puncture` Skill Package is loaded after this change
- **THEN** it SHALL declare `behavior.template = damage_zone`, `shape = rectangle`, and `classification.damage_type = physical`

#### Scenario: Show ground spike Chinese text
- **WHEN** the skill name, description, damage reason, VFX feedback, or floating text for `active_puncture` is shown
- **THEN** the player-visible Chinese text SHALL describe `地刺` rather than a melee slash or ranged instant puncture

#### Scenario: Fire a rectangular spike line toward target direction
- **WHEN** Skill Runtime executes the ground spike skill
- **THEN** it SHALL create a rectangular damage zone from the player or cast source position toward the locked target direction, or nearest target direction when no explicit locked target is available

#### Scenario: Ground spike rectangle hit testing
- **WHEN** ground spike resolves targets
- **THEN** targets inside the rectangle defined by origin, facing direction, `length`, `width`, and angle offset SHALL be eligible for hit, while targets beyond length or outside width SHALL NOT be hit

#### Scenario: Ground spike timing and damage events
- **WHEN** ground spike is cast
- **THEN** target life SHALL NOT be reduced at release time or before `hit_at_ms`, and life reduction SHALL occur through `damage` events at or after `hit_at_ms`

#### Scenario: Ground spike physical presentation events
- **WHEN** a target is hit by ground spike
- **THEN** Skill Runtime SHALL output `damage`, `hit_vfx`, and `floating_text` events with `damage_type = physical`

### Requirement: Damage Zone SkillEvent
V1 SHALL express circular and rectangular hit zones through real `damage_zone` SkillEvents.

#### Scenario: Emit damage zone event
- **WHEN** Skill Runtime executes a skill using `damage_zone`
- **THEN** it SHALL emit a `damage_zone` event containing `shape`, `origin`, `origin_world_position`, `facing_policy`, `facing_direction`, `facing_angle_deg`, `hit_at_ms`, `max_targets`, `damage_type`, `vfx_key`, and payload data

#### Scenario: Include circle geometry
- **WHEN** the emitted `damage_zone` event has `shape = circle`
- **THEN** its payload SHALL include `radius` and effective angle information of 360 degrees

#### Scenario: Include rectangle geometry
- **WHEN** the emitted `damage_zone` event has `shape = rectangle`
- **THEN** its payload SHALL include `length`, `width`, angle offset or equivalent angle field, and the runtime facing direction

#### Scenario: Timeline displays damage zone events
- **WHEN** SkillEvent timeline displays a damage zone skill run
- **THEN** it SHALL show `cast_start`, `damage_zone`, `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when present

#### Scenario: Timeline event fields
- **WHEN** SkillEvent timeline displays a `damage_zone` related event
- **THEN** it SHALL include `timestamp_ms`, `delay_ms`, `duration_ms`, `source_entity`, `target_entity`, `amount`, `damage_type`, `vfx_key`, `reason_key`, and `payload`

### Requirement: SkillEditor Damage Zone Module
SkillEditor SHALL expose one shared damage zone module for skills whose `behavior.template` is `damage_zone`.

#### Scenario: Show common damage zone fields
- **WHEN** SkillEditor opens a `damage_zone` Skill Package
- **THEN** it SHALL expose editable common fields for zone shape, origin policy, facing policy, hit timing, max targets, status chance scale, and VFX key

#### Scenario: Show circle fields
- **WHEN** SkillEditor edits a `damage_zone` package with `shape = circle`
- **THEN** it SHALL show `radius` and SHALL hide angle or show it read-only as 360 degrees

#### Scenario: Show rectangle fields
- **WHEN** SkillEditor edits a `damage_zone` package with `shape = rectangle`
- **THEN** it SHALL show `length`, `width`, and angle offset or equivalent angle field

#### Scenario: Save only whitelisted fields
- **WHEN** SkillEditor saves a `damage_zone` Skill Package
- **THEN** it SHALL validate through the skill schema and behavior-template whitelist and SHALL NOT write undeclared fields or frontend-only fake params

#### Scenario: Chinese validation errors
- **WHEN** SkillEditor rejects invalid `damage_zone` values
- **THEN** it SHALL display Chinese error text and SHALL NOT persist invalid skill data

### Requirement: WebApp Damage Zone Consumption
WebApp SHALL render damage zone visuals from `damage_zone` SkillEvent payloads.

#### Scenario: Render circle damage zone from event
- **WHEN** WebApp receives a `damage_zone` event with `shape = circle`
- **THEN** it SHALL render a circular damage zone using event-provided origin, radius, timing, and VFX key

#### Scenario: Render rectangle damage zone from event
- **WHEN** WebApp receives a `damage_zone` event with `shape = rectangle`
- **THEN** it SHALL render a rectangular ground spike line using event-provided origin, facing direction, length, width, angle, timing, and VFX key

#### Scenario: Do not guess damage zone behavior
- **WHEN** WebApp renders frost nova or ground spike
- **THEN** it SHALL NOT infer behavior from skill id, legacy skill template id, behavior type, visual effect name, or VFX key

#### Scenario: Render presentation events from events
- **WHEN** WebApp receives `damage`, `hit_vfx`, or `floating_text`
- **THEN** it SHALL render damage, hit effects, and floating text from those events rather than from static fake events

### Requirement: Damage Zone Test Arena Acceptance
Skill Test Arena SHALL validate both circular frost nova and rectangular ground spike using real SkillEvents.

#### Scenario: Validate circle radius behavior
- **WHEN** Skill Test Arena runs `active_frost_nova`
- **THEN** it SHALL verify circular in-radius targets are hit, out-of-radius targets are not hit, and changing `radius` changes hit coverage

#### Scenario: Validate rectangle length behavior
- **WHEN** Skill Test Arena runs ground spike
- **THEN** it SHALL verify targets within rectangle length are hit, targets beyond length are not hit, and changing `length` changes hit coverage

#### Scenario: Validate rectangle width behavior
- **WHEN** Skill Test Arena runs ground spike
- **THEN** it SHALL verify targets within rectangle width are hit, targets outside width are not hit, and changing `width` changes lateral hit coverage

#### Scenario: Validate rectangle angle behavior
- **WHEN** Skill Test Arena runs ground spike
- **THEN** it SHALL verify changing angle offset or equivalent angle field changes the rectangle hit direction

#### Scenario: Validate damage timing
- **WHEN** Skill Test Arena observes a `damage_zone` skill before `hit_at_ms`
- **THEN** it SHALL verify target life is unchanged until `damage` events occur at or after `hit_at_ms`

#### Scenario: Validate modifier stack effect
- **WHEN** Skill Test Arena runs a `damage_zone` skill with the test Modifier Stack
- **THEN** the stack SHALL affect final damage, zone geometry, or status chance runtime parameters used by actual SkillEvents without writing production inventory, gem instances, or Skill Package data

### Requirement: Damage Zone AI Self-Test Report
The AI self-test report SHALL evaluate `damage_zone` skills from real Skill Test Arena results.

#### Scenario: Report frost nova circle checks
- **WHEN** an AI self-test report is generated for `active_frost_nova`
- **THEN** it SHALL check for `damage_zone`, `shape = circle`, circle origin, radius hit coverage, damage timing, cold damage, hit VFX, floating text, and radius parameter effects

#### Scenario: Report ground spike rectangle checks
- **WHEN** an AI self-test report is generated for ground spike
- **THEN** it SHALL check for `damage_zone`, `shape = rectangle`, origin, facing toward locked or nearest target, length/width/angle hit coverage, damage timing, physical damage, hit VFX, floating text, and geometry parameter effects

#### Scenario: Report Chinese conclusion and fixes
- **WHEN** a `damage_zone` AI self-test report finishes evaluation
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes

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

### Requirement: Lightning Chain Skill Package
V1 SHALL migrate `active_lightning_chain / 连锁闪电` from the old skill template path into a Skill Package.

#### Scenario: Load lightning chain Skill Package
- **WHEN** `active_lightning_chain` is migrated
- **THEN** the system SHALL load it from `configs/skills/active/active_lightning_chain/skill.yaml`

#### Scenario: Use chain behavior template
- **WHEN** the `active_lightning_chain` Skill Package is loaded
- **THEN** it SHALL declare `behavior.template = chain`

#### Scenario: Use lightning damage type
- **WHEN** the `active_lightning_chain` Skill Package is validated
- **THEN** it SHALL declare `classification.damage_type = lightning`

#### Scenario: Keep Chinese player-facing text
- **WHEN** `active_lightning_chain` name, description, damage reason, VFX feedback, screen feedback, or floating text is shown
- **THEN** the player-visible text SHALL be Chinese and SHALL come from localization keys

#### Scenario: Do not migrate other active skills
- **WHEN** this change is applied
- **THEN** it SHALL NOT create Skill Packages for `active_lava_orb`, `active_fungal_petards`, or any other active skill outside this change

### Requirement: Chain Behavior Template
V1 SHALL provide a declarative `chain` behavior template for real multi-target lightning jumps.

#### Scenario: Declare chain template fields
- **WHEN** `configs/skills/behavior_templates/chain.yaml` is validated
- **THEN** it SHALL declare a whitelist including `chain_count`, `chain_radius`, `chain_delay_ms`, `damage_falloff_per_chain`, `target_policy`, `allow_repeat_target`, `max_targets`, and `segment_vfx_key`

#### Scenario: Validate numeric chain fields
- **WHEN** a Skill Package declares `behavior.template = chain`
- **THEN** validation SHALL require positive integer `chain_count`, positive `chain_radius`, non-negative `chain_delay_ms`, and legal numeric-range `damage_falloff_per_chain`

#### Scenario: Validate target selection fields
- **WHEN** a Skill Package declares `behavior.template = chain`
- **THEN** validation SHALL require enum `target_policy` with first-version support for `nearest_not_hit`, boolean `allow_repeat_target` defaulting to `false`, and positive integer or explicitly declared `unlimited` `max_targets`

#### Scenario: Validate key-only segment VFX
- **WHEN** a Skill Package declares `segment_vfx_key`
- **THEN** validation SHALL treat it as a key-only field and SHALL NOT use it as player-visible text

#### Scenario: Reject undeclared chain params
- **WHEN** a Skill Package declares `behavior.template = chain`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, frontend-only fake params, and params not declared by the `chain` template

#### Scenario: Generate real chain segments
- **WHEN** Skill Runtime executes a `chain` skill
- **THEN** it SHALL generate one or more `chain_segment` SkillEvents from the initial target through subsequent chained targets according to `chain_count`, `chain_radius`, `target_policy`, `allow_repeat_target`, and `max_targets`

### Requirement: SkillEditor Chain Field Support
SkillEditor SHALL expose a dedicated `chain` module before the lightning chain migration is considered complete.

#### Scenario: Show all editable chain fields
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template = chain`
- **THEN** it SHALL expose editable fields for `chain_count`, `chain_radius`, `chain_delay_ms`, `damage_falloff_per_chain`, `target_policy`, `allow_repeat_target`, `max_targets`, and `segment_vfx_key`

#### Scenario: Show read-only chain summaries
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template = chain`
- **THEN** it SHALL show a read-only maximum chain segment summary and a read-only estimated total chain duration summary

#### Scenario: Validate chain editor fields
- **WHEN** SkillEditor saves `chain` behavior params
- **THEN** it SHALL validate integer fields, numeric ranges, enum fields, boolean fields, key-only `segment_vfx_key`, and unknown fields through the skill schema and behavior-template whitelist

#### Scenario: Reject invalid chain values in Chinese
- **WHEN** SkillEditor rejects invalid `chain_count`, `chain_radius`, `chain_delay_ms`, `damage_falloff_per_chain`, `target_policy`, `allow_repeat_target`, `max_targets`, `segment_vfx_key`, or undeclared fields
- **THEN** it SHALL display Chinese error text and SHALL NOT persist invalid skill data

#### Scenario: Do not save frontend-only chain params
- **WHEN** SkillEditor saves a `chain` Skill Package
- **THEN** it SHALL NOT write frontend-only fake params or any field not declared by the `chain` behavior template

### Requirement: Lightning Chain SkillEvent
V1 SHALL express `active_lightning_chain` through real SkillEvents for chain segments, damage, and presentation.

#### Scenario: Emit chain event timeline
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** it SHALL output `cast_start`, one or more `chain_segment`, one or more `damage`, `hit_vfx`, `floating_text`, and `cooldown_update` when present

#### Scenario: Include required event fields
- **WHEN** SkillEvent timeline displays `active_lightning_chain` events
- **THEN** each relevant event SHALL include `timestamp_ms`, `delay_ms`, `duration_ms`, `source_entity`, `target_entity`, `amount`, `damage_type`, `vfx_key`, `reason_key`, and `payload`

#### Scenario: Include chain segment payload
- **WHEN** Skill Runtime outputs a `chain_segment`
- **THEN** its payload SHALL include `segment_index`, `from_target`, `to_target`, `start_position`, `end_position`, `chain_radius`, `chain_delay_ms`, `damage_scale`, and `vfx_key`

#### Scenario: Select initial and subsequent targets
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** it SHALL select the nearest enemy as the initial target and then choose subsequent targets within `chain_radius` according to `target_policy`

#### Scenario: Do not repeat targets by default
- **WHEN** `allow_repeat_target = false`
- **THEN** Skill Runtime SHALL NOT choose an already-hit target for a later chain segment

#### Scenario: Apply chain count and target limits
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** `chain_count` SHALL limit the maximum number of `chain_segment` events and `max_targets` SHALL limit the maximum number of damaged targets

#### Scenario: Delay damage by chain segment timing
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** target life SHALL NOT be reduced at `cast_start`, and life reduction SHALL occur only through `damage` events at or after the corresponding `chain_segment`

#### Scenario: Apply lightning damage and falloff
- **WHEN** a target is damaged by `active_lightning_chain`
- **THEN** the `damage` event SHALL use `damage_type = lightning`, and later chain segments SHALL apply damage according to `damage_falloff_per_chain`

#### Scenario: Emit presentation events from real hits
- **WHEN** a target is hit by `active_lightning_chain`
- **THEN** Skill Runtime SHALL emit `hit_vfx` and `floating_text` aligned with the corresponding `damage` event

#### Scenario: Do not fake chain behavior
- **WHEN** Skill Runtime executes `active_lightning_chain`
- **THEN** it SHALL NOT resolve the skill as a single visual line, a release-time instant damage batch, a static fake event list, or an `active_lightning_chain` special branch in Combat Runtime

### Requirement: Lightning Chain Test Arena Acceptance
Skill Test Arena SHALL validate `active_lightning_chain` using real `chain_segment` and `damage` results.

#### Scenario: Validate three target row chain behavior
- **WHEN** Skill Test Arena runs `active_lightning_chain` in the three-target-row scenario
- **THEN** it SHALL verify the initial target is hit, subsequent targets are selected by `chain_radius`, and chain segment order is visible

#### Scenario: Validate dense pack chain behavior
- **WHEN** Skill Test Arena runs `active_lightning_chain` in the dense-pack scenario
- **THEN** it SHALL verify real multi-target jumps and SHALL verify targets are not repeated by default

#### Scenario: Validate single dummy timing
- **WHEN** Skill Test Arena runs `active_lightning_chain` in the single-dummy scenario
- **THEN** it SHALL verify the base cast, chain segment, damage, hit VFX, floating text, and no life reduction before the relevant damage event

#### Scenario: Validate chain count parameter
- **WHEN** Skill Test Arena changes `chain_count`
- **THEN** the number of emitted `chain_segment` events SHALL change according to the configured limit

#### Scenario: Validate chain radius parameter
- **WHEN** Skill Test Arena changes `chain_radius`
- **THEN** the set of reachable chained targets SHALL change according to the configured radius

#### Scenario: Validate chain delay parameter
- **WHEN** Skill Test Arena changes `chain_delay_ms`
- **THEN** the time interval between chain segments and corresponding damage events SHALL change

#### Scenario: Validate damage falloff parameter
- **WHEN** Skill Test Arena changes `damage_falloff_per_chain`
- **THEN** later chain segment damage amounts SHALL change according to the configured falloff

#### Scenario: Validate modifier stack effects
- **WHEN** Skill Test Arena runs `active_lightning_chain` with the test Modifier Stack
- **THEN** the stack SHALL affect final damage or chain runtime parameters used by actual SkillEvents without writing production inventory, gem instances, or Skill Package data

### Requirement: Lightning Chain AI Self-Test Report
The AI self-test report SHALL evaluate `active_lightning_chain` from real Skill Test Arena results.

#### Scenario: Generate lightning chain report
- **WHEN** `python tools\generate_skill_test_report.py --skill active_lightning_chain --scenario dense_pack` is run
- **THEN** it SHALL generate a Chinese AI self-test report based on real test results

#### Scenario: Check required chain events
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether `chain_segment`, multiple `chain_segment` events, `damage`, `hit_vfx`, and `floating_text` exist

#### Scenario: Check chain timing and damage type
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether damage is not earlier than the corresponding `chain_segment`, no HP is reduced at `cast_start`, and `damage_type = lightning`

#### Scenario: Check target selection behavior
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether multiple targets are hit, whether the default behavior avoids repeated targets, and whether out-of-radius targets are not chained

#### Scenario: Check chain parameter effects
- **WHEN** the AI self-test report evaluates `active_lightning_chain`
- **THEN** it SHALL check whether changing `chain_count`, `chain_radius`, `chain_delay_ms`, and `damage_falloff_per_chain` changes real chain results

#### Scenario: Report Chinese conclusion and fixes
- **WHEN** the AI self-test report finishes evaluating `active_lightning_chain`
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes

### Requirement: SkillEditor projectile launch point direct adjustment
SkillEditor SHALL provide a direct scene adjustment flow for editable projectile launch positions that updates the current draft `behavior.params.spawn_offset` without bypassing existing save validation.

#### Scenario: Enter direct adjustment from launch position section
- **WHEN** the user opens an editable Skill Package whose behavior template supports persisted `spawn_offset`
- **THEN** the "发射位置" section SHALL provide a Chinese "直接调整" action that enters scene adjustment mode

#### Scenario: Ice shards uses generic projectile spread
- **WHEN** `active_ice_shards` is editable in SkillEditor
- **THEN** it SHALL use the generic `projectile` behavior template with projectile count and spread-angle params rather than requiring a separate fan-projectile template

#### Scenario: Hide editor shell during adjustment
- **WHEN** scene adjustment mode is active
- **THEN** the full SkillEditor panel SHALL be temporarily hidden while the editor draft remains mounted and available

#### Scenario: Drag launch point in battle scene
- **WHEN** the user drags the launch-point handle in the battle scene
- **THEN** SkillEditor SHALL convert the dragged scene position into `behavior.params.spawn_offset.x` and `behavior.params.spawn_offset.y` relative to the current cast source in the editor draft

#### Scenario: Confirm adjusted position
- **WHEN** the user confirms the adjusted launch position
- **THEN** SkillEditor SHALL return to the full editor panel with the numeric launch offset fields and read-only launch-point preview reflecting the adjusted draft value

#### Scenario: Cancel adjusted position
- **WHEN** the user cancels scene adjustment mode
- **THEN** SkillEditor SHALL restore the launch offset values that existed before entering adjustment mode and return to the full editor panel

#### Scenario: Save still uses existing validation
- **WHEN** the user saves after confirming a directly adjusted launch position
- **THEN** SkillEditor SHALL use the existing save flow, schema validation, and behavior-template whitelist before writing the Skill Package

#### Scenario: Do not expose unsupported templates
- **WHEN** the current Skill Package behavior template does not allow persisted `spawn_offset`
- **THEN** SkillEditor SHALL NOT enable direct launch-position adjustment for that package

#### Scenario: No runtime behavior change
- **WHEN** Skill Runtime executes a projectile skill after this editor change is applied
- **THEN** projectile spawning, targeting, trajectory, damage, and SkillEvent semantics SHALL remain determined by existing runtime logic and the saved `spawn_offset` value

