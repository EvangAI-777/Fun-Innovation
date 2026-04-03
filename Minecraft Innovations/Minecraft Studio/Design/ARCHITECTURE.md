# Minecraft Studio Architecture

Full technical design for the Minecraft modding IDE.

## System Overview

Minecraft Studio is a monolithic desktop application with five major subsystems that communicate through an internal event bus and shared project model.

```
+------------------+     +------------------+     +------------------+
|   Explorer       |     |   3D Viewport    |     |   Properties     |
|   Panel          |<--->|   (Embedded MC)  |<--->|   Panel          |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+--------+------------------------+------------------------+---------+
|                         Project Model                              |
|   (Registry, AST, Resources, Metadata -- backed by SQLite)        |
+--------+------------------------+------------------------+---------+
         |                        |                        |
         v                        v                        v
+------------------+     +------------------+     +------------------+
|   Code Editor    |     |  Visual Editors  |     |  Export Engine   |
+------------------+     +------------------+     +------------------+
```

## Component Details

### 1. IDE Shell (`src/app/`)

The outer application frame. Manages window layout, panel docking, menus, keybindings, preferences, and the plugin system.

**Technology:** JavaFX or Jetpack Compose Desktop. JavaFX is the conservative choice (mature, well-documented, Java-native). Compose Desktop is the modern choice (Kotlin-first, declarative, better DPI scaling). Decision deferred until prototyping.

**Responsibilities:**
- Window management and panel layout (dockable, resizable, hideable)
- Global keybinding system
- Preferences/settings persistence
- Theme support (light/dark, customizable)
- Update mechanism
- Plugin API for third-party extensions

### 2. Explorer Panel (`src/explorer/`)

A tree view of the mod's registry entries, organized by type. Mirrors Roblox Studio's Explorer but structured around Minecraft's registry system.

**Registry Nodes:**

| Node | Registry | Contents |
|------|----------|----------|
| Blocks | `BuiltInRegistries.BLOCK` | Custom block definitions |
| Items | `BuiltInRegistries.ITEM` | Custom item definitions |
| Entities | `BuiltInRegistries.ENTITY_TYPE` | Custom entity types |
| World Generation | Multiple | Biomes, features, structures, noise settings |
| Recipes | `BuiltInRegistries.RECIPE_TYPE` | All recipe types |
| Loot Tables | Resource location references | Block drops, mob drops, chest loot |
| Events | Studio event bus | Custom event handlers |
| GUI | Screen registry | Custom screens and HUDs |
| Networking | Channel registry | Custom packet definitions |
| Data Packs | File system | Functions, tags, advancements |
| Resource Pack | File system | Textures, models, sounds, lang |

**Behavior:**
- Double-click opens the appropriate visual editor or code file
- Right-click context menu: rename, duplicate, delete, show in code
- Drag-and-drop for reordering and cross-referencing
- Search/filter across all registry types
- Badges showing warnings (missing texture, invalid reference, deprecation)

### 3. 3D Viewport (`src/viewport/`)

An embedded Minecraft client instance running inside the IDE process.

**Classloader Isolation:**
```
Studio ClassLoader (parent)
  |-- Studio Classes (IDE, editors, UI)
  |-- Minecraft ClassLoader (child, isolated)
       |-- Minecraft Core Classes (vanilla)
       |-- Mod ClassLoader (child, disposable)
            |-- Compiled Mod Classes
```

On hot-reload:
1. Incremental compiler produces updated `.class` files
2. Mod ClassLoader is discarded
3. New Mod ClassLoader created with updated classes
4. Minecraft instance state preserved (world, entities, player position)
5. Registries re-initialized with new mod content
6. Elapsed time: < 2 seconds

**Editor Overlays:**
- Chunk boundary wireframes (toggle: F3+G equivalent)
- Light level display (sky light, block light)
- Entity AI visualization (pathfinding, goals, targets)
- Block state inspector (hover to see all properties)
- Redstone signal strength overlay with update order
- World gen debug (biome boundaries, feature placement, structure bounding boxes)
- Freeze/step mode (pause tick, advance one tick at a time)

### 4. Code Editor (`src/editor/`)

A full-featured Java/Kotlin editor embedded in the IDE.

**Language Support:**
- Java 21+ (records, sealed classes, pattern matching, virtual threads)
- Kotlin (coroutines, data classes, extension functions, DSL builders)
- JSON (for data packs, resource packs, configs)
- TOML (for mod configs)
- `.mcfunction` (Minecraft function files with syntax highlighting)

**Editor Features:**
- Syntax highlighting with Minecraft-aware semantic tokens
- Autocomplete against decompiled Minecraft source (configurable mapping set)
- Inline documentation on hover (Minecraft classes, mod API, Studio API)
- Live error checking (red squiggles on compile errors, yellow on deprecation)
- Refactoring: rename (updates registry references), extract method, move class, inline
- Go to definition (works across mod code and decompiled Minecraft source)
- Find usages (includes registry references, JSON references, annotation processors)
- Snippets: `new block`, `new item`, `new entity`, `new biome` generators
- Mixin assistant: browse Minecraft source visually, click a method, generate mixin class

