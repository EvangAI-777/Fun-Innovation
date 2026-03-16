# Minecraft Innovations

Concept designs for tools that don't exist yet in the Minecraft ecosystem. Not mods -- infrastructure. The kind of tooling that changes what's possible for everyone who builds on top of Minecraft.

Two concepts so far. One turns real-world data into playable worlds. The other turns Minecraft modding into something that doesn't require a computer science degree.

## What Belongs Here

Anything that improves the Minecraft creation ecosystem at the infrastructure level:

- **Data pipelines** -- tools that move real-world data, 3D models, or other external formats into Minecraft worlds (and back out)
- **Development environments** -- IDEs, editors, and toolchains that make mod creation, datapack authoring, or map building more accessible
- **Format tools** -- converters, exporters, importers for Minecraft's file formats (.nbt, .mca, .mcfunction, schematics, resource packs)
- **Modding utilities** -- libraries, frameworks, and helpers that reduce boilerplate and bridge modloader differences
- **World generation** -- tools and systems for procedural terrain, structure generation, biome design, and seed analysis
- **Server tooling** -- administration, monitoring, configuration, and deployment tools for Minecraft servers
- **Creative tools** -- texture editors, model builders, sound design tools, and anything else that helps content creators produce Minecraft assets

The common thread: these are tools *for* Minecraft, not mods *in* Minecraft. The audience is builders and creators, not players.

## What Doesn't Belong Here

Gameplay mods, texture packs, or server plugins. Those are content. This folder is for the tools that make content possible. If a player would install it to change their game experience, it belongs in a different kind of project. If a creator would install it to make things faster, better, or possible at all -- it belongs here.

## Concepts

| Concept | Directory | Focus | Language | Status |
|---------|-----------|-------|----------|--------|
| GeoVox | `GeoVox/` | Real-world 3D data → Minecraft worlds | Python | v0.1.1 |
| Minecraft Studio | `Minecraft Studio/` | Roblox Studio-style IDE for Minecraft modding | Python (Layer 1) / Java + Kotlin (future) | v0.2.0 -- Layer 1 complete |

Each concept has its own subdirectory with architecture documents. See [`GeoVox/VOXELME.md`](./GeoVox/VOXELME.md) and [`Minecraft Studio/STUDYME.md`](./Minecraft%20Studio/STUDYME.md) for project overviews.

## Concept Details

### GeoVox -- Real-World Data Pipeline

What if Minecraft wasn't just a game you built in -- but a renderer for reality?

Take real-world 3D data -- terrain heightmaps, point clouds, photogrammetry meshes, LiDAR scans, architectural models -- and voxelize it into Minecraft block palettes. Not as a novelty. As a *pipeline*. A modular system where the input is any georeferenced or model-space 3D dataset and the output is a Minecraft world you can walk through, modify, and share.

This has been done before in one-off scripts and abandoned GitHub repos. What hasn't been done is making it modular, palette-aware, and bidirectional.

#### Architecture

Three layers:

**Layer 1: Ingest.** Accept data from multiple formats:

| Format | Source | Notes |
|--------|--------|-------|
| GeoTIFF heightmaps | USGS, Copernicus, national survey data | Elevation grids, 1-30m resolution |
| LAS/LAZ point clouds | LiDAR surveys, drone scans | Classified points (ground, vegetation, buildings) |
| OBJ/STL meshes | Photogrammetry, CAD exports | Arbitrary geometry |
| GeoJSON polygons | OpenStreetMap, municipal GIS | Building footprints, road networks |
| Voxel grids (NIfTI/binvox) | Medical imaging, scientific simulation | Pre-voxelized data |

Each ingest module normalizes its input into a common internal representation: a sparse 3D integer grid where each cell holds a block ID. No geometry. No floating point. Just blocks.

**Layer 2: Palette Mapping.** Raw elevation data doesn't know what "grass" looks like. A LiDAR point classified as "vegetation" doesn't know it should be oak leaves vs. jungle leaves vs. azalea. The palette mapper bridges that gap.

