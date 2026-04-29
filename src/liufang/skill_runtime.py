from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, hypot, pi, sin
from typing import Any

from .skill_effects import FinalSkillInstance


SKILL_EVENT_TYPES = frozenset(
    {
        "cast_start",
        "projectile_spawn",
        "projectile_hit",
        "chain_segment",
        "area_spawn",
        "melee_arc",
        "orbit_spawn",
        "orbit_tick",
        "delayed_area_prime",
        "delayed_area_explode",
        "damage",
        "hit_vfx",
        "floating_text",
        "cooldown_update",
    }
)


@dataclass(frozen=True)
class SkillEvent:
    event_id: str
    type: str
    timestamp_ms: int
    source_entity: str
    target_entity: str
    position: dict[str, float]
    direction: dict[str, float]
    delay_ms: int
    duration_ms: int
    amount: float | None
    damage_type: str
    skill_instance_id: str
    vfx_key: str
    sfx_key: str
    reason_key: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "type": self.type,
            "timestamp_ms": self.timestamp_ms,
            "source_entity": self.source_entity,
            "target_entity": self.target_entity,
            "position": dict(self.position),
            "direction": dict(self.direction),
            "delay_ms": self.delay_ms,
            "duration_ms": self.duration_ms,
            "amount": self.amount,
            "damage_type": self.damage_type,
            "skill_instance_id": self.skill_instance_id,
            "vfx_key": self.vfx_key,
            "sfx_key": self.sfx_key,
            "reason_key": self.reason_key,
            "payload": dict(self.payload),
        }


class SkillRuntimeError(ValueError):
    pass


@dataclass(frozen=True)
class _RuntimeTarget:
    entity_id: str
    position: dict[str, float]


