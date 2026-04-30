import seamlessStoneGroundBloodUrl from "../assest/battle/tiles/cropped/seamless_stone_ground_blood.png";
import seamlessStoneGroundBrokenUrl from "../assest/battle/tiles/cropped/seamless_stone_ground_broken.png";
import seamlessStoneGroundCrackedUrl from "../assest/battle/tiles/cropped/seamless_stone_ground_cracked.png";
import seamlessStoneGroundPlainUrl from "../assest/battle/tiles/cropped/seamless_stone_ground_plain.png";

export type BattleTerrainTileKind = "ground" | "blocked" | "object";
export type TerrainTileAssetId =
  | "seamless_stone_ground_plain"
  | "seamless_stone_ground_broken"
  | "seamless_stone_ground_cracked"
  | "seamless_stone_ground_blood";

export type TerrainTileAsset = {
  id: TerrainTileAssetId;
  terrainKind: "stone" | "broken" | "cracked" | "blood";
  src: string;
  width: number;
  height: number;
  anchorX: number;
  anchorY: number;
};

const SEAMLESS_GROUND_TILE_WIDTH = 570;
const SEAMLESS_GROUND_TILE_HEIGHT = 380;

export const TERRAIN_TILE_ASSETS: Record<TerrainTileAssetId, TerrainTileAsset> = {
  seamless_stone_ground_plain: createTerrainAsset("seamless_stone_ground_plain", "stone", seamlessStoneGroundPlainUrl),
  seamless_stone_ground_broken: createTerrainAsset("seamless_stone_ground_broken", "broken", seamlessStoneGroundBrokenUrl),
  seamless_stone_ground_cracked: createTerrainAsset("seamless_stone_ground_cracked", "cracked", seamlessStoneGroundCrackedUrl),
  seamless_stone_ground_blood: createTerrainAsset("seamless_stone_ground_blood", "blood", seamlessStoneGroundBloodUrl)
};

const SEAMLESS_GROUND_DEFAULT_VARIANTS: TerrainTileAsset[] = [
  TERRAIN_TILE_ASSETS.seamless_stone_ground_plain,
  TERRAIN_TILE_ASSETS.seamless_stone_ground_broken,
  TERRAIN_TILE_ASSETS.seamless_stone_ground_cracked
];

function createTerrainAsset(id: TerrainTileAssetId, terrainKind: TerrainTileAsset["terrainKind"], src: string): TerrainTileAsset {
  return {
    id,
    terrainKind,
    src,
    width: SEAMLESS_GROUND_TILE_WIDTH,
    height: SEAMLESS_GROUND_TILE_HEIGHT,
    anchorX: 0.5,
    anchorY: 0
  };
}

export function tileHash(x: number, y: number) {
  let value = (x + 11) * 374761393 + (y + 17) * 668265263;
  value = (value ^ (value >> 13)) * 1274126177;
  return Math.abs(value ^ (value >> 16));
}

export function terrainAssetForTile(tileKind: BattleTerrainTileKind, x: number, y: number, assetId?: TerrainTileAssetId) {
  if (tileKind === "blocked") return null;
  if (assetId) return TERRAIN_TILE_ASSETS[assetId];
  if (tileKind === "object") return TERRAIN_TILE_ASSETS.seamless_stone_ground_blood;
  return SEAMLESS_GROUND_DEFAULT_VARIANTS[tileHash(x, y) % SEAMLESS_GROUND_DEFAULT_VARIANTS.length];
}
