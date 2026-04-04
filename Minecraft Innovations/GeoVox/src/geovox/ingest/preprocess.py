"""Heightmap preprocessing -- smoothing, cropping, and resampling operations."""

from __future__ import annotations

import numpy as np


def smooth_heightmap(data: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply a uniform box filter to smooth a heightmap.

    Uses a simple sliding-window mean (no scipy dependency).
    Edge pixels are handled by zero-padding.
    """
    if kernel_size < 1 or kernel_size % 2 == 0:
        raise ValueError(f"kernel_size must be a positive odd integer, got {kernel_size}")
    if data.ndim != 2:
        raise ValueError(f"Expected 2D array, got {data.ndim}D")

    pad = kernel_size // 2
    padded = np.pad(data, pad, mode="edge")
    result = np.zeros_like(data, dtype=np.float64)

    for dz in range(kernel_size):
        for dx in range(kernel_size):
            result += padded[dz:dz + data.shape[0], dx:dx + data.shape[1]]

    return result / (kernel_size * kernel_size)


def crop_heightmap(
    data: np.ndarray, x: int, z: int, width: int, height: int
) -> np.ndarray:
    """Crop a rectangular region from a heightmap.

    Args:
        data: 2D heightmap array (rows=z, cols=x).
        x: Starting column index.
        z: Starting row index.
        width: Number of columns to keep.
        height: Number of rows to keep.
    """
    if data.ndim != 2:
        raise ValueError(f"Expected 2D array, got {data.ndim}D")
    rows, cols = data.shape
    if x < 0 or z < 0 or x + width > cols or z + height > rows:
        raise ValueError(
            f"Crop region ({x},{z},{width},{height}) out of bounds for "
            f"array of shape ({rows},{cols})"
        )
    return data[z:z + height, x:x + width].copy()


def resample_heightmap(
    data: np.ndarray, target_width: int, target_height: int
) -> np.ndarray:
    """Resample a heightmap to a new size using bilinear interpolation.

    Pure numpy implementation -- no scipy or PIL dependency.
    """
    if data.ndim != 2:
        raise ValueError(f"Expected 2D array, got {data.ndim}D")
    if target_width < 1 or target_height < 1:
        raise ValueError(f"Target dimensions must be positive, got ({target_width}, {target_height})")

    src_h, src_w = data.shape
    # Create coordinate grids for the target
    out_z = np.linspace(0, src_h - 1, target_height)
    out_x = np.linspace(0, src_w - 1, target_width)
    xv, zv = np.meshgrid(out_x, out_z)

    # Bilinear interpolation
    x0 = np.floor(xv).astype(int)
    z0 = np.floor(zv).astype(int)
    x1 = np.minimum(x0 + 1, src_w - 1)
    z1 = np.minimum(z0 + 1, src_h - 1)

    xf = xv - x0
    zf = zv - z0

    top = data[z0, x0] * (1 - xf) + data[z0, x1] * xf
    bot = data[z1, x0] * (1 - xf) + data[z1, x1] * xf
    return top * (1 - zf) + bot * zf
