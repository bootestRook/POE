import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

const root = process.cwd();
const app = readFileSync(join(root, "webapp", "App.tsx"), "utf8");
const css = readFileSync(join(root, "webapp", "styles.css"), "utf8");
const html = readFileSync(join(root, "index.html"), "utf8");
const state = loadCurrentState();
const localization = readFileSync(join(root, "configs", "localization", "zh_cn.toml"), "utf8");
const skillEditorAdapter = readFileSync(join(root, "src", "liufang", "skill_editor.py"), "utf8");
const webApi = readFileSync(join(root, "src", "liufang", "web_api.py"), "utf8");
const skillEditorRunner = readFileSync(join(root, "skillEditor_run.bat"), "utf8");
const workbenchFramePath = join(root, "webapp", "assets", "workbench-frame.png");
const unitAnimationRuntime = readFileSync(join(root, "webapp", "unitAnimation.ts"), "utf8");
const unitAssets = readFileSync(join(root, "webapp", "unitAssets.ts"), "utf8");
const unitAnimationManifest = JSON.parse(readFileSync(join(root, "assest", "battle", "units", "manifests", "unit-animations-manifest.json"), "utf8"));

function loadCurrentState() {
  const script = [
    "import json, sys",
    "from pathlib import Path",
    "sys.path.insert(0, str(Path('src').resolve()))",
    "from liufang.web_api import V1WebAppApi",
    "print(json.dumps(V1WebAppApi(Path('configs')).state(), ensure_ascii=False))"
  ].join("\n");
  return JSON.parse(execFileSync("python", ["-c", script], { cwd: root, encoding: "utf8" }).replace(/^\uFEFF/, ""));
}

const requiredText = [
  "数独宝石流放like V1",
  "开始游戏",
  "拖拽：放置宝石",
  "C：打开/关闭背包"
];

for (const text of requiredText) {
  if (!app.includes(text) && !html.includes(text)) {
    throw new Error(`缺少中文页面文本：${text}`);
  }
}

const requiredCode = [
  "draggable",
  "onDropGem",
  "GemTooltip",
  "FireBoltView",
  "SkillEvent",
  "skill-editor-workspace",
  "skill-editor-left-pane",
  "skill-editor-middle-pane",
  "skill-editor-right-pane",
  "skill-editor-bottom-bar",
  "skill-editor-projectile-panel",
  "showLaunchPoints",
  "showTargetPoint",
  "showDirectionLines",
  "showCollisionRadius",
  "showSearchRange",
  "validateDraftBeforeSave",
  "scheduledSkillEvents",
  "createProjectileSkillEvents",
  "consumeSkillEvent",
  "createMeleeArcSkillEvents",
  "createDamageZoneSkillEvents",
  "projectile_spawn",
  "melee_arc",
  "damage_zone",
  "hit_vfx",
  "floating_text",
  "data-skill-event=\"projectile_spawn\"",
  "data-skill-event=\"melee_arc\"",
  "data-skill-event=\"damage_zone\"",
  "hover-linked",
  "hover-dim",
  "right-workbench",
  "bag-empty-cell",
  "repeat(12, var(--slot-size))",
  "--slot-size: 60px",
  "workbench-frame.png",
  "state.board.cells.flat().map",
  "boardBoxBoundaryClasses",
  "data-box-boundary",
  "box-border-top",
  "box-border-right",
  "box-border-bottom",
  "box-border-left",
  ".board-cell::after",
  "--board-legal-shadow",
  "selectedGemInstanceId",
  "previewCell",
  "legalPlacementCells",
  "previewAffectedCells",
  "previewAffectedGems",
  "previewRelations",
  "previewInvalidReason",
  "usePlacementPreview",
  "usePlacementInvalidReason",
  "sudokuDigitKey",
  "isAllowedRoute",
  "isPassiveGem",
  "preview-target-cell",
  "preview-dot-cell",
  "data-preview-skill-refresh",
  "invalid-drop-cell"
];

for (const text of requiredCode) {
  if (!app.includes(text) && !css.includes(text)) {
    throw new Error(`缺少 WebApp 交互或样式能力：${text}`);
  }
}

