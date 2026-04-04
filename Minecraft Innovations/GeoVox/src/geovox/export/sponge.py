"""Export a VoxelGrid as a Sponge Schematic v2 (.schem) file.

Sponge schematics use NBT format with a specific schema. Block data is stored
as a varint-encoded byte array referencing a palette of block states.
"""

from __future__ import annotations

from pathlib import Path

from ..core.grid import VoxelGrid
from .nbt import (
    TAG_BYTE_ARRAY,
    TAG_COMPOUND,
    TAG_INT,
    TAG_SHORT,
    TAG_STRING,
    write_nbt_file,
)

# Sponge Schematic v2
SCHEMA_VERSION = 2
# Minecraft data version for 1.21.x
DATA_VERSION = 3700


def _encode_varint(value: int) -> list[int]:
    """Encode a non-negative integer as a Minecraft-style varint (LEB128)."""
    result = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            byte |= 0x80
        result.append(byte)
        if not value:
            break
    return result


def export_sponge(
    grid: VoxelGrid,
    output: str | Path,
    origin: tuple[int, int, int] = (0, 0, 0),
    name: str = "GeoVox Export",
    author: str = "GeoVox",
) -> list[Path]:
    """Export a block grid as a Sponge Schematic v2 (.schem) file.

    Args:
        grid: VoxelGrid with Minecraft block name strings (post-palette).
        output: Output path (extension added automatically).
        origin: Offset written into the Offset metadata tag.
        name: Schematic name stored in Metadata.
        author: Author name stored in Metadata.

    Returns:
        List of written file paths.
    """
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not grid.cells:
        return []

    (x0, y0, z0), (x1, y1, z1) = grid.bounds()
    width = x1 - x0 + 1
    height = y1 - y0 + 1
    length = z1 - z0 + 1

    # Build palette: block name -> varint index
    palette_map: dict[str, int] = {}
    for block in grid.cells.values():
        if isinstance(block, str) and block not in palette_map:
            palette_map[block] = len(palette_map)

    # Encode block data as varint byte array (YZX order per Sponge spec)
    block_bytes: list[int] = []
    for y in range(height):
        for z in range(length):
            for x in range(width):
                block = grid.get(x + x0, y + y0, z + z0, default="minecraft:air")
                if isinstance(block, int):
                    block = "minecraft:air"
                if block not in palette_map:
                    palette_map[block] = len(palette_map)
                idx = palette_map[block]
                block_bytes.extend(_encode_varint(idx))

    # Build palette NBT compound: block_name -> TAG_INT(index)
    palette_nbt = {}
    for block_name, idx in palette_map.items():
        palette_nbt[block_name] = (TAG_INT, idx)

    # Metadata compound
    metadata = {
        "Name": (TAG_STRING, name),
        "Author": (TAG_STRING, author),
    }

    # Root compound (Sponge Schematic v2)
    root = {
        "Version": (TAG_INT, SCHEMA_VERSION),
        "DataVersion": (TAG_INT, DATA_VERSION),
        "Width": (TAG_SHORT, width),
        "Height": (TAG_SHORT, height),
        "Length": (TAG_SHORT, length),
        "Offset": (TAG_COMPOUND, {
            "x": (TAG_INT, origin[0]),
            "y": (TAG_INT, origin[1]),
            "z": (TAG_INT, origin[2]),
        }),
        "Metadata": (TAG_COMPOUND, metadata),
        "PaletteMax": (TAG_INT, len(palette_map)),
        "Palette": (TAG_COMPOUND, palette_nbt),
        "BlockData": (TAG_BYTE_ARRAY, block_bytes),
    }

    out_path = output.with_suffix(".schem")
    write_nbt_file(str(out_path), "Schematic", root)
    return [out_path]
