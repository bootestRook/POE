## Why

当前 V1 技能系统已经能把盘面、宝石和战斗串起来，但技能语义正在退化为“即时扣血 + 换皮特效”：Combat Runtime 直接拿 `FinalSkillInstance.final_damage` 扣血，WebApp 再根据 `behavior_type` 和 `visual_effect` 猜测表现。这个结构无法支撑高品质技能表现、真实投射物命中时机、链式/延迟/环绕等行为差异，也会让后续 SkillEditor 被迫反向适配前后端分叉逻辑。

本 change 的目标是重构技能系统框架，把技能定义、行为模板、最终实例、战斗事件和 WebApp 表现统一到可校验、可扩展、可逐步迁移的 Skill Package 管线中。当前仍存在 active change `refactor-three-gem-kinds-v1-phase2`，本 change 不修改它、不覆盖它；后续 Apply 应在三类宝石字段迁移完成后进行，或至少兼容 `gem_kind` / `sudoku_digit` 字段模型。

## What Changes

- 将集中式 `configs/skills/skill_templates.toml` 迁移方向定义为每个主动技能一个 Skill Package：`configs/skills/active/<skill_id>/skill.yaml`。
- 新增统一 `configs/skills/schema/skill.schema.json` 的设计要求，用于校验技能定义字段、枚举、引用和玩家可见中文本地化 key。
- 定义白名单 Behavior Template 机制：技能 YAML 只能引用受控模板和参数，不允许写任意脚本、复杂 DSL 或表达式解释器。
- 定义 V1 第一批行为模板：`projectile`、`fan_projectile`、`chain`、`player_nova`、`melee_arc`、`line_pierce`、`orbit`、`delayed_area`。
- 扩展 `FinalSkillInstance` 职责：承接主动宝石、被动、辅助、数独关系和 modifier 聚合后的最终技能参数，作为 Skill Runtime 输入。
- 新增 `SkillEvent[]` 作为 Runtime 和 WebApp 的共同语言，覆盖释放、投射物、命中、伤害、VFX、浮字、冷却等事件。
- 明确 Combat Runtime 不再写具体技能分支；Combat Runtime 调用 Skill Runtime 并消费结算事件，不负责解释技能类型。
- 明确 WebApp 不再根据 `behavior_type + visual_effect` 猜技能表现，而是消费真实 `SkillEvent[]` 渲染表现。
- 第一轮 Apply 只允许实现 `active_fire_bolt` 垂直切片，验证 Skill Package、schema、FinalSkillInstance、SkillEvent、Combat Runtime 和 WebApp 事件消费链路。
- 其他 7 个主动技能第一轮保持旧行为，不得半迁移、不得破坏现有可运行能力。
- 后续阶段正式加入 SkillEditor V0：浏览器内打开已迁移 Skill Package，按模块编辑 schema 和 behavior template 白名单允许字段。
- 后续阶段正式加入 Modifier 测试栈：在编辑器中临时选择辅助宝石效果或 scaling modifier，用于测试技能表现，不写入真实宝石实例或 `skill.yaml`。
- 后续阶段正式加入 Skill Test Arena：用受控木桩和怪物布局验证技能行为、伤害时机、命中目标和 SkillEvent 序列。
- 后续阶段正式加入 SkillEvent 时间线查看器：显示真实事件序列和关键字段，辅助判断表现与结算是否一致。
- 后续阶段正式加入 AI 自测报告：基于真实测试结果生成中文 Markdown 或 JSON 报告，对比玩家侧描述、SkillEvent、伤害和命中结果。
- SkillEditor 不采用复杂节点编辑器，不实现任意脚本 DSL 或复杂表达式解释器。
- 所有玩家可见文本必须使用中文；OpenSpec 关键字、字段名和枚举名可保留英文。

### 为什么使用 Skill Package

Skill Package 让每个主动技能拥有独立目录、独立 `skill.yaml`、独立行为模板引用和独立表现配置，避免继续把 8 个技能塞进大表字段中。这样可以让 schema 校验、局部迁移、差异审查、未来 SkillEditor 写回和技能资源组织都围绕单个技能发生，而不是修改一张难以表达行为语义的大表。

### 为什么第一轮只做火焰弹垂直切片

