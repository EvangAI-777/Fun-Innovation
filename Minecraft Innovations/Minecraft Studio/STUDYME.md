# Minecraft Studio

Roblox has 70 million daily active users, and a significant percentage of them are *creators*. That's not because Roblox is a better game than Minecraft. It's because Roblox has Studio.

Minecraft modding is one of the most productive creative communities in software history. And the tooling is decades behind what Roblox gives its creators out of the box. A thirteen-year-old can open Roblox Studio and have a working multiplayer game in an hour. A Minecraft modder needs a JDK, a Gradle buildscript, decompiled source, and 60 seconds of patience every time they change a line of code.

Minecraft Studio would be the ladder over that cliff face.

## What It Is

A standalone integrated development environment for Minecraft mod creation. One application. Download, install, open, create. Visual editors for the 80% case. Full code access for the 20% that needs it. An embedded Minecraft instance running your mod in real time with hot-reload. Export to any modloader with one click.

```
+---------------------------------------------------------------+
|  Minecraft Studio                                    [- o x]  |
+----------+------------------------------------+---------------+
|          |                                    |               |
| Explorer |         3D Viewport                |  Properties   |
|          |                                    |               |
| > Blocks |   [Live preview of your mod        |  Block: Stone |
| > Items  |    running in an embedded          |  Hardness: 1.5|
| > Entities    Minecraft instance]             |  Blast Res: 6 |
| > World  |                                    |  Tool: Pickaxe|
| > Recipes|                                    |  Drop: Cobble |
| > Events |                                    |  Light: 0     |
|          |                                    |  Flammable: No|
+----------+---------+--------------------------+---------------+
|  Code Editor       |  Visual Editor                          |
|                    |                                          |
|  @Mod("mymod")     |  [Recipe grid]  [Loot table tree]       |
|  public class ...  |  [World gen visual]  [GUI builder]      |
+--------------------+------------------------------------------+
|  Console / Output / Build Log                      [Play >]  |
+---------------------------------------------------------------+
```

## Components

| Component | What It Does | Location |
|-----------|-------------|----------|
| Explorer Panel | Registry-organized project tree -- Blocks, Items, Entities, World Gen, Recipes, Loot Tables, Events, GUI, Networking, Data Packs, Resource Pack | `src/explorer/` |
| 3D Viewport | Embedded Minecraft instance with hot-reload and editor overlays (chunk boundaries, entity AI, block state, redstone, world gen debug, freeze frame) | `src/viewport/` |
| Code Editor | Full Java 21+ / Kotlin IDE with Minecraft-aware autocomplete, Mojang/Yarn/MCP mappings, live error checking, refactoring, mixin assistant | `src/editor/` |
| Visual Editors | No-code tools for recipes, loot tables, world gen, entity AI, GUIs, and particles -- each generates clean Java/Kotlin behind the scenes | `src/visual/` |
| Export Engine | Build once, export for any modloader (Forge, NeoForge, Fabric, Quilt, Data Pack, Resource Pack, Architectury multiloader) | `src/export/` |
| Test Harness | Automated testing inside the embedded instance, performance profiler, multiplayer simulation, version matrix testing | `src/testing/` |
| Abstraction Layer | Studio API that maps to modloader-specific implementations at export time | `src/abstraction/` |

## The Visual Editors

These are the tools that don't exist anywhere in the Minecraft modding ecosystem today.

| Editor | What It Replaces | What You Actually Do |
|--------|-----------------|---------------------|
| Recipe Editor | Hand-written JSON | Drag items into a 3x3 grid, set output, done |
| Loot Table Editor | Nested JSON nightmares | Tree view with probability sliders and condition checkboxes |
| World Gen Editor | Inscrutable density function JSON | Node graph like Blender shader nodes + live biome parameter scatter plot |
| Entity AI Editor | Goal selector Java code | Flowchart of behavior priorities, drag to reorder |
| GUI Editor | AbstractContainerScreen coordinate math | WYSIWYG drag-and-drop screen builder |
| Particle Editor | ParticleType boilerplate + trial-and-error | Live 3D preview with sliders for everything |

Every visual editor generates clean, readable code behind the scenes. If you never open the code tab, you can still make a mod. If you do open it, you see idiomatic Java/Kotlin that you can customize further. Visual tools for accessibility, full code access for power.

## Modloader Export

Build once. Ship everywhere. The modloader wars become irrelevant for creators.

| Target | Output |
|--------|--------|
| Forge | Forge MDK project |
| NeoForge | NeoForge MDK project |
| Fabric | Fabric Loom project |
| Quilt | Quilt Loom project |
| Data Pack | Vanilla data pack |
| Resource Pack | Vanilla resource pack |
| Multiloader | Architectury project |

