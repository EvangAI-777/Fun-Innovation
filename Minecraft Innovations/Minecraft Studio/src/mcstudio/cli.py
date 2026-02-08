"""mcstudio CLI -- create, configure, and export Minecraft mod projects."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mcstudio.model.project import ModProject
from mcstudio.model.block import Block, BlockMaterial
from mcstudio.model.item import Item, FoodProperties, CreativeTab
from mcstudio.model.recipe import ShapedRecipe, ShapelessRecipe, SmeltingRecipe
from mcstudio.model.loot import LootTable
from mcstudio.export.base import export_project, EXPORTERS


def cmd_new(args: argparse.Namespace) -> None:
    """Create a new mod project."""
    project = ModProject(
        mod_id=args.mod_id,
        name=args.name or args.mod_id.replace("_", " ").title(),
        description=args.description or "",
        mc_version=args.mc_version,
    )
    path = project.save(args.output or f"{args.mod_id}.json")
    print(f"Created project: {project.name} ({project.mod_id})")
    print(f"Saved to: {path}")


def cmd_add_block(args: argparse.Namespace) -> None:
    """Add a block to an existing project."""
    project = ModProject.load(args.project)
    material = BlockMaterial(args.material) if args.material else BlockMaterial.STONE
    block = Block(
        block_id=args.block_id,
        material=material,
        hardness=args.hardness,
        resistance=args.resistance,
        luminance=args.luminance,
        requires_tool=args.requires_tool,
    )
    project.add_block(block)
    # Auto-add self-drop loot table
    lt = LootTable.block_self_drop(block.block_id)
    project.add_loot_table(lt)
    project.save(args.project)
    print(f"Added block: {block.block_id} (material={material.value})")


def cmd_add_item(args: argparse.Namespace) -> None:
    """Add an item to an existing project."""
    project = ModProject.load(args.project)
    food = None
    if args.food:
        food = FoodProperties(nutrition=args.nutrition, saturation=args.saturation)
    item = Item(
        item_id=args.item_id,
        max_stack_size=args.stack_size,
        food=food,
    )
    project.add_item(item)
    project.save(args.project)
    print(f"Added item: {item.item_id}")


def cmd_export(args: argparse.Namespace) -> None:
    """Export a project to a modloader-specific Gradle project."""
    project = ModProject.load(args.project)
    output_dir = Path(args.output or ".")
    loader = args.loader
    path = export_project(project, loader, output_dir)
    print(f"Exported {project.name} for {loader}: {path}")


def cmd_info(args: argparse.Namespace) -> None:
    """Show project information."""
    project = ModProject.load(args.project)
    print(f"Project: {project.name}")
    print(f"Mod ID:  {project.mod_id}")
    print(f"Version: {project.version}")
    print(f"MC:      {project.mc_version}")
    print(f"Blocks:  {len(project.blocks)}")
    print(f"Items:   {len(project.items)}")
    print(f"Recipes: {len(project.recipes)}")
    print(f"Loot:    {len(project.loot_tables)}")
    if project.blocks:
        print("\nBlocks:")
        for b in project.blocks:
            print(f"  {b.block_id} ({b.material.value}, hardness={b.hardness})")
    if project.items:
        print("\nItems:")
        for i in project.items:
            extra = " [food]" if i.is_food else ""
            print(f"  {i.item_id} (stack={i.max_stack_size}{extra})")


def cmd_loaders(args: argparse.Namespace) -> None:
    """List available export loaders."""
    print("Available loaders:")
    for name in sorted(EXPORTERS):
        exporter = EXPORTERS[name]()
        print(f"  {name:12s}  {exporter.loader_name()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mcstudio",
        description="Minecraft Studio -- mod data model and export engine",
    )
    sub = parser.add_subparsers(dest="command")

    # new
    p_new = sub.add_parser("new", help="Create a new mod project")
    p_new.add_argument("mod_id", help="Mod ID (lowercase, e.g. cool_mod)")
    p_new.add_argument("--name", help="Display name")
    p_new.add_argument("--description", help="Mod description")
    p_new.add_argument("--mc-version", default="1.21.4", help="Minecraft version")
    p_new.add_argument("--output", "-o", help="Output file path")

    # add-block
    p_block = sub.add_parser("add-block", help="Add a block to a project")
    p_block.add_argument("project", help="Project JSON file")
    p_block.add_argument("block_id", help="Block ID (e.g. custom_ore)")
    p_block.add_argument("--material", default="stone", help="Block material")
    p_block.add_argument("--hardness", type=float, default=1.5)
    p_block.add_argument("--resistance", type=float, default=6.0)
    p_block.add_argument("--luminance", type=int, default=0)
    p_block.add_argument("--requires-tool", action="store_true")

    # add-item
    p_item = sub.add_parser("add-item", help="Add an item to a project")
    p_item.add_argument("project", help="Project JSON file")
    p_item.add_argument("item_id", help="Item ID (e.g. magic_dust)")
    p_item.add_argument("--stack-size", type=int, default=64)
    p_item.add_argument("--food", action="store_true", help="Mark as food item")
    p_item.add_argument("--nutrition", type=int, default=4)
    p_item.add_argument("--saturation", type=float, default=0.3)

    # export
    p_export = sub.add_parser("export", help="Export project to a modloader")
    p_export.add_argument("project", help="Project JSON file")
    p_export.add_argument("loader", help="Target loader (fabric, forge, datapack)")
    p_export.add_argument("--output", "-o", help="Output directory")

    # info
    p_info = sub.add_parser("info", help="Show project information")
    p_info.add_argument("project", help="Project JSON file")

    # loaders
    sub.add_parser("loaders", help="List available export loaders")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "new": cmd_new,
        "add-block": cmd_add_block,
        "add-item": cmd_add_item,
        "export": cmd_export,
        "info": cmd_info,
        "loaders": cmd_loaders,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
