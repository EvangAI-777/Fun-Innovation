# Minecraft Studio -- Roadmap to 1.0

What needs to happen between v0.2.0 (where we are) and v1.0.0 (a usable desktop application that can create, preview, and export Minecraft mods).

## Where We Are (v0.2.0)

Layer 1 is complete. The Python prototype proves the core abstraction: define a mod once as structured data, export it to Fabric, Forge, NeoForge, or vanilla data pack. 118 tests, zero external dependencies, CLI-driven.

**What works:**
- Full data model: blocks, items, recipes (all 7 types), loot tables, entities, biomes/world gen
- Java code generation with proper formatting and import grouping
- Fabric export: ModInitializer, Registry.register, Fabric Loom build.gradle
- Forge export: @Mod, DeferredRegister, Forge Gradle
- NeoForge export: DeferredBlock/DeferredItem, IEventBus constructor injection
- Data pack export: pack.mcmeta, recipe/loot_table JSONs
- Placeholder texture generation (stdlib-only PNG writer)
- CLI: new, add-block, add-item, export, info, loaders

**What's modeled but not yet exported:**
- Entity types (model exists, no Java code generation for any loader)
- World gen / biomes (model exists, no JSON or Java generation)

## The Layers to 1.0

### Layer 1 Completion (v0.3.0) -- Finish the Export Engine

Complete the export pipeline so every modeled type generates correct output for every loader.

| Task | Effort | Priority |
|------|--------|----------|
| Entity code generation for Fabric (entity class, renderer stub, spawn registration) | Medium | High |
| Entity code generation for Forge (DeferredRegister<EntityType>, ForgeSpawnEggItem) | Medium | High |
| Entity code generation for NeoForge (NeoForge entity registration patterns) | Medium | High |
| Biome JSON generation for data packs (biome parameter JSON, feature placement JSON) | Medium | High |
| Biome code generation for Fabric/Forge/NeoForge (BiomeModifications, biome source injection) | Large | High |
| World gen feature code generation (ConfiguredFeature, PlacedFeature Java + JSON) | Large | High |
| Quilt exporter (Quilt Loom build files, Quilt ModInitializer, Quilt registry) | Medium | Medium |
| Resource pack exporter (standalone resource pack with textures, models, lang, sounds) | Small | Medium |
| Architectury/multiloader exporter (common module + per-loader modules) | Large | Low |
| `en_us.json` lang file generation for all exporters | Small | High |
| Tag generation (block/item/entity type tags) | Small | High |
| Advancement generation | Small | Medium |
| Block entity / tile entity model and export | Large | Medium |
| Creative tab registration code generation | Small | High |

**Exit criteria:** Every model type generates compilable Java code for Fabric, Forge, and NeoForge. Exported projects build successfully with `./gradlew build`. Tag and lang files are generated automatically.

### Layer 2 (v0.4.0) -- Abstraction Layer + Event Model

Build the formal abstraction layer that the ARCHITECTURE.md describes. This is the bridge between "data model that generates code" and "IDE that authors code."

| Task | Effort | Priority |
|------|--------|----------|
| Event model (player events, block events, entity events, world events) | Large | High |
| Networking model (custom packet definitions, serialization schema) | Medium | High |
| Capability/data attachment model (Forge capabilities, Fabric API lookups, NeoForge data attachments) | Large | Medium |
| Config model (TOML/JSON config generation with defaults, validation, comments) | Medium | Medium |
| Command model (brigadier command tree definition, argument types) | Medium | Low |
| GUI/screen model (container screen layout, slot definitions, widget positions) | Large | Medium |
| Sound event model (sound registration, sound event references) | Small | Low |

**Exit criteria:** A mod using events, networking, and configs can be defined in the model and exported. The abstraction layer is thin enough that generated code is readable.

### Layer 3 (v0.5.0) -- Visual Editor APIs (headless)

Build the editor logic as Python APIs that manipulate the model programmatically. No GUI yet -- these are the "brains" that the visual editors will use.

