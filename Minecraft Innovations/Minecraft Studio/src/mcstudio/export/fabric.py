"""Fabric mod project exporter -- generates a complete Fabric Loom Gradle project."""

from __future__ import annotations

from pathlib import Path

from mcstudio.model.project import ModProject
from mcstudio.codegen.java import JavaWriter, to_java_string, to_pascal_case
from .base import Exporter, _register

# Fabric Loom Gradle versions tied to MC version
_FABRIC_VERSIONS = {
    "1.21.4": {"fabric_api": "0.114.0+1.21.4", "yarn": "1.21.4+build.8", "loader": "0.16.10", "loom": "1.9-SNAPSHOT"},
    "1.21.3": {"fabric_api": "0.110.5+1.21.3", "yarn": "1.21.3+build.4", "loader": "0.16.9", "loom": "1.9-SNAPSHOT"},
    "1.20.4": {"fabric_api": "0.97.0+1.20.4", "yarn": "1.20.4+build.3", "loader": "0.15.11", "loom": "1.7-SNAPSHOT"},
}
_DEFAULT_VERSIONS = {"fabric_api": "0.114.0+1.21.4", "yarn": "1.21.4+build.8", "loader": "0.16.10", "loom": "1.9-SNAPSHOT"}


@_register
class FabricExporter(Exporter):
    def loader_name(self) -> str:
        return "fabric"

    def export(self, project: ModProject, output_dir: Path) -> Path:
        root = output_dir / f"{project.mod_id}-fabric"
        versions = _FABRIC_VERSIONS.get(project.mc_version, _DEFAULT_VERSIONS)

        self._write_build_gradle(root, project, versions)
        self._write_gradle_properties(root, project, versions)
        self._write_settings_gradle(root, project)
        self._write_fabric_mod_json(root, project)
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
    id 'fabric-loom' version '{versions["loom"]}'
    id 'maven-publish'
}}

version = project.mod_version
group = project.maven_group

base {{
    archivesName = project.archives_base_name
}}

repositories {{
}}

dependencies {{
    minecraft "com.mojang:minecraft:${{project.minecraft_version}}"
    mappings "net.fabricmc:yarn:${{project.yarn_mappings}}:v2"
    modImplementation "net.fabricmc:fabric-loader:${{project.loader_version}}"
    modImplementation "net.fabricmc.fabric-api:fabric-api:${{project.fabric_version}}"
}}

processResources {{
    inputs.property "version", project.version
    filteringCharset "UTF-8"

    filesMatching("fabric.mod.json") {{
        expand "version": project.version
    }}
}}

tasks.withType(JavaCompile).configureEach {{
    it.options.release = 21
}}

java {{
    withSourcesJar()
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}}
"""
        self._write_file(root / "build.gradle", content)

    def _write_gradle_properties(self, root: Path, project: ModProject, versions: dict) -> None:
        content = f"""org.gradle.jvmargs=-Xmx1G
