from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
UNIT_ROOT = ROOT / "assest" / "battle" / "units"
RAW_DIR = UNIT_ROOT / "raw"
CROPPED_DIR = UNIT_ROOT / "cropped"
SHEETS_DIR = UNIT_ROOT / "sheets"
MANIFEST_DIR = UNIT_ROOT / "manifests"
FORMAL_CROPPED_DIR = CROPPED_DIR / "formal"

DIRECTIONS_8 = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]
DIRECTIONS_4 = ["down", "right", "up", "left"]


@dataclass(frozen=True)
class UnitSpec:
    unit_id: str
    raw_file: str
    states: tuple[str, ...]
    rows: tuple[tuple[str, str], ...]
    fps: dict[str, int]
    loop: dict[str, bool]
    anchor_x: float
    anchor_y: float
    scale: float
    frame_padding_x: int
    frame_padding_y: int


UNITS = [
    UnitSpec(
        unit_id="player_adventurer",
        raw_file="formal_player_whitehair_girl_actions_imagegen.png",
        states=("idle", "walk"),
        rows=tuple((state, direction) for state in ("idle", "walk") for direction in DIRECTIONS_4),
        fps={"idle": 4, "walk": 8},
        loop={"idle": True, "walk": True},
        anchor_x=0.5,
        anchor_y=0.955,
        scale=1.0,
        frame_padding_x=18,
        frame_padding_y=18,
    ),
    UnitSpec(
        unit_id="enemy_imp",
        raw_file="formal_enemy_imp_actions_imagegen.png",
        states=("idle", "walk", "attack"),
        rows=tuple((state, direction) for state in ("idle", "walk", "attack") for direction in DIRECTIONS_4),
        fps={"idle": 4, "walk": 9, "attack": 10},
        loop={"idle": True, "walk": True, "attack": False},
        anchor_x=0.5,
        anchor_y=0.945,
        scale=1.0,
        frame_padding_x=18,
        frame_padding_y=18,
    ),
    UnitSpec(
        unit_id="enemy_brute",
        raw_file="formal_enemy_brute_actions_imagegen.png",
        states=("idle", "walk", "attack"),
        rows=tuple((state, direction) for state in ("idle", "walk", "attack") for direction in DIRECTIONS_4),
        fps={"idle": 3, "walk": 7, "attack": 9},
        loop={"idle": True, "walk": True, "attack": False},
        anchor_x=0.5,
        anchor_y=0.965,
        scale=1.0,
        frame_padding_x=24,
        frame_padding_y=24,
    ),
]

ID_PREFIX = {
    ("player_adventurer", "idle"): "player_whitehair_girl_idle",
    ("player_adventurer", "walk"): "player_whitehair_girl_walk",
    ("enemy_imp", "idle"): "enemy_imp_idle",
    ("enemy_imp", "walk"): "enemy_imp_walk",
    ("enemy_imp", "attack"): "enemy_imp_attack",
    ("enemy_brute", "idle"): "enemy_brute_idle",
    ("enemy_brute", "walk"): "enemy_brute_walk",
    ("enemy_brute", "attack"): "enemy_brute_attack",
}


