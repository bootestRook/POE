from __future__ import annotations

import json
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import (
    ALLOWED_PREVIEW_SHOW_FIELDS,
    GemDefinition,
    SupportBaseModifier,
    _skill_template_from_package,
    load_board_rules,
    load_behavior_templates,
    load_gem_definitions,
    load_localization,
    load_relation_coefficients,
    load_skill_scaling_rules,
    load_skill_schema,
    load_skill_templates,
    load_yaml_file,
    validate_skill_package_data,
)
from .gem_board import SudokuGemBoard
from .inventory import GemInventory
from .skill_effects import AppliedModifier, FinalSkillInstance, SkillEffectCalculator
from .skill_runtime import SkillEvent, SkillRuntime


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
TESTABLE_SKILL_ID = "active_fire_bolt"
TEST_ACTIVE_INSTANCE_ID = "skill_editor_test_active_fire_bolt"
POWER_MIN = 0.0
POWER_MAX = 10.0
RELATION_ALIASES = {
    "adjacent": "adjacent",
    "row": "same_row",
    "column": "same_column",
    "box": "same_box",
    "same_row": "same_row",
    "same_column": "same_column",
    "same_box": "same_box",
}
RELATION_TEXT = {
    "adjacent": "相邻",
    "same_row": "同行",
    "same_column": "同列",
    "same_box": "同宫",
}
TEST_ARENA_SOURCE = {"x": 0.0, "y": -12.0}
TEST_ARENA_SCENES = (
    {
        "scene_id": "single_dummy",
        "name_text": "单体木桩",
        "enemies": (
            {"enemy_id": "dummy_1", "name_text": "训练木桩", "position": {"x": 360.0, "y": -12.0}, "max_life": 100.0},
        ),
    },
    {
        "scene_id": "three_horizontal",
        "name_text": "三目标横排",
        "enemies": (
            {"enemy_id": "dummy_left", "name_text": "左侧木桩", "position": {"x": 360.0, "y": -72.0}, "max_life": 100.0},
            {"enemy_id": "dummy_mid", "name_text": "中间木桩", "position": {"x": 360.0, "y": -12.0}, "max_life": 100.0},
            {"enemy_id": "dummy_right", "name_text": "右侧木桩", "position": {"x": 360.0, "y": 48.0}, "max_life": 100.0},
        ),
    },
    {
        "scene_id": "vertical_queue",
        "name_text": "纵向队列",
        "enemies": (
            {"enemy_id": "dummy_front", "name_text": "前排木桩", "position": {"x": 240.0, "y": -12.0}, "max_life": 100.0},
            {"enemy_id": "dummy_middle", "name_text": "中排木桩", "position": {"x": 360.0, "y": -12.0}, "max_life": 100.0},
            {"enemy_id": "dummy_back", "name_text": "后排木桩", "position": {"x": 480.0, "y": -12.0}, "max_life": 100.0},
        ),
    },
    {
        "scene_id": "dense_pack",
        "name_text": "密集小怪",
        "enemies": (
            {"enemy_id": "pack_1", "name_text": "密集小怪一", "position": {"x": 330.0, "y": -32.0}, "max_life": 60.0},
            {"enemy_id": "pack_2", "name_text": "密集小怪二", "position": {"x": 360.0, "y": -12.0}, "max_life": 60.0},
            {"enemy_id": "pack_3", "name_text": "密集小怪三", "position": {"x": 390.0, "y": 8.0}, "max_life": 60.0},
            {"enemy_id": "pack_4", "name_text": "密集小怪四", "position": {"x": 360.0, "y": 38.0}, "max_life": 60.0},
        ),
    },
)
TIMELINE_EVENT_TYPES = (
    "cast_start",
    "projectile_spawn",
    "projectile_hit",
    "damage",
    "hit_vfx",
    "floating_text",
    "cooldown_update",
)

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


