from __future__ import annotations

from dataclasses import dataclass

from .config import (
    AffixDefinition,
    ConduitAmplifier,
    GemDefinition,
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


@dataclass(frozen=True)
class FinalSkillInstance:
    active_gem_instance_id: str
    base_gem_id: str
    skill_template_id: str
    tags: frozenset[str]
    base_damage: float
    final_damage: float
    base_cooldown_ms: int
    final_cooldown_ms: int
    projectile_count: int
    area_multiplier: float
    speed_multiplier: float
    applied_modifiers: tuple[AppliedModifier, ...]


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
            if self.board.inventory.require(instance_id).is_active_skill
        ]
        return tuple(self.calculate_for_active(instance) for instance in active_instances)

    def calculate_for_active(self, active: GemInstance) -> FinalSkillInstance:
        definition = self.definitions[active.base_gem_id]
        if definition.skill_template_id is None:
            raise SkillEffectError("skill_effect.error.missing_template", "主动技能缺少技能模板")
        template = self.skill_templates[definition.skill_template_id]
        modifiers: list[AppliedModifier] = []
        dedupe: set[tuple[str, str, str]] = set()

        # 1-2. 读取主动技能基础定义并应用主动宝石自身随机词缀。
        for roll in active.prefix_affixes + active.suffix_affixes + active.implicit_affixes:
            self._append_affix_modifier(
                modifiers,
                dedupe,
                source=active,
                target=active,
                roll=roll,
                relation="self",
                scale=1.0,
                reason_key="modifier.active_affix",
                active_tags=template.tags,
            )

        # 3-6. 查找可影响目标的辅助宝石，应用基础效果、随机词缀和导管放大。
        for support, relation in self._support_sources_for(active):
            support_definition = self.definitions[support.base_gem_id]
            if not self._gem_filter_matches(support_definition, template.tags):
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
            for roll in support.prefix_affixes + support.suffix_affixes + support.implicit_affixes:
                self._append_affix_modifier(
                    modifiers,
                    dedupe,
                    source=support,
                    target=active,
                    roll=roll,
                    relation=relation,
                    scale=relation_scale,
                    reason_key="modifier.support_affix",
                    active_tags=template.tags,
                )

        # 7-9. 汇总 additive/final 并输出最终技能实例。
        return self._build_final_skill(active, template, tuple(modifiers))

    def _support_sources_for(self, active: GemInstance) -> list[tuple[GemInstance, str]]:
        sources: list[tuple[GemInstance, str]] = []
        for instance_id in self.board.view().cells.values():
            if instance_id == active.instance_id:
                continue
            instance = self.board.inventory.require(instance_id)
            if "support_gem" not in instance.tags:
                continue
            relation = self._effective_relation(instance.instance_id, active.instance_id)
            if relation is not None:
                sources.append((instance, relation))
        return sources

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
        total = 0.0
        for roll in instance.prefix_affixes + instance.suffix_affixes + instance.implicit_affixes:
            if roll.stat == stat:
                total += float(roll.value)
        return 1.0 + total / 100.0

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
            )
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
            )
        )

    def _gem_filter_matches(self, definition: GemDefinition, active_tags: frozenset[str]) -> bool:
        if definition.apply_filter_tags_any and not (definition.apply_filter_tags_any & active_tags):
            return False
        if definition.apply_filter_tags_all and not definition.apply_filter_tags_all.issubset(active_tags):
            return False
        if definition.apply_filter_tags_none and definition.apply_filter_tags_none & active_tags:
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

        return FinalSkillInstance(
            active_gem_instance_id=active.instance_id,
            base_gem_id=active.base_gem_id,
            skill_template_id=template.template_id,
            tags=template.tags,
            base_damage=template.base_damage,
            final_damage=final_damage,
            base_cooldown_ms=template.base_cooldown_ms,
            final_cooldown_ms=max(0, round(cooldown)),
            projectile_count=max(1, 1 + round(additive.get("projectile_count_add", 0.0))),
            area_multiplier=1.0 + additive.get("area_add_percent", 0.0) / 100.0,
            speed_multiplier=speed_multiplier,
            applied_modifiers=modifiers,
        )

    def _sum_by_stat(self, modifiers: list[AppliedModifier], layer: str) -> dict[str, float]:
        result: dict[str, float] = {}
        for modifier in modifiers:
            if modifier.layer != layer:
                continue
            result[modifier.stat] = result.get(modifier.stat, 0.0) + modifier.value
        return result
