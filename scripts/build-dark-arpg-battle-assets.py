from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BATTLE_ROOT = ROOT / "assest" / "battle"
TILE_ROOT = BATTLE_ROOT / "tiles"
EDGE_ROOT = BATTLE_ROOT / "edges"
PROP_ROOT = BATTLE_ROOT / "props"
UNIT_ROOT = BATTLE_ROOT / "units"
COMMON_MANIFEST_DIR = BATTLE_ROOT / "manifests"

ISO_TILE_W = 128
ISO_TILE_H = 64
EDGE_H = 104

GROUND_SPECS = [
    ("ground_base", (94, 71, 55), "base"),
    ("ground_dark", (58, 49, 48), "dark"),
    ("ground_cracked", (82, 58, 50), "cracked"),
    ("ground_stone", (88, 78, 72), "stone"),
    ("ground_ritual", (94, 63, 55), "ritual"),
    ("ground_dirt", (108, 74, 54), "dirt"),
]

EDGE_SPECS = [
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
    ("player_whitehair_girl_idle", "unit", (82, 112), 0.5, 0.955),
    ("enemy_imp_idle", "unit", (82, 86), 0.5, 0.948),
    ("enemy_brute_idle", "unit", (124, 138), 0.5, 0.968),
]

PROP_SPECS = [
    ("prop_shrine", "prop", (136, 164), 0.5, 0.956),
    ("prop_broken_pillar", "prop", (112, 142), 0.5, 0.952),
    ("prop_stone_pillar", "prop", (108, 174), 0.5, 0.958),
    ("prop_rock_cluster_small", "prop", (96, 76), 0.5, 0.918),
    ("prop_rock_cluster_tall", "prop", (116, 152), 0.5, 0.956),
    ("prop_dead_branches", "prop", (132, 108), 0.5, 0.928),
    ("prop_skull_pile", "prop", (104, 78), 0.5, 0.91),
    ("prop_brazier", "prop", (96, 120), 0.5, 0.948),
    ("prop_bone_altar", "prop", (136, 120), 0.5, 0.94),
    ("prop_ruined_gate", "prop", (154, 174), 0.5, 0.958),
]


def ensure_dirs() -> None:
    for root in (TILE_ROOT, EDGE_ROOT, PROP_ROOT, UNIT_ROOT):
        for name in ("raw", "cropped", "manifests"):
            (root / name).mkdir(parents=True, exist_ok=True)
    COMMON_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)


def rgba(color: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def shift(color: tuple[int, int, int], amount: int, alpha: int = 255) -> tuple[int, int, int, int]:
    return tuple(max(0, min(255, channel + amount)) for channel in color) + (alpha,)


def jittered(points: list[tuple[float, float]], rng: random.Random, amount: float = 1.4) -> list[tuple[float, float]]:
    return [(x + rng.uniform(-amount, amount), y + rng.uniform(-amount, amount)) for x, y in points]


def diamond_mask(size: tuple[int, int] = (ISO_TILE_W, ISO_TILE_H)) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon([(width / 2, 0), (width - 1, height / 2), (width / 2, height - 1), (0, height / 2)], fill=255)
    return mask


def draw_scratches(draw: ImageDraw.ImageDraw, rng: random.Random, color: tuple[int, int, int, int], count: int) -> None:
    for _ in range(count):
        x = rng.randrange(20, 108)
        y = rng.randrange(12, 54)
        length = rng.randrange(6, 18)
        angle = rng.uniform(-0.8, 0.8)
        draw.line((x, y, x + math.cos(angle) * length, y + math.sin(angle) * length), fill=color, width=1)


def draw_pebbles(draw: ImageDraw.ImageDraw, rng: random.Random, mask: Image.Image, count: int, palette: list[tuple[int, int, int]]) -> None:
    pixels = mask.load()
    for _ in range(count):
        x = rng.randrange(8, ISO_TILE_W - 8)
        y = rng.randrange(5, ISO_TILE_H - 5)
        if pixels[x, y] == 0:
            continue
        rx = rng.randrange(2, 7)
        ry = rng.randrange(1, 4)
        color = rgba(rng.choice(palette), rng.randrange(120, 220))
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color, outline=(24, 19, 18, 70))


