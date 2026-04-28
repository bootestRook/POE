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
        api.mount("web_seed_active_fire_bolt_1", 0, 0)
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
