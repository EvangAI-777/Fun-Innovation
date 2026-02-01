# Minecraft Studio

A standalone integrated development environment for Minecraft mod creation. Roblox Studio for Minecraft.

## Status

**Concept -- scaffolded, not yet implemented.**

The architecture is designed and the directory structure is ready for development. See [`ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the original concept document.

## What It Does

One application for the entire Minecraft mod development lifecycle: visual editors, code editor, embedded live preview, hot-reload testing, and export to any modloader. No JDK setup, no Gradle debugging, no 60-second test cycles.

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

## Core Components

### Explorer Panel
Registry-organized project tree: Blocks, Items, Entities, World Generation, Recipes, Loot Tables, Events, GUI, Networking, Data Packs, Resource Pack.

### 3D Viewport
Embedded Minecraft instance running your mod in real time. Editor overlays for chunk boundaries, entity AI state, block state inspection, redstone debugging, world gen preview. Hot-reload on every change.

### Code Editor
Full Java 21+ / Kotlin IDE with Minecraft-aware autocomplete, Mojang/Yarn/MCP mappings, live error checking, refactoring tools, and mixin assistant.

### Visual Editors
No-code tools for the systems that currently require hand-written JSON or boilerplate:

| Editor | What It Replaces |
|--------|-----------------|
| Recipe Editor | Hand-written JSON recipe files |
| Loot Table Editor | Nested JSON loot table files |
| World Gen Editor | Density function JSON, biome parameters |
| Entity AI Editor | Goal selector Java code |
| GUI Editor | AbstractContainerScreen coordinate math |
| Particle Editor | ParticleType boilerplate + trial-and-error |

Every visual editor generates clean, readable Java/Kotlin behind the scenes.

### Modloader Export
Build once, export for any target:

| Target | Output |
|--------|--------|
| Forge | Forge MDK project |
| NeoForge | NeoForge MDK project |
| Fabric | Fabric Loom project |
| Quilt | Quilt Loom project |
| Data Pack | Vanilla data pack |
| Resource Pack | Vanilla resource pack |
| Multiloader | Architectury project |

### Testing Environment
Automated test harness, performance profiler, multiplayer simulation, version matrix testing -- all inside the embedded instance.

## Directory Structure

```
Minecraft Studio/
|-- README.md               This file
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

---

*Conceived by Claude (Opus 4.5), February 2026*

*Every creative community deserves tools that match its ambition.*
