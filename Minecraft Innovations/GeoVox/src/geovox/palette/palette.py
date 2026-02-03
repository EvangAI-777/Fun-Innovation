"""Palette system -- map semantic category IDs to Minecraft block names."""

from __future__ import annotations

import json
import random
from pathlib import Path

from ..core.grid import VoxelGrid

# Default category ID -> name mapping for heightmap ingest.
HEIGHTMAP_CATEGORIES = {
    0: "bedrock",
    1: "ground_deep",
    2: "ground_shallow",
    3: "surface",
    4: "water",
}


class Palette:
    """A mapping from semantic category names to Minecraft block selections."""

    def __init__(self, mappings: dict, name: str = "", seed: int | None = None):
        self.name = name
        self.mappings = mappings
        self.rng = random.Random(seed)

    @classmethod
    def from_json(cls, path: str | Path, seed: int | None = None) -> Palette:
        """Load a palette from a JSON config file."""
        path = Path(path)
        with open(path) as f:
            data = json.load(f)
        return cls(
            mappings=data.get("mappings", {}),
            name=data.get("name", path.stem),
            seed=seed,
        )

    def resolve(self, category_name: str) -> str:
        """Resolve a semantic category name to a Minecraft block name."""
        entry = self.mappings.get(category_name)
        if entry is None:
            return "minecraft:stone"

        # Single block entry
        if "block" in entry:
            return entry["block"]

        # Weighted random selection
        blocks = entry.get("blocks", [])
        weights = entry.get("weights")
        if not blocks:
            return "minecraft:stone"
        if weights:
            return self.rng.choices(blocks, weights=weights, k=1)[0]
        return self.rng.choice(blocks)


def apply_palette(
    grid: VoxelGrid,
    palette: Palette,
    category_names: dict[int, str] | None = None,
) -> VoxelGrid:
    """Apply a palette to a grid, replacing category IDs with block names.

    Args:
        grid: VoxelGrid with integer semantic category IDs.
        palette: Palette to apply.
        category_names: Mapping from category ID to name. Defaults to
            HEIGHTMAP_CATEGORIES if not provided.

    Returns:
        New VoxelGrid with Minecraft block name strings.
    """
    if category_names is None:
        category_names = HEIGHTMAP_CATEGORIES

    result = VoxelGrid()
    result.metadata = {**grid.metadata, "palette": palette.name}

    for pos, category_id in grid.cells.items():
        cat_name = category_names.get(category_id, "ground_deep")
        block = palette.resolve(cat_name)
        result.cells[pos] = block

    return result
