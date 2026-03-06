"""Block definitions for Minecraft mods."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

_BLOCK_ID_RE = re.compile(r"^[a-z][a-z0-9_./-]{0,63}$")


class BlockMaterial(Enum):
    """Block material types affecting mining behavior and sounds."""
    STONE = "stone"
    WOOD = "wood"
    DIRT = "dirt"
    METAL = "metal"
    SAND = "sand"
    WOOL = "wool"
    GLASS = "glass"
    ICE = "ice"
    LEAVES = "leaves"
    PLANT = "plant"
    CORAL = "coral"
    AMETHYST = "amethyst"
    NETHER = "nether"
    SCULK = "sculk"


@dataclass(frozen=True)
class BlockDrop:
    """An item dropped when a block is broken."""
    item_id: str
    count_min: int = 1
    count_max: int = 1
    requires_silk_touch: bool = False

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "count_min": self.count_min,
            "count_max": self.count_max,
            "requires_silk_touch": self.requires_silk_touch,
        }

    @classmethod
    def from_dict(cls, data: dict) -> BlockDrop:
        return cls(**data)


@dataclass
class Block:
    """A custom block definition."""
    block_id: str
    material: BlockMaterial = BlockMaterial.STONE
    hardness: float = 1.5
    resistance: float = 6.0
    requires_tool: bool = False
    luminance: int = 0
    slipperiness: float = 0.6
    no_collision: bool = False
    transparent: bool = False
    drops: list[BlockDrop] = field(default_factory=list)
    has_block_item: bool = True

    def __post_init__(self) -> None:
        if not _BLOCK_ID_RE.match(self.block_id):
            raise ValueError(
                f"Invalid block ID: {self.block_id!r}. Must be lowercase, start with "
                "a letter, and contain only a-z, 0-9, underscore, dot, slash, or hyphen."
            )
        if self.hardness < -1.0:
            raise ValueError(f"Hardness must be >= -1.0, got {self.hardness}")
        if self.resistance < 0:
            raise ValueError(f"Resistance must be >= 0, got {self.resistance}")
        if not (0 <= self.luminance <= 15):
            raise ValueError(f"Luminance must be 0-15, got {self.luminance}")

    @property
    def java_class_name(self) -> str:
        from mcstudio.codegen.java import to_pascal_case
        return to_pascal_case(self.block_id) + "Block"

    @property
    def java_constant(self) -> str:
        return self.block_id.upper()

    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "material": self.material.value,
            "hardness": self.hardness,
            "resistance": self.resistance,
            "requires_tool": self.requires_tool,
            "luminance": self.luminance,
            "slipperiness": self.slipperiness,
            "no_collision": self.no_collision,
            "transparent": self.transparent,
            "drops": [d.to_dict() for d in self.drops],
            "has_block_item": self.has_block_item,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Block:
        drops = [BlockDrop.from_dict(d) for d in data.get("drops", [])]
        return cls(
            block_id=data["block_id"],
            material=BlockMaterial(data.get("material", "stone")),
            hardness=data.get("hardness", 1.5),
            resistance=data.get("resistance", 6.0),
            requires_tool=data.get("requires_tool", False),
            luminance=data.get("luminance", 0),
            slipperiness=data.get("slipperiness", 0.6),
            no_collision=data.get("no_collision", False),
            transparent=data.get("transparent", False),
            drops=drops,
            has_block_item=data.get("has_block_item", True),
        )

    def __repr__(self) -> str:
        return f"Block({self.block_id!r}, material={self.material.value})"
