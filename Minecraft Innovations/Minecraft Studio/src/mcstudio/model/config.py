"""Mod configuration data model -- typed config entries with validation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConfigEntry:
    """A single configuration entry."""
    key: str
    value_type: str  # "bool", "int", "float", "string"
    default: bool | int | float | str
    comment: str = ""
    min_value: int | float | None = None
    max_value: int | float | None = None

    def __post_init__(self) -> None:
        valid_types = ("bool", "int", "float", "string")
        if self.value_type not in valid_types:
            raise ValueError(f"Invalid value_type: {self.value_type!r}. Must be one of {valid_types}")

    def to_dict(self) -> dict:
        d: dict = {
            "key": self.key,
            "value_type": self.value_type,
            "default": self.default,
        }
        if self.comment:
            d["comment"] = self.comment
        if self.min_value is not None:
            d["min_value"] = self.min_value
        if self.max_value is not None:
            d["max_value"] = self.max_value
        return d

    @classmethod
    def from_dict(cls, data: dict) -> ConfigEntry:
        return cls(
            key=data["key"],
            value_type=data["value_type"],
            default=data["default"],
            comment=data.get("comment", ""),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
        )


@dataclass
class ConfigSection:
    """A named section of configuration entries."""
    name: str
    comment: str = ""
    entries: list[ConfigEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "entries": [e.to_dict() for e in self.entries],
        }
        if self.comment:
            d["comment"] = self.comment
        return d

    @classmethod
    def from_dict(cls, data: dict) -> ConfigSection:
        return cls(
            name=data["name"],
            comment=data.get("comment", ""),
            entries=[ConfigEntry.from_dict(e) for e in data.get("entries", [])],
        )


@dataclass
class ModConfig:
    """Top-level mod configuration."""
    sections: list[ConfigSection] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "sections": [s.to_dict() for s in self.sections],
        }

    @classmethod
    def from_dict(cls, data: dict) -> ModConfig:
        return cls(
            sections=[ConfigSection.from_dict(s) for s in data.get("sections", [])],
        )
