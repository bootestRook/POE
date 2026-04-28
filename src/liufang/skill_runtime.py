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
    ) -> tuple[SkillEvent, ...]:
        if not skill.uses_skill_event_pipeline:
            raise SkillRuntimeError("skill does not use the SkillEvent pipeline")
        if skill.behavior_template != "projectile":
            raise SkillRuntimeError(f"unsupported behavior template: {skill.behavior_template}")
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
