# Roblox Innovations

Design concepts for bringing every INVALID_REQUEST project into Roblox Studio. Not ports -- reimaginings that take advantage of 3D space, physics, and multiplayer. All buildable with stock Studio and Luau. No plugins, no external APIs, no outbound HTTP requests. (Two projects use `HttpService` internally for JSON serialization -- no network calls are made.)

Each concept has its own subdirectory for Roblox Studio files as development progresses.

## Concepts

| Concept | Directory | Source | Version | Status |
|---------|-----------|--------|---------|--------|
| Flow Field Obby | `Flow Field Obby/` | `flowfield.html` | 1.0.1 | Built |
| Verse Engine Skywriting | `Verse Engine Skywriting/` | `verse_engine.py` | 1.0.2 | Built |
| Ecosystem Survival | `Ecosystem Survival/` | `ecosystem.html` | 1.0.2 | Built |
| Generative Music Rooms | `Generative Music Rooms/` | `generative-music.html` | 1.0.2 | Built |
| Living Story RPG | `Living Story RPG/` | `living_story.py` | 1.0.2 | Built |
| Academic Planner Study Hub | `Academic Planner Study Hub/` | `academic-planner.html` | 1.0.1 | Built |
| Notes Organizer Bulletin Board | `Notes Organizer Bulletin Board/` | `notes-organizer.html` | 1.0.1 | Built |

## Implementation Details

### Ecosystem Survival -- Built

Third-person survival. Pick a species at spawn. Herbivores navigate biome terrain and eat plants while fleeing predators. Predators hunt with cooldowns and manage stamina. NPC plants grow, mature, and spread seeds. Players coexist with NPC flora and fauna in a Perlin-noise biome grid. Energy decays over time -- eat to survive, sprint to chase or flee, reproduce to grow your population. The leaderboard tracks ecosystem health, not kills.

| File | Type | Studio Location |
|------|------|-----------------|
| `EcosystemConfig.luau` | ModuleScript | ReplicatedStorage |
| `CreatureManager.luau` | ModuleScript | ServerStorage |
| `EcosystemServer.luau` | Script | ServerScriptService |
| `EcosystemClient.luau` | LocalScript | StarterPlayerScripts |
| `SETUP.md` | Setup guide | -- |

See [`Ecosystem Survival/SETUP.md`](./Ecosystem%20Survival/SETUP.md) for full setup instructions.

### Flow Field Obby -- Built

Floating platforms drift through space on noise-driven currents. Some regions are calm, some are turbulent. Players learn to read the flow. Particle emitters on every surface stream in the direction of movement. Checkpoints are the only stationary objects in the entire experience.

| File | Type | Studio Location |
|------|------|-----------------|
| `FlowFieldConfig.luau` | ModuleScript | ReplicatedStorage |
| `PlatformGenerator.luau` | ModuleScript | ServerStorage |
| `FlowFieldServer.luau` | Script | ServerScriptService |
| `FlowFieldClient.luau` | LocalScript | StarterPlayerScripts |
| `SETUP.md` | Setup guide | -- |

See [`Flow Field Obby/SETUP.md`](./Flow%20Field%20Obby/SETUP.md) for full setup instructions.

### Generative Music Rooms -- Built

Six mood-themed rooms in a hexagonal ring. Each room's walls are shaped by a different waveform (sine, sawtooth, square, triangle, noise). Floor tiles pulse in ripple patterns synced to a global beat clock. Walk between rooms and the visuals cross-fade. The composition reacts to player count and activity -- more players means more layers, running adds percussion, jumping triggers melodic hits, standing still lets the ambient bed breathe. Fully functional as a visual installation; populate `MusicConfig.SoundAssets` with Creator Store audio IDs for the full audio-reactive experience.

| File | Type | Studio Location |
|------|------|-----------------|
| `MusicConfig.luau` | ModuleScript | ReplicatedStorage |
| `SoundscapeEngine.luau` | ModuleScript | ServerStorage |
| `MusicServer.luau` | Script | ServerScriptService |
| `MusicClient.luau` | LocalScript | StarterPlayerScripts |
| `SETUP.md` | Setup guide | -- |

See [`Generative Music Rooms/SETUP.md`](./Generative%20Music%20Rooms/SETUP.md) for full setup instructions.

### Living Story RPG -- Built

A persistent multiplayer town where NPCs remember individual players via DataStore. Seven NPCs with branching dialogue trees -- the Keeper, the Guide, the Wounded Stranger, the Merchant, the Scholar, the Guardian, and the Voice. Each conversation adjusts seven personality traits (curious, cautious, bold, kind, detached, honest, deceptive) and stores memories. The town's mood -- lighting, fog, sky colour, NPC greetings -- shifts based on the aggregate personality of all online players. The Voice in the tower reflects your accumulated choices back at you with personality-aware endings. Typewriter text effect in the dialogue GUI as a nod to the terminal-based original.

| File | Type | Studio Location |
|------|------|-----------------|
| `StoryConfig.luau` | ModuleScript | ReplicatedStorage |
| `DialogueManager.luau` | ModuleScript | ServerStorage |
| `StoryServer.luau` | Script | ServerScriptService |
| `StoryClient.luau` | LocalScript | StarterPlayerScripts |
| `SETUP.md` | Setup guide | -- |

See [`Living Story RPG/SETUP.md`](./Living%20Story%20RPG/SETUP.md) for full setup instructions.

### Verse Engine Skywriting -- Built

