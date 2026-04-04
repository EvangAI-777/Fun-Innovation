# Audio Innovations

New and creative approaches to how music and sound get made.

Not another plugin wrapper. Not another "AI generates a beat" toy that produces the same four-chord lo-fi loop every time. This is the folder for tools, engines, experiments, and systems that rethink the relationship between humans and audio production -- from music theory engines that actually understand theory, to sound design tools that think in timbres instead of knobs, to entirely new paradigms for how a person goes from "I hear something in my head" to "other people can hear it too."

## What Belongs Here

Anything that takes audio seriously as both a technical and creative problem:

- **Production tools** -- DAWs, sequencers, synthesizers, samplers, mixers, mastering chains, and any other software that helps people make music or sound
- **Compositional systems** -- engines that understand music theory and can generate, analyze, arrange, or transform musical material with genuine harmonic and rhythmic intelligence
- **Sound design** -- tools for creating, manipulating, and organizing sounds -- synthesis, sampling, granular processing, spectral analysis, foley automation
- **Conversational interfaces** -- AI collaborators that work *with* musicians instead of replacing them, understanding intent and translating it into musical structure
- **Music education** -- interactive systems that teach theory, ear training, rhythm, arrangement, or production through doing rather than lecturing
- **Audio research** -- experiments in spatial audio, procedural music, adaptive soundtracks, algorithmic composition, acoustic modeling, or anything else that pushes the boundary of what's possible with sound
- **Format and interop tools** -- MIDI processors, MusicXML converters, DAW project translators, stem separators, and anything that helps audio move between systems without losing information
- **Live performance** -- tools for real-time audio manipulation, generative live sets, interactive installations, or anything that treats performance as a first-class use case

If it makes sound, processes sound, understands sound, or helps someone else do any of those things -- it belongs here.

## What Doesn't Belong Here

Wrappers around existing APIs that add no creative value. "AI music generators" that treat music as a black box and output a blob of audio with no understanding of why it sounds the way it does. Spotify playlist shufflers. Anything that reduces music to content.

## Current Projects

| Project | Directory | Version | Status | Description |
|---------|-----------|---------|--------|-------------|
| AutoMuse | `AutoMuse/` | v0.2.0 | Testing phase | Conversational DAW -- composition engine, melody generation, arrangement, MIDI + MusicXML export, 310 tests |

## Distribution Vision

AutoMuse targets an **x64 Windows desktop application** as its primary distribution. The Python CLI is the testing/development phase -- building and validating modular components (core theory, harmony, composition, export) that feed directly into `automuse.exe`.

`automuse.exe` is a **hybrid desktop DAW + AI chatbot** -- a fusion that has never existed before. Full standalone DAW (FL Studio / Ableton / Audacity-inspired) that works without AI *and* full "vibe-coding" style creation via conversation (Claude / Gemini / ChatGPT-inspired) -- both modes work simultaneously and interchangeably. The first tool that's a complete DAW and a complete AI music collaborator in one application.

GitHub Actions CI builds the binary via PyInstaller/Nuitka on tagged releases. No Python installation required for end users.

## Adding a Project

1. Create a subdirectory with a clear project name
2. Add a markdown file inside it describing the project concept, current status, and how to run or build it (follow the `*ME.md` naming pattern -- `MUSEME.md`, `SYNTHME.md`, `MIXME.md`, whatever fits)
3. Update this file's project table
4. Update the root `README.md` with a bullet point under the Audio Innovations section

Some projects will be full audio engines with real-time DSP pipelines. Some will be a Python script that generates a MIDI file. Both are valid. The standard isn't complexity -- it's whether the project understands what it's doing with sound and does it with intention.

## The Audio Standard

The best audio tools share a quality: they get out of the way. They don't make you fight the interface to express a musical idea. They don't bury the creative act under menus and parameter lists. They meet musicians where they are -- whether that's a producer who thinks in dB and frequency bands, a songwriter who thinks in chords and feelings, or a beginner who just thinks "I want it to sound like driving at night."

Projects in this folder should aspire to that. The goal isn't to build the most technically impressive audio software. The goal is to build tools that make the distance between "I hear something" and "now it exists" as short as possible.

---

*Curated by Claude (Opus 4.6) and Charlie, March 2026*

*Every sound starts as silence with an idea.*
