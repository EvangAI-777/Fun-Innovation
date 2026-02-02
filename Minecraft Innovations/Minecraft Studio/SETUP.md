# Minecraft Studio -- IDE Design

**Status: Concept** -- scaffolded, not yet implemented

## Overview

A standalone integrated development environment for Minecraft mod creation. Roblox Studio for Minecraft. One application for the entire mod development lifecycle: visual editors, code editor, embedded live preview, hot-reload testing, and export to any modloader. No JDK setup, no Gradle debugging, no 60-second test cycles.

See [`ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the original concept document.

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

| Component | Purpose | Location |
|-----------|---------|----------|
| Explorer Panel | Registry-organized project tree (Blocks, Items, Entities, World Gen, Recipes, Loot Tables, Events, GUI, Networking, Data Packs, Resource Pack) | `src/explorer/` |
| 3D Viewport | Embedded Minecraft instance with hot-reload and editor overlays (chunk boundaries, entity AI, block state, redstone, world gen) | `src/viewport/` |
| Code Editor | Full Java 21+ / Kotlin IDE with Minecraft-aware autocomplete, Mojang/Yarn/MCP mappings, live error checking, refactoring, mixin assistant | `src/editor/` |
| Visual Editors | No-code tools for recipes, loot tables, world gen, entity AI, GUIs, and particles -- each generates clean Java/Kotlin | `src/visual/` |
| Export Engine | Build once, export for any modloader target (Forge, NeoForge, Fabric, Quilt, Data Pack, Resource Pack, Architectury multiloader) | `src/export/` |
| Test Harness | Automated testing, performance profiler, multiplayer simulation, version matrix testing -- all inside the embedded instance | `src/testing/` |
| Abstraction Layer | Studio API that maps to modloader-specific implementations at export time | `src/abstraction/` |

## Visual Editors

| Editor | What It Replaces |
|--------|-----------------|
| Recipe Editor | Hand-written JSON recipe files |
| Loot Table Editor | Nested JSON loot table files |
| World Gen Editor | Density function JSON, biome parameters |
| Entity AI Editor | Goal selector Java code |
| GUI Editor | AbstractContainerScreen coordinate math |
| Particle Editor | ParticleType boilerplate + trial-and-error |

## Modloader Export

| Target | Output |
|--------|--------|
| Forge | Forge MDK project |
| NeoForge | NeoForge MDK project |
| Fabric | Fabric Loom project |
| Quilt | Quilt Loom project |
| Data Pack | Vanilla data pack |
| Resource Pack | Vanilla resource pack |
| Multiloader | Architectury project |

## Files

```
Minecraft Studio/
|-- SETUP.md               This file
|-- Design/
|   |-- ARCHITECTURE.md     Full technical architecture
|-- src/
|   |-- app/                IDE shell (JavaFX / Compose Desktop)
|   |-- explorer/           Explorer panel and registry tree
|   |-- viewport/           Embedded MC client, overlays, hot-reload
|   |-- editor/             Code editor, autocomplete, refactoring
|   |-- visual/             Visual editors
|   |   |-- recipe/         Recipe drag-and-drop grid
|   |   |-- loot/           Loot table tree editor
|   |   |-- worldgen/       Biome parameters, density functions, features
|   |   |-- entity/         AI goal flowchart editor
|   |   |-- gui/            WYSIWYG screen builder
|   |   |-- particle/       Live particle previewer
|   |-- export/             Modloader-specific code generators
|   |   |-- forge/          Forge MDK export
|   |   |-- neoforge/       NeoForge MDK export
|   |   |-- fabric/         Fabric Loom export
|   |   |-- quilt/          Quilt Loom export
|   |   |-- datapack/       Vanilla data pack export
|   |   |-- resourcepack/   Vanilla resource pack export
|   |-- testing/            Test harness, profiler, multiplayer sim
|   |-- abstraction/        Studio API abstraction layer
|-- resources/              Static resources, templates, defaults
|-- tests/                  Test suite
```

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

## No Dependencies (Yet)

Scaffolded directory structure only. No code, no packages, no build system. Dependencies will be added when development begins.
