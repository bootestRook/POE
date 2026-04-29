from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.combat import Position
from liufang.config import (
    load_affix_definitions,
    load_board_rules,
    load_gem_definitions,
    load_relation_coefficients,
    load_skill_scaling_rules,
    load_skill_templates,
)
from liufang.gem_board import SudokuGemBoard
from liufang.inventory import GemInventory
from liufang.skill_effects import SkillEffectCalculator
from liufang.skill_runtime import SkillRuntime


class SkillRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config_root = ROOT / "configs"
        self.definitions = load_gem_definitions(self.config_root)
        self.inventory = GemInventory(self.definitions)
        self.board = SudokuGemBoard(load_board_rules(self.config_root), self.inventory)
        self.calculator = SkillEffectCalculator(
            board=self.board,
            definitions=self.definitions,
            skill_templates=load_skill_templates(self.config_root),
            relation_coefficients=load_relation_coefficients(self.config_root),
            scaling_rules=load_skill_scaling_rules(self.config_root),
            affix_definitions={
                definition.affix_id: definition
                for definition in load_affix_definitions(self.config_root)
            },
        )

    def test_fire_bolt_projectile_outputs_required_skill_events(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        final_skill = self.calculator.calculate_all()[0]

        events = SkillRuntime().execute(
            final_skill,
            source_entity="player_1",
            source_position=Position(0, 0),
            target_entity="monster_1",
            target_position=Position(100, 0),
            timestamp_ms=10,
        )

        expected_spawn_count = final_skill.projectile_count
        self.assertEqual(
            [event.type for event in events],
            ["projectile_spawn"] * expected_spawn_count + ["damage", "hit_vfx", "floating_text"] * expected_spawn_count,
        )
        spawn = events[0]
        impact_events = events[expected_spawn_count:]
        damage, hit_vfx, floating_text = impact_events[:3]
        runtime_params = final_skill.runtime_params or {}
        projectile_speed = max(1.0, float(runtime_params.get("projectile_speed", 720.0)))
        burst_interval_ms = max(0, int(runtime_params.get("burst_interval_ms", 0)))
        spread_angle_deg = max(0.0, float(runtime_params.get("spread_angle_deg", 0.0)))
        expected_duration_ms = round(100 / projectile_speed * 1000)
        expected_duration_ms = max(
            int(runtime_params.get("min_duration_ms", 0)),
            min(expected_duration_ms, int(runtime_params.get("max_duration_ms", 1000))),
        )
        self.assertEqual(spawn.position, {"x": 0.0, "y": 0.0})
        self.assertEqual(spawn.payload["projectile_count"], expected_spawn_count)
        if expected_spawn_count > 1:
            self.assertEqual(events[1].delay_ms, burst_interval_ms)
            if spread_angle_deg > 0:
                self.assertNotEqual(spawn.payload["end_position"], {"x": 100.0, "y": 0.0})
                self.assertNotEqual(events[0].direction, events[1].direction)
            self.assertEqual(events[0].payload["spread_angle_deg"], spread_angle_deg)
            self.assertEqual(impact_events[-3].payload["projectile_index"], expected_spawn_count)
            self.assertEqual(impact_events[-3].delay_ms, expected_duration_ms + burst_interval_ms * (expected_spawn_count - 1))
        else:
            self.assertEqual(spawn.payload["end_position"], {"x": 100.0, "y": 0.0})
        self.assertEqual(spawn.duration_ms, expected_duration_ms)
        self.assertEqual(damage.delay_ms, spawn.duration_ms)
        self.assertEqual(damage.timestamp_ms, 10 + expected_duration_ms)
        self.assertEqual(damage.target_entity, "monster_1")
        self.assertEqual(damage.amount, final_skill.final_damage)
        self.assertEqual(damage.damage_type, "fire")
        self.assertEqual(damage.reason_key, "skill_event.fire_bolt.damage_reason")
        self.assertEqual(hit_vfx.delay_ms, damage.delay_ms)
        self.assertEqual(floating_text.delay_ms, damage.delay_ms)
        self.assertIn("火焰伤害", floating_text.payload["text"])


    def test_fire_bolt_projectile_multi_target_runtime_respects_pierce_and_projectile_count(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        final_skill = self.calculator.calculate_all()[0]
        runtime_params = dict(final_skill.runtime_params or {})
        runtime_params["projectile_count"] = 2
        runtime_params["hit_policy"] = "pierce"
        runtime_params["pierce_count"] = 1
        final_skill = final_skill.__class__(
            **{**final_skill.__dict__, "projectile_count": 2, "runtime_params": runtime_params}
        )

        events = SkillRuntime().execute(
            final_skill,
            source_entity="player_1",
            source_position=Position(0, 0),
            target_entity="monster_1",
            target_position=Position(100, 0),
            timestamp_ms=10,
            target_entities=[
                {"entity_id": "monster_1", "position": {"x": 100, "y": 0}},
                {"entity_id": "monster_2", "position": {"x": 160, "y": 0}},
            ],
        )

        damage_events = [event for event in events if event.type == "damage"]
        spawn_events = [event for event in events if event.type == "projectile_spawn"]
        self.assertEqual(len(spawn_events), 2)
        self.assertEqual(len(damage_events), 4)
        self.assertEqual({event.target_entity for event in damage_events}, {"monster_1", "monster_2"})


if __name__ == "__main__":
    unittest.main()
