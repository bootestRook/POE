from __future__ import annotations

from copy import deepcopy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liufang.skill_editor import ACTIVE_SKILL_ORDER, SkillEditorService, chinese_validation_error
from liufang.web_api import V1WebAppApi


class SkillEditorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config_root = ROOT / "configs"
        self.view = SkillEditorService(self.config_root).view()

    def entries_by_id(self) -> dict[str, dict]:
        return {entry["id"]: entry for entry in self.view["entries"]}

    def temp_config_root(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "configs"
        shutil.copytree(self.config_root, target)
        return target

    def temp_service_and_package(self) -> tuple[SkillEditorService, dict, Path]:
        config_root = self.temp_config_root()
        service = SkillEditorService(config_root)
        package = deepcopy(service.view()["entries"][0]["package_data"])
        path = config_root / "skills" / "active" / "active_fire_bolt" / "skill.yaml"
        return service, package, path

    def package_from_view(self, config_root: Path) -> dict:
        view = SkillEditorService(config_root).view()
        return deepcopy(view["entries"][0]["package_data"])

    def test_skill_editor_view_exposes_active_fire_bolt_editable_package(self) -> None:
        entries = self.entries_by_id()
        fire_bolt = entries["active_fire_bolt"]

        self.assertEqual(self.view["title_text"], "技能编辑器 V0")
        self.assertEqual(fire_bolt["name_text"], "火焰弹")
        self.assertTrue(fire_bolt["migrated"])
        self.assertTrue(fire_bolt["openable"])
        self.assertTrue(fire_bolt["editable"])
        self.assertEqual(fire_bolt["skill_yaml_path"], "configs/skills/active/active_fire_bolt/skill.yaml")
        self.assertEqual(fire_bolt["behavior_template"], "projectile")
        self.assertTrue(fire_bolt["schema_status"]["is_valid"])
        self.assertEqual(fire_bolt["schema_status"]["text"], "结构校验通过")
        self.assertEqual(fire_bolt["detail"]["id"], "active_fire_bolt")
        self.assertEqual(fire_bolt["detail"]["version"], "1.0.0")
        self.assertEqual(fire_bolt["detail"]["damage_type"], "fire")
        self.assertEqual(fire_bolt["detail"]["damage_form"], "spell")
        self.assertEqual(fire_bolt["detail"]["tags"], ["spell", "fire", "projectile"])
        self.assertEqual(fire_bolt["detail"]["cooldown_ms"], 700)
        self.assertEqual(fire_bolt["detail"]["base_damage"], 12)
        self.assertGreater(fire_bolt["package_data"]["behavior"]["params"]["projectile_speed"], 0)

    def test_skill_editor_options_cover_phase7_modules(self) -> None:
        options = self.view["options"]

        self.assertIn({"value": "fire", "text": "火焰"}, options["damage_types"])
        self.assertIn({"value": "spell", "text": "法术"}, options["damage_forms"])
        self.assertIn({"value": "spell", "text": "法术"}, options["cast_modes"])
        self.assertIn({"value": "nearest_enemy", "text": "最近敌人"}, options["target_selectors"])
        self.assertIn({"value": "first_hit", "text": "首次命中"}, options["hit_policies"])
        self.assertIn({"value": "on_projectile_hit", "text": "投射物命中时"}, options["damage_timings"])
        self.assertIn({"value": "final_damage", "text": "最终伤害"}, options["preview_fields"])

    def test_unmigrated_active_skills_are_locked(self) -> None:
        entries = self.entries_by_id()
        self.assertEqual(tuple(entries), ACTIVE_SKILL_ORDER)
        for skill_id in ACTIVE_SKILL_ORDER:
            if skill_id == "active_fire_bolt":
                continue
            self.assertFalse(entries[skill_id]["migrated"])
            self.assertFalse(entries[skill_id]["openable"])
            self.assertFalse(entries[skill_id]["editable"])
            self.assertEqual(entries[skill_id]["status_text"], "未迁移 / 不可编辑")
            self.assertIsNone(entries[skill_id]["detail"])
            self.assertIsNone(entries[skill_id]["package_data"])

    def test_modifier_stack_view_reads_testable_modifiers(self) -> None:
        modifier_stack = self.view["modifier_stack"]
        modifiers = {modifier["id"]: modifier for modifier in modifier_stack["available_modifiers"]}

        self.assertEqual(modifier_stack["panel_title_text"], "测试 Modifier 栈")
        self.assertIn("仅用于测试", modifier_stack["notice_text"])
        self.assertIn({"value": "adjacent", "text": "相邻"}, modifier_stack["relation_options"])
        self.assertIn({"value": "same_row", "text": "同行"}, modifier_stack["relation_options"])
        self.assertIn({"value": "same_column", "text": "同列"}, modifier_stack["relation_options"])
        self.assertIn({"value": "same_box", "text": "同宫"}, modifier_stack["relation_options"])
        self.assertIn("support_extra_projectile", modifiers)
        self.assertIn("support_fire_mastery", modifiers)
        self.assertTrue(modifiers["support_extra_projectile"]["stats"])
        self.assertFalse(any("affix" in modifier for modifier in modifiers))

    def test_modifier_stack_preview_applies_one_modifier(self) -> None:
        service = SkillEditorService(self.config_root)

        result = service.preview_modifier_stack(
            {
                "skill_id": "active_fire_bolt",
                "modifier_ids": ["support_fire_mastery"],
                "relation": "same_row",
                "source_power": 1,
                "target_power": 1,
                "conduit_power": 1,
            }
        )

        self.assertTrue(result["ok"], result["message_text"])
        preview = result["preview"]
        self.assertGreater(preview["tested"]["final_damage"], preview["baseline"]["final_damage"])
        self.assertEqual(preview["relation_text"], "同行")
        self.assertTrue(preview["applied_modifiers"])
        self.assertFalse(preview["writes_real_data"])

    def test_modifier_stack_preview_applies_multiple_modifiers(self) -> None:
        service = SkillEditorService(self.config_root)

        result = service.preview_modifier_stack(
            {
                "skill_id": "active_fire_bolt",
                "modifier_ids": ["support_fire_mastery", "support_extra_projectile", "support_projectile_speed"],
                "relation": "same_row",
                "source_power": 1,
                "target_power": 1,
                "conduit_power": 1,
            }
        )

        self.assertTrue(result["ok"], result["message_text"])
        preview = result["preview"]
        self.assertGreater(preview["tested"]["final_damage"], preview["baseline"]["final_damage"])
        self.assertGreater(preview["tested"]["projectile_count"], preview["baseline"]["projectile_count"])
        self.assertGreater(preview["tested"]["projectile_speed"], preview["baseline"]["projectile_speed"])

    def test_modifier_stack_preview_accepts_relation_and_power_parameters(self) -> None:
        service = SkillEditorService(self.config_root)

        weak = service.preview_modifier_stack(
            {
                "skill_id": "active_fire_bolt",
                "modifier_ids": ["support_fire_mastery"],
                "relation": "same_row",
                "source_power": 1,
                "target_power": 1,
                "conduit_power": 1,
            }
        )
        strong = service.preview_modifier_stack(
            {
                "skill_id": "active_fire_bolt",
                "modifier_ids": ["support_fire_mastery"],
                "relation": "row",
                "source_power": 2,
                "target_power": 1.5,
                "conduit_power": 1.25,
            }
        )

        self.assertTrue(strong["ok"], strong["message_text"])
        self.assertEqual(strong["preview"]["relation"], "same_row")
        self.assertGreater(strong["preview"]["tested"]["final_damage"], weak["preview"]["tested"]["final_damage"])

    def test_modifier_stack_preview_rejects_invalid_power_with_chinese_error(self) -> None:
        service = SkillEditorService(self.config_root)

        result = service.preview_modifier_stack(
            {
                "skill_id": "active_fire_bolt",
                "modifier_ids": ["support_fire_mastery"],
                "relation": "same_row",
                "source_power": -1,
                "target_power": 1,
                "conduit_power": 1,
            }
        )

        self.assertFalse(result["ok"])
        self.assertIn("source_power 必须在", result["message_text"])

    def test_modifier_stack_preview_reports_unapplied_filter_reason(self) -> None:
        service = SkillEditorService(self.config_root)

        result = service.preview_modifier_stack(
            {
                "skill_id": "active_fire_bolt",
                "modifier_ids": ["support_wide_effect"],
                "relation": "same_row",
                "source_power": 1,
                "target_power": 1,
                "conduit_power": 1,
            }
        )

        self.assertTrue(result["ok"], result["message_text"])
        unapplied = result["preview"]["unapplied_modifiers"]
        self.assertTrue(unapplied)
        self.assertIn("不匹配", unapplied[0]["reason_text"])

    def test_modifier_stack_preview_does_not_write_skill_yaml_or_real_inventory(self) -> None:
        config_root = self.temp_config_root()
        service = SkillEditorService(config_root)
        path = config_root / "skills" / "active" / "active_fire_bolt" / "skill.yaml"
        before = path.read_text(encoding="utf-8")

        result = service.preview_modifier_stack(
            {
                "skill_id": "active_fire_bolt",
                "modifier_ids": ["support_extra_projectile", "support_projectile_speed"],
                "relation": "same_row",
                "source_power": 2,
                "target_power": 2,
                "conduit_power": 1,
            }
        )
        api = V1WebAppApi(config_root)

        self.assertTrue(result["ok"], result["message_text"])
        self.assertEqual(path.read_text(encoding="utf-8"), before)
        self.assertFalse(any(instance.get("instance_id", "").startswith("test_modifier:") for instance in api.state()["inventory"]))
        self.assertNotIn("random_affixes", str(result))

    def test_skill_test_arena_view_lists_controlled_scenes_and_testable_skill(self) -> None:
        arena = self.view["test_arena"]
        skills = {skill["id"]: skill for skill in arena["skills"]}
        scenes = {scene["scene_id"]: scene for scene in arena["scenes"]}

        self.assertEqual(arena["panel_title_text"], "技能测试场")
        self.assertTrue(skills["active_fire_bolt"]["testable"])
        for skill_id in ACTIVE_SKILL_ORDER:
            if skill_id == "active_fire_bolt":
                continue
            self.assertFalse(skills[skill_id]["testable"])
            self.assertEqual(skills[skill_id]["status_text"], "未迁移 / 不可测试")
        self.assertIn("single_dummy", scenes)
        self.assertIn("three_horizontal", scenes)
        self.assertIn("vertical_queue", scenes)
        self.assertIn("dense_pack", scenes)
        for scene in scenes.values():
            self.assertTrue(scene["enemies"])
            self.assertIn("enemy_id", scene["enemies"][0])
            self.assertIn("position", scene["enemies"][0])
            self.assertTrue(scene["enemies"][0]["is_alive"])

    def test_skill_test_arena_single_dummy_uses_real_events_and_delayed_damage(self) -> None:
        result = SkillEditorService(self.config_root).run_test_arena(
            {"skill_id": "active_fire_bolt", "scene_id": "single_dummy"}
        )

        self.assertTrue(result["ok"], result["message_text"])
        arena = result["result"]
        self.assertTrue(arena["has_projectile_spawn"])
        self.assertTrue(arena["has_damage"])
        self.assertTrue(arena["has_hit_vfx"])
        self.assertTrue(arena["has_floating_text"])
        self.assertTrue(arena["flight_no_damage_passed"])
        self.assertFalse(arena["writes_real_data"])
        self.assertGreater(arena["flight_duration_ms"], 0)
        self.assertEqual(arena["stages"][0]["monsters"][0]["current_life"], arena["stages"][0]["monsters"][0]["max_life"])
        self.assertLess(arena["monsters"][0]["current_life"], arena["monsters"][0]["max_life"])
        self.assertTrue(arena["hit_targets"])
        self.assertTrue(arena["damage_results"])

    def test_skill_event_timeline_exposes_real_events_and_required_fields(self) -> None:
        result = SkillEditorService(self.config_root).run_test_arena(
            {"skill_id": "active_fire_bolt", "scene_id": "single_dummy"}
        )

        self.assertTrue(result["ok"], result["message_text"])
        arena = result["result"]
        timeline = arena["event_timeline"]
        self.assertEqual(timeline, sorted(timeline, key=lambda event: (event["timestamp_ms"], event["original_index"])))
        self.assertEqual({item["type"] for item in arena["timeline_supported_types"]}, {
            "cast_start",
            "projectile_spawn",
            "projectile_hit",
            "damage",
            "hit_vfx",
            "floating_text",
            "cooldown_update",
        })
        self.assertIn("projectile_spawn", [event["type"] for event in timeline])
        self.assertIn("damage", [event["type"] for event in timeline])
        self.assertIn("hit_vfx", [event["type"] for event in timeline])
        self.assertIn("floating_text", [event["type"] for event in timeline])
        for event in timeline:
            for field in [
                "timestamp_ms",
                "delay_ms",
                "duration_ms",
                "source_entity",
                "target_entity",
                "amount",
                "damage_type",
                "vfx_key",
                "reason_key",
                "payload",
            ]:
                self.assertIn(field, event)
        damage = next(event for event in timeline if event["type"] == "damage")
        hit_vfx = next(event for event in timeline if event["type"] == "hit_vfx")
        floating_text = next(event for event in timeline if event["type"] == "floating_text")
        self.assertGreater(damage["amount"], 0)
        self.assertEqual(damage["damage_type"], "fire")
        self.assertTrue(hit_vfx["vfx_key"])
        self.assertTrue(floating_text["reason_key"])
        self.assertTrue(arena["timeline_checks"]["damage_after_or_at_projectile_spawn"])
        self.assertTrue(arena["timeline_checks"]["flight_no_damage_passed"])
        self.assertTrue(arena["timeline_checks"]["basic_timing_passed"])

    def test_skill_event_timeline_modifier_stack_reflects_tested_amount_without_writing_file(self) -> None:
        config_root = self.temp_config_root()
        service = SkillEditorService(config_root)
        path = config_root / "skills" / "active" / "active_fire_bolt" / "skill.yaml"
        before = path.read_text(encoding="utf-8")

        base = service.run_test_arena({"skill_id": "active_fire_bolt", "scene_id": "single_dummy"})
        modified = service.run_test_arena(
            {
                "skill_id": "active_fire_bolt",
                "scene_id": "single_dummy",
                "use_modifier_stack": True,
                "modifier_ids": ["support_fire_mastery"],
                "relation": "same_row",
                "source_power": 1,
                "target_power": 1,
                "conduit_power": 1,
            }
        )

        self.assertTrue(base["ok"], base["message_text"])
        self.assertTrue(modified["ok"], modified["message_text"])
        base_damage = next(event for event in base["result"]["event_timeline"] if event["type"] == "damage")
        modified_damage = next(event for event in modified["result"]["event_timeline"] if event["type"] == "damage")
        self.assertGreater(modified_damage["amount"], base_damage["amount"])
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_skill_test_arena_projectile_speed_changes_flight_duration(self) -> None:
        service = SkillEditorService(self.config_root)
        package = deepcopy(self.entries_by_id()["active_fire_bolt"]["package_data"])
        package["behavior"]["params"]["projectile_speed"] = 360
        slow = service.run_test_arena({"skill_id": "active_fire_bolt", "scene_id": "single_dummy", "package": package})
        package["behavior"]["params"]["projectile_speed"] = 720
        fast = service.run_test_arena({"skill_id": "active_fire_bolt", "scene_id": "single_dummy", "package": package})

        self.assertTrue(slow["ok"], slow["message_text"])
        self.assertTrue(fast["ok"], fast["message_text"])
        self.assertGreater(slow["result"]["flight_duration_ms"], fast["result"]["flight_duration_ms"])

    def test_skill_test_arena_base_damage_changes_damage_result(self) -> None:
        service = SkillEditorService(self.config_root)
        package = deepcopy(self.entries_by_id()["active_fire_bolt"]["package_data"])
        package["hit"]["base_damage"] = 10
        weak = service.run_test_arena({"skill_id": "active_fire_bolt", "scene_id": "single_dummy", "package": package})
        package["hit"]["base_damage"] = 20
        strong = service.run_test_arena({"skill_id": "active_fire_bolt", "scene_id": "single_dummy", "package": package})

        self.assertTrue(weak["ok"], weak["message_text"])
        self.assertTrue(strong["ok"], strong["message_text"])
        self.assertLess(
            weak["result"]["damage_results"][0]["amount"],
            strong["result"]["damage_results"][0]["amount"],
        )

    def test_skill_test_arena_modifier_stack_changes_result_without_writing_file(self) -> None:
        config_root = self.temp_config_root()
        service = SkillEditorService(config_root)
        path = config_root / "skills" / "active" / "active_fire_bolt" / "skill.yaml"
        before = path.read_text(encoding="utf-8")

        base = service.run_test_arena({"skill_id": "active_fire_bolt", "scene_id": "single_dummy", "use_modifier_stack": False})
        modified = service.run_test_arena(
            {
                "skill_id": "active_fire_bolt",
                "scene_id": "single_dummy",
                "use_modifier_stack": True,
                "modifier_ids": ["support_fire_mastery", "support_extra_projectile"],
                "relation": "same_row",
                "source_power": 1,
                "target_power": 1,
                "conduit_power": 1,
            }
        )

        self.assertTrue(base["ok"], base["message_text"])
        self.assertTrue(modified["ok"], modified["message_text"])
        self.assertGreater(modified["result"]["tested"]["final_damage"], base["result"]["tested"]["final_damage"])
        self.assertGreater(modified["result"]["tested"]["projectile_count"], base["result"]["tested"]["projectile_count"])
        self.assertEqual(path.read_text(encoding="utf-8"), before)
        self.assertNotIn("random_affixes", str(modified))

    def test_skill_test_arena_pierce_hits_multiple_targets_in_vertical_queue(self) -> None:
        service = SkillEditorService(self.config_root)
        package = deepcopy(self.entries_by_id()["active_fire_bolt"]["package_data"])
        package["behavior"]["params"]["hit_policy"] = "pierce"
        package["behavior"]["params"]["pierce_count"] = 2
        package["behavior"]["params"]["projectile_count"] = 1

        result = service.run_test_arena(
            {"skill_id": "active_fire_bolt", "scene_id": "vertical_queue", "package": package}
        )

        self.assertTrue(result["ok"], result["message_text"])
        self.assertGreaterEqual(len(result["result"]["hit_targets"]), 2)

    def test_id_field_is_readonly_and_file_is_not_written(self) -> None:
        service, package, path = self.temp_service_and_package()
        before = path.read_text(encoding="utf-8")

        package["id"] = "active_fire_bolt_changed"
        result = service.save_package("active_fire_bolt", package)

        self.assertFalse(result["ok"])
        self.assertIn("id 为只读字段", result["message_text"])
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_save_version_success_and_reload(self) -> None:
        service, package, path = self.temp_service_and_package()

        package["version"] = "1.0.1"
        result = service.save_package("active_fire_bolt", package)

        self.assertTrue(result["ok"])
        self.assertIn("保存成功", result["message_text"])
        self.assertIn("version: 1.0.1", path.read_text(encoding="utf-8"))
        self.assertEqual(self.package_from_view(path.parents[3])["version"], "1.0.1")

    def test_save_cooldown_success_and_reload(self) -> None:
        service, package, path = self.temp_service_and_package()

        package["cast"]["cooldown_ms"] = 650
        result = service.save_package("active_fire_bolt", package)

        self.assertTrue(result["ok"])
        self.assertEqual(self.package_from_view(path.parents[3])["cast"]["cooldown_ms"], 650)

    def test_save_projectile_speed_success_and_reload(self) -> None:
        service, package, path = self.temp_service_and_package()

        package["behavior"]["params"]["projectile_speed"] = 900
        result = service.save_package("active_fire_bolt", package)

        self.assertTrue(result["ok"])
        self.assertEqual(self.package_from_view(path.parents[3])["behavior"]["params"]["projectile_speed"], 900)

    def test_save_base_damage_success_and_reload(self) -> None:
        service, package, path = self.temp_service_and_package()

        package["hit"]["base_damage"] = 18
        result = service.save_package("active_fire_bolt", package)

        self.assertTrue(result["ok"])
        self.assertEqual(self.package_from_view(path.parents[3])["hit"]["base_damage"], 18)

    def test_save_preview_show_fields_success_and_reload(self) -> None:
        service, package, path = self.temp_service_and_package()

        package["preview"]["show_fields"] = ["final_damage", "base_damage", "damage_type"]
        result = service.save_package("active_fire_bolt", package)

        self.assertTrue(result["ok"])
        self.assertEqual(self.package_from_view(path.parents[3])["preview"]["show_fields"], ["final_damage", "base_damage", "damage_type"])

    def test_invalid_behavior_param_fails_without_writing_file(self) -> None:
        service, package, path = self.temp_service_and_package()
        before = path.read_text(encoding="utf-8")

        package["behavior"]["params"]["forbidden_param"] = 1
        result = service.save_package("active_fire_bolt", package)

        self.assertFalse(result["ok"])
        self.assertIn("行为参数不在模板白名单内", result["message_text"])
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_invalid_enum_fails_with_chinese_error_without_writing_file(self) -> None:
        service, package, path = self.temp_service_and_package()
        before = path.read_text(encoding="utf-8")

        package["classification"]["damage_type"] = "arcane"
        result = service.save_package("active_fire_bolt", package)

        self.assertFalse(result["ok"])
        self.assertIn("伤害类型不在允许范围内", result["message_text"])
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_web_api_save_returns_refreshed_skill_editor_state(self) -> None:
        config_root = self.temp_config_root()
        api = V1WebAppApi(config_root)
        api.mount("web_seed_active_1_active_fire_bolt", 0, 0)
        package = deepcopy(api.state()["skill_editor"]["entries"][0]["package_data"])

        package["cast"]["cooldown_ms"] = 680
        package["behavior"]["params"]["projectile_count"] = 6
        package["behavior"]["params"]["hit_policy"] = "pierce"
        package["behavior"]["params"]["pierce_count"] = 4
        payload = api.save_skill_package("active_fire_bolt", package)

        self.assertTrue(payload["ok"])
        self.assertIn("保存成功", payload["message_text"])
        self.assertEqual(payload["state"]["skill_editor"]["entries"][0]["package_data"]["cast"]["cooldown_ms"], 680)
        self.assertEqual(payload["state"]["skill_editor"]["entries"][0]["package_data"]["behavior"]["params"]["projectile_count"], 6)
        self.assertEqual(payload["state"]["skill_editor"]["entries"][0]["package_data"]["behavior"]["params"]["pierce_count"], 4)
        skill_preview = payload["state"]["skill_preview"][0]
        self.assertEqual(skill_preview["projectile_count"], 6)
        self.assertEqual(skill_preview["runtime_params"]["projectile_count"], 6)
        self.assertEqual(skill_preview["runtime_params"]["hit_policy"], "pierce")
        self.assertEqual(skill_preview["runtime_params"]["pierce_count"], 4)

    def test_validation_errors_are_chinese(self) -> None:
        message = chinese_validation_error(ValueError("skill package behavior.template is not allowed: active_bad"))

        self.assertEqual(message, "行为模板不在白名单内： active_bad")


if __name__ == "__main__":
    unittest.main()