def chroma_to_alpha(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            green_score = g - max(r, b)
            if g > 120 and green_score > 42:
                alpha = 0 if green_score > 88 else max(0, min(255, 255 - green_score * 3))
                pixels[x, y] = (r, g, b, alpha)
    return rgba


def trim_alpha(image: Image.Image) -> Image.Image:
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        return image
    return image.crop(bbox)


def projection_counts(image: Image.Image, axis: str, threshold: int = 24) -> list[int]:
    alpha = image.getchannel("A")
    width, height = alpha.size
    if axis == "x":
        return [sum(1 for y in range(height) if alpha.getpixel((x, y)) > threshold) for x in range(width)]
    return [sum(1 for x in range(width) if alpha.getpixel((x, y)) > threshold) for y in range(height)]


def infer_grid_edges(counts: list[int], segments: int) -> list[int]:
    length = len(counts)
    approx = length / segments
    search_radius = max(6, int(approx * 0.28))
    edges = [0]
    for index in range(1, segments):
        target = round(index * approx)
        start = max(edges[-1] + 1, target - search_radius)
        end = min(length - 1, target + search_radius)
        if start >= end:
            best = start
        else:
            best = min(range(start, end + 1), key=lambda value: (counts[value], abs(value - target)))
        edges.append(best)
    edges.append(length)
    return edges


def connected_components(image: Image.Image, min_area: int = 6) -> list[dict[str, float]]:
    alpha = image.getchannel("A")
    width, height = alpha.size
    data = alpha.load()
    visited = bytearray(width * height)
    components: list[dict[str, float]] = []
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if visited[index] or data[x, y] <= 24:
                continue
            stack = [(x, y)]
            visited[index] = 1
            min_x = max_x = x
            min_y = max_y = y
            area = 0
            while stack:
                cx, cy = stack.pop()
                area += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    next_index = ny * width + nx
                    if visited[next_index] or data[nx, ny] <= 24:
                        continue
                    visited[next_index] = 1
                    stack.append((nx, ny))
            if area >= min_area:
                components.append(
                    {
                        "left": min_x,
                        "top": min_y,
                        "right": max_x + 1,
                        "bottom": max_y + 1,
                        "area": area,
                        "center_x": (min_x + max_x + 1) / 2,
                        "center_y": (min_y + max_y + 1) / 2,
                    }
                )
    return sorted(components, key=lambda component: component["area"], reverse=True)


def slice_sheet_grid(image: Image.Image, rows: int, cols: int, gutter: int = 0) -> list[list[Image.Image]]:
    alpha_image = chroma_to_alpha(image)
    width, height = alpha_image.size
    components = connected_components(alpha_image)
    cells: list[list[list[dict[str, float]]]] = [[[] for _ in range(cols)] for _ in range(rows)]
    available = {(row, col) for row in range(rows) for col in range(cols)}
    cell_width = width / cols
    cell_height = height / rows

    for component in components:
        if not available:
            break
        best_cell = min(
            available,
            key=lambda cell: (
                abs(component["center_x"] - (cell[1] + 0.5) * cell_width)
                + abs(component["center_y"] - (cell[0] + 0.5) * cell_height)
            ),
        )
        cells[best_cell[0]][best_cell[1]].append(component)
        available.remove(best_cell)

    for component in components[rows * cols:]:
        target_row, target_col = min(
            ((row, col) for row in range(rows) for col in range(cols)),
            key=lambda cell: abs(component["center_x"] - (cell[1] + 0.5) * cell_width)
            + abs(component["center_y"] - (cell[0] + 0.5) * cell_height),
        )
        if not cells[target_row][target_col]:
            continue
        main = cells[target_row][target_col][0]
        margin_x = max(36, int((main["right"] - main["left"]) * 0.45))
        margin_y = max(36, int((main["bottom"] - main["top"]) * 0.45))
        inside_main_bounds = (
            main["left"] - margin_x <= component["center_x"] <= main["right"] + margin_x
            and main["top"] - margin_y <= component["center_y"] <= main["bottom"] + margin_y
        )
        if inside_main_bounds:
            cells[target_row][target_col].append(component)

    grid: list[list[Image.Image]] = []
    for row in range(rows):
        row_frames: list[Image.Image] = []
        for col in range(cols):
            assigned = cells[row][col]
            if assigned:
                left = max(0, min(int(component["left"]) for component in assigned) - gutter)
                top = max(0, min(int(component["top"]) for component in assigned) - gutter)
                right = min(width, max(int(component["right"]) for component in assigned) + gutter)
                bottom = min(height, max(int(component["bottom"]) for component in assigned) + gutter)
            else:
                left = max(0, round(col * cell_width) - gutter)
                top = max(0, round(row * cell_height) - gutter)
                right = min(width, round((col + 1) * cell_width) + gutter)
                bottom = min(height, round((row + 1) * cell_height) + gutter)
            frame = trim_alpha(alpha_image.crop((left, top, right, bottom)))
            row_frames.append(frame if frame.size != (0, 0) else Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
        grid.append(row_frames)
    return grid


def normalize_sheet(frames: list[Image.Image], padding_x: int, padding_y: int, anchor_x: float, anchor_y: float) -> tuple[Image.Image, int, int]:
    frame_w = max(frame.width for frame in frames) + padding_x * 2
    frame_h = max(frame.height for frame in frames) + padding_y * 2
    anchor_px = round(frame_w * anchor_x)
    anchor_py = round(frame_h * anchor_y)
    sheet = Image.new("RGBA", (frame_w * len(frames), frame_h), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        left = index * frame_w + anchor_px - round(frame.width * anchor_x)
        top = anchor_py - round(frame.height * anchor_y)
        sheet.alpha_composite(frame, (left, top))
    return sheet, frame_w, frame_h


def write_contact_sheet(entries: list[dict[str, object]]) -> None:
    samples = [entry for entry in entries if entry["direction"] in ("down", "right")]
    cell_w = max(int(entry["frameWidth"]) for entry in samples) + 52
    cell_h = max(int(entry["frameHeight"]) for entry in samples) + 48
    cols = 4
    rows = (len(samples) + cols - 1) // cols
    contact = Image.new("RGBA", (cell_w * cols, cell_h * rows), (22, 22, 22, 255))
    draw = ImageDraw.Draw(contact)
    for index, entry in enumerate(samples):
        sheet = Image.open(ROOT / str(entry["path"]).lstrip("/")).convert("RGBA")
        frame = sheet.crop((0, 0, int(entry["frameWidth"]), int(entry["frameHeight"])))
        col = index % cols
        row = index // cols
        left = col * cell_w + (cell_w - frame.width) // 2
        top = row * cell_h + cell_h - frame.height - 22
        anchor_x = left + frame.width * float(entry["anchorX"])
        anchor_y = top + frame.height * float(entry["anchorY"])
        draw.ellipse((anchor_x - 26, anchor_y - 5, anchor_x + 26, anchor_y + 7), fill=(0, 0, 0, 90))
        contact.alpha_composite(frame, (left, top))
        draw.text((col * cell_w + 8, row * cell_h + 8), f"{entry['unitId']} {entry['state']} {entry['direction']}", fill=(232, 224, 190, 255))
        sheet.close()
    contact.save(MANIFEST_DIR / "formal-unit-actions-contact-sheet.png")


def main() -> int:
    CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    FORMAL_CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    for unit in UNITS:
        raw = Image.open(RAW_DIR / unit.raw_file).convert("RGBA")
        grid = slice_sheet_grid(raw, len(unit.rows), 4)
        for row_index, (state, direction) in enumerate(unit.rows):
            asset_id = f"{ID_PREFIX[(unit.unit_id, state)]}_{direction}"
            for frame_index, frame in enumerate(grid[row_index]):
                frame.save(FORMAL_CROPPED_DIR / f"{asset_id}_f{frame_index:02d}.png")
            sheet, frame_w, frame_h = normalize_sheet(grid[row_index], unit.frame_padding_x, unit.frame_padding_y, unit.anchor_x, unit.anchor_y)
            output = SHEETS_DIR / f"{asset_id}.png"
            sheet.save(output)
            entries.append(
                {
                    "unitId": unit.unit_id,
                    "state": state,
                    "direction": direction,
                    "id": asset_id,
                    "path": "/" + output.relative_to(ROOT).as_posix(),
                    "frameCount": 4,
                    "fps": unit.fps[state],
                    "loop": unit.loop[state],
                    "durationMs": round(4 / unit.fps[state] * 1000),
                    "frameWidth": frame_w,
                    "frameHeight": frame_h,
                    "width": sheet.width,
                    "height": sheet.height,
                    "anchorX": unit.anchor_x,
                    "anchorY": unit.anchor_y,
                    "scale": unit.scale,
                    "fallbackState": "idle" if state != "idle" else None,
                    "fallbackDirection": "down",
                    "playbackRate": 1,
                    "sourceRaw": f"/{(RAW_DIR / unit.raw_file).relative_to(ROOT).as_posix()}",
                }
            )
        raw.close()

    manifest = {
        "source": "imagegen formal action sheets",
        "directions": DIRECTIONS_8,
        "implementedDirections": DIRECTIONS_4,
        "states": ["idle", "walk", "attack"],
        "assets": entries,
    }
    (MANIFEST_DIR / "unit-animations-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(entries)
    print(f"processed {len(entries)} formal imagegen action sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
