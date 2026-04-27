# Tasks

## Phase 0：项目现状扫描与约束确认

**目标：** 确认当前项目结构、OpenSpec 状态、V1 来源文档和禁止越界范围。

**涉及模块：** OpenSpec、项目根目录、文档输入。

**实施状态：**

- [x] 已确认当前 OpenSpec active changes 和 specs 状态。
- [x] 已确认 change 名称为 `implement-v1-minimal-sudoku-gem-loop`。
- [x] 已确认 V1 来源范围来自《V1正式最小循环开发文档.md》。
- [x] 已确认当前目录不是 git 仓库，无可确认的当前分支。
- [x] 已确认本阶段不写 gameplay 代码。

**禁止越界事项：**

- 不写 gameplay 代码。
- 不修改运行时代码。
- 不从旧 Demo 或其他项目复制实现。
- 不扩展 V1 以外系统。

**验收标准：**

- 已确认当前 OpenSpec active changes 和 specs 状态。
- 已确认 V1 来源范围来自《V1正式最小循环开发文档.md》。
- 已确认本 change 名称为 `implement-v1-minimal-sudoku-gem-loop`。
- 已确认本阶段只做现状扫描与约束确认，不写 gameplay 代码。

**推荐验证命令：**

```powershell
openspec.cmd list --json
Get-ChildItem -Recurse openspec
```

## Phase 1：配置结构与校验框架

**目标：** 建立 V1 配置拆分和校验边界，保证正式项目结构而不是 Demo 大表。

**涉及模块：** Core Foundation、Content Rule Data。

**实施状态：**

- [x] 已创建 `configs/` 拆分结构。
- [x] 已建立 V1 配置校验入口 `tools/validate_v1_configs.py`。
- [x] 已建立玩家属性配置。
- [x] 已覆盖 ID 唯一性、引用存在性、标签合法性、stat 合法性、gem_type 合法性、中文本地化 key 存在性、value_range 合法性、affix group 合法性。
- [x] 已运行配置校验并通过。

**禁止越界事项：**

- 禁止创建 `all.xxx.toml` 大杂烩配置。
- 禁止把行 / 列 / 宫规则写死到技能代码。
- 禁止让内部 ID 直接作为玩家可见文案。

**验收标准：**

- 配置结构按 `configs/core/`、`configs/player/`、`configs/combat/`、`configs/gems/`、`configs/sudoku_board/`、`configs/skills/`、`configs/affixes/`、`configs/loot/`、`configs/localization/` 拆分。
- 校验框架覆盖 ID 唯一性、引用存在性、标签合法性、stat 合法性、gem_type 合法性、中文本地化 key 存在性、value_range 合法性、affix group 合法性。
- 玩家属性覆盖 V1 指定的生命、移动、拾取、技能槽、伤害、速度、冷却、范围、投射物、暴击、状态概率和四类伤害提高属性。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 2：内容规则数据

**目标：** 定义 V1 可掉落、可展示、可计算的宝石、标签、技能模板、伤害类型、状态和中文本地化规则。

**涉及模块：** Content Rule Data。

**实施状态：**

- [x] 已完成 8 个主动技能宝石定义。
- [x] 已完成 24 个辅助宝石结构定义。
- [x] 已补全宝石标签、伤害类型、状态效果占位和技能模板定义。
- [x] 已补全 Phase 2 所需中文本地化 key。
- [x] 已扩展配置校验并覆盖 Phase 2 内容规则数据。

**禁止越界事项：**

- 禁止加入装备、地图、货币、腐化、法力、复杂属性成长、多职业内容。
- 禁止把辅助宝石做成无标签过滤的普通数值插件。
- 禁止引入英文玩家可见文案。

**验收标准：**

