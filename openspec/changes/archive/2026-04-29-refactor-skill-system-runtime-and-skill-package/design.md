## Context

当前 V1 技能系统相关结构如下：

- `configs/skills/` 只有 `skill_templates.toml` 和 `skill_scaling_rules.toml`，主动技能定义仍集中在一张大表中。
- `src/liufang/skill_effects.py` 已有 `FinalSkillInstance`，但它仍主要承载最终数值、`behavior_type` 和 `visual_effect`，没有事件化表达技能行为。
- `src/liufang/combat.py` 在冷却到期后直接用 `final_damage` 扣血，伤害时机与真实投射物命中时机没有分层。
- `src/liufang/presentation.py` 负责宝石详情、技能预览和中文展示，但技能表现仍依赖最终技能字段。
- `webapp/App.tsx` 中战斗表现根据 `behavior_type`、`damage_type`、`visual_effect` 和 `projectile_count` 等字段推断，前端承担了技能行为猜测。
- `webapp/styles.css` 已存在若干技能表现样式，但它们不是由统一事件协议驱动。
- `tests/` 已覆盖 combat、presentation、skill_effects、v1_loop 等路径，后续 Apply 必须扩展而不是绕过这些测试。

当前仍存在 active change `refactor-three-gem-kinds-v1-phase2`，状态为 complete 但未归档。本 change 的 Apply 阶段不应修改它，也不应把技能系统重构设计成覆盖它。技能系统重构应在三类宝石字段迁移完成后进行，或至少兼容 `gem_kind` / `sudoku_digit` 字段模型。

## Goals / Non-Goals

**Goals:**

- 将主动技能定义从集中表迁移到 Skill Package。
- 每个主动技能拥有独立目录和独立 `skill.yaml`。
- 用统一 `skill.schema.json` 校验技能定义。
- 用白名单 Behavior Template 执行技能行为。
- 用 `FinalSkillInstance` 承接宝石、被动、辅助、数独关系和 modifier 后的最终技能参数。
- 用 `SkillEvent[]` 作为 Runtime 与 WebApp 的共同语言。
- 让 Combat Runtime 不再写具体技能分支。
- 让 WebApp 不再根据 `behavior_type + visual_effect` 猜技能表现。
- 第一轮 Apply 只做 `active_fire_bolt` 垂直切片。
- 后续阶段实现 SkillEditor V0 基础壳和模块化字段编辑。
- 后续阶段实现 Modifier 测试栈、Skill Test Arena、SkillEvent 时间线查看器和 AI 自测报告。

**Non-Goals:**

- 本 change 提案阶段不写运行时代码、不修改 WebApp、不迁移技能配置。
- 第一轮 Apply 不迁移全部 8 个主动技能。
- 不实现节点编辑器、任意脚本 DSL 或复杂表达式解释器。
- Modifier 测试栈不写入真实宝石实例、不恢复随机词缀生成或随机词缀 UI。
- 不删除当前可运行能力。
- 不引入英文玩家可见文案。
- 不用静态假事件替代真实 `SkillEvent` 设计。

## Decisions

### Decision 1: 使用 Skill Package 替代大表式 skill_templates

目标结构：

```text
configs/
  skills/
    schema/
      skill.schema.json
    active/
      active_fire_bolt/
        skill.yaml
      active_ice_shards/
        skill.yaml
      active_lightning_chain/
        skill.yaml
      active_frost_nova/
        skill.yaml
      active_puncture/
        skill.yaml
      active_penetrating_shot/
        skill.yaml
      active_lava_orb/
        skill.yaml
      active_fungal_petards/
        skill.yaml
    behavior_templates/
      projectile.yaml
      fan_projectile.yaml
      chain.yaml
      player_nova.yaml
      melee_arc.yaml
      line_pierce.yaml
      orbit.yaml
      delayed_area.yaml
```

每个 `skill.yaml` 至少描述：

```text
id
version
display.name_key
display.description_key
classification.tags
classification.damage_type
classification.damage_form
cast.mode
cast.target_selector
cast.search_range
cast.cooldown_ms
cast.windup_ms
cast.recovery_ms
behavior.template
behavior.params
hit.base_damage
hit.can_crit
hit.can_apply_status
scaling.additive_stats
scaling.final_stats
scaling.runtime_params
presentation.vfx
presentation.sfx
presentation.floating_text
presentation.screen_feedback
preview.show_fields
```

