from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.config import load_skill_packages


def main() -> int:
    try:
        packages = load_skill_packages(ROOT / "configs")
    except Exception as exc:
        print(f"Skill Package validation failed: {exc}")
        return 1
    print("Skill Package validation passed: " + ", ".join(sorted(packages)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
