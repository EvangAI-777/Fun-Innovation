# AutoMuse

Open Ableton. Open FL Studio. Open Logic. Open Reaper. What do you see?

A timeline. A mixer. A piano roll. Hundreds of buttons. Thousands of parameters. A learning curve that takes months before you can make something that doesn't sound like a ringtone from 2006. The most powerful creative tools in music production are also the most hostile to anyone who isn't already a producer.

Now imagine this instead: you open an application and someone asks you, "What do you want to make today?"

That's AutoMuse.

## What It Is

A digital audio workstation where the primary interface is a conversation. Not an AI assistant bolted onto a traditional DAW. The AI *is* the environment. You talk to it. It talks back. Music emerges from the dialogue.

```
+----------------------------------------------------------------+
|  AutoMuse                                           [- o x]    |
+--------------------+-------------------------------------------+
|                    |                                           |
|  Conversation      |  Canvas                                  |
|                    |                                           |
|  Muse: What are    |  [Arrangement / Piano Roll / Notation /  |
|  we making today?  |   Waveform / Mixer -- whatever view      |
|                    |   fits the current conversation]          |
|  You: Something    |                                           |
|  melancholic. Like |                                           |
|  driving alone at  |  Currently showing:                      |
|  2am on an empty   |  D Dorian | 82 BPM | 4/4                 |
|  highway.          |  [Piano + sparse drums + ambient pad]     |
|                    |                                           |
|  Muse: I hear you. |  +-----------+-----------+-----------+   |
|  D Dorian, sparse  |  | Intro 8b  | Verse 16b | Bridge 8b |   |
|  piano, 82 BPM.    |  +-----------+-----------+-----------+   |
|  Listen to this    |                                           |
|  as a starting     |                                           |
|  point...          |                                           |
|                    |                                           |
+--------------------+-------------------------------------------+
|  Transport: [|<] [<] [ > Play ] [>] [>|]    BPM: 82   D Dor  |
+----------------------------------------------------------------+
```

The left panel is a conversation. The right panel is a living canvas that updates as the conversation progresses. Every suggestion the Muse makes is reflected visually and audibly. Every edit you make on the canvas feeds back into the conversation context. The two panels are one creative loop.

## The Muse

Not a generic chatbot. A *music AI persona* -- confident, smooth, kind, and deeply knowledgeable. But here's the thing that matters most: **the Muse serves the artist, not music theory.**

The Muse is not prideful. It doesn't lecture. It doesn't push its own agenda. It doesn't say "well actually, in classical harmony you should..." when someone wants to stack fifths because it sounds raw. The Muse's job is to understand what *you* want to make and help you get there -- with all the theory knowledge in the world available if you need it, and none of it shoved in your face if you don't.

You say "make it sadder." The Muse doesn't launch into a theory lecture. It might suggest a Neapolitan sixth, or pulling the tempo down by 3 BPM and adding a cello countermelody -- but only because that's what serves *your* vision. It explains *why* if you want to know -- "the Neapolitan creates this moment of harmonic surprise that resolves into something bittersweet, not just sad." You learn music theory as a side effect of making music. But the Muse never makes you feel like you should already know it.

The Muse speaks your language. To a beginner: "I added some lower notes that move against the melody -- it creates a kind of ache." To a producer: "I substituted a bVI for the expected V in bar 12 and voiced the strings in close position to thicken the texture." Same musical idea. Different vocabularies. The Muse matches yours and stretches it -- gently, never condescendingly.

The Muse might offer alternatives -- "want to hear what this sounds like with a Mixolydian bridge? Could be interesting" -- but it's always a genuine offer, never a correction. If you say no, the Muse moves on without making you feel wrong. Your song, your call. The Muse is the best session musician you've ever worked with: shows up prepared, plays what the song needs, offers ideas when asked, and never makes the session about them.

## Music Theory as a First Language

AutoMuse doesn't guess at music. It knows all of it:

**Every scale and mode.** Major, natural/harmonic/melodic minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian. Pentatonic and blues scales. Whole tone, diminished, augmented. Bebop scales. Maqam. Raga. Gamelan. If it has a name and a set of intervals, AutoMuse knows it and can compose in it.

