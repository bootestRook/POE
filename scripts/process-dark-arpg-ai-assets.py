from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
BATTLE_ROOT = ROOT / "assest" / "battle"
TILE_ROOT = BATTLE_ROOT / "tiles"
EDGE_ROOT = BATTLE_ROOT / "edges"
PROP_ROOT = BATTLE_ROOT / "props"
UNIT_ROOT = BATTLE_ROOT / "units"
COMMON_MANIFEST_DIR = BATTLE_ROOT / "manifests"

UNIT_SOURCE = UNIT_ROOT / "raw" / "dark-arpg-units-ai-source.png"
PROP_SOURCE = PROP_ROOT / "raw" / "dark-arpg-props-ai-source.png"
TERRAIN_SOURCE = TILE_ROOT / "raw" / "dark-arpg-terrain-edges-ai-source.png"

GROUND_IDS = ["ground_base", "ground_dark", "ground_cracked", "ground_stone", "ground_ritual", "ground_dirt"]
EDGE_IDS = [
    "edge_cliff_n",
    "edge_cliff_s",
    "edge_cliff_e",
    "edge_cliff_w",
    "edge_cliff_inner_corner",
    "edge_cliff_outer_corner",
    "edge_lava_border",
    "edge_void_border",
]
UNIT_SPECS = [
    ("player_whitehair_girl_idle", 112, 0.5, 0.956),
    ("enemy_imp_idle", 88, 0.5, 0.948),
    ("enemy_brute_idle", 138, 0.5, 0.968),
]
PROP_SPECS = [
    ("prop_shrine", 164, 0.5, 0.956),
    ("prop_broken_pillar", 142, 0.5, 0.952),
    ("prop_stone_pillar", 174, 0.5, 0.958),
    ("prop_rock_cluster_small", 76, 0.5, 0.918),
    ("prop_rock_cluster_tall", 152, 0.5, 0.956),
    ("prop_dead_branches", 108, 0.5, 0.928),
    ("prop_skull_pile", 78, 0.5, 0.91),
    ("prop_brazier", 120, 0.5, 0.948),
    ("prop_bone_altar", 120, 0.5, 0.94),
    ("prop_ruined_gate", 174, 0.5, 0.958),
]


def is_key_pixel(red: int, green: int, blue: int, alpha: int) -> bool:
    if alpha == 0:
        return True
    return green > 110 and green > red * 1.35 and green > blue * 1.35


def make_transparent(source: Image.Image) -> Image.Image:
    image = source.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if is_key_pixel(red, green, blue, alpha):
                pixels[x, y] = (0, 0, 0, 0)
                continue
            dominant = max(red, blue)
            if green > dominant + 14:
                pixels[x, y] = (red, min(green, dominant + 8), blue, alpha)
    return image


def padded_bounds(image: Image.Image, padding: int) -> tuple[int, int, int, int]:
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("empty alpha crop")
    left, top, right, bottom = bounds
    return max(0, left - padding), max(0, top - padding), min(image.width, right + padding), min(image.height, bottom + padding)


def alpha_components(image: Image.Image) -> list[tuple[int, int, int, int, int]]:
    alpha = image.getchannel("A")
    pixels = alpha.load()
    width, height = image.size
    seen: set[tuple[int, int]] = set()
    components: list[tuple[int, int, int, int, int]] = []
    for y in range(height):
        for x in range(width):
            if (x, y) in seen or pixels[x, y] <= 12:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            left = right = x
            top = bottom = y
            count = 0
            while stack:
                cx, cy = stack.pop()
                count += 1
                left = min(left, cx)
                right = max(right, cx)
                top = min(top, cy)
                bottom = max(bottom, cy)
                for nx in (cx - 1, cx, cx + 1):
                    for ny in (cy - 1, cy, cy + 1):
                        if nx < 0 or ny < 0 or nx >= width or ny >= height:
                            continue
                        if (nx, ny) in seen or pixels[nx, ny] <= 12:
                            continue
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            components.append((left, top, right + 1, bottom + 1, count))
    return components


