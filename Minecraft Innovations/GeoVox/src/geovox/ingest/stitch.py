"""Multi-heightmap stitching -- combine multiple heightmap tiles into one array."""

from __future__ import annotations

import numpy as np


def stitch_heightmaps(
    tiles: list[tuple[np.ndarray, int, int]],
    overlap_mode: str = "average",
) -> np.ndarray:
    """Combine multiple heightmap tiles into a single array.

    Args:
        tiles: List of (heightmap_array, col_offset, row_offset) tuples.
            Offsets are in pixels from the top-left of the combined grid.
        overlap_mode: How to handle overlapping regions.
            "average" averages overlapping values, "last" uses the last tile.

    Returns:
        Combined 2D heightmap array.
    """
    if not tiles:
        raise ValueError("No tiles provided")
    if overlap_mode not in ("average", "last"):
        raise ValueError(f"Unknown overlap_mode: {overlap_mode!r}")

    # Compute output dimensions
    max_col = 0
    max_row = 0
    for data, col_off, row_off in tiles:
        if data.ndim != 2:
            raise ValueError(f"Expected 2D array, got {data.ndim}D")
        rows, cols = data.shape
        max_row = max(max_row, row_off + rows)
        max_col = max(max_col, col_off + cols)

    result = np.zeros((max_row, max_col), dtype=np.float64)
    counts = np.zeros((max_row, max_col), dtype=np.float64)

    for data, col_off, row_off in tiles:
        rows, cols = data.shape
        r_slice = slice(row_off, row_off + rows)
        c_slice = slice(col_off, col_off + cols)

        if overlap_mode == "last":
            result[r_slice, c_slice] = data.astype(np.float64)
            counts[r_slice, c_slice] = 1.0
        else:  # average
            result[r_slice, c_slice] += data.astype(np.float64)
            counts[r_slice, c_slice] += 1.0

    # Avoid division by zero for unfilled regions
    counts[counts == 0] = 1.0
    if overlap_mode == "average":
        result /= counts

    return result
