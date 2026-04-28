from __future__ import annotations

import ast
import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

GEM_KINDS = frozenset({"active_skill", "passive_skill", "support"})
ALLOWED_SKILL_BEHAVIOR_TEMPLATES = frozenset(
    {
        "projectile",
        "fan_projectile",
        "chain",
        "player_nova",
        "melee_arc",
        "line_pierce",
        "orbit",
        "delayed_area",
    }
)
LOCALIZATION_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]*$")
SCRIPT_FIELD_NAMES = frozenset(
    {
        "script",
        "scripts",
        "code",
        "expression",
        "expressions",
        "formula",
        "formulas",
        "dsl",
    }
)
SKILL_PACKAGE_REQUIRED_PATHS = (
    ("id",),
    ("version",),
    ("display", "name_key"),
    ("display", "description_key"),
    ("classification", "tags"),
    ("classification", "damage_type"),
    ("classification", "damage_form"),
    ("cast", "mode"),
    ("cast", "target_selector"),
    ("cast", "search_range"),
    ("cast", "cooldown_ms"),
    ("cast", "windup_ms"),
    ("cast", "recovery_ms"),
    ("behavior", "template"),
    ("behavior", "params"),
    ("hit", "base_damage"),
    ("hit", "can_crit"),
    ("hit", "can_apply_status"),
    ("scaling", "additive_stats"),
    ("scaling", "final_stats"),
    ("scaling", "runtime_params"),
    ("presentation", "vfx"),
    ("presentation", "sfx"),
    ("presentation", "floating_text"),
    ("presentation", "screen_feedback"),
    ("preview", "show_fields"),
)
SKILL_PACKAGE_TOP_LEVEL_FIELDS = frozenset(
    {"id", "version", "display", "classification", "cast", "behavior", "hit", "scaling", "presentation", "preview"}
)
SKILL_PACKAGE_FIELD_ALLOWLISTS = {
    "display": frozenset({"name_key", "description_key"}),
    "classification": frozenset({"tags", "damage_type", "damage_form"}),
    "cast": frozenset({"mode", "target_selector", "search_range", "cooldown_ms", "windup_ms", "recovery_ms"}),
    "behavior": frozenset({"template", "params"}),
    "hit": frozenset(
        {
            "base_damage",
            "can_crit",
            "can_apply_status",
            "damage_timing",
            "hit_delay_ms",
            "hit_radius",
            "target_policy",
        }
    ),
    "scaling": frozenset({"additive_stats", "final_stats", "runtime_params"}),
    "presentation": frozenset(
        {
            "vfx",
            "cast_vfx_key",
            "projectile_vfx_key",
            "hit_vfx_key",
            "sfx",
            "floating_text",
            "floating_text_style",
            "screen_feedback",
            "hit_stop_ms",
            "camera_shake",
        }
    ),
    "preview": frozenset({"show_fields"}),
}
ALLOWED_PREVIEW_SHOW_FIELDS = frozenset(
    {
        "final_damage",
        "final_cooldown_ms",
        "projectile_count",
        "speed_multiplier",
        "base_damage",
        "base_cooldown_ms",
        "damage_type",
        "damage_form",
    }
)


@dataclass(frozen=True)
class PassiveEffect:
    stat: str
    value: float
    layer: str
    target: str


@dataclass(frozen=True)
class GemDefinition:
    base_gem_id: str
    gem_type: str
    gem_kind: str
    sudoku_digit: int
    tags: frozenset[str]
    name_key: str = ""
    description_key: str = ""
    category: str = ""
    effect_stats: tuple[str, ...] = ()
    passive_effects: tuple[PassiveEffect, ...] = ()
    skill_template_id: str | None = None
    visual_effect: str = ""
    shape_effect: str = ""
    apply_filter_target_kinds: frozenset[str] = frozenset()
    apply_filter_tags_any: frozenset[str] = frozenset()
    apply_filter_tags_all: frozenset[str] = frozenset()
    apply_filter_tags_none: frozenset[str] = frozenset()

    @property
    def is_active_skill(self) -> bool:
        return self.gem_kind == "active_skill"

    @property
    def is_passive_skill(self) -> bool:
        return self.gem_kind == "passive_skill"

    @property
    def is_support(self) -> bool:
        return self.gem_kind == "support"


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
    allowed_sudoku_digits: frozenset[int]
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
    visual_effect: str = ""
    scaling_stats: tuple[str, ...] = ()
    skill_package_id: str = ""
    skill_package_version: str = ""
    behavior_template: str = ""
    damage_form: str = ""
    cast: dict[str, Any] = field(default_factory=dict)
    hit: dict[str, Any] = field(default_factory=dict)
    runtime_params: dict[str, Any] = field(default_factory=dict)
    presentation_keys: dict[str, str] = field(default_factory=dict)
    preview_show_fields: tuple[str, ...] = ()


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


