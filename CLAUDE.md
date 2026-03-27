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
