from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
UNIT_ROOT = ROOT / "assets" / "battle" / "units"
RAW_DIR = UNIT_ROOT / "raw"
CROPPED_DIR = UNIT_ROOT / "cropped"
SHEETS_DIR = UNIT_ROOT / "sheets"
MANIFEST_DIR = UNIT_ROOT / "manifests"
FORMAL_CROPPED_DIR = CROPPED_DIR / "formal"

DIRECTIONS_8 = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]
DIRECTIONS_LR = ["left", "right"]
FIXED_FRAME_SIZE = 128
FIXED_FRAME_PADDING = 6


@dataclass(frozen=True)
class UnitSpec:
    unit_id: str
    raw_file: str
    states: tuple[str, ...]
    rows: tuple[tuple[str, str], ...]
    source_rows: int
    source_row_indices: tuple[int, ...]
    fps: dict[str, int]
    loop: dict[str, bool]
    anchor_x: float
    anchor_y: float
    scale: float
    frame_padding_x: int
    frame_padding_y: int
    max_body_height: int


UNITS = [
    UnitSpec(
        unit_id="player_adventurer",
        raw_file="formal_player_whitehair_girl_lr_right_source_imagegen.png",
        states=("idle", "walk"),
        rows=(("idle", "right"), ("walk", "right")),
        source_rows=4,
        source_row_indices=(1, 3),
        fps={"idle": 4, "walk": 8},
        loop={"idle": True, "walk": True},
        anchor_x=0.5,
        anchor_y=0.955,
        scale=1.5,
        frame_padding_x=18,
        frame_padding_y=18,
        max_body_height=172,
    ),
    UnitSpec(
        unit_id="enemy_imp",
        raw_file="formal_enemy_imp_lr_right_source_imagegen.png",
        states=("idle", "walk", "attack"),
        rows=(("idle", "right"), ("walk", "right"), ("attack", "right")),
        source_rows=3,
        source_row_indices=(0, 1, 2),
        fps={"idle": 4, "walk": 9, "attack": 10},
        loop={"idle": True, "walk": True, "attack": False},
        anchor_x=0.5,
        anchor_y=0.945,
        scale=1.325,
        frame_padding_x=18,
        frame_padding_y=18,
        max_body_height=128,
    ),
    UnitSpec(
        unit_id="enemy_brute",
        raw_file="formal_enemy_brute_lr_right_source_imagegen.png",
        states=("idle", "walk", "attack"),
        rows=(("idle", "right"), ("walk", "right"), ("attack", "right")),
        source_rows=3,
        source_row_indices=(0, 1, 2),
        fps={"idle": 3, "walk": 7, "attack": 9},
        loop={"idle": True, "walk": True, "attack": False},
        anchor_x=0.5,
        anchor_y=0.965,
        scale=2.075,
        frame_padding_x=24,
        frame_padding_y=24,
        max_body_height=224,
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
            magenta_score = min(r, b) - g
            if g > 120 and green_score > 42:
                pixels[x, y] = (r, g, b, 0)
            elif r > 140 and b > 110 and magenta_score > 36:
                pixels[x, y] = (r, g, b, 0)
    return rgba


def trim_alpha(image: Image.Image) -> Image.Image:
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        return image
    return image.crop(bbox)


def remove_small_alpha_islands(image: Image.Image) -> Image.Image:
    components = connected_components(image, min_area=4)
    if len(components) <= 1:
        return image

    main = components[0]
    largest_area = main["area"]
    keep = [main]
    for component in components[1:]:
        vertical_overlap = min(component["bottom"], main["bottom"]) - max(component["top"], main["top"])
        overlaps_body = vertical_overlap > 0
        large_action_part = component["area"] >= largest_area * 0.18
        if large_action_part or (overlaps_body and component["area"] >= max(96, largest_area * 0.03)):
            keep.append(component)

    cleaned = Image.new("RGBA", image.size, (0, 0, 0, 0))
    for component in keep:
        box = (
            int(component["left"]),
            int(component["top"]),
            int(component["right"]),
            int(component["bottom"]),
        )
        cleaned.alpha_composite(image.crop(box), box[:2])
    return trim_alpha(cleaned)


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
    cell_width = width / cols
    cell_height = height / rows

    grid: list[list[Image.Image]] = []
    for row in range(rows):
        row_frames: list[Image.Image] = []
        for col in range(cols):
            left = max(0, round(col * cell_width) - gutter)
            top = max(0, round(row * cell_height) - gutter)
            right = min(width, round((col + 1) * cell_width) + gutter)
            bottom = min(height, round((row + 1) * cell_height) + gutter)
            frame = remove_small_alpha_islands(trim_alpha(alpha_image.crop((left, top, right, bottom))))
            row_frames.append(frame if frame.size != (0, 0) else Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
        grid.append(row_frames)
    return grid


def slice_sheet_components(image: Image.Image, rows: int, cols: int) -> list[list[Image.Image]]:
    alpha_image = chroma_to_alpha(image)
    width, height = alpha_image.size
    cell_width = width / cols
    cell_height = height / rows
    components = [
        component
        for component in connected_components(alpha_image, min_area=32)
        if component["area"] >= 180 and component["right"] - component["left"] >= 14 and component["bottom"] - component["top"] >= 14
    ]
    used: set[int] = set()
    grid: list[list[Image.Image]] = []
    for row in range(rows):
        row_frames: list[Image.Image] = []
        for col in range(cols):
            expected_x = (col + 0.5) * cell_width
            expected_y = (row + 0.5) * cell_height
            candidates = [
                (index, component)
                for index, component in enumerate(components)
                if index not in used
                and col * cell_width - cell_width * 0.2 <= component["center_x"] <= (col + 1) * cell_width + cell_width * 0.2
                and row * cell_height - cell_height * 0.35 <= component["center_y"] <= (row + 1) * cell_height + cell_height * 0.35
            ]
            if not candidates:
                candidates = [(index, component) for index, component in enumerate(components) if index not in used]
            if not candidates:
                row_frames.append(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
                continue
            index, component = min(
                candidates,
                key=lambda item: (
                    abs(item[1]["center_x"] - expected_x) / cell_width
                    + abs(item[1]["center_y"] - expected_y) / cell_height
                    - min(item[1]["area"], 8000) / 100000,
                ),
            )
            used.add(index)
            pad = 6
            box = (
                max(0, int(component["left"]) - pad),
                max(0, int(component["top"]) - pad),
                min(width, int(component["right"]) + pad),
                min(height, int(component["bottom"]) + pad),
            )
            row_frames.append(remove_small_alpha_islands(trim_alpha(alpha_image.crop(box))))
        grid.append(row_frames)
    return grid


def normalize_frame_row(frames: list[Image.Image], padding_x: int, padding_y: int, anchor_x: float, anchor_y: float) -> tuple[Image.Image, int, int]:
    frame_w = FIXED_FRAME_SIZE
    frame_h = FIXED_FRAME_SIZE
    anchor_px = round(frame_w * anchor_x)
    anchor_py = round(frame_h * anchor_y)
    sheet = Image.new("RGBA", (frame_w * len(frames), frame_h), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        left = index * frame_w + anchor_px - round(frame.width * anchor_x)
        top = anchor_py - round(frame.height * anchor_y)
        sheet.alpha_composite(frame, (left, top))
    return sheet, frame_w, frame_h


def normalize_action_sheet(rows: list[tuple[str, list[Image.Image]]], unit: UnitSpec) -> tuple[Image.Image, int, int, dict[str, int]]:
    frame_w = FIXED_FRAME_SIZE
    frame_h = FIXED_FRAME_SIZE
    sheet = Image.new("RGBA", (frame_w * 4, frame_h * len(rows)), (0, 0, 0, 0))
    frame_rows: dict[str, int] = {}
    for row_index, (direction, frames) in enumerate(rows):
        row_sheet, _, _ = normalize_frame_row(frames, unit.frame_padding_x, unit.frame_padding_y, unit.anchor_x, unit.anchor_y)
        sheet.alpha_composite(row_sheet, (0, row_index * frame_h))
        frame_rows[direction] = row_index
    return sheet, frame_w, frame_h, frame_rows


def fixed_frame_fit_ratio(frames: list[Image.Image]) -> float:
    max_width = max((frame.width for frame in frames), default=1)
    max_height = max((frame.height for frame in frames), default=1)
    inner_size = FIXED_FRAME_SIZE - FIXED_FRAME_PADDING * 2
    return min(inner_size / max(1, max_width), inner_size / max(1, max_height), 1)


def scale_frames_with_ratio(frames: list[Image.Image], ratio: float) -> list[Image.Image]:
    if ratio >= 0.999:
        return frames
    return [
        frame.resize((max(1, round(frame.width * ratio)), max(1, round(frame.height * ratio))), Image.Resampling.LANCZOS)
        for frame in frames
    ]


def scale_frames_to_body_height(frames: list[Image.Image], max_body_height: int) -> list[Image.Image]:
    scaled: list[Image.Image] = []
    for frame in frames:
        bbox = frame.getchannel("A").getbbox()
        if not bbox:
            scaled.append(frame)
            continue
        body_height = bbox[3] - bbox[1]
        if body_height <= max_body_height:
            scaled.append(frame)
            continue
        ratio = max_body_height / body_height
        width = max(1, round(frame.width * ratio))
        height = max(1, round(frame.height * ratio))
        scaled.append(frame.resize((width, height), Image.Resampling.LANCZOS))
    return scaled


def offset_alpha_region(image: Image.Image, box: tuple[int, int, int, int], dx: int, dy: int = 0) -> Image.Image:
    if dx == 0 and dy == 0:
        return image
    left, top, right, bottom = box
    region = image.crop(box)
    base = image.copy()
    clear = Image.new("RGBA", region.size, (0, 0, 0, 0))
    base.paste(clear, box, region)
    base.alpha_composite(region, (left + dx, top + dy))
    return trim_alpha(base)


def synthesize_walk_stride(frames: list[Image.Image], direction: str) -> list[Image.Image]:
    """Make four-frame side-view walks read as alternating feet.

    The imagegen source often keeps the same leading foot in every cell. This
    small lower-body phase pass preserves the authored torso/head art while
    moving the lower-left and lower-right foot regions in opposite directions.
    """
    if not frames:
        return frames
    phased: list[Image.Image] = []
    facing = 1 if direction == "right" else -1
    phase_offsets = [-3, 3, 3, -3]
    lift_offsets = [0, -1, 0, -1]
    for index, frame in enumerate(frames):
        image = frame.copy()
        bbox = image.getchannel("A").getbbox()
        if not bbox:
            phased.append(image)
            continue
        left, top, right, bottom = bbox
        width = right - left
        height = bottom - top
        lower_top = top + round(height * 0.62)
        mid_x = left + width // 2
        stride = phase_offsets[index % len(phase_offsets)] * facing
        lift = lift_offsets[index % len(lift_offsets)]
        front_box = (mid_x, lower_top, right, bottom)
        back_box = (left, lower_top, mid_x, bottom)
        image = offset_alpha_region(image, front_box, stride, lift)
        image = offset_alpha_region(image, back_box, -stride, 0)
        phased.append(trim_alpha(image))
    return phased


def synthesize_attack_action(frames: list[Image.Image], direction: str) -> list[Image.Image]:
    """Build clean attack motion from body art only, with no generated VFX."""
    clean = [remove_small_alpha_islands(trim_alpha(frame)) for frame in frames]
    fallback_source = next((frame for frame in clean if frame.getchannel("A").getbbox()), None)
    if fallback_source is None:
        return clean
    while len(clean) < 4:
        clean.append(fallback_source.copy())

    facing = 1 if direction == "right" else -1
    transforms = [
        {"scale": 0.98, "rotate": -4 * facing, "dx": -3 * facing, "dy": 1},
        {"scale": 1.03, "rotate": 6 * facing, "dx": 5 * facing, "dy": -1},
        {"scale": 1.08, "rotate": 10 * facing, "dx": 10 * facing, "dy": -1},
        {"scale": 1.0, "rotate": 0, "dx": 0, "dy": 0},
    ]
    action_frames: list[Image.Image] = []
    for index, spec in enumerate(transforms):
        source = clean[min(index, len(clean) - 1)]
        if not source.getchannel("A").getbbox():
            source = fallback_source
        scale = float(spec["scale"])
        resized = source.resize(
            (max(1, round(source.width * scale)), max(1, round(source.height * scale))),
            Image.Resampling.LANCZOS,
        )
        rotated = resized.rotate(float(spec["rotate"]), resample=Image.Resampling.BICUBIC, expand=True)
        canvas_w = rotated.width + 28
        canvas_h = rotated.height + 18
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        canvas.alpha_composite(rotated, (14 + int(spec["dx"]), 9 + int(spec["dy"])))
        action_frames.append(remove_small_alpha_islands(trim_alpha(canvas)))
    return action_frames


def write_contact_sheet(entries: list[dict[str, object]]) -> None:
    samples = [entry for entry in entries if entry["direction"] in DIRECTIONS_LR]
    cell_w = max(int(entry["frameWidth"]) for entry in samples) + 52
    cell_h = max(int(entry["frameHeight"]) for entry in samples) + 48
    cols = 4
    rows = (len(samples) + cols - 1) // cols
    contact = Image.new("RGBA", (cell_w * cols, cell_h * rows), (22, 22, 22, 255))
    draw = ImageDraw.Draw(contact)
    for index, entry in enumerate(samples):
        sheet = Image.open(ROOT / str(entry["path"]).lstrip("/")).convert("RGBA")
        frame_y = int(entry.get("frameRow", 0)) * int(entry["frameHeight"])
        frame = sheet.crop((0, frame_y, int(entry["frameWidth"]), frame_y + int(entry["frameHeight"])))
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


def prepare_animation_frames(
    asset_id: str,
    state: str,
    direction: str,
    frames: list[Image.Image],
    unit: UnitSpec,
    fit_ratio: float,
) -> list[Image.Image]:
    if state == "walk":
        frames = synthesize_walk_stride(frames, direction)
    elif state == "attack":
        frames = synthesize_attack_action(frames, direction)
    frames = scale_frames_with_ratio(scale_frames_to_body_height(frames, unit.max_body_height), fit_ratio)
    for frame_index, frame in enumerate(frames):
        frame.save(FORMAL_CROPPED_DIR / f"{asset_id}_f{frame_index:02d}.png")
    return frames


def append_animation_entries(
    entries: list[dict[str, object]],
    unit: UnitSpec,
    state: str,
    direction_frames: dict[str, list[Image.Image]],
    source_raw: Path,
) -> None:
    asset_prefix = ID_PREFIX[(unit.unit_id, state)]
    rows = [(direction, direction_frames[direction]) for direction in ("right", "left")]
    sheet, frame_w, frame_h, frame_rows = normalize_action_sheet(rows, unit)
    output = SHEETS_DIR / f"{asset_prefix}.png"
    sheet.save(output)
    for direction in ("right", "left"):
        entries.append(
            {
                "unitId": unit.unit_id,
                "state": state,
                "direction": direction,
                "id": f"{asset_prefix}_{direction}",
                "path": "/" + output.relative_to(ROOT).as_posix(),
                "frameCount": 4,
                "fps": unit.fps[state],
                "loop": unit.loop[state],
                "durationMs": round(4 / unit.fps[state] * 1000),
                "frameWidth": frame_w,
                "frameHeight": frame_h,
                "frameRow": frame_rows[direction],
                "width": sheet.width,
                "height": sheet.height,
                "anchorX": unit.anchor_x,
                "anchorY": unit.anchor_y,
                "scale": unit.scale,
                "fallbackState": "idle" if state != "idle" else None,
                "fallbackDirection": "right",
                "playbackRate": 1,
                "sourceRaw": f"/{source_raw.relative_to(ROOT).as_posix()}",
            }
        )


def main() -> int:
    CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    FORMAL_CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    for prefix in sorted(set(ID_PREFIX.values())):
        for old_sheet in SHEETS_DIR.glob(f"{prefix}_*.png"):
            old_sheet.unlink()
    for unit in UNITS:
        raw = Image.open(RAW_DIR / unit.raw_file).convert("RGBA")
        grid = slice_sheet_grid(raw, unit.source_rows, 4)
        source_rows = [grid[index] for index in unit.source_row_indices]
        right_frame_sets = [frames for frames in source_rows]
        left_frame_sets = [[ImageOps.mirror(frame) for frame in frames] for frames in right_frame_sets]
        fit_ratio = fixed_frame_fit_ratio([frame for frames in [*right_frame_sets, *left_frame_sets] for frame in frames])
        for row_index, (state, _direction) in enumerate(unit.rows):
            source_row_index = 0 if state == "attack" else row_index
            right_asset_id = f"{ID_PREFIX[(unit.unit_id, state)]}_right"
            left_asset_id = f"{ID_PREFIX[(unit.unit_id, state)]}_left"
            right_frames = prepare_animation_frames(
                right_asset_id,
                state,
                "right",
                right_frame_sets[source_row_index],
                unit,
                fit_ratio,
            )
            left_frames = prepare_animation_frames(
                left_asset_id,
                state,
                "left",
                left_frame_sets[source_row_index],
                unit,
                fit_ratio,
            )
            append_animation_entries(
                entries,
                unit,
                state,
                {"right": right_frames, "left": left_frames},
                RAW_DIR / unit.raw_file,
            )
        raw.close()

    manifest = {
        "source": "imagegen formal action sheets",
        "directions": DIRECTIONS_8,
        "implementedDirections": DIRECTIONS_LR,
        "states": ["idle", "walk", "attack"],
        "assets": entries,
    }
    (MANIFEST_DIR / "unit-animations-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_contact_sheet(entries)
    print(f"processed {len(entries)} formal imagegen action sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