def load_yaml_file(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, data)]
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError(f"YAML indentation must use two-space levels: {path}:{line_number}")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"YAML indentation is invalid: {path}:{line_number}")
        key, separator, value = line.strip().partition(":")
        if not separator or not key.strip():
            raise ValueError(f"YAML line must be a key/value pair: {path}:{line_number}")
        parent = stack[-1][1]
        key = key.strip()
        value = value.strip()
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_yaml_scalar(value)
    return data


def _parse_yaml_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise ValueError(f"YAML inline arrays must use quoted scalar values: {value}") from exc
        if not isinstance(parsed, list):
            raise ValueError(f"YAML inline array expected: {value}")
        return parsed
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def load_localization(config_root: Path) -> dict[str, str]:
    data = load_toml(config_root / "localization" / "zh_cn.toml")
    strings = data.get("strings", {})
    if not isinstance(strings, dict):
        raise ValueError("localization/zh_cn.toml must contain [strings]")
    return {str(key): str(value) for key, value in strings.items()}


def load_board_rules(config_root: Path) -> BoardRules:
    layout = load_toml(config_root / "sudoku_board" / "board_layout.toml")["board"]
    placement = load_toml(config_root / "sudoku_board" / "placement_rules.toml")["placement"]
    allowed_gem_types = frozenset(placement["allowed_gem_types"])
    return BoardRules(
        rows=int(layout["rows"]),
        columns=int(layout["columns"]),
        box_rows=int(layout["box_rows"]),
        box_columns=int(layout["box_columns"]),
        allowed_gem_types=allowed_gem_types,
        allowed_sudoku_digits=frozenset(_sudoku_digit_from_gem_type(gem_type) for gem_type in allowed_gem_types),
        require_active_skill_to_enter_combat=bool(placement["require_active_skill_to_enter_combat"]),
        allow_empty_board_to_enter_combat=bool(placement["allow_empty_board_to_enter_combat"]),
    )


def load_gem_definitions(config_root: Path) -> dict[str, GemDefinition]:
    definitions: dict[str, GemDefinition] = {}
    for relative, table in [
        (Path("gems") / "active_skill_gems.toml", "active_skill_gems"),
        (Path("gems") / "passive_skill_gems.toml", "passive_skill_gems"),
        (Path("gems") / "support_gems.toml", "support_gems"),
    ]:
        data = load_toml(config_root / relative)
        for entry in data.get(table, []):
            base_gem_id = entry["id"]
            apply_filter = entry.get("apply_filter", {})
            gem_type = entry.get("gem_type") or f"gem_type_{entry.get('sudoku_digit')}"
            gem_kind = _gem_kind_from_entry(entry)
            sudoku_digit = int(entry.get("sudoku_digit", _sudoku_digit_from_gem_type(gem_type)))
            _require_valid_gem_kind(gem_kind, base_gem_id)
            _require_valid_sudoku_digit(sudoku_digit, base_gem_id)
            definitions[base_gem_id] = GemDefinition(
                base_gem_id=base_gem_id,
                gem_type=gem_type,
                gem_kind=gem_kind,
                sudoku_digit=sudoku_digit,
                tags=frozenset(entry["tags"]),
                name_key=entry.get("name_key", ""),
                description_key=entry.get("description_key", ""),
                category=entry.get("category", ""),
                effect_stats=tuple(entry.get("effect_stats", [])),
                passive_effects=tuple(_passive_effects(entry)),
                skill_template_id=entry.get("skill_template"),
                visual_effect=str(entry.get("visual_effect", "")),
                shape_effect=str(entry.get("shape_effect", "")),
                apply_filter_target_kinds=frozenset(apply_filter.get("target_kinds", [])),
                apply_filter_tags_any=frozenset(apply_filter.get("tags_any", [])),
                apply_filter_tags_all=frozenset(apply_filter.get("tags_all", [])),
                apply_filter_tags_none=frozenset(apply_filter.get("tags_none", [])),
            )
    return definitions


