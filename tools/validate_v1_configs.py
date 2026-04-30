from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"
sys.path.insert(0, str(ROOT / "src"))

from liufang.config import load_skill_packages

EXPECTED_FILES = [
    "core/id_rules.toml",
    "core/random_rules.toml",
    "player/player_base_stats.toml",
    "player/player_stat_defs.toml",
    "combat/damage_types.toml",
    "combat/hit_rules.toml",
    "combat/status_effects.toml",
    "gems/gem_type_defs.toml",
    "gems/active_skill_gems.toml",
    "gems/passive_skill_gems.toml",
    "gems/support_gems.toml",
    "gems/gem_tag_defs.toml",
    "gems/gem_instance_schema.toml",
    "sudoku_board/board_layout.toml",
    "sudoku_board/placement_rules.toml",
    "sudoku_board/relation_rules.toml",
    "sudoku_board/effect_routing_rules.toml",
    "skills/skill_templates.toml",
    "skills/skill_scaling_rules.toml",
    "affixes/affix_defs.toml",
    "affixes/affix_spawn_rules.toml",
    "affixes/affix_groups.toml",
    "affixes/affix_tiers.toml",
    "loot/gem_drop_pools.toml",
    "loot/drop_weight_rules.toml",
    "localization/zh_cn.toml",
]
EXPECTED_SKILL_PACKAGE_FILES = [
    "skills/schema/skill.schema.json",
    "skills/active/active_fire_bolt/skill.yaml",
    "skills/active/active_ice_shards/skill.yaml",
    "skills/active/active_lightning_chain/skill.yaml",
    "skills/active/active_penetrating_shot/skill.yaml",
    "skills/active/active_frost_nova/skill.yaml",
    "skills/active/active_puncture/skill.yaml",
    "skills/behavior_templates/projectile.yaml",
    "skills/behavior_templates/chain.yaml",
    "skills/behavior_templates/player_nova.yaml",
    "skills/behavior_templates/melee_arc.yaml",
    "skills/behavior_templates/damage_zone.yaml",
]

REQUIRED_STATS = {
    "max_life",
    "current_life",
    "move_speed",
    "skill_slots_active",
    "damage_add_percent",
    "damage_final_percent",
    "attack_speed_add_percent",
    "cast_speed_add_percent",
    "skill_speed_final_percent",
    "cooldown_reduction_percent",
    "added_cooldown_ms",
    "area_add_percent",
    "projectile_count_add",
    "projectile_speed_add_percent",
    "crit_chance_add_percent",
    "crit_damage_add_percent",
    "status_chance_add_percent",
    "physical_damage_add_percent",
    "fire_damage_add_percent",
    "cold_damage_add_percent",
    "lightning_damage_add_percent",
}

FORBIDDEN_V1_STATS = {
    "mana",
    "mana_regen",
    "strength",
    "dexterity",
    "intelligence",
    "armor",
    "evasion",
    "energy_shield",
    "resistance_fire",
    "resistance_cold",
    "resistance_lightning",
}

REQUIRED_TAGS = {
    "gem",
    "active_skill_gem",
    "passive_skill_gem",
    "support_gem",
    "loot_gem",
    "gem_type_1",
    "gem_type_2",
    "gem_type_3",
    "gem_type_4",
    "gem_type_5",
    "gem_type_6",
    "gem_type_7",
    "gem_type_8",
    "gem_type_9",
    "attack",
    "spell",
    "melee",
    "ranged",
    "bow",
    "summon",
    "physical",
    "fire",
    "cold",
    "lightning",
    "projectile",
    "area",
    "chain",
    "pierce",
    "orbit",
    "nova",
    "dot",
    "aura",
    "trap_or_mine",
    "skill_fire_bolt",
    "skill_ice_shards",
    "skill_lightning_chain",
    "skill_frost_nova",
    "skill_puncture",
    "skill_penetrating_shot",
    "skill_lava_orb",
    "skill_fungal_petards",
    "support_damage",
    "support_speed",
    "support_cooldown",
    "support_area",
    "support_projectile",
    "support_crit",
    "support_status",
    "support_level",
    "support_relation",
    "support_conduit",
    "support_shape",
}

