# Roblox Innovations

Design concepts for bringing every INVALID_REQUEST project into Roblox Studio. Not ports -- reimaginings that take advantage of 3D space, physics, and multiplayer. All buildable with stock Studio and Luau. No plugins, no external APIs, no outbound HTTP requests. (Two projects use `HttpService` internally for JSON serialization -- no network calls are made.)

Each concept has its own subdirectory for Roblox Studio files as development progresses.

## What Belongs Here

Anything that reimagines a creative concept for Roblox's 3D multiplayer environment:

- **Reimaginings** -- taking an existing project (from this repo or elsewhere) and redesigning it for 3D space, physics, and real-time multiplayer
- **Original experiences** -- new Roblox projects built with the same philosophy: stock Studio, pure Luau, no plugins, no external dependencies
- **Multiplayer experiments** -- projects that explore what happens when a solo experience becomes shared (social dynamics, emergent behavior, collaborative creation)
- **Educational experiences** -- virtual campuses, interactive simulations, study tools that take advantage of spatial interaction
- **Art installations** -- generative visuals, spatial audio, interactive poetry, anything that treats Roblox as a medium for creative expression rather than just a game platform

The constraint is simple: everything must be buildable with stock Roblox Studio and Luau. No plugins. No external APIs. No outbound HTTP requests. If it can't run on a fresh Studio install, it doesn't belong.

## What Doesn't Belong Here

Plugin-dependent projects. Experiences that require external services or API keys. Anything that makes network calls to third-party servers. The point is that every project here is self-contained within the Roblox ecosystem -- a teacher or student can open Studio, follow the SETUP.md, and have a working experience without installing anything else.

## Concepts

| Concept | Directory | Source | Version | Status |
|---------|-----------|--------|---------|--------|
| Flow Field Obby | `Flow Field Obby/` | `flowfield.html` | 1.0.3 | Built |
| Verse Engine Skywriting | `Verse Engine Skywriting/` | `verse_engine.py` | 1.0.3 | Built |
| Ecosystem Survival | `Ecosystem Survival/` | `ecosystem.html` | 1.0.3 | Built |
| Generative Music Rooms | `Generative Music Rooms/` | `generative-music.html` | 1.0.3 | Built |
| Living Story RPG | `Living Story RPG/` | `living_story.py` | 1.0.3 | Built |
| Academic Planner Study Hub | `Academic Planner Study Hub/` | `academic-planner.html` | 1.0.3 | Built |
| Notes Organizer Bulletin Board | `Notes Organizer Bulletin Board/` | `notes-organizer.html` | 1.0.3 | Built |

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

### Code changes (1.0.1 -- 1.0.2)

- **Font enum update** -- `Enum.Font.Gotham` and `Enum.Font.GothamBold` replaced with `Enum.Font.BuilderSans` and `Enum.Font.BuilderSansBold` across 13 files. The old names still work (Roblox aliases them) but the canonical names are now BuilderSans/BuilderSansBold.
- **Service access pattern** -- Two files used `game.ReplicatedStorage` direct property access instead of `game:GetService("ReplicatedStorage")`. Corrected to the canonical `:GetService()` pattern.
- **Unused import removed** -- `StoryServer.luau` imported `HttpService` but never used it. Removed.

### Code changes (1.0.3 -- full code audit)

Critical fixes:
- **Verse Engine infinite loop** -- `enforceMaxPoems()` used a `while` loop that never reduced `#activePoems`, freezing the server when the poem cap was reached. Replaced with a bounded `for` loop over excess poems.
- **Notes Organizer room overlap** -- All players' rooms were placed at identical grid positions. Added per-player slot offsets so each player's rooms occupy unique world space.
- **Notes Organizer pending folder ID** -- Client folder entries were stuck with ID `"pending"` forever. Now resolved when the server's `folderCreated` event arrives with the real ID.

Bug fixes:
- **Music Rooms `sound.Playing`** -- `sound.Playing` is not a valid Roblox Sound property. Changed to `sound.IsPlaying` so room crossfading doesn't restart already-playing sounds.
- **Living Story RPG `choiceCount`** -- `choiceCount` was incremented inside the trait loop, counting once per trait instead of once per choice. Moved outside the loop.
- **Flow Field camera shake** -- Camera shake was invisible because `RenderStepped:Connect` runs before the default camera controller overwrites the CFrame. Changed to `BindToRenderStep` at `Camera.Value + 1` priority.
- **Music Rooms per-room BPM** -- All rooms pulsed at hardcoded 120 BPM regardless of their configured tempo. Beat events now fire per-room using each room's own BPM (64, 72, 80, 100, 120, 140).

