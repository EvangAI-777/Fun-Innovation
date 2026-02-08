"""Tests for the palette system."""

import json
import tempfile
from pathlib import Path

from geovox.core.grid import VoxelGrid
from geovox.palette.palette import Palette, apply_palette, HEIGHTMAP_CATEGORIES


def test_single_block_resolve():
    p = Palette(mappings={"surface": {"block": "minecraft:grass_block"}})
    assert p.resolve("surface") == "minecraft:grass_block"


def test_unknown_category_fallback():
    p = Palette(mappings={})
    assert p.resolve("nonexistent") == "minecraft:stone"


def test_weighted_random_with_seed():
    p = Palette(
        mappings={
            "ground_deep": {
                "blocks": ["minecraft:stone", "minecraft:andesite"],
                "weights": [0.8, 0.2],
            }
        },
        seed=42,
    )
    results = {p.resolve("ground_deep") for _ in range(50)}
    # With enough samples, both blocks should appear
    assert "minecraft:stone" in results


def test_palette_from_json():
    data = {
        "name": "test-palette",
        "version": "1.21",
        "mappings": {
            "bedrock": {"block": "minecraft:bedrock"},
            "surface": {"block": "minecraft:grass_block"},
        },
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.flush()
        p = Palette.from_json(f.name, seed=0)

    assert p.name == "test-palette"
    assert p.resolve("bedrock") == "minecraft:bedrock"
    assert p.resolve("surface") == "minecraft:grass_block"
    Path(f.name).unlink()


def test_apply_palette():
    grid = VoxelGrid()
    grid.set(0, 0, 0, 0)  # bedrock category
    grid.set(0, 1, 0, 1)  # ground_deep category
    grid.set(0, 2, 0, 3)  # surface category

    p = Palette(
        mappings={
            "bedrock": {"block": "minecraft:bedrock"},
            "ground_deep": {"block": "minecraft:stone"},
            "surface": {"block": "minecraft:grass_block"},
        },
        seed=0,
    )

    result = apply_palette(grid, p)
    assert result.get(0, 0, 0) == "minecraft:bedrock"
    assert result.get(0, 1, 0) == "minecraft:stone"
    assert result.get(0, 2, 0) == "minecraft:grass_block"
    assert len(result) == 3


def test_apply_palette_preserves_metadata():
    grid = VoxelGrid()
    grid.metadata = {"source": "test.png"}
    grid.set(0, 0, 0, 0)

    p = Palette(
        mappings={"bedrock": {"block": "minecraft:bedrock"}},
        name="test",
        seed=0,
    )

    result = apply_palette(grid, p)
    assert result.metadata["source"] == "test.png"
    assert result.metadata["palette"] == "test"


def test_empty_blocks_fallback():
    p = Palette(mappings={"empty": {"blocks": [], "weights": []}})
    assert p.resolve("empty") == "minecraft:stone"