def filter_components(image: Image.Image, mode: str) -> Image.Image:
    components = alpha_components(image)
    if not components:
        return image
    largest = max(component[4] for component in components)
    width, height = image.size
    keep: list[tuple[int, int, int, int, int]] = []
    for component in components:
        left, top, right, bottom, area = component
        cx = (left + right) / 2 / width
        cy = (top + bottom) / 2 / height
        if mode == "single":
            if area == largest:
                keep.append(component)
        elif mode == "largest":
            if area >= largest * 0.08 and 0.03 <= cx <= 0.97:
                keep.append(component)
        else:
            if area >= max(20, largest * 0.012) and 0.07 <= cx <= 0.93 and 0.02 <= cy <= 0.98:
                keep.append(component)

    cleaned = Image.new("RGBA", image.size, (0, 0, 0, 0))
    for left, top, right, bottom, _area in keep:
        cleaned.alpha_composite(image.crop((left, top, right, bottom)), (left, top))
    return cleaned


def resize_to_height(image: Image.Image, target_height: int) -> Image.Image:
    scale = target_height / image.height
    target_width = max(1, round(image.width * scale))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def resize_to_width(image: Image.Image, target_width: int) -> Image.Image:
    scale = target_width / image.width
    target_height = max(1, round(image.height * scale))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def crop_cell(source: Image.Image, left: int, top: int, right: int, bottom: int, padding: int = 10, filter_mode: str = "center") -> Image.Image:
    transparent = make_transparent(source.crop((left, top, right, bottom)))
    transparent = filter_components(transparent, filter_mode)
    return transparent.crop(padded_bounds(transparent, padding))


def manifest_entry(asset_id: str, asset_type: str, path: Path, anchor_x: float, anchor_y: float) -> dict[str, object]:
    with Image.open(path) as image:
        width, height = image.size
    return {
        "id": asset_id,
        "type": asset_type,
        "path": "/" + path.relative_to(ROOT).as_posix(),
        "width": width,
        "height": height,
        "anchorX": anchor_x,
        "anchorY": anchor_y,
    }


def write_contact_sheet(entries: list[dict[str, object]], output: Path, columns: int) -> None:
    images: list[tuple[dict[str, object], Image.Image]] = []
    for entry in entries:
        images.append((entry, Image.open(ROOT / str(entry["path"]).lstrip("/")).convert("RGBA")))
    cell_width = max(image.width for _entry, image in images) + 38
    cell_height = max(image.height for _entry, image in images) + 38
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGBA", (cell_width * columns, cell_height * rows), (25, 26, 24, 255))
    draw = ImageDraw.Draw(sheet)
    for index, (entry, image) in enumerate(images):
        col = index % columns
        row = index // columns
        left = col * cell_width + (cell_width - image.width) // 2
        top = row * cell_height + cell_height - image.height - 16
        anchor_x = left + image.width * float(entry["anchorX"])
        anchor_y = top + image.height * float(entry["anchorY"])
        if float(entry["anchorY"]) > 0:
            draw.ellipse((anchor_x - 24, anchor_y - 5, anchor_x + 24, anchor_y + 7), fill=(0, 0, 0, 85))
        sheet.alpha_composite(image, (left, top))
        draw.line((anchor_x, row * cell_height + 8, anchor_x, (row + 1) * cell_height - 8), fill=(226, 218, 168, 72))
        draw.line((col * cell_width + 8, anchor_y, (col + 1) * cell_width - 8, anchor_y), fill=(226, 218, 168, 72))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    for _entry, image in images:
        image.close()


