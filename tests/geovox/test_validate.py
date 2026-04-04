"""Tests for palette validation."""

import pytest

from geovox.palette.validate import validate_palette, EXPECTED_CATEGORIES


def _valid_palette():
    return {
        "name": "test",
        "mappings": {
            "bedrock": {"block": "minecraft:bedrock"},
            "ground_deep": {"block": "minecraft:stone"},
            "ground_shallow": {"block": "minecraft:dirt"},
            "surface": {"block": "minecraft:grass_block"},
            "water": {"block": "minecraft:water"},
        },
    }


class TestValidatePalette:
    def test_valid_palette(self):
        errors = validate_palette(_valid_palette())
        assert errors == []

    def test_missing_mappings_key(self):
        errors = validate_palette({"name": "test"})
        assert any("Missing 'mappings'" in e for e in errors)

    def test_empty_mappings(self):
        errors = validate_palette({"mappings": {}})
        assert any("empty" in e for e in errors)

    def test_not_dict(self):
        errors = validate_palette("not a dict")
        assert any("JSON object" in e for e in errors)

    def test_missing_block_and_blocks(self):
        data = _valid_palette()
        data["mappings"]["bedrock"] = {"invalid": True}
        errors = validate_palette(data)
        assert any("'block' or 'blocks'" in e for e in errors)

    def test_both_block_and_blocks(self):
        data = _valid_palette()
        data["mappings"]["bedrock"] = {"block": "minecraft:bedrock", "blocks": ["minecraft:bedrock"]}
        errors = validate_palette(data)
        assert any("both" in e for e in errors)

    def test_block_missing_prefix(self):
        data = _valid_palette()
        data["mappings"]["bedrock"] = {"block": "bedrock"}
        errors = validate_palette(data)
        assert any("minecraft:" in e for e in errors)

    def test_weights_length_mismatch(self):
        data = _valid_palette()
        data["mappings"]["ground_deep"] = {
            "blocks": ["minecraft:stone", "minecraft:andesite"],
            "weights": [0.5],
        }
        errors = validate_palette(data)
        assert any("weights length" in e for e in errors)

    def test_negative_weight(self):
        data = _valid_palette()
        data["mappings"]["ground_deep"] = {
            "blocks": ["minecraft:stone"],
            "weights": [-1.0],
        }
        errors = validate_palette(data)
        assert any("non-negative" in e for e in errors)

    def test_missing_standard_categories(self):
        data = {
            "mappings": {
                "bedrock": {"block": "minecraft:bedrock"},
            }
        }
        errors = validate_palette(data)
        assert any("Missing standard categories" in e for e in errors)

    def test_weighted_blocks_valid(self):
        data = _valid_palette()
        data["mappings"]["ground_deep"] = {
            "blocks": ["minecraft:stone", "minecraft:andesite"],
            "weights": [0.7, 0.3],
        }
        errors = validate_palette(data)
        assert errors == []

    def test_blocks_without_weights_valid(self):
        data = _valid_palette()
        data["mappings"]["ground_deep"] = {
            "blocks": ["minecraft:stone", "minecraft:andesite"],
        }
        errors = validate_palette(data)
        assert errors == []
