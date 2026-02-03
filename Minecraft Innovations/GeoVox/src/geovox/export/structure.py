"""Export a VoxelGrid as a Minecraft .nbt structure file.

Structure files can be loaded in-game via structure blocks or the /place command.
"""

from __future__ import annotations

from pathlib import Path

from ..core.grid import VoxelGrid
from .nbt import (
    TAG_COMPOUND,
    TAG_INT,
    TAG_LIST,
    TAG_STRING,
    write_nbt_file,
)

# DataVersion for Minecraft 1.21.x
DATA_VERSION = 3700


def export_structure(
    grid: VoxelGrid,
    output: str | Path,
    origin: tuple[int, int, int] = (0, 0, 0),
) -> list[Path]:
    """Export a block grid as a Minecraft .nbt structure file.

    Args:
        grid: VoxelGrid with Minecraft block name strings (post-palette).
        output: Output path (extension added automatically).
        origin: Offset applied to all coordinates before writing.

    Returns:
        List of written file paths.
    """
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not grid.cells:
        return []

    ox, oy, oz = origin
    (x0, y0, z0), (x1, y1, z1) = grid.bounds()

    # Build palette: unique block names -> index
    palette_map: dict[str, int] = {}
    for block in grid.cells.values():
        if isinstance(block, str) and block not in palette_map:
            palette_map[block] = len(palette_map)

    # Structure dimensions (relative, 1-indexed size)
    size_x = x1 - x0 + 1
    size_y = y1 - y0 + 1
    size_z = z1 - z0 + 1

    # Build block list (positions relative to structure origin)
    blocks = []
    for (x, y, z), block in grid.cells.items():
        if not isinstance(block, str):
            continue
        pos_compound = {
            "pos": (TAG_LIST, (TAG_INT, [x - x0 + ox, y - y0 + oy, z - z0 + oz])),
            "state": (TAG_INT, palette_map[block]),
        }
        blocks.append(pos_compound)

    # Build palette list
    palette_entries = [None] * len(palette_map)
    for block_name, idx in palette_map.items():
        palette_entries[idx] = {"Name": (TAG_STRING, block_name)}

    # Assemble root compound
    root = {
        "DataVersion": (TAG_INT, DATA_VERSION),
        "size": (TAG_LIST, (TAG_INT, [size_x, size_y, size_z])),
        "palette": (TAG_LIST, (TAG_COMPOUND, palette_entries)),
        "blocks": (TAG_LIST, (TAG_COMPOUND, blocks)),
        "entities": (TAG_LIST, (TAG_COMPOUND, [])),
    }

    out_path = output.with_suffix(".nbt")
    write_nbt_file(str(out_path), "", root)
    return [out_path]
