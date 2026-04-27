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
    load_skill_scaling_rules,
    load_relation_coefficients,
    load_skill_templates,
)
from liufang.gem_board import SudokuGemBoard
from liufang.inventory import AffixRoll, GemInventory
from liufang.loot import LootRuntime
from liufang.presentation import PresentationService
from liufang.skill_effects import SkillEffectCalculator


class PresentationTest(unittest.TestCase):
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

    def test_gem_detail_uses_localized_names_affixes_targets_and_filters(self) -> None:
        active = self.inventory.add_instance(
            "active",
            "active_fire_bolt",
            rarity="magic",
            prefix_affixes=(
                AffixRoll("affix_damage_percent_t1", "damage_add_percent", 10, "prefix", "damage_scaling"),
            ),
        )
        support = self.inventory.add_instance("support", "support_fire_mastery")
        self.board.mount_gem(active.instance_id, 0, 0)
        self.board.mount_gem(support.instance_id, 0, 3)
        final_skills = self.calculator().calculate_all()

        active_detail = self.presenter.gem_detail(active, board=self.board, final_skills=final_skills)
        self.assertEqual(active_detail["name_text"], self.presenter.localizer.text("gem.active_fire_bolt.name"))
        self.assertEqual(active_detail["category_text"], self.presenter.localizer.text("tag.active_skill_gem.name"))
        self.assertEqual(active_detail["gem_type"]["number"], 1)
        self.assertEqual(len(active_detail["random_affixes"]), 1)
        self.assertEqual(
            active_detail["random_affixes"][0]["name_text"],
            self.presenter.localizer.text("affix.damage_percent.t1.name"),
        )
        self.assertTrue(active_detail["current_effective_targets"])

        support_detail = self.presenter.gem_detail(support, board=self.board, final_skills=final_skills)
        self.assertEqual(support_detail["category_text"], self.presenter.localizer.text("tag.support_gem.name"))
        self.assertEqual(
            support_detail["can_affect"]["tags_any"][0]["text"],
            self.presenter.localizer.text("tag.fire.name"),
        )
        self.assertEqual(
            support_detail["current_effective_targets"][0]["name_text"],
            self.presenter.localizer.text("gem.active_fire_bolt.name"),
        )

    def test_board_view_includes_grid_boxes_prompts_highlights_influence_and_skill_preview(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance("support", "support_fire_mastery")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("support", 0, 3)
        final_skills = self.calculator().calculate_all()

        view = self.presenter.board_view(self.board, final_skills=final_skills)
        self.assertEqual(len(view["cells"]), 9)
        self.assertEqual(len(view["cells"][0]), 9)
        self.assertEqual(len(view["boxes"]), 9)
        self.assertEqual(view["prompts"], [self.presenter.localizer.text("ui.board.valid")])
        self.assertTrue(view["highlights"]["same_row"])
        self.assertTrue(view["influence_preview"])
        self.assertEqual(
            view["skill_preview"][0]["name_text"],
            self.presenter.localizer.text("gem.active_fire_bolt.name"),
        )

    def test_board_view_shows_localized_invalid_prompt(self) -> None:
        self.inventory.add_instance("support", "support_fast_attack")
        self.board.mount_gem("support", 0, 0)

        view = self.presenter.board_view(self.board)
        self.assertFalse(view["can_enter_combat"])
        self.assertIn(self.presenter.localizer.text("board.enter_combat.no_active_skill"), view["prompts"])

    def test_combat_hud_and_drop_prompt_use_localized_text(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        session = CombatSession.start(
            player=Player("player_1", current_life=100, max_life=100, position=Position(0, 0), pickup_radius=2),
            monsters=[Monster("monster_1", current_life=5, max_life=5, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(),
        )

        session.tick(1)
        hud = self.presenter.combat_hud(session)
        self.assertEqual(hud["player_life"]["label_text"], self.presenter.localizer.text("ui.hud.player_life"))
        self.assertEqual(hud["alive_monsters"]["value"], 0)
        self.assertEqual(hud["drop_prompts"][0]["status_text"], self.presenter.localizer.text("ui.drop.not_picked"))
        self.assertEqual(hud["pickup_prompts"][0]["status_text"], self.presenter.localizer.text("ui.pickup.pending"))

        session.pickup_nearby()
        picked_prompt = self.presenter.drop_prompt(session.dropped_gems[0])
        self.assertEqual(picked_prompt["status_text"], self.presenter.localizer.text("ui.drop.picked"))
        self.assertEqual(
            picked_prompt["inventory_result_text"],
            self.presenter.localizer.text("ui.pickup.success"),
        )


if __name__ == "__main__":
    unittest.main()
