import type { BakedMapAssetDefinition } from "./bakedMapAssets";

export type BakedMapMeta = {
  id: string;
  biome: string;
  display_name: string;
  background: string;
  walkable_mask: string;
  blocker_mask: string;
  spawn_mask: string;
  pixel_width: number;
  pixel_height: number;
  world_width: number;
  world_height: number;
  grid_size: number;
  player_spawn_policy: string;
  enemy_spawn_policy: string;
  elite_spawn_policy: string;
  boss_spawn_policy: string;
  exit_policy: string;
  collision_source: string;
  navigation_source: string;
};

export type MapPoint = {
  x: number;
  y: number;
  gridX: number;
  gridY: number;
};

export type BakedBattleMapData = {
  id: string;
  displayName: string;
  backgroundUrl: string;
  meta: BakedMapMeta;
  gridWidth: number;
  gridHeight: number;
  walkableGrid: boolean[][];
  blockerGrid: boolean[][];
  walkablePoints: MapPoint[];
  playerSpawn: MapPoint;
  enemySpawnPoints: MapPoint[];
  eliteSpawnPoints: MapPoint[];
  bossPoints: MapPoint[];
  exitPoints: MapPoint[];
  interactionPoints: MapPoint[];
  debugWarnings: string[];
};

type LoadedImageData = {
  image: HTMLImageElement;
  data: ImageData;
};

type ColorKey = "blue" | "green" | "yellow" | "magenta" | "cyan" | "orange";

const SPAWN_COLORS: Record<ColorKey, { r: number; g: number; b: number; label: string }> = {
  blue: { r: 0, g: 0, b: 255, label: "玩家出生点" },
  green: { r: 0, g: 255, b: 0, label: "普通怪刷新区" },
  yellow: { r: 255, g: 255, b: 0, label: "精英怪刷新区" },
  magenta: { r: 255, g: 0, b: 255, label: "Boss 区域" },
  cyan: { r: 0, g: 255, b: 255, label: "出口" },
  orange: { r: 255, g: 153, b: 0, label: "交互点" }
};

export async function loadBakedBattleMap(asset: BakedMapAssetDefinition): Promise<BakedBattleMapData> {
  const [background, walkableMask, blockerMask, spawnMask] = await Promise.all([
    loadImageData(asset.backgroundUrl),
    loadImageData(asset.walkableMaskUrl),
    loadImageData(asset.blockerMaskUrl),
    loadImageData(asset.spawnMaskUrl)
  ]);

  validateImageSizes(asset.meta, background, walkableMask, blockerMask, spawnMask);

  const gridSize = asset.meta.grid_size;
  if (!Number.isFinite(gridSize) || gridSize <= 0) {
    throw new Error("地图校验失败：grid_size 必须是大于 0 的数字。");
  }

  const gridWidth = Math.ceil(asset.meta.pixel_width / gridSize);
  const gridHeight = Math.ceil(asset.meta.pixel_height / gridSize);
  const blockerGrid = createBooleanGrid(gridWidth, gridHeight, false);
  const walkableGrid = createBooleanGrid(gridWidth, gridHeight, false);
  const debugWarnings: string[] = [];

  for (let gridY = 0; gridY < gridHeight; gridY += 1) {
    for (let gridX = 0; gridX < gridWidth; gridX += 1) {
      const pixel = gridCenterPixel(asset.meta, gridX, gridY);
      const blocker = isExactColor(blockerMask.data, pixel.x, pixel.y, 255, 0, 0);
      const walkable = isExactColor(walkableMask.data, pixel.x, pixel.y, 255, 255, 255) && !blocker;
      blockerGrid[gridY][gridX] = blocker;
      walkableGrid[gridY][gridX] = walkable;
    }
  }

  const walkablePoints = collectWalkablePoints(asset.meta, walkableGrid);
  if (walkablePoints.length === 0) {
    throw new Error("地图校验失败：至少需要一个可行走区域。");
  }

  const playerColorPixels = collectColorPixels(spawnMask.data, SPAWN_COLORS.blue);
  const rawPlayerSpawn = playerColorPixels.length > 0
    ? centroidPoint(asset.meta, playerColorPixels)
    : mapCenterPoint(asset.meta);
  if (playerColorPixels.length === 0) {
    debugWarnings.push("地图遮罩警告：未找到蓝色玩家出生区域，已使用地图中心附近最近的可行走格。");
  }
  const playerSpawn = ensureWalkablePoint(asset.meta, rawPlayerSpawn, walkableGrid, debugWarnings, "玩家出生点");

  const enemySpawnPoints = collectSpawnCells(asset.meta, spawnMask.data, SPAWN_COLORS.green, walkableGrid, debugWarnings);
  const eliteSpawnPoints = collectSpawnCells(asset.meta, spawnMask.data, SPAWN_COLORS.yellow, walkableGrid, debugWarnings);
  const bossPoints = collectCentroidPoint(asset.meta, spawnMask.data, SPAWN_COLORS.magenta, walkableGrid, debugWarnings);
  const exitPoints = collectCentroidPoint(asset.meta, spawnMask.data, SPAWN_COLORS.cyan, walkableGrid, debugWarnings);
  const interactionPoints = collectCentroidPoint(asset.meta, spawnMask.data, SPAWN_COLORS.orange, walkableGrid, debugWarnings);

  for (const warning of debugWarnings) console.warn(warning);

  return {
    id: asset.id,
    displayName: asset.meta.display_name,
    backgroundUrl: asset.backgroundUrl,
    meta: asset.meta,
    gridWidth,
    gridHeight,
    walkableGrid,
    blockerGrid,
    walkablePoints,
    playerSpawn,
    enemySpawnPoints,
    eliteSpawnPoints,
    bossPoints,
    exitPoints,
    interactionPoints,
    debugWarnings
  };
}

