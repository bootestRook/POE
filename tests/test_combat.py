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

    def player(self, item_interaction_reach: float = 2.0) -> Player:
        return Player(
            player_id="player_1",
            current_life=100,
            max_life=100,
            position=Position(0, 0),
            item_interaction_reach=item_interaction_reach,
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
            monsters=[Monster("monster_1", current_life=200, max_life=200, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(),
        )

        first_events = session.tick(1)
        self.assertEqual(first_events, ())
        self.assertEqual(session.monsters[0].current_life, 200)
        expected_spawn_count = session.active_skill_instances[0].projectile_count
        burst_interval_ms = int((session.active_skill_instances[0].runtime_params or {}).get("burst_interval_ms", 0))
        self.assertEqual(
            [event.type for event in session.skill_events],
            ["projectile_spawn"] * expected_spawn_count + ["damage", "hit_vfx", "floating_text"] * expected_spawn_count,
        )

        projectile_duration_ms = session.skill_events[0].duration_ms
        before_hit_events = session.tick(projectile_duration_ms - 1)
        self.assertEqual(before_hit_events, ())
        self.assertEqual(session.monsters[0].current_life, 200)

        hit_events = session.tick(1)
        expected_first_wave = expected_spawn_count if burst_interval_ms == 0 else 1
        self.assertEqual(len(hit_events), expected_first_wave)
        self.assertEqual(hit_events[0].skill_instance.active_gem_instance_id, "active")
        self.assertEqual(hit_events[0].damage, session.active_skill_instances[0].final_damage)
        self.assertEqual(
            session.monsters[0].current_life,
            200 - session.active_skill_instances[0].final_damage * expected_first_wave,
        )

        second_events = session.tick(max(1, burst_interval_ms))
        if expected_spawn_count > 1 and burst_interval_ms > 0:
            self.assertEqual(len(second_events), 1)
        else:
            self.assertEqual(second_events, ())

    def test_non_packaged_active_skills_keep_legacy_immediate_path(self) -> None:
        self.inventory.add_instance("active", "active_ice_shards")
        self.board.mount_gem("active", 0, 0)
        session = CombatSession.start(
            player=self.player(),
            monsters=[Monster("monster_1", current_life=30, max_life=30, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(),
        )

        events = session.tick(1)

        self.assertEqual(len(events), 1)
        self.assertEqual(session.active_skill_instances[0].skill_package_id, "")
        self.assertEqual(session.monsters[0].current_life, 22)
        self.assertEqual(session.skill_events, [])

    def test_passive_self_stat_applies_before_combat_and_does_not_release(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.inventory.add_instance("passive", "passive_vitality")
        self.board.mount_gem("active", 0, 0)
        self.board.mount_gem("passive", 1, 0)

        session = CombatSession.start(
            player=self.player(),
            monsters=[Monster("monster_1", current_life=30, max_life=30, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(),
        )

        self.assertEqual(session.player.max_life, 125)
        self.assertEqual(session.player.current_life, 125)
        self.assertEqual(len(session.active_skill_instances), 1)
        self.assertEqual(session.active_skill_instances[0].active_gem_instance_id, "active")

    def test_kill_triggers_gem_drop_and_pickup_enters_inventory(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        session = CombatSession.start(
            player=self.player(item_interaction_reach=2.0),
            monsters=[Monster("monster_1", current_life=5, max_life=5, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(seed=3),
        )

        session.tick(1)
        events = session.tick(420)
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

    def test_item_interaction_reach_blocks_far_drops_until_player_is_near(self) -> None:
        self.inventory.add_instance("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)
        session = CombatSession.start(
            player=self.player(item_interaction_reach=1.0),
            monsters=[Monster("monster_1", current_life=5, max_life=5, position=Position(5, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self.calculator(),
            loot_runtime=self.loot_runtime(seed=4),
        )

        session.tick(1)
        session.tick(420)
        self.assertEqual(len(session.dropped_gems), 1)
        self.assertEqual(session.pickup_nearby(), ())
        self.assertFalse(session.dropped_gems[0].picked_up)

        session.player.position = Position(5, 0)
        self.assertEqual(len(session.pickup_nearby()), 1)
        self.assertTrue(session.dropped_gems[0].picked_up)


if __name__ == "__main__":
    unittest.main()