- 主动技能宝石覆盖 8 个：`active_fire_bolt`、`active_ice_shards`、`active_lightning_chain`、`active_frost_nova`、`active_puncture`、`active_penetrating_shot`、`active_lava_orb`、`active_fungal_petards`。
- 辅助宝石覆盖 24 个结构：通用技能改造 8 个、伤害类型强化 4 个、投射物 / 范围专项 4 个、高风险高收益 3 个、技能等级类 2 个、行列宫导管 3 个。
- 宝石标签覆盖基础标签、来源标签、伤害类型标签、技能行为标签、辅助功能标签、盘面关系标签。
- 所有玩家可见对象都有中文本地化 key。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 3：数独宝石盘运行时

**目标：** 实现 9x9 数独盘数据、上盘 / 下盘、合法性检查和关系计算规格。

**涉及模块：** Gem Board Runtime、Inventory / Storage、Presentation UX。

**实施状态：**

- [x] 已实现 9x9 数独宝石盘数据结构。
- [x] 已实现宝石上盘 / 下盘状态更新。
- [x] 已实现 gem_type 合法性与同行 / 同列 / 同宫重复检查。
- [x] 已实现同行 / 同列 / 同宫 / 上下左右相邻关系计算。
- [x] 已输出支持 UI 高亮和影响预览的数据结构。
- [x] 已实现空盘 / 无主动技能宝石禁止进入战斗判定。
- [x] 已增加 Phase 3 单元测试并通过。

**禁止越界事项：**

- 禁止把数独盘做成普通摆放限制。
- 禁止在盘面运行时生成掉落。
- 禁止在盘面运行时直接播放技能表现。

**验收标准：**

- 盘面为 9 行、9 列、9 个 3x3 宫。
- 每颗上盘宝石必须有 `gem_type_1` 到 `gem_type_9`。
- 同行、同列、同宫内相同 `gem_type` 判定为非法。
- 支持上下左右相邻关系。
- 支持同行、同列、同宫、相邻关系高亮和影响预览所需数据。
- 无主动技能宝石或空盘时禁止进入战斗。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 4：词缀、掉落、库存

**目标：** 定义并实现宝石实例、稀有度、随机词缀、掉落池、拾取入库和库存管理规格。

**涉及模块：** Content Rule Data、Loot Runtime、Inventory / Storage、Presentation UX。

**实施状态：**

- [x] 已实现宝石实例数据结构，基础定义与实例分离。
- [x] 已实现 normal / magic / rare 稀有度与随机词缀数量规则。
- [x] 已实现词缀定义结构、词缀互斥组校验和盘面词缀方向配置。
- [x] 已实现支持随机对象注入的随机词缀生成流程。
- [x] 已实现掉落池读取、权重随机、宝石掉落实例生成和拾取入库。
- [x] 已扩展库存管理，支持保存、锁定、筛选、排序和上盘 / 下盘状态保留。
- [x] 已增加 Phase 4 单元测试并通过。

**禁止越界事项：**

- 禁止延后随机词缀。
- 禁止掉落装备、货币、地图、材料。
- 禁止把基础宝石定义复制进宝石实例。

**验收标准：**

- 宝石基础定义与宝石实例分离。
- 稀有度覆盖 `normal` / 普通 / 0 条词缀、`magic` / 魔法 / 1 条词缀、`rare` / 稀有 / 2 条词缀。
- 词缀覆盖 `prefix`、`suffix`、`implicit`。
- 词缀大类覆盖技能数值、标签强化、盘面来源、盘面接受、高风险代价、词缀互斥组。
- 盘面词缀方向覆盖 `source_power_row`、`source_power_column`、`source_power_box`、`target_power_row`、`target_power_column`、`target_power_box`。
- 掉落流程能生成宝石实例，拾取后进入库存，库存支持上盘 / 下盘状态。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 5：技能最终效果计算

**目标：** 定义并实现 source / target 效果路由与技能最终 modifier 汇总。

**涉及模块：** Gem Board Runtime、Skill Runtime、Content Rule Data。

**实施状态：**