**Compilation:**
- Eclipse ECJ for Java (incremental, sub-second for single-file changes)
- Kotlin compiler daemon for Kotlin (persistent daemon, incremental)
- Error output to Console panel with clickable line references

### 5. Visual Editors (`src/visual/`)

No-code tools that generate Java/Kotlin source behind the scenes. All visual editors maintain a bidirectional link with code -- changes in the visual editor update the code, and hand-edits to the generated code update the visual editor (where possible).

#### Recipe Editor (`src/visual/recipe/`)
- Grid layouts: 3x3 shaped, 2x2 shaped, shapeless, smithing, stonecutting, brewing, campfire, blasting, smoking
- Drag items from a searchable palette into grid slots
- Set output item, count, and NBT
- Custom recipe type schema builder for non-vanilla recipes
- Generates: `RecipeProvider` data generation class + runtime recipe registration

#### Loot Table Editor (`src/visual/loot/`)
- Tree view: table → pools → entries
- Pool config: rolls (min/max), bonus rolls per luck level
- Entry types: item (with count, enchantment, NBT functions), table reference, tag, empty
- Conditions as checkboxes/sliders: killed by player, looting bonus, biome filter, random chance
- Functions: set count, enchant randomly, set NBT, copy name, exploration map
- Generates: `LootTableProvider` data generation class

#### World Generation Editor (`src/visual/worldgen/`)
- **Biome parameter visualizer:** 2D/3D scatter plot of temperature, humidity, continentalness, erosion, depth, weirdness. Custom biomes shown as colored points. Drag to reposition. Real-time conflict detection.
- **Density function graph:** Node-based editor (like Blender shader nodes). Nodes: add, multiply, noise, spline, clamp, cache, blend, abs, square, half_negative. Connect nodes. Live cross-section preview.
- **Feature placement previewer:** Toggle features on/off, see placement patterns across chunks, adjust count/spread/chance with sliders.
- **Structure template editor:** 3D editor for structure pieces, jigsaw connection points, processor lists, pool weights.
- Generates: biome JSON, density function JSON, feature placement JSON, structure template NBT

#### Entity AI Editor (`src/visual/entity/`)
- Flowchart of goal selector priorities
- Each goal as a configurable node: wander, flee, attack, follow, eat, breed, swim, panic, look at player
- Target selector configuration: nearest attackable, hurt by, owner
- Drag to reorder priority
- Attribute editor: health, speed, attack damage, follow range, knockback resistance
- Spawn rule configuration: biome, light level, block, height range
- Generates: entity class with `registerGoals()`, attributes, spawn rules

#### GUI Editor (`src/visual/gui/`)
- WYSIWYG screen layout canvas
- Draggable widgets: slots, buttons, labels, progress bars, text fields, images
- Slot binding to inventory (player, container, custom)
- Button wiring to packet sends
- Layout guides and snapping
- Generates: `AbstractContainerScreen` + `AbstractContainerMenu` + slot definitions + packet handlers

#### Particle Editor (`src/visual/particle/`)
- Live 3D preview in viewport
- Sliders: count, speed, spread, lifetime, gravity, collision
- Color picker with gradient support
- Shape presets: point, sphere, ring, cone, line
- Generates: `ParticleType` registration + client particle factory + server spawn packet

### 6. Export Engine (`src/export/`)

Transforms the Studio project model into modloader-specific projects.

**Abstraction Layer (`src/abstraction/`):**

Studio code is authored against the abstraction API:

```java
// Studio abstraction (what you write)
Studio.registerBlock("mymod:custom_block", MyBlock::new, properties);

// Forge export (what gets generated)
public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, "mymod");
public static final RegistryObject<Block> CUSTOM_BLOCK = BLOCKS.register("custom_block", () -> new MyBlock(properties));

// Fabric export (what gets generated)
public static final Block CUSTOM_BLOCK = Registry.register(BuiltInRegistries.BLOCK, ResourceLocation.fromNamespaceAndPath("mymod", "custom_block"), new MyBlock(properties));
```

**Export Targets:**

Each exporter generates a complete, buildable project:

| Target | Build System | Key Patterns |
|--------|-------------|--------------|
| Forge (`src/export/forge/`) | Forge Gradle | `@Mod`, `DeferredRegister`, Forge event bus |
| NeoForge (`src/export/neoforge/`) | NeoForge Gradle | `@Mod`, NeoForge registry, NeoForge events |
| Fabric (`src/export/fabric/`) | Fabric Loom | `ModInitializer`, `Registry.register`, Fabric callbacks |
| Quilt (`src/export/quilt/`) | Quilt Loom | Quilt `ModInitializer`, Quilt registry, Quilt API |
| Data Pack (`src/export/datapack/`) | None | `.mcfunction` files, JSON, `pack.mcmeta` |
| Resource Pack (`src/export/resourcepack/`) | None | Textures, models, sounds, blockstate overrides |

