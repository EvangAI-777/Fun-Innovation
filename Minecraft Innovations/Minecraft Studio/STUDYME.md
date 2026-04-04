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

See [`ARCHITECTURE.md`](./Design/ARCHITECTURE.md) for the full technical design and [`MCME.md`](../MCME.md) for the theme overview.

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

## Roadmap

Minecraft Studio is built in layers. Each layer is fully functional and testable on its own before the next begins.

| Layer | Name | What It Delivers | Status |
|-------|------|-----------------|--------|
| **1** | **Data Model + Export Engine** | Complete mod content model, Java code generation, multi-loader project export, entity/worldgen codegen, lang files, tags, creative tabs, CLI | **v0.3.0 -- complete** |
| **2** | **Abstraction Layer** | Event model + codegen, config model + codegen, Quilt exporter, resource pack exporter, advancement model + export | **v0.4.0 -- in progress** |
| **3** | **Visual Editors (headless)** | Recipe editor, loot table editor, entity AI editor, world gen editor -- as programmatic APIs that generate model objects (no GUI yet) | Planned |
| **4** | **IDE Shell + Explorer** | JavaFX or Compose Desktop application frame, Explorer panel, Properties panel, project management | Planned |
| **5** | **Code Editor** | Embedded Java/Kotlin editor with Minecraft-aware autocomplete, ECJ incremental compilation | Planned |
| **6** | **Visual Editor GUI** | Wire the Layer 3 APIs into interactive JavaFX/Compose panels with drag-and-drop | Planned |
| **7** | **3D Viewport** | Embedded Minecraft client with classloader isolation and hot-reload | Planned |
| **8** | **Testing + Publishing** | In-viewport test harness, performance profiler, one-click CurseForge/Modrinth publish | Planned |

## Status

### Layer 1: Data Model + Export Engine -- v0.3.0 (complete)

Zero external dependencies. Python 3.10+. `pip install -e .` then `mcstudio` to use.

**Data model** (`mcstudio.model`):

| Module | What it does |
|--------|-------------|
| `project` | Complete mod project container with JSON save/load, registry management, Java class/package name generation, creative tab label, duplicate ID enforcement across all registries |
| `block` | Block definitions -- 14 material types, hardness, resistance, luminance, tool requirements, drops, collision, transparency, tags. Resource location ID validation |
| `item` | Item definitions -- stack sizes, creative tabs, food properties (nutrition, saturation, meat, always-edible), tool properties (tier, damage, speed, durability), tags. Resource location ID validation |
| `recipe` | All 7 vanilla recipe types -- shaped, shapeless, smelting, blasting, smoking, stonecutting, smithing transform |
| `loot` | Loot tables with pools, weighted entries, all 6 condition types (silk touch, without silk touch, match tool, explosion, player kill, random chance with configurable probability), functions (set count, enchant, looting) |
| `entity` | Entity type definitions -- 8 base classes (LivingEntity through TamableAnimal), 15 AI goal types, entity attributes, spawn rules with biome targeting and mob categories, hitbox dimensions |
| `worldgen` | World generation -- biomes with multi-noise parameters (temperature, humidity, continentalness, erosion, depth, weirdness), sky/fog/water/grass colors, 11 feature types, placement configs with height ranges |

### Layer 2: Abstraction Layer -- v0.4.0

Building on Layer 1's foundation with cross-cutting mod features: events, configs, advancements, and two new exporters.

**New model types** (`mcstudio.model`):

| Module | What it does |
|--------|-------------|
| `advancement` | Custom advancements -- display (icon, title, description, frame), criteria with trigger types (inventory_changed, placed_block, killed_entity, etc.), requirements (AND/OR logic), parent chains |
| `event` | Event handler model -- 14 event types (player join/leave/respawn, block break/place, entity spawn/death, server lifecycle, world tick/load), priority levels, custom body lines |
| `config` | Typed mod configuration -- ConfigEntry (bool/int/float/string with defaults, comments, min/max ranges), ConfigSection, ModConfig. Per-loader codegen |

**New code generation** (`mcstudio.codegen`):

| Module | What it does |
|--------|-------------|
| `events` | Per-loader event handler Java class generation. Fabric/Quilt: callback-based registration (ServerPlayConnectionEvents, PlayerBlockBreakEvents, etc.). Forge: @SubscribeEvent on MinecraftForge.EVENT_BUS. NeoForge: @SubscribeEvent on NeoForge.EVENT_BUS |
| `config` | Per-loader config class generation. Forge/NeoForge: ForgeConfigSpec.Builder with defineInRange, comments, sections. Fabric/Quilt: simple JSON config loader class + default config JSON file |

**New exporters** (`mcstudio.export`):

| Module | What it does |
|--------|-------------|
| `quilt` | Full Quilt Loom project export -- quilt.mod.json (schema_version 1, quilt_loader section), QSL dependencies, ModContainer-based initializer. Registry code reuses Fabric patterns via QSL compatibility |
| `resourcepack` | Standalone resource pack export -- pack.mcmeta, blockstate/model JSONs, lang file, placeholder textures, empty sounds.json |

**Export engine additions** (all 6 exporters):
- Advancement JSON export under `data/<mod_id>/advancement/`
- Event handler class generation with mod class registration calls
- Config class generation with loader-specific patterns
- Advancement lang entries auto-generated

219 passing tests across 3 test files. 6 export targets: Fabric, Forge, NeoForge, Quilt, Data Pack, Resource Pack.

### What the prototype proves

The data model and export engine are the foundation that validates the core abstraction: define a mod once, export it for any loader. Every registry type (blocks, items, recipes, loot tables, entities, biomes, advancements, events, configs) serializes to JSON, round-trips cleanly, and generates correct loader-specific Java code.

Every piece of this puzzle has been built in isolation by the Minecraft modding community -- Blockbench for visual tooling, Architectury for cross-loader abstraction, IntelliJ's Minecraft Development plugin for IDE integration. Nobody has assembled them into one coherent application. The prototype proves the abstraction works. Visual editors, the embedded viewport, and the full IDE shell build on top.

### Post-1.0: Standalone x64 Windows Binary

The binary release is the real product. Minecraft Studio will be packaged as a standalone application using jlink/jpackage with an embedded JRE — a downloadable installer that users run without installing Java, Gradle, or any development tools. All the zero-dependency constraints in the current prototype phase are practical compromises for keeping the pip-installable package lightweight and CI-friendly. They do not apply to the binary release.

The standalone executable can ship with full dependencies: JavaFX for the IDE shell, rich GUI libraries, embedded Minecraft client, full compilation toolchain — everything the design docs describe. The bundled JRE handles it all. Users don't install Java, don't configure PATH, don't care about JDK versions.

The Python CLI prototype can also be compiled via PyInstaller/Nuitka as a standalone `mcstudio.exe` for users who want just the export engine without the IDE. Both distribution channels serve different users.

---

*Conceived by Claude (Opus 4.5), February 2026. Layer 1 implemented by Claude (Opus 4.6), February-April 2026.*

*Because every coordinate system eventually leads to Minecraft.*
