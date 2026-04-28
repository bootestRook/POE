from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PROP_ROOT = ROOT / "assest" / "battle" / "props"
RAW_IMAGE = PROP_ROOT / "raw" / "battle-props-sheet-generated.png"
CROPPED_DIR = PROP_ROOT / "cropped"
ATLAS_DIR = PROP_ROOT / "atlas"
MANIFEST_DIR = PROP_ROOT / "manifest"

PROP_LAYOUT = [
    ("rock_small", 0, 0),
    ("rock_tall", 1, 0),
    ("pillar", 2, 0),
    ("shrine", 0, 1),
    ("crate_stone", 1, 1),
    ("broken_obelisk", 2, 1),
]

TARGET_HEIGHTS = {
    "rock_small": 78,
    "rock_tall": 154,
    "pillar": 178,
    "shrine": 184,
    "crate_stone": 118,
    "broken_obelisk": 176,
}


def is_key_pixel(pixel: tuple[int, int, int, int]) -> bool:
    red, green, blue, _alpha = pixel
    return green >= 130 and green >= red * 1.45 and green >= blue * 1.45


def make_transparent(source: Image.Image) -> Image.Image:
    rgba = source.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if is_key_pixel((red, green, blue, alpha)):
                pixels[x, y] = (0, 0, 0, 0)
    return despill_green_edges(rgba)


def has_transparent_neighbor(alpha_pixels, width: int, height: int, x: int, y: int, radius: int = 2) -> bool:
    for next_y in range(max(0, y - radius), min(height, y + radius + 1)):
        for next_x in range(max(0, x - radius), min(width, x + radius + 1)):
            if alpha_pixels[next_x, next_y] == 0:
                return True
    return False


def despill_green_edges(image: Image.Image) -> Image.Image:
    rgba = image.copy()
    pixels = rgba.load()
    alpha = rgba.getchannel("A")
    alpha_pixels = alpha.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha_value = pixels[x, y]
            if alpha_value == 0:
                continue
            if not has_transparent_neighbor(alpha_pixels, width, height, x, y):
                continue
            dominant = max(red, blue)
            if green > dominant + 18:
                if green > dominant * 1.55 and green > 120:
                    pixels[x, y] = (0, 0, 0, 0)
                else:
                    pixels[x, y] = (red, min(green, dominant + 14), blue, alpha_value)
    return rgba


def alpha_bounds(image: Image.Image, padding: int = 8) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("没有找到可裁剪的不透明像素。")
    left, top, right, bottom = bounds
    return (
        max(0, left - padding),
        max(0, top - padding),
        min(image.width, right + padding),
        min(image.height, bottom + padding),
    )


def component_bounds(image: Image.Image) -> list[tuple[int, int, int, int]]:
    alpha = image.getchannel("A")
    pixels = alpha.load()
    width, height = alpha.size
    seen: set[tuple[int, int]] = set()
    bounds: list[tuple[int, int, int, int]] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in seen or pixels[x, y] <= 0:
                continue

            queue = deque([(x, y)])
            seen.add((x, y))
            left = right = x
            top = bottom = y
            count = 0

            while queue:
                current_x, current_y = queue.popleft()
                count += 1
                left = min(left, current_x)
                right = max(right, current_x)
                top = min(top, current_y)
                bottom = max(bottom, current_y)

                for next_x in (current_x - 1, current_x, current_x + 1):
                    for next_y in (current_y - 1, current_y, current_y + 1):
                        if next_x < 0 or next_y < 0 or next_x >= width or next_y >= height:
                            continue
                        if (next_x, next_y) in seen or pixels[next_x, next_y] <= 0:
                            continue
                        seen.add((next_x, next_y))
                        queue.append((next_x, next_y))

            if count >= 500:
                bounds.append((left, top, right + 1, bottom + 1))

    return sorted(bounds, key=lambda box: (box[1], box[0]))


def prop_bounds_from_cell(image: Image.Image, column: int, row: int) -> tuple[int, int, int, int]:
    cell_width = image.width // 3
    cell_height = image.height // 2
    cell_left = column * cell_width
    cell_top = row * cell_height
    cell = image.crop((cell_left, cell_top, cell_left + cell_width, cell_top + cell_height))
    bounds = alpha_bounds(cell, padding=0)
    left, top, right, bottom = bounds
    return cell_left + left, cell_top + top, cell_left + right, cell_top + bottom


def crop_and_resize(image: Image.Image, bounds: tuple[int, int, int, int], prop_type: str) -> tuple[Image.Image, float]:
    left, top, right, bottom = bounds
    padded = (
        max(0, left - 16),
        max(0, top - 14),
        min(image.width, right + 16),
        min(image.height, bottom + 18),
    )
    cropped = image.crop(padded)

    target_height = TARGET_HEIGHTS[prop_type]
    scale = target_height / cropped.height
    target_width = max(1, round(cropped.width * scale))
    resample = Image.Resampling.LANCZOS
    resized = cropped.resize((target_width, target_height), resample)

    alpha_bottom = (bottom - padded[1]) * scale
    anchor_y = min(0.98, max(0.86, alpha_bottom / target_height))
    return resized, round(anchor_y, 3)


def build_atlas(images: list[tuple[str, Image.Image, float]]) -> tuple[Image.Image, list[dict[str, object]]]:
    padding = 8
    atlas_width = 512
    x = padding
    y = padding
    row_height = 0
    placements: list[tuple[str, Image.Image, float, int, int]] = []

    for prop_type, image, anchor_y in images:
        if x + image.width + padding > atlas_width:
            x = padding
            y += row_height + padding
            row_height = 0
        placements.append((prop_type, image, anchor_y, x, y))
        x += image.width + padding
        row_height = max(row_height, image.height)

    atlas_height = y + row_height + padding
    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    frames: list[dict[str, object]] = []

    for prop_type, image, anchor_y, frame_x, frame_y in placements:
        atlas.alpha_composite(image, (frame_x, frame_y))
        frames.append(
            {
                "id": prop_type,
                "type": prop_type,
                "x": frame_x,
                "y": frame_y,
                "width": image.width,
                "height": image.height,
                "anchorX": 0.5,
                "anchorY": anchor_y,
                "src": f"/assest/battle/props/cropped/{prop_type}.png",
            }
        )

    return atlas, frames


def main() -> int:
    if not RAW_IMAGE.exists():
        raise FileNotFoundError(f"缺少原始生成图：{RAW_IMAGE}")

    CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    transparent = make_transparent(Image.open(RAW_IMAGE))
    cropped_images: list[tuple[str, Image.Image, float]] = []
    for prop_type, column, row in PROP_LAYOUT:
        box = prop_bounds_from_cell(transparent, column, row)
        image, anchor_y = crop_and_resize(transparent, box, prop_type)
        image.save(CROPPED_DIR / f"{prop_type}.png")
        cropped_images.append((prop_type, image, anchor_y))

    atlas, frames = build_atlas(cropped_images)
    atlas.save(ATLAS_DIR / "battle-props-atlas.png")

    manifest = {
        "atlas": "/assest/battle/props/atlas/battle-props-atlas.png",
        "frames": frames,
    }
    (ATLAS_DIR / "battle-props-atlas.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (MANIFEST_DIR / "battle-props-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 {len(frames)} 个 props，atlas 尺寸 {atlas.width}x{atlas.height}。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