REQUIRED_DAMAGE_TYPES = {"physical", "fire", "cold", "lightning"}
REQUIRED_STATUS_EFFECTS = {"burning", "chill", "bleed"}
REQUIRED_BOARD_RELATIONS = {"adjacent", "same_row", "same_column", "same_box"}
REQUIRED_BOARD_LOCALIZATION_KEYS = {
    "board.enter_combat.empty_board",
    "board.enter_combat.no_active_skill",
    "board.invalid_sudoku_digit",
    "board.duplicate_sudoku_digit.row",
    "board.duplicate_sudoku_digit.column",
    "board.duplicate_sudoku_digit.box",
}
REQUIRED_RARITY_COUNTS = {"normal": 0, "magic": 1, "rare": 2}
REQUIRED_AFFIX_GENERATIONS = {"prefix", "suffix", "implicit"}
REQUIRED_AFFIX_CATEGORIES = {
    "skill_numeric",
    "tag_enhancement",
    "board_source",
    "board_target",
    "risk_reward_cost",
}
REQUIRED_BOARD_AFFIX_STATS = {
    "source_power_row",
    "source_power_column",
    "source_power_box",
    "target_power_row",
    "target_power_column",
    "target_power_box",
}
REQUIRED_AFFIX_GROUPS = {
    "damage_scaling",
    "speed_scaling",
    "projectile_scaling",
    "relation_source",
    "relation_target",
    "risk_reward",
}
REQUIRED_LOOT_POOLS = {"gem_basic", "active_skill_gems", "passive_skill_gems", "support_gems"}
REQUIRED_GEM_KINDS = {"active_skill", "passive_skill", "support"}
REQUIRED_PHASE4_LOCALIZATION_KEYS = {
    "rarity.normal.name",
    "rarity.magic.name",
    "rarity.rare.name",
    "affix.error.candidate_shortage",
    "loot.error.empty_pool",
    "loot.error.invalid_entry",
}
REQUIRED_PHASE5_LOCALIZATION_KEYS = {
    "skill_effect.error.invalid_board",
    "skill_effect.error.cannot_enter_combat",
    "skill_effect.error.missing_template",
    "modifier.support_base",
    "modifier.passive_base",
    "modifier.support_to_passive",
    "modifier.self_stat_passive",
    "modifier.conduit_amplifier",
    "modifier.ignored.unknown_affix",
    "modifier.ignored.apply_filter",
    "modifier.ignored.board_power_trace",
    "modifier.ignored.unsupported_stat",
    "modifier.ignored.duplicate_source_target_stat",
}
REQUIRED_PHASE6_LOCALIZATION_KEYS = {
    "combat.error.no_active_skill",
}
REQUIRED_PHASE7_LOCALIZATION_KEYS = {
    "ui.board.valid",
    "ui.board.box_suffix",
    "ui.gem.base_skill_effect",
    "ui.gem.passive_effect",
    "ui.gem.support_effect",
    "ui.gem.affects_self",
    "ui.gem.affects_filtered_targets",
    "ui.gem.affects_active_or_passive",
    "ui.gem.affects_active_targets",
    "ui.gem.self_stat_target",
    "ui.gem.active_target",
    "ui.affix.unknown",
    "ui.affix.gen.prefix",
    "ui.affix.gen.suffix",
    "ui.affix.gen.implicit",
    "ui.effect.active",
    "ui.effect.none",
    "ui.skill.base_damage",
    "ui.skill.final_damage",
    "ui.skill.base_cooldown_ms",
    "ui.skill.final_cooldown_ms",
    "ui.skill.projectile_count",
    "ui.skill.area_multiplier",
    "ui.skill.speed_multiplier",
    "ui.skill.ready",
    "ui.skill.cooldown",
    "ui.hud.player_life",
    "ui.hud.move_speed",
    "ui.hud.elapsed_ms",
    "ui.hud.alive_monsters",
    "ui.drop.picked",
    "ui.drop.not_picked",
    "ui.pickup.success",
    "ui.pickup.pending",
    "ui.pickup.out_of_range",
    "ui.modifier.layer.additive",
    "ui.modifier.layer.final",
    "ui.modifier.layer.ignored",
    "ui.modifier.conduit_multiplier",
    "ui.relation.self",
    *{f"ui.gem_type.{number}.identity" for number in range(1, 10)},
}
REQUIRED_RELATION_COEFFICIENTS = {
    "adjacent": 1.25,
    "same_row": 1.0,
    "same_column": 1.0,
    "same_box": 1.0,
}

REQUIRED_ACTIVE_GEMS = {
    "active_fire_bolt": "skill_fire_bolt",
    "active_ice_shards": "skill_ice_shards",
    "active_lightning_chain": "skill_lightning_chain",
    "active_frost_nova": "skill_frost_nova",
    "active_puncture": "skill_puncture",
    "active_penetrating_shot": "skill_penetrating_shot",
    "active_lava_orb": "skill_lava_orb",
    "active_fungal_petards": "skill_fungal_petards",
}

REQUIRED_SUPPORT_GEMS = {
    "general_skill_modifier": {
        "support_fast_attack",
        "support_fast_cast",
        "support_skill_haste",
        "support_cooldown_focus",
        "support_heavy_impact",
        "support_wide_effect",
        "support_stable_output",
        "support_precision",
    },
    "damage_type_enhancer": {
        "support_physical_mastery",
        "support_fire_mastery",
        "support_cold_mastery",
        "support_lightning_mastery",
    },
    "projectile_area_specialist": {
        "support_extra_projectile",
        "support_shotgun",
        "support_projectile_speed",
        "support_area_magnify",
    },
    "risk_reward": {
        "support_overcharge",
        "support_overkill",
        "support_critical_burst",
    },
    "skill_level": {
        "support_elemental_level",
        "support_attack_spell_level",
        "support_projectile_level",
    },
    "board_conduit": {
        "support_row_conduit",
        "support_column_conduit",
        "support_box_conduit",
    },
    "skill_shape_modifier": {
        "support_fire_bolt_fork",
        "support_fire_bolt_nova",
        "support_fire_bolt_rain",
        "support_fire_bolt_lance",
        "support_fire_bolt_orbit",
        "support_ice_shards_fan",
        "support_ice_shards_storm",
        "support_ice_shards_mirror",
        "support_ice_shards_wall",
        "support_ice_shards_freeze_burst",
        "support_lightning_chain_fork",
        "support_lightning_chain_storm",
        "support_lightning_chain_ball",
        "support_lightning_chain_nova",
        "support_lightning_chain_beam",
        "support_frost_nova_double_ring",
        "support_frost_nova_mist",
        "support_frost_nova_spikes",
        "support_frost_nova_pulse",
        "support_frost_nova_glacier",
        "support_puncture_arc",
        "support_puncture_dash",
        "support_puncture_spin",
        "support_puncture_bleed_burst",
        "support_puncture_shadow_combo",
        "support_penetrating_shot_multi",
        "support_penetrating_shot_blast",
        "support_penetrating_shot_ricochet",
        "support_penetrating_shot_chain",
        "support_penetrating_shot_fan",
        "support_lava_orb_double",
        "support_lava_orb_volcano",
        "support_lava_orb_nova",
        "support_lava_orb_trail",
        "support_lava_orb_gravity",
        "support_fungal_petards_cloud",
        "support_fungal_petards_cluster",
        "support_fungal_petards_chain_burst",
        "support_fungal_petards_decoy",
        "support_fungal_petards_shock_spore",
    },
}
REQUIRED_PASSIVE_GEMS = {
    "passive_fire_focus",
    "passive_vitality",
    "passive_swift_gathering",
}

