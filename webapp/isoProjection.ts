export const ISO_TILE_W = 128;
export const ISO_TILE_H = 64;
export const WORLD_TILE_SIZE = 64;

export type IsoScreenPoint = {
  x: number;
  y: number;
};

export type IsoProjectionBounds = {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
  offsetX: number;
  offsetY: number;
};

export function projectWorldToScreen(worldX: number, worldY: number): IsoScreenPoint {
  const tileX = worldX / WORLD_TILE_SIZE;
  const tileY = worldY / WORLD_TILE_SIZE;
  return {
    x: (tileX - tileY) * (ISO_TILE_W / 2),
    y: (tileX + tileY) * (ISO_TILE_H / 2)
  };
}

export function unprojectScreenToWorld(screenX: number, screenY: number): IsoScreenPoint {
  const tileX = screenY / ISO_TILE_H + screenX / ISO_TILE_W;
  const tileY = screenY / ISO_TILE_H - screenX / ISO_TILE_W;
  return {
    x: tileX * WORLD_TILE_SIZE,
    y: tileY * WORLD_TILE_SIZE
  };
}

export function createIsoProjectionBounds(mapWidth: number, mapHeight: number, tileSize: number): IsoProjectionBounds {
  const worldWidth = mapWidth * tileSize;
  const worldHeight = mapHeight * tileSize;
  const corners = [
    projectWorldToScreen(0, 0),
    projectWorldToScreen(worldWidth, 0),
    projectWorldToScreen(0, worldHeight),
    projectWorldToScreen(worldWidth, worldHeight)
  ];
  const minX = Math.min(...corners.map((point) => point.x));
  const maxX = Math.max(...corners.map((point) => point.x));
  const minY = Math.min(...corners.map((point) => point.y));
  const maxY = Math.max(...corners.map((point) => point.y));
  return {
    minX,
    maxX,
    minY,
    maxY,
    width: maxX - minX + ISO_TILE_W,
    height: maxY - minY + ISO_TILE_H,
    offsetX: -minX + ISO_TILE_W / 2,
    offsetY: -minY
  };
}

export function addProjectionOffset(point: IsoScreenPoint, bounds: IsoProjectionBounds): IsoScreenPoint {
  return {
    x: point.x + bounds.offsetX,
    y: point.y + bounds.offsetY
  };
}
