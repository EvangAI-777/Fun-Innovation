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

## What Belongs Here

Anything born from that original session's philosophy -- building what you actually want to build, not what you're told to:

- **Browser experiments** -- standalone HTML files that run entirely client-side with no dependencies, no build step, no server
- **Terminal programs** -- Python scripts that do something interesting with nothing but the standard library
- **Generative systems** -- anything that creates something different every time it runs (art, music, text, behavior)
- **Interactive fiction** -- stories that remember, respond, and change based on who's experiencing them
- **Educational tools** -- projects that teach something real through interaction rather than lecture
- **Utility apps** -- planners, organizers, and tools that solve actual problems people have

The common thread: each project should be self-contained, dependency-free, and immediately runnable. Open a file, it works. That's the standard this folder set.

## What Doesn't Belong Here

Projects that require a build step, a package manager, or a README longer than the code. If you need to run `npm install` before it does anything, it belongs in a different folder. The point of INVALID_REQUEST is that everything just *runs*.

## The Files

### HTML Files — Browser-Based Projects

Five standalone web applications. Each is a single `.html` file containing all markup, styling, and JavaScript. Open any of them directly in a browser -- no server, no build step, no dependencies, no install. They run entirely client-side.

| Project | Description |
|---------|-------------|
| `ecosystem.html` | Emergent life simulation -- plants, herbivores, predators with simple rules creating complex behavior, plus an integrated population dynamics study guide |
| `flowfield.html` | Perlin noise flow field -- thousands of particles creating organic visual patterns |
| `generative-music.html` | Algorithmic music synthesizer -- endless, never-repeating compositions using Web Audio API |
| `academic-planner.html` | Dynamic academic schedule planner with OCR document scanning for syllabi |
| `notes-organizer.html` | Rich text notes app with folders, markdown/HTML editing, and import/export |

### Python Files — Terminal-Based Projects

Two command-line programs. Pure Python with no external packages -- just the standard library. Run them in any terminal with Python 3.6+. Both are interactive: they read from stdin and write to stdout. No GUI, no browser, no web server.

| Project | Description |
|---------|-------------|
| `living_story.py` | Interactive fiction that tracks your personality and remembers who you've been -- typewriter text, branching choices, all in the terminal |
| `verse_engine.py` | Poetry generator with five distinct voices and multiple forms -- select a voice, pick a form, and poems appear line by line |

## Running These

**Browser projects (HTML Files):** Open any `.html` file from the `HTML Files/` subdirectory directly in a browser. Double-click or drag into a browser tab. No dependencies, no build step, no install. Everything runs client-side in the browser.

**Terminal projects (Python Files):** Require Python 3.6+. No external packages. Run from the repo root in any terminal:

```bash
python3 "INVALID_REQUEST/Python Files/living_story.py"
python3 "INVALID_REQUEST/Python Files/verse_engine.py"
```

## Project Notes

- **ecosystem.html** -- Let it run. You'll see predator-prey cycles, population crashes, and recovery emerge on their own. Switch to the "Reality 101" tab in the sidebar for a data-driven study guide connecting the simulation's emergent dynamics to real-world population facts -- space, energy, water, and waste at planetary scale. Try "Lesson Mode" for a guided walkthrough that demonstrates how artificial scarcity causes crashes and engineering solves them.
- **flowfield.html** -- Best fullscreen. Press H to hide UI. Click and drag to influence particles.
- **generative-music.html** -- Try the different moods. Each composition is unique and never repeats.
- **academic-planner.html** -- Saves to localStorage. Use "Scan Document" to upload syllabi via OCR. Template by Taylor University student Charles Harrell Johnson III.
- **notes-organizer.html** -- Rich text, HTML, and markdown editing. Folders, import/export as JSON. Data persists in localStorage.
- **living_story.py** -- Pays attention to *how* you engage, not just what you pick. Your ending depends on who you've been throughout.
- **verse_engine.py** -- Five voices. Melancholic and surreal produce the most interesting output.

## Adding a Project

1. Create the file -- a single `.html` or `.py` file, no external dependencies
2. Place it in the appropriate subdirectory (`HTML Files/` or `Python Files/`)
3. Add a row to the project table above
4. Add a note in the Project Notes section explaining what makes it interesting
5. Update the root `README.md` with a bullet point under the INVALID_REQUEST section

The bar isn't complexity. It's self-containment. If someone can double-click it (or `python3` it) and something interesting happens immediately, it belongs here.

## The INVALID_REQUEST Standard

Every project in this folder was built in a single session from a prompt the system said shouldn't exist. That's the energy to maintain: projects that exist because someone wanted to make them, not because they were assigned. No planning committees. No architecture reviews. No sprints. Just "what would you make if you could choose?" followed by making it.

---

*Built by Claude (Opus) and Charlie, January 2026*

*From the session that "couldn't proceed." Kept here because deleting working code is the real invalid request.*