const projectileVfxLifetimeChecks = [
  "PROJECTILE_BODY_EXIT_FADE_DURATION",
  "fireBoltAliveRemaining",
  "projectileBodyOpacity",
  "event.payload?.expire_world_position ?? event.payload?.end_position",
  "ttl: aliveDuration + PROJECTILE_BODY_EXIT_FADE_DURATION",
  "const opacity = projectileBodyOpacity(bolt)",
  "vfxFrameIndexInRow(sheets.projectile, sheets.projectileFrameRow, aliveRemaining, duration)",
  "data-projectile-alive-remaining",
  "data-projectile-fade-duration"
];

for (const text of projectileVfxLifetimeChecks) {
  if (!app.includes(text)) {
    throw new Error(`缂哄皯鎶曞皠鐗╃敓瀛樻湡/娣″嚭鍒嗙妫€鏌ワ細${text}`);
  }
}

const fireBoltViewSource = app.slice(app.indexOf("function FireBoltView"), app.indexOf("function LegacyFireBoltView"));
if (fireBoltViewSource.includes("const opacity = Math.max(0, bolt.ttl / duration);")) {
  throw new Error("鎶曞皠鐗╂湰浣撻€忔槑搴︿笉鑳藉啀缁戝畾鍒版暣娈甸琛?ttl/duration銆?");
}

const unitAnimationCodeChecks = [
  "resolveUnitAnimation",
  "resolveDirection",
  "resolveAnimationPlaybackRate",
  "animationSpeedMultiplier",
  "getAnimationFrame",
  "fallbackAnimation",
  "baseMoveSpeed",
  "currentMoveSpeed",
  "unitMovementState",
  "UNIT_RUN_SPEED_RATIO",
  "data-animation-state",
  "data-animation-direction",
  "data-animation-playback-rate",
  "unit-animations-manifest.json"
];

for (const text of unitAnimationCodeChecks) {
  if (!app.includes(text) && !unitAnimationRuntime.includes(text) && !unitAssets.includes(text)) {
    throw new Error(`缺少单位动画运行时或接入点：${text}`);
  }
}

const spriteTestChecks = [
  "initialSpriteTestMode",
  "/sprite-test",
  "mode\") === \"sprite-test\"",
  "SpriteTestScene",
  "data-mode=\"sprite-test\"",
  "Sprites 动作测试场景",
  "待机测试区",
  "行走测试区",
  "奔跑测试区",
  "run",
  "缺少动作：",
  "缺少方向：",
  "缺少帧配置：",
  "碰撞框显示",
  "挂点显示",
  "网格显示",
  "截图模式",
  "返回正式入口",
  "SPRITE_TEST_PATHS",
  "UNIT_ANIMATION_ASSETS"
];

for (const text of spriteTestChecks) {
  if (!app.includes(text)) {
    throw new Error(`缺少 Sprites 动作测试场入口或中文界面：${text}`);
  }
}

function hasAnimation(unitId, stateName) {
  return unitAnimationManifest.assets.some((asset) => asset.unitId === unitId && asset.state === stateName);
}

const requiredUnitAnimations = [
  ["player_adventurer", "idle"],
  ["player_adventurer", "walk"],
  ["player_adventurer", "run"]
];

for (const [unitId, stateName] of requiredUnitAnimations) {
  if (!hasAnimation(unitId, stateName)) {
    throw new Error(`缺少单位动画资源：${unitId}/${stateName}`);
  }
}

if (hasAnimation("player_adventurer", "attack")) {
  throw new Error("主角本轮不应包含 attack 动画。");
}

for (const direction of ["left", "right"]) {
  if (!unitAnimationManifest.assets.some((asset) => asset.unitId === "player_adventurer" && asset.direction === direction)) {
    throw new Error(`缺少角色方向动画资源：player_adventurer/${direction}`);
  }
}

