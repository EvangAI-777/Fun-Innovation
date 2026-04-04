"""Sparse 3D voxel grid -- the common representation between all pipeline layers."""

from __future__ import annotations

import numpy as np


class VoxelGrid:
    """Sparse 3D integer grid.

    Keys are (x, y, z) integer tuples. Values are semantic category IDs
    (during ingest) or Minecraft block name strings (after palette mapping).
    """

    def __init__(self):
        self.cells: dict[tuple[int, int, int], int | str] = {}
        self.metadata: dict = {}

    def set(self, x: int, y: int, z: int, value: int | str) -> None:
        self.cells[(x, y, z)] = value

    def get(self, x: int, y: int, z: int, default: int | str = 0) -> int | str:
        return self.cells.get((x, y, z), default)

    def bounds(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        """Return (min_corner, max_corner) of occupied cells."""
        if not self.cells:
            return (0, 0, 0), (0, 0, 0)
        coords = list(self.cells.keys())
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        zs = [c[2] for c in coords]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def fill_column(self, x: int, z: int, y_min: int, y_max: int, value: int | str) -> None:
        """Fill a vertical column from y_min to y_max (inclusive)."""
        for y in range(y_min, y_max + 1):
            self.cells[(x, y, z)] = value

    def __len__(self) -> int:
        return len(self.cells)

    def __contains__(self, key: tuple[int, int, int]) -> bool:
        return key in self.cells

    def merge(self, other: VoxelGrid, offset: tuple[int, int, int] = (0, 0, 0)) -> None:
        """Merge another grid into this one, with an optional position offset.

        Cells from `other` overwrite existing cells at the same position.
        Metadata is not merged.
        """
        ox, oy, oz = offset
        for (x, y, z), val in other.cells.items():
            self.cells[(x + ox, y + oy, z + oz)] = val

    def compute_slope(self) -> np.ndarray | None:
        """Compute slope (gradient magnitude) per column from elevation metadata.

        Requires 'elevation' key in metadata containing a 2D numpy array.
        Returns a 2D array of slope values (gradient magnitude), or None
        if no elevation data is available.
        """
        elevation = self.metadata.get("elevation")
        if elevation is None:
            return None

        gy, gx = np.gradient(elevation.astype(np.float64))
        slope = np.sqrt(gx ** 2 + gy ** 2)
        self.metadata["slope"] = slope
        return slope

    def __repr__(self) -> str:
        (x0, y0, z0), (x1, y1, z1) = self.bounds()
        return (
            f"VoxelGrid({len(self.cells):,} cells, "
            f"bounds=({x0},{y0},{z0})..({x1},{y1},{z1}))"
        )
