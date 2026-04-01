# CLAUDE.md

## Project Overview

Fun-Innovation is a multi-project creative monorepo — a collaboration between human (Charlie) and AI (Claude). Projects span Python, Luau (Roblox), and HTML/JavaScript, organized by creative theme rather than technical category. The philosophy is experimental and playful: build things that have never existed before.

## Project Structure

```
INVALID_REQUEST/          — Original 7 projects (HTML apps + Python CLI tools)
Roblox Innovations/       — 7 multiplayer Roblox reimaginings (Luau)
Minecraft Innovations/
  GeoVox/                 — Voxel pipeline (Python, v0.1.1)
  Minecraft Studio/       — Mod IDE with multi-loader export (Python, v0.2.0)
Audio Innovations/
  AutoMuse/               — Music composition engine (Python, v0.1.0)
OMNI INNOVATIONS/
  Omniversal Calculator/  — Multi-universe calculator (HTML/JS, v1.4.0)
  Omni Writer/            — Creative writing tool (HTML/JS, v2.1.0)
  Omniversal Mathematics/ — Math framework (HTML/JS)
Undertale Innovations/
  OvertaleRPG/            — Fan game revival (HTML/JS)
tests/                    — All test suites (785 tests across 6 suites)
.github/workflows/        — CI (ci.yml) and GitHub Pages deployment (pages.yml)
```

## Build & Test Commands

```bash
make install          # Install GeoVox, AutoMuse, Minecraft Studio (editable) + pytest
make test             # Run all 6 test suites (785 tests)
make test-geovox      # GeoVox tests (27 tests)
make test-roblox      # Roblox static analysis (102 tests)
make test-originals   # Original project tests (48 tests)
make test-automuse    # AutoMuse tests (197 tests)
make test-mcstudio    # Minecraft Studio tests (118 tests)
make test-omniversal  # Omniversal suite (293 tests)
make clean            # Remove __pycache__, *.egg-info, dist/, build/
```

## Conventions

- **Zero/minimal dependencies** — This is intentional. AutoMuse and Minecraft Studio have zero deps. GeoVox uses only numpy + Pillow. Don't add dependencies unless absolutely necessary.
- **Documentation naming** — Each theme has a `*ME.md` file (e.g., `FUNME.md`, `HEARME.md`, `MUSEME.md`). Each Roblox project has a `SETUP.md`.
- **Roblox project pattern** — Every Roblox project uses a 4-script modular architecture (Server, Client, Config, Shared) documented in its `SETUP.md`.
- **Python packages** — GeoVox, AutoMuse, and Minecraft Studio are installable packages with CLI entry points (`geovox`, `automuse`, `mcstudio`).
- **Tests live in `tests/`** — All test files are in the top-level `tests/` directory, organized by project. AutoMuse and Minecraft Studio tests must run from their package directory (see Makefile).

## CI & Deployment

- **CI** (`.github/workflows/ci.yml`) runs on push to main/master and on PRs. Jobs: GeoVox (Python 3.10 + 3.12), Roblox, Originals, Omniversal, AutoMuse, Minecraft Studio.
- **GitHub Pages** (`.github/workflows/pages.yml`) deploys the repo as a static site on push to main/master. Browser-based projects (Omniversal Calculator, Omni Writer, OvertaleRPG) are accessible via Pages.

## Commit & Push Strategy

**CRITICAL: Commit and push small, logical units — never batch large-scale file revisions into a single massive commit.**

- **Small logical commits** — After completing each logical section of work (e.g., one file updated, one feature added, one bug fixed), commit and push immediately. Do not accumulate dozens of file changes before committing.
- **Why this matters** — Large-scale commits risk hitting push failures, context window limits, and network timeouts. When a large push fails partway through, the entire session stalls — wasting time, tokens, and money while Claude retries or the user has to intervene. Small pushes succeed reliably and make progress incremental and recoverable.
- **The cost of batching** — Trying to stage and push 10+ file changes at once often leads to: git errors that require manual cleanup, exceeded context from reviewing too many diffs at once, and wasted API credits from Claude spinning on retry loops or re-reading the same files. A failed large push can burn significant credits with zero progress to show for it.
- **The right workflow** — Edit a logical unit of files, commit with a clear message describing that unit, push, then move to the next unit. Each push should be small enough that if it fails, retrying is trivial. This keeps the session productive and the user's costs low.
- **A "section" is NOT a file** — This is a common AI pitfall. Do not treat each file as the smallest commitable unit. Files contain internal subsections — a config block, a handler function, a UI component — and each of those subsections can be written, committed, and pushed independently. For example, when building a Roblox project's Server script, commit after writing the initialization logic, then commit again after adding the event handlers, then again after the cleanup logic. Do not wait until the entire Server script is finished.
- **Unfinished files are fine** — It is semantically okay for a file to be incomplete at any given commit. That's what commits are for — they represent incremental progress, not finished products. Committing a half-written file is far better than losing all progress because a massive end-of-session push failed.
- **Commit and push after each logical section** — Do not hoard commits locally. After each small logical section is written, commit it and push it to the branch. This ensures progress is saved remotely and recoverable even if the session dies. Pushing frequently is safe — the user handles the final GitHub merge (merging the branch into main). Pushing to a feature branch is not the same as merging; it's just saving your work.
- **Logical sections vary by context** — What counts as a "logical section" depends on the file type, the project, and the task at hand. A Roblox Server script might break into init, event handlers, and cleanup. A Python module might break into imports/config, core logic, and CLI entry point. An HTML file might break into structure, styles, and scripts. Refer to the Claude Code plan file and this CLAUDE.md for guidance on how the current task should be decomposed.
- **Ask the user when unsure** — If it's unclear how to break a task into logical sections, or what granularity of commits makes sense for a particular file or project, ask the user for clarification. It's always better to ask than to guess wrong and batch too much work into one commit.

