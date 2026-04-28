from __future__ import annotations

import json
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import (
    ALLOWED_PREVIEW_SHOW_FIELDS,
    load_behavior_templates,
    load_gem_definitions,
    load_localization,
    load_skill_schema,
    load_yaml_file,
    validate_skill_package_data,
)


ACTIVE_SKILL_ORDER = (
    "active_fire_bolt",
    "active_ice_shards",
    "active_lightning_chain",
    "active_frost_nova",
    "active_puncture",
    "active_penetrating_shot",
    "active_lava_orb",
    "active_fungal_petards",
)
OPENABLE_SKILL_PACKAGES = frozenset({"active_fire_bolt"})
EDITABLE_SKILL_PACKAGES = frozenset({"active_fire_bolt"})

PACKAGE_KEY_ORDER = (
    "id",
    "version",
    "display",
    "classification",
    "cast",
    "behavior",
    "hit",
    "scaling",
    "presentation",
    "preview",
)
NESTED_KEY_ORDER = {
    "display": ("name_key", "description_key"),
    "classification": ("tags", "damage_type", "damage_form"),
    "cast": ("mode", "target_selector", "search_range", "cooldown_ms", "windup_ms", "recovery_ms"),
    "behavior": ("template", "params"),
    "params": (
        "projectile_count",
        "burst_interval_ms",
        "spread_angle_deg",
        "projectile_speed",
        "projectile_width",
        "projectile_height",
        "max_distance",
        "hit_policy",
        "pierce_count",
        "collision_radius",
        "spawn_offset",
        "projectile_radius",
        "impact_radius",
        "max_targets",
        "min_duration_ms",
        "max_duration_ms",
    ),
    "spawn_offset": ("x", "y"),
    "hit": ("base_damage", "can_crit", "can_apply_status", "damage_timing", "hit_delay_ms", "hit_radius", "target_policy"),
    "scaling": ("additive_stats", "final_stats", "runtime_params"),
    "presentation": (
        "vfx",
        "cast_vfx_key",
        "projectile_vfx_key",
        "hit_vfx_key",
        "sfx",
        "floating_text",
        "floating_text_style",
        "screen_feedback",
        "hit_stop_ms",
        "camera_shake",
    ),
    "preview": ("show_fields",),
}
LOCALIZATION_PRESENTATION_KEYS = frozenset(
    {
        "vfx",
        "cast_vfx_key",
        "projectile_vfx_key",
        "hit_vfx_key",
        "sfx",
        "floating_text",
        "floating_text_style",
        "screen_feedback",
    }
)


@dataclass(frozen=True)
class SkillPackageReadResult:
    data: dict[str, Any]
    path: Path
    validation_error: str | None

    @property
    def is_valid(self) -> bool:
        return self.validation_error is None


