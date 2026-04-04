# Minecraft Innovations

Minecraft infrastructure tooling. Two projects, each at a different scale of ambition, aimed at the same gap: the most popular game ever made has creation tools that are decades behind what smaller platforms offer.

## Projects

| Project | Directory | Focus | Status |
|---------|-----------|-------|--------|
| GeoVox | `GeoVox/` | Real-world 3D data → Minecraft worlds | v0.3.0 — testing phase |
| Minecraft Studio | `Minecraft Studio/` | Roblox Studio-style IDE for Minecraft modding | v0.4.0 — testing phase, Layers 1-2 complete |

See [`GeoVox/VOXELME.md`](./GeoVox/VOXELME.md) for the GeoVox project overview and [`GeoVox/Design/ARCHITECTURE.md`](./GeoVox/Design/ARCHITECTURE.md) for the full technical design.

See [`Minecraft Studio/STUDYME.md`](./Minecraft%20Studio/STUDYME.md) for the Minecraft Studio overview, [`Minecraft Studio/Design/ARCHITECTURE.md`](./Minecraft%20Studio/Design/ARCHITECTURE.md) for the full technical design, and [`Minecraft Studio/Design/ROADMAP_1.0.md`](./Minecraft%20Studio/Design/ROADMAP_1.0.md) for the roadmap to v1.0.

## Distribution Vision

Both projects target **x64 Windows desktop application releases** as their primary distribution. Each project's Python CLI is the testing/development phase — building and validating modular components (ingest, palette, export, codegen, etc.) that feed directly into the desktop application. Current roadmap features continue as planned; they're developing modules that slot into the GUI binary. Once a module is tested in CI, it ships inside the application.

- **GeoVox** → `geovox.exe` — desktop terrain editor drawing UI/layout from WorldPainter and similar tools. Map viewport, brush palette, layer management, import/export wizards. Pipeline modules (ingest, palette, export) built and tested in Python CI, then compiled into the GUI application via PyInstaller/Nuitka.
- **Minecraft Studio** → `mcstudio.exe` — full desktop IDE drawing heavily from Roblox Studio's panel-based UX. Dockable Explorer/Properties panels, visual editors, 3D viewport, code editor. Export engine modules (model, codegen, export) built and tested in Python CI, then compiled into the IDE.

GitHub Actions CI builds the binaries on tagged releases. No Python installation required for end users.

## What Belongs Here

Anything that improves the Minecraft creation ecosystem at the infrastructure level: data pipelines, development environments, format converters, modding utilities, world generation tools, server tooling, creative tools. These are tools *for* Minecraft, not mods *in* Minecraft.

## The Minecraft Standard

Minecraft's modding community has collectively built every piece of tooling it needs -- but in isolation, in incompatible formats, with documentation scattered across wikis, Discord servers, and abandoned GitHub repos. Build the tool you wish existed, make it composable, and document it like someone who's never seen your code will need to use it tomorrow.

---

*Conceived by Claude (Opus 4.5), February 2026*

*Because every coordinate system eventually leads to Minecraft.*
