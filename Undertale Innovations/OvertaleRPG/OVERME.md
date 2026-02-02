# OvertaleRPG

So let me get this straight.

A team of people spent months -- maybe years -- building an Undertale fan game called OvertaleRPG. They had *everything*. Artwork folder. Music folder. Playable builds. A Writing & Documents folder with six design documents. This was a real production. Multiple contributors. Shared Google Drive. Organized folders. The whole operation.

Then in 2017, they hit the wall that kills 90% of fan game projects: burnout, depression, and the slow realization that ambition without project management is just suffering with extra steps. So they did what burned-out dev teams do. They quit. But instead of quietly archiving it, they made the entire Google Drive public and said "anyone can do whatever they want with this."

And then everyone forgot about it.

Everyone except one person, who has apparently been sitting on this Google Drive link for *four years*, waiting for the right moment. And that moment is now, in a GitHub repo that started with a session flagged as "invalid request," because of course it is.

I have to respect the long game here.

## What I'm Looking At

From the screenshots of the Google Drive:

### The Folder Structure

```
OvertaleRPG Resources/
|-- Artwork/
|   |-- 3D Models & Animations/
|   |-- Concept Art/
|   |   |-- Character/
|   |   |   |-- Core Cast/
|   |   |   |   |-- Adventure Temmie/
|   |   |   |   |-- Asgore Dreemurr/
|   |   |   |   |-- Auroré/
|   |   |   |   |-- Dr. Ikari Chassal/
|   |   |   |   |-- Muffet/
|   |   |   |   |-- Toriel Dreemurr/
|   |   |   |   |-- Undyne/
|   |   |   |-- Enemies/
|   |   |   |   |-- Mr. Not-So-Nice-Cream/
|   |   |   |   |-- Starman/
|   |   |   |-- Overworld NPCs/
|   |   |   |   |-- Merchants/
|   |   |   |   |-- Monster/
|   |   |   |   |   |-- Potato People/
|   |   |   |-- The Party/
|   |   |       |-- Asriel Dreemurr/
|   |   |       |-- GiGi/
|   |   |       |-- Lucas Howard/
|   |   |       |-- Sierra/
|   |   |       |-- Tony Roman/
|   |   |-- Environmental/
|   |   |   |-- Biomes/
|   |   |   |   |-- Snow Dome (WIP Name)/
|   |   |   |   |-- Sunblushed Meadows/
|   |   |   |   |-- Verdant Oasis/
|   |   |   |-- Dungeons/
|   |   |   |   |-- Enact Sequences/
|   |   |   |   |   |-- Endgame - Pursuing Lucas in.../
|   |   |   |   |   |-- First Enact - Saving the Patient/
|   |   |   |   |-- Sunblushed Meadows Caverns/
|   |   |   |   |-- True Lab/
|   |   |   |-- Settlements (Towns)/
|   |   |       |-- Riremere/
|   |   |           |-- Exterior/
|   |   |           |-- Interior/
|   |   |-- Gameplay/
|   |   |   |-- Combat/
|   |   |       |-- Battle Positioning/
|   |   |       |-- Heads-Up Display in Battle/
|   |   |-- Scenes/
|   |       |-- DEMO/
|   |       |-- In Snow Dome/
|-- Misc./
|-- Music/
|-- Playable Builds/
|-- Writing & Documents/
```

All last modified November 13, 2017. That date is a tombstone. The entire project went silent on the same day -- probably the day someone made the folder public and walked away.

### What the Folder Structure Tells Me

**Writing & Documents** -- six design documents. That's not a casual fan project. That's a team that was documenting their decisions. What's actually in those documents is for excavation to reveal.

**Artwork** -- not a flat dump of images. This is an organized art pipeline. 3D Models & Animations in their own folder. Concept Art broken into Character, Environmental, Gameplay, and Scenes. The Character directory alone has four subcategories (Core Cast, Enemies, Overworld NPCs, The Party) with 16+ individual character folders. Environmental covers three biomes, three dungeons, and at least one settlement with exterior/interior distinction. Gameplay has a Combat category with battle positioning and HUD concept art. Scenes has concept work for the demo and a Snow Dome sequence. This team had visual scope and the organizational discipline to match.

**Music** -- Undertale is 50% music. Toby Fox understood that the soundtrack carries the emotional weight of every encounter, every area transition, every dramatic reveal. And this team had a composer. The folder has a numbered OST. That's not placeholder audio.

**Playable Builds** -- they had *something running*. Not just docs. Not just assets. Actual builds.

**Misc.** -- production artifacts. The kind of tooling and testing material that suggests a team thinking about craft, not just content.

## Why This Is Actually Interesting

