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
        if skill.behavior_template not in {"projectile", "fan_projectile", "player_nova"}:
            raise SkillRuntimeError(f"unsupported behavior template: {skill.behavior_template}")
        if skill.behavior_template == "player_nova":
            targets = tuple(_runtime_targets(target_entities)) if target_entities is not None else (
                _RuntimeTarget(target_entity, _position_dict(target_position)),
            )
            return self._player_nova_events(
                skill,
                source_entity=source_entity,
                source_position=_position_dict(source_position),
                targets=targets,
                timestamp_ms=timestamp_ms,
            )
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

    def _player_nova_events(
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
        radius = max(1.0, float(runtime_params.get("radius", 360.0)))
        expand_duration_ms = max(0, int(runtime_params.get("expand_duration_ms", 0)))
        hit_at_ms = max(0, int(runtime_params.get("hit_at_ms", skill.hit.get("hit_delay_ms", 0) if skill.hit else 0)))
        hit_at_ms = min(hit_at_ms, expand_duration_ms) if expand_duration_ms > 0 else hit_at_ms
        max_targets = max(1, int(runtime_params.get("max_targets", len(targets) or 1)))
        ring_width = max(1.0, float(runtime_params.get("ring_width", 48.0)))
        center_policy = str(runtime_params.get("center_policy", "player_center"))
        damage_falloff = str(runtime_params.get("damage_falloff_by_distance", "none"))
        status_chance_scale = max(0.0, float(runtime_params.get("status_chance_scale", 1.0)))
        center = dict(source_position)
        vfx_key = presentation.get("vfx", skill.visual_effect)
        hit_vfx_key = presentation.get("hit_vfx_key", vfx_key)
        sfx_key = presentation.get("sfx", "")
        floating_key = presentation.get("floating_text", "skill_event.fire_bolt.floating_text")
        reason_key = _damage_reason_key(skill)
        damage_amount = skill.final_damage
        area_id = f"{skill.active_gem_instance_id}.{timestamp_ms}.area.1"
        sorted_targets = sorted(
            (
                (target, hypot(target.position["x"] - center["x"], target.position["y"] - center["y"]))
                for target in targets
            ),
            key=lambda item: item[1],
        )
        hit_targets = tuple((target, distance) for target, distance in sorted_targets if distance <= radius)[:max_targets]
        primary_target = hit_targets[0][0] if hit_targets else (targets[0] if targets else _RuntimeTarget("", center))
        primary_direction = _direction(center, primary_target.position)
        events: list[SkillEvent] = [
            SkillEvent(
                event_id=_event_id(skill, timestamp_ms, 0, "cast_start"),
                type="cast_start",
                timestamp_ms=timestamp_ms,
                source_entity=source_entity,
                target_entity=primary_target.entity_id,
                position=center,
                direction=primary_direction,
                delay_ms=0,
                duration_ms=0,
                amount=None,
                damage_type=skill.damage_type,
                skill_instance_id=skill.active_gem_instance_id,
                vfx_key=presentation.get("cast_vfx_key", vfx_key),
                sfx_key=sfx_key,
                reason_key="",
                payload={"skill_id": skill.skill_package_id or skill.skill_template_id, "center_policy": center_policy},
            ),
            SkillEvent(
                event_id=_event_id(skill, timestamp_ms, 1, "area_spawn"),
                type="area_spawn",
                timestamp_ms=timestamp_ms,
                source_entity=source_entity,
                target_entity=primary_target.entity_id,
                position=center,
                direction={"x": 0.0, "y": 0.0},
                delay_ms=0,
                duration_ms=expand_duration_ms,
                amount=None,
                damage_type=skill.damage_type,
                skill_instance_id=skill.active_gem_instance_id,
                vfx_key=vfx_key,
                sfx_key=sfx_key,
                reason_key="",
                payload={
                    "area_id": area_id,
                    "skill_id": skill.skill_package_id or skill.skill_template_id,
                    "center": dict(center),
                    "center_world_position": dict(center),
                    "radius": radius,
                    "ring_width": ring_width,
                    "duration_ms": expand_duration_ms,
                    "expand_duration_ms": expand_duration_ms,
                    "hit_at_ms": hit_at_ms,
                    "damage_type": skill.damage_type,
                    "vfx_key": vfx_key,
                    "center_policy": center_policy,
                    "damage_falloff_by_distance": damage_falloff,
                    "status_chance_scale": status_chance_scale,
                    "max_targets": max_targets,
                    "hit_target_count": len(hit_targets),
                },
            ),
        ]
        next_index = 2
        floating_text = _damage_text(damage_amount, skill.damage_type)
        for target, target_distance in hit_targets:
            target_direction = _direction(center, target.position)
            area_payload = {
                "area_id": area_id,
                "skill_id": skill.skill_package_id or skill.skill_template_id,
                "center": dict(center),
                "center_world_position": dict(center),
                "radius": radius,
                "ring_width": ring_width,
                "hit_at_ms": hit_at_ms,
                "target_distance": target_distance,
                "target_world_position": dict(target.position),
                "damage_falloff_by_distance": damage_falloff,
                "status_chance_scale": status_chance_scale,
                "skill_name": skill.skill_package_id or skill.skill_template_id,
            }
            for event_type, amount, duration, vfx, reason, position in (
                ("damage", damage_amount, 0, hit_vfx_key, reason_key, target.position),
                ("hit_vfx", None, 420, hit_vfx_key, reason_key, target.position),
                ("floating_text", damage_amount, 800, hit_vfx_key, floating_key, {"x": target.position["x"], "y": target.position["y"] - 28.0}),
            ):
                payload = {**area_payload}
                if event_type == "floating_text":
                    payload["text"] = floating_text
                events.append(
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, next_index, event_type),
                        type=event_type,
                        timestamp_ms=timestamp_ms + hit_at_ms,
                        source_entity=source_entity,
                        target_entity=target.entity_id,
                        position=dict(position),
                        direction=target_direction,
                        delay_ms=hit_at_ms,
                        duration_ms=duration,
                        amount=amount,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=vfx,
                        sfx_key=sfx_key,
                        reason_key=reason,
                        payload=payload,
                    )
                )
                next_index += 1
        return _sorted_events(events)

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
        max_duration_ms = _optional_int(runtime_params.get("max_duration_ms"))
        projectile_count = max(1, int(runtime_params.get("projectile_count", skill.projectile_count)))
        burst_interval_ms = max(0, int(runtime_params.get("burst_interval_ms", 0)))
        spread_angle_deg = _spread_angle_deg(runtime_params, skill.behavior_template)
        angle_step_deg = _angle_step_deg(runtime_params, skill.behavior_template)
        damage_amount = skill.final_damage * _per_projectile_damage_scale(runtime_params, skill.behavior_template)
        max_distance = max(1.0, float(runtime_params.get("max_distance", 520.0)))
        pierce_count = max(0, int(runtime_params.get("pierce_count", 0)))
        hit_policy = str(runtime_params.get("hit_policy", "first_hit"))
        visual_distance = max_distance if hit_policy == "pierce" or pierce_count > 0 else 0.0
        spawn_position = _spawn_position(source_position, runtime_params)
        distance = hypot(target_position["x"] - spawn_position["x"], target_position["y"] - spawn_position["y"])
        visual_distance = visual_distance or distance
        duration_ms = _duration_ms(visual_distance, projectile_speed, min_duration_ms, max_duration_ms)
        impact_duration_ms = _duration_ms(distance, projectile_speed, min_duration_ms, max_duration_ms)
        direction = _direction(spawn_position, target_position)
        vfx_key = presentation.get("projectile_vfx_key", presentation.get("vfx", skill.visual_effect))
        hit_vfx_key = presentation.get("hit_vfx_key", presentation.get("vfx", vfx_key))
        sfx_key = presentation.get("sfx", "")
        floating_key = presentation.get("floating_text", "skill_event.fire_bolt.floating_text")
        reason_key = _damage_reason_key(skill)
        floating_text = _damage_text(damage_amount, skill.damage_type)

        spread_angles = _spread_angles(projectile_count, spread_angle_deg, angle_step_deg)
        directions = tuple(
            _rotate_direction(direction, spread_angle) if spread_angle else dict(direction)
            for spread_angle in spread_angles
        )
        events = [
            SkillEvent(
                event_id=_event_id(skill, timestamp_ms, 0, "cast_start"),
                type="cast_start",
                timestamp_ms=timestamp_ms,
                source_entity=source_entity,
                target_entity=target_entity,
                position=source_position,
                direction=direction,
                delay_ms=0,
                duration_ms=0,
                amount=None,
                damage_type=skill.damage_type,
                skill_instance_id=skill.active_gem_instance_id,
                vfx_key=presentation.get("cast_vfx_key", vfx_key),
                sfx_key=sfx_key,
                reason_key="",
                payload={"skill_id": skill.skill_package_id or skill.skill_template_id},
            ),
            *[
            SkillEvent(
                event_id=_event_id(skill, timestamp_ms, index + 1, "projectile_spawn"),
                type="projectile_spawn",
                timestamp_ms=timestamp_ms + index * burst_interval_ms,
                source_entity=source_entity,
                target_entity=target_entity,
                position=spawn_position,
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
                    "end_position": _projectile_end_position(spawn_position, projectile_direction, visual_distance),
                    "spawn_world_position": dict(spawn_position),
                    "target_world_position": dict(target_position),
                    "direction_world": dict(projectile_direction),
                    "velocity_world": {
                        "x": projectile_direction["x"] * projectile_speed,
                        "y": projectile_direction["y"] * projectile_speed,
                    },
                    "projectile_id": _projectile_id(skill, timestamp_ms, index + 1),
                    "skill_id": skill.skill_package_id or skill.skill_template_id,
                    "vfx_spawn_world_position": dict(spawn_position),
                    "vfx_direction_world": dict(projectile_direction),
                    "projectile_index": index + 1,
                    "projectile_count": projectile_count,
                    "pierce_remaining": pierce_count if hit_policy == "pierce" or pierce_count > 0 else 0,
                    "projectile_speed": projectile_speed,
                    "lifetime_ms": duration_ms,
                    "expire_time_ms": timestamp_ms + index * burst_interval_ms + duration_ms,
                    "expire_world_position": _projectile_end_position(spawn_position, projectile_direction, visual_distance),
                    "local_spread_angle": spread_angles[index],
                    "fan_angle": spread_angle_deg,
                    "burst_interval_ms": burst_interval_ms,
                    "spread_angle_deg": spread_angle_deg,
                    "spread_angle": spread_angle_deg,
                    "angle_step": angle_step_deg,
                    "spawn_pattern": runtime_params.get("spawn_pattern", "centered_fan"),
                    "projectile_radius": runtime_params.get("projectile_radius", 0),
                    "impact_radius": runtime_params.get("impact_radius", 0),
                },
            )
            for index, projectile_direction in enumerate(directions)
            ],
        ]
        for index, projectile_direction in enumerate(directions):
            projectile_delay_ms = index * burst_interval_ms
            impact_delay_ms = projectile_delay_ms + impact_duration_ms
            impact_position = _projectile_end_position(spawn_position, projectile_direction, distance)
            projectile_payload = {
                "projectile_index": index + 1,
                "projectile_count": projectile_count,
                "projectile_id": _projectile_id(skill, timestamp_ms, index + 1),
                "skill_id": skill.skill_package_id or skill.skill_template_id,
                "impact_world_position": dict(impact_position),
                "hit_world_position": dict(impact_position),
                "direction_world": dict(projectile_direction),
                "velocity_world": {
                    "x": projectile_direction["x"] * projectile_speed,
                    "y": projectile_direction["y"] * projectile_speed,
                },
                "pierce_remaining": pierce_count if hit_policy == "pierce" or pierce_count > 0 else 0,
                "projectile_speed": projectile_speed,
                "lifetime_ms": duration_ms,
                "expire_time_ms": timestamp_ms + projectile_delay_ms + duration_ms,
                "expire_world_position": _projectile_end_position(spawn_position, projectile_direction, visual_distance),
                "projectile_continues": impact_delay_ms < projectile_delay_ms + duration_ms,
                "impact_kind": "projectile_hit_continue" if impact_delay_ms < projectile_delay_ms + duration_ms else "projectile_final_impact",
                "local_spread_angle": spread_angles[index],
                "fan_angle": spread_angle_deg,
                "hit_policy": hit_policy,
                "pierce_count": pierce_count,
            }
            events.extend(
                [
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, projectile_count + index * 4 + 1, "projectile_hit"),
                        type="projectile_hit",
                        timestamp_ms=timestamp_ms + impact_delay_ms,
                        source_entity=source_entity,
                        target_entity=target_entity,
                        position=impact_position,
                        direction=projectile_direction,
                        delay_ms=impact_delay_ms,
                        duration_ms=0,
                        amount=None,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=hit_vfx_key,
                        sfx_key=sfx_key,
                        reason_key=reason_key,
                        payload=projectile_payload,
                    ),
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, projectile_count + index * 4 + 2, "damage"),
                        type="damage",
                        timestamp_ms=timestamp_ms + impact_delay_ms,
                        source_entity=source_entity,
                        target_entity=target_entity,
                        position=impact_position,
                        direction=projectile_direction,
                        delay_ms=impact_delay_ms,
                        duration_ms=0,
                        amount=damage_amount,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=hit_vfx_key,
                        sfx_key=sfx_key,
                        reason_key=reason_key,
                        payload=projectile_payload,
                    ),
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, projectile_count + index * 4 + 3, "hit_vfx"),
                        type="hit_vfx",
                        timestamp_ms=timestamp_ms + impact_delay_ms,
                        source_entity=source_entity,
                        target_entity=target_entity,
                        position=impact_position,
                        direction=projectile_direction,
                        delay_ms=impact_delay_ms,
                        duration_ms=420,
                        amount=None,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=hit_vfx_key,
                        sfx_key=sfx_key,
                        reason_key=reason_key,
                        payload=projectile_payload,
                    ),
                    SkillEvent(
                        event_id=_event_id(skill, timestamp_ms, projectile_count + index * 4 + 4, "floating_text"),
                        type="floating_text",
                        timestamp_ms=timestamp_ms + impact_delay_ms,
                        source_entity=source_entity,
                        target_entity=target_entity,
                        position=impact_position,
                        direction=projectile_direction,
                        delay_ms=impact_delay_ms,
                        duration_ms=800,
                        amount=damage_amount,
                        damage_type=skill.damage_type,
                        skill_instance_id=skill.active_gem_instance_id,
                        vfx_key=hit_vfx_key,
                        sfx_key=sfx_key,
                        reason_key=floating_key,
                        payload={**projectile_payload, "text": floating_text},
                    ),
                ]
            )
        return _sorted_events(events)

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
        projectile_speed = max(1.0, float(runtime_params.get("projectile_speed", 720.0)))
        min_duration_ms = int(runtime_params.get("min_duration_ms", 0))
        max_duration_ms = _optional_int(runtime_params.get("max_duration_ms"))
        projectile_count = max(1, int(runtime_params.get("projectile_count", skill.projectile_count)))
        burst_interval_ms = max(0, int(runtime_params.get("burst_interval_ms", 0)))
        spread_angle_deg = _spread_angle_deg(runtime_params, skill.behavior_template)
        angle_step_deg = _angle_step_deg(runtime_params, skill.behavior_template)
        damage_amount = skill.final_damage * _per_projectile_damage_scale(runtime_params, skill.behavior_template)
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
        visual_distance = max_distance if hit_policy == "pierce" or pierce_count > 0 else 0.0
        spawn_position = _spawn_position(source_position, runtime_params)
        primary_target = min(
            targets,
            key=lambda target: hypot(target.position["x"] - spawn_position["x"], target.position["y"] - spawn_position["y"]),
        )
        primary_distance = min(
            max_distance,
            hypot(primary_target.position["x"] - spawn_position["x"], primary_target.position["y"] - spawn_position["y"]),
        )
        visual_distance = visual_distance or primary_distance
        duration_ms = _duration_ms(visual_distance, projectile_speed, min_duration_ms, max_duration_ms)
        direction = _direction(spawn_position, primary_target.position)
        spread_angles = _spread_angles(projectile_count, spread_angle_deg, angle_step_deg)
        directions = tuple(
            _rotate_direction(direction, spread_angle) if spread_angle else dict(direction)
            for spread_angle in spread_angles
        )
        vfx_key = presentation.get("projectile_vfx_key", presentation.get("vfx", skill.visual_effect))
        hit_vfx_key = presentation.get("hit_vfx_key", presentation.get("vfx", vfx_key))
        sfx_key = presentation.get("sfx", "")
        floating_key = presentation.get("floating_text", "skill_event.fire_bolt.floating_text")
        reason_key = _damage_reason_key(skill)
        floating_text = _damage_text(damage_amount, skill.damage_type)
        events: list[SkillEvent] = []
        next_index = 1
        events.append(
            SkillEvent(
                event_id=_event_id(skill, timestamp_ms, 0, "cast_start"),
                type="cast_start",
                timestamp_ms=timestamp_ms,
                source_entity=source_entity,
                target_entity=primary_target.entity_id,
                position=source_position,
                direction=direction,
                delay_ms=0,
                duration_ms=0,
                amount=None,
                damage_type=skill.damage_type,
                skill_instance_id=skill.active_gem_instance_id,
                vfx_key=presentation.get("cast_vfx_key", vfx_key),
                sfx_key=sfx_key,
                reason_key="",
                payload={"skill_id": skill.skill_package_id or skill.skill_template_id},
            )
        )

        for projectile_index, projectile_direction in enumerate(directions, start=1):
            projectile_delay_ms = (projectile_index - 1) * burst_interval_ms
            events.append(
                SkillEvent(
                    event_id=_event_id(skill, timestamp_ms, next_index, "projectile_spawn"),
                    type="projectile_spawn",
                    timestamp_ms=timestamp_ms + projectile_delay_ms,
                    source_entity=source_entity,
                    target_entity=primary_target.entity_id,
                    position=spawn_position,
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
                            "x": spawn_position["x"] + projectile_direction["x"] * visual_distance,
                            "y": spawn_position["y"] + projectile_direction["y"] * visual_distance,
                        },
                        "spawn_world_position": dict(spawn_position),
                        "target_world_position": dict(primary_target.position),
                        "direction_world": dict(projectile_direction),
                        "velocity_world": {
                            "x": projectile_direction["x"] * projectile_speed,
                            "y": projectile_direction["y"] * projectile_speed,
                        },
                        "projectile_id": _projectile_id(skill, timestamp_ms, projectile_index),
                        "skill_id": skill.skill_package_id or skill.skill_template_id,
                        "vfx_spawn_world_position": dict(spawn_position),
                        "vfx_direction_world": dict(projectile_direction),
                        "projectile_index": projectile_index,
                        "projectile_count": projectile_count,
                        "pierce_remaining": pierce_count if hit_policy == "pierce" or pierce_count > 0 else 0,
                        "projectile_speed": projectile_speed,
                        "lifetime_ms": duration_ms,
                        "expire_time_ms": timestamp_ms + projectile_delay_ms + duration_ms,
                        "expire_world_position": {
                            "x": spawn_position["x"] + projectile_direction["x"] * visual_distance,
                            "y": spawn_position["y"] + projectile_direction["y"] * visual_distance,
                        },
                        "local_spread_angle": spread_angles[projectile_index - 1],
                        "fan_angle": spread_angle_deg,
                        "burst_interval_ms": burst_interval_ms,
                        "spread_angle_deg": spread_angle_deg,
                        "spread_angle": spread_angle_deg,
                        "angle_step": angle_step_deg,
                        "spawn_pattern": runtime_params.get("spawn_pattern", "centered_fan"),
                        "projectile_radius": runtime_params.get("projectile_radius", 0),
                        "impact_radius": runtime_params.get("impact_radius", 0),
                    },
                )
            )
            next_index += 1

        for projectile_index, projectile_direction in enumerate(directions, start=1):
            projectile_delay_ms = (projectile_index - 1) * burst_interval_ms
            projectile_hits = _projectile_hit_targets(
                spawn_position,
                projectile_direction,
                targets,
                max_distance=max_distance,
                collision_radius=collision_radius,
                max_hits=max_hits_per_projectile,
            )
            for hit_order, (target, forward) in enumerate(projectile_hits):
                impact_duration_ms = _duration_ms(forward, projectile_speed, min_duration_ms, max_duration_ms)
                impact_delay_ms = projectile_delay_ms + impact_duration_ms
                impact_position = _projectile_end_position(spawn_position, projectile_direction, forward)
                pierce_remaining = max(0, max_hits_per_projectile - hit_order - 1)
                projectile_continues = pierce_remaining > 0 or impact_delay_ms < projectile_delay_ms + duration_ms
                projectile_payload = {
                    "projectile_index": projectile_index,
                    "projectile_count": projectile_count,
                    "projectile_id": _projectile_id(skill, timestamp_ms, projectile_index),
                    "skill_id": skill.skill_package_id or skill.skill_template_id,
                    "impact_world_position": dict(impact_position),
                    "hit_world_position": dict(impact_position),
                    "target_world_position": dict(target.position),
                    "direction_world": dict(projectile_direction),
                    "velocity_world": {
                        "x": projectile_direction["x"] * projectile_speed,
                        "y": projectile_direction["y"] * projectile_speed,
                    },
                    "pierce_remaining": pierce_remaining,
                    "projectile_speed": projectile_speed,
                    "lifetime_ms": duration_ms,
                    "expire_time_ms": timestamp_ms + projectile_delay_ms + duration_ms,
                    "expire_world_position": {
                        "x": spawn_position["x"] + projectile_direction["x"] * visual_distance,
                        "y": spawn_position["y"] + projectile_direction["y"] * visual_distance,
                    },
                    "projectile_continues": projectile_continues,
                    "impact_kind": "projectile_hit_continue" if projectile_continues else "projectile_final_impact",
                    "local_spread_angle": spread_angles[projectile_index - 1],
                    "fan_angle": spread_angle_deg,
                    "hit_policy": hit_policy,
                    "pierce_count": pierce_count,
                }
                events.extend(
                    [
                        SkillEvent(
                            event_id=_event_id(skill, timestamp_ms, next_index, "projectile_hit"),
                            type="projectile_hit",
                            timestamp_ms=timestamp_ms + impact_delay_ms,
                            source_entity=source_entity,
                            target_entity=target.entity_id,
                            position=impact_position,
                            direction=projectile_direction,
                            delay_ms=impact_delay_ms,
                            duration_ms=0,
                            amount=None,
                            damage_type=skill.damage_type,
                            skill_instance_id=skill.active_gem_instance_id,
                            vfx_key=hit_vfx_key,
                            sfx_key=sfx_key,
                            reason_key=reason_key,
                            payload=projectile_payload,
                        ),
                        SkillEvent(
                            event_id=_event_id(skill, timestamp_ms, next_index + 1, "damage"),
                            type="damage",
                            timestamp_ms=timestamp_ms + impact_delay_ms,
                            source_entity=source_entity,
                            target_entity=target.entity_id,
                            position=impact_position,
                            direction=projectile_direction,
                            delay_ms=impact_delay_ms,
                            duration_ms=0,
                            amount=damage_amount,
                            damage_type=skill.damage_type,
                            skill_instance_id=skill.active_gem_instance_id,
                            vfx_key=hit_vfx_key,
                            sfx_key=sfx_key,
                            reason_key=reason_key,
                            payload=projectile_payload,
                        ),
                        SkillEvent(
                            event_id=_event_id(skill, timestamp_ms, next_index + 2, "hit_vfx"),
                            type="hit_vfx",
                            timestamp_ms=timestamp_ms + impact_delay_ms,
                            source_entity=source_entity,
                            target_entity=target.entity_id,
                            position=impact_position,
                            direction=projectile_direction,
                            delay_ms=impact_delay_ms,
                            duration_ms=420,
                            amount=None,
                            damage_type=skill.damage_type,
                            skill_instance_id=skill.active_gem_instance_id,
                            vfx_key=hit_vfx_key,
                            sfx_key=sfx_key,
                            reason_key=reason_key,
                            payload=projectile_payload,
                        ),
                        SkillEvent(
                            event_id=_event_id(skill, timestamp_ms, next_index + 3, "floating_text"),
                            type="floating_text",
                            timestamp_ms=timestamp_ms + impact_delay_ms,
                            source_entity=source_entity,
                            target_entity=target.entity_id,
                            position=impact_position,
                            direction=projectile_direction,
                            delay_ms=impact_delay_ms,
                            duration_ms=800,
                            amount=damage_amount,
                            damage_type=skill.damage_type,
                            skill_instance_id=skill.active_gem_instance_id,
                            vfx_key=hit_vfx_key,
                            sfx_key=sfx_key,
                            reason_key=floating_key,
                            payload={**projectile_payload, "text": floating_text},
                        ),
                    ]
                )
                next_index += 4
        return _sorted_events(events)