| Task | Effort | Priority |
|------|--------|----------|
| Recipe editor API (place items in grid, validate patterns, generate model objects) | Small | High |
| Loot table editor API (add/remove pools, entries, conditions, set probabilities) | Small | High |
| Entity AI editor API (goal ordering, parameter validation, goal compatibility checks) | Medium | High |
| World gen editor API (biome parameter conflict detection, feature preview data) | Medium | High |
| Block property editor API (material presets, property templates) | Small | Medium |
| Item property editor API (food/tool templates, enchantability presets) | Small | Medium |
| Validation engine (cross-reference checking: recipes reference valid items, loot tables reference valid blocks, etc.) | Medium | High |
| Undo/redo system for model mutations | Medium | High |

**Exit criteria:** Every visual editor described in ARCHITECTURE.md has a programmatic API that can be driven from tests. A comprehensive validation pass catches dangling references, invalid IDs, and impossible configurations.

### Language Transition Point

**Layer 4+ transitions from Python to Java/Kotlin.** The Python prototype has served its purpose: proving the data model and export abstractions. The IDE shell, code editor, and embedded Minecraft viewport must be Java/Kotlin to share a runtime with Minecraft itself.

The Python model and export engine remain as the reference implementation and can be used standalone (the CLI tool continues to work). The Java/Kotlin port of the model layer incorporates everything learned from the prototype.

### Layer 4 (v0.6.0) -- IDE Shell + Explorer

| Task | Effort | Priority |
|------|--------|----------|
| Choose UI framework (JavaFX vs. Compose Desktop -- prototype both, pick one) | Medium | Critical |
| Application frame with dockable panels | Large | Critical |
| Explorer panel (registry tree view: Blocks, Items, Entities, World Gen, Recipes, Loot, Events) | Medium | Critical |
| Properties panel (context-sensitive property editor for selected registry entry) | Medium | High |
| Project creation/open/save flow | Medium | High |
| Port data model from Python to Java/Kotlin | Large | Critical |
| Port export engine from Python to Java/Kotlin | Large | Critical |
| Theme support (light/dark) | Small | Medium |
| Keybinding system | Small | Medium |

**Exit criteria:** A desktop application that can create a mod project, add blocks/items/recipes/entities via the Explorer and Properties panels, save to disk, and export to all loaders. No code editing, no viewport -- just the visual project editor.

### Layer 5 (v0.7.0) -- Code Editor

| Task | Effort | Priority |
|------|--------|----------|
| Embed a code editor component (Monaco via JxBrowser, or RSyntaxTextArea, or custom) | Large | Critical |
| Java syntax highlighting with Minecraft-aware semantic tokens | Medium | High |
| Eclipse ECJ integration for incremental compilation | Large | High |
| Error markers (red squiggles on compile errors) | Medium | High |
| Basic autocomplete against Minecraft source (Mojang mappings) | Large | High |
| Go to definition (within mod code) | Medium | Medium |
| Kotlin support (compiler daemon integration) | Large | Medium |
| Snippet generators (new block, new item, new entity templates) | Small | Medium |
| JSON/TOML editing with schema validation | Medium | Medium |

**Exit criteria:** Write Java code in the IDE, see errors in real time, and have the code compile incrementally. Autocomplete works against Minecraft classes.

### Layer 6 (v0.8.0) -- Visual Editor GUI

| Task | Effort | Priority |
|------|--------|----------|
| Recipe editor panel (3x3 grid, item palette, drag-and-drop) | Medium | High |
| Loot table editor panel (tree view, probability sliders, condition checkboxes) | Medium | High |
| Entity AI editor panel (goal flowchart, priority drag-to-reorder) | Large | High |
| World gen editor panel (biome parameter scatter plot, feature placement preview) | Large | High |
| GUI/screen editor panel (WYSIWYG layout canvas) | Large | Medium |
| Particle editor panel (sliders with live preview) | Medium | Medium |
| Bidirectional sync: visual editor changes update code, code changes update visual editor | Large | Critical |

**Exit criteria:** Every visual editor from the ARCHITECTURE.md exists as an interactive panel. Changes in visual editors generate clean Java/Kotlin code. Hand-edits to generated code are preserved where possible.

