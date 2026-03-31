# Dual-Project Roadmap Plan: GeoVox v0.2.0 + Minecraft Studio v0.3.0

## Context

GeoVox (v0.1.1) and Minecraft Studio (v0.2.0) are both at natural inflection points. GeoVox has a working pipeline but its documented next steps (`.mca` export, LAS/LAZ, OBJ/STL) all require heavy external dependencies — conflicting with the project's minimal-deps philosophy. Minecraft Studio completed Layer 1 but has two unfinished gaps (entity and worldgen export) plus a full Layer 2 ahead.

This plan identifies what's **feasible and high-impact** for each project's next version bump, respecting the zero/minimal-dependency constraint and the small-commit workflow.

---

## GeoVox: v0.1.1 → v0.2.0

### Theme: "Palette Composition + Export Polish"

The top roadmap item (`.mca` export) requires `anvil-parser` or `amulet-core`. The next two items require PDAL and trimesh. **Palette composition** is the first roadmap item achievable with zero new dependencies — and it's a meaningful capability upgrade that makes existing features more powerful.

### What to Build

#### 1. Palette Composition Engine (High Priority)
Stack multiple palette layers so that elevation, slope, and moisture can all influence block selection simultaneously.

**Files to create/modify:**
- `Minecraft Innovations/GeoVox/src/geovox/palette/composer.py` (NEW) — `PaletteComposer` class that accepts ordered palette layers with priority rules
- `Minecraft Innovations/GeoVox/src/geovox/palette/palette.py` — Add `merge()` or `compose()` method to `Palette` class for combining palettes
- `Minecraft Innovations/GeoVox/src/geovox/cli.py` — Add `--palette` flag support for multiple palette files (comma-separated or repeated flag)
- `Minecraft Innovations/GeoVox/palettes/elevation-overlay.json` (NEW) — Example overlay palette keyed to elevation bands
- `Minecraft Innovations/GeoVox/palettes/slope-overlay.json` (NEW) — Example overlay palette for steep vs flat terrain
- `tests/geovox/test_composer.py` (NEW) — Tests for palette composition

**Design:**
- A `PaletteComposer` takes a list of `(Palette, condition_fn)` tuples
- Each layer can override specific categories based on grid metadata (elevation, slope angle, position)
- Later layers override earlier ones where their conditions match
- The base palette always provides defaults; overlays selectively override
- Slope calculation from the heightmap grid (gradient approximation using neighboring cells) — uses numpy, no new deps

#### 2. Litematica Export (Medium Priority)
`.litematic` is the second planned export format and can be implemented **without external dependencies** — it's a custom NBT format (which GeoVox already has a writer for).

**Files to create/modify:**
- `Minecraft Innovations/GeoVox/src/geovox/export/litematic.py` (NEW) — Litematica schematic exporter using existing `nbt.py` writer
- `Minecraft Innovations/GeoVox/src/geovox/export/__init__.py` — Register new exporter
- `Minecraft Innovations/GeoVox/src/geovox/cli.py` — Add `litematic` to `--format` choices
- `tests/geovox/test_pipeline.py` — Add litematic export tests

**Why this works without deps:** The existing `nbt.py` is a custom minimal NBT binary writer. Litematica's `.litematic` format is NBT-based (similar to `.nbt` structures but with different schema). Reuse the existing writer with a new schema layout.

#### 3. Grid Enhancements for Composition (Supporting)
Add slope/gradient calculation to the VoxelGrid so palette composition has terrain metadata to work with.

**Files to modify:**
- `Minecraft Innovations/GeoVox/src/geovox/core/grid.py` — Add `compute_slope()` method that calculates gradient magnitude per column using numpy
- `Minecraft Innovations/GeoVox/src/geovox/ingest/heightmap.py` — Store raw elevation array as grid metadata for slope computation
- `tests/geovox/test_grid.py` — Tests for slope computation

