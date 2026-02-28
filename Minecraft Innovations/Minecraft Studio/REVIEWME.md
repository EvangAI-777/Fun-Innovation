# Minecraft Studio -- Next Steps Review

A review of the v0.1.0 prototype focused on how the current foundation supports future layers and what to build next.

## What's Here

Layer 1 is solid. 1,929 lines of source across 16 files, 83 passing tests in under a second, zero external dependencies. The data model covers blocks (14 materials, hardness/resistance/luminance validation), items (food + tool properties, creative tabs), all 7 vanilla recipe types, and loot tables with conditions and functions. Three working exporters produce complete, buildable projects for Fabric, Forge, and vanilla Data Packs. A CLI ties it together with 6 commands.

The architecture is clean: `model/` defines what a mod contains, `codegen/` generates Java source, `export/` produces loader-specific project trees. Each layer only depends on the one below it. This is the right structure.

## How the Foundation Supports Future Layers

### What works well

**The model layer is the interface for everything above it.** Visual editors only need to construct dataclasses and call `project.add_block()`, `project.add_recipe()`, etc. The Properties panel just reads and writes dataclass fields. The Explorer panel iterates `project.blocks`, `project.items`, `project.recipes`. Every future UI component consumes the same model -- no adapter layer needed.

**Protocol-based recipe system (`recipe.py:9-13`) is the right pattern.** The `Recipe` protocol defines `recipe_id`, `recipe_type()`, and `to_dict()` -- structural typing that lets 7 concrete recipe classes satisfy the interface without inheritance. Entity types, world gen features, and other polymorphic registries should follow this exact pattern.

**Exporter auto-registration (`base.py:132-134`) makes adding loaders trivial.** The `@_register` decorator extracts the loader name from the class name and adds it to the `EXPORTERS` dict. Adding NeoForge or Quilt is: write the class, decorate it, import it in `_init_exporters()`. No registry boilerplate.

**Generated Java code is idiomatic per loader.** Fabric gets `Registry.register()` with `Identifier.of()`. Forge gets `DeferredRegister` with `RegistryObject`. The generated code is what a human modder would write -- not framework-wrapped abstractions. This matters: when users open the Code Editor and read the generated source, it should teach them how Minecraft modding actually works, not how your abstraction works.

**`JavaWriter` (`codegen/java.py`) is reusable for all future codegen.** Import grouping (java.\* first, then others), indent tracking, field/annotation/block helpers -- this handles entity classes, GUI screens, world gen providers, event handlers, anything that needs Java output. The builder pattern (`w.set_package().add_import().open_block()...`) composes cleanly.

**JSON round-trips on every model object.** Every dataclass has `to_dict()` / `from_dict()`. This directly becomes the project file format (already does via `ModProject.save()`/`.load()`). It also enables undo/redo -- snapshot state before a change, restore on undo. And it's the migration path to SQLite: `to_dict()` produces the intermediate representation, SQLite stores it.

### What's missing before building higher layers

**No change propagation.** When a visual editor modifies a block's hardness, nothing notifies the Properties panel, the 3D viewport, or the export engine. Before building any UI, you need an observer/event system on the model layer. This doesn't have to be complex -- a simple callback registry on `ModProject` that fires on `add_block`, `remove_block`, `modify_block`, etc. is enough to start. The architecture doc describes a full event bus (`ARCHITECTURE.md:7`), but a lightweight observer pattern gets you there incrementally.

**No `model/event.py`.** The architecture describes event wiring ("when player breaks block, if block is X, drop item Y with 30% chance"), but there's no event model yet. Events are fundamental to modding -- `PlayerBreakBlockEvent`, `EntitySpawnEvent`, `PlayerJoinEvent`. Even a simple binding model (`EventBinding(event_type, condition, action)`) would unlock the visual event editor and generate `@SubscribeEvent` (Forge) / event callback (Fabric) code in the exporters.

**No entity model.** Entities are the most complex and intimidating part of Minecraft modding: attributes, AI goals, spawn rules, renderers, loot tables. They're also the highest-value addition for accessibility. The current model pattern (dataclass + `to_dict`/`from_dict` + exporter support) extends naturally to entities.

## What to Build Next

### 1. Small fixes first

These are quick wins that strengthen the foundation before building on top of it.

