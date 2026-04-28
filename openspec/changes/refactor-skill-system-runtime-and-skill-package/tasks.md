## 0. Phase 0：现状扫描与兼容边界确认

目标：确认当前技能系统、三类宝石字段迁移状态和第一轮垂直切片边界。

涉及模块：`configs/skills/`、`src/liufang/skill_effects.py`、`src/liufang/combat.py`、`src/liufang/presentation.py`、`webapp/App.tsx`、`webapp/styles.css`、`tests/`、`openspec/changes/refactor-three-gem-kinds-v1-phase2/`。

允许修改范围：仅允许记录扫描结论或在后续 Apply 中补充最小兼容注释与测试计划；不允许在 Phase 0 修改运行时代码。

禁止越界事项：不得修改 `refactor-three-gem-kinds-v1-phase2` artifacts；不得覆盖 `gem_kind` / `sudoku_digit` 字段模型；不得迁移技能配置。

验收标准：确认 `refactor-three-gem-kinds-v1-phase2` 是否仍 active，确认当前技能加载、最终实例、战斗扣血和 WebApp 表现推断入口。

推荐验证命令：

```powershell
cmd /c openspec list
cmd /c openspec validate refactor-three-gem-kinds-v1-phase2 --strict
```

- [x] 0.1 检查 OpenSpec active changes，并记录 `refactor-three-gem-kinds-v1-phase2` 状态。
- [x] 0.2 检查 `configs/skills/` 当前文件和 `skill_templates.toml` 的 8 个主动技能定义。
- [x] 0.3 检查 `FinalSkillInstance`、Combat Runtime 即时扣血路径和 WebApp 技能表现推断路径。
- [x] 0.4 确认 Apply 入口必须兼容 `gem_kind` / `sudoku_digit`，并锁定第一轮只做 `active_fire_bolt`。

## 1. Phase 1：Skill Package schema 与加载器

目标：建立 Skill Package 目录、`skill.schema.json` 和最小加载路径。

涉及模块：`configs/skills/schema/`、`configs/skills/active/active_fire_bolt/`、技能配置加载代码、配置校验工具、相关测试。

允许修改范围：仅新增 schema、火焰弹 `skill.yaml`、最小 Skill Package loader 和校验测试。

禁止越界事项：不得删除 `skill_templates.toml`；不得迁移其他 7 个技能；不得写任意脚本 DSL 或表达式解释器；不得引入英文玩家可见文案。

验收标准：`active_fire_bolt` 能从 `skill.yaml` 加载并通过 `skill.schema.json`；其他 7 个技能仍走旧路径。

推荐验证命令：

```powershell
python tools\validate_v1_configs.py
python -m unittest tests.test_skill_effects
cmd /c openspec validate refactor-skill-system-runtime-and-skill-package --strict
```

- [x] 1.1 新增 `configs/skills/schema/skill.schema.json`，覆盖必需字段、枚举、类型和模板引用边界。
- [x] 1.2 新增 `configs/skills/active/active_fire_bolt/skill.yaml`，只迁移火焰弹定义。
- [x] 1.3 新增或扩展 Skill Package loader，使其能读取火焰弹 package 并保留旧 `skill_templates.toml` 兼容路径。
- [x] 1.4 将 `active_fire_bolt` 的 display / presentation 字段限制为本地化 key。
- [x] 1.5 增加配置校验测试，覆盖 schema 成功、缺字段失败、非法模板失败和英文玩家文本防回归。

## 2. Phase 2：FinalSkillInstance 与 modifier 接口适配

目标：让 `FinalSkillInstance` 承接 Skill Package、宝石、被动、辅助、数独关系和 modifier 后的最终参数。

涉及模块：`src/liufang/skill_effects.py`、宝石定义加载、数独关系 / modifier 聚合、`tests/test_skill_effects.py`、`tests/test_presentation.py`。

允许修改范围：只扩展最终技能实例结构和火焰弹路径所需适配；允许保留旧字段兼容 WebApp 过渡。

禁止越界事项：不得把行为脚本写入 `FinalSkillInstance`；不得从旧 `gem_type` 推断宝石大类或数独数字；不得迁移其他 7 个技能。

验收标准：火焰弹能从 Skill Package 生成最终实例；被动、辅助、数独关系 modifier 仍按 `gem_kind` / `sudoku_digit` 兼容路径聚合；旧技能不回归。

推荐验证命令：

```powershell
python -m unittest tests.test_skill_effects tests.test_presentation
python -m unittest discover tests
```