def _gem_kind_from_entry(entry: dict[str, Any]) -> str:
    if "gem_kind" in entry:
        return str(entry["gem_kind"])
    tags = set(entry.get("tags", []))
    if "active_skill_gem" in tags:
        return "active_skill"
    if "passive_skill_gem" in tags:
        return "passive_skill"
    if "support_gem" in tags:
        return "support"
    return ""


def _sudoku_digit_from_gem_type(gem_type: str) -> int:
    try:
        return int(str(gem_type).rsplit("_", 1)[-1])
    except ValueError as exc:
        raise ValueError(f"宝石 gem_type 无法映射为数独数字：{gem_type}") from exc


def _require_valid_gem_kind(gem_kind: str, base_gem_id: str) -> None:
    if gem_kind not in GEM_KINDS:
        raise ValueError(f"宝石大类不合法：{base_gem_id}")


def _require_valid_sudoku_digit(sudoku_digit: int, base_gem_id: str) -> None:
    if not 1 <= sudoku_digit <= 9:
        raise ValueError(f"宝石数独数字不合法：{base_gem_id}")


def _passive_effects(entry: dict[str, Any]) -> list[PassiveEffect]:
    effects: list[PassiveEffect] = []
    for effect in entry.get("passive_effects", []):
        effects.append(
            PassiveEffect(
                stat=str(effect["stat"]),
                value=float(effect["value"]),
                layer=str(effect.get("layer", "additive")),
                target=str(effect["target"]),
            )
        )
    return effects


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


def load_skill_schema(config_root: Path) -> dict[str, Any]:
    path = config_root / "skills" / "schema" / "skill.schema.json"
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("skill.schema.json root must be an object")
    return data


def load_behavior_templates(config_root: Path) -> dict[str, dict[str, Any]]:
    template_dir = config_root / "skills" / "behavior_templates"
    templates: dict[str, dict[str, Any]] = {}
    if not template_dir.exists():
        return templates
    for path in sorted(template_dir.glob("*.yaml")):
        template = load_yaml_file(path)
        template_id = str(template.get("id", path.stem))
        if template_id != path.stem:
            raise ValueError(f"behavior template id must match file name: {path}")
        if template_id not in ALLOWED_SKILL_BEHAVIOR_TEMPLATES:
            raise ValueError(f"behavior template is not whitelisted: {template_id}")
        allowed_params = template.get("allowed_params", [])
        if not isinstance(allowed_params, list) or not all(isinstance(item, str) for item in allowed_params):
            raise ValueError(f"behavior template allowed_params must be a string array: {template_id}")
        templates[template_id] = template
    return templates


def load_skill_packages(config_root: Path) -> dict[str, dict[str, Any]]:
    active_dir = config_root / "skills" / "active"
    if not active_dir.exists():
        return {}
    schema = load_skill_schema(config_root)
    behavior_templates = load_behavior_templates(config_root)
    packages: dict[str, dict[str, Any]] = {}
    for path in sorted(active_dir.glob("*/skill.yaml")):
        package = load_yaml_file(path)
        validate_skill_package_data(package, schema, behavior_templates, path)
        package_id = str(package["id"])
        packages[package_id] = package
    return packages


