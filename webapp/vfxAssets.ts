import fireBoltManifest from "../assest/battle/vfx/fire_bolt/fire_bolt.vfx.json";
import fireBoltImpactExplosionUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_impact_explosion.png";
import fireBoltProjectileLoopUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_projectile_loop.png";
import fireBoltSparksUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_sparks.png";
import fireBoltTrailPuffsUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_trail_puffs.png";

export type VfxBlendMode = "screen" | "normal";

export type VfxSpriteSheet = {
  image: string;
  src: string;
  frameWidth: number;
  frameHeight: number;
  columns: number;
  rows: number;
  frameCount: number;
  fps: number;
  anchorX: number;
  anchorY: number;
  blendMode: VfxBlendMode;
};

export type FireBoltVfxManifest = {
  projectileLoop: VfxSpriteSheet;
  trailPuffs: VfxSpriteSheet;
  impactExplosion: VfxSpriteSheet;
  sparks: VfxSpriteSheet;
};

const fireBoltUrls: Record<string, string> = {
  "fire_bolt_projectile_loop.png": fireBoltProjectileLoopUrl,
  "fire_bolt_trail_puffs.png": fireBoltTrailPuffsUrl,
  "fire_bolt_impact_explosion.png": fireBoltImpactExplosionUrl,
  "fire_bolt_sparks.png": fireBoltSparksUrl
};

function withSource(sheet: Omit<VfxSpriteSheet, "src">): VfxSpriteSheet {
  return {
    ...sheet,
    src: fireBoltUrls[sheet.image] ?? sheet.image
  };
}

const rawFireBoltManifest = fireBoltManifest as {
  projectileLoop: Omit<VfxSpriteSheet, "src">;
  trailPuffs: Omit<VfxSpriteSheet, "src">;
  impactExplosion: Omit<VfxSpriteSheet, "src">;
  sparks: Omit<VfxSpriteSheet, "src">;
};

export const FIRE_BOLT_VFX: FireBoltVfxManifest = {
  projectileLoop: withSource(rawFireBoltManifest.projectileLoop),
  trailPuffs: withSource(rawFireBoltManifest.trailPuffs),
  impactExplosion: withSource(rawFireBoltManifest.impactExplosion),
  sparks: withSource(rawFireBoltManifest.sparks)
};
