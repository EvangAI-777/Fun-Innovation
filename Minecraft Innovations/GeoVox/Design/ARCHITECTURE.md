# GeoVox Architecture

Full technical design for the real-world data to Minecraft pipeline.

## Overview

GeoVox is a three-layer pipeline: **Ingest → Palette → Export**. Each layer is modular. Any ingest module can feed any palette, and any palette can feed any exporter. The common internal representation between layers is a **sparse 3D integer grid** -- each cell holds a block ID or semantic category tag.

## Layer 1: Ingest

Each ingest module reads a specific data format and normalizes it into the common grid representation.

### Modules

| Module | Input Format | Strategy |
|--------|-------------|----------|
| `geotiff` | GeoTIFF heightmaps (.tif) | Read elevation raster, map each pixel to a column of blocks. Elevation value → column height. Classification bands → semantic tags. |
| `pointcloud` | LAS/LAZ point clouds (.las, .laz) | Bin points into voxel cells. Point classification codes (ground, vegetation, building) become semantic tags. Density thresholds for solid vs. empty. |
| `mesh` | OBJ/STL meshes (.obj, .stl) | Scanline voxelization. Ray-cast along each axis to determine interior/exterior/surface. Surface normals inform orientation-dependent block placement. |
| `geojson` | GeoJSON polygons (.geojson) | Extrude 2D polygons to 3D based on height properties. Building footprints become solid volumes. Road polygons become surface layers. |
| `voxel` | NIfTI/binvox (.nii, .binvox) | Direct read -- data is already voxelized. Map integer labels to semantic categories. |

### Common Grid Format

```python
class VoxelGrid:
    """Sparse 3D integer grid. Keys are (x, y, z) tuples. Values are semantic category IDs."""
    cells: dict[tuple[int, int, int], int]
    metadata: dict  # CRS, origin, scale, source info
```

Sparse representation keeps memory manageable for large, mostly-empty volumes (a mountain range is mostly air). Dense operations (NumPy arrays) used for bounded subregions when performance matters.

### Coordinate System

- X: East-West (Minecraft X)
- Y: Vertical (Minecraft Y)
- Z: North-South (Minecraft Z)
- Origin configurable via CLI (default: center of input data → Minecraft 0,64,0)
- Scale configurable (default: 1 meter = 1 block)

## Layer 2: Palette Mapping

Transforms a grid of semantic category IDs into a grid of Minecraft block IDs.

### Palette Format

JSON config files:

```json
{
  "name": "vanilla-survival",
  "description": "Standard Minecraft survival blocks",
  "version": "1.21",
  "mappings": {
    "ground_low": {
      "blocks": ["minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt"],
      "weights": [0.7, 0.2, 0.1]
    },
    "ground_high": {
      "blocks": ["minecraft:stone", "minecraft:andesite", "minecraft:diorite"],
      "weights": [0.6, 0.2, 0.2]
    },
    "water": {
      "block": "minecraft:water",
      "depth_absorption": true
    },
    "vegetation": {
      "blocks": ["minecraft:oak_leaves", "minecraft:birch_leaves"],
      "weights": [0.6, 0.4]
    },
    "building_wall": {
      "blocks": ["minecraft:bricks", "minecraft:stone_bricks", "minecraft:smooth_stone"],
      "weights": [0.4, 0.4, 0.2]
    },
    "building_roof": {
      "blocks": ["minecraft:dark_oak_planks", "minecraft:spruce_planks"],
      "weights": [0.5, 0.5]
    },
    "road": {
      "blocks": ["minecraft:gray_concrete", "minecraft:stone_slab"],
      "weights": [0.7, 0.3]
    }
  }
}
```

### Palette Composition

Multiple palette layers can stack:

1. **Elevation** drives base material (low ground → grass, high ground → stone)
2. **Slope angle** adds variation (cliff faces get exposed stone regardless of elevation)
3. **Moisture/satellite data** shifts vegetation density
4. **Classification labels** from LiDAR override everything where they exist

The system composes these layers in priority order. Later layers override earlier ones where they have data.

### Palette Library

Sample palettes to ship with the tool:

- `vanilla-survival.json` -- Standard Minecraft blocks
- `steampunk.json` -- Deepslate, copper, tuff, dark wood
- `pixel-art.json` -- Wool and concrete for flat-color rendering
- `nether.json` -- Nether blocks for alien terrain
- `end.json` -- End stone, purpur, chorus for otherworldly landscapes

## Layer 3: Export

Writes the final block grid to Minecraft-compatible formats.

### Exporters

| Exporter | Output | Notes |
|----------|--------|-------|
| `world` | `.mca` region files | Full playable world. Handles chunk/section layout, biome assignment, heightmap recalculation, light propagation. Drop into saves folder. |
| `structure` | `.nbt` structure files | For pasting into existing worlds via structure blocks. Max 48x48x48 per structure; large builds auto-split. |
| `litematica` | `.litematic` schematics | For Litematica mod users. Includes material list metadata. |
| `datapack` | `.mcfunction` files | `setblock` commands. Slow but works on any server. Includes batch chunking to avoid command limits. |

### World Export Details

The `.mca` exporter is the most complex:

1. **Chunk generation** -- 16x16 columns, 16-block-tall sections
2. **Block palette** -- Per-section palette compression (Minecraft's internal format)
3. **Biome assignment** -- Based on palette metadata or input data classification
4. **Heightmap calculation** -- WORLD_SURFACE, OCEAN_FLOOR, MOTION_BLOCKING computed from block data
5. **Light propagation** -- Sky light from top, block light from emissive blocks
6. **Spawn point** -- Placed at the highest solid block near grid center

## CLI Design

```
geovox <command> [options]

Commands:
  ingest <file>       Read input data into grid format
  palette <config>    Apply palette mapping to grid
  export <format>     Write grid to Minecraft format
  pipeline <config>   Run a full ingest→palette→export pipeline from config
  info <file>         Show metadata about an input file
  preview <file>      ASCII preview of grid contents

Global options:
  --scale <float>     Meters per block (default: 1.0)
  --origin <x,y,z>    Minecraft origin for grid center
  --verbose           Show progress and statistics
  --output, -o        Output path
```

## Bidirectional Workflow

The reverse path: modified Minecraft world → diff → 3D export.

1. Import original data as world A
2. Player/builder modifies world → world B
3. GeoVox diffs A and B at the block level
4. Changed blocks exported as point cloud, mesh, or heightmap delta
5. Minecraft becomes a 3D voxel editor for landscape architecture, urban planning, or terrain proposals

This is a stretch goal -- the forward path (data → Minecraft) ships first.

---

*Full concept details in [`../MCME.md`](../MCME.md)*
