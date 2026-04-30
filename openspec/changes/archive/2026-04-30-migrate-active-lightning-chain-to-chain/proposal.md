## Why

`active_lightning_chain / 连锁闪电` 仍在旧 `skill_templates.toml` 路径中，无法用当前 Skill Package、SkillEditor、Skill Test Arena、SkillEvent 时间线和 AI 自测报告能力完整验证。它是下一个需要迁移的主动技能，因为火球、冰片、穿透射击、冰霜新星和地刺已经建立了可复用的技能包、行为模板、事件时间线和自测闭环。

连锁闪电的核心体验是“连续跳跃”，不是从玩家到目标的一条闪电线换皮；如果没有真实多目标跳跃、链段顺序、链半径、链次数限制和默认不重复命中同一目标，玩家看到的只是单体远程伤害，无法表达连锁技能语义。

## What Changes

- 规划将 `active_lightning_chain / 连锁闪电` 从旧技能模板迁移到未来的 `configs/skills/active/active_lightning_chain/skill.yaml`。
- 规划新增 `chain` behavior template，用于描述真实多目标链式跳跃、链段时序、链半径、跳跃次数、目标选择策略、伤害衰减和链段 VFX key。
- 迁移后的玩家实际体验目标为：“自动向最近敌人释放闪电链，命中初始目标后，在一定半径内跳跃到附近未命中的敌人，造成多段闪电伤害，并显示连续电弧、命中特效与伤害浮字。”
- 规划 SkillEditor 新增 `chain` 连锁模块，暴露 `chain` 模板全部字段，并通过 schema 和 template 白名单保存。
- 规划 SkillRuntime 通过真实 `chain_segment`、`damage`、`hit_vfx`、`floating_text`、`cooldown_update` 事件表达链段、命中、伤害和表现。
- 规划 Skill Test Arena 增加三目标横排、密集小怪和单体木桩验收连锁闪电。
- 规划 AI 自测报告基于真实测试结果判断连锁闪电是否符合玩家侧描述。
- 本 change 不迁移其他主动技能，不修改已迁移技能能力。
- 本 change 不做节点编辑器、不做脚本 DSL、不做复杂表达式解释器。
- 本轮只做 OpenSpec Explore 和 Propose，不写运行时代码，不改 WebApp，不创建 `active_lightning_chain/skill.yaml`。

## Capabilities

### New Capabilities

- 无。

### Modified Capabilities

- `v1-minimal-sudoku-gem-loop`: 增加连锁闪电 Skill Package、`chain` behavior template、SkillEditor 字段、SkillEvent、Skill Test Arena 和 AI 自测报告的验收要求。

## Impact

- 后续 Apply 允许新增或修改 `configs/skills/behavior_templates/chain.yaml`、`configs/skills/active/active_lightning_chain/skill.yaml`、技能 schema、中文本地化、SkillEditor、SkillRuntime、SkillEvent 消费、Skill Test Arena、AI 自测报告和相关测试。
- 后续 Apply 必须保留 `active_lava_orb`、`active_fungal_petards` 等未迁移技能旧路径，不得迁移其他主动技能。
- 后续 Apply 不得修改正式掉落、库存、宝石盘，不得恢复随机词缀 UI 或生成，不得引入英文玩家可见文案。
