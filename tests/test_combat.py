from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.affixes import AffixGenerator
from liufang.combat import CombatSession, CombatStartError, Monster, Player, Position
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
from liufang.skill_effects import SkillEffectCalculator


class CombatTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config_root = ROOT / "configs"
        self.definitions = load_gem_definitions(self.config_root)
        self.inventory = GemInventory(self.definitions)
        self.board = SudokuGemBoard(load_board_rules(self.config_root), self.inventory)
        self.affix_definitions = load_affix_definitions(self.config_root)

    def calculator(self) -> SkillEffectCalculator:
        return SkillEffectCalculator(
            board=self.board,
            definitions=self.definitions,
            skill_templates=load_skill_templates(self.config_root),
            relation_coefficients=load_relation_coefficients(self.config_root),
            scaling_rules=load_skill_scaling_rules(self.config_root),
            affix_definitions={definition.affix_id: definition for definition in self.affix_definitions},
        )

    def loot_runtime(self, seed: int = 1) -> LootRuntime:
        generator = AffixGenerator(
            self.affix_definitions,
            load_rarity_affix_counts(self.config_root),
            random.Random(seed),
        )
        return LootRuntime.from_configs(
            self.config_root,
            self.definitions,
            {"normal": 1},
            generator,
            rng=random.Random(seed),
        )

    def player(self, pickup_radius: float = 2.0) -> Player:
        return Player(
            player_id="player_1",
            current_life=100,
            max_life=100,
            position=Position(0, 0),
            pickup_radius=pickup_radius,
        )

    def test_start_requires_legal_board_and_active_skill(self) -> None:
        with self.assertRaises(CombatStartError) as empty_error:
            CombatSession.start(
                player=self.player(),
                monsters=[],
                inventory=self.inventory,
                skill_effect_calculator=self.calculator(),
                loot_runtime=self.loot_runtime(),
            )
        self.assertEqual(empty_error.exception.error_key, "board.enter_combat.empty_board")

        self.inventory.add_instance("support", "support_fast_attack")
        self.board.mount_gem("support", 0, 0)
        with self.assertRaises(CombatStartError) as no_active_error:
            CombatSession.start(
                player=self.player(),
                monsters=[],
                inventory=self.inventory,
                skill_effect_calculator=self.calculator(),
                loot_runtime=self.loot_runtime(),
            )
        self.assertEqual(no_active_error.exception.error_key, "board.enter_combat.no_active_skill")

    def test_auto_release_uses_final_skill_instance_and_cooldown(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        session = CombatSession.start(
            player=self.player(),
            monsters=[Monster("monster_1", current_life=30, max_life=30, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(),
        )

        first_events = session.tick(1)
        self.assertEqual(len(first_events), 1)
        self.assertEqual(first_events[0].skill_instance.active_gem_instance_id, "active")
        self.assertEqual(first_events[0].damage, session.active_skill_instances[0].final_damage)
        self.assertEqual(session.monsters[0].current_life, 18)

        second_events = session.tick(100)
        self.assertEqual(second_events, ())

    def test_kill_triggers_gem_drop_and_pickup_enters_inventory(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        session = CombatSession.start(
            player=self.player(pickup_radius=2.0),
            monsters=[Monster("monster_1", current_life=5, max_life=5, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(seed=3),
        )

        events = session.tick(1)
        self.assertTrue(events[0].killed)
        self.assertFalse(session.monsters[0].is_alive)
        self.assertEqual(len(session.dropped_gems), 1)
        dropped = session.dropped_gems[0]
        self.assertFalse(dropped.picked_up)
        self.assertIn("gem", dropped.gem_instance.tags)
        self.assertIn(dropped.gem_instance.rarity, {"normal", "magic", "rare"})

        picked = session.pickup_nearby()
        self.assertEqual(len(picked), 1)
        self.assertTrue(dropped.picked_up)
        stored = self.inventory.require(dropped.gem_instance.instance_id)
        self.assertEqual(stored.base_gem_id, dropped.gem_instance.base_gem_id)
        self.assertEqual(stored.rarity, dropped.gem_instance.rarity)
        self.assertEqual(stored.random_affixes, ())
        self.assertEqual(dropped.gem_instance.random_affixes, ())
        self.assertEqual(stored.locked, dropped.gem_instance.locked)
        self.assertEqual(stored.board_position, dropped.gem_instance.board_position)

        self.assertEqual(session.pickup_nearby(), ())

    def test_pickup_radius_blocks_far_drops_until_player_is_near(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        session = CombatSession.start(
            player=self.player(pickup_radius=1.0),
            monsters=[Monster("monster_1", current_life=5, max_life=5, position=Position(5, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(seed=4),
        )

        session.tick(1)
        self.assertEqual(len(session.dropped_gems), 1)
        self.assertEqual(session.pickup_nearby(), ())
        self.assertFalse(session.dropped_gems[0].picked_up)

        session.player.position = Position(5, 0)
        self.assertEqual(len(session.pickup_nearby()), 1)
        self.assertTrue(session.dropped_gems[0].picked_up)


if __name__ == "__main__":
    unittest.main()
