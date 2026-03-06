"""Entity type definitions for Minecraft mods."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

_ENTITY_ID_RE = re.compile(r"^[a-z][a-z0-9_./-]{0,63}$")


class EntityBase(Enum):
    """Base entity classes available in Minecraft."""
    LIVING_ENTITY = "living_entity"
    MOB = "mob"
    PATH_FINDER_MOB = "path_finder_mob"
    ANIMAL = "animal"
    MONSTER = "monster"
    WATER_ANIMAL = "water_animal"
    FLYING_MOB = "flying_mob"
    TAMABLE_ANIMAL = "tamable_animal"


class MobCategory(Enum):
    """Mob spawn categories."""
    MONSTER = "monster"
    CREATURE = "creature"
    AMBIENT = "ambient"
    AXOLOTLS = "axolotls"
    UNDERGROUND_WATER_CREATURE = "underground_water_creature"
    WATER_CREATURE = "water_creature"
    WATER_AMBIENT = "water_ambient"
    MISC = "misc"


class AIGoalType(Enum):
    """Common AI goal types."""
    FLOAT_SWIM = "float_swim"
    MELEE_ATTACK = "melee_attack"
    RANGED_ATTACK = "ranged_attack"
    WANDER_RANDOMLY = "wander_randomly"
    LOOK_AT_PLAYER = "look_at_player"
    RANDOM_LOOK_AROUND = "random_look_around"
    FLEE_ENTITY = "flee_entity"
    PANIC = "panic"
    BREED = "breed"
    TEMPT = "tempt"
    FOLLOW_PARENT = "follow_parent"
    EAT_BLOCK = "eat_block"
    LEAP_AT_TARGET = "leap_at_target"
    HURT_BY_TARGET = "hurt_by_target"
    NEAREST_ATTACKABLE_TARGET = "nearest_attackable_target"


@dataclass(frozen=True)
class AIGoal:
    """A single AI goal with priority and parameters."""
    goal_type: AIGoalType
    priority: int = 0
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict = {
            "goal_type": self.goal_type.value,
            "priority": self.priority,
        }
        if self.params:
            d["params"] = self.params
        return d

    @classmethod
    def from_dict(cls, data: dict) -> AIGoal:
        return cls(
            goal_type=AIGoalType(data["goal_type"]),
            priority=data.get("priority", 0),
            params=data.get("params", {}),
        )


@dataclass(frozen=True)
class EntityAttribute:
    """An entity attribute override (e.g. max_health=20)."""
    attribute: str  # e.g. "max_health", "movement_speed", "attack_damage"
    value: float

    def to_dict(self) -> dict:
        return {"attribute": self.attribute, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> EntityAttribute:
        return cls(attribute=data["attribute"], value=data["value"])


@dataclass(frozen=True)
class SpawnRules:
    """Entity spawn rules."""
    category: MobCategory = MobCategory.CREATURE
    weight: int = 10
    min_group: int = 1
    max_group: int = 3
    biomes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "weight": self.weight,
            "min_group": self.min_group,
            "max_group": self.max_group,
            "biomes": self.biomes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SpawnRules:
        return cls(
            category=MobCategory(data.get("category", "creature")),
            weight=data.get("weight", 10),
            min_group=data.get("min_group", 1),
            max_group=data.get("max_group", 3),
            biomes=data.get("biomes", []),
        )


@dataclass
class EntityType:
    """A custom entity type definition."""
    entity_id: str
    base_class: EntityBase = EntityBase.MOB
    width: float = 0.6
    height: float = 1.8
    attributes: list[EntityAttribute] = field(default_factory=list)
    goals: list[AIGoal] = field(default_factory=list)
    spawn_rules: SpawnRules | None = None
    loot_table_id: str | None = None
    fireproof: bool = False
    can_swim: bool = True

    def __post_init__(self) -> None:
        if not _ENTITY_ID_RE.match(self.entity_id):
            raise ValueError(
                f"Invalid entity ID: {self.entity_id!r}. Must be lowercase, start with "
                "a letter, and contain only a-z, 0-9, underscore, dot, slash, or hyphen."
            )
        if self.width <= 0:
            raise ValueError(f"Width must be > 0, got {self.width}")
        if self.height <= 0:
            raise ValueError(f"Height must be > 0, got {self.height}")

    @property
    def java_class_name(self) -> str:
        from mcstudio.codegen.java import to_pascal_case
        return to_pascal_case(self.entity_id) + "Entity"

    @property
    def java_constant(self) -> str:
        return self.entity_id.upper()

    def to_dict(self) -> dict:
        d: dict = {
            "entity_id": self.entity_id,
            "base_class": self.base_class.value,
            "width": self.width,
            "height": self.height,
            "attributes": [a.to_dict() for a in self.attributes],
            "goals": [g.to_dict() for g in self.goals],
            "fireproof": self.fireproof,
            "can_swim": self.can_swim,
        }
        if self.spawn_rules:
            d["spawn_rules"] = self.spawn_rules.to_dict()
        if self.loot_table_id:
            d["loot_table_id"] = self.loot_table_id
        return d

    @classmethod
    def from_dict(cls, data: dict) -> EntityType:
        spawn = SpawnRules.from_dict(data["spawn_rules"]) if "spawn_rules" in data else None
        return cls(
            entity_id=data["entity_id"],
            base_class=EntityBase(data.get("base_class", "mob")),
            width=data.get("width", 0.6),
            height=data.get("height", 1.8),
            attributes=[EntityAttribute.from_dict(a) for a in data.get("attributes", [])],
            goals=[AIGoal.from_dict(g) for g in data.get("goals", [])],
            spawn_rules=spawn,
            loot_table_id=data.get("loot_table_id"),
            fireproof=data.get("fireproof", False),
            can_swim=data.get("can_swim", True),
        )

    def __repr__(self) -> str:
        return f"EntityType({self.entity_id!r}, base={self.base_class.value})"