火焰弹是最小且最适合验证的 `projectile` 技能。第一轮只做它，可以完整验证“配置加载 -> schema 校验 -> FinalSkillInstance -> SkillEvent[] -> Combat 结算 -> WebApp 表现”的真实路径，同时把迁移风险限制在一个主动技能内。

### 为什么暂不直接做完整 SkillEditor

SkillEditor V0 必须进入当前技能系统重构，因为 Skill Package 的价值不只是把 YAML 拆文件，而是让设计、校验、预览、测试和后续迁移围绕同一个技能包闭环。没有编辑器验收，`skill.schema.json`、behavior template 白名单和 presentation key 很容易停留在后端加载格式，无法验证它们是否能支撑真实内容迭代。

本 change 只要求模块化 SkillEditor V0，不做完整复杂编辑器。V0 以 `skill.yaml`、`skill.schema.json` 和 behavior template 为边界，只编辑白名单字段，先覆盖 `active_fire_bolt`，不创建节点编辑器、不引入脚本能力。

### 为什么需要 Skill Test Arena

高品质技能表现不能只靠配置加载和普通战斗 smoke 验收。Skill Test Arena 用固定测试场景隔离变量，让火焰弹的投射物飞行、命中时机、目标选择、伤害结果、VFX、浮字和 SkillEvent 时间线可重复验证。后续每个 behavior template 迁移时，都必须先在测试场中证明行为语义成立。

### 为什么 AI 自测报告是必要验收

技能表现的失败常常不是“代码报错”，而是玩家描述、事件时间线、伤害结算和视觉反馈不一致。AI 自测报告必须基于真实测试结果生成，把期望玩家侧描述、实际 SkillEvent、实际伤害、命中目标、表现完整性和不一致项放在一份用户可审阅的中文报告中，作为迁移新技能前的质量门槛。

### 为什么采用模块化面板而不是复杂节点编辑器

当前 Skill Package 和 behavior template 仍是 V1 基础架构，最需要的是可控字段编辑、schema 校验和测试闭环。模块化面板能直接对应基础信息、释放参数、子弹、伤害点、表现和预览字段，足够支撑火焰弹和后续模板增量扩展。复杂节点编辑器会过早引入图结构、连线语义和脚本化表达风险，不符合本 change 的白名单模板原则。

### 为什么 Modifier 测试栈只用于测试

Modifier 测试栈用于在编辑器中临时模拟辅助宝石、scaling modifier、关系、source_power、target_power 和 conduit 条件，帮助验证 `FinalSkillInstance` 与 SkillEvent 是否随构筑条件变化。它不得写入真实宝石实例，不得恢复随机词缀生成或 UI，也不得把随机词缀字段加入真实技能文件。真实构筑数据仍来自当前宝石、被动、辅助和数独关系系统。

### 为什么暂不一口气迁移 8 个技能

8 个主动技能分别需要投射、扇形、多目标跳跃、玩家中心范围、近战扇形、直线贯穿、持续环绕、延迟爆炸等行为。如果第一轮同时迁移，难以判断失败来自 schema、行为模板、事件管线、WebApp 表现还是某个技能行为本身；也容易在现有可运行能力上产生大面积回归。

## Capabilities

### New Capabilities

- 无。本 change 不新增独立业务 capability，而是在现有 V1 最小循环能力中重构技能系统框架。

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: 技能定义、技能运行时、战斗结算事件和 WebApp 技能表现要求发生变化；新增 Skill Package、白名单 Behavior Template、FinalSkillInstance 扩展和 `SkillEvent[]` 事件接口要求。

## Impact

- OpenSpec 影响范围：`openspec/changes/refactor-skill-system-runtime-and-skill-package/`。
- 后续 Apply 预计影响但本轮不修改：`configs/skills/`、`src/liufang/skill_effects.py`、`src/liufang/combat.py`、`src/liufang/presentation.py`、SkillEditor / Skill Test Arena WebApp 入口、`webapp/App.tsx`、`webapp/styles.css`、`tests/`、AI 自测报告生成工具。
- 与 `refactor-three-gem-kinds-v1-phase2` 的关系：本 change 后续实现不得覆盖三类宝石字段迁移；应在该迁移完成后推进，或在兼容 `gem_kind` / `sudoku_digit` 的前提下推进。
- 验证影响：后续 Apply 必须保持配置校验、Python 单元测试、OpenSpec strict validate 和 WebApp build 通过。
