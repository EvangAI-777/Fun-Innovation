"""Minimal NBT (Named Binary Tag) writer for Minecraft structure files.

Implements only the tag types needed for structure file export.
All values are big-endian per the NBT specification.
"""

from __future__ import annotations

import gzip
import io
import struct

# Tag type IDs
TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10


def write_nbt_file(path: str, root_name: str, root: dict, compress: bool = True) -> None:
    """Write an NBT compound to a file, optionally gzip-compressed.

    Args:
        path: Output file path.
        root_name: Name of the root compound tag (usually empty string).
        root: Dictionary describing the root compound contents.
              Keys are tag names, values are (tag_type, payload) tuples.
        compress: Whether to gzip-compress the output (standard for .nbt files).
    """
    buf = io.BytesIO()
    _write_tag_header(buf, TAG_COMPOUND, root_name)
    _write_compound_payload(buf, root)

    data = buf.getvalue()
    if compress:
        with open(path, "wb") as f:
            f.write(gzip.compress(data))
    else:
        with open(path, "wb") as f:
            f.write(data)


def _write_tag_header(buf: io.BytesIO, tag_type: int, name: str) -> None:
    """Write a tag type byte and name."""
    buf.write(struct.pack(">b", tag_type))
    encoded = name.encode("utf-8")
    buf.write(struct.pack(">H", len(encoded)))
    buf.write(encoded)


def _write_compound_payload(buf: io.BytesIO, compound: dict) -> None:
    """Write the payload of a compound tag (named children + END)."""
    for name, (tag_type, value) in compound.items():
        _write_tag_header(buf, tag_type, name)
        _write_payload(buf, tag_type, value)
    buf.write(struct.pack(">b", TAG_END))


def _write_payload(buf: io.BytesIO, tag_type: int, value) -> None:
    """Write a tag's payload (without header)."""
    if tag_type == TAG_BYTE:
        buf.write(struct.pack(">b", value))
    elif tag_type == TAG_SHORT:
        buf.write(struct.pack(">h", value))
    elif tag_type == TAG_INT:
        buf.write(struct.pack(">i", value))
    elif tag_type == TAG_LONG:
        buf.write(struct.pack(">q", value))
    elif tag_type == TAG_FLOAT:
        buf.write(struct.pack(">f", value))
    elif tag_type == TAG_DOUBLE:
        buf.write(struct.pack(">d", value))
    elif tag_type == TAG_STRING:
        encoded = value.encode("utf-8")
        buf.write(struct.pack(">H", len(encoded)))
        buf.write(encoded)
    elif tag_type == TAG_LIST:
        element_type, elements = value
        buf.write(struct.pack(">b", element_type))
        buf.write(struct.pack(">i", len(elements)))
        for elem in elements:
            _write_payload(buf, element_type, elem)
    elif tag_type == TAG_COMPOUND:
        _write_compound_payload(buf, value)