- [x] 2.1 扩展 `FinalSkillInstance` 字段，记录 `skill_package_id`、模板、cast、hit、runtime 参数、presentation key 和来源上下文。
- [x] 2.2 适配火焰弹从 Skill Package 到 `FinalSkillInstance` 的构建路径。
- [x] 2.3 保持主动、被动、辅助、数独关系 modifier 聚合顺序不破坏现有三类宝石行为。
- [x] 2.4 增加测试覆盖火焰弹最终实例字段和旧技能兼容路径。

## 3. Phase 3：SkillEvent 管线

目标：定义并实现最小 `SkillEvent[]` 数据结构和 Skill Runtime 输出管线。

涉及模块：新增或扩展 Skill Runtime 代码、`src/liufang/combat.py`、`src/liufang/skill_effects.py`、事件序列化结构、Python 单元测试。

允许修改范围：只实现火焰弹需要的 `projectile_spawn`、`damage`、`hit_vfx`、`floating_text` 事件和通用事件类型定义。

禁止越界事项：不得用静态假事件替代真实 Skill Runtime 输出；不得一次实现全部行为模板；不得让 Combat Runtime 写具体技能分支。

验收标准：火焰弹释放能生成真实事件序列；`damage` 事件携带伤害、目标、伤害类型、技能实例 ID 和原因 key。

推荐验证命令：

```powershell
python -m unittest tests.test_combat tests.test_skill_effects
```

- [x] 3.1 定义 `SkillEvent` 类型，预留所有规范要求的事件类型和通用字段。
- [x] 3.2 新增 Skill Runtime 最小入口，接收 `FinalSkillInstance` 并调用白名单模板。
- [x] 3.3 实现 `projectile` 模板的火焰弹事件输出。
- [x] 3.4 增加测试断言火焰弹事件顺序和字段完整性。

## 4. Phase 4：火焰弹 projectile 垂直切片

目标：完成 `active_fire_bolt` 从 package 到投射物命中、伤害、VFX、浮字的完整闭环。

涉及模块：`configs/skills/active/active_fire_bolt/skill.yaml`、`configs/skills/behavior_templates/projectile.yaml`、Skill Runtime、Combat Runtime、测试。

允许修改范围：只允许实现 `active_fire_bolt` 和 `projectile` 模板所需最小逻辑。

禁止越界事项：不得迁移 `active_ice_shards`、`active_lightning_chain`、`active_frost_nova`、`active_puncture`、`active_penetrating_shot`、`active_lava_orb`、`active_fungal_petards`；不得破坏旧行为。

验收标准：火焰弹输出 `projectile_spawn`、`damage`、`hit_vfx`、`floating_text`；伤害时机与投射物命中时机一致；其他 7 个技能仍可运行。

推荐验证命令：

```powershell
python -m unittest tests.test_combat tests.test_skill_effects tests.test_v1_loop
python -m unittest discover tests
```

- [x] 4.1 新增 `configs/skills/behavior_templates/projectile.yaml`，声明允许参数和事件输出形态。
- [x] 4.2 将火焰弹释放接入 `projectile` 模板。
- [x] 4.3 调整 Combat Runtime 消费 `damage` 事件进行生命扣除。
- [x] 4.4 增加测试断言火焰弹命中前不扣血、命中时扣血。
- [x] 4.5 增加测试断言其他 7 个技能仍走旧路径且未被半迁移。

## 5. Phase 5：WebApp 消费 SkillEvent

目标：让 WebApp 通过 `SkillEvent[]` 渲染火焰弹表现。

涉及模块：`webapp/App.tsx`、`webapp/styles.css`、WebApp 数据适配层、前端 build。

允许修改范围：只接入火焰弹事件消费和最小事件渲染；允许复用现有样式，但以事件驱动。

禁止越界事项：不得继续用 `behavior_type + visual_effect` 猜火焰弹行为；不得实现完整前端技能运行时；不得新增英文玩家可见文案。

验收标准：WebApp 根据 `projectile_spawn` 渲染投射物，根据 `damage` / `hit_vfx` / `floating_text` 渲染命中和中文浮字；WebApp build 通过。

推荐验证命令：

```powershell
cmd /c npm run build
python -m unittest tests.test_presentation
```

- [x] 5.1 扩展 WebApp 数据模型，接收火焰弹 `SkillEvent[]`。
- [x] 5.2 将火焰弹投射物动画改为由 `projectile_spawn` 事件驱动。
- [x] 5.3 将命中特效和浮字改为由 `damage`、`hit_vfx`、`floating_text` 事件驱动。
- [x] 5.4 保留其他 7 个技能旧表现路径，不在第一轮强行改造。
- [x] 5.5 运行 WebApp build，并检查玩家可见文本仍为中文。