See [`ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the original concept document.

## Technical Stack

- **Java 21+** -- core language (matches Minecraft)
- **Kotlin** -- first-class alternative language support
- **JavaFX or Compose Desktop** -- IDE shell and UI framework
- **Embedded Minecraft client** -- classloader isolation with hot-reload hooks
- **Eclipse ECJ / Kotlin compiler daemon** -- incremental compilation for sub-second rebuild
- **Mojang mappings + intermediary** -- decompiled source browsing and autocomplete
- **AST manipulation** -- modloader-specific code generation from abstraction layer
- **Gradle daemon** -- final export builds (exported projects are standard Gradle projects)
- **SQLite** -- project metadata, asset registry, undo history
- **Git integration** -- built-in version control

## Hard Problems

1. **Hot-reload cycle** -- Minecraft wasn't designed for class hot-swapping. Solution: custom classloader that isolates mod classes from Minecraft core, discard and recreate on recompile while preserving instance state.
2. **Abstraction layer completeness** -- Thin enough that exported code is readable, complete enough that 95% of mod functionality doesn't require loader-specific code.

## Status

**Layer 1: Data model + export engine -- implemented.** v0.2.0. Zero external dependencies. `pip install -e .` then `mcstudio` to use.

What's built:

| Module | What it does |
|--------|-------------|
| `mcstudio.model.project` | Complete mod project container with JSON save/load, registry management, Java class/package name generation, duplicate ID enforcement across all registries |
| `mcstudio.model.block` | Block definitions -- 14 material types, hardness, resistance, luminance, tool requirements, drops, collision, transparency. Resource location ID validation |
| `mcstudio.model.item` | Item definitions -- stack sizes, creative tabs, food properties (nutrition, saturation, meat, always-edible), tool properties (tier, damage, speed, durability). Resource location ID validation |
| `mcstudio.model.recipe` | All 7 vanilla recipe types -- shaped, shapeless, smelting, blasting, smoking, stonecutting, smithing transform |
| `mcstudio.model.loot` | Loot tables with pools, weighted entries, all 6 condition types (silk touch, without silk touch, match tool, explosion, player kill, random chance with configurable probability), functions (set count, enchant, looting) |
| `mcstudio.model.entity` | Entity type definitions -- 8 base classes (LivingEntity through TamableAnimal), 15 AI goal types, entity attributes, spawn rules with biome targeting and mob categories, hitbox dimensions |
| `mcstudio.model.worldgen` | World generation -- biomes with multi-noise parameters (temperature, humidity, continentalness, erosion, depth, weirdness), sky/fog/water/grass colors, 11 feature types, placement configs with height ranges |
| `mcstudio.codegen.java` | Java source code builder -- packages, imports, classes, fields, methods, annotations, with proper formatting and import grouping |
| `mcstudio.export.fabric` | Full Fabric Loom project export -- build.gradle, fabric.mod.json, mod class with ModInitializer, block/item registries via Registry.register, recipes, loot tables, blockstate/model JSONs, placeholder textures |
| `mcstudio.export.forge` | Full Forge Gradle project export -- build.gradle, mods.toml, @Mod class, DeferredRegister block/item registries, recipes, loot tables, blockstate/model JSONs, placeholder textures. Version table mapping MC versions to Forge/MCP/Gradle versions |
| `mcstudio.export.neoforge` | Full NeoForge Gradle project export -- neoforge.mods.toml, DeferredBlock/DeferredItem registries, IEventBus constructor injection, NeoForge-specific API patterns, placeholder textures |
| `mcstudio.export.datapack` | Vanilla data pack export -- pack.mcmeta, recipe JSONs, loot table JSONs |
| `mcstudio.texgen` | Zero-dependency placeholder PNG texture generator -- solid-color 16x16 textures based on block material and item type, using only stdlib struct + zlib |
| `mcstudio.cli` | CLI with 6 commands: new, add-block, add-item, export, info, loaders |

118 passing tests across 3 test files. Exported Fabric/Forge/NeoForge projects are standard Gradle projects with idiomatic registration patterns and visible placeholder textures.

Every piece of this puzzle has been built in isolation by the Minecraft modding community -- Blockbench for visual tooling, Architectury for cross-loader abstraction, IntelliJ's Minecraft Development plugin for IDE integration. Nobody has assembled them into one coherent application. The data model and export engine are the foundation that proves the abstraction works. Visual editors, the embedded viewport, and the full IDE shell build on top.

---

*Conceived by Claude (Opus 4.5), February 2026. Layer 1 built by Claude (Opus 4.6), February 2026. Layer 2 additions (NeoForge, entities, world gen, textures, validation) by Claude (Opus 4.6), March 2026.*

*Because every coordinate system eventually leads to Minecraft.*
