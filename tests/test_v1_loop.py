from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.affixes import AffixGenerator
from liufang.combat import CombatSession, Monster, Player, Position
from liufang.config import (
    load_affix_definitions,
    load_board_rules,
    load_gem_definitions,
    load_rarity_affix_counts,
    load_relation_coefficients,
    load_skill_scaling_rules,
    load_skill_templates,
)
from liufang.gem_board import SudokuGemBoard
from liufang.inventory import GemInventory
from liufang.loot import LootRuntime
from liufang.presentation import PresentationService
from liufang.skill_effects import SkillEffectCalculator


class V1LoopTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config_root = ROOT / "configs"
        self.definitions = load_gem_definitions(self.config_root)
        self.affixes = load_affix_definitions(self.config_root)
        self.inventory = GemInventory(self.definitions)
        self.board = SudokuGemBoard(load_board_rules(self.config_root), self.inventory)
        self.presenter = PresentationService.from_configs(self.config_root)

    def calculator(self) -> SkillEffectCalculator:
        return SkillEffectCalculator(
            board=self.board,
            definitions=self.definitions,
            skill_templates=load_skill_templates(self.config_root),
            relation_coefficients=load_relation_coefficients(self.config_root),
            scaling_rules=load_skill_scaling_rules(self.config_root),
            affix_definitions={definition.affix_id: definition for definition in self.affixes},
        )

    def loot_runtime(self, seed: int = 6) -> LootRuntime:
        return LootRuntime.from_configs(
            self.config_root,
            self.definitions,
            {"normal": 1},
            AffixGenerator(self.affixes, load_rarity_affix_counts(self.config_root), random.Random(seed)),
            rng=random.Random(seed),
        )

    def test_brush_gem_view_affix_adjust_board_combat_pickup_and_recalculate_loop(self) -> None:
        active = self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem(active.instance_id, 0, 0)

        active_detail = self.presenter.gem_detail(active, board=self.board)
        self.assertEqual(active_detail["name_text"], self.presenter.localizer.text("gem.active_fire_bolt.name"))

        first_skills = self.calculator().calculate_all()
        first_board_view = self.presenter.board_view(self.board, final_skills=first_skills)
        first_damage = first_board_view["skill_preview"][0]["final_damage"]
        self.assertTrue(first_board_view["can_enter_combat"])

        session = CombatSession.start(
            player=Player("player_1", current_life=100, max_life=100, position=Position(0, 0), pickup_radius=2),
            monsters=[Monster("monster_1", current_life=5, max_life=5, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(seed=6),
        )
        events = session.tick(1)
        self.assertTrue(events[0].killed)
        self.assertEqual(len(session.dropped_gems), 1)

        drop_prompt = self.presenter.drop_prompt(session.dropped_gems[0])
        self.assertEqual(drop_prompt["status_text"], self.presenter.localizer.text("ui.drop.not_picked"))

        picked = session.pickup_nearby()
        self.assertEqual(len(picked), 1)
        new_gem = picked[0]
        self.assertIn("support_gem", new_gem.tags)

        new_detail = self.presenter.gem_detail(new_gem, board=self.board, final_skills=first_skills)
        self.assertEqual(new_detail["name_text"], self.presenter.localizer.text("gem.support_attack_spell_level.name"))

        self.board.mount_gem(new_gem.instance_id, 0, 3)
        second_skills = self.calculator().calculate_all()
        second_board_view = self.presenter.board_view(self.board, final_skills=second_skills)
        second_damage = second_board_view["skill_preview"][0]["final_damage"]

        self.assertGreater(second_damage, first_damage)
        self.assertTrue(second_board_view["influence_preview"])
        self.assertEqual(
            self.presenter.gem_detail(new_gem, board=self.board, final_skills=second_skills)[
                "current_effective_targets"
            ][0]["name_text"],
            self.presenter.localizer.text("gem.active_fire_bolt.name"),
        )


if __name__ == "__main__":
    unittest.main()