**Add `block_id` / `item_id` validation.** Right now you can do `Block(block_id="Bad Block!")` and it'll produce broken Java constants and invalid resource locations. The `_validate_mod_id()` function in `project.py:16-23` already does this for mod IDs -- apply the same regex pattern to block and item IDs in their `__post_init__` methods. Minecraft resource locations require `[a-z0-9_/.-]`.

**Enforce unique recipe IDs.** `project.py:60-62` -- `add_recipe()` just appends without checking for duplicates. Both `add_block()` (`project.py:48-52`) and `add_item()` (`project.py:54-58`) already check. Recipe ID collisions cause silent overwrites during export.

**Fix loot condition coverage.** `base.py:79-87` -- the `condition_map` only handles 4 of the 6 `LootCondition` enum values. `WITHOUT_SILK_TOUCH` and `MATCH_TOOL` fall through to the generic handler on line 105, which produces `{"condition": "minecraft:without_silk_touch"}` -- not a valid Minecraft condition. `without_silk_touch` should be an inverted `match_tool` predicate. `match_tool` needs a configurable predicate parameter.

**Make `random_chance` configurable.** `base.py:82` hardcodes `"chance": 0.5` for all `RANDOM_CHANCE` conditions. The `LootCondition` enum has no parameter support. Consider making conditions dataclasses instead of enums (or adding a `params` dict to `LootEntry`), so `random_chance(0.3)` can produce `{"chance": 0.3}`.

**Add a Forge version table.** `fabric.py:12-17` has `_FABRIC_VERSIONS` mapping MC versions to Fabric API/Yarn/Loader/Loom versions -- this is excellent. The Forge exporter doesn't have an equivalent; `forge.py` hardcodes a single Forge version. Add a `_FORGE_VERSIONS` dict mapping MC versions to Forge/MCP/Gradle versions.

**Move the inline import.** `project.py:138` -- `from .recipe import recipe_from_dict` is inside the `for` loop body in `load()`. It works (Python caches imports), but it's misleading -- move it to the top of the method or the module.

**Consolidate `to_pascal_case`.** `project.py:94` and `block.py:73` both inline `"".join(word.capitalize() for word in name.split("_"))`. `codegen/java.py:80-82` already exports `to_pascal_case()`. Import and use it instead of duplicating the logic.

### 2. NeoForge exporter

NeoForge replaced Forge as the primary modloader for Minecraft 1.20.2+. It's the highest value-per-effort addition because:
- The community is actively migrating from Forge to NeoForge
- It's structurally similar to Forge (fork `forge.py` as a starting point)
- The differences are well-defined: `net.neoforged` package names, `DeferredRegister.create(Registries.BLOCKS)` instead of `ForgeRegistries.BLOCKS`, NeoForge event bus instead of Forge event bus, different `mods.toml` format (now `neoforge.mods.toml`)
- You already have the exporter architecture to slot it in

Estimated scope: ~350 lines (mirroring `forge.py:335`), plus tests.

### 3. Entity model

Add `model/entity.py` following the established patterns:

```
EntityType dataclass:
  - entity_id: str
  - base_class: EntityBase enum (LivingEntity, Mob, Animal, Monster, etc.)
  - attributes: list[EntityAttribute]  (health, speed, attack_damage, follow_range, etc.)
  - goals: list[AIGoal]  (wander, flee, attack_melee, look_at_player, swim, etc.)
  - spawn_rules: SpawnRules  (biomes, light_level, block_below, weight, min/max_group)
  - loot_table: str | None  (reference to a LootTable)
  - width, height: float  (hitbox)

AIGoal dataclass:
  - goal_type: AIGoalType enum
  - priority: int
  - params: dict  (speed, distance, interval, etc.)
```

Update `ModProject` to add `entities: list[EntityType]`, `add_entity()`, `get_entity()`. Update all three exporters to generate entity registration, attribute providers, and `registerGoals()` methods. The Fabric and Forge registration patterns are different enough to justify separate codegen in each exporter.

This is the most complex addition but also the most impactful for the "make modding accessible" vision. Entity creation is where most beginners give up.

### 4. World gen model

Add `model/worldgen.py`:

