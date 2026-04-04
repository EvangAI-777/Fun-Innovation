"""Forge mod project exporter -- generates a complete Forge Gradle project."""

from __future__ import annotations

from pathlib import Path

from mcstudio.model.project import ModProject
from mcstudio.codegen.java import JavaWriter, to_java_string, to_pascal_case
from .base import Exporter, _register

# Forge version mappings per Minecraft version
_FORGE_VERSIONS = {
    "1.21.4": {"forge": "54.1.0", "loader_range": "[54,)", "gradle": "[6.0.24,6.2)"},
    "1.21.3": {"forge": "53.0.0", "loader_range": "[53,)", "gradle": "[6.0.24,6.2)"},
    "1.20.4": {"forge": "49.0.0", "loader_range": "[49,)", "gradle": "[6.0.24,6.2)"},
    "1.20.1": {"forge": "47.3.0", "loader_range": "[47,)", "gradle": "[6.0,6.2)"},
}
_DEFAULT_FORGE = {"forge": "54.1.0", "loader_range": "[54,)", "gradle": "[6.0.24,6.2)"}


@_register
class ForgeExporter(Exporter):
    def loader_name(self) -> str:
        return "forge"

    def export(self, project: ModProject, output_dir: Path) -> Path:
        root = output_dir / f"{project.mod_id}-forge"
        versions = _FORGE_VERSIONS.get(project.mc_version, _DEFAULT_FORGE)

        self._write_build_gradle(root, project, versions)
        self._write_gradle_properties(root, project)
        self._write_settings_gradle(root, project)
        self._write_mods_toml(root, project, versions)
        self._write_pack_mcmeta(root, project)
        self._write_mod_class(root, project)
        self._write_block_registry(root, project)
        self._write_item_registry(root, project)
        self._write_entity_registry(root, project)
        self._write_creative_tab(root, project)
        self._write_worldgen(root, project)
        self._write_recipes(root, project)
        self._write_loot_tables(root, project)
        self._write_tag_files(root / "src" / "main" / "resources" / "data", project)
        self._write_advancements(root / "src" / "main" / "resources" / "data", project)
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
    id 'net.minecraftforge.gradle' version '{versions["gradle"]}'
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
    minecraft 'net.minecraftforge:forge:{project.mc_version}-{versions["forge"]}'
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

    def _write_mods_toml(self, root: Path, project: ModProject, versions: dict) -> None:
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
modId="forge"
mandatory=true
versionRange="{loader_range}"
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
        if project.entities:
            w.line(f"{cls_name}Entities.register(modEventBus);")
        if project.blocks or project.items:
            w.line(f"{cls_name}CreativeTab.register(modEventBus);")
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

    def _write_creative_tab(self, root: Path, project: ModProject) -> None:
        if not project.blocks and not project.items:
            return
        pkg = project.java_package
        cls_name = project.java_class_name
        w = JavaWriter()
        w.set_package(pkg)
        w.add_import("net.minecraft.core.registries.Registries")
        w.add_import("net.minecraft.network.chat.Component")
        w.add_import("net.minecraft.world.item.CreativeModeTab")
        w.add_import("net.minecraft.world.item.ItemStack")
        w.add_import("net.minecraftforge.eventbus.api.IEventBus")
        w.add_import("net.minecraftforge.registries.DeferredRegister")
        w.add_import("net.minecraftforge.registries.RegistryObject")
        w.line()
        w.open_block(f"public class {cls_name}CreativeTab")
        w.line(f"public static final DeferredRegister<CreativeModeTab> TABS = "
               f"DeferredRegister.create(Registries.CREATIVE_MODE_TAB, {cls_name}.MOD_ID);")
        w.line()
        w.line(f'public static final RegistryObject<CreativeModeTab> TAB = TABS.register("creative_tab",')
        w.line(f"    () -> CreativeModeTab.builder()")
        w.line(f'        .title(Component.translatable("itemGroup.{project.mod_id}"))')
        if project.blocks:
            w.line(f"        .icon(() -> new ItemStack({cls_name}Blocks.{project.blocks[0].java_constant}.get()))")
        elif project.items:
            w.line(f"        .icon(() -> new ItemStack({cls_name}Items.{project.items[0].java_constant}.get()))")
        w.line("        .displayItems((params, output) -> {")
        for block in project.blocks:
            w.line(f"            output.accept({cls_name}Blocks.{block.java_constant}.get());")
        for item in project.items:
            w.line(f"            output.accept({cls_name}Items.{item.java_constant}.get());")
        w.line("        })")
        w.line("        .build());")
        w.line()
        w.open_block("public static void register(IEventBus modEventBus)")
        w.line("TABS.register(modEventBus);")
        w.close_block()
        w.close_block()

        pkg_path = pkg.replace(".", "/")
        self._write_file(root / "src" / "main" / "java" / pkg_path / f"{cls_name}CreativeTab.java", w.build())

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
                # Forge biome modifier JSON
                step = _feature_to_generation_step(feature.feature_type)
                self._write_json(
                    data / "forge" / "biome_modifier" / f"add_{feature.feature_id}.json",
                    {
                        "type": "forge:add_features",
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
            "net.minecraft.world.entity.EntityType",
            "net.minecraft.world.entity.MobCategory",
            "net.minecraft.world.item.Item",
            "net.minecraftforge.common.ForgeSpawnEggItem",
            "net.minecraftforge.eventbus.api.IEventBus",
            "net.minecraftforge.registries.DeferredRegister",
            "net.minecraftforge.registries.ForgeRegistries",
            "net.minecraftforge.registries.RegistryObject",
        )
        if any(e.attributes for e in project.entities):
            w.add_import(
                "net.minecraftforge.event.entity.EntityAttributeCreationEvent",
                "net.minecraftforge.eventbus.api.SubscribeEvent",
                "net.minecraftforge.fml.common.Mod",
            )
        w.line()
        w.open_block(f"public class {cls_name}Entities")
        w.field(
            "public static final", "DeferredRegister<EntityType<?>>", "ENTITY_TYPES",
            f"DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, {cls_name}.MOD_ID)",
        )
        w.field(
            "public static final", "DeferredRegister<Item>", "SPAWN_EGGS",
            f"DeferredRegister.create(ForgeRegistries.ITEMS, {cls_name}.MOD_ID)",
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
                "public static final", f"RegistryObject<EntityType<{entity.java_class_name}>>",
                entity.java_constant,
                f'ENTITY_TYPES.register("{entity.entity_id}", () -> {builder}.build("{entity.entity_id}"))',
            )
            w.field(
                "public static final", "RegistryObject<Item>",
                f"{entity.java_constant}_SPAWN_EGG",
                f'SPAWN_EGGS.register("{entity.entity_id}_spawn_egg", () -> new ForgeSpawnEggItem({entity.java_constant}, 0x333333, 0x999999, new Item.Properties()))',
            )
        w.line()
        w.open_block("public static void register(IEventBus eventBus)")
        w.line("ENTITY_TYPES.register(eventBus);")
        w.line("SPAWN_EGGS.register(eventBus);")
        w.close_block()

        if any(e.attributes for e in project.entities):
            w.line()
            w.annotation(f"Mod.EventBusSubscriber(modid = {cls_name}.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)")
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
