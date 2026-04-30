## Context

当前技能系统框架已经支持 schema-backed Skill Package、behavior template 白名单、SkillEditor 模块、Skill Test Arena、SkillEvent 时间线、WebApp 事件消费和中文 AI 自测报告。上一个地刺 / `damage_zone` 相关 change 已完成并归档，当前已迁移 Skill Package 至少包含 `active_fire_bolt`、`active_ice_shards`、`active_penetrating_shot`、`active_frost_nova` 和 `active_puncture`。

`active_lightning_chain / 连锁闪电` 仍在旧 `skill_templates.toml` 路径中。旧路径无法声明真实连锁跳跃字段，也无法用 SkillEvent 表达链段顺序、链半径、链次数、链段时序和默认不重复命中目标等语义。迁移后的目标体验是：

“自动向最近敌人释放闪电链，命中初始目标后，在一定半径内跳跃到附近未命中的敌人，造成多段闪电伤害，并显示连续电弧、命中特效与伤害浮字。”

## Goals / Non-Goals

**Goals:**

- 规划 `active_lightning_chain` Skill Package 结构，未来路径为 `configs/skills/active/active_lightning_chain/skill.yaml`。
- 规划新增 `configs/skills/behavior_templates/chain.yaml`，用声明式字段表达真实多目标连锁。
- 让 SkillEditor 暴露 `chain` 模板全部可编辑字段，并显示只读链段摘要和预计总时长摘要。
- 让 SkillRuntime 后续实现真实 `chain_segment`、`damage`、`hit_vfx`、`floating_text` 事件序列。
- 让 WebApp 后续只消费真实 SkillEvent，不根据 skill id、旧模板 id、behavior type、VFX key 或视觉名称猜行为。
- 让 Skill Test Arena 后续验证三目标横排、密集小怪和单体木桩场景中的连锁效果。
- 让 AI 自测报告后续基于真实测试结果输出中文通过 / 部分通过 / 不通过结论。

**Non-Goals:**

- 本轮不写运行时代码、不改 WebApp、不创建 `active_lightning_chain/skill.yaml`。
- 不迁移 `active_lava_orb`、`active_fungal_petards` 或其他主动技能。
- 不修改 `active_fire_bolt`、`active_ice_shards`、`active_penetrating_shot`、`active_frost_nova`、`active_puncture` 已完成能力。
- 不修改正式掉落、库存、宝石盘。
- 不创建节点编辑器、脚本 DSL 或复杂表达式解释器。
- 不允许前端猜技能行为，不允许静态假事件。
- 不引入英文玩家可见文案。

## Decisions

### 1. `active_lightning_chain` Skill Package 结构

后续 Apply 应新增：

`configs/skills/active/active_lightning_chain/skill.yaml`

该 Skill Package 必须包含：

- `id`
- `version`
- `display.name_key`
- `display.description_key`
- `classification.tags`
- `classification.damage_type = lightning`
- `classification.damage_form`
- `cast.mode`
- `cast.target_selector`
- `cast.search_range`
- `cast.cooldown_ms`
- `cast.windup_ms`
- `cast.recovery_ms`
- `behavior.template = chain`
- `behavior.params`
- `hit.base_damage`
- `hit.can_crit`
- `hit.can_apply_status`
- `scaling.additive_stats`
- `scaling.final_stats`
- `scaling.runtime_params`
- `presentation.vfx`
- `presentation.sfx`
- `presentation.floating_text`
- `presentation.screen_feedback`
- `preview.show_fields`

玩家可见文本必须通过中文本地化 key 提供。`segment_vfx_key`、VFX key、SFX key 和 reason key 只能作为 key，不得作为玩家可见文本直接展示。

拒绝方案：继续使用旧 `skill_templates.toml`。旧路径不能表达 schema 约束、模板白名单、链段事件和编辑器字段的统一验收。

### 2. `chain` Behavior Template

后续 Apply 应新增：

`configs/skills/behavior_templates/chain.yaml`

字段白名单至少包含：

- `chain_count`
- `chain_radius`
- `chain_delay_ms`
- `damage_falloff_per_chain`
- `target_policy`
- `allow_repeat_target`
- `max_targets`
- `segment_vfx_key`

字段约束：

