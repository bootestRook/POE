## ADDED Requirements

### Requirement: 冰棱散射 Skill Package
V1 SHALL migrate `active_ice_shards` / `冰棱散射` from the old centralized skill template path into an active Skill Package after the `active_fire_bolt` vertical slice is complete.

#### Scenario: 从 active Skill Package 加载冰棱散射
- **WHEN** `active_ice_shards` is considered migrated
- **THEN** the system SHALL load it from `configs/skills/active/active_ice_shards/skill.yaml`

#### Scenario: 使用 fan_projectile 行为模板
- **WHEN** the migrated `active_ice_shards` Skill Package is validated
- **THEN** it SHALL declare `behavior.template = fan_projectile`

#### Scenario: 保持中文玩家可见文本
- **WHEN** `active_ice_shards` name, description, hit reason, floating text, VFX feedback, or screen feedback is shown to the player
- **THEN** the player-visible text SHALL be Chinese and SHALL come from localization keys rather than embedded English text

#### Scenario: 不迁移其他主动技能
- **WHEN** this migration is applied
- **THEN** `active_lightning_chain`, `active_frost_nova`, `active_puncture`, `active_penetrating_shot`, `active_lava_orb`, and `active_fungal_petards` SHALL remain on their existing behavior paths unless a later change migrates them explicitly

### Requirement: fan_projectile Behavior Template
V1 SHALL provide a whitelisted `fan_projectile` Behavior Template for deterministic fan-shaped multi-projectile skills.

#### Scenario: 生成扇形多投射 SkillEvent
- **WHEN** Skill Runtime executes a skill using `fan_projectile`
- **THEN** it SHALL generate multiple projectile SkillEvents spread across a fan based on target direction, projectile count, spread angle, angle step, speed, distance, spawn pattern, and hit policy

#### Scenario: 声明 fan_projectile 参数白名单
- **WHEN** `configs/skills/behavior_templates/fan_projectile.yaml` is validated
- **THEN** it SHALL declare allowed params including `projectile_count`, `projectile_speed`, `projectile_width`, `projectile_height`, `spread_angle`, `angle_step`, `max_distance`, `hit_policy`, `collision_radius`, `spawn_pattern`, and `per_projectile_damage_scale`

#### Scenario: 禁止脚本和未声明参数
- **WHEN** a Skill Package declares `behavior.template = fan_projectile`
- **THEN** validation SHALL reject scripts, expression DSL fields, complex expression interpreter fields, function-call strings, and any params not declared by the `fan_projectile` template

### Requirement: SkillEditor fan_projectile 字段支持
SkillEditor SHALL expose and validate every editable `fan_projectile` field before any skill using `fan_projectile` is considered migrated.

#### Scenario: 暴露 fan_projectile 子弹模块字段
- **WHEN** SkillEditor opens a Skill Package whose `behavior.template` is `fan_projectile`
- **THEN** it SHALL expose editable fields for `projectile_count`, `projectile_speed`, `projectile_width`, `projectile_height`, `spread_angle`, `angle_step`, `max_distance`, `hit_policy`, `collision_radius`, `spawn_pattern`, and `per_projectile_damage_scale`, plus a read-only flight time or per-projectile flight time summary

#### Scenario: 使用 schema 和模板白名单校验
- **WHEN** SkillEditor edits or saves a `fan_projectile` Skill Package
- **THEN** it SHALL validate values through both the skill schema and behavior template whitelist and SHALL NOT write fields that the template does not declare

#### Scenario: 校验 fan_projectile 数值和枚举
- **WHEN** SkillEditor validates `fan_projectile` params
- **THEN** `projectile_count` SHALL be a positive integer, `spread_angle` and `angle_step` SHALL respect declared ranges, `projectile_speed`, `projectile_width`, `projectile_height`, `max_distance`, and `collision_radius` SHALL be legal positive numbers, `hit_policy` and `spawn_pattern` SHALL use declared enum values, and `per_projectile_damage_scale` SHALL respect its declared numeric range

### Requirement: 冰棱散射 SkillEvent
`active_ice_shards` SHALL express projectile generation, hit, damage, and presentation through real SkillEvents.

