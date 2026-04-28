from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .affixes import AffixGenerator
from .combat import CombatSession, Monster, Player, Position
from .config import (
    load_affix_definitions,
    load_board_rules,
    load_gem_definitions,
    load_rarity_affix_counts,
    load_relation_coefficients,
    load_skill_scaling_rules,
    load_skill_templates,
)
from .gem_board import SudokuGemBoard
from .inventory import GemInventory, GemInstance
from .loot import LootRuntime
from .presentation import PresentationService
from .skill_effects import FinalSkillInstance, SkillEffectCalculator, SkillEffectError


@dataclass
class V1WebAppApi:
    config_root: Path
    definitions: dict = field(init=False)
    inventory: GemInventory = field(init=False)
    board: SudokuGemBoard = field(init=False)
    presenter: PresentationService = field(init=False)
    combat_session: CombatSession | None = None
    logs: list[str] = field(default_factory=list)
    _loot_seed: int = 6

    def __post_init__(self) -> None:
        self.definitions = load_gem_definitions(self.config_root)
        self.inventory = GemInventory(self.definitions)
        self.board = SudokuGemBoard(load_board_rules(self.config_root), self.inventory)
        self.presenter = PresentationService.from_configs(self.config_root)
        self._seed_inventory()

    def state(self) -> dict[str, Any]:
        final_skills, skill_error = self._final_skills_or_error()
        board_view = self.presenter.board_view(self.board, final_skills=final_skills)
        inventory = [
            self.presenter.gem_detail(instance, board=self.board, final_skills=final_skills)
            for instance in self.inventory.sort_instances("acquired_order")
        ]
        inventory.append(self._test_item_detail())
        drops = []
        if self.combat_session is not None:
            drops = [self.presenter.drop_prompt(drop) for drop in self.combat_session.dropped_gems]
        return {
            "inventory": inventory,
            "board": board_view,
            "skill_preview": [self.presenter.skill_preview(skill) for skill in final_skills],
            "skill_error": skill_error,
            "combat": self.presenter.combat_hud(self.combat_session) if self.combat_session else None,
            "drops": drops,
            "logs": list(self.logs),
            "ui_text": {
                "only_gems_on_board": self.presenter.localizer.text("ui.inventory.only_gems_on_board"),
            },
        }

    def mount(self, instance_id: str, row: int, column: int) -> dict[str, Any]:
        self.board.mount_gem(instance_id, row, column)
        instance = self.inventory.require(instance_id)
        self.logs.append(f"已将{self._gem_name(instance)}放入第{row + 1}行第{column + 1}列。")
        return self.state()

    def unmount(self, instance_id: str) -> dict[str, Any]:
        instance = self.inventory.require(instance_id)
        self.board.unmount_gem(instance_id)
        self.logs.append(f"已将{self._gem_name(instance)}从盘面取下。")
        return self.state()

    def start_combat(self) -> dict[str, Any]:
        session = CombatSession.start(
            player=Player("player_1", current_life=100, max_life=100, position=Position(0, 0), pickup_radius=2),
            monsters=[Monster("monster_1", current_life=5, max_life=5, position=Position(1, 0))],
            inventory=self.inventory,
            skill_effect_calculator=self._calculator(),
            loot_runtime=self._loot_runtime(),
        )
        events = session.tick(1)
        self.combat_session = session
        self.logs.append("开始战斗。")
        for event in events:
            skill_name = self.presenter.localizer.text(self.definitions[event.skill_instance.base_gem_id].name_key)
            killed_text = "击杀怪物" if event.killed else "命中怪物"
            self.logs.append(f"{skill_name}自动释放，造成{event.damage:.2f}伤害，{killed_text}。")
        for dropped in session.dropped_gems:
            self.logs.append(f"掉落宝石：{self._gem_name(dropped.gem_instance)}。")
        return self.state()

    def pickup(self, drop_id: str) -> dict[str, Any]:
        if self.combat_session is None:
            raise ValueError("当前没有可拾取的掉落。")
        target = next((drop for drop in self.combat_session.dropped_gems if drop.drop_id == drop_id), None)
        if target is None:
            raise ValueError("掉落不存在。")
        if target.picked_up:
            raise ValueError("该宝石已经拾取。")
        picked = self.combat_session.pickup_nearby()
        if not picked:
            raise ValueError("没有位于拾取范围内的宝石。")
        for instance in picked:
            self.logs.append(f"已拾取{self._gem_name(instance)}并加入库存。")
        return self.state()

    def _seed_inventory(self) -> None:
        active = self.inventory.add_instance(
            "web_active_fire_bolt",
            "active_fire_bolt",
            rarity="magic",
        )
        self.inventory.add_instance("web_support_fire_mastery", "support_fire_mastery")
        self.inventory.add_instance("web_support_fast_cast", "support_fast_cast")
        self.board.mount_gem(active.instance_id, 0, 0)
        self.logs.append("已准备初始宝石和数独盘。")

    def _final_skills_or_error(self) -> tuple[tuple[FinalSkillInstance, ...], str | None]:
        try:
            return self._calculator().calculate_all(), None
        except SkillEffectError as exc:
            return (), self.presenter.localizer.text(exc.error_key)

    def _calculator(self) -> SkillEffectCalculator:
        affixes = load_affix_definitions(self.config_root)
        return SkillEffectCalculator(
            board=self.board,
            definitions=self.definitions,
            skill_templates=load_skill_templates(self.config_root),
            relation_coefficients=load_relation_coefficients(self.config_root),
            scaling_rules=load_skill_scaling_rules(self.config_root),
            affix_definitions={definition.affix_id: definition for definition in affixes},
        )

    def _loot_runtime(self) -> LootRuntime:
        seed = self._loot_seed
        self._loot_seed += 1
        affixes = load_affix_definitions(self.config_root)
        return LootRuntime.from_configs(
            self.config_root,
            self.definitions,
            {"normal": 1},
            AffixGenerator(affixes, load_rarity_affix_counts(self.config_root), random.Random(seed)),
            rng=random.Random(seed),
        )

    def _gem_name(self, instance: GemInstance) -> str:
        return self.presenter.localizer.text(self.definitions[instance.base_gem_id].name_key)

    def _test_item_detail(self) -> dict[str, Any]:
        name_text = self.presenter.localizer.text("item.test_whetstone.name")
        description_text = self.presenter.localizer.text("item.test_whetstone.description")
        category_text = self.presenter.localizer.text("item.category.normal_item")
        return {
            "instance_id": "web_test_whetstone",
            "item_kind": "ordinary",
            "name_text": name_text,
            "description_text": description_text,
            "category_text": category_text,
            "gem_type": {"id": "", "display_text": category_text, "identity_text": description_text},
            "rarity_text": self.presenter.localizer.text("rarity.normal.name"),
            "level": 1,
            "locked": False,
            "board_position": None,
            "tags": [{"id": "test_item", "text": self.presenter.localizer.text("tag.test_item.name")}],
            "base_effect": {},
            "can_affect": {"summary_text": description_text, "tags_any": [], "tags_all": [], "tags_none": []},
            "current_effective_targets": [],
            "board_relations": [],
            "tooltip_view": {
                "icon_text": name_text[:1],
                "name_text": name_text,
                "subtitle_text": f"{category_text} 路 {self.presenter.localizer.text('rarity.normal.name')}",
                "type_identity_text": description_text,
                "tags": [{"id": "test_item", "text": self.presenter.localizer.text("tag.test_item.name"), "tone": "category"}],
                "sections": {
                    "description": {
                        "title_text": self.presenter.localizer.text("ui.tooltip.section.description"),
                        "lines": [description_text],
                    },
                    "stats": {"title_text": self.presenter.localizer.text("ui.tooltip.section.stats"), "lines": []},
                    "current_targets": {"title_text": self.presenter.localizer.text("ui.tooltip.section.current_targets"), "lines": []},
                    "rules": {
                        "title_text": self.presenter.localizer.text("ui.tooltip.section.rules"),
                        "lines": [self.presenter.localizer.text("ui.inventory.only_gems_on_board")],
                    },
                },
            },
        }


def encode_json(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False).encode("utf-8")
