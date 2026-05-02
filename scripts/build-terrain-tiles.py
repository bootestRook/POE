from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance


ROOT = Path(__file__).resolve().parents[1]
TILE_ROOT = ROOT / "assets" / "battle" / "tiles"
RAW_IMAGE = TILE_ROOT / "raw" / "terrain-tiles-generated.png"
CROPPED_DIR = TILE_ROOT / "cropped"
MANIFEST_DIR = TILE_ROOT / "manifest"

TILE_LAYOUT = [
    ("ground_grass_base", "grass", 0, 0),
    ("ground_grass_dark", "grass_dark", 1, 0),
    ("ground_dirt_patch", "dirt_patch", 0, 1),
    ("ground_stone_patch", "stone_patch", 1, 1),
]

TILE_SIZE = 128


def normalize_tile(tile: Image.Image) -> Image.Image:
    resized = tile.convert("RGB").resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS)
    softened = ImageEnhance.Contrast(resized).enhance(0.92)
    softened = ImageEnhance.Color(softened).enhance(0.96)
    return softened.convert("RGBA")


def crop_tile(source: Image.Image, column: int, row: int) -> Image.Image:
    cell_width = source.width // 2
    cell_height = source.height // 2
    left = column * cell_width
    top = row * cell_height
    right = source.width if column == 1 else left + cell_width
    bottom = source.height if row == 1 else top + cell_height
    return source.crop((left, top, right, bottom))


def write_contact_sheet(images: list[Image.Image]) -> None:
    padding = 8
    sheet = Image.new("RGBA", (TILE_SIZE * 2 + padding, TILE_SIZE * 2 + padding), (20, 24, 18, 255))
    draw = ImageDraw.Draw(sheet)

    for index, image in enumerate(images):
        column = index % 2
        row = index // 2
        left = column * (TILE_SIZE + padding)
        top = row * (TILE_SIZE + padding)
        sheet.alpha_composite(image, (left, top))
        draw.rectangle((left, top, left + TILE_SIZE - 1, top + TILE_SIZE - 1), outline=(255, 255, 255, 24))

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(MANIFEST_DIR / "tiles-qa-contact-sheet.png")


def main() -> int:
    if not RAW_IMAGE.exists():
        raise FileNotFoundError(f"缺少原始地面生成图：{RAW_IMAGE}")

    CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    source = Image.open(RAW_IMAGE)
    frames: list[dict[str, object]] = []
    contact_images: list[Image.Image] = []

    for tile_id, terrain_kind, column, row in TILE_LAYOUT:
        image = normalize_tile(crop_tile(source, column, row))
        image.save(CROPPED_DIR / f"{tile_id}.png")
        contact_images.append(image)
        frames.append(
            {
                "id": tile_id,
                "terrainKind": terrain_kind,
                "width": TILE_SIZE,
                "height": TILE_SIZE,
                "src": f"/assets/battle/tiles/cropped/{tile_id}.png",
            }
        )

    manifest = {"tileSize": TILE_SIZE, "tiles": frames}
    (MANIFEST_DIR / "battle-tiles-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(contact_images)

    print(f"已生成 {len(frames)} 个地面 tile，单块尺寸 {TILE_SIZE}x{TILE_SIZE}。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
