#!/usr/bin/env python3
"""Validate sprite frames and emit a Chinese Markdown report."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate sprite frame files.")
    parser.add_argument("--input", required=True, help="Frame directory")
    parser.add_argument("--frame-width", type=int, default=256)
    parser.add_argument("--frame-height", type=int, default=256)
    parser.add_argument("--report", required=True, help="Markdown report output path")
    return parser.parse_args()


def has_visible_pixels(img: Image.Image) -> bool:
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.getchannel("A")
    return alpha.getbbox() is not None


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob("*.png"))
    rows = []
    groups: dict[str, list[Path]] = defaultdict(list)
    ok = True

    for file in files:
        img = Image.open(file)
        mode_ok = img.mode in {"RGBA", "LA"} or "transparency" in img.info
        size_ok = img.size == (args.frame_width, args.frame_height)
        visible_ok = has_visible_pixels(img.convert("RGBA"))
        parts = file.stem.split("_")
        group = "_".join(parts[:-1]) if len(parts) >= 4 else file.stem
        groups[group].append(file)

        if not (mode_ok and size_ok and visible_ok):
            ok = False

        rows.append(
            f"| {file.name} | {img.size[0]}x{img.size[1]} | {'通过' if size_ok else '失败'} | {'通过' if mode_ok else '失败'} | {'通过' if visible_ok else '失败'} |"
        )

    lines = [
        "# 序列帧校验报告",
        "",
        f"- 输入目录：`{input_dir}`",
        f"- 期望尺寸：`{args.frame_width}x{args.frame_height}`",
        f"- PNG 文件数：`{len(files)}`",
        f"- 总结论：{'通过' if ok else '失败'}",
        "",
        "## 文件检查",
        "",
        "| 文件 | 实际尺寸 | 尺寸 | Alpha | 非空白 |",
        "|---|---|---|---|---|",
        *rows,
        "",
        "## 分组统计",
        "",
        "| 分组 | 帧数 |",
        "|---|---:|",
    ]

    for group, group_files in sorted(groups.items()):
        lines.append(f"| {group} | {len(group_files)} |")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"校验报告已生成：{report_path}")
    if not ok:
        raise SystemExit("存在校验失败项。")


if __name__ == "__main__":
    main()