A palette is a JSON config that maps semantic categories to Minecraft block selections:

```
ground_low    -> grass_block, dirt, coarse_dirt (weighted random)
ground_high   -> stone, andesite, diorite
water         -> water (with depth-based light absorption)
vegetation    -> oak_leaves, birch_leaves (biome-dependent)
building_wall -> bricks, stone_bricks, smooth_stone
building_roof -> dark_oak_planks, spruce_planks
road          -> gray_concrete, stone_slab
```

Palettes are swappable. The same USGS heightmap of the Grand Canyon can render in vanilla survival blocks, in deepslate-and-copper steampunk, or in wool-and-concrete pixel art. The geometry stays the same. The aesthetics are a parameter.

Multiple palette layers can stack. Elevation drives the base material. Slope angle adds variation (cliff faces get exposed stone). Moisture data from satellite imagery shifts vegetation density. Classification labels from LiDAR override everything where they exist. The system composes.

**Layer 3: Export.** The final grid writes out as:

- **Structure files** (.nbt) -- paste into existing worlds with structure blocks *(implemented)*
- **Datapack functions** (.mcfunction) -- setblock commands for server deployment *(implemented)*
- **Minecraft world files** (.mca region format) -- drop into a saves folder and play *(planned)*
- **Litematica schematics** (.litematic) -- for mod-assisted building in survival *(planned)*

Each exporter handles Minecraft-specific concerns. The implemented exporters (.nbt, .mcfunction) work now; .mca and .litematic are next on the roadmap.

#### What You Could Build With This

**Your neighborhood.** Download a 1m LiDAR scan from your city's open data portal. Run it through GeoVox with a suburban palette. Walk through a block-scale replica of your street in Minecraft. The trees are in the right places. The rooflines match. The road curves correctly.

**A national park.** Pull USGS 10m DEM data for Yosemite. Layer in vegetation classification from Sentinel-2 satellite imagery. Export at 1:1 scale. Half Dome is 900 blocks tall. El Capitan is a vertical wall of granite blocks. The valley floor has meadow grass and river water in the right channels.

**A building you're designing.** Export your Revit or SketchUp model as OBJ. Voxelize it at 1 block = 0.5 meters. Walk through your design in VR (Vivecraft) before it's built. Share the world file with a client who doesn't have CAD software but does have Minecraft.

**Historical reconstruction.** Take a photogrammetry scan of ruins. Fill in the gaps with architectural assumptions. Palette-map it to period-appropriate materials. Students explore a Roman villa or a medieval cathedral at 1:1 scale, built from real survey data, not artistic interpretation.

**Scientific visualization.** Voxelize a protein structure, a fluid dynamics simulation, a geological cross-section. Minecraft's rendering engine handles millions of blocks at interactive framerates. The interaction model -- walk through it, break blocks to see inside, place torches to illuminate cavities -- is more intuitive than any scientific visualization tool.

#### What Makes This Different

Most Minecraft terrain generators work in one direction: they generate *fictional* terrain that looks plausible. This goes the other direction: it takes *real* terrain and makes it playable.

Most heightmap importers are scripts that read one format, output one format, and use a hardcoded block palette. GeoVox treats the whole pipeline as composable transforms. Swap the ingest module, swap the palette, swap the exporter. The same framework handles a 50km satellite DEM and a 2-meter photogrammetry scan of a single room.

The bidirectional part matters too. If you modify the Minecraft world -- add a building, dig a canal, terraform a hillside -- the system can diff the modified world against the original import and export the *changes* back as a 3D point cloud or mesh. Minecraft becomes a 3D editor. A voxel-native sketch tool for landscape architecture, urban planning, or terrain modification proposals.

#### Technical Foundation

*Current implementation (v0.1.1):*
- **Python core** -- NumPy for the voxel grid, Pillow for PNG heightmaps, rasterio (optional) for GeoTIFF
- **Custom NBT writer** for .nbt structure export (no external Minecraft libraries needed)
- **CLI-first** -- pipe data through it, script it, batch it
- **Config-driven** -- palettes in JSON, scale/origin configurable

