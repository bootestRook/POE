"""Deprecated prototype.

This script generated placeholder motion by transforming a single idle image.
It is intentionally no longer used for formal unit action assets. Use
scripts/process-formal-unit-action-sheets.py for imagegen-authored action sheets.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
UNIT_ROOT = ROOT / "assest" / "battle" / "units"
CROPPED_DIR = UNIT_ROOT / "cropped"
SHEETS_DIR = UNIT_ROOT / "sheets"
MANIFEST_DIR = UNIT_ROOT / "manifests"
RAW_DIR = UNIT_ROOT / "raw"

DIRECTIONS_4 = ["down", "right", "up", "left"]
DIRECTIONS_8 = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]

UNITS = {
    "player_adventurer": {
        "source": "player_whitehair_girl_idle.png",
        "states": {
            "idle": {"id": "player_whitehair_girl_idle", "frames": 4, "fps": 4, "loop": True},
            "walk": {"id": "player_whitehair_girl_walk", "frames": 6, "fps": 8, "loop": True},
        },
        "anchorX": 0.5,
        "anchorY": 0.956,
        "scale": 1.0,
    },
    "enemy_imp": {
        "source": "enemy_imp_idle.png",
        "states": {
            "idle": {"id": "enemy_imp_idle", "frames": 4, "fps": 4, "loop": True},
            "walk": {"id": "enemy_imp_walk", "frames": 6, "fps": 8, "loop": True},
            "attack": {"id": "enemy_imp_attack", "frames": 6, "fps": 10, "loop": False},
        },
        "anchorX": 0.5,
        "anchorY": 0.948,
        "scale": 1.0,
        "mirrorHorizontalDirections": True,
    },
    "enemy_brute": {
        "source": "enemy_brute_idle.png",
        "states": {
            "idle": {"id": "enemy_brute_idle", "frames": 4, "fps": 3, "loop": True},
            "walk": {"id": "enemy_brute_walk", "frames": 6, "fps": 7, "loop": True},
            "attack": {"id": "enemy_brute_attack", "frames": 7, "fps": 9, "loop": False},
        },
        "anchorX": 0.5,
        "anchorY": 0.968,
        "scale": 1.0,
        "mirrorHorizontalDirections": True,
    },
}


def direction_variant(source: Image.Image, direction: str, mirror_horizontal_directions: bool) -> Image.Image:
    flip_directions = ("right", "up_right", "down_right") if mirror_horizontal_directions else ("left", "up_left", "down_left")
    if direction in flip_directions:
        return source.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if direction in ("up", "up_right"):
        image = source.copy()
        overlay = Image.new("RGBA", image.size, (34, 28, 36, 42))
        return Image.alpha_composite(image, overlay)
    return source.copy()


def frame_transform(source: Image.Image, state: str, frame: int, frame_count: int, direction: str) -> tuple[Image.Image, int, int]:
    phase = (frame / frame_count) * math.tau
    image = source.copy()
    offset_x = 0
    offset_y = 0
    if state == "idle":
        scale_y = 1 + 0.012 * math.sin(phase)
        image = image.resize((image.width, max(1, round(image.height * scale_y))), Image.Resampling.LANCZOS)
    elif state == "walk":
        stride = math.sin(phase)
        lift = abs(stride)
        lean = 3.5 * stride
        scale_x = 1 + 0.025 * lift
        scale_y = 1 - 0.025 * lift
        image = image.resize(
            (max(1, round(image.width * scale_x)), max(1, round(image.height * scale_y))),
            Image.Resampling.LANCZOS,
        )
        image = image.rotate(lean, resample=Image.Resampling.BICUBIC, expand=True)
        offset_y = round(-3 * lift)
        if direction in ("right", "down_right", "up_right"):
            offset_x = round(3 * stride)
        elif direction in ("left", "down_left", "up_left"):
            offset_x = round(-3 * stride)
    elif state == "attack":
        progress = frame / max(1, frame_count - 1)
        lunge = math.sin(progress * math.pi)
        windup = -0.12 if progress < 0.28 else 0
        scale = 1 + 0.08 * lunge + windup
        next_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
        image = image.resize(next_size, Image.Resampling.LANCZOS)
        image = image.rotate((18 if direction != "left" else -18) * lunge, resample=Image.Resampling.BICUBIC, expand=True)
        forward = round(lunge * 12)
        if direction in ("right", "down_right", "up_right"):
            offset_x = forward
        elif direction in ("left", "down_left", "up_left"):
            offset_x = -forward
        elif direction == "up":
            offset_y = -forward
        else:
            offset_y = round(forward * 0.45)
    return image, offset_x, offset_y


def motion_overlay(frame_image: Image.Image, state: str, frame: int, frame_count: int, direction: str, anchor_x: int, anchor_y: int) -> None:
    draw = ImageDraw.Draw(frame_image, "RGBA")
    phase = frame / max(1, frame_count - 1)
    if state == "walk":
        side = -1 if frame % 2 == 0 else 1
        dust_x = anchor_x + side * 14
        dust_y = anchor_y - 4
        alpha = 80 if frame % 3 != 0 else 42
        foot_color = (34, 20, 16, 150)
        draw.ellipse((anchor_x + side * 10 - 12, anchor_y - 14, anchor_x + side * 10 + 12, anchor_y - 5), fill=foot_color)
        draw.ellipse((anchor_x - side * 14 - 10, anchor_y - 9, anchor_x - side * 14 + 10, anchor_y - 1), fill=(42, 25, 18, 120))
        draw.ellipse((dust_x - 18, dust_y - 4, dust_x + 20, dust_y + 6), fill=(74, 52, 38, alpha))
        draw.ellipse((anchor_x - side * 6 - 8, dust_y - 2, anchor_x - side * 6 + 10, dust_y + 4), fill=(122, 91, 62, max(24, alpha - 28)))
    elif state == "attack":
        lunge = math.sin(phase * math.pi)
        if lunge <= 0:
            return
        if direction == "left":
            arc_box = (anchor_x - 70, anchor_y - 78, anchor_x + 24, anchor_y - 16)
            start, end = 198, 326
        elif direction == "up":
            arc_box = (anchor_x - 52, anchor_y - 105, anchor_x + 58, anchor_y - 24)
            start, end = 215, 340
        elif direction == "down":
            arc_box = (anchor_x - 50, anchor_y - 72, anchor_x + 62, anchor_y + 5)
            start, end = 24, 148
        else:
            arc_box = (anchor_x - 24, anchor_y - 78, anchor_x + 72, anchor_y - 16)
            start, end = 214, 342
        width = max(3, round(5 * lunge))
        ghost_alpha = round(46 * lunge)
        if direction == "left":
            draw.polygon([(anchor_x - 10, anchor_y - 72), (anchor_x - 76, anchor_y - 54), (anchor_x - 14, anchor_y - 28)], fill=(255, 110, 52, ghost_alpha))
        elif direction == "right":
            draw.polygon([(anchor_x + 10, anchor_y - 72), (anchor_x + 78, anchor_y - 54), (anchor_x + 16, anchor_y - 28)], fill=(255, 110, 52, ghost_alpha))
        elif direction == "up":
            draw.polygon([(anchor_x - 38, anchor_y - 58), (anchor_x, anchor_y - 112), (anchor_x + 38, anchor_y - 58)], fill=(255, 110, 52, ghost_alpha))
        else:
            draw.polygon([(anchor_x - 40, anchor_y - 36), (anchor_x, anchor_y + 10), (anchor_x + 42, anchor_y - 36)], fill=(255, 110, 52, ghost_alpha))
        draw.arc(arc_box, start=start, end=end, fill=(255, 238, 170, round(190 * lunge)), width=width)
        draw.arc(arc_box, start=start + 8, end=end - 10, fill=(255, 92, 38, round(130 * lunge)), width=max(2, width - 2))
        draw.ellipse((anchor_x - 26, anchor_y - 5, anchor_x + 28, anchor_y + 6), fill=(46, 29, 22, round(72 * lunge)))


def make_sheet(
    source: Image.Image,
    state: str,
    direction: str,
    frame_count: int,
    anchor_x: float,
    anchor_y: float,
    mirror_horizontal_directions: bool,
) -> tuple[Image.Image, int, int]:
    directed = direction_variant(source, direction, mirror_horizontal_directions)
    frame_width = directed.width + 34
    frame_height = directed.height + 28
    anchor_px = round(frame_width * anchor_x)
    anchor_py = round(frame_height * anchor_y)
    sheet = Image.new("RGBA", (frame_width * frame_count, frame_height), (0, 0, 0, 0))
    for frame in range(frame_count):
        image, offset_x, offset_y = frame_transform(directed, state, frame, frame_count, direction)
        left = frame * frame_width + anchor_px - round(image.width * anchor_x) + offset_x
        top = anchor_py - round(image.height * anchor_y) + offset_y
        sheet.alpha_composite(image, (left, top))
        frame_canvas = Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, 0))
        motion_overlay(frame_canvas, state, frame, frame_count, direction, anchor_px, anchor_py)
        sheet.alpha_composite(frame_canvas, (frame * frame_width, 0))
    return sheet, frame_width, frame_height


def write_contact_sheet(entries: list[dict[str, object]]) -> None:
    samples = [entry for entry in entries if entry["direction"] in ("down", "right") and entry["state"] in ("idle", "walk", "attack")]
    columns = 3
    cell_width = max(int(entry["frameWidth"]) for entry in samples) + 38
    cell_height = max(int(entry["frameHeight"]) for entry in samples) + 38
    rows = math.ceil(len(samples) / columns)
    sheet = Image.new("RGBA", (columns * cell_width, rows * cell_height), (24, 25, 23, 255))
    draw = ImageDraw.Draw(sheet)
    for index, entry in enumerate(samples):
        image = Image.open(ROOT / str(entry["path"]).lstrip("/")).convert("RGBA")
        frame = image.crop((0, 0, int(entry["frameWidth"]), int(entry["frameHeight"])))
        col = index % columns
        row = index // columns
        left = col * cell_width + (cell_width - frame.width) // 2
        top = row * cell_height + cell_height - frame.height - 16
        anchor_x = left + frame.width * float(entry["anchorX"])
        anchor_y = top + frame.height * float(entry["anchorY"])
        draw.ellipse((anchor_x - 24, anchor_y - 5, anchor_x + 24, anchor_y + 7), fill=(0, 0, 0, 85))
        sheet.alpha_composite(frame, (left, top))
        draw.line((anchor_x, row * cell_height + 8, anchor_x, (row + 1) * cell_height - 8), fill=(226, 218, 168, 72))
        draw.line((col * cell_width + 8, anchor_y, (col + 1) * cell_width - 8, anchor_y), fill=(226, 218, 168, 72))
        image.close()
    sheet.save(MANIFEST_DIR / "unit-animations-contact-sheet.png")


def main() -> int:
    print(
        "Deprecated: build-unit-animation-sheets.py creates prototype pseudo motion from idle art. "
        "Use scripts/process-formal-unit-action-sheets.py for formal imagegen action resources."
    )
    return 2
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    for unit_id, unit in UNITS.items():
        source = Image.open(CROPPED_DIR / str(unit["source"])).convert("RGBA")
        for state, state_spec in unit["states"].items():
            for direction in DIRECTIONS_4:
                frame_count = int(state_spec["frames"])
                fps = int(state_spec["fps"])
                sheet, frame_width, frame_height = make_sheet(
                    source,
                    state,
                    direction,
                    frame_count,
                    float(unit["anchorX"]),
                    float(unit["anchorY"]),
                    bool(unit.get("mirrorHorizontalDirections", False)),
                )
                output = SHEETS_DIR / f"{state_spec['id']}_{direction}.png"
                sheet.save(output)
                entries.append(
                    {
                        "unitId": unit_id,
                        "state": state,
                        "direction": direction,
                        "id": f"{state_spec['id']}_{direction}",
                        "path": "/" + output.relative_to(ROOT).as_posix(),
                        "frameCount": frame_count,
                        "fps": fps,
                        "loop": bool(state_spec["loop"]),
                        "durationMs": round(frame_count / fps * 1000),
                        "frameWidth": frame_width,
                        "frameHeight": frame_height,
                        "width": sheet.width,
                        "height": sheet.height,
                        "anchorX": float(unit["anchorX"]),
                        "anchorY": float(unit["anchorY"]),
                        "scale": float(unit["scale"]),
                        "fallbackState": "idle" if state != "idle" else None,
                        "fallbackDirection": "down",
                        "playbackRate": 1,
                    }
                )
        source.close()

    manifest = {
        "directions": DIRECTIONS_8,
        "implementedDirections": DIRECTIONS_4,
        "states": ["idle", "walk", "attack"],
        "assets": entries,
    }
    (MANIFEST_DIR / "unit-animations-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(entries)
    print(f"generated {len(entries)} unit animation sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