```
Biome dataclass:
  - biome_id: str
  - temperature, humidity, continentalness, erosion, depth, weirdness: float
  - sky_color, fog_color, water_color, water_fog_color, grass_color: str (hex)
  - features: list[PlacedFeature]
  - spawn_settings: dict[MobCategory, list[SpawnerData]]

PlacedFeature dataclass:
  - feature_id: str
  - feature_type: FeatureType enum (ore, tree, flower, lake, etc.)
  - placement: PlacementConfig (count, height_range, rarity, etc.)
```

World gen is primarily JSON output -- biome JSON, feature JSON, placement JSON -- with minimal Java codegen (just a `ModWorldGen` class that registers biome sources and feature keys). This makes it a medium-effort addition with high visual impact: the world gen visual editor described in `ARCHITECTURE.md:147-152` operates entirely on this model.

### 5. Placeholder texture generation

Right now, exported projects have no textures. The blockstate and model JSONs reference `mod_id:block/block_id` and `mod_id:item/item_id`, but no PNG files exist. The exported project compiles but every block and item renders as the missing-texture purple-and-black checkerboard.

Add a simple texture generator (using Pillow, which is already a dependency in the sibling GeoVox project) that creates solid-color placeholder PNGs during export. Color based on `BlockMaterial` -- stone gets gray, wood gets brown, metal gets silver, etc. Overlay the block/item ID as text. This makes the `mcstudio new → add-block → export → gradle build → run` workflow produce a visible, functional mod on the first try.

This is a quality-of-life improvement, not a core feature. But it dramatically improves the first-run experience and demonstrates the end-to-end pipeline working.

## How Visual Editors Will Connect

Each visual editor in the architecture (`ARCHITECTURE.md:128-177`) maps directly onto the model layer:

| Visual Editor | Model It Operates On | Already Exists? |
|--------------|---------------------|-----------------|
| Recipe Editor | `model/recipe.py` (all 7 types) | Model: yes. Editor: no. |
| Loot Table Editor | `model/loot.py` (tables, pools, entries, conditions) | Model: yes. Editor: no. |
| World Gen Editor | `model/worldgen.py` (biomes, features, placement) | Model: no. |
| Entity AI Editor | `model/entity.py` (goals, attributes, spawn rules) | Model: no. |
| GUI Editor | `model/gui.py` (screens, slots, buttons, widgets) | Model: no. |
| Particle Editor | `model/particle.py` (types, count, speed, color) | Model: no. |

The pattern is clear: each visual editor is a UI layer that reads and writes model dataclasses. The model layer is the API boundary. Build the models first, then the editors become pure UI work.

The missing piece before any visual editor works is **change notification**. When the recipe editor modifies a `ShapedRecipe`, the code editor needs to regenerate, the Properties panel needs to update, and the project needs to mark itself as dirty. Add an observer pattern to `ModProject` before starting on editors.

## Architecture Roadmap

Based on what's here and what the architecture documents describe, here's a suggested layer ordering:

```
Layer 1 (done):  Data model + export engine + CLI
Layer 2 (next):  Small fixes + NeoForge + entity/worldgen models
Layer 3:         Observer pattern on model + undo/redo via to_dict snapshots
Layer 4:         JavaFX/Compose shell + Explorer panel + Properties panel
Layer 5:         Visual editors (recipe first -- simplest, highest confidence)
Layer 6:         Code editor (Java/Kotlin with Minecraft autocomplete)
Layer 7:         Embedded viewport + hot-reload
```

Layers 2-3 are pure Python with no UI dependencies. Layer 4 is where you commit to a UI framework (JavaFX vs Compose Desktop -- the architecture doc defers this decision, and that's wise). Layers 5-6 build on the shell. Layer 7 is the hardest: classloader isolation, state preservation across reloads, editor overlays.

The current Python implementation is a prototyping tool and CLI. The final IDE described in the architecture is Java/Kotlin. The Python model layer is still valuable as a specification -- the dataclass definitions, validation rules, serialization formats, and export patterns all translate directly to Java/Kotlin equivalents. The test suite becomes the acceptance test for the Java port.

---

*Reviewed February 2026. Layer 1 is a strong foundation -- clean separation, correct patterns, comprehensive tests. The next steps are incremental: fix the small issues, add entity and world gen models, then build the observer pattern that lets UI layers consume the model. Each step is independently useful and testable.*
