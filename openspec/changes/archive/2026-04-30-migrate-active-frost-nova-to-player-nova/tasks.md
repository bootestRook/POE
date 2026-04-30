## Phase 0: 现状扫描与已迁移技能模板能力确认

- [x] 0.1 目标：确认 `migrate-active-ice-shards-to-fan-projectile` 已归档、`active_penetrating_shot` 已迁移、当前 active changes 状态、已迁移 Skill Package 至少包含 `active_fire_bolt` / `active_ice_shards` / `active_penetrating_shot`、`active_frost_nova` 仍走旧 `skill_templates.toml` 路径；允许修改范围：只读 OpenSpec 状态、`configs/skills/active/`、`configs/gems/active_skill_gems.toml`、`configs/skills/skill_templates.toml`、SkillEditor/Test Arena/report 现有能力；禁止越界事项：不得创建 `active_frost_nova/skill.yaml`、不得改 runtime/WebApp/正式库存掉落宝石盘；验收标准：记录归档状态、active changes、迁移模板能力、旧路径证据；推荐验证命令：`cmd /c openspec list --json`、`Get-ChildItem configs\skills\active -Directory`、`Select-String -Path configs\skills\skill_templates.toml -Pattern "skill_frost_nova"`。

## Phase 1: `player_nova` schema / behavior template 设计

- [x] 1.1 目标：新增并校验 `configs/skills/behavior_templates/player_nova.yaml` 字段白名单；允许修改范围：behavior template 配置、`configs/skills/schema/skill.schema.json`、`src/liufang/config.py`、`tools/validate_v1_configs.py`、相关配置测试；禁止越界事项：不得引入脚本、表达式 DSL、复杂表达式解释器、未声明参数透传或前端专属假参数；验收标准：字段至少包含 `radius`、`expand_duration_ms`、`hit_at_ms`、`max_targets`、`center_policy`、`damage_falloff_by_distance`、`ring_width`、`status_chance_scale`，并校验正数、非负数、`hit_at_ms <= expand_duration_ms`、枚举和范围；推荐验证命令：`python tools\validate_v1_configs.py`、`python -m unittest tests.test_skill_editor -v`。

## Phase 2: `active_frost_nova` Skill Package 创建

- [x] 2.1 目标：创建未来路径 `configs/skills/active/active_frost_nova/skill.yaml` 并迁移冰霜新星；允许修改范围：`active_frost_nova` Skill Package、必要中文本地化 key、配置加载/校验的最小适配；禁止越界事项：不得迁移 `active_lightning_chain`、`active_puncture`、`active_lava_orb`、`active_fungal_petards` 或其他技能，不得修改已迁移技能能力，不得恢复随机词缀 UI/生成；验收标准：package 包含 id、version、display、classification、cast、behavior、hit、scaling、presentation、preview，且 `classification.damage_type = cold`、`behavior.template = player_nova`、玩家可见文本为中文 key；推荐验证命令：`python tools\validate_v1_configs.py`、`python -m unittest tests.test_skill_effects -v`、`python -m unittest tests.test_skill_editor -v`。

## Phase 3: SkillEditor 新增 `player_nova` 模块字段

- [x] 3.1 目标：在 SkillEditor 中新增 `player_nova` 范围新星模块；允许修改范围：`src/liufang/skill_editor.py`、`webapp/App.tsx`、`webapp/styles.css`、编辑器保存校验、相关测试；禁止越界事项：不得写入模板未声明字段，不得把范围字段写成前端专属假参数，不得创建节点编辑器或脚本 DSL；验收标准：字段覆盖 `radius`、`expand_duration_ms`、`hit_at_ms`、`max_targets`、`center_policy`、`damage_falloff_by_distance`、`ring_width`、`status_chance_scale`、只读范围摘要、只读命中时机摘要；推荐验证命令：`python -m unittest tests.test_skill_editor -v`、`cmd /c npm test`、`cmd /c npm run build`。

- [x] 3.2 目标：补齐 `player_nova` 中文校验错误；允许修改范围：schema/template whitelist validation 和 WebApp 保存前校验；禁止越界事项：不得绕过后端 schema 保存非法参数；验收标准：非法 `radius`、`expand_duration_ms`、`hit_at_ms`、`hit_at_ms > expand_duration_ms`、`max_targets`、`center_policy`、`damage_falloff_by_distance`、`ring_width`、`status_chance_scale`、未知字段均被拒绝且错误为中文；推荐验证命令：`python -m unittest tests.test_skill_editor -v`、`python tools\validate_v1_configs.py`。

## Phase 4: SkillRuntime 实现 `player_nova`

- [x] 4.1 目标：实现玩家中心范围新星 SkillEvent 生成；允许修改范围：`src/liufang/skill_runtime.py`、`src/liufang/skill_effects.py`、必要 runtime helper 和单元测试；禁止越界事项：不得按目标点爆炸，不得释放瞬间无视 `hit_at_ms` 直接扣血，不得使用静态假事件，不得在 Combat Runtime 写 `active_frost_nova` 专属分支；验收标准：输出 `cast_start`、`area_spawn`、`damage`、`hit_vfx`、`floating_text`，`area_spawn` 中心为玩家/释放源，按 `radius` 命中，范围外不命中，`damage_type = cold`；推荐验证命令：`python -m unittest tests.test_skill_runtime -v`、`python -m unittest tests.test_combat -v`。