def validate_skill_package_data(
    package: dict[str, Any],
    schema: dict[str, Any],
    behavior_templates: dict[str, dict[str, Any]],
    path: Path | None = None,
) -> None:
    if not isinstance(package, dict):
        raise ValueError("skill package root must be an object")
    _reject_script_fields(package, ())
    _reject_unknown_fields(package, SKILL_PACKAGE_TOP_LEVEL_FIELDS, "root", str(package.get("id", "<unknown>")))
    for required_path in SKILL_PACKAGE_REQUIRED_PATHS:
        if _nested_value(package, required_path) is None:
            raise ValueError(f"skill package missing required field: {'.'.join(required_path)}")

    package_id = _require_string(package["id"], "id")
    if path is not None and path.parent.name != package_id:
        raise ValueError(f"skill package id must match directory name: {path}")
    version = _require_string(package["version"], "version")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ValueError(f"skill package version must use MAJOR.MINOR.PATCH: {package_id}")

    display = _require_mapping(package["display"], "display")
    _reject_unknown_fields(display, SKILL_PACKAGE_FIELD_ALLOWLISTS["display"], "display", package_id)
    _require_localization_key_shape(display["name_key"], "display.name_key")
    _require_localization_key_shape(display["description_key"], "display.description_key")

    classification = _require_mapping(package["classification"], "classification")
    _reject_unknown_fields(classification, SKILL_PACKAGE_FIELD_ALLOWLISTS["classification"], "classification", package_id)
    tags = classification["tags"]
    if not isinstance(tags, list) or not tags or not all(isinstance(tag, str) and tag for tag in tags):
        raise ValueError(f"skill package classification.tags must be a non-empty string array: {package_id}")
    if classification["damage_type"] not in {"physical", "fire", "cold", "lightning"}:
        raise ValueError(f"skill package has invalid damage_type: {package_id}")
    if classification["damage_form"] not in {"attack", "spell", "secondary", "damage_over_time"}:
        raise ValueError(f"skill package has invalid damage_form: {package_id}")

    cast = _require_mapping(package["cast"], "cast")
    _reject_unknown_fields(cast, SKILL_PACKAGE_FIELD_ALLOWLISTS["cast"], "cast", package_id)
    if cast["mode"] not in {"instant", "attack", "spell"}:
        raise ValueError(f"skill package has invalid cast.mode: {package_id}")
    if cast["target_selector"] not in {"nearest_enemy", "target_enemy", "self", "ground"}:
        raise ValueError(f"skill package has invalid cast.target_selector: {package_id}")
    if not _is_number(cast["search_range"]) or cast["search_range"] < 0:
        raise ValueError(f"skill package cast.search_range must be non-negative: {package_id}")
    for field_name in ["cooldown_ms", "windup_ms", "recovery_ms"]:
        if not _is_integer(cast[field_name]) or cast[field_name] < 0:
            raise ValueError(f"skill package cast.{field_name} must be a non-negative integer: {package_id}")

    behavior = _require_mapping(package["behavior"], "behavior")
    _reject_unknown_fields(behavior, SKILL_PACKAGE_FIELD_ALLOWLISTS["behavior"], "behavior", package_id)
    behavior_template = _require_string(behavior["template"], "behavior.template")
    if behavior_template not in ALLOWED_SKILL_BEHAVIOR_TEMPLATES or behavior_template not in behavior_templates:
        raise ValueError(f"skill package behavior.template is not allowed: {package_id}")
    params = _require_mapping(behavior["params"], "behavior.params")
    allowed_params = set(behavior_templates[behavior_template].get("allowed_params", []))
    for param_name, param_value in params.items():
        if param_name not in allowed_params:
            raise ValueError(f"skill package behavior.params has unsupported parameter '{param_name}': {package_id}")
        _validate_behavior_param(
            param_name,
            param_value,
            _require_mapping(behavior_templates[behavior_template].get("param_constraints", {}), "param_constraints").get(param_name, {}),
            package_id,
        )

    hit = _require_mapping(package["hit"], "hit")
    _reject_unknown_fields(hit, SKILL_PACKAGE_FIELD_ALLOWLISTS["hit"], "hit", package_id)
    if not _is_number(hit["base_damage"]) or hit["base_damage"] < 0:
        raise ValueError(f"skill package hit.base_damage must be non-negative: {package_id}")
    if not isinstance(hit["can_crit"], bool) or not isinstance(hit["can_apply_status"], bool):
        raise ValueError(f"skill package hit crit/status fields must be booleans: {package_id}")
    if "damage_timing" in hit and hit["damage_timing"] not in {"on_projectile_hit"}:
        raise ValueError(f"skill package hit.damage_timing is invalid: {package_id}")
    if "hit_delay_ms" in hit and (not _is_integer(hit["hit_delay_ms"]) or hit["hit_delay_ms"] < 0):
        raise ValueError(f"skill package hit.hit_delay_ms must be a non-negative integer: {package_id}")
    if "hit_radius" in hit and (not _is_number(hit["hit_radius"]) or hit["hit_radius"] < 0):
        raise ValueError(f"skill package hit.hit_radius must be non-negative: {package_id}")
    if "target_policy" in hit and hit["target_policy"] not in {"selected_target", "nearest_enemy"}:
        raise ValueError(f"skill package hit.target_policy is invalid: {package_id}")

    scaling = _require_mapping(package["scaling"], "scaling")
    _reject_unknown_fields(scaling, SKILL_PACKAGE_FIELD_ALLOWLISTS["scaling"], "scaling", package_id)
    for field_name in ["additive_stats", "final_stats", "runtime_params"]:
        values = scaling[field_name]
        if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
            raise ValueError(f"skill package scaling.{field_name} must be a string array: {package_id}")

    presentation = _require_mapping(package["presentation"], "presentation")
    _reject_unknown_fields(presentation, SKILL_PACKAGE_FIELD_ALLOWLISTS["presentation"], "presentation", package_id)
    for key in ["vfx", "sfx", "floating_text", "screen_feedback", "cast_vfx_key", "projectile_vfx_key", "hit_vfx_key", "floating_text_style"]:
        if key in presentation:
            _require_localization_key_shape(presentation[key], f"presentation.{key}")
    if "hit_stop_ms" in presentation and (not _is_integer(presentation["hit_stop_ms"]) or presentation["hit_stop_ms"] < 0):
        raise ValueError(f"skill package presentation.hit_stop_ms must be a non-negative integer: {package_id}")
    if "camera_shake" in presentation and (not _is_number(presentation["camera_shake"]) or presentation["camera_shake"] < 0):
        raise ValueError(f"skill package presentation.camera_shake must be non-negative: {package_id}")

    preview = _require_mapping(package["preview"], "preview")
    _reject_unknown_fields(preview, SKILL_PACKAGE_FIELD_ALLOWLISTS["preview"], "preview", package_id)
    show_fields = preview["show_fields"]
    if not isinstance(show_fields, list) or not all(isinstance(item, str) and item for item in show_fields):
        raise ValueError(f"skill package preview.show_fields must be a string array: {package_id}")
    unknown_preview_fields = sorted(set(show_fields) - ALLOWED_PREVIEW_SHOW_FIELDS)
    if unknown_preview_fields:
        raise ValueError(f"skill package preview.show_fields has unknown fields {unknown_preview_fields}: {package_id}")

    # The file is intentionally not executed as JSON Schema here. The checked
    # schema fields are the contract this loader enforces without adding a DSL.
    if "required" not in schema:
        raise ValueError("skill.schema.json must declare root required fields")


