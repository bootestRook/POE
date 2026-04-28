from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
UNIT_ROOT = ROOT / "assest" / "battle" / "units"
RAW_IMAGE = UNIT_ROOT / "raw" / "unit-sprites-generated.png"
CROPPED_DIR = UNIT_ROOT / "cropped"
ATLAS_DIR = UNIT_ROOT / "atlas"
MANIFEST_DIR = UNIT_ROOT / "manifest"

UNIT_LAYOUT = [
    {
        "id": "player_adventurer_idle_down",
        "unitType": "player_adventurer",
        "direction": "down",
        "column": 0,
        "targetHeight": 92,
    },
    {
        "id": "enemy_imp_idle_down",
        "unitType": "enemy_imp",
        "direction": "down",
        "column": 1,
        "targetHeight": 78,
    },
    {
        "id": "enemy_brute_idle_down",
        "unitType": "enemy_brute",
        "direction": "down",
        "column": 2,
        "targetHeight": 116,
    },
]


def is_key_pixel(pixel: tuple[int, int, int, int]) -> bool:
    red, green, blue, alpha = pixel
    if alpha == 0:
        return True
    return green >= 150 and green >= max(red, blue) * 1.65 and red <= 130 and blue <= 130


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
            if green > dominant + 20:
                if green > dominant * 1.65 and green > 145:
                    pixels[x, y] = (0, 0, 0, 0)
                else:
                    pixels[x, y] = (red, min(green, dominant + 12), blue, alpha_value)

    return rgba


def remove_small_alpha_components(image: Image.Image, min_area: int = 700) -> Image.Image:
    rgba = image.copy()
    alpha = rgba.getchannel("A")
    alpha_pixels = alpha.load()
    width, height = rgba.size
    seen: set[tuple[int, int]] = set()
    remove: list[tuple[int, int]] = []

    for y in range(height):
        for x in range(width):
            if (x, y) in seen or alpha_pixels[x, y] == 0:
                continue

            queue = deque([(x, y)])
            seen.add((x, y))
            component: list[tuple[int, int]] = []

            while queue:
                current_x, current_y = queue.popleft()
                component.append((current_x, current_y))

                for next_x in (current_x - 1, current_x, current_x + 1):
                    for next_y in (current_y - 1, current_y, current_y + 1):
                        if next_x < 0 or next_y < 0 or next_x >= width or next_y >= height:
                            continue
                        if (next_x, next_y) in seen or alpha_pixels[next_x, next_y] == 0:
                            continue
                        seen.add((next_x, next_y))
                        queue.append((next_x, next_y))

            if len(component) < min_area:
                remove.extend(component)

    pixels = rgba.load()
    for x, y in remove:
        pixels[x, y] = (0, 0, 0, 0)

    return rgba


def make_transparent(source: Image.Image) -> Image.Image:
    rgba = source.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size

    for y in range(height):
        for x in range(width):
            if is_key_pixel(pixels[x, y]):
                pixels[x, y] = (0, 0, 0, 0)

    return remove_small_alpha_components(despill_green_edges(rgba))


def alpha_bounds(image: Image.Image, padding: int = 18) -> tuple[int, int, int, int]:
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("没有找到可裁剪的单位像素。")
    left, top, right, bottom = bounds
    return (
        max(0, left - padding),
        max(0, top - padding),
        min(image.width, right + padding),
        min(image.height, bottom + padding + 8),
    )


def unit_bounds_from_cell(image: Image.Image, column: int) -> tuple[int, int, int, int]:
    cell_width = image.width // len(UNIT_LAYOUT)
    cell_left = column * cell_width
    cell_right = image.width if column == len(UNIT_LAYOUT) - 1 else cell_left + cell_width
    cell = image.crop((cell_left, 0, cell_right, image.height))
    left, top, right, bottom = alpha_bounds(cell, padding=20)
    return cell_left + left, top, cell_left + right, bottom


