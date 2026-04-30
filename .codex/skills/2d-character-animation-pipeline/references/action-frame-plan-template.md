# Action Frame Plan 模板

```md
# Action Frame Plan：<action_id>

## 基础信息

- action_id：<action>_<direction>
- character_id：<角色ID>
- direction：right
- frame_count：<帧数>
- frame_size：256x256
- loop_type：loop / once
- view：2.5D / dimetric / top-down / side-view
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
| 0 | key |  |  |  |  |  |  |  |  |  |
| 1 | inbetween |  |  |  |  |  |  |  |  |  |

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