class SkillRuntime:
    def execute(
        self,
        skill: FinalSkillInstance,
        *,
        source_entity: str,
        source_position: object,
        target_entity: str,
        target_position: object,
        timestamp_ms: int,
        target_entities: object | None = None,
    ) -> tuple[SkillEvent, ...]:
        if not skill.uses_skill_event_pipeline:
            raise SkillRuntimeError("skill does not use the SkillEvent pipeline")
        if skill.behavior_template != "projectile":
            raise SkillRuntimeError(f"unsupported behavior template: {skill.behavior_template}")
        if target_entities is not None:
            targets = tuple(_runtime_targets(target_entities))
            if targets:
                return self._projectile_multi_target_events(
                    skill,
                    source_entity=source_entity,
                    source_position=_position_dict(source_position),
                    targets=targets,
                    timestamp_ms=timestamp_ms,
                )
        return self._projectile_events(
            skill,
            source_entity=source_entity,
            source_position=_position_dict(source_position),
            target_entity=target_entity,
            target_position=_position_dict(target_position),
            timestamp_ms=timestamp_ms,
        )

    def _projectile_events(
        self,
        skill: FinalSkillInstance,
        *,
        source_entity: str,
        source_position: dict[str, float],
        target_entity: str,
        target_position: dict[str, float],
        timestamp_ms: int,
    ) -> tuple[SkillEvent, ...]:
        runtime_params = skill.runtime_params or {}
        presentation = skill.presentation_keys or {}
        projectile_speed = max(1.0, float(runtime_params.get("projectile_speed", 720.0)))
        min_duration_ms = int(runtime_params.get("min_duration_ms", 0))
        max_duration_ms = int(runtime_params.get("max_duration_ms", 1000))
        projectile_count = max(1, int(runtime_params.get("projectile_count", skill.projectile_count)))
        burst_interval_ms = max(0, int(runtime_params.get("burst_interval_ms", 0)))
        spread_angle_deg = max(0.0, float(runtime_params.get("spread_angle_deg", 0.0)))
        distance = hypot(target_position["x"] - source_position["x"], target_position["y"] - source_position["y"])
        duration_ms = int(round(distance / projectile_speed * 1000))
        duration_ms = max(min_duration_ms, min(duration_ms, max_duration_ms))
        direction = _direction(source_position, target_position)
        vfx_key = presentation.get("vfx", skill.visual_effect)
        sfx_key = presentation.get("sfx", "")
        floating_key = presentation.get("floating_text", "skill_event.fire_bolt.floating_text")
        reason_key = "skill_event.fire_bolt.damage_reason"
        floating_text = _damage_text(skill.final_damage, skill.damage_type)

        directions = _spread_directions(direction, projectile_count, spread_angle_deg)
        events = [
            SkillEvent(
                event_id=_event_id(skill, timestamp_ms, index + 1, "projectile_spawn"),
                type="projectile_spawn",
                timestamp_ms=timestamp_ms + index * burst_interval_ms,
                source_entity=source_entity,
                target_entity=target_entity,
                position=source_position,
                direction=projectile_direction,
                delay_ms=index * burst_interval_ms,
                duration_ms=duration_ms,
                amount=None,
                damage_type=skill.damage_type,
                skill_instance_id=skill.active_gem_instance_id,
                vfx_key=vfx_key,
                sfx_key=sfx_key,
                reason_key="",
                payload={
                    "end_position": {
                        "x": source_position["x"] + projectile_direction["x"] * distance,
                        "y": source_position["y"] + projectile_direction["y"] * distance,
                    },
                    "projectile_index": index + 1,
                    "projectile_count": projectile_count,
                    "burst_interval_ms": burst_interval_ms,
                    "spread_angle_deg": spread_angle_deg,
                    "projectile_radius": runtime_params.get("projectile_radius", 0),
                    "impact_radius": runtime_params.get("impact_radius", 0),
                },
            )
            for index, projectile_direction in enumerate(directions)
        ]
        for index, projectile_direction in enumerate(directions):
            projectile_delay_ms = index * burst_interval_ms
            impact_delay_ms = projectile_delay_ms + duration_ms
            projectile_payload = {
                "projectile_index": index + 1,
                "projectile_count": projectile_count,
            }
            events.extend(
                [
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, projectile_count + index * 3 + 1, "damage"),
                        type="damage",
                        timestamp_ms=timestamp_ms + impact_delay_ms,
                        source_entity=source_entity,
                        target_entity=target_entity,
                        position=target_position,
                        direction=projectile_direction,
                        delay_ms=impact_delay_ms,
                        duration_ms=0,
                        amount=skill.final_damage,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=vfx_key,
                        sfx_key=sfx_key,
                        reason_key=reason_key,
                        payload=projectile_payload,
                    ),
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, projectile_count + index * 3 + 2, "hit_vfx"),
                        type="hit_vfx",
                        timestamp_ms=timestamp_ms + impact_delay_ms,
                        source_entity=source_entity,
                        target_entity=target_entity,
                        position=target_position,
                        direction=projectile_direction,
                        delay_ms=impact_delay_ms,
                        duration_ms=420,
                        amount=None,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=vfx_key,
                        sfx_key=sfx_key,
                        reason_key=reason_key,
                        payload=projectile_payload,
                    ),
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, projectile_count + index * 3 + 3, "floating_text"),
                        type="floating_text",
                        timestamp_ms=timestamp_ms + impact_delay_ms,
                        source_entity=source_entity,
                        target_entity=target_entity,
                        position=target_position,
                        direction=projectile_direction,
                        delay_ms=impact_delay_ms,
                        duration_ms=800,
                        amount=skill.final_damage,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=vfx_key,
                        sfx_key=sfx_key,
                        reason_key=floating_key,
                        payload={**projectile_payload, "text": floating_text},
                    ),
                ]
            )
        return tuple(events)

    def _projectile_multi_target_events(
        self,
        skill: FinalSkillInstance,
        *,
        source_entity: str,
        source_position: dict[str, float],
        targets: tuple[_RuntimeTarget, ...],
        timestamp_ms: int,
    ) -> tuple[SkillEvent, ...]:
        runtime_params = skill.runtime_params or {}
        presentation = skill.presentation_keys or {}
        primary_target = targets[0]
        projectile_speed = max(1.0, float(runtime_params.get("projectile_speed", 720.0)))
        min_duration_ms = int(runtime_params.get("min_duration_ms", 0))
        max_duration_ms = int(runtime_params.get("max_duration_ms", 1000))
        projectile_count = max(1, int(runtime_params.get("projectile_count", skill.projectile_count)))
        burst_interval_ms = max(0, int(runtime_params.get("burst_interval_ms", 0)))
        spread_angle_deg = max(0.0, float(runtime_params.get("spread_angle_deg", 0.0)))
        max_distance = max(1.0, float(runtime_params.get("max_distance", 520.0)))
        collision_radius = max(
            1.0,
            float(runtime_params.get("collision_radius", 0.0)),
            float(runtime_params.get("projectile_radius", 0.0)),
            float(runtime_params.get("projectile_width", 0.0)) / 2.0,
            float(runtime_params.get("projectile_height", 0.0)) / 2.0,
        )
        pierce_count = max(0, int(runtime_params.get("pierce_count", 0)))
        hit_policy = str(runtime_params.get("hit_policy", "first_hit"))
        max_hits_per_projectile = pierce_count + 1 if hit_policy == "pierce" or pierce_count > 0 else 1
        primary_distance = min(
            max_distance,
            hypot(primary_target.position["x"] - source_position["x"], primary_target.position["y"] - source_position["y"]),
        )
        duration_ms = _duration_ms(primary_distance, projectile_speed, min_duration_ms, max_duration_ms)
        direction = _direction(source_position, primary_target.position)
        directions = _spread_directions(direction, projectile_count, spread_angle_deg)
        vfx_key = presentation.get("vfx", skill.visual_effect)
        sfx_key = presentation.get("sfx", "")
        floating_key = presentation.get("floating_text", "skill_event.fire_bolt.floating_text")
        reason_key = "skill_event.fire_bolt.damage_reason"
        floating_text = _damage_text(skill.final_damage, skill.damage_type)
        events: list[SkillEvent] = []
        next_index = 1

        for projectile_index, projectile_direction in enumerate(directions, start=1):
            projectile_delay_ms = (projectile_index - 1) * burst_interval_ms
            events.append(
                SkillEvent(
                    event_id=_event_id(skill, timestamp_ms, next_index, "projectile_spawn"),
                    type="projectile_spawn",
                    timestamp_ms=timestamp_ms + projectile_delay_ms,
                    source_entity=source_entity,
                    target_entity=primary_target.entity_id,
                    position=source_position,
                    direction=projectile_direction,
                    delay_ms=projectile_delay_ms,
                    duration_ms=duration_ms,
                    amount=None,
                    damage_type=skill.damage_type,
                    skill_instance_id=skill.active_gem_instance_id,
                    vfx_key=vfx_key,
                    sfx_key=sfx_key,
                    reason_key="",
                    payload={
                        "end_position": {
                            "x": source_position["x"] + projectile_direction["x"] * max_distance,
                            "y": source_position["y"] + projectile_direction["y"] * max_distance,
                        },
                        "projectile_index": projectile_index,
                        "projectile_count": projectile_count,
                        "burst_interval_ms": burst_interval_ms,
                        "spread_angle_deg": spread_angle_deg,
                        "projectile_radius": runtime_params.get("projectile_radius", 0),
                        "impact_radius": runtime_params.get("impact_radius", 0),
                    },
                )
            )
            next_index += 1

        for projectile_index, projectile_direction in enumerate(directions, start=1):
            projectile_delay_ms = (projectile_index - 1) * burst_interval_ms
            for target, forward in _projectile_hit_targets(
                source_position,
                projectile_direction,
                targets,
                max_distance=max_distance,
                collision_radius=collision_radius,
                max_hits=max_hits_per_projectile,
            ):
                impact_duration_ms = _duration_ms(forward, projectile_speed, min_duration_ms, max_duration_ms)
                impact_delay_ms = projectile_delay_ms + impact_duration_ms
                projectile_payload = {
                    "projectile_index": projectile_index,
                    "projectile_count": projectile_count,
                    "hit_policy": hit_policy,
                    "pierce_count": pierce_count,
                }
                events.extend(
                    [
                        SkillEvent(
                            event_id=_event_id(skill, timestamp_ms, next_index, "damage"),
                            type="damage",
                            timestamp_ms=timestamp_ms + impact_delay_ms,
                            source_entity=source_entity,
                            target_entity=target.entity_id,
                            position=target.position,
                            direction=projectile_direction,
                            delay_ms=impact_delay_ms,
                            duration_ms=0,
                            amount=skill.final_damage,
                            damage_type=skill.damage_type,
                            skill_instance_id=skill.active_gem_instance_id,
                            vfx_key=vfx_key,
                            sfx_key=sfx_key,
                            reason_key=reason_key,
                            payload=projectile_payload,
                        ),
                        SkillEvent(
                            event_id=_event_id(skill, timestamp_ms, next_index + 1, "hit_vfx"),
                            type="hit_vfx",
                            timestamp_ms=timestamp_ms + impact_delay_ms,
                            source_entity=source_entity,
                            target_entity=target.entity_id,
                            position=target.position,
                            direction=projectile_direction,
                            delay_ms=impact_delay_ms,
                            duration_ms=420,
                            amount=None,
                            damage_type=skill.damage_type,
                            skill_instance_id=skill.active_gem_instance_id,
                            vfx_key=vfx_key,
                            sfx_key=sfx_key,
                            reason_key=reason_key,
                            payload=projectile_payload,
                        ),
                        SkillEvent(
                            event_id=_event_id(skill, timestamp_ms, next_index + 2, "floating_text"),
                            type="floating_text",
                            timestamp_ms=timestamp_ms + impact_delay_ms,
                            source_entity=source_entity,
                            target_entity=target.entity_id,
                            position=target.position,
                            direction=projectile_direction,
                            delay_ms=impact_delay_ms,
                            duration_ms=800,
                            amount=skill.final_damage,
                            damage_type=skill.damage_type,
                            skill_instance_id=skill.active_gem_instance_id,
                            vfx_key=vfx_key,
                            sfx_key=sfx_key,
                            reason_key=floating_key,
                            payload={**projectile_payload, "text": floating_text},
                        ),
                    ]
                )
                next_index += 3
        return tuple(events)


