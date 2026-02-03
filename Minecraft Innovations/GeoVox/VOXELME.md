# GeoVox

The real world is a voxel grid. Nobody's built the pipeline to prove it.

Every city has LiDAR scans. Every national park has elevation data. Every building under construction has a CAD model. Every archaeological dig has photogrammetry. All of it is 3D data sitting in formats that require specialized software to view -- and Minecraft is a 3D engine that 200 million people already know how to use.

GeoVox connects those two facts.

## What It Is

A modular Python pipeline that takes real-world 3D data and converts it into playable Minecraft worlds. Not a heightmap importer. Not a one-off script. A composable system where the input format, the block palette, and the output format are all independent, swappable modules.

```
Input Data → [ Ingest ] → Sparse 3D Grid → [ Palette ] → Block Grid → [ Export ] → Minecraft Files
```

Same USGS heightmap of the Grand Canyon can render in vanilla survival blocks, in deepslate-and-copper steampunk, or in wool-and-concrete pixel art. The geometry stays the same. The aesthetics are a parameter.

## Architecture

Three layers. Each is independent. Swap any of them without touching the others.

**Layer 1: Ingest** -- Normalize any supported format into a common sparse 3D integer grid.

| Format | Source | Library |
|--------|--------|---------|
| GeoTIFF heightmaps | USGS, Copernicus, national surveys | rasterio |
| LAS/LAZ point clouds | LiDAR surveys, drone scans | PDAL |
| OBJ/STL meshes | Photogrammetry, CAD exports | trimesh |
| GeoJSON polygons | OpenStreetMap, municipal GIS | built-in |
| Voxel grids (NIfTI/binvox) | Medical imaging, scientific sim | nibabel/binvox |

**Layer 2: Palette Mapping** -- Map semantic categories (ground, vegetation, water, building) to Minecraft blocks via JSON config. Palettes are swappable. Multiple layers can stack -- elevation drives base material, slope adds cliff faces, moisture shifts vegetation, LiDAR classification overrides everything.

**Layer 3: Export** -- Write the block grid out.

| Format | Use Case |
|--------|----------|
| `.mca` world files | Drop into saves folder and play |
| `.nbt` structure files | Paste into existing worlds with structure blocks |
| `.litematic` schematics | Mod-assisted building in survival |
| `.mcfunction` datapack | Server deployment via setblock commands |

## What You Could Build With This

Your neighborhood from a city LiDAR scan. A national park at 1:1 scale. A building you're designing, walked through in VR before it's built. A Roman villa reconstructed from photogrammetry. A protein structure. A fluid dynamics simulation. Minecraft as a renderer for anything that exists in three dimensions.

The bidirectional part matters too. Modify the Minecraft world -- add a building, dig a canal, terraform a hillside -- and diff the changes back as a point cloud or mesh. Minecraft becomes a voxel-native sketch tool for landscape architecture, urban planning, or terrain modification proposals.

## Files

```
GeoVox/
|-- VOXELME.md             This file
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

See [`ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the original concept document.

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

## Hard Problems

1. **Scale management** -- 1:1 mountain ranges are billions of blocks. Needs LOD or selective import.
2. **Palette intelligence** -- Automatic material assignment from classification data is an unsolved UX problem.
3. **Minecraft constraints** -- 384-block build height (post-1.18), chunk loading radius, entity limits.

## Status

**v0.1.1 -- Structure export and palette variety.** Two export formats, themed palettes, and a full test suite. The pipeline can now output both `.mcfunction` setblock commands and `.nbt` structure files loadable via structure blocks.

What's here:
- **Ingest:** Grayscale PNG and GeoTIFF (via optional rasterio) heightmap reader with configurable Y scaling, sea level, and terrain layering (bedrock → stone → dirt → grass)
- **Palette:** JSON config loader with weighted random block selection. Ships with vanilla-survival (built-in), steampunk (deepslate/copper), and nether (netherrack/basalt) palettes.
- **Export:** `.mcfunction` setblock exporter with automatic file batching, plus `.nbt` structure file exporter using a custom minimal NBT binary writer
- **CLI:** `geovox pipeline` (with `--format mcfunction|structure`), `geovox info`, `geovox preview` (ASCII terrain visualization)
- **Tests:** 27 tests covering grid, palette, heightmap ingest, both exporters, NBT writer, and full pipeline integration
- **Example:** Test terrain generator script (`examples/generate_test_terrain.py`)

What's next: `.mca` world file export (drop into saves and play), point cloud ingest (LAS/LAZ), mesh ingest (OBJ/STL), palette composition (stacking multiple layers), and the bidirectional workflow.

## Dedication

Dedicated to Jonathan Doud, Taylor University classmate and collaborator/inspiration for this project.

---

*Conceived by Claude (Opus 4.5), February 2026*

*The real world is already the most detailed voxel grid there is.*
