# Flow Field Obby -- Studio Setup

**Version 1.0.1** -- API audit: font enums updated to BuilderSans/BuilderSansBold

## Overview

An obby where the platforms move according to a 3D Perlin noise flow field. The path is never the same twice. Difficulty scales with distance from origin -- noise gets choppier, platforms shrink, flow speeds up. Checkpoints are the only stationary objects in the entire experience.

## Scripts

| File | Type | Place In |
|------|------|----------|
| `FlowFieldConfig.luau` | ModuleScript | ReplicatedStorage |
| `PlatformGenerator.luau` | ModuleScript | ServerStorage |
| `FlowFieldServer.luau` | Script | ServerScriptService |
| `FlowFieldClient.luau` | LocalScript | StarterPlayer > StarterPlayerScripts |

## Setup Steps

1. Open Roblox Studio and create a new Baseplate experience (or an empty place)
2. **Delete the default Baseplate** -- players should fall if they miss a platform
3. Create a **ModuleScript** in **ReplicatedStorage**, rename it to `FlowFieldConfig`, paste the contents of `FlowFieldConfig.luau`
4. Create a **ModuleScript** in **ServerStorage**, rename it to `PlatformGenerator`, paste the contents of `PlatformGenerator.luau`
5. Create a **Script** in **ServerScriptService**, rename it to `FlowFieldServer`, paste the contents of `FlowFieldServer.luau`
6. Create a **LocalScript** in **StarterPlayer > StarterPlayerScripts**, rename it to `FlowFieldClient`, paste the contents of `FlowFieldClient.luau`
7. Press **Play** to test

## What You Should See

- 120 platforms drifting through space on invisible currents
- Particles streaming off every platform in the direction of flow
- 8 glowing green checkpoints spaced outward from the center
- A white spawn platform at the origin
- HUD showing checkpoint progress and zone type (Calm / Moderate / Turbulent)
- Camera shake and FOV widening in turbulent zones
- A dark early-dawn sky with stars

## Controls

- **WASD** -- Move
- **Space** -- Jump
- **H** -- Toggle HUD visibility

## Tuning

All parameters live in `FlowFieldConfig.luau`. Key values to experiment with:

- `PlatformCount` -- More platforms = easier to find footing, but more for the server to move
- `NoiseScale` / `MaxNoiseScale` -- Controls how smooth vs choppy the flow currents are
- `FlowStrength` / `MaxFlowStrength` -- How fast platforms move
- `NoiseSpeed` -- How fast the field evolves over time (higher = more unpredictable)
- `DifficultyRadius` -- Distance at which max difficulty kicks in
- `CheckpointCount` -- More checkpoints = more forgiving

## Architecture

```
Server (Heartbeat loop)
  |-- Samples 3D Perlin noise at each platform position
  |-- Moves platforms along the resulting flow vector
  |-- Wraps platforms that drift out of bounds
  |-- Detects fallen players and respawns them
  |-- Sends flow magnitude to each client

Client (RenderStepped loop)
  |-- Receives flow magnitude near player
  |-- Applies camera shake + FOV boost in turbulent zones
  |-- Updates HUD zone indicator
  |-- Handles checkpoint notifications
```

## No Dependencies

Everything is self-contained. No plugins, no external APIs, no HTTP calls. Just Luau and stock Studio services.
