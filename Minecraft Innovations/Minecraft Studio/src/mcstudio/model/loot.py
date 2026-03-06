"""Loot table definitions for block drops, mob drops, and chest loot."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LootCondition(Enum):
    """Common loot table conditions."""
    SURVIVES_EXPLOSION = "survives_explosion"
    KILLED_BY_PLAYER = "killed_by_player"
    RANDOM_CHANCE = "random_chance"
    MATCH_TOOL = "match_tool"
    SILK_TOUCH = "silk_touch"
    WITHOUT_SILK_TOUCH = "without_silk_touch"


class LootFunction(Enum):
    """Common loot table functions."""
    SET_COUNT = "set_count"
    ENCHANT_RANDOMLY = "enchant_randomly"
    APPLY_BONUS = "apply_bonus"
    EXPLOSION_DECAY = "explosion_decay"
    COPY_NAME = "copy_name"
    FURNACE_SMELT = "furnace_smelt"
    LOOTING_ENCHANT = "looting_enchant"


@dataclass
class LootEntry:
    """A single entry in a loot pool.

    ``condition_params`` maps condition enum values to parameter dicts.
    For example: ``{"random_chance": {"chance": 0.3}}`` or
    ``{"match_tool": {"items": ["minecraft:shears"]}}``.
    """
    item_id: str
    weight: int = 1
    count_min: int = 1
    count_max: int = 1
    conditions: list[LootCondition] = field(default_factory=list)
    functions: list[LootFunction] = field(default_factory=list)
    condition_params: dict[str, dict] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict = {
            "item_id": self.item_id,
            "weight": self.weight,
            "count_min": self.count_min,
            "count_max": self.count_max,
            "conditions": [c.value for c in self.conditions],
            "functions": [f.value for f in self.functions],
        }
        if self.condition_params:
            d["condition_params"] = self.condition_params
        return d

    @classmethod
    def from_dict(cls, data: dict) -> LootEntry:
        return cls(
            item_id=data["item_id"],
            weight=data.get("weight", 1),
            count_min=data.get("count_min", 1),
            count_max=data.get("count_max", 1),
            conditions=[LootCondition(c) for c in data.get("conditions", [])],
            functions=[LootFunction(f) for f in data.get("functions", [])],
            condition_params=data.get("condition_params", {}),
        )


@dataclass
class LootPool:
    """A pool within a loot table."""
    rolls_min: int = 1
    rolls_max: int = 1
    bonus_rolls: float = 0.0
    entries: list[LootEntry] = field(default_factory=list)
    conditions: list[LootCondition] = field(default_factory=list)
    condition_params: dict[str, dict] = field(default_factory=dict)

    def add_entry(self, entry: LootEntry) -> LootEntry:
        self.entries.append(entry)
        return entry

    def to_dict(self) -> dict:
        d: dict = {
            "rolls_min": self.rolls_min,
            "rolls_max": self.rolls_max,
            "bonus_rolls": self.bonus_rolls,
            "entries": [e.to_dict() for e in self.entries],
            "conditions": [c.value for c in self.conditions],
        }
        if self.condition_params:
            d["condition_params"] = self.condition_params
        return d

    @classmethod
    def from_dict(cls, data: dict) -> LootPool:
        return cls(
            rolls_min=data.get("rolls_min", 1),
            rolls_max=data.get("rolls_max", 1),
            bonus_rolls=data.get("bonus_rolls", 0.0),
            entries=[LootEntry.from_dict(e) for e in data.get("entries", [])],
            conditions=[LootCondition(c) for c in data.get("conditions", [])],
            condition_params=data.get("condition_params", {}),
        )


@dataclass
class LootTable:
    """A complete loot table (block drops, mob drops, or chest loot)."""
    table_id: str
    table_type: str = "block"  # block, entity, chest
    pools: list[LootPool] = field(default_factory=list)

    def add_pool(self, pool: LootPool | None = None) -> LootPool:
        if pool is None:
            pool = LootPool()
        self.pools.append(pool)
        return pool

    @classmethod
    def block_self_drop(cls, block_id: str) -> LootTable:
        """Create a standard block self-drop loot table."""
        table = cls(table_id=f"blocks/{block_id}", table_type="block")
        pool = table.add_pool()
        pool.add_entry(LootEntry(
            item_id=block_id,
            conditions=[LootCondition.SURVIVES_EXPLOSION],
        ))
        return table

    def to_dict(self) -> dict:
        return {
            "table_id": self.table_id,
            "table_type": self.table_type,
            "pools": [p.to_dict() for p in self.pools],
        }

    @classmethod
    def from_dict(cls, data: dict) -> LootTable:
        return cls(
            table_id=data["table_id"],
            table_type=data.get("table_type", "block"),
            pools=[LootPool.from_dict(p) for p in data.get("pools", [])],
        )

    def __repr__(self) -> str:
        return f"LootTable({self.table_id!r}, pools={len(self.pools)})"
