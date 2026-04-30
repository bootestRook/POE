#!/usr/bin/env python3
"""Slice one horizontal sprite row into fixed-size PNG frames."""

from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Slice a horizontal sprite row into PNG frames.")
    parser.add_argument("--input", required=True, help="Input row image path")
    parser.add_argument("--output", required=True, help="Output frame directory")
    parser.add_argument("--character", required=True, help="Character id")
    parser.add_argument("--action", required=True, help="Action name, e.g. walk")
    parser.add_argument("--direction", default="right", help="Direction, default: right")
    parser.add_argument("--frame-width", type=int, default=256)
    parser.add_argument("--frame-height", type=int, default=256)
    parser.add_argument("--frame-count", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src).convert("RGBA")
    expected_size = (args.frame_width * args.frame_count, args.frame_height)
    if img.size != expected_size:
        raise SystemExit(
            f"尺寸不匹配：输入={img.size}，期望={expected_size}。停止切帧，避免错误裁剪。"
        )

    for index in range(args.frame_count):
        left = index * args.frame_width
        box = (left, 0, left + args.frame_width, args.frame_height)
        frame = img.crop(box)
        name = f"{args.character}_{args.action}_{args.direction}_{index:03d}.png"
        frame.save(out_dir / name)

    print(f"已切分 {args.frame_count} 帧到：{out_dir}")


if __name__ == "__main__":
    main()