- `chain_count` 必须为正整数。
- `chain_radius` 必须为正数。
- `chain_delay_ms` 必须为非负数。
- `damage_falloff_per_chain` 必须为合法数值范围；第一版建议使用 `0 <= damage_falloff_per_chain <= 1`，表示每跳衰减比例。
- `target_policy` 使用枚举，第一版至少支持 `nearest_not_hit`。
- `allow_repeat_target` 为布尔值，默认 `false`。
- `max_targets` 必须为正整数，或使用明确声明的 `unlimited` 枚举。
- `segment_vfx_key` 只能写 key。
- 禁止脚本、表达式 DSL、未声明参数、函数调用字符串、前端专属假参数。

拒绝方案：把连锁逻辑写成前端字段或 VFX 名称约定。连锁是否跳跃、跳到谁、何时扣血属于战斗结算和 SkillEvent 事实，不能由 WebApp 推断。

### 3. SkillEditor `chain` 模块

SkillEditor 后续必须新增 `chain` 连锁模块。

可编辑字段：

- `chain_count`
- `chain_radius`
- `chain_delay_ms`
- `damage_falloff_per_chain`
- `target_policy`
- `allow_repeat_target`
- `max_targets`
- `segment_vfx_key`

只读摘要：

- 最大链段摘要：由 `chain_count`、`max_targets`、`allow_repeat_target` 推导。
- 预计链总时长摘要：由 `chain_count` 和 `chain_delay_ms` 推导。

校验要求：

- `target_policy` 使用枚举。
- `allow_repeat_target` 使用布尔控件。
- `chain_count`、`max_targets` 有整数校验。
- `chain_radius`、`chain_delay_ms`、`damage_falloff_per_chain` 有范围校验。
- `segment_vfx_key` 只允许写 key，不能作为玩家可见文案。
- 保存前必须执行 schema 与 behavior template 白名单校验。
- 非法字段和值必须中文报错。
- 不允许写入模板未声明字段。
- 不允许把连锁逻辑写成前端专属假参数。

拒绝方案：仅在 SkillEditor 中新增视觉预览字段。编辑器必须保存真实 Skill Package 参数，并由 schema 和模板白名单约束。

### 4. SkillRuntime `chain` 行为

`chain` 后续必须通过通用 behavior template 分发实现，不允许在 Combat Runtime 写 `active_lightning_chain` 专属分支。

执行语义：

- 选择最近敌人作为初始目标。
- 命中初始目标后，在 `chain_radius` 内寻找下一个未命中敌人。
- `target_policy = nearest_not_hit` 时，从上一命中目标出发选择半径内最近未命中目标。
- 按 `chain_count` 限制最大链段数量。
- 按 `max_targets` 限制最大命中目标数。
- 默认 `allow_repeat_target = false`，不得重复命中同一目标。
- 每段链都有独立 `chain_segment` 事件。
- 每个被命中的目标都有 `damage` 事件。
- `damage` 后或同时输出 `hit_vfx` 和 `floating_text`。
- `damage_type = lightning`。
- `chain_delay_ms` 控制每段链的时间间隔。
- `damage_falloff_per_chain` 控制后续链段伤害衰减。
- 不允许只画一条线。
- 不允许释放瞬间一次性扣血。
- 不允许静态假事件。

事件时序建议：

- `cast_start` 在释放开始时输出。
- 第 0 段 `chain_segment` 表示从玩家或释放源到初始目标。
- 第 N 段 `chain_segment` 表示从上一个目标到下一个目标。
- 对应 `damage` 的 `timestamp_ms` 不得早于该段 `chain_segment.timestamp_ms`。
- 第 N 段事件的时间偏移应体现 `chain_delay_ms * N` 或等价延迟模型。

### 5. SkillEvent 时间线

时间线必须显示：

- `cast_start`
- `chain_segment`，多段
- `damage`，多段
- `hit_vfx`
- `floating_text`
- `cooldown_update`，如存在

所有相关事件字段必须包含：

- `timestamp_ms`
- `delay_ms`
- `duration_ms`
- `source_entity`
- `target_entity`
- `amount`
- `damage_type`
- `vfx_key`
- `reason_key`
- `payload`

`chain_segment.payload` 必须能表达：

- `segment_index`
- `from_target`
- `to_target`
- `start_position`
- `end_position`
- `chain_radius`
- `chain_delay_ms`
- `damage_scale`
- `vfx_key`

### 6. WebApp 事件消费

WebApp 后续必须根据真实 `chain_segment` 渲染连续电弧。渲染所需起点、终点、链段顺序、链段时间、VFX、damage、hit_vfx 和 floating_text 均来自 SkillEvent。

