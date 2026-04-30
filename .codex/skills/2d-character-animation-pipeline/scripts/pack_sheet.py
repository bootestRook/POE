#!/usr/bin/env python3
"""Pack sprite frames into a sheet, one animation per row."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pack frames into a sprite sheet.")
    parser.add_argument("--input", required=True, help="Frame directory")
    parser.add_argument("--output", required=True, help="Output sheet path")
    parser.add_argument("--character", required=True, help="Character id")
    parser.add_argument("--frame-width", type=int, default=256)
    parser.add_argument("--frame-height", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    groups: dict[str, list[Path]] = defaultdict(list)
    for file in sorted(input_dir.glob(f"{args.character}_*.png")):
        parts = file.stem.split("_")
        if len(parts) < 4 or not parts[-1].isdigit():
            continue
        action = parts[-3]
        direction = parts[-2]
        groups[f"{action}_{direction}"].append(file)

    preferred_order = [
        "idle_right", "idle_left",
        "walk_right", "walk_left",
        "run_right", "run_left",
        "attack_right", "attack_left",
        "cast_right", "cast_left",
        "hit_right", "hit_left",
        "death_right", "death_left",
    ]
    keys = [key for key in preferred_order if key in groups] + [key for key in sorted(groups) if key not in preferred_order]
    if not keys:
        raise SystemExit(f"未找到可拼接帧：{input_dir}")

    max_frames = max(len(groups[key]) for key in keys)
    sheet = Image.new("RGBA", (max_frames * args.frame_width, len(keys) * args.frame_height), (0, 0, 0, 0))

    for row, key in enumerate(keys):
        for col, file in enumerate(sorted(groups[key])):
            img = Image.open(file).convert("RGBA")
            if img.size != (args.frame_width, args.frame_height):
                raise SystemExit(f"尺寸不匹配：{file}，实际={img.size}")
            sheet.alpha_composite(img, (col * args.frame_width, row * args.frame_height))

    sheet.save(output)
    print(f"sheet 已生成：{output}")
    print("行顺序：")
    for key in keys:
        print(f"- {key}")


if __name__ == "__main__":
    main()
