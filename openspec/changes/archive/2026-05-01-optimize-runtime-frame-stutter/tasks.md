## 1. OpenSpec 验证任务

- [x] 1.1 创建 `proposal.md`、`design.md`、`tasks.md` 和 `specs/v1-minimal-sudoku-gem-loop/spec.md`。
- [x] 1.2 如果 OpenSpec CLI 可用，运行 `openspec validate optimize-runtime-frame-stutter --strict`。
- [x] 1.3 如果 OpenSpec CLI 不可用，至少确认新增文件路径和规格增量格式正确。

## 2. 性能观测任务

- [x] 2.1 在 WebApp 运行时增加低开销性能观测 ref，记录帧耗时、逻辑耗时、活动对象数、排队事件数和掉帧次数。
- [x] 2.2 在技能编辑器或开发显示区域低频展示性能摘要，玩家可见文本保持中文。
- [x] 2.3 确保性能观测不开启额外高频 React render。

## 3. SkillEvent 批处理任务

- [x] 3.1 将同帧到期的 scheduled SkillEvent 收集为有序数组。
- [x] 3.2 新增批量消费函数，一次性聚合 projectile、hit_vfx、floating_text、damage_zone、area_spawn、melee_arc、chain_segment 和 damage 的状态变更。
- [x] 3.3 保持同 timestamp 事件的现有排序规则和消费结果。
- [x] 3.4 确认即时事件和延迟事件都走一致的批处理路径。

## 4. 每帧状态更新收敛任务

- [x] 4.1 收敛 VFX TTL 衰减逻辑，减少每帧多组重复 map/filter 和多次提交。
- [x] 4.2 避免同一帧内多次更新敌人状态；敌人移动、技能伤害和死亡处理应可在同帧合并或有明确顺序。
- [x] 4.3 将仅服务动画时间的高频值优先放入 ref，只有 UI 需要显示时才低频同步。
- [x] 4.4 保持玩家移动、敌人移动、技能冷却和伤害结算结果不变。

## 5. 视觉对象预算任务

- [x] 5.1 为投射物体、命中特效、浮字、范围/连锁/近战视觉对象增加展示上限。
- [x] 5.2 超过上限时只裁剪前端表现对象，不丢弃 SkillEvent 或伤害结果。
- [x] 5.3 裁剪策略优先移除最旧或接近结束的表现对象。

## 6. 技能编辑器调试层优化任务

- [x] 6.1 调试辅助线只在技能编辑器或显式调试开关开启时渲染。
- [x] 6.2 对发射点、目标点、方向线、碰撞半径和搜索范围的坐标投影做复用或 memo。
- [x] 6.3 事件时间线 payload 默认折叠或限制渲染数量，展开时仍能查看原始 payload。
- [x] 6.4 保持现有中文按钮、提示和测试场事件详情。

## 7. 回归测试任务

- [x] 7.1 运行 `python -m unittest tests.test_skill_runtime` 并通过。
- [x] 7.2 运行 `npm run build` 并通过。
- [x] 7.3 运行 `npm test` 并通过。
- [x] 7.4 增加或更新 smoke 检查，覆盖批量事件消费、性能观测字段和技能编辑器测试场关键能力。

## 8. 范围约束任务

- [x] 8.1 不修改正式技能数值、技能 schema、伤害公式、命中规则、冷却规则或 SkillEvent 语义。
- [x] 8.2 不修改宝石盘、掉落、词缀、库存、数独规则和非运行时性能相关 UI。
- [x] 8.3 不引入 Canvas/WebGL 全量重写或新战斗引擎。
