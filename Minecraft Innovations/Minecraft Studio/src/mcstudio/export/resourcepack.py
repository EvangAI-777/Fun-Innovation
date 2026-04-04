"""Resource Pack exporter -- generates a standalone Minecraft resource pack."""

from __future__ import annotations

from pathlib import Path

from mcstudio.model.project import ModProject
from .base import Exporter, _register


@_register
class ResourcePackExporter(Exporter):
    def loader_name(self) -> str:
        return "resourcepack"

    def export(self, project: ModProject, output_dir: Path) -> Path:
        root = output_dir / f"{project.mod_id}-resourcepack"

        self._write_pack_mcmeta(root, project)
        self._write_blockstate_models(root, project)
        assets = root / "assets" / project.mod_id
        self._write_textures(assets, project)
        lang = self._generate_lang(project)
        if lang:
            self._write_json(assets / "lang" / "en_us.json", lang)
        self._write_sounds_json(assets)

        return root

    def _write_pack_mcmeta(self, root: Path, project: ModProject) -> None:
        self._write_json(root / "pack.mcmeta", {
            "pack": {
                "pack_format": 34,
                "description": project.description or f"{project.name} resource pack",
            }
        })

    def _write_blockstate_models(self, root: Path, project: ModProject) -> None:
        for block in project.blocks:
            blockstate = {
                "variants": {
                    "": {"model": f"{project.mod_id}:block/{block.block_id}"}
                }
            }
            self._write_json(
                root / "assets" / project.mod_id / "blockstates" / f"{block.block_id}.json",
                blockstate,
            )
            block_model = {
                "parent": "minecraft:block/cube_all",
                "textures": {
                    "all": f"{project.mod_id}:block/{block.block_id}"
                }
            }
            self._write_json(
                root / "assets" / project.mod_id / "models" / "block" / f"{block.block_id}.json",
                block_model,
            )
            if block.has_block_item:
                item_model = {
                    "parent": f"{project.mod_id}:block/{block.block_id}"
                }
                self._write_json(
                    root / "assets" / project.mod_id / "models" / "item" / f"{block.block_id}.json",
                    item_model,
                )
        for item in project.items:
            item_model = {
                "parent": "minecraft:item/generated",
                "textures": {
                    "layer0": f"{project.mod_id}:item/{item.item_id}"
                }
            }
            self._write_json(
                root / "assets" / project.mod_id / "models" / "item" / f"{item.item_id}.json",
                item_model,
            )

    def _write_sounds_json(self, assets_dir: Path) -> None:
        self._write_json(assets_dir / "sounds.json", {})