- [x] 已实现 source / target 效果路由。
- [x] 已实现关系系数读取与应用。
- [x] 已实现主动技能宝石自身随机词缀应用。
- [x] 已实现辅助宝石基础效果与随机词缀应用。
- [x] 已实现行 / 列 / 宫导管放大。
- [x] 已实现 additive modifier 与 final modifier 汇总。
- [x] 已输出最终技能实例并保留 applied_modifiers 来源信息。
- [x] 已增加 Phase 5 单元测试并通过。

**禁止越界事项：**

- 禁止无限递归传播。
- 禁止导管产生新的二次传播链。
- 禁止同一来源宝石对同一目标宝石同一 stat 重复结算。
- 禁止引入复杂表达式解释器。

**验收标准：**

- 效果路由覆盖 Source、Target、Relation、Power。
- 关系系数覆盖相邻、同行、同列、同宫。
- 相邻关系与同行 / 同列重叠时只结算一次。
- 导管只放大行 / 列 / 宫传播效果。
- 技能最终效果按“主动技能基础定义 -> 主动宝石随机词缀 -> 可影响它的辅助宝石 -> 辅助基础效果 -> 辅助随机词缀 -> 行 / 列 / 宫导管放大 -> additive -> final -> 最终技能实例”顺序计算。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 6：最小战斗循环

**目标：** 让 V1 战斗只服务刷宝石闭环，支持自动释放已激活技能、击杀怪物、触发宝石掉落和拾取。

**涉及模块：** Combat Runtime、Skill Runtime、Loot Runtime、Inventory / Storage。

**实施状态：**

- [x] 已实现最小 Combat Runtime。
- [x] 已接入 Phase 5 产出的最终技能实例。
- [x] 已实现战斗中按 final_cooldown_ms 自动释放已激活主动技能。
- [x] 已实现最小玩家、怪物、掉落宝石和战斗会话实体。
- [x] 已实现怪物生命、受击、死亡。
- [x] 已实现击杀事件触发 Loot Runtime 生成宝石掉落。
- [x] 已实现 pickup_radius 范围判定和拾取入库。
- [x] 已增加 Phase 6 单元测试并通过。

**禁止越界事项：**

- 禁止加入复杂关卡目标。
- 禁止加入装备、货币、地图奖励。
- 禁止加入法力或复杂防御体系。

**验收标准：**

- 战斗中自动释放盘面已激活主动技能。
- 技能表现使用 Phase 5 产出的最终技能实例。
- 击杀怪物触发宝石掉落。
- 拾取范围由 `pickup_radius` 支持。
- 拾取宝石进入库存并保留随机词缀。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 7：中文 UI 与体验闭环

**目标：** 完成玩家可见的宝石查看、数独盘调整、技能预览、掉落提示和战斗反馈，形成闭环体验。

**涉及模块：** Presentation UX、Inventory / Storage、Gem Board Runtime、Skill Runtime、Combat Runtime、Loot Runtime。

**实施状态：**

- [x] 已实现最小中文展示层，覆盖宝石详情、数独盘展示、非法提示、高亮数据、影响范围预览、技能最终效果预览、战斗 HUD、掉落提示与最小体验闭环测试。

**禁止越界事项：**

- 禁止英文玩家可见文案。
- 禁止 UI 自行判定核心规则。
- 禁止把规格外系统做成 UI 入口。

**验收标准：**

- 宝石详情展示中文名称、类型、标签、基础效果或辅助效果、随机词缀、词缀数值、可影响对象、当前实际生效对象。
- 数独盘 UI 展示 9x9 格子、3x3 宫分区、非法摆放提示、同行 / 同列 / 同宫高亮、影响范围预览、技能最终效果预览。
- 战斗 HUD、掉落提示、非法摆放提示、技能最终效果说明全部为中文。
- 玩家能完成“刷宝石 -> 看词缀 -> 调盘面 -> 技能表现变化 -> 再刷宝石”的闭环。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 7B：WebApp 可操作入口

