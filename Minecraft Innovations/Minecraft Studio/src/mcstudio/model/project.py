"""Top-level mod project model -- the container for all mod content."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .block import Block
from .item import Item
from .recipe import Recipe
from .loot import LootTable
from .entity import EntityType
from .worldgen import Biome
from .advancement import Advancement
from .event import EventHandler
from .config import ModConfig


def _validate_mod_id(mod_id: str) -> str:
    """Validate a mod ID follows Minecraft conventions: lowercase, alphanumeric, underscores."""
    if not re.match(r"^[a-z][a-z0-9_]{1,63}$", mod_id):
        raise ValueError(
            f"Invalid mod ID: {mod_id!r}. Must be lowercase, start with a letter, "
            "contain only a-z, 0-9, underscore, and be 2-64 characters."
        )
    return mod_id


@dataclass
class ModProject:
    """A complete Minecraft mod project."""

    mod_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    authors: list[str] = field(default_factory=list)
    mc_version: str = "1.21.4"
    license: str = "All Rights Reserved"

    creative_tab_label: str | None = None  # Custom creative tab name; None = use mod name

    blocks: list[Block] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    entities: list[EntityType] = field(default_factory=list)
    biomes: list[Biome] = field(default_factory=list)
    recipes: list[Recipe] = field(default_factory=list)
    loot_tables: list[LootTable] = field(default_factory=list)
    advancements: list[Advancement] = field(default_factory=list)
    event_handlers: list[EventHandler] = field(default_factory=list)
    config: ModConfig | None = None

    def __post_init__(self) -> None:
        self.mod_id = _validate_mod_id(self.mod_id)

    # --- Registry helpers ---

    def add_block(self, block: Block) -> Block:
        if any(b.block_id == block.block_id for b in self.blocks):
            raise ValueError(f"Duplicate block ID: {block.block_id!r}")
        self.blocks.append(block)
        return block

    def add_item(self, item: Item) -> Item:
        if any(i.item_id == item.item_id for i in self.items):
            raise ValueError(f"Duplicate item ID: {item.item_id!r}")
        self.items.append(item)
        return item

    def add_entity(self, entity: EntityType) -> EntityType:
        if any(e.entity_id == entity.entity_id for e in self.entities):
            raise ValueError(f"Duplicate entity ID: {entity.entity_id!r}")
        self.entities.append(entity)
        return entity

    def get_entity(self, entity_id: str) -> EntityType | None:
        for e in self.entities:
            if e.entity_id == entity_id:
                return e
        return None

    def add_biome(self, biome: Biome) -> Biome:
        if any(b.biome_id == biome.biome_id for b in self.biomes):
            raise ValueError(f"Duplicate biome ID: {biome.biome_id!r}")
        self.biomes.append(biome)
        return biome

    def get_biome(self, biome_id: str) -> Biome | None:
        for b in self.biomes:
            if b.biome_id == biome_id:
                return b
        return None

    def add_recipe(self, recipe: Recipe) -> Recipe:
        if any(r.recipe_id == recipe.recipe_id for r in self.recipes):
            raise ValueError(f"Duplicate recipe ID: {recipe.recipe_id!r}")
        self.recipes.append(recipe)
        return recipe

    def add_loot_table(self, loot_table: LootTable) -> LootTable:
        self.loot_tables.append(loot_table)
        return loot_table

    def add_event_handler(self, handler: EventHandler) -> EventHandler:
        self.event_handlers.append(handler)
        return handler

    def add_advancement(self, advancement: Advancement) -> Advancement:
        if any(a.advancement_id == advancement.advancement_id for a in self.advancements):
            raise ValueError(f"Duplicate advancement ID: {advancement.advancement_id!r}")
        self.advancements.append(advancement)
        return advancement

    def get_block(self, block_id: str) -> Block | None:
        for b in self.blocks:
            if b.block_id == block_id:
                return b
        return None

    def get_item(self, item_id: str) -> Item | None:
        for i in self.items:
            if i.item_id == item_id:
                return i
        return None

    # --- Resource location helpers ---

    def resource_location(self, name: str) -> str:
        """Full resource location: mod_id:name."""
        return f"{self.mod_id}:{name}"

    @property
    def java_package(self) -> str:
        """Java package name derived from mod ID."""
        return f"com.{self.mod_id}.{self.mod_id}"

    @property
    def java_class_name(self) -> str:
        """Main mod class name (PascalCase from mod ID)."""
        from mcstudio.codegen.java import to_pascal_case
        return to_pascal_case(self.mod_id)

    # --- Serialization ---

    def to_dict(self) -> dict:
        return {
            "mod_id": self.mod_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "authors": self.authors,
            "mc_version": self.mc_version,
            "license": self.license,
            "creative_tab_label": self.creative_tab_label,
            "blocks": [b.to_dict() for b in self.blocks],
            "items": [i.to_dict() for i in self.items],
            "entities": [e.to_dict() for e in self.entities],
            "biomes": [b.to_dict() for b in self.biomes],
            "recipes": [r.to_dict() for r in self.recipes],
            "loot_tables": [lt.to_dict() for lt in self.loot_tables],
            "advancements": [a.to_dict() for a in self.advancements],
            "event_handlers": [h.to_dict() for h in self.event_handlers],
            "config": self.config.to_dict() if self.config else None,
        }

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path

    @classmethod
    def load(cls, path: str | Path) -> ModProject:
        with open(path) as f:
            data = json.load(f)
        project = cls(
            mod_id=data["mod_id"],
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            authors=data.get("authors", []),
            mc_version=data.get("mc_version", "1.21.4"),
            license=data.get("license", "All Rights Reserved"),
            creative_tab_label=data.get("creative_tab_label"),
        )
        for bd in data.get("blocks", []):
            project.add_block(Block.from_dict(bd))
        for id_ in data.get("items", []):
            project.add_item(Item.from_dict(id_))
        for ed in data.get("entities", []):
            project.add_entity(EntityType.from_dict(ed))
        for bd in data.get("biomes", []):
            project.add_biome(Biome.from_dict(bd))
        from .recipe import recipe_from_dict
        for rd in data.get("recipes", []):
            project.add_recipe(recipe_from_dict(rd))
        for ld in data.get("loot_tables", []):
            project.add_loot_table(LootTable.from_dict(ld))
        for ad in data.get("advancements", []):
            project.add_advancement(Advancement.from_dict(ad))
        for hd in data.get("event_handlers", []):
            project.add_event_handler(EventHandler.from_dict(hd))
        config_data = data.get("config")
        if config_data:
            project.config = ModConfig.from_dict(config_data)
        return project

    def __repr__(self) -> str:
        return (
            f"ModProject({self.mod_id!r}, blocks={len(self.blocks)}, "
            f"items={len(self.items)}, entities={len(self.entities)}, "
            f"recipes={len(self.recipes)})"
        )
