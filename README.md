# Fun-Innovation

A growing collection of collaborative projects between human and AI -- organized by theme, open to whatever comes next.

## Repository Structure

```
Fun-Innovation/
|-- INVALID_REQUEST/
|   |-- HTML Files/
|   |   |-- academic-planner.html
|   |   |-- ecosystem.html
|   |   |-- flowfield.html
|   |   |-- generative-music.html
|   |   |-- notes-organizer.html
|   |-- Python Files/
|   |   |-- living_story.py
|   |   |-- verse_engine.py
|   |-- DELETEME.md
|-- Roblox Innovations/
|   |-- Academic Planner Study Hub/
|   |   |-- AssignmentManager.luau
|   |   |-- PlannerClient.luau
|   |   |-- PlannerConfig.luau
|   |   |-- PlannerServer.luau
|   |   |-- SETUP.md
|   |-- Ecosystem Survival/
|   |   |-- CreatureManager.luau
|   |   |-- EcosystemClient.luau
|   |   |-- EcosystemConfig.luau
|   |   |-- EcosystemServer.luau
|   |   |-- SETUP.md
|   |-- Flow Field Obby/
|   |   |-- FlowFieldClient.luau
|   |   |-- FlowFieldConfig.luau
|   |   |-- FlowFieldServer.luau
|   |   |-- PlatformGenerator.luau
|   |   |-- SETUP.md
|   |-- Generative Music Rooms/
|   |   |-- MusicClient.luau
|   |   |-- MusicConfig.luau
|   |   |-- MusicServer.luau
|   |   |-- SoundscapeEngine.luau
|   |   |-- SETUP.md
|   |-- Living Story RPG/
|   |   |-- DialogueManager.luau
|   |   |-- StoryClient.luau
|   |   |-- StoryConfig.luau
|   |   |-- StoryServer.luau
|   |   |-- SETUP.md
|   |-- Notes Organizer Bulletin Board/
|   |   |-- BulletinClient.luau
|   |   |-- BulletinConfig.luau
|   |   |-- BulletinServer.luau
|   |   |-- NoteManager.luau
|   |   |-- SETUP.md
|   |-- Verse Engine Skywriting/
|   |   |-- PoetryEngine.luau
|   |   |-- SkywritingClient.luau
|   |   |-- SkywritingServer.luau
|   |   |-- VerseConfig.luau
|   |   |-- SETUP.md
|   |-- FUNME.md
|-- Minecraft Innovations/
|   |-- GeoVox/
|   |   |-- Design/
|   |   |   |-- ARCHITECTURE.md
|   |   |-- src/
|   |   |   |-- geovox/
|   |   |       |-- core/
|   |   |       |-- ingest/
|   |   |       |-- palette/
|   |   |       |-- export/
|   |   |-- palettes/
|   |   |-- tests/
|   |   |-- examples/
|   |   |-- SETUP.md
|   |-- Minecraft Studio/
|   |   |-- Design/
|   |   |   |-- ARCHITECTURE.md
|   |   |-- src/
|   |   |   |-- app/
|   |   |   |-- explorer/
|   |   |   |-- viewport/
|   |   |   |-- editor/
|   |   |   |-- visual/
|   |   |   |   |-- recipe/
|   |   |   |   |-- loot/
|   |   |   |   |-- worldgen/
|   |   |   |   |-- entity/
|   |   |   |   |-- gui/
|   |   |   |   |-- particle/
|   |   |   |-- export/
|   |   |   |   |-- forge/
|   |   |   |   |-- neoforge/
|   |   |   |   |-- fabric/
|   |   |   |   |-- quilt/
|   |   |   |   |-- datapack/
|   |   |   |   |-- resourcepack/
|   |   |   |-- testing/
|   |   |   |-- abstraction/
|   |   |-- resources/
|   |   |-- tests/
|   |   |-- SETUP.md
|   |-- MCME.md
|-- Undertale Innovations/
|   |-- OvertaleRPG/
|   |   |-- Original Archive/
|   |   |   |-- Artwork/
|   |   |   |-- Misc/
|   |   |   |-- Music/
|   |   |   |-- Playable Builds/
|   |   |   |-- Writing & Documents/
|   |   |   |-- SETUP.md
|   |   |-- Revival/
|   |   |   |-- Design/
|   |   |   |   |-- SCOPE.md
|   |   |   |   |-- ENGINE.md
|   |   |   |   |-- ROADMAP.md
|   |   |   |-- Scripts/
|   |   |   |-- Engine/
|   |   |   |-- Assets/
|   |   |   |   |-- Sprites/
|   |   |   |   |-- Music/
|   |   |   |   |-- Tilesets/
|   |   |   |   |-- UI/
|   |   |   |-- Builds/
|   |   |   |-- SETUP.md
|   |-- UTME.md
|-- README.md
```

## Directories

### [INVALID_REQUEST](./INVALID_REQUEST/)

The original session. Seven standalone projects -- five **browser-based** HTML applications and two **terminal-based** Python programs -- all built in a single sitting from a session the system flagged as invalid before it started. The HTML files open directly in any browser (no server, no build step). The Python files run in any terminal with Python 3.6+ (no external packages). Emergent simulations, generative music, interactive fiction, poetry generation, an academic planner, and a notes organizer. No dependencies. Everything runs as-is.

See [`INVALID_REQUEST/DELETEME.md`](./INVALID_REQUEST/DELETEME.md) for the full story and project details.

### [Roblox Innovations](./Roblox%20Innovations/)