class SkillEditorService:
    """Builds and saves the active_fire_bolt SkillEditor view."""

    def __init__(self, config_root: Path) -> None:
        self.config_root = config_root

    def view(self) -> dict[str, Any]:
        localization = load_localization(self.config_root)
        definitions = load_gem_definitions(self.config_root)
        package_results = self._read_active_skill_packages()
        entries = []
        for skill_id in ACTIVE_SKILL_ORDER:
            definition = definitions.get(skill_id)
            package_result = package_results.get(skill_id)
            name_text = localization.get(definition.name_key, skill_id) if definition else skill_id
            if package_result and skill_id in OPENABLE_SKILL_PACKAGES:
                entries.append(self._migrated_entry(skill_id, name_text, package_result))
            else:
                entries.append(self._unmigrated_entry(skill_id, name_text))

        return {
            "title_text": "技能编辑器 V0",
            "subtitle_text": "模块化编辑已迁移技能包",
            "selected_id": "active_fire_bolt",
            "entries": entries,
            "options": skill_editor_options(),
        }

    def save_package(self, skill_id: str, package: dict[str, Any]) -> dict[str, Any]:
        if skill_id not in EDITABLE_SKILL_PACKAGES:
            return self._save_result(False, "该技能尚未迁移，当前不可编辑。")
        if not isinstance(package, dict):
            return self._save_result(False, "保存内容格式错误，必须是技能包对象。")
        if package.get("id") != skill_id:
            return self._save_result(False, "id 为只读字段，不允许修改。")

        path = self._package_path(skill_id)
        if not path.is_file():
            return self._save_result(False, "技能包文件不存在，无法保存。")

        package_to_save = deepcopy(package)
        try:
            schema = load_skill_schema(self.config_root)
            behavior_templates = load_behavior_templates(self.config_root)
            validate_skill_package_data(package_to_save, schema, behavior_templates, path)
            self._validate_localization_references(package_to_save)
        except Exception as exc:
            return self._save_result(False, chinese_validation_error(exc))

        path.write_text(dump_skill_package_yaml(package_to_save), encoding="utf-8")
        return self._save_result(True, "保存成功，已重新读取技能包。")

    def _save_result(self, ok: bool, message_text: str) -> dict[str, Any]:
        return {
            "ok": ok,
            "message_text": message_text,
            "skill_editor": self.view(),
        }

    def _read_active_skill_packages(self) -> dict[str, SkillPackageReadResult]:
        active_dir = self.config_root / "skills" / "active"
        if not active_dir.exists():
            return {}

        schema = load_skill_schema(self.config_root)
        behavior_templates = load_behavior_templates(self.config_root)
        results: dict[str, SkillPackageReadResult] = {}
        for path in sorted(active_dir.glob("*/skill.yaml")):
            try:
                package = load_yaml_file(path)
                package_id = str(package.get("id", path.parent.name))
                validate_skill_package_data(package, schema, behavior_templates, path)
                self._validate_localization_references(package)
                results[package_id] = SkillPackageReadResult(package, path, None)
            except Exception as exc:
                package_id = path.parent.name
                package = {"id": package_id}
                results[package_id] = SkillPackageReadResult(package, path, chinese_validation_error(exc))
        return results

    def _migrated_entry(self, skill_id: str, name_text: str, result: SkillPackageReadResult) -> dict[str, Any]:
        package = result.data
        classification = _mapping(package.get("classification"))
        cast = _mapping(package.get("cast"))
        behavior = _mapping(package.get("behavior"))
        hit = _mapping(package.get("hit"))
        relative_path = self._relative_path(result.path)
        schema_status = {
            "is_valid": result.is_valid,
            "text": "结构校验通过" if result.is_valid else "结构校验失败",
            "errors": [] if result.is_valid else [result.validation_error or "结构校验失败。"],
        }
        return {
            "id": skill_id,
            "name_text": name_text,
            "migrated": True,
            "openable": result.is_valid,
            "editable": result.is_valid and skill_id in EDITABLE_SKILL_PACKAGES,
            "status_text": "已迁移，可编辑" if result.is_valid else "已迁移，需修复",
            "skill_yaml_path": relative_path,
            "behavior_template": str(behavior.get("template", "")),
            "schema_status": schema_status,
            "detail": {
                "id": str(package.get("id", skill_id)),
                "version": str(package.get("version", "")),
                "damage_type": str(classification.get("damage_type", "")),
                "damage_form": str(classification.get("damage_form", "")),
                "tags": list(classification.get("tags", [])) if isinstance(classification.get("tags", []), list) else [],
                "cooldown_ms": cast.get("cooldown_ms"),
                "base_damage": hit.get("base_damage"),
            },
            "package_data": deepcopy(package) if result.is_valid else None,
        }

    def _unmigrated_entry(self, skill_id: str, name_text: str) -> dict[str, Any]:
        return {
            "id": skill_id,
            "name_text": name_text,
            "migrated": False,
            "openable": False,
            "editable": False,
            "status_text": "未迁移 / 不可编辑",
            "skill_yaml_path": "",
            "behavior_template": "",
            "schema_status": {
                "is_valid": False,
                "text": "未迁移，未执行结构校验",
                "errors": [],
            },
            "detail": None,
            "package_data": None,
        }

    def _validate_localization_references(self, package: dict[str, Any]) -> None:
        localization = load_localization(self.config_root)
        display = _mapping(package.get("display"))
        for key_name in ("name_key", "description_key"):
            localization_key = str(display.get(key_name, ""))
            _require_localized_chinese_text(localization_key, localization, f"display.{key_name}")

        presentation = _mapping(package.get("presentation"))
        for key_name in LOCALIZATION_PRESENTATION_KEYS:
            if key_name in presentation:
                localization_key = str(presentation[key_name])
                _require_localized_chinese_text(localization_key, localization, f"presentation.{key_name}")

    def _package_path(self, skill_id: str) -> Path:
        return self.config_root / "skills" / "active" / skill_id / "skill.yaml"

    def _relative_path(self, path: Path) -> str:
        try:
            return path.relative_to(self.config_root.parent).as_posix()
        except ValueError:
            return path.as_posix()