def create_ground_tile(asset_id: str, base: tuple[int, int, int], variant: str, seed: int) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", (ISO_TILE_W, ISO_TILE_H), (0, 0, 0, 0))
    mask = diamond_mask()
    paint = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(paint)

    for y in range(ISO_TILE_H):
        amount = 18 - int(y * 0.7)
        draw.line((0, y, ISO_TILE_W, y), fill=shift(base, amount))

    draw_pebbles(draw, rng, mask, 150, [shift(base, -16)[:3], shift(base, 10)[:3], (63, 48, 46), (127, 86, 62)])

    if variant == "stone":
        for _ in range(22):
            cx = rng.randrange(18, 110)
            cy = rng.randrange(13, 52)
            rx = rng.randrange(6, 14)
            ry = rng.randrange(3, 7)
            pts = [(cx + math.cos(math.tau * i / 6) * rx * rng.uniform(0.7, 1.2), cy + math.sin(math.tau * i / 6) * ry * rng.uniform(0.7, 1.2)) for i in range(6)]
            tone = rng.randrange(83, 119)
            draw.polygon(pts, fill=(tone, tone - 9, tone - 14, 210), outline=(34, 27, 26, 130))
    elif variant == "cracked":
        draw_scratches(draw, rng, (30, 22, 20, 180), 18)
        for _ in range(5):
            x = rng.randrange(24, 104)
            y = rng.randrange(18, 48)
            pts = [(x, y)]
            for _seg in range(4):
                x += rng.randrange(-12, 14)
                y += rng.randrange(-5, 7)
                pts.append((x, y))
            draw.line(pts, fill=(25, 18, 17, 210), width=2)
    elif variant == "ritual":
        cx, cy = ISO_TILE_W / 2, ISO_TILE_H / 2
        draw.ellipse((cx - 34, cy - 15, cx + 34, cy + 15), outline=(122, 50, 44, 190), width=3)
        draw.ellipse((cx - 22, cy - 10, cx + 22, cy + 10), outline=(188, 84, 54, 130), width=2)
        for i in range(8):
            a = math.tau * i / 8
            draw.line((cx + math.cos(a) * 16, cy + math.sin(a) * 7, cx + math.cos(a) * 31, cy + math.sin(a) * 13), fill=(165, 67, 47, 160), width=1)
    elif variant == "dark":
        overlay = Image.new("RGBA", image.size, (34, 28, 35, 95))
        paint = Image.alpha_composite(paint, overlay)
    elif variant == "dirt":
        for _ in range(24):
            x = rng.randrange(12, 116)
            y = rng.randrange(10, 56)
            draw.arc((x - 10, y - 5, x + 10, y + 5), start=rng.randrange(0, 160), end=rng.randrange(200, 360), fill=(64, 37, 30, 90), width=1)

    paint.putalpha(mask)
    image.alpha_composite(paint)
    edge = ImageDraw.Draw(image)
    diamond = [(ISO_TILE_W / 2, 1), (ISO_TILE_W - 2, ISO_TILE_H / 2), (ISO_TILE_W / 2, ISO_TILE_H - 2), (1, ISO_TILE_H / 2)]
    edge.line(diamond + [diamond[0]], fill=(28, 20, 19, 165), width=2)
    edge.line([diamond[3], diamond[0], diamond[1]], fill=(188, 147, 105, 48), width=1)
    return image


def draw_cliff_wall(draw: ImageDraw.ImageDraw, rng: random.Random, side: str, lava: bool = False, void: bool = False) -> None:
    rock = (58, 48, 49)
    dark = (25, 21, 24)
    glow = (202, 69, 39)
    if side in ("s", "corner", "lava", "void"):
        top = [(0, 32), (64, 64), (127, 32)]
        bottom = [(7, 32), (64, 101), (121, 32)]
        fill = (35, 30, 32, 225) if void else (61, 42, 37, 238)
        draw.polygon(bottom, fill=fill, outline=(22, 17, 18, 210))
        for i in range(11):
            x = 12 + i * 10 + rng.randrange(-3, 4)
            y0 = 40 + rng.randrange(-4, 6)
            y1 = 82 + rng.randrange(-7, 9)
            draw.line((x, y0, x + rng.randrange(-7, 8), y1), fill=(22, 17, 18, 110), width=2)
        if lava:
            draw.polygon([(17, 58), (64, 99), (111, 58), (100, 77), (64, 94), (27, 76)], fill=(139, 37, 28, 170))
            draw.line((26, 72, 47, 80, 64, 93, 90, 78, 104, 68), fill=(242, 101, 45, 170), width=2)
        if void:
            draw.ellipse((14, 62, 114, 102), fill=(5, 4, 8, 95))
        draw.line(top, fill=(119, 80, 65, 95), width=2)
    if side in ("n", "e", "w", "corner"):
        for _ in range(10):
            x = rng.randrange(12, 116)
            y = rng.randrange(8, 42)
            h = rng.randrange(9, 23)
            pts = [(x, y - h), (x + rng.randrange(7, 15), y), (x, y + rng.randrange(3, 8)), (x - rng.randrange(7, 14), y)]
            draw.polygon(pts, fill=rgba(rock, 230), outline=rgba(dark, 210))
            draw.line((x - 2, y - h + 4, x + 2, y + 2), fill=(119, 96, 82, 80), width=1)


