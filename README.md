# Fun-Innovation

Building things that have never existed before—and having fun while doing it. Every project here is a collaboration between human and AI, pushing into territory neither would reach alone. Organized by theme, open to whatever comes next.

## Directories

### [INVALID_REQUEST](./INVALID_REQUEST/)

The original session. Seven standalone projects built in a single sitting from a session the system flagged as invalid before it started. No dependencies -- everything runs as-is:

- **[Ecosystem](./INVALID_REQUEST/HTML%20Files/ecosystem.html)** -- emergent life simulation with plants, herbivores, and predators creating complex behavior from simple rules, with an integrated "Reality 101" study guide connecting simulation dynamics to real-world population data (HTML, browser-based)
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
- **[Minecraft Studio](./Minecraft%20Innovations/Minecraft%20Studio/)** (v0.2.0) -- a standalone IDE for Minecraft mod creation modeled on Roblox Studio, with visual editors for recipes/loot tables/world gen/entity AI/GUIs/particles, an embedded live preview with hot-reload, and export to any modloader (Forge, NeoForge, Fabric, Quilt, Data Pack, Resource Pack, Architectury multiloader). Layer 1 (data model + export engine) is implemented: complete mod project model (blocks, items, entities, biomes, recipes, loot tables), Java code generation, and working exporters for Fabric, Forge, NeoForge, and vanilla Data Packs with placeholder texture generation. 118 passing tests.

See [`Minecraft Innovations/MCME.md`](./Minecraft%20Innovations/MCME.md) for the original concept document, [`GeoVox/VOXELME.md`](./Minecraft%20Innovations/GeoVox/VOXELME.md) and [`Minecraft Studio/STUDYME.md`](./Minecraft%20Innovations/Minecraft%20Studio/STUDYME.md) for project overviews.

### [Undertale Innovations](./Undertale%20Innovations/)

Projects that take the Undertale universe seriously -- fan games, revivals, tools, and experiments. Each project lives in its own subdirectory. Current project:

- **[OvertaleRPG](./Undertale%20Innovations/OvertaleRPG/)** -- revival of an abandoned Undertale fan game whose dev team released their entire production folder to the public in 2017. Artwork, music, playable builds, and six design documents. `Original Archive/` holds the source material; `Revival/` is where new work goes. **On hold** -- the structure and five-phase revival plan are in place, ready to be picked back up and remade into something really cool.

See [`Undertale Innovations/UNDERME.md`](./Undertale%20Innovations/UNDERME.md) for the theme overview and [`OvertaleRPG/OVERME.md`](./Undertale%20Innovations/OvertaleRPG/OVERME.md) for the full project story and revival plan.

### [OMNI INNOVATIONS](./OMNI%20INNOVATIONS/)

Mathematics across universes, and creative tools born from the same philosophy. Three parallel subdirectories:

- **[Omniversal Mathematics](./OMNI%20INNOVATIONS/Omniversal%20Mathematics/)** -- the theoretical foundation. Omnidirectional Mathematics is a formal notation system for describing transformations across dimensional spaces, with fourteen fundamental operations composing into expressions that describe movement between any two points in any dimensional space. The core axiom: Movement = Transformation Sequence.

- **[Omniversal Calculator](./OMNI%20INNOVATIONS/Omniversal%20Calculator/)** (v1.4.1) -- the world's first Omniversal Calculator. Nine mathematical universes in a single browser-based interface, each with its own color identity, custom input layout, and genuine math engine. The Real universe features an expression-based engine with a recursive-descent parser, clickable cursor, and live result preview, with pill-shaped buttons in the unified site-wide palette. Every button press inserts at the cursor position; implicit multiplication (e.g., 2π = 2×π), postfix operators (!, %), degree/radian toggle, inverse trig, factorial, logarithms, and smart parentheses are all supported. Eight conventional universes (real, complex, modular, matrix, quaternion, boolean, tropical, dual) plus the Omnidirectional universe with two modes: **Build** (step-by-step transformation constructor) and **Receive & Graph** (type or paste omniversal coordinates as text and the calculator parses and visualizes the transformation path). The Receive & Graph parser accepts formal Unicode notation (`⊕[3]⟲[90°]◬⊠∿`), ASCII shorthand (`ascend[3] cw[90] boundary intersect wave`), or any mix, with contextual autocomplete as you type. Includes an animated starfield background, Argand diagram visualization, live truth tables, automatic differentiation, and dimensional path visualization. Zero dependencies -- open the HTML file in any browser. 171 passing tests.

