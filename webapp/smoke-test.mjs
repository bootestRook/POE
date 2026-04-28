import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const app = readFileSync(join(root, "webapp", "App.tsx"), "utf8");
const css = readFileSync(join(root, "webapp", "styles.css"), "utf8");
const html = readFileSync(join(root, "index.html"), "utf8");
const state = JSON.parse(readFileSync(join(root, "webapp-state.json"), "utf8").replace(/^\uFEFF/, ""));
const localization = readFileSync(join(root, "configs", "localization", "zh_cn.toml"), "utf8");
const skillEditorAdapter = readFileSync(join(root, "src", "liufang", "skill_editor.py"), "utf8");
const webApi = readFileSync(join(root, "src", "liufang", "web_api.py"), "utf8");
const skillEditorRunner = readFileSync(join(root, "skillEditor_run.bat"), "utf8");
const workbenchFramePath = join(root, "webapp", "assets", "workbench-frame.png");
const unitAnimationRuntime = readFileSync(join(root, "webapp", "unitAnimation.ts"), "utf8");
const unitAssets = readFileSync(join(root, "webapp", "unitAssets.ts"), "utf8");
const unitAnimationManifest = JSON.parse(readFileSync(join(root, "assest", "battle", "units", "manifests", "unit-animations-manifest.json"), "utf8"));

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
  "scheduledSkillEvents",
  "createProjectileSkillEvents",
  "consumeSkillEvent",
  "projectile_spawn",
  "hit_vfx",
  "floating_text",
  "data-skill-event=\"projectile_spawn\"",
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

const unitAnimationCodeChecks = [
  "resolveUnitAnimation",
  "resolveDirection",
  "resolveAnimationPlaybackRate",
  "animationSpeedMultiplier",
  "getAnimationFrame",
  "fallbackAnimation",
  "baseMoveSpeed",
  "currentMoveSpeed",
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

function hasAnimation(unitId, stateName) {
  return unitAnimationManifest.assets.some((asset) => asset.unitId === unitId && asset.state === stateName);
}

const requiredUnitAnimations = [
  ["player_adventurer", "idle"],
  ["player_adventurer", "walk"],
  ["enemy_imp", "idle"],
  ["enemy_imp", "walk"],
  ["enemy_imp", "attack"],
  ["enemy_brute", "idle"],
  ["enemy_brute", "walk"],
  ["enemy_brute", "attack"]
];

for (const [unitId, stateName] of requiredUnitAnimations) {
  if (!hasAnimation(unitId, stateName)) {
    throw new Error(`缺少单位动画资源：${unitId}/${stateName}`);
  }
}

if (hasAnimation("player_adventurer", "attack")) {
  throw new Error("主角本轮不应包含 attack 动画。");
}

for (const direction of ["down", "right", "up", "left"]) {
  for (const unitId of ["player_adventurer", "enemy_imp", "enemy_brute"]) {
    if (!unitAnimationManifest.assets.some((asset) => asset.unitId === unitId && asset.direction === direction)) {
      throw new Error(`缺少 4 方向动画资源：${unitId}/${direction}`);
    }
  }
}

for (const direction of ["down_right", "up_right", "up_left", "down_left"]) {
  if (!unitAnimationManifest.directions.includes(direction)) {
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
  "火焰弹",
  "技能文件路径",
  "行为模板",
  "结构校验通过",
  "未迁移 / 不可编辑",
  "不可打开",
  "基础信息模块",
  "释放参数模块",
  "投射物子弹模块",
  "伤害点模块",
  "表现模块",
  "预览字段模块",
  "id（只读）",
  "保存技能包",
  "保存成功",
  "/api/skill-editor/save",
  "requestSkillEditorSave",
  "initialSkillEditorOpen",
  "initialSkillEditorMode",
  "/skill-editor",
  "params.get(\"skill_editor\")",
  "SkillPackageData",
  "版本",
  "冷却毫秒",
  "投射物速度",
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
  "rotateDirection",
  "selectProjectileTargets",
  "ProjectileDamageTarget",
  "projectileIndex",
  ".p${projectileIndex + 1}.damage",
  "maxHitsPerProjectile",
  "collisionRadius * 3",
  "projectileLineMetrics",
  "pierce_count"
];

for (const text of skillEditorChecks) {
  if (!app.includes(text) && !skillEditorAdapter.includes(text) && !webApi.includes(text) && !localization.includes(text) && !skillEditorRunner.includes(text)) {
    throw new Error(`缺少技能编辑器 V0 中文界面或只读数据展示：${text}`);
  }
}

const forbiddenSkillEditorText = [
  ">Save<",
  ">Edit<",
  "SkillEditor V0",
  ">保存<",
  "Modifier 测试栈",
  "测试场景",
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
