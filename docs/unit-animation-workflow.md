# 单位动画资源接入工作流

本文档用于后续接入新的 2.5D / dimetric 战斗单位动画。当前第一版只覆盖表现层、资源管线和前端动画状态机，不改变战斗数值、技能、宝石、掉落或后端逻辑。

## 命名规范

单位动画资源使用：

```text
{unit_asset_id}_{state}_{direction}.png
```

示例：

```text
player_whitehair_girl_walk_down.png
enemy_imp_attack_right.png
enemy_brute_idle_up.png
```

`unitId` 使用运行时单位类型：

```text
player_adventurer
enemy_imp
enemy_brute
```

`state` 当前支持：

```text
idle
walk
attack
```

主角第一版只允许 `idle / walk`，不要添加主角 `attack`。

## 目录规范

原始图放置：

```text
assets/battle/units/raw
```

裁剪后的 spritesheet 放置：

```text
assets/battle/units/cropped
```

清单与 QA 图放置：

```text
assets/battle/units/manifests
```

不要重命名 `assets/` 目录。

## 裁剪 / 去背景 / 缩放流程

1. 将原始单位图或生成 sheet 放入 `assets/battle/units/raw`。
2. 确认背景为可去除的纯色或透明底。
3. 运行资源脚本：

```powershell
python scripts\build-unit-animation-sheets.py
```

4. 脚本输出横向 spritesheet，每张图包含同一单位、同一状态、同一方向的连续帧。
5. 检查：

```text
assets/battle/units/manifests/unit-animations-contact-sheet.png
```

重点看脚底锚点是否稳定、帧之间是否跳位、白边是否明显。

## Manifest 字段

`assets/battle/units/manifests/unit-animations-manifest.json` 中每个动画条目必须包含：

```text
unitId
state
direction
frameCount
fps
loop
durationMs
frameWidth
frameHeight
anchorX
anchorY
scale
fallbackState
fallbackDirection
playbackRate
```

`frameWidth / frameHeight` 是单帧尺寸，不是整张 spritesheet 尺寸。`anchorX / anchorY` 是脚底锚点比例。

## 状态定义

`idle`：单位静止待机，循环播放。

`walk`：单位移动时播放，循环播放。主角移动速度变化时，播放倍率通过 `animationSpeedMultiplier` / `resolveAnimationPlaybackRate` 调整。

`attack`：怪物攻击表现，非循环播放。攻击动画未播完前，不被 `walk / idle` 覆盖。

## 方向命名

代码预留 8 方向：

```text
down
down_right
right
up_right
up
up_left
left
down_left
```

第一版实际资源实现 4 方向：

```text
down
right
up
left
```

缺失方向必须走 `fallbackAnimation`，不要在渲染分支中临时判断。

## 锚点检查方法

1. 打开 `unit-animations-contact-sheet.png`。
2. 竖线应穿过单位脚底中心。
3. 横线应贴近脚底接地点。
4. walk 每一帧脚底不能明显上下漂移。
5. attack 可以有前冲，但最终锚点仍应回到脚底。

## 帧率和播放倍率

默认建议：

```text
idle: 3-4 fps
walk: 7-8 fps
attack: 9-10 fps
```

移动速度倍率接口：

```text
animationSpeedMultiplier = clamp(currentMoveSpeed / baseMoveSpeed, min, max)
```

当前实现位于：

```text
webapp/unitAnimation.ts
```

不要把 walk fps 写死在 React 渲染分支里。

## 新增一个单位动画的标准步骤

1. 准备单位 idle 原图或完整动画原始 sheet。
2. 放入 `assets/battle/units/raw`。
3. 在 `scripts/build-unit-animation-sheets.py` 中添加单位配置。
4. 生成 spritesheet 和 manifest。
5. 在 `webapp/unitAssets.ts` 中确保 `unitId` 能被运行时解析。
6. 在 `webapp/unitAnimation.ts` 中确认状态 fallback 正常。
7. 运行构建和 smoke。

## 测试 / 构建命令

```powershell
npm.cmd run build
npm.cmd test
python -m unittest discover tests
openspec.cmd validate --all --strict
```

## 常见问题

白边：背景去除阈值太保守，或原图边缘有绿色溢色。先检查 alpha，再做 despill。

裁剪跳位：每帧独立裁剪会导致画面抖动。spritesheet 应统一 `frameWidth / frameHeight` 和脚底锚点。

脚底漂移：`anchorY` 不稳定或生成帧时垂直 bob 过大。优先修锚点，再调整动画。

方向缺失：manifest 可只实现 4 方向，但 `directions` 必须保留 8 方向命名，运行时统一 fallback。

walk 像滑行：提高 walk 帧数或增加脚步横向摆动；同时检查 `animationSpeedMultiplier` 是否随移动速度变化。

attack 被 idle 打断：攻击状态必须记录 `attackStartedAtMs / attackUntilMs`，并在 `resolveUnitAnimation` 中优先于 walk / idle。
