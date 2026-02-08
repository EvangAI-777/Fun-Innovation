"""Forge mod project exporter -- generates a complete Forge Gradle project."""

from __future__ import annotations

from pathlib import Path

from mcstudio.model.project import ModProject
from mcstudio.codegen.java import JavaWriter, to_java_string, to_pascal_case
from .base import Exporter, _register


@_register
class ForgeExporter(Exporter):
    def loader_name(self) -> str:
        return "forge"

    def export(self, project: ModProject, output_dir: Path) -> Path:
        root = output_dir / f"{project.mod_id}-forge"

        self._write_build_gradle(root, project)
        self._write_gradle_properties(root, project)
        self._write_settings_gradle(root, project)
        self._write_mods_toml(root, project)
        self._write_pack_mcmeta(root, project)
        self._write_mod_class(root, project)
        self._write_block_registry(root, project)
        self._write_item_registry(root, project)
        self._write_recipes(root, project)
        self._write_loot_tables(root, project)
        self._write_blockstate_models(root, project)

        return root

    def _write_build_gradle(self, root: Path, project: ModProject) -> None:
        content = f"""plugins {{
    id 'eclipse'
    id 'idea'
    id 'net.minecraftforge.gradle' version '[6.0.24,6.2)'
}}

version = '{project.version}'
group = 'com.{project.mod_id}'
archivesBaseName = '{project.mod_id}'

java.toolchain.languageVersion = JavaLanguageVersion.of(21)

minecraft {{
    mappings channel: 'official', version: '{project.mc_version}'
    runs {{
        client {{
            workingDirectory project.file('run')
            property 'forge.logging.markers', 'REGISTRIES'
            property 'forge.logging.console.level', 'debug'
            mods {{
                {project.mod_id} {{
                    source sourceSets.main
                }}
            }}
        }}
        server {{
            workingDirectory project.file('run')
            property 'forge.logging.console.level', 'debug'
            mods {{
                {project.mod_id} {{
                    source sourceSets.main
                }}
            }}
        }}
    }}
}}

dependencies {{
    minecraft 'net.minecraftforge:forge:{project.mc_version}-49.0.0'
}}

jar {{
    manifest {{
        attributes([
            "Specification-Title"     : "{project.mod_id}",
            "Specification-Vendor"    : "{', '.join(project.authors) or project.mod_id}",
            "Specification-Version"   : "1",
            "Implementation-Title"    : project.name,
            "Implementation-Version"  : project.version,
            "Implementation-Vendor"   : "{', '.join(project.authors) or project.mod_id}",
        ])
    }}
}}
"""
        self._write_file(root / "build.gradle", content)

    def _write_gradle_properties(self, root: Path, project: ModProject) -> None:
        self._write_file(root / "gradle.properties", "org.gradle.jvmargs=-Xmx3G\n")

    def _write_settings_gradle(self, root: Path, project: ModProject) -> None:
        self._write_file(root / "settings.gradle", f"""pluginManagement {{
    repositories {{
        gradlePluginPortal()
        maven {{ url = 'https://maven.minecraftforge.net/' }}
    }}
}}

plugins {{
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}}
""")

    def _write_mods_toml(self, root: Path, project: ModProject) -> None:
        authors_str = ", ".join(project.authors) if project.authors else ""
        content = f"""modLoader="javafml"
loaderVersion="[49,)"
license="{project.license}"

[[mods]]
modId="{project.mod_id}"
version="${{file.jarVersion}}"
displayName="{project.name}"
description='''{project.description}'''
authors="{authors_str}"

[[dependencies.{project.mod_id}]]
modId="forge"
mandatory=true
versionRange="[49,)"
ordering="NONE"
side="BOTH"

[[dependencies.{project.mod_id}]]
modId="minecraft"
mandatory=true
versionRange="[{project.mc_version}]"
ordering="NONE"
side="BOTH"
"""
        meta_dir = root / "src" / "main" / "resources" / "META-INF"
        self._write_file(meta_dir / "mods.toml", content)

    def _write_pack_mcmeta(self, root: Path, project: ModProject) -> None:
        self._write_json(
            root / "src" / "main" / "resources" / "pack.mcmeta",
            {"pack": {"description": project.description, "pack_format": 26}},
        )

    def _write_mod_class(self, root: Path, project: ModProject) -> None:
        pkg = project.java_package
        cls_name = project.java_class_name
        w = JavaWriter()
        w.set_package(pkg)
        w.add_import(
            "net.minecraftforge.fml.common.Mod",
            "net.minecraftforge.eventbus.api.IEventBus",
            "net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext",
            "org.slf4j.Logger",
            "com.mojang.logging.LogUtils",
        )
        w.line()
        w.annotation(f'Mod({cls_name}.MOD_ID)')
        w.open_block(f"public class {cls_name}")
        w.field("public static final", "String", "MOD_ID", to_java_string(project.mod_id))
        w.field("private static final", "Logger", "LOGGER", "LogUtils.getLogger()")
        w.line()
        w.open_block(f"public {cls_name}()")
        w.line("IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();")
        if project.blocks:
            w.line(f"{cls_name}Blocks.register(modEventBus);")
        if project.items:
            w.line(f"{cls_name}Items.register(modEventBus);")
        w.line(f'LOGGER.info("Initializing {project.name}");')
        w.close_block()
        w.close_block()

        pkg_path = pkg.replace(".", "/")
        self._write_file(root / "src" / "main" / "java" / pkg_path / f"{cls_name}.java", w.build())

    def _write_block_registry(self, root: Path, project: ModProject) -> None:
        if not project.blocks:
            return
        pkg = project.java_package
        cls_name = project.java_class_name
        w = JavaWriter()
        w.set_package(pkg)
        w.add_import(
            "net.minecraft.world.level.block.Block",
            "net.minecraft.world.level.block.state.BlockBehaviour",
            "net.minecraft.world.item.BlockItem",
            "net.minecraft.world.item.Item",
            "net.minecraftforge.eventbus.api.IEventBus",
            "net.minecraftforge.registries.DeferredRegister",
            "net.minecraftforge.registries.ForgeRegistries",
            "net.minecraftforge.registries.RegistryObject",
        )
        w.line()
        w.open_block(f"public class {cls_name}Blocks")
        w.field(
            "public static final", "DeferredRegister<Block>", "BLOCKS",
            f"DeferredRegister.create(ForgeRegistries.BLOCKS, {cls_name}.MOD_ID)",
        )
        w.field(
            "public static final", "DeferredRegister<Item>", "BLOCK_ITEMS",
            f"DeferredRegister.create(ForgeRegistries.ITEMS, {cls_name}.MOD_ID)",
        )
        w.line()
        for block in project.blocks:
            props = f"BlockBehaviour.Properties.of().strength({block.hardness}f, {block.resistance}f)"
            if block.luminance:
                props += f".lightLevel(state -> {block.luminance})"
            if block.no_collision:
                props += ".noCollision()"
            if block.requires_tool:
                props += ".requiresCorrectToolForDrops()"
            w.field(
                "public static final", "RegistryObject<Block>", block.java_constant,
                f'BLOCKS.register("{block.block_id}", () -> new Block({props}))',
            )
            if block.has_block_item:
                w.field(
                    "public static final", "RegistryObject<Item>",
                    f"{block.java_constant}_ITEM",
                    f'BLOCK_ITEMS.register("{block.block_id}", () -> new BlockItem({block.java_constant}.get(), new Item.Properties()))',
                )
        w.line()
        w.open_block("public static void register(IEventBus eventBus)")
        w.line("BLOCKS.register(eventBus);")
        w.line("BLOCK_ITEMS.register(eventBus);")
        w.close_block()
        w.close_block()

        pkg_path = pkg.replace(".", "/")
        self._write_file(root / "src" / "main" / "java" / pkg_path / f"{cls_name}Blocks.java", w.build())

    def _write_item_registry(self, root: Path, project: ModProject) -> None:
        if not project.items:
            return
        pkg = project.java_package
        cls_name = project.java_class_name
        w = JavaWriter()
        w.set_package(pkg)
        w.add_import(
            "net.minecraft.world.item.Item",
            "net.minecraftforge.eventbus.api.IEventBus",
            "net.minecraftforge.registries.DeferredRegister",
            "net.minecraftforge.registries.ForgeRegistries",
            "net.minecraftforge.registries.RegistryObject",
        )
        if any(i.is_food for i in project.items):
            w.add_import("net.minecraft.world.food.FoodProperties")
        w.line()
        w.open_block(f"public class {cls_name}Items")
        w.field(
            "public static final", "DeferredRegister<Item>", "ITEMS",
            f"DeferredRegister.create(ForgeRegistries.ITEMS, {cls_name}.MOD_ID)",
        )
        w.line()
        for item in project.items:
            settings = "new Item.Properties()"
            if item.max_stack_size != 64:
                settings += f".stacksTo({item.max_stack_size})"
            if item.fireproof:
                settings += ".fireResistant()"
            if item.is_food:
                food = item.food
                food_builder = (
                    f"new FoodProperties.Builder()"
                    f".nutrition({food.nutrition}).saturationMod({food.saturation}f)"
                )
                if food.is_meat:
                    food_builder += ".meat()"
                if food.can_always_eat:
                    food_builder += ".alwaysEat()"
                food_builder += ".build()"
                settings += f".food({food_builder})"
            w.field(
                "public static final", "RegistryObject<Item>", item.java_constant,
                f'ITEMS.register("{item.item_id}", () -> new Item({settings}))',
            )
        w.line()
        w.open_block("public static void register(IEventBus eventBus)")
        w.line("ITEMS.register(eventBus);")
        w.close_block()
        w.close_block()

        pkg_path = pkg.replace(".", "/")
        self._write_file(root / "src" / "main" / "java" / pkg_path / f"{cls_name}Items.java", w.build())

    def _write_recipes(self, root: Path, project: ModProject) -> None:
        for recipe in project.recipes:
            data_path = (
                root / "src" / "main" / "resources" / "data"
                / project.mod_id / "recipes" / f"{recipe.recipe_id}.json"
            )
            self._write_json(data_path, self._recipe_to_json(recipe))

    def _write_loot_tables(self, root: Path, project: ModProject) -> None:
        for lt in project.loot_tables:
            data_path = (
                root / "src" / "main" / "resources" / "data"
                / project.mod_id / "loot_tables" / f"{lt.table_id}.json"
            )
            self._write_json(data_path, self._loot_table_to_json(lt, project.mod_id))

    def _write_blockstate_models(self, root: Path, project: ModProject) -> None:
        res = root / "src" / "main" / "resources"
        for block in project.blocks:
            blockstate = {
                "variants": {
                    "": {"model": f"{project.mod_id}:block/{block.block_id}"}
                }
            }
            self._write_json(
                res / "assets" / project.mod_id / "blockstates" / f"{block.block_id}.json",
                blockstate,
            )
            block_model = {
                "parent": "minecraft:block/cube_all",
                "textures": {"all": f"{project.mod_id}:block/{block.block_id}"}
            }
            self._write_json(
                res / "assets" / project.mod_id / "models" / "block" / f"{block.block_id}.json",
                block_model,
            )
            if block.has_block_item:
                item_model = {"parent": f"{project.mod_id}:block/{block.block_id}"}
                self._write_json(
                    res / "assets" / project.mod_id / "models" / "item" / f"{block.block_id}.json",
                    item_model,
                )
        for item in project.items:
            item_model = {
                "parent": "minecraft:item/generated",
                "textures": {"layer0": f"{project.mod_id}:item/{item.item_id}"}
            }
            self._write_json(
                res / "assets" / project.mod_id / "models" / "item" / f"{item.item_id}.json",
                item_model,
            )
