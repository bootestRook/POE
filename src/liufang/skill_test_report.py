from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from math import acos, hypot
from pathlib import Path
from typing import Any

from .skill_editor import SkillEditorService


EXPECTED_PLAYER_DESCRIPTIONS = {
    "active_fire_bolt": "发射一枚火球，命中敌人造成火焰伤害。",
    "active_ice_shards": "自动向最近敌人方向射出多枚冰霜冰棱，冰棱以扇形展开飞行，命中后造成冰霜伤害，并显示冰霜命中特效与伤害浮字。",
    "active_frost_nova": "自动以玩家自身为中心释放一圈向外扩散的冰霜新星，命中范围内敌人后造成冰霜伤害，并显示冰霜范围爆发特效与伤害浮字。",
    "active_puncture": "自动朝锁定敌人的方向发出一列地刺，命中矩形范围内敌人后造成物理伤害，并显示地刺命中特效与伤害浮字。",
}


@dataclass(frozen=True)
class SkillTestReportRequest:
    skill_id: str = "active_fire_bolt"
    scenario_id: str = "single_dummy"
    use_modifier_stack: bool = False
    modifier_ids: tuple[str, ...] = ()
    relation: str = "adjacent"
    source_power: float = 1.0
    target_power: float = 1.0
    conduit_power: float = 1.0


@dataclass(frozen=True)
class SkillTestReport:
    markdown: str
    conclusion: str
    inconsistencies: tuple[str, ...]
    suggestions: tuple[str, ...]
    source_result: dict[str, Any]


def generate_skill_test_report(config_root: Path, request: SkillTestReportRequest) -> SkillTestReport:
    service = SkillEditorService(config_root)
    editor_view = service.view()
    entry = _require_skill_entry(editor_view, request.skill_id)
    arena_result = _run_arena(service, request)
    modifier_stack = _modifier_stack_summary(editor_view, request, arena_result)
    checks = _report_checks(service, entry, request, arena_result)
    conclusion, reasons = _conclusion(checks)
    inconsistencies = tuple(reason for reason in reasons if reason)
    suggestions = _suggestions(inconsistencies)
    markdown = _markdown_report(
        entry=entry,
        arena_result=arena_result,
        modifier_stack=modifier_stack,
        expected_description=EXPECTED_PLAYER_DESCRIPTIONS.get(request.skill_id, "暂无受控期望描述。"),
        checks=checks,
        conclusion=conclusion,
        inconsistencies=inconsistencies,
        suggestions=suggestions,
    )
    return SkillTestReport(
        markdown=markdown,
        conclusion=conclusion,
        inconsistencies=inconsistencies,
        suggestions=suggestions,
        source_result=arena_result,
    )


def write_skill_test_report(
    config_root: Path,
    request: SkillTestReportRequest,
    output_dir: Path,
    *,
    timestamp: datetime | None = None,
) -> Path:
    report = generate_skill_test_report(config_root, request)
    output_dir.mkdir(parents=True, exist_ok=True)
    moment = timestamp or datetime.now()
    filename = f"{request.skill_id}_{request.scenario_id}_{moment:%Y%m%d_%H%M%S}.md"
    output_path = output_dir / filename
    output_path.write_text(report.markdown, encoding="utf-8")
    return output_path


def _run_arena(service: SkillEditorService, request: SkillTestReportRequest, package: dict[str, Any] | None = None) -> dict[str, Any]:
    arena_payload = {
        "skill_id": request.skill_id,
        "scene_id": request.scenario_id,
        "package": package,
        "use_modifier_stack": request.use_modifier_stack if package is None else False,
        "modifier_ids": list(request.modifier_ids) if package is None else [],
        "relation": request.relation,
        "source_power": request.source_power,
        "target_power": request.target_power,
        "conduit_power": request.conduit_power,
    }
    arena_response = service.run_test_arena(arena_payload)
    if not arena_response["ok"] or arena_response["result"] is None:
        raise ValueError(arena_response["message_text"])
    return arena_response["result"]


def _require_skill_entry(editor_view: dict[str, Any], skill_id: str) -> dict[str, Any]:
    for entry in editor_view["entries"]:
        if entry["id"] == skill_id and entry["openable"]:
            return entry
    raise ValueError("技能尚未迁移为可测试 Skill Package。")