def _event_id(skill: FinalSkillInstance, timestamp_ms: int, index: int, event_type: str) -> str:
    return f"{skill.active_gem_instance_id}.{timestamp_ms}.{index}.{event_type}"


def _sorted_events(events: list[SkillEvent]) -> tuple[SkillEvent, ...]:
    return tuple(sorted(events, key=lambda event: (event.timestamp_ms, _runtime_event_sort_order(event.type), event.event_id)))


def _runtime_event_sort_order(event_type: str) -> int:
    return {
        "cast_start": 0,
        "area_spawn": 1,
        "projectile_spawn": 1,
        "projectile_hit": 2,
        "damage": 3,
        "hit_vfx": 4,
        "floating_text": 5,
        "cooldown_update": 6,
    }.get(event_type, 99)


def _projectile_id(skill: FinalSkillInstance, timestamp_ms: int, projectile_index: int) -> str:
    return f"{skill.active_gem_instance_id}.{timestamp_ms}.projectile.{projectile_index}"


def _position_dict(position: object) -> dict[str, float]:
    return {
        "x": float(getattr(position, "x")),
        "y": float(getattr(position, "y")),
    }


def _spawn_position(source_position: dict[str, float], runtime_params: dict[str, Any]) -> dict[str, float]:
    offset = runtime_params.get("spawn_offset", {})
    if not isinstance(offset, dict):
        offset = {}
    return {
        "x": source_position["x"] + float(offset.get("x", 0.0)),
        "y": source_position["y"] + float(offset.get("y", 0.0)),
    }


