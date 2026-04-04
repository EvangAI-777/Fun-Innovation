# GeoVox

The real world is a voxel grid. Nobody's built the pipeline to prove it.

Every city has LiDAR scans. Every national park has elevation data. Every building under construction has a CAD model. Every archaeological dig has photogrammetry. All of it is 3D data sitting in formats that require specialized software to view -- and Minecraft is a 3D engine that 200 million people already know how to use.

GeoVox connects those two facts.

## What It Is

A modular Python pipeline that takes real-world 3D data and converts it into playable Minecraft worlds. Currently a heightmap importer, but architected to grow into a universal 3D-to-Minecraft pipeline. The input format, block palette, and output format are independent, swappable modules.

```
Input Data → [ Ingest ] → Sparse 3D Grid → [ Palette ] → Block Grid → [ Export ] → Minecraft Files
```

Same USGS heightmap of the Grand Canyon can render in vanilla survival blocks, in deepslate-and-copper steampunk, or in wool-and-concrete pixel art. The geometry stays the same. The aesthetics are a parameter.

## Architecture

Three independent layers: **Ingest** (normalize input to sparse 3D grid), **Palette** (map semantic categories to Minecraft blocks via JSON), **Export** (write block grid to Minecraft formats). Swap any layer without touching the others.

See [`Design/ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the theme overview.

## Technical Stack

**Current (v0.2.0):**
- **Python 3.10+** -- core language
- **NumPy** -- voxel grid operations
- **Pillow** -- PNG heightmap ingest
- **rasterio** (optional) -- GeoTIFF ingest
- **Custom NBT writer** -- .nbt structure export without external Minecraft libraries

**Planned:**
- **PDAL** -- LAS/LAZ point cloud ingest
- **trimesh** -- OBJ/STL mesh voxelization
- **anvil-parser or amulet-core** -- .mca world file export

**Design principles:**
- **CLI-first** -- pipe data through it, script it, batch it
- **Config-driven** -- palettes, scale, origin offset all in JSON
- **No Minecraft installation required** -- reads and writes files only

## Hard Problems

1. **Scale management** -- 1:1 mountain ranges are billions of blocks. Needs LOD or selective import.
2. **Palette intelligence** -- Automatic material assignment from classification data is an unsolved UX problem.
3. **Minecraft constraints** -- 384-block build height (post-1.18), chunk loading radius, entity limits.

## Status

**v0.2.0 -- Palette composition, Litematica export, slope computation.** Three export formats, terrain-aware palette composition, and 48 tests. The pipeline now supports stacking multiple palette layers with elevation/slope conditions, outputting `.litematic` schematics alongside `.mcfunction` and `.nbt`.

What's here:
- **Ingest:** Grayscale PNG and GeoTIFF (via optional rasterio) heightmap reader with configurable Y scaling, sea level, and terrain layering (bedrock → stone → dirt → grass). Raw elevation stored as grid metadata.
- **Palette:** JSON config loader with weighted random block selection. Ships with vanilla-survival (built-in), steampunk (deepslate/copper), nether (netherrack/basalt), elevation-overlay (snow/ice), and slope-overlay (stone/gravel) palettes.
- **Palette composition:** `PaletteComposer` stacks multiple palette layers with condition functions (elevation, slope, custom). Later layers override earlier where conditions match. CLI `--palette` flag accepts comma-separated palette files.
- **Grid slope:** `compute_slope()` method on `VoxelGrid` using gradient magnitude per column via numpy.
- **Export:** `.mcfunction` setblock exporter with automatic file batching, `.nbt` structure file exporter, and `.litematic` schematic exporter -- all using a custom minimal NBT binary writer (no external Minecraft libraries).
- **CLI:** `geovox pipeline` (with `--format mcfunction|structure|litematic`, `--palette`), `geovox info`, `geovox preview` (ASCII terrain visualization)
- **Tests:** 48 tests covering grid, slope, palette, composer, heightmap ingest, all three exporters, NBT writer, and full pipeline integration
- **Example:** Test terrain generator script (`examples/generate_test_terrain.py`)

**What's next (v0.3.0):**

- **Multi-heightmap stitching** — Combine multiple heightmaps into one grid for large-area terrain
- **Sponge schematic export** — `.schem` format (also NBT-based, like litematica)
- **Heightmap preprocessing** — Smoothing, cropping, resampling (numpy only)
- **Preview enhancements** — Richer ASCII visualization, statistics output
- **Palette validation/linting** — Check palette JSON for errors, missing categories

**Longer-term roadmap:**
- `.mca` world file export (drop into saves and play) — requires `anvil-parser` or `amulet-core`
- Point cloud ingest (LAS/LAZ) — requires PDAL
- Mesh ingest (OBJ/STL) — requires trimesh
- Bidirectional workflow (diff modified world → export changes as 3D data)

## Dedication

Dedicated to Jonathan Doud, Taylor University classmate and collaborator/inspiration for this project.

---

*Conceived by Claude (Opus 4.5), February 2026*

*The real world is already the most detailed voxel grid there is.*
