import fireBoltManifest from "../assest/battle/vfx/fire_bolt/fire_bolt.vfx.json";
import fireBoltImpactExplosionUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_impact_explosion.png";
import fireBoltProjectileLoopUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_projectile_loop.png";
import fireBoltSparksUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_sparks.png";
import fireBoltTrailPuffsUrl from "../assest/battle/vfx/fire_bolt/fire_bolt_trail_puffs.png";
import iceShardsManifest from "../assest/battle/vfx/ice_shards/ice_shards.vfx.json";
import iceShardsCrystalSparksUrl from "../assest/battle/vfx/ice_shards/ice_shards_crystal_sparks.png";
import iceShardsImpactBurstUrl from "../assest/battle/vfx/ice_shards/ice_shards_impact_burst.png";
import iceShardsProjectileLoopUrl from "../assest/battle/vfx/ice_shards/ice_shards_projectile_loop.png";
import iceShardsTrailFrostUrl from "../assest/battle/vfx/ice_shards/ice_shards_trail_frost.png";
import penetratingShotManifest from "../assest/battle/vfx/penetrating_shot/penetrating_shot.vfx.json";
import penetratingShotImpactSparksUrl from "../assest/battle/vfx/penetrating_shot/penetrating_shot_impact_sparks.png";
import penetratingShotMuzzleFlashUrl from "../assest/battle/vfx/penetrating_shot/penetrating_shot_muzzle_flash.png";
import penetratingShotProjectileLoopUrl from "../assest/battle/vfx/penetrating_shot/penetrating_shot_projectile_loop.png";
import penetratingShotTrailLinesUrl from "../assest/battle/vfx/penetrating_shot/penetrating_shot_trail_lines.png";

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

export type IceShardsVfxManifest = {
  projectileLoop: VfxSpriteSheet;
  trailFrost: VfxSpriteSheet;
  impactBurst: VfxSpriteSheet;
  crystalSparks: VfxSpriteSheet;
};

export type PenetratingShotVfxManifest = {
  muzzleFlash: VfxSpriteSheet;
  projectileLoop: VfxSpriteSheet;
  trailLines: VfxSpriteSheet;
  impactSparks: VfxSpriteSheet;
};

const fireBoltUrls: Record<string, string> = {
  "fire_bolt_projectile_loop.png": fireBoltProjectileLoopUrl,
  "fire_bolt_trail_puffs.png": fireBoltTrailPuffsUrl,
  "fire_bolt_impact_explosion.png": fireBoltImpactExplosionUrl,
  "fire_bolt_sparks.png": fireBoltSparksUrl
};

const iceShardsUrls: Record<string, string> = {
  "ice_shards_projectile_loop.png": iceShardsProjectileLoopUrl,
  "ice_shards_trail_frost.png": iceShardsTrailFrostUrl,
  "ice_shards_impact_burst.png": iceShardsImpactBurstUrl,
  "ice_shards_crystal_sparks.png": iceShardsCrystalSparksUrl
};

const penetratingShotUrls: Record<string, string> = {
  "penetrating_shot_muzzle_flash.png": penetratingShotMuzzleFlashUrl,
  "penetrating_shot_projectile_loop.png": penetratingShotProjectileLoopUrl,
  "penetrating_shot_trail_lines.png": penetratingShotTrailLinesUrl,
  "penetrating_shot_impact_sparks.png": penetratingShotImpactSparksUrl
};

function withSource(sheet: Omit<VfxSpriteSheet, "src">, urls: Record<string, string>): VfxSpriteSheet {
  return {
    ...sheet,
    src: urls[sheet.image] ?? sheet.image
  };
}

const rawFireBoltManifest = fireBoltManifest as {
  projectileLoop: Omit<VfxSpriteSheet, "src">;
  trailPuffs: Omit<VfxSpriteSheet, "src">;
  impactExplosion: Omit<VfxSpriteSheet, "src">;
  sparks: Omit<VfxSpriteSheet, "src">;
};

const rawIceShardsManifest = iceShardsManifest as {
  projectileLoop: Omit<VfxSpriteSheet, "src">;
  trailFrost: Omit<VfxSpriteSheet, "src">;
  impactBurst: Omit<VfxSpriteSheet, "src">;
  crystalSparks: Omit<VfxSpriteSheet, "src">;
};

const rawPenetratingShotManifest = penetratingShotManifest as {
  muzzleFlash: Omit<VfxSpriteSheet, "src">;
  projectileLoop: Omit<VfxSpriteSheet, "src">;
  trailLines: Omit<VfxSpriteSheet, "src">;
  impactSparks: Omit<VfxSpriteSheet, "src">;
};

export const FIRE_BOLT_VFX: FireBoltVfxManifest = {
  projectileLoop: withSource(rawFireBoltManifest.projectileLoop, fireBoltUrls),
  trailPuffs: withSource(rawFireBoltManifest.trailPuffs, fireBoltUrls),
  impactExplosion: withSource(rawFireBoltManifest.impactExplosion, fireBoltUrls),
  sparks: withSource(rawFireBoltManifest.sparks, fireBoltUrls)
};

export const ICE_SHARDS_VFX: IceShardsVfxManifest = {
  projectileLoop: withSource(rawIceShardsManifest.projectileLoop, iceShardsUrls),
  trailFrost: withSource(rawIceShardsManifest.trailFrost, iceShardsUrls),
  impactBurst: withSource(rawIceShardsManifest.impactBurst, iceShardsUrls),
  crystalSparks: withSource(rawIceShardsManifest.crystalSparks, iceShardsUrls)
};

export const PENETRATING_SHOT_VFX: PenetratingShotVfxManifest = {
  muzzleFlash: withSource(rawPenetratingShotManifest.muzzleFlash, penetratingShotUrls),
  projectileLoop: withSource(rawPenetratingShotManifest.projectileLoop, penetratingShotUrls),
  trailLines: withSource(rawPenetratingShotManifest.trailLines, penetratingShotUrls),
  impactSparks: withSource(rawPenetratingShotManifest.impactSparks, penetratingShotUrls)
};
