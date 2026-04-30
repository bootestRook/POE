#!/usr/bin/env python3
"""Generate a local HTML preview for interactively adjusting tile crop boxes."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path

from PIL import Image


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = value.lower().split("x", 1)
        return int(width), int(height)
    except Exception as exc:
        raise argparse.ArgumentTypeError(f"expected WIDTHxHEIGHT, got {value!r}") from exc


def relative_url(from_file: Path, target: Path) -> str:
    rel = os.path.relpath(target.resolve(), from_file.resolve().parent)
    return Path(rel).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cols", type=int, default=4)
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--cell-size", type=parse_size, default=(256, 160))
    parser.add_argument("--tile-size", type=parse_size, default=(128, 64))
    parser.add_argument("--min-tile-size", type=parse_size, default=(64, 32))
    parser.add_argument("--max-tile-size", type=parse_size)
    parser.add_argument("--step", type=int, default=2)
    parser.add_argument("--slice-script", type=Path, default=Path(".codex/skills/make-iso-map-tiles/scripts/slice_iso_tiles.py"))
    args = parser.parse_args()

    raw = Image.open(args.raw)
    expected = (args.cols * args.cell_size[0], args.rows * args.cell_size[1])
    if raw.size != expected:
        raise SystemExit(f"raw size {raw.size} does not match grid {expected}")

    max_tile_size = args.max_tile_size or args.cell_size
    args.out.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "rawUrl": relative_url(args.out, args.raw),
        "rawPath": str(args.raw),
        "sliceScript": str(args.slice_script),
        "cols": args.cols,
        "rows": args.rows,
        "cellWidth": args.cell_size[0],
        "cellHeight": args.cell_size[1],
        "tileWidth": args.tile_size[0],
        "tileHeight": args.tile_size[1],
        "minTileWidth": args.min_tile_size[0],
        "minTileHeight": args.min_tile_size[1],
        "maxTileWidth": max_tile_size[0],
        "maxTileHeight": max_tile_size[1],
        "step": args.step,
    }

    document = HTML_TEMPLATE.replace("__CONFIG_JSON__", html.escape(json.dumps(config), quote=False))
    args.out.write_text(document, encoding="utf-8")
    print(f"preview={args.out}")
    return 0


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Adjustable Tile Crop Preview</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: Segoe UI, Arial, sans-serif;
      background: #1d1d22;
      color: #ececf0;
    }
    body {
      margin: 0;
      display: grid;
      grid-template-columns: minmax(320px, 1fr) 360px;
      min-height: 100vh;
    }
    main {
      overflow: auto;
      padding: 20px;
      background:
        linear-gradient(45deg, #333 25%, transparent 25%),
        linear-gradient(-45deg, #333 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #333 75%),
        linear-gradient(-45deg, transparent 75%, #333 75%),
        #28282d;
      background-position: 0 0, 0 8px, 8px -8px, -8px 0;
      background-size: 16px 16px;
    }
    aside {
      border-left: 1px solid #3d3d45;
      padding: 20px;
      background: #24242a;
    }
    .stage {
      position: relative;
      width: max-content;
      line-height: 0;
    }
    img {
      display: block;
      max-width: none;
    }
    svg {
      position: absolute;
      inset: 0;
      pointer-events: none;
    }
    label {
      display: grid;
      gap: 8px;
      margin: 0 0 18px;
      font-size: 13px;
      color: #cfcfd7;
    }
    .row {
      display: grid;
      grid-template-columns: 1fr 86px;
      gap: 10px;
      align-items: center;
    }
    input[type="number"] {
      width: 100%;
      box-sizing: border-box;
      border: 1px solid #51515b;
      border-radius: 6px;
      background: #18181d;
      color: #f4f4f7;
      padding: 8px;
    }
    input[type="range"] {
      width: 100%;
    }
    pre {
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      border: 1px solid #3e3e47;
      border-radius: 8px;
      background: #18181d;
      padding: 12px;
      line-height: 1.45;
      color: #d8e8ff;
    }
    .stat {
      display: grid;
      grid-template-columns: 140px 1fr;
      gap: 8px;
      margin: 8px 0;
      font-size: 13px;
    }
    button {
      border: 1px solid #4f6f8d;
      border-radius: 6px;
      background: #24445f;
      color: #fff;
      padding: 9px 12px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <main>
    <div class="stage">
      <img id="raw" alt="raw tile sheet" />
      <svg id="overlay"></svg>
    </div>
  </main>
  <aside>
    <h1>Crop Box</h1>
    <label>
      Width
      <div class="row">
        <input id="widthRange" type="range" />
        <input id="widthNumber" type="number" />
      </div>
    </label>
    <label>
      Height
      <div class="row">
        <input id="heightRange" type="range" />
        <input id="heightNumber" type="number" />
      </div>
    </label>
    <div class="stat"><span>Cell</span><strong id="cellStat"></strong></div>
    <div class="stat"><span>Crop</span><strong id="cropStat"></strong></div>
    <div class="stat"><span>Margin in cell</span><strong id="marginStat"></strong></div>
    <button id="copyButton" type="button">Copy Slice Command</button>
    <pre id="command"></pre>
  </aside>
  <script id="config" type="application/json">__CONFIG_JSON__</script>
  <script>
    const config = JSON.parse(document.getElementById("config").textContent);
    const raw = document.getElementById("raw");
    const overlay = document.getElementById("overlay");
    const widthRange = document.getElementById("widthRange");
    const widthNumber = document.getElementById("widthNumber");
    const heightRange = document.getElementById("heightRange");
    const heightNumber = document.getElementById("heightNumber");
    const command = document.getElementById("command");
    const cropStat = document.getElementById("cropStat");
    const cellStat = document.getElementById("cellStat");
    const marginStat = document.getElementById("marginStat");
    const copyButton = document.getElementById("copyButton");

    raw.src = config.rawUrl;
    cellStat.textContent = `${config.cellWidth}x${config.cellHeight}, ${config.cols}x${config.rows}`;

    function setupInput(range, number, min, max, value, step) {
      range.min = min;
      range.max = max;
      range.step = step;
      range.value = value;
      number.min = min;
      number.max = max;
      number.step = step;
      number.value = value;
      range.addEventListener("input", () => {
        number.value = range.value;
        draw();
      });
      number.addEventListener("input", () => {
        range.value = number.value;
        draw();
      });
    }

    function line(x1, y1, x2, y2, color, width) {
      const node = document.createElementNS("http://www.w3.org/2000/svg", "line");
      node.setAttribute("x1", x1);
      node.setAttribute("y1", y1);
      node.setAttribute("x2", x2);
      node.setAttribute("y2", y2);
      node.setAttribute("stroke", color);
      node.setAttribute("stroke-width", width);
      overlay.appendChild(node);
    }

    function rect(x, y, w, h) {
      const node = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      node.setAttribute("x", x);
      node.setAttribute("y", y);
      node.setAttribute("width", w);
      node.setAttribute("height", h);
      node.setAttribute("fill", "none");
      node.setAttribute("stroke", "#00eaff");
      node.setAttribute("stroke-width", 3);
      overlay.appendChild(node);
    }

    function cross(cx, cy) {
      line(cx - 8, cy, cx + 8, cy, "#ffffff", 2);
      line(cx, cy - 8, cx, cy + 8, "#ffffff", 2);
    }

    function draw() {
      const tileWidth = Number(widthNumber.value);
      const tileHeight = Number(heightNumber.value);
      const sheetWidth = config.cols * config.cellWidth;
      const sheetHeight = config.rows * config.cellHeight;
      overlay.setAttribute("width", sheetWidth);
      overlay.setAttribute("height", sheetHeight);
      overlay.setAttribute("viewBox", `0 0 ${sheetWidth} ${sheetHeight}`);
      overlay.replaceChildren();

      for (let col = 0; col <= config.cols; col += 1) {
        const x = col * config.cellWidth;
        line(x, 0, x, sheetHeight, "#ff3030", 3);
      }
      for (let row = 0; row <= config.rows; row += 1) {
        const y = row * config.cellHeight;
        line(0, y, sheetWidth, y, "#ff3030", 3);
      }
      for (let row = 0; row < config.rows; row += 1) {
        for (let col = 0; col < config.cols; col += 1) {
          const left = col * config.cellWidth + Math.floor((config.cellWidth - tileWidth) / 2);
          const top = row * config.cellHeight + Math.floor((config.cellHeight - tileHeight) / 2);
          rect(left, top, tileWidth, tileHeight);
          cross(col * config.cellWidth + Math.floor(config.cellWidth / 2), row * config.cellHeight + Math.floor(config.cellHeight / 2));
        }
      }

      cropStat.textContent = `${tileWidth}x${tileHeight}`;
      marginStat.textContent = `${Math.floor((config.cellWidth - tileWidth) / 2)}px x ${Math.floor((config.cellHeight - tileHeight) / 2)}px`;
      command.textContent = [
        "python", config.sliceScript,
        "--raw", config.rawPath,
        "--mode slice",
        "--confirmed",
        "--cols", config.cols,
        "--rows", config.rows,
        "--cell-size", `${config.cellWidth}x${config.cellHeight}`,
        "--tile-size", `${tileWidth}x${tileHeight}`,
        "--safe-size", `${tileWidth}x${tileHeight}`
      ].join(" ");
    }

    copyButton.addEventListener("click", async () => {
      await navigator.clipboard.writeText(command.textContent);
    });

    setupInput(widthRange, widthNumber, config.minTileWidth, config.maxTileWidth, config.tileWidth, config.step);
    setupInput(heightRange, heightNumber, config.minTileHeight, config.maxTileHeight, config.tileHeight, config.step);
    draw();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