export function isMapPointWalkable(map: BakedBattleMapData, x: number, y: number) {
  const gridX = Math.floor(x / map.meta.grid_size);
  const gridY = Math.floor(y / map.meta.grid_size);
  return Boolean(map.walkableGrid[gridY]?.[gridX]);
}

export function clampToMapBounds(map: BakedBattleMapData, point: { x: number; y: number }, padding = 24) {
  return {
    x: clamp(point.x, padding, map.meta.world_width - padding),
    y: clamp(point.y, padding, map.meta.world_height - padding)
  };
}

export function resolveWalkableMove(map: BakedBattleMapData | null, current: { x: number; y: number }, next: { x: number; y: number }) {
  if (!map) return next;
  const clamped = clampToMapBounds(map, next);
  if (isMapPointWalkable(map, clamped.x, clamped.y)) return clamped;

  const xOnly = clampToMapBounds(map, { x: clamped.x, y: current.y });
  if (isMapPointWalkable(map, xOnly.x, xOnly.y)) return xOnly;

  const yOnly = clampToMapBounds(map, { x: current.x, y: clamped.y });
  if (isMapPointWalkable(map, yOnly.x, yOnly.y)) return yOnly;

  return current;
}

function loadImageData(src: string): Promise<LoadedImageData> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      const context = canvas.getContext("2d", { willReadFrequently: true });
      if (!context) {
        reject(new Error("地图校验失败：浏览器无法读取地图遮罩像素。"));
        return;
      }
      context.drawImage(image, 0, 0);
      resolve({ image, data: context.getImageData(0, 0, canvas.width, canvas.height) });
    };
    image.onerror = () => reject(new Error(`地图资源加载失败：无法加载图片 ${src}。`));
    image.src = src;
  });
}

function validateImageSizes(meta: BakedMapMeta, background: LoadedImageData, walkableMask: LoadedImageData, blockerMask: LoadedImageData, spawnMask: LoadedImageData) {
  const images = [
    { name: "background.png", image: background.image },
    { name: "walkable_mask.png", image: walkableMask.image },
    { name: "blocker_mask.png", image: blockerMask.image },
    { name: "spawn_mask.png", image: spawnMask.image }
  ];
  for (const item of images) {
    if (item.image.naturalWidth !== meta.pixel_width || item.image.naturalHeight !== meta.pixel_height) {
      throw new Error(`地图校验失败：${item.name} 尺寸必须与 map_meta.json 的 pixel_width / pixel_height 一致。`);
    }
  }
}

function createBooleanGrid(width: number, height: number, value: boolean) {
  return Array.from({ length: height }, () => Array.from({ length: width }, () => value));
}

function gridCenterPixel(meta: BakedMapMeta, gridX: number, gridY: number) {
  return {
    x: clamp(Math.floor(gridX * meta.grid_size + meta.grid_size / 2), 0, meta.pixel_width - 1),
    y: clamp(Math.floor(gridY * meta.grid_size + meta.grid_size / 2), 0, meta.pixel_height - 1)
  };
}

function collectWalkablePoints(meta: BakedMapMeta, walkableGrid: boolean[][]) {
  const points: MapPoint[] = [];
  for (let gridY = 0; gridY < walkableGrid.length; gridY += 1) {
    for (let gridX = 0; gridX < (walkableGrid[gridY]?.length ?? 0); gridX += 1) {
      if (walkableGrid[gridY][gridX]) points.push(gridToWorldPoint(meta, gridX, gridY));
    }
  }
  return points;
}