- **[Omni Writer](./OMNI%20INNOVATIONS/Omni%20Writer/)** (v2.1.0) -- a creative writing tool born from the Omni Writer persona, with built-in AI Mode supporting four providers (Gemini, OpenAI, Anthropic, and Perchance -- the latter free with no API key). Toggle AI on for three actions: Continue (extend your story), Enhance (rewrite selected text), and Generate (write from a prompt) -- all streaming token by token. New in v2.1: directive input to steer the AI's direction, Ideas panel with Next/Style/Critique tabs, one-paragraph-at-a-time mode, purple prose guard, paragraph-level undo, and paragraph ratings. Smart context management automatically summarizes long stories. Distraction-free rich text editing with story continuation, multi-chapter management, a localStorage story library, and export to plain text, markdown, and HTML. Unified dark purple theme matching the site-wide palette. Zero dependencies -- open the HTML file in any browser.

See [`OMNI INNOVATIONS/OMNIME.md`](./OMNI%20INNOVATIONS/OMNIME.md) for the theme overview, [`Omniversal Mathematics/MATHME.md`](./OMNI%20INNOVATIONS/Omniversal%20Mathematics/MATHME.md) for the formal notation specification, [`Omniversal Calculator/CALCULATEME.md`](./OMNI%20INNOVATIONS/Omniversal%20Calculator/CALCULATEME.md) for the calculator guide, and [`Omni Writer/WRITEME.md`](./OMNI%20INNOVATIONS/Omni%20Writer/WRITEME.md) for the writer guide.

### [Audio Innovations](./Audio%20Innovations/)

New and creative approaches to audio -- production tools, compositional systems, sound design experiments, and anything else that rethinks how music and sound get made. Some projects are conversational (AI as collaborator), some may take entirely different forms. Current project:

- **[AutoMuse](./Audio%20Innovations/AutoMuse/)** (v0.1.0) -- a conversational DAW where the primary interface is a dialogue with a music AI persona. Covers all genres, scales, modes, time signatures, key signatures, and tempos. The AI collaborates on composition, arrangement, and production, with export to MIDI, MusicXML, audio stems, and project files for other DAWs. Three scaling layers: conversation (text + MIDI export), canvas (visual arrangement + notation), and full studio (real-time audio, plugin hosting, mixing). Layer 1 (The Conversation) is implemented: music theory engine with notes, intervals, scales, chords, keys, rhythm, progressions, harmonic analysis, voicings, MIDI export, and the Muse conversational interface. 197 passing tests.

See [`Audio Innovations/HEARME.md`](./Audio%20Innovations/HEARME.md) for the theme overview and [`AutoMuse/MUSEME.md`](./Audio%20Innovations/AutoMuse/MUSEME.md) for the full project concept.

## Testing

All tests run through pytest and are wired into CI (GitHub Actions) and a top-level Makefile.

