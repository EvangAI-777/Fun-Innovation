"""World generation Java code generation -- biome modifications and feature registration."""

from __future__ import annotations

from mcstudio.model.worldgen import Biome, PlacedFeature, FeatureType
from mcstudio.codegen.java import JavaWriter, to_pascal_case


def generate_biome_json(biome: Biome, mod_id: str) -> dict:
    """Generate a Minecraft biome JSON for data pack export."""
    def hex_to_int(hex_str: str) -> int:
        return int(hex_str.lstrip("#"), 16)

    effects: dict = {
        "sky_color": hex_to_int(biome.sky_color),
        "fog_color": hex_to_int(biome.fog_color),
        "water_color": hex_to_int(biome.water_color),
        "water_fog_color": hex_to_int(biome.water_fog_color),
    }
    if biome.grass_color:
        effects["grass_color"] = hex_to_int(biome.grass_color)
    if biome.foliage_color:
        effects["foliage_color"] = hex_to_int(biome.foliage_color)

    return {
        "temperature": biome.temperature,
        "downfall": biome.humidity,
        "effects": effects,
        "spawners": {},
        "spawn_costs": biome.spawn_costs,
        "carvers": {"air": []},
        "features": [
            [],  # raw_generation
            [],  # lakes
            [],  # local_modifications
            [],  # underground_structures
            [],  # surface_structures
            [],  # strongholds
            [f"{mod_id}:{f.feature_id}" for f in biome.features if f.feature_type == FeatureType.ORE],
            [],  # underground_decoration
            [f"{mod_id}:{f.feature_id}" for f in biome.features if f.feature_type in (FeatureType.FLOWER, FeatureType.RANDOM_PATCH, FeatureType.VEGETATION_PATCH)],
            [f"{mod_id}:{f.feature_id}" for f in biome.features if f.feature_type == FeatureType.TREE],
            [],  # top_layer_modification
        ],
    }


def generate_configured_feature_json(feature: PlacedFeature, mod_id: str) -> dict:
    """Generate a configured_feature JSON."""
    if feature.feature_type == FeatureType.ORE:
        return {
            "type": "minecraft:ore",
            "config": {
                "size": feature.size,
                "discard_chance_on_air_exposure": 0.0,
                "targets": [
                    {
                        "target": {"predicate_type": "minecraft:tag_match", "tag": "minecraft:stone_ore_replaceables"},
                        "state": {"Name": feature.block},
                    }
                ],
            },
        }
    if feature.feature_type == FeatureType.RANDOM_PATCH:
        return {
            "type": "minecraft:random_patch",
            "config": {
                "tries": feature.size,
                "xz_spread": 7,
                "y_spread": 3,
                "feature": {
                    "feature": {
                        "type": "minecraft:simple_block",
                        "config": {"to_place": {"type": "minecraft:simple_state_provider", "state": {"Name": feature.block}}},
                    },
                    "placement": [],
                },
            },
        }
    # Generic fallback
    return {
        "type": f"minecraft:{feature.feature_type.value}",
        "config": {"size": feature.size, "block": feature.block},
    }


def generate_placed_feature_json(feature: PlacedFeature, mod_id: str) -> dict:
    """Generate a placed_feature JSON."""
    placement_modifiers = [
        {"type": "minecraft:count", "count": feature.placement.count},
        {"type": "minecraft:in_square"},
        {
            "type": "minecraft:height_range",
            "height": {
                "type": f"minecraft:{feature.placement.height_range_type.value}",
                "min_inclusive": {"absolute": feature.placement.height_min},
                "max_inclusive": {"absolute": feature.placement.height_max},
            },
        },
        {"type": "minecraft:biome"},
    ]
    if feature.placement.rarity is not None:
        placement_modifiers.insert(0, {"type": "minecraft:rarity_filter", "chance": feature.placement.rarity})

    return {
        "feature": f"{mod_id}:{feature.feature_id}",
        "placement": placement_modifiers,
    }


def generate_fabric_biome_modifications(biome: Biome, package: str, mod_class: str) -> str:
    """Generate Fabric BiomeModifications API calls for adding features to biomes."""
    w = JavaWriter()
    w.set_package(package)
    w.add_import(
        "net.fabricmc.fabric.api.biome.v1.BiomeModifications",
        "net.fabricmc.fabric.api.biome.v1.BiomeSelectors",
        "net.minecraft.resources.ResourceLocation",
        "net.minecraft.core.registries.Registries",
        "net.minecraft.resources.ResourceKey",
        "net.minecraft.world.level.levelgen.GenerationStep",
    )
    w.line()
    w.open_block(f"public class {to_pascal_case(biome.biome_id)}BiomeFeatures")
    w.open_block("public static void register()")
    for feature in biome.features:
        step = _feature_to_generation_step(feature.feature_type)
        w.line(f'BiomeModifications.addFeature(BiomeSelectors.foundInOverworld(), GenerationStep.Decoration.{step}, ResourceKey.create(Registries.PLACED_FEATURE, ResourceLocation.fromNamespaceAndPath({mod_class}.MOD_ID, "{feature.feature_id}")));')
    w.close_block()
    w.close_block()
    return w.build()


def _feature_to_generation_step(feature_type: FeatureType) -> str:
    """Map feature type to GenerationStep.Decoration constant."""
    mapping = {
        FeatureType.ORE: "UNDERGROUND_ORES",
        FeatureType.TREE: "VEGETAL_DECORATION",
        FeatureType.FLOWER: "VEGETAL_DECORATION",
        FeatureType.VEGETATION_PATCH: "VEGETAL_DECORATION",
        FeatureType.RANDOM_PATCH: "VEGETAL_DECORATION",
        FeatureType.LAKE: "LAKES",
        FeatureType.SPRING: "VEGETAL_DECORATION",
        FeatureType.GEODE: "LOCAL_MODIFICATIONS",
        FeatureType.FOSSIL: "UNDERGROUND_STRUCTURES",
        FeatureType.DISK: "UNDERGROUND_ORES",
        FeatureType.ICEBERG: "SURFACE_STRUCTURES",
    }
    return mapping.get(feature_type, "UNDERGROUND_ORES")