for (const action of ["idle", "walk", "run"]) {
  for (const direction of ["left", "right"]) {
    const asset = unitAnimationManifest.assets.find((item) => item.unitId === "player_adventurer" && item.state === action && item.direction === direction);
    if (!asset) throw new Error(`缺少规范角色动作资源：player_adventurer/${action}/${direction}`);
    if (asset.frameCount !== 6) throw new Error(`角色动作帧数错误：${action}/${direction}`);
    if (!String(asset.path).includes(`player_adventurer_${action}_${direction}.png`)) {
      throw new Error(`角色动作 sheet 命名不规范：${asset.path}`);
    }
    if (!String(asset.framesPath ?? "").includes(`/frames/player_adventurer/${action}/${direction}`)) {
      throw new Error(`角色动作序列帧目录不规范：${asset.framesPath}`);
    }
  }
}

for (const direction of ["left", "right"]) {
  if (!unitAnimationManifest.implementedDirections.includes(direction)) {
    throw new Error(`缺少 8 方向预留命名：${direction}`);
  }
}

for (const field of ["unitId", "state", "direction", "frameCount", "fps", "loop", "durationMs", "frameWidth", "frameHeight", "anchorX", "anchorY", "scale", "fallbackDirection", "playbackRate"]) {
  if (!unitAnimationManifest.assets.every((asset) => Object.prototype.hasOwnProperty.call(asset, field))) {
    throw new Error(`单位动画 manifest 缺少字段：${field}`);
  }
}

const skillEditorChecks = [
  "SkillEditorPanel",
  "skill_editor",
  "技能编辑器",
  "技能文件列表",
  "仅编辑已迁移技能包允许的字段",
  "active_fire_bolt",
  "active_ice_shards",
  "active_penetrating_shot",
  "active_frost_nova",
  "active_puncture",
  "player_nova",
  "melee_arc",
  "damage_zone",
  "area_spawn",
  "近战扇形模块",
  "melee-arc-vfx",
  "createMeleeArcSkillEvents",
  "selectMeleeArcTargets",
  "player-nova-vfx",
  "createPlayerNovaSkillEvents",
  "selectPlayerNovaTargets",
  "selectDamageZoneTargets",
  "penetrating_shot",
  "PENETRATING_SHOT_VFX",
  "PENETRATING_SHOT_ART_FACING_OFFSET_DEG",
  "penetrating_shot-muzzle-vfx",
  "fan_projectile",
  "火焰弹",
  "冰棱散射",
  "技能配置来源",
  "行为模板",
  "结构校验通过",
  "未迁移 / 不可编辑",
  "不可打开",
  "基础信息模块",
  "释放参数模块",
  "投射物模块",
  "伤害点模块",
  "表现模块",
  "预览字段模块",
  "技能编号（只读）",
  "保存技能包",
  "保存成功",
  "/api/skill-editor/save",
  "requestSkillEditorSave",
  "openSkillEditorPanel",
  "initialSkillEditorOpen",
  "initialSkillEditorMode",
  "/skill-editor",
  "params.get(\"skill_editor\")",
  "SkillPackageData",
  "版本",
  "冷却毫秒",
  "投射物速度",
  "扇形投射物模块",
  "扇形角度",
  "角度步长",
  "生成模式",
  "单枚伤害倍率",
  "只读飞行时间摘要",
  "连发间隔毫秒",
  "散射角度",
  "基础伤害",
  "预览字段",
  "SkillRuntimeGuideLayer",
  "编辑器运行辅助线",
  "runtime-skill-guides",
  "runtime-skill-search-ring",
  "runtime-skill-collision-ring",
  "runtime-skill-trajectory-line",
  "projectileLaneOffsets",
  "projectileSpreadDirections",
  "projectileSpreadAngleDeg",
  "projectileAngleStepDeg",
  "isProjectileSkillTemplate",
  "rotateDirection",
  "selectProjectileTargets",
  "ProjectileDamageTarget",
  "projectileIndex",
  "data-projectile-index",
  "data-current-world-x",
  "data-velocity-world-x",
  "data-local-spread-angle",
  "data-pierce-remaining",
  "data-projectile-speed",
  "data-impact-kind",
  ".p${projectileIndex + 1}.damage",
  "maxHitsPerProjectile",
  "collisionRadius * 3",
  "projectileLineMetrics",
  "pierce_count",
  "测试词缀栈",
  "可测试辅助效果",
  "已选择效果",
  "清空测试栈",
  "应用测试栈",
  "仅用于测试，不会写入技能文件",
  "关系模拟",
  "相邻",
  "同行",
  "同列",
  "同宫",
  "来源强度",
  "目标强度",
  "导管强度",
  "临时最终技能实例预览",
  "原始最终伤害",
  "测试后最终伤害",
  "未生效词缀列表",
  "/api/skill-editor/modifier-preview",
  "requestSkillEditorModifierPreview",
  "技能测试场",
  "单体木桩",
  "三目标横排",
  "纵向队列",
  "密集小怪",
  "运行测试",
  "暂停",
  "单步",
  "重置",
  "启用测试词缀栈",
  "本次事件原始摘要",
  "飞行期间未扣血：通过",
  "/api/skill-editor/test-arena/run",
  "requestSkillTestArenaRun",
  "技能事件时间线",
  "支持识别的事件类型",
  "释放开始",
  "投射物命中",
  "冷却更新",
  "事件时间",
  "存在多枚投射物",
  "扇形方向可见",
  "延迟",
  "持续时间",
  "来源实体",
  "目标实体",
  "伤害类型",
  "特效标识",
  "原因标识",
  "附加数据",
  "基础时序检查",
  "event_timeline",
  "timeline_checks",
  "payload_text"
];

