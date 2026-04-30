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

## Codex 执行模板

```text
使用 2d-character-animation-pipeline skill，为 <角色ID> 制作 <动作> 动作序列帧。

执行要求：
1. 先输出 Action Frame Plan，不允许直接生成或处理 sprite sheet。
2. 只处理 right 方向母版。
3. left 方向由 right 镜像生成。
4. 单帧尺寸为 256x256。
5. 动作帧数为 <帧数>。
6. 视角为 <视角>。
7. 输出单帧 PNG、manifest、中文自测报告。
8. 不修改战斗数值、技能逻辑、角色属性、敌人逻辑。
9. 所有给用户审阅的 Markdown 文档必须使用中文；OpenSpec 必需关键字可保留英文。
```
