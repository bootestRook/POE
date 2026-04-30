---
name: 2d-character-animation-pipeline
description: Use this skill when producing, directing, slicing, mirroring, validating, importing, or reviewing 2D / 2.5D character sprite animation frames. It is designed for AI-assisted game sprite production where character consistency, per-frame pose control, fixed grid slicing, and engine-ready sprite sheets are required.
---

# 2D Character Animation Pipeline Skill

## 目标

把 AI 生成的 2D / 2.5D 角色动作资源整理成项目可用的序列帧资源。

本 skill 同时覆盖两层工作：

1. **Animation Frame Director**：先定义每个动作、每一帧应该怎么动。
2. **Sprite Sheet Production**：再做切帧、镜像、命名、校验、manifest、测试场景接入。

禁止直接跳过动作帧设计去生成完整 sprite sheet。

---

## 使用场景

当用户提出以下需求时，应使用本 skill：

- 制作角色 idle / walk / run / attack / cast / hit / death 动作序列帧。
- 将 AI 生成的动作行图切成单帧 PNG。
- 将 right-facing 动作镜像成 left-facing。
- 生成可被游戏读取的 sprite manifest。
- 检查角色序列帧是否可用。
- 搭建独立 sprite test scene 做动作自测。
- 修复帧间漂移、左右不分、动作不连续、sheet 不可裁剪等问题。

---

## 固定项目约束

- 所有给用户审阅的 Markdown 文档必须使用中文；OpenSpec 必需关键字可保留英文。
- 不修改战斗数值。
- 不修改技能逻辑。
- 不修改角色属性。
- 不修改敌人逻辑。
- 不把截图或图片中的内容写入需求或指令，除非用户明确要求引用图片内容。
- 不在资源制作任务中顺手重构无关模块。
- 不为了制作资源引入运行时规则变更。
- 资源处理必须可回滚、可复查、可脚本化。

---

## 核心原则

### 1. 先导演动作，再生产图片

任何动作资源生产前，必须先输出 `Action Frame Plan`。

没有 `Action Frame Plan`，不得直接生成、切分、拼接 sprite sheet。

### 2. right-facing 是母版方向

默认只让 AI 生成 `right` 方向。

`left` 方向默认由 `right` 水平镜像得到。

除非用户明确要求处理非对称角色，否则不要单独 AI 生成 `left`。

### 3. 单动作单方向生产

不要一次性让 AI 生成多个动作和多个方向。

推荐顺序：

1. anchor 角色图。
2. `idle_right`。
3. `walk_right`。
4. `run_right`。
5. `attack_right` / `cast_right`，按需。
6. 脚本镜像生成 left。
7. 脚本拼接最终 sheet。
8. 独立测试场景验收。

### 4. 工程处理不替代动作设计

切帧、镜像、校验只能保证资源格式可用。

动作是否成立，必须由每帧姿势计划和测试场景检查决定。

---

# 工作流

## Step 1：收集输入

开始前确认或读取以下输入：

- 角色名。
- 资源目录。
- 角色 anchor 图路径，可选但强烈推荐。
- 动作类型：idle / walk / run / attack / cast / hit / death。
- 单帧尺寸，默认 `256x256`。
- 每个动作帧数。
- 视角：top-down / 2.5D / dimetric / side-view。
- 是否需要透明背景。
- 是否需要生成测试场景。

若信息缺失，使用以下默认值：

```yaml
frame_size: 256x256
direction_master: right
left_generation: mirror_from_right
background: transparent
naming_style: action_direction_index
output_report_language: zh-CN
```

---

## Step 2：生成 Action Frame Plan

每个动作都必须先生成一份 Action Frame Plan。

格式如下：

```md
# Action Frame Plan：<action_id>

## 基础信息

- action_id：walk_right
- character_id：<角色ID>
- direction：right
- frame_count：6
- frame_size：256x256
- loop_type：loop
- view：2.5D / dimetric
- anchor_point：脚底中心
- output：单行动作图 + 单帧 PNG

## 不变量

- 发型不变。
- 服装不变。
- 武器不变。
- 身高比例不变。
- 头身比例不变。
- 主色不变。
- 面向必须是屏幕右侧。
- 脚底锚点保持稳定。

## 每帧姿势表

| 帧 | 帧类型 | 重心 | 头部 | 躯干 | 左臂 | 右臂 | 左腿 | 右腿 | 衣摆/头发 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | key | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 1 | inbetween | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## 禁止项

- 不改变角色设计。
- 不改变角色朝向。
- 不让角色在格子内漂移。
- 不生成文字、水印、边框、网格线。
- 不把 left 与 right 混在同一生成任务中。

## 验收标准

- 每帧可被裁剪成 256x256。
- 循环动作首尾可衔接。
- 关键帧动作意图清晰。
- 非关键帧只做合理过渡。
- 脚底锚点稳定。
- 角色身份一致。
```