for (const text of skillEditorChecks) {
  if (!app.includes(text) && !skillEditorAdapter.includes(text) && !webApi.includes(text) && !localization.includes(text) && !skillEditorRunner.includes(text)) {
    throw new Error(`缺少技能编辑器 V0 中文界面或只读数据展示：${text}`);
  }
}

const penetratingShotEditorEntry = state.skill_editor.entries.find((entry) => entry.id === "active_penetrating_shot");
if (!penetratingShotEditorEntry?.openable || !penetratingShotEditorEntry?.editable || !penetratingShotEditorEntry?.package_data) {
  throw new Error("active_penetrating_shot must be openable and editable in SkillEditor state.");
}

const forbiddenSkillEditorText = [
  ">Save<",
  ">Edit<",
  "SkillEditor V0",
  "测试 Modifier 栈",
  "启用测试 Modifier 栈",
  "SkillEvent 时间线",
  "modifier 列表",
  "特效 Key",
  "原因 Key",
  "skill.yaml",
  ">保存<",
  "自测报告",
  "编辑器专用预览场景",
  "固定木桩预览",
  "skill-editor-preview-stage"
];

for (const text of forbiddenSkillEditorText) {
  if (app.includes(text)) {
    throw new Error(`技能编辑器 V0 不应出现本轮禁止的界面文案或英文按钮：${text}`);
  }
}

const removedButtons = ["上盘", "下盘"];
for (const text of removedButtons) {
  if (app.includes(`<button`) && app.includes(`>${text}<`)) {
    throw new Error(`仍存在不需要的按钮：${text}`);
  }
}

const removedPanels = ["gear-rail", "skill-preview-panel", "装备栏", "技能预览"];
for (const text of removedPanels) {
  if (app.includes(text)) {
    throw new Error(`仍存在已要求移除的 UI：${text}`);
  }
}

const removedWorkbenchText = ["宝石库存", "数独宝石盘", "盘面合法"];
for (const text of removedWorkbenchText) {
  if (app.includes(text)) {
    throw new Error(`右侧工作台仍存在需要去掉的文字：${text}`);
  }
}

const removedHudText = ["skill-strip", "skill-card", "counter"];
for (const text of removedHudText) {
  if (app.includes(text) || css.includes(text)) {
    throw new Error(`仍存在已要求移除的底部战斗条 UI：${text}`);
  }
}

if (!existsSync(workbenchFramePath)) {
  throw new Error("缺少生图底框资产 webapp/assets/workbench-frame.png。");
}

const obviousEnglishButtonText = [
  ">Start<",
  ">Fight<",
  ">Pick up<",
  ">Mount<",
  ">Unmount<",
  ">Select<",
  "LMB：拾取"
];

