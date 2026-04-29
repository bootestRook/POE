from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.skill_test_report import SkillTestReportRequest, write_skill_test_report


def main() -> int:
    parser = argparse.ArgumentParser(description="生成技能自测报告。")
    parser.add_argument("--skill", default="active_fire_bolt", help="测试技能 ID。")
    parser.add_argument("--scenario", default="single_dummy", help="测试场景 ID。")
    parser.add_argument("--modifier", action="append", default=[], help="加入一个测试 Modifier，可重复传入。")
    parser.add_argument("--relation", default="adjacent", help="模拟关系。")
    parser.add_argument("--source-power", default=1.0, type=float, help="来源强度。")
    parser.add_argument("--target-power", default=1.0, type=float, help="目标强度。")
    parser.add_argument("--conduit-power", default=1.0, type=float, help="导管强度。")
    parser.add_argument("--output-dir", default=str(ROOT / "reports" / "skill_tests"), help="报告输出目录。")
    args = parser.parse_args()

    request = SkillTestReportRequest(
        skill_id=args.skill,
        scenario_id=args.scenario,
        use_modifier_stack=bool(args.modifier),
        modifier_ids=tuple(args.modifier),
        relation=args.relation,
        source_power=args.source_power,
        target_power=args.target_power,
        conduit_power=args.conduit_power,
    )
    output_path = write_skill_test_report(ROOT / "configs", request, Path(args.output_dir))
    print(f"技能自测报告已生成：{output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
