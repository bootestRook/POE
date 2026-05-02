from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.skill_expression_calibration import (  # noqa: E402
    calibrate_skill_expression,
    calibration_report_to_markdown,
    report_to_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate current-POV skill expression calibration recommendations.")
    parser.add_argument("--config-root", default=str(ROOT / "configs"), help="Config root to read.")
    parser.add_argument("--markdown", help="Optional Markdown report output path.")
    args = parser.parse_args()

    report = calibrate_skill_expression(Path(args.config_root))
    print(report_to_json(report))
    if args.markdown:
        output_path = Path(args.markdown)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(calibration_report_to_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