**目标：** 在 Phase 7 Python 展示层基础上补充浏览器可打开、可操作的 WebApp 入口，让玩家能在页面中完成 V1 最小循环。

**涉及模块：** Presentation UX、WebApp Entry、Inventory / Storage、Gem Board Runtime、Skill Runtime、Combat Runtime、Loot Runtime、Core Foundation。

**实施状态：**

- [x] 已创建 Vite + React + TypeScript WebApp 工程入口。
- [x] 已创建最小 Python API / 适配层，供 WebApp 复用当前 V1 规则能力。
- [x] 已实现宝石库存列表、宝石详情面板和宝石随机词缀展示。
- [x] 已实现 9x9 数独宝石盘可视化、选中格子、上盘和下盘操作。
- [x] 已实现数独合法性中文提示，以及同行 / 同列 / 同宫 / 相邻高亮。
- [x] 已实现技能最终效果预览和 modifier 来源说明。
- [x] 已实现最小战斗按钮、战斗结果、掉落宝石和拾取入库展示。
- [x] 已增加 WebApp 构建与 smoke 测试，确认中文标题、库存、9x9 盘、技能预览、战斗控制存在且不出现明显英文玩家可见按钮文本。

**禁止越界事项：**

- 禁止只做 Python presenter 就结束。
- 禁止只做静态假 UI。
- 禁止前端重新硬编码一套与 Python 规则不一致的数独 / 掉落 / 技能计算规则。
- 禁止创建 demo / prototype / temp / scratch 目录。
- 禁止引入装备、地图、货币、腐化、法力、属性成长、抗性、防御、赛季、多职业。
- 禁止引入英文玩家可见文案。

**验收标准：**

- WebApp 可在浏览器打开，并显示标题“数独宝石流放like V1”。
- 主界面包含左侧宝石库存、中间 9x9 数独宝石盘、右侧宝石详情与技能预览、底部战斗控制与掉落日志。
- 玩家可以选择库存宝石、选择格子、上盘、下盘，并看到盘面合法性提示与关系高亮。
- 玩家可以查看宝石中文详情、随机词缀、可影响对象、当前实际生效对象。
- 玩家可以预览已激活主动技能的最终伤害、最终冷却、投射物数量、范围倍率、速度倍率和 modifier 来源。
- 玩家可以点击开始战斗，看到自动释放技能日志、击杀结果、掉落宝石，并拾取入库刷新库存。
- 所有玩家可见标题、按钮、提示、HUD、日志和错误均为中文。

**推荐验证命令：**

```powershell
npm install
npm run build
npm test
python tools\validate_v1_configs.py
python -m unittest discover -s tests
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
```

## Phase 8：验证、构建、回归测试

**目标：** 对 V1 最小循环执行规格、配置、构建和关键行为回归验证。

**涉及模块：** 全部 V1 模块。

**实施状态：**

- [x] 已完成 WebApp 构建、smoke 测试、Python 配置校验、Python 单元测试与 OpenSpec strict validate 验证。

**禁止越界事项：**

- 禁止用跳过校验来通过构建。
- 禁止用硬编码内容绕过配置校验。
- 禁止在回归阶段加入 V1 外系统补丁。

**验收标准：**

- OpenSpec strict validate 通过。
- 配置校验通过。
- WebApp 构建通过。
- 单元测试覆盖配置校验、数独合法性、关系计算、词缀生成、效果路由、技能 modifier 汇总。
- 集成测试覆盖掉落、拾取、入库、上盘 / 下盘、自动释放技能、中文 UI 关键文案。
- WebApp smoke 测试覆盖中文标题、库存区域、9x9 数独盘区域、技能预览区域、战斗控制区域和明显英文玩家可见按钮文本检查。
- 回归测试确认 V1 禁止系统没有玩家可见入口。

**推荐验证命令：**

```powershell
openspec.cmd validate implement-v1-minimal-sudoku-gem-loop --strict
# 后续实现阶段按项目实际命令补充：
# npm test
# npm run build
```
