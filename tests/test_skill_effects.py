from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.config import (
    SkillScalingRules,
    SupportBaseModifier,
    load_behavior_templates,
    load_affix_definitions,
    load_board_rules,
    load_gem_definitions,
    load_relation_coefficients,
    load_skill_scaling_rules,
    load_skill_packages,
    load_skill_schema,
    load_skill_templates,
    validate_skill_package_data,
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

    def test_active_fire_bolt_loads_from_skill_package(self) -> None:
        packages = load_skill_packages(self.config_root)
        templates = load_skill_templates(self.config_root)

        self.assertEqual(set(packages), {"active_fire_bolt", "active_ice_shards", "active_penetrating_shot", "active_frost_nova"})
        self.assertEqual(packages["active_fire_bolt"]["behavior"]["template"], "projectile")
        self.assertEqual(packages["active_ice_shards"]["behavior"]["template"], "fan_projectile")
        self.assertEqual(packages["active_penetrating_shot"]["behavior"]["template"], "projectile")
        self.assertEqual(packages["active_frost_nova"]["behavior"]["template"], "player_nova")
        self.assertEqual(packages["active_penetrating_shot"]["behavior"]["params"]["hit_policy"], "pierce")
        self.assertEqual(templates["skill_fire_bolt"].skill_package_id, "active_fire_bolt")
        self.assertEqual(templates["skill_fire_bolt"].behavior_template, "projectile")
        self.assertEqual(templates["skill_ice_shards"].skill_package_id, "active_ice_shards")
        self.assertEqual(templates["skill_ice_shards"].behavior_template, "fan_projectile")
        self.assertEqual(templates["skill_ice_shards"].damage_type, "cold")
        self.assertEqual(templates["skill_penetrating_shot"].skill_package_id, "active_penetrating_shot")
        self.assertEqual(templates["skill_penetrating_shot"].behavior_template, "projectile")
        self.assertEqual(templates["skill_penetrating_shot"].damage_type, "physical")
        self.assertEqual(templates["skill_frost_nova"].skill_package_id, "active_frost_nova")
        self.assertEqual(templates["skill_frost_nova"].behavior_template, "player_nova")
        self.assertEqual(templates["skill_frost_nova"].damage_type, "cold")

    def test_skill_package_schema_rejects_missing_required_field(self) -> None:
        package = deepcopy(load_skill_packages(self.config_root)["active_fire_bolt"])
        del package["hit"]["base_damage"]

        with self.assertRaisesRegex(ValueError, "hit.base_damage"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

    def test_skill_package_schema_rejects_invalid_behavior_template(self) -> None:
        package = deepcopy(load_skill_packages(self.config_root)["active_fire_bolt"])
        package["behavior"]["template"] = "scripted_projectile"

        with self.assertRaisesRegex(ValueError, "behavior.template"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

    def test_skill_package_schema_rejects_invalid_behavior_params(self) -> None:
        package = deepcopy(load_skill_packages(self.config_root)["active_fire_bolt"])
        package["behavior"]["params"]["script"] = "deal_damage()"

        with self.assertRaisesRegex(ValueError, "script"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

    def test_fan_projectile_schema_rejects_unknown_fields_and_invalid_values(self) -> None:
        package = deepcopy(load_skill_packages(self.config_root)["active_ice_shards"])
        package["behavior"]["params"]["forbidden_param"] = 1

        with self.assertRaisesRegex(ValueError, "unsupported parameter"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

        package = deepcopy(load_skill_packages(self.config_root)["active_ice_shards"])
        package["behavior"]["params"]["projectile_count"] = 0
        with self.assertRaisesRegex(ValueError, "projectile_count"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

        package = deepcopy(load_skill_packages(self.config_root)["active_ice_shards"])
        package["behavior"]["params"]["spread_angle"] = 181
        with self.assertRaisesRegex(ValueError, "spread_angle"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

        package = deepcopy(load_skill_packages(self.config_root)["active_ice_shards"])
        package["behavior"]["params"]["hit_policy"] = "chain"
        with self.assertRaisesRegex(ValueError, "hit_policy"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

    def test_player_nova_schema_rejects_unknown_fields_and_invalid_values(self) -> None:
        package = deepcopy(load_skill_packages(self.config_root)["active_frost_nova"])
        package["behavior"]["params"]["forbidden_param"] = 1

        with self.assertRaisesRegex(ValueError, "unsupported parameter"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

        package = deepcopy(load_skill_packages(self.config_root)["active_frost_nova"])
        package["behavior"]["params"]["radius"] = 0
        with self.assertRaisesRegex(ValueError, "radius"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

        package = deepcopy(load_skill_packages(self.config_root)["active_frost_nova"])
        package["behavior"]["params"]["hit_at_ms"] = package["behavior"]["params"]["expand_duration_ms"] + 1
        with self.assertRaisesRegex(ValueError, "hit_at_ms"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
            )

        package = deepcopy(load_skill_packages(self.config_root)["active_frost_nova"])
        package["behavior"]["params"]["center_policy"] = "target_point"
        with self.assertRaisesRegex(ValueError, "center_policy"):
            validate_skill_package_data(
                package,
                load_skill_schema(self.config_root),
                load_behavior_templates(self.config_root),
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

    def test_support_base_and_conduit_apply_without_random_affixes(self) -> None:
        active = self.inventory.add_instance("active", "active_fire_bolt")
        support = self.inventory.add_instance("support", "support_fire_mastery")
        self.inventory.add_instance("conduit", "support_row_conduit")
        self.board.mount_gem(active.instance_id, 0, 0)
        self.board.mount_gem(support.instance_id, 0, 3)
        self.board.mount_gem("conduit", 0, 6)

        final_skill = self.calculator.calculate_all()[0]
        self.assertEqual(final_skill.active_gem_instance_id, "active")
        self.assertEqual(final_skill.skill_template_id, "skill_fire_bolt")
        self.assertEqual(final_skill.skill_package_id, "active_fire_bolt")
        self.assertEqual(final_skill.skill_package_version, "1.0.0")
        self.assertEqual(final_skill.behavior_template, "projectile")
        self.assertEqual(final_skill.cast["target_selector"], "nearest_enemy")
        self.assertEqual(final_skill.hit["base_damage"], 12)
        package_count = load_skill_packages(self.config_root)["active_fire_bolt"]["behavior"]["params"]["projectile_count"]
        self.assertEqual(final_skill.projectile_count, package_count)
        self.assertEqual(final_skill.runtime_params["max_targets"], 1)
        self.assertEqual(final_skill.presentation_keys["floating_text"], "skill_event.fire_bolt.floating_text")
        self.assertEqual(final_skill.source_context["gem_kind"], "active_skill")
        self.assertEqual(final_skill.source_context["sudoku_digit"], 1)
        self.assertEqual(final_skill.base_damage, 12)
        self.assertAlmostEqual(final_skill.final_damage, 14.7, places=3)
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
        self.assertFalse(any("affix" in modifier.reason_key for modifier in final_skill.applied_modifiers))

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
        self.inventory.add_instance("support", "support_overcharge")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("support", 0, 3)

        duplicate_rules = SkillScalingRules(
            stat_layers=self.calculator.scaling_rules.stat_layers,
            support_base_modifiers=self.calculator.scaling_rules.support_base_modifiers
            + (SupportBaseModifier("support_overcharge", "damage_final_percent", 5, "final"),),
            conduit_amplifiers=self.calculator.scaling_rules.conduit_amplifiers,
        )
        self.calculator.scaling_rules = duplicate_rules

        final_skill = self.calculator.calculate_all()[0]
        damage_final_modifiers = [
            modifier for modifier in final_skill.applied_modifiers if modifier.stat == "damage_final_percent"
        ]
        self.assertEqual(len(damage_final_modifiers), 2)
        self.assertTrue(damage_final_modifiers[0].applied)
        self.assertFalse(damage_final_modifiers[1].applied)
        self.assertEqual(damage_final_modifiers[1].reason_key, "modifier.ignored.duplicate_source_target_stat")

    def test_final_skill_output_contains_core_fields(self) -> None:
        self.inventory.add_instance("active", "active_ice_shards")
        self.inventory.add_instance("support", "support_extra_projectile")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("support", 0, 3)

        final_skill = self.calculator.calculate_all()[0]
        self.assertEqual(final_skill.base_gem_id, "active_ice_shards")
        self.assertEqual(final_skill.skill_package_id, "active_ice_shards")
        self.assertEqual(final_skill.behavior_template, "fan_projectile")
        self.assertEqual(final_skill.projectile_count, 4)
        expected_spread_angle = load_skill_packages(self.config_root)["active_ice_shards"]["behavior"]["params"]["spread_angle"]
        self.assertEqual(final_skill.runtime_params["spread_angle"], expected_spread_angle)
        self.assertGreater(final_skill.final_cooldown_ms, 0)
        self.assertGreater(final_skill.area_multiplier, 0)
        self.assertIsInstance(final_skill.applied_modifiers, tuple)

    def test_passive_to_active_and_support_to_passive_are_applied_in_order(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance("passive", "passive_fire_focus")
        self.inventory.add_instance("support", "support_fire_mastery")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("passive", 1, 0)
        self.board.mount_gem("support", 1, 3)

        final_skill = self.calculator.calculate_all()[0]
        support_to_passive = [
            modifier for modifier in final_skill.applied_modifiers if modifier.reason_key == "modifier.support_to_passive"
        ]
        passive_to_active = [
            modifier for modifier in final_skill.applied_modifiers if modifier.reason_key == "modifier.passive_base"
        ]

        self.assertTrue(support_to_passive)
        self.assertTrue(passive_to_active)
        self.assertLess(
            final_skill.applied_modifiers.index(support_to_passive[0]),
            final_skill.applied_modifiers.index(passive_to_active[0]),
        )
        self.assertEqual(support_to_passive[0].target_instance_id, "passive")
        self.assertEqual(passive_to_active[0].source_instance_id, "passive")
        self.assertEqual(passive_to_active[0].target_instance_id, "active")
        self.assertGreater(final_skill.final_damage, 12)

    def test_support_to_support_and_passive_recursive_routes_are_forbidden(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance("passive_a", "passive_fire_focus")
        self.inventory.add_instance("passive_b", "passive_vitality")
        self.inventory.add_instance("support_a", "support_fire_mastery")
        self.inventory.add_instance("support_b", "support_fast_cast")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("passive_a", 1, 0)
        self.board.mount_gem("passive_b", 1, 1)
        self.board.mount_gem("support_a", 1, 3)
        self.board.mount_gem("support_b", 1, 4)

        final_skill = self.calculator.calculate_all()[0]
        routes = {(modifier.source_instance_id, modifier.target_instance_id) for modifier in final_skill.applied_modifiers}

        self.assertNotIn(("support_a", "support_b"), routes)
        self.assertNotIn(("support_b", "support_a"), routes)
        self.assertNotIn(("passive_b", "passive_a"), routes)
        self.assertNotIn(("passive_a", "passive_b"), routes)

    def test_passive_self_stats_update_player_attributes(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance("life", "passive_vitality")
        self.inventory.add_instance("speed", "passive_swift_gathering")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("life", 1, 0)
        self.board.mount_gem("speed", 2, 0)

        class PlayerStub:
            current_life = 100
            max_life = 100
            move_speed = 1.0

        player = PlayerStub()
        modifiers = self.calculator.apply_player_stat_contributions(player)

        self.assertEqual({modifier.stat for modifier in modifiers}, {"max_life", "move_speed"})
        self.assertEqual(player.max_life, 125)
        self.assertEqual(player.current_life, 125)
        self.assertAlmostEqual(player.move_speed, 1.1)

    def test_each_active_skill_has_five_visible_shape_supports(self) -> None:
        active_skill_tags = {
            "active_fire_bolt": "skill_fire_bolt",
            "active_ice_shards": "skill_ice_shards",
            "active_lightning_chain": "skill_lightning_chain",
            "active_frost_nova": "skill_frost_nova",
            "active_puncture": "skill_puncture",
            "active_penetrating_shot": "skill_penetrating_shot",
            "active_lava_orb": "skill_lava_orb",
            "active_fungal_petards": "skill_fungal_petards",
        }

        for active_id, skill_tag in active_skill_tags.items():
            with self.subTest(active_id=active_id):
                inventory = GemInventory(self.definitions)
                board = SudokuGemBoard(load_board_rules(self.config_root), inventory)
                calculator = SkillEffectCalculator(
                    board=board,
                    definitions=self.definitions,
                    skill_templates=load_skill_templates(self.config_root),
                    relation_coefficients=load_relation_coefficients(self.config_root),
                    scaling_rules=load_skill_scaling_rules(self.config_root),
                    affix_definitions={},
                )
                shape_supports = [
                    definition
                    for definition in self.definitions.values()
                    if definition.category == "skill_shape_modifier"
                    and skill_tag in definition.apply_filter_tags_all
                ]

                self.assertEqual(len(shape_supports), 5)
                inventory.add_instance("active", active_id)
                board.mount_gem("active", 0, 0)
                for index, support_definition in enumerate(
                    sorted(shape_supports, key=lambda definition: definition.sudoku_digit)
                ):
                    instance_id = f"shape_{index}"
                    inventory.add_instance(instance_id, support_definition.base_gem_id)
                    board.mount_gem(instance_id, 0, index + 1)

                final_skill = calculator.calculate_all()[0]

                self.assertEqual(
                    set(final_skill.shape_effects),
                    {definition.shape_effect for definition in shape_supports},
                )

    def test_only_active_skill_gems_generate_final_skill_instances(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance("passive", "passive_fire_focus")
        self.inventory.add_instance("support", "support_fire_mastery")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("passive", 1, 0)
        self.board.mount_gem("support", 1, 3)

        final_skills = self.calculator.calculate_all()

        self.assertEqual(len(final_skills), 1)
        self.assertEqual(final_skills[0].active_gem_instance_id, "active")


if __name__ == "__main__":
    unittest.main()