## 6. Phase 6：SkillEditor V0 基础壳

目标：实现浏览器内可视化技能编辑器基础结构，能打开已迁移的 Skill Package。

涉及模块：SkillEditor WebApp 入口、Skill Package 读取接口、`configs/skills/active/`、`skill.schema.json`、中文本地化、前端 smoke。

允许修改范围：只允许实现编辑器基础壳、文件列表、只读信息展示和 schema 状态展示。

禁止越界事项：不得打开未迁移的 7 个旧技能作为可编辑 Skill Package；不得迁移其他技能；不得创建节点编辑器；不得写任意脚本 DSL 或复杂表达式解释器。

验收标准：浏览器可打开 SkillEditor V0；列表只包含已迁移 Skill Package；第一版至少能打开 `active_fire_bolt/skill.yaml`；显示技能中文名、路径、`behavior.template` 和 schema 校验状态；所有玩家可见文本为中文。

推荐验证命令：

```powershell
python tools\validate_v1_configs.py
cmd /c npm run build
cmd /c npm test
cmd /c openspec validate refactor-skill-system-runtime-and-skill-package --strict
```

- [x] 6.1 新增 SkillEditor V0 浏览器入口或 WebApp 内编辑器视图。
- [x] 6.2 读取 `configs/skills/active/` 下已迁移 Skill Package 列表。
- [x] 6.3 只允许 `active_fire_bolt/skill.yaml` 作为第一版可打开 package。
- [x] 6.4 显示技能中文名、`skill.yaml` 路径、`behavior.template` 和 schema 校验状态。
- [x] 6.5 对未迁移 7 个主动技能显示不可编辑状态，不提供保存入口。

## 7. Phase 7：SkillEditor 模块化字段编辑

目标：按模块分类编辑 `active_fire_bolt` 当前已有字段。

涉及模块：SkillEditor 表单、`skill.schema.json`、`projectile` behavior template、保存接口、中文错误展示、前端 smoke。

允许修改范围：只允许编辑 schema 和 behavior template 白名单允许的字段；保存前必须校验。

禁止越界事项：不得写任意脚本；不得写表达式 DSL；不得把测试 modifier 写入真实 `skill.yaml`；不得引入英文玩家可见文案。

验收标准：编辑器按基础信息、释放参数、子弹、伤害点、表现、预览字段模块展示并编辑 `active_fire_bolt`；保存前校验；失败显示中文错误；保存后仍通过配置校验。

推荐验证命令：

```powershell
python tools\validate_v1_configs.py
python -m unittest discover tests
cmd /c npm run build
cmd /c npm test
```

- [x] 7.1 实现基础信息模块：`id` 只读、`version`、`display.name_key`、`display.description_key`、`classification.tags`、`classification.damage_type`、`classification.damage_form`。
- [x] 7.2 实现释放参数模块：`cast.mode`、`cast.target_selector`、`cast.search_range`、`cast.cooldown_ms`、`cast.windup_ms`、`cast.recovery_ms`。
- [x] 7.3 实现 `projectile` 子弹模块：`projectile_count`、`projectile_speed`、`projectile_width`、`projectile_height`、`max_distance`、`hit_policy`、`pierce_count`、`collision_radius`、`spawn_offset`、`travel_duration` 或只读飞行时间。
- [x] 7.4 实现伤害点模块：`hit.base_damage`、`hit.can_crit`、`hit.can_apply_status`、`damage_type`、`damage_form`、`damage_timing`、`hit_delay_ms`、`hit_radius`、`target_policy`。
- [x] 7.5 实现表现模块：`cast_vfx_key`、`projectile_vfx_key`、`hit_vfx_key`、`sfx_key`、`floating_text_style`、`hit_stop_ms`、`camera_shake`。
- [x] 7.6 实现预览字段模块：`preview.show_fields`。
- [x] 7.7 保存前执行 schema 和 behavior template 白名单校验，失败时显示中文错误。

## 8. Phase 8：Modifier 测试栈

目标：在编辑器中允许临时选择辅助宝石效果或 scaling modifier，用于测试 `active_fire_bolt` 在不同构筑条件下的实际表现。

涉及模块：SkillEditor 测试面板、`configs/gems/support_gems.toml`、`configs/skills/skill_scaling_rules.toml`、临时 `FinalSkillInstance` 构建、测试结果视图。

允许修改范围：只允许构建测试运行上下文，不写真实宝石实例，不写真实 `skill.yaml`。

