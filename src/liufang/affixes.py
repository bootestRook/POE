from __future__ import annotations

import random
from dataclasses import dataclass

from .config import AffixDefinition, GemDefinition
from .inventory import AffixRoll


class AffixGenerationError(ValueError):
    def __init__(self, error_key: str, message: str) -> None:
        super().__init__(message)
        self.error_key = error_key
        self.message = message


@dataclass
class AffixGenerator:
    definitions: list[AffixDefinition]
    rarity_affix_counts: dict[str, int]
    rng: random.Random

    def generate_for_gem(self, gem: GemDefinition, rarity: str) -> tuple[AffixRoll, ...]:
        count = self.rarity_affix_counts[rarity]
        if count == 0:
            return ()

        selected: list[AffixRoll] = []
        used_ids: set[str] = set()
        used_groups: set[str] = set()
        for _ in range(count):
            candidates = [
                definition
                for definition in self.definitions
                if definition.gen in {"prefix", "suffix"}
                and definition.affix_id not in used_ids
                and definition.group not in used_groups
                and self._spawn_weight(definition, gem) > 0
                and self._passes_apply_filter(definition, gem)
            ]
            if not candidates:
                raise AffixGenerationError("affix.error.candidate_shortage", "可用词缀候选不足")
            definition = self._weighted_choice(candidates, gem)
            used_ids.add(definition.affix_id)
            used_groups.add(definition.group)
            selected.append(self._roll(definition))
        return tuple(selected)

    def _passes_apply_filter(self, definition: AffixDefinition, gem: GemDefinition) -> bool:
        if not definition.apply_filter_tags:
            return True
        return bool(definition.apply_filter_tags & gem.tags)

    def _spawn_weight(self, definition: AffixDefinition, gem: GemDefinition) -> int:
        return sum(weight for tag, weight in definition.spawn_weights.items() if tag in gem.tags)

    def _weighted_choice(self, candidates: list[AffixDefinition], gem: GemDefinition) -> AffixDefinition:
        total = sum(self._spawn_weight(candidate, gem) for candidate in candidates)
        pick = self.rng.uniform(0, total)
        current = 0.0
        for candidate in candidates:
            current += self._spawn_weight(candidate, gem)
            if pick <= current:
                return candidate
        return candidates[-1]

    def _roll(self, definition: AffixDefinition) -> AffixRoll:
        minimum, maximum = definition.value_range
        if isinstance(minimum, int) and isinstance(maximum, int):
            value: int | float = self.rng.randint(minimum, maximum)
        else:
            value = self.rng.uniform(float(minimum), float(maximum))
        return AffixRoll(
            affix_id=definition.affix_id,
            stat=definition.stat,
            value=value,
            gen=definition.gen,
            group=definition.group,
        )