function collectColorPixels(data: ImageData, color: { r: number; g: number; b: number }) {
  const points: { x: number; y: number }[] = [];
  for (let y = 0; y < data.height; y += 1) {
    for (let x = 0; x < data.width; x += 1) {
      if (isExactColor(data, x, y, color.r, color.g, color.b)) points.push({ x, y });
    }
  }
  return points;
}

function collectSpawnCells(meta: BakedMapMeta, data: ImageData, color: { r: number; g: number; b: number; label: string }, walkableGrid: boolean[][], warnings: string[]) {
  const cells = new Map<string, MapPoint>();
  for (const pixel of collectColorPixels(data, color)) {
    const gridX = Math.floor(pixel.x / meta.grid_size);
    const gridY = Math.floor(pixel.y / meta.grid_size);
    const key = `${gridX},${gridY}`;
    if (!cells.has(key)) {
      cells.set(key, ensureWalkablePoint(meta, gridToWorldPoint(meta, gridX, gridY), walkableGrid, warnings, color.label));
    }
  }
  return [...cells.values()];
}

function collectCentroidPoint(meta: BakedMapMeta, data: ImageData, color: { r: number; g: number; b: number; label: string }, walkableGrid: boolean[][], warnings: string[]) {
  const pixels = collectColorPixels(data, color);
  if (pixels.length === 0) return [];
  return [ensureWalkablePoint(meta, centroidPoint(meta, pixels), walkableGrid, warnings, color.label)];
}

function centroidPoint(meta: BakedMapMeta, pixels: { x: number; y: number }[]) {
  const total = pixels.reduce((sum, pixel) => ({ x: sum.x + pixel.x, y: sum.y + pixel.y }), { x: 0, y: 0 });
  return pixelToWorldPoint(meta, total.x / pixels.length, total.y / pixels.length);
}

function mapCenterPoint(meta: BakedMapMeta) {
  return { x: meta.world_width / 2, y: meta.world_height / 2, gridX: Math.floor(meta.world_width / meta.grid_size / 2), gridY: Math.floor(meta.world_height / meta.grid_size / 2) };
}

function pixelToWorldPoint(meta: BakedMapMeta, pixelX: number, pixelY: number): MapPoint {
  const scaleX = meta.world_width / meta.pixel_width;
  const scaleY = meta.world_height / meta.pixel_height;
  const x = pixelX * scaleX;
  const y = pixelY * scaleY;
  return {
    x,
    y,
    gridX: Math.floor(x / meta.grid_size),
    gridY: Math.floor(y / meta.grid_size)
  };
}

function gridToWorldPoint(meta: BakedMapMeta, gridX: number, gridY: number): MapPoint {
  return {
    x: gridX * meta.grid_size + meta.grid_size / 2,
    y: gridY * meta.grid_size + meta.grid_size / 2,
    gridX,
    gridY
  };
}

function ensureWalkablePoint(meta: BakedMapMeta, point: MapPoint, walkableGrid: boolean[][], warnings: string[], label: string) {
  if (walkableGrid[point.gridY]?.[point.gridX]) return gridToWorldPoint(meta, point.gridX, point.gridY);
  const nearest = nearestWalkablePoint(meta, point, walkableGrid);
  warnings.push(`地图遮罩警告：${label} 不在可行走区域，已自动移动到最近可行走格。`);
  return nearest;
}

function nearestWalkablePoint(meta: BakedMapMeta, point: MapPoint, walkableGrid: boolean[][]) {
  let best: MapPoint | null = null;
  let bestDistance = Number.POSITIVE_INFINITY;
  for (let gridY = 0; gridY < walkableGrid.length; gridY += 1) {
    for (let gridX = 0; gridX < (walkableGrid[gridY]?.length ?? 0); gridX += 1) {
      if (!walkableGrid[gridY][gridX]) continue;
      const candidate = gridToWorldPoint(meta, gridX, gridY);
      const distance = Math.hypot(candidate.x - point.x, candidate.y - point.y);
      if (distance < bestDistance) {
        best = candidate;
        bestDistance = distance;
      }
    }
  }
  if (!best) throw new Error("地图校验失败：没有可用于点位修正的可行走格。");
  return best;
}

function isExactColor(data: ImageData, x: number, y: number, r: number, g: number, b: number) {
  const offset = (y * data.width + x) * 4;
  return data.data[offset] === r && data.data[offset + 1] === g && data.data[offset + 2] === b;
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}
