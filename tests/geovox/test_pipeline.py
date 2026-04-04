"""Integration tests for the full pipeline: ingest -> palette -> export."""

import gzip
import struct
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from geovox.core.grid import VoxelGrid
from geovox.ingest.heightmap import ingest_heightmap, BEDROCK, GROUND_DEEP, GROUND_SHALLOW, SURFACE, WATER
from geovox.palette.palette import Palette, apply_palette
from geovox.export.mcfunction import export_mcfunction
from geovox.export.structure import export_structure
from geovox.export.nbt import TAG_COMPOUND, write_nbt_file, TAG_INT, TAG_STRING
from geovox.export.litematic import export_litematic
from geovox.export.sponge import export_sponge


def _make_test_heightmap(size: int = 8, value: int = 128) -> Path:
    """Create a simple flat heightmap PNG for testing."""
    arr = np.full((size, size), value, dtype=np.uint8)
    path = Path(tempfile.mktemp(suffix=".png"))
    Image.fromarray(arr, mode="L").save(path)
    return path


def _simple_palette() -> Palette:
    return Palette(
        mappings={
            "bedrock": {"block": "minecraft:bedrock"},
            "ground_deep": {"block": "minecraft:stone"},
            "ground_shallow": {"block": "minecraft:dirt"},
            "surface": {"block": "minecraft:grass_block"},
            "water": {"block": "minecraft:water"},
        },
        name="test",
        seed=0,
    )


# --- Heightmap ingest tests ---


def test_ingest_flat():
    """A uniform heightmap should produce columns all the same height."""
    path = _make_test_heightmap(4, value=128)
    try:
        grid = ingest_heightmap(path, y_scale=(0, 64))
        assert len(grid) > 0
        # All columns should have identical structure (flat terrain)
        # With all-same-value pixels, h_max == h_min so everything normalizes to 0,
        # meaning each column has only a bedrock block at y=0.
        max_ys = set()
        for (x, y, z) in grid.cells:
            # Track the maximum y per column
            max_ys.add(y)
        # Flat means one distinct max-y across all columns
        assert len(max_ys) == 1, f"Expected uniform height, got y-levels {max_ys}"
    finally:
        path.unlink()


def test_ingest_with_sea_level():
    """Low pixels should get water fill up to sea level."""
    # Make a heightmap with low values so terrain is short
    path = _make_test_heightmap(4, value=0)
    try:
        grid = ingest_heightmap(path, y_scale=(0, 64), sea_level=32)
        water_cells = [pos for pos, val in grid.cells.items() if val == WATER]
        assert len(water_cells) > 0
    finally:
        path.unlink()


def test_ingest_metadata():
    path = _make_test_heightmap(4)
    try:
        grid = ingest_heightmap(path, y_scale=(0, 64), sea_level=32)
        assert grid.metadata["sea_level"] == 32
        assert grid.metadata["y_scale"] == (0, 64)
    finally:
        path.unlink()


# --- mcfunction export tests ---


def test_export_mcfunction_single_file():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")
    grid.set(1, 0, 0, "minecraft:dirt")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_mcfunction(grid, out)
        assert len(paths) == 1
        content = paths[0].read_text()
        assert "setblock 0 0 0 minecraft:stone" in content
        assert "setblock 1 0 0 minecraft:dirt" in content


def test_export_mcfunction_with_origin():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_mcfunction(grid, out, origin=(100, 64, 200))
        content = paths[0].read_text()
        assert "setblock 100 64 200 minecraft:stone" in content


def test_export_mcfunction_empty():
    grid = VoxelGrid()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_mcfunction(grid, out)
        assert paths == []


def test_export_mcfunction_batching():
    grid = VoxelGrid()
    for i in range(10):
        grid.set(i, 0, 0, "minecraft:stone")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_mcfunction(grid, out, batch_size=3)
        assert len(paths) == 4  # 10 blocks / 3 per batch = 4 files


# --- NBT structure export tests ---


def test_export_structure_creates_nbt():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")
    grid.set(1, 1, 1, "minecraft:dirt")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_structure(grid, out)
        assert len(paths) == 1
        assert paths[0].suffix == ".nbt"
        assert paths[0].exists()

        # Verify it's valid gzip
        with open(paths[0], "rb") as f:
            data = gzip.decompress(f.read())
        # First byte should be TAG_Compound (10)
        assert data[0] == TAG_COMPOUND


def test_export_structure_empty():
    grid = VoxelGrid()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_structure(grid, out)
        assert paths == []