def create_edge_tile(asset_id: str, seed: int) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", (ISO_TILE_W, EDGE_H), (0, 0, 0, 0))
    top = create_ground_tile(asset_id, (67, 48, 43), "dark", seed + 3)
    image.alpha_composite(top, (0, 0))
    draw = ImageDraw.Draw(image)
    if asset_id.endswith("_n"):
        draw_cliff_wall(draw, rng, "n")
    elif asset_id.endswith("_s"):
        draw_cliff_wall(draw, rng, "s")
    elif asset_id.endswith("_e"):
        draw_cliff_wall(draw, rng, "e")
        draw.line((64, 1, 126, 32, 64, 64), fill=(27, 21, 22, 185), width=3)
    elif asset_id.endswith("_w"):
        draw_cliff_wall(draw, rng, "w")
        draw.line((64, 1, 2, 32, 64, 64), fill=(27, 21, 22, 185), width=3)
    elif asset_id.endswith("inner_corner"):
        draw_cliff_wall(draw, rng, "corner")
        draw.arc((24, 10, 106, 74), 170, 302, fill=(33, 25, 25, 210), width=4)
    elif asset_id.endswith("outer_corner"):
        draw_cliff_wall(draw, rng, "s")
        draw.polygon([(1, 32), (64, 64), (14, 73)], fill=(31, 24, 25, 190))
        draw.polygon([(127, 32), (64, 64), (112, 73)], fill=(31, 24, 25, 190))
    elif asset_id.endswith("lava_border"):
        draw_cliff_wall(draw, rng, "lava", lava=True)
    elif asset_id.endswith("void_border"):
        draw_cliff_wall(draw, rng, "void", void=True)
    return image