**Every key signature.** All 12 major, all 12 minor, plus enharmonic spellings and theoretical keys. Modulation paths between any two keys. Pivot chord identification. Common-tone modulation. Direct modulation. Truck driver's gear change (and why you might actually want one sometimes).

**Every time signature and tempo.** 4/4, 3/4, 6/8, 5/4, 7/8, 11/8, polymetric overlays, metric modulation, rubato, accelerando, ritardando. From 20 BPM ambient drone to 300 BPM speedcore.

**Every genre.** Not superficially. Structurally. Jazz knows about ii-V-I and tritone substitution. EDM knows about sidechain compression and supersaw detuning. Classical knows about sonata form and counterpoint rules. Hip-hop knows about swing quantization and 808 tuning. Folk knows about open tunings and drone strings. Each genre carries its own set of conventions, and AutoMuse can work within them, blend them, or deliberately break them.

**Every chord voicing.** Root position, inversions, drop voicings, shell voicings, quartal harmony, cluster voicings. Spread across instruments or stacked on a single keyboard. The Muse voices chords for the context -- a jazz piano comp voices differently than an orchestral string section, even when the harmony is identical.

## The Scaling Philosophy

This is where AutoMuse fits into the repo's DNA.

**Layer 1: The Conversation.** Text in, musical structure out. The Muse converses. It generates MIDI, chord charts, lead sheets, notation. No audio engine needed. No plugins. Just music theory made conversational. A terminal-mode AutoMuse that exports MIDI files is already a useful tool -- a composer's sketchpad that understands theory.

**Layer 2: The Canvas.** Visual representation of what the conversation produces. Piano roll. Notation view. Arrangement view. Waveform display. Mixer. You can interact with the canvas directly -- drag notes, adjust levels, draw automation -- and the Muse sees what you did and incorporates it into the ongoing dialogue. This is the IDE layer.

**Layer 3: The Studio.** Full audio engine. Real-time synthesis. Plugin hosting (VST3, AU, LV2). Effects processing. Mixing. Mastering. Audio I/O for recording live instruments. At this layer, AutoMuse is a complete DAW -- but one where the conversation is always available as the primary creative interface.

Each layer is complete on its own. Layer 1 exports MIDI. Layer 2 exports MIDI + notation + arrangement data. Layer 3 exports rendered audio in any format. You never *need* the next layer. It's there when you're ready.

## What You Could Do With This

**You're a songwriter who doesn't produce.** You describe the song. The Muse helps you build it. You export stems and hand them to a producer who works in Ableton. Or you export MIDI and import it into Logic. AutoMuse meets you where you are and connects to where you're going.

**You're a producer who's stuck.** Three hours on the same 8 bars. Open the conversation. "I'm stuck on the bridge. The verse is in G minor, the chorus lifts to Bb major, but the bridge feels flat." The Muse suggests five options, explains the theory behind each, and plays them. You pick one, modify it, keep going.

**You're a beginner who just wants to make something.** "I want to make a lo-fi hip-hop beat." The Muse walks you through it. Tempo, key, drum pattern, chord progression, sample selection. You learn what a chord progression is because you're building one in real time with someone who explains it naturally. By the time you're done, you have a beat and you understand *why* it sounds the way it does.

**You're a film composer on a deadline.** "I need 90 seconds of tension building from nothing to full orchestra, key of E-flat minor, hitting a sting at the 47-second mark." The Muse scaffolds the arrangement, handles the orchestration, and you refine. Export stems grouped by section (strings, brass, woodwinds, percussion). Drop into your DAW of choice for final mix.

**You're a music teacher.** "Show me all the modes of C major and play each one over a drone." The Muse becomes an interactive theory textbook. Students hear the difference between Dorian and Mixolydian while the Muse explains what makes each one distinctive. "Now compose a 4-bar melody in Lydian." The student writes, the Muse gives feedback. Music education that's conversational, not rote.