## Token Efficiency & Session Management

Tokens are spent on two things: **context** (what Claude reads) and **output** (what Claude writes). Most waste comes from vague tasks requiring clarification rounds, agents launched for things a direct tool call could handle, and asking Claude to explore before telling it where to look.

### Be specific about the target

Bad:
> "There's a bug in the authentication flow, can you look into it?"

Good:
> "In `src/auth/session.ts` around line 84, `validateToken()` isn't checking expiry before returning `true`. Add the expiry check."

The second version skips file discovery and clarification rounds — probably 80% fewer tokens. If you already know where something lives, say so. "Read `src/utils/parser.py` lines 40–80" costs far less than "find where the parsing logic is."

### Avoid agents for directed searches

Agents are powerful but expensive. Skip them for anything with a clear target:

- "Find the definition of `parseConfig`" → use Grep directly
- "Check if `utils.js` calls `fetch`" → use Grep directly
- "What's in `config/defaults.json`?" → use Read directly

Use agents only for genuinely open-ended work: researching an unfamiliar codebase, scanning upstream project history across many commits, or running a multi-step background task.

### Front-load constraints

Tell Claude what NOT to do at the start of a task — not after it has already done it. Useful constraints:

- "Don't spawn agents, use direct tool calls."
- "Don't refactor anything outside the specific function I'm asking about."
- "Keep the change under 20 lines."
- "Don't add comments, docstrings, or type annotations."

Correcting an unwanted 200-line response costs more tokens than preventing it.

### Ask for a plan before big implementations

For anything touching more than 3 files, ask Claude to describe the approach in one paragraph before writing any code. If the approach is wrong, course-correct there — not after the implementation is already written.

### Narrow the scope of exploratory tasks

Bad:
> "Scan all recent upstream changes and tell me what's relevant."

Better:
> "Fetch the v2.4 release notes page and summarize only the breaking API changes."

Scoping the question scopes the work. The second version produces the same useful output with a fraction of the tool calls.

### One task, one session

Sessions accumulate context. The longer a session runs, the more tokens go to context overhead. When a logical unit of work is done (a bug fix, a feature, a research task), commit, push, and start a fresh session for the next thing.

### Token Cost Reference

| Operation | Relative Cost |
|-----------|--------------|
| Direct file read (Read tool) | Low |
| Direct Grep/Glob search | Low |
| Single WebFetch | Medium |
| Single WebSearch | Medium |
| Agent (foreground, simple task) | High |
| Agent (foreground, research task) | Very High |
| Large refactor across 10+ files | Very High |
| Back-and-forth correction loops | Compounds fast |

### Emergency Mode (Near the Cap)

When at ~10% remaining tokens:

1. **No agents.** Every task uses direct tool calls only.
2. **No exploration.** Know the file before asking about it.
3. **One thing.** Pick the single highest-value task and do only that.
4. **Short outputs.** Ask for concise responses: "in one paragraph", "under 20 lines of code", "just the diff, no explanation."
5. **Skip the docs.** No comments, docstrings, or summaries unless they are the actual deliverable.
6. **Commit before you start.** If the session ends mid-task, you want a clean base to return to next week.

### What's Actually Worth Spending Tokens On

In rough priority order:

1. **Bug fixes with a clear reproduction** — high value, tight scope
2. **Implementing a feature you've already designed** — efficient when you provide the spec upfront
3. **One-time research with durable output** — pays for itself if findings are written down
4. **Refactoring** — low priority; defer unless actively blocking work
5. **Exploration / "what does this code do?"** — use sparingly; read it yourself when you can

### The Meta-Principle

Claude Code works best when you treat it like a skilled contractor, not a search engine. A contractor does their best work when handed a blueprint, not when asked to figure out what to build. The more you've thought through a task before opening a session, the more of your token budget goes toward actual work rather than planning overhead.

**Hand Claude a blueprint. Don't ask it to design the building.**

---

## Style Notes

- No linter, formatter, or type checker is configured. Don't add one unless asked.
- Respect the experimental, creative tone. Don't impose enterprise patterns.
- Projects are organized by creative theme — keep it that way.
