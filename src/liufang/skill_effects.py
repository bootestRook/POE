from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import (
    AffixDefinition,
    ConduitAmplifier,
    GemDefinition,
    PassiveEffect,
    SkillScalingRules,
    SkillTemplate,
    SupportBaseModifier,
)
from .gem_board import GemRelation, SudokuGemBoard
from .inventory import AffixRoll, GemInstance


BOARD_SOURCE_STATS = {
    "same_row": "source_power_row",
    "same_column": "source_power_column",
    "same_box": "source_power_box",
}
BOARD_TARGET_STATS = {
    "same_row": "target_power_row",
    "same_column": "target_power_column",
    "same_box": "target_power_box",
}
RELATION_PRIORITY = ("adjacent", "same_row", "same_column", "same_box")


class SkillEffectError(ValueError):
    def __init__(self, error_key: str, message: str) -> None:
        super().__init__(message)
        self.error_key = error_key
        self.message = message


@dataclass(frozen=True)
class AppliedModifier:
    source_instance_id: str
    source_base_gem_id: str
    target_instance_id: str
    stat: str
    value: float
    layer: str
    relation: str
    reason_key: str
    applied: bool = True
    target_base_gem_id: str = ""
    shape_effect: str = ""


@dataclass(frozen=True)
class FinalSkillInstance:
    active_gem_instance_id: str
    base_gem_id: str
    skill_template_id: str
    tags: frozenset[str]
    base_damage: float
    final_damage: float
    damage_type: str
    behavior_type: str
    visual_effect: str
    shape_effects: tuple[str, ...]
    base_cooldown_ms: int
    final_cooldown_ms: int
    projectile_count: int
    area_multiplier: float
    speed_multiplier: float
    applied_modifiers: tuple[AppliedModifier, ...]
    skill_package_id: str = ""
    skill_package_version: str = ""
    behavior_template: str = ""
    cast: dict[str, Any] | None = None
    hit: dict[str, Any] | None = None
    runtime_params: dict[str, Any] | None = None
    presentation_keys: dict[str, str] | None = None
    source_context: dict[str, Any] | None = None

    @property
    def uses_skill_event_pipeline(self) -> bool:
        return bool(self.skill_package_id and self.behavior_template)


@dataclass(frozen=True)
class PlayerStatModifier:
    source_instance_id: str
    source_base_gem_id: str
    stat: str
    value: float
    layer: str
    reason_key: str