def test_nbt_write_roundtrip():
    """Verify the NBT writer produces valid binary."""
    root = {
        "TestInt": (TAG_INT, 42),
        "TestString": (TAG_STRING, "hello"),
    }

    with tempfile.NamedTemporaryFile(suffix=".nbt", delete=False) as f:
        path = f.name

    try:
        write_nbt_file(path, "test", root, compress=False)
        with open(path, "rb") as f:
            data = f.read()

        # Should start with TAG_Compound header
        assert data[0] == TAG_COMPOUND
        # Root name "test" should be in the binary
        assert b"test" in data
        assert b"TestInt" in data
        assert b"hello" in data
    finally:
        Path(path).unlink()


# --- Full pipeline integration ---


def test_full_pipeline():
    """Run the full ingest -> palette -> export pipeline."""
    path = _make_test_heightmap(8, value=128)
    try:
        grid = ingest_heightmap(path, y_scale=(0, 32))
        palette = _simple_palette()
        block_grid = apply_palette(grid, palette)

        # All values should be strings now
        for val in block_grid.cells.values():
            assert isinstance(val, str)
            assert val.startswith("minecraft:")

        with tempfile.TemporaryDirectory() as tmp:
            # Test mcfunction export
            mc_paths = export_mcfunction(block_grid, Path(tmp) / "mc_out")
            assert len(mc_paths) >= 1

            # Test structure export
            nbt_paths = export_structure(block_grid, Path(tmp) / "nbt_out")
            assert len(nbt_paths) == 1
            assert nbt_paths[0].suffix == ".nbt"
    finally:
        path.unlink()


# --- Litematica export tests ---


def test_export_litematic_creates_file():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")
    grid.set(1, 1, 1, "minecraft:dirt")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_litematic(grid, out)
        assert len(paths) == 1
        assert paths[0].suffix == ".litematic"
        assert paths[0].exists()

        # Verify it's valid gzip containing NBT
        with open(paths[0], "rb") as f:
            data = gzip.decompress(f.read())
        assert data[0] == TAG_COMPOUND


def test_export_litematic_empty():
    grid = VoxelGrid()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_litematic(grid, out)
        assert paths == []


def test_export_litematic_contains_metadata():
    grid = VoxelGrid()
    grid.metadata = {"source": "test_terrain.png"}
    grid.set(0, 0, 0, "minecraft:stone")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_litematic(grid, out, name="Test Schematic", author="TestBot")
        assert len(paths) == 1
        with open(paths[0], "rb") as f:
            data = gzip.decompress(f.read())
        assert b"Test Schematic" in data
        assert b"TestBot" in data


def test_export_litematic_with_origin():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_litematic(grid, out, origin=(100, 64, 200))
        assert len(paths) == 1
        assert paths[0].exists()


def test_full_pipeline_litematic():
    path = _make_test_heightmap(4, value=128)
    try:
        grid = ingest_heightmap(path, y_scale=(0, 16))
        palette = _simple_palette()
        block_grid = apply_palette(grid, palette)

        with tempfile.TemporaryDirectory() as tmp:
            paths = export_litematic(block_grid, Path(tmp) / "lit_out")
            assert len(paths) == 1
            assert paths[0].suffix == ".litematic"
    finally:
        path.unlink()


# --- Sponge schematic export tests ---


def test_export_sponge_creates_file():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")
    grid.set(1, 1, 1, "minecraft:dirt")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_sponge(grid, out)
        assert len(paths) == 1
        assert paths[0].suffix == ".schem"
        assert paths[0].exists()

        # Verify it's valid gzip containing NBT
        with open(paths[0], "rb") as f:
            data = gzip.decompress(f.read())
        assert data[0] == TAG_COMPOUND


def test_export_sponge_empty():
    grid = VoxelGrid()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_sponge(grid, out)
        assert paths == []


def test_export_sponge_contains_metadata():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_sponge(grid, out, name="Test Sponge", author="TestBot")
        assert len(paths) == 1
        with open(paths[0], "rb") as f:
            data = gzip.decompress(f.read())
        assert b"Test Sponge" in data
        assert b"TestBot" in data


def test_export_sponge_contains_palette():
    grid = VoxelGrid()
    grid.set(0, 0, 0, "minecraft:stone")
    grid.set(1, 0, 0, "minecraft:dirt")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test"
        paths = export_sponge(grid, out)
        with open(paths[0], "rb") as f:
            data = gzip.decompress(f.read())
        assert b"minecraft:stone" in data
        assert b"minecraft:dirt" in data


def test_full_pipeline_sponge():
    path = _make_test_heightmap(4, value=128)
    try:
        grid = ingest_heightmap(path, y_scale=(0, 16))
        palette = _simple_palette()
        block_grid = apply_palette(grid, palette)

        with tempfile.TemporaryDirectory() as tmp:
            paths = export_sponge(block_grid, Path(tmp) / "sponge_out")
            assert len(paths) == 1
            assert paths[0].suffix == ".schem"
    finally:
        path.unlink()