def _reject_script_fields(value: Any, path: tuple[str, ...]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key) in SCRIPT_FIELD_NAMES:
                dotted = ".".join(path + (str(key),))
                raise ValueError(f"skill package must not contain script-like field: {dotted}")
            _reject_script_fields(nested, path + (str(key),))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_script_fields(nested, path + (str(index),))


def _reject_unknown_fields(value: dict[str, Any], allowed: frozenset[str], label: str, package_id: str) -> None:
    unknown = sorted(set(str(key) for key in value) - allowed)
    if unknown:
        raise ValueError(f"skill package {label} has unsupported fields {unknown}: {package_id}")


def _validate_behavior_param(param_name: str, param_value: Any, constraint: Any, package_id: str) -> None:
    if not isinstance(constraint, dict):
        constraint = {}
    expected_type = constraint.get("type")
    if expected_type == "integer":
        if not _is_integer(param_value):
            raise ValueError(f"skill package behavior.params.{param_name} must be an integer: {package_id}")
        _validate_minimum(param_name, param_value, constraint, package_id)
        return
    if expected_type == "number":
        if not _is_number(param_value):
            raise ValueError(f"skill package behavior.params.{param_name} must be a number: {package_id}")
        _validate_minimum(param_name, param_value, constraint, package_id)
        return
    if expected_type == "string":
        if not isinstance(param_value, str):
            raise ValueError(f"skill package behavior.params.{param_name} must be a string enum: {package_id}")
        enum_values = constraint.get("enum", [])
        if isinstance(enum_values, list) and enum_values and param_value not in enum_values:
            raise ValueError(f"skill package behavior.params.{param_name} has invalid enum value: {package_id}")
        return
    if expected_type == "object":
        if not isinstance(param_value, dict):
            raise ValueError(f"skill package behavior.params.{param_name} must be an object: {package_id}")
        required = constraint.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in param_value:
                    raise ValueError(f"skill package behavior.params.{param_name} missing field {key}: {package_id}")
        properties = constraint.get("properties", [])
        if isinstance(properties, list):
            _reject_unknown_fields(param_value, frozenset(str(key) for key in properties), f"behavior.params.{param_name}", package_id)
        for key, value in param_value.items():
            if not _is_number(value):
                raise ValueError(f"skill package behavior.params.{param_name}.{key} must be a number: {package_id}")
        return
    if isinstance(param_value, str):
        raise ValueError(f"skill package behavior.params must not contain expression strings: {package_id}.{param_name}")


