import propBoneAltarUrl from "../assest/battle/props/cropped/prop_bone_altar.png";
import propBrazierUrl from "../assest/battle/props/cropped/prop_brazier.png";
import propBrokenPillarUrl from "../assest/battle/props/cropped/prop_broken_pillar.png";
import propDeadBranchesUrl from "../assest/battle/props/cropped/prop_dead_branches.png";
import propRockClusterSmallUrl from "../assest/battle/props/cropped/prop_rock_cluster_small.png";
import propRockClusterTallUrl from "../assest/battle/props/cropped/prop_rock_cluster_tall.png";
import propRuinedGateUrl from "../assest/battle/props/cropped/prop_ruined_gate.png";
import propShrineUrl from "../assest/battle/props/cropped/prop_shrine.png";
import propSkullPileUrl from "../assest/battle/props/cropped/prop_skull_pile.png";
import propStonePillarUrl from "../assest/battle/props/cropped/prop_stone_pillar.png";

export type ScenePropType =
  | "prop_shrine"
  | "prop_broken_pillar"
  | "prop_stone_pillar"
  | "prop_rock_cluster_small"
  | "prop_rock_cluster_tall"
  | "prop_dead_branches"
  | "prop_skull_pile"
  | "prop_brazier"
  | "prop_bone_altar"
  | "prop_ruined_gate";

export type ScenePropAsset = {
  id: ScenePropType;
  type: ScenePropType;
  src: string;
  width: number;
  height: number;
  anchorX: number;
  anchorY: number;
};

export type SceneProp = {
  id: string;
  type: ScenePropType;
  assetId: ScenePropType;
  x: number;
  y: number;
  width: number;
  height: number;
};

export const BATTLE_PROP_ASSETS: Record<ScenePropType, ScenePropAsset> = {
  prop_shrine: {
    id: "prop_shrine",
    type: "prop_shrine",
    src: propShrineUrl,
    width: 108,
    height: 164,
    anchorX: 0.5,
    anchorY: 0.956
  },
  prop_broken_pillar: {
    id: "prop_broken_pillar",
    type: "prop_broken_pillar",
    src: propBrokenPillarUrl,
    width: 112,
    height: 142,
    anchorX: 0.5,
    anchorY: 0.952
  },
  prop_stone_pillar: {
    id: "prop_stone_pillar",
    type: "prop_stone_pillar",
    src: propStonePillarUrl,
    width: 105,
    height: 174,
    anchorX: 0.5,
    anchorY: 0.958
  },
  prop_rock_cluster_small: {
    id: "prop_rock_cluster_small",
    type: "prop_rock_cluster_small",
    src: propRockClusterSmallUrl,
    width: 88,
    height: 76,
    anchorX: 0.5,
    anchorY: 0.918
  },
  prop_rock_cluster_tall: {
    id: "prop_rock_cluster_tall",
    type: "prop_rock_cluster_tall",
    src: propRockClusterTallUrl,
    width: 93,
    height: 152,
    anchorX: 0.5,
    anchorY: 0.956
  },
  prop_dead_branches: {
    id: "prop_dead_branches",
    type: "prop_dead_branches",
    src: propDeadBranchesUrl,
    width: 102,
    height: 108,
    anchorX: 0.5,
    anchorY: 0.928
  },
  prop_skull_pile: {
    id: "prop_skull_pile",
    type: "prop_skull_pile",
    src: propSkullPileUrl,
    width: 95,
    height: 78,
    anchorX: 0.5,
    anchorY: 0.91
  },
  prop_brazier: {
    id: "prop_brazier",
    type: "prop_brazier",
    src: propBrazierUrl,
    width: 77,
    height: 120,
    anchorX: 0.5,
    anchorY: 0.948
  },
  prop_bone_altar: {
    id: "prop_bone_altar",
    type: "prop_bone_altar",
    src: propBoneAltarUrl,
    width: 117,
    height: 120,
    anchorX: 0.5,
    anchorY: 0.94
  },
  prop_ruined_gate: {
    id: "prop_ruined_gate",
    type: "prop_ruined_gate",
    src: propRuinedGateUrl,
    width: 123,
    height: 174,
    anchorX: 0.5,
    anchorY: 0.958
  }
};
