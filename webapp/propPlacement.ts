import { BATTLE_PROP_ASSETS, SceneProp, ScenePropType } from "./sceneProps";
import { BattleTerrainTileKind, tileHash } from "./terrainAssets";

type TilemapForProps = {
  tileSize: number;
  width: number;
  height: number;
  tiles: BattleTerrainTileKind[][];
  spawnPoint: {
    tileX: number;
    tileY: number;
  };
};

type WeightedProp = {
  type: ScenePropType;
  weight: number;
};

const PROP_WEIGHTS: WeightedProp[] = [
  { type: "prop_rock_cluster_small", weight: 24 },
  { type: "prop_dead_branches", weight: 18 },
  { type: "prop_skull_pile", weight: 14 },
  { type: "prop_rock_cluster_tall", weight: 12 },
  { type: "prop_broken_pillar", weight: 10 },
  { type: "prop_brazier", weight: 7 },
  { type: "prop_stone_pillar", weight: 6 },
  { type: "prop_bone_altar", weight: 4 },
  { type: "prop_shrine", weight: 3 },
  { type: "prop_ruined_gate", weight: 2 }
];

const FORCED_POIS: { type: ScenePropType; dx: number; dy: number }[] = [
  { type: "prop_bone_altar", dx: 4, dy: -2 },
  { type: "prop_shrine", dx: -5, dy: 2 },
  { type: "prop_ruined_gate", dx: 6, dy: 2 },
  { type: "prop_brazier", dx: -3, dy: -3 }
];

export function createProceduralSceneProps(tilemap: TilemapForProps): SceneProp[] {
  const props: SceneProp[] = [];
  const occupied: { x: number; y: number }[] = [];

  for (const poi of FORCED_POIS) {
    const tileX = tilemap.spawnPoint.tileX + poi.dx;
    const tileY = tilemap.spawnPoint.tileY + poi.dy;
    if (!canPlaceProp(tilemap, tileX, tileY, occupied, 2.2)) continue;
    props.push(createProp(poi.type, tilemap, tileX, tileY, 0, 0, "poi"));
    occupied.push({ x: tileX, y: tileY });
  }

  for (let y = 1; y < tilemap.height - 1; y += 1) {
    for (let x = 1; x < tilemap.width - 1; x += 1) {
      if (!canPlaceProp(tilemap, x, y, occupied, 1.75)) continue;
      const hash = tileHash(x + 101, y + 53);
      if (hash % 100 >= 7) continue;
      const type = weightedPropType(hash);
      const jitterX = (((hash >> 4) % 17) - 8) * 1.8;
      const jitterY = (((hash >> 9) % 13) - 6) * 1.6;
      props.push(createProp(type, tilemap, x, y, jitterX, jitterY, "scatter"));
      occupied.push({ x, y });
    }
  }

  return props;
}

function canPlaceProp(tilemap: TilemapForProps, tileX: number, tileY: number, occupied: { x: number; y: number }[], minDistance: number) {
  const tile = tilemap.tiles[tileY]?.[tileX];
  if (tile !== "ground" && tile !== "object") return false;
  const dx = tileX - tilemap.spawnPoint.tileX;
  const dy = tileY - tilemap.spawnPoint.tileY;
  if (Math.hypot(dx, dy) < 3.4) return false;
  if (tileX <= 1 || tileY <= 1 || tileX >= tilemap.width - 2 || tileY >= tilemap.height - 2) return false;
  return occupied.every((point) => Math.hypot(point.x - tileX, point.y - tileY) >= minDistance);
}

function weightedPropType(hash: number): ScenePropType {
  const total = PROP_WEIGHTS.reduce((sum, item) => sum + item.weight, 0);
  let cursor = hash % total;
  for (const item of PROP_WEIGHTS) {
    cursor -= item.weight;
    if (cursor < 0) return item.type;
  }
  return "prop_rock_cluster_small";
}

function createProp(type: ScenePropType, tilemap: TilemapForProps, tileX: number, tileY: number, jitterX: number, jitterY: number, source: "poi" | "scatter"): SceneProp {
  const asset = BATTLE_PROP_ASSETS[type];
  return {
    id: `${source}-${type}-${tileX}-${tileY}`,
    type,
    assetId: type,
    x: tileX * tilemap.tileSize + tilemap.tileSize / 2 + jitterX,
    y: tileY * tilemap.tileSize + tilemap.tileSize / 2 + jitterY,
    width: asset.width,
    height: asset.height
  };
}
