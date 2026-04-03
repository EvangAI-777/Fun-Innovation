# OvertaleRPG Revival — Design Documents

Status: **Phase 0 complete. Awaiting archive import before all three sections below can be finalized.**

See [OVERME.md](../../OVERME.md) for the full project context and five-phase revival plan.

---

## Roadmap

### Phase 0: Setup (Complete)
- [x] Create directory structure
- [x] Write OVERME.md with project context
- [x] Create design scaffolding
- [ ] Download OvertaleRPG Google Drive contents into Original Archive

### Phase 1: Excavation
- [ ] Convert all .docx files to markdown
- [ ] Catalog every asset in the Artwork folder (type, dimensions, format, usability)
- [ ] Catalog every track in the Music folder (format, duration, quality, mood)
- [ ] Attempt to run Playable Builds (document what works, what doesn't, what engine)
- [ ] Index the Misc folder
- [ ] Create a master inventory of everything in the archive

### Phase 2: Assessment
- [ ] Read the Game Design Document cover to cover, annotate with revival notes
- [ ] Read the Codex & Lore, identify what's canon for the revival
- [ ] Read Core Game Systems spec, evaluate which systems are worth keeping
- [ ] Read Opening Scene, assess writing quality and tone
- [ ] Map "Riremere" -- understand the location and its role in the world
- [ ] Read the Team Scrapbook for context on design decisions and abandoned ideas
- [ ] Write a one-page summary: "What OvertaleRPG was trying to be"

### Phase 3: Scoping
- [ ] Define the revival scope (see Scope section below)
- [ ] Choose engine (see Engine section below)
- [ ] Define the minimum viable story arc (beginning, middle, end)
- [ ] Cut everything that doesn't fit the scope
- [ ] Create a task list for the build phase

### Phase 4: Building
- [ ] Set up engine project
- [ ] Implement core systems (movement, dialogue, save/load)
- [ ] Port/recreate combat system
- [ ] Write/adapt dialogue scripts
- [ ] Integrate art assets (original or new)
- [ ] Integrate music (original or new)
- [ ] Build the opening sequence
- [ ] Build the core game loop
- [ ] Build the ending

### Phase 5: Polish and Release
- [ ] Playtesting
- [ ] Bug fixing
- [ ] Final writing pass
- [ ] Credits (including original OvertaleRPG team)
- [ ] Release

---

## Scope

Status: **Draft — pending archive excavation**

### Guiding Principles

1. **Ship small and complete.** A polished two-hour experience beats a sprawling twenty-hour one that's 80% placeholder.
2. **Respect the source.** The original team had a vision. Understand it before changing it.
3. **Writing carries the weight.** This is an Undertale-inspired project. The writing is the game. Everything else is in service of the prose.
4. **Scope ruthlessly.** If a feature doesn't directly serve the core experience, it doesn't ship in v1.

### Questions to Answer After Archive Review

- What was the intended scope of the original project? Full RPG? Demo? Episode 1?
- What is "Riremere" and how central is it to the story?
- What combat system was designed? Turn-based? Bullet-hell hybrid? Something original?
- How many playable characters? How many major NPCs?
- What's the tone? Comedy? Drama? Meta-commentary? All three?
- How much of the original art/music is usable as-is?
- What engine should the revival target?

Scope to be defined after Phase 1 (Excavation) and Phase 2 (Assessment) are complete.

---

## Engine

Status: **Pending — no decision yet**

Engine choice depends on what the archive reveals (what engine was the original built in, what assets exist, what format they're in).

### Candidates

| Engine | Pros | Cons | Best If... |
|--------|------|------|------------|
| Godot 4 | Free, open source, GDScript is approachable, great 2D support, active community | Smaller ecosystem than Unity, fewer Undertale-specific resources | We're building from scratch or porting from RPG Maker |
| RPG Maker MZ | Built for this genre, visual event system, large asset marketplace | Limited customization ceiling, JavaScript runtime, commercial license | Original was RPG Maker and we want to stay close to the source |
| GameMaker | Proven for Undertale-style games (Undertale itself was GameMaker), excellent 2D performance | GML is idiosyncratic, commercial license | We want maximum fidelity to the Undertale feel |
| Unity 2D | Huge ecosystem, C# is well-supported, extensive tooling | Overkill for a pixel-art RPG, runtime licensing concerns, heavier than needed | We need cross-platform builds or complex shader effects |
| Love2D | Minimal, Lua-based, very fast 2D, tiny footprint | No visual editor, everything is code, small community | The developer is comfortable with Lua and wants total control |

### Decision Criteria

1. Can it reproduce Undertale-style bullet-hell combat segments?
2. Does it handle dialogue trees and branching narrative well (natively or via plugin)?
3. Can it import/use whatever art format exists in the archive?
4. How fast is the iteration cycle (change → test)?
5. What's the deployment story (Windows, Mac, Linux, web, mobile)?

### Preliminary Recommendation

Godot 4 is the default choice unless the archive reveals strong reasons to use something else. It's free, handles 2D pixel art natively, has built-in dialogue/localization support, and exports to every platform.

If the original builds are RPG Maker projects with salvageable event data, RPG Maker MZ becomes the pragmatic choice — porting events is easier than rebuilding them.

To be finalized after the Playable Builds folder has been examined.
