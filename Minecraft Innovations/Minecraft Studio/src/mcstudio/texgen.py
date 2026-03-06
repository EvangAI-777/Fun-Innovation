"""Minimal placeholder texture generator -- zero external dependencies.

Generates 16x16 solid-color PNG files for blocks and items so exported
mods are immediately runnable without missing-texture checkerboards.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

from mcstudio.model.block import Block, BlockMaterial
from mcstudio.model.item import Item
from mcstudio.model.project import ModProject

# Material -> (R, G, B) mapping for placeholder block textures
_MATERIAL_COLORS: dict[str, tuple[int, int, int]] = {
    "stone": (128, 128, 128),
    "wood": (139, 90, 43),
    "dirt": (134, 96, 67),
    "metal": (192, 192, 192),
    "sand": (219, 211, 160),
    "wool": (233, 233, 233),
    "glass": (180, 215, 230),
    "ice": (160, 200, 255),
    "leaves": (60, 140, 50),
    "plant": (80, 180, 60),
    "coral": (230, 100, 120),
    "amethyst": (140, 80, 200),
    "nether": (130, 40, 40),
    "sculk": (10, 40, 50),
}

# Default color for items
_ITEM_COLOR: tuple[int, int, int] = (200, 180, 120)


def _make_png(r: int, g: int, b: int, size: int = 16) -> bytes:
    """Generate a minimal solid-color PNG image as raw bytes.

    Creates a valid PNG file with a single IDAT chunk containing
    unfiltered rows of the specified color.
    """

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"

    # IHDR: width, height, bit depth 8, color type 2 (RGB)
    ihdr_data = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)

    # IDAT: raw pixel data with filter byte 0 (none) per row
    raw = b""
    row = bytes([r, g, b]) * size
    for _ in range(size):
        raw += b"\x00" + row  # filter byte + RGB pixels
    idat_data = zlib.compress(raw)
    idat = _chunk(b"IDAT", idat_data)

    # IEND
    iend = _chunk(b"IEND", b"")

    return sig + ihdr + idat + iend


def generate_block_texture(block: Block, output_path: Path) -> Path:
    """Generate a placeholder texture for a block."""
    color = _MATERIAL_COLORS.get(block.material.value, (128, 128, 128))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(_make_png(*color))
    return output_path


def generate_item_texture(item: Item, output_path: Path) -> Path:
    """Generate a placeholder texture for an item."""
    if item.is_food:
        color = (200, 120, 80)
    elif item.is_tool:
        color = (160, 160, 170)
    else:
        color = _ITEM_COLOR
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(_make_png(*color))
    return output_path


def generate_project_textures(project: ModProject, assets_dir: Path) -> list[Path]:
    """Generate all placeholder textures for a project.

    ``assets_dir`` should be the ``assets/<mod_id>`` directory inside
    the exported project's resources.

    Returns a list of generated file paths.
    """
    generated = []
    for block in project.blocks:
        path = assets_dir / "textures" / "block" / f"{block.block_id}.png"
        generate_block_texture(block, path)
        generated.append(path)
    for item in project.items:
        path = assets_dir / "textures" / "item" / f"{item.item_id}.png"
        generate_item_texture(item, path)
        generated.append(path)
    return generated
