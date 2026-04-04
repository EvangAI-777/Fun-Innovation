# Minecraft Studio -- Roadmap to 1.0

What needs to happen between v0.4.0 (where we are) and v1.0.0 (a usable desktop application that can create, preview, and export Minecraft mods).

## Where We Are (v0.4.0)

Layers 1-2 are complete. The Python prototype proves the core abstraction: define a mod once as structured data, export it to Fabric, Forge, NeoForge, Quilt, vanilla data pack, or resource pack. 219 tests, zero external dependencies, CLI-driven. All modeled types generate correct output for all 6 loaders.

**What works:**
- Full data model: blocks (with tags), items (with tags), recipes (all 7 types), loot tables, entities (8 base classes, 15 AI goals), biomes/world gen (11 feature types), advancements, event handlers (14 event types), mod configs (typed entries with ranges)
- Java code generation: JavaWriter, entity class generator, worldgen codegen, per-loader event handler codegen, per-loader config class codegen
- Fabric export: ModInitializer, Registry.register, entity registry, BiomeModifications API, FabricItemGroup creative tab, event callbacks, JSON config loader, advancements, lang file, tag JSONs
- Forge export: @Mod, DeferredRegister, @SubscribeEvent events, ForgeConfigSpec config, advancements, lang file, tag JSONs
- NeoForge export: DeferredBlock/DeferredItem/DeferredHolder, NeoForge.EVENT_BUS events, ForgeConfigSpec config, advancements, lang file, tag JSONs
- Quilt export: quilt.mod.json, QSL dependencies, ModContainer initializer, event callbacks, JSON config, advancements
- Data pack export: recipes, loot tables, tags, worldgen JSONs, advancements
- Resource pack export: pack.mcmeta, blockstate/model JSONs, lang file, textures, sounds.json
- Placeholder texture generation (stdlib-only PNG writer)
- CLI: new, add-block, add-item, export, info, loaders

## The Layers to 1.0

### Layer 1 (v0.3.0) -- Export Engine ✓ DONE

All core export tasks complete. Every modeled type generates correct output for every loader.

### Layer 2 (v0.4.0) -- Abstraction Layer ✓ DONE

| Task | Status |
|------|--------|
| Event model (14 event types, per-loader codegen for Fabric/Forge/NeoForge/Quilt) | **Done** |
| Config model (typed entries with ranges, ForgeConfigSpec + JSON config codegen) | **Done** |
| Advancement model (display, criteria, triggers, requirements, JSON export) | **Done** |
| Quilt exporter (quilt.mod.json, QSL, ModContainer initializer) | **Done** |
| Resource pack exporter (pack.mcmeta, models, textures, lang, sounds) | **Done** |
| Networking model (custom packet definitions, serialization schema) | Remaining |
| Capability/data attachment model | Remaining |
| Command model (brigadier command tree) | Remaining |
| GUI/screen model (container screen layout) | Remaining |
| Sound event model | Remaining |
| Architectury/multiloader exporter | Remaining |
| Block entity / tile entity model | Remaining |

**Exit criteria (met for events/config/advancements):** A mod using events and configs can be defined in the model and exported. The abstraction layer is thin enough that generated code is readable.

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
| 1 | v0.3.0 | **Done** -- entity/worldgen codegen, lang, tags, creative tabs |
| 2 | v0.4.0 | **Done** -- events, configs, advancements, Quilt, resource pack |
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

3. **Abstraction layer completeness** (Layer 2) -- The layer must be thin enough that generated code is readable but complete enough that 95% of mod functionality doesn't require loader-specific code. v0.4.0 proves this for events and configs; networking and capabilities are the remaining test.

4. **Java/Kotlin port** (Layer 4) -- Rewriting the model and export engine from Python to Java/Kotlin is mechanical but large. The Python test suite provides a specification; the Java port must pass equivalent tests.

## What Can Ship Incrementally

Each layer is a usable product on its own:

- **v0.3.0** -- **Shipped.** Complete CLI tool for generating mod projects with entity/worldgen codegen, lang files, tags, and creative tabs.
- **v0.4.0** -- **Shipped.** Abstraction layer with events, configs, advancements, Quilt and resource pack exporters. 6 export targets, 219 tests.
- **v0.6.0** -- Desktop project editor. Create mods visually, export to any loader. No code editing or preview, but functional.
- **v0.7.0** -- Desktop project editor with code editing. Competitive with IntelliJ + Minecraft Development plugin for the visual workflow.
- **v1.0.0** -- The full vision. Roblox Studio for Minecraft.

## Post-1.0: Standalone x64 Windows Binary

The binary release is the real product. Minecraft Studio will be packaged as a standalone application using jlink/jpackage with an embedded JRE — a downloadable installer that users run without installing Java, Gradle, or any development tools. All the zero-dependency constraints in the current prototype phase are practical compromises for keeping the pip-installable package lightweight and CI-friendly. They do not apply to the binary release.

The standalone executable can ship with full dependencies: JavaFX for the IDE shell, rich GUI libraries, embedded Minecraft client, full compilation toolchain — everything described in Layers 4-8. The bundled JRE handles it all. Users download an installer, run it, and start creating mods.

The Python CLI prototype can also be compiled via PyInstaller/Nuitka as a standalone `mcstudio.exe` for users who want just the export engine without the IDE. Both distribution channels serve different users, and both will be maintained.
