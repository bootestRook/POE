from __future__ import annotations

import json
import math
import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BATTLE_ROOT = ROOT / "assets" / "battle"
ISO_TILE_ROOT = BATTLE_ROOT / "iso_tiles"
UNIT_ROOT = BATTLE_ROOT / "units"
PROP_ROOT = BATTLE_ROOT / "props"
COMMON_MANIFEST_DIR = BATTLE_ROOT / "manifests"

ISO_TILE_W = 128
ISO_TILE_H = 64

TILE_SPECS = [
    ("iso_ground_base", "tile", (68, 86, 48), "base"),
    ("iso_ground_dark", "tile", (42, 55, 36), "dark"),
    ("iso_ground_stone", "tile", (88, 86, 76), "stone"),
    ("iso_ground_crack", "tile", (74, 66, 48), "crack"),
]

UNIT_SPECS = [
    (
        "player_adventurer_iso_idle",
        "unit",
        UNIT_ROOT / "cropped" / "player_adventurer_idle_down.png",
        UNIT_ROOT / "cropped" / "player_adventurer_iso_idle.png",
        0.5,
        0.967,
    ),
    (
        "enemy_imp_iso_idle",
        "unit",
        UNIT_ROOT / "cropped" / "enemy_imp_idle_down.png",
        UNIT_ROOT / "cropped" / "enemy_imp_iso_idle.png",
        0.5,
        0.949,
    ),
    (
        "enemy_brute_iso_idle",
        "unit",
        UNIT_ROOT / "cropped" / "enemy_brute_idle_down.png",
        UNIT_ROOT / "cropped" / "enemy_brute_iso_idle.png",
        0.5,
        0.974,
    ),
]

PROP_SPECS = [
    ("rock_small_iso", "prop", PROP_ROOT / "cropped" / "rock_small.png", PROP_ROOT / "cropped" / "rock_small_iso.png", 0.5, 0.923),
    ("rock_tall_iso", "prop", PROP_ROOT / "cropped" / "rock_tall.png", PROP_ROOT / "cropped" / "rock_tall_iso.png", 0.5, 0.959),
    ("pillar_iso", "prop", PROP_ROOT / "cropped" / "pillar.png", PROP_ROOT / "cropped" / "pillar_iso.png", 0.5, 0.96),
    ("shrine_iso", "prop", PROP_ROOT / "cropped" / "shrine.png", PROP_ROOT / "cropped" / "shrine_iso.png", 0.5, 0.958),
]


def ensure_dirs() -> None:
    for path in [
        ISO_TILE_ROOT / "raw",
        ISO_TILE_ROOT / "cropped",
        ISO_TILE_ROOT / "manifests",
        UNIT_ROOT / "raw",
        UNIT_ROOT / "cropped",
        UNIT_ROOT / "manifests",
        PROP_ROOT / "raw",
        PROP_ROOT / "cropped",
        PROP_ROOT / "manifests",
        COMMON_MANIFEST_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def clamp_channel(value: float) -> int:
    return max(0, min(255, round(value)))


def shifted_color(color: tuple[int, int, int], amount: float) -> tuple[int, int, int, int]:
    return (
        clamp_channel(color[0] + amount),
        clamp_channel(color[1] + amount),
        clamp_channel(color[2] + amount),
        255,
    )


def draw_noise(draw: ImageDraw.ImageDraw, mask: Image.Image, base_color: tuple[int, int, int], seed: int) -> None:
    rng = random.Random(seed)
    pixels = mask.load()
    for _ in range(1550):
        x = rng.randrange(0, ISO_TILE_W)
        y = rng.randrange(0, ISO_TILE_H)
        if pixels[x, y] == 0:
            continue
        radius = rng.choice((1, 1, 2, 2, 3))
        shade = rng.uniform(-26, 24)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=shifted_color(base_color, shade))


def draw_stones(draw: ImageDraw.ImageDraw, rng: random.Random) -> None:
    for _ in range(18):
        cx = rng.randrange(26, 102)
        cy = rng.randrange(17, 48)
        rx = rng.randrange(5, 12)
        ry = rng.randrange(3, 7)
        points = []
        for index in range(6):
            angle = math.tau * index / 6
            points.append((cx + math.cos(angle) * rx * rng.uniform(0.75, 1.12), cy + math.sin(angle) * ry * rng.uniform(0.75, 1.12)))
        tone = rng.randrange(78, 116)
        draw.polygon(points, fill=(tone, tone - 3, tone - 13, 210), outline=(42, 42, 36, 110))