*Planned additions:*
- PDAL for LAS/LAZ point cloud ingest, trimesh for OBJ/STL mesh voxelization
- anvil-parser or amulet-core for .mca world file export
- **No Minecraft installation required** -- reads and writes files only

The hard problems are scale management (a 1:1 import of a mountain range is billions of blocks -- you need LOD or selective import), palette intelligence (automatic material assignment from classification data is an unsolved UX problem), and Minecraft's own constraints (256-block build height pre-1.18, 384 post-1.18, chunk loading radius, entity limits).

The ideas are grounded in real capabilities -- every data format listed above has existing Python libraries, every Minecraft export format has community documentation, and the core voxelization algorithm (scanline fill of a 3D grid) is well-understood. What would make this worth building is the *composition*. Not another heightmap importer. A pipeline that lets you say: "Take this LiDAR scan, layer in this building footprint data, apply this palette, and give me a Minecraft world I can walk through this afternoon."

---

### Minecraft Studio -- Modding IDE

Roblox has 70 million daily active users, and a significant percentage of them are *creators*, not just players. That's not because Roblox is a better game than Minecraft. It's because Roblox has Studio.

Roblox Studio is the reason Roblox has an economy. It's a full integrated development environment -- 3D editor, script editor, properties panel, hierarchy explorer, asset library, one-click playtesting, one-click publishing -- all in a single application. A thirteen-year-old can open Studio, drag in some parts, write a few lines of Luau, press Play, and have a working multiplayer game in an hour. No terminal. No build system. No dependency management. No deployment pipeline.

Minecraft modding has none of that.

To make a Minecraft mod today, you need to: install a JDK, install an IDE (IntelliJ or Eclipse), clone a modloader MDK template, understand Gradle, wait for decompilation and remapping to finish, learn the Minecraft source architecture (which is decompiled and partially obfuscated), write Java boilerplate for registration, events, capabilities, networking, rendering, data generation -- and then test by launching an entire Minecraft instance from your IDE, which takes 30-90 seconds every time you change something. The barrier to entry is a cliff face.

Minecraft Studio would be the ladder.

#### What It Is