def _event_id(skill: FinalSkillInstance, timestamp_ms: int, index: int, event_type: str) -> str:
    return f"{skill.active_gem_instance_id}.{timestamp_ms}.{index}.{event_type}"


def _position_dict(position: object) -> dict[str, float]:
    return {
        "x": float(getattr(position, "x")),
        "y": float(getattr(position, "y")),
    }


def _direction(source: dict[str, float], target: dict[str, float]) -> dict[str, float]:
    dx = target["x"] - source["x"]
    dy = target["y"] - source["y"]
    length = hypot(dx, dy)
    if length <= 0:
        return {"x": 1.0, "y": 0.0}
    return {"x": dx / length, "y": dy / length}


def _duration_ms(distance: float, projectile_speed: float, min_duration_ms: int, max_duration_ms: int) -> int:
    duration_ms = int(round(max(0.0, distance) / max(1.0, projectile_speed) * 1000))
    return max(min_duration_ms, min(duration_ms, max_duration_ms))


def _runtime_targets(target_entities: object) -> tuple[_RuntimeTarget, ...]:
    if not isinstance(target_entities, (list, tuple)):
        raise SkillRuntimeError("target_entities must be a list")
    return tuple(_runtime_target(target) for target in target_entities)


def _runtime_target(target: object) -> _RuntimeTarget:
    if isinstance(target, dict):
        entity_id = str(target.get("entity_id") or target.get("enemy_id") or target.get("target_entity") or "")
        position = target.get("position")
    else:
        entity_id = str(getattr(target, "entity_id", "") or getattr(target, "enemy_id", "") or getattr(target, "monster_id", ""))
        position = getattr(target, "position", None)
    if not entity_id:
        raise SkillRuntimeError("target entity id is required")
    return _RuntimeTarget(entity_id=entity_id, position=_position_dict_any(position))