def _modifier_stack_summary(
    editor_view: dict[str, Any],
    request: SkillTestReportRequest,
    arena_result: dict[str, Any],
) -> dict[str, Any]:
    available = {modifier["id"]: modifier for modifier in editor_view["modifier_stack"]["available_modifiers"]}
    selected = [
        {
            "id": modifier_id,
            "name_text": available.get(modifier_id, {}).get("name_text", modifier_id),
            "stats": available.get(modifier_id, {}).get("stats", []),
        }
        for modifier_id in request.modifier_ids
    ]
    return {
        "enabled": request.use_modifier_stack,
        "relation_text": arena_result["modifier_relation_text"],
        "source_power": request.source_power,
        "target_power": request.target_power,
        "conduit_power": request.conduit_power,
        "selected": selected,
        "baseline": arena_result["baseline"],
        "tested": arena_result["tested"],
    }


def _report_checks(
    service: SkillEditorService,
    entry: dict[str, Any],
    request: SkillTestReportRequest,
    arena_result: dict[str, Any],
) -> dict[str, bool]:
    timeline_checks = arena_result["timeline_checks"]
    damage_results = arena_result["damage_results"]
    damage_events = [event for event in arena_result["event_timeline"] if event["type"] == "damage"]
    spawn_events = [event for event in arena_result["event_timeline"] if event["type"] == "projectile_spawn"]
    area_events = [event for event in arena_result["event_timeline"] if event["type"] == "area_spawn"]
    melee_events = [event for event in arena_result["event_timeline"] if event["type"] == "melee_arc"]
    zone_events = [event for event in arena_result["event_timeline"] if event["type"] == "damage_zone"]
    uses_area_nova = entry.get("behavior_template") == "player_nova"
    uses_melee_arc = entry.get("behavior_template") == "melee_arc"
    uses_damage_zone = entry.get("behavior_template") == "damage_zone"
    expected_damage_type = "physical" if request.skill_id == "active_puncture" else ("cold" if request.skill_id in {"active_ice_shards", "active_frost_nova"} else "fire")
    life_reduced = any(monster["current_life"] < monster["max_life"] for monster in arena_result["monsters"])
    modifier_changed = (
        arena_result["baseline"]["final_damage"] != arena_result["tested"]["final_damage"]
        or arena_result["baseline"]["final_cooldown_ms"] != arena_result["tested"]["final_cooldown_ms"]
        or arena_result["baseline"]["projectile_count"] != arena_result["tested"]["projectile_count"]
        or arena_result["baseline"]["projectile_speed"] != arena_result["tested"]["projectile_speed"]
        or arena_result["baseline"].get("radius") != arena_result["tested"].get("radius")
        or arena_result["baseline"].get("length") != arena_result["tested"].get("length")
        or arena_result["baseline"].get("width") != arena_result["tested"].get("width")
    )
    return {
        "uses_area_nova": uses_area_nova,
        "uses_melee_arc": uses_melee_arc,
        "uses_damage_zone": uses_damage_zone,
        "expected_damage_type": expected_damage_type,
        "has_projectile_spawn": bool(timeline_checks["has_projectile_spawn"]),
        "has_multiple_projectile_spawn": request.skill_id != "active_ice_shards" or bool(timeline_checks.get("has_multiple_projectile_spawn")),
        "fan_direction_passed": request.skill_id != "active_ice_shards" or bool(timeline_checks.get("fan_direction_passed")),
        "has_area_spawn": (not uses_area_nova) or bool(timeline_checks.get("has_area_spawn")),
        "area_center_passed": (not uses_area_nova) or bool(timeline_checks.get("area_center_passed")),
        "damage_after_or_at_area_hit": (not uses_area_nova) or bool(timeline_checks.get("damage_after_or_at_area_hit")),
        "area_range_targets_passed": (not uses_area_nova) or _area_range_targets_passed(area_events, damage_events),
        "has_melee_arc": (not uses_melee_arc) or bool(timeline_checks.get("has_melee_arc")),
        "melee_arc_origin_passed": (not uses_melee_arc) or bool(timeline_checks.get("melee_arc_origin_passed")),
        "melee_arc_faces_nearest_target": (not uses_melee_arc) or _melee_arc_faces_nearest_target(melee_events, arena_result["initial_monsters"]),
        "damage_after_or_at_melee_hit": (not uses_melee_arc) or bool(timeline_checks.get("damage_after_or_at_melee_hit")),
        "melee_arc_targets_passed": (not uses_melee_arc) or _melee_arc_targets_passed(melee_events, damage_events),
        "has_damage_zone": (not uses_damage_zone) or bool(timeline_checks.get("has_damage_zone")),
        "damage_zone_origin_passed": (not uses_damage_zone) or bool(timeline_checks.get("damage_zone_origin_passed")),
        "damage_zone_faces_nearest_target": (not uses_damage_zone) or _damage_zone_faces_nearest_target(zone_events, arena_result["initial_monsters"]),
        "damage_after_or_at_damage_zone_hit": (not uses_damage_zone) or bool(timeline_checks.get("damage_after_or_at_damage_zone_hit")),
        "damage_zone_targets_passed": (not uses_damage_zone) or _damage_zone_targets_passed(zone_events, damage_events),
        "has_projectile_hit": bool(timeline_checks.get("has_projectile_hit")),
        "has_damage": bool(timeline_checks["has_damage"]),
        "has_hit_vfx": bool(timeline_checks["has_hit_vfx"]),
        "has_floating_text": bool(timeline_checks["has_floating_text"]),
        "damage_after_or_at_projectile_spawn": bool(timeline_checks["damage_after_or_at_projectile_spawn"]),
        "flight_no_damage_passed": bool(timeline_checks["flight_no_damage_passed"]),
        "life_reduced_after_damage": life_reduced,
        "damage_type_expected": bool(damage_events) and all(event["damage_type"] == expected_damage_type for event in damage_events),
        "hit_target_exists": bool(arena_result["hit_targets"]) and bool(damage_results),
        "modifier_stack_changed_result": (not arena_result["modifier_stack_enabled"]) or modifier_changed,
        **_parameter_variant_checks(service, entry, request, spawn_events),
    }


