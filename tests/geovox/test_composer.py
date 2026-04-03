"""Tests for the palette composition system."""

import numpy as np

from geovox.core.grid import VoxelGrid
from geovox.palette.palette import Palette, HEIGHTMAP_CATEGORIES
from geovox.palette.composer import (
    PaletteComposer,
    apply_composed_palette,
    elevation_condition,
    slope_condition,
)


def _make_grid_with_elevation():
    """Create a small grid with elevation and slope metadata."""
    grid = VoxelGrid()
    elevation = np.array([
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90],
    ], dtype=np.float64)
    grid.metadata["elevation"] = elevation
    grid.compute_slope()
    # Add some cells (surface category = 3)
    for z in range(3):
        for x in range(3):
            grid.set(x, 0, z, 3)
    return grid


def test_composer_single_layer():
    base = Palette(
        mappings={"surface": {"block": "minecraft:grass_block"}},
        seed=0,
    )
    composer = PaletteComposer()
    composer.add_layer(base)

    grid = VoxelGrid()
    result = composer.resolve("surface", 0, 0, grid)
    assert result == "minecraft:grass_block"


def test_composer_unknown_category_fallback():
    composer = PaletteComposer()
    grid = VoxelGrid()
    assert composer.resolve("nonexistent", 0, 0, grid) == "minecraft:stone"


def test_composer_layer_override():
    base = Palette(mappings={"surface": {"block": "minecraft:grass_block"}}, seed=0)
    overlay = Palette(mappings={"surface": {"block": "minecraft:snow_block"}}, seed=0)

    composer = PaletteComposer()
    composer.add_layer(base)
    composer.add_layer(overlay)  # No condition = always applies

    grid = VoxelGrid()
    assert composer.resolve("surface", 0, 0, grid) == "minecraft:snow_block"


def test_composer_conditional_override():
    base = Palette(mappings={"surface": {"block": "minecraft:grass_block"}}, seed=0)
    high_overlay = Palette(mappings={"surface": {"block": "minecraft:snow_block"}}, seed=0)

    composer = PaletteComposer()
    composer.add_layer(base)
    composer.add_layer(high_overlay, condition=elevation_condition(70, 100))

    grid = _make_grid_with_elevation()

    # Low elevation column (10) -- base palette
    assert composer.resolve("surface", 0, 0, grid) == "minecraft:grass_block"
    # High elevation column (90) -- overlay
    assert composer.resolve("surface", 2, 2, grid) == "minecraft:snow_block"


def test_composer_partial_override():
    """Overlay only defines 'surface'; base provides 'bedrock'."""
    base = Palette(mappings={
        "bedrock": {"block": "minecraft:bedrock"},
        "surface": {"block": "minecraft:grass_block"},
    }, seed=0)
    overlay = Palette(mappings={
        "surface": {"block": "minecraft:snow_block"},
    }, seed=0)

    composer = PaletteComposer()
    composer.add_layer(base)
    composer.add_layer(overlay)

    grid = VoxelGrid()
    assert composer.resolve("bedrock", 0, 0, grid) == "minecraft:bedrock"
    assert composer.resolve("surface", 0, 0, grid) == "minecraft:snow_block"


def test_elevation_condition():
    grid = _make_grid_with_elevation()
    cond = elevation_condition(40, 60)

    assert cond(0, 1, grid) is True   # elevation[1, 0] = 40
    assert cond(1, 1, grid) is True   # elevation[1, 1] = 50
    assert cond(0, 0, grid) is False  # elevation[0, 0] = 10


def test_elevation_condition_no_metadata():
    grid = VoxelGrid()
    cond = elevation_condition(0, 100)
    assert cond(0, 0, grid) is False


def test_elevation_condition_out_of_bounds():
    grid = _make_grid_with_elevation()
    cond = elevation_condition(0, 100)
    assert cond(99, 99, grid) is False


def test_slope_condition():
    grid = _make_grid_with_elevation()
    slope = grid.metadata["slope"]
    # The center cell should have a non-zero slope
    center_slope = float(slope[1, 1])

    steep = slope_condition(center_slope - 0.1, center_slope + 0.1)
    assert steep(1, 1, grid) is True

    very_steep = slope_condition(center_slope + 100)
    assert very_steep(1, 1, grid) is False


def test_slope_condition_no_metadata():
    grid = VoxelGrid()
    cond = slope_condition(0)
    assert cond(0, 0, grid) is False


def test_apply_composed_palette():
    grid = _make_grid_with_elevation()

    base = Palette(mappings={"surface": {"block": "minecraft:grass_block"}}, seed=0)
    overlay = Palette(mappings={"surface": {"block": "minecraft:snow_block"}}, seed=0)

    composer = PaletteComposer()
    composer.add_layer(base)
    composer.add_layer(overlay, condition=elevation_condition(70, 100))

    result = apply_composed_palette(grid, composer)

    # Low elevation cells get grass
    assert result.get(0, 0, 0) == "minecraft:grass_block"
    # High elevation cells get snow
    assert result.get(2, 0, 2) == "minecraft:snow_block"
    assert result.metadata["palette"] == "composed"


def test_apply_composed_palette_preserves_metadata():
    grid = VoxelGrid()
    grid.metadata = {"source": "test.png", "elevation": np.ones((2, 2))}
    grid.set(0, 0, 0, 3)

    base = Palette(mappings={"surface": {"block": "minecraft:stone"}}, seed=0)
    composer = PaletteComposer()
    composer.add_layer(base)

    result = apply_composed_palette(grid, composer)
    assert result.metadata["source"] == "test.png"