def _validate_minimum(param_name: str, param_value: int | float, constraint: dict[str, Any], package_id: str) -> None:
    minimum = constraint.get("minimum")
    if isinstance(minimum, (int, float)) and param_value < minimum:
        raise ValueError(f"skill package behavior.params.{param_name} is below minimum {minimum}: {package_id}")
    maximum = constraint.get("maximum")
    if isinstance(maximum, (int, float)) and param_value > maximum:
        raise ValueError(f"skill package behavior.params.{param_name} is above maximum {maximum}: {package_id}")


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _nested_value(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"skill package field must be an object: {label}")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"skill package field must be a non-empty string: {label}")
    return value


def _require_localization_key_shape(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if not LOCALIZATION_KEY_PATTERN.match(text) or "." not in text:
        raise ValueError(f"skill package field must be a localization key: {label}")
    return text


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
            visual_effect=str(entry.get("visual_effect", "")),
            scaling_stats=tuple(entry.get("scaling_stats", [])),
        )
        templates[template.template_id] = template
    for package in load_skill_packages(config_root).values():
        template = _skill_template_from_package(package)
        templates[template.template_id] = template
    return templates


def _skill_template_from_package(package: dict[str, Any]) -> SkillTemplate:
    package_id = str(package["id"])
    classification = package["classification"]
    cast = dict(package["cast"])
    behavior = package["behavior"]
    hit = dict(package["hit"])
    scaling = package["scaling"]
    presentation = package["presentation"]
    runtime_params = dict(behavior["params"])
    template_id = _legacy_template_id_from_package_id(package_id)
    return SkillTemplate(
        template_id=template_id,
        tags=frozenset(str(tag) for tag in classification["tags"]),
        base_damage=float(hit["base_damage"]),
        base_cooldown_ms=int(cast["cooldown_ms"]),
        name_key=str(package["display"]["name_key"]),
        damage_type=str(classification["damage_type"]),
        behavior_type=str(behavior["template"]),
        visual_effect=str(presentation["vfx"]),
        scaling_stats=tuple(
            str(stat)
            for stat in (
                list(scaling["additive_stats"])
                + list(scaling["final_stats"])
                + list(scaling["runtime_params"])
            )
        ),
        skill_package_id=package_id,
        skill_package_version=str(package["version"]),
        behavior_template=str(behavior["template"]),
        damage_form=str(classification["damage_form"]),
        cast=cast,
        hit=hit,
        runtime_params=runtime_params,
        presentation_keys={key: str(value) for key, value in presentation.items()},
        preview_show_fields=tuple(str(field) for field in package["preview"]["show_fields"]),
    )


def _legacy_template_id_from_package_id(package_id: str) -> str:
    if package_id.startswith("active_"):
        return f"skill_{package_id[len('active_'):]}"
    return package_id


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