def _position_dict_any(position: object) -> dict[str, float]:
    if isinstance(position, dict):
        return {"x": float(position["x"]), "y": float(position["y"])}
    return _position_dict(position)


def _projectile_hit_targets(
    source: dict[str, float],
    direction: dict[str, float],
    targets: tuple[_RuntimeTarget, ...],
    *,
    max_distance: float,
    collision_radius: float,
    max_hits: int,
) -> tuple[tuple[_RuntimeTarget, float], ...]:
    candidates = []
    for target in targets:
        dx = target.position["x"] - source["x"]
        dy = target.position["y"] - source["y"]
        forward = dx * direction["x"] + dy * direction["y"]
        perpendicular = abs(dx * direction["y"] - dy * direction["x"])
        if forward < 0 or forward > max_distance:
            continue
        candidates.append((target, forward, perpendicular))
    line_targets = sorted(
        (candidate for candidate in candidates if candidate[2] <= collision_radius),
        key=lambda candidate: candidate[1],
    )
    selected = list(line_targets[:max(1, max_hits)])
    if len(selected) < max_hits and max_hits > 1:
        selected_ids = {target.entity_id for target, _, _ in selected}
        assist_targets = sorted(
            (
                candidate
                for candidate in candidates
                if candidate[0].entity_id not in selected_ids and candidate[2] <= collision_radius * 3
            ),
            key=lambda candidate: (candidate[2], candidate[1]),
        )
        selected.extend(assist_targets[: max_hits - len(selected)])
    return tuple((target, forward) for target, forward, _ in selected)


def _spread_directions(direction: dict[str, float], projectile_count: int, spread_angle_deg: float) -> tuple[dict[str, float], ...]:
    count = max(1, projectile_count)
    if count == 1 or spread_angle_deg <= 0:
        return tuple(dict(direction) for _ in range(count))
    center = (count - 1) / 2
    return tuple(
        _rotate_direction(direction, ((index - center) / max(1, count - 1)) * spread_angle_deg)
        for index in range(count)
    )


def _rotate_direction(direction: dict[str, float], angle_deg: float) -> dict[str, float]:
    radians = angle_deg * pi / 180
    cosine = cos(radians)
    sine = sin(radians)
    return {
        "x": direction["x"] * cosine - direction["y"] * sine,
        "y": direction["x"] * sine + direction["y"] * cosine,
    }


def _damage_text(amount: float, damage_type: str) -> str:
    damage_type_text = {
        "fire": "火焰",
        "cold": "冰霜",
        "lightning": "闪电",
        "physical": "物理",
    }.get(damage_type, "技能")
    return f"{round(amount)}点{damage_type_text}伤害"
