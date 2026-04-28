from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.config import load_board_rules, load_gem_definitions
from liufang.gem_board import SudokuGemBoard
from liufang.inventory import GemInstance, GemInventory


class SudokuGemBoardTest(unittest.TestCase):
    def setUp(self) -> None:
        config_root = ROOT / "configs"
        self.rules = load_board_rules(config_root)
        self.definitions = load_gem_definitions(config_root)
        self.inventory = GemInventory(self.definitions)
        self.board = SudokuGemBoard(self.rules, self.inventory)

    def add(self, instance_id: str, base_gem_id: str) -> None:
        self.inventory.add_instance(instance_id, base_gem_id)

    def add_as_type(self, instance_id: str, base_gem_id: str, gem_type: str) -> None:
        definition = self.definitions[base_gem_id]
        tags = frozenset(tag for tag in definition.tags if not tag.startswith("gem_type_")) | {gem_type}
        self.inventory.add_existing_instance(
            GemInstance(
                instance_id=instance_id,
                base_gem_id=base_gem_id,
                gem_type=gem_type,
                tags=tags,
            )
        )

    def test_mount_unmount_updates_occupancy(self) -> None:
        self.add("gem_1", "active_fire_bolt")
        view = self.board.mount_gem("gem_1", 0, 0)
        self.assertEqual(view.cells[(0, 0)], "gem_1")
        self.assertEqual(self.inventory.require("gem_1").board_position.row, 0)

        view = self.board.unmount_gem("gem_1")
        self.assertNotIn((0, 0), view.cells)
        self.assertIsNone(self.inventory.require("gem_1").board_position)

    def test_mount_rejects_invalid_coordinate_occupied_cell_missing_instance_and_double_mount(self) -> None:
        self.add("gem_1", "active_fire_bolt")
        self.add("gem_2", "support_fast_attack")

        with self.assertRaisesRegex(ValueError, "坐标超出"):
            self.board.mount_gem("gem_1", 9, 0)
        with self.assertRaisesRegex(ValueError, "不存在"):
            self.board.mount_gem("missing", 0, 0)

        self.board.mount_gem("gem_1", 0, 0)
        with self.assertRaisesRegex(ValueError, "格子已被占用"):
            self.board.mount_gem("gem_2", 0, 0)
        with self.assertRaisesRegex(ValueError, "多个格子"):
            self.board.mount_gem("gem_1", 0, 1)

    def test_duplicate_gem_type_in_row_column_and_box_is_reported(self) -> None:
        self.add("active", "active_fire_bolt")
        self.add("support_a", "support_fast_attack")
        self.add("support_b", "support_fast_cast")
        self.add("support_c", "support_skill_haste")

        self.board.mount_gem("active", 4, 4)
        self.board.mount_gem("support_a", 0, 0)
        self.board.mount_gem("support_b", 0, 3)
        self.board.mount_gem("support_c", 2, 1)

        validation = self.board.validate()
        keys = {issue.error_key for issue in validation.issues}
        self.assertIn("board.duplicate_gem_type.row", keys)
        self.assertIn("board.duplicate_gem_type.box", keys)
        self.assertFalse(validation.is_valid)

    def test_column_duplicate_is_reported(self) -> None:
        self.add("active", "active_fire_bolt")
        self.add("support_a", "support_fast_attack")
        self.add("support_b", "support_fast_cast")

        self.board.mount_gem("active", 8, 8)
        self.board.mount_gem("support_a", 0, 0)
        self.board.mount_gem("support_b", 3, 0)

        validation = self.board.validate()
        keys = {issue.error_key for issue in validation.issues}
        self.assertIn("board.duplicate_gem_type.column", keys)

    def test_different_gem_types_use_distinct_color_groups(self) -> None:
        self.add_as_type("type_6", "support_lightning_mastery", "gem_type_6")
        self.add_as_type("type_8", "support_elemental_level", "gem_type_8")
        self.add_as_type("type_7", "support_wide_effect", "gem_type_7")
        self.add_as_type("type_9", "support_row_conduit", "gem_type_9")

        self.board.mount_gem("type_6", 0, 0)
        self.board.mount_gem("type_8", 0, 3)
        self.board.mount_gem("type_7", 1, 1)
        self.board.mount_gem("type_9", 4, 1)

        validation = self.board.validate()
        duplicate_keys = {issue.error_key for issue in validation.issues}
        self.assertNotIn("board.duplicate_gem_type.row", duplicate_keys)
        self.assertNotIn("board.duplicate_gem_type.column", duplicate_keys)
        self.assertNotIn("board.duplicate_gem_type.box", duplicate_keys)

    def test_relations_and_highlights_include_row_column_box_and_adjacent(self) -> None:
        self.add("active_a", "active_fire_bolt")
        self.add("active_b", "active_ice_shards")
        self.add("support_a", "support_physical_mastery")

        self.board.mount_gem("active_a", 0, 0)
        self.board.mount_gem("active_b", 0, 1)
        self.board.mount_gem("support_a", 1, 0)

        view = self.board.view()
        relation_types = {relation.relation for relation in view.relations}
        self.assertIn("same_row", relation_types)
        self.assertIn("same_column", relation_types)
        self.assertIn("same_box", relation_types)
        self.assertIn("adjacent", relation_types)
        self.assertIn(0, view.highlights["same_row"])
        self.assertIn(0, view.highlights["same_column"])
        self.assertIn(0, view.highlights["same_box"])
        self.assertIn((0, 0), view.highlights["adjacent"])

    def test_diagonal_is_not_adjacent(self) -> None:
        self.add("active_a", "active_fire_bolt")
        self.add("active_b", "active_ice_shards")

        self.board.mount_gem("active_a", 0, 0)
        self.board.mount_gem("active_b", 1, 1)

        adjacent = [relation for relation in self.board.relations() if relation.relation == "adjacent"]
        self.assertEqual(adjacent, [])

    def test_empty_or_no_active_skill_cannot_enter_combat_with_chinese_reason(self) -> None:
        validation = self.board.validate()
        self.assertFalse(validation.can_enter_combat)
        self.assertEqual(validation.enter_combat_error_key, "board.enter_combat.empty_board")
        self.assertEqual(validation.enter_combat_message, "空盘不可进入战斗")

        self.add("support", "support_fast_attack")
        self.board.mount_gem("support", 0, 0)
        validation = self.board.validate()
        self.assertFalse(validation.can_enter_combat)
        self.assertEqual(validation.enter_combat_error_key, "board.enter_combat.no_active_skill")
        self.assertEqual(validation.enter_combat_message, "没有主动技能宝石不可进入战斗")

    def test_active_skill_allows_enter_combat_when_board_is_valid(self) -> None:
        self.add("active", "active_fire_bolt")
        self.board.mount_gem("active", 0, 0)

        validation = self.board.validate()
        self.assertTrue(validation.is_valid)
        self.assertTrue(validation.can_enter_combat)
        self.assertIsNone(validation.enter_combat_error_key)


if __name__ == "__main__":
    unittest.main()
