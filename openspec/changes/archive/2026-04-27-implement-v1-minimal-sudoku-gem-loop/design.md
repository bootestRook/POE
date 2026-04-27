## Context

《V1正式最小循环开发文档.md》定义了一个以数独宝石盘为核心构筑系统的正式 V1。V1 的关键差异点不是“流放辅助宝石 + 数独摆放限制”，而是“宝石随机词缀 + 数独盘面关系 + 技能表现变化”。因此设计必须把数独盘作为效果路由器处理，把随机词缀作为刷宝循环的必需内容处理。

当前仓库 OpenSpec 结构为空白：`openspec/specs/` 无 baseline specs，`openspec/changes/` 无 active changes。因此本 change 新增一组 V1 最小循环规格，不修改既有业务代码。

## Goals / Non-Goals

**Goals:**

- 固化 V1 正式最小循环边界。
- 明确八个模块边界，避免 Demo 式脚本堆叠。
- 明确配置拆分结构和校验目标。
- 明确宝石基础定义与宝石实例分离。
- 明确 9x9 数独盘合法性、关系计算和效果路由。
- 明确随机词缀生成、掉落、库存、上盘、战斗之间的数据流。
- 明确技能最终效果计算顺序。
- 明确中文 UI 展示要求。

**Non-Goals:**

- 不实现 V1 外系统业务代码。
- 不引入装备、装备词缀、地图词缀、腐化、复杂货币、法力、力量 / 敏捷 / 智力成长、完整抗性、完整护甲 / 闪避 / 能量护盾、赛季、复杂技能树、多职业。
- 不从旧 Demo 或其他项目复制实现。
- 不把数独盘降级成普通摆放限制。
- 不把辅助宝石降级成普通数值插件。
- 不延后随机词缀。
- 不引入英文玩家可见文案。

## Decisions

### 模块边界

V1 按以下八个模块推进：

| 模块 | 职责 | 禁止越界 |
|---|---|---|
| Core Foundation | 配置加载、配置校验、ID 引用解析、随机数与随机种子、事件、时间、日志、调试开关、本地存档基础 | 不写具体宝石、技能、怪物规则；不写 UI 文案 |
| Content Rule Data | 玩家属性、伤害类型、宝石标签、主动技能宝石、辅助宝石、词缀、数独盘规则、技能模板、状态、掉落池、中文本地化 | 不写战斗运行时、不操作实体、不处理输入和渲染 |
| Gem Board Runtime | 9x9 盘面、宝石放置/移除、数独合法性、行/列/宫/相邻关系、source/target 关系、modifier 汇总触发 | 不生成掉落、不决定怪物行为、不播放技能表现 |
| Skill Runtime | 技能实例化、冷却、释放、投射物、范围伤害、命中、状态、标签匹配、modifier 应用 | 不计算数独合法性、不生成词缀、不决定掉落 |
| Combat Runtime | 玩家、怪物、怪物生成、移动、生命/死亡、战斗时间、击杀事件、掉落触发、胜负 | 不承担宝石库存和盘面编辑 |
| Loot Runtime | 掉落池读取、权重、宝石基础类型随机、随机词缀生成、掉落物实例化、拾取、入库 | 只掉落宝石，不掉落装备、货币、地图、材料 |
| Inventory / Storage | 宝石实例保存、基础定义引用、随机词缀保存、锁定、筛选、排序、上盘/下盘、本地存档 | 不做复杂背包格子形状 |
| Presentation UX | 宝石盘 UI、详情 UI、词缀展示、合法性提示、技能最终效果预览、战斗 HUD、掉落提示、中文文案 | 不承载核心规则判定 |
| WebApp Entry | 浏览器可打开页面、库存列表、9x9 数独盘操作、宝石详情、技能预览、战斗控制、掉落拾取展示 | 不重新实现一套与 Python 规则层不一致的数独、掉落或技能计算规则 |