#### Scenario: 输出多条 projectile_spawn
- **WHEN** migrated `active_ice_shards` is cast with `projectile_count` greater than one
- **THEN** Skill Runtime SHALL output one `projectile_spawn` event per generated ice shard with independent direction data

#### Scenario: 命中后输出结算和表现事件
- **WHEN** an ice shard hits a target according to real collision or hit policy resolution
- **THEN** Skill Runtime SHALL output `projectile_hit`, `damage`, `hit_vfx`, and `floating_text` events for that hit

#### Scenario: damage 事件负责扣血
- **WHEN** `active_ice_shards` is cast
- **THEN** target life SHALL NOT be reduced at release time, and life reduction SHALL be caused by `damage` events after projectile travel and hit timing

#### Scenario: 冰霜伤害类型
- **WHEN** `active_ice_shards` emits a `damage` event
- **THEN** the event SHALL declare `damage_type = cold`

### Requirement: 冰棱散射测试场验收
Skill Test Arena SHALL validate migrated `active_ice_shards` through controlled scenarios that prove fan-shaped multi-projectile behavior.

#### Scenario: 三目标横排验证扇形多投射
- **WHEN** Skill Test Arena runs migrated `active_ice_shards` in the three-target horizontal row scenario
- **THEN** it SHALL verify multiple ice shard spawns, visible fan angle distribution, real hit targets, and damage only after projectile hit timing

#### Scenario: 密集小怪验证多目标覆盖
- **WHEN** Skill Test Arena runs migrated `active_ice_shards` in the dense small monster scenario
- **THEN** it SHALL verify that hit targets come from real projectile collision or hit policy resolution and that multiple projectiles can affect the result

#### Scenario: 单体木桩验证基础伤害时序
- **WHEN** Skill Test Arena runs migrated `active_ice_shards` against a single dummy
- **THEN** it SHALL verify no life is reduced during projectile flight and life is reduced only after `projectile_hit` and `damage`

#### Scenario: 参数修改影响实际事件
- **WHEN** SkillEditor or the arena test stack changes `projectile_count`, `spread_angle`, or `projectile_speed`
- **THEN** Skill Test Arena SHALL show changed projectile event count, changed fan direction distribution, or changed flight time respectively

#### Scenario: Modifier 测试栈影响结果
- **WHEN** Skill Test Arena runs `active_ice_shards` with a test Modifier Stack
- **THEN** the stack SHALL affect final damage or projectile runtime parameters used by actual SkillEvents without writing real inventory, gem instance, or Skill Package data

### Requirement: 冰棱散射 AI 自测报告
The AI self-test report SHALL evaluate migrated `active_ice_shards` against real Skill Test Arena results and the expected Chinese player-facing behavior.

#### Scenario: 基于真实结果判断玩家侧描述
- **WHEN** an AI self-test report is generated for migrated `active_ice_shards`
- **THEN** it SHALL compare actual SkillEvent sequences, damage results, hit targets, and presentation events against the expected description "自动向最近敌人方向射出多枚冰霜冰棱，冰棱以扇形展开飞行，命中后造成冰霜伤害，并显示冰霜命中特效与伤害浮字。"

#### Scenario: 检查关键事件和时序
- **WHEN** the report evaluates `active_ice_shards`
- **THEN** it SHALL check whether multiple `projectile_spawn` events exist, projectile directions form a fan, `projectile_hit` exists, `damage` exists, `hit_vfx` exists, `floating_text` exists, `damage` is not earlier than `projectile_spawn`, no life is reduced during projectile flight, and `damage_type` is `cold`

#### Scenario: 检查参数修改效果
- **WHEN** the report compares baseline and modified arena runs
- **THEN** it SHALL check whether changing `projectile_count` changes projectile event count and whether changing `spread_angle` changes projectile directions

#### Scenario: 输出中文结论和修复建议
- **WHEN** the report finishes evaluation
- **THEN** it SHALL output a conclusion of `通过`, `部分通过`, or `不通过`, plus Chinese inconsistency items and suggested fixes
