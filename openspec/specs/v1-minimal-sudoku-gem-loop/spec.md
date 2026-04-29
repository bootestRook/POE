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

