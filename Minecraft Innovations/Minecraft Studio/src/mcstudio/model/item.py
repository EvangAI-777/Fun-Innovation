"""Item definitions for Minecraft mods."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

_ITEM_ID_RE = re.compile(r"^[a-z][a-z0-9_./-]{0,63}$")


class CreativeTab(Enum):
    """Creative mode inventory tabs."""
    BUILDING_BLOCKS = "building_blocks"
    COLORED_BLOCKS = "colored_blocks"
    NATURAL_BLOCKS = "natural_blocks"
    FUNCTIONAL_BLOCKS = "functional_blocks"
    REDSTONE_BLOCKS = "redstone_blocks"
    TOOLS_AND_UTILITIES = "tools_and_utilities"
    COMBAT = "combat"
    FOOD_AND_DRINKS = "food_and_drinks"
    INGREDIENTS = "ingredients"
    SPAWN_EGGS = "spawn_eggs"


class ToolTier(Enum):
    """Tool mining tier."""
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    GOLD = "gold"
    DIAMOND = "diamond"
    NETHERITE = "netherite"


@dataclass(frozen=True)
class FoodProperties:
    """Food-related item properties."""
    nutrition: int = 4
    saturation: float = 0.3
    is_meat: bool = False
    can_always_eat: bool = False
    eat_seconds: float = 1.6

    def to_dict(self) -> dict:
        return {
            "nutrition": self.nutrition,
            "saturation": self.saturation,
            "is_meat": self.is_meat,
            "can_always_eat": self.can_always_eat,
            "eat_seconds": self.eat_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> FoodProperties:
        return cls(**data)


@dataclass(frozen=True)
class ToolProperties:
    """Tool-related item properties."""
    tier: ToolTier = ToolTier.IRON
    attack_damage: float = 1.0
    attack_speed: float = -2.8
    durability: int = 250

    def to_dict(self) -> dict:
        return {
            "tier": self.tier.value,
            "attack_damage": self.attack_damage,
            "attack_speed": self.attack_speed,
            "durability": self.durability,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ToolProperties:
        return cls(
            tier=ToolTier(data.get("tier", "iron")),
            attack_damage=data.get("attack_damage", 1.0),
            attack_speed=data.get("attack_speed", -2.8),
            durability=data.get("durability", 250),
        )


@dataclass
class Item:
    """A custom item definition."""
    item_id: str
    max_stack_size: int = 64
    creative_tab: CreativeTab = CreativeTab.INGREDIENTS
    food: FoodProperties | None = None
    tool: ToolProperties | None = None
    fireproof: bool = False
    glint: bool = False

    def __post_init__(self) -> None:
        if not _ITEM_ID_RE.match(self.item_id):
            raise ValueError(
                f"Invalid item ID: {self.item_id!r}. Must be lowercase, start with "
                "a letter, and contain only a-z, 0-9, underscore, dot, slash, or hyphen."
            )
        if not (1 <= self.max_stack_size <= 64):
            raise ValueError(f"Max stack size must be 1-64, got {self.max_stack_size}")

    @property
    def java_constant(self) -> str:
        return self.item_id.upper()

    @property
    def is_food(self) -> bool:
        return self.food is not None

    @property
    def is_tool(self) -> bool:
        return self.tool is not None

    def to_dict(self) -> dict:
        d: dict = {
            "item_id": self.item_id,
            "max_stack_size": self.max_stack_size,
            "creative_tab": self.creative_tab.value,
            "fireproof": self.fireproof,
            "glint": self.glint,
        }
        if self.food:
            d["food"] = self.food.to_dict()
        if self.tool:
            d["tool"] = self.tool.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Item:
        food = FoodProperties.from_dict(data["food"]) if "food" in data else None
        tool = ToolProperties.from_dict(data["tool"]) if "tool" in data else None
        return cls(
            item_id=data["item_id"],
            max_stack_size=data.get("max_stack_size", 64),
            creative_tab=CreativeTab(data.get("creative_tab", "ingredients")),
            food=food,
            tool=tool,
            fireproof=data.get("fireproof", False),
            glint=data.get("glint", False),
        )

    def __repr__(self) -> str:
        extra = ""
        if self.is_food:
            extra += ", food"
        if self.is_tool:
            extra += f", tool={self.tool.tier.value}"
        return f"Item({self.item_id!r}{extra})"
