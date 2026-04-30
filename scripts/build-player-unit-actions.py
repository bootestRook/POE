from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
UNIT_ROOT = ROOT / "assest" / "battle" / "units"
FRAME_ROOT = UNIT_ROOT / "frames" / "player_adventurer"
SHEET_DIR = UNIT_ROOT / "sheets"
MANIFEST_DIR = UNIT_ROOT / "manifests"

UNIT_ID = "player_adventurer"
DIRECTIONS_8 = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]
DIRECTIONS_LR = ["left", "right"]
ACTIONS = {
    "idle": {"fps": 6, "loop": True},
    "walk": {"fps": 8, "loop": True},
    "run": {"fps": 11, "loop": True},
}
FRAME_COUNT = 6
ANCHOR_X = 0.5
ANCHOR_Y = 0.975
SCALE = 1.0


def frame_sort_key(path: Path) -> tuple[int, str]:
    matches = re.findall(r"(\d+)(?=\.png$)", path.name, flags=re.IGNORECASE)
    return (int(matches[-1]) if matches else 0, path.name)


def canonical_frame_path(action: str, direction: str, frame_index: int) -> Path:
    return FRAME_ROOT / action / direction / f"{UNIT_ID}_{action}_{direction}_f{frame_index:02d}.png"


def collect_source_frames(action: str) -> list[Path]:
    canonical = sorted((FRAME_ROOT / action / "right").glob(f"{UNIT_ID}_{action}_right_f*.png"))
    if canonical:
        return canonical
    legacy_dir = UNIT_ROOT / action
    return sorted(legacy_dir.glob("*.png"), key=frame_sort_key)


def normalize_right_frames(action: str) -> list[Path]:
    sources = collect_source_frames(action)
    if len(sources) != FRAME_COUNT:
        raise RuntimeError(f"{action} needs {FRAME_COUNT} frames, found {len(sources)}")

    target_dir = FRAME_ROOT / action / "right"
    target_dir.mkdir(parents=True, exist_ok=True)
    normalized: list[Path] = []
    for index, source in enumerate(sources):
        target = canonical_frame_path(action, "right", index)
        if source.resolve() == target.resolve():
            normalized.append(target)
            continue
        if target.exists():
            target.unlink()
        shutil.move(str(source), str(target))
        normalized.append(target)
    return normalized


def write_left_frames(action: str, right_frames: list[Path]) -> list[Path]:
    left_dir = FRAME_ROOT / action / "left"
    left_dir.mkdir(parents=True, exist_ok=True)
    left_frames: list[Path] = []
    for index, right_path in enumerate(right_frames):
        left_path = canonical_frame_path(action, "left", index)
        with Image.open(right_path) as image:
            ImageOps.mirror(image.convert("RGBA")).save(left_path)
        left_frames.append(left_path)
    return left_frames


def write_sheet(action: str, direction: str, frames: list[Path]) -> dict[str, object]:
    images = [Image.open(path).convert("RGBA") for path in frames]
    try:
        widths = {image.width for image in images}
        heights = {image.height for image in images}
        if len(widths) != 1 or len(heights) != 1:
            raise RuntimeError(f"{action}/{direction} frame sizes are not consistent")
        frame_width = images[0].width
        frame_height = images[0].height
        sheet = Image.new("RGBA", (frame_width * len(images), frame_height), (0, 0, 0, 0))
        for index, image in enumerate(images):
            sheet.alpha_composite(image, (index * frame_width, 0))
        SHEET_DIR.mkdir(parents=True, exist_ok=True)
        output = SHEET_DIR / f"{UNIT_ID}_{action}_{direction}.png"
        sheet.save(output)
    finally:
        for image in images:
            image.close()

    fps = int(ACTIONS[action]["fps"])
    return {
        "unitId": UNIT_ID,
        "state": action,
        "direction": direction,
        "id": f"{UNIT_ID}_{action}_{direction}",
        "path": "/" + output.relative_to(ROOT).as_posix(),
        "framesPath": "/" + (FRAME_ROOT / action / direction).relative_to(ROOT).as_posix(),
        "frameCount": FRAME_COUNT,
        "fps": fps,
        "loop": bool(ACTIONS[action]["loop"]),
        "durationMs": round(FRAME_COUNT / fps * 1000),
        "frameWidth": frame_width,
        "frameHeight": frame_height,
        "frameRow": 0,
        "width": frame_width * FRAME_COUNT,
        "height": frame_height,
        "anchorX": ANCHOR_X,
        "anchorY": ANCHOR_Y,
        "scale": SCALE,
        "fallbackState": "idle" if action != "idle" else None,
        "fallbackDirection": "right",
        "playbackRate": 1,
    }


def remove_empty_legacy_action_dirs() -> None:
    for action in ACTIONS:
        legacy_dir = UNIT_ROOT / action
        if legacy_dir.exists() and legacy_dir.is_dir() and not any(legacy_dir.iterdir()):
            legacy_dir.rmdir()


def main() -> int:
    entries: list[dict[str, object]] = []
    for action in ACTIONS:
        right_frames = normalize_right_frames(action)
        left_frames = write_left_frames(action, right_frames)
        entries.append(write_sheet(action, "right", right_frames))
        entries.append(write_sheet(action, "left", left_frames))

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source": "player_adventurer normalized action frame sequences",
        "directions": DIRECTIONS_8,
        "implementedDirections": DIRECTIONS_LR,
        "states": list(ACTIONS.keys()),
        "assets": entries,
    }
    (MANIFEST_DIR / "unit-animations-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    remove_empty_legacy_action_dirs()
    print(f"built {len(entries)} {UNIT_ID} animation assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
