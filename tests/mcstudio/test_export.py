"""Tests for all export engines (Fabric, Forge, Data Pack)."""

import json
import tempfile
from pathlib import Path

import pytest

from mcstudio.model.project import ModProject
from mcstudio.model.block import Block, BlockMaterial
from mcstudio.model.item import Item, FoodProperties
from mcstudio.model.recipe import ShapedRecipe, ShapelessRecipe, SmeltingRecipe
from mcstudio.model.loot import LootTable, LootPool, LootEntry, LootCondition
from mcstudio.model.entity import EntityType, EntityBase, AIGoal, AIGoalType, EntityAttribute, SpawnRules, MobCategory
from mcstudio.model.worldgen import Biome, PlacedFeature, FeatureType, PlacementConfig
from mcstudio.export.base import export_project, EXPORTERS
from mcstudio.export.fabric import FabricExporter
from mcstudio.export.forge import ForgeExporter
from mcstudio.export.neoforge import NeoForgeExporter
from mcstudio.export.datapack import DataPackExporter


def _make_project() -> ModProject:
    """Create a test project with blocks, items, recipes, and loot tables."""
    p = ModProject(
        mod_id="testmod",
        name="Test Mod",
        description="A test mod for testing exports",
        authors=["Tester"],
        mc_version="1.21.4",
    )
    p.add_block(Block(
        block_id="magic_ore",
        material=BlockMaterial.STONE,
        hardness=4.0,
        resistance=10.0,
        luminance=7,
        requires_tool=True,
    ))
    p.add_item(Item(item_id="magic_gem", max_stack_size=16))
    p.add_item(Item(
        item_id="magic_berry",
        food=FoodProperties(nutrition=6, saturation=0.5),
    ))
    p.add_recipe(ShapedRecipe(
        recipe_id="magic_ore_from_gems",
        pattern=["GGG", "GGG", "GGG"],
        key={"G": "testmod:magic_gem"},
        result="testmod:magic_ore",
    ))
    p.add_recipe(SmeltingRecipe(
        recipe_id="magic_gem_from_ore",
        ingredient="testmod:magic_ore",
        result="testmod:magic_gem",
        experience=1.0,
    ))
    p.add_loot_table(LootTable.block_self_drop("magic_ore"))
    return p


class TestExporterRegistry:
    def test_available_loaders(self):
        assert "fabric" in EXPORTERS
        assert "forge" in EXPORTERS
        assert "neoforge" in EXPORTERS
        assert "datapack" in EXPORTERS

    def test_unknown_loader(self):
        p = _make_project()
        with pytest.raises(ValueError, match="Unknown loader"):
            export_project(p, "quilt", "/tmp")