**Multiloader (Architectury):**
- Common module with shared code (Studio abstraction layer compiled to Architectury API)
- Per-loader modules generated from common module
- Architectury Gradle buildscript

### 7. Testing Environment (`src/testing/`)

**Automated Tests:**
```java
@StudioTest
void customBlockDropsItem() {
    world.setBlock(pos, ModBlocks.CUSTOM_BLOCK);
    player.setMainHand(Items.DIAMOND_PICKAXE);
    player.breakBlock(pos);
    assertThat(world.getBlock(pos)).isAir();
    assertThat(player.inventory()).contains(ModItems.CUSTOM_ITEM);
}
```

Tests execute inside the embedded Minecraft instance. No separate server. No `@GameTest` boilerplate.

**Performance Profiler:**
- Server tick time breakdown (per-system: entities, blocks, world gen, networking)
- Entity count and type distribution
- Chunk loading time and queue depth
- Memory allocation rate and GC pauses
- Custom mod hook timing

**Multiplayer Simulation:**
- Spawn N simulated player connections
- Configurable movement patterns (exploring, stationary, building)
- Network latency injection
- Concurrent chunk loading stress test

**Version Matrix:**
- Project compatibility map per Minecraft version
- Automatic API migration hints (renamed methods, moved registries, changed signatures)
- Export and test against multiple versions from one project

## Data Model

### Project File (SQLite)

```
studio_project.db
  |-- registry_entries    (type, id, properties, source_file, visual_editor_state)
  |-- source_files        (path, content_hash, last_modified, compilation_state)
  |-- resources           (path, type, content_hash, preview_thumbnail)
  |-- undo_history        (timestamp, action, before_state, after_state)
  |-- metadata            (project_name, mod_id, version, minecraft_version, authors)
  |-- export_configs      (target, settings, last_export_time)
```

## Implementation Status

This architecture document describes the full vision. The project is being built in layers, with each layer fully functional before the next begins.

### Layer 1: Data Model + Export Engine (v0.2.0 -- complete)

The Python prototype implements the **Project Model** and **Export Engine** subsystems from the diagram above. This is the foundation that proves the cross-loader abstraction works before investing in the full IDE shell.

| Architecture Component | Implementation | Status |
|----------------------|----------------|--------|
| Project Model -- Block registry | `mcstudio.model.block` -- 14 materials, full property set | Done |
| Project Model -- Item registry | `mcstudio.model.item` -- food, tool, creative tab support | Done |
| Project Model -- Recipe registry | `mcstudio.model.recipe` -- all 7 vanilla types | Done |
| Project Model -- Loot table registry | `mcstudio.model.loot` -- pools, conditions, functions | Done |
| Project Model -- Entity registry | `mcstudio.model.entity` -- 8 base classes, 15 AI goals, spawn rules | Done (model only) |
| Project Model -- World gen registry | `mcstudio.model.worldgen` -- biomes, features, placement | Done (model only) |
| Project Model -- Serialization | JSON save/load with full round-trip | Done |
| Export Engine -- Fabric | Complete Fabric Loom project generation | Done |
| Export Engine -- Forge | Complete Forge Gradle project generation | Done |
| Export Engine -- NeoForge | Complete NeoForge Gradle project generation | Done |
| Export Engine -- Data Pack | Vanilla data pack generation | Done |
| Export Engine -- Quilt | Quilt Loom project generation | Not started |
| Export Engine -- Resource Pack | Standalone resource pack generation | Not started |
| Export Engine -- Multiloader | Architectury project generation | Not started |
| Code Generation | `mcstudio.codegen.java` -- JavaWriter with formatting | Done |
| Texture Generation | `mcstudio.texgen` -- placeholder PNGs from stdlib | Done |
| CLI | 6 commands: new, add-block, add-item, export, info, loaders | Done |
| Explorer Panel | -- | Not started (Layer 4) |
| 3D Viewport | -- | Not started (Layer 7) |
| Code Editor | -- | Not started (Layer 5) |
| Visual Editors | -- | Not started (Layers 3+6) |
| Testing Environment | -- | Not started (Layer 8) |
| IDE Shell | -- | Not started (Layer 4) |

**What "model only" means:** Entity and world gen types have complete data models with serialization, validation, and test coverage, but the exporters don't yet generate Java entity classes or biome JSON for specific loaders. The model is ready; the code generation for these types is the next step.

**What Layer 1 proves:** A mod can be defined once as a structured data model and exported to three different modloaders (Fabric, Forge, NeoForge) plus vanilla data packs, producing correct, buildable Gradle projects with idiomatic registration patterns. The abstraction works.

118 passing tests. Zero external dependencies.

---

*Theme overview: [`../MCME.md`](../MCME.md)*
