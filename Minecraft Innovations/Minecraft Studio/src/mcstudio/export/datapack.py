"""Data Pack exporter -- generates a vanilla Minecraft data pack (no modloader)."""

from __future__ import annotations

from pathlib import Path

from mcstudio.model.project import ModProject
from .base import Exporter, _register


@_register
class DataPackExporter(Exporter):
    def loader_name(self) -> str:
        return "datapack"

    def export(self, project: ModProject, output_dir: Path) -> Path:
        root = output_dir / f"{project.mod_id}-datapack"

        self._write_pack_mcmeta(root, project)
        self._write_recipes(root, project)
        self._write_loot_tables(root, project)

        return root

    def _write_pack_mcmeta(self, root: Path, project: ModProject) -> None:
        self._write_json(root / "pack.mcmeta", {
            "pack": {
                "pack_format": 26,
                "description": project.description or f"{project.name} data pack",
            }
        })

    def _write_recipes(self, root: Path, project: ModProject) -> None:
        for recipe in project.recipes:
            path = root / "data" / project.mod_id / "recipe" / f"{recipe.recipe_id}.json"
            self._write_json(path, self._recipe_to_json(recipe))

    def _write_loot_tables(self, root: Path, project: ModProject) -> None:
        for lt in project.loot_tables:
            path = root / "data" / project.mod_id / "loot_table" / f"{lt.table_id}.json"
            self._write_json(path, self._loot_table_to_json(lt, project.mod_id))