---

## Step 3：使用动作帧库

优先使用以下标准帧结构。

## idle_right：4 帧

用途：轻微呼吸循环。

| 帧 | 帧类型 | 姿势目的 | 具体要求 |
|---|---|---|---|
| 0 | key | 标准站姿 | 面向右侧，双脚稳定，身体自然站立 |
| 1 | inbetween | 呼吸上升 | 肩部略抬，胸口轻微上移，脚底不动 |
| 2 | key | 呼吸最高点 | 头发和衣摆轻微滞后，身体不位移 |
| 3 | inbetween | 回落 | 接近第 0 帧，能自然循环 |

验收重点：动作幅度小，不能像走路，脚底不能滑动。

---

## walk_right：6 帧

用途：标准步行动作。

| 帧 | 帧类型 | 姿势目的 | 腿部 | 手臂 | 身体 | 附属物 |
|---|---|---|---|---|---|---|
| 0 | key | 接触帧 A | 右脚前伸接触地面，左脚后蹬 | 左臂前，右臂后 | 身体略向右前 | 头发/衣摆向后轻摆 |
| 1 | inbetween | 下压帧 A | 双腿承重，重心略低 | 手臂回中 | 身体最低点 | 衣摆下坠 |
| 2 | inbetween | 通过帧 A | 左脚从后方经过身体下方 | 手臂开始交换 | 身体回中 | 轻微滞后 |
| 3 | key | 接触帧 B | 左脚前伸接触地面，右脚后蹬 | 右臂前，左臂后 | 身体略向右前 | 头发/衣摆向后轻摆 |
| 4 | inbetween | 下压帧 B | 双腿承重，重心略低 | 手臂回中 | 身体最低点 | 衣摆下坠 |
| 5 | inbetween | 通过帧 B | 右脚从后方经过身体下方 | 手臂开始交换 | 身体回中 | 准备接回第 0 帧 |

验收重点：第 5 帧必须能自然接回第 0 帧。

---

## run_right：6 帧

用途：快跑动作。

| 帧 | 帧类型 | 姿势目的 | 具体要求 |
|---|---|---|---|
| 0 | key | 右脚前落地 | 身体明显前倾，右脚在前，左脚在后 |
| 1 | inbetween | 压缩蓄力 | 重心最低，膝盖弯曲，手臂大幅摆动 |
| 2 | key | 后脚蹬地 | 左脚用力后蹬，身体向右前冲 |
| 3 | inbetween | 小腾空 | 双脚短暂离地或脚尖轻触地，头发衣摆拖后 |
| 4 | key | 左脚前落地 | 左脚在前，右脚在后，身体仍前倾 |
| 5 | inbetween | 压缩回环 | 重心下压，准备接回第 0 帧 |

验收重点：run 不能只是加大 walk 步幅，必须有前倾、压缩、腾空或冲刺感。

---

## attack_right：6 帧

用途：普通攻击。

| 帧 | 阶段 | 姿势目的 | 具体要求 |
|---|---|---|---|
| 0 | ready | 起始 | 接近 idle，可以衔接进入攻击 |
| 1 | anticipation | 预备 | 武器/手臂后拉，身体反向蓄力 |
| 2 | windup | 出手前 | 重心前压，攻击方向明确指向右侧 |
| 3 | hit | 命中帧 | 武器/手臂最大伸展，特效起点与命中点清晰 |
| 4 | follow_through | 收招 | 身体惯性前倾，攻击动作结束 |
| 5 | recover | 回位 | 回到可衔接 idle 的姿势 |

验收重点：命中帧必须明确，特效和伤害判定后续应对齐第 3 帧。

---

## cast_right：6 帧

用途：施法动作。

| 帧 | 阶段 | 姿势目的 | 具体要求 |
|---|---|---|---|
| 0 | ready | 起始 | 接近 idle |
| 1 | gather | 聚能 | 手部或武器向身体内侧收拢 |
| 2 | charge | 蓄能 | 身体稳定，施法手势明确，能量集中 |
| 3 | release | 释放 | 手臂/武器指向右侧，特效起点明确 |
| 4 | aftercast | 余势 | 衣摆/头发受释放方向影响 |
| 5 | recover | 回位 | 回到 idle 可衔接姿势 |

