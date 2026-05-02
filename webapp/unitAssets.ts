import unitAnimationManifest from "../assets/battle/units/manifests/unit-animations-manifest.json";

export type UnitDirection = "down" | "down_right" | "right" | "up_right" | "up" | "up_left" | "left" | "down_left";
export type UnitAnimationState = "idle" | "walk" | "attack";
export type UnitVisualType = "player_adventurer" | "enemy_imp" | "enemy_brute";

export type UnitAnimationAsset = {
  id: string;
  path: string;
  unitId: UnitVisualType;
  state: UnitAnimationState;
  direction: UnitDirection;
  src: string;
  frameCount: number;
  fps: number;
  loop: boolean;
  durationMs: number;
  frameWidth: number;
  frameHeight: number;
  frameRow: number;
  width: number;
  height: number;
  anchorX: number;
  anchorY: number;
  scale: number;
  fallbackState?: UnitAnimationState | null;
  fallbackDirection: UnitDirection;
  playbackRate: number;
};

export type UnitAnimationManifest = {
  directions: UnitDirection[];
  implementedDirections: UnitDirection[];
  states: UnitAnimationState[];
  assets: Omit<UnitAnimationAsset, "src">[];
};

const unitAnimationSheetUrls = import.meta.glob([
  "../assets/battle/units/sheets/*.png",
  "!../assets/battle/units/sheets/*_run_*.png"
], {
  eager: true,
  query: "?url",
  import: "default"
}) as Record<string, string>;

function assetUrl(path: string) {
  return unitAnimationSheetUrls[`..${path}`] ?? path;
}

const manifest = unitAnimationManifest as UnitAnimationManifest;

export const UNIT_ANIMATION_ASSETS: UnitAnimationAsset[] = manifest.assets.map((asset) => ({
  ...asset,
  src: assetUrl(asset.path)
}));

export const UNIT_ANIMATION_BY_KEY = new Map(
  UNIT_ANIMATION_ASSETS.map((asset) => [unitAnimationKey(asset.unitId, asset.state, asset.direction), asset])
);

export function unitAnimationKey(unitId: UnitVisualType, state: UnitAnimationState, direction: UnitDirection) {
  return `${unitId}:${state}:${direction}`;
}

export function implementedUnitDirections() {
  return manifest.implementedDirections;
}

export function resolveUnitSprite(unitType: UnitVisualType, direction: UnitDirection = "right") {
  return UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitType, "idle", direction))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitType, "idle", "right"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitType, "idle", "left"))!;
}

export function selectEnemyUnitType(enemyId: number): UnitVisualType {
  void enemyId;
  return "enemy_imp";
}