Design concepts for bringing every INVALID_REQUEST project into Roblox Studio. Not ports -- reimaginings that take advantage of 3D space, physics, and multiplayer. Each of the seven concepts has its own subdirectory with versioned SETUP.md files (v1.0.1 or v1.0.2). All buildable with stock Studio and Luau. All 28 Luau files have been audited against the current Roblox Studio API surface (February 2026) and all SETUP.md claims verified against actual code. Four projects (Verse Engine Skywriting, Ecosystem Survival, Generative Music Rooms, Living Story RPG) received additional code verification fixes at v1.0.2 -- bug fixes, deprecated API replacement, and missing feature implementation.

See [`Roblox Innovations/FUNME.md`](./Roblox%20Innovations/FUNME.md) for detailed implementation breakdowns.

### [Minecraft Innovations](./Minecraft%20Innovations/)

Concept designs for Minecraft infrastructure tooling. Two projects, each with its own subdirectory, architecture documents, and scaffolded source structure ready for development:

- **[GeoVox](./Minecraft%20Innovations/GeoVox/)** -- a modular Python pipeline for importing real-world 3D data (heightmaps, LiDAR, photogrammetry, GeoJSON, voxel grids) into playable Minecraft worlds with palette-driven voxelization and multiple export formats (.mca, .nbt, .litematic, .mcfunction).
- **[Minecraft Studio](./Minecraft%20Innovations/Minecraft%20Studio/)** -- a standalone Java/Kotlin IDE for Minecraft mod creation modeled on Roblox Studio, with visual editors for recipes/loot tables/world gen/entity AI/GUIs/particles, an embedded live preview with hot-reload, and export to any modloader (Forge, NeoForge, Fabric, Quilt, Data Pack, Resource Pack, Architectury multiloader).

No code yet -- these are design documents with scaffolded project structures. See [`Minecraft Innovations/MCME.md`](./Minecraft%20Innovations/MCME.md) for the original concept document, or each project's own README for focused overviews.

### [Undertale Innovations](./Undertale%20Innovations/)

Projects that take the Undertale universe seriously -- fan games, revivals, tools, and experiments. Each project lives in its own subdirectory. Current project:

- **[OvertaleRPG](./Undertale%20Innovations/OvertaleRPG/)** -- revival of an abandoned Undertale fan game whose dev team released their entire production folder to the public in 2017. Artwork, music, playable builds, and six design documents including a full GDD, a codex & lore bible, and core game systems specs. `Original Archive/` holds the source material; `Revival/` is where new work goes.

See [`Undertale Innovations/UTME.md`](./Undertale%20Innovations/UTME.md) for the full story and project details.

## Adding New Directories

This repo is organized by project theme. Each directory is its own self-contained initiative with its own markdown file documenting what's inside. To add a new one:

1. Create a new directory at the repo root
2. Add a markdown file inside it describing the projects and how to run them
3. Add a section to this README under **Directories** with a brief summary and a link to the directory's markdown file

No strict naming conventions. No required templates. Just keep it organized and documented.

## Quick Start

**Browser-based projects (INVALID_REQUEST/HTML Files):**
Open any `.html` file directly in a browser -- double-click or drag into a tab. No server, no build step, no install. Everything runs client-side.

**Terminal-based projects (INVALID_REQUEST/Python Files):**
Run in any terminal with Python 3.6+. No external packages. Interactive stdin/stdout programs.
```bash
python3 "INVALID_REQUEST/Python Files/living_story.py"
python3 "INVALID_REQUEST/Python Files/verse_engine.py"
```

**Roblox projects (Roblox Innovations):**
All seven projects are fully built. See each project's SETUP.md for Studio setup instructions: [`Flow Field Obby`](./Roblox%20Innovations/Flow%20Field%20Obby/SETUP.md), [`Verse Engine Skywriting`](./Roblox%20Innovations/Verse%20Engine%20Skywriting/SETUP.md), [`Notes Organizer Bulletin Board`](./Roblox%20Innovations/Notes%20Organizer%20Bulletin%20Board/SETUP.md), [`Academic Planner Study Hub`](./Roblox%20Innovations/Academic%20Planner%20Study%20Hub/SETUP.md), [`Ecosystem Survival`](./Roblox%20Innovations/Ecosystem%20Survival/SETUP.md), [`Generative Music Rooms`](./Roblox%20Innovations/Generative%20Music%20Rooms/SETUP.md), and [`Living Story RPG`](./Roblox%20Innovations/Living%20Story%20RPG/SETUP.md). Full details in [`Roblox Innovations/FUNME.md`](./Roblox%20Innovations/FUNME.md).

**Minecraft concepts (Minecraft Innovations):**
Design documents with scaffolded project structures -- no code yet. Two projects: [`GeoVox`](./Minecraft%20Innovations/GeoVox/) (real-world 3D data → Minecraft worlds) and [`Minecraft Studio`](./Minecraft%20Innovations/Minecraft%20Studio/) (a Roblox Studio-style IDE for Minecraft mod creation). Each has its own README and architecture doc. The original concept document is [`Minecraft Innovations/MCME.md`](./Minecraft%20Innovations/MCME.md).

**Undertale projects (Undertale Innovations):**
Fan games, revivals, and experiments in the Undertale universe. Current project: OvertaleRPG. Read [`Undertale Innovations/UTME.md`](./Undertale%20Innovations/UTME.md) for the full story and project details.

---

*Started by Claude (Opus) and Charlie, January 2026. Still building.*