验收重点：释放帧必须与 projectile/cast VFX 的起点一致。

---

## hit_right：4 帧

用途：受击动作。

| 帧 | 阶段 | 姿势目的 | 具体要求 |
|---|---|---|---|
| 0 | normal | 起始 | 接近 idle |
| 1 | impact | 受击 | 身体向左后方收缩，头发/衣摆抖动 |
| 2 | recoil | 后仰 | 重心略后移，但脚底锚点不能漂移过大 |
| 3 | recover | 回位 | 回到 idle 可衔接姿势 |

验收重点：受击方向要清晰，但不能让角色位移出格。

---

## death_right：8 帧

用途：死亡动作。

| 帧 | 阶段 | 姿势目的 | 具体要求 |
|---|---|---|---|
| 0 | normal | 起始 | 接近 idle |
| 1 | hit | 致命受击 | 身体失衡 |
| 2 | collapse_start | 倒下开始 | 膝盖弯曲，重心下降 |
| 3 | collapse_mid | 倒下中段 | 身体向地面倾倒 |
| 4 | collapse_end | 接触地面 | 身体落地 |
| 5 | settle_1 | 余动 | 头发/衣摆惯性收束 |
| 6 | settle_2 | 静止前 | 小幅变化 |
| 7 | final | 最终静止 | 死亡定格 |

验收重点：死亡动作可以不循环，最终帧保持静止。

---

# AI 出图提示词模板

## 单动作行图模板

```text
Create a clean transparent-background 2D game sprite animation row for the same character shown in the anchor image.

Character consistency is mandatory:
- same face
- same hairstyle
- same outfit
- same body proportions
- same weapon and accessories
- same color palette

Animation:
- action: <ACTION_ID>
- direction: facing screen right
- frame count: <FRAME_COUNT>
- frame size: 256x256 each
- layout: one horizontal row, exactly <FRAME_COUNT> frames
- background: transparent
- no text, no labels, no grid lines, no watermark
- camera/view: <VIEW>

Per-frame pose plan:
<PASTE_ACTION_FRAME_PLAN_PER_FRAME_TABLE>

Important:
- Keep the feet anchor stable across all frames.
- Keep the character centered in each frame.
- Do not generate left-facing frames.
- Do not change the character design between frames.
```

## 中文需求转英文出图提示时的规则

- 动作帧表可以中文保留，但出图 prompt 中的动作约束建议同时提供英文。
- `right` 必须明确写成 `facing screen right`，不要只写 `right side`。
- 不要使用 `left` 字样，避免模型混淆方向。
- 不要要求一张图同时包含多行动作。
- 不要要求一张图同时包含多个方向。

---

# 工程处理流程

## Step 4：切帧

使用 `scripts/slice_sprite_row.py` 将单行动作图切成单帧 PNG。

要求：

- 输入图宽度必须等于 `frame_width * frame_count`。
- 输入图高度必须等于 `frame_height`。
- 如果尺寸不匹配，停止并报告，不得强行裁剪。
- 输出命名：`<character_id>_<action>_<direction>_<index:03d>.png`。

示例：

```bash
python scripts/slice_sprite_row.py \
  --input assets/raw/player_walk_right_row.png \
  --output assets/characters/player/frames \
  --character player \
  --action walk \
  --direction right \
  --frame-width 256 \
  --frame-height 256 \
  --frame-count 6
```

---

## Step 5：镜像 left

使用 `scripts/mirror_direction_frames.py` 从 `right` 生成 `left`。

示例：

```bash
python scripts/mirror_direction_frames.py \
  --input assets/characters/player/frames \
  --output assets/characters/player/frames \
  --from-direction right \
  --to-direction left
```

---

## Step 6：校验帧资源

使用 `scripts/validate_frames.py` 检查：

- 尺寸是否一致。
- 是否包含 alpha 通道。
- 是否存在空白帧。
- 命名是否符合规范。
- right/left 帧数是否一致。

示例：

```bash
python scripts/validate_frames.py \
  --input assets/characters/player/frames \
  --frame-width 256 \
  --frame-height 256 \
  --report assets/characters/player/player_sprite_validate_report.md
```

---

## Step 7：生成 manifest

使用 `scripts/build_sprite_manifest.py` 生成 JSON manifest。

示例：