### 配置拆分

V1 配置必须采用多文件拆分，禁止 `all.xxx.toml` 大杂烩配置。建议结构固定为：

```text
configs/
  core/
    id_rules.toml
    random_rules.toml

  player/
    player_base_stats.toml
    player_stat_defs.toml

  combat/
    damage_types.toml
    hit_rules.toml
    status_effects.toml

  gems/
    gem_type_defs.toml
    active_skill_gems.toml
    support_gems.toml
    gem_tag_defs.toml
    gem_instance_schema.toml

  sudoku_board/
    board_layout.toml
    placement_rules.toml
    relation_rules.toml
    effect_routing_rules.toml

  skills/
    skill_templates.toml
    skill_scaling_rules.toml

  affixes/
    affix_defs.toml
    affix_spawn_rules.toml
    affix_groups.toml
    affix_tiers.toml

  loot/
    gem_drop_pools.toml
    drop_weight_rules.toml

  localization/
    zh_cn.toml
```

拆分原则：

- 单文件单职责。
- 定义和实例分离。
- 标签和效果分离。
- 中文文案独立。
- 掉落、词缀、权重随机规则独立。
- 盘面行、列、宫、相邻规则独立，不写死在技能代码中。

### 玩家属性集合

`player_stat_defs.toml` 必须覆盖以下 V1 属性：

- `max_life` / 最大生命；
- `current_life` / 当前生命；
- `move_speed` / 移动速度；
- `pickup_radius` / 拾取范围；
- `skill_slots_active` / 激活技能数量；
- `damage_add_percent` / 伤害提高；
- `damage_final_percent` / 最终伤害修正；
- `attack_speed_add_percent` / 攻击速度提高；
- `cast_speed_add_percent` / 施法速度提高；
- `skill_speed_final_percent` / 技能速度最终修正；
- `cooldown_reduction_percent` / 冷却缩减；
- `added_cooldown_ms` / 附加冷却；
- `area_add_percent` / 范围提高；
- `projectile_count_add` / 投射物数量增加；
- `projectile_speed_add_percent` / 投射物速度提高；
- `crit_chance_add_percent` / 暴击率提高；
- `crit_damage_add_percent` / 暴击伤害提高；
- `status_chance_add_percent` / 状态施加概率提高；
- `physical_damage_add_percent` / 物理伤害提高；
- `fire_damage_add_percent` / 火焰伤害提高；
- `cold_damage_add_percent` / 冰霜伤害提高；
- `lightning_damage_add_percent` / 闪电伤害提高。

### 宝石基础定义与宝石实例分离

基础宝石定义描述可掉落内容本身，例如内部 ID、中文名称 key、`gem_type`、标签、基础效果、适用条件、技能模板引用。

宝石实例描述玩家实际获得的个体，例如：

```toml
[gem_instance]
instance_id = "gem_inst_000001"
base_gem_id = "active_fire_bolt"
gem_type = "gem_type_1"
rarity = "magic"
level = 1
prefix_affixes = ["affix_damage_percent_t1"]
suffix_affixes = ["affix_row_source_power_t1"]
implicit_affixes = []
locked = false
```

运行时和存档只能保存实例对基础定义的引用，不能把基础定义复制进实例。

### 主动技能宝石与辅助宝石

V1 主动技能宝石固定覆盖 8 个：

| ID | 中文名 |
|---|---|
| `active_fire_bolt` | 火焰弹 |
| `active_ice_shards` | 冰棱散射 |
| `active_lightning_chain` | 连锁闪电 |
| `active_frost_nova` | 冰霜新星 |
| `active_puncture` | 穿刺 |
| `active_penetrating_shot` | 贯穿射击 |
| `active_lava_orb` | 熔岩球 |
| `active_fungal_petards` | 真菌爆弹 |

V1 辅助宝石固定覆盖 24 个结构：