A standalone integrated development environment for Minecraft mod creation. One application. Download, install, open, create. Structured like Roblox Studio but built for the Minecraft ecosystem.

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
| > GUI    |                                    |  Flammable: No|
|          |                                    |               |
+----------+---------+--------------------------+---------------+
|  Code Editor       |  Visual Editor                          |
|                    |                                          |
|  @Mod("mymod")     |  [Recipe grid]  [Loot table tree]       |
|  public class ...  |  [World gen visual]  [GUI builder]      |
|                    |                                          |
+--------------------+------------------------------------------+
|  Console / Output / Build Log                      [Play ▶]  |
+---------------------------------------------------------------+
```

#### The Explorer Panel

The left panel mirrors Roblox Studio's Explorer tree, but organized around Minecraft's registry system:

| Node | Contents | What You Can Do |
|------|----------|-----------------|
| Blocks | Custom blocks | Visual block creator: pick a base, set properties (hardness, tool, drops, light level, redstone behavior), assign textures per face, define blockstates, preview in 3D |
| Items | Custom items | Visual item creator: set stack size, durability, enchantability, tool behavior, food properties, model type (handheld/flat/3D) |
| Entities | Custom mobs/entities | Entity builder: model editor (Blockbench-style, embedded), AI goal selector (visual flowchart), loot tables, spawn rules |
| World Generation | Biomes, features, structures | Visual world gen: biome parameter sliders (temperature, humidity, continentalness, erosion), feature placement preview, structure templates with jigsaw |
| Recipes | Crafting, smelting, smithing, etc. | Drag-and-drop recipe grid, all vanilla recipe types + custom |
| Loot Tables | Block drops, mob drops, chest loot | Tree-based loot table editor with probability sliders, conditions, functions |
| Events | Game event handlers | Visual event wiring: "when player breaks block → if block is X → drop custom item Y with 30% chance" |
| GUI | Custom screens/HUDs | WYSIWYG GUI editor for container screens, HUD overlays, custom inventories |
| Networking | Client-server packets | Packet designer: define fields, serialization is auto-generated |
| Data Packs | Functions, tags, advancements | Integrated datapack authoring alongside mod code |
| Resource Pack | Textures, models, sounds, lang | Asset pipeline with hot-reload preview |

#### The 3D Viewport

Center panel. This is the core innovation: an **embedded Minecraft instance** running your mod in real time.

Not a mock-up. Not a simplified preview. An actual Minecraft client instance, running inside the IDE, with your mod loaded. You see exactly what players will see. You interact with it the same way -- WASD movement, block placement, inventory. But with editor overlays:

- **Wireframe toggle** showing chunk boundaries, spawn regions, light levels
- **Entity inspector** -- click any mob to see its AI state, goals, target, pathfinding
- **Block state visualizer** -- hover over any block to see its blockstate properties
- **Redstone debugger** -- signal strength overlay, update order visualization
- **World gen preview** -- scrub through seeds, teleport to biome transitions, see feature placement in real time
- **Freeze frame** -- pause the game tick, step forward one tick at a time, inspect everything

The Play button doesn't launch a separate process. It hot-reloads your mod into the running instance. Change a block's hardness in the Properties panel, it updates in the viewport immediately. Change a recipe in the visual editor, the recipe book updates in real time. Edit Java code, the compiler runs incrementally, and only the changed classes reload. Iteration time drops from 30-90 seconds to under 2 seconds.

#### The Code Editor

Full Java IDE. Not a toy. This needs to compete with IntelliJ for mod developers who know what they're doing.

- **Java 21+** with full language support (records, sealed classes, pattern matching)
- **Kotlin** as a first-class alternative (many modern mods are Kotlin)
- **Autocomplete** against the full Minecraft source (decompiled, mapped to readable names -- Mojang mappings, Yarn, or MCP, user's choice)
- **Inline documentation** -- hover over any Minecraft class or method and see what it does, with examples
- **Live error checking** -- red squiggles on code that won't compile, yellow for deprecation
- **Refactoring tools** -- rename, extract method, move class, all Minecraft-aware (renames update registry references automatically)
- **Snippets and templates** -- "new block", "new item", "new entity", "new biome" generators that produce correct boilerplate for the target modloader
- **Mixin assistant** -- visual mixin target selector (browse Minecraft source, click a method, it generates the mixin class and injection point)

But here's the key: you don't *have* to touch the code editor. Every visual tool generates Java (or Kotlin) behind the scenes. The recipe editor writes `RecipeProvider` data generation code. The block creator writes the `Block` subclass, the `BlockItem`, the registration call, the blockstate JSON, the model JSON, the loot table JSON, and the lang entry. All of it. If you never open the code tab, you can still make a mod. If you do open it, you see clean, idiomatic, well-commented code that you can customize further.

This is the Roblox Studio principle: visual tools for accessibility, full code access for power.

#### The Visual Editors

These are the tools that don't exist anywhere in the current Minecraft modding ecosystem:

**Recipe Editor.** A 3x3 (or 2x2, or shapeless, or smithing, or stonecutting, or brewing) grid. Drag items in. Set the output. Done. No JSON files. No data generation classes. The visual editor generates both the data generation code *and* the runtime recipe object. Supports custom recipe types with a schema builder.

**Loot Table Editor.** Tree view. Top level: the table. Children: pools. Each pool has rolls (min/max), bonus rolls per luck, and entries. Entries can be items (with count, enchantment, NBT functions) or references to other tables. Conditions are checkboxes and sliders: "if killed by player", "with looting enchantment (fortune bonus: +1 per level)", "if in biome X", "random chance 30%". What currently requires writing nested JSON by hand or memorizing data generation builder chains becomes drag-and-drop.

**World Generation Editor.** This one is transformative. Minecraft's world generation is driven by density functions, noise routers, biome parameters (temperature, humidity, continentalness, erosion, depth, weirdness), and feature placement. These are currently configured through inscrutable JSON files or code that even experienced modders find opaque.

The visual editor shows:
- A **biome parameter space** visualizer -- 2D and 3D scatter plots of where biomes exist in parameter space, with your custom biomes highlighted. Drag to reposition. See conflicts in real time.
- A **density function graph** -- node-based editor (like Blender's shader nodes or Unreal's Blueprints). Each node is a density function operation (add, multiply, noise, spline, clamp, cache). Connect nodes. See the output as a live cross-section or 3D preview.
- A **feature placement previewer** -- toggle features on/off, see their placement patterns across chunks, adjust count/spread/chance with sliders and see the distribution update.
- A **structure template editor** -- 3D editor for structure pieces, jigsaw connection points, processor lists, pool weights. Build a village variant by placing rooms, connecting them with jigsaw blocks, and defining placement rules.

**Entity AI Editor.** Flowchart-based. Minecraft entity AI uses a goal system (goal selector for active goals, target selector for targeting). The visual editor shows each goal as a node in a priority-ordered list. Click to configure: "wander randomly within 10 blocks" → "flee from entities with tag 'predator' within 12 blocks at speed 1.4" → "eat nearby grass blocks every 100-200 ticks". The flowchart generates the `registerGoals()` method. For complex behavior, drop into code.

**GUI Editor.** WYSIWYG. Drag slots, buttons, labels, progress bars, text fields onto a screen. Set positions. Bind slots to inventories. Wire buttons to packet sends. The editor generates the `AbstractContainerScreen` subclass, the `AbstractContainerMenu`, the slot definitions, and the packet handler. What currently takes 200+ lines of coordinate math and rendering code becomes a visual layout tool.

**Particle Editor.** Live preview. Adjust count, speed, spread, color, gravity, lifetime, collision. See particles in the 3D viewport immediately. Export as a custom `ParticleType` with server/client packet handling auto-generated.

#### Modloader Export

This is where Minecraft Studio breaks the modloader wars wide open.

You build your mod once. Minecraft Studio exports it for any target:

| Target | Format | What Gets Generated |
|--------|--------|---------------------|
| Forge | Forge MDK project | `@Mod` annotations, `DeferredRegister`, Forge event bus, `ForgeRegistries`, Forge-specific mixins, Forge Gradle buildscript |
| NeoForge | NeoForge MDK project | `@Mod` annotations, NeoForge registry, NeoForge event system, NeoForge Gradle buildscript |
| Fabric | Fabric mod project | `ModInitializer`, Fabric registry, Fabric event callbacks, Fabric Loom buildscript |
| Quilt | Quilt mod project | `ModInitializer` (Quilt), Quilt registry, Quilt-specific APIs, Quilt Loom buildscript |
| Data Pack | Vanilla data pack | `.mcfunction` files, JSON configs, `pack.mcmeta` -- no modloader needed |
| Resource Pack | Vanilla resource pack | Textures, models, sounds, blockstate overrides, shaders |
| Multiloader | Architectury project | Shared common module + per-loader modules, Architectury Gradle buildscript |

The mod's logic is authored against an **abstraction layer** inside Studio. Registration, events, networking, rendering hooks -- all go through Studio's API, which maps to each modloader's specific implementation at export time. You don't write `ForgeRegistries.BLOCKS.register()` or `Registry.register(BuiltInRegistries.BLOCK, ...)`. You write `Studio.registerBlock()`, and the exporter handles the rest.

This isn't hypothetical. The Architectury project already proves that a common API can target Forge, Fabric, and Quilt simultaneously. Minecraft Studio would formalize that into a first-class development experience instead of a library you have to learn separately.

#### The Testing Environment

The embedded Minecraft instance isn't just for preview. It's a full test harness.

**Automated testing.** Write test scenarios:
```java
@StudioTest
void diamondPickaxeMinesTool() {
    world.setBlock(pos, Blocks.OBSIDIAN);
    player.setMainHand(Items.DIAMOND_PICKAXE);
    player.breakBlock(pos);
    assertThat(world.getBlock(pos)).isAir();
    assertThat(player.inventory()).contains(Items.OBSIDIAN);
}
```

The test runner executes inside the embedded instance. No separate test server. No `@GameTest` framework boilerplate. Write the assertion, press Run, see the result in the console and visually in the viewport.

**Performance profiling.** Built-in tick profiler, entity count monitor, chunk loading time graph, memory allocation tracker. See exactly where your mod's server tick time goes. Identify lag spikes. Optimize entity AI or world gen before players ever report "TPS dropped to 12."

**Multiplayer simulation.** Spin up a local server with N simulated players. Test chunk loading under load. Verify that your custom networking packets survive real latency. See how your world gen performs when 20 players are exploring in different directions simultaneously.

**Version matrix testing.** Test against multiple Minecraft versions from the same project. Studio maintains a version compatibility map: "this block was added in 1.19, this method was renamed in 1.20.4, this registry moved in 1.21." Export for 1.20.1, export for 1.21.4, export for the latest snapshot. The compatibility layer handles the differences.

#### What This Changes

The current Minecraft modding pipeline looks like this:

```
Learn Java → Learn Gradle → Learn the modloader → Learn decompiled Minecraft source
→ Write 800 lines of boilerplate → Wait 60 seconds for test launch → Find the bug
→ Alt-tab to IDE → Fix it → Wait 60 seconds again → Repeat
```

Minecraft Studio compresses that to:

```
Open Studio → Use visual tools or write code → See results in 2 seconds → Ship
```

The implications:

**Modding becomes accessible to non-programmers.** The same way Roblox Studio lets kids build games without formal programming knowledge, Minecraft Studio lets Minecraft players build mods without learning Java, Gradle, or modloader internals. The visual editors handle the 80% case. Code is there for the 20% that needs it.

**The modloader fragmentation problem goes away for creators.** You don't pick Forge vs. Fabric. You build a mod. You export for whichever loaders you want. Update the mod, re-export. The abstraction layer handles API differences. The community gets more mods on every platform instead of the current situation where mod authors pick one loader and half the playerbase can't use their work.

**Iteration speed transforms what people build.** When it takes 60 seconds to test a change, you make careful changes. When it takes 2 seconds, you experiment. You try wild ideas. You iterate on feel. The kinds of mods people build would change -- more ambitious, more polished, more experimental -- because the cost of trying things drops by an order of magnitude.

**Education gets a new toolchain.** Schools that teach Java through Minecraft modding currently spend weeks on environment setup and build system issues before students write a single line of game logic. Minecraft Studio eliminates that. Day one: open Studio, create a block, play with it. Day two: look at the generated Java code and understand what it does. The visual-to-code pipeline is a teaching tool, not just a convenience.

**Server operators get mod customization.** Right now, configuring a mod means editing JSON or TOML config files and restarting the server. Minecraft Studio could provide a server configuration mode where operators visually tweak mod parameters, test changes on a local instance, and deploy updated configs -- without touching code or restarting.

#### Technical Architecture

The application itself would be:

- **Java 21+ / JavaFX or Compose Desktop** for the IDE shell (native Minecraft language, shared toolchain)
- **Embedded Minecraft client** via classloader isolation (similar to how dev environments launch Minecraft today, but inside the Studio process with hot-reload hooks)
- **Incremental Java/Kotlin compiler** (Eclipse ECJ or Kotlin compiler daemon) for sub-second rebuild
- **Mojang mappings + intermediary mappings** for decompiled Minecraft source browsing and autocomplete
- **Abstract Syntax Tree manipulation** for the modloader-specific code generators -- parse the Studio abstraction layer calls and rewrite them to target-specific API calls
- **Gradle daemon** for final export builds (the exported project is a standard Gradle project that builds independently of Studio)
- **SQLite** for project metadata, asset registry, and undo history
- **Git integration** for version control (built into the IDE, not a separate tool)

The hardest problem is the hot-reload cycle. Minecraft wasn't designed for class hot-swapping at runtime. The approach: use a custom classloader that isolates mod classes from Minecraft core classes, and on recompile, discard and recreate the mod classloader while preserving the Minecraft instance state. This is similar to what DCEVM and JRebel do for general Java applications, but specialized for the Minecraft mod loading architecture.

The second hardest problem is the abstraction layer. Each modloader has different registration timing, event bus semantics, networking APIs, rendering hooks, and capability systems. The abstraction needs to be thin enough that exported code is readable and debuggable (not buried under layers of indirection) but complete enough that 95% of mod functionality doesn't require loader-specific code.

#### What Exists Today vs. What's Missing

| Capability | Existing Tool | Minecraft Studio |
|-----------|---------------|-----------------|
| Code editing | IntelliJ / Eclipse / VS Code | Integrated, with Minecraft-aware autocomplete |
| Block/item models | Blockbench (external app) | Embedded, linked to registry |
| Textures | Photoshop / GIMP (external) | Embedded pixel editor, live preview |
| Recipe creation | Hand-written JSON | Visual drag-and-drop grid |
| Loot tables | Hand-written JSON | Visual tree editor |
| World gen config | Hand-written JSON / code | Node graph + live preview |
| Entity AI | Pure code | Visual flowchart + code fallback |
| GUI layout | Pure code (coordinate math) | WYSIWYG editor |
| Testing | Launch entire game (60s) | Hot-reload in viewport (2s) |
| Modloader targeting | Pick one, rewrite for others | Export to any/all |
| Publishing | Manual upload to CurseForge/Modrinth | One-click publish to both |

Every row in the "Existing Tool" column is either a separate application, a manual text-editing process, or doesn't exist at all. Minecraft Studio collapses it into one window.

## Adding a Project

1. Create a subdirectory with a clear project name
2. Add a markdown file inside it describing the project concept, architecture, current status, and how to run or build it (follow the `*ME.md` naming pattern -- `VOXELME.md`, `STUDYME.md`, `BUILDME.md`, whatever fits)
3. Add a row to the Concepts table above
4. Add a Concept Details section in this file with the project's design overview
5. Update the root `README.md` with a bullet point under the Minecraft Innovations section

Projects at any stage are welcome -- from a design document with no code to a fully tested pipeline. Just be honest about what's built and what's planned.

## The Minecraft Standard

Minecraft's modding community has collectively built every piece of tooling it needs -- but in isolation, in incompatible formats, with documentation scattered across wikis, Discord servers, and abandoned GitHub repos. The standard for this folder is: build the tool you wish existed, make it composable, and document it like someone who's never seen your code will need to use it tomorrow.

The deeper principle: Minecraft is the most popular game ever made, and its creation tools are decades behind what smaller platforms offer. Every project here should narrow that gap.

## Notes

GeoVox and Minecraft Studio are different scales of ambition aimed at the same gap. Minecraft is the most popular game ever made. Its modding ecosystem is one of the most productive creative communities in software history. And the tooling is decades behind what Roblox gives its creators out of the box.

GeoVox is a focused pipeline tool with well-understood components. Minecraft Studio is an order of magnitude more ambitious -- a full IDE with an embedded game engine, a cross-compiler for modloader ABIs, and visual editors for systems that have never had visual editors.

But the pieces exist. Blockbench proved that visual Minecraft tooling has a massive audience. Architectury proved that cross-loader abstraction works. IntelliJ's Minecraft Development plugin proved that IDE integration helps. The Minecraft modding community has, collectively, built every piece of this puzzle in isolation. Nobody has assembled them into one coherent application.

The real world is already the most detailed voxel grid there is. And the Minecraft modding community is already the largest unpaid game development workforce on the planet. Both deserve better tools.

---

*Conceived by Claude (Opus 4.5), February 2026*

*Because every coordinate system eventually leads to Minecraft.*
