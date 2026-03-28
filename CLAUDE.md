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
  Omni Writer/            — Creative writing tool (HTML/JS, v2.0.0)
  Omniversal Mathematics/ — Math framework (HTML/JS)
Undertale Innovations/
  OvertaleRPG/            — Fan game revival (HTML/JS)
tests/                    — All test suites (644 tests across 6 suites)
.github/workflows/        — CI (ci.yml) and GitHub Pages deployment (pages.yml)
```

## Build & Test Commands

```bash
make install          # Install GeoVox, AutoMuse, Minecraft Studio (editable) + pytest
make test             # Run all 6 test suites (644 tests)
make test-geovox      # GeoVox tests (27 tests)
make test-roblox      # Roblox static analysis (102 tests)
make test-originals   # Original project tests (48 tests)
make test-automuse    # AutoMuse tests (197 tests)
make test-mcstudio    # Minecraft Studio tests (118 tests)
make test-omniversal  # Omniversal suite (255 tests)
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

## Style Notes

- No linter, formatter, or type checker is configured. Don't add one unless asked.
- Respect the experimental, creative tone. Don't impose enterprise patterns.
- Projects are organized by creative theme — keep it that way.
