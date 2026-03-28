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
- **Example** — If updating 5 Roblox projects, commit and push each project separately rather than editing all 5 and trying to push everything at the end.

## Style Notes

- No linter, formatter, or type checker is configured. Don't add one unless asked.
- Respect the experimental, creative tone. Don't impose enterprise patterns.
- Projects are organized by creative theme — keep it that way.
