from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from .affixes import AffixGenerator
from .config import GemDefinition, load_toml
from .inventory import GemInstance, GemInventory


class LootGenerationError(ValueError):
    def __init__(self, error_key: str, message: str) -> None:
        super().__init__(message)
        self.error_key = error_key
        self.message = message


@dataclass(frozen=True)
class DropEntry:
    weight: int
    base_gem_id: str | None = None
    tag: str | None = None


class LootRuntime:
    def __init__(
        self,
        definitions: dict[str, GemDefinition],
        drop_pools: dict[str, list[DropEntry]],
        rarity_weights: dict[str, int],
        affix_generator: AffixGenerator,
        rng: random.Random | None = None,
    ) -> None:
        self._definitions = definitions
        self._drop_pools = drop_pools
        self._rarity_weights = rarity_weights
        self._affix_generator = affix_generator
        self._rng = rng or random.Random()
        self._next_instance_number = 1

    @classmethod
    def from_configs(
        cls,
        config_root: Path,
        definitions: dict[str, GemDefinition],
        rarity_weights: dict[str, int],
        affix_generator: AffixGenerator,
        rng: random.Random | None = None,
    ) -> "LootRuntime":
        pools_data = load_toml(config_root / "loot" / "gem_drop_pools.toml")
        pools: dict[str, list[DropEntry]] = {}
        for pool_name, pool_data in pools_data.get("drop_pool", {}).items():
            entries: list[DropEntry] = []
            for entry in pool_data.get("entries", []):
                entries.append(
                    DropEntry(
                        weight=int(entry["weight"]),
                        base_gem_id=entry.get("id"),
                        tag=entry.get("tag"),
                    )
                )
            pools[pool_name] = entries
        return cls(definitions, pools, rarity_weights, affix_generator, rng=rng)

    def generate_drop(self) -> GemInstance:
        base_gem_id = self._choose_base_gem_id()
        rarity = self._weighted_key(self._rarity_weights)
        definition = self._definitions[base_gem_id]
        instance = GemInstance(
            instance_id=self._next_instance_id(),
            base_gem_id=base_gem_id,
            gem_type=definition.gem_type,
            rarity=rarity,
            level=1,
            locked=False,
            tags=definition.tags,
            board_position=None,
        )
        return instance

    def pickup(self, instance: GemInstance, inventory: GemInventory) -> GemInstance:
        return inventory.add_existing_instance(instance)

    def _choose_base_gem_id(self) -> str:
        top_entry = self._weighted_entry(self._require_pool("gem_basic"))
        if top_entry.tag == "active_skill_gem":
            return self._choose_from_pool("active_skill_gems")
        if top_entry.tag == "support_gem":
            return self._choose_from_pool("support_gems")
        if top_entry.base_gem_id:
            return top_entry.base_gem_id
        raise LootGenerationError("loot.error.invalid_entry", "掉落池配置不合法")

    def _choose_from_pool(self, pool_name: str) -> str:
        entry = self._weighted_entry(self._require_pool(pool_name))
        if entry.base_gem_id is not None:
            if entry.base_gem_id not in self._definitions:
                raise LootGenerationError("loot.error.invalid_entry", "掉落池配置不合法")
            return entry.base_gem_id
        if entry.tag is None:
            raise LootGenerationError("loot.error.invalid_entry", "掉落池配置不合法")
        candidates = [
            definition.base_gem_id
            for definition in self._definitions.values()
            if entry.tag in definition.tags
        ]
        if not candidates:
            raise LootGenerationError("loot.error.empty_pool", "掉落池为空")
        return candidates[self._rng.randrange(len(candidates))]

    def _require_pool(self, pool_name: str) -> list[DropEntry]:
        entries = self._drop_pools.get(pool_name, [])
        if not entries:
            raise LootGenerationError("loot.error.empty_pool", "掉落池为空")
        return entries

    def _weighted_entry(self, entries: list[DropEntry]) -> DropEntry:
        total = sum(entry.weight for entry in entries)
        if total <= 0:
            raise LootGenerationError("loot.error.invalid_entry", "掉落池配置不合法")
        pick = self._rng.uniform(0, total)
        current = 0.0
        for entry in entries:
            current += entry.weight
            if pick <= current:
                return entry
        return entries[-1]

    def _weighted_key(self, weights: dict[str, int]) -> str:
        total = sum(weights.values())
        pick = self._rng.uniform(0, total)
        current = 0.0
        for key, weight in weights.items():
            current += weight
            if pick <= current:
                return key
        return next(reversed(weights))

    def _next_instance_id(self) -> str:
        instance_id = f"gem_inst_{self._next_instance_number:06d}"
        self._next_instance_number += 1
        return instance_id