def _direction(source: dict[str, float], target: dict[str, float]) -> dict[str, float]:
    dx = target["x"] - source["x"]
    dy = target["y"] - source["y"]
    length = hypot(dx, dy)
    if length <= 0:
        return {"x": 1.0, "y": 0.0}
    return {"x": dx / length, "y": dy / length}


def _duration_ms(distance: float, projectile_speed: float, min_duration_ms: int, max_duration_ms: int | None) -> int:
    duration_ms = int(round(max(0.0, distance) / max(1.0, projectile_speed) * 1000))
    if max_duration_ms is not None:
        duration_ms = min(duration_ms, max_duration_ms)
    return max(min_duration_ms, duration_ms)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _projectile_end_position(
    source: dict[str, float],
    direction: dict[str, float],
    distance: float,
) -> dict[str, float]:
    return {
        "x": source["x"] + direction["x"] * distance,
        "y": source["y"] + direction["y"] * distance,
    }


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


def _spread_angle_deg(runtime_params: dict[str, Any], behavior_template: str) -> float:
    if behavior_template == "fan_projectile":
        return max(0.0, float(runtime_params.get("spread_angle", 0.0)))
    return max(0.0, float(runtime_params.get("spread_angle_deg", 0.0)))


def _angle_step_deg(runtime_params: dict[str, Any], behavior_template: str) -> float:
    return max(0.0, float(runtime_params.get("angle_step", 0.0)))