def _area_range_targets_passed(area_events: list[dict[str, Any]], damage_events: list[dict[str, Any]]) -> bool:
    if not area_events or not damage_events:
        return False
    area = area_events[0]
    payload = area.get("payload", {})
    center = payload.get("center", area.get("position", {})) if isinstance(payload, dict) else area.get("position", {})
    radius = float(payload.get("radius", 0)) if isinstance(payload, dict) else 0.0
    if not isinstance(center, dict) or radius <= 0:
        return False
    for event in damage_events:
        event_payload = event.get("payload", {})
        target = event_payload.get("target_world_position", event.get("position", {})) if isinstance(event_payload, dict) else event.get("position", {})
        if not isinstance(target, dict):
            return False
        target_distance = (
            (float(target.get("x", 0.0)) - float(center.get("x", 0.0))) ** 2
            + (float(target.get("y", 0.0)) - float(center.get("y", 0.0))) ** 2
        ) ** 0.5
        if target_distance > radius:
            return False
    return True


def _melee_arc_faces_nearest_target(melee_events: list[dict[str, Any]], initial_monsters: list[dict[str, Any]]) -> bool:
    if not melee_events or not initial_monsters:
        return False
    event = melee_events[0]
    payload = event.get("payload", {})
    origin = payload.get("origin", event.get("position", {})) if isinstance(payload, dict) else event.get("position", {})
    facing = payload.get("facing_direction", event.get("direction", {})) if isinstance(payload, dict) else event.get("direction", {})
    if not isinstance(origin, dict) or not isinstance(facing, dict):
        return False
    nearest = sorted(
        initial_monsters,
        key=lambda monster: _point_distance(origin, monster.get("position", {})),
    )[0]
    expected = _direction(origin, nearest.get("position", {}))
    actual = _direction({"x": 0.0, "y": 0.0}, facing)
    return _angle_between_degrees(expected, actual) <= 1.0


def _melee_arc_targets_passed(melee_events: list[dict[str, Any]], damage_events: list[dict[str, Any]]) -> bool:
    if not melee_events or not damage_events:
        return False
    event = melee_events[0]
    payload = event.get("payload", {})
    origin = payload.get("origin", event.get("position", {})) if isinstance(payload, dict) else event.get("position", {})
    facing = payload.get("facing_direction", event.get("direction", {})) if isinstance(payload, dict) else event.get("direction", {})
    arc_radius = float(payload.get("arc_radius", 0.0)) if isinstance(payload, dict) else 0.0
    arc_angle = float(payload.get("arc_angle", 0.0)) if isinstance(payload, dict) else 0.0
    if arc_radius <= 0 or arc_angle <= 0 or not isinstance(origin, dict) or not isinstance(facing, dict):
        return False
    for damage in damage_events:
        damage_payload = damage.get("payload", {})
        target = damage_payload.get("target_world_position", damage.get("position", {})) if isinstance(damage_payload, dict) else damage.get("position", {})
        if not isinstance(target, dict):
            return False
        if _point_distance(origin, target) > arc_radius + 0.001:
            return False
        if _angle_between_degrees(_direction(origin, target), _direction({"x": 0.0, "y": 0.0}, facing)) > arc_angle / 2 + 0.001:
            return False
    return True


