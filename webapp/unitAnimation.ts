import {
  implementedUnitDirections,
  UNIT_ANIMATION_BY_KEY,
  UnitAnimationAsset,
  UnitAnimationState,
  UnitDirection,
  UnitVisualType,
  unitAnimationKey
} from "./unitAssets";

export type UnitAnimationContext = {
  unitId: UnitVisualType;
  requestedState: UnitAnimationState;
  movementVector: { x: number; y: number };
  fallbackDirection: UnitDirection;
  elapsedMs: number;
  baseMoveSpeed: number;
  currentMoveSpeed: number;
  attackStartedAtMs?: number;
  attackUntilMs?: number;
};

export type UnitAnimationFrame = {
  animation: UnitAnimationAsset;
  frameIndex: number;
  playbackRate: number;
};

const EIGHT_TO_HORIZONTAL_DIRECTION: Record<UnitDirection, UnitDirection> = {
  down: "right",
  down_right: "right",
  right: "right",
  up_right: "right",
  up: "right",
  up_left: "left",
  left: "left",
  down_left: "left"
};
const GENERIC_FALLBACK_UNIT_ID: UnitVisualType = "player_adventurer";

export function resolveDirection(vector: { x: number; y: number }, fallbackDirection: UnitDirection): UnitDirection {
  if (Math.hypot(vector.x, vector.y) < 0.001) return fallbackDirection;
  const angle = Math.atan2(vector.y, vector.x);
  const octant = Math.round((angle / (Math.PI / 4) + 8) % 8);
  const directions: UnitDirection[] = ["right", "down_right", "down", "down_left", "left", "up_left", "up", "up_right"];
  return directions[octant % directions.length];
}

export function resolveAnimationPlaybackRate(context: Pick<UnitAnimationContext, "requestedState" | "baseMoveSpeed" | "currentMoveSpeed">) {
  if (context.requestedState !== "walk") return 1;
  return animationSpeedMultiplier(context);
}

export function animationSpeedMultiplier(context: Pick<UnitAnimationContext, "baseMoveSpeed" | "currentMoveSpeed">) {
  if (context.baseMoveSpeed <= 0) return 1;
  return clamp(context.currentMoveSpeed / context.baseMoveSpeed, 0.65, 1.75);
}

export function fallbackAnimation(unitId: UnitVisualType, state: UnitAnimationState, direction: UnitDirection): UnitAnimationAsset {
  const implementedDirections = implementedUnitDirections();
  const implementedDirection = implementedDirections.includes(direction)
    ? direction
    : implementedDirections.includes(EIGHT_TO_HORIZONTAL_DIRECTION[direction])
      ? EIGHT_TO_HORIZONTAL_DIRECTION[direction]
      : implementedDirections[0] ?? "right";
  return (
    UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitId, state, implementedDirection))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitId, state, "right"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitId, state, "left"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitId, "idle", implementedDirection))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitId, "idle", "right"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(unitId, "idle", "left"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(GENERIC_FALLBACK_UNIT_ID, state, implementedDirection))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(GENERIC_FALLBACK_UNIT_ID, state, "right"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(GENERIC_FALLBACK_UNIT_ID, state, "left"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(GENERIC_FALLBACK_UNIT_ID, "idle", implementedDirection))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(GENERIC_FALLBACK_UNIT_ID, "idle", "right"))
    ?? UNIT_ANIMATION_BY_KEY.get(unitAnimationKey(GENERIC_FALLBACK_UNIT_ID, "idle", "left"))
    ?? UNIT_ANIMATION_ASSETS[0]
  );
}

export function resolveUnitAnimation(context: UnitAnimationContext): UnitAnimationFrame {
  const attackActive = context.attackUntilMs !== undefined && context.elapsedMs < context.attackUntilMs;
  const requestedState = attackActive ? "attack" : context.requestedState;
  const direction = resolveDirection(context.movementVector, context.fallbackDirection);
  const animation = fallbackAnimation(context.unitId, requestedState, direction);
  const playbackRate = resolveAnimationPlaybackRate({ ...context, requestedState });
  return getAnimationFrame(animation, context.elapsedMs - (attackActive ? context.attackStartedAtMs ?? 0 : 0), playbackRate);
}

export function getAnimationFrame(animation: UnitAnimationAsset, elapsedMs: number, playbackRate = 1): UnitAnimationFrame {
  const frameDuration = 1000 / Math.max(1, animation.fps * playbackRate * animation.playbackRate);
  const rawFrame = Math.floor(Math.max(0, elapsedMs) / frameDuration);
  const frameIndex = animation.loop ? rawFrame % animation.frameCount : Math.min(animation.frameCount - 1, rawFrame);
  return {
    animation,
    frameIndex,
    playbackRate
  };
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}