minecraft_version={project.mc_version}
yarn_mappings={versions["yarn"]}
loader_version={versions["loader"]}
mod_version={project.version}
maven_group=com.{project.mod_id}
archives_base_name={project.mod_id}
fabric_version={versions["fabric_api"]}
"""
        self._write_file(root / "gradle.properties", content)

    def _write_settings_gradle(self, root: Path, project: ModProject) -> None:
        self._write_file(root / "settings.gradle", f'pluginManagement {{\n    repositories {{\n        maven {{ url = "https://maven.fabricmc.net/" }}\n        mavenCentral()\n        gradlePluginPortal()\n    }}\n}}\n')

    def _write_fabric_mod_json(self, root: Path, project: ModProject) -> None:
        mod_json = {
            "schemaVersion": 1,
            "id": project.mod_id,
            "version": "${version}",
            "name": project.name,
            "description": project.description,
            "authors": project.authors,
            "contact": {},
            "license": project.license,
            "environment": "*",
            "entrypoints": {
                "main": [f"{project.java_package}.{project.java_class_name}"],
            },
            "depends": {
                "fabricloader": ">=0.16.0",
                "minecraft": f"~{project.mc_version}",
                "java": ">=21",
                "fabric-api": "*",
            },
        }
        res = root / "src" / "main" / "resources"
        self._write_json(res / "fabric.mod.json", mod_json)

    def _write_mod_class(self, root: Path, project: ModProject) -> None:
        pkg = project.java_package
        cls_name = project.java_class_name
        w = JavaWriter()
        w.set_package(pkg)
        w.add_import("net.fabricmc.api.ModInitializer")
        w.add_import("org.slf4j.Logger")
        w.add_import("org.slf4j.LoggerFactory")
        w.line()
        w.open_block(f"public class {cls_name} implements ModInitializer")
        w.field("public static final", "String", "MOD_ID", to_java_string(project.mod_id))
        w.field("public static final", "Logger", "LOGGER", f"LoggerFactory.getLogger(MOD_ID)")
        w.line()
        w.annotation("Override")
        w.open_block("public void onInitialize()")
        w.line(f"LOGGER.info(\"Initializing {project.name}\");")
        if project.blocks:
            w.line(f"{cls_name}Blocks.register();")
        if project.items:
            w.line(f"{cls_name}Items.register();")
        if project.entities:
            w.line(f"{cls_name}Entities.register();")
        for biome in project.biomes:
            biome_cls = to_pascal_case(biome.biome_id)
            w.line(f"{biome_cls}BiomeFeatures.register();")
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
            "net.minecraft.block.AbstractBlock",
            "net.minecraft.block.Block",
            "net.minecraft.item.BlockItem",
            "net.minecraft.item.Item",
            "net.minecraft.registry.Registries",
            "net.minecraft.registry.Registry",
            "net.minecraft.util.Identifier",
        )
        w.line()
        w.open_block(f"public class {cls_name}Blocks")
        for block in project.blocks:
            props = f"AbstractBlock.Settings.create().strength({block.hardness}f, {block.resistance}f)"
            if block.luminance:
                props += f".luminance(state -> {block.luminance})"
            if block.no_collision:
                props += ".noCollision()"
            if block.requires_tool:
                props += ".requiresTool()"
            w.field(
                "public static final", "Block", block.java_constant,
                f"new Block({props})",
            )
        w.line()
        w.open_block("public static void register()")
        for block in project.blocks:
            rl = f'Identifier.of({cls_name}.MOD_ID, "{block.block_id}")'
            w.line(f"Registry.register(Registries.BLOCK, {rl}, {block.java_constant});")
            if block.has_block_item:
                w.line(f"Registry.register(Registries.ITEM, {rl}, new BlockItem({block.java_constant}, new Item.Settings()));")
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
            "net.minecraft.item.Item",
            "net.minecraft.registry.Registries",
            "net.minecraft.registry.Registry",
            "net.minecraft.util.Identifier",
        )
        if any(i.is_food for i in project.items):
            w.add_import("net.minecraft.component.type.FoodComponent")
        w.line()
        w.open_block(f"public class {cls_name}Items")
        for item in project.items:
            settings = "new Item.Settings()"
            if item.max_stack_size != 64:
                settings += f".maxCount({item.max_stack_size})"
            if item.fireproof:
                settings += ".fireproof()"
            if item.is_food:
                food = item.food
                food_builder = (
                    f"new FoodComponent.Builder()"
                    f".nutrition({food.nutrition}).saturationModifier({food.saturation}f)"
                )
                if food.is_meat:
                    food_builder += ".meat()"
                if food.can_always_eat:
                    food_builder += ".alwaysEdible()"
                food_builder += ".build()"
                settings += f".food({food_builder})"
            w.field("public static final", "Item", item.java_constant, f"new Item({settings})")
        w.line()
        w.open_block("public static void register()")
        for item in project.items:
            rl = f'Identifier.of({cls_name}.MOD_ID, "{item.item_id}")'
            w.line(f"Registry.register(Registries.ITEM, {rl}, {item.java_constant});")
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
            generate_fabric_biome_modifications,
        )
        pkg = project.java_package
        cls_name = project.java_class_name
        pkg_path = pkg.replace(".", "/")
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
            # Fabric biome modifications class
            code = generate_fabric_biome_modifications(biome, pkg, cls_name)
            biome_cls = to_pascal_case(biome.biome_id)
            self._write_file(
                root / "src" / "main" / "java" / pkg_path / f"{biome_cls}BiomeFeatures.java", code,
            )

    def _write_entity_registry(self, root: Path, project: ModProject) -> None:
        if not project.entities:
            return
        from mcstudio.codegen.entity import generate_entity_class, generate_entity_renderer
        pkg = project.java_package
        cls_name = project.java_class_name
        pkg_path = pkg.replace(".", "/")

        # Write individual entity classes
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

        # Write entity registry class
        w = JavaWriter()
        w.set_package(pkg)
        w.add_import(
            "net.minecraft.core.Registry",
            "net.minecraft.core.registries.BuiltInRegistries",
            "net.minecraft.resources.ResourceLocation",
            "net.minecraft.world.entity.EntityType",
            "net.minecraft.world.entity.MobCategory",
            "net.minecraft.world.item.Item",
            "net.minecraft.world.item.SpawnEggItem",
        )
        if any(e.attributes for e in project.entities):
            w.add_import(
                "net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry",
            )
        w.line()
        w.open_block(f"public class {cls_name}Entities")
        for entity in project.entities:
            cat = entity.spawn_rules.category.value.upper() if entity.spawn_rules else "CREATURE"
            builder = (
                f'EntityType.Builder.of({entity.java_class_name}::new, MobCategory.{cat})'
                f'.sized({entity.width}f, {entity.height}f)'
            )
            if entity.fireproof:
                builder += ".fireImmune()"
            w.field(
                "public static final", f"EntityType<{entity.java_class_name}>",
                entity.java_constant,
                f'{builder}.build()',
            )
        w.line()
        w.open_block("public static void register()")
        for entity in project.entities:
            rl = f'ResourceLocation.fromNamespaceAndPath({cls_name}.MOD_ID, "{entity.entity_id}")'
            w.line(f"Registry.register(BuiltInRegistries.ENTITY_TYPE, {rl}, {entity.java_constant});")
            # Spawn egg
            w.line(f'Registry.register(BuiltInRegistries.ITEM, ResourceLocation.fromNamespaceAndPath({cls_name}.MOD_ID, "{entity.entity_id}_spawn_egg"), new SpawnEggItem({entity.java_constant}, 0x333333, 0x999999, new Item.Properties()));')
            # Attributes
            if entity.attributes:
                w.line(f"FabricDefaultAttributeRegistry.register({entity.java_constant}, {entity.java_class_name}.createAttributes());")
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
            # Blockstate JSON
            blockstate = {
                "variants": {
                    "": {"model": f"{project.mod_id}:block/{block.block_id}"}
                }
            }
            self._write_json(
                res / "assets" / project.mod_id / "blockstates" / f"{block.block_id}.json",
                blockstate,
            )
            # Block model JSON (simple cube)
            block_model = {
                "parent": "minecraft:block/cube_all",
                "textures": {
                    "all": f"{project.mod_id}:block/{block.block_id}"
                }
            }
            self._write_json(
                res / "assets" / project.mod_id / "models" / "block" / f"{block.block_id}.json",
                block_model,
            )
            # Block item model
            if block.has_block_item:
                item_model = {
                    "parent": f"{project.mod_id}:block/{block.block_id}"
                }
                self._write_json(
                    res / "assets" / project.mod_id / "models" / "item" / f"{block.block_id}.json",
                    item_model,
                )
        # Item models
        for item in project.items:
            item_model = {
                "parent": "minecraft:item/generated",
                "textures": {
                    "layer0": f"{project.mod_id}:item/{item.item_id}"
                }
            }
            self._write_json(
                res / "assets" / project.mod_id / "models" / "item" / f"{item.item_id}.json",
                item_model,
            )