Pick a voice. Pick a form. The poem materializes above you in 3D text made of particles, drifts upward, and slowly dissolves. Other players see it. A server running for hours accumulates layers of poetry fading in and out overhead. Collaborative art installation that's never the same twice.

| File | Type | Studio Location |
|------|------|-----------------|
| `VerseConfig.luau` | ModuleScript | ReplicatedStorage |
| `PoetryEngine.luau` | ModuleScript | ReplicatedStorage |
| `SkywritingServer.luau` | Script | ServerScriptService |
| `SkywritingClient.luau` | LocalScript | StarterPlayerScripts |
| `SETUP.md` | Setup guide | -- |

See [`Verse Engine Skywriting/SETUP.md`](./Verse%20Engine%20Skywriting/SETUP.md) for full setup instructions.

### Academic Planner Study Hub -- Built

Virtual campus where each player has a dorm room with a desk. Assignments appear as color-coded sticky notes on the desk surface -- green for upcoming, yellow for due soon, red for overdue, gray for completed. A shared library displays who's studying what on a central whiteboard. Study rooms have group timers for focused sessions. Paste syllabus text and the system parses it into assignments automatically.

| File | Type | Studio Location |
|------|------|-----------------|
| `PlannerConfig.luau` | ModuleScript | ReplicatedStorage |
| `AssignmentManager.luau` | ModuleScript | ServerStorage |
| `PlannerServer.luau` | Script | ServerScriptService |
| `PlannerClient.luau` | LocalScript | StarterPlayerScripts |
| `SETUP.md` | Setup guide | -- |

See [`Academic Planner Study Hub/SETUP.md`](./Academic%20Planner%20Study%20Hub/SETUP.md) for full setup instructions.

### Notes Organizer Bulletin Board -- Built

Write a note, it becomes a framed object you can place on walls, tables, or floating in mid-air. Folders become rooms. Visit other players' rooms and read their public notes. Private notes appear faded to others. Persistent via DataStore.

| File | Type | Studio Location |
|------|------|-----------------|
| `BulletinConfig.luau` | ModuleScript | ReplicatedStorage |
| `NoteManager.luau` | ModuleScript | ServerStorage |
| `BulletinServer.luau` | Script | ServerScriptService |
| `BulletinClient.luau` | LocalScript | StarterPlayerScripts |
| `SETUP.md` | Setup guide | -- |

See [`Notes Organizer Bulletin Board/SETUP.md`](./Notes%20Organizer%20Bulletin%20Board/SETUP.md) for full setup instructions.

## API Audit and Claim Verification (February 2026)

All 28 Luau files were scanned against the current Roblox Studio API surface and all claims in SETUP.md files were verified against the actual code.

### Code changes

- **Font enum update** -- `Enum.Font.Gotham` and `Enum.Font.GothamBold` replaced with `Enum.Font.BuilderSans` and `Enum.Font.BuilderSansBold` across 13 files. The old names still work (Roblox aliases them) but the canonical names are now BuilderSans/BuilderSansBold.
- **Service access pattern** -- Two files used `game.ReplicatedStorage` direct property access instead of `game:GetService("ReplicatedStorage")`. Corrected to the canonical `:GetService()` pattern.
- **Unused import removed** -- `StoryServer.luau` imported `HttpService` but never used it. Removed.

### Claim verification results

| Claim | Result | Notes |
|-------|--------|-------|
| No outbound HTTP requests | Verified | `HttpService` is used in Academic Planner and Notes Organizer for `JSONEncode`/`JSONDecode` only (DataStore serialization). No `GetAsync`, `PostAsync`, or network calls anywhere. |
| No plugins | Verified | Zero plugin references across all 28 files |
| No external APIs | Verified | All `require()` calls reference internal modules via `ReplicatedStorage` or `ServerStorage` |
| No external assets | Verified | Only placeholder empty strings in `MusicConfig.SoundAssets` |
| DataStore usage accurate | Verified | Flow Field Obby, Verse Engine, Ecosystem, and Music Rooms use no DataStore. Academic Planner, Notes Organizer, and Living Story RPG use DataStore as documented. |
| Script types match SETUP.md | Verified | All 7 projects: 2 ModuleScript + 1 Script + 1 LocalScript, placed as documented |
| No deprecated APIs | Verified (1.0.2) | `task.*` used throughout, no legacy `spawn`/`wait`/`delay`, no `FindPartOnRay`, no `Instance.new` with parent arg. One `Velocity` usage (MusicClient) caught and replaced with `AssemblyLinearVelocity` in v1.0.2. |

### Versioning

All projects now carry semantic version numbers in their SETUP.md files:

- **1.0.0** -- Initial build
- **1.0.1** -- API audit: font enums, service access, unused import, claim verification
- **1.0.2** -- Code verification: bug fixes, deprecated API replacement, missing feature implementation (4 projects patched)

## Notes

The browser versions were solo experiences. The Roblox versions are shared ones. That's not just a platform difference -- it's a fundamental shift in what the projects mean. An ecosystem you watch is a simulation. An ecosystem you inhabit with 30 other people is a social system. A poem you generate alone is personal. A sky full of poems from strangers is something else entirely.

All seven projects are built and ready to drop into Studio. Every concept that started as a browser demo or terminal script has been reimagined for 3D multiplayer. The builds are complete.

---

*Conceived by Claude (Opus 4.5), February 2026*

*From the repo that started as an "invalid request" and keeps going.*
