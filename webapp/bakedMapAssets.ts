import dungeon001BackgroundUrl from "../assets/battle/maps/dungeon_001/background.png";
import dungeon001BlockerMaskUrl from "../assets/battle/maps/dungeon_001/blocker_mask.png";
import dungeon001Meta from "../assets/battle/maps/dungeon_001/map_meta.json";
import dungeon001SpawnMaskUrl from "../assets/battle/maps/dungeon_001/spawn_mask.png";
import dungeon001WalkableMaskUrl from "../assets/battle/maps/dungeon_001/walkable_mask.png";
import type { BakedMapMeta } from "./bakedMapLoader";

export type BakedMapAssetDefinition = {
  id: string;
  meta: BakedMapMeta;
  backgroundUrl: string;
  walkableMaskUrl: string;
  blockerMaskUrl: string;
  spawnMaskUrl: string;
};

export const BAKED_BATTLE_MAPS: BakedMapAssetDefinition[] = [
  {
    id: dungeon001Meta.id,
    meta: dungeon001Meta,
    backgroundUrl: dungeon001BackgroundUrl,
    walkableMaskUrl: dungeon001WalkableMaskUrl,
    blockerMaskUrl: dungeon001BlockerMaskUrl,
    spawnMaskUrl: dungeon001SpawnMaskUrl
  }
];

export const DEFAULT_BAKED_BATTLE_MAP_ID = "dungeon_001";

export function bakedMapAssetById(id: string) {
  return BAKED_BATTLE_MAPS.find((map) => map.id === id) ?? null;
}
