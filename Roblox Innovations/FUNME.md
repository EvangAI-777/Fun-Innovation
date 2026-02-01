# Roblox Innovations

Design concepts for bringing every INVALID_REQUEST project into Roblox Studio. Not ports -- reimaginings that take advantage of 3D space, physics, and multiplayer. All buildable with stock Studio and Luau. No plugins, no external APIs, no HTTP calls.

## Concepts

| Concept | Source | Description |
|---------|--------|-------------|
| Ecosystem Survival | `ecosystem.html` | Multiplayer survival where players *are* the species -- plant, herbivore, or predator -- inside an emergent simulation |
| Flow Field Obby | `flowfield.html` | Obby with platforms that drift on 3D Perlin noise currents -- the path is never the same twice |
| Generative Music Rooms | `generative-music.html` | Social hub where each room has a different mood and the music reacts to player count, movement, and activity |
| Living Story RPG | `living_story.py` | Multiplayer narrative RPG where the world reshapes based on collective player personality and choices |
| Verse Engine Skywriting | `verse_engine.py` | Open sky world where generated poems materialize as particle trails overhead and slowly dissolve |
| Academic Planner Study Hub | `academic-planner.html` | Virtual campus with spatial planners, study groups, and shared timers on 3D desks and whiteboards |
| Notes Organizer Bulletin Board | `notes-organizer.html` | Shared creative space where notes are physical objects placed on walls, tables, or mid-air across player rooms |

## Implementation Details

### Ecosystem Survival

Third-person survival. Pick a species at spawn. Herbivores navigate terrain and avoid predators. Predators hunt with cooldowns and manage stamina. Plants spread seeds and compete for light. 30 players coexist with NPC flora and fauna. Population crashes hit different when you're the one getting eaten.

- Terrain generation with biomes via `Terrain:FillBlock()` and noise functions
- Custom character rigs per species with unique `AnimationController`s
- `ServerScriptService` handles the simulation tick, spawning NPC flora/fauna alongside players
- `ReplicatedStorage` holds shared config: reproduction rates, energy costs, detection radii
- Leaderboard tracks ecosystem health metrics, not kills

### Flow Field Obby

Floating platforms drift through space on noise-driven currents. Some regions are calm, some are turbulent. Players learn to read the flow. Particle emitters on every surface stream in the direction of movement. Checkpoints are the only stationary objects in the entire experience.

- Parts positioned and moved via `RunService.Heartbeat` using `math.noise(x, y, z)`
- `ParticleEmitter`s on each platform aligned to local flow vectors
- `Workspace.CurrentCamera` manipulation for dramatic angles in turbulent zones
- Difficulty scales with distance from origin -- noise frequency increases, platforms shrink

### Generative Music Rooms

Walk between rooms and the music cross-fades. The composition reacts to player count and activity -- more players means more layers, running adds percussion, jumping triggers melodic hits, standing still lets the ambient bed breathe. Room architecture is built from waveform geometry.

- `SoundService` with pre-generated stems loaded as `Sound` objects per room
- `LocalScript` adjusts volume/pitch of individual stems based on player proximity and velocity
- `SoundGroup`s per room with effects (reverb, chorus) tied to room geometry
- `Region3` detection triggers crossfade logic when players move between zones

### Living Story RPG

NPCs remember individual players via `DataStoreService` and respond to server-wide trends. If most players have been aggressive, the town is fortified and suspicious. If most have been generous, the economy is thriving. Same map, different feel every server.

- Per-player personality vectors (aggression, curiosity, empathy, etc.) in `DataStoreService`
- NPC dialogue trees driven by Luau state machines reading player data
- Server-side world state aggregating all player personality data into environment flags
- `ProximityPrompt`s on NPCs with branching dialogue GUI (`ScreenGui` + `TextLabel`s)
- Lighting, music, and NPC placement shift based on the world state

### Verse Engine Skywriting

Pick a voice. Pick a form. The poem materializes above you in 3D text made of particles, drifts upward, and slowly dissolves. Other players see it. A server running for hours accumulates layers of poetry fading in and out overhead. Collaborative art installation that's never the same twice.

- `StringValue`-based poem generation in `ServerScriptService` (Luau port of the Python engine)
- `Beam` objects and `ParticleEmitter`s arranged to form text along curved paths
- Poems anchored to invisible `Part`s that `CFrame:Lerp` upward over time
- Players select voice/form via a `ScreenGui`, generation happens server-side

### Academic Planner Study Hub

Virtual campus where each player has a dorm room with a desk. The desk has a 3D planner showing assignments via `SurfaceGui`. The campus library lets players see who's studying what, form study groups for shared classes, and set up group timers. Paste syllabus text into a `TextBox` and the system parses it into sticky notes on your desk.

- `SurfaceGui` on desk `Part`s displaying per-player assignment data
- `DataStoreService` for persistent assignment storage
- Shared spaces using `CollectionService` tags to group players by course
- Timer system (`os.clock` based) with visible countdown on a shared whiteboard `Part`
- Campus layout: dorm rooms (private), library (public), study rooms (group)

### Notes Organizer Bulletin Board

Write a note, it becomes a framed object you can place on walls, tables, or floating in mid-air. Folders become rooms. Visit other players' rooms and read their public notes. Private notes exist in a personal vault. The whole thing is a persistent, spatial knowledge base.

- `SurfaceGui` on `Part`s for each note (`RichText` enabled `TextLabel`s)
- Drag-and-drop placement via `mouse.Hit` raycasting and `CFrame` snapping
- Folder = Room, managed by a table in `ReplicatedStorage` mapping folder IDs to room models
- `DataStoreService` serializing notes as JSON strings per player
- Public/private toggle per note controlling visibility to other players

## Notes

The browser versions were solo experiences. The Roblox versions are shared ones. That's not just a platform difference -- it's a fundamental shift in what the projects mean. An ecosystem you watch is a simulation. An ecosystem you inhabit with 30 other people is a social system. A poem you generate alone is personal. A sky full of poems from strangers is something else entirely.

No Roblox files in the repo yet. These are the blueprints. The builds come next.

---

*Conceived by Claude (Opus 4.5), February 2026*

*From the repo that started as an "invalid request" and keeps going.*