理由：Skill Package 让技能定义、行为、表现和预览字段以单技能为单位组织。后续 SkillEditor 可以围绕一个 package 做读写，而不是修改集中大表。

替代方案：继续扩展 `skill_templates.toml`。放弃原因是大表只能表达字段差异，无法清晰表达行为模板参数、事件输出、表现资源和编辑器边界。

### Decision 2: skill.schema.json 只校验结构、枚举和引用边界

`skill.schema.json` 应校验：

- 必需字段存在。
- `id` 与目录名一致。
- `version` 格式合法。
- `classification.damage_type`、`classification.damage_form`、`cast.mode`、`cast.target_selector` 为枚举值。
- `behavior.template` 只能引用白名单模板。
- `behavior.params` 只能包含模板允许的参数。
- `scaling.additive_stats`、`scaling.final_stats`、`scaling.runtime_params` 只能引用合法 stat。
- `presentation.*` 引用 key，不写玩家可见英文文本。
- `preview.show_fields` 只能引用可展示字段。

schema 不负责执行行为、不解释表达式、不计算数值。跨文件语义校验由配置校验器在后续 Apply 中完成。

### Decision 3: Behavior Template 必须是白名单

V1 第一批行为模板：

| 主动技能 | 行为模板 | 语义 |
|---|---|---|
| `active_fire_bolt` | `projectile` | 标准投射物 |
| `active_ice_shards` | `fan_projectile` | 扇形多投射 |
| `active_lightning_chain` | `chain` | 真实多目标跳跃 |
| `active_frost_nova` | `player_nova` | 以玩家为中心范围爆发 |
| `active_puncture` | `melee_arc` | 近战扇形 / 短距离斩击 |
| `active_penetrating_shot` | `line_pierce` | 直线路径贯穿 |
| `active_lava_orb` | `orbit` | 持续环绕 tick |
| `active_fungal_petards` | `delayed_area` | 延迟范围爆炸 |

模板文件定义允许参数、默认值、事件输出形态和结算时机。技能 YAML 只能填模板参数，不能写脚本。

理由：白名单模板能让行为表现可测试、可校验、可编辑，同时避免任意脚本带来的安全、调试和回放问题。

### Decision 4: FinalSkillInstance 是最终参数，不是行为脚本

`FinalSkillInstance` 应继续作为主动技能进入战斗的最终实例，但需要从旧的“最终数值 + 前端提示字段”扩展为 Skill Runtime 的输入。建议结构预留：

```text
skill_instance_id
active_gem_instance_id
skill_package_id
skill_package_version
template
tags
damage_type
damage_form
cast
hit
scaling_result
runtime_params
presentation_keys
applied_modifiers
source_context
```

`FinalSkillInstance` 不执行技能行为。它只承接：

- 主动宝石基础技能定义。
- 被动技能宝石贡献。
- 辅助宝石贡献。
- 数独关系 modifier。
- additive / final / runtime 参数聚合结果。
- 与 `gem_kind` / `sudoku_digit` 兼容的来源信息。

### Decision 5: SkillEvent[] 是 Runtime 与 WebApp 的共同语言

`SkillEvent` 至少预留类型：

```text
cast_start
projectile_spawn
projectile_hit
chain_segment
area_spawn
melee_arc
orbit_spawn
orbit_tick
delayed_area_prime
delayed_area_explode
damage
hit_vfx
floating_text
cooldown_update
```

事件必须能表达：

```text
event_id
type
timestamp_ms
source_entity
target_entity
position
direction
delay_ms
duration_ms
amount
damage_type
skill_instance_id
vfx_key
sfx_key
reason_key
payload
```

`damage` 事件代表真实结算点。对于 `projectile`，`damage` 必须在投射物命中事件之后或同一命中时刻产生，不能在释放瞬间提前扣血。

### Decision 6: Combat Runtime 与 Skill Runtime 分层

分层职责：

```text
Combat Runtime
  - 管理战斗 tick、实体、生命、死亡、掉落触发
  - 管理自动释放时机和冷却推进
  - 调用 Skill Runtime 执行最终技能实例
  - 消费 damage / cooldown_update 等结算事件
  - 不写 fire_bolt / chain / nova 等具体技能分支

Skill Runtime
  - 接收 FinalSkillInstance
  - 根据 behavior.template 调用白名单行为模板
  - 生成 SkillEvent[]
  - 确定命中、延迟、持续时间、tick 和事件顺序
  - 不直接操作 WebApp DOM 或前端样式

Presentation / WebApp
  - 消费 SkillEvent[]
  - 根据 vfx_key / sfx_key / floating_text / screen_feedback 渲染表现
  - 不用 behavior_type + visual_effect 猜行为
```