for (const text of obviousEnglishButtonText) {
  if (app.includes(text)) {
    throw new Error(`发现明显英文玩家可见按钮文本：${text}`);
  }
}

const boundaryChecks = [
  "row === 0 || row === 3 || row === 6",
  "row === 2 || row === 5 || row === 8",
  "column === 0 || column === 3 || column === 6",
  "column === 2 || column === 5 || column === 8"
];

for (const text of boundaryChecks) {
  if (!app.includes(text)) {
    throw new Error(`缺少 3x3 九宫格边界计算：${text}`);
  }
}

if (state.board.cells.flat().length !== 81) {
  throw new Error("WebApp 宝石盘必须渲染 81 个格子。");
}

const previewText = ["可放置", "不可放置", "预览落点", "影响同行", "影响同列", "影响同宫", "影响相邻", "放下后预计影响", "无可影响目标"];
for (const text of previewText) {
  if (!app.includes(text)) {
    throw new Error(`缺少待放置预览中文文案：${text}`);
  }
}

const phase2Text = ["被动技能宝石", "同数独数字宝石不能位于同一行、列或宫格", "左键：拾取"];
for (const text of phase2Text) {
  if (!app.includes(text) && !JSON.stringify(state).includes(text) && !localization.includes(text)) {
    throw new Error(`缺少三类宝石中文文案：${text}`);
  }
}

const damageRichTextChecks = [
  "\"火焰\": \"damage-fire\"",
  "\"冰霜\": \"damage-cold\"",
  "\"闪电\": \"damage-lightning\"",
  "\"物理\": \"damage-physical\"",
  "\"混沌\": \"damage-chaos\"",
  ".tooltip-tone-damage-physical",
  "tooltip-stat-rich-value"
];
for (const text of damageRichTextChecks) {
  if (!app.includes(text) && !css.includes(text)) {
    throw new Error(`缺少伤害类型富文本高亮能力：${text}`);
  }
}
if (/\.tooltip-tone-damage-physical\s*{[^}]*color:\s*#d0d0d0/i.test(css)) {
  throw new Error("物理伤害高亮色不能接近普通正文灰色。");
}

for (const item of state.inventory) {
  if (typeof item.description_text === "string" && /适合验证|标签/.test(item.description_text)) {
    throw new Error(`宝石描述仍包含开发用语：${item.name_text} / ${item.description_text}`);
  }
}

const randomAffixRenderChecks = [
  "sections.random_affixes",
  "tooltip-affix-line"
];
for (const text of randomAffixRenderChecks) {
  if (app.includes(text)) {
    throw new Error(`随机词缀 UI 不应回归：${text}`);
  }
}

const previewDataChecks = [
  "legalPlacementCells.has(hoveredBoardCell)",
  "previewRelationTypes(targetCell, cell)",
  "previewAffectedCells.set",
  "previewAffectedGems.set",
  "return \"preview-dot-cell\";",
  "data-preview-invalid-reason",
  "data-preview-relations"
];

for (const text of previewDataChecks) {
  if (!app.includes(text)) {
    throw new Error(`缺少待放置预览数据：${text}`);
  }
}

if (/\.legal-drop-cell\s*{[^}]*border:/s.test(css) || /\.board-slot-hover\s*{[^}]*border:/s.test(css)) {
  throw new Error("合法/悬浮高亮不应直接设置宝石盘格子外边框。");
}

if (!/\.board-cell::after\s*{[^}]*z-index:\s*8;/s.test(css)) {
  throw new Error("3x3 九宫格分区线必须使用高优先级 overlay。");
}

if (!/\.legal-drop-cell\s*{[^}]*inset 0 0 0 1px/s.test(css)) {
  throw new Error("合法格高亮必须保持为细内描边，不能压过九宫格分区线。");
}

if (!existsSync(join(root, "dist", "index.html"))) {
  throw new Error("缺少构建产物 dist/index.html，请先运行 npm run build。");
}

console.log("WebApp smoke 测试通过。");
