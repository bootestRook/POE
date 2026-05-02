from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.skill_editor import SkillEditorService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Skill Test Arena for a migrated active skill package.")
    parser.add_argument("--skill", default="active_fire_bolt", help="Active skill package id.")
    parser.add_argument("--scenario", default="single_dummy", help="Skill Test Arena scenario id.")
    parser.add_argument("--modifier", action="append", default=[], help="Temporary modifier id; may be repeated.")
    parser.add_argument("--relation", default="adjacent", help="Temporary modifier relation.")
    parser.add_argument("--source-power", default=1.0, type=float, help="Temporary source power.")
    parser.add_argument("--target-power", default=1.0, type=float, help="Temporary target power.")
    parser.add_argument("--conduit-power", default=1.0, type=float, help="Temporary conduit power.")
    args = parser.parse_args()

    service = SkillEditorService(ROOT / "configs")
    result = service.run_test_arena(
        {
            "skill_id": args.skill,
            "scene_id": args.scenario,
            "use_modifier_stack": bool(args.modifier),
            "modifier_ids": args.modifier,
            "relation": args.relation,
            "source_power": args.source_power,
            "target_power": args.target_power,
            "conduit_power": args.conduit_power,
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
