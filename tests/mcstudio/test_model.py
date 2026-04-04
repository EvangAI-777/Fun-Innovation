"""Tests for the mod project data model."""

import json
import tempfile
from pathlib import Path

import pytest

from mcstudio.model.project import ModProject
from mcstudio.model.block import Block, BlockMaterial, BlockDrop
from mcstudio.model.item import Item, FoodProperties, ToolProperties, ToolTier, CreativeTab
from mcstudio.model.recipe import (
    ShapedRecipe, ShapelessRecipe, SmeltingRecipe, BlastingRecipe,
    SmokingRecipe, StonecuttingRecipe, SmithingRecipe, recipe_from_dict,
)
from mcstudio.model.advancement import (
    Advancement, AdvancementDisplay, AdvancementCriterion, AdvancementFrame,
    INVENTORY_CHANGED, PLACED_BLOCK, KILLED_ENTITY,
)
from mcstudio.model.loot import LootTable, LootPool, LootEntry, LootCondition, LootFunction
from mcstudio.model.entity import (
    EntityType, EntityBase, AIGoal, AIGoalType, EntityAttribute, SpawnRules, MobCategory,
)
from mcstudio.model.worldgen import Biome, PlacedFeature, PlacementConfig, FeatureType, HeightRangeType


# --- ModProject ---