#### 4. Version Bump + Docs
- `Minecraft Innovations/GeoVox/src/geovox/__init__.py` — Bump to `0.2.0`
- `Minecraft Innovations/GeoVox/VOXELME.md` — Update status section

---

## Minecraft Studio: v0.2.0 → v0.3.0

### Theme: "Complete the Export Engine"

The ROADMAP_1.0.md explicitly defines v0.3.0 as "Layer 1 Completion — Finish the Export Engine." Entity and worldgen models exist but generate no code. This is the natural and documented next step.

### What to Build

#### 1. Entity Code Generation — All Loaders (High Priority)
Entity types are fully modeled (`model/entity.py`: 8 base classes, 15 AI goal types, attributes, spawn rules) but produce no Java output.

**Files to create/modify:**
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/codegen/entity.py` (NEW) — Entity Java class generator (extends appropriate base class, registers attributes, adds AI goals, spawn egg)
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/fabric.py` — Add entity registration (Registry.register for EntityType, spawn egg item, renderer stub, attributes event)
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/forge.py` — Add entity registration (DeferredRegister<EntityType>, ForgeSpawnEggItem, EntityAttributeCreationEvent)
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/neoforge.py` — Add entity registration (NeoForge DeferredHolder, RegisterSpawnPlacementsEvent)
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/datapack.py` — Entity type tags if applicable
- `tests/mcstudio/test_codegen.py` — Entity codegen tests
- `tests/mcstudio/test_export.py` — Entity export tests for each loader

**Scope per loader:**
- Entity class extending base (Mob, Animal, Monster, etc.)
- `createAttributes()` method with attribute values
- AI goal registration in `registerGoals()`
- Spawn egg item registration
- Renderer stub class
- Entity type registration with dimensions and spawn rules

#### 2. World Gen / Biome JSON Generation (High Priority)
Worldgen model exists (`model/worldgen.py`: biomes with multi-noise params, 11 feature types, placement configs) but generates no output.

**Files to create/modify:**
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/codegen/worldgen.py` (NEW) — ConfiguredFeature and PlacedFeature Java generation
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/datapack.py` — Biome JSON, configured_feature JSON, placed_feature JSON generation
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/fabric.py` — BiomeModifications API calls for Fabric
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/forge.py` — BiomeLoadingEvent / BiomeModifier JSON for Forge
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/neoforge.py` — NeoForge BiomeModifier pattern
- `tests/mcstudio/test_codegen.py` — Worldgen codegen tests
- `tests/mcstudio/test_export.py` — Worldgen export tests

#### 3. Language File Generation (Small, High Priority)
`en_us.json` lang file generation for all exporters — currently no translatable names are generated.

**Files to modify:**
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/base.py` — Add `generate_lang()` method to base exporter
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/fabric.py` — Call lang generation, write `en_us.json`
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/forge.py` — Same
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/neoforge.py` — Same
- Tests for lang file output

**Logic:** Auto-generate translation keys from block/item/entity IDs using Minecraft's naming convention (`block.mod_id.block_name`, `item.mod_id.item_name`, `entity.mod_id.entity_name`). Convert snake_case IDs to Title Case display names.

#### 4. Tag Generation (Small, High Priority)
Block, item, and entity type tag JSON files.

**Files to modify:**
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/model/block.py` — Add `tags` field (e.g., `mineable/pickaxe`, `needs_stone_tool`)
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/model/item.py` — Add `tags` field
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/export/base.py` — Tag JSON generation logic
- All loader exporters — Write tag files to `data/mod_id/tags/`
- Tests for tag generation

#### 5. Creative Tab Registration (Small, High Priority)
Currently blocks and items are registered but not assigned to creative tabs.

**Files to modify:**
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/model/project.py` — Add creative tab definition to project model
- All loader exporters — Add creative tab registration code (Fabric: ItemGroupEvents, Forge: CreativeModeTabEvent, NeoForge: BuildCreativeModeTabContentsEvent)
- Tests