def draw_cracks(draw: ImageDraw.ImageDraw, rng: random.Random) -> None:
    for _ in range(9):
        x = rng.randrange(30, 98)
        y = rng.randrange(18, 46)
        points = [(x, y)]
        for _segment in range(rng.randrange(2, 5)):
            x += rng.randrange(-14, 15)
            y += rng.randrange(-5, 7)
            points.append((x, y))
        draw.line(points, fill=(23, 20, 16, 150), width=rng.choice((1, 1, 2)))


def create_iso_tile(tile_id: str, base_color: tuple[int, int, int], variant: str, seed: int) -> Image.Image:
    image = Image.new("RGBA", (ISO_TILE_W, ISO_TILE_H), (0, 0, 0, 0))
    mask = Image.new("L", (ISO_TILE_W, ISO_TILE_H), 0)
    mask_draw = ImageDraw.Draw(mask)
    diamond = [(ISO_TILE_W // 2, 0), (ISO_TILE_W - 1, ISO_TILE_H // 2), (ISO_TILE_W // 2, ISO_TILE_H - 1), (0, ISO_TILE_H // 2)]
    mask_draw.polygon(diamond, fill=255)

    top = Image.new("RGBA", image.size, (0, 0, 0, 0))
    top_draw = ImageDraw.Draw(top)
    for y in range(ISO_TILE_H):
        light = 18 - y * 0.42
        top_draw.line((0, y, ISO_TILE_W, y), fill=shifted_color(base_color, light))
    draw_noise(top_draw, mask, base_color, seed)
    rng = random.Random(seed + 19)

    if variant == "stone":
        draw_stones(top_draw, rng)
    if variant == "crack":
        draw_cracks(top_draw, rng)
        for _ in range(18):
            x = rng.randrange(12, 116)
            y = rng.randrange(10, 56)
            if mask.getpixel((x, y)) > 0:
                top_draw.ellipse((x - 2, y - 1, x + 2, y + 1), fill=(98, 84, 58, 130))
    if variant == "dark":
        top = Image.blend(top, Image.new("RGBA", image.size, (12, 18, 14, 255)), 0.24)
        top.putalpha(mask)

    top.putalpha(mask)
    image.alpha_composite(top)

    edge = ImageDraw.Draw(image)
    edge.line([(0, ISO_TILE_H // 2), (ISO_TILE_W // 2, ISO_TILE_H - 1), (ISO_TILE_W - 1, ISO_TILE_H // 2)], fill=(18, 22, 15, 155), width=2)
    edge.line([(0, ISO_TILE_H // 2), (ISO_TILE_W // 2, 0), (ISO_TILE_W - 1, ISO_TILE_H // 2)], fill=(175, 180, 128, 46), width=1)

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.polygon([(0, ISO_TILE_H // 2), (ISO_TILE_W // 2, ISO_TILE_H - 1), (ISO_TILE_W - 1, ISO_TILE_H // 2)], fill=(0, 0, 0, 38))
    image = Image.alpha_composite(image, shadow.filter(ImageFilter.GaussianBlur(0.35)))
    return image


def image_manifest_entry(asset_id: str, asset_type: str, path: Path, anchor_x: float, anchor_y: float) -> dict[str, object]:
    with Image.open(path) as image:
        width, height = image.size
    relative = "/" + path.relative_to(ROOT).as_posix()
    return {
        "id": asset_id,
        "type": asset_type,
        "path": relative,
        "width": width,
        "height": height,
        "anchorX": anchor_x,
        "anchorY": anchor_y,
    }


def copy_image(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing source image: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def write_contact_sheet(entries: list[dict[str, object]], output: Path, columns: int = 4) -> None:
    opened: list[tuple[dict[str, object], Image.Image]] = []
    for entry in entries:
        path = ROOT / str(entry["path"]).lstrip("/")
        opened.append((entry, Image.open(path).convert("RGBA")))

    if not opened:
        return

    cell_width = max(image.width for _entry, image in opened) + 42
    cell_height = max(image.height for _entry, image in opened) + 42
    rows = math.ceil(len(opened) / columns)
    sheet = Image.new("RGBA", (cell_width * columns, cell_height * rows), (24, 30, 22, 255))
    draw = ImageDraw.Draw(sheet)

    for index, (entry, image) in enumerate(opened):
        column = index % columns
        row = index // columns
        left = column * cell_width + (cell_width - image.width) // 2
        top = row * cell_height + cell_height - image.height - 18
        anchor_x = left + image.width * float(entry["anchorX"])
        anchor_y = top + image.height * float(entry["anchorY"])
        draw.ellipse((anchor_x - 22, anchor_y - 5, anchor_x + 22, anchor_y + 7), fill=(0, 0, 0, 82))
        sheet.alpha_composite(image, (left, top))
        draw.line((anchor_x, row * cell_height + 8, anchor_x, (row + 1) * cell_height - 8), fill=(220, 240, 180, 72))
        draw.line((column * cell_width + 8, anchor_y, (column + 1) * cell_width - 8, anchor_y), fill=(220, 240, 180, 72))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    for _entry, image in opened:
        image.close()


def build_tiles() -> list[dict[str, object]]:
    tile_entries: list[dict[str, object]] = []
    raw_sheet = Image.new("RGBA", (ISO_TILE_W * 2, ISO_TILE_H * 2), (0, 0, 0, 0))
    contact = Image.new("RGBA", (ISO_TILE_W * 2 + 24, ISO_TILE_H * 2 + 24), (22, 28, 20, 255))

    for index, (tile_id, tile_type, color, variant) in enumerate(TILE_SPECS):
        image = create_iso_tile(tile_id, color, variant, seed=811 + index * 47)
        cropped_path = ISO_TILE_ROOT / "cropped" / f"{tile_id}.png"
        image.save(cropped_path)

        column = index % 2
        row = index // 2
        raw_sheet.alpha_composite(image, (column * ISO_TILE_W, row * ISO_TILE_H))
        contact.alpha_composite(image, (12 + column * ISO_TILE_W, 12 + row * ISO_TILE_H))
        tile_entries.append(image_manifest_entry(tile_id, tile_type, cropped_path, 0.5, 0.0))

    raw_sheet.save(ISO_TILE_ROOT / "raw" / "iso-ground-source-sheet.png")
    contact.save(ISO_TILE_ROOT / "manifests" / "iso-tiles-qa-contact-sheet.png")
    (ISO_TILE_ROOT / "manifests" / "iso-tiles-manifest.json").write_text(
        json.dumps({"tileWidth": ISO_TILE_W, "tileHeight": ISO_TILE_H, "assets": tile_entries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return tile_entries


def build_copied_assets(specs: list[tuple[str, str, Path, Path, float, float]], manifest_path: Path, raw_source: Path, raw_target_name: str) -> list[dict[str, object]]:
    if raw_source.exists():
        copy_image(raw_source, raw_source.parent / raw_target_name)

    entries: list[dict[str, object]] = []
    for asset_id, asset_type, source, target, anchor_x, anchor_y in specs:
        copy_image(source, target)
        entries.append(image_manifest_entry(asset_id, asset_type, target, anchor_x, anchor_y))

    manifest_path.write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def write_common_manifest(tiles: list[dict[str, object]], units: list[dict[str, object]], props: list[dict[str, object]]) -> None:
    payload = {
        "projection": {
            "kind": "dimetric",
            "isoTileWidth": ISO_TILE_W,
            "isoTileHeight": ISO_TILE_H,
            "worldTileSize": 64,
        },
        "assets": tiles + units + props,
    }
    (COMMON_MANIFEST_DIR / "iso-battle-assets-manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    ensure_dirs()
    tiles = build_tiles()
    units = build_copied_assets(
        UNIT_SPECS,
        UNIT_ROOT / "manifests" / "iso-units-manifest.json",
        UNIT_ROOT / "raw" / "unit-sprites-generated.png",
        "iso-units-source.png",
    )
    props = build_copied_assets(
        PROP_SPECS,
        PROP_ROOT / "manifests" / "iso-props-manifest.json",
        PROP_ROOT / "raw" / "battle-props-sheet-generated.png",
        "iso-props-source.png",
    )
    write_contact_sheet(units, UNIT_ROOT / "manifests" / "iso-units-qa-contact-sheet.png", columns=3)
    write_contact_sheet(props, PROP_ROOT / "manifests" / "iso-props-qa-contact-sheet.png", columns=4)
    write_common_manifest(tiles, units, props)
    print(f"生成 {len(tiles)} 个菱形地块、{len(units)} 个单位 sprite、{len(props)} 个场景 props。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
