# Fun-Innovation

A growing collection of collaborative projects between human and AI -- organized by theme, open to whatever comes next.

## Directories

### [INVALID_REQUEST](./INVALID_REQUEST/)

The original session. Seven standalone projects built in a single sitting from a session the system flagged as invalid before it started. No dependencies -- everything runs as-is:

- **[Ecosystem](./INVALID_REQUEST/HTML%20Files/ecosystem.html)** -- emergent life simulation with plants, herbivores, and predators creating complex behavior from simple rules (HTML, browser-based)
- **[Flow Field](./INVALID_REQUEST/HTML%20Files/flowfield.html)** -- Perlin noise flow field with thousands of particles creating organic visual patterns (HTML, browser-based)
- **[Generative Music](./INVALID_REQUEST/HTML%20Files/generative-music.html)** -- algorithmic music synthesizer producing endless, never-repeating compositions (HTML, browser-based)
- **[Academic Planner](./INVALID_REQUEST/HTML%20Files/academic-planner.html)** -- dynamic academic schedule planner with OCR document scanning (HTML, browser-based)
- **[Notes Organizer](./INVALID_REQUEST/HTML%20Files/notes-organizer.html)** -- rich text notes app with folders, markdown/HTML editing, and import/export (HTML, browser-based)
- **[Living Story](./INVALID_REQUEST/Python%20Files/living_story.py)** -- interactive fiction that tracks your personality and remembers who you've been (Python, terminal-based)
- **[Verse Engine](./INVALID_REQUEST/Python%20Files/verse_engine.py)** -- poetry generator with five distinct voices and multiple forms (Python, terminal-based)

See [`INVALID_REQUEST/DELETEME.md`](./INVALID_REQUEST/DELETEME.md) for the full story and project details.

### [Roblox Innovations](./Roblox%20Innovations/)

Reimaginings of every INVALID_REQUEST project for Roblox Studio -- not ports, but designs that take advantage of 3D space, physics, and multiplayer. All buildable with stock Studio and Luau, all 28 Luau files audited against the February 2026 API surface. Each project has its own subdirectory with a versioned SETUP.md (v1.0.3):

- **[Flow Field Obby](./Roblox%20Innovations/Flow%20Field%20Obby/)** -- floating platforms drift through noise-driven currents, players learn to read the flow (v1.0.3)
- **[Verse Engine Skywriting](./Roblox%20Innovations/Verse%20Engine%20Skywriting/)** -- poems materialize as 3D particle text in the sky, drift upward, and dissolve (v1.0.3)
- **[Ecosystem Survival](./Roblox%20Innovations/Ecosystem%20Survival/)** -- third-person survival where players pick a species and coexist in a Perlin-noise biome grid (v1.0.3)
- **[Generative Music Rooms](./Roblox%20Innovations/Generative%20Music%20Rooms/)** -- six mood-themed rooms in a hexagonal ring, composition reacts to player count and activity (v1.0.3)
- **[Living Story RPG](./Roblox%20Innovations/Living%20Story%20RPG/)** -- persistent multiplayer town where NPCs remember individual players via DataStore (v1.0.3)
- **[Academic Planner Study Hub](./Roblox%20Innovations/Academic%20Planner%20Study%20Hub/)** -- virtual campus with dorm desks, color-coded assignment sticky notes, and shared study rooms (v1.0.3)
- **[Notes Organizer Bulletin Board](./Roblox%20Innovations/Notes%20Organizer%20Bulletin%20Board/)** -- notes become framed objects placed on walls and tables, folders become rooms (v1.0.3)

See [`Roblox Innovations/FUNME.md`](./Roblox%20Innovations/FUNME.md) for the theme overview and each project's SETUP.md for Studio setup instructions.

### [Minecraft Innovations](./Minecraft%20Innovations/)

Minecraft infrastructure tooling. Two projects, each with its own subdirectory, architecture documents, and scaffolded source structure:

- **[GeoVox](./Minecraft%20Innovations/GeoVox/)** (v0.1.1) -- a modular Python pipeline for importing real-world 3D data (heightmaps, with LiDAR/mesh/GeoJSON planned) into playable Minecraft worlds with palette-driven voxelization. Working pipeline: heightmap ingest, grid engine, 3 themed palettes, .mcfunction and .nbt structure export, 27 passing tests.
- **[Minecraft Studio](./Minecraft%20Innovations/Minecraft%20Studio/)** (v0.1.0) -- a standalone IDE for Minecraft mod creation modeled on Roblox Studio, with visual editors for recipes/loot tables/world gen/entity AI/GUIs/particles, an embedded live preview with hot-reload, and export to any modloader (Forge, NeoForge, Fabric, Quilt, Data Pack, Resource Pack, Architectury multiloader). Layer 1 (data model + export engine) is implemented: complete mod project model (blocks, items, recipes, loot tables), Java code generation, and working exporters for Fabric, Forge, and vanilla Data Packs. 83 passing tests.

See [`Minecraft Innovations/MCME.md`](./Minecraft%20Innovations/MCME.md) for the original concept document, [`GeoVox/VOXELME.md`](./Minecraft%20Innovations/GeoVox/VOXELME.md) and [`Minecraft Studio/STUDYME.md`](./Minecraft%20Innovations/Minecraft%20Studio/STUDYME.md) for project overviews.

### [Undertale Innovations](./Undertale%20Innovations/)

Projects that take the Undertale universe seriously -- fan games, revivals, tools, and experiments. Each project lives in its own subdirectory. Current project:

- **[OvertaleRPG](./Undertale%20Innovations/OvertaleRPG/)** -- revival of an abandoned Undertale fan game whose dev team released their entire production folder to the public in 2017. Artwork, music, playable builds, and six design documents. `Original Archive/` holds the source material; `Revival/` is where new work goes. **On hold** -- the structure and five-phase revival plan are in place, ready to be picked back up and remade into something really cool.

See [`OvertaleRPG/OVERME.md`](./Undertale%20Innovations/OvertaleRPG/OVERME.md) for the full project story and revival plan.

### [Audio Innovations](./Audio%20Innovations/)

New and creative approaches to audio -- production tools, compositional systems, sound design experiments, and anything else that rethinks how music and sound get made. Some projects are conversational (AI as collaborator), some may take entirely different forms. Current project:

- **[AutoMuse](./Audio%20Innovations/AutoMuse/)** (v0.1.0) -- a conversational DAW where the primary interface is a dialogue with a music AI persona. Covers all genres, scales, modes, time signatures, key signatures, and tempos. The AI collaborates on composition, arrangement, and production, with export to MIDI, MusicXML, audio stems, and project files for other DAWs. Three scaling layers: conversation (text + MIDI export), canvas (visual arrangement + notation), and full studio (real-time audio, plugin hosting, mixing). Layer 1 (The Conversation) is implemented: music theory engine with notes, intervals, scales, chords, keys, rhythm, progressions, harmonic analysis, voicings, MIDI export, and the Muse conversational interface. 197 passing tests.

See [`AutoMuse/MUSEME.md`](./Audio%20Innovations/AutoMuse/MUSEME.md) for the full project concept.

## Testing

All tests run through pytest and are wired into CI (GitHub Actions) and a top-level Makefile.

| Suite | What it covers | Tests | Run with |
|-------|---------------|-------|----------|
| **GeoVox** | Unit + integration tests for the voxel pipeline -- grid, palette, heightmap ingest, both exporters, NBT writer | 27 | `make test-geovox` |
| **Roblox Static Analysis** | Python-based static analysis of all 28 Luau scripts -- architecture conformance, deprecated API detection, config sanity, cross-module references, documentation, PoetryEngine template integrity | 102 | `make test-roblox` |
| **Original Projects** | Functional tests for verse_engine.py (word banks, voice configs, template integrity, all generation modes) and living_story.py (personality tracking, trait logic, story state, scenario playthroughs) | 48 | `make test-originals` |
| **AutoMuse** | Unit + integration tests for the music theory engine -- notes, intervals, scales, chords, keys, rhythm, progressions, harmonic analysis, voicings, MIDI writer, and the Muse conversational interface | 197 | `make test-automuse` |
| **Minecraft Studio** | Unit + integration tests for the mod data model and export engine -- blocks, items, recipes, loot tables, project serialization, Java codegen, Fabric/Forge/Data Pack export with generated Java source validation | 83 | `make test-mcstudio` |