def skill_editor_options() -> dict[str, Any]:
    return {
        "damage_types": [
            {"value": "physical", "text": "物理"},
            {"value": "fire", "text": "火焰"},
            {"value": "cold", "text": "冰霜"},
            {"value": "lightning", "text": "闪电"},
        ],
        "damage_forms": [
            {"value": "attack", "text": "攻击"},
            {"value": "spell", "text": "法术"},
            {"value": "secondary", "text": "次要"},
            {"value": "damage_over_time", "text": "持续伤害"},
        ],
        "cast_modes": [
            {"value": "instant", "text": "瞬发"},
            {"value": "attack", "text": "攻击"},
            {"value": "spell", "text": "法术"},
        ],
        "target_selectors": [
            {"value": "nearest_enemy", "text": "最近敌人"},
            {"value": "target_enemy", "text": "指定敌人"},
            {"value": "self", "text": "自身"},
            {"value": "ground", "text": "地面"},
        ],
        "hit_policies": [
            {"value": "first_hit", "text": "首次命中"},
            {"value": "pierce", "text": "贯穿"},
        ],
        "damage_timings": [{"value": "on_projectile_hit", "text": "投射物命中时"}],
        "target_policies": [
            {"value": "selected_target", "text": "当前目标"},
            {"value": "nearest_enemy", "text": "最近敌人"},
        ],
        "preview_fields": [
            {"value": "final_damage", "text": "最终伤害"},
            {"value": "final_cooldown_ms", "text": "最终冷却"},
            {"value": "projectile_count", "text": "投射物数量"},
            {"value": "speed_multiplier", "text": "速度倍率"},
            {"value": "base_damage", "text": "基础伤害"},
            {"value": "base_cooldown_ms", "text": "基础冷却"},
            {"value": "damage_type", "text": "伤害类型"},
            {"value": "damage_form", "text": "伤害形式"},
        ],
    }


def dump_skill_package_yaml(package: dict[str, Any]) -> str:
    return _dump_yaml_mapping(package, 0, PACKAGE_KEY_ORDER).rstrip() + "\n"


def chinese_validation_error(error: Exception) -> str:
    message = str(error)
    replacements = {
        "skill package root must be an object": "技能包根节点必须是对象",
        "skill.schema.json root must be an object": "结构定义根节点必须是对象",
        "skill.schema.json must declare root required fields": "结构定义必须声明根级必填字段",
        "skill package missing required field:": "缺少必填字段：",
        "skill package id must match directory name:": "技能 ID 必须与目录名一致：",
        "skill package version must use MAJOR.MINOR.PATCH:": "版本号必须使用 主版本.次版本.修订版本：",
        "skill package behavior.template is not allowed:": "行为模板不在白名单内：",
        "skill package behavior.params has unsupported parameter": "行为参数不在模板白名单内",
        "skill package behavior.params must not contain expression strings:": "行为参数不允许包含表达式字符串：",
        "skill package behavior.params.": "行为参数错误：",
        "skill package has invalid damage_type:": "伤害类型不在允许范围内：",
        "skill package has invalid damage_form:": "伤害形式不在允许范围内：",
        "skill package has invalid cast.mode:": "释放模式不在允许范围内：",
        "skill package has invalid cast.target_selector:": "目标选择方式不在允许范围内：",
        "skill package cast.": "释放参数错误：",
        "skill package hit.": "伤害点参数错误：",
        "skill package presentation.": "表现参数错误：",
        "skill package preview.show_fields has unknown fields": "预览字段包含未开放字段",
        "skill package must not contain script-like field:": "不允许脚本字段：",
        "missing localization key": "缺少本地化 key",
        "localized text must be Chinese": "本地化文本必须是中文",
    }
    for source, target in replacements.items():
        if source in message:
            return message.replace(source, target)
    return "配置文件未通过结构校验，请检查技能包字段。"


def _dump_yaml_mapping(data: dict[str, Any], indent: int, order: tuple[str, ...] | None = None) -> str:
    lines: list[str] = []
    keys = _ordered_keys(data, order)
    for key in keys:
        value = data[key]
        prefix = " " * indent + f"{key}:"
        if isinstance(value, dict):
            nested_order = NESTED_KEY_ORDER.get(str(key))
            lines.append(prefix)
            lines.append(_dump_yaml_mapping(value, indent + 2, nested_order))
        else:
            lines.append(f"{prefix} {_yaml_scalar(value)}")
    return "\n".join(lines)


def _ordered_keys(data: dict[str, Any], order: tuple[str, ...] | None) -> list[str]:
    if not order:
        return list(data)
    ordered = [key for key in order if key in data]
    ordered.extend(key for key in data if key not in ordered)
    return ordered


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return "null"
    text = str(value)
    if re.match(r"^[A-Za-z0-9_.-]+$", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def _require_localized_chinese_text(localization_key: str, localization: dict[str, str], label: str) -> None:
    if localization_key not in localization:
        raise ValueError(f"missing localization key {label}: {localization_key}")
    if not _contains_cjk(localization[localization_key]):
        raise ValueError(f"localized text must be Chinese {label}: {localization_key}")


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