Hardening:
- **Deprecated `tick()` removal** -- All `tick()` calls across 5 files replaced with `os.clock()`. `tick()` is deprecated and returns an epoch timestamp (unsuitable for relative timing); `os.clock()` returns a high-resolution monotonic value.
- **DataStore error logging** -- Silent `pcall` wrappers around `SetAsync` and `GetAsync` in Academic Planner, Living Story RPG, and Notes Organizer now capture and `warn()` errors instead of discarding them.
- **Notes Organizer input validation** -- Added `type()` checks on position/normal number values from the client to prevent data corruption.
- **Living Story RPG global leak** -- `closeDialogue` was accidentally global. Forward-declared as `local` with assignment after `showChoices` definition.
- **Living Story RPG dead import** -- Unused `RunService` import removed.

### Claim verification results

| Claim | Result | Notes |
|-------|--------|-------|
| No outbound HTTP requests | Verified | `HttpService` is used in Academic Planner and Notes Organizer for `JSONEncode`/`JSONDecode` only (DataStore serialization). No `GetAsync`, `PostAsync`, or network calls anywhere. |
| No plugins | Verified | Zero plugin references across all 28 files |
| No external APIs | Verified | All `require()` calls reference internal modules via `ReplicatedStorage` or `ServerStorage` |
| No external assets | Verified | Only placeholder empty strings in `MusicConfig.SoundAssets` |
| DataStore usage accurate | Verified | Flow Field Obby, Verse Engine, Ecosystem, and Music Rooms use no DataStore. Academic Planner, Notes Organizer, and Living Story RPG use DataStore as documented. |
| Script types match SETUP.md | Verified | All 7 projects: 2 ModuleScript + 1 Script + 1 LocalScript, placed as documented |
| No deprecated APIs | Verified (1.0.3) | `task.*` used throughout, no legacy `spawn`/`wait`/`delay`, no `FindPartOnRay`, no `Instance.new` with parent arg. `Velocity` replaced with `AssemblyLinearVelocity` in v1.0.2. All `tick()` calls replaced with `os.clock()` in v1.0.3. |

### Versioning

All projects now carry semantic version numbers in their SETUP.md files:

- **1.0.0** -- Initial build
- **1.0.1** -- API audit: font enums, service access, unused import, claim verification
- **1.0.2** -- Code verification: bug fixes, deprecated API replacement, missing feature implementation (4 projects patched)
- **1.0.3** -- Full code audit: 3 critical fixes, 4 bug fixes, `tick()` removal, DataStore error logging, input validation, dead code cleanup

## Adding a Project

1. Create a subdirectory with a clear project name
2. Add a `SETUP.md` with Studio setup instructions (script placement, service locations, configuration)
3. Add a row to the Concepts table above
4. Add a markdown file if the project needs a deeper overview (follow the `*ME.md` naming pattern)
5. Update this file's Implementation Details section
6. Update the root `README.md` with a bullet point under the Roblox Innovations section

Every project should include a SETUP.md that takes someone from a blank Studio place to a running experience in under 10 minutes. If the setup requires more than that, the project needs simplifying.

## The Roblox Standard

Roblox Studio is a creative tool that 70 million people have access to. Projects in this folder should honor that accessibility. No gatekeeping through complexity. No assuming the reader knows Luau internals. Write clear SETUP.md files, comment code where the logic isn't obvious, and always test on a fresh place to make sure the instructions actually work.

The deeper standard: every project here should justify being in 3D multiplayer. If it works just as well as a flat webpage, it shouldn't be a Roblox experience. The question is always "what does spatial, shared, physics-driven interaction add to this concept?"

## Notes

The browser versions were solo experiences. The Roblox versions are shared ones. That's not just a platform difference -- it's a fundamental shift in what the projects mean. An ecosystem you watch is a simulation. An ecosystem you inhabit with 30 other people is a social system. A poem you generate alone is personal. A sky full of poems from strangers is something else entirely.

All seven projects are built and ready to drop into Studio. Every concept that started as a browser demo or terminal script has been reimagined for 3D multiplayer. The builds are complete.

---

*Conceived by Claude (Opus 4.5), February 2026*

*From the repo that started as an "invalid request" and keeps going.*
