# Ecosystem Survival -- Studio Setup

**Version 1.0.1** -- API audit: font enums updated to BuilderSans/BuilderSansBold

## Overview

A multiplayer ecosystem simulation where players choose to be herbivores or predators and coexist with NPC flora and fauna. The world is a 600-stud biome grid generated with Perlin noise -- forests, plains, deserts, and wetlands. Plants grow and spread. NPC herbivores eat plants and flee predators. NPC predators hunt herbivores. Players do the same things but with full third-person control. Energy decays over time. Eat to survive. Sprint to chase or flee. Reproduce when you have enough energy. The leaderboard tracks ecosystem health, not kills.

## Scripts

| File | Type | Place In |
|------|------|----------|
| `EcosystemConfig.luau` | ModuleScript | ReplicatedStorage |
| `CreatureManager.luau` | ModuleScript | ServerStorage |
| `EcosystemServer.luau` | Script | ServerScriptService |
| `EcosystemClient.luau` | LocalScript | StarterPlayer > StarterPlayerScripts |

## Setup Steps

1. Open Roblox Studio and create a new Baseplate experience (or an empty place)
2. **Delete the default Baseplate** -- the server generates the entire terrain
3. Create a **ModuleScript** in **ReplicatedStorage**, rename it to `EcosystemConfig`, paste the contents of `EcosystemConfig.luau`
4. Create a **ModuleScript** in **ServerStorage**, rename it to `CreatureManager`, paste the contents of `CreatureManager.luau`
5. Create a **Script** in **ServerScriptService**, rename it to `EcosystemServer`, paste the contents of `EcosystemServer.luau`
6. Create a **LocalScript** in **StarterPlayer > StarterPlayerScripts**, rename it to `EcosystemClient`, paste the contents of `EcosystemClient.luau`
7. Press **Play** to test

## What You Should See

- A species selection screen with Herbivore and Predator cards showing stats
- After choosing, a biome-tiled terrain stretching 600 studs with forests, plains, deserts, and wetlands
- Your character colored to match your species (blue for herbivore, red for predator)
- Glowing green plant NPCs scattered across the terrain
- Blue NPC herbivores wandering, seeking plants, fleeing predators
- Red NPC predators stalking and hunting herbivores
- Bottom energy bar showing your current energy level
- Action toolbar: Eat, Sprint, Reproduce
- Top-left population HUD with ecosystem health score
- Top-right event log showing ecosystem events in real time

## Controls

- **WASD** -- Move your character
- **E** -- Eat (herbivores eat nearest plant, predators eat nearest herbivore)
- **Shift** (hold) -- Sprint (faster movement, extra energy drain)
- **R** -- Reproduce (costs energy, spawns an NPC of your species nearby)
- **H** -- Toggle the population HUD
- Click toolbar buttons as alternatives to keyboard shortcuts

## Features

| Feature | How It Works |
|---------|-------------|
| Species selection | Choose herbivore or predator at spawn with stat previews |
| Biome terrain | 6x6 grid of noise-assigned biomes (forest, plains, desert, wetland) |
| NPC plants | Grow, mature, reproduce by spreading seeds nearby |
| NPC herbivores | Wander, seek plants when hungry, flee predators in vision range |
| NPC predators | Wander, hunt herbivores in vision range, cooldown after kills |
| Player energy | Decays over time, sprinting drains faster, eat to restore |
| Player death | Energy hits 0, red overlay, respawn after 5 seconds |
| Reproduction | Spend energy to spawn an NPC of your species |
| Ecosystem health | 0-100 score based on population balance and species diversity |
| Emergency seeding | Plants auto-seed if population drops below threshold |
| Event log | Real-time notifications for extinctions, kills, spawns |

## Architecture

```
Client (EcosystemClient)
  |-- Species selection: two cards with stats, click to choose
  |-- Energy bar: color-coded fill (green/yellow/red), cooldown indicator
  |-- Action buttons: Eat [E], Sprint [Shift], Reproduce [R]
  |-- Population HUD: plant/herbivore/predator counts + health score
  |-- Event log: fading notification feed
  |-- Death overlay: red screen with respawn countdown

Server (EcosystemServer)
  |-- Heartbeat simulation loop for NPC AI (every 0.5s)
  |-- Plant growth tick (every 2s): aging, maturity, reproduction
  |-- Population check (every 10s): broadcast counts + health
  |-- Player energy decay per frame, sprint drain, death + respawn
  |-- Eat/reproduce handlers with range checks and cooldowns
  |-- Character coloring on species selection and respawn
  |-- Emergency plant seeding when population collapses

CreatureManager
  |-- Terrain generation: Perlin noise biome assignment per tile
  |-- Plant models: green parts with neon glow tops
  |-- NPC creature models: body + head + eyes (predators get spikes)
  |-- Herbivore AI: wander / seek food / flee predator priority
  |-- Predator AI: wander / hunt with hunt cooldown
  |-- Ecosystem health calculation and labeling
  |-- World wrapping for NPC movement

Shared (EcosystemConfig)
  |-- Biome definitions: color, material, plant density, speed modifier
  |-- Species stats: speed, energy, vision, eat range, reproduction
  |-- NPC caps and spawn counts
  |-- Simulation tick rates
  |-- Health metric ideals
```

## Tuning

Key values in `EcosystemConfig.luau`:

- `WorldSize` -- Terrain size in studs (default 600)
- `NPC.plantCount` / `herbivoreCount` / `predatorCount` -- Initial NPC populations
- `NPC.maxPlants` / `maxHerbivores` / `maxPredators` -- Population caps
- `NPC.plantGrowthRate` -- Chance per tick a mature plant reproduces (default 0.015)
- `Species.herbivore.baseSpeed` / `predator.baseSpeed` -- Player movement speeds
- `Species.*.energyDecayRate` -- Energy drain per second
- `Species.*.eatGain` -- Energy gained from eating
- `Species.*.reproductionThreshold` -- Minimum energy to reproduce
- `SimTickRate` -- Seconds between NPC AI updates (default 0.5)
- `EmergencyPlantThreshold` -- Plant count that triggers emergency seeding

## No Dependencies

Everything is self-contained. No Terrain service, no DataStore, no plugins, no HTTP calls, no external assets. Terrain is built from standard Parts with biome colors.