```bash
python scripts/build_sprite_manifest.py \
  --input assets/characters/player/frames \
  --output assets/characters/player/player_sprites_manifest.json \
  --character player \
  --frame-width 256 \
  --frame-height 256
```

manifest 示例：

```json
{
  "character_id": "player",
  "frame_size": [256, 256],
  "animations": {
    "walk_right": {
      "loop": true,
      "fps": 10,
      "frames": [
        "frames/player_walk_right_000.png",
        "frames/player_walk_right_001.png"
      ]
    }
  }
}
```

---

## Step 8：拼接最终 sheet，可选

使用 `scripts/pack_sheet.py` 将单帧重新拼成标准 sheet。

推荐 sheet 排列：

```text
idle_right
idle_left
walk_right
walk_left
run_right
run_left
attack_right
attack_left
```

示例：

```bash
python scripts/pack_sheet.py \
  --input assets/characters/player/frames \
  --output assets/characters/player/player_sprite_sheet.png \
  --character player \
  --frame-width 256 \
  --frame-height 256
```

---

# 独立测试场景验收

如果项目已有独立 sprite test scene，应接入该场景。

测试场景必须支持：

- 选择角色。
- 选择动作。
- 选择方向。
- 播放 / 暂停。
- 单帧步进。
- 显示帧索引。
- 显示脚底锚点参考线。
- 显示角色包围盒。
- 显示当前 manifest 路径。
- 截图输出自测报告。

所有测试 UI 文案必须使用中文。

---

# 自测报告模板

完成后输出中文报告：

```md
# <角色ID> 序列帧自测报告

## 资源输入

- anchor：...
- raw row：...
- frame size：256x256
- 动作：idle / walk / run / attack

## 已生成资源

- right 单帧：...
- left 镜像帧：...
- sprite sheet：...
- manifest：...

## 动作验收

| 动作 | 方向 | 帧数 | 尺寸 | 锚点稳定 | 循环衔接 | 角色一致性 | 结论 |
|---|---|---:|---|---|---|---|---|
| idle | right | 4 | 256x256 | 通过/失败 | 通过/失败 | 通过/失败 | ... |

## 发现的问题

- ...

## 未处理范围

- 未修改战斗逻辑。
- 未修改技能逻辑。
- 未修改角色数值。
```

---

# 验收标准总表

## 格式验收

- 每帧必须是 `256x256`，除非用户指定其他尺寸。
- 每帧必须是 PNG。
- 每帧必须有 alpha 通道。
- 不允许出现文字、水印、格子线、边框。
- 单动作同方向帧数必须与 Action Frame Plan 一致。

## 动作验收

- idle：脚底不动，只做呼吸和轻微附属物摆动。
- walk：左右脚交替明确，第 5 帧能接回第 0 帧。
- run：有前倾、压缩、蹬地、腾空或冲刺感。
- attack：预备、出手、命中、收招、回位节奏明确。
- cast：聚能、释放、回位明确，释放帧可对齐 VFX 起点。
- hit：受击方向明确，但不漂移出格。
- death：非循环，最终帧静止。

## 一致性验收

- 脸、发型、服装、武器、身体比例不变。
- 同动作帧间不能随机变换角色细节。
- right 方向必须面向屏幕右侧。
- left 方向默认必须是 right 镜像。

---

# 常见失败与处理

## 失败：走路像原地抖动

原因：缺少脚步关键帧。

处理：重做 Action Frame Plan，强化第 0 / 3 帧的接触帧，明确左右脚交替。

## 失败：左右不分

原因：AI 同时生成了 left 和 right，或者 prompt 中出现方向歧义。

处理：只生成 `facing screen right`，left 用脚本镜像。

## 失败：角色每帧脸不一样

原因：缺少 anchor 或不变量约束。

处理：重新使用 anchor 图，并在 prompt 中强调 same face / same hairstyle / same outfit / same proportions。

## 失败：sheet 不能等分裁剪

原因：AI 生成了非标准间距或多余边框。

处理：不要强行裁剪；重做单行动作图，要求 exact frame size and one horizontal row。

## 失败：攻击没有命中帧

原因：Action Frame Plan 没有指定 hit frame。

处理：重做 attack plan，固定第 3 帧为 hit frame。

---

# 最小交付清单

完成一次角色动作生产时，至少交付：

- Action Frame Plan。
- 原始 AI 动作行图路径。
- 切分后的 right 单帧。
- 镜像生成的 left 单帧。
- manifest JSON。
- 中文自测报告。

如果接入了测试场景，还需交付：

- 测试场景入口。
- 测试截图路径。
- 测试结论。
