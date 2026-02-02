# GeoVox -- Pipeline Design

**Status: Concept** -- scaffolded, not yet implemented

## Overview

A modular pipeline for transforming real-world 3D data into playable Minecraft worlds. Takes terrain heightmaps, LiDAR point clouds, photogrammetry meshes, building footprints, and voxel grids -- and converts them into Minecraft worlds you can walk through, modify, and share.

Not a one-off heightmap importer. A composable pipeline where you swap ingest modules, palette configs, and export formats independently.

See [`ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the original concept document.

## Architecture

Three layers:

```
Input Data → [ Ingest ] → Sparse 3D Grid → [ Palette ] → Block Grid → [ Export ] → Minecraft Files
```

**Layer 1: Ingest** -- Normalize any supported format into a common sparse 3D integer grid.

**Layer 2: Palette Mapping** -- Map semantic categories (ground, vegetation, water, building) to Minecraft blocks via JSON palette configs. Palettes are swappable -- same geometry, different aesthetics.

**Layer 3: Export** -- Write the block grid to any supported Minecraft format.

## Supported Formats

### Ingest (Input)

| Format | Source | Library |
|--------|--------|---------|
| GeoTIFF heightmaps | USGS, Copernicus, national surveys | rasterio |
| LAS/LAZ point clouds | LiDAR surveys, drone scans | PDAL |
| OBJ/STL meshes | Photogrammetry, CAD exports | trimesh |
| GeoJSON polygons | OpenStreetMap, municipal GIS | built-in |
| Voxel grids (NIfTI/binvox) | Medical imaging, scientific sim | nibabel/binvox |

### Export (Output)

| Format | Use Case |
|--------|----------|
| `.mca` world files | Drop into saves folder and play |
| `.nbt` structure files | Paste into existing worlds with structure blocks |
| `.litematic` schematics | Mod-assisted building in survival |
| `.mcfunction` datapack | Server deployment via setblock commands |

## Files

```
GeoVox/
|-- SETUP.md               This file
|-- Design/
|   |-- ARCHITECTURE.md     Full technical architecture
|-- src/
|   |-- geovox/
|       |-- core/           Sparse 3D grid, common types
|       |-- ingest/         Format-specific ingest modules
|       |-- palette/        Palette loading and block mapping
|       |-- export/         Format-specific export modules
|-- palettes/               Sample palette JSON configs
|-- tests/                  Test suite
|-- examples/               Example pipelines and sample data
```

## Technical Stack

- **Python 3.10+** -- core language
- **NumPy** -- voxel grid operations
- **rasterio** -- GeoTIFF/raster ingest
- **PDAL** -- LAS/LAZ point cloud ingest
- **trimesh** -- OBJ/STL mesh voxelization
- **anvil-parser or amulet-core** -- Minecraft world I/O
- **CLI-first** -- pipe data through it, script it, batch it
- **Config-driven** -- palettes, scale, origin offset, chunk alignment all in JSON
- **No Minecraft installation required** -- reads and writes files only

## Getting Started

Not yet implemented. When development begins:

```bash
# Install
pip install -e .

# Basic usage
geovox ingest heightmap.tif --palette vanilla.json --export world --output ./my-world

# Pipeline composition
geovox ingest scan.laz | geovox palette steampunk.json | geovox export litematic -o build.litematic
```

## Hard Problems

1. **Scale management** -- 1:1 mountain ranges are billions of blocks. Needs LOD or selective import.
2. **Palette intelligence** -- Automatic material assignment from classification data is an unsolved UX problem.
3. **Minecraft constraints** -- 384-block build height (post-1.18), chunk loading radius, entity limits.

## No Dependencies (Yet)

Scaffolded directory structure only. No code, no packages, no build system. Dependencies will be added when development begins.
