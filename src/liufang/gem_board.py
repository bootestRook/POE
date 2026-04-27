from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .config import BoardRules
from .inventory import BoardPosition, GemInventory, GemInstance

RelationType = Literal["same_row", "same_column", "same_box", "adjacent"]


@dataclass(frozen=True)
class BoardIssue:
    error_key: str
    message: str
    instance_ids: tuple[str, ...] = ()
    positions: tuple[BoardPosition, ...] = ()


@dataclass(frozen=True)
class GemRelation:
    source_instance_id: str
    target_instance_id: str
    relation: RelationType
    source_position: BoardPosition
    target_position: BoardPosition


@dataclass(frozen=True)
class BoardValidation:
    is_valid: bool
    issues: tuple[BoardIssue, ...]
    can_enter_combat: bool
    enter_combat_error_key: str | None = None
    enter_combat_message: str | None = None


@dataclass(frozen=True)
class BoardView:
    cells: dict[tuple[int, int], str]
    relations: tuple[GemRelation, ...]
    highlights: dict[str, dict[int | tuple[int, int], tuple[str, ...]]]
    validation: BoardValidation


@dataclass
class SudokuGemBoard:
    rules: BoardRules
    inventory: GemInventory
    _cells: dict[tuple[int, int], str] = field(default_factory=dict)

    def mount_gem(self, instance_id: str, row: int, column: int) -> BoardView:
        position = BoardPosition(row=row, column=column)
        self._require_position_in_range(position)
        if (row, column) in self._cells:
            raise ValueError("该格子已被占用")

        instance = self.inventory.require(instance_id)
        if instance.board_position is not None:
            raise ValueError("同一个宝石实例不能同时占用多个格子")
        self._require_legal_gem_type(instance)

        self._cells[(row, column)] = instance_id
        self.inventory.set_board_position(instance_id, position)
        return self.view()

    def unmount_gem(self, instance_id: str) -> BoardView:
        instance = self.inventory.require(instance_id)
        position = instance.board_position
        if position is None:
            raise ValueError("宝石未在盘面上")

        self._cells.pop((position.row, position.column), None)
        self.inventory.set_board_position(instance_id, None)
        return self.view()

    def validate(self) -> BoardValidation:
        issues: list[BoardIssue] = []
        mounted = self._mounted_by_instance_id()

        for instance in mounted.values():
            self._append_gem_type_issue(instance, issues)

        self._append_duplicate_issues(mounted, issues)

        can_enter_combat = True
        enter_key: str | None = None
        enter_message: str | None = None
        if not mounted and not self.rules.allow_empty_board_to_enter_combat:
            can_enter_combat = False
            enter_key = "board.enter_combat.empty_board"
            enter_message = "空盘不可进入战斗"
        elif (
            self.rules.require_active_skill_to_enter_combat
            and not any(instance.is_active_skill for instance in mounted.values())
        ):
            can_enter_combat = False
            enter_key = "board.enter_combat.no_active_skill"
            enter_message = "没有主动技能宝石不可进入战斗"

        return BoardValidation(
            is_valid=not issues,
            issues=tuple(issues),
            can_enter_combat=can_enter_combat,
            enter_combat_error_key=enter_key,
            enter_combat_message=enter_message,
        )

    def relations(self) -> tuple[GemRelation, ...]:
        mounted = list(self._mounted_by_instance_id().values())
        relations: list[GemRelation] = []
        for index, source in enumerate(mounted):
            for target in mounted[index + 1 :]:
                source_position = source.board_position
                target_position = target.board_position
                if source_position is None or target_position is None:
                    continue
                for relation in self._relation_types(source_position, target_position):
                    relations.append(
                        GemRelation(
                            source_instance_id=source.instance_id,
                            target_instance_id=target.instance_id,
                            relation=relation,
                            source_position=source_position,
                            target_position=target_position,
                        )
                    )
        return tuple(relations)

    def view(self) -> BoardView:
        relations = self.relations()
        return BoardView(
            cells=dict(self._cells),
            relations=relations,
            highlights=self._highlight_data(relations),
            validation=self.validate(),
        )

    def _require_position_in_range(self, position: BoardPosition) -> None:
        if not (0 <= position.row < self.rules.rows and 0 <= position.column < self.rules.columns):
            raise ValueError("坐标超出数独宝石盘范围")

    def _require_legal_gem_type(self, instance: GemInstance) -> None:
        if instance.gem_type not in self.rules.allowed_gem_types:
            raise ValueError("宝石 gem_type 不合法")

    def _append_gem_type_issue(self, instance: GemInstance, issues: list[BoardIssue]) -> None:
        if instance.board_position is None:
            return
        if instance.gem_type not in self.rules.allowed_gem_types:
            issues.append(
                BoardIssue(
                    error_key="board.invalid_gem_type",
                    message="宝石 gem_type 不合法",
                    instance_ids=(instance.instance_id,),
                    positions=(instance.board_position,),
                )
            )

    def _append_duplicate_issues(
        self,
        mounted: dict[str, GemInstance],
        issues: list[BoardIssue],
    ) -> None:
        groups: dict[tuple[str, int, str], list[GemInstance]] = {}
        for instance in mounted.values():
            position = instance.board_position
            if position is None:
                continue
            box_index = self._box_index(position)
            for scope, value in [
                ("row", position.row),
                ("column", position.column),
                ("box", box_index),
            ]:
                groups.setdefault((scope, value, instance.gem_type), []).append(instance)

        key_by_scope = {
            "row": ("board.duplicate_gem_type.row", "同一行不能出现重复 gem_type"),
            "column": ("board.duplicate_gem_type.column", "同一列不能出现重复 gem_type"),
            "box": ("board.duplicate_gem_type.box", "同一 3x3 宫不能出现重复 gem_type"),
        }
        for (scope, _value, _gem_type), instances in groups.items():
            if len(instances) < 2:
                continue
            error_key, message = key_by_scope[scope]
            issues.append(
                BoardIssue(
                    error_key=error_key,
                    message=message,
                    instance_ids=tuple(instance.instance_id for instance in instances),
                    positions=tuple(instance.board_position for instance in instances if instance.board_position),
                )
            )

    def _mounted_by_instance_id(self) -> dict[str, GemInstance]:
        mounted: dict[str, GemInstance] = {}
        for (_row, _column), instance_id in self._cells.items():
            instance = self.inventory.require(instance_id)
            if instance.board_position is not None:
                mounted[instance_id] = instance
        return mounted

    def _relation_types(self, a: BoardPosition, b: BoardPosition) -> tuple[RelationType, ...]:
        relations: list[RelationType] = []
        if a.row == b.row:
            relations.append("same_row")
        if a.column == b.column:
            relations.append("same_column")
        if self._box_index(a) == self._box_index(b):
            relations.append("same_box")
        if abs(a.row - b.row) + abs(a.column - b.column) == 1:
            relations.append("adjacent")
        return tuple(relations)

    def _box_index(self, position: BoardPosition) -> int:
        box_row = position.row // self.rules.box_rows
        box_column = position.column // self.rules.box_columns
        boxes_per_row = self.rules.columns // self.rules.box_columns
        return box_row * boxes_per_row + box_column

    def _highlight_data(
        self,
        relations: tuple[GemRelation, ...],
    ) -> dict[str, dict[int | tuple[int, int], tuple[str, ...]]]:
        row: dict[int, set[str]] = {}
        column: dict[int, set[str]] = {}
        box: dict[int, set[str]] = {}
        adjacent: dict[tuple[int, int], set[str]] = {}

        for relation in relations:
            source = relation.source_position
            target = relation.target_position
            ids = {relation.source_instance_id, relation.target_instance_id}
            if relation.relation == "same_row":
                row.setdefault(source.row, set()).update(ids)
            elif relation.relation == "same_column":
                column.setdefault(source.column, set()).update(ids)
            elif relation.relation == "same_box":
                box.setdefault(self._box_index(source), set()).update(ids)
            elif relation.relation == "adjacent":
                adjacent.setdefault((source.row, source.column), set()).add(relation.target_instance_id)
                adjacent.setdefault((target.row, target.column), set()).add(relation.source_instance_id)

        return {
            "same_row": {key: tuple(sorted(value)) for key, value in row.items()},
            "same_column": {key: tuple(sorted(value)) for key, value in column.items()},
            "same_box": {key: tuple(sorted(value)) for key, value in box.items()},
            "adjacent": {key: tuple(sorted(value)) for key, value in adjacent.items()},
        }

