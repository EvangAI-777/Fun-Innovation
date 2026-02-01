# Living Story RPG -- Studio Setup

**Version 1.0.1** -- API audit: font enums updated to BuilderSans/BuilderSansBold, service access normalized to GetService, unused HttpService import removed

A persistent multiplayer town where NPCs remember you. Your choices accumulate into a personality tracked across sessions via DataStore. The town's mood — its lighting, atmosphere, and NPC greetings — shifts based on the collective personality of everyone who visits. Same map, different feel every server.

Seven NPCs, each with branching dialogue trees. The Keeper at the gate, the Guide at the crossroads, the Wounded Stranger by the wall, the Merchant in the market, the Scholar in the library, the Guardian at the tower, and the Voice inside. Every conversation adjusts your personality traits and stores memories. When you reach the Voice, it knows who you've been.

## Architecture

```
StoryConfig.luau        (ModuleScript → ReplicatedStorage)
  Personality traits, NPC definitions, dialogue trees, world moods, town layout

DialogueManager.luau    (ModuleScript → ServerStorage)
  Town geometry builder, NPC model builder, dialogue tree traversal, template injection

StoryServer.luau        (Script → ServerScriptService)
  DataStore persistence, world mood computation, dialogue processing, NPC memory

StoryClient.luau        (LocalScript → StarterPlayerScripts)
  Dialogue GUI with typewriter effect, personality HUD, ProximityPrompt handling
```

## Setup Steps

1. **Open** a new Roblox Studio baseplate (or empty place)

2. **Delete** the default baseplate part — the town generates its own ground

3. **Create the module scripts:**
   - In **ReplicatedStorage**, create a **ModuleScript** named `StoryConfig`
   - Paste the contents of `StoryConfig.luau`
   - In **ServerStorage**, create a **ModuleScript** named `DialogueManager`
   - Paste the contents of `DialogueManager.luau`

4. **Create the server script:**
   - In **ServerScriptService**, create a **Script** named `StoryServer`
   - Paste the contents of `StoryServer.luau`

5. **Create the client script:**
   - In **StarterPlayer → StarterPlayerScripts**, create a **LocalScript** named `StoryClient`
   - Paste the contents of `StoryClient.luau`

6. **Enable API Services:**
   - Game Settings → Security → Enable **Studio Access to API Services** (for DataStore)

7. **Press Play** to test

## What You'll See

- A **town** with stone paths, a central fountain, buildings, and seven NPCs
- Walk up to any NPC and a **ProximityPrompt** appears — press E to talk
- **Dialogue** appears in a classic RPG text box at the bottom of the screen with typewriter text
- **Choices** appear as numbered buttons — each one modifies your personality
- **Personality HUD** (top-left) shows 7 trait bars updating in real time
- **Town Mood** (top-right) shows the current collective mood

## The NPCs

| NPC | Location | Dialogue Theme |
|-----|----------|---------------|
| The Keeper | Town gate | Why are you here? Tests honesty/curiosity/boldness |
| The Guide | Crossroads | Direction and instinct — which path do you take? |
| The Wounded Stranger | Shelter wall | Empathy test — help, observe, ignore, or confront |
| The Merchant | Market stall | Trust and shrewdness — honest trade or deceptive barter |
| The Scholar | Library | Curiosity reward — understanding how the world works |
| The Guardian | Tower entrance | Worthiness test — how do you justify yourself? |
| The Voice | Inside the tower | Reflects your personality back — the climactic encounter |

## Personality System

Seven traits, same as the original Python version:

| Trait | Description |
|-------|-------------|
| Curious | Explores, asks questions, investigates |
| Cautious | Hesitates, thinks first, avoids risk |
| Bold | Acts decisively, takes risks, confronts |
| Kind | Helps, empathizes, protects |
| Detached | Observes, stays neutral, holds back |
| Honest | Tells truth, direct, transparent |
| Deceptive | Lies, manipulates, hides |

Every dialogue choice adds points to one or more traits. Your dominant trait determines:
- How NPCs respond to you (return visit dialogue)
- What the Voice says when you reach the tower
- Your ending text and narrative conclusion

## World Mood

The server aggregates all online players' personality data and computes a collective mood:

| Mood | Dominant Trait | Effect |
|------|---------------|--------|
| Welcoming | Kind | Warm sky, bright light, green tones |
| Tense | Bold | Orange sky, dramatic lighting |
| Quiet | Cautious | Dim, muted, whispering atmosphere |
| Suspicious | Deceptive | Fog, shadows, dark ambiance |
| Curious | Curious | Blue-tinged, open, clear |
| Neutral | (none dominant) | Default balanced lighting |

The mood updates every 30 seconds. NPC greetings change with the mood. Lighting, fog, and sky color transition smoothly.

## Persistence

- Personality traits, memories, visited NPCs, and choice count are saved to **DataStoreService**
- Auto-saves every 2 minutes and on player disconnect
- Return visits show different dialogue — NPCs acknowledge they've seen you before
- Your accumulated personality carries across sessions and servers

## Controls

| Key | Action |
|-----|--------|
| E (near NPC) | Start conversation |
| 1-4 | Select dialogue choice |
| Enter / Space / Click | Continue (when no choices) |
| Escape | Close dialogue |
| H | Toggle HUD |

## Configuration

All tuning is in `StoryConfig.luau`:

- **Dialogue trees**: Full branching conversations per NPC with trait effects and memory triggers
- **World moods**: Threshold values, sky/ambient colors, fog distance, brightness
- **Town layout**: Building positions, sizes, materials
- **NPC definitions**: Positions, appearance colors, dialogue keys
- **Timing**: Typewriter speed, line pauses, auto-save interval, world state update rate
- **Template tokens**: `{name}`, `{tendency}`, `{memory_reflection}`, `{ending_*}` for dynamic text

## The Original → The Reimagining

The Python version was a solo terminal experience: linear story, typewriter text, branching choices, one playthrough at a time. The personality died when you closed the terminal.

The Roblox version makes personality persistent and social. Your choices follow you across sessions. Other players' choices shape the world you walk through. The same town feels different depending on who's been there. The NPCs remember everyone individually. The Voice at the end doesn't just reflect you — it reflects everyone.

An interactive fiction that remembers who you are. All of you.

---

*Reimagined from `living_story.py` — from solo text adventure to persistent multiplayer narrative.*