禁止越界事项：不得恢复随机词缀生成；不得恢复随机词缀 UI；不得把随机词缀字段加入真实技能文件；不得把测试 modifier 写入真实宝石实例。

验收标准：可从辅助宝石配置或 scaling rules 选择一个或多个测试 modifier；可选择相邻、同行、同列、同宫关系；可设置 `source_power`、`target_power`、conduit 测试参数；测试 modifier 只影响测试运行。

推荐验证命令：

```powershell
python -m unittest discover tests
cmd /c npm run build
cmd /c npm test
```

- [ ] 8.1 从当前辅助宝石配置或 `skill_scaling_rules` 读取可测试 modifier。
- [ ] 8.2 支持选择一个或多个测试 modifier。
- [ ] 8.3 支持选择模拟关系：相邻、同行、同列、同宫。
- [ ] 8.4 支持设置 `source_power`、`target_power` 和 conduit 测试参数。
- [ ] 8.5 确认测试 modifier 只作用于测试运行，不写入真实数据。
- [ ] 8.6 增加防回归检查，确保不恢复随机词缀生成或随机词缀 UI。

## 9. Phase 9：Skill Test Arena

目标：提供技能测试专用场景，用来验证技能行为、伤害时机、命中目标和表现事件。

涉及模块：Skill Test Arena WebApp 视图、测试场景定义、Skill Runtime、SkillEvent 展示、前端 smoke、Python 测试。

允许修改范围：只允许实现受控测试场景和测试运行，不迁移剩余 7 个技能。

禁止越界事项：不得用静态假事件替代真实 SkillEvent；不得绕过 `FinalSkillInstance`；不得让测试场结果写入真实技能文件。

验收标准：测试场包含单体木桩、三目标横排、纵向队列、密集小怪；支持选择技能、启用或关闭测试 Modifier Stack、运行、暂停、单步、重置、查看怪物生命、命中目标、实际伤害和 SkillEvent 时间线。

推荐验证命令：

```powershell
python -m unittest discover tests
cmd /c npm run build
cmd /c npm test
```

- [ ] 9.1 实现单体木桩测试场景。
- [ ] 9.2 实现三目标横排测试场景。
- [ ] 9.3 实现纵向队列测试场景。
- [ ] 9.4 实现密集小怪测试场景。
- [ ] 9.5 支持选择 `active_fire_bolt` 并应用或关闭测试 Modifier Stack。
- [ ] 9.6 支持运行、暂停、单步和重置。
- [ ] 9.7 展示怪物生命、命中目标、实际伤害结果和 SkillEvent 时间线。
- [ ] 9.8 验证 `active_fire_bolt` 投射物飞行期间不扣血，到达目标后才生成 `damage` 并扣血。
- [ ] 9.9 验证修改 `projectile_speed`、`hit.base_damage` 和测试 modifier 后，`FinalSkillInstance` 与 SkillEvent 数值变化。

## 10. Phase 10：SkillEvent 时间线查看器

目标：在编辑器 / 测试场景中显示真实 SkillEvent 序列。

涉及模块：SkillEditor、Skill Test Arena、SkillEvent 序列化、时间线 UI、前端 smoke。

允许修改范围：只允许展示真实 SkillEvent，不创建假事件。

禁止越界事项：不得用前端猜测事件替代 Runtime 输出；不得隐藏关键事件字段；不得引入英文玩家可见文案。

验收标准：时间线至少显示 `cast_start`、`projectile_spawn`、`projectile_hit`、`damage`、`hit_vfx`、`floating_text`、`cooldown_update`；每个事件显示关键字段。

推荐验证命令：

```powershell
cmd /c npm run build
cmd /c npm test
```

- [ ] 10.1 显示 `cast_start`、`projectile_spawn`、`projectile_hit`、`damage`、`hit_vfx`、`floating_text`、`cooldown_update` 事件类型。
- [ ] 10.2 每个事件显示 `timestamp_ms`、`delay_ms`、`duration_ms`、`source_entity`、`target_entity`、`amount`、`damage_type`、`vfx_key`、`reason_key`、`payload`。
- [ ] 10.3 时间线数据来源必须是真实 SkillEvent 序列。

## 11. Phase 11：AI 自测报告

目标：提供 Codex 可运行、用户可审阅的技能自测报告机制。

涉及模块：Skill Test Arena 结果导出、报告生成工具、Markdown 或 JSON 输出、Python 测试、中文文本检查。

允许修改范围：只允许基于真实测试结果生成报告。

