import edgeCliffEUrl from "../assest/battle/edges/cropped/edge_cliff_e.png";
import edgeCliffInnerCornerUrl from "../assest/battle/edges/cropped/edge_cliff_inner_corner.png";
import edgeCliffNUrl from "../assest/battle/edges/cropped/edge_cliff_n.png";
import edgeCliffOuterCornerUrl from "../assest/battle/edges/cropped/edge_cliff_outer_corner.png";
import edgeCliffSUrl from "../assest/battle/edges/cropped/edge_cliff_s.png";
import edgeCliffWUrl from "../assest/battle/edges/cropped/edge_cliff_w.png";
import edgeLavaBorderUrl from "../assest/battle/edges/cropped/edge_lava_border.png";
import edgeVoidBorderUrl from "../assest/battle/edges/cropped/edge_void_border.png";

export type EdgeTileAssetId =
  | "edge_cliff_n"
  | "edge_cliff_s"
  | "edge_cliff_e"
  | "edge_cliff_w"
  | "edge_cliff_inner_corner"
  | "edge_cliff_outer_corner"
  | "edge_lava_border"
  | "edge_void_border";

export type EdgeTileAsset = {
  id: EdgeTileAssetId;
  src: string;
  width: number;
  height: number;
  anchorX: number;
  anchorY: number;
};

export const EDGE_TILE_ASSETS: Record<EdgeTileAssetId, EdgeTileAsset> = {
  edge_cliff_n: {
    id: "edge_cliff_n",
    src: edgeCliffNUrl,
    width: 128,
    height: 154,
    anchorX: 0.5,
    anchorY: 0
  },
  edge_cliff_s: {
    id: "edge_cliff_s",
    src: edgeCliffSUrl,
    width: 128,
    height: 154,
    anchorX: 0.5,
    anchorY: 0
  },
  edge_cliff_e: {
    id: "edge_cliff_e",
    src: edgeCliffEUrl,
    width: 128,
    height: 160,
    anchorX: 0.5,
    anchorY: 0
  },
  edge_cliff_w: {
    id: "edge_cliff_w",
    src: edgeCliffWUrl,
    width: 128,
    height: 165,
    anchorX: 0.5,
    anchorY: 0
  },
  edge_cliff_inner_corner: {
    id: "edge_cliff_inner_corner",
    src: edgeCliffInnerCornerUrl,
    width: 128,
    height: 108,
    anchorX: 0.5,
    anchorY: 0
  },
  edge_cliff_outer_corner: {
    id: "edge_cliff_outer_corner",
    src: edgeCliffOuterCornerUrl,
    width: 128,
    height: 158,
    anchorX: 0.5,
    anchorY: 0
  },
  edge_lava_border: {
    id: "edge_lava_border",
    src: edgeLavaBorderUrl,
    width: 128,
    height: 142,
    anchorX: 0.5,
    anchorY: 0
  },
  edge_void_border: {
    id: "edge_void_border",
    src: edgeVoidBorderUrl,
    width: 128,
    height: 155,
    anchorX: 0.5,
    anchorY: 0
  }
};
