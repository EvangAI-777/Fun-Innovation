"""Base exporter interface and dispatch."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from mcstudio.model.project import ModProject


class Exporter(ABC):
    """Base class for all mod project exporters."""

    @abstractmethod
    def loader_name(self) -> str: ...

    @abstractmethod
    def export(self, project: ModProject, output_dir: Path) -> Path: ...

    def _write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def _write_json(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n")

    def _recipe_to_json(self, recipe) -> dict:
        """Convert a recipe model to vanilla Minecraft recipe JSON."""
        from mcstudio.model.recipe import (
            ShapedRecipe, ShapelessRecipe, SmeltingRecipe, BlastingRecipe,
            SmokingRecipe, StonecuttingRecipe, SmithingRecipe,
        )
        if isinstance(recipe, ShapedRecipe):
            return {
                "type": "minecraft:crafting_shaped",
                "pattern": recipe.pattern,
                "key": {k: {"item": v} for k, v in recipe.key.items()},
                "result": {"id": recipe.result, "count": recipe.count},
            }
        if isinstance(recipe, ShapelessRecipe):
            return {
                "type": "minecraft:crafting_shapeless",
                "ingredients": [{"item": i} for i in recipe.ingredients],
                "result": {"id": recipe.result, "count": recipe.count},
            }
        if isinstance(recipe, (SmeltingRecipe, BlastingRecipe, SmokingRecipe)):
            type_map = {
                SmeltingRecipe: "minecraft:smelting",
                BlastingRecipe: "minecraft:blasting",
                SmokingRecipe: "minecraft:smoking",
            }
            return {
                "type": type_map[type(recipe)],
                "ingredient": {"item": recipe.ingredient},
                "result": {"id": recipe.result},
                "experience": recipe.experience,
                "cookingtime": recipe.cooking_time,
            }
        if isinstance(recipe, StonecuttingRecipe):
            return {
                "type": "minecraft:stonecutting",
                "ingredient": {"item": recipe.ingredient},
                "result": {"id": recipe.result, "count": recipe.count},
            }
        if isinstance(recipe, SmithingRecipe):
            return {
                "type": "minecraft:smithing_transform",
                "template": {"item": recipe.template},
                "base": {"item": recipe.base},
                "addition": {"item": recipe.addition},
                "result": {"id": recipe.result},
            }
        raise ValueError(f"Unknown recipe type: {type(recipe)}")

    def _loot_table_to_json(self, loot_table, mod_id: str) -> dict:
        """Convert a loot table model to vanilla Minecraft loot table JSON."""
        condition_map = {
            "survives_explosion": {"condition": "minecraft:survives_explosion"},
            "killed_by_player": {"condition": "minecraft:killed_by_player"},
            "random_chance": {"condition": "minecraft:random_chance", "chance": 0.5},
            "silk_touch": {
                "condition": "minecraft:match_tool",
                "predicate": {"enchantments": [{"enchantment": "minecraft:silk_touch", "levels": {"min": 1}}]},
            },
        }
        pools = []
        for pool in loot_table.pools:
            entries = []
            for entry in pool.entries:
                e: dict = {
                    "type": "minecraft:item",
                    "name": f"{mod_id}:{entry.item_id}" if ":" not in entry.item_id else entry.item_id,
                }
                if entry.weight != 1:
                    e["weight"] = entry.weight
                if entry.count_min != 1 or entry.count_max != 1:
                    e["functions"] = [{
                        "function": "minecraft:set_count",
                        "count": {"min": entry.count_min, "max": entry.count_max},
                    }]
                if entry.conditions:
                    e["conditions"] = [
                        condition_map.get(c.value, {"condition": f"minecraft:{c.value}"})
                        for c in entry.conditions
                    ]
                entries.append(e)
            p: dict = {
                "rolls": pool.rolls_min if pool.rolls_min == pool.rolls_max else {
                    "min": pool.rolls_min, "max": pool.rolls_max,
                },
                "entries": entries,
            }
            if pool.bonus_rolls:
                p["bonus_rolls"] = pool.bonus_rolls
            if pool.conditions:
                p["conditions"] = [
                    condition_map.get(c.value, {"condition": f"minecraft:{c.value}"})
                    for c in pool.conditions
                ]
            pools.append(p)
        return {
            "type": f"minecraft:{loot_table.table_type}",
            "pools": pools,
        }


EXPORTERS: dict[str, type[Exporter]] = {}


def _register(cls: type[Exporter]) -> type[Exporter]:
    EXPORTERS[cls.__name__.replace("Exporter", "").lower()] = cls
    return cls


def export_project(project: ModProject, loader: str, output_dir: str | Path) -> Path:
    """Export a project using the named loader."""
    loader = loader.lower().strip()
    if loader == "data_pack":
        loader = "datapack"
    if loader not in EXPORTERS:
        raise ValueError(
            f"Unknown loader: {loader!r}. Available: {', '.join(sorted(EXPORTERS))}"
        )
    exporter = EXPORTERS[loader]()
    return exporter.export(project, Path(output_dir))


# Import submodules to trigger registration
def _init_exporters() -> None:
    from . import fabric, forge, datapack  # noqa: F401

_init_exporters()