禁止越界事项：不得生成静态假报告；不得用英文自然语言报告；不得绕过真实 SkillEvent 和伤害结果。

验收标准：报告为 Markdown 或 JSON，自然语言部分中文；报告包含测试技能 ID、中文名、路径、模板、场景、测试 modifier、期望描述、实际 SkillEvent、伤害、命中目标、表现完整性、伤害时机一致性、是否符合描述、不一致项和建议修复。

推荐验证命令：

```powershell
python -m unittest discover tests
cmd /c npm test
```

- [ ] 11.1 定义真实测试结果到报告的数据结构。
- [ ] 11.2 生成 Markdown 或 JSON 自测报告。
- [ ] 11.3 报告包含测试技能 ID、技能中文名、`skill.yaml` 路径和 `behavior_template`。
- [ ] 11.4 报告包含测试场景、测试 Modifier Stack、期望玩家侧描述、实际 SkillEvent 序列、实际伤害结果和实际命中目标。
- [ ] 11.5 报告判断表现事件是否完整、伤害时机是否与表现一致、是否符合描述。
- [ ] 11.6 报告输出不一致项列表和建议修复项。

## 12. Phase 12：剩余 7 个主动技能迁移计划

目标：只规划剩余 7 个主动技能的迁移顺序和编辑器字段扩展要求，不实现迁移。

涉及模块：OpenSpec 任务记录、SkillEditor 字段扩展计划、behavior template 迁移计划。

允许修改范围：只允许补充计划，不允许迁移 7 个技能运行时或配置。

禁止越界事项：不得半迁移；不得创建未校验 `skill.yaml` 假完成；没有编辑器字段支持的技能不得标记为完成迁移。

验收标准：明确每个技能的 behavior template、编辑器字段扩展要求、测试场验收和 AI 自测报告要求。

推荐验证命令：

```powershell
cmd /c openspec validate refactor-skill-system-runtime-and-skill-package --strict
```

- [ ] 12.1 规划 `active_ice_shards -> fan_projectile`，并列出 SkillEditor 必须新增的 `fan_projectile` 字段。
- [ ] 12.2 规划 `active_lightning_chain -> chain`，并列出 SkillEditor 必须新增的 `chain` 字段。
- [ ] 12.3 规划 `active_frost_nova -> player_nova`，并列出 SkillEditor 必须新增的 `player_nova` 字段。
- [ ] 12.4 规划 `active_puncture -> melee_arc`，并列出 SkillEditor 必须新增的 `melee_arc` 字段。
- [ ] 12.5 规划 `active_penetrating_shot -> line_pierce`，并列出 SkillEditor 必须新增的 `line_pierce` 字段。
- [ ] 12.6 规划 `active_lava_orb -> orbit`，并列出 SkillEditor 必须新增的 `orbit` 字段。
- [ ] 12.7 规划 `active_fungal_petards -> delayed_area`，并列出 SkillEditor 必须新增的 `delayed_area` 字段。
- [ ] 12.8 明确每迁移一个 behavior template，SkillEditor 必须同步新增该模板所有可编辑字段。

## 13. Phase 13：验证与回归

目标：确保后续 SkillEditor、Skill Test Arena、AI 自测报告和现有技能运行能力全部通过回归。

涉及模块：全部本 change 后续 Apply 修改范围。

允许修改范围：只允许修复本 change 引入的问题；不得进行无关重构。

禁止越界事项：不得删除当前可运行能力；不得引入英文玩家可见文案；不得修改无关模块来绕过测试。

验收标准：OpenSpec strict validate、配置校验、Python 单元测试、WebApp build、WebApp smoke、中文玩家可见文本检查通过；`active_fire_bolt` SkillEditor 打开、编辑、保存、测试、报告生成闭环通过。

推荐验证命令：

```powershell
cmd /c openspec validate refactor-skill-system-runtime-and-skill-package --strict
python tools\validate_v1_configs.py
python -m unittest discover tests
cmd /c npm run build
cmd /c npm test
```

- [ ] 13.1 运行 `cmd /c openspec validate refactor-skill-system-runtime-and-skill-package --strict`。
- [ ] 13.2 运行 `python tools\validate_v1_configs.py`。
- [ ] 13.3 运行 `python -m unittest discover tests`。
- [ ] 13.4 运行 `cmd /c npm run build`。
- [ ] 13.5 运行 `cmd /c npm test`。
- [ ] 13.6 检查中文玩家可见文本。
- [ ] 13.7 验证 `active_fire_bolt` SkillEditor 打开、编辑、保存、测试、报告生成闭环。