def draw_shadow(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.ellipse(box, fill=(0, 0, 0, 88))


def draw_rock(draw: ImageDraw.ImageDraw, rng: random.Random, cx: int, cy: int, rx: int, ry: int, color: tuple[int, int, int]) -> None:
    pts = [(cx + math.cos(math.tau * i / 7) * rx * rng.uniform(0.7, 1.18), cy + math.sin(math.tau * i / 7) * ry * rng.uniform(0.75, 1.16)) for i in range(7)]
    draw.polygon(pts, fill=rgba(color, 245), outline=(25, 20, 20, 235))
    draw.line((cx - rx * 0.35, cy - ry * 0.5, cx + rx * 0.25, cy + ry * 0.1), fill=(160, 132, 111, 90), width=2)


def draw_flame(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    draw.polygon([(cx, cy - 28 * scale), (cx + 14 * scale, cy - 4 * scale), (cx + 3 * scale, cy + 9 * scale), (cx - 13 * scale, cy - 3 * scale)], fill=(203, 58, 34, 230))
    draw.polygon([(cx + 1 * scale, cy - 19 * scale), (cx + 8 * scale, cy - 2 * scale), (cx, cy + 5 * scale), (cx - 7 * scale, cy - 1 * scale)], fill=(255, 151, 55, 235))
    draw.polygon([(cx, cy - 11 * scale), (cx + 4 * scale, cy - 1 * scale), (cx, cy + 3 * scale), (cx - 4 * scale, cy)], fill=(255, 216, 104, 230))


def create_prop(asset_id: str, size: tuple[int, int], seed: int) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    w, h = size
    base_y = h - 11
    draw_shadow(draw, (int(w * 0.18), base_y - 8, int(w * 0.82), base_y + 8))
    stone = (91, 78, 70)
    dark = (25, 20, 20)

    if asset_id in ("prop_rock_cluster_small", "prop_rock_cluster_tall"):
        count = 6 if asset_id.endswith("small") else 9
        for i in range(count):
            cx = rng.randrange(int(w * 0.22), int(w * 0.78))
            cy = rng.randrange(int(h * 0.42), base_y)
            rx = rng.randrange(12, 25 if asset_id.endswith("small") else 31)
            ry = rng.randrange(9, 21 if asset_id.endswith("small") else 31)
            if asset_id.endswith("tall") and i < 3:
                cy -= rng.randrange(24, 56)
                ry += rng.randrange(20, 42)
            draw_rock(draw, rng, cx, cy, rx, ry, shift(stone, rng.randrange(-18, 15))[:3])
    elif asset_id in ("prop_stone_pillar", "prop_broken_pillar"):
        x0, x1 = int(w * 0.34), int(w * 0.67)
        top = 22 if asset_id == "prop_stone_pillar" else 48
        draw.polygon([(x0, top), (x1, top + 8), (x1 - 5, base_y), (x0 + 4, base_y - 6)], fill=(83, 72, 66, 245), outline=rgba(dark, 245))
        for y in range(top + 18, base_y, 24):
            draw.line((x0 + 2, y, x1 - 4, y + 5), fill=(37, 28, 27, 160), width=2)
        draw_rock(draw, rng, w // 2, top, 34, 14, (107, 94, 84))
        if asset_id == "prop_broken_pillar":
            draw.polygon([(x0 - 2, top + 5), (w // 2, top - 22), (x1 + 2, top + 3), (x1 - 7, top + 12)], fill=(72, 62, 58, 245), outline=rgba(dark, 245))
    elif asset_id == "prop_shrine":
        draw_rock(draw, rng, w // 2, base_y - 12, 48, 18, (76, 66, 61))
        draw.rectangle((w // 2 - 25, h * 0.35, w // 2 + 25, base_y - 18), fill=(69, 58, 56, 245), outline=rgba(dark, 240))
        draw.polygon([(w // 2 - 38, h * 0.37), (w // 2, h * 0.2), (w // 2 + 38, h * 0.37)], fill=(86, 75, 69, 245), outline=rgba(dark, 240))
        draw_flame(draw, w // 2, int(h * 0.62), 0.72)
    elif asset_id == "prop_brazier":
        draw_rock(draw, rng, w // 2, base_y - 11, 34, 12, (62, 52, 49))
        draw.rectangle((w // 2 - 20, base_y - 38, w // 2 + 20, base_y - 20), fill=(47, 38, 36, 250), outline=rgba(dark, 240))
        draw_flame(draw, w // 2, base_y - 39, 0.85)
    elif asset_id == "prop_dead_branches":
        for _ in range(16):
            x = rng.randrange(22, w - 22)
            y = rng.randrange(base_y - 12, base_y)
            length = rng.randrange(24, 58)
            angle = rng.uniform(-2.7, -0.45)
            x2 = x + math.cos(angle) * length
            y2 = y + math.sin(angle) * length
            draw.line((x, y, x2, y2), fill=(45, 33, 30, 235), width=rng.randrange(2, 4))
            draw.line((x2, y2, x2 + rng.randrange(-14, 15), y2 + rng.randrange(-13, 2)), fill=(36, 27, 25, 220), width=2)
    elif asset_id in ("prop_skull_pile", "prop_bone_altar"):
        for _ in range(12 if asset_id.endswith("pile") else 18):
            x = rng.randrange(20, w - 20)
            y = rng.randrange(base_y - 34, base_y - 4)
            draw.ellipse((x - 8, y - 6, x + 8, y + 7), fill=(151, 133, 108, 235), outline=rgba(dark, 210))
            draw.ellipse((x - 4, y - 1, x - 1, y + 2), fill=rgba(dark, 170))
            draw.ellipse((x + 1, y - 1, x + 4, y + 2), fill=rgba(dark, 170))
        if asset_id == "prop_bone_altar":
            draw.rectangle((w * 0.23, base_y - 56, w * 0.77, base_y - 31), fill=(68, 50, 45, 235), outline=rgba(dark, 225))
            draw_flame(draw, w // 2, base_y - 62, 0.58)
    elif asset_id == "prop_ruined_gate":
        for x in (int(w * 0.26), int(w * 0.73)):
            draw.rectangle((x - 14, h * 0.32, x + 14, base_y - 12), fill=(69, 57, 55, 245), outline=rgba(dark, 240))
            draw_rock(draw, rng, x, int(h * 0.3), 24, 13, (91, 78, 70))
        draw.polygon([(w * 0.22, h * 0.38), (w * 0.5, h * 0.24), (w * 0.78, h * 0.38), (w * 0.71, h * 0.44), (w * 0.5, h * 0.33), (w * 0.29, h * 0.44)], fill=(81, 66, 62, 245), outline=rgba(dark, 240))
        draw.polygon([(w * 0.28, h * 0.45), (w * 0.41, h * 0.49), (w * 0.41, base_y - 18), (w * 0.28, base_y - 28)], fill=(89, 26, 31, 220), outline=(31, 17, 18, 210))
        draw.polygon([(w * 0.59, h * 0.49), (w * 0.72, h * 0.45), (w * 0.72, base_y - 28), (w * 0.59, base_y - 18)], fill=(89, 26, 31, 220), outline=(31, 17, 18, 210))

    return image.filter(ImageFilter.UnsharpMask(radius=0.8, percent=95, threshold=3))


def create_unit(asset_id: str, size: tuple[int, int], seed: int) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    w, h = size
    base_y = h - 10
    draw_shadow(draw, (int(w * 0.2), base_y - 6, int(w * 0.8), base_y + 7))
    outline = (25, 18, 19, 245)

    if asset_id == "player_whitehair_girl_idle":
        cx = w // 2
        draw.line((cx - 15, base_y - 24, cx - 24, base_y - 3), fill=(42, 29, 25, 255), width=7)
        draw.line((cx + 13, base_y - 24, cx + 22, base_y - 3), fill=(42, 29, 25, 255), width=7)
        draw.polygon([(cx - 20, base_y - 58), (cx + 18, base_y - 58), (cx + 25, base_y - 24), (cx - 24, base_y - 24)], fill=(66, 42, 39, 245), outline=outline)
        draw.polygon([(cx - 19, base_y - 55), (cx - 38, base_y - 36), (cx - 31, base_y - 22), (cx - 17, base_y - 39)], fill=(56, 67, 52, 235), outline=outline)
        draw.polygon([(cx + 18, base_y - 54), (cx + 34, base_y - 38), (cx + 26, base_y - 25), (cx + 14, base_y - 39)], fill=(72, 55, 45, 235), outline=outline)
        draw.line((cx + 27, base_y - 38, cx + 43, base_y - 67), fill=(151, 137, 116, 245), width=3)
        draw.line((cx + 42, base_y - 69, cx + 47, base_y - 76), fill=(221, 210, 172, 230), width=2)
        draw.ellipse((cx - 15, base_y - 85, cx + 15, base_y - 56), fill=(165, 121, 92, 255), outline=outline)
        hair = (226, 222, 202)
        draw.pieslice((cx - 23, base_y - 93, cx + 23, base_y - 48), 190, 350, fill=rgba(hair, 255), outline=outline)
        draw.polygon([(cx - 24, base_y - 77), (cx - 10, base_y - 96), (cx + 8, base_y - 85), (cx + 20, base_y - 75), (cx + 13, base_y - 58), (cx - 20, base_y - 58)], fill=rgba(hair, 255), outline=outline)
        draw.ellipse((cx - 8, base_y - 72, cx - 4, base_y - 68), fill=(27, 20, 20, 230))
        draw.ellipse((cx + 5, base_y - 72, cx + 9, base_y - 68), fill=(27, 20, 20, 230))
        draw.line((cx - 5, base_y - 63, cx + 6, base_y - 62), fill=(94, 48, 47, 210), width=1)
        draw.line((cx - 8, base_y - 18, cx - 9, base_y - 2), fill=(42, 29, 25, 255), width=6)
        draw.line((cx + 9, base_y - 18, cx + 10, base_y - 2), fill=(42, 29, 25, 255), width=6)
    elif asset_id == "enemy_imp_idle":
        cx = w // 2
        red = (151, 50, 40)
        draw.line((cx - 18, base_y - 24, cx - 25, base_y - 4), fill=rgba(red, 250), width=8)
        draw.line((cx + 18, base_y - 24, cx + 25, base_y - 4), fill=rgba(red, 250), width=8)
        draw.ellipse((cx - 25, base_y - 61, cx + 25, base_y - 18), fill=rgba(red, 250), outline=outline)
        draw.polygon([(cx - 17, base_y - 58), (cx - 34, base_y - 73), (cx - 26, base_y - 48)], fill=(184, 80, 44, 245), outline=outline)
        draw.polygon([(cx + 17, base_y - 58), (cx + 34, base_y - 73), (cx + 26, base_y - 48)], fill=(184, 80, 44, 245), outline=outline)
        draw.ellipse((cx - 12, base_y - 47, cx - 5, base_y - 40), fill=(255, 180, 67, 245), outline=outline)
        draw.ellipse((cx + 5, base_y - 47, cx + 12, base_y - 40), fill=(255, 180, 67, 245), outline=outline)
        draw.arc((cx - 12, base_y - 39, cx + 12, base_y - 23), 10, 170, fill=outline, width=2)
        draw.line((cx - 24, base_y - 34, cx - 38, base_y - 22), fill=rgba(red, 240), width=5)
        draw.line((cx + 24, base_y - 34, cx + 38, base_y - 22), fill=rgba(red, 240), width=5)
    else:
        cx = w // 2
        skin = (128, 93, 70)
        armor = (82, 62, 61)
        draw.line((cx - 25, base_y - 44, cx - 34, base_y - 4), fill=(70, 49, 40, 255), width=15)
        draw.line((cx + 23, base_y - 44, cx + 33, base_y - 4), fill=(70, 49, 40, 255), width=15)
        draw.ellipse((cx - 40, base_y - 98, cx + 40, base_y - 28), fill=rgba(skin, 255), outline=outline)
        draw.polygon([(cx - 45, base_y - 87), (cx + 45, base_y - 83), (cx + 35, base_y - 33), (cx - 34, base_y - 34)], fill=rgba(armor, 245), outline=outline)
        draw.ellipse((cx - 27, base_y - 129, cx + 25, base_y - 83), fill=rgba(skin, 255), outline=outline)
        for sx in (-33, 33):
            draw.polygon([(cx + sx, base_y - 109), (cx + sx + (10 if sx > 0 else -10), base_y - 126), (cx + sx + (19 if sx > 0 else -19), base_y - 101)], fill=(122, 107, 90, 245), outline=outline)
        draw.ellipse((cx - 13, base_y - 108, cx - 6, base_y - 101), fill=(255, 190, 82, 235), outline=outline)
        draw.ellipse((cx + 6, base_y - 108, cx + 13, base_y - 101), fill=(255, 190, 82, 235), outline=outline)
        draw.arc((cx - 18, base_y - 101, cx + 18, base_y - 83), 15, 165, fill=outline, width=3)
        draw.line((cx - 48, base_y - 67, cx - 62, base_y - 20), fill=(72, 52, 43, 255), width=14)
        draw.line((cx + 47, base_y - 67, cx + 61, base_y - 22), fill=(72, 52, 43, 255), width=14)
        draw.line((cx + 52, base_y - 29, cx + 68, base_y - 6), fill=(57, 42, 37, 245), width=10)

    return image.filter(ImageFilter.UnsharpMask(radius=0.8, percent=100, threshold=3))


def save_sheet(images: list[tuple[str, Image.Image]], output: Path, columns: int) -> None:
    cell_w = max(image.width for _name, image in images) + 20
    cell_h = max(image.height for _name, image in images) + 20
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGBA", (cell_w * columns, cell_h * rows), (24, 25, 23, 255))
    for index, (_name, image) in enumerate(images):
        x = (index % columns) * cell_w + (cell_w - image.width) // 2
        y = (index // columns) * cell_h + (cell_h - image.height) // 2
        sheet.alpha_composite(image, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


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
    if not images:
        return
    cell_w = max(image.width for _entry, image in images) + 38
    cell_h = max(image.height for _entry, image in images) + 38
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGBA", (cell_w * columns, cell_h * rows), (25, 26, 24, 255))
    draw = ImageDraw.Draw(sheet)
    for index, (entry, image) in enumerate(images):
        col = index % columns
        row = index // columns
        x = col * cell_w + (cell_w - image.width) // 2
        y = row * cell_h + cell_h - image.height - 16
        ax = x + image.width * float(entry["anchorX"])
        ay = y + image.height * float(entry["anchorY"])
        draw.ellipse((ax - 24, ay - 5, ax + 24, ay + 7), fill=(0, 0, 0, 85))
        sheet.alpha_composite(image, (x, y))
        draw.line((ax, row * cell_h + 8, ax, (row + 1) * cell_h - 8), fill=(226, 218, 168, 72))
        draw.line((col * cell_w + 8, ay, (col + 1) * cell_w - 8, ay), fill=(226, 218, 168, 72))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    for _entry, image in images:
        image.close()


def build_tiles() -> list[dict[str, object]]:
    sheet_images: list[tuple[str, Image.Image]] = []
    entries: list[dict[str, object]] = []
    for index, (asset_id, base, variant) in enumerate(GROUND_SPECS):
        image = create_ground_tile(asset_id, base, variant, 1400 + index * 53)
        output = TILE_ROOT / "cropped" / f"{asset_id}.png"
        image.save(output)
        sheet_images.append((asset_id, image))
        entries.append(manifest_entry(asset_id, "tile", output, 0.5, 0.0))
    save_sheet(sheet_images, TILE_ROOT / "raw" / "dark-arpg-ground-source-sheet.png", columns=3)
    write_contact_sheet(entries, TILE_ROOT / "manifests" / "dark-arpg-tiles-contact-sheet.png", columns=3)
    (TILE_ROOT / "manifests" / "dark-arpg-tiles-manifest.json").write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def build_edges() -> list[dict[str, object]]:
    sheet_images: list[tuple[str, Image.Image]] = []
    entries: list[dict[str, object]] = []
    for index, asset_id in enumerate(EDGE_SPECS):
        image = create_edge_tile(asset_id, 2400 + index * 59)
        output = EDGE_ROOT / "cropped" / f"{asset_id}.png"
        image.save(output)
        sheet_images.append((asset_id, image))
        entries.append(manifest_entry(asset_id, "edge", output, 0.5, 0.0))
    save_sheet(sheet_images, EDGE_ROOT / "raw" / "dark-arpg-edge-source-sheet.png", columns=4)
    write_contact_sheet(entries, EDGE_ROOT / "manifests" / "dark-arpg-edges-contact-sheet.png", columns=4)
    (EDGE_ROOT / "manifests" / "dark-arpg-edges-manifest.json").write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def build_units() -> list[dict[str, object]]:
    sheet_images: list[tuple[str, Image.Image]] = []
    entries: list[dict[str, object]] = []
    for index, (asset_id, asset_type, size, anchor_x, anchor_y) in enumerate(UNIT_SPECS):
        image = create_unit(asset_id, size, 3400 + index * 61)
        output = UNIT_ROOT / "cropped" / f"{asset_id}.png"
        image.save(output)
        sheet_images.append((asset_id, image))
        entries.append(manifest_entry(asset_id, asset_type, output, anchor_x, anchor_y))
    save_sheet(sheet_images, UNIT_ROOT / "raw" / "dark-arpg-units-source-sheet.png", columns=3)
    write_contact_sheet(entries, UNIT_ROOT / "manifests" / "dark-arpg-units-contact-sheet.png", columns=3)
    (UNIT_ROOT / "manifests" / "dark-arpg-units-manifest.json").write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def build_props() -> list[dict[str, object]]:
    sheet_images: list[tuple[str, Image.Image]] = []
    entries: list[dict[str, object]] = []
    for index, (asset_id, asset_type, size, anchor_x, anchor_y) in enumerate(PROP_SPECS):
        image = create_prop(asset_id, size, 4400 + index * 67)
        output = PROP_ROOT / "cropped" / f"{asset_id}.png"
        image.save(output)
        sheet_images.append((asset_id, image))
        entries.append(manifest_entry(asset_id, asset_type, output, anchor_x, anchor_y))
    save_sheet(sheet_images, PROP_ROOT / "raw" / "dark-arpg-props-source-sheet.png", columns=5)
    write_contact_sheet(entries, PROP_ROOT / "manifests" / "dark-arpg-props-contact-sheet.png", columns=5)
    (PROP_ROOT / "manifests" / "dark-arpg-props-manifest.json").write_text(json.dumps({"assets": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def main() -> int:
    ensure_dirs()
    tiles = build_tiles()
    edges = build_edges()
    units = build_units()
    props = build_props()
    manifest = {
        "style": "hand-drawn dark cartoon dimetric ARPG",
        "projection": {
            "kind": "dimetric",
            "isoTileWidth": ISO_TILE_W,
            "isoTileHeight": ISO_TILE_H,
            "worldTileSize": 64,
        },
        "assets": tiles + edges + units + props,
    }
    (COMMON_MANIFEST_DIR / "dark-arpg-battle-assets-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"generated {len(tiles)} tiles, {len(edges)} edges, {len(props)} props, {len(units)} units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
