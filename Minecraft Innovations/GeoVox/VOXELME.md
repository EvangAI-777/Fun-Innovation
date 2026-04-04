# GeoVox

The real world is a voxel grid. Nobody's built the pipeline to prove it.

Every city has LiDAR scans. Every national park has elevation data. Every building under construction has a CAD model. Every archaeological dig has photogrammetry. All of it is 3D data sitting in formats that require specialized software to view -- and Minecraft is a 3D engine that 200 million people already know how to use.

GeoVox connects those two facts.

## What It Is

A pipeline that converts real-world 3D data into playable Minecraft worlds, shipping as a standalone `geovox.exe` desktop application for Windows x64. The GUI draws UI principles and familiar layout concepts from WorldPainter and similar terrain editors — map viewport, brush/tool palette, layer management, import/export wizards. Each pipeline stage (ingest, palette, export) is developed and tested as a modular Python component, then compiled into the desktop application via GitHub Actions CI. Currently a heightmap importer, but architected to grow into a universal 3D-to-Minecraft pipeline. The input format, block palette, and output format are independent, swappable modules.

```
Input Data → [ Ingest ] → Sparse 3D Grid → [ Palette ] → Block Grid → [ Export ] → Minecraft Files
```

Same USGS heightmap of the Grand Canyon can render in vanilla survival blocks, in deepslate-and-copper steampunk, or in wool-and-concrete pixel art. The geometry stays the same. The aesthetics are a parameter.

## Architecture

Three independent layers: **Ingest** (normalize input to sparse 3D grid), **Palette** (map semantic categories to Minecraft blocks via JSON), **Export** (write block grid to Minecraft formats). Swap any layer without touching the others.

See [`Design/ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the theme overview.

## Technical Stack

**Current (v0.3.0):**
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
- **Binary-first distribution** -- the product is `geovox.exe`, a desktop terrain editor for Windows x64 drawing from WorldPainter's familiar layout. The Python CLI is the modular development/testing harness — each module (ingest, palette, export) is built and tested here, then compiled into the desktop application

## Hard Problems

1. **Scale management** -- 1:1 mountain ranges are billions of blocks. Needs LOD or selective import.
2. **Palette intelligence** -- Automatic material assignment from classification data is an unsolved UX problem.
3. **Minecraft constraints** -- 384-block build height (post-1.18), chunk loading radius, entity limits.

## Status

**v0.3.0 (Testing Phase) -- Preprocessing, stitching, Sponge export, palette validation.** Four export formats, heightmap preprocessing pipeline, multi-tile stitching, palette validation, and 89 tests. Full preprocessing → ingest → palette → export pipeline with comprehensive CLI.

What's here:
- **Ingest:** Grayscale PNG and GeoTIFF (via optional rasterio) heightmap reader with configurable Y scaling, sea level, and terrain layering (bedrock → stone → dirt → grass). Raw elevation stored as grid metadata.
- **Preprocessing:** Heightmap smoothing (box filter), cropping, and bilinear resampling -- all pure numpy, applied before ingest via CLI `--smooth`, `--crop`, `--resample` flags.
- **Multi-heightmap stitching:** Combine multiple heightmap tiles at arbitrary offsets with overlap averaging or last-wins mode. CLI `--stitch` flag parses `"a.png:0,0;b.png:256,0"` specs. `VoxelGrid.merge()` for post-palette grid composition.
- **Palette:** JSON config loader with weighted random block selection. Ships with vanilla-survival (built-in), steampunk (deepslate/copper), nether (netherrack/basalt), elevation-overlay (snow/ice), and slope-overlay (stone/gravel) palettes.
- **Palette composition:** `PaletteComposer` stacks multiple palette layers with condition functions (elevation, slope, custom). Later layers override earlier where conditions match. CLI `--palette` flag accepts comma-separated palette files.
- **Palette validation:** `validate_palette()` checks for missing keys, invalid block names, weight/block length mismatches, missing standard categories. CLI `geovox validate <palette.json>` subcommand.
- **Grid slope:** `compute_slope()` method on `VoxelGrid` using gradient magnitude per column via numpy.
- **Export:** `.mcfunction` setblock exporter with automatic file batching, `.nbt` structure file exporter, `.litematic` schematic exporter, and `.schem` Sponge Schematic v2 exporter (varint-encoded block data) -- all using a custom minimal NBT binary writer (no external Minecraft libraries).
- **Preview:** ASCII terrain visualization with `--stats` (min/max/mean/median/stddev) and `--color` (ANSI 256-color elevation gradient).
- **CLI:** `geovox pipeline` (with `--format mcfunction|structure|litematic|sponge`, `--palette`, `--smooth`, `--crop`, `--resample`, `--stitch`), `geovox info`, `geovox preview` (with `--stats`, `--color`), `geovox validate`
- **Tests:** 89 tests covering grid, slope, merge, palette, composer, validation, heightmap ingest, preprocessing, stitching, all four exporters, NBT writer, and full pipeline integration
- **Example:** Test terrain generator script (`examples/generate_test_terrain.py`)

Each module is developed and tested in the Python CLI, then compiled directly into `geovox.exe`. Current roadmap features are building the modules that ship inside the binary.

**What's next (v0.4.0 — Module Development + Binary Milestone):**

- **x64 Windows binary** — GitHub Actions CI workflow builds `geovox.exe` via PyInstaller/Nuitka on tagged releases, packaging all tested modules into a single downloadable desktop application
- `.mca` world file export (drop into saves and play) — requires `anvil-parser` or `amulet-core`
- Point cloud ingest (LAS/LAZ) — requires PDAL
- Mesh ingest (OBJ/STL) — requires trimesh
- Bidirectional workflow (diff modified world → export changes as 3D data)

**Primary Distribution: x64 Windows Binary**

The x64 desktop application is the product. GeoVox ships as a desktop terrain editor drawing UI principles from WorldPainter and similar tools — map viewport with pan/zoom, brush and tool palettes, layer management, import/export wizards. The familiar layout means anyone who's used WorldPainter or World Machine can sit down and start working.

Each pipeline module (ingest, palette, export, preprocessing, stitching, validation) is developed and tested as a Python component in CI. Once tested, the modules are compiled together into the `geovox.exe` desktop application via PyInstaller or Nuitka. GitHub Actions builds the binary on every tagged release.

The desktop application ships with full dependencies: scipy for signal processing, PDAL for point cloud ingest, rasterio for GeoTIFF, trimesh for mesh voxelization, rich for terminal UI — everything that was deferred as "too heavy" for a pip package. The bundled runtime handles it all. Users don't manage virtualenvs, don't install numpy, don't care about dependency trees. They download `geovox.exe` and run it.

The Python CLI remains available as the modular development/testing harness for contributors and CI. Both distribution channels serve different users, and both will be maintained.

## Dedication

Dedicated to Jonathan Doud, Taylor University classmate and collaborator/inspiration for this project.

---

*Conceived by Claude (Opus 4.5), February 2026*

*The real world is already the most detailed voxel grid there is.*
