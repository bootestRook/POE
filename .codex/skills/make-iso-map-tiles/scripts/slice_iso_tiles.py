#!/usr/bin/env python3
"""Preview and slice centered 128x64 isometric map tiles from a raw sheet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = value.lower().split("x", 1)
        return int(width), int(height)
    except Exception as exc:
        raise argparse.ArgumentTypeError(f"expected WIDTHxHEIGHT, got {value!r}") from exc


def rel_asset_path(path: Path, repo_root: Path | None) -> str:
    if repo_root:
        try:
            return "/" + path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            pass
    return path.as_posix()


def crop_rect(col: int, row: int, cell_size: tuple[int, int], tile_size: tuple[int, int]) -> tuple[int, int, int, int]:
    cell_w, cell_h = cell_size
    tile_w, tile_h = tile_size
    left = col * cell_w + (cell_w - tile_w) // 2
    top = row * cell_h + (cell_h - tile_h) // 2
    return left, top, left + tile_w, top + tile_h


def chroma_key_magenta(tile: Image.Image, threshold: float) -> Image.Image:
    rgba = np.array(tile.convert("RGBA"))
    rgb = rgba[..., :3].astype(int)
    magenta = np.array([255, 0, 255])
    dist = np.sqrt(((rgb - magenta) ** 2).sum(axis=2))
    rgba[dist < threshold, 3] = 0
    return Image.fromarray(rgba, "RGBA")


def draw_preview(
    raw: Image.Image,
    out: Path,
    cols: int,
    rows: int,
    cell_size: tuple[int, int],
    tile_size: tuple[int, int],
    safe_size: tuple[int, int],
) -> None:
    preview = raw.convert("RGBA")
    draw = ImageDraw.Draw(preview)
    cell_w, cell_h = cell_size
    tile_w, tile_h = tile_size
    width, height = preview.size

    for col in range(cols + 1):
        x = col * cell_w
        draw.line([(x, 0), (x, height)], fill=(255, 48, 48, 230), width=3)
    for row in range(rows + 1):
        y = row * cell_h
        draw.line([(0, y), (width, y)], fill=(255, 48, 48, 230), width=3)

    for row in range(rows):
        for col in range(cols):
            left, top, right, bottom = crop_rect(col, row, cell_size, tile_size)
            draw.rectangle([left, top, right, bottom], outline=(0, 240, 255, 255), width=3)
            cx = col * cell_w + cell_w // 2
            cy = row * cell_h + cell_h // 2
            draw.line([(cx - 7, cy), (cx + 7, cy)], fill=(255, 255, 255, 255), width=2)
            draw.line([(cx, cy - 7), (cx, cy + 7)], fill=(255, 255, 255, 255), width=2)

    out.parent.mkdir(parents=True, exist_ok=True)
    preview.convert("RGB").save(out)


def build_contact_sheet(tile_paths: list[Path], out: Path, tile_size: tuple[int, int], cols: int) -> None:
    tile_w, tile_h = tile_size
    rows = (len(tile_paths) + cols - 1) // cols
    pad = 24
    label_h = 18
    width = cols * tile_w + (cols + 1) * pad
    height = rows * (tile_h + label_h) + (rows + 1) * pad
    sheet = Image.new("RGBA", (width, height), (36, 36, 36, 255))
    draw = ImageDraw.Draw(sheet)

    for idx, path in enumerate(tile_paths):
        col = idx % cols
        row = idx // cols
        x = pad + col * (tile_w + pad)
        y = pad + row * (tile_h + label_h + pad)
        for yy in range(y, y + tile_h, 8):
            for xx in range(x, x + tile_w, 8):
                shade = 84 if ((xx - x) // 8 + (yy - y) // 8) % 2 else 116
                draw.rectangle([xx, yy, min(xx + 7, x + tile_w - 1), min(yy + 7, y + tile_h - 1)], fill=(shade, shade, shade, 255))
        tile = Image.open(path).convert("RGBA")
        sheet.alpha_composite(tile, (x, y))
        draw.rectangle([x, y, x + tile_w, y + tile_h], outline=(0, 240, 255, 255), width=1)
        draw.text((x, y + tile_h + 3), path.stem, fill=(235, 235, 235, 255))

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preview", "slice"))
    parser.add_argument("--confirmed", action="store_true", help="Required for --mode slice after user approval.")
    parser.add_argument("--cols", type=int, default=4)
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--cell-size", type=parse_size, default=(256, 160))
    parser.add_argument("--tile-size", type=parse_size, default=(128, 64))
    parser.add_argument("--safe-size", type=parse_size, default=(104, 48), help="Visible content must fit inside this centered box.")
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--contact", type=Path)
    parser.add_argument("--prefix", default="tile")
    parser.add_argument("--names", help="Comma-separated tile IDs. Count must match cols*rows.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--chroma-threshold", type=float, default=35.0)
    args = parser.parse_args()

    raw = Image.open(args.raw).convert("RGBA")
    expected_size = (args.cols * args.cell_size[0], args.rows * args.cell_size[1])
    if raw.size != expected_size:
        raise SystemExit(f"raw size {raw.size} does not match grid {expected_size}")

    if args.mode == "preview":
        preview = args.preview or args.raw.with_name(args.raw.stem + "-split-preview.png")
        draw_preview(raw, preview, args.cols, args.rows, args.cell_size, args.tile_size, args.safe_size)
        print(f"preview={preview}")
        return 0

    if not args.confirmed:
        raise SystemExit("--confirmed is required for slicing. Show the split preview to the user first and wait for approval.")
    if not args.out:
        raise SystemExit("--out is required for slicing")

    names = [f"{args.prefix}_{idx:02d}" for idx in range(args.cols * args.rows)]
    if args.names:
        names = [name.strip() for name in args.names.split(",") if name.strip()]
        expected_count = args.cols * args.rows
        if len(names) != expected_count:
            raise SystemExit(f"--names provided {len(names)} names, expected {expected_count}")

    args.out.mkdir(parents=True, exist_ok=True)
    tile_paths: list[Path] = []
    assets = []
    tile_w, tile_h = args.tile_size
    for idx, tile_id in enumerate(names):
        col = idx % args.cols
        row = idx // args.cols
        rect = crop_rect(col, row, args.cell_size, args.tile_size)
        tile = chroma_key_magenta(raw.crop(rect), args.chroma_threshold)
        out_path = args.out / f"{tile_id}.png"
        tile.save(out_path)

        alpha = np.array(tile.getchannel("A"))
        ys, xs = np.where(alpha > 0)
        if len(xs) == 0:
            raise SystemExit(f"{tile_id} is empty after chroma key")
        bbox = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
        safe_w, safe_h = args.safe_size
        safe_x0 = (tile_w - safe_w) // 2
        safe_y0 = (tile_h - safe_h) // 2
        safe_x1 = safe_x0 + safe_w
        safe_y1 = safe_y0 + safe_h
        if bbox[0] < safe_x0 or bbox[1] < safe_y0 or bbox[2] > safe_x1 or bbox[3] > safe_y1:
            raise SystemExit(
                f"{tile_id} content bbox {bbox} exceeds centered safe box "
                f"{[safe_x0, safe_y0, safe_x1, safe_y1]}"
            )
        tile_paths.append(out_path)
        assets.append(
            {
                "id": tile_id,
                "type": "tile",
                "path": rel_asset_path(out_path, args.repo_root),
                "width": tile_w,
                "height": tile_h,
                "sourceRaw": rel_asset_path(args.raw, args.repo_root),
                "sourceCell": {"col": col, "row": row, "width": args.cell_size[0], "height": args.cell_size[1]},
                "sourceCrop": {"x": rect[0], "y": rect[1], "width": tile_w, "height": tile_h},
                "safeContentBox": {"width": args.safe_size[0], "height": args.safe_size[1]},
                "contentBBox": {"x": bbox[0], "y": bbox[1], "width": bbox[2] - bbox[0], "height": bbox[3] - bbox[1]},
                "anchorX": 0.5,
                "anchorY": 0.5,
            }
        )

    if args.contact:
        build_contact_sheet(tile_paths, args.contact, args.tile_size, args.cols)

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "type": "isometric-tile-pack",
            "tileWidth": tile_w,
            "tileHeight": tile_h,
            "safeContentWidth": args.safe_size[0],
            "safeContentHeight": args.safe_size[1],
            "cellWidth": args.cell_size[0],
            "cellHeight": args.cell_size[1],
            "columns": args.cols,
            "rows": args.rows,
            "raw": rel_asset_path(args.raw, args.repo_root),
            "contactSheet": rel_asset_path(args.contact, args.repo_root) if args.contact else None,
            "assets": assets,
        }
        args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"sliced={len(tile_paths)}")
    print(f"out={args.out}")
    if args.manifest:
        print(f"manifest={args.manifest}")
    if args.contact:
        print(f"contact={args.contact}")
    print("validation=all cropped tiles are exact size, RGBA, non-empty, and inside safe content box")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
