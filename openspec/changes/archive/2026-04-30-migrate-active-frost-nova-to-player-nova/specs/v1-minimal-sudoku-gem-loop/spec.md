## ADDED Requirements

### Requirement: 冰霜新星 Skill Package
V1 SHALL migrate `active_frost_nova` / `冰霜新星` from the old centralized skill template path into an active Skill Package.

#### Scenario: 从 active Skill Package 加载冰霜新星
- **WHEN** `active_frost_nova` is considered migrated
- **THEN** the system SHALL load it from `configs/skills/active/active_frost_nova/skill.yaml`

#### Scenario: 使用 player_nova 行为模板
- **WHEN** the migrated `active_frost_nova` Skill Package is validated
- **THEN** it SHALL declare `behavior.template = player_nova`

#### Scenario: 保持中文玩家可见文本
- **WHEN** `active_frost_nova` name, description, damage reason, floating text, VFX feedback, or screen feedback is shown to the player
- **THEN** the player-visible text SHALL be Chinese and SHALL come from localization keys rather than embedded English text

#### Scenario: 不迁移其他主动技能
- **WHEN** this migration is applied
- **THEN** `active_lightning_chain`, `active_puncture`, `active_lava_orb`, and `active_fungal_petards` SHALL remain on their existing behavior paths unless a later change migrates them explicitly

### Requirement: player_nova Behavior Template
V1 SHALL provide a whitelisted `player_nova` Behavior Template for deterministic player-centered expanding nova skills.

#### Scenario: 以玩家为中心生成范围新星 SkillEvent
- **WHEN** Skill Runtime executes a skill using `player_nova`
- **THEN** it SHALL generate an `area_spawn` SkillEvent centered on the player or cast source position using declared radius, ring width, expansion duration, hit timing, target cap, damage falloff, and presentation params

#### Scenario: 声明 player_nova 参数白名单
- **WHEN** `configs/skills/behavior_templates/player_nova.yaml` is validated
- **THEN** it SHALL declare allowed params including `radius`, `expand_duration_ms`, `hit_at_ms`, `max_targets`, `center_policy`, `damage_falloff_by_distance`, `ring_width`, and `status_chance_scale`

#### Scenario: 校验 player_nova 参数约束
- **WHEN** a Skill Package declares `behavior.template = player_nova`
- **THEN** validation SHALL require positive `radius`, non-negative `expand_duration_ms`, non-negative `hit_at_ms`, `hit_at_ms` not greater than `expand_duration_ms`, positive integer or explicitly declared unlimited `max_targets`, `center_policy = player_center`, legal `damage_falloff_by_distance`, positive `ring_width`, and ranged `status_chance_scale`

#### Scenario: 禁止脚本和未声明参数
- **WHEN** a Skill Package declares `behavior.template = player_nova`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, frontend-only fake params, and any params not declared by the `player_nova` template

### Requirement: SkillEditor player_nova 字段支持
SkillEditor SHALL expose and validate every editable `player_nova` field before `active_frost_nova` is considered migrated.

