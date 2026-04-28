export type IsoDepthPoint = {
  x: number;
  y: number;
};

export function dimetricDepth(worldX: number, worldY: number): number {
  return worldX + worldY;
}

export function compareDimetricDepth(left: IsoDepthPoint, right: IsoDepthPoint): number {
  return dimetricDepth(left.x, left.y) - dimetricDepth(right.x, right.y);
}
