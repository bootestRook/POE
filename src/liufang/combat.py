from __future__ import annotations

from dataclasses import dataclass, field
from math import dist

from .inventory import BoardPosition, GemInstance, GemInventory
from .loot import LootRuntime
from .skill_effects import FinalSkillInstance, SkillEffectCalculator, SkillEffectError


class CombatStartError(ValueError):
    def __init__(self, error_key: str, message: str) -> None:
        super().__init__(message)
        self.error_key = error_key
        self.message = message


@dataclass(frozen=True)
class Position:
    x: float
    y: float


@dataclass
class Player:
    player_id: str
    current_life: float
    max_life: float
    position: Position
    pickup_radius: float


@dataclass
class Monster:
    monster_id: str
    current_life: float
    max_life: float
    position: Position
    is_alive: bool = True

    def take_hit(self, damage: float) -> bool:
        if not self.is_alive:
            return False
        self.current_life = max(0.0, self.current_life - damage)
        if self.current_life <= 0:
            self.is_alive = False
            return True
        return False


@dataclass
class DroppedGem:
    drop_id: str
    gem_instance: GemInstance
    position: Position
    picked_up: bool = False


@dataclass
class SkillCooldown:
    skill: FinalSkillInstance
    remaining_ms: int = 0


@dataclass
class SkillReleaseEvent:
    skill_instance: FinalSkillInstance
    monster_id: str
    damage: float
    killed: bool


@dataclass
class CombatSession:
    player: Player
    monsters: list[Monster]
    dropped_gems: list[DroppedGem]
    elapsed_ms: int
    active_skill_instances: tuple[FinalSkillInstance, ...]
    inventory: GemInventory
    loot_runtime: LootRuntime
    _cooldowns: dict[str, SkillCooldown] = field(default_factory=dict)
    _next_drop_number: int = 1

    @classmethod
    def start(
        cls,
        *,
        player: Player,
        monsters: list[Monster],
        inventory: GemInventory,
        skill_effect_calculator: SkillEffectCalculator,
        loot_runtime: LootRuntime,
    ) -> "CombatSession":
        try:
            active_skill_instances = skill_effect_calculator.calculate_all()
        except SkillEffectError as exc:
            raise CombatStartError(exc.error_key, exc.message) from exc
        if not active_skill_instances:
            raise CombatStartError("combat.error.no_active_skill", "没有主动技能宝石不可进入战斗")

        session = cls(
            player=player,
            monsters=monsters,
            dropped_gems=[],
            elapsed_ms=0,
            active_skill_instances=active_skill_instances,
            inventory=inventory,
            loot_runtime=loot_runtime,
        )
        session._cooldowns = {
            skill.active_gem_instance_id: SkillCooldown(skill=skill, remaining_ms=0)
            for skill in active_skill_instances
        }
        return session

    def tick(self, delta_ms: int) -> tuple[SkillReleaseEvent, ...]:
        self.elapsed_ms += delta_ms
        events: list[SkillReleaseEvent] = []
        for cooldown in self._cooldowns.values():
            cooldown.remaining_ms = max(0, cooldown.remaining_ms - delta_ms)
            while cooldown.remaining_ms == 0:
                monster = self._first_alive_monster()
                if monster is None:
                    break
                killed = monster.take_hit(cooldown.skill.final_damage)
                event = SkillReleaseEvent(
                    skill_instance=cooldown.skill,
                    monster_id=monster.monster_id,
                    damage=cooldown.skill.final_damage,
                    killed=killed,
                )
                events.append(event)
                if killed:
                    self._drop_from_monster(monster)
                cooldown.remaining_ms = max(1, cooldown.skill.final_cooldown_ms)
        return tuple(events)

    def pickup_nearby(self) -> tuple[GemInstance, ...]:
        picked: list[GemInstance] = []
        for dropped in self.dropped_gems:
            if dropped.picked_up:
                continue
            if self._distance(self.player.position, dropped.position) > self.player.pickup_radius:
                continue
            stored = self.loot_runtime.pickup(dropped.gem_instance, self.inventory)
            dropped.picked_up = True
            picked.append(stored)
        return tuple(picked)

    def _drop_from_monster(self, monster: Monster) -> DroppedGem:
        dropped = DroppedGem(
            drop_id=f"drop_{self._next_drop_number:06d}",
            gem_instance=self.loot_runtime.generate_drop(),
            position=monster.position,
            picked_up=False,
        )
        self._next_drop_number += 1
        self.dropped_gems.append(dropped)
        return dropped

    def _first_alive_monster(self) -> Monster | None:
        for monster in self.monsters:
            if monster.is_alive:
                return monster
        return None

    def _distance(self, a: Position, b: Position) -> float:
        return dist((a.x, a.y), (b.x, b.y))
