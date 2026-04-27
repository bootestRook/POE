from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.config import (
    load_affix_definitions,
    load_board_rules,
    load_gem_definitions,
    load_relation_coefficients,
    load_skill_scaling_rules,
    load_skill_templates,
)
from liufang.gem_board import SudokuGemBoard
from liufang.inventory import AffixRoll, GemInventory
from liufang.skill_effects import SkillEffectCalculator, SkillEffectError


class SkillEffectTest(unittest.TestCase):
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

    def test_invalid_or_empty_board_does_not_output_combat_skill(self) -> None:
        with self.assertRaises(SkillEffectError) as empty_error:
            self.calculator.calculate_all()
        self.assertEqual(empty_error.exception.error_key, "board.enter_combat.empty_board")

        self.inventory.add_instance("active_a", "active_fire_bolt")
        self.inventory.add_instance("active_b", "active_ice_shards")
        self.board.mount_gem("active_a", 0, 0)
        self.board.mount_gem("active_b", 0, 1)

        with self.assertRaises(SkillEffectError) as invalid_error:
            self.calculator.calculate_all()
        self.assertEqual(invalid_error.exception.error_key, "skill_effect.error.invalid_board")

    def test_active_self_affix_support_affix_source_target_power_and_conduit_are_applied(self) -> None:
        active = self.inventory.add_instance(
            "active",
            "active_fire_bolt",
            prefix_affixes=(
                AffixRoll("affix_damage_percent_t1", "damage_add_percent", 10, "prefix", "damage_scaling"),
            ),
            suffix_affixes=(
                AffixRoll("affix_row_target_power_t1", "target_power_row", 20, "suffix", "relation_target"),
            ),
        )
        support = self.inventory.add_instance(
            "support",
            "support_fire_mastery",
            prefix_affixes=(
                AffixRoll("affix_damage_percent_t1", "damage_add_percent", 5, "prefix", "damage_scaling"),
            ),
            suffix_affixes=(
                AffixRoll("affix_row_source_power_t1", "source_power_row", 10, "suffix", "relation_source"),
            ),
        )
        self.inventory.add_instance("conduit", "support_row_conduit")
        self.board.mount_gem(active.instance_id, 0, 0)
        self.board.mount_gem(support.instance_id, 0, 3)
        self.board.mount_gem("conduit", 0, 6)

        final_skill = self.calculator.calculate_all()[0]
        self.assertEqual(final_skill.active_gem_instance_id, "active")
        self.assertEqual(final_skill.skill_template_id, "skill_fire_bolt")
        self.assertEqual(final_skill.base_damage, 12)
        self.assertAlmostEqual(final_skill.final_damage, 17.754, places=3)
        self.assertTrue(
            any(modifier.reason_key == "modifier.conduit_amplifier" for modifier in final_skill.applied_modifiers)
        )
        self.assertTrue(
            any(
                modifier.source_instance_id == "support"
                and modifier.target_instance_id == "active"
                and modifier.stat == "fire_damage_add_percent"
                and modifier.relation == "same_row"
                for modifier in final_skill.applied_modifiers
            )
        )
        self.assertTrue(
            any(
                modifier.stat == "target_power_row"
                and modifier.reason_key == "modifier.ignored.board_power_trace"
                for modifier in final_skill.applied_modifiers
            )
        )

    def test_apply_filter_blocks_non_matching_support(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance("support", "support_fast_attack")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("support", 0, 3)

        final_skill = self.calculator.calculate_all()[0]
        self.assertEqual(final_skill.final_damage, 12)
        self.assertFalse(
            any(modifier.source_base_gem_id == "support_fast_attack" for modifier in final_skill.applied_modifiers)
        )

    def test_adjacent_relation_takes_priority_over_row_column_or_box(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance(
            "support",
            "support_fast_cast",
            suffix_affixes=(
                AffixRoll("affix_row_source_power_t1", "source_power_row", 50, "suffix", "relation_source"),
            ),
        )
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("support", 0, 1)

        final_skill = self.calculator.calculate_all()[0]
        cast_modifier = next(
            modifier for modifier in final_skill.applied_modifiers if modifier.stat == "cast_speed_add_percent"
        )
        self.assertEqual(cast_modifier.relation, "adjacent")
        self.assertAlmostEqual(cast_modifier.value, 18.75)
        self.assertAlmostEqual(final_skill.speed_multiplier, 1.1875)

    def test_same_source_target_stat_is_settled_once(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance(
            "support",
            "support_overcharge",
            suffix_affixes=(
                AffixRoll("affix_overload_cost_t1", "added_cooldown_ms", 100, "suffix", "risk_reward"),
            ),
        )
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("support", 0, 3)

        final_skill = self.calculator.calculate_all()[0]
        added_cooldown_modifiers = [
            modifier for modifier in final_skill.applied_modifiers if modifier.stat == "added_cooldown_ms"
        ]
        self.assertEqual(len(added_cooldown_modifiers), 2)
        self.assertTrue(added_cooldown_modifiers[0].applied)
        self.assertFalse(added_cooldown_modifiers[1].applied)
        self.assertEqual(added_cooldown_modifiers[1].reason_key, "modifier.ignored.duplicate_source_target_stat")

    def test_final_skill_output_contains_core_fields(self) -> None:
        self.inventory.add_instance("active", "active_ice_shards")
        self.inventory.add_instance("support", "support_extra_projectile")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("support", 0, 3)

        final_skill = self.calculator.calculate_all()[0]
        self.assertEqual(final_skill.base_gem_id, "active_ice_shards")
        self.assertEqual(final_skill.projectile_count, 2)
        self.assertGreater(final_skill.final_cooldown_ms, 0)
        self.assertGreater(final_skill.area_multiplier, 0)
        self.assertIsInstance(final_skill.applied_modifiers, tuple)


if __name__ == "__main__":
    unittest.main()