### Decision 7: 第一轮 Apply 只做 active_fire_bolt 垂直切片

第一轮验收目标：

1. 火焰弹从 `configs/skills/active/active_fire_bolt/skill.yaml` 加载。
2. 火焰弹通过 `skill.schema.json` 校验。
3. 火焰弹生成 `FinalSkillInstance`。
4. 火焰弹输出 `SkillEvent[]`：`projectile_spawn`、`damage`、`hit_vfx`、`floating_text`。
5. WebApp 消费 `SkillEvent` 渲染火焰弹表现。
6. 火焰弹伤害时机与投射物命中时机一致。
7. 现有配置校验、Python 单元测试、OpenSpec 校验、WebApp build 继续通过。
8. 其他 7 个技能暂时保持旧行为。

### Decision 8: WebApp 只消费事件，不反推技能行为

WebApp 后续应从后端或本地规则适配层接收 `SkillEvent[]`，并以事件为渲染输入：

- `projectile_spawn` 创建投射物表现。
- `projectile_hit` 或同 tick `damage` 决定命中点。
- `hit_vfx` 使用 `vfx_key` 播放命中特效。
- `floating_text` 使用 `amount`、`damage_type`、`reason_key` 显示中文浮字。
- `cooldown_update` 更新 HUD。

WebApp 可以保留样式和动画资产，但不再通过 `behavior_type` 推断路径、不再用 `visual_effect` 猜伤害类型或技能语义。

### Decision 9: SkillEditor V0 是 Skill Package 的浏览器编辑入口

SkillEditor V0 应作为 WebApp 内浏览器可打开的编辑入口，只面向已迁移的 Skill Package。第一版至少能打开 `configs/skills/active/active_fire_bolt/skill.yaml`。

SkillEditor 基础壳显示：

- 技能文件列表。
- 已迁移 Skill Package 来源目录。
- 技能中文名。
- `skill.yaml` 路径。
- `behavior.template`。
- 当前 schema 校验状态。

SkillEditor 不允许把未迁移的 7 个旧技能显示为可编辑 Skill Package。旧技能可以作为“未迁移计划项”展示，但不得提供编辑入口、保存入口或假 package 状态。

### Decision 10: SkillEditor 读写关系以 schema 和 behavior template 为边界

SkillEditor 的读写关系：

```text
configs/skills/active/<skill_id>/skill.yaml
  -> SkillEditor 读取
  -> skill.schema.json 校验字段结构
  -> behavior_templates/<template>.yaml 决定可编辑参数白名单
  -> 保存前重新校验
  -> 只写回 schema 和模板白名单允许字段
```

编辑器必须遵守：

- 单技能 package 目录是编辑单位。
- `skill.schema.json` 是字段、枚举、必需字段和基础控件生成依据。
- Behavior Template 提供可编辑参数白名单。
- `preview.show_fields` 决定编辑器和预览面板可展示字段。
- `presentation.*` 只存 key，玩家可见文本仍来自中文本地化。
- 保存失败必须显示中文错误。
- 不允许写任意脚本、表达式 DSL 或测试 modifier。

### Decision 11: SkillEditor 采用模块化编辑面板

编辑器采用固定模块面板，而不是节点图。

基础信息模块：

- `id` 只读。
- `version`。
- `display.name_key`。
- `display.description_key`。
- `classification.tags`。
- `classification.damage_type`。
- `classification.damage_form`。

释放参数模块：

- `cast.mode`。
- `cast.target_selector`。
- `cast.search_range`。
- `cast.cooldown_ms`。
- `cast.windup_ms`。
- `cast.recovery_ms`。

`projectile` 子弹模块：

- `projectile_count`。
- `projectile_speed`。
- `projectile_width`。
- `projectile_height`。
- `max_distance`。
- `hit_policy`。
- `pierce_count`。
- `collision_radius`。
- `spawn_offset`。
- `travel_duration` 或由速度和距离计算出的只读飞行时间。

伤害点模块：

