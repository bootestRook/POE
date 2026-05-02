from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.gem_combination_report import (  # noqa: E402
    generate_gem_combination_report,
    report_to_json,
    report_to_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a non-destructive gem combination effect report.")
    parser.add_argument("--config-root", default=str(ROOT / "configs"), help="Config root to read.")
    parser.add_argument("--markdown", help="Optional Markdown report output path.")
    args = parser.parse_args()

    report = generate_gem_combination_report(Path(args.config_root))
    print(report_to_json(report))
    if args.markdown:
        output_path = Path(args.markdown)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_to_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
