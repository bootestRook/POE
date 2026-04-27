from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GemDefinition:
    base_gem_id: str
    gem_type: str
    tags: frozenset[str]
    name_key: str = ""
    description_key: str = ""
    category: str = ""
    effect_stats: tuple[str, ...] = ()
    skill_template_id: str | None = None
    apply_filter_tags_any: frozenset[str] = frozenset()
    apply_filter_tags_all: frozenset[str] = frozenset()
    apply_filter_tags_none: frozenset[str] = frozenset()

    @property
    def is_active_skill(self) -> bool:
        return "active_skill_gem" in self.tags


@dataclass(frozen=True)
class AffixDefinition:
    affix_id: str
    gen: str
    category: str
    stat: str
    value_range: tuple[int | float, int | float]
    group: str
    spawn_weights: dict[str, int]
    apply_filter_tags: frozenset[str]
    name_key: str = ""
    description_key: str = ""


@dataclass(frozen=True)
class BoardRules:
    rows: int
    columns: int
    box_rows: int
    box_columns: int
    allowed_gem_types: frozenset[str]
    require_active_skill_to_enter_combat: bool
    allow_empty_board_to_enter_combat: bool


@dataclass(frozen=True)
class SkillTemplate:
    template_id: str
    tags: frozenset[str]
    base_damage: float
    base_cooldown_ms: int
    name_key: str = ""
    damage_type: str = ""
    behavior_type: str = ""
    scaling_stats: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupportBaseModifier:
    support_id: str
    stat: str
    value: float
    layer: str


@dataclass(frozen=True)
class ConduitAmplifier:
    support_id: str
    relation: str
    multiplier: float


@dataclass(frozen=True)
class SkillScalingRules:
    stat_layers: dict[str, str]
    support_base_modifiers: tuple[SupportBaseModifier, ...]
    conduit_amplifiers: tuple[ConduitAmplifier, ...]


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"TOML root must be a table: {path}")
    return data


def load_localization(config_root: Path) -> dict[str, str]:
    data = load_toml(config_root / "localization" / "zh_cn.toml")
    strings = data.get("strings", {})
    if not isinstance(strings, dict):
        raise ValueError("localization/zh_cn.toml must contain [strings]")
    return {str(key): str(value) for key, value in strings.items()}


def load_board_rules(config_root: Path) -> BoardRules:
    layout = load_toml(config_root / "sudoku_board" / "board_layout.toml")["board"]
    placement = load_toml(config_root / "sudoku_board" / "placement_rules.toml")["placement"]
    return BoardRules(
        rows=int(layout["rows"]),
        columns=int(layout["columns"]),
        box_rows=int(layout["box_rows"]),
        box_columns=int(layout["box_columns"]),
        allowed_gem_types=frozenset(placement["allowed_gem_types"]),
        require_active_skill_to_enter_combat=bool(placement["require_active_skill_to_enter_combat"]),
        allow_empty_board_to_enter_combat=bool(placement["allow_empty_board_to_enter_combat"]),
    )


def load_gem_definitions(config_root: Path) -> dict[str, GemDefinition]:
    definitions: dict[str, GemDefinition] = {}
    for relative, table in [
        (Path("gems") / "active_skill_gems.toml", "active_skill_gems"),
        (Path("gems") / "support_gems.toml", "support_gems"),
    ]:
        data = load_toml(config_root / relative)
        for entry in data.get(table, []):
            base_gem_id = entry["id"]
            apply_filter = entry.get("apply_filter", {})
            definitions[base_gem_id] = GemDefinition(
                base_gem_id=base_gem_id,
                gem_type=entry["gem_type"],
                tags=frozenset(entry["tags"]),
                name_key=entry.get("name_key", ""),
                description_key=entry.get("description_key", ""),
                category=entry.get("category", ""),
                effect_stats=tuple(entry.get("effect_stats", [])),
                skill_template_id=entry.get("skill_template"),
                apply_filter_tags_any=frozenset(apply_filter.get("tags_any", [])),
                apply_filter_tags_all=frozenset(apply_filter.get("tags_all", [])),
                apply_filter_tags_none=frozenset(apply_filter.get("tags_none", [])),
            )
    return definitions


def load_affix_definitions(config_root: Path) -> list[AffixDefinition]:
    data = load_toml(config_root / "affixes" / "affix_defs.toml")
    definitions: list[AffixDefinition] = []
    for entry in data.get("affixes", []):
        value_range = entry["value_range"]
        apply_filter = entry.get("apply_filter", {})
        definitions.append(
            AffixDefinition(
                affix_id=entry["id"],
                gen=entry["gen"],
                category=entry["category"],
                stat=entry["stat"],
                value_range=(value_range[0], value_range[1]),
                group=entry["group"],
                spawn_weights={
                    spawn_entry["tag"]: int(spawn_entry["weight"])
                    for spawn_entry in entry.get("spawn_tags", [])
                },
                apply_filter_tags=frozenset(apply_filter.get("tags_any", [])),
                name_key=entry.get("name_key", ""),
                description_key=entry.get("description_key", ""),
            )
        )
    return definitions


def load_rarity_affix_counts(config_root: Path) -> dict[str, int]:
    data = load_toml(config_root / "gems" / "gem_instance_schema.toml")
    return {key: int(value) for key, value in data["rarity_affix_counts"].items()}


def load_rarity_weights(config_root: Path) -> dict[str, int]:
    data = load_toml(config_root / "loot" / "drop_weight_rules.toml")
    return {key: int(value) for key, value in data["rarity_weights"].items()}


def load_skill_templates(config_root: Path) -> dict[str, SkillTemplate]:
    data = load_toml(config_root / "skills" / "skill_templates.toml")
    templates: dict[str, SkillTemplate] = {}
    for entry in data.get("skill_templates", []):
        template = SkillTemplate(
            template_id=entry["template_id"],
            tags=frozenset(entry["tags"]),
            base_damage=float(entry["base_damage"]),
            base_cooldown_ms=int(entry["base_cooldown_ms"]),
            name_key=entry.get("name_key", ""),
            damage_type=entry.get("damage_type", ""),
            behavior_type=entry.get("behavior_type", ""),
            scaling_stats=tuple(entry.get("scaling_stats", [])),
        )
        templates[template.template_id] = template
    return templates


def load_relation_coefficients(config_root: Path) -> dict[str, float]:
    data = load_toml(config_root / "sudoku_board" / "relation_rules.toml")
    return {entry["id"]: float(entry["coefficient"]) for entry in data.get("relations", [])}


def load_skill_scaling_rules(config_root: Path) -> SkillScalingRules:
    data = load_toml(config_root / "skills" / "skill_scaling_rules.toml")
    return SkillScalingRules(
        stat_layers={key: str(value) for key, value in data.get("stat_layers", {}).items()},
        support_base_modifiers=tuple(
            SupportBaseModifier(
                support_id=entry["support_id"],
                stat=entry["stat"],
                value=float(entry["value"]),
                layer=entry["layer"],
            )
            for entry in data.get("support_base_modifiers", [])
        ),
        conduit_amplifiers=tuple(
            ConduitAmplifier(
                support_id=entry["support_id"],
                relation=entry["relation"],
                multiplier=float(entry["multiplier"]),
            )
            for entry in data.get("conduit_amplifiers", [])
        ),
    )