#### 6. Version Bump + Docs
- `Minecraft Innovations/Minecraft Studio/pyproject.toml` — Bump to `0.3.0`
- `Minecraft Innovations/Minecraft Studio/src/mcstudio/__init__.py` — Bump version
- `Minecraft Innovations/Minecraft Studio/STUDYME.md` — Update status

---

## Sequencing Strategy

Interleave work between projects in logical units to keep commits small and progress steady:

### Phase A: GeoVox Foundation
1. Grid slope computation (`grid.py` + tests)
2. Palette composer core (`composer.py` + tests)
3. CLI integration for multi-palette (`cli.py`)
4. Example overlay palettes (2 JSON files)

### Phase B: Minecraft Studio Entity Export
5. Entity codegen module (`codegen/entity.py` + tests)
6. Fabric entity export (modify `fabric.py` + tests)
7. Forge entity export (modify `forge.py` + tests)
8. NeoForge entity export (modify `neoforge.py` + tests)

### Phase C: GeoVox Litematica
9. Litematica exporter (`export/litematic.py` + tests)
10. CLI format option + export registry update

### Phase D: Minecraft Studio Worldgen + Polish
11. Biome/feature JSON generation for datapacks
12. Worldgen codegen for Fabric/Forge/NeoForge
13. Language file generation (all loaders)
14. Tag generation (all loaders)
15. Creative tab registration (all loaders)

### Phase E: Version Bumps
16. GeoVox version bump to 0.2.0 + doc updates
17. Minecraft Studio version bump to 0.3.0 + doc updates

---

## Verification

After implementation, verify with:

```bash
make test-geovox      # Should pass 27 existing + new composer/litematic/slope tests
make test-mcstudio    # Should pass 118 existing + new entity/worldgen/lang/tag tests
make test             # Full suite — all 644+ tests pass
```

Additionally:
- `geovox pipeline terrain.png -o test --palette palettes/vanilla-survival.json,palettes/elevation-overlay.json` should compose palettes
- `geovox pipeline terrain.png -o test --format litematic` should produce a valid `.litematic` file
- `mcstudio new test_mod && mcstudio add-block test_mod stone_block && mcstudio export test_mod fabric` should produce a project with `en_us.json` and tag files

---

## Key Files Referenced (Existing, to Reuse)

| File | What to Reuse |
|------|---------------|
| `GeoVox/src/geovox/export/nbt.py` | NBT binary writer — reuse for litematica format |
| `GeoVox/src/geovox/palette/palette.py` | `Palette` class, `resolve()`, `apply_palette()` |
| `GeoVox/src/geovox/core/grid.py` | `VoxelGrid` sparse grid with metadata |
| `GeoVox/src/geovox/ingest/heightmap.py` | Heightmap → grid with elevation data |
| `Studio/src/mcstudio/codegen/java.py` | `JavaWriter` class for Java source generation |
| `Studio/src/mcstudio/model/entity.py` | Entity model (8 base types, 15 AI goals) |
| `Studio/src/mcstudio/model/worldgen.py` | Biome + feature models |
| `Studio/src/mcstudio/export/base.py` | Base `Exporter` ABC and dispatch registry |
| `Studio/src/mcstudio/export/fabric.py` | Fabric export patterns to extend |
| `Studio/src/mcstudio/export/forge.py` | Forge export patterns to extend |
| `Studio/src/mcstudio/export/neoforge.py` | NeoForge export patterns to extend |

---

## Scope Summary

| Project | Version | New Files | Modified Files | Est. New Tests |
|---------|---------|-----------|----------------|----------------|
| GeoVox | 0.2.0 | 4 (composer.py, litematic.py, 2 palette JSONs) | 5 (grid.py, heightmap.py, palette.py, cli.py, __init__.py) | ~20-25 |
| Minecraft Studio | 0.3.0 | 2 (entity.py, worldgen.py codegen) | 8 (all exporters, block/item models, project.py) | ~30-40 |