def crop_and_resize(image: Image.Image, bounds: tuple[int, int, int, int], target_height: int) -> tuple[Image.Image, float]:
    left, top, right, bottom = bounds
    cropped = image.crop((left, top, right, bottom))
    if cropped.getchannel("A").getbbox() is None:
        raise ValueError("裁剪后的单位没有可见像素。")

    scale = target_height / cropped.height
    target_width = max(1, round(cropped.width * scale))
    resized = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
    resized = remove_small_alpha_components(resized, min_area=160)
    final_bounds = alpha_bounds(resized, padding=6)
    finalized = resized.crop(final_bounds)
    final_alpha_bounds = finalized.getchannel("A").getbbox()
    if final_alpha_bounds is None:
        raise ValueError("最终裁剪后的单位没有可见像素。")

    anchor_y = min(0.98, max(0.88, final_alpha_bounds[3] / finalized.height))
    return finalized, round(anchor_y, 3)


def build_atlas(images: list[tuple[dict[str, object], Image.Image, float]]) -> tuple[Image.Image, list[dict[str, object]]]:
    padding = 10
    atlas_width = 384
    x = padding
    y = padding
    row_height = 0
    placements: list[tuple[dict[str, object], Image.Image, float, int, int]] = []

    for unit, image, anchor_y in images:
        if x + image.width + padding > atlas_width:
            x = padding
            y += row_height + padding
            row_height = 0
        placements.append((unit, image, anchor_y, x, y))
        x += image.width + padding
        row_height = max(row_height, image.height)

    atlas_height = y + row_height + padding
    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    frames: list[dict[str, object]] = []

    for unit, image, anchor_y, frame_x, frame_y in placements:
        atlas.alpha_composite(image, (frame_x, frame_y))
        unit_id = str(unit["id"])
        frames.append(
            {
                "id": unit_id,
                "unitType": unit["unitType"],
                "direction": unit["direction"],
                "x": frame_x,
                "y": frame_y,
                "width": image.width,
                "height": image.height,
                "anchorX": 0.5,
                "anchorY": anchor_y,
                "src": f"/assest/battle/units/cropped/{unit_id}.png",
                "recommendedRenderWidth": image.width,
                "recommendedRenderHeight": image.height,
            }
        )

    return atlas, frames


def write_contact_sheet(images: list[Image.Image]) -> None:
    tile_width = max(image.width for image in images) + 28
    tile_height = max(image.height for image in images) + 28
    sheet = Image.new("RGBA", (tile_width * len(images), tile_height), (28, 30, 25, 255))
    draw = ImageDraw.Draw(sheet)

    for index, image in enumerate(images):
        left = index * tile_width + (tile_width - image.width) // 2
        top = tile_height - image.height - 14
        shadow_y = top + int(image.height * 0.94)
        draw.ellipse((left + image.width * 0.24, shadow_y - 5, left + image.width * 0.76, shadow_y + 9), fill=(0, 0, 0, 95))
        sheet.alpha_composite(image, (left, top))

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(MANIFEST_DIR / "units-qa-contact-sheet.png")


def main() -> int:
    if not RAW_IMAGE.exists():
        raise FileNotFoundError(f"缺少原始单位生成图：{RAW_IMAGE}")

    CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    transparent = make_transparent(Image.open(RAW_IMAGE))
    processed: list[tuple[dict[str, object], Image.Image, float]] = []
    contact_images: list[Image.Image] = []

    for unit in UNIT_LAYOUT:
        box = unit_bounds_from_cell(transparent, int(unit["column"]))
        image, anchor_y = crop_and_resize(transparent, box, int(unit["targetHeight"]))
        image.save(CROPPED_DIR / f"{unit['id']}.png")
        processed.append((unit, image, anchor_y))
        contact_images.append(image)

    atlas, frames = build_atlas(processed)
    atlas.save(ATLAS_DIR / "battle-units-atlas.png")

    manifest = {
        "atlas": "/assest/battle/units/atlas/battle-units-atlas.png",
        "frames": frames,
    }
    (ATLAS_DIR / "battle-units-atlas.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (MANIFEST_DIR / "battle-units-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(contact_images)

    print(f"已生成 {len(frames)} 个单位 sprite，atlas 尺寸 {atlas.width}x{atlas.height}。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