def _damage_zone_faces_nearest_target(zone_events: list[dict[str, Any]], initial_monsters: list[dict[str, Any]]) -> bool:
    if not zone_events:
        return False
    event = zone_events[0]
    payload = event.get("payload", {})
    if isinstance(payload, dict) and payload.get("shape") == "circle":
        return True
    origin = payload.get("origin", event.get("position", {})) if isinstance(payload, dict) else event.get("position", {})
    facing = payload.get("facing_direction", event.get("direction", {})) if isinstance(payload, dict) else event.get("direction", {})
    if not initial_monsters or not isinstance(origin, dict) or not isinstance(facing, dict):
        return False
    nearest = sorted(initial_monsters, key=lambda monster: _point_distance(origin, monster.get("position", {})))[0]
    expected = _direction(origin, nearest.get("position", {}))
    actual = _direction({"x": 0.0, "y": 0.0}, facing)
    return _angle_between_degrees(expected, actual) <= 1.0


def _damage_zone_targets_passed(zone_events: list[dict[str, Any]], damage_events: list[dict[str, Any]]) -> bool:
    if not zone_events or not damage_events:
        return False
    event = zone_events[0]
    payload = event.get("payload", {})
    origin = payload.get("origin", event.get("position", {})) if isinstance(payload, dict) else event.get("position", {})
    if not isinstance(origin, dict):
        return False
    shape = str(payload.get("shape", "circle")) if isinstance(payload, dict) else "circle"
    if shape == "circle":
        radius = float(payload.get("radius", 0.0)) if isinstance(payload, dict) else 0.0
        return radius > 0 and all(
            _point_distance(origin, _damage_target_position(event)) <= radius + 0.001
            for event in damage_events
        )
    if shape == "rectangle":
        direction = payload.get("direction_world", event.get("direction", {})) if isinstance(payload, dict) else event.get("direction", {})
        length = float(payload.get("length", 0.0)) if isinstance(payload, dict) else 0.0
        width = float(payload.get("width", 0.0)) if isinstance(payload, dict) else 0.0
        if length <= 0 or width <= 0 or not isinstance(direction, dict):
            return False
        for damage in damage_events:
            target = _damage_target_position(damage)
            dx = float(target.get("x", 0.0)) - float(origin.get("x", 0.0))
            dy = float(target.get("y", 0.0)) - float(origin.get("y", 0.0))
            forward = dx * float(direction.get("x", 0.0)) + dy * float(direction.get("y", 0.0))
            lateral = abs(dx * -float(direction.get("y", 0.0)) + dy * float(direction.get("x", 0.0)))
            if forward < -0.001 or forward > length + 0.001 or lateral > width / 2.0 + 0.001:
                return False
        return True
    return False