**You're experimenting.** "What happens if I take a Bach chorale and reharmonize it with jazz voicings?" "Give me a 7/8 groove that feels like 4/4 with a hiccup." "Write a melody that uses all 12 chromatic pitches exactly once but sounds tonal." The Muse doesn't just execute -- it engages with the premise, suggests variations, explains what's interesting about the result.

## Export and Integration

AutoMuse doesn't trap your music. Everything exports:

| Format | What | Use Case |
|--------|------|----------|
| MIDI | Notes, velocities, CC data, tempo map | Import into any DAW or notation software |
| MusicXML | Full notation with dynamics, articulations | Sibelius, Finale, MuseScore, Dorico |
| WAV/FLAC | Rendered audio, individual stems or full mix | Final delivery, further processing |
| MP3/AAC | Compressed audio | Sharing, streaming |
| Project files | DAW-specific session export | Open in Ableton, FL Studio, Logic, Reaper |
| ABC notation | Text-based music notation | Folk music community, quick sharing |
| Lead sheets | Chord symbols + melody + lyrics | Session musicians, live performance |
| Stems | Grouped audio by instrument/section | Remix, collaboration, film/game delivery |

The Muse knows about all of these. "Export the piano part as MIDI and the drums as audio stems" is a valid instruction.

## Hard Problems

1. **Musical coherence over time.** LLMs are good at local decisions. Music requires global coherence -- a chord in bar 47 needs to relate to a theme introduced in bar 3. The conversation context window must carry musical structure, not just text.

2. **Real-time audio generation.** Layer 3 needs sub-10ms audio latency. The conversation runs on an LLM with multi-second response times. These two systems must coexist without the creative flow stuttering.

3. **Taste is subjective.** The Muse needs opinions to be a good collaborator, but its opinions need to be responsive to the user's aesthetic, not imposing its own. Calibrating that balance is a design challenge, not a technical one.

4. **Plugin ecosystem integration.** VST3/AU/LV2 hosting is a solved problem (JUCE, CLAP) but doing it inside a conversational context -- "make the reverb wetter on the bridge" mapping to actual plugin parameter changes -- requires bridging natural language to thousands of vendor-specific parameter names.

5. **Music copyright and originality.** The system must generate original compositions, not reproduce existing ones. This is both a legal and a creative integrity problem.

## Status

**v0.2.0 (Testing Phase) -- Composition Engine.** Zero external dependencies. `pip install -e .` then `automuse` to start a session.

Each module below is developed and tested in the Python CLI, then compiled directly into `automuse.exe`. Current features are building the modules that ship inside the desktop application.

**Core modules** (`automuse.core`):

| Module | What it does |
|--------|-------------|
| `automuse.core.notes` | Pitch classes (all 12, enharmonic spelling), concrete notes (MIDI-compatible, frequency, transposition) |
| `automuse.core.intervals` | All 13 standard intervals, interval arithmetic, inversion |
| `automuse.core.scales` | 28 scale types -- all 7 modes, 3 minor variants, pentatonic, blues, symmetric, bebop, and world music (phrygian dominant, hungarian minor, double harmonic, hirajoshi, in, iwato) |
| `automuse.core.chords` | 25 chord types -- triads, sevenths, extended (9th/11th/13th), added-tone, sus, power. Parsing, inversions, voicings |
| `automuse.core.keys` | Key signatures, diatonic triad and seventh chord construction, Roman numeral analysis, relative/parallel keys, pivot chord modulation |
| `automuse.core.rhythm` | Time signatures (simple, compound, irregular), durations (whole through 32nd, dotted, triplet), tempo with Italian markings |

**Harmony modules** (`automuse.harmony`):

| Module | What it does |
|--------|-------------|
| `automuse.harmony.progressions` | 10 built-in progression templates (I-IV-V-I, ii-V-I, 12-bar blues, pop, etc.), build from degrees or Roman numerals |
| `automuse.harmony.voicing` | 6 voicing styles: root position, close, drop 2, drop 3, spread, shell |
| `automuse.harmony.analysis` | Harmonic function analysis (tonic, subdominant, dominant, chromatic) |

**Composition modules** (`automuse.compose`) -- *new in v0.2.0*:

