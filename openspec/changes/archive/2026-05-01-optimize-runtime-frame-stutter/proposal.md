## Why

当前 WebApp 运行时在技能特效较多、投射物数量较多、技能编辑器调试辅助线开启或测试场事件时间线较长时，会出现卡顿和掉帧。现有主循环每帧会分别更新玩家、敌人、浮字、投射物、范围特效、近战弧、连锁段、伤害区域、命中特效和排队 SkillEvent；当同一帧内有多个技能事件到期时，还会逐个触发 `setState`。这会把一次逻辑帧拆成多次 React 更新和多次组件树重算。

这次优化的目标不是改变技能伤害、命中、冷却、投射物轨迹或 SkillEvent 语义，而是减少每帧渲染压力，并增加可验证的帧性能观测入口，让之后可以确认卡顿是降低了，而不是凭体感判断。

## What Changes

- 增加轻量运行时性能观测：记录帧耗时、逻辑步耗时、同帧消费事件数、活动 VFX 数、敌人数和最近掉帧次数，并在开发/技能编辑器场景中可见。
- 将同一帧到期的 SkillEvent 批量消费，避免每个事件各自触发独立状态更新。
- 合并每帧战斗状态更新路径，减少 `stepGame` 中多组 `setState` 造成的重复渲染。
- 限制或汇总高频视觉对象：浮字、命中特效、投射物体、范围/连锁视觉对象在超量时按既定策略裁剪或合并展示，不影响实际伤害事件。
- 降低技能编辑器调试层开销：调试辅助线、碰撞圈、搜索范围和事件时间线只渲染当前必要内容，长列表使用上限或虚拟化策略。
- 让动画帧计算尽量从 React render 路径移到 memo/ref/纯计算缓存中，避免每帧创建大量临时对象和 inline style 对象。
- 增加最小回归测试或 smoke 检查，确保优化后 SkillEvent 数量、事件顺序、伤害结果和关键中文 UI 仍保持一致。

## Capabilities

### New Capabilities

- `v1-minimal-sudoku-gem-loop`: 增加 WebApp 运行时帧性能观测、同帧事件批处理、视觉对象预算和技能编辑器调试层性能验收要求。

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: 约束运行时性能优化不得改变 Skill Runtime、Combat Runtime、正式伤害、技能配置 schema 或 SkillEvent 语义。

## Impact

允许修改范围：

- `webapp/App.tsx`
- `webapp/styles.css`
- `webapp/smoke-test.mjs`
- `src/liufang/skill_editor.py`，仅当测试场返回性能观测摘要需要补充字段
- `src/liufang/web_api.py`，仅当技能编辑器接口需要透传测试场性能摘要
- `tests/test_skill_runtime.py`，仅用于证明 SkillEvent 语义未变

禁止修改范围：

- `src/liufang/skill_runtime.py` 的技能行为语义、伤害、命中、冷却、目标选择和事件排序规则
- `src/liufang/combat.py`
- `src/liufang/gem_board.py`
- `src/liufang/loot.py`
- `src/liufang/affixes.py`
- `src/liufang/inventory.py`
- `configs/skills/**` 的正式技能数值和 schema
- `configs/sudoku_board/**`
- `configs/loot/**`
- `configs/affixes/**`
- 非运行时性能相关 UI 重做

本次不覆盖：

- 新战斗引擎
- Canvas/WebGL 全量重写
- 技能数值平衡
- 伤害公式调整
- 敌人 AI 重写
- 资源美术替换
- 构建系统重构
