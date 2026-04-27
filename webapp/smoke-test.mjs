import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const app = readFileSync(join(root, "webapp", "App.tsx"), "utf8");
const css = readFileSync(join(root, "webapp", "styles.css"), "utf8");
const html = readFileSync(join(root, "index.html"), "utf8");
const workbenchFramePath = join(root, "webapp", "assets", "workbench-frame.png");

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
  "hover-linked",
  "hover-dim",
  "right-workbench",
  "bag-empty-cell",
  "repeat(12, var(--slot-size))",
  "--slot-size: 60px",
  "workbench-frame.png"
];

for (const text of requiredCode) {
  if (!app.includes(text) && !css.includes(text)) {
    throw new Error(`缺少 WebApp 交互或样式能力：${text}`);
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
  ">Select<"
];

for (const text of obviousEnglishButtonText) {
  if (app.includes(text)) {
    throw new Error(`发现明显英文玩家可见按钮文本：${text}`);
  }
}

if (!existsSync(join(root, "dist", "index.html"))) {
  throw new Error("缺少构建产物 dist/index.html，请先运行 npm run build。");
}

console.log("WebApp smoke 测试通过。");