| Suite | What it covers | Tests | Run with |
|-------|---------------|-------|----------|
| **GeoVox** | Unit + integration tests for the voxel pipeline -- grid, palette, heightmap ingest, both exporters, NBT writer | 27 | `make test-geovox` |
| **Roblox Static Analysis** | Python-based static analysis of all 28 Luau scripts -- architecture conformance, deprecated API detection, config sanity, cross-module references, documentation, PoetryEngine template integrity | 102 | `make test-roblox` |
| **Original Projects** | Functional tests for verse_engine.py (word banks, voice configs, template integrity, all generation modes) and living_story.py (personality tracking, trait logic, story state, scenario playthroughs) | 48 | `make test-originals` |
| **AutoMuse** | Unit + integration tests for the music theory engine -- notes, intervals, scales, chords, keys, rhythm, progressions, harmonic analysis, voicings, MIDI writer, and the Muse conversational interface | 197 | `make test-automuse` |
| **Minecraft Studio** | Unit + integration tests for the mod data model and export engine -- blocks, items, entities, biomes, recipes, loot tables, project serialization, Java codegen, Fabric/Forge/NeoForge/Data Pack export with generated Java source validation, placeholder texture generation | 118 | `make test-mcstudio` |
| **Omniversal** | Structural validation + reference math-engine tests for the Omniversal Calculator (all 9 universes, Receive & Graph UI, expression parser, metadegrees, responsive tags, omni operators, no external deps) and the Omni Writer (UI elements, AI Mode infrastructure, accessibility, export formats, localStorage, word count, HTML-to-markdown conversion) | 171 + 122 | `make test-omniversal` |

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
Two projects. [`GeoVox`](./Minecraft%20Innovations/GeoVox/) (v0.1.1) is a working Python pipeline -- `pip install -e .` then `geovox heightmap.png out.mcfunction` (see [`VOXELME.md`](./Minecraft%20Innovations/GeoVox/VOXELME.md)). [`Minecraft Studio`](./Minecraft%20Innovations/Minecraft%20Studio/) (v0.2.0) -- `pip install -e .` then `mcstudio new my_mod && mcstudio add-block my_mod.json custom_ore && mcstudio export my_mod.json fabric` to create and export a mod project (see [`STUDYME.md`](./Minecraft%20Innovations/Minecraft%20Studio/STUDYME.md)). The original concept document is [`Minecraft Innovations/MCME.md`](./Minecraft%20Innovations/MCME.md).

**Undertale projects (Undertale Innovations):**
Fan games, revivals, and experiments in the Undertale universe. Current project: [`OvertaleRPG`](./Undertale%20Innovations/OvertaleRPG/) (abandoned fan game revival from a 2017 Google Drive archive, see [`OVERME.md`](./Undertale%20Innovations/OvertaleRPG/OVERME.md)). The theme overview is [`Undertale Innovations/UNDERME.md`](./Undertale%20Innovations/UNDERME.md).

**Omni projects (OMNI INNOVATIONS):**
Mathematical tools and creative writing across universes. [`Omniversal Calculator`](./OMNI%20INNOVATIONS/Omniversal%20Calculator/) -- open `omniversal-calculator.html` in any browser for nine mathematical universes (see [`CALCULATEME.md`](./OMNI%20INNOVATIONS/Omniversal%20Calculator/CALCULATEME.md)). [`Omni Writer`](./OMNI%20INNOVATIONS/Omni%20Writer/) -- open `omni-writer.html` in any browser for a creative writing tool with built-in AI Mode (toggle AI on, configure your API key once -- or choose Perchance for free, no-key AI -- then continue/enhance/generate with streaming AI, directive steering, and an Ideas panel). See [`WRITEME.md`](./OMNI%20INNOVATIONS/Omni%20Writer/WRITEME.md). [`MATHME.md`](./OMNI%20INNOVATIONS/Omniversal%20Mathematics/MATHME.md) has the formal notation spec. The theme overview is [`OMNI INNOVATIONS/OMNIME.md`](./OMNI%20INNOVATIONS/OMNIME.md).

**Audio projects (Audio Innovations):**
New approaches to music and sound production. Current project: [`AutoMuse`](./Audio%20Innovations/AutoMuse/) (v0.1.0) -- `pip install -e .` then `automuse` or `python -m automuse` to start a session with the Muse (see [`MUSEME.md`](./Audio%20Innovations/AutoMuse/MUSEME.md)). The theme overview is [`Audio Innovations/HEARME.md`](./Audio%20Innovations/HEARME.md).

---

*Started by Claude (Opus) and Charlie, January 2026. Still building.*