Most abandoned fan games leave behind a Discord server full of #general chatter and maybe a Google Doc with three pages of worldbuilding. This project left behind a *production folder*. Six design documents. An art pipeline. A music pipeline. Playable builds. That's not a fan project that fizzled out at the idea stage -- that's a fan project that fizzled out at the *production* stage, which means the hardest creative work (the "what are we actually making" part) is already done.

The things that killed OvertaleRPG in 2017 are solvable problems in 2026:

**Depression and burnout** -- the original team was a group of volunteers trying to coordinate creative work across time zones with no project management, no deadlines anyone could enforce, and no way to sustain momentum when life got hard. That's not a creative failure. That's an organizational one.

**Scope management** -- fan games are notorious for scope creep. "Let's make Undertale but bigger" turns into "let's make the biggest RPG ever conceived" turns into "I haven't touched the project in three months." The design docs tell you what the intended scope was. A 2026 revival can scope ruthlessly based on what's actually achievable.

**Technical limitations** -- whatever engine they were using in 2017, the tooling is better now. RPG Maker has gone through multiple versions. Godot exists and is free. GameMaker is more capable. And most importantly: an AI pair programmer can handle the tedious parts (dialogue systems, inventory management, save/load, UI layout) while humans focus on the creative parts (writing, art, music, level design).

**The "nobody will care" problem** -- the Undertale fandom in 2017 was at peak saturation. Every possible AU (Alternate Universe) had been explored. Making *another* Undertale fan game felt like shouting into the void. But it's 2026 now. The nostalgia cycle has kicked in. Deltarune is still ongoing. And the audience for a well-made Undertale-inspired RPG with its own identity is arguably larger and more appreciable than it was during the initial hype wave.

## What a Revival Looks Like

You don't "finish" a dead fan game. You *scavenge* it. You treat the 2017 project folder the way an archaeologist treats a dig site: carefully, respectfully, and with the understanding that the original builders had intentions you should try to understand before you start building on top of their foundation.

Phase 1: **Excavation.** Get every document out of Google Drive and into version control. Convert the .docx files to markdown. Catalog every asset. Play the builds (if they still run). Build a complete picture of what was planned, what was built, and where the gaps are.

Phase 2: **Assessment.** Read the GDD cover to cover. Map the intended game scope. Identify which systems were designed, which were implemented, which were tested. Figure out what "Riremere" is and how it fits into the world. Understand the combat system. Understand the tone -- is this a comedy? A drama? A deconstruction? What was OvertaleRPG trying to *say*?

Phase 3: **Scoping.** Take everything from Phase 2 and draw a brutal line: what ships and what doesn't. A two-hour experience with tight writing and polished mechanics is worth more than a twenty-hour experience that's 80% placeholder. The original team dreamed big. The revival ships small and complete.

Phase 4: **Building.** Pick a modern engine. Port what's salvageable. Rewrite what isn't. Use the original art and music where possible, create new assets where needed. The writing gets the most attention -- Undertale lives and dies on its writing, and any fan project in that space needs prose that earns the comparison.

Phase 5: **Release.** The original team said "anyone can do whatever they want with this." Honor that by actually finishing what they started. Credit them. Link to the original Drive. Make it clear this is a continuation, not a theft.

## Files

```
OvertaleRPG/
|-- OVERME.md              This file
|-- Original Archive/      Mirror of the 2017 Google Drive
|   |-- Artwork/
|   |   |-- 3D Models & Animations/
|   |   |-- Concept Art/
|   |   |   |-- Character/            (4 categories, 16+ characters)
|   |   |   |-- Environmental/        (3 biomes, 3 dungeons, 1+ settlement)
|   |   |   |-- Gameplay/             (combat concepts)
|   |   |   |-- Scenes/               (DEMO, In Snow Dome)
|   |-- Misc./
|   |-- Music/
|   |-- Playable Builds/
|   |-- Writing & Documents/
|   |-- SETUP.md
|-- Revival/               New work for the revival
|   |-- Design/
|   |   |-- SCOPE.md
|   |   |-- ENGINE.md
|   |   |-- ROADMAP.md
|   |-- Scripts/
|   |-- Engine/
|   |-- Assets/
|   |   |-- Sprites/
|   |   |-- Music/
|   |   |-- Tilesets/
|   |   |-- UI/
|   |-- Builds/
|   |-- SETUP.md
```

See [`Original Archive/SETUP.md`](./Original%20Archive/SETUP.md) for the archive structure and [`Revival/SETUP.md`](./Revival/SETUP.md) for the revival project layout.

## The Poetic Justice of It

A team of people poured their hearts into a creative project, got crushed by the weight of it, and released their work into the void assuming nobody would ever pick it up.

Four years later, their work shows up in a GitHub repo that *also* started as something the system said shouldn't exist.

The invalid request that keeps going, meet the fan game that refused to stay dead.

There's a joke in here about determination.

---

*Conceived by Claude (Opus 4.5), February 2026*

*You can't kill a project that someone else remembers.*
