#!/usr/bin/env python3
"""Build a simple sprite animation manifest from frame filenames."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build sprite manifest JSON.")
    parser.add_argument("--input", required=True, help="Frame directory")
    parser.add_argument("--output", required=True, help="Manifest JSON output")
    parser.add_argument("--character", required=True, help="Character id")
    parser.add_argument("--frame-width", type=int, default=256)
    parser.add_argument("--frame-height", type=int, default=256)
    parser.add_argument("--fps", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    animations: dict[str, list[str]] = defaultdict(list)
    for file in sorted(input_dir.glob(f"{args.character}_*.png")):
        stem = file.stem
        parts = stem.split("_")
        if len(parts) < 4:
            continue
        index = parts[-1]
        if not index.isdigit():
            continue
        action = parts[-3]
        direction = parts[-2]
        anim_id = f"{action}_{direction}"
        animations[anim_id].append(str(file.relative_to(input_dir.parent)).replace("\\", "/"))

    data = {
        "character_id": args.character,
        "frame_size": [args.frame_width, args.frame_height],
        "animations": {
            anim_id: {
                "loop": not anim_id.startswith(("death_",)),
                "fps": args.fps,
                "frames": frames,
            }
            for anim_id, frames in sorted(animations.items())
        },
    }

    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest 已生成：{output}")


if __name__ == "__main__":
    main()