def _per_projectile_damage_scale(runtime_params: dict[str, Any], behavior_template: str) -> float:
    if behavior_template != "fan_projectile":
        return 1.0
    return max(0.01, float(runtime_params.get("per_projectile_damage_scale", 1.0)))


def _damage_reason_key(skill: FinalSkillInstance) -> str:
    skill_id = skill.skill_package_id or skill.skill_template_id
    if "ice_shards" in skill_id:
        return "skill_event.ice_shards.damage_reason"
    if "fire_bolt" in skill_id:
        return "skill_event.fire_bolt.damage_reason"
    return f"skill_event.{skill_id}.damage_reason"


def _spread_directions(
    direction: dict[str, float],
    projectile_count: int,
    spread_angle_deg: float,
    angle_step_deg: float = 0.0,
) -> tuple[dict[str, float], ...]:
    spread_angles = _spread_angles(projectile_count, spread_angle_deg, angle_step_deg)
    return tuple(
        _rotate_direction(direction, spread_angle) if spread_angle else dict(direction)
        for spread_angle in spread_angles
    )


def _spread_angles(projectile_count: int, spread_angle_deg: float, angle_step_deg: float = 0.0) -> tuple[float, ...]:
    count = max(1, projectile_count)
    if count == 1 or spread_angle_deg <= 0:
        return tuple(0.0 for _ in range(count))
    center = (count - 1) / 2
    if angle_step_deg > 0:
        maximum_step = spread_angle_deg / max(1, count - 1)
        step = min(angle_step_deg, maximum_step)
        return tuple((index - center) * step for index in range(count))
    return tuple(
        ((index - center) / max(1, count - 1)) * spread_angle_deg
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