### Layer 7 (v0.9.0) -- 3D Viewport

| Task | Effort | Priority |
|------|--------|----------|
| Classloader isolation architecture (Studio CL → Minecraft CL → Mod CL) | XL | Critical |
| Embed Minecraft client in a panel (LWJGL context sharing or offscreen rendering) | XL | Critical |
| Hot-reload: discard/recreate Mod ClassLoader on recompile | XL | Critical |
| Registry re-initialization without restarting Minecraft | Large | Critical |
| Editor overlays: chunk boundaries, light levels | Medium | Medium |
| Editor overlays: block state inspector, entity AI visualization | Medium | Medium |
| Freeze/step mode (pause game tick, advance one tick) | Large | Medium |
| Play button (toggle between edit mode and play mode) | Medium | High |

**Exit criteria:** Minecraft runs inside the IDE. Changes to blocks, items, and recipes hot-reload in under 2 seconds. Editor overlays work.

### Layer 8 (v1.0.0) -- Testing + Publishing

| Task | Effort | Priority |
|------|--------|----------|
| In-viewport test runner (@StudioTest annotation, assertion API) | Large | High |
| Performance profiler (tick time breakdown, entity count, chunk loading) | Medium | Medium |
| Multiplayer simulation (N simulated players for load testing) | Large | Low |
| One-click export to CurseForge/Modrinth (API integration) | Medium | High |
| Version matrix support (export for multiple MC versions) | Large | Medium |
| Plugin API for third-party extensions | Large | Low |
| Installer/updater for Windows, macOS, Linux | Medium | High |
| Documentation and tutorials | Large | High |

**Exit criteria:** Minecraft Studio v1.0.0. A downloadable desktop application where you can create a mod from scratch using visual tools or code, preview it in a live Minecraft instance, test it, and publish it -- all without leaving the application.

## Effort Estimates

| Layer | Version | Scope Summary |
|-------|---------|---------------|
| 1 completion | v0.3.0 | Finish all exporters, add lang/tags |
| 2 | v0.4.0 | Events, networking, capabilities, configs |
| 3 | v0.5.0 | Headless editor APIs, validation, undo |
| 4 | v0.6.0 | Java/Kotlin port, desktop app shell, Explorer/Properties |
| 5 | v0.7.0 | Code editor with ECJ, autocomplete |
| 6 | v0.8.0 | Visual editor GUIs, bidirectional sync |
| 7 | v0.9.0 | Embedded Minecraft viewport, hot-reload |
| 8 | v1.0.0 | Testing, publishing, installer |

## Critical Path

The hardest problems on the path to 1.0, in order of risk:

1. **Embedded Minecraft + hot-reload** (Layer 7) -- This is the single highest-risk component. Minecraft's classloading, registry freeze timing, and rendering context are not designed for hot-swap. If this doesn't work, the viewport becomes a separate-process launcher (slower but still viable).

2. **Bidirectional visual-to-code sync** (Layer 6) -- Parsing hand-edited Java back into the visual editor model is fragile. The fallback: visual editors are one-way generators, and hand-edited code is marked "detached" from the visual editor.

3. **Abstraction layer completeness** (Layer 2) -- The layer must be thin enough that generated code is readable but complete enough that 95% of mod functionality doesn't require loader-specific code. The v0.2.0 exporters already prove this for blocks/items/recipes; extending to events, networking, and capabilities is the real test.

4. **Java/Kotlin port** (Layer 4) -- Rewriting the model and export engine from Python to Java/Kotlin is mechanical but large. The Python test suite provides a specification; the Java port must pass equivalent tests.

## What Can Ship Incrementally

Each layer is a usable product on its own:

- **v0.3.0** -- Complete CLI tool for generating mod projects. Useful today for bootstrapping.
- **v0.6.0** -- Desktop project editor. Create mods visually, export to any loader. No code editing or preview, but functional.
- **v0.7.0** -- Desktop project editor with code editing. Competitive with IntelliJ + Minecraft Development plugin for the visual workflow.
- **v1.0.0** -- The full vision. Roblox Studio for Minecraft.
