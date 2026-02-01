# Engine Evaluation

Status: **Pending -- no decision yet**

Engine choice depends on what we find in the archive (what engine was the original built in, what assets exist, what format they're in). This doc tracks the options.

## Candidates

| Engine | Pros | Cons | Best If... |
|--------|------|------|------------|
| Godot 4 | Free, open source, GDScript is approachable, great 2D support, active community | Smaller ecosystem than Unity, fewer Undertale-specific resources | We're building from scratch or porting from RPG Maker |
| RPG Maker MZ | Built for this genre, visual event system, large asset marketplace | Limited customization ceiling, JavaScript runtime, commercial license | Original was RPG Maker and we want to stay close to the source |
| GameMaker | Proven for Undertale-style games (Undertale itself was GameMaker), excellent 2D performance | GML is idiosyncratic, commercial license | We want maximum fidelity to the Undertale feel |
| Unity 2D | Huge ecosystem, C# is well-supported, extensive tooling | Overkill for a pixel-art RPG, runtime licensing concerns, heavier than needed | We need cross-platform builds or complex shader effects |
| Love2D | Minimal, Lua-based, very fast 2D, tiny footprint | No visual editor, everything is code, small community | The developer is comfortable with Lua and wants total control |

## Decision Criteria

1. Can it reproduce Undertale-style bullet-hell combat segments?
2. Does it handle dialogue trees and branching narrative well (natively or via plugin)?
3. Can it import/use whatever art format exists in the archive?
4. How fast is the iteration cycle (change → test)?
5. What's the deployment story (Windows, Mac, Linux, web, mobile)?

## Recommendation (Preliminary)

Godot 4 is the default choice unless the archive reveals strong reasons to use something else. It's free, it handles 2D pixel art natively, it has built-in dialogue/localization support, and it can export to every platform. The GDScript learning curve is gentler than C#/GML for new contributors.

If the original builds are RPG Maker projects with salvageable event data, RPG Maker MZ becomes the pragmatic choice -- porting events is easier than rebuilding them.

To be finalized after the Playable Builds folder has been examined.