FORBIDDEN_CONFIG_IDS = {
    "equipment",
    "gear",
    "map",
    "currency",
    "corruption",
    "mana",
    "mana_regen",
    "strength",
    "dexterity",
    "intelligence",
    "armor",
    "evasion",
    "energy_shield",
    "resistance",
    "season",
    "class",
    "profession",
}


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError("TOML root must be a table")
    return data


def items(data: dict[str, Any], table: str) -> list[dict[str, Any]]:
    value = data.get(table, [])
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        nested = value.get("items", [])
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
    return []


def unique_ids(entries: list[dict[str, Any]], label: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for entry in entries:
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            errors.append(f"{label}: entry missing non-empty id")
            continue
        if entry_id in seen:
            errors.append(f"{label}: duplicate id '{entry_id}'")
        seen.add(entry_id)
    return seen


def require_localization(
    entry: dict[str, Any],
    label: str,
    localization: dict[str, str],
    errors: list[str],
) -> None:
    name_key = entry.get("name_key")
    entry_id = entry.get("id", "<unknown>")
    if not isinstance(name_key, str) or not name_key:
        errors.append(f"{label}: '{entry_id}' missing name_key")
        return
    value = localization.get(name_key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: '{entry_id}' missing localization key '{name_key}'")
    if value == entry_id:
        errors.append(f"{label}: '{entry_id}' localization must not expose internal id")


def require_localized_key(
    entry: dict[str, Any],
    key: str,
    label: str,
    localization: dict[str, str],
    errors: list[str],
) -> None:
    entry_id = entry.get("id") or entry.get("template_id") or "<unknown>"
    localization_key = entry.get(key)
    if not isinstance(localization_key, str) or not localization_key:
        errors.append(f"{label}: '{entry_id}' missing {key}")
        return
    value = localization.get(localization_key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: '{entry_id}' missing localization key '{localization_key}'")
    if value == entry_id:
        errors.append(f"{label}: '{entry_id}' localization must not expose internal id")


def check_tags(tag_refs: Any, tag_ids: set[str], context: str, errors: list[str]) -> None:
    if tag_refs is None:
        return
    if not isinstance(tag_refs, list):
        errors.append(f"{context}: tag references must be an array")
        return
    for tag in tag_refs:
        if tag not in tag_ids:
            errors.append(f"{context}: unknown tag '{tag}'")


def check_gem_kind_and_digit(entry: dict[str, Any], expected_kind: str, context: str, errors: list[str]) -> None:
    gem_kind = entry.get("gem_kind")
    if gem_kind != expected_kind:
        errors.append(f"{context}: gem_kind must be '{expected_kind}'")
    if gem_kind not in REQUIRED_GEM_KINDS:
        errors.append(f"{context}: invalid gem_kind '{gem_kind}'")
    sudoku_digit = entry.get("sudoku_digit")
    if not isinstance(sudoku_digit, int) or not 1 <= sudoku_digit <= 9:
        errors.append(f"{context}: sudoku_digit must be an integer from 1 to 9")
    gem_type = entry.get("gem_type")
    if isinstance(gem_type, str) and gem_type.startswith("gem_type_") and isinstance(sudoku_digit, int):
        try:
            legacy_digit = int(gem_type.rsplit("_", 1)[-1])
        except ValueError:
            errors.append(f"{context}: gem_type cannot map to sudoku_digit")
        else:
            if legacy_digit != sudoku_digit:
                errors.append(f"{context}: legacy gem_type and sudoku_digit must match during migration")


def check_no_random_affix_fields(entry: dict[str, Any], context: str, errors: list[str]) -> None:
    forbidden_fields = {"prefix_affixes", "suffix_affixes", "implicit_affixes", "random_affixes"}
    present = sorted(forbidden_fields & set(entry))
    if present:
        errors.append(f"{context}: real gem config must not contain random affix fields: {', '.join(present)}")


def check_forbidden_config_entries(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            check_forbidden_config_entries(nested, f"{path}.{key}", errors)
        return
    if isinstance(value, list):
        for index, nested in enumerate(value):
            check_forbidden_config_entries(nested, f"{path}[{index}]", errors)
        return
    if not isinstance(value, str):
        return

    field_name = path.rsplit(".", 1)[-1]
    if field_name not in {"id", "category", "v1_role", "behavior_type"}:
        return
    lowered = value.lower()
    for forbidden in FORBIDDEN_CONFIG_IDS:
        if forbidden in lowered:
            errors.append(f"{path}: forbidden V1 config entry '{value}' contains '{forbidden}'")


def validate() -> list[str]:
    errors: list[str] = []

    if not CONFIGS.exists():
        return ["configs directory does not exist"]

    for relative in EXPECTED_FILES:
        if not (CONFIGS / relative).is_file():
            errors.append(f"missing required config file: configs/{relative}")
    for relative in EXPECTED_SKILL_PACKAGE_FILES:
        if not (CONFIGS / relative).is_file():
            errors.append(f"missing required skill package file: configs/{relative}")

    for path in CONFIGS.rglob("*.toml"):
        if path.name.startswith("all."):
            errors.append(f"forbidden aggregate config file: {path.relative_to(ROOT)}")

    data: dict[str, dict[str, Any]] = {}
    for relative in EXPECTED_FILES:
        path = CONFIGS / relative
        if not path.exists():
            continue
        try:
            data[relative] = load_toml(path)
        except Exception as exc:
            errors.append(f"invalid TOML in configs/{relative}: {exc}")

    for relative, parsed in data.items():
        check_forbidden_config_entries(parsed, f"configs/{relative}", errors)

    localization = data.get("localization/zh_cn.toml", {}).get("strings", {})
    if not isinstance(localization, dict):
        errors.append("localization/zh_cn.toml: [strings] table is required")
        localization = {}
    try:
        skill_packages = load_skill_packages(CONFIGS)
    except Exception as exc:
        errors.append(f"skill packages: {exc}")
        skill_packages = {}
    expected_skill_packages = {"active_fire_bolt", "active_ice_shards", "active_lightning_chain", "active_penetrating_shot", "active_frost_nova", "active_puncture"}
    if set(skill_packages) != expected_skill_packages:
        errors.append("skill packages must contain active_fire_bolt, active_ice_shards, active_lightning_chain, active_penetrating_shot, active_frost_nova and active_puncture in this apply slice")
    for package_id, package in skill_packages.items():
        display = package.get("display", {})
        presentation = package.get("presentation", {})
        for key_name in ["name_key", "description_key"]:
            localization_key = display.get(key_name) if isinstance(display, dict) else None
            if localization_key not in localization:
                errors.append(f"skill package '{package_id}' missing localization key '{localization_key}'")
        if isinstance(presentation, dict):
            for key_name, localization_key in presentation.items():
                if key_name in {"hit_stop_ms", "camera_shake"}:
                    continue
                if localization_key not in localization:
                    errors.append(
                        f"skill package '{package_id}' presentation.{key_name} missing localization key '{localization_key}'"
                    )

    id_pattern = data.get("core/id_rules.toml", {}).get("id_rules", {}).get(
        "allowed_pattern", "^[a-z][a-z0-9_]*$"
    )
    try:
        compiled_id_pattern = re.compile(str(id_pattern))
    except re.error as exc:
        errors.append(f"core/id_rules.toml: invalid allowed_pattern: {exc}")
        compiled_id_pattern = re.compile(r"^[a-z][a-z0-9_]*$")

    stats = items(data.get("player/player_stat_defs.toml", {}), "stats")
    stat_ids = unique_ids(stats, "player stats", errors)
    missing_stats = sorted(REQUIRED_STATS - stat_ids)
    if missing_stats:
        errors.append(f"player stats missing required ids: {', '.join(missing_stats)}")
    forbidden_stats = sorted(FORBIDDEN_V1_STATS & stat_ids)
    if forbidden_stats:
        errors.append(f"player stats contain V1-forbidden ids: {', '.join(forbidden_stats)}")
    for stat in stats:
        stat_id = stat.get("id")
        if isinstance(stat_id, str) and not compiled_id_pattern.match(stat_id):
            errors.append(f"player stats: id '{stat_id}' does not match id_rules")
        require_localization(stat, "player stats", localization, errors)

    player_base = data.get("player/player_base_stats.toml", {}).get("player_base", {})
    if not isinstance(player_base, dict):
        errors.append("player/player_base_stats.toml: [player_base] table is required")
        player_base = {}
    for stat_id in player_base:
        if stat_id not in stat_ids:
            errors.append(f"player_base: unknown stat '{stat_id}'")

    damage_types = items(data.get("combat/damage_types.toml", {}), "damage_types")
    damage_type_ids = unique_ids(damage_types, "damage types", errors)
    if damage_type_ids != REQUIRED_DAMAGE_TYPES:
        errors.append("damage types must be exactly physical, fire, cold, and lightning")
    for damage_type in damage_types:
        require_localization(damage_type, "damage types", localization, errors)
        require_localized_key(damage_type, "display_name_key", "damage types", localization, errors)

    status_effects = items(data.get("combat/status_effects.toml", {}), "status_effects")
    status_effect_ids = unique_ids(status_effects, "status effects", errors)
    if status_effect_ids != REQUIRED_STATUS_EFFECTS:
        errors.append("status effects must be exactly burning, chill, and bleed")
    for status_effect in status_effects:
        require_localization(status_effect, "status effects", localization, errors)
        require_localized_key(status_effect, "display_name_key", "status effects", localization, errors)
        require_localized_key(status_effect, "description_key", "status effects", localization, errors)
        if status_effect.get("v1_runtime") != "placeholder":
            errors.append(f"status effects: '{status_effect.get('id')}' must remain a V1 placeholder")

    gem_types = items(data.get("gems/gem_type_defs.toml", {}), "gem_types")
    gem_type_ids = unique_ids(gem_types, "gem types", errors)
    expected_gem_types = {f"gem_type_{number}" for number in range(1, 10)}
    if gem_type_ids != expected_gem_types:
        errors.append("gem types must be exactly gem_type_1 through gem_type_9")
    for gem_type in gem_types:
        require_localization(gem_type, "gem types", localization, errors)

    tags = items(data.get("gems/gem_tag_defs.toml", {}), "tags")
    tag_ids = unique_ids(tags, "gem tags", errors)
    missing_tags = sorted(REQUIRED_TAGS - tag_ids)
    extra_required_context = sorted(tag_ids - REQUIRED_TAGS)
    if missing_tags:
        errors.append(f"gem tags missing required ids: {', '.join(missing_tags)}")
    for tag in tags:
        require_localization(tag, "gem tags", localization, errors)
        require_localized_key(tag, "display_name_key", "gem tags", localization, errors)
    for damage_type_id in damage_type_ids:
        if damage_type_id not in tag_ids:
            errors.append(f"damage type '{damage_type_id}' must also exist as a tag")

    placement = data.get("sudoku_board/placement_rules.toml", {}).get("placement", {})
    allowed_gem_types = placement.get("allowed_gem_types", []) if isinstance(placement, dict) else []
    board_layout = data.get("sudoku_board/board_layout.toml", {}).get("board", {})
    if not isinstance(board_layout, dict):
        errors.append("board_layout.toml: [board] table is required")
        board_layout = {}
    if (
        board_layout.get("rows") != 9
        or board_layout.get("columns") != 9
        or board_layout.get("box_rows") != 3
        or board_layout.get("box_columns") != 3
    ):
        errors.append("board layout must be fixed at 9 rows, 9 columns, and 3x3 boxes")
    if not isinstance(placement, dict):
        errors.append("placement_rules.toml: [placement] table is required")
        placement = {}
    if placement.get("allow_empty_board_to_enter_combat") is not False:
        errors.append("placement.allow_empty_board_to_enter_combat must be false")
    if placement.get("require_active_skill_to_enter_combat") is not True:
        errors.append("placement.require_active_skill_to_enter_combat must be true")
    if set(allowed_gem_types) != expected_gem_types:
        errors.append("placement.allowed_gem_types must reference all gem_type_1 through gem_type_9")
    for gem_type in allowed_gem_types:
        if gem_type not in gem_type_ids:
            errors.append(f"placement: unknown gem_type '{gem_type}'")

    relations = items(data.get("sudoku_board/relation_rules.toml", {}), "relations")
    relation_ids = unique_ids(relations, "relations", errors)
    if relation_ids != REQUIRED_BOARD_RELATIONS:
        errors.append("board relations must be exactly adjacent, same_row, same_column, and same_box")
    for relation in relations:
        require_localization(relation, "relations", localization, errors)
        relation_id = str(relation.get("id"))
        if relation_id in REQUIRED_RELATION_COEFFICIENTS:
            actual = float(relation.get("coefficient"))
            expected = REQUIRED_RELATION_COEFFICIENTS[relation_id]
            if actual != expected:
                errors.append(f"relation '{relation_id}' coefficient must be {expected}")
    for required_key in REQUIRED_BOARD_LOCALIZATION_KEYS:
        if required_key not in localization:
            errors.append(f"localization missing board key '{required_key}'")
    for required_key in REQUIRED_PHASE4_LOCALIZATION_KEYS:
        if required_key not in localization:
            errors.append(f"localization missing Phase 4 key '{required_key}'")
    for required_key in REQUIRED_PHASE5_LOCALIZATION_KEYS:
        if required_key not in localization:
            errors.append(f"localization missing Phase 5 key '{required_key}'")
    for required_key in REQUIRED_PHASE6_LOCALIZATION_KEYS:
        if required_key not in localization:
            errors.append(f"localization missing Phase 6 key '{required_key}'")
    for required_key in REQUIRED_PHASE7_LOCALIZATION_KEYS:
        if required_key not in localization:
            errors.append(f"localization missing Phase 7 key '{required_key}'")

    routing_stats = items(data.get("sudoku_board/effect_routing_rules.toml", {}), "routing_stats")
    routing_stat_ids = unique_ids(routing_stats, "routing stats", errors)
    for routing_stat in routing_stats:
        require_localization(routing_stat, "routing stats", localization, errors)

    legal_stat_ids = stat_ids | routing_stat_ids

    affix_groups = items(data.get("affixes/affix_groups.toml", {}), "affix_groups")
    affix_group_ids = unique_ids(affix_groups, "affix groups", errors)
    if affix_group_ids != REQUIRED_AFFIX_GROUPS:
        errors.append("affix groups must exactly cover V1 mutual exclusion groups")
    for group in affix_groups:
        require_localization(group, "affix groups", localization, errors)

    affix_tiers = items(data.get("affixes/affix_tiers.toml", {}), "affix_tiers")
    unique_ids(affix_tiers, "affix tiers", errors)
    for tier in affix_tiers:
        require_localization(tier, "affix tiers", localization, errors)

    skill_templates = items(data.get("skills/skill_templates.toml", {}), "skill_templates")
    skill_template_ids = unique_ids(skill_templates, "skill templates", errors)
    skill_template_ids_from_template_id: set[str] = set()
    for template in skill_templates:
        context = f"skill_templates:{template.get('id', '<unknown>')}"
        template_id = template.get("template_id")
        if not isinstance(template_id, str) or not template_id:
            errors.append(f"{context}: missing template_id")
        elif template_id in skill_template_ids_from_template_id:
            errors.append(f"skill templates: duplicate template_id '{template_id}'")
        else:
            skill_template_ids_from_template_id.add(template_id)
        for required_field in [
            "name_key",
            "damage_type",
            "behavior_type",
            "base_damage",
            "base_cooldown_ms",
            "tags",
            "scaling_stats",
        ]:
            if required_field not in template:
                errors.append(f"{context}: missing {required_field}")
        if template.get("damage_type") not in damage_type_ids:
            errors.append(f"{context}: unknown damage_type '{template.get('damage_type')}'")
        if not isinstance(template.get("base_damage"), (int, float)):
            errors.append(f"{context}: base_damage must be numeric")
        if not isinstance(template.get("base_cooldown_ms"), int) or template.get("base_cooldown_ms", 0) <= 0:
            errors.append(f"{context}: base_cooldown_ms must be a positive integer")
        check_tags(template.get("tags"), tag_ids, context, errors)
        scaling_stats = template.get("scaling_stats", [])
        if not isinstance(scaling_stats, list):
            errors.append(f"{context}: scaling_stats must be an array")
        else:
            for stat in scaling_stats:
                if stat not in stat_ids:
                    errors.append(f"{context}: unknown scaling stat '{stat}'")
        require_localization(template, "skill templates", localization, errors)

    all_skill_template_ids = skill_template_ids | skill_template_ids_from_template_id

    active_gems = items(data.get("gems/active_skill_gems.toml", {}), "active_skill_gems")
    active_gem_ids = unique_ids(active_gems, "active skill gems", errors)
    if active_gem_ids != set(REQUIRED_ACTIVE_GEMS):
        errors.append("active skill gems must match the 8 V1 active gem ids exactly")
    for gem in active_gems:
        context = f"active_skill_gems:{gem.get('id', '<unknown>')}"
        gem_id = gem.get("id")
        check_gem_kind_and_digit(gem, "active_skill", context, errors)
        check_no_random_affix_fields(gem, context, errors)
        if gem.get("gem_type") != "gem_type_1":
            errors.append(f"{context}: active skill gems must use gem_type_1")
        if gem.get("sudoku_digit") != 1:
            errors.append(f"{context}: active skill gems must use sudoku_digit 1")
        tags_value = gem.get("tags")
        check_tags(tags_value, tag_ids, context, errors)
        tags_set = set(tags_value) if isinstance(tags_value, list) else set()
        if "attack" in tags_set and "spell" in tags_set:
            errors.append(f"{context}: active gem cannot be both attack and spell in V1")
        if gem.get("skill_template") not in all_skill_template_ids:
            errors.append(f"{context}: unknown skill_template '{gem.get('skill_template')}'")
        if gem_id in REQUIRED_ACTIVE_GEMS and gem.get("skill_template") != REQUIRED_ACTIVE_GEMS[gem_id]:
            errors.append(f"{context}: expected skill_template '{REQUIRED_ACTIVE_GEMS[gem_id]}'")
        require_localization(gem, "active skill gems", localization, errors)
        require_localized_key(gem, "description_key", "active skill gems", localization, errors)

    passive_gems = items(data.get("gems/passive_skill_gems.toml", {}), "passive_skill_gems")
    passive_gem_ids = unique_ids(passive_gems, "passive skill gems", errors)
    if passive_gem_ids != REQUIRED_PASSIVE_GEMS:
        errors.append("passive skill gems must match the planned V1 Phase 2 passive ids exactly")
    for gem in passive_gems:
        context = f"passive_skill_gems:{gem.get('id', '<unknown>')}"
        check_gem_kind_and_digit(gem, "passive_skill", context, errors)
        check_no_random_affix_fields(gem, context, errors)
        if "skill_template" in gem:
            errors.append(f"{context}: passive skill gems must not declare skill_template")
        if gem.get("gem_type") not in gem_type_ids:
            errors.append(f"{context}: unknown gem_type '{gem.get('gem_type')}'")
        tags_value = gem.get("tags")
        check_tags(tags_value, tag_ids, context, errors)
        tags_set = set(tags_value) if isinstance(tags_value, list) else set()
        if "passive_skill_gem" not in tags_set:
            errors.append(f"{context}: passive skill gems must include passive_skill_gem tag")
        passive_effects = gem.get("passive_effects", [])
        if not isinstance(passive_effects, list) or not passive_effects:
            errors.append(f"{context}: passive skill gem must declare passive_effects")
        else:
            for effect in passive_effects:
                if not isinstance(effect, dict):
                    errors.append(f"{context}: passive_effects entries must be tables")
                    continue
                if effect.get("target") not in {"active_skill", "self_stat"}:
                    errors.append(f"{context}: passive effect target must be active_skill or self_stat")
                stat = effect.get("stat")
                if stat not in legal_stat_ids:
                    errors.append(f"{context}: unknown passive effect stat '{stat}'")
                if not isinstance(effect.get("value"), (int, float)):
                    errors.append(f"{context}: passive effect value must be numeric")
                if effect.get("layer") not in {"additive", "final"}:
                    errors.append(f"{context}: passive effect layer must be additive or final")
        apply_filter = gem.get("apply_filter", {})
        if isinstance(apply_filter, dict):
            target_kinds = apply_filter.get("target_kinds", [])
            if target_kinds:
                for kind in target_kinds:
                    if kind not in REQUIRED_GEM_KINDS - {"support"}:
                        errors.append(f"{context}: invalid passive target kind '{kind}'")
            check_tags(apply_filter.get("tags_any"), tag_ids, context, errors)
            check_tags(apply_filter.get("tags_all"), tag_ids, context, errors)
            check_tags(apply_filter.get("tags_none"), tag_ids, context, errors)
        require_localization(gem, "passive skill gems", localization, errors)
        require_localized_key(gem, "description_key", "passive skill gems", localization, errors)

    support_gems = items(data.get("gems/support_gems.toml", {}), "support_gems")
    support_gem_ids = unique_ids(support_gems, "support gems", errors)
    required_support_ids = set().union(*REQUIRED_SUPPORT_GEMS.values())
    if support_gem_ids != required_support_ids:
        errors.append("support gems must match the planned V1 support gem ids exactly")
    category_counts: dict[str, int] = {}
    for gem in support_gems:
        context = f"support_gems:{gem.get('id', '<unknown>')}"
        category = gem.get("category")
        check_gem_kind_and_digit(gem, "support", context, errors)
        check_no_random_affix_fields(gem, context, errors)
        if isinstance(category, str):
            category_counts[category] = category_counts.get(category, 0) + 1
        if gem.get("gem_type") not in gem_type_ids:
            errors.append(f"{context}: unknown gem_type '{gem.get('gem_type')}'")
        tags_value = gem.get("tags")
        check_tags(tags_value, tag_ids, context, errors)
        apply_filter = gem.get("apply_filter")
        if not isinstance(apply_filter, dict) or not any(
            apply_filter.get(key) for key in ["tags_any", "tags_all", "tags_none"]
        ):
            errors.append(f"{context}: support gem must declare non-empty apply_filter tags")
        elif isinstance(apply_filter, dict):
            target_kinds = apply_filter.get("target_kinds", [])
            if not isinstance(target_kinds, list) or not target_kinds:
                errors.append(f"{context}: support gem must declare apply_filter.target_kinds")
            else:
                for kind in target_kinds:
                    if kind not in {"active_skill", "passive_skill"}:
                        errors.append(f"{context}: support target kind must be active_skill or passive_skill")
            check_tags(apply_filter.get("tags_any"), tag_ids, context, errors)
            check_tags(apply_filter.get("tags_all"), tag_ids, context, errors)
            check_tags(apply_filter.get("tags_none"), tag_ids, context, errors)
        effect_stats = gem.get("effect_stats", [])
        if not isinstance(effect_stats, list) or not effect_stats:
            errors.append(f"{context}: support gem must declare effect_stats")
        elif isinstance(effect_stats, list):
            for stat in effect_stats:
                if stat not in legal_stat_ids:
                    errors.append(f"{context}: unknown effect stat '{stat}'")
        require_localization(gem, "support gems", localization, errors)
        require_localized_key(gem, "description_key", "support gems", localization, errors)

    for category, expected_ids in REQUIRED_SUPPORT_GEMS.items():
        actual_ids = {gem.get("id") for gem in support_gems if gem.get("category") == category}
        if actual_ids != expected_ids:
            errors.append(
                f"support gem category '{category}' must contain {len(expected_ids)} expected ids"
            )

    scaling_rules = data.get("skills/skill_scaling_rules.toml", {})
    stat_layers = scaling_rules.get("stat_layers", {})
    if not isinstance(stat_layers, dict):
        errors.append("skill_scaling_rules.toml: [stat_layers] table is required")
        stat_layers = {}
    for stat, layer in stat_layers.items():
        if stat not in legal_stat_ids:
            errors.append(f"stat_layers: unknown stat '{stat}'")
        if layer not in {"additive", "final"}:
            errors.append(f"stat_layers: stat '{stat}' has invalid layer '{layer}'")

    support_base_modifiers = scaling_rules.get("support_base_modifiers", [])
    if not isinstance(support_base_modifiers, list) or not support_base_modifiers:
        errors.append("support_base_modifiers must be non-empty")
        support_base_modifiers = []
    modifier_support_ids = {entry.get("support_id") for entry in support_base_modifiers}
    missing_modifier_supports = required_support_ids - modifier_support_ids - {
        "support_row_conduit",
        "support_column_conduit",
        "support_box_conduit",
    }
    if missing_modifier_supports:
        errors.append(
            "support_base_modifiers missing support ids: "
            + ", ".join(sorted(str(item) for item in missing_modifier_supports))
        )
    for entry in support_base_modifiers:
        if entry.get("support_id") not in required_support_ids:
            errors.append(f"support_base_modifiers: unknown support_id '{entry.get('support_id')}'")
        if entry.get("stat") not in legal_stat_ids:
            errors.append(f"support_base_modifiers: unknown stat '{entry.get('stat')}'")
        if entry.get("layer") not in {"additive", "final"}:
            errors.append(f"support_base_modifiers: invalid layer '{entry.get('layer')}'")
        if not isinstance(entry.get("value"), (int, float)):
            errors.append("support_base_modifiers: value must be numeric")

    conduit_amplifiers = scaling_rules.get("conduit_amplifiers", [])
    expected_conduits = {
        ("support_row_conduit", "same_row"),
        ("support_column_conduit", "same_column"),
        ("support_box_conduit", "same_box"),
    }
    actual_conduits = {(entry.get("support_id"), entry.get("relation")) for entry in conduit_amplifiers}
    if actual_conduits != expected_conduits:
        errors.append("conduit_amplifiers must cover row, column, and box conduits only")
    for entry in conduit_amplifiers:
        if entry.get("relation") == "adjacent":
            errors.append("conduit_amplifiers must not affect adjacent relation")
        if not isinstance(entry.get("multiplier"), (int, float)) or entry.get("multiplier") <= 1:
            errors.append("conduit_amplifiers multiplier must be greater than 1")

    schema = data.get("gems/gem_instance_schema.toml", {})
    schema_fields = set(schema.get("gem_instance_schema", {}).get("required_fields", []))
    required_instance_fields = {
        "instance_id",
        "base_gem_id",
        "gem_kind",
        "sudoku_digit",
        "gem_type",
        "rarity",
        "level",
        "locked",
        "board_position",
    }
    if not required_instance_fields.issubset(schema_fields):
        errors.append("gem instance schema missing required Phase 2 fields")
    forbidden_instance_fields = {"prefix_affixes", "suffix_affixes", "implicit_affixes", "random_affixes"}
    if forbidden_instance_fields & schema_fields:
        errors.append("gem instance schema must not require random affix fields in Phase 2")
    rarity_counts = schema.get("rarity_affix_counts", {})
    if rarity_counts != REQUIRED_RARITY_COUNTS:
        errors.append("rarity affix counts must be normal=0, magic=1, rare=2")

    affixes = items(data.get("affixes/affix_defs.toml", {}), "affixes")
    affix_ids = unique_ids(affixes, "affixes", errors)
    affix_generations: set[str] = set()
    affix_categories: set[str] = set()
    affix_stats: set[str] = set()
    for affix in affixes:
        context = f"affix_defs:{affix.get('id', '<unknown>')}"
        affix_generations.add(str(affix.get("gen")))
        affix_categories.add(str(affix.get("category")))
        affix_stats.add(str(affix.get("stat")))
        if affix.get("gen") not in REQUIRED_AFFIX_GENERATIONS:
            errors.append(f"{context}: gen must be prefix, suffix, or implicit")
        if affix.get("category") not in REQUIRED_AFFIX_CATEGORIES:
            errors.append(f"{context}: unknown V1 affix category '{affix.get('category')}'")
        if affix.get("stat") not in legal_stat_ids:
            errors.append(f"{context}: unknown stat '{affix.get('stat')}'")
        if affix.get("group") not in affix_group_ids:
            errors.append(f"{context}: unknown affix group '{affix.get('group')}'")
        value_range = affix.get("value_range")
        if (
            not isinstance(value_range, list)
            or len(value_range) != 2
            or not all(isinstance(value, (int, float)) for value in value_range)
            or value_range[0] > value_range[1]
        ):
            errors.append(f"{context}: value_range must be [min, max] with min <= max")
        spawn_tags = affix.get("spawn_tags", [])
        if not isinstance(spawn_tags, list) or not spawn_tags:
            errors.append(f"{context}: spawn_tags must be non-empty")
        else:
            check_tags([entry.get("tag") for entry in spawn_tags], tag_ids, context, errors)
            for entry in spawn_tags:
                if not isinstance(entry.get("weight"), int) or entry.get("weight") <= 0:
                    errors.append(f"{context}: spawn tag weights must be positive integers")
        apply_filter = affix.get("apply_filter", {})
        if isinstance(apply_filter, dict):
            check_tags(apply_filter.get("tags_any"), tag_ids, context, errors)
            check_tags(apply_filter.get("tags_all"), tag_ids, context, errors)
            check_tags(apply_filter.get("tags_none"), tag_ids, context, errors)
        require_localization(affix, "affixes", localization, errors)
        require_localized_key(affix, "description_key", "affixes", localization, errors)
    if not REQUIRED_AFFIX_GENERATIONS.issubset(affix_generations):
        errors.append("affixes must cover prefix, suffix, and implicit")
    if not REQUIRED_AFFIX_CATEGORIES.issubset(affix_categories):
        errors.append("affixes must cover all V1 affix categories")
    if not REQUIRED_BOARD_AFFIX_STATS.issubset(affix_stats):
        errors.append("affixes must cover all V1 board affix directions")

    rarity_weights = data.get("loot/drop_weight_rules.toml", {}).get("rarity_weights", {})
    for rarity in REQUIRED_RARITY_COUNTS:
        if rarity not in rarity_weights:
            errors.append(f"drop_weight_rules: missing rarity weight '{rarity}'")
        elif not isinstance(rarity_weights[rarity], int) or rarity_weights[rarity] <= 0:
            errors.append(f"drop_weight_rules: rarity weight '{rarity}' must be positive")

    drop_pool = data.get("loot/gem_drop_pools.toml", {}).get("drop_pool", {})
    if not isinstance(drop_pool, dict):
        errors.append("gem_drop_pools.toml: [drop_pool.*] tables are required")
        drop_pool = {}
    if set(drop_pool) != REQUIRED_LOOT_POOLS:
        errors.append("drop pools must be exactly gem_basic, active_skill_gems, passive_skill_gems, and support_gems")
    for pool_name, pool in drop_pool.items():
        entries = pool.get("entries", []) if isinstance(pool, dict) else []
        if not isinstance(entries, list) or not entries:
            errors.append(f"drop pool '{pool_name}' must have non-empty entries")
            continue
        for entry in entries:
            has_id = isinstance(entry.get("id"), str)
            has_tag = isinstance(entry.get("tag"), str)
            if has_id == has_tag:
                errors.append(f"drop pool '{pool_name}' entries must reference exactly one id or tag")
            if has_id and entry["id"] not in active_gem_ids | passive_gem_ids | support_gem_ids:
                errors.append(f"drop pool '{pool_name}': unknown gem id '{entry['id']}'")
            if has_tag and entry["tag"] not in tag_ids:
                errors.append(f"drop pool '{pool_name}': unknown tag '{entry['tag']}'")
            if not isinstance(entry.get("weight"), int) or entry.get("weight") <= 0:
                errors.append(f"drop pool '{pool_name}' weights must be positive integers")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("V1 配置校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("V1 配置校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
