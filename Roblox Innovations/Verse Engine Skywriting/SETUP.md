# Verse Engine Skywriting -- Studio Setup

**Version 1.0.3** -- Critical fix: `enforceMaxPoems()` infinite loop replaced with bounded iteration, `tick()` replaced with `os.clock()`

## Overview

An open sky world where players generate poems that materialize as glowing 3D text overhead. Pick a voice (melancholic, hopeful, surreal, observational, fierce). Pick a form (poem, haiku, couplet, fragment). The poem appears above you in your voice's color, drifts upward, and slowly dissolves. Other players see every poem. A server running for hours accumulates layers of poetry fading in and out across the sky.

## Scripts

| File | Type | Place In |
|------|------|----------|
| `VerseConfig.luau` | ModuleScript | ReplicatedStorage |
| `PoetryEngine.luau` | ModuleScript | ReplicatedStorage |
| `SkywritingServer.luau` | Script | ServerScriptService |
| `SkywritingClient.luau` | LocalScript | StarterPlayer > StarterPlayerScripts |

## Setup Steps

1. Open Roblox Studio and create a new Baseplate experience (or an empty place)
2. **Delete the default Baseplate** -- the server script creates its own dark ground plane
3. Create a **ModuleScript** in **ReplicatedStorage**, rename it to `VerseConfig`, paste the contents of `VerseConfig.luau`
4. Create a **ModuleScript** in **ReplicatedStorage**, rename it to `PoetryEngine`, paste the contents of `PoetryEngine.luau`
5. Create a **Script** in **ServerScriptService**, rename it to `SkywritingServer`, paste the contents of `SkywritingServer.luau`
6. Create a **LocalScript** in **StarterPlayer > StarterPlayerScripts**, rename it to `SkywritingClient`, paste the contents of `SkywritingClient.luau`
7. Press **Play** to test

## What You Should See

- A dark ground plane under a deep night sky with 5000 stars
- A generator panel in the bottom left with five voice buttons and four form buttons
- Click "Write to the Sky" and glowing text appears above your character
- Text drifts upward with particle trails in the voice's color
- A feed in the top right shows who wrote what (visible to all players)
- Poems fade in over 1.5 seconds, hold for 18 seconds, then dissolve over 8 seconds
- Text is readable from both sides (front and back SurfaceGui)

## Controls

- **Voice buttons** -- Select which poetic voice to use
- **Form buttons** -- Select poem, haiku, couplet, or fragment
- **Write to the Sky** -- Generate and display a poem (5-second cooldown)
- **F2** -- Toggle screenshot mode (hides all UI including core GUI)

## Voice Colors

| Voice | Color | Personality |
|-------|-------|-------------|
| Melancholic | Blue | Loss, memory, weight |
| Hopeful | Gold | Growth, light, opening |
| Surreal | Purple | Strange, shifting, dreamlike |
| Observational | Green | Quiet, still, noticing |
| Fierce | Red | Sharp, urgent, alive |

## The Poetry Engine

The poem generation is a faithful Luau port of the original `verse_engine.py`. It uses:

- **5 word bank categories**: nature, time, emotion, body, abstract (each with nouns, verbs, adjectives)
- **5 template types**: simple, medium, complex, question, statement
- **5 voices**: each with preferred concepts, template types, word biases, and rhythm settings
- **4 forms**: full poem (3-10 lines), haiku (5-7-5), couplet (2 lines), fragment (1 line)

Voices bias toward specific words (e.g., melancholic prefers "fades", "aches", "lost") and the engine tracks used words to reduce repetition within a single poem.

## Tuning

All parameters live in `VerseConfig.luau`. Key values:

- `TextHeight` -- How high above the player poems appear
- `DriftSpeed` -- How fast poems float upward
- `HoldDuration` -- How long poems stay at full visibility
- `FadeOutDuration` -- How long the dissolve takes
- `MaxActivePoems` -- Server-wide cap (oldest dissolve early if exceeded)
- `GenerationCooldown` -- Seconds between generations per player

## Architecture

```
Client (SkywritingClient)
  |-- Voice/form selection GUI
  |-- Fires RequestPoem to server on button click
  |-- Receives PoemCreated for the notification feed
  |-- Screenshot mode (F2)

Server (SkywritingServer)
  |-- Receives RequestPoem, validates, checks cooldown
  |-- Calls PoetryEngine.generate() for poem text
  |-- Creates 3D Parts with SurfaceGui TextLabels above the player
  |-- Heartbeat loop: drifts poems upward, manages fade lifecycle
  |-- Fires PoemCreated to all clients

Shared (PoetryEngine)
  |-- Word banks, templates, voice configs
  |-- generate(form, voice) returns { lines, voice }
```

## No Dependencies

Everything is self-contained. The poetry engine is pure Luau string manipulation -- no HTTP calls, no external word lists, no plugins.
