"""Palette composition -- stack multiple palette layers with conditional overrides."""

from __future__ import annotations

from typing import Callable

from ..core.grid import VoxelGrid
from .palette import Palette, HEIGHTMAP_CATEGORIES


class PaletteComposer:
    """Compose multiple palette layers with optional conditions.

    Each layer is a (Palette, condition_fn) pair. The condition function
    receives (x, z, grid) and returns True if this layer should apply at
    that column. Layers are evaluated in order; later layers override
    earlier ones where their conditions match.
    """

    def __init__(self):
        self.layers: list[tuple[Palette, Callable | None]] = []

    def add_layer(self, palette: Palette, condition: Callable | None = None) -> None:
        self.layers.append((palette, condition))

    def resolve(self, category_name: str, x: int, z: int, grid: VoxelGrid) -> str:
        """Resolve a category using layered palettes.

        Walks layers in order. The last matching layer's resolution wins.
        """
        result = "minecraft:stone"
        for palette, condition in self.layers:
            if condition is not None and not condition(x, z, grid):
                continue
            entry = palette.mappings.get(category_name)
            if entry is not None:
                result = palette.resolve(category_name)
        return result


def apply_composed_palette(
    grid: VoxelGrid,
    composer: PaletteComposer,
    category_names: dict[int, str] | None = None,
) -> VoxelGrid:
    """Apply a composed palette to a grid.

    Like apply_palette but uses PaletteComposer for per-column layer resolution.
    """
    if category_names is None:
        category_names = HEIGHTMAP_CATEGORIES

    result = VoxelGrid()
    result.metadata = {**grid.metadata, "palette": "composed"}

    for pos, category_id in grid.cells.items():
        x, _y, z = pos
        cat_name = category_names.get(category_id, "ground_deep")
        block = composer.resolve(cat_name, x, z, grid)
        result.cells[pos] = block

    return result


def elevation_condition(min_y: float, max_y: float) -> Callable:
    """Create a condition that matches columns within an elevation range."""
    def condition(x: int, z: int, grid: VoxelGrid) -> bool:
        elevation = grid.metadata.get("elevation")
        if elevation is None:
            return False
        rows, cols = elevation.shape
        if z < 0 or z >= rows or x < 0 or x >= cols:
            return False
        return min_y <= float(elevation[z, x]) <= max_y
    return condition


def slope_condition(min_slope: float, max_slope: float = float("inf")) -> Callable:
    """Create a condition that matches columns within a slope range."""
    def condition(x: int, z: int, grid: VoxelGrid) -> bool:
        slope = grid.metadata.get("slope")
        if slope is None:
            return False
        rows, cols = slope.shape
        if z < 0 or z >= rows or x < 0 or x >= cols:
            return False
        return min_slope <= float(slope[z, x]) <= max_slope
    return condition
