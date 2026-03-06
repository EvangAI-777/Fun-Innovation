"""World generation definitions -- biomes and features for Minecraft mods."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

_BIOME_ID_RE = re.compile(r"^[a-z][a-z0-9_./-]{0,63}$")


class FeatureType(Enum):
    """Common world generation feature types."""
    ORE = "ore"
    TREE = "tree"
    FLOWER = "flower"
    VEGETATION_PATCH = "vegetation_patch"
    LAKE = "lake"
    SPRING = "spring"
    GEODE = "geode"
    FOSSIL = "fossil"
    DISK = "disk"
    ICEBERG = "iceberg"
    RANDOM_PATCH = "random_patch"


class HeightRangeType(Enum):
    """Height range distribution types for feature placement."""
    UNIFORM = "uniform"
    TRIANGLE = "triangle"
    TRAPEZOID = "trapezoid"


@dataclass(frozen=True)
class PlacementConfig:
    """Feature placement configuration."""
    count: int = 8
    height_min: int = -64
    height_max: int = 320
    height_range_type: HeightRangeType = HeightRangeType.UNIFORM
    rarity: int | None = None  # 1/N chance per chunk, None = always

    def to_dict(self) -> dict:
        d: dict = {
            "count": self.count,
            "height_min": self.height_min,
            "height_max": self.height_max,
            "height_range_type": self.height_range_type.value,
        }
        if self.rarity is not None:
            d["rarity"] = self.rarity
        return d

    @classmethod
    def from_dict(cls, data: dict) -> PlacementConfig:
        return cls(
            count=data.get("count", 8),
            height_min=data.get("height_min", -64),
            height_max=data.get("height_max", 320),
            height_range_type=HeightRangeType(data.get("height_range_type", "uniform")),
            rarity=data.get("rarity"),
        )


@dataclass
class PlacedFeature:
    """A placed feature definition (what + where)."""
    feature_id: str
    feature_type: FeatureType = FeatureType.ORE
    block: str = "minecraft:iron_ore"
    size: int = 9  # vein size for ores, radius for patches, etc.
    placement: PlacementConfig = field(default_factory=PlacementConfig)

    def to_dict(self) -> dict:
        return {
            "feature_id": self.feature_id,
            "feature_type": self.feature_type.value,
            "block": self.block,
            "size": self.size,
            "placement": self.placement.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> PlacedFeature:
        return cls(
            feature_id=data["feature_id"],
            feature_type=FeatureType(data.get("feature_type", "ore")),
            block=data.get("block", "minecraft:iron_ore"),
            size=data.get("size", 9),
            placement=PlacementConfig.from_dict(data.get("placement", {})),
        )


@dataclass
class Biome:
    """A custom biome definition with climate parameters and features."""
    biome_id: str

    # Climate parameters (Minecraft multi-noise biome source)
    temperature: float = 0.5
    humidity: float = 0.5
    continentalness: float = 0.0
    erosion: float = 0.0
    depth: float = 0.0
    weirdness: float = 0.0

    # Visual properties
    sky_color: str = "#78A7FF"
    fog_color: str = "#C0D8FF"
    water_color: str = "#3F76E4"
    water_fog_color: str = "#050533"
    grass_color: str | None = None  # None = use default for temperature
    foliage_color: str | None = None

    # Features placed in this biome
    features: list[PlacedFeature] = field(default_factory=list)

    # Mob spawns (category -> list of entity IDs with weights)
    spawn_costs: dict[str, dict] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not _BIOME_ID_RE.match(self.biome_id):
            raise ValueError(
                f"Invalid biome ID: {self.biome_id!r}. Must be lowercase, start with "
                "a letter, and contain only a-z, 0-9, underscore, dot, slash, or hyphen."
            )

    def to_dict(self) -> dict:
        d: dict = {
            "biome_id": self.biome_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "continentalness": self.continentalness,
            "erosion": self.erosion,
            "depth": self.depth,
            "weirdness": self.weirdness,
            "sky_color": self.sky_color,
            "fog_color": self.fog_color,
            "water_color": self.water_color,
            "water_fog_color": self.water_fog_color,
            "features": [f.to_dict() for f in self.features],
        }
        if self.grass_color:
            d["grass_color"] = self.grass_color
        if self.foliage_color:
            d["foliage_color"] = self.foliage_color
        if self.spawn_costs:
            d["spawn_costs"] = self.spawn_costs
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Biome:
        return cls(
            biome_id=data["biome_id"],
            temperature=data.get("temperature", 0.5),
            humidity=data.get("humidity", 0.5),
            continentalness=data.get("continentalness", 0.0),
            erosion=data.get("erosion", 0.0),
            depth=data.get("depth", 0.0),
            weirdness=data.get("weirdness", 0.0),
            sky_color=data.get("sky_color", "#78A7FF"),
            fog_color=data.get("fog_color", "#C0D8FF"),
            water_color=data.get("water_color", "#3F76E4"),
            water_fog_color=data.get("water_fog_color", "#050533"),
            grass_color=data.get("grass_color"),
            foliage_color=data.get("foliage_color"),
            features=[PlacedFeature.from_dict(f) for f in data.get("features", [])],
            spawn_costs=data.get("spawn_costs", {}),
        )

    def __repr__(self) -> str:
        return f"Biome({self.biome_id!r}, temp={self.temperature}, features={len(self.features)})"