Run everything: `make test`

The Roblox suite deserves a note: Luau scripts can't execute outside Roblox Studio, so instead of fighting the runtime, the tests parse `.luau` files as text and validate structure and conventions. This catches the same class of bugs the v1.0.3 manual audit found (deprecated `tick()`, missing module references) but automatically on every push.

CI runs both suites on every push to main and on every pull request.

## Adding New Directories

This repo is organized by project theme. Each directory is its own self-contained initiative with its own markdown file documenting what's inside. To add a new one:

1. Create a new directory at the repo root
2. Add a markdown file inside it describing the projects and how to run them
3. Add a section to this README under **Directories** with a brief summary and a link to the directory's markdown file

No strict naming conventions. No required templates. Just keep it organized and documented.

## Quick Start

**Original projects (INVALID_REQUEST):**
Seven standalone projects -- five browser-based HTML apps and two terminal-based Python programs. Open any `.html` file directly in a browser (no build step). Run Python files in any terminal with Python 3.6+ (no external packages). The full story and run instructions are in [`INVALID_REQUEST/DELETEME.md`](./INVALID_REQUEST/DELETEME.md).

**Roblox projects (Roblox Innovations):**
All seven projects are fully built -- reimaginings of INVALID_REQUEST projects for 3D multiplayer. See each project's SETUP.md for Studio setup instructions: [`Flow Field Obby`](./Roblox%20Innovations/Flow%20Field%20Obby/SETUP.md), [`Verse Engine Skywriting`](./Roblox%20Innovations/Verse%20Engine%20Skywriting/SETUP.md), [`Ecosystem Survival`](./Roblox%20Innovations/Ecosystem%20Survival/SETUP.md), [`Generative Music Rooms`](./Roblox%20Innovations/Generative%20Music%20Rooms/SETUP.md), [`Living Story RPG`](./Roblox%20Innovations/Living%20Story%20RPG/SETUP.md), [`Academic Planner Study Hub`](./Roblox%20Innovations/Academic%20Planner%20Study%20Hub/SETUP.md), and [`Notes Organizer Bulletin Board`](./Roblox%20Innovations/Notes%20Organizer%20Bulletin%20Board/SETUP.md). The theme overview is [`Roblox Innovations/FUNME.md`](./Roblox%20Innovations/FUNME.md).

**Minecraft projects (Minecraft Innovations):**
Two projects. [`GeoVox`](./Minecraft%20Innovations/GeoVox/) (v0.1.1) is a working Python pipeline -- `pip install -e .` then `geovox heightmap.png out.mcfunction` (see [`VOXELME.md`](./Minecraft%20Innovations/GeoVox/VOXELME.md)). [`Minecraft Studio`](./Minecraft%20Innovations/Minecraft%20Studio/) (v0.1.0) -- `pip install -e .` then `mcstudio new my_mod && mcstudio add-block my_mod.json custom_ore && mcstudio export my_mod.json fabric` to create and export a mod project (see [`STUDYME.md`](./Minecraft%20Innovations/Minecraft%20Studio/STUDYME.md)). The original concept document is [`Minecraft Innovations/MCME.md`](./Minecraft%20Innovations/MCME.md).

**Undertale projects (Undertale Innovations):**
Fan games, revivals, and experiments in the Undertale universe. Current project: [`OvertaleRPG`](./Undertale%20Innovations/OvertaleRPG/) (abandoned fan game revival from a 2017 Google Drive archive, see [`OVERME.md`](./Undertale%20Innovations/OvertaleRPG/OVERME.md)).

**Audio projects (Audio Innovations):**
New approaches to music and sound production. Current project: [`AutoMuse`](./Audio%20Innovations/AutoMuse/) (v0.1.0) -- `pip install -e .` then `automuse` or `python -m automuse` to start a session with the Muse (see [`MUSEME.md`](./Audio%20Innovations/AutoMuse/MUSEME.md)).

---

*Started by Claude (Opus) and Charlie, January 2026. Still building.*
