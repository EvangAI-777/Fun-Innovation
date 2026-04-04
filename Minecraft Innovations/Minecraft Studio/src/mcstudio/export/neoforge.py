"""NeoForge mod project exporter -- generates a complete NeoForge Gradle project."""

from __future__ import annotations

from pathlib import Path

from mcstudio.model.project import ModProject
from mcstudio.codegen.java import JavaWriter, to_java_string, to_pascal_case
from .base import Exporter, _register

# NeoForge version mappings per Minecraft version
_NEOFORGE_VERSIONS = {
    "1.21.4": {"neoforge": "21.4.0-beta", "loader_range": "[4,)", "neogradle": "7.0.163"},
    "1.21.3": {"neoforge": "21.3.0-beta", "loader_range": "[4,)", "neogradle": "7.0.163"},
    "1.20.4": {"neoforge": "20.4.237", "loader_range": "[2,)", "neogradle": "7.0.145"},
}
_DEFAULT_NEOFORGE = {"neoforge": "21.4.0-beta", "loader_range": "[4,)", "neogradle": "7.0.163"}


@_register
class NeoForgeExporter(Exporter):
    def loader_name(self) -> str:
        return "neoforge"

    def export(self, project: ModProject, output_dir: Path) -> Path:
        root = output_dir / f"{project.mod_id}-neoforge"
        versions = _NEOFORGE_VERSIONS.get(project.mc_version, _DEFAULT_NEOFORGE)

        self._write_build_gradle(root, project, versions)
        self._write_gradle_properties(root, project, versions)
        self._write_settings_gradle(root, project, versions)
        self._write_neoforge_mods_toml(root, project, versions)
        self._write_pack_mcmeta(root, project)
        self._write_mod_class(root, project)
        self._write_block_registry(root, project)
        self._write_item_registry(root, project)
        self._write_entity_registry(root, project)
        self._write_worldgen(root, project)
        self._write_recipes(root, project)
        self._write_loot_tables(root, project)
        self._write_tag_files(root / "src" / "main" / "resources" / "data", project)
        self._write_blockstate_models(root, project)
        assets = root / "src" / "main" / "resources" / "assets" / project.mod_id
        self._write_textures(assets, project)
        lang = self._generate_lang(project)
        if lang:
            self._write_json(assets / "lang" / "en_us.json", lang)

        return root

    def _write_build_gradle(self, root: Path, project: ModProject, versions: dict) -> None:
        content = f"""plugins {{
    id 'eclipse'
    id 'idea'
    id 'net.neoforged.gradle.userdev' version '{versions["neogradle"]}'
}}

version = '{project.version}'
group = 'com.{project.mod_id}'

base {{
    archivesName = '{project.mod_id}'
}}

java.toolchain.languageVersion = JavaLanguageVersion.of(21)

minecraft {{
    accessTransformers {{
        file rootProject.file('src/main/resources/META-INF/accesstransformer.cfg')
    }}
}}

runs {{
    client {{
        systemProperty 'forge.logging.markers', 'REGISTRIES'
        systemProperty 'forge.logging.console.level', 'debug'
    }}
    server {{
        systemProperty 'forge.logging.console.level', 'debug'
    }}
}}

dependencies {{
    implementation "net.neoforged:neoforge:{versions["neoforge"]}"
}}
"""
        self._write_file(root / "build.gradle", content)

    def _write_gradle_properties(self, root: Path, project: ModProject, versions: dict) -> None:
        self._write_file(root / "gradle.properties", "org.gradle.jvmargs=-Xmx3G\n")

    def _write_settings_gradle(self, root: Path, project: ModProject, versions: dict) -> None:
        self._write_file(root / "settings.gradle", f"""pluginManagement {{
    repositories {{
        gradlePluginPortal()
        maven {{ url = 'https://maven.neoforged.net/releases' }}
    }}
}}

plugins {{
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}}
""")

    def _write_neoforge_mods_toml(self, root: Path, project: ModProject, versions: dict) -> None:
        authors_str = ", ".join(project.authors) if project.authors else ""
        loader_range = versions["loader_range"]
        content = f"""modLoader="javafml"
loaderVersion="{loader_range}"
license="{project.license}"

[[mods]]
modId="{project.mod_id}"
version="${{file.jarVersion}}"
displayName="{project.name}"
description='''{project.description}'''
authors="{authors_str}"

[[dependencies.{project.mod_id}]]
modId="neoforge"
type="required"
versionRange="{loader_range}"
ordering="NONE"
side="BOTH"

[[dependencies.{project.mod_id}]]
modId="minecraft"
type="required"
versionRange="[{project.mc_version}]"
ordering="NONE"
side="BOTH"
"""
        meta_dir = root / "src" / "main" / "resources" / "META-INF"
        self._write_file(meta_dir / "neoforge.mods.toml", content)

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
            "net.neoforged.bus.api.IEventBus",
            "net.neoforged.fml.common.Mod",
            "org.slf4j.Logger",
            "com.mojang.logging.LogUtils",
        )
        w.line()
        w.annotation(f'Mod({cls_name}.MOD_ID)')
        w.open_block(f"public class {cls_name}")
        w.field("public static final", "String", "MOD_ID", to_java_string(project.mod_id))
        w.field("private static final", "Logger", "LOGGER", "LogUtils.getLogger()")
        w.line()
        w.open_block(f"public {cls_name}(IEventBus modEventBus)")
        if project.blocks:
            w.line(f"{cls_name}Blocks.register(modEventBus);")
        if project.items:
            w.line(f"{cls_name}Items.register(modEventBus);")
        if project.entities:
            w.line(f"{cls_name}Entities.register(modEventBus);")
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
            "net.minecraft.core.registries.Registries",
            "net.minecraft.world.level.block.Block",
            "net.minecraft.world.level.block.state.BlockBehaviour",
            "net.minecraft.world.item.BlockItem",
            "net.minecraft.world.item.Item",
            "net.neoforged.bus.api.IEventBus",
            "net.neoforged.neoforge.registries.DeferredBlock",
            "net.neoforged.neoforge.registries.DeferredItem",
            "net.neoforged.neoforge.registries.DeferredRegister",
        )
        w.line()
        w.open_block(f"public class {cls_name}Blocks")
        w.field(
            "public static final", "DeferredRegister.Blocks", "BLOCKS",
            f"DeferredRegister.createBlocks({cls_name}.MOD_ID)",
        )
        w.field(
            "public static final", "DeferredRegister.Items", "BLOCK_ITEMS",
            f"DeferredRegister.createItems({cls_name}.MOD_ID)",
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
                "public static final", "DeferredBlock<Block>", block.java_constant,
                f'BLOCKS.register("{block.block_id}", () -> new Block({props}))',
            )
            if block.has_block_item:
                w.field(
                    "public static final", "DeferredItem<BlockItem>",
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
            "net.neoforged.bus.api.IEventBus",
            "net.neoforged.neoforge.registries.DeferredItem",
            "net.neoforged.neoforge.registries.DeferredRegister",
        )
        if any(i.is_food for i in project.items):
            w.add_import("net.minecraft.world.food.FoodProperties")
        w.line()
        w.open_block(f"public class {cls_name}Items")
        w.field(
            "public static final", "DeferredRegister.Items", "ITEMS",
            f"DeferredRegister.createItems({cls_name}.MOD_ID)",
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
                    f".nutrition({food.nutrition}).saturationModifier({food.saturation}f)"
                )
                if food.is_meat:
                    food_builder += ".meat()"
                if food.can_always_eat:
                    food_builder += ".alwaysEdible()"
                food_builder += ".build()"
                settings += f".food({food_builder})"
            w.field(
                "public static final", "DeferredItem<Item>", item.java_constant,
                f'ITEMS.register("{item.item_id}", () -> new Item({settings}))',
            )
        w.line()
        w.open_block("public static void register(IEventBus eventBus)")
        w.line("ITEMS.register(eventBus);")
        w.close_block()
        w.close_block()

        pkg_path = pkg.replace(".", "/")
        self._write_file(root / "src" / "main" / "java" / pkg_path / f"{cls_name}Items.java", w.build())

    def _write_worldgen(self, root: Path, project: ModProject) -> None:
        if not project.biomes:
            return
        from mcstudio.codegen.worldgen import (
            generate_biome_json,
            generate_configured_feature_json,
            generate_placed_feature_json,
            _feature_to_generation_step,
        )
        data = root / "src" / "main" / "resources" / "data" / project.mod_id
        for biome in project.biomes:
            self._write_json(
                data / "worldgen" / "biome" / f"{biome.biome_id}.json",
                generate_biome_json(biome, project.mod_id),
            )
            for feature in biome.features:
                self._write_json(
                    data / "worldgen" / "configured_feature" / f"{feature.feature_id}.json",
                    generate_configured_feature_json(feature, project.mod_id),
                )
                self._write_json(
                    data / "worldgen" / "placed_feature" / f"{feature.feature_id}.json",
                    generate_placed_feature_json(feature, project.mod_id),
                )
                step = _feature_to_generation_step(feature.feature_type)
                self._write_json(
                    data / "neoforge" / "biome_modifier" / f"add_{feature.feature_id}.json",
                    {
                        "type": "neoforge:add_features",
                        "biomes": "#minecraft:is_overworld",
                        "features": [f"{project.mod_id}:{feature.feature_id}"],
                        "step": step.lower(),
                    },
                )

    def _write_entity_registry(self, root: Path, project: ModProject) -> None:
        if not project.entities:
            return
        from mcstudio.codegen.entity import generate_entity_class, generate_entity_renderer
        pkg = project.java_package
        cls_name = project.java_class_name
        pkg_path = pkg.replace(".", "/")

        for entity in project.entities:
            code = generate_entity_class(entity, pkg)
            self._write_file(
                root / "src" / "main" / "java" / pkg_path / f"{entity.java_class_name}.java", code,
            )
            renderer_code = generate_entity_renderer(entity, pkg, cls_name)
            self._write_file(
                root / "src" / "main" / "java" / pkg_path / "client" / f"{entity.java_class_name}Renderer.java",
                renderer_code,
            )

        w = JavaWriter()
        w.set_package(pkg)
        w.add_import(
            "net.minecraft.core.registries.Registries",
            "net.minecraft.world.entity.EntityType",
            "net.minecraft.world.entity.MobCategory",
            "net.minecraft.world.item.Item",
            "net.minecraft.world.item.SpawnEggItem",
            "net.neoforged.bus.api.IEventBus",
            "net.neoforged.neoforge.registries.DeferredHolder",
            "net.neoforged.neoforge.registries.DeferredRegister",
        )
        if any(e.attributes for e in project.entities):
            w.add_import(
                "net.neoforged.bus.api.SubscribeEvent",
                "net.neoforged.fml.common.EventBusSubscriber",
                "net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent",
            )
        w.line()
        w.open_block(f"public class {cls_name}Entities")
        w.field(
            "public static final", "DeferredRegister<EntityType<?>>", "ENTITY_TYPES",
            f"DeferredRegister.create(Registries.ENTITY_TYPE, {cls_name}.MOD_ID)",
        )
        w.field(
            "public static final", "DeferredRegister<Item>", "SPAWN_EGGS",
            f"DeferredRegister.create(Registries.ITEM, {cls_name}.MOD_ID)",
        )
        w.line()
        for entity in project.entities:
            cat = entity.spawn_rules.category.value.upper() if entity.spawn_rules else "CREATURE"
            builder = (
                f'EntityType.Builder.of({entity.java_class_name}::new, MobCategory.{cat})'
                f'.sized({entity.width}f, {entity.height}f)'
            )
            if entity.fireproof:
                builder += ".fireImmune()"
            w.field(
                "public static final",
                f"DeferredHolder<EntityType<?>, EntityType<{entity.java_class_name}>>",
                entity.java_constant,
                f'ENTITY_TYPES.register("{entity.entity_id}", () -> {builder}.build("{entity.entity_id}"))',
            )
            w.field(
                "public static final", "DeferredHolder<Item, SpawnEggItem>",
                f"{entity.java_constant}_SPAWN_EGG",
                f'SPAWN_EGGS.register("{entity.entity_id}_spawn_egg", () -> new SpawnEggItem({entity.java_constant}.get(), 0x333333, 0x999999, new Item.Properties()))',
            )
        w.line()
        w.open_block("public static void register(IEventBus eventBus)")
        w.line("ENTITY_TYPES.register(eventBus);")
        w.line("SPAWN_EGGS.register(eventBus);")
        w.close_block()

        if any(e.attributes for e in project.entities):
            w.line()
            w.annotation(f'EventBusSubscriber(modid = {cls_name}.MOD_ID, bus = EventBusSubscriber.Bus.MOD)')
            w.open_block("public static class AttributeEvents")
            w.annotation("SubscribeEvent")
            w.open_block("public static void onEntityAttributeCreation(EntityAttributeCreationEvent event)")
            for entity in project.entities:
                if entity.attributes:
                    w.line(f"event.put({entity.java_constant}.get(), {entity.java_class_name}.createAttributes().build());")
            w.close_block()
            w.close_block()

        w.close_block()

        self._write_file(
            root / "src" / "main" / "java" / pkg_path / f"{cls_name}Entities.java", w.build(),
        )

    def _write_recipes(self, root: Path, project: ModProject) -> None:
        for recipe in project.recipes:
            data_path = (
                root / "src" / "main" / "resources" / "data"
                / project.mod_id / "recipe" / f"{recipe.recipe_id}.json"
            )
            self._write_json(data_path, self._recipe_to_json(recipe))

    def _write_loot_tables(self, root: Path, project: ModProject) -> None:
        for lt in project.loot_tables:
            data_path = (
                root / "src" / "main" / "resources" / "data"
                / project.mod_id / "loot_table" / f"{lt.table_id}.json"
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
