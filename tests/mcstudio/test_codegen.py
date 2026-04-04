"""Tests for Java code generation utilities."""

from mcstudio.codegen.java import JavaWriter, to_java_string, to_pascal_case, to_camel_case
from mcstudio.codegen.entity import generate_entity_class, generate_entity_renderer
from mcstudio.codegen.worldgen import (
    generate_biome_json,
    generate_configured_feature_json,
    generate_placed_feature_json,
    generate_fabric_biome_modifications,
)
from mcstudio.model.entity import (
    EntityType, EntityBase, AIGoal, AIGoalType, EntityAttribute, SpawnRules,
)
from mcstudio.model.worldgen import Biome, PlacedFeature, FeatureType, PlacementConfig


class TestJavaWriter:
    def test_empty(self):
        w = JavaWriter()
        assert w.build() == ""

    def test_package(self):
        w = JavaWriter()
        w.set_package("com.example.mod")
        result = w.build()
        assert result.startswith("package com.example.mod;\n")

    def test_imports(self):
        w = JavaWriter()
        w.add_import("net.minecraft.block.Block")
        w.add_import("java.util.List")
        result = w.build()
        assert "import java.util.List;" in result
        assert "import net.minecraft.block.Block;" in result
        # java.* should come first
        lines = result.strip().split("\n")
        java_idx = next(i for i, l in enumerate(lines) if "java.util" in l)
        mc_idx = next(i for i, l in enumerate(lines) if "net.minecraft" in l)
        assert java_idx < mc_idx

    def test_no_duplicate_imports(self):
        w = JavaWriter()
        w.add_import("java.util.List", "java.util.List")
        result = w.build()
        assert result.count("java.util.List") == 1

    def test_class_block(self):
        w = JavaWriter()
        w.open_block("public class MyClass")
        w.line("int x = 5;")
        w.close_block()
        result = w.build()
        assert "public class MyClass {" in result
        assert "    int x = 5;" in result
        assert "}" in result

    def test_nested_blocks(self):
        w = JavaWriter()
        w.open_block("public class Outer")
        w.open_block("public void method()")
        w.line("return;")
        w.close_block()
        w.close_block()
        result = w.build()
        assert "        return;" in result

    def test_field(self):
        w = JavaWriter()
        w.field("public static final", "String", "NAME", '"hello"')
        result = w.build()
        assert 'public static final String NAME = "hello";' in result

    def test_annotation(self):
        w = JavaWriter()
        w.annotation("Override")
        w.line("public void run() {}")
        result = w.build()
        assert "@Override" in result

    def test_comment(self):
        w = JavaWriter()
        w.comment("This is a comment")
        assert "// This is a comment" in w.build()

    def test_full_class(self):
        w = JavaWriter()
        w.set_package("com.test")
        w.add_import("java.util.List")
        w.open_block("public class Test")
        w.field("private", "int", "count", "0")
        w.line()
        w.open_block("public int getCount()")
        w.line("return count;")
        w.close_block()
        w.close_block()
        result = w.build()
        assert "package com.test;" in result
        assert "import java.util.List;" in result
        assert "public class Test {" in result
        assert "private int count = 0;" in result
        assert "return count;" in result


class TestHelpers:
    def test_to_java_string(self):
        assert to_java_string("hello") == '"hello"'
        assert to_java_string('say "hi"') == '"say \\"hi\\""'
        assert to_java_string("line\nbreak") == '"line\\nbreak"'

    def test_to_pascal_case(self):
        assert to_pascal_case("cool_mod") == "CoolMod"
        assert to_pascal_case("hello") == "Hello"
        assert to_pascal_case("a_b_c") == "ABC"

    def test_to_camel_case(self):
        assert to_camel_case("cool_mod") == "coolMod"
        assert to_camel_case("hello") == "hello"
        assert to_camel_case("my_great_var") == "myGreatVar"


