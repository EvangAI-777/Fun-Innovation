"""Advancement data model -- custom advancements for mod content."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class AdvancementFrame(Enum):
    """Display frame style for advancement icons."""
    TASK = "task"
    GOAL = "goal"
    CHALLENGE = "challenge"


# Common trigger type constants
INVENTORY_CHANGED = "minecraft:inventory_changed"
PLACED_BLOCK = "minecraft:placed_block"
KILLED_ENTITY = "minecraft:killed_entity"
ENTER_BIOME = "minecraft:location"
IMPOSSIBLE = "minecraft:impossible"
TICK = "minecraft:tick"
CONSUME_ITEM = "minecraft:consume_item"


@dataclass
class AdvancementCriterion:
    """A single criterion within an advancement."""
    name: str
    trigger: str
    conditions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "trigger": self.trigger,
            "conditions": self.conditions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AdvancementCriterion:
        return cls(
            name=data["name"],
            trigger=data["trigger"],
            conditions=data.get("conditions", {}),
        )


@dataclass
class AdvancementDisplay:
    """Display information for an advancement."""
    icon: str  # Item ID, e.g. "minecraft:diamond" or "mymod:magic_ore"
    title: str
    description: str
    frame: AdvancementFrame = AdvancementFrame.TASK
    show_toast: bool = True
    announce_to_chat: bool = True
    hidden: bool = False

    def to_dict(self) -> dict:
        return {
            "icon": self.icon,
            "title": self.title,
            "description": self.description,
            "frame": self.frame.value,
            "show_toast": self.show_toast,
            "announce_to_chat": self.announce_to_chat,
            "hidden": self.hidden,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AdvancementDisplay:
        return cls(
            icon=data["icon"],
            title=data["title"],
            description=data["description"],
            frame=AdvancementFrame(data.get("frame", "task")),
            show_toast=data.get("show_toast", True),
            announce_to_chat=data.get("announce_to_chat", True),
            hidden=data.get("hidden", False),
        )


def _validate_advancement_id(advancement_id: str) -> str:
    if not re.match(r"^[a-z][a-z0-9_/]{0,127}$", advancement_id):
        raise ValueError(
            f"Invalid advancement ID: {advancement_id!r}. "
            "Must be lowercase, start with a letter, contain only a-z, 0-9, underscore, slash."
        )
    return advancement_id


@dataclass
class Advancement:
    """A Minecraft advancement."""
    advancement_id: str
    display: AdvancementDisplay
    parent: str | None = None  # None = root advancement
    criteria: list[AdvancementCriterion] = field(default_factory=list)
    requirements: list[list[str]] | None = None  # None = all criteria required (AND)

    def __post_init__(self) -> None:
        self.advancement_id = _validate_advancement_id(self.advancement_id)

    def to_dict(self) -> dict:
        d: dict = {
            "advancement_id": self.advancement_id,
            "display": self.display.to_dict(),
            "criteria": [c.to_dict() for c in self.criteria],
        }
        if self.parent is not None:
            d["parent"] = self.parent
        if self.requirements is not None:
            d["requirements"] = self.requirements
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Advancement:
        return cls(
            advancement_id=data["advancement_id"],
            display=AdvancementDisplay.from_dict(data["display"]),
            parent=data.get("parent"),
            criteria=[AdvancementCriterion.from_dict(c) for c in data.get("criteria", [])],
            requirements=data.get("requirements"),
        )

    def to_json(self, mod_id: str) -> dict:
        """Convert to Minecraft advancement JSON format."""
        result: dict = {}

        if self.parent:
            result["parent"] = self.parent if ":" in self.parent else f"{mod_id}:{self.parent}"

        result["display"] = {
            "icon": {"id": self.display.icon},
            "title": {"translate": f"advancement.{mod_id}.{self.advancement_id}.title"},
            "description": {"translate": f"advancement.{mod_id}.{self.advancement_id}.description"},
            "frame": self.display.frame.value,
            "show_toast": self.display.show_toast,
            "announce_to_chat": self.display.announce_to_chat,
            "hidden": self.display.hidden,
        }

        criteria_json = {}
        for criterion in self.criteria:
            entry: dict = {"trigger": criterion.trigger}
            if criterion.conditions:
                entry["conditions"] = criterion.conditions
            criteria_json[criterion.name] = entry
        result["criteria"] = criteria_json

        if self.requirements is not None:
            result["requirements"] = self.requirements

        return result