@dataclass(frozen=True)
class _ArenaPoint:
    x: float
    y: float


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
            "modifier_stack": self.modifier_stack_view(),
            "test_arena": self.test_arena_view(entries),
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

    def modifier_stack_view(self) -> dict[str, Any]:
        return {
            "panel_title_text": "测试 Modifier 栈",
            "available_title_text": "可测试辅助效果",
            "selected_title_text": "已选择效果",
            "notice_text": "仅用于测试，不会写入技能文件、宝石实例、库存或随机词缀。",
            "relation_label_text": "关系模拟",
            "power_label_text": "测试参数",
            "apply_button_text": "应用测试栈",
            "clear_button_text": "清空测试栈",
            "relation_options": [
                {"value": "adjacent", "text": "相邻"},
                {"value": "same_row", "text": "同行"},
                {"value": "same_column", "text": "同列"},
                {"value": "same_box", "text": "同宫"},
            ],
            "power_limits": {"min": POWER_MIN, "max": POWER_MAX},
            "available_modifiers": self._testable_modifier_options(),
        }

    def preview_modifier_stack(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            skill_id = str(payload.get("skill_id", TESTABLE_SKILL_ID))
            if skill_id != TESTABLE_SKILL_ID:
                raise ValueError("当前测试栈只支持已迁移的火焰弹。")
            selected_ids = payload.get("modifier_ids", [])
            if not isinstance(selected_ids, list) or not all(isinstance(item, str) for item in selected_ids):
                raise ValueError("测试效果列表格式错误。")
            relation = self._normalize_relation(str(payload.get("relation", "adjacent")))
            source_power = self._validated_power(payload.get("source_power", 1.0), "source_power")
            target_power = self._validated_power(payload.get("target_power", 1.0), "target_power")
            conduit_power = self._validated_power(payload.get("conduit_power", 1.0), "conduit_power")
            baseline, tested = self._build_modifier_stack_preview(
                selected_ids=selected_ids,
                relation=relation,
                source_power=source_power,
                target_power=target_power,
                conduit_power=conduit_power,
            )
            return {
                "ok": True,
                "message_text": "测试栈已应用，结果仅用于预览。",
                "preview": {
                    "skill_id": skill_id,
                    "skill_name_text": self._localized_text("gem.active_fire_bolt.name"),
                    "relation": relation,
                    "relation_text": RELATION_TEXT[relation],
                    "source_power": source_power,
                    "target_power": target_power,
                    "conduit_power": conduit_power,
                    "baseline": self._final_skill_summary(baseline),
                    "tested": self._final_skill_summary(tested),
                    "applied_modifiers": [
                        self._modifier_preview_view(modifier)
                        for modifier in tested.applied_modifiers
                        if modifier.applied
                    ],
                    "unapplied_modifiers": [
                        self._modifier_preview_view(modifier)
                        for modifier in tested.applied_modifiers
                        if not modifier.applied
                    ],
                    "writes_real_data": False,
                },
            }
        except Exception as exc:
            return {"ok": False, "message_text": _chinese_modifier_stack_error(exc), "preview": None}

    def test_arena_view(self, entries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        if entries is None:
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
            "panel_title_text": "技能测试场",
            "entry_button_text": "进入测试场",
            "notice_text": "测试场只使用临时数据，不会写入技能文件、宝石实例、库存或掉落。",
            "skills": [
                {
                    "id": entry["id"],
                    "name_text": entry["name_text"],
                    "testable": entry["id"] == TESTABLE_SKILL_ID and bool(entry["openable"]),
                    "status_text": "可测试" if entry["id"] == TESTABLE_SKILL_ID and bool(entry["openable"]) else "未迁移 / 不可测试",
                }
                for entry in entries
            ],
            "scenes": [self._scene_view(scene) for scene in TEST_ARENA_SCENES],
        }

    def run_test_arena(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            skill_id = str(payload.get("skill_id", TESTABLE_SKILL_ID))
            if skill_id != TESTABLE_SKILL_ID:
                raise ValueError("当前测试场只允许运行已迁移的火焰弹技能包。")
            scene_id = str(payload.get("scene_id", "single_dummy"))
            scene = self._require_scene(scene_id)
            package = self._package_for_test_payload(payload)
            use_modifier_stack = bool(payload.get("use_modifier_stack", False))
            relation = self._normalize_relation(str(payload.get("relation", "adjacent")))
            source_power = self._validated_power(payload.get("source_power", 1.0), "source_power")
            target_power = self._validated_power(payload.get("target_power", 1.0), "target_power")
            conduit_power = self._validated_power(payload.get("conduit_power", 1.0), "conduit_power")
            selected_ids = payload.get("modifier_ids", [])
            if not isinstance(selected_ids, list) or not all(isinstance(item, str) for item in selected_ids):
                raise ValueError("测试效果列表格式错误。")

            baseline, final_skill = self._build_test_final_skill(
                package=package,
                selected_ids=selected_ids if use_modifier_stack else [],
                relation=relation,
                source_power=source_power,
                target_power=target_power,
                conduit_power=conduit_power,
            )
            enemies = [self._enemy_runtime_view(enemy) for enemy in scene["enemies"]]
            events = SkillRuntime().execute(
                final_skill,
                source_entity="skill_test_player",
                source_position=_ArenaPoint(TEST_ARENA_SOURCE["x"], TEST_ARENA_SOURCE["y"]),
                target_entity=enemies[0]["enemy_id"],
                target_position=_ArenaPoint(enemies[0]["position"]["x"], enemies[0]["position"]["y"]),
                timestamp_ms=0,
                target_entities=[
                    {"entity_id": enemy["enemy_id"], "position": enemy["position"]}
                    for enemy in enemies
                ],
            )
            result = self._test_arena_result(
                scene=scene,
                enemies=enemies,
                events=events,
                baseline=baseline,
                final_skill=final_skill,
                use_modifier_stack=use_modifier_stack,
                relation=relation,
                source_power=source_power,
                target_power=target_power,
                conduit_power=conduit_power,
            )
            return {
                "ok": True,
                "message_text": "测试运行完成，结果仅用于技能编辑器临时验证。",
                "result": result,
            }
        except Exception as exc:
            return {"ok": False, "message_text": _chinese_test_arena_error(exc), "result": None}

    def _save_result(self, ok: bool, message_text: str) -> dict[str, Any]:
        return {
            "ok": ok,
            "message_text": message_text,
            "skill_editor": self.view(),
        }

    def _testable_modifier_options(self) -> list[dict[str, Any]]:
        definitions = load_gem_definitions(self.config_root)
        scaling_rules = load_skill_scaling_rules(self.config_root)
        localization = load_localization(self.config_root)
        grouped: dict[str, list[SupportBaseModifier]] = {}
        for modifier in scaling_rules.support_base_modifiers:
            grouped.setdefault(modifier.support_id, []).append(modifier)
        conduit_by_support: dict[str, list[dict[str, Any]]] = {}
        for amplifier in scaling_rules.conduit_amplifiers:
            conduit_by_support.setdefault(amplifier.support_id, []).append(
                {
                    "stat": "conduit_multiplier",
                    "value": amplifier.multiplier,
                    "layer": "final",
                    "relation": amplifier.relation,
                }
            )

        options: list[dict[str, Any]] = []
        for support_id in sorted(set(grouped) | set(conduit_by_support)):
            definition = definitions.get(support_id)
            if definition is None or not definition.is_support:
                continue
            stats = [
                self._stat_option_view(modifier.stat, modifier.value, modifier.layer, localization)
                for modifier in grouped.get(support_id, [])
            ]
            stats.extend(
                self._stat_option_view(
                    str(entry["stat"]),
                    float(entry["value"]),
                    str(entry["layer"]),
                    localization,
                    relation=str(entry["relation"]),
                )
                for entry in conduit_by_support.get(support_id, [])
            )
            options.append(
                {
                    "id": support_id,
                    "name_text": localization.get(definition.name_key, support_id),
                    "description_text": _format_description(
                        localization.get(definition.description_key, ""),
                        _support_description_values(
                            grouped.get(support_id, []),
                            conduit_by_support.get(support_id, []),
                        ),
                    ),
                    "source_text": "辅助宝石配置 / scaling 规则",
                    "category": definition.category,
                    "stats": stats,
                    "filter_text": _apply_filter_text(definition, localization),
                }
            )
        return options

    def _build_modifier_stack_preview(
        self,
        *,
        selected_ids: list[str],
        relation: str,
        source_power: float,
        target_power: float,
        conduit_power: float,
    ) -> tuple[FinalSkillInstance, FinalSkillInstance]:
        calculator, active = self._test_calculator()
        template = load_skill_templates(self.config_root)["skill_fire_bolt"]
        baseline = calculator.calculate_for_active(active)
        modifiers = tuple(
            self._test_applied_modifiers(
                selected_ids=selected_ids,
                relation=relation,
                source_power=source_power,
                target_power=target_power,
                conduit_power=conduit_power,
            )
        )
        tested = calculator._build_final_skill(active, template, modifiers)
        return baseline, tested

    def _build_test_final_skill(
        self,
        *,
        package: dict[str, Any],
        selected_ids: list[str],
        relation: str,
        source_power: float,
        target_power: float,
        conduit_power: float,
    ) -> tuple[FinalSkillInstance, FinalSkillInstance]:
        calculator, active = self._test_calculator()
        template = _skill_template_from_package(package)
        baseline = calculator._build_final_skill(active, template, ())
        modifiers = tuple(
            self._test_applied_modifiers(
                selected_ids=selected_ids,
                relation=relation,
                source_power=source_power,
                target_power=target_power,
                conduit_power=conduit_power,
            )
        )
        tested = calculator._build_final_skill(active, template, modifiers)
        return baseline, tested

    def _test_applied_modifiers(
        self,
        *,
        selected_ids: list[str],
        relation: str,
        source_power: float,
        target_power: float,
        conduit_power: float,
    ) -> list[AppliedModifier]:
        definitions = load_gem_definitions(self.config_root)
        scaling_rules = load_skill_scaling_rules(self.config_root)
        relation_coefficients = load_relation_coefficients(self.config_root)
        active_definition = definitions[TESTABLE_SKILL_ID]
        support_modifiers: dict[str, list[SupportBaseModifier]] = {}
        for modifier in scaling_rules.support_base_modifiers:
            support_modifiers.setdefault(modifier.support_id, []).append(modifier)
        conduit_relations = {amplifier.support_id for amplifier in scaling_rules.conduit_amplifiers}
        conduit_by_support = {
            amplifier.support_id: amplifier.multiplier
            for amplifier in scaling_rules.conduit_amplifiers
            if amplifier.relation == relation
        }

        modifiers: list[AppliedModifier] = []
        dedupe: set[tuple[str, str, str]] = set()
        relation_scale = relation_coefficients[relation]
        if relation != "adjacent":
            relation_scale *= source_power * target_power * conduit_power
        selected_conduit_multiplier = 1.0
        for support_id in selected_ids:
            if support_id in conduit_by_support:
                selected_conduit_multiplier *= conduit_by_support[support_id]
                modifiers.append(
                    self._test_modifier(
                        support_id=support_id,
                        stat="conduit_multiplier",
                        value=conduit_by_support[support_id],
                        layer="final",
                        relation=relation,
                        applied=True,
                        reason_key="modifier.conduit_amplifier",
                    )
                )
            elif support_id in conduit_relations:
                modifiers.append(
                    self._test_modifier(
                        support_id=support_id,
                        stat="conduit_multiplier",
                        value=1.0,
                        layer="ignored",
                        relation=relation,
                        applied=False,
                        reason_key="modifier.ignored.relation_mismatch",
                    )
                )

        for support_id in selected_ids:
            definition = definitions.get(support_id)
            if definition is None or not definition.is_support:
                modifiers.append(self._ignored_unknown_modifier(support_id, relation))
                continue
            base_modifiers = support_modifiers.get(support_id, [])
            if not base_modifiers:
                if support_id not in conduit_by_support:
                    modifiers.append(
                        self._test_modifier(
                            support_id=support_id,
                            stat="unknown",
                            value=0,
                            layer="ignored",
                            relation=relation,
                            applied=False,
                            reason_key="modifier.ignored.no_supported_stat",
                        )
                    )
                continue
            if not _gem_filter_matches(definition, active_definition):
                for base_modifier in base_modifiers:
                    modifiers.append(
                        self._test_modifier(
                            support_id=support_id,
                            stat=base_modifier.stat,
                            value=base_modifier.value,
                            layer="ignored",
                            relation=relation,
                            applied=False,
                            reason_key="modifier.ignored.apply_filter",
                        )
                    )
                continue
            for base_modifier in base_modifiers:
                if base_modifier.stat not in scaling_rules.stat_layers:
                    modifiers.append(
                        self._test_modifier(
                            support_id=support_id,
                            stat=base_modifier.stat,
                            value=base_modifier.value,
                            layer="ignored",
                            relation=relation,
                            applied=False,
                            reason_key="modifier.ignored.unsupported_stat",
                        )
                    )
                    continue
                dedupe_key = (support_id, TEST_ACTIVE_INSTANCE_ID, base_modifier.stat)
                if dedupe_key in dedupe:
                    modifiers.append(
                        self._test_modifier(
                            support_id=support_id,
                            stat=base_modifier.stat,
                            value=base_modifier.value,
                            layer="ignored",
                            relation=relation,
                            applied=False,
                            reason_key="modifier.ignored.duplicate_source_target_stat",
                        )
                    )
                    continue
                dedupe.add(dedupe_key)
                modifiers.append(
                    self._test_modifier(
                        support_id=support_id,
                        stat=base_modifier.stat,
                        value=base_modifier.value * relation_scale * selected_conduit_multiplier,
                        layer=base_modifier.layer,
                        relation=relation,
                        applied=True,
                        reason_key="modifier.support_base",
                    )
                )
        return modifiers

    def _test_calculator(self) -> tuple[SkillEffectCalculator, Any]:
        definitions = load_gem_definitions(self.config_root)
        inventory = GemInventory(definitions)
        board = SudokuGemBoard(load_board_rules(self.config_root), inventory)
        active = inventory.add_instance(TEST_ACTIVE_INSTANCE_ID, TESTABLE_SKILL_ID)
        calculator = SkillEffectCalculator(
            board=board,
            definitions=definitions,
            skill_templates=load_skill_templates(self.config_root),
            relation_coefficients=load_relation_coefficients(self.config_root),
            scaling_rules=load_skill_scaling_rules(self.config_root),
            affix_definitions={},
        )
        return calculator, active

    def _test_modifier(
        self,
        *,
        support_id: str,
        stat: str,
        value: float,
        layer: str,
        relation: str,
        applied: bool,
        reason_key: str,
    ) -> AppliedModifier:
        definitions = load_gem_definitions(self.config_root)
        definition = definitions.get(support_id)
        return AppliedModifier(
            source_instance_id=f"test_modifier:{support_id}",
            source_base_gem_id=support_id if support_id in definitions else TESTABLE_SKILL_ID,
            target_instance_id=TEST_ACTIVE_INSTANCE_ID,
            target_base_gem_id=TESTABLE_SKILL_ID,
            stat=stat,
            value=float(value),
            layer=layer,
            relation=relation,
            reason_key=reason_key,
            applied=applied,
            shape_effect=definition.shape_effect if definition is not None else "",
        )

    def _ignored_unknown_modifier(self, support_id: str, relation: str) -> AppliedModifier:
        return AppliedModifier(
            source_instance_id=f"test_modifier:{support_id}",
            source_base_gem_id=TESTABLE_SKILL_ID,
            target_instance_id=TEST_ACTIVE_INSTANCE_ID,
            target_base_gem_id=TESTABLE_SKILL_ID,
            stat="unknown",
            value=0.0,
            layer="ignored",
            relation=relation,
            reason_key="modifier.ignored.unknown_modifier",
            applied=False,
        )

    def _final_skill_summary(self, final_skill: FinalSkillInstance) -> dict[str, Any]:
        runtime_params = final_skill.runtime_params or {}
        return {
            "final_damage": final_skill.final_damage,
            "final_cooldown_ms": final_skill.final_cooldown_ms,
            "projectile_count": final_skill.projectile_count,
            "projectile_speed": runtime_params.get("projectile_speed", 0),
        }

    def _package_for_test_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        package = payload.get("package")
        if package is None:
            result = self._read_active_skill_packages().get(TESTABLE_SKILL_ID)
            if result is None or not result.is_valid:
                raise ValueError("火焰弹技能包未通过校验，无法运行测试场。")
            package = result.data
        if not isinstance(package, dict):
            raise ValueError("测试技能包内容格式错误。")
        if package.get("id") != TESTABLE_SKILL_ID:
            raise ValueError("测试场第一版只允许运行 active_fire_bolt。")
        package_to_test = deepcopy(package)
        schema = load_skill_schema(self.config_root)
        behavior_templates = load_behavior_templates(self.config_root)
        validate_skill_package_data(package_to_test, schema, behavior_templates, self._package_path(TESTABLE_SKILL_ID))
        self._validate_localization_references(package_to_test)
        return package_to_test

    def _require_scene(self, scene_id: str) -> dict[str, Any]:
        for scene in TEST_ARENA_SCENES:
            if scene["scene_id"] == scene_id:
                return scene
        raise ValueError("测试场景不存在。")

    def _scene_view(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "scene_id": scene["scene_id"],
            "name_text": scene["name_text"],
            "enemies": [self._enemy_runtime_view(enemy) for enemy in scene["enemies"]],
        }

    def _enemy_runtime_view(self, enemy: dict[str, Any]) -> dict[str, Any]:
        return {
            "enemy_id": enemy["enemy_id"],
            "name_text": enemy["name_text"],
            "position": {"x": float(enemy["position"]["x"]), "y": float(enemy["position"]["y"])},
            "max_life": float(enemy["max_life"]),
            "current_life": float(enemy["max_life"]),
            "is_alive": True,
        }

    def _test_arena_result(
        self,
        *,
        scene: dict[str, Any],
        enemies: list[dict[str, Any]],
        events: tuple[SkillEvent, ...],
        baseline: FinalSkillInstance,
        final_skill: FinalSkillInstance,
        use_modifier_stack: bool,
        relation: str,
        source_power: float,
        target_power: float,
        conduit_power: float,
    ) -> dict[str, Any]:
        stages = _arena_stages(enemies, events)
        final_stage = stages[-1] if stages else _arena_stage("初始状态", enemies, (), ())
        event_counts = _event_counts(events)
        damage_events = [event for event in events if event.type == "damage"]
        first_damage_delay = min((event.delay_ms for event in damage_events), default=0)
        spawn_stage = stages[0] if stages else final_stage
        return {
            "skill_id": TESTABLE_SKILL_ID,
            "skill_name_text": self._localized_text("gem.active_fire_bolt.name"),
            "scene_id": scene["scene_id"],
            "scene_name_text": scene["name_text"],
            "modifier_stack_enabled": use_modifier_stack,
            "modifier_relation_text": RELATION_TEXT[relation],
            "source_power": source_power,
            "target_power": target_power,
            "conduit_power": conduit_power,
            "baseline": self._final_skill_summary(baseline),
            "tested": self._final_skill_summary(final_skill),
            "monsters": final_stage["monsters"],
            "initial_monsters": deepcopy(enemies),
            "hit_targets": _hit_targets(enemies, damage_events),
            "damage_results": _damage_results(enemies, damage_events),
            "event_count": len(events),
            "event_counts": event_counts,
            "has_projectile_spawn": event_counts.get("projectile_spawn", 0) > 0,
            "has_damage": event_counts.get("damage", 0) > 0,
            "has_hit_vfx": event_counts.get("hit_vfx", 0) > 0,
            "has_floating_text": event_counts.get("floating_text", 0) > 0,
            "flight_no_damage_passed": all(
                monster["current_life"] == monster["max_life"]
                for monster in spawn_stage["monsters"]
            ),
            "flight_duration_ms": first_damage_delay,
            "stages": stages,
            "event_summary": _event_summary(events),
            "event_timeline": _event_timeline(events),
            "timeline_supported_types": [
                {"type": event_type, "text": _event_type_text(event_type)}
                for event_type in TIMELINE_EVENT_TYPES
            ],
            "timeline_checks": _timeline_checks(events, spawn_stage["monsters"]),
            "writes_real_data": False,
        }

    def _modifier_preview_view(self, modifier: AppliedModifier) -> dict[str, Any]:
        localization = load_localization(self.config_root)
        definitions = load_gem_definitions(self.config_root)
        definition = definitions.get(modifier.source_base_gem_id)
        return {
            "id": modifier.source_base_gem_id,
            "name_text": localization.get(definition.name_key, modifier.source_base_gem_id) if definition else modifier.source_base_gem_id,
            "stat": self._stat_option_view(modifier.stat, modifier.value, modifier.layer, localization),
            "value": modifier.value,
            "layer": modifier.layer,
            "layer_text": _layer_text(modifier.layer, localization),
            "relation": modifier.relation,
            "relation_text": RELATION_TEXT.get(modifier.relation, modifier.relation),
            "reason_key": modifier.reason_key,
            "reason_text": _reason_text(modifier.reason_key, localization),
            "applied": modifier.applied,
        }

    def _stat_option_view(
        self,
        stat: str,
        value: float,
        layer: str,
        localization: dict[str, str],
        *,
        relation: str = "",
    ) -> dict[str, Any]:
        if stat == "conduit_multiplier":
            stat_text = localization.get("ui.modifier.conduit_multiplier", "导管放大倍率")
        else:
            prefix = "routing_stat" if stat.startswith(("source_power_", "target_power_")) else "stat"
            stat_text = localization.get(f"{prefix}.{stat}.name", stat)
        return {
            "stat": stat,
            "stat_text": stat_text,
            "value": value,
            "layer": layer,
            "layer_text": _layer_text(layer, localization),
            "relation": relation,
            "relation_text": RELATION_TEXT.get(relation, "") if relation else "",
        }

    def _normalize_relation(self, relation: str) -> str:
        normalized = RELATION_ALIASES.get(relation)
        if normalized is None:
            raise ValueError("关系模拟只能选择相邻、同行、同列或同宫。")
        return normalized

    def _validated_power(self, value: Any, label: str) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} 必须是数字。") from exc
        if not POWER_MIN <= number <= POWER_MAX:
            raise ValueError(f"{label} 必须在 {POWER_MIN:g} 到 {POWER_MAX:g} 之间。")
        return number

    def _localized_text(self, key: str) -> str:
        localization = load_localization(self.config_root)
        return localization.get(key, key)

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


def _support_description_values(
    modifiers: list[SupportBaseModifier],
    conduits: list[dict[str, Any]],
) -> dict[str, str]:
    values: dict[str, str] = {}
    for modifier in modifiers:
        values[modifier.stat] = _format_config_number(modifier.value)
        values[f"{modifier.stat}_abs"] = _format_config_number(abs(modifier.value))
        if "projectile_count" in modifier.stat:
            values[f"{modifier.stat}_text"] = _count_text(modifier.value, "枚")
    for conduit in conduits:
        multiplier = float(conduit["value"])
        values["conduit_multiplier"] = _format_config_number(multiplier)
        values["conduit_bonus_percent"] = _format_config_number((multiplier - 1) * 100)
    return values


def _format_description(template: str, values: dict[str, str]) -> str:
    try:
        return template.format(**values)
    except (KeyError, ValueError):
        return template


def _count_text(value: float, counter: str) -> str:
    number = int(value) if float(value).is_integer() else value
    text = {
        0: "零",
        1: "一",
        2: "两",
        3: "三",
        4: "四",
        5: "五",
        6: "六",
        7: "七",
        8: "八",
        9: "九",
        10: "十",
    }.get(number, _format_config_number(value))
    return f"{text}{counter}"


def _format_config_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


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


def _gem_filter_matches(definition: GemDefinition, target_definition: GemDefinition) -> bool:
    if definition.apply_filter_target_kinds and target_definition.gem_kind not in definition.apply_filter_target_kinds:
        return False
    target_tags = target_definition.tags
    if definition.apply_filter_tags_any and not (definition.apply_filter_tags_any & target_tags):
        return False
    if definition.apply_filter_tags_all and not definition.apply_filter_tags_all.issubset(target_tags):
        return False
    if definition.apply_filter_tags_none and definition.apply_filter_tags_none & target_tags:
        return False
    return True


def _apply_filter_text(definition: GemDefinition, localization: dict[str, str]) -> str:
    parts: list[str] = []
    if definition.apply_filter_target_kinds:
        parts.append("目标：" + "、".join(_gem_kind_text(kind, localization) for kind in sorted(definition.apply_filter_target_kinds)))
    if definition.apply_filter_tags_any:
        parts.append("任一标签：" + "、".join(_tag_text(tag, localization) for tag in sorted(definition.apply_filter_tags_any)))
    if definition.apply_filter_tags_all:
        parts.append("全部标签：" + "、".join(_tag_text(tag, localization) for tag in sorted(definition.apply_filter_tags_all)))
    if definition.apply_filter_tags_none:
        parts.append("排除标签：" + "、".join(_tag_text(tag, localization) for tag in sorted(definition.apply_filter_tags_none)))
    return "；".join(parts) if parts else "无额外过滤条件"


def _gem_kind_text(gem_kind: str, localization: dict[str, str]) -> str:
    key_by_kind = {
        "active_skill": "tag.active_skill_gem.name",
        "passive_skill": "tag.passive_skill_gem.name",
        "support": "tag.support_gem.name",
    }
    return localization.get(key_by_kind.get(gem_kind, ""), gem_kind)


def _tag_text(tag: str, localization: dict[str, str]) -> str:
    return localization.get(f"tag.{tag}.name", tag)


def _layer_text(layer: str, localization: dict[str, str]) -> str:
    return localization.get(f"ui.modifier.layer.{layer}", "未生效" if layer == "ignored" else layer)


def _reason_text(reason_key: str, localization: dict[str, str]) -> str:
    fallbacks = {
        "modifier.ignored.unknown_modifier": "测试效果不存在。",
        "modifier.ignored.apply_filter": "适用标签不匹配，未生效。",
        "modifier.ignored.no_supported_stat": "该效果没有当前可测试的属性。",
        "modifier.ignored.relation_mismatch": "导管效果与当前模拟关系不匹配。",
        "modifier.ignored.unsupported_stat": "当前阶段暂不支持该属性。",
    }
    return localization.get(reason_key, fallbacks.get(reason_key, reason_key))


def _chinese_modifier_stack_error(error: Exception) -> str:
    message = str(error)
    if _contains_cjk(message):
        return message
    return "测试 Modifier 栈计算失败，请检查选择的效果和测试参数。"


def _chinese_test_arena_error(error: Exception) -> str:
    message = str(error)
    if _contains_cjk(message):
        return message
    return "技能测试场运行失败，请检查技能包、测试场景和测试参数。"


def _arena_stages(enemies: list[dict[str, Any]], events: tuple[SkillEvent, ...]) -> list[dict[str, Any]]:
    spawn_events = tuple(event for event in events if event.type == "projectile_spawn")
    stages = [_arena_stage("投射物飞行中", enemies, events, spawn_events)]
    damage_delays = sorted({event.delay_ms for event in events if event.type == "damage"})
    for delay in damage_delays:
        stage_events = tuple(event for event in events if event.delay_ms <= delay)
        stages.append(_arena_stage(f"{delay} 毫秒命中结算", enemies, events, stage_events))
    return stages


def _arena_stage(
    stage_name_text: str,
    enemies: list[dict[str, Any]],
    all_events: tuple[SkillEvent, ...],
    applied_events: tuple[SkillEvent, ...],
) -> dict[str, Any]:
    life_by_id = {enemy["enemy_id"]: float(enemy["max_life"]) for enemy in enemies}
    damage_events = [event for event in applied_events if event.type == "damage"]
    for event in sorted(damage_events, key=lambda item: (item.delay_ms, item.event_id)):
        if event.target_entity in life_by_id:
            life_by_id[event.target_entity] = max(0.0, life_by_id[event.target_entity] - float(event.amount or 0.0))
    monsters = []
    for enemy in enemies:
        current_life = life_by_id[enemy["enemy_id"]]
        monsters.append(
            {
                **deepcopy(enemy),
                "current_life": current_life,
                "is_alive": current_life > 0,
            }
        )
    return {
        "stage_name_text": stage_name_text,
        "monsters": monsters,
        "hit_targets": _hit_targets(enemies, damage_events),
        "damage_results": _damage_results(enemies, damage_events),
        "applied_event_count": len(applied_events),
        "event_summary": _event_summary(applied_events),
        "total_event_count": len(all_events),
    }


def _event_counts(events: tuple[SkillEvent, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        counts[event.type] = counts.get(event.type, 0) + 1
    return counts


def _event_summary(events: tuple[SkillEvent, ...]) -> list[dict[str, Any]]:
    return [
        {
            "event_id": event.event_id,
            "type": event.type,
            "type_text": _event_type_text(event.type),
            "delay_ms": event.delay_ms,
            "duration_ms": event.duration_ms,
            "target_entity": event.target_entity,
            "amount": event.amount,
            "projectile_index": event.payload.get("projectile_index"),
        }
        for event in sorted(events, key=lambda item: (item.delay_ms, _event_sort_order(item.type), item.event_id))
    ]


def _event_timeline(events: tuple[SkillEvent, ...]) -> list[dict[str, Any]]:
    timeline = []
    for original_index, event in enumerate(events):
        item = event.to_dict()
        item["original_index"] = original_index
        item["type_text"] = _event_type_text(event.type)
        item["payload_text"] = json.dumps(event.payload, ensure_ascii=False, sort_keys=True)
        timeline.append(item)
    return sorted(timeline, key=lambda item: (int(item["timestamp_ms"]), int(item["original_index"])))


def _timeline_checks(events: tuple[SkillEvent, ...], flight_stage_monsters: list[dict[str, Any]]) -> dict[str, Any]:
    event_counts = _event_counts(events)
    spawn_times = [event.timestamp_ms for event in events if event.type == "projectile_spawn"]
    damage_times = [event.timestamp_ms for event in events if event.type == "damage"]
    damage_after_spawn = bool(spawn_times and damage_times and min(damage_times) >= min(spawn_times))
    flight_no_damage = all(
        monster["current_life"] == monster["max_life"]
        for monster in flight_stage_monsters
    )
    basic_timing_passed = (
        event_counts.get("projectile_spawn", 0) > 0
        and event_counts.get("damage", 0) > 0
        and event_counts.get("hit_vfx", 0) > 0
        and event_counts.get("floating_text", 0) > 0
        and damage_after_spawn
        and flight_no_damage
    )
    return {
        "has_projectile_spawn": event_counts.get("projectile_spawn", 0) > 0,
        "has_damage": event_counts.get("damage", 0) > 0,
        "has_hit_vfx": event_counts.get("hit_vfx", 0) > 0,
        "has_floating_text": event_counts.get("floating_text", 0) > 0,
        "damage_after_or_at_projectile_spawn": damage_after_spawn,
        "flight_no_damage_passed": flight_no_damage,
        "basic_timing_passed": basic_timing_passed,
    }


def _event_sort_order(event_type: str) -> int:
    order = {
        "projectile_spawn": 0,
        "damage": 1,
        "hit_vfx": 2,
        "floating_text": 3,
    }
    return order.get(event_type, 99)


def _event_type_text(event_type: str) -> str:
    return {
        "cast_start": "释放开始",
        "projectile_spawn": "投射物生成",
        "projectile_hit": "投射物命中",
        "damage": "伤害结算",
        "hit_vfx": "命中特效",
        "floating_text": "伤害浮字",
        "cooldown_update": "冷却更新",
    }.get(event_type, event_type)


def _hit_targets(enemies: list[dict[str, Any]], damage_events: list[SkillEvent]) -> list[dict[str, str]]:
    enemies_by_id = {enemy["enemy_id"]: enemy for enemy in enemies}
    seen: set[str] = set()
    targets = []
    for event in damage_events:
        if event.target_entity in seen:
            continue
        seen.add(event.target_entity)
        enemy = enemies_by_id.get(event.target_entity)
        targets.append(
            {
                "enemy_id": event.target_entity,
                "name_text": enemy["name_text"] if enemy else event.target_entity,
            }
        )
    return targets


def _damage_results(enemies: list[dict[str, Any]], damage_events: list[SkillEvent]) -> list[dict[str, Any]]:
    enemies_by_id = {enemy["enemy_id"]: enemy for enemy in enemies}
    return [
        {
            "enemy_id": event.target_entity,
            "name_text": enemies_by_id.get(event.target_entity, {}).get("name_text", event.target_entity),
            "amount": float(event.amount or 0.0),
            "delay_ms": event.delay_ms,
            "projectile_index": event.payload.get("projectile_index"),
        }
        for event in sorted(damage_events, key=lambda item: (item.delay_ms, item.event_id))
    ]


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