WebApp 禁止通过 `behavior_type`、`visual_effect`、`skill_lightning_chain`、`active_lightning_chain`、`segment_vfx_key` 或视觉名称猜测连锁行为。

### 7. Skill Test Arena 验收

重点场景：

- 三目标横排：验证链段顺序、链半径和链次数限制。
- 密集小怪：验证真实多目标跳跃和默认不重复命中。
- 单体木桩：验证基础时序和单目标回归。

必须验证：

- 初始目标被命中。
- 后续目标按 `chain_radius` 被选中。
- `chain_count` 限制链段数量。
- 默认不重复命中同一目标。
- `chain_delay_ms` 改变链段时间间隔。
- `damage_falloff_per_chain` 改变后续链段伤害。
- `chain_radius` 改变可跳跃目标范围。
- `damage` 事件后扣血。
- `hit_vfx` / `floating_text` 与 `damage` 对齐。
- Modifier 测试栈能影响最终伤害或连锁参数。

### 8. AI 自测报告

期望玩家侧描述：

“自动向最近敌人释放闪电链，命中初始目标后，在一定半径内跳跃到附近未命中的敌人，造成多段闪电伤害，并显示连续电弧、命中特效与伤害浮字。”

报告必须检查：

- 是否存在 `chain_segment`。
- 是否存在多段 `chain_segment`。
- 是否存在 `damage`。
- 是否存在 `hit_vfx`。
- 是否存在 `floating_text`。
- `damage` 是否不早于对应 `chain_segment`。
- 是否命中多个目标。
- 默认是否不重复命中同一目标。
- `chain_count` 修改后链段数量是否变化。
- `chain_radius` 修改后可跳跃目标是否变化。
- `chain_delay_ms` 修改后链段时间间隔是否变化。
- `damage_falloff_per_chain` 修改后后续伤害是否变化。
- `damage_type` 是否为 `lightning`。
- 结论为 `通过` / `部分通过` / `不通过`。
- 输出中文不一致项和建议修复项。

## Risks / Trade-offs

- 链段计数含义可能混淆为“跳跃次数”或“命中目标数” -> 在 schema、编辑器摘要、测试中统一定义为最大 `chain_segment` 数，并用 `max_targets` 限制目标数。
- 默认不重复命中可能导致目标不足时提前结束 -> AI 报告和测试场应把提前结束视为合法，只要没有静态补假事件。
- `damage_falloff_per_chain` 可能与现有伤害 modifier 顺序冲突 -> 后续 Apply 应明确先计算基础/加成/最终伤害，再按链段应用 `damage_scale` 或等价衰减。
- WebApp 可能复用旧单线闪电视觉 -> smoke test 和代码审查必须确认连续电弧来自多段 `chain_segment`。
- 旧模板仍存在未迁移技能 -> 后续 Apply 只新增 `active_lightning_chain` Skill Package，不迁移其他技能。

## Migration Plan

1. Phase 0 扫描当前归档状态、active changes、已迁移 Skill Package 和旧路径。
2. Phase 1 新增 `chain` schema / behavior template 设计与校验。
3. Phase 2 新增 `active_lightning_chain` Skill Package。
4. Phase 3 SkillEditor 新增 `chain` 连锁模块字段和中文校验。
5. Phase 4 SkillRuntime 实现通用 `chain` 行为和真实事件时序。
6. Phase 5 WebApp 消费 `chain_segment`、`damage`、`hit_vfx`、`floating_text`。
7. Phase 6 Skill Test Arena 接入连锁闪电场景。
8. Phase 7 SkillEvent 时间线与 AI 自测报告接入连锁闪电。
9. Phase 8 运行配置校验、Python 单测、OpenSpec strict validate、npm build/test 和 AI 自测报告。

Rollback strategy: 后续 Apply 保留旧 `skill_templates.toml` 中未迁移技能路径。若 `chain` 行为未通过验证，可移除新增 `active_lightning_chain` Skill Package 和 `chain` template，连锁闪电回退旧路径，且不影响已迁移技能。

## Open Questions

- `chain_count` 是否包含从玩家到初始目标的第 0 段？建议包含所有 `chain_segment`，即第 0 段也计入。
- `damage_falloff_per_chain = 0.2` 是否表示每跳减少 20%，还是每跳乘以 0.2？建议表示每跳减少 20%，实际事件 payload 输出明确 `damage_scale`。
- 后续是否允许 `allow_repeat_target = true` 的循环链？第一版可以 schema 支持布尔值，但测试默认必须覆盖 `false`。