| 类别 | 数量 | 说明 |
|---|---:|---|
| 通用技能改造 | 8 | 攻速、施法、急速、冷却、重击、范围、稳定输出、精密等 |
| 伤害类型强化 | 4 | 物理、火焰、冰霜、闪电 |
| 投射物 / 范围专项 | 4 | 额外投射、散射、投射物速度、范围放大 |
| 高风险高收益 | 3 | 过载、超量杀伤、暴击爆发 |
| 技能等级类 | 2 | 元素精通、战技精通 |
| 行列宫导管 | 3 | 行导管、列导管、宫导管 |

辅助宝石必须显式声明 `apply_filter`，不能只通过 stat 字段名隐含适用对象。

### 数独盘合法性

V1 使用标准 9x9 数独盘：

- 9 行；
- 9 列；
- 9 个 3x3 宫；
- 每颗上盘宝石必须有 `gem_type`，范围为 `gem_type_1` 到 `gem_type_9`。

合法性规则：

- 同一行不能有重复 `gem_type`。
- 同一列不能有重复 `gem_type`。
- 同一宫不能有重复 `gem_type`。
- 至少存在 1 个主动技能宝石才允许进入战斗。
- 空盘不可进入战斗。

### 行 / 列 / 宫 / 相邻关系

V1 只计算四类关系：

- 同行：两颗宝石处于同一横行。
- 同列：两颗宝石处于同一纵列。
- 同宫：两颗宝石处于同一个 3x3 宫。
- 相邻：上下左右四方向相邻。

V1 暂不实现对角、骑士步、全局连接、指定编号大小连接、奇偶连接、顺子连接。

默认关系系数：

| 关系 | 系数 |
|---|---:|
| 相邻 | 1.25 |
| 同行 | 1.00 |
| 同列 | 1.00 |
| 同宫 | 1.00 |

如果两颗宝石同时满足相邻和同行 / 同列，只按相邻关系计算一次，不额外叠加同行 / 同列。

### source / target 效果路由

V1 使用固定枚举模型，不做复杂表达式解释器：

```text
最终传播效果 = 来源宝石效果 x 来源强度 x 目标接受强度 x 关系系数
```

概念定义：

- Source：提供效果的宝石。
- Target：接收效果的宝石。
- Relation：两颗宝石之间的盘面关系。
- Power：对应关系下的传播或接受强度。

V1 传播限制：

- 辅助宝石可以影响主动技能宝石。
- 导管宝石可以放大行 / 列 / 宫传播。
- 主动技能宝石默认不反向影响辅助宝石，除非拥有明确词缀。
- 同一来源宝石对同一目标宝石同一 stat 只结算一次。
- 不做无限递归传播。
- 导管只放大，不产生新的二次传播链。

### 宝石随机词缀生成流程

V1 稀有度覆盖：

| 稀有度 ID | 中文名 | 随机词缀数量 |
|---|---|---:|
| `normal` | 普通 | 0 |
| `magic` | 魔法 | 1 |
| `rare` | 稀有 | 2 |

V1 词缀类型覆盖：

- `prefix`；
- `suffix`；
- `implicit`；
- 技能数值词缀；
- 标签强化词缀；
- 盘面来源词缀；
- 盘面接受词缀；
- 高风险代价词缀；
- 词缀互斥组。

盘面词缀方向必须覆盖：

- `source_power_row`；
- `source_power_column`；
- `source_power_box`；
- `target_power_row`；
- `target_power_column`；
- `target_power_box`。

生成流程：

```text
确定掉落宝石基础类型
-> 确定宝石稀有度
-> 根据稀有度确定词缀数量
-> 根据宝石标签筛选可用词缀
-> 根据词缀权重随机候选
-> 检查词缀互斥组
-> 生成词缀数值范围
-> 保存为宝石实例
```

### 技能最终效果计算顺序

V1 固定使用以下顺序：

