"""Heightmap ingest -- read grayscale images or GeoTIFF elevation data into a VoxelGrid."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from ..core.grid import VoxelGrid

# Semantic category IDs assigned during heightmap ingest.
# These are mapped to block names by the palette layer.
BEDROCK = 0
GROUND_DEEP = 1
GROUND_SHALLOW = 2
SURFACE = 3
WATER = 4


def ingest_heightmap(
    path: str | Path,
    y_scale: tuple[int, int] = (0, 128),
    sea_level: int | None = None,
    dirt_depth: int = 3,
) -> VoxelGrid:
    """Read a heightmap image and convert it to a VoxelGrid.

    Each pixel becomes a column of blocks. Brighter pixels produce taller
    columns. The column is layered: bedrock at the bottom, stone fill,
    a dirt layer near the surface, and grass on top.

    Args:
        path: Path to a grayscale PNG, TIFF, or GeoTIFF file.
        y_scale: (y_min, y_max) range to map pixel values onto.
        sea_level: Y level for water fill. None to disable.
        dirt_depth: Number of dirt blocks below the surface.

    Returns:
        VoxelGrid with semantic category IDs assigned to each cell.
    """
    path = Path(path)
    heightmap = _read_heightmap(path)

    grid = VoxelGrid()
    grid.metadata = {
        "source": str(path),
        "source_shape": heightmap.shape,
        "y_scale": y_scale,
        "sea_level": sea_level,
    }

    y_min, y_max = y_scale
    h_min, h_max = float(heightmap.min()), float(heightmap.max())
    if h_max == h_min:
        h_max = h_min + 1  # avoid division by zero for flat images

    rows, cols = heightmap.shape
    for z in range(rows):
        for x in range(cols):
            normalized = (float(heightmap[z, x]) - h_min) / (h_max - h_min)
            height = int(y_min + normalized * (y_max - y_min))
            _fill_terrain_column(grid, x, z, height, dirt_depth)

            if sea_level is not None and height < sea_level:
                grid.fill_column(x, z, height + 1, sea_level, WATER)

    return grid


def _fill_terrain_column(
    grid: VoxelGrid, x: int, z: int, height: int, dirt_depth: int
) -> None:
    """Fill a single terrain column with layered semantic categories."""
    if height < 0:
        return

    # Bedrock at y=0
    grid.set(x, 0, z, BEDROCK)

    # Stone fill from y=1 up to the dirt layer
    stone_top = max(0, height - dirt_depth)
    if stone_top > 1:
        grid.fill_column(x, z, 1, stone_top, GROUND_DEEP)

    # Dirt layer below the surface block
    dirt_bottom = max(1, stone_top + 1)
    if dirt_bottom <= height - 1:
        grid.fill_column(x, z, dirt_bottom, height - 1, GROUND_SHALLOW)

    # Surface block (grass)
    if height > 0:
        grid.set(x, height, z, SURFACE)


def _read_heightmap(path: Path) -> np.ndarray:
    """Read a heightmap file and return a 2D numpy array of elevation values."""
    suffix = path.suffix.lower()

    # Try rasterio for GeoTIFF (optional dependency)
    if suffix in (".tif", ".tiff"):
        try:
            import rasterio

            with rasterio.open(path) as src:
                return src.read(1).astype(np.float64)
        except ImportError:
            pass  # fall through to PIL

    # PIL for PNG, BMP, JPEG, and TIFF fallback
    img = Image.open(path).convert("L")
    return np.array(img, dtype=np.float64)
