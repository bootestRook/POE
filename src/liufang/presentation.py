from __future__ import annotations

from dataclasses import dataclass
from math import dist
from pathlib import Path
from typing import Any

from .combat import CombatSession, DroppedGem
from .config import (
    AffixDefinition,
    GemDefinition,
    SkillScalingRules,
    SkillTemplate,
    load_affix_definitions,
    load_gem_definitions,
    load_localization,
    load_skill_scaling_rules,
    load_skill_templates,
)
from .gem_board import BoardIssue, GemRelation, SudokuGemBoard
from .inventory import AffixRoll, GemInstance
from .skill_effects import AppliedModifier, FinalSkillInstance


@dataclass(frozen=True)
class Localizer:
    strings: dict[str, str]

    def text(self, key: str) -> str:
        value = self.strings.get(key)
        if value:
            return value
        return f"未配置文案：{key}"


@dataclass
class PresentationService:
    localizer: Localizer
    definitions: dict[str, GemDefinition]
    skill_templates: dict[str, SkillTemplate]
    scaling_rules: SkillScalingRules
    affix_definitions: dict[str, AffixDefinition]

    @classmethod
    def from_configs(cls, config_root: Path) -> "PresentationService":
        affixes = load_affix_definitions(config_root)
        return cls(
            localizer=Localizer(load_localization(config_root)),
            definitions=load_gem_definitions(config_root),
            skill_templates=load_skill_templates(config_root),
            scaling_rules=load_skill_scaling_rules(config_root),
            affix_definitions={definition.affix_id: definition for definition in affixes},
        )

    def gem_detail(
        self,
        instance: GemInstance,
        *,
        board: SudokuGemBoard | None = None,
        final_skills: tuple[FinalSkillInstance, ...] = (),
    ) -> dict[str, Any]:
        definition = self.definitions[instance.base_gem_id]
        return {
            "instance_id": instance.instance_id,
            "name_text": self.localizer.text(definition.name_key),
            "description_text": self.localizer.text(definition.description_key),
            "category_text": self._gem_category_text(definition),
            "gem_type": self._gem_type_view(instance.gem_type),
            "rarity_text": self.localizer.text(f"rarity.{instance.rarity}.name"),
            "level": instance.level,
            "locked": instance.locked,
            "board_position": self._position_view(instance.board_position),
            "tags": [self._tag_view(tag) for tag in sorted(instance.tags)],
            "base_effect": self._base_effect_view(definition),
            "random_affixes": [self._affix_roll_view(roll) for roll in instance.random_affixes],
            "implicit_affixes": [self._affix_roll_view(roll) for roll in instance.implicit_affixes],
            "can_affect": self._apply_filter_view(definition),
            "current_effective_targets": self._current_effective_targets(instance, final_skills),
            "board_relations": self._relations_for_instance(instance, board) if board is not None else [],
        }

    def board_view(
        self,
        board: SudokuGemBoard,
        *,
        final_skills: tuple[FinalSkillInstance, ...] = (),
    ) -> dict[str, Any]:
        runtime_view = board.view()
        validation = runtime_view.validation
        prompts = [self._issue_text(issue) for issue in validation.issues]
        if validation.enter_combat_error_key:
            prompts.append(self.localizer.text(validation.enter_combat_error_key))
        if not prompts:
            prompts.append(self.localizer.text("ui.board.valid"))

        return {
            "cells": self._cells_view(board),
            "boxes": self._boxes_view(board),
            "placed_gems": [
                self._placed_gem_view(board.inventory.require(instance_id))
                for instance_id in runtime_view.cells.values()
            ],
            "is_valid": validation.is_valid,
            "can_enter_combat": validation.can_enter_combat,
            "prompts": prompts,
            "highlights": self._highlights_view(runtime_view.highlights),
            "influence_preview": self._influence_preview(board),
            "skill_preview": [self.skill_preview(skill) for skill in final_skills],
        }

    def skill_preview(self, skill: FinalSkillInstance) -> dict[str, Any]:
        definition = self.definitions[skill.base_gem_id]
        template = self.skill_templates[skill.skill_template_id]
        return {
            "active_gem_instance_id": skill.active_gem_instance_id,
            "name_text": self.localizer.text(definition.name_key),
            "template_text": self.localizer.text(template.name_key),
            "labels": {
                "base_damage": self.localizer.text("ui.skill.base_damage"),
                "final_damage": self.localizer.text("ui.skill.final_damage"),
                "base_cooldown_ms": self.localizer.text("ui.skill.base_cooldown_ms"),
                "final_cooldown_ms": self.localizer.text("ui.skill.final_cooldown_ms"),
                "projectile_count": self.localizer.text("ui.skill.projectile_count"),
                "area_multiplier": self.localizer.text("ui.skill.area_multiplier"),
                "speed_multiplier": self.localizer.text("ui.skill.speed_multiplier"),
            },
            "base_damage": skill.base_damage,
            "final_damage": skill.final_damage,
            "base_cooldown_ms": skill.base_cooldown_ms,
            "final_cooldown_ms": skill.final_cooldown_ms,
            "projectile_count": skill.projectile_count,
            "area_multiplier": skill.area_multiplier,
            "speed_multiplier": skill.speed_multiplier,
            "tags": [self._tag_view(tag) for tag in sorted(skill.tags)],
            "applied_modifiers": [
                self._modifier_view(modifier) for modifier in skill.applied_modifiers
            ],
        }

    def combat_hud(self, session: CombatSession) -> dict[str, Any]:
        cooldowns = getattr(session, "_cooldowns", {})
        return {
            "player_life": {
                "label_text": self.localizer.text("ui.hud.player_life"),
                "current": session.player.current_life,
                "max": session.player.max_life,
            },
            "elapsed_ms": {
                "label_text": self.localizer.text("ui.hud.elapsed_ms"),
                "value": session.elapsed_ms,
            },
            "alive_monsters": {
                "label_text": self.localizer.text("ui.hud.alive_monsters"),
                "value": sum(1 for monster in session.monsters if monster.is_alive),
            },
            "active_skills": [
                {
                    "name_text": self.localizer.text(self.definitions[cooldown.skill.base_gem_id].name_key),
                    "remaining_ms": cooldown.remaining_ms,
                    "status_text": self.localizer.text(
                        "ui.skill.ready" if cooldown.remaining_ms == 0 else "ui.skill.cooldown"
                    ),
                }
                for cooldown in cooldowns.values()
            ],
            "drop_prompts": [self.drop_prompt(dropped) for dropped in session.dropped_gems],
            "pickup_prompts": [self._pickup_prompt(session, dropped) for dropped in session.dropped_gems],
        }

    def drop_prompt(self, dropped: DroppedGem) -> dict[str, Any]:
        definition = self.definitions[dropped.gem_instance.base_gem_id]
        return {
            "drop_id": dropped.drop_id,
            "name_text": self.localizer.text(definition.name_key),
            "rarity_text": self.localizer.text(f"rarity.{dropped.gem_instance.rarity}.name"),
            "picked_up": dropped.picked_up,
            "status_text": self.localizer.text(
                "ui.drop.picked" if dropped.picked_up else "ui.drop.not_picked"
            ),
            "inventory_result_text": self.localizer.text(
                "ui.pickup.success" if dropped.picked_up else "ui.pickup.pending"
            ),
        }

    def _gem_type_view(self, gem_type: str) -> dict[str, Any]:
        number = gem_type.rsplit("_", 1)[-1]
        return {
            "id": gem_type,
            "number": int(number),
            "display_text": self.localizer.text(f"gem_type.{number}.name"),
            "identity_text": self.localizer.text(f"ui.gem_type.{number}.identity"),
        }

    def _gem_category_text(self, definition: GemDefinition) -> str:
        if definition.is_active_skill:
            return self.localizer.text("tag.active_skill_gem.name")
        return self.localizer.text("tag.support_gem.name")

    def _tag_view(self, tag: str) -> dict[str, str]:
        return {"id": tag, "text": self.localizer.text(f"tag.{tag}.name")}

    def _base_effect_view(self, definition: GemDefinition) -> dict[str, Any]:
        if definition.skill_template_id:
            template = self.skill_templates[definition.skill_template_id]
            return {
                "title_text": self.localizer.text("ui.gem.base_skill_effect"),
                "template_text": self.localizer.text(template.name_key),
                "damage_type_text": self.localizer.text(f"damage_type.{template.damage_type}.name"),
                "base_damage": template.base_damage,
                "base_cooldown_ms": template.base_cooldown_ms,
                "scaling_stats": [self._stat_view(stat) for stat in template.scaling_stats],
            }

        modifiers = [
            modifier
            for modifier in self.scaling_rules.support_base_modifiers
            if modifier.support_id == definition.base_gem_id
        ]
        return {
            "title_text": self.localizer.text("ui.gem.support_effect"),
            "modifiers": [
                {
                    "stat": self._stat_view(modifier.stat),
                    "value": modifier.value,
                    "layer_text": self.localizer.text(f"ui.modifier.layer.{modifier.layer}"),
                }
                for modifier in modifiers
            ],
        }

    def _affix_roll_view(self, roll: AffixRoll) -> dict[str, Any]:
        definition = self.affix_definitions.get(roll.affix_id)
        return {
            "affix_id": roll.affix_id,
            "name_text": self.localizer.text(definition.name_key) if definition else self.localizer.text("ui.affix.unknown"),
            "description_text": self.localizer.text(definition.description_key) if definition else self.localizer.text("ui.affix.unknown"),
            "gen_text": self.localizer.text(f"ui.affix.gen.{roll.gen}"),
            "stat": self._stat_view(roll.stat),
            "value": roll.value,
            "group_text": self.localizer.text(f"affix_group.{roll.group}.name"),
        }

    def _stat_view(self, stat: str) -> dict[str, str]:
        prefix = "routing_stat" if stat.startswith(("source_power_", "target_power_")) else "stat"
        return {"id": stat, "text": self.localizer.text(f"{prefix}.{stat}.name")}

    def _apply_filter_view(self, definition: GemDefinition) -> dict[str, Any]:
        if definition.is_active_skill:
            return {"summary_text": self.localizer.text("ui.gem.affects_self"), "tags_any": [], "tags_all": [], "tags_none": []}
        return {
            "summary_text": self.localizer.text("ui.gem.affects_filtered_targets"),
            "tags_any": [self._tag_view(tag) for tag in sorted(definition.apply_filter_tags_any)],
            "tags_all": [self._tag_view(tag) for tag in sorted(definition.apply_filter_tags_all)],
            "tags_none": [self._tag_view(tag) for tag in sorted(definition.apply_filter_tags_none)],
        }

    def _current_effective_targets(
        self,
        instance: GemInstance,
        final_skills: tuple[FinalSkillInstance, ...],
    ) -> list[dict[str, str]]:
        targets: dict[str, dict[str, str]] = {}
        for skill in final_skills:
            if instance.instance_id == skill.active_gem_instance_id:
                targets[skill.active_gem_instance_id] = {
                    "instance_id": skill.active_gem_instance_id,
                    "name_text": self.localizer.text(self.definitions[skill.base_gem_id].name_key),
                    "status_text": self.localizer.text("ui.effect.active"),
                }
            for modifier in skill.applied_modifiers:
                if modifier.source_instance_id != instance.instance_id or not modifier.applied:
                    continue
                target_definition = self.definitions[skill.base_gem_id]
                targets[modifier.target_instance_id] = {
                    "instance_id": modifier.target_instance_id,
                    "name_text": self.localizer.text(target_definition.name_key),
                    "status_text": self.localizer.text("ui.effect.active"),
                }
        if targets:
            return list(targets.values())
        return [{"instance_id": "", "name_text": self.localizer.text("ui.effect.none"), "status_text": self.localizer.text("ui.effect.none")}]

    def _relations_for_instance(
        self,
        instance: GemInstance,
        board: SudokuGemBoard,
    ) -> list[dict[str, Any]]:
        return [
            self._relation_view(board, relation)
            for relation in board.relations()
            if instance.instance_id in {relation.source_instance_id, relation.target_instance_id}
        ]

    def _cells_view(self, board: SudokuGemBoard) -> list[list[dict[str, Any]]]:
        runtime_view = board.view()
        rows: list[list[dict[str, Any]]] = []
        for row in range(board.rules.rows):
            row_cells: list[dict[str, Any]] = []
            for column in range(board.rules.columns):
                instance_id = runtime_view.cells.get((row, column))
                instance = board.inventory.require(instance_id) if instance_id else None
                row_cells.append(
                    {
                        "row": row,
                        "column": column,
                        "box": self._box_index(board, row, column),
                        "gem": self._placed_gem_view(instance) if instance else None,
                    }
                )
            rows.append(row_cells)
        return rows

    def _boxes_view(self, board: SudokuGemBoard) -> list[dict[str, Any]]:
        boxes: list[dict[str, Any]] = []
        boxes_per_row = board.rules.columns // board.rules.box_columns
        total_boxes = boxes_per_row * (board.rules.rows // board.rules.box_rows)
        for box_index in range(total_boxes):
            start_row = (box_index // boxes_per_row) * board.rules.box_rows
            start_column = (box_index % boxes_per_row) * board.rules.box_columns
            cells = [
                {"row": row, "column": column}
                for row in range(start_row, start_row + board.rules.box_rows)
                for column in range(start_column, start_column + board.rules.box_columns)
            ]
            boxes.append({"box": box_index, "label_text": f"{box_index + 1}{self.localizer.text('ui.board.box_suffix')}", "cells": cells})
        return boxes

    def _placed_gem_view(self, instance: GemInstance) -> dict[str, Any]:
        definition = self.definitions[instance.base_gem_id]
        return {
            "instance_id": instance.instance_id,
            "name_text": self.localizer.text(definition.name_key),
            "category_text": self._gem_category_text(definition),
            "gem_type": self._gem_type_view(instance.gem_type),
            "rarity_text": self.localizer.text(f"rarity.{instance.rarity}.name"),
            "position": self._position_view(instance.board_position),
        }

    def _position_view(self, position: Any) -> dict[str, int] | None:
        if position is None:
            return None
        return {"row": position.row, "column": position.column}

    def _issue_text(self, issue: BoardIssue) -> str:
        return self.localizer.text(issue.error_key)

    def _highlights_view(
        self,
        highlights: dict[str, dict[int | tuple[int, int], tuple[str, ...]]],
    ) -> dict[str, list[dict[str, Any]]]:
        return {
            relation: [
                {
                    "target": target,
                    "relation_text": self.localizer.text(f"relation.{relation}.name"),
                    "instance_ids": instance_ids,
                }
                for target, instance_ids in entries.items()
            ]
            for relation, entries in highlights.items()
        }

    def _influence_preview(self, board: SudokuGemBoard) -> list[dict[str, Any]]:
        return [self._relation_view(board, relation) for relation in board.relations()]

    def _relation_view(self, board: SudokuGemBoard, relation: GemRelation) -> dict[str, Any]:
        source = board.inventory.require(relation.source_instance_id)
        target = board.inventory.require(relation.target_instance_id)
        return {
            "source": self._placed_gem_view(source),
            "target": self._placed_gem_view(target),
            "relation": relation.relation,
            "relation_text": self.localizer.text(f"relation.{relation.relation}.name"),
        }

    def _modifier_view(self, modifier: AppliedModifier) -> dict[str, Any]:
        return {
            "source_instance_id": modifier.source_instance_id,
            "source_name_text": self.localizer.text(self.definitions[modifier.source_base_gem_id].name_key),
            "target_instance_id": modifier.target_instance_id,
            "stat": self._stat_view(modifier.stat)
            if modifier.stat != "conduit_multiplier"
            else {"id": modifier.stat, "text": self.localizer.text("ui.modifier.conduit_multiplier")},
            "value": modifier.value,
            "layer_text": self.localizer.text(f"ui.modifier.layer.{modifier.layer}"),
            "relation_text": self.localizer.text(f"relation.{modifier.relation}.name")
            if modifier.relation != "self"
            else self.localizer.text("ui.relation.self"),
            "reason_text": self.localizer.text(modifier.reason_key),
            "applied": modifier.applied,
        }

    def _pickup_prompt(self, session: CombatSession, dropped: DroppedGem) -> dict[str, Any]:
        if dropped.picked_up:
            status_key = "ui.pickup.success"
        elif dist(
            (session.player.position.x, session.player.position.y),
            (dropped.position.x, dropped.position.y),
        ) <= session.player.pickup_radius:
            status_key = "ui.pickup.pending"
        else:
            status_key = "ui.pickup.out_of_range"
        return {
            "drop_id": dropped.drop_id,
            "name_text": self.localizer.text(self.definitions[dropped.gem_instance.base_gem_id].name_key),
            "status_text": self.localizer.text(status_key),
        }

    def _box_index(self, board: SudokuGemBoard, row: int, column: int) -> int:
        box_row = row // board.rules.box_rows
        box_column = column // board.rules.box_columns
        boxes_per_row = board.rules.columns // board.rules.box_columns
        return box_row * boxes_per_row + box_column