def process_units() -> list[dict[str, object]]:
    source = Image.open(UNIT_SOURCE)
    output_dir = UNIT_ROOT / "cropped"
    entries: list[dict[str, object]] = []
    cell_width = source.width / len(UNIT_SPECS)
    for index, (asset_id, target_height, anchor_x, anchor_y) in enumerate(UNIT_SPECS):
        cell = crop_cell(source, round(index * cell_width), 0, round((index + 1) * cell_width), source.height, padding=18, filter_mode="single")
        image = resize_to_height(cell, target_height)
        output = output_dir / f"{asset_id}.png"
        image.save(output)
        entries.append(manifest_entry(asset_id, "unit", output, anchor_x, anchor_y))
    (UNIT_ROOT / "manifests" / "dark-arpg-units-manifest.json").write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(entries, UNIT_ROOT / "manifests" / "dark-arpg-units-contact-sheet.png", columns=3)
    return entries


def process_props() -> list[dict[str, object]]:
    source = Image.open(PROP_SOURCE)
    output_dir = PROP_ROOT / "cropped"
    entries: list[dict[str, object]] = []
    cell_width = source.width / 5
    cell_height = source.height / 2
    for index, (asset_id, target_height, anchor_x, anchor_y) in enumerate(PROP_SPECS):
        row = index // 5
        col = index % 5
        cell = crop_cell(source, round(col * cell_width), round(row * cell_height), round((col + 1) * cell_width), round((row + 1) * cell_height), padding=16, filter_mode="center")
        image = resize_to_height(cell, target_height)
        output = output_dir / f"{asset_id}.png"
        image.save(output)
        entries.append(manifest_entry(asset_id, "prop", output, anchor_x, anchor_y))
    (PROP_ROOT / "manifests" / "dark-arpg-props-manifest.json").write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(entries, PROP_ROOT / "manifests" / "dark-arpg-props-contact-sheet.png", columns=5)
    return entries


def process_terrain() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    source = Image.open(TERRAIN_SOURCE)
    tile_entries: list[dict[str, object]] = []
    edge_entries: list[dict[str, object]] = []
    top_height = round(source.height * 0.43)
    tile_cell_width = source.width / 6
    for index, asset_id in enumerate(GROUND_IDS):
        cell = crop_cell(source, round(index * tile_cell_width), 0, round((index + 1) * tile_cell_width), top_height, padding=8, filter_mode="largest")
        image = resize_to_width(cell, 128)
        output = TILE_ROOT / "cropped" / f"{asset_id}.png"
        image.save(output)
        tile_entries.append(manifest_entry(asset_id, "tile", output, 0.5, 0.0))

    edge_cell_width = source.width / 8
    for index, asset_id in enumerate(EDGE_IDS):
        cell = crop_cell(source, round(index * edge_cell_width), top_height, round((index + 1) * edge_cell_width), source.height, padding=8, filter_mode="largest")
        image = resize_to_width(cell, 128)
        output = EDGE_ROOT / "cropped" / f"{asset_id}.png"
        image.save(output)
        edge_entries.append(manifest_entry(asset_id, "edge", output, 0.5, 0.0))

    (TILE_ROOT / "manifests" / "dark-arpg-tiles-manifest.json").write_text(json.dumps({"assets": tile_entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    (EDGE_ROOT / "manifests" / "dark-arpg-edges-manifest.json").write_text(json.dumps({"assets": edge_entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(tile_entries, TILE_ROOT / "manifests" / "dark-arpg-tiles-contact-sheet.png", columns=3)
    write_contact_sheet(edge_entries, EDGE_ROOT / "manifests" / "dark-arpg-edges-contact-sheet.png", columns=4)
    return tile_entries, edge_entries


def main() -> int:
    tiles, edges = process_terrain()
    units = process_units()
    props = process_props()
    manifest = {
        "style": "AI generated hand-drawn dark cartoon dimetric ARPG",
        "projection": {
            "kind": "dimetric",
            "isoTileWidth": 128,
            "isoTileHeight": 64,
            "worldTileSize": 64,
        },
        "assets": tiles + edges + units + props,
    }
    COMMON_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    (COMMON_MANIFEST_DIR / "dark-arpg-battle-assets-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"processed {len(tiles)} tiles, {len(edges)} edges, {len(props)} props, {len(units)} units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
