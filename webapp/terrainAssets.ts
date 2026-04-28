import groundBaseUrl from "../assest/battle/tiles/cropped/ground_base.png";
import groundCrackedUrl from "../assest/battle/tiles/cropped/ground_cracked.png";
import groundDarkUrl from "../assest/battle/tiles/cropped/ground_dark.png";
import groundDirtUrl from "../assest/battle/tiles/cropped/ground_dirt.png";
import groundRitualUrl from "../assest/battle/tiles/cropped/ground_ritual.png";
import groundStoneUrl from "../assest/battle/tiles/cropped/ground_stone.png";

export type BattleTerrainTileKind = "ground" | "blocked" | "object";
export type TerrainTileAssetId = "ground_base" | "ground_dark" | "ground_cracked" | "ground_stone" | "ground_ritual" | "ground_dirt";

export type TerrainTileAsset = {
  id: TerrainTileAssetId;
  terrainKind: "base" | "dark" | "cracked" | "stone" | "ritual" | "dirt";
  src: string;
  width: number;
  height: number;
  anchorX: number;
  anchorY: number;
};

export const TERRAIN_TILE_ASSETS: Record<TerrainTileAssetId, TerrainTileAsset> = {
  ground_base: {
    id: "ground_base",
    terrainKind: "base",
    src: groundBaseUrl,
    width: 128,
    height: 109,
    anchorX: 0.5,
    anchorY: 0
  },
  ground_dark: {
    id: "ground_dark",
    terrainKind: "dark",
    src: groundDarkUrl,
    width: 128,
    height: 103,
    anchorX: 0.5,
    anchorY: 0
  },
  ground_cracked: {
    id: "ground_cracked",
    terrainKind: "cracked",
    src: groundCrackedUrl,
    width: 128,
    height: 96,
    anchorX: 0.5,
    anchorY: 0
  },
  ground_stone: {
    id: "ground_stone",
    terrainKind: "stone",
    src: groundStoneUrl,
    width: 128,
    height: 96,
    anchorX: 0.5,
    anchorY: 0
  },
  ground_ritual: {
    id: "ground_ritual",
    terrainKind: "ritual",
    src: groundRitualUrl,
    width: 128,
    height: 103,
    anchorX: 0.5,
    anchorY: 0
  },
  ground_dirt: {
    id: "ground_dirt",
    terrainKind: "dirt",
    src: groundDirtUrl,
    width: 128,
    height: 108,
    anchorX: 0.5,
    anchorY: 0
  }
};

const GROUND_VARIANTS: TerrainTileAsset[] = [
  TERRAIN_TILE_ASSETS.ground_base,
  TERRAIN_TILE_ASSETS.ground_base,
  TERRAIN_TILE_ASSETS.ground_dark,
  TERRAIN_TILE_ASSETS.ground_cracked,
  TERRAIN_TILE_ASSETS.ground_stone,
  TERRAIN_TILE_ASSETS.ground_dirt
];

export function tileHash(x: number, y: number) {
  let value = (x + 11) * 374761393 + (y + 17) * 668265263;
  value = (value ^ (value >> 13)) * 1274126177;
  return Math.abs(value ^ (value >> 16));
}

export function terrainAssetForTile(tileKind: BattleTerrainTileKind, x: number, y: number) {
  if (tileKind === "blocked") return null;
  if (tileKind === "object") return TERRAIN_TILE_ASSETS.ground_ritual;
  return GROUND_VARIANTS[tileHash(x, y) % GROUND_VARIANTS.length];
}