class TestFabricExport:
    def test_generates_project(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            assert root.exists()
            assert (root / "build.gradle").exists()
            assert (root / "gradle.properties").exists()
            assert (root / "settings.gradle").exists()

    def test_fabric_mod_json(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            fmj = root / "src" / "main" / "resources" / "fabric.mod.json"
            assert fmj.exists()
            data = json.loads(fmj.read_text())
            assert data["id"] == "testmod"
            assert data["name"] == "Test Mod"
            assert "main" in data["entrypoints"]

    def test_mod_class(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            mod_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "Testmod.java"
            assert mod_java.exists()
            content = mod_java.read_text()
            assert "implements ModInitializer" in content
            assert 'MOD_ID = "testmod"' in content
            assert "TestmodBlocks.register()" in content
            assert "TestmodItems.register()" in content

    def test_block_registry(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            blocks_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "TestmodBlocks.java"
            assert blocks_java.exists()
            content = blocks_java.read_text()
            assert "MAGIC_ORE" in content
            assert "strength(4.0f, 10.0f)" in content
            assert "luminance" in content or "lightLevel" in content
            assert "requiresTool" in content

    def test_item_registry(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            items_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "TestmodItems.java"
            assert items_java.exists()
            content = items_java.read_text()
            assert "MAGIC_GEM" in content
            assert "MAGIC_BERRY" in content
            assert "FoodComponent" in content
            assert "nutrition(6)" in content

    def test_recipe_json(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            recipe_path = root / "src" / "main" / "resources" / "data" / "testmod" / "recipe" / "magic_ore_from_gems.json"
            assert recipe_path.exists()
            data = json.loads(recipe_path.read_text())
            assert data["type"] == "minecraft:crafting_shaped"
            assert data["pattern"] == ["GGG", "GGG", "GGG"]

    def test_loot_table_json(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            loot_path = root / "src" / "main" / "resources" / "data" / "testmod" / "loot_table" / "blocks" / "magic_ore.json"
            assert loot_path.exists()
            data = json.loads(loot_path.read_text())
            assert data["type"] == "minecraft:block"

    def test_loot_condition_params(self):
        """Test that condition_params flow through to exported loot JSON."""
        p = ModProject(mod_id="testmod", name="Test")
        lt = LootTable(table_id="blocks/ore", table_type="block")
        pool = lt.add_pool()
        pool.add_entry(LootEntry(
            item_id="diamond",
            conditions=[LootCondition.RANDOM_CHANCE, LootCondition.WITHOUT_SILK_TOUCH],
            condition_params={"random_chance": {"chance": 0.3}},
        ))
        p.add_loot_table(lt)
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            loot_path = root / "src" / "main" / "resources" / "data" / "testmod" / "loot_table" / "blocks" / "ore.json"
            data = json.loads(loot_path.read_text())
            conditions = data["pools"][0]["entries"][0]["conditions"]
            # random_chance with custom value
            rc = [c for c in conditions if c.get("condition") == "minecraft:random_chance"]
            assert len(rc) == 1
            assert rc[0]["chance"] == 0.3
            # without_silk_touch as inverted condition
            inv = [c for c in conditions if c.get("condition") == "minecraft:inverted"]
            assert len(inv) == 1
            assert inv[0]["term"]["condition"] == "minecraft:match_tool"

    def test_blockstate_and_models(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            assets = root / "src" / "main" / "resources" / "assets" / "testmod"
            assert (assets / "blockstates" / "magic_ore.json").exists()
            assert (assets / "models" / "block" / "magic_ore.json").exists()
            assert (assets / "models" / "item" / "magic_ore.json").exists()
            assert (assets / "models" / "item" / "magic_gem.json").exists()

    def test_placeholder_textures(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            assets = root / "src" / "main" / "resources" / "assets" / "testmod"
            block_tex = assets / "textures" / "block" / "magic_ore.png"
            item_tex = assets / "textures" / "item" / "magic_gem.png"
            assert block_tex.exists()
            assert item_tex.exists()
            # Verify it's a valid PNG (starts with PNG signature)
            assert block_tex.read_bytes()[:4] == b"\x89PNG"
            assert item_tex.read_bytes()[:4] == b"\x89PNG"


class TestForgeExport:
    def test_generates_project(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            assert root.exists()
            assert (root / "build.gradle").exists()
            assert (root / "settings.gradle").exists()

    def test_mods_toml(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            toml_path = root / "src" / "main" / "resources" / "META-INF" / "mods.toml"
            assert toml_path.exists()
            content = toml_path.read_text()
            assert 'modId="testmod"' in content
            assert 'displayName="Test Mod"' in content

    def test_mod_class(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            mod_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "Testmod.java"
            assert mod_java.exists()
            content = mod_java.read_text()
            assert "@Mod(" in content
            assert "DeferredRegister" not in content  # That's in the blocks class
            assert "modEventBus" in content

    def test_block_registry_uses_deferred_register(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            blocks_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "TestmodBlocks.java"
            content = blocks_java.read_text()
            assert "DeferredRegister" in content
            assert "RegistryObject<Block>" in content
            assert "MAGIC_ORE" in content
            assert "strength(4.0f, 10.0f)" in content

    def test_item_registry_uses_deferred_register(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            items_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "TestmodItems.java"
            content = items_java.read_text()
            assert "DeferredRegister" in content
            assert "RegistryObject<Item>" in content
            assert "FoodProperties" in content

    def test_recipe_json(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            # Forge uses "recipes" directory (plural)
            recipe_path = root / "src" / "main" / "resources" / "data" / "testmod" / "recipes" / "magic_ore_from_gems.json"
            assert recipe_path.exists()


class TestNeoForgeExport:
    def test_generates_project(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            assert root.exists()
            assert (root / "build.gradle").exists()
            assert (root / "settings.gradle").exists()

    def test_neoforge_mods_toml(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            toml_path = root / "src" / "main" / "resources" / "META-INF" / "neoforge.mods.toml"
            assert toml_path.exists()
            content = toml_path.read_text()
            assert 'modId="testmod"' in content
            assert 'modId="neoforge"' in content

    def test_mod_class(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            mod_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "Testmod.java"
            content = mod_java.read_text()
            assert "net.neoforged.fml.common.Mod" in content
            assert "IEventBus modEventBus" in content

    def test_block_registry_uses_deferred_block(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            blocks_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "TestmodBlocks.java"
            content = blocks_java.read_text()
            assert "DeferredRegister.Blocks" in content or "DeferredBlock" in content
            assert "createBlocks" in content
            assert "MAGIC_ORE" in content

    def test_item_registry(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            items_java = root / "src" / "main" / "java" / "com" / "testmod" / "testmod" / "TestmodItems.java"
            content = items_java.read_text()
            assert "DeferredRegister.Items" in content or "DeferredItem" in content
            assert "createItems" in content

    def test_recipe_json(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            recipe_path = root / "src" / "main" / "resources" / "data" / "testmod" / "recipe" / "magic_ore_from_gems.json"
            assert recipe_path.exists()


class TestDataPackExport:
    def test_generates_pack(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = DataPackExporter().export(p, Path(td))
            assert root.exists()
            assert (root / "pack.mcmeta").exists()

    def test_pack_mcmeta(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = DataPackExporter().export(p, Path(td))
            data = json.loads((root / "pack.mcmeta").read_text())
            assert data["pack"]["pack_format"] == 26

    def test_recipes(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = DataPackExporter().export(p, Path(td))
            recipe_path = root / "data" / "testmod" / "recipe" / "magic_ore_from_gems.json"
            assert recipe_path.exists()
            data = json.loads(recipe_path.read_text())
            assert "type" in data

    def test_loot_tables(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = DataPackExporter().export(p, Path(td))
            loot_path = root / "data" / "testmod" / "loot_table" / "blocks" / "magic_ore.json"
            assert loot_path.exists()


class TestExportDispatch:
    def test_fabric_dispatch(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = export_project(p, "fabric", td)
            assert "fabric" in root.name

    def test_forge_dispatch(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = export_project(p, "forge", td)
            assert "forge" in root.name

    def test_neoforge_dispatch(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = export_project(p, "neoforge", td)
            assert "neoforge" in root.name

    def test_datapack_dispatch(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = export_project(p, "datapack", td)
            assert "datapack" in root.name

    def test_case_insensitive(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = export_project(p, "FABRIC", td)
            assert root.exists()


class TestEmptyProject:
    def test_fabric_no_blocks(self):
        p = ModProject(mod_id="emptymod", name="Empty Mod")
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            mod_java = root / "src" / "main" / "java" / "com" / "emptymod" / "emptymod" / "Emptymod.java"
            content = mod_java.read_text()
            assert "EmptymodBlocks" not in content
            assert "EmptymodItems" not in content

    def test_forge_no_blocks(self):
        p = ModProject(mod_id="emptymod", name="Empty Mod")
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            mod_java = root / "src" / "main" / "java" / "com" / "emptymod" / "emptymod" / "Emptymod.java"
            content = mod_java.read_text()
            assert "EmptymodBlocks" not in content

    def test_neoforge_no_blocks(self):
        p = ModProject(mod_id="emptymod", name="Empty Mod")
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            mod_java = root / "src" / "main" / "java" / "com" / "emptymod" / "emptymod" / "Emptymod.java"
            content = mod_java.read_text()
            assert "EmptymodBlocks" not in content

    def test_datapack_no_recipes(self):
        p = ModProject(mod_id="emptymod", name="Empty Mod")
        with tempfile.TemporaryDirectory() as td:
            root = DataPackExporter().export(p, Path(td))
            assert (root / "pack.mcmeta").exists()
            # No data directory should be created
            assert not (root / "data" / "emptymod" / "recipe").exists()


def _make_entity_project() -> ModProject:
    """Create a project with entities for testing entity export."""
    p = ModProject(mod_id="entitymod", name="Entity Mod")
    p.add_entity(EntityType(
        entity_id="shadow_beast",
        base_class=EntityBase.MONSTER,
        width=1.2,
        height=2.0,
        attributes=[
            EntityAttribute("max_health", 40.0),
            EntityAttribute("attack_damage", 8.0),
            EntityAttribute("movement_speed", 0.3),
        ],
        goals=[
            AIGoal(AIGoalType.FLOAT_SWIM, priority=0),
            AIGoal(AIGoalType.MELEE_ATTACK, priority=1),
            AIGoal(AIGoalType.WANDER_RANDOMLY, priority=5),
            AIGoal(AIGoalType.LOOK_AT_PLAYER, priority=6),
        ],
        spawn_rules=SpawnRules(category=MobCategory.MONSTER, weight=5),
        fireproof=True,
    ))
    return p


class TestEntityExport:
    def test_fabric_entity_export(self):
        p = _make_entity_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            pkg_path = "src/main/java/com/entitymod/entitymod"

            # Entity class generated
            entity_java = root / pkg_path / "ShadowBeastEntity.java"
            assert entity_java.exists()
            content = entity_java.read_text()
            assert "extends Monster" in content
            assert "registerGoals" in content
            assert "createAttributes" in content

            # Renderer generated
            renderer = root / pkg_path / "client" / "ShadowBeastEntityRenderer.java"
            assert renderer.exists()

            # Entity registry
            entities_java = root / pkg_path / "EntitymodEntities.java"
            assert entities_java.exists()
            reg_content = entities_java.read_text()
            assert "SHADOW_BEAST" in reg_content
            assert "MobCategory.MONSTER" in reg_content
            assert "fireImmune()" in reg_content
            assert "SpawnEggItem" in reg_content
            assert "FabricDefaultAttributeRegistry" in reg_content

            # Mod class references entities
            mod_java = root / pkg_path / "Entitymod.java"
            content = mod_java.read_text()
            assert "EntitymodEntities.register()" in content

    def test_forge_entity_export(self):
        p = _make_entity_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            pkg_path = "src/main/java/com/entitymod/entitymod"

            entity_java = root / pkg_path / "ShadowBeastEntity.java"
            assert entity_java.exists()

            entities_java = root / pkg_path / "EntitymodEntities.java"
            assert entities_java.exists()
            content = entities_java.read_text()
            assert "DeferredRegister" in content
            assert "SHADOW_BEAST" in content
            assert "ForgeSpawnEggItem" in content
            assert "EntityAttributeCreationEvent" in content
            assert "fireImmune()" in content

            mod_java = root / pkg_path / "Entitymod.java"
            assert "EntitymodEntities.register(modEventBus)" in mod_java.read_text()

    def test_neoforge_entity_export(self):
        p = _make_entity_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            pkg_path = "src/main/java/com/entitymod/entitymod"

            entity_java = root / pkg_path / "ShadowBeastEntity.java"
            assert entity_java.exists()

            entities_java = root / pkg_path / "EntitymodEntities.java"
            assert entities_java.exists()
            content = entities_java.read_text()
            assert "DeferredHolder" in content
            assert "SHADOW_BEAST" in content
            assert "SpawnEggItem" in content
            assert "EntityAttributeCreationEvent" in content
            assert "fireImmune()" in content

            mod_java = root / pkg_path / "Entitymod.java"
            assert "EntitymodEntities.register(modEventBus)" in mod_java.read_text()

    def test_no_entity_no_registry(self):
        p = ModProject(mod_id="emptymod", name="Empty Mod")
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            mod_java = root / "src" / "main" / "java" / "com" / "emptymod" / "emptymod" / "Emptymod.java"
            assert "EmptymodEntities" not in mod_java.read_text()


def _make_worldgen_project() -> ModProject:
    """Create a project with biomes and features for testing worldgen export."""
    p = ModProject(mod_id="worldmod", name="World Mod")
    p.add_biome(Biome(
        biome_id="crystal_caves",
        temperature=0.3,
        humidity=0.8,
        sky_color="#6688CC",
        water_color="#2244AA",
        features=[
            PlacedFeature(
                feature_id="crystal_ore",
                feature_type=FeatureType.ORE,
                block="worldmod:crystal_ore",
                size=12,
                placement=PlacementConfig(count=4, height_min=0, height_max=64),
            ),
        ],
    ))
    return p


class TestWorldgenExport:
    def test_datapack_worldgen(self):
        p = _make_worldgen_project()
        with tempfile.TemporaryDirectory() as td:
            root = DataPackExporter().export(p, Path(td))
            data = root / "data" / "worldmod"
            biome_json = data / "worldgen" / "biome" / "crystal_caves.json"
            assert biome_json.exists()
            biome_data = json.loads(biome_json.read_text())
            assert biome_data["temperature"] == 0.3

            cf_json = data / "worldgen" / "configured_feature" / "crystal_ore.json"
            assert cf_json.exists()
            cf_data = json.loads(cf_json.read_text())
            assert cf_data["type"] == "minecraft:ore"

            pf_json = data / "worldgen" / "placed_feature" / "crystal_ore.json"
            assert pf_json.exists()

    def test_fabric_worldgen(self):
        p = _make_worldgen_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            res = root / "src" / "main" / "resources" / "data" / "worldmod"
            assert (res / "worldgen" / "biome" / "crystal_caves.json").exists()
            assert (res / "worldgen" / "configured_feature" / "crystal_ore.json").exists()
            assert (res / "worldgen" / "placed_feature" / "crystal_ore.json").exists()

            # Fabric biome modifications Java file (named after biome)
            pkg_path = "src/main/java/com/worldmod/worldmod"
            features_java = root / pkg_path / "CrystalCavesBiomeFeatures.java"
            assert features_java.exists()
            content = features_java.read_text()
            assert "BiomeModifications.addFeature" in content
            assert "crystal_ore" in content

    def test_forge_worldgen(self):
        p = _make_worldgen_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            res = root / "src" / "main" / "resources" / "data" / "worldmod"
            assert (res / "worldgen" / "biome" / "crystal_caves.json").exists()
            assert (res / "worldgen" / "configured_feature" / "crystal_ore.json").exists()
            assert (res / "worldgen" / "placed_feature" / "crystal_ore.json").exists()

            # Forge biome modifier JSON
            modifier_path = res / "forge" / "biome_modifier"
            assert modifier_path.exists()

    def test_neoforge_worldgen(self):
        p = _make_worldgen_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            res = root / "src" / "main" / "resources" / "data" / "worldmod"
            assert (res / "worldgen" / "biome" / "crystal_caves.json").exists()

            # NeoForge biome modifier JSON
            modifier_path = res / "neoforge" / "biome_modifier"
            assert modifier_path.exists()

    def test_no_biome_no_worldgen(self):
        p = ModProject(mod_id="emptymod", name="Empty Mod")
        with tempfile.TemporaryDirectory() as td:
            root = DataPackExporter().export(p, Path(td))
            assert not (root / "data" / "emptymod" / "worldgen").exists()


class TestLangExport:
    def test_fabric_lang_file(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            lang_path = root / "src" / "main" / "resources" / "assets" / "testmod" / "lang" / "en_us.json"
            assert lang_path.exists()
            lang = json.loads(lang_path.read_text())
            assert lang["block.testmod.magic_ore"] == "Magic Ore"
            assert lang["item.testmod.magic_gem"] == "Magic Gem"
            assert lang["item.testmod.magic_berry"] == "Magic Berry"

    def test_forge_lang_file(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = ForgeExporter().export(p, Path(td))
            lang_path = root / "src" / "main" / "resources" / "assets" / "testmod" / "lang" / "en_us.json"
            assert lang_path.exists()
            lang = json.loads(lang_path.read_text())
            assert "block.testmod.magic_ore" in lang

    def test_neoforge_lang_file(self):
        p = _make_project()
        with tempfile.TemporaryDirectory() as td:
            root = NeoForgeExporter().export(p, Path(td))
            lang_path = root / "src" / "main" / "resources" / "assets" / "testmod" / "lang" / "en_us.json"
            assert lang_path.exists()

    def test_entity_lang_entries(self):
        p = _make_entity_project()
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            lang_path = root / "src" / "main" / "resources" / "assets" / "entitymod" / "lang" / "en_us.json"
            assert lang_path.exists()
            lang = json.loads(lang_path.read_text())
            assert lang["entity.entitymod.shadow_beast"] == "Shadow Beast"
            assert lang["item.entitymod.shadow_beast_spawn_egg"] == "Shadow Beast Spawn Egg"

    def test_empty_project_no_lang(self):
        p = ModProject(mod_id="emptymod", name="Empty Mod")
        with tempfile.TemporaryDirectory() as td:
            root = FabricExporter().export(p, Path(td))
            lang_path = root / "src" / "main" / "resources" / "assets" / "emptymod" / "lang" / "en_us.json"
            assert not lang_path.exists()
