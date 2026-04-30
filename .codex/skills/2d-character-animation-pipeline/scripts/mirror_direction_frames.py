#!/usr/bin/env python3
"""Mirror right-facing PNG frames into left-facing frames."""

from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror direction frames horizontally.")
    parser.add_argument("--input", required=True, help="Input frame directory")
    parser.add_argument("--output", required=True, help="Output frame directory")
    parser.add_argument("--from-direction", default="right")
    parser.add_argument("--to-direction", default="left")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob(f"*_{args.from_direction}_*.png"))
    if not files:
        raise SystemExit(f"未找到方向为 {args.from_direction} 的 PNG 帧：{input_dir}")

    for src in files:
        dst_name = src.name.replace(f"_{args.from_direction}_", f"_{args.to_direction}_")
        img = Image.open(src).convert("RGBA")
        mirrored = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        mirrored.save(output_dir / dst_name)

    print(f"已从 {args.from_direction} 镜像生成 {args.to_direction}：{len(files)} 帧")


if __name__ == "__main__":
    main()
