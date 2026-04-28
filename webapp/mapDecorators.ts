import { EDGE_TILE_ASSETS, EdgeTileAsset } from "./edgeTileAssets";
import { BattleTerrainTileKind, tileHash } from "./terrainAssets";

function isBlocked(tiles: BattleTerrainTileKind[][], x: number, y: number) {
  return !tiles[y]?.[x] || tiles[y][x] === "blocked";
}

function isGroundLike(tile: BattleTerrainTileKind) {
  return tile === "ground" || tile === "object";
}

export function edgeAssetsForTile(tiles: BattleTerrainTileKind[][], x: number, y: number): EdgeTileAsset[] {
  const tile = tiles[y]?.[x];
  if (!tile || !isGroundLike(tile)) return [];

  const north = isBlocked(tiles, x, y - 1);
  const south = isBlocked(tiles, x, y + 1);
  const east = isBlocked(tiles, x + 1, y);
  const west = isBlocked(tiles, x - 1, y);
  if (!north && !south && !east && !west) return [];

  const hash = tileHash(x, y);
  const result: EdgeTileAsset[] = [];

  if ((north && west) || (north && east)) {
    result.push(EDGE_TILE_ASSETS.edge_cliff_inner_corner);
  } else if ((south && west) || (south && east)) {
    result.push(EDGE_TILE_ASSETS.edge_cliff_outer_corner);
  }

  if (south) {
    if (hash % 11 === 0) result.push(EDGE_TILE_ASSETS.edge_lava_border);
    else if (hash % 13 === 0) result.push(EDGE_TILE_ASSETS.edge_void_border);
    else result.push(EDGE_TILE_ASSETS.edge_cliff_s);
  }
  if (north && result.length < 2) result.push(EDGE_TILE_ASSETS.edge_cliff_n);
  if (east && result.length < 2) result.push(EDGE_TILE_ASSETS.edge_cliff_e);
  if (west && result.length < 2) result.push(EDGE_TILE_ASSETS.edge_cliff_w);

  return result.slice(0, 2);
}
