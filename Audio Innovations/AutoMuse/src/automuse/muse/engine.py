"""The Muse -- AutoMuse's conversational music theory engine.

Layer 1 implementation: text-based interaction producing theory analysis,
scale/chord/progression output, and MIDI export. No audio engine, no GUI --
pure music knowledge made conversational.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from automuse.core.notes import PitchClass, Note
from automuse.core.scales import Scale, SCALE_TYPES
from automuse.core.chords import Chord, CHORD_TYPES
from automuse.core.keys import Key
from automuse.core.rhythm import Tempo, TimeSignature, COMMON_TIME, Duration, WHOLE, QUARTER
from automuse.harmony.progressions import ProgressionBuilder, Progression
from automuse.harmony.voicing import voice_chord, VoicingStyle
from automuse.harmony.analysis import analyze_progression
from automuse.midi.writer import MidiWriter
from automuse.compose.motif import Motif, MotifNote
from automuse.compose.melody import MelodyGenerator, MelodyConfig, MelodyContour
from automuse.compose.arrangement import Arrangement, Section, SectionType, ArrangementTemplates
from automuse.export.musicxml import MusicXMLWriter
from .commands import parse_command, Command


class Muse:
    """The conversational music theory engine.

    Maintains session state (current key, tempo, time signature) and
    responds to commands with theory-backed output.
    """

    def __init__(self) -> None:
        self._key: Key = Key("C", "major")
        self._tempo: Tempo = Tempo(120)
        self._time_sig: TimeSignature = COMMON_TIME
        self._last_progression: Progression | None = None
        self._last_melody: Motif | None = None
        self._last_arrangement: Arrangement | None = None
        self._melody_gen: MelodyGenerator = MelodyGenerator()
        self._history: list[tuple[str, str]] = []

    # --- State accessors ---

    @property
    def key(self) -> Key:
        return self._key

    @property
    def tempo(self) -> Tempo:
        return self._tempo

    @property
    def time_signature(self) -> TimeSignature:
        return self._time_sig

    @property
    def last_progression(self) -> Progression | None:
        return self._last_progression

    @property
    def last_melody(self) -> Motif | None:
        return self._last_melody

    @property
    def last_arrangement(self) -> Arrangement | None:
        return self._last_arrangement

    # --- Main entry point ---

    def respond(self, user_input: str) -> str:
        """Process user input and return the Muse's response."""
        cmd = parse_command(user_input)
        handler = getattr(self, f"_handle_{cmd.action}", None)
        if handler:
            response = handler(cmd)
        else:
            response = self._handle_chat(cmd)
        self._history.append((user_input, response))
        return response

    # --- Command handlers ---

    def _handle_empty(self, cmd: Command) -> str:
        return "I'm listening. What do you want to make?"

    def _handle_help(self, cmd: Command) -> str:
        return (
            "Available commands:\n"
            "  scale <root> <type>        -- Show a scale (e.g. scale D dorian)\n"
            "  chord <symbol>             -- Show a chord (e.g. chord Cmaj7)\n"
            "  key <root> <major|minor>   -- Set the working key\n"
            "  progression <template>     -- Generate a progression (e.g. progression ii-V-I)\n"
            "  tempo <bpm>                -- Set tempo\n"
            "  time <n>/<d>               -- Set time signature\n"
            "  voicing <symbol> <style>   -- Voice a chord (styles: close, drop 2, spread, shell)\n"
            "  analyze                    -- Analyze the last progression\n"
            "  modulate <root> <quality>  -- Find pivot chords to a new key\n"
            "  transpose <semitones>      -- Transpose the current key\n"
            "  suggest                    -- Suggest a progression for the current key\n"
            "  melody [len] [contour]     -- Generate a melody (e.g. melody 8 arch)\n"
            "  motif <transform> [args]   -- Transform last melody (transpose, invert, retrograde)\n"
            "  arrange [template]         -- Create arrangement (e.g. arrange pop, arrange aaba)\n"
            "  export [filename]          -- Export last progression/melody as MIDI\n"
            "  exportxml [filename]       -- Export last melody/progression as MusicXML\n"
            "  save [name]                -- Save session state to file\n"
            "  load <name>                -- Load session state from file\n"
            "  help                       -- Show this help\n"
            "  quit                       -- Exit\n"
            f"\nCurrent session: {self._key.name} | {self._tempo} | {self._time_sig}"
        )

    def _handle_scale(self, cmd: Command) -> str:
        if len(cmd.args) < 2:
            return "Usage: scale <root> <type> (e.g. scale D dorian)"
        root = cmd.args[0]
        scale_type = " ".join(cmd.args[1:]).lower()
        try:
            scale = Scale(root, scale_type)
        except ValueError as e:
            return str(e)
        pcs = scale.pitch_classes()
        notes = scale.notes()
        return (
            f"{scale.name}\n"
            f"Notes: {' '.join(str(pc) for pc in pcs)}\n"
            f"MIDI: {' '.join(str(n) for n in notes)}\n"
            f"Intervals: {' '.join(str(i) for i in scale.scale_type.intervals)}\n"
            f"Degrees: {scale.scale_type.degree_count}"
        )

    def _handle_chord(self, cmd: Command) -> str:
        if not cmd.args:
            return "Usage: chord <symbol> (e.g. chord Cmaj7, chord Bbm)"
        symbol = cmd.args[0]
        try:
            chord = Chord.parse(symbol)
        except ValueError as e:
            return str(e)
        pcs = chord.pitch_classes()
        notes = chord.notes()
        return (
            f"{chord.symbol} ({chord.chord_type.name})\n"
            f"Notes: {' '.join(str(pc) for pc in pcs)}\n"
            f"MIDI: {' '.join(str(n) for n in notes)}\n"
            f"Intervals: {chord.chord_type.intervals}"
        )

    def _handle_key(self, cmd: Command) -> str:
        if len(cmd.args) < 2:
            return f"Current key: {self._key.name}\nUsage: key <root> <major|minor>"
        root = cmd.args[0]
        quality = cmd.args[1].lower()
        try:
            self._key = Key(root, quality)
        except ValueError as e:
            return str(e)
        triads = self._key.diatonic_triads()
        roman_str = " ".join(dc.roman for dc in triads)
        rel = self._key.relative()
        par = self._key.parallel()
        return (
            f"Key set to {self._key.name}\n"
            f"Signature: {self._key.signature} ({'sharps' if self._key.signature >= 0 else 'flats'})\n"
            f"Diatonic triads: {roman_str}\n"
            f"Relative: {rel.name} | Parallel: {par.name}"
        )

    def _handle_progression(self, cmd: Command) -> str:
        if not cmd.args:
            templates = ProgressionBuilder.available_templates()
            return "Available templates:\n  " + "\n  ".join(templates)
        template = " ".join(cmd.args)
        builder = ProgressionBuilder(self._key)
        try:
            prog = builder.from_template(template)
        except ValueError as e:
            return str(e)
        self._last_progression = prog
        chord_names = " | ".join(str(s.chord) for s in prog.steps)
        roman_names = " | ".join(s.roman for s in prog.steps)
        return (
            f"Progression in {self._key.name}:\n"
            f"Roman: {roman_names}\n"
            f"Chords: {chord_names}\n"
            f"({len(prog)} chords, export with 'export')"
        )

    def _handle_tempo(self, cmd: Command) -> str:
        if not cmd.args:
            return f"Current tempo: {self._tempo}"
        try:
            bpm = float(cmd.args[0])
            self._tempo = Tempo(bpm)
        except (ValueError, IndexError):
            return "Usage: tempo <bpm> (e.g. tempo 120)"
        return f"Tempo set to {self._tempo}"

    def _handle_time(self, cmd: Command) -> str:
        if not cmd.args:
            return f"Current time signature: {self._time_sig}"
        try:
            parts = cmd.args[0].split("/")
            num, den = int(parts[0]), int(parts[1])
            self._time_sig = TimeSignature(num, den)
        except (ValueError, IndexError):
            return "Usage: time <n>/<d> (e.g. time 3/4, time 7/8)"
        return f"Time signature set to {self._time_sig} ({self._time_sig.feel})"

    def _handle_voicing(self, cmd: Command) -> str:
        if len(cmd.args) < 1:
            styles = ", ".join(s.value for s in VoicingStyle)
            return f"Usage: voicing <chord> [style]\nStyles: {styles}"
        try:
            chord = Chord.parse(cmd.args[0])
        except ValueError as e:
            return str(e)
        style = VoicingStyle.ROOT_POSITION
        if len(cmd.args) >= 2:
            style_name = " ".join(cmd.args[1:]).lower()
            for s in VoicingStyle:
                if s.value == style_name:
                    style = s
                    break
        notes = voice_chord(chord, style)
        return (
            f"{chord.symbol} voiced as {style.value}:\n"
            f"Notes: {' '.join(str(n) for n in notes)}\n"
            f"MIDI: {', '.join(str(n.midi) for n in notes)}"
        )

    def _handle_analyze(self, cmd: Command) -> str:
        if self._last_progression is None:
            return "Nothing to analyze. Generate a progression first."
        results = analyze_progression(self._last_progression)
        lines = [f"Analysis of progression in {self._key.name}:"]
        for r in results:
            lines.append(f"  {r.roman:8s} {str(r.chord):8s} -> {r.function}")
        return "\n".join(lines)

    def _handle_modulate(self, cmd: Command) -> str:
        if len(cmd.args) < 2:
            return "Usage: modulate <root> <major|minor>"
        try:
            target = Key(cmd.args[0], cmd.args[1])
        except ValueError as e:
            return str(e)
        pivots = self._key.pivot_chords(target)
        if not pivots:
            return (
                f"No common diatonic triads between {self._key.name} "
                f"and {target.name}. Try a direct or chromatic modulation."
            )
        lines = [f"Pivot chords from {self._key.name} to {target.name}:"]
        for mine, theirs in pivots:
            lines.append(f"  {mine.chord.symbol}: {mine.roman} -> {theirs.roman}")
        return "\n".join(lines)

    def _handle_transpose(self, cmd: Command) -> str:
        if not cmd.args:
            return "Usage: transpose <semitones> (e.g. transpose 5, transpose -2)"
        try:
            semitones = int(cmd.args[0])
        except ValueError:
            return "Usage: transpose <semitones> (must be an integer)"
        new_root = self._key.root.transpose(semitones)
        self._key = Key(new_root, self._key.quality)
        return f"Key transposed to {self._key.name}"

    def _handle_suggest(self, cmd: Command) -> str:
        builder = ProgressionBuilder(self._key)
        suggestions = [
            ("I-IV-V-I", "Classic cadential progression"),
            ("I-V-vi-IV", "The 'pop' progression (Axis of Awesome)"),
            ("ii-V-I", "Jazz standard turnaround"),
            ("vi-IV-I-V", "Emotional pop/rock (minor start)"),
            ("I-vi-IV-V", "50s/doo-wop progression"),
        ]
        if self._key.quality == "minor":
            suggestions = [
                ("i-bVI-bIII-bVII", "Natural minor descending"),
                ("ii-V-I", "Jazz minor turnaround"),
                ("I-IV-V-I", "Minor cadential"),
                ("vi-IV-I-V", "Borrowed from relative major"),
                ("12-bar blues", "Blues in minor"),
            ]
        lines = [f"Suggestions for {self._key.name}:"]
        for name, desc in suggestions:
            try:
                prog = builder.from_template(name)
                chords = " | ".join(str(s.chord) for s in prog.steps[:4])
                if len(prog) > 4:
                    chords += " | ..."
                lines.append(f"  {name:25s} {desc}\n{'':27s}{chords}")
            except ValueError:
                lines.append(f"  {name:25s} {desc}")
        return "\n".join(lines)

    def _handle_melody(self, cmd: Command) -> str:
        length = 8
        contour = MelodyContour.ARCH
        step_bias = 0.7

        for arg in cmd.args:
            arg_lower = arg.lower()
            if arg_lower.isdigit():
                length = int(arg_lower)
            elif arg_lower == "stepwise":
                step_bias = 0.9
            elif arg_lower == "skippy":
                step_bias = 0.3
            else:
                for c in MelodyContour:
                    if c.value == arg_lower:
                        contour = c
                        break

        scale = self._key.scale
        config = MelodyConfig(scale, octave=4, length=length, contour=contour, step_bias=step_bias)
        self._last_melody = self._melody_gen.generate(config)

        note_strs = " ".join(str(mn.note) for mn in self._last_melody)
        return (
            f"Generated {length}-note melody in {self._key.name} ({contour.value} contour):\n"
            f"  {note_strs}\n"
            f"({self._last_melody.duration_ticks} ticks. "
            f"Transform with 'motif', export with 'export' or 'exportxml')"
        )

    def _handle_motif(self, cmd: Command) -> str:
        if self._last_melody is None:
            return "No melody to transform. Generate one with 'melody' first."
        if not cmd.args:
            return (
                "Usage: motif <transform> [args]\n"
                "  motif transpose <semitones>  -- Shift all pitches\n"
                "  motif invert                 -- Mirror pitches around first note\n"
                "  motif retrograde             -- Reverse note order\n"
                "  motif augment                -- Double all durations\n"
                "  motif diminish               -- Halve all durations"
            )

        transform = cmd.args[0].lower()

        if transform == "transpose":
            semitones = int(cmd.args[1]) if len(cmd.args) > 1 else 2
            self._last_melody = self._last_melody.transpose(semitones)
            label = f"transposed {semitones} semitones"
        elif transform == "invert":
            self._last_melody = self._last_melody.invert()
            label = "inverted"
        elif transform == "retrograde":
            self._last_melody = self._last_melody.retrograde()
            label = "retrograded"
        elif transform == "augment":
            self._last_melody = self._last_melody.augment()
            label = "augmented (2x duration)"
        elif transform == "diminish":
            self._last_melody = self._last_melody.diminish()
            label = "diminished (0.5x duration)"
        else:
            return f"Unknown transform: {transform}. Try transpose, invert, retrograde, augment, diminish."

        note_strs = " ".join(str(mn.note) for mn in self._last_melody)
        return f"Melody {label}:\n  {note_strs}"

    def _handle_arrange(self, cmd: Command) -> str:
        templates = {
            "pop": ArrangementTemplates.pop,
            "verse-chorus": ArrangementTemplates.verse_chorus,
            "aaba": ArrangementTemplates.aaba,
            "blues": ArrangementTemplates.blues_12bar,
            "12-bar": ArrangementTemplates.blues_12bar,
            "through-composed": ArrangementTemplates.through_composed,
        }

        if not cmd.args:
            if self._last_arrangement:
                return f"Current arrangement: {self._last_arrangement.section_map}"
            available = ", ".join(sorted(templates))
            return f"Usage: arrange <template>\nTemplates: {available}"

        template_name = cmd.args[0].lower()
        if template_name not in templates:
            available = ", ".join(sorted(templates))
            return f"Unknown template: {template_name}. Available: {available}"

        sections = templates[template_name]()
        self._last_arrangement = Arrangement(
            title=f"AutoMuse {template_name.title()}",
            key=self._key,
            tempo=self._tempo,
            time_sig=self._time_sig,
        )
        for section in sections:
            self._last_arrangement.add_section(section)

        return (
            f"Arrangement ({template_name}) in {self._key.name} at {self._tempo}:\n"
            f"  {self._last_arrangement.section_map}\n"
            f"  {self._last_arrangement.total_bars} bars, "
            f"~{self._last_arrangement.duration_seconds:.0f}s"
        )

    def _handle_save(self, cmd: Command) -> str:
        import json
        name = cmd.args[0] if cmd.args else "session"
        filename = f"{name}.automuse.json"
        state = {
            "key": self._key.name,
            "tempo": self._tempo.bpm,
            "time_sig": str(self._time_sig),
        }
        if self._last_arrangement:
            state["arrangement"] = self._last_arrangement.to_dict()
        Path(filename).write_text(json.dumps(state, indent=2))
        return f"Session saved to {filename}"

    def _handle_load(self, cmd: Command) -> str:
        import json
        if not cmd.args:
            return "Usage: load <name> (e.g. load mysession)"
        name = cmd.args[0]
        filename = f"{name}.automuse.json"
        path = Path(filename)
        if not path.exists():
            return f"File not found: {filename}"
        state = json.loads(path.read_text())
        key_parts = state["key"].split()
        self._key = Key(key_parts[0], key_parts[1] if len(key_parts) > 1 else "major")
        self._tempo = Tempo(state["tempo"])
        ts_parts = state["time_sig"].split("/")
        self._time_sig = TimeSignature(int(ts_parts[0]), int(ts_parts[1]))
        if "arrangement" in state:
            self._last_arrangement = Arrangement.from_dict(state["arrangement"])
        return (
            f"Session loaded from {filename}\n"
            f"  Key: {self._key.name} | Tempo: {self._tempo} | Time: {self._time_sig}"
        )

    def _handle_exportxml(self, cmd: Command) -> str:
        if self._last_melody is None and self._last_progression is None:
            return "Nothing to export. Generate a melody or progression first."
        filename = cmd.args[0] if cmd.args else None
        if filename is None:
            filename = tempfile.mktemp(suffix=".musicxml", prefix="automuse_")
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".musicxml")

        writer = MusicXMLWriter(title="AutoMuse Export", composer="AutoMuse")
        pid = writer.add_part("Piano")

        if self._last_melody is not None:
            writer.write_notes(pid, list(self._last_melody), key=self._key, time_sig=self._time_sig)
            what = f"melody ({len(self._last_melody)} notes)"
        elif self._last_progression is not None:
            writer.write_chord_symbols(pid, self._last_progression)
            what = f"progression ({len(self._last_progression)} chords)"
        else:
            return "Nothing to export."

        writer.save(path)
        return f"Exported {what} to {path}"

    def _handle_export(self, cmd: Command) -> str:
        if self._last_progression is None and self._last_melody is None:
            return "Nothing to export. Generate a progression or melody first."
        filename = cmd.args[0] if cmd.args else None
        if filename is None:
            filename = tempfile.mktemp(suffix=".mid", prefix="automuse_")
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".mid")
        writer = MidiWriter()
        track = writer.add_track("AutoMuse Export")
        track.set_tempo(0, self._tempo)
        track.set_time_signature(0, self._time_sig)

        if self._last_melody is not None:
            tick = 0
            for mn in self._last_melody:
                writer.write_note(track, mn.note, tick, mn.duration, mn.velocity)
                tick += mn.duration.ticks
            writer.save(path)
            return f"Exported melody to {path} ({len(self._last_melody)} notes, {self._tempo})"

        if self._last_progression is not None:
            writer.write_progression(track, self._last_progression, start_tick=0, octave=3)
            writer.save(path)
            return f"Exported to {path} ({len(self._last_progression)} chords, {self._tempo})"

        return "Nothing to export."

    def _handle_quit(self, cmd: Command) -> str:
        return "SESSION_END"

    def _handle_chat(self, cmd: Command) -> str:
        text = cmd.raw.lower()
        words = set(text.split())
        # Basic conversational responses for Layer 1
        if words & {"hello", "hi", "hey"}:
            return f"Hey! I'm the Muse. We're in {self._key.name} at {self._tempo}. What do you want to make?"
        if "sad" in text or "melanchol" in text:
            self._key = Key("D", "minor")
            return (
                "I hear you. Let's move to D minor -- the saddest of all keys.\n"
                f"Key set to {self._key.name}. Try 'suggest' for some progressions."
            )
        if "happy" in text or "bright" in text or "uplifting" in text:
            self._key = Key("C", "major")
            return (
                "Something bright! C major is wide open.\n"
                f"Key set to {self._key.name}. Try 'suggest' for some progressions."
            )
        if "jazz" in text:
            self._key = Key("Bb", "major")
            self._tempo = Tempo(132)
            return (
                "Jazz -- nice. Bb major is the jazz home key. Tempo at 132.\n"
                "Try 'progression ii-V-I' to start, or 'suggest' for more options."
            )
        if "blues" in text:
            self._key = Key("E", "major")
            self._tempo = Tempo(96)
            return (
                "The blues. E major, 96 BPM, shuffle feel.\n"
                "Try 'progression 12-bar blues' to lay it down."
            )
        return (
            f"I'm working in {self._key.name} at {self._tempo}. "
            "Try 'help' to see what I can do, or describe a mood and I'll set the stage."
        )

    def _handle_play(self, cmd: Command) -> str:
        return (
            "Layer 1 is text + MIDI only -- no audio playback yet. "
            "Export with 'export' and open in your DAW or MIDI player."
        )