class TestModProject:
    def test_create(self):
        p = ModProject(mod_id="cool_mod", name="Cool Mod")
        assert p.mod_id == "cool_mod"
        assert p.name == "Cool Mod"
        assert p.version == "1.0.0"

    def test_invalid_mod_id(self):
        with pytest.raises(ValueError, match="Invalid mod ID"):
            ModProject(mod_id="Bad-Mod!", name="Nope")

    def test_mod_id_must_start_with_letter(self):
        with pytest.raises(ValueError):
            ModProject(mod_id="123mod", name="Nope")

    def test_mod_id_no_uppercase(self):
        with pytest.raises(ValueError):
            ModProject(mod_id="CoolMod", name="Nope")

    def test_java_names(self):
        p = ModProject(mod_id="cool_mod", name="Cool Mod")
        assert p.java_package == "com.cool_mod.cool_mod"
        assert p.java_class_name == "CoolMod"

    def test_resource_location(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        assert p.resource_location("custom_ore") == "mymod:custom_ore"

    def test_add_block(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        b = p.add_block(Block(block_id="test_block"))
        assert len(p.blocks) == 1
        assert p.get_block("test_block") is b

    def test_duplicate_block(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        p.add_block(Block(block_id="ore"))
        with pytest.raises(ValueError, match="Duplicate"):
            p.add_block(Block(block_id="ore"))

    def test_add_item(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        i = p.add_item(Item(item_id="gem"))
        assert len(p.items) == 1
        assert p.get_item("gem") is i

    def test_duplicate_item(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        p.add_item(Item(item_id="gem"))
        with pytest.raises(ValueError, match="Duplicate"):
            p.add_item(Item(item_id="gem"))

    def test_duplicate_recipe(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        p.add_recipe(SmeltingRecipe(recipe_id="smelt_gem", ingredient="mymod:ore", result="mymod:gem"))
        with pytest.raises(ValueError, match="Duplicate recipe"):
            p.add_recipe(SmeltingRecipe(recipe_id="smelt_gem", ingredient="mymod:ore", result="mymod:gem"))

    def test_get_missing(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        assert p.get_block("nope") is None
        assert p.get_item("nope") is None


class TestProjectSerialization:
    def _make_project(self) -> ModProject:
        p = ModProject(mod_id="testmod", name="Test Mod", description="A test")
        p.add_block(Block(block_id="custom_ore", material=BlockMaterial.STONE, hardness=3.0))
        p.add_item(Item(item_id="custom_gem", max_stack_size=16))
        p.add_recipe(ShapedRecipe(
            recipe_id="gem_block",
            pattern=["GGG", "GGG", "GGG"],
            key={"G": "testmod:custom_gem"},
            result="testmod:custom_ore",
        ))
        p.add_loot_table(LootTable.block_self_drop("custom_ore"))
        return p

    def test_to_dict(self):
        p = self._make_project()
        d = p.to_dict()
        assert d["mod_id"] == "testmod"
        assert len(d["blocks"]) == 1
        assert len(d["items"]) == 1
        assert len(d["recipes"]) == 1
        assert len(d["loot_tables"]) == 1

    def test_save_and_load(self):
        p = self._make_project()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        p.save(path)
        loaded = ModProject.load(path)
        assert loaded.mod_id == "testmod"
        assert len(loaded.blocks) == 1
        assert len(loaded.items) == 1
        assert len(loaded.recipes) == 1
        assert loaded.blocks[0].block_id == "custom_ore"
        assert loaded.blocks[0].hardness == 3.0
        path.unlink()

    def test_json_roundtrip(self):
        p = self._make_project()
        d = p.to_dict()
        json_str = json.dumps(d)
        loaded = json.loads(json_str)
        assert loaded["mod_id"] == "testmod"


# --- Block ---

class TestBlock:
    def test_defaults(self):
        b = Block(block_id="stone_block")
        assert b.material == BlockMaterial.STONE
        assert b.hardness == 1.5
        assert b.resistance == 6.0
        assert b.luminance == 0

    def test_custom_properties(self):
        b = Block(
            block_id="glowstone_ore",
            material=BlockMaterial.STONE,
            hardness=3.0,
            resistance=10.0,
            luminance=12,
            requires_tool=True,
        )
        assert b.luminance == 12
        assert b.requires_tool is True

    def test_invalid_block_id(self):
        with pytest.raises(ValueError, match="Invalid block ID"):
            Block(block_id="Bad Block!")
        with pytest.raises(ValueError, match="Invalid block ID"):
            Block(block_id="UPPER")
        with pytest.raises(ValueError, match="Invalid block ID"):
            Block(block_id="1starts_with_number")

    def test_invalid_luminance(self):
        with pytest.raises(ValueError):
            Block(block_id="bad", luminance=16)
        with pytest.raises(ValueError):
            Block(block_id="bad", luminance=-1)

    def test_invalid_hardness(self):
        with pytest.raises(ValueError):
            Block(block_id="bad", hardness=-2.0)

    def test_java_names(self):
        b = Block(block_id="custom_ore")
        assert b.java_class_name == "CustomOreBlock"
        assert b.java_constant == "CUSTOM_ORE"

    def test_block_drop(self):
        drop = BlockDrop(item_id="diamond", count_min=1, count_max=3)
        assert drop.item_id == "diamond"
        d = drop.to_dict()
        loaded = BlockDrop.from_dict(d)
        assert loaded.count_max == 3

    def test_serialization(self):
        b = Block(block_id="test", material=BlockMaterial.WOOD, luminance=5)
        d = b.to_dict()
        loaded = Block.from_dict(d)
        assert loaded.block_id == "test"
        assert loaded.material == BlockMaterial.WOOD
        assert loaded.luminance == 5

    def test_all_materials(self):
        for mat in BlockMaterial:
            b = Block(block_id="test", material=mat)
            assert b.material == mat


# --- Item ---

class TestItem:
    def test_defaults(self):
        i = Item(item_id="gem")
        assert i.max_stack_size == 64
        assert not i.is_food
        assert not i.is_tool

    def test_food(self):
        food = FoodProperties(nutrition=8, saturation=0.8, is_meat=True)
        i = Item(item_id="steak", food=food)
        assert i.is_food
        assert i.food.nutrition == 8

    def test_tool(self):
        tool = ToolProperties(tier=ToolTier.DIAMOND, durability=1561)
        i = Item(item_id="pick", tool=tool, max_stack_size=1)
        assert i.is_tool
        assert i.tool.tier == ToolTier.DIAMOND

    def test_invalid_item_id(self):
        with pytest.raises(ValueError, match="Invalid item ID"):
            Item(item_id="Bad Item!")
        with pytest.raises(ValueError, match="Invalid item ID"):
            Item(item_id="UPPER")

    def test_invalid_stack_size(self):
        with pytest.raises(ValueError):
            Item(item_id="bad", max_stack_size=0)
        with pytest.raises(ValueError):
            Item(item_id="bad", max_stack_size=65)

    def test_serialization(self):
        food = FoodProperties(nutrition=4, saturation=0.3)
        i = Item(item_id="berry", food=food, fireproof=True)
        d = i.to_dict()
        loaded = Item.from_dict(d)
        assert loaded.item_id == "berry"
        assert loaded.is_food
        assert loaded.food.nutrition == 4
        assert loaded.fireproof is True


# --- Recipes ---

class TestRecipes:
    def test_shaped_recipe(self):
        r = ShapedRecipe(
            recipe_id="diamond_sword",
            pattern=[" D ", " D ", " S "],
            key={"D": "minecraft:diamond", "S": "minecraft:stick"},
            result="minecraft:diamond_sword",
        )
        assert r.recipe_type() == "crafting_shaped"
        assert len(r.pattern) == 3

    def test_shaped_invalid_pattern(self):
        with pytest.raises(ValueError):
            ShapedRecipe(recipe_id="bad", pattern=[], key={}, result="x")
        with pytest.raises(ValueError):
            ShapedRecipe(recipe_id="bad", pattern=["ABCD"], key={}, result="x")

    def test_shapeless_recipe(self):
        r = ShapelessRecipe(
            recipe_id="flint_and_steel",
            ingredients=["minecraft:iron_ingot", "minecraft:flint"],
            result="minecraft:flint_and_steel",
        )
        assert r.recipe_type() == "crafting_shapeless"

    def test_shapeless_invalid_count(self):
        with pytest.raises(ValueError):
            ShapelessRecipe(recipe_id="bad", ingredients=[], result="x")

    def test_smelting_recipe(self):
        r = SmeltingRecipe(
            recipe_id="iron_ingot",
            ingredient="minecraft:raw_iron",
            result="minecraft:iron_ingot",
            experience=0.7,
        )
        assert r.recipe_type() == "smelting"
        assert r.cooking_time == 200

    def test_blasting_recipe(self):
        r = BlastingRecipe(
            recipe_id="iron_ingot_blast",
            ingredient="minecraft:raw_iron",
            result="minecraft:iron_ingot",
        )
        assert r.recipe_type() == "blasting"
        assert r.cooking_time == 100

    def test_smoking_recipe(self):
        r = SmokingRecipe(
            recipe_id="cooked_beef",
            ingredient="minecraft:beef",
            result="minecraft:cooked_beef",
        )
        assert r.recipe_type() == "smoking"

    def test_stonecutting_recipe(self):
        r = StonecuttingRecipe(
            recipe_id="stone_bricks",
            ingredient="minecraft:stone",
            result="minecraft:stone_bricks",
        )
        assert r.recipe_type() == "stonecutting"

    def test_smithing_recipe(self):
        r = SmithingRecipe(
            recipe_id="netherite_sword",
            template="minecraft:netherite_upgrade_smithing_template",
            base="minecraft:diamond_sword",
            addition="minecraft:netherite_ingot",
            result="minecraft:netherite_sword",
        )
        assert r.recipe_type() == "smithing_transform"

    def test_recipe_serialization(self):
        r = ShapedRecipe(
            recipe_id="test",
            pattern=["AB", "BA"],
            key={"A": "minecraft:stone", "B": "minecraft:dirt"},
            result="minecraft:cobblestone",
            count=4,
        )
        d = r.to_dict()
        loaded = recipe_from_dict(d)
        assert loaded.recipe_id == "test"
        assert loaded.count == 4

    def test_all_recipe_types_roundtrip(self):
        recipes = [
            ShapedRecipe("r1", ["A"], {"A": "x"}, "y"),
            ShapelessRecipe("r2", ["x"], "y"),
            SmeltingRecipe("r3", "x", "y"),
            BlastingRecipe("r4", "x", "y"),
            SmokingRecipe("r5", "x", "y"),
            StonecuttingRecipe("r6", "x", "y"),
            SmithingRecipe("r7", "t", "b", "a", "r"),
        ]
        for recipe in recipes:
            d = recipe.to_dict()
            loaded = recipe_from_dict(d)
            assert loaded.recipe_id == recipe.recipe_id

    def test_unknown_recipe_type(self):
        with pytest.raises(ValueError, match="Unknown recipe type"):
            recipe_from_dict({"type": "fake", "recipe_id": "x"})


# --- Loot Tables ---

class TestLootTables:
    def test_self_drop(self):
        lt = LootTable.block_self_drop("custom_ore")
        assert lt.table_id == "blocks/custom_ore"
        assert lt.table_type == "block"
        assert len(lt.pools) == 1
        assert len(lt.pools[0].entries) == 1
        assert lt.pools[0].entries[0].item_id == "custom_ore"

    def test_custom_pool(self):
        lt = LootTable(table_id="chests/dungeon", table_type="chest")
        pool = lt.add_pool()
        pool.rolls_min = 2
        pool.rolls_max = 5
        pool.add_entry(LootEntry(item_id="diamond", weight=1, count_min=1, count_max=3))
        pool.add_entry(LootEntry(item_id="gold_ingot", weight=5))
        assert len(pool.entries) == 2

    def test_conditions_and_functions(self):
        entry = LootEntry(
            item_id="coal",
            conditions=[LootCondition.SURVIVES_EXPLOSION],
            functions=[LootFunction.SET_COUNT],
        )
        assert LootCondition.SURVIVES_EXPLOSION in entry.conditions
        assert LootFunction.SET_COUNT in entry.functions

    def test_condition_params(self):
        entry = LootEntry(
            item_id="diamond",
            conditions=[LootCondition.RANDOM_CHANCE],
            condition_params={"random_chance": {"chance": 0.3}},
        )
        assert entry.condition_params["random_chance"]["chance"] == 0.3
        d = entry.to_dict()
        assert "condition_params" in d
        loaded = LootEntry.from_dict(d)
        assert loaded.condition_params["random_chance"]["chance"] == 0.3

    def test_condition_params_empty_omitted(self):
        entry = LootEntry(item_id="coal")
        d = entry.to_dict()
        assert "condition_params" not in d

    def test_serialization(self):
        lt = LootTable.block_self_drop("ore")
        d = lt.to_dict()
        loaded = LootTable.from_dict(d)
        assert loaded.table_id == "blocks/ore"
        assert len(loaded.pools) == 1
        assert loaded.pools[0].entries[0].item_id == "ore"


# --- Entities ---

class TestEntityType:
    def test_defaults(self):
        e = EntityType(entity_id="custom_mob")
        assert e.base_class == EntityBase.MOB
        assert e.width == 0.6
        assert e.height == 1.8
        assert e.can_swim is True

    def test_custom_entity(self):
        e = EntityType(
            entity_id="fire_elemental",
            base_class=EntityBase.MONSTER,
            width=1.2,
            height=2.4,
            fireproof=True,
            attributes=[
                EntityAttribute("max_health", 40.0),
                EntityAttribute("attack_damage", 8.0),
            ],
            goals=[
                AIGoal(AIGoalType.FLOAT_SWIM, priority=0),
                AIGoal(AIGoalType.MELEE_ATTACK, priority=1, params={"speed": 1.2}),
                AIGoal(AIGoalType.WANDER_RANDOMLY, priority=5),
            ],
            spawn_rules=SpawnRules(
                category=MobCategory.MONSTER,
                weight=5,
                min_group=1,
                max_group=2,
                biomes=["minecraft:nether_wastes"],
            ),
            loot_table_id="entities/fire_elemental",
        )
        assert e.base_class == EntityBase.MONSTER
        assert e.fireproof is True
        assert len(e.attributes) == 2
        assert len(e.goals) == 3
        assert e.spawn_rules.category == MobCategory.MONSTER
        assert e.loot_table_id == "entities/fire_elemental"

    def test_invalid_entity_id(self):
        with pytest.raises(ValueError, match="Invalid entity ID"):
            EntityType(entity_id="Bad Entity!")

    def test_invalid_dimensions(self):
        with pytest.raises(ValueError, match="Width must be > 0"):
            EntityType(entity_id="bad_mob", width=0)
        with pytest.raises(ValueError, match="Height must be > 0"):
            EntityType(entity_id="bad_mob", height=-1)

    def test_java_names(self):
        e = EntityType(entity_id="fire_elemental")
        assert e.java_class_name == "FireElementalEntity"
        assert e.java_constant == "FIRE_ELEMENTAL"

    def test_serialization(self):
        e = EntityType(
            entity_id="test_mob",
            base_class=EntityBase.ANIMAL,
            attributes=[EntityAttribute("max_health", 20.0)],
            goals=[AIGoal(AIGoalType.WANDER_RANDOMLY, priority=5)],
            spawn_rules=SpawnRules(weight=8, biomes=["minecraft:plains"]),
        )
        d = e.to_dict()
        loaded = EntityType.from_dict(d)
        assert loaded.entity_id == "test_mob"
        assert loaded.base_class == EntityBase.ANIMAL
        assert len(loaded.attributes) == 1
        assert loaded.attributes[0].value == 20.0
        assert len(loaded.goals) == 1
        assert loaded.goals[0].goal_type == AIGoalType.WANDER_RANDOMLY
        assert loaded.spawn_rules.biomes == ["minecraft:plains"]

    def test_all_base_classes(self):
        for base in EntityBase:
            e = EntityType(entity_id="test", base_class=base)
            assert e.base_class == base

    def test_all_goal_types(self):
        for gt in AIGoalType:
            goal = AIGoal(goal_type=gt, priority=0)
            d = goal.to_dict()
            loaded = AIGoal.from_dict(d)
            assert loaded.goal_type == gt


class TestProjectEntities:
    def test_add_entity(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        e = p.add_entity(EntityType(entity_id="custom_mob"))
        assert len(p.entities) == 1
        assert p.get_entity("custom_mob") is e

    def test_duplicate_entity(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        p.add_entity(EntityType(entity_id="custom_mob"))
        with pytest.raises(ValueError, match="Duplicate entity"):
            p.add_entity(EntityType(entity_id="custom_mob"))

    def test_entity_serialization_roundtrip(self):
        p = ModProject(mod_id="testmod", name="Test")
        p.add_entity(EntityType(
            entity_id="test_mob",
            attributes=[EntityAttribute("max_health", 30.0)],
            goals=[AIGoal(AIGoalType.MELEE_ATTACK, priority=1)],
        ))
        d = p.to_dict()
        assert len(d["entities"]) == 1

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            p.save(f.name)
            loaded = ModProject.load(f.name)
        assert len(loaded.entities) == 1
        assert loaded.entities[0].entity_id == "test_mob"
        assert loaded.entities[0].attributes[0].value == 30.0


# --- World Gen ---

class TestBiome:
    def test_defaults(self):
        b = Biome(biome_id="crystal_fields")
        assert b.temperature == 0.5
        assert b.humidity == 0.5
        assert b.sky_color == "#78A7FF"
        assert len(b.features) == 0

    def test_custom_biome(self):
        b = Biome(
            biome_id="volcanic_wastes",
            temperature=2.0,
            humidity=0.0,
            sky_color="#FF4400",
            fog_color="#AA2200",
            grass_color="#553300",
            features=[
                PlacedFeature(
                    feature_id="magma_ore",
                    feature_type=FeatureType.ORE,
                    block="minecraft:magma_block",
                    size=12,
                    placement=PlacementConfig(count=15, height_min=0, height_max=64),
                ),
            ],
        )
        assert b.temperature == 2.0
        assert len(b.features) == 1
        assert b.features[0].size == 12

    def test_invalid_biome_id(self):
        with pytest.raises(ValueError, match="Invalid biome ID"):
            Biome(biome_id="Bad Biome!")

    def test_serialization(self):
        b = Biome(
            biome_id="test_biome",
            temperature=1.5,
            grass_color="#00FF00",
            features=[
                PlacedFeature(
                    feature_id="test_ore",
                    feature_type=FeatureType.ORE,
                    block="mymod:test_ore",
                    placement=PlacementConfig(count=4, rarity=3),
                ),
            ],
        )
        d = b.to_dict()
        assert d["grass_color"] == "#00FF00"
        loaded = Biome.from_dict(d)
        assert loaded.biome_id == "test_biome"
        assert loaded.temperature == 1.5
        assert loaded.grass_color == "#00FF00"
        assert len(loaded.features) == 1
        assert loaded.features[0].placement.rarity == 3

    def test_all_feature_types(self):
        for ft in FeatureType:
            f = PlacedFeature(feature_id="test", feature_type=ft)
            d = f.to_dict()
            loaded = PlacedFeature.from_dict(d)
            assert loaded.feature_type == ft

    def test_placement_config_roundtrip(self):
        pc = PlacementConfig(
            count=20,
            height_min=-32,
            height_max=128,
            height_range_type=HeightRangeType.TRIANGLE,
            rarity=5,
        )
        d = pc.to_dict()
        loaded = PlacementConfig.from_dict(d)
        assert loaded.count == 20
        assert loaded.height_range_type == HeightRangeType.TRIANGLE
        assert loaded.rarity == 5


class TestProjectBiomes:
    def test_add_biome(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        b = p.add_biome(Biome(biome_id="crystal_fields"))
        assert len(p.biomes) == 1
        assert p.get_biome("crystal_fields") is b

    def test_duplicate_biome(self):
        p = ModProject(mod_id="mymod", name="My Mod")
        p.add_biome(Biome(biome_id="crystal_fields"))
        with pytest.raises(ValueError, match="Duplicate biome"):
            p.add_biome(Biome(biome_id="crystal_fields"))

    def test_biome_serialization_roundtrip(self):
        p = ModProject(mod_id="testmod", name="Test")
        p.add_biome(Biome(
            biome_id="test_biome",
            temperature=1.2,
            features=[PlacedFeature(feature_id="test_ore")],
        ))
        d = p.to_dict()
        assert len(d["biomes"]) == 1

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            p.save(f.name)
            loaded = ModProject.load(f.name)
        assert len(loaded.biomes) == 1
        assert loaded.biomes[0].biome_id == "test_biome"
        assert loaded.biomes[0].temperature == 1.2


class TestAdvancement:
    def test_defaults(self):
        display = AdvancementDisplay(
            icon="minecraft:diamond",
            title="First Diamond",
            description="Mine your first diamond",
        )
        adv = Advancement(advancement_id="first_diamond", display=display)
        assert adv.parent is None
        assert adv.display.frame == AdvancementFrame.TASK
        assert adv.display.show_toast is True

    def test_with_criteria(self):
        display = AdvancementDisplay(
            icon="minecraft:diamond",
            title="Diamond!",
            description="Get a diamond",
            frame=AdvancementFrame.CHALLENGE,
        )
        adv = Advancement(
            advancement_id="get_diamond",
            display=display,
            criteria=[
                AdvancementCriterion(
                    name="has_diamond",
                    trigger=INVENTORY_CHANGED,
                    conditions={"items": [{"items": "minecraft:diamond"}]},
                )
            ],
        )
        assert len(adv.criteria) == 1
        assert adv.criteria[0].trigger == INVENTORY_CHANGED

    def test_invalid_id(self):
        display = AdvancementDisplay(icon="minecraft:stone", title="T", description="D")
        with pytest.raises(ValueError, match="Invalid advancement ID"):
            Advancement(advancement_id="UPPER_CASE", display=display)

    def test_serialization_roundtrip(self):
        display = AdvancementDisplay(
            icon="mymod:magic_ore",
            title="Magic!",
            description="Find magic ore",
            frame=AdvancementFrame.GOAL,
            hidden=True,
        )
        adv = Advancement(
            advancement_id="find_magic",
            display=display,
            parent="mymod:root",
            criteria=[
                AdvancementCriterion(name="found_ore", trigger=PLACED_BLOCK),
            ],
            requirements=[["found_ore"]],
        )
        d = adv.to_dict()
        restored = Advancement.from_dict(d)
        assert restored.advancement_id == "find_magic"
        assert restored.parent == "mymod:root"
        assert restored.display.frame == AdvancementFrame.GOAL
        assert restored.display.hidden is True
        assert len(restored.criteria) == 1
        assert restored.requirements == [["found_ore"]]

    def test_to_json(self):
        display = AdvancementDisplay(
            icon="testmod:gem", title="Gem", description="Get gem",
        )
        adv = Advancement(
            advancement_id="get_gem",
            display=display,
            parent="root",
            criteria=[
                AdvancementCriterion(name="has_gem", trigger=INVENTORY_CHANGED),
            ],
        )
        j = adv.to_json("testmod")
        assert j["parent"] == "testmod:root"
        assert j["display"]["icon"]["id"] == "testmod:gem"
        assert "has_gem" in j["criteria"]
        assert j["criteria"]["has_gem"]["trigger"] == INVENTORY_CHANGED


class TestProjectAdvancements:
    def test_add_advancement(self):
        p = ModProject(mod_id="testmod", name="Test")
        display = AdvancementDisplay(icon="minecraft:stone", title="T", description="D")
        adv = p.add_advancement(Advancement(advancement_id="root", display=display))
        assert len(p.advancements) == 1
        assert adv.advancement_id == "root"

    def test_duplicate_advancement(self):
        p = ModProject(mod_id="testmod", name="Test")
        display = AdvancementDisplay(icon="minecraft:stone", title="T", description="D")
        p.add_advancement(Advancement(advancement_id="root", display=display))
        with pytest.raises(ValueError, match="Duplicate advancement"):
            p.add_advancement(Advancement(advancement_id="root", display=display))

    def test_advancement_serialization_roundtrip(self):
        p = ModProject(mod_id="testmod", name="Test")
        display = AdvancementDisplay(icon="minecraft:stone", title="Root", description="Start")
        p.add_advancement(Advancement(
            advancement_id="root",
            display=display,
            criteria=[AdvancementCriterion(name="tick", trigger="minecraft:tick")],
        ))
        d = p.to_dict()
        assert len(d["advancements"]) == 1

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            p.save(f.name)
            loaded = ModProject.load(f.name)
        assert len(loaded.advancements) == 1
        assert loaded.advancements[0].advancement_id == "root"