- `hit.base_damage`。
- `hit.can_crit`。
- `hit.can_apply_status`。
- `damage_type`。
- `damage_form`。
- `damage_timing`。
- `hit_delay_ms`。
- `hit_radius`。
- `target_policy`。

表现模块：

- `cast_vfx_key`。
- `projectile_vfx_key`。
- `hit_vfx_key`。
- `sfx_key`。
- `floating_text_style`。
- `hit_stop_ms`。
- `camera_shake`。

预览字段模块：

- `preview.show_fields`。

模块化面板的设计原因是字段可以直接映射到 schema、behavior template 和测试验收。节点编辑器会引入额外语义和表达能力，不符合白名单模板原则。

### Decision 12: Modifier 测试栈只作用于测试运行

Modifier 测试栈用于编辑器内临时测试 `active_fire_bolt` 在不同构筑条件下的表现。它可以从当前辅助宝石配置或 `skill_scaling_rules` 读取可测试 modifier，并允许测试者选择：

- 一个或多个测试 modifier。
- 模拟关系：相邻、同行、同列、同宫。
- `source_power`。
- `target_power`。
- conduit 测试参数。

测试 modifier 只进入测试运行的临时 `FinalSkillInstance` 构建，不写入真实宝石实例，不写入真实 `skill.yaml`，不恢复随机词缀生成，不恢复随机词缀 UI，不把随机词缀字段加入真实技能文件。

### Decision 13: Skill Test Arena 是技能行为的受控验证环境

Skill Test Arena 是编辑器旁路的测试场，不替代正式 Combat Runtime。第一版场景：

- 单体木桩。
- 三目标横排。
- 纵向队列。
- 密集小怪。

测试场必须支持：

- 选择技能，第一版至少支持 `active_fire_bolt`。
- 应用或关闭测试 Modifier Stack。
- 运行测试。
- 暂停。
- 单步。
- 重置。
- 查看怪物生命。
- 查看命中目标。
- 查看实际伤害结果。
- 查看 SkillEvent 时间线。

`active_fire_bolt` 在测试场中的验收包括：运行后生成 `projectile_spawn`；投射物飞行期间不扣血；到达目标后生成 `damage`；`damage` 后生成 `hit_vfx` 和 `floating_text`；木桩生命正确减少；修改 `projectile_speed` 后飞行时间变化；修改 `hit.base_damage` 后伤害变化；加入测试 modifier 后 `FinalSkillInstance` 和 SkillEvent 数值变化。

### Decision 14: SkillEvent 时间线查看器显示真实事件序列

时间线查看器显示真实 SkillEvent 序列，不显示静态假事件。第一版至少显示：

- `cast_start`。
- `projectile_spawn`。
- `projectile_hit`。
- `damage`。
- `hit_vfx`。
- `floating_text`。
- `cooldown_update`。

每个事件至少显示：

- `timestamp_ms`。
- `delay_ms`。
- `duration_ms`。
- `source_entity`。
- `target_entity`。
- `amount`。
- `damage_type`。
- `vfx_key`。
- `reason_key`。
- `payload`。

时间线用于对齐“玩家看到什么”和“Runtime 在什么时候结算什么”。

### Decision 15: AI 自测报告必须基于真实测试结果

AI 自测报告由 Codex 可运行的测试机制生成，输出 Markdown 或 JSON，自然语言部分必须中文。报告必须基于真实 Skill Test Arena 结果，不允许静态假报告。

报告结构：

```text
测试技能 ID
技能中文名
skill.yaml 路径
behavior_template
测试场景
测试 Modifier Stack
期望玩家侧描述
实际 SkillEvent 序列
实际伤害结果
实际命中目标
表现事件是否完整
伤害时机是否与表现一致
是否符合描述
不一致项列表
建议修复项
```

报告的判断逻辑应以真实事件和伤害结果为输入：例如投射物飞行期间木桩生命未变化、`damage` 后生命减少、`hit_vfx` 和 `floating_text` 与 `damage` 同时或之后出现。

### Decision 16: 后续迁移 7 个技能时同步扩展编辑器字段

每迁移一个 behavior template，SkillEditor 必须先支持该模板的全部可编辑字段。没有编辑器字段支持的技能不得标记为完成迁移。

后续模板映射：

| 主动技能 | behavior_template |
|---|---|
| `active_ice_shards` | `fan_projectile` |
| `active_lightning_chain` | `chain` |
| `active_frost_nova` | `player_nova` |
| `active_puncture` | `melee_arc` |
| `active_penetrating_shot` | `line_pierce` |
| `active_lava_orb` | `orbit` |
| `active_fungal_petards` | `delayed_area` |

迁移禁止事项：

- 禁止半迁移。
- 禁止创建未校验 `skill.yaml` 假完成。
- 禁止技能行为已经迁移但编辑器缺少对应字段。
- 禁止绕过 Skill Test Arena 和 AI 自测报告。

### Decision 17: 与 gem_kind / sudoku_digit 重构的依赖关系

技能系统重构依赖三类宝石字段迁移提供稳定来源字段：

- `gem_kind` 用于区分 `active_skill`、`passive_skill`、`support`。
- `sudoku_digit` 用于数独冲突和盘面关系。
- 技能系统不得继续从旧 `gem_type` 推断宝石大类或数独数字。
- Apply 阶段若 `refactor-three-gem-kinds-v1-phase2` 尚未归档，应先确认当前代码已具备 `gem_kind` / `sudoku_digit` 兼容层，再进行火焰弹切片。

## Migration Plan

Phase 0：现状扫描与兼容边界确认。

Phase 1：Skill Package schema 与加载器。

Phase 2：`FinalSkillInstance` 与 modifier 接口适配。

Phase 3：`SkillEvent` 管线。

Phase 4：火焰弹 `projectile` 垂直切片。

Phase 5：WebApp 消费 `SkillEvent`。

Phase 6：SkillEditor V0 基础壳。

Phase 7：SkillEditor 模块化字段编辑。

Phase 8：Modifier 测试栈。

Phase 9：Skill Test Arena。

Phase 10：SkillEvent 时间线查看器。

Phase 11：AI 自测报告。

Phase 12：剩余 7 个主动技能迁移计划。

Phase 13：验证与回归。

回滚策略：第一轮 Apply 应保留旧 `skill_templates.toml` 路径作为其他 7 个技能的兼容路径。若火焰弹切片失败，可以仅回退火焰弹 package 加载和事件管线接入，不影响其他技能旧行为。

## Risks / Trade-offs

- [Risk] 新事件管线与旧即时扣血路径短期并存，可能出现两套结算路径。Mitigation: 第一轮仅允许 `active_fire_bolt` 使用事件管线，其他技能显式走旧路径，并用测试锁定。
- [Risk] WebApp 事件动画和后端事件时间轴不同步。Mitigation: 事件必须携带 `timestamp_ms`、`delay_ms`、`duration_ms`，WebApp 只按事件调度。
- [Risk] schema 过早设计过宽会变成隐形 DSL。Mitigation: `behavior.params` 只允许模板声明字段，禁止表达式和脚本。
- [Risk] 一次迁移 8 个技能导致大范围回归。Mitigation: tasks 明确第一轮只迁移火焰弹。
- [Risk] 与三类宝石字段迁移冲突。Mitigation: Apply 前检查 `gem_kind` / `sudoku_digit` 状态，设计和任务中写明依赖与兼容边界。
- [Risk] SkillEditor 保存能力绕过 schema 或模板白名单。Mitigation: 保存前必须运行 schema 校验和 behavior template 参数白名单校验，失败显示中文错误。
- [Risk] Modifier 测试栈污染真实数据。Mitigation: 测试栈只存在于测试运行上下文，不写入真实宝石实例、随机词缀字段或 `skill.yaml`。
- [Risk] AI 自测报告变成静态说明文档。Mitigation: 报告必须引用真实 Skill Test Arena 结果、SkillEvent 序列、伤害结果和命中目标。

## Open Questions

- 第一轮 SkillEvent 是完全由 Python 后端生成，还是通过 WebApp 复用 Python 规则适配层生成，需要在 Apply Phase 0 结合当前运行方式确认。
- `skill.schema.json` 使用 JSON Schema 哪个 draft 版本，需要以后续校验工具兼容性为准。
- WebApp 的事件流是一次性战斗结果快照，还是逐 tick 增量流，第一轮可先采用最小可测试形式。
- SkillEditor V0 是复用现有 WebApp 单页入口，还是新增独立路由 / 页面，需要后续 Apply 结合当前前端结构决定。
- AI 自测报告第一版由 Python CLI、WebApp 操作导出，还是二者共享同一测试结果结构，需要后续 Apply 确认。
