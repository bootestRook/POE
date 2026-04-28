from __future__ import annotations

from dataclasses import dataclass, field
from math import dist

from .inventory import BoardPosition, GemInstance, GemInventory
from .loot import LootRuntime
from .skill_effects import FinalSkillInstance, SkillEffectCalculator, SkillEffectError
from .skill_runtime import SkillEvent, SkillRuntime


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
    item_interaction_reach: float
    move_speed: float = 1.0


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
    skill_events: tuple[SkillEvent, ...] = ()


@dataclass
class PendingSkillEvent:
    skill: FinalSkillInstance
    event: SkillEvent
    remaining_ms: int


@dataclass
class CombatSession:
    player: Player
    monsters: list[Monster]
    dropped_gems: list[DroppedGem]
    elapsed_ms: int
    active_skill_instances: tuple[FinalSkillInstance, ...]
    inventory: GemInventory
    loot_runtime: LootRuntime
    skill_events: list[SkillEvent] = field(default_factory=list)
    _cooldowns: dict[str, SkillCooldown] = field(default_factory=dict)
    _pending_skill_events: list[PendingSkillEvent] = field(default_factory=list)
    _skill_runtime: SkillRuntime = field(default_factory=SkillRuntime)
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
        skill_effect_calculator.apply_player_stat_contributions(player)

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
        events: list[SkillReleaseEvent] = list(self._consume_pending_skill_events(delta_ms))
        for cooldown in self._cooldowns.values():
            cooldown.remaining_ms = max(0, cooldown.remaining_ms - delta_ms)
            while cooldown.remaining_ms == 0:
                monster = self._first_alive_monster()
                if monster is None:
                    break
                if cooldown.skill.uses_skill_event_pipeline:
                    skill_events = self._skill_runtime.execute(
                        cooldown.skill,
                        source_entity=self.player.player_id,
                        source_position=self.player.position,
                        target_entity=monster.monster_id,
                        target_position=monster.position,
                        timestamp_ms=self.elapsed_ms,
                    )
                    self.skill_events.extend(skill_events)
                    self._queue_pending_skill_events(cooldown.skill, skill_events)
                else:
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

    def _queue_pending_skill_events(
        self,
        skill: FinalSkillInstance,
        skill_events: tuple[SkillEvent, ...],
    ) -> None:
        for event in skill_events:
            if event.delay_ms <= 0:
                continue
            self._pending_skill_events.append(
                PendingSkillEvent(skill=skill, event=event, remaining_ms=event.delay_ms)
            )

    def _consume_pending_skill_events(self, delta_ms: int) -> tuple[SkillReleaseEvent, ...]:
        release_events: list[SkillReleaseEvent] = []
        remaining: list[PendingSkillEvent] = []
        for pending in self._pending_skill_events:
            pending.remaining_ms -= delta_ms
            if pending.remaining_ms > 0:
                remaining.append(pending)
                continue
            if pending.event.type == "damage":
                release_event = self._consume_damage_event(pending.skill, pending.event)
                if release_event is not None:
                    release_events.append(release_event)
        self._pending_skill_events = remaining
        return tuple(release_events)

    def _consume_damage_event(
        self,
        skill: FinalSkillInstance,
        event: SkillEvent,
    ) -> SkillReleaseEvent | None:
        target = self._monster_by_id(event.target_entity)
        if target is None:
            return None
        damage = float(event.amount or 0.0)
        killed = target.take_hit(damage)
        if killed:
            self._drop_from_monster(target)
        related_events = tuple(
            skill_event
            for skill_event in self.skill_events
            if skill_event.skill_instance_id == event.skill_instance_id
            and skill_event.timestamp_ms == event.timestamp_ms
        )
        return SkillReleaseEvent(
            skill_instance=skill,
            monster_id=target.monster_id,
            damage=damage,
            killed=killed,
            skill_events=related_events or (event,),
        )

    def pickup_nearby(self) -> tuple[GemInstance, ...]:
        picked: list[GemInstance] = []
        for dropped in self.dropped_gems:
            if dropped.picked_up:
                continue
            if self._distance(self.player.position, dropped.position) > self.player.item_interaction_reach:
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

    def _monster_by_id(self, monster_id: str) -> Monster | None:
        for monster in self.monsters:
            if monster.monster_id == monster_id:
                return monster
        return None

    def _distance(self, a: Position, b: Position) -> float:
        return dist((a.x, a.y), (b.x, b.y))