def _damage_target_position(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload", {})
    target = payload.get("target_world_position", event.get("position", {})) if isinstance(payload, dict) else event.get("position", {})
    return target if isinstance(target, dict) else {}


def _point_distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    return hypot(float(left.get("x", 0.0)) - float(right.get("x", 0.0)), float(left.get("y", 0.0)) - float(right.get("y", 0.0)))


def _direction(origin: dict[str, Any], target: dict[str, Any]) -> dict[str, float]:
    dx = float(target.get("x", 0.0)) - float(origin.get("x", 0.0))
    dy = float(target.get("y", 0.0)) - float(origin.get("y", 0.0))
    length = hypot(dx, dy) or 1.0
    return {"x": dx / length, "y": dy / length}


def _angle_between_degrees(left: dict[str, float], right: dict[str, float]) -> float:
    dot = max(-1.0, min(1.0, left["x"] * right["x"] + left["y"] * right["y"]))
    return acos(dot) * 180.0 / 3.141592653589793


def _parameter_variant_checks(
    service: SkillEditorService,
    entry: dict[str, Any],
    request: SkillTestReportRequest,
    baseline_spawns: list[dict[str, Any]],
) -> dict[str, bool]:
    if request.skill_id == "active_puncture":
        package = entry.get("package_data")
        if not isinstance(package, dict):
            return {
                "projectile_count_changes_events": True,
                "spread_angle_changes_directions": True,
                "radius_changes_hit_targets": True,
                "length_changes_hit_targets": False,
                "width_changes_hit_targets": False,
            }
        base_result = _run_arena(service, request, package)
        length_package = deepcopy(package)
        length_params = length_package["behavior"]["params"]
        length_params["length"] = max(1.0, float(length_params.get("length", 1.0)) * 0.4)
        length_result = _run_arena(service, request, length_package)
        width_package = deepcopy(package)
        width_params = width_package["behavior"]["params"]
        width_params["width"] = max(1.0, float(width_params.get("width", 96.0)) * 0.4)
        width_result = _run_arena(service, request, width_package)
        return {
            "projectile_count_changes_events": True,
            "spread_angle_changes_directions": True,
            "radius_changes_hit_targets": True,
            "length_changes_hit_targets": _hit_target_ids(base_result) != _hit_target_ids(length_result),
            "width_changes_hit_targets": _hit_target_ids(base_result) != _hit_target_ids(width_result),
        }
    if request.skill_id == "active_frost_nova":
        package = entry.get("package_data")
        if not isinstance(package, dict):
            return {
                "projectile_count_changes_events": True,
                "spread_angle_changes_directions": True,
                "radius_changes_hit_targets": False,
                "length_changes_hit_targets": True,
                "width_changes_hit_targets": True,
            }
        radius_package = deepcopy(package)
        radius_params = radius_package["behavior"]["params"]
        radius_params["radius"] = max(1.0, float(radius_params.get("radius", 1.0)) * 0.25)
        base_result = _run_arena(service, request, package)
        radius_result = _run_arena(service, request, radius_package)
        return {
            "projectile_count_changes_events": True,
            "spread_angle_changes_directions": True,
            "radius_changes_hit_targets": len(base_result.get("hit_targets", [])) != len(radius_result.get("hit_targets", [])),
            "length_changes_hit_targets": True,
            "width_changes_hit_targets": True,
        }
    if request.skill_id != "active_ice_shards":
        return {"projectile_count_changes_events": True, "spread_angle_changes_directions": True}
    package = entry.get("package_data")
    if not isinstance(package, dict):
        return {"projectile_count_changes_events": False, "spread_angle_changes_directions": False}

    count_package = deepcopy(package)
    count_params = count_package["behavior"]["params"]
    count_params["projectile_count"] = int(count_params.get("projectile_count", 1)) + 1
    count_result = _run_arena(service, request, count_package)

    angle_package = deepcopy(package)
    angle_params = angle_package["behavior"]["params"]
    base_spread_angle = float(angle_params.get("spread_angle", 0.0))
    base_angle_step = float(angle_params.get("angle_step", 0.0))
    angle_params["spread_angle"] = base_spread_angle - 10.0 if base_spread_angle >= 180.0 else min(180.0, max(1.0, base_spread_angle + 10.0))
    angle_params["angle_step"] = base_angle_step - 5.0 if base_angle_step >= 90.0 else min(90.0, max(1.0, base_angle_step + 5.0))
    angle_result = _run_arena(service, request, angle_package)

    baseline_directions = _spawn_directions(baseline_spawns)
    changed_directions = _spawn_directions(
        [event for event in angle_result.get("event_timeline", []) if event.get("type") == "projectile_spawn"]
    )
    return {
        "projectile_count_changes_events": int(count_result.get("event_counts", {}).get("projectile_spawn", 0)) != len(baseline_spawns),
        "spread_angle_changes_directions": bool(baseline_directions and changed_directions and baseline_directions != changed_directions),
    }


def _spawn_directions(events: list[dict[str, Any]]) -> tuple[tuple[float, float], ...]:
    return tuple(
        (
            round(float(event.get("direction", {}).get("x", 0.0)), 4),
            round(float(event.get("direction", {}).get("y", 0.0)), 4),
        )
        for event in events
    )


def _hit_target_ids(arena_result: dict[str, Any]) -> tuple[str, ...]:
    return tuple(target["enemy_id"] for target in arena_result.get("hit_targets", []))


def _conclusion(checks: dict[str, bool]) -> tuple[str, tuple[str, ...]]:
    if checks.get("uses_damage_zone"):
        critical = (
            "has_damage_zone",
            "damage_zone_origin_passed",
            "damage_zone_faces_nearest_target",
            "has_damage",
            "damage_after_or_at_damage_zone_hit",
            "flight_no_damage_passed",
            "life_reduced_after_damage",
            "damage_type_expected",
            "hit_target_exists",
            "damage_zone_targets_passed",
            "radius_changes_hit_targets",
            "length_changes_hit_targets",
            "width_changes_hit_targets",
        )
    elif checks.get("uses_melee_arc"):
        critical = (
            "has_melee_arc",
            "melee_arc_origin_passed",
            "melee_arc_faces_nearest_target",
            "has_damage",
            "damage_after_or_at_melee_hit",
            "flight_no_damage_passed",
            "life_reduced_after_damage",
            "damage_type_expected",
            "hit_target_exists",
            "melee_arc_targets_passed",
            "arc_radius_changes_hit_targets",
            "arc_angle_changes_hit_targets",
        )
    elif checks.get("uses_area_nova"):
        critical = (
            "has_area_spawn",
            "area_center_passed",
            "has_damage",
            "damage_after_or_at_area_hit",
            "flight_no_damage_passed",
            "life_reduced_after_damage",
            "damage_type_expected",
            "hit_target_exists",
            "area_range_targets_passed",
            "radius_changes_hit_targets",
        )
    else:
        critical = (
            "has_projectile_spawn",
            "has_multiple_projectile_spawn",
            "fan_direction_passed",
            "has_projectile_hit",
            "has_damage",
            "damage_after_or_at_projectile_spawn",
            "flight_no_damage_passed",
            "life_reduced_after_damage",
            "damage_type_expected",
            "hit_target_exists",
            "projectile_count_changes_events",
            "spread_angle_changes_directions",
        )
    presentation = ("has_hit_vfx", "has_floating_text")
    failed_critical = [key for key in critical if not checks[key]]
    failed_presentation = [key for key in presentation if not checks[key]]
    failed_modifier = [] if checks["modifier_stack_changed_result"] else ["modifier_stack_changed_result"]
    reasons = tuple(_check_failure_text(key) for key in failed_critical + failed_presentation + failed_modifier)
    if failed_critical:
        return "不通过", reasons
    if failed_presentation or failed_modifier:
        return "部分通过", reasons
    return "通过", ()


def _check_failure_text(key: str) -> str:
    return {
        "has_projectile_spawn": "缺少投射物生成事件。",
        "has_multiple_projectile_spawn": "缺少多枚投射物生成事件。",
        "fan_direction_passed": "投射物方向没有形成扇形分布。",
        "has_projectile_hit": "缺少投射物命中事件。",
        "has_damage": "缺少伤害结算事件。",
        "damage_after_or_at_projectile_spawn": "伤害结算早于投射物生成。",
        "flight_no_damage_passed": "投射物飞行期间发生了扣血。",
        "life_reduced_after_damage": "伤害事件后目标生命没有减少。",
        "damage_type_expected": "伤害类型与技能期望不一致。",
        "hit_target_exists": "没有实际命中目标。",
        "projectile_count_changes_events": "修改 projectile_count 后投射物事件数量没有变化。",
        "spread_angle_changes_directions": "修改 spread_angle 后投射物方向没有变化。",
        "has_area_spawn": "缺少范围生成 area_spawn 事件。",
        "area_center_passed": "area_spawn 中心不是玩家或释放源位置。",
        "damage_after_or_at_area_hit": "damage 早于 hit_at_ms 结算。",
        "area_range_targets_passed": "范围命中目标与 radius 判断不一致。",
        "radius_changes_hit_targets": "修改 radius 后命中目标没有变化。",
        "has_melee_arc": "缺少近战扇形 melee_arc 事件。",
        "melee_arc_origin_passed": "melee_arc 起点不是玩家或释放源位置。",
        "melee_arc_faces_nearest_target": "melee_arc 未朝向最近敌人。",
        "damage_after_or_at_melee_hit": "damage 早于 melee_arc 的 hit_at_ms。",
        "melee_arc_targets_passed": "近战扇形内外或距离命中判断不一致。",
        "arc_radius_changes_hit_targets": "修改 arc_radius 后命中目标没有变化。",
        "arc_angle_changes_hit_targets": "修改 arc_angle 后命中目标没有变化。",
        "has_damage_zone": "缺少伤害结算区域 damage_zone 事件。",
        "damage_zone_origin_passed": "damage_zone 起点不是玩家或释放源位置。",
        "damage_zone_faces_nearest_target": "矩形 damage_zone 未朝向锁定或最近敌人。",
        "damage_after_or_at_damage_zone_hit": "damage 早于 damage_zone 的 hit_at_ms。",
        "damage_zone_targets_passed": "伤害区域内外或距离命中判断不一致。",
        "length_changes_hit_targets": "修改 length 后命中目标没有变化。",
        "width_changes_hit_targets": "修改 width 后命中目标没有变化。",
        "has_hit_vfx": "缺少命中特效事件。",
        "has_floating_text": "缺少伤害浮字事件。",
        "modifier_stack_changed_result": "测试 Modifier 栈开启后最终伤害或关键参数没有变化。",
    }[key]


def _suggestions(inconsistencies: tuple[str, ...]) -> tuple[str, ...]:
    if not inconsistencies:
        return ("暂无修复建议，当前测试结果与期望描述一致。",)
    suggestions = []
    for item in inconsistencies:
        if "投射物" in item or "伤害结算" in item:
            suggestions.append("检查 fan_projectile 行为模板和 SkillRuntime 事件生成顺序。")
        elif "生命" in item:
            suggestions.append("检查测试场 damage 事件消费与怪物生命结算。")
        elif "特效" in item or "浮字" in item:
            suggestions.append("检查 presentation key 与 SkillEvent 表现事件输出。")
        elif "Modifier" in item:
            suggestions.append("检查测试 Modifier 栈是否正确进入 FinalSkillInstance 计算。")
        else:
            suggestions.append("检查 Skill Package、FinalSkillInstance 与 SkillEvent 管线。")
    return tuple(dict.fromkeys(suggestions))


def _markdown_report(
    *,
    entry: dict[str, Any],
    arena_result: dict[str, Any],
    modifier_stack: dict[str, Any],
    expected_description: str,
    checks: dict[str, bool],
    conclusion: str,
    inconsistencies: tuple[str, ...],
    suggestions: tuple[str, ...],
) -> str:
    lines = [
        "# 技能自测报告",
        "",
        "## 测试概览",
        f"- 测试技能 ID：`{arena_result['skill_id']}`",
        f"- 技能中文名：{arena_result['skill_name_text']}",
        f"- 测试场景：{arena_result['scene_name_text']}",
        f"- 描述一致性结论：{conclusion}",
        "",
        "## 技能信息",
        f"- skill.yaml 路径：`{entry['skill_yaml_path']}`",
        f"- behavior_template：`{entry['behavior_template']}`",
        "",
        "## 测试场景",
        f"- 场景 ID：`{arena_result['scene_id']}`",
        f"- 怪物生命变化：{_monster_life_text(arena_result)}",
        "",
        "## 测试 Modifier Stack",
        *_modifier_lines(modifier_stack),
        "",
        "## 期望玩家侧描述",
        expected_description,
        "",
        "## 实际事件序列摘要",
        *_event_lines(arena_result["event_timeline"]),
        "",
        "## 实际伤害与命中结果",
        *_damage_lines(arena_result),
        "",
        "## 表现完整性检查",
        f"- damage_zone：{_pass_text(checks.get('has_damage_zone', True))}",
        f"- 伤害区域起点：{_pass_text(checks.get('damage_zone_origin_passed', True))}",
        f"- 伤害区域朝向：{_pass_text(checks.get('damage_zone_faces_nearest_target', True))}",
        f"- area_spawn：{_pass_text(checks.get('has_area_spawn', True))}",
        f"- 玩家中心：{_pass_text(checks.get('area_center_passed', True))}",
        f"- melee_arc：{_pass_text(checks.get('has_melee_arc', True))}",
        f"- 近战扇形起点：{_pass_text(checks.get('melee_arc_origin_passed', True))}",
        f"- 朝向最近目标：{_pass_text(checks.get('melee_arc_faces_nearest_target', True))}",
        f"- projectile_spawn：{_pass_text(checks['has_projectile_spawn'])}",
        f"- 多枚 projectile_spawn：{_pass_text(checks['has_multiple_projectile_spawn'])}",
        f"- 扇形方向：{_pass_text(checks['fan_direction_passed'])}",
        f"- projectile_hit：{_pass_text(checks['has_projectile_hit'])}",
        f"- damage：{_pass_text(checks['has_damage'])}",
        f"- hit_vfx：{_pass_text(checks['has_hit_vfx'])}",
        f"- floating_text：{_pass_text(checks['has_floating_text'])}",
        "",
        "## 伤害时机一致性检查",
        f"- damage 不早于 projectile_spawn：{_pass_text(checks['damage_after_or_at_projectile_spawn'])}",
        f"- damage 不早于 hit_at_ms：{_pass_text(checks.get('damage_after_or_at_area_hit', True))}",
        f"- damage 不早于 melee_arc hit_at_ms：{_pass_text(checks.get('damage_after_or_at_melee_hit', True))}",
        f"- damage 不早于 damage_zone hit_at_ms：{_pass_text(checks.get('damage_after_or_at_damage_zone_hit', True))}",
        f"- 投射物飞行期间未扣血：{_pass_text(checks['flight_no_damage_passed'])}",
        f"- damage 后目标生命减少：{_pass_text(checks['life_reduced_after_damage'])}",
        f"- damage_type 为 {checks['expected_damage_type']}：{_pass_text(checks['damage_type_expected'])}",
        f"- 存在命中目标：{_pass_text(checks['hit_target_exists'])}",
        f"- projectile_count 修改后事件数量变化：{_pass_text(checks['projectile_count_changes_events'])}",
        f"- spread_angle 修改后方向变化：{_pass_text(checks['spread_angle_changes_directions'])}",
        f"- radius 修改后命中目标变化：{_pass_text(checks.get('radius_changes_hit_targets', True))}",
        f"- length 修改后命中目标变化：{_pass_text(checks.get('length_changes_hit_targets', True))}",
        f"- width 修改后命中目标变化：{_pass_text(checks.get('width_changes_hit_targets', True))}",
        f"- 范围内外命中判断：{_pass_text(checks.get('area_range_targets_passed', True))}",
        f"- 伤害区域命中判断：{_pass_text(checks.get('damage_zone_targets_passed', True))}",
        f"- arc_radius 修改后命中目标变化：{_pass_text(checks.get('arc_radius_changes_hit_targets', True))}",
        f"- arc_angle 修改后命中目标变化：{_pass_text(checks.get('arc_angle_changes_hit_targets', True))}",
        f"- 近战扇形命中判断：{_pass_text(checks.get('melee_arc_targets_passed', True))}",
        f"- 测试 Modifier Stack 变化检查：{_pass_text(checks['modifier_stack_changed_result'])}",
        "",
        "## 描述一致性结论",
        f"{conclusion}。{_conclusion_reason(conclusion, inconsistencies)}",
        "",
        "## 不一致项列表",
        *_list_or_empty(inconsistencies, "未发现不一致项。"),
        "",
        "## 建议修复项",
        *_list_or_empty(suggestions, "暂无修复建议。"),
        "",
    ]
    return "\n".join(lines)


def _modifier_lines(modifier_stack: dict[str, Any]) -> list[str]:
    lines = [
        f"- 是否启用：{'已启用' if modifier_stack['enabled'] else '未启用'}",
        f"- 模拟关系：{modifier_stack['relation_text']}",
        f"- source_power：{modifier_stack['source_power']}",
        f"- target_power：{modifier_stack['target_power']}",
        f"- conduit_power：{modifier_stack['conduit_power']}",
        f"- 原始最终伤害：{modifier_stack['baseline']['final_damage']}",
        f"- 测试后最终伤害：{modifier_stack['tested']['final_damage']}",
        f"- 原始投射物数量：{modifier_stack['baseline']['projectile_count']}",
        f"- 测试后投射物数量：{modifier_stack['tested']['projectile_count']}",
    ]
    selected = modifier_stack["selected"]
    if selected:
        lines.append("- 已选择效果：" + "、".join(f"{item['name_text']}（`{item['id']}`）" for item in selected))
    else:
        lines.append("- 已选择效果：无")
    return lines


def _event_lines(events: list[dict[str, Any]]) -> list[str]:
    if not events:
        return ["- 无事件。"]
    return [
        (
            f"- {event['type_text']}（`{event['type']}`）："
            f"事件时间 {event['timestamp_ms']} 毫秒，延迟 {event['delay_ms']} 毫秒，"
            f"持续 {event['duration_ms']} 毫秒，目标 `{event['target_entity'] or '无'}`，"
            f"数值 {event['amount'] if event['amount'] is not None else '无'}，"
            f"伤害类型 `{event['damage_type'] or '无'}`，特效 `{event['vfx_key'] or '无'}`，"
            f"原因 `{event['reason_key'] or '无'}`，附加数据 `{event['payload_text']}`"
        )
        for event in events
    ]


def _damage_lines(arena_result: dict[str, Any]) -> list[str]:
    lines = []
    if arena_result["hit_targets"]:
        lines.append("- 实际命中目标：" + "、".join(target["name_text"] for target in arena_result["hit_targets"]))
    else:
        lines.append("- 实际命中目标：无")
    if arena_result["damage_results"]:
        for damage in arena_result["damage_results"]:
            lines.append(f"- {damage['name_text']}：{damage['amount']} 点伤害，延迟 {damage['delay_ms']} 毫秒。")
    else:
        lines.append("- 实际伤害结果：无")
    return lines


def _monster_life_text(arena_result: dict[str, Any]) -> str:
    initial = {monster["enemy_id"]: monster for monster in arena_result["initial_monsters"]}
    parts = []
    for monster in arena_result["monsters"]:
        before = initial.get(monster["enemy_id"], monster)["current_life"]
        after = monster["current_life"]
        parts.append(f"{monster['name_text']} {before} -> {after}")
    return "；".join(parts)


def _pass_text(value: bool) -> str:
    return "通过" if value else "未通过"


def _conclusion_reason(conclusion: str, inconsistencies: tuple[str, ...]) -> str:
    if conclusion == "通过":
        return "核心事件、伤害时机、生命变化、扇形方向和表现事件均符合期望描述。"
    return "；".join(inconsistencies)


def _list_or_empty(items: tuple[str, ...], empty_text: str) -> list[str]:
    if not items:
        return [f"- {empty_text}"]
    return [f"- {item}" for item in items]