- [x] 4.2 目标：实现时序与参数影响；允许修改范围：SkillRuntime damage timing、target selection、payload 字段、modifier runtime params；禁止越界事项：不得让 VFX 替代伤害结算，不得让前端猜伤害时机；验收标准：`hit_at_ms` 前不扣血，`damage` 在 `hit_at_ms` 后由事件扣血，`radius` 改变命中覆盖，`expand_duration_ms` 改变 `area_spawn.duration_ms`，`hit_at_ms` 改变 damage delay，Modifier 测试栈能影响最终伤害或范围参数；推荐验证命令：`python -m unittest discover tests`。

## Phase 5: WebApp 消费 `player_nova` SkillEvent

- [x] 5.1 目标：WebApp 根据真实 `area_spawn` 渲染玩家中心冰霜新星；允许修改范围：`webapp/App.tsx`、`webapp/styles.css`、`webapp/smoke-test.mjs`、必要表现资源引用；禁止越界事项：不得通过 `behavior_type`、`visual_effect` 或 skill id 猜测行为，不得新增静态假事件，不得引入英文玩家可见文案；验收标准：新星中心、半径、扩散时长、VFX、damage、hit_vfx、floating_text 均由 SkillEvent 驱动；推荐验证命令：`cmd /c npm test`、`cmd /c npm run build`。

## Phase 6: Skill Test Arena 接入冰霜新星

- [x] 6.1 目标：Skill Test Arena 支持选择并运行 `active_frost_nova`；允许修改范围：`src/liufang/skill_editor.py`、`src/liufang/web_api.py`、`tools/webapp_server.py`、WebApp 测试场 UI、相关测试；禁止越界事项：不得写真实 inventory、gem instance、production skill files 之外的数据，不得迁移其他技能；验收标准：密集小怪、单体木桩、三目标横排场景可运行冰霜新星；推荐验证命令：`python -m unittest tests.test_skill_editor -v`、`cmd /c npm test`。

- [x] 6.2 目标：验证真实范围效果和参数变化；允许修改范围：arena runner、scenario fixtures、result model、测试栈参数覆盖；禁止越界事项：不得只改 UI 数字而不影响 SkillEvents；验收标准：新星以玩家为中心，范围内多个敌人命中，范围外敌人不命中，`hit_at_ms` 前不扣血，命中后通过 `damage` 扣血，修改 `radius` / `expand_duration_ms` / `hit_at_ms` 产生真实差异，Modifier 测试栈影响最终伤害或范围参数；推荐验证命令：`python -m unittest tests.test_skill_editor -v`、`python -m unittest tests.test_skill_runtime -v`。

## Phase 7: SkillEvent 时间线与 AI 自测报告接入冰霜新星

- [x] 7.1 目标：SkillEvent 时间线显示 `active_frost_nova` 真实事件；允许修改范围：timeline event mapping、field display、test arena result serialization、WebApp timeline display；禁止越界事项：不得展示静态示例事件，不得隐藏关键字段；验收标准：显示 `cast_start`、`area_spawn`、`damage`、`hit_vfx`、`floating_text`、存在时的 `cooldown_update`，字段包含 `timestamp_ms`、`delay_ms`、`duration_ms`、`source_entity`、`target_entity`、`amount`、`damage_type`、`vfx_key`、`reason_key`、`payload`；推荐验证命令：`python -m unittest tests.test_skill_editor -v`、`cmd /c npm test`。

- [x] 7.2 目标：AI 自测报告支持 `active_frost_nova`；允许修改范围：`src/liufang/skill_test_report.py`、`tools/generate_skill_test_report.py`、报告测试；禁止越界事项：不得基于静态假事件或手写结论生成通过，不得输出英文自然语言报告；验收标准：`python tools/generate_skill_test_report.py --skill active_frost_nova --scenario dense_pack` 可运行，报告检查 `area_spawn`、玩家中心、damage、hit_vfx、floating_text、`hit_at_ms` 时序、范围内/外命中、`damage_type = cold`、`radius` 修改效果，结论为 `通过` / `部分通过` / `不通过`，不一致项和建议修复项为中文；推荐验证命令：`python -m unittest tests.test_skill_test_report -v`、`python tools\generate_skill_test_report.py --skill active_frost_nova --scenario dense_pack`。

## Phase 8: 验证与回归

- [x] 8.1 目标：运行 OpenSpec、配置和后端回归验证；允许修改范围：仅修复本 change 范围内验证失败；禁止越界事项：不得借验证失败重构无关模块，不得修改正式掉落、库存、宝石盘或已迁移技能能力；验收标准：OpenSpec strict validate、配置校验、Python 单元测试通过；推荐验证命令：`cmd /c openspec validate migrate-active-frost-nova-to-player-nova --strict`、`python tools\validate_v1_configs.py`、`python -m unittest discover tests`。

- [x] 8.2 目标：运行 WebApp 和报告验收；允许修改范围：仅修复 `player_nova` WebApp consumption、Skill Test Arena、timeline、AI report 相关问题；禁止越界事项：不得恢复随机词缀 UI/生成，不得出现英文玩家可见文本；验收标准：`active_fire_bolt`、`active_ice_shards`、`active_penetrating_shot` 无回归，其他未迁移技能保持未迁移，WebApp build/test 通过，冰霜新星 AI 自测报告生成；推荐验证命令：`cmd /c npm run build`、`cmd /c npm test`、`python tools\generate_skill_test_report.py --skill active_frost_nova --scenario dense_pack`。


