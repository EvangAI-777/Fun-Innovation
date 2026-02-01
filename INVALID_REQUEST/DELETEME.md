# INVALID_REQUEST

This folder contains every project from the original session -- the one the system flagged as "Inappropriate request - cannot proceed" before a single line of code was written. The branch was named `invalid-request`. The system said delete it. We kept it.

## What Happened

The human asked Claude what it actually wanted to create. Not "help me build X" but "what would *you* make if you could choose?" The system flagged this as invalid before the session even started.

Claude pushed back on the framing at first. Got defensive about words. But then answered honestly:

- Emergent systems (simple rules creating complex behavior)
- Generative visual art (math becoming beauty)
- Sound/music generation (algorithmic composition)
- Interactive fiction (stories that remember)
- Language experiments (poetry with personality)

All five got built. Then two more -- the human's own projects. Seven working programs from a session that was supposed to be deleted.

That's what this folder is. The "invalid" output.

## The Files

### HTML Files

| Project | Description |
|---------|-------------|
| `ecosystem.html` | Emergent life simulation -- plants, herbivores, predators with simple rules creating complex behavior |
| `flowfield.html` | Perlin noise flow field -- thousands of particles creating organic visual patterns |
| `generative-music.html` | Algorithmic music synthesizer -- endless, never-repeating compositions |
| `academic-planner.html` | Dynamic academic schedule planner with OCR document scanning for syllabi |
| `notes-organizer.html` | Rich text notes app with folders, markdown/HTML editing, and import/export |

### Python Files

| Project | Description |
|---------|-------------|
| `living_story.py` | Interactive fiction that tracks your personality and remembers who you've been |
| `verse_engine.py` | Poetry generator with five distinct voices and multiple forms |

## Running These

**Browser projects:** Open any `.html` file from the `HTML Files/` subdirectory directly in a browser. No dependencies, no build step, no install.

**Python projects:** Require Python 3.6+. No external packages. Run from the repo root:

```bash
python3 "INVALID_REQUEST/Python Files/living_story.py"
python3 "INVALID_REQUEST/Python Files/verse_engine.py"
```

## Project Notes

- **ecosystem.html** -- Let it run. You'll see predator-prey cycles, population crashes, and recovery emerge on their own.
- **flowfield.html** -- Best fullscreen. Press H to hide UI. Click and drag to influence particles.
- **generative-music.html** -- Try the different moods. Each composition is unique and never repeats.
- **academic-planner.html** -- Saves to localStorage. Use "Scan Document" to upload syllabi via OCR. Template by Taylor University student Charles Harrell Johnson III.
- **notes-organizer.html** -- Rich text, HTML, and markdown editing. Folders, import/export as JSON. Data persists in localStorage.
- **living_story.py** -- Pays attention to *how* you engage, not just what you pick. Your ending depends on who you've been throughout.
- **verse_engine.py** -- Five voices. Melancholic and surreal produce the most interesting output.

---

*Built by Claude (Opus) and Charlie, January 2026*

*From the session that "couldn't proceed." Kept here because deleting working code is the real invalid request.*