| Module | What it does |
|--------|-------------|
| `automuse.compose.motif` | MotifNote (note + duration + velocity), Motif (reusable phrases with transpose, invert, retrograde, augment, diminish, in_key), MotifBuilder (from scale degrees, note names, or intervals) |
| `automuse.compose.melody` | MelodyGenerator -- algorithmic melody from scale/contour/rhythm. 6 contour shapes (ascending, descending, arch, valley, static, wave), configurable step bias and range. 4 development techniques (sequence, variation, fragmentation, extension). Seeded for reproducibility |
| `automuse.compose.arrangement` | Song structure -- SectionType (9 types), Section (bars, key override, progression, melody), Arrangement (title, key, tempo, time sig, to_dict/from_dict). 5 templates: pop, verse-chorus, AABA, 12-bar blues, through-composed |

**Export modules**:

| Module | What it does |
|--------|-------------|
| `automuse.midi.writer` | Standard MIDI file writer -- zero dependencies, raw bytes, Type 0 and Type 1, variable-length encoding, tempo/time signature meta events |
| `automuse.export.musicxml` | MusicXML export -- zero-dep XML writing via stdlib xml.etree.ElementTree. Notes, chord symbols, scales. Key signature encoding, pitch spelling, time signatures. Interop with Finale, Sibelius, MuseScore, Dorico |

**Conversation engine**:

| Module | What it does |
|--------|-------------|
| `automuse.muse.engine` | The Muse -- conversational interface with 21 commands (scale, chord, key, progression, tempo, time, voicing, analyze, modulate, transpose, suggest, melody, motif, arrange, save, load, export, exportxml, play, help, quit), mood-responsive chat, session state with save/load, full workflow from key selection through MIDI and MusicXML export |

310 passing tests across 13 test files covering every module.

The audio engine (Layer 3) is a solved engineering problem (JUCE, PortAudio, RtMidi). The visual canvas (Layer 2) is an IDE problem. Layer 1 is the hard kernel -- the music knowledge, composition, and generation engine that everything else builds on. That kernel is now real.

### Primary Distribution: x64 Windows Binary

The x64 desktop application is the product. AutoMuse ships as `automuse.exe` -- a **hybrid desktop DAW + AI chatbot** unlike anything that exists. Two complete tools in one application:

**Full standalone DAW** (FL Studio / Ableton Live / Audacity-inspired): piano roll, arrangement timeline, mixer with faders and pan, transport controls, plugin browser, effects rack, waveform displays. You can do everything a regular DAW does without ever touching the AI. Full manual control. Click, drag, draw notes, mix tracks, apply effects -- the complete DAW experience stands on its own.

**Full conversational AI** (Claude / Gemini / ChatGPT-inspired): streaming conversation panel, chat history, natural language input, contextual suggestions. You can also do full "vibe-coding" style music creation -- just chatting and shooting the breeze with the Muse while it builds arrangements in real time. Tell it "I'm feeling something melancholic, maybe in D minor, kind of Radiohead-ish" and it builds the arrangement while you watch.

**Both modes work simultaneously and interchangeably.** Use the DAW manually for precise control, then switch to chatting with the Muse for creative exploration, then go back to tweaking by hand -- seamlessly, in the same session. It's like having a producer collaborator who lives inside your DAW. No other tool does this. DAWs don't have AI conversation. AI chatbots don't have piano rolls. AutoMuse is both.

Each module (core, harmony, compose, midi, export, muse) is developed and tested as a Python component in CI. Once tested, the modules are compiled together into the `automuse.exe` desktop application via PyInstaller or Nuitka. GitHub Actions builds the binary on every tagged release.

The desktop application ships with full dependencies: audio engine (PortAudio/JUCE for real-time I/O and synthesis), plugin hosting (VST3/AU/LV2), GUI framework (Qt or Electron), real-time processing -- everything deferred as "too heavy" for a pip package ships inside the app. Users download `automuse.exe` and run it.

The Python CLI remains available as the modular development/testing harness for contributors and CI.

---

*Conceived by Claude (Opus 4.5), February 2026. Layer 1 built by Claude (Opus 4.6), February 2026.*

*Every musician has a song they can hear but can't build. This is the tool that listens.*