class TestEntityCodegen:
    def _make_entity(self, **kwargs):
        defaults = dict(
            entity_id="test_mob",
            base_class=EntityBase.MONSTER,
            width=0.8,
            height=1.6,
        )
        defaults.update(kwargs)
        return EntityType(**defaults)

    def test_basic_entity_class(self):
        entity = self._make_entity()
        code = generate_entity_class(entity, "com.test.mod")
        assert "package com.test.mod;" in code
        assert "public class TestMobEntity extends Monster" in code
        assert "super(entityType, level);" in code
        assert "import net.minecraft.world.entity.monster.Monster;" in code

    def test_entity_with_attributes(self):
        entity = self._make_entity(attributes=[
            EntityAttribute("max_health", 30.0),
            EntityAttribute("movement_speed", 0.25),
            EntityAttribute("attack_damage", 5.0),
        ])
        code = generate_entity_class(entity, "com.test.mod")
        assert "createAttributes()" in code
        assert "Attributes.MAX_HEALTH, 30.0" in code
        assert "Attributes.MOVEMENT_SPEED, 0.25" in code
        assert "Attributes.ATTACK_DAMAGE, 5.0" in code
        assert "import net.minecraft.world.entity.ai.attributes.AttributeSupplier;" in code

    def test_entity_with_goals(self):
        entity = self._make_entity(goals=[
            AIGoal(AIGoalType.FLOAT_SWIM, priority=0),
            AIGoal(AIGoalType.MELEE_ATTACK, priority=1, params={"speed": 1.2}),
            AIGoal(AIGoalType.LOOK_AT_PLAYER, priority=5, params={"distance": 6.0}),
            AIGoal(AIGoalType.RANDOM_LOOK_AROUND, priority=6),
        ])
        code = generate_entity_class(entity, "com.test.mod")
        assert "registerGoals()" in code
        assert "FloatGoal" in code
        assert "MeleeAttackGoal(this, 1.2, true)" in code
        assert "LookAtPlayerGoal(this, Player.class, 6.0f)" in code
        assert "RandomLookAroundGoal(this)" in code
        assert "import net.minecraft.world.entity.player.Player;" in code

    def test_entity_goals_sorted_by_priority(self):
        entity = self._make_entity(goals=[
            AIGoal(AIGoalType.RANDOM_LOOK_AROUND, priority=3),
            AIGoal(AIGoalType.FLOAT_SWIM, priority=0),
        ])
        code = generate_entity_class(entity, "com.test.mod")
        swim_pos = code.index("FloatGoal")
        look_pos = code.index("RandomLookAroundGoal")
        assert swim_pos < look_pos

    def test_animal_base_class(self):
        entity = self._make_entity(base_class=EntityBase.ANIMAL)
        code = generate_entity_class(entity, "com.test.mod")
        assert "extends Animal" in code
        assert "import net.minecraft.world.entity.animal.Animal;" in code

    def test_all_base_classes_generate(self):
        for base in EntityBase:
            entity = self._make_entity(base_class=base)
            code = generate_entity_class(entity, "com.test.mod")
            assert "extends" in code
            assert "package com.test.mod;" in code

    def test_entity_renderer(self):
        entity = self._make_entity()
        code = generate_entity_renderer(entity, "com.test.mod", "TestMod")
        assert "package com.test.mod.client;" in code
        assert "class TestMobEntityRenderer" in code
        assert "MobRenderer" in code
        assert 'textures/entity/test_mob.png' in code

    def test_entity_no_goals_no_register_goals(self):
        entity = self._make_entity(goals=[])
        code = generate_entity_class(entity, "com.test.mod")
        assert "registerGoals" not in code

    def test_entity_no_attributes_no_create_attributes(self):
        entity = self._make_entity(attributes=[])
        code = generate_entity_class(entity, "com.test.mod")
        assert "createAttributes" not in code

    def test_all_goal_types_generate(self):
        for goal_type in AIGoalType:
            entity = self._make_entity(goals=[AIGoal(goal_type, priority=0)])
            code = generate_entity_class(entity, "com.test.mod")
            assert "addGoal(0," in code


class TestWorldgenCodegen:
    def _make_biome(self):
        return Biome(
            biome_id="crystal_caves",
            temperature=0.3,
            humidity=0.8,
            sky_color="#6688CC",
            water_color="#2244AA",
            features=[
                PlacedFeature(
                    feature_id="crystal_ore",
                    feature_type=FeatureType.ORE,
                    block="testmod:crystal_ore",
                    size=12,
                    placement=PlacementConfig(count=4, height_min=0, height_max=64),
                ),
            ],
        )

    def test_biome_json(self):
        biome = self._make_biome()
        result = generate_biome_json(biome, "testmod")
        assert result["temperature"] == 0.3
        assert result["downfall"] == 0.8
        assert result["effects"]["sky_color"] == 0x6688CC
        assert result["effects"]["water_color"] == 0x2244AA
        assert "features" in result

    def test_biome_json_with_grass_color(self):
        biome = Biome(biome_id="green_biome", grass_color="#00FF00")
        result = generate_biome_json(biome, "testmod")
        assert result["effects"]["grass_color"] == 0x00FF00

    def test_configured_feature_ore(self):
        feature = PlacedFeature(
            feature_id="test_ore",
            feature_type=FeatureType.ORE,
            block="testmod:test_ore",
            size=8,
        )
        result = generate_configured_feature_json(feature, "testmod")
        assert result["type"] == "minecraft:ore"
        assert result["config"]["size"] == 8

    def test_configured_feature_random_patch(self):
        feature = PlacedFeature(
            feature_id="test_patch",
            feature_type=FeatureType.RANDOM_PATCH,
            block="minecraft:poppy",
            size=64,
        )
        result = generate_configured_feature_json(feature, "testmod")
        assert result["type"] == "minecraft:random_patch"
        assert result["config"]["tries"] == 64

    def test_placed_feature_json(self):
        feature = PlacedFeature(
            feature_id="test_ore",
            feature_type=FeatureType.ORE,
            block="testmod:test_ore",
            placement=PlacementConfig(count=4, height_min=-16, height_max=48),
        )
        result = generate_placed_feature_json(feature, "testmod")
        assert result["feature"] == "testmod:test_ore"
        assert len(result["placement"]) >= 3

    def test_placed_feature_with_rarity(self):
        feature = PlacedFeature(
            feature_id="rare_ore",
            placement=PlacementConfig(count=1, rarity=4),
        )
        result = generate_placed_feature_json(feature, "testmod")
        rarity_mod = [m for m in result["placement"] if m.get("type") == "minecraft:rarity_filter"]
        assert len(rarity_mod) == 1
        assert rarity_mod[0]["chance"] == 4

    def test_fabric_biome_modifications(self):
        biome = self._make_biome()
        code = generate_fabric_biome_modifications(biome, "com.test.mod", "TestMod")
        assert "BiomeModifications.addFeature" in code
        assert "crystal_ore" in code
        assert "UNDERGROUND_ORES" in code
        assert "package com.test.mod;" in code