@dataclass
class SkillEffectCalculator:
    board: SudokuGemBoard
    definitions: dict[str, GemDefinition]
    skill_templates: dict[str, SkillTemplate]
    relation_coefficients: dict[str, float]
    scaling_rules: SkillScalingRules
    affix_definitions: dict[str, AffixDefinition]

    def calculate_all(self) -> tuple[FinalSkillInstance, ...]:
        validation = self.board.validate()
        if not validation.is_valid:
            raise SkillEffectError("skill_effect.error.invalid_board", "非法盘面不可用于战斗")
        if not validation.can_enter_combat:
            raise SkillEffectError(
                validation.enter_combat_error_key or "skill_effect.error.cannot_enter_combat",
                validation.enter_combat_message or "当前盘面不可进入战斗",
            )

        active_instances = [
            self.board.inventory.require(instance_id)
            for instance_id in self.board.view().cells.values()
            if self.board.inventory.require(instance_id).gem_kind == "active_skill"
        ]
        return tuple(self.calculate_for_active(instance) for instance in active_instances)

    def calculate_for_active(self, active: GemInstance) -> FinalSkillInstance:
        definition = self.definitions[active.base_gem_id]
        if active.gem_kind != "active_skill":
            raise SkillEffectError("skill_effect.error.missing_template", "主动技能缺少技能模板")
        if definition.skill_template_id is None:
            raise SkillEffectError("skill_effect.error.missing_template", "主动技能缺少技能模板")
        template = self.skill_templates[definition.skill_template_id]
        modifiers: list[AppliedModifier] = []
        dedupe: set[tuple[str, str, str]] = set()

        # 第二阶段真实技能计算不读取随机词缀，只保留辅助与被动关系。
        for support, relation in self._support_sources_for(active):
            support_definition = self.definitions[support.base_gem_id]
            if not self._gem_filter_matches(support_definition, definition):
                continue
            relation_scale, conduit_modifiers = self._relation_scale(support, active, relation)
            modifiers.extend(conduit_modifiers)
            for base_modifier in self._support_base_modifiers(support.base_gem_id):
                self._append_raw_modifier(
                    modifiers,
                    dedupe,
                    source=support,
                    target=active,
                    stat=base_modifier.stat,
                    raw_value=base_modifier.value,
                    layer=base_modifier.layer,
                    relation=relation,
                    scale=relation_scale,
                    reason_key="modifier.support_base",
                )

        self._append_passive_contributions(active, definition, modifiers, dedupe)
        return self._build_final_skill(active, template, tuple(modifiers))

    def calculate_player_stat_modifiers(self) -> tuple[PlayerStatModifier, ...]:
        validation = self.board.validate()
        if not validation.is_valid:
            return ()
        modifiers: list[PlayerStatModifier] = []
        for passive in self._passive_instances():
            passive_definition = self.definitions[passive.base_gem_id]
            supported_values = self._support_values_for_passive(passive, passive_definition, "self_stat", [])
            for effect in passive_definition.passive_effects:
                if effect.target != "self_stat":
                    continue
                value = effect.value + supported_values.get(effect.stat, 0.0)
                modifiers.append(
                    PlayerStatModifier(
                        source_instance_id=passive.instance_id,
                        source_base_gem_id=passive.base_gem_id,
                        stat=effect.stat,
                        value=value,
                        layer=effect.layer,
                        reason_key="modifier.self_stat_passive",
                    )
                )
        return tuple(modifiers)

    def apply_player_stat_contributions(self, player: object) -> tuple[PlayerStatModifier, ...]:
        modifiers = self.calculate_player_stat_modifiers()
        max_life_add = sum(modifier.value for modifier in modifiers if modifier.stat == "max_life")
        move_speed_add = sum(modifier.value for modifier in modifiers if modifier.stat == "move_speed")

        if max_life_add:
            old_max = float(getattr(player, "max_life"))
            old_current = float(getattr(player, "current_life"))
            setattr(player, "max_life", old_max + max_life_add)
            if old_current >= old_max:
                setattr(player, "current_life", old_current + max_life_add)
        if move_speed_add:
            base_move_speed = float(getattr(player, "move_speed", 1.0))
            setattr(player, "move_speed", base_move_speed * (1.0 + move_speed_add / 100.0))
        return modifiers

    def _support_sources_for(self, target: GemInstance) -> list[tuple[GemInstance, str]]:
        sources: list[tuple[GemInstance, str]] = []
        for instance_id in self.board.view().cells.values():
            if instance_id == target.instance_id:
                continue
            instance = self.board.inventory.require(instance_id)
            if instance.gem_kind != "support":
                continue
            if target.gem_kind == "support":
                continue
            relation = self._effective_relation(instance.instance_id, target.instance_id)
            if relation is not None:
                sources.append((instance, relation))
        return sources

    def _passive_instances(self) -> list[GemInstance]:
        return [
            self.board.inventory.require(instance_id)
            for instance_id in self.board.view().cells.values()
            if self.board.inventory.require(instance_id).gem_kind == "passive_skill"
        ]

    def _append_passive_contributions(
        self,
        active: GemInstance,
        active_definition: GemDefinition,
        modifiers: list[AppliedModifier],
        dedupe: set[tuple[str, str, str]],
    ) -> None:
        for passive in self._passive_instances():
            passive_definition = self.definitions[passive.base_gem_id]
            if not self._gem_filter_matches(passive_definition, active_definition):
                continue
            relation = self._effective_relation(passive.instance_id, active.instance_id)
            if relation is None:
                continue
            supported_values = self._support_values_for_passive(passive, passive_definition, "active_skill", modifiers, dedupe)
            relation_scale, conduit_modifiers = self._relation_scale(passive, active, relation)
            modifiers.extend(conduit_modifiers)
            for effect in passive_definition.passive_effects:
                if effect.target != "active_skill":
                    continue
                self._append_passive_effect_modifier(
                    modifiers,
                    dedupe,
                    source=passive,
                    target=active,
                    effect=effect,
                    relation=relation,
                    scale=relation_scale,
                    extra_value=supported_values.get(effect.stat, 0.0),
                )

    def _support_values_for_passive(
        self,
        passive: GemInstance,
        passive_definition: GemDefinition,
        target_effect_kind: str,
        modifiers: list[AppliedModifier],
        dedupe: set[tuple[str, str, str]] | None = None,
    ) -> dict[str, float]:
        supported_stats = {
            effect.stat
            for effect in passive_definition.passive_effects
            if effect.target == target_effect_kind
        }
        values: dict[str, float] = {}
        local_dedupe: set[tuple[str, str, str]] = set()
        for support, relation in self._support_sources_for(passive):
            support_definition = self.definitions[support.base_gem_id]
            if not self._gem_filter_matches(support_definition, passive_definition):
                continue
            relation_scale, conduit_modifiers = self._relation_scale(support, passive, relation)
            modifiers.extend(conduit_modifiers)
            for base_modifier in self._support_base_modifiers(support.base_gem_id):
                if base_modifier.stat not in supported_stats:
                    continue
                key = (support.instance_id, passive.instance_id, base_modifier.stat)
                route_dedupe = dedupe if dedupe is not None else local_dedupe
                if key in route_dedupe:
                    self._append_ignored(
                        modifiers,
                        support,
                        passive,
                        base_modifier.stat,
                        base_modifier.value,
                        relation,
                        "modifier.ignored.duplicate_source_target_stat",
                    )
                    continue
                route_dedupe.add(key)
                value = base_modifier.value * relation_scale
                values[base_modifier.stat] = values.get(base_modifier.stat, 0.0) + value
                modifiers.append(
                    AppliedModifier(
                        source_instance_id=support.instance_id,
                        source_base_gem_id=support.base_gem_id,
                        target_instance_id=passive.instance_id,
                        stat=base_modifier.stat,
                        value=value,
                        layer=base_modifier.layer,
                        relation=relation,
                        reason_key="modifier.support_to_passive",
                        applied=True,
                        target_base_gem_id=passive.base_gem_id,
                    )
                )
        return values

    def _effective_relation(self, source_id: str, target_id: str) -> str | None:
        relations = [
            relation.relation
            for relation in self.board.relations()
            if {relation.source_instance_id, relation.target_instance_id} == {source_id, target_id}
        ]
        for candidate in RELATION_PRIORITY:
            if candidate in relations:
                return candidate
        return None

    def _relation_scale(
        self,
        source: GemInstance,
        target: GemInstance,
        relation: str,
    ) -> tuple[float, list[AppliedModifier]]:
        relation_coefficient = self.relation_coefficients[relation]
        if relation == "adjacent":
            return relation_coefficient, []

        source_power = self._board_power(source, BOARD_SOURCE_STATS[relation])
        target_power = self._board_power(target, BOARD_TARGET_STATS[relation])
        conduit_multiplier, conduit_modifiers = self._conduit_multiplier(target, relation)
        return relation_coefficient * source_power * target_power * conduit_multiplier, conduit_modifiers

    def _board_power(self, instance: GemInstance, stat: str) -> float:
        return 1.0

    def _conduit_multiplier(
        self,
        target: GemInstance,
        relation: str,
    ) -> tuple[float, list[AppliedModifier]]:
        multiplier = 1.0
        modifiers: list[AppliedModifier] = []
        for conduit in self._matching_conduits(target, relation):
            amplifier = self._conduit_amplifier(conduit.base_gem_id, relation)
            if amplifier is None:
                continue
            multiplier *= amplifier.multiplier
            modifiers.append(
                AppliedModifier(
                    source_instance_id=conduit.instance_id,
                    source_base_gem_id=conduit.base_gem_id,
                    target_instance_id=target.instance_id,
                    stat="conduit_multiplier",
                    value=amplifier.multiplier,
                    layer="final",
                    relation=relation,
                    reason_key="modifier.conduit_amplifier",
                    applied=True,
                    target_base_gem_id=target.base_gem_id,
                )
            )
        return multiplier, modifiers

    def _matching_conduits(self, target: GemInstance, relation: str) -> list[GemInstance]:
        conduits: list[GemInstance] = []
        for instance_id in self.board.view().cells.values():
            instance = self.board.inventory.require(instance_id)
            if "support_conduit" not in instance.tags:
                continue
            if self._effective_relation(instance.instance_id, target.instance_id) == relation:
                conduits.append(instance)
        return conduits

    def _conduit_amplifier(self, support_id: str, relation: str) -> ConduitAmplifier | None:
        for amplifier in self.scaling_rules.conduit_amplifiers:
            if amplifier.support_id == support_id and amplifier.relation == relation:
                return amplifier
        return None

    def _support_base_modifiers(self, support_id: str) -> list[SupportBaseModifier]:
        return [
            modifier
            for modifier in self.scaling_rules.support_base_modifiers
            if modifier.support_id == support_id
        ]

    def _append_affix_modifier(
        self,
        modifiers: list[AppliedModifier],
        dedupe: set[tuple[str, str, str]],
        *,
        source: GemInstance,
        target: GemInstance,
        roll: AffixRoll,
        relation: str,
        scale: float,
        reason_key: str,
        active_tags: frozenset[str],
    ) -> None:
        affix_definition = self.affix_definitions.get(roll.affix_id)
        if affix_definition is None:
            self._append_ignored(modifiers, source, target, roll.stat, roll.value, relation, "modifier.ignored.unknown_affix")
            return
        if affix_definition.apply_filter_tags and not (affix_definition.apply_filter_tags & active_tags):
            self._append_ignored(modifiers, source, target, roll.stat, roll.value, relation, "modifier.ignored.apply_filter")
            return
        if roll.stat.startswith("source_power_") or roll.stat.startswith("target_power_"):
            self._append_ignored(modifiers, source, target, roll.stat, roll.value, relation, "modifier.ignored.board_power_trace")
            return
        layer = self.scaling_rules.stat_layers.get(roll.stat)
        if layer is None:
            self._append_ignored(modifiers, source, target, roll.stat, roll.value, relation, "modifier.ignored.unsupported_stat")
            return
        self._append_raw_modifier(
            modifiers,
            dedupe,
            source=source,
            target=target,
            stat=roll.stat,
            raw_value=float(roll.value),
            layer=layer,
            relation=relation,
            scale=scale,
            reason_key=reason_key,
        )

    def _append_raw_modifier(
        self,
        modifiers: list[AppliedModifier],
        dedupe: set[tuple[str, str, str]],
        *,
        source: GemInstance,
        target: GemInstance,
        stat: str,
        raw_value: float,
        layer: str,
        relation: str,
        scale: float,
        reason_key: str,
    ) -> None:
        key = (source.instance_id, target.instance_id, stat)
        if key in dedupe:
            self._append_ignored(modifiers, source, target, stat, raw_value, relation, "modifier.ignored.duplicate_source_target_stat")
            return
        dedupe.add(key)
        value = raw_value * scale
        source_definition = self.definitions.get(source.base_gem_id)
        modifiers.append(
            AppliedModifier(
                source_instance_id=source.instance_id,
                source_base_gem_id=source.base_gem_id,
                target_instance_id=target.instance_id,
                stat=stat,
                value=value,
                layer=layer,
                relation=relation,
                reason_key=reason_key,
                target_base_gem_id=target.base_gem_id,
                shape_effect=source_definition.shape_effect if source_definition is not None else "",
            )
        )

    def _append_passive_effect_modifier(
        self,
        modifiers: list[AppliedModifier],
        dedupe: set[tuple[str, str, str]],
        *,
        source: GemInstance,
        target: GemInstance,
        effect: PassiveEffect,
        relation: str,
        scale: float,
        extra_value: float,
    ) -> None:
        self._append_raw_modifier(
            modifiers,
            dedupe,
            source=source,
            target=target,
            stat=effect.stat,
            raw_value=effect.value + extra_value,
            layer=effect.layer,
            relation=relation,
            scale=scale,
            reason_key="modifier.passive_base",
        )

    def _append_ignored(
        self,
        modifiers: list[AppliedModifier],
        source: GemInstance,
        target: GemInstance,
        stat: str,
        value: float,
        relation: str,
        reason_key: str,
    ) -> None:
        modifiers.append(
            AppliedModifier(
                source_instance_id=source.instance_id,
                source_base_gem_id=source.base_gem_id,
                target_instance_id=target.instance_id,
                stat=stat,
                value=float(value),
                layer="ignored",
                relation=relation,
                reason_key=reason_key,
                applied=False,
                target_base_gem_id=target.base_gem_id,
            )
        )

    def _gem_filter_matches(self, definition: GemDefinition, target_definition: GemDefinition) -> bool:
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

    def _build_final_skill(
        self,
        active: GemInstance,
        template: SkillTemplate,
        modifiers: tuple[AppliedModifier, ...],
    ) -> FinalSkillInstance:
        applied = [modifier for modifier in modifiers if modifier.applied]
        additive = self._sum_by_stat(applied, "additive")
        final = [modifier for modifier in applied if modifier.layer == "final"]
        shape_effects = tuple(
            dict.fromkeys(modifier.shape_effect for modifier in applied if modifier.shape_effect)
        )
        active_definition = self.definitions[active.base_gem_id]

        damage_add = additive.get("damage_add_percent", 0.0)
        for damage_stat, tag in [
            ("physical_damage_add_percent", "physical"),
            ("fire_damage_add_percent", "fire"),
            ("cold_damage_add_percent", "cold"),
            ("lightning_damage_add_percent", "lightning"),
        ]:
            if tag in template.tags:
                damage_add += additive.get(damage_stat, 0.0)
        final_damage = template.base_damage * (1.0 + damage_add / 100.0)
        for modifier in final:
            if modifier.stat == "damage_final_percent":
                final_damage *= 1.0 + modifier.value / 100.0

        speed_add = additive.get("projectile_speed_add_percent", 0.0)
        if "attack" in template.tags:
            speed_add += additive.get("attack_speed_add_percent", 0.0)
        if "spell" in template.tags:
            speed_add += additive.get("cast_speed_add_percent", 0.0)
        speed_multiplier = 1.0 + speed_add / 100.0
        for modifier in final:
            if modifier.stat == "skill_speed_final_percent":
                speed_multiplier *= 1.0 + modifier.value / 100.0

        cooldown = template.base_cooldown_ms + additive.get("added_cooldown_ms", 0.0)
        cooldown *= max(0.0, 1.0 - additive.get("cooldown_reduction_percent", 0.0) / 100.0)
        if speed_multiplier > 0:
            cooldown /= speed_multiplier
        area_multiplier = 1.0 + additive.get("area_add_percent", 0.0) / 100.0
        runtime_params = dict(template.runtime_params)
        if "projectile_speed" in runtime_params:
            runtime_params["projectile_speed"] = float(runtime_params["projectile_speed"]) * speed_multiplier
        if "radius" in runtime_params:
            runtime_params["radius"] = float(runtime_params["radius"]) * area_multiplier
        if "arc_radius" in runtime_params:
            runtime_params["arc_radius"] = float(runtime_params["arc_radius"]) * area_multiplier
        if "length" in runtime_params:
            runtime_params["length"] = float(runtime_params["length"]) * area_multiplier
        if "width" in runtime_params:
            runtime_params["width"] = float(runtime_params["width"]) * area_multiplier
        if "status_chance_scale" in runtime_params:
            runtime_params["status_chance_scale"] = float(runtime_params["status_chance_scale"]) * (
                1.0 + additive.get("status_chance_add_percent", 0.0) / 100.0
            )
        base_projectile_count = int(runtime_params.get("projectile_count", 1))
        runtime_params["projectile_count"] = max(
            1,
            base_projectile_count + round(additive.get("projectile_count_add", 0.0)),
        )
        runtime_params["max_targets"] = max(1, int(runtime_params.get("max_targets", 1)))

        return FinalSkillInstance(
            active_gem_instance_id=active.instance_id,
            base_gem_id=active.base_gem_id,
            skill_template_id=template.template_id,
            tags=template.tags,
            base_damage=template.base_damage,
            final_damage=final_damage,
            damage_type=template.damage_type,
            behavior_type=template.behavior_type,
            visual_effect=active_definition.visual_effect or template.visual_effect or template.behavior_type,
            shape_effects=shape_effects,
            base_cooldown_ms=template.base_cooldown_ms,
            final_cooldown_ms=max(0, round(cooldown)),
            projectile_count=int(runtime_params["projectile_count"]),
            area_multiplier=area_multiplier,
            speed_multiplier=speed_multiplier,
            applied_modifiers=modifiers,
            skill_package_id=template.skill_package_id,
            skill_package_version=template.skill_package_version,
            behavior_template=template.behavior_template,
            cast=dict(template.cast),
            hit=dict(template.hit),
            runtime_params=runtime_params,
            presentation_keys=dict(template.presentation_keys),
            source_context={
                "active_gem_instance_id": active.instance_id,
                "base_gem_id": active.base_gem_id,
                "gem_kind": active.gem_kind,
                "sudoku_digit": active.sudoku_digit,
            },
        )

    def _sum_by_stat(self, modifiers: list[AppliedModifier], layer: str) -> dict[str, float]:
        result: dict[str, float] = {}
        for modifier in modifiers:
            if modifier.layer != layer:
                continue
            result[modifier.stat] = result.get(modifier.stat, 0.0) + modifier.value
        return result