#### Scenario: 暴露 player_nova 范围新星模块字段
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template` is `player_nova`
- **THEN** it SHALL expose editable fields for `radius`, `expand_duration_ms`, `hit_at_ms`, `max_targets`, `center_policy`, `damage_falloff_by_distance`, `ring_width`, and `status_chance_scale`, plus read-only range summary and hit timing summary

#### Scenario: 使用枚举和范围校验
- **WHEN** SkillEditor edits or saves a `player_nova` Skill Package
- **THEN** `center_policy` SHALL use an enum limited to player center in the first version, `radius`, `expand_duration_ms`, `hit_at_ms`, `ring_width`, and `status_chance_scale` SHALL use declared range validation, and `max_targets` SHALL use integer validation or an explicitly declared unlimited enum

#### Scenario: 使用 schema 和模板白名单校验
- **WHEN** SkillEditor saves a `player_nova` Skill Package
- **THEN** it SHALL validate through both the skill schema and behavior template whitelist and SHALL NOT write undeclared fields or frontend-only fake params

#### Scenario: 输出中文校验错误
- **WHEN** SkillEditor rejects invalid `player_nova` values such as `hit_at_ms > expand_duration_ms`, invalid enum values, or invalid numeric ranges
- **THEN** it SHALL display Chinese error text and SHALL NOT write invalid skill data

### Requirement: 冰霜新星 SkillEvent
`active_frost_nova` SHALL express area generation, hit timing, damage, and presentation through real SkillEvents.

#### Scenario: 输出 area_spawn
- **WHEN** migrated `active_frost_nova` is cast
- **THEN** Skill Runtime SHALL output an `area_spawn` event centered on the player or cast source position with radius, ring width, duration, hit timing, damage type, VFX key, and payload data

#### Scenario: 按玩家中心半径判断命中
- **WHEN** `active_frost_nova` resolves targets
- **THEN** targets inside the player-centered radius SHALL be eligible for hit and targets outside the radius SHALL NOT be hit

#### Scenario: damage 事件负责扣血
- **WHEN** `active_frost_nova` is cast
- **THEN** target life SHALL NOT be reduced at release time or before `hit_at_ms`, and life reduction SHALL be caused by `damage` events at or after `hit_at_ms`

#### Scenario: 输出伤害和表现事件
- **WHEN** an in-range target is hit by `active_frost_nova`
- **THEN** Skill Runtime SHALL output `damage`, `hit_vfx`, and `floating_text` events for that target after or with the hit timing

#### Scenario: 冰霜伤害类型
- **WHEN** `active_frost_nova` emits a `damage` event
- **THEN** the event SHALL declare `damage_type = cold`

#### Scenario: 禁止目标点爆炸和静态假事件
- **WHEN** Skill Runtime executes `active_frost_nova`
- **THEN** it SHALL NOT use target-point explosion semantics, static fake events, or a Combat Runtime branch specific to `active_frost_nova`

### Requirement: 冰霜新星测试场验收
Skill Test Arena SHALL validate migrated `active_frost_nova` through controlled scenarios that prove player-centered area behavior.

#### Scenario: 密集小怪验证范围多目标命中
- **WHEN** Skill Test Arena runs migrated `active_frost_nova` in the dense small monster scenario
- **THEN** it SHALL verify the nova is centered on the player, multiple in-range enemies can be hit, and out-of-range enemies are not hit

#### Scenario: 单体木桩验证伤害时序
- **WHEN** Skill Test Arena runs migrated `active_frost_nova` against a single dummy
- **THEN** it SHALL verify no life is reduced before `hit_at_ms` and life is reduced only by `damage` events at or after `hit_at_ms`

#### Scenario: 三目标横排验证范围边界
- **WHEN** Skill Test Arena runs migrated `active_frost_nova` in the three-target horizontal row scenario
- **THEN** it SHALL verify that targets inside the configured radius are hit and targets outside the configured radius are not hit

#### Scenario: 参数修改影响真实测试结果
- **WHEN** SkillEditor or the arena test stack changes `radius`, `expand_duration_ms`, or `hit_at_ms`
- **THEN** Skill Test Arena SHALL show changed target coverage, changed presentation timing, or changed damage timing respectively

#### Scenario: Modifier 测试栈影响结果
- **WHEN** Skill Test Arena runs `active_frost_nova` with a test Modifier Stack
- **THEN** the stack SHALL affect final damage or range runtime parameters used by actual SkillEvents without writing real inventory, gem instance, or Skill Package data

### Requirement: 冰霜新星 AI 自测报告
The AI self-test report SHALL evaluate migrated `active_frost_nova` against real Skill Test Arena results and the expected Chinese player-facing behavior.

#### Scenario: 基于真实结果判断玩家侧描述
- **WHEN** an AI self-test report is generated for migrated `active_frost_nova`
- **THEN** it SHALL compare actual SkillEvent sequences, damage results, hit targets, and presentation events against the expected description "自动以玩家自身为中心释放一圈向外扩散的冰霜新星，命中范围内敌人后造成冰霜伤害，并显示冰霜范围爆发特效与伤害浮字。"

#### Scenario: 检查 area_spawn 和玩家中心
- **WHEN** the report evaluates `active_frost_nova`
- **THEN** it SHALL check whether `area_spawn` exists and whether its center is the player or cast source position

#### Scenario: 检查关键事件和时序
- **WHEN** the report evaluates `active_frost_nova`
- **THEN** it SHALL check whether `damage`, `hit_vfx`, and `floating_text` exist, whether `damage` is not earlier than `hit_at_ms`, whether no life is reduced before `hit_at_ms`, and whether `damage_type` is `cold`

#### Scenario: 检查范围命中规则
- **WHEN** the report evaluates `active_frost_nova`
- **THEN** it SHALL check whether in-range targets are hit, out-of-range targets are not hit, and changing `radius` changes hit target coverage

#### Scenario: 输出中文结论和修复建议
- **WHEN** the report finishes evaluation
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes
