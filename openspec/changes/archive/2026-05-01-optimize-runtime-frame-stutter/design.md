## Context

当前 WebApp 的主运行路径在 `webapp/App.tsx` 中由 `requestAnimationFrame` 驱动。`stepGame` 每帧会推进时间、玩家移动、敌人移动、技能冷却、技能事件、浮字和多类 VFX。技能编辑器测试场还会把 Skill Runtime 生成的事件时间线展示给前端。

已观察到的风险点：

- `stepGame` 每帧调用多组 `setState`，包括 `setElapsed`、`setPlayer`、`setEnemies`、`setTexts`、`setBolts`、`setAreaNovas`、`setMeleeArcs`、`setChainSegments`、`setDamageZones`、`setHitVfxs`。
- `consumeScheduledSkillEvents` 会逐个调用 `consumeSkillEvent`；同一帧多个事件到期时，每个事件可能继续触发独立 state 更新。
- 多投射物、穿透、连锁、范围伤害、浮字和调试辅助线会快速增加 DOM 节点数。
- 技能编辑器调试层会渲染发射点、目标点、方向线、碰撞半径、搜索范围和时间线详情，适合调试但不适合无上限刷新。
- 当前缺少明确的帧耗时和掉帧计数，优化结果难以量化。

## Goals / Non-Goals

目标：

- 降低主运行时和技能编辑器测试场的掉帧概率。
- 将同帧技能事件批量落地，减少 React 更新次数。
- 降低每帧分配的临时对象、数组和 inline style 数量。
- 给开发者提供轻量性能观测，能看到帧耗时、逻辑耗时和活动对象数量。
- 保持 SkillEvent 事件数量、顺序、payload、伤害和命中语义不变。
- 保持玩家可见 UI 中文。

非目标：

- 不重写为 Canvas 或 WebGL。
- 不替换 React。
- 不改变 Skill Runtime 的行为模板语义。
- 不调整技能伤害、冷却、飞行速度、命中、穿透、连锁或范围规则。
- 不修改正式技能配置数值。
- 不做无关 UI 视觉重做。

## Proposed Approach

### 一、增加帧性能观测

在 WebApp 运行时维护一个轻量 `runtimePerf` 观测结构，数据可以放在 `useRef` 中，每隔固定时间或在技能编辑器面板中以低频状态同步。

观测字段：

- `frame_ms`
- `logic_ms`
- `active_projectiles`
- `active_hit_vfx`
- `active_area_vfx`
- `active_floating_text`
- `active_enemies`
- `scheduled_events`
- `consumed_events_this_frame`
- `dropped_frame_count`

掉帧可先定义为单帧间隔超过 33ms 或逻辑步耗时超过 16ms。该阈值只用于开发观测，不影响玩法。

### 二、同帧 SkillEvent 批处理

将 `consumeScheduledSkillEvents(dt)` 从“找到 ready 后逐个调用 `consumeSkillEvent`”改为“收集 ready events 后一次批处理”。

批处理函数按事件类型把本帧新增对象聚合：

- projectile spawn -> 一次追加 bolts
- hit vfx / projectile impact -> 一次追加 hitVfxs
- floating_text -> 一次追加 texts
- damage_zone_prime / damage_zone -> 一次更新 damageZones
- area_spawn -> 一次追加 areaNovas
- melee_arc -> 一次追加 meleeArcs
- chain_segment -> 一次追加 chainSegments
- damage -> 一次更新 enemies / kills / combat logs

事件顺序仍使用现有 `SkillEvent` 顺序；批处理只能减少 React 更新次数，不得重排事件或合并真实伤害事件。

### 三、合并每帧状态推进

保留当前数据结构的前提下，减少每帧独立状态更新：

- 活动 VFX 的 TTL 衰减可以在一个 `advanceRuntimeVisuals(dt)` 中计算，再按类型一次性提交。
- 敌人移动和伤害应用避免在同一帧多次 `setEnemies`。
- 技能冷却触发生成的客户端表现事件先进入本帧批处理队列，再统一提交。
- `elapsed` 如果只用于动画时间，可用 ref 承接高频值，低频同步给需要显示的 UI。

### 四、视觉对象预算

新增前端展示预算，避免极端情况下 DOM 数量失控。预算只限制表现对象，不丢弃 SkillEvent、伤害和测试结果。

建议初始预算：

- 投射物体：最多 80
- 命中特效：最多 80
- 浮字：最多 60
- 范围/连锁/近战视觉对象合计：最多 80
- 战斗日志：保持现有小上限
- 技能编辑器事件时间线默认显示最近或当前选中上下文附近的有限条目

当超过预算时，优先裁剪最旧且已经接近结束的表现对象。正式伤害、怪物 HP 和测试场结果不得受预算影响。

### 五、降低调试层渲染成本

技能编辑器调试辅助线仍保留，但应满足：

- 调试层只在技能编辑器或显式开启时渲染。
- 搜索范围、碰撞半径等复杂 DOM 节点按开关和当前选中技能/事件渲染。
- 同类辅助线可以复用计算结果，避免每次 render 重复投影世界坐标。
- 时间线 payload 文本默认折叠或延迟展开，避免长 JSON 每帧进入布局。

### 六、保持运行时语义

优化后的行为必须满足：

- Skill Runtime 输出事件不因前端优化而改变。
- WebApp 消费事件后，伤害目标、伤害值、命中时机和死亡结果与优化前一致。
- 投射物飞行、连锁段、伤害区域、近战弧和浮字仍来自 SkillEvent，不从技能 ID 或特效名猜测。
- 技能编辑器测试场仍能展示真实 `event_timeline` 和 `timeline_checks`。

## Verification

实现时需要执行：

- `python -m unittest tests.test_skill_runtime`
- `npm run build`
- `npm test`

并补充至少一种性能向 smoke 检查：

- 检查 WebApp 包含批量事件消费入口和性能观测字段。
- 检查技能编辑器测试场仍保留 `event_timeline`、`timeline_checks` 和中文可见文案。
- 如果可自动化，运行一个多投射物/多目标场景，确认事件数量和伤害结果不变。

## Risks / Trade-offs

- 风险：批处理事件时不小心改变事件顺序。缓解：ready events 必须保留原排序，测试覆盖同 timestamp 的事件顺序和伤害结果。
- 风险：视觉对象预算被误用于逻辑事件。缓解：预算只作用于前端 VFX 数组，不作用于 SkillEvent、敌人 HP 或测试结果。
- 风险：性能面板本身造成额外刷新。缓解：性能数据用 ref 高频记录，低频同步 UI。
- 风险：过度合并 state 造成 diff 过大。缓解：第一轮只合并技能事件消费和 VFX TTL 更新，不做架构性重写。