```text
读取主动技能基础定义
-> 应用主动技能宝石自身随机词缀
-> 查找盘面中可影响它的辅助宝石
-> 应用辅助宝石基础效果
-> 应用辅助宝石随机词缀
-> 应用行 / 列 / 宫导管放大
-> 汇总 additive modifier
-> 汇总 final modifier
-> 输出最终技能实例
```

数值层级只保留：

- base：技能模板提供的基础伤害、基础冷却等。
- additive：伤害提高、范围提高等同类相加。
- final：最终伤害、最终技能速度等独立乘算。

### 掉落、库存、上盘、战斗之间的数据流

```text
Combat Runtime 击杀事件
-> Loot Runtime 读取 gem_drop_pools 与 drop_weight_rules
-> Loot Runtime 选择基础宝石、稀有度并生成随机词缀
-> Loot Runtime 生成掉落物实例
-> 拾取进入 Inventory / Storage
-> Presentation UX 展示宝石详情和词缀
-> 玩家从库存上盘或下盘
-> Gem Board Runtime 校验数独合法性并计算关系
-> Skill Runtime 按最终 modifier 生成技能实例
-> Combat Runtime 自动释放已激活技能
```

### 中文 UI 要求

所有玩家可见文本必须使用中文，并从 `configs/localization/zh_cn.toml` 或等价本地化资源读取。必须覆盖：

- 宝石名称；
- 技能名称；
- 辅助宝石名称；
- 标签显示名；
- 词缀名称；
- 词缀说明；
- 非法摆放提示；
- 技能最终效果说明；
- 掉落提示；
- 战斗 HUD。

### WebApp 可操作入口

V1 不允许只停留在 Python presenter / view model。Presentation UX 必须提供可在浏览器打开的 WebApp 入口，作为玩家实际操作最小循环的第一屏。

WebApp 技术边界：

- 若项目已有前端技术栈，沿用现有技术栈；当前项目没有 `package.json` 时，建立最小正式 Vite + React + TypeScript 工程。
- WebApp 必须通过最小后端或适配层调用当前 Python V1 规则层，不能在前端重新硬编码一套数独合法性、掉落、库存或技能最终效果计算规则。
- WebApp 只承载展示和交互编排，不承担核心规则判定。
- 不创建 `demo`、`prototype`、`temp`、`scratch` 等临时目录。

WebApp 主界面固定为：

- 左侧：宝石库存列表。
- 中间：9x9 数独宝石盘。
- 右侧：宝石详情与技能最终效果预览。
- 底部：战斗控制与掉落日志。

WebApp 必须支持：

- 查看宝石中文名、主动 / 辅助类型、稀有度、`gem_type` 和随机词缀摘要。
- 选择宝石并放入选中的 9x9 格子。
- 从盘面下盘宝石。
- 展示数独合法性中文提示。
- 展示同行、同列、同宫、相邻高亮。
- 展示宝石详情、标签、可影响对象和当前实际生效对象。
- 展示已激活主动技能、最终伤害、最终冷却、投射物数量、范围倍率、速度倍率和 modifier 来源。
- 点击“开始战斗”，展示玩家生命、怪物数量、自动释放技能日志、击杀结果、掉落宝石和拾取入库结果。
- 所有按钮、标题、提示、HUD、日志、错误都必须是中文玩家可见文本。

## Risks / Trade-offs

- 24 个辅助宝石和随机词缀会增加配置校验压力；需要优先建立校验框架，避免内容表失控。
- source / target 路由如果边界不严，会产生重复结算或递归传播；V1 必须固定“同一来源同一目标同一 stat 只结算一次”和“导管只放大”的限制。
- 中文 UI 要求会增加本地化 key 校验工作，但这是避免英文玩家可见文案的必要成本。
- V1 明确不做装备、法力、复杂成长等系统，短期内容丰富度会受限；这是为了确保刷宝石和数独盘关系成为项目核心。
