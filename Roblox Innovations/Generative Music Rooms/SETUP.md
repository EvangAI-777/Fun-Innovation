# Generative Music Rooms -- Studio Setup

**Version 1.0.3** -- Per-room BPM (beat events now fire at each room's configured tempo), `sound.Playing` fixed to `sound.IsPlaying`, `tick()` replaced with `os.clock()`

Six mood-themed rooms arranged in a hexagonal ring around a central lobby. Each room is built from waveform-shaped walls (sine, sawtooth, square, triangle, noise) and a grid of floor tiles that pulse on the beat. Walk between rooms and the music cross-fades. The composition reacts to player count and activity — more players means more layers, running adds percussion, jumping triggers melodic hits, standing still lets the ambient bed breathe.

The visual rhythm system is fully self-contained and works without any audio assets. To add actual sound, populate `MusicConfig.SoundAssets` with Roblox audio asset IDs from the Creator Store.

## Architecture

```
MusicConfig.luau        (ModuleScript → ReplicatedStorage)
  Room definitions, scales, layer thresholds, visual parameters

SoundscapeEngine.luau   (ModuleScript → ServerStorage)
  Waveform math, room geometry builder, beat clock, scale helpers

MusicServer.luau        (Script → ServerScriptService)
  Beat clock, player room tracking, activity detection, layer activation

MusicClient.luau        (LocalScript → StarterPlayerScripts)
  Sound crossfade, visual beat pulses, activity reporting, HUD
```

## Setup Steps

1. **Open** a new Roblox Studio baseplate (or empty place)

2. **Delete** the default baseplate part — the experience generates its own geometry

3. **Create the module scripts:**
   - In **ReplicatedStorage**, create a **ModuleScript** named `MusicConfig`
   - Paste the contents of `MusicConfig.luau`
   - In **ServerStorage**, create a **ModuleScript** named `SoundscapeEngine`
   - Paste the contents of `SoundscapeEngine.luau`

4. **Create the server script:**
   - In **ServerScriptService**, create a **Script** named `MusicServer`
   - Paste the contents of `MusicServer.luau`

5. **Create the client script:**
   - In **StarterPlayer → StarterPlayerScripts**, create a **LocalScript** named `MusicClient`
   - Paste the contents of `MusicClient.luau`

6. **Press Play** to test

## What You'll See

- A central **lobby** with a glowing pedestal and directional signs pointing to each room
- **Six rooms** radiating outward, each with distinct wall shapes and color palettes:
  - **Calm** — gentle sine walls, cool blue, slow pulse
  - **Dreamy** — flowing sine walls with open sky, purple with floating particles
  - **Tense** — jagged sawtooth walls, deep red, fast aggressive pulse
  - **Uplifting** — triangle wave walls with open sky, bright green, energetic
  - **Dark** — blocky square walls, near-black with purple glow, heavy pulse
  - **Chaos** — noise-driven walls with open sky, orange, rapid everything
- **Floor tiles** pulse in ripple patterns on each beat
- **Neon walls** flash to the room's pulse color on every beat
- **Particle emitters** burst on downbeats
- The **HUD** shows current room name, BPM/scale, active layers, player count, and your activity

## How Layers Work

Each room has five sound layers: **bass**, **pad**, **melody**, **arp**, and **percussion**. Layers activate based on:

| Condition | Effect |
|-----------|--------|
| Player count meets threshold | Layer activates (thresholds vary per room) |
| Any player running | Percussion activates regardless of count |
| Any player jumping | Melody activates regardless of count |
| Any player standing still 3+ seconds | Pad activates regardless of count |

The layer panel (bottom-left HUD) shows green dots for active layers in real time.

## Adding Audio

The experience is designed to work as a visual installation by default. To add actual music:

1. **Find loops** on the [Creator Store](https://create.roblox.com/store) (search for "ambient loop", "bass loop", "percussion loop", etc.)
2. **Copy the asset ID** for each sound (format: `rbxassetid://123456789`)
3. **Edit `MusicConfig.luau`** — find the `SoundAssets` table and fill in IDs:
   ```lua
   calm = {
       bass       = "rbxassetid://YOUR_BASS_ID",
       pad        = "rbxassetid://YOUR_PAD_ID",
       melody     = "rbxassetid://YOUR_MELODY_ID",
       arp        = "rbxassetid://YOUR_ARP_ID",
       percussion = "rbxassetid://YOUR_PERCUSSION_ID",
   },
   ```
4. Each room can have completely different sounds — the system handles crossfade and layer mixing automatically

## Controls

| Key | Action |
|-----|--------|
| Walk between rooms | Crossfade to new room's audio + visuals |
| Run (hold Shift) | Activates percussion layer |
| Jump (Space) | Triggers melodic layer |
| Stand still 3+ seconds | Boosts ambient pad layer |
| H | Toggle HUD |

## Configuration

All tuning is in `MusicConfig.luau`:

- **Room layout**: `LobbyRadius`, `RoomSize`, `HallwayWidth`
- **Scales**: 10 musical scales (pentatonic, major, minor, dorian, phrygian, lydian, mixolydian, blues, japanese, arabic)
- **Per-room**: wall style, BPM, root note, layer thresholds, colors, particle rates
- **Activity**: speed thresholds for running/still detection, jump cooldown
- **Visual**: wave resolution, amplitude, floor tile size, pulse duration, crossfade time

## Notes

- No plugins, no external APIs, no HTTP calls — runs on stock Roblox Studio
- The waveform geometry is deterministic: same config always produces the same walls
- Beat clock syncs from server epoch, so all players see the same visual pulses
- Floor tile ripples use a modular pattern `(gridX + gridZ) % beatsPerMeasure` for satisfying wave propagation
- Rooms are spaced 80 studs from center in a hexagonal ring — plenty of room to walk between them
- The Chaos room has all layer thresholds at 1, so even a solo player gets the full experience there

---

*Reimagined from `generative-music.html` — from solo Web Audio synthesis to shared spatial soundscape.*
