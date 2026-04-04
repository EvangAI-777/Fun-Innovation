"""Score model -- multi-track composition container with MIDI/MusicXML export.

The Score assembles Parts (melody, harmony, bass, drums, countermelody, pad)
into a unified, exportable composition. Each Part becomes a separate track in
MIDI (Type 1) or a separate part/staff in MusicXML.
"""

from __future__ import annotations

from enum import Enum

from ..core.notes import Note
from ..core.keys import Key
from ..core.rhythm import Tempo, TimeSignature, Duration, COMMON_TIME, QUARTER
from ..midi.writer import MidiWriter, MidiTrack
from ..export.musicxml import MusicXMLWriter
from .motif import Motif, MotifNote
from .drums import DrumPattern


class InstrumentType(Enum):
    """Instrument roles within a score."""

    MELODY = "melody"
    HARMONY = "harmony"
    BASS = "bass"
    DRUMS = "drums"
    COUNTER_MELODY = "counter_melody"
    PAD = "pad"


# Default GM program numbers for each instrument type
_GM_PROGRAMS: dict[InstrumentType, int] = {
    InstrumentType.MELODY: 0,        # Acoustic Grand Piano
    InstrumentType.HARMONY: 0,       # Piano
    InstrumentType.BASS: 32,         # Acoustic Bass
    InstrumentType.DRUMS: 0,         # N/A (channel 9)
    InstrumentType.COUNTER_MELODY: 73,  # Flute
    InstrumentType.PAD: 48,          # String Ensemble
}


class Part:
    """A single instrument part within a score."""

    __slots__ = ("name", "instrument_type", "channel", "motif", "drum_pattern")

    def __init__(
        self,
        name: str,
        instrument_type: InstrumentType,
        channel: int = 0,
        motif: Motif | None = None,
        drum_pattern: DrumPattern | None = None,
    ) -> None:
        if not 0 <= channel <= 15:
            raise ValueError(f"MIDI channel must be 0-15, got {channel}")
        self.name = name
        self.instrument_type = instrument_type
        self.channel = channel
        self.motif = motif
        self.drum_pattern = drum_pattern

    @property
    def is_drums(self) -> bool:
        return self.channel == 9

    @property
    def total_ticks(self) -> int:
        if self.motif is not None:
            return self.motif.duration_ticks
        if self.drum_pattern is not None:
            return self.drum_pattern.ticks
        return 0

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "instrument_type": self.instrument_type.value,
            "channel": self.channel,
        }
        if self.motif is not None:
            d["motif"] = [
                {"note": str(mn.note), "duration_ticks": mn.duration.ticks, "velocity": mn.velocity}
                for mn in self.motif
            ]
        if self.drum_pattern is not None:
            d["drum_pattern"] = [
                {"instrument": h.instrument.value, "tick": h.tick, "velocity": h.velocity}
                for h in self.drum_pattern.hits
            ]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Part:
        from .drums import DrumHit, GMPercussion
        inst_type = InstrumentType(d["instrument_type"])
        motif = None
        if "motif" in d:
            notes = []
            for nd in d["motif"]:
                note = Note.parse(nd["note"])
                dur = Duration(nd["duration_ticks"], "loaded")
                notes.append(MotifNote(note, dur, nd["velocity"]))
            motif = Motif(notes)

        drum_pattern = None
        if "drum_pattern" in d:
            hits = [
                DrumHit(GMPercussion(h["instrument"]), h["tick"], h["velocity"])
                for h in d["drum_pattern"]
            ]
            drum_pattern = DrumPattern(hits)

        return cls(d["name"], inst_type, d["channel"], motif, drum_pattern)

    def __repr__(self) -> str:
        return f"Part({self.name!r}, {self.instrument_type.value}, ch={self.channel})"


class Score:
    """Top-level composition container combining multiple Parts."""

    __slots__ = ("_title", "_key", "_tempo", "_time_sig", "_parts", "_arrangement")

    def __init__(
        self,
        title: str = "Untitled",
        key: Key | None = None,
        tempo: Tempo | None = None,
        time_sig: TimeSignature = COMMON_TIME,
        arrangement: object | None = None,
    ) -> None:
        self._title = title
        self._key = key
        self._tempo = tempo or Tempo(120)
        self._time_sig = time_sig
        self._parts: dict[str, Part] = {}
        self._arrangement = arrangement

    @property
    def title(self) -> str:
        return self._title

    @property
    def key(self) -> Key | None:
        return self._key

    @property
    def tempo(self) -> Tempo:
        return self._tempo

    @property
    def time_sig(self) -> TimeSignature:
        return self._time_sig

    @property
    def parts(self) -> list[Part]:
        return list(self._parts.values())

    @property
    def total_ticks(self) -> int:
        if not self._parts:
            return 0
        return max(p.total_ticks for p in self._parts.values())

    @property
    def duration_seconds(self) -> float:
        ticks = self.total_ticks
        if ticks == 0:
            return 0.0
        beats = ticks / QUARTER.ticks
        return beats * (60.0 / self._tempo.bpm)

    def add_part(self, part: Part) -> None:
        self._parts[part.name] = part

    def remove_part(self, name: str) -> None:
        if name in self._parts:
            del self._parts[name]

    def get_part(self, name: str) -> Part | None:
        return self._parts.get(name)

    def to_midi(self, writer: MidiWriter | None = None) -> MidiWriter:
        """Render all parts into a multi-track MIDI file (Type 1)."""
        if writer is None:
            writer = MidiWriter()

        # Conductor track with tempo and time signature
        conductor = writer.add_track("Conductor")
        conductor.set_tempo(0, self._tempo)
        conductor.set_time_signature(0, self._time_sig)

        for part in self._parts.values():
            track = writer.add_track(part.name)

            if part.is_drums and part.drum_pattern is not None:
                # Drum parts: write hits to channel 9
                for hit in part.drum_pattern.hits:
                    track.add_note(hit.tick, hit.instrument.value, QUARTER.ticks // 2, hit.velocity, 9)
            elif part.motif is not None:
                # Melodic parts: write notes on assigned channel
                program = _GM_PROGRAMS.get(part.instrument_type, 0)
                track.program_change(0, program, part.channel)
                tick = 0
                for mn in part.motif:
                    track.add_note(tick, mn.note.midi, mn.duration.ticks, mn.velocity, part.channel)
                    tick += mn.duration.ticks

        return writer

    def to_musicxml(self, writer: MusicXMLWriter | None = None) -> MusicXMLWriter:
        """Render all parts as separate MusicXML parts."""
        if writer is None:
            writer = MusicXMLWriter(title=self._title)

        for part in self._parts.values():
            part_id = writer.add_part(part.name, part.name)
            if part.motif is not None:
                writer.write_notes(part_id, list(part.motif), self._key, self._time_sig)

        return writer

    def to_dict(self) -> dict:
        d: dict = {
            "title": self._title,
            "tempo": self._tempo.bpm,
            "time_sig": f"{self._time_sig.numerator}/{self._time_sig.denominator}",
            "parts": {name: p.to_dict() for name, p in self._parts.items()},
        }
        if self._key is not None:
            d["key"] = {"root": self._key.root.name, "quality": self._key.quality}
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Score:
        key = None
        if "key" in d:
            key = Key(d["key"]["root"], d["key"]["quality"])
        tempo = Tempo(d["tempo"])
        ts_parts = d["time_sig"].split("/")
        time_sig = TimeSignature(int(ts_parts[0]), int(ts_parts[1]))
        score = cls(d["title"], key, tempo, time_sig)
        for name, pd in d["parts"].items():
            score.add_part(Part.from_dict(pd))
        return score

    def __repr__(self) -> str:
        return f"Score({self._title!r}, {len(self._parts)} parts)"


class ScoreBuilder:
    """Convenience factory for building common score configurations."""

    @staticmethod
    def from_parts(
        title: str = "Composition",
        key: Key | None = None,
        tempo: Tempo | None = None,
        time_sig: TimeSignature = COMMON_TIME,
        melody: Motif | None = None,
        bass: Motif | None = None,
        drums: DrumPattern | None = None,
        counter: Motif | None = None,
    ) -> Score:
        """Build a score from individual parts."""
        score = Score(title, key, tempo, time_sig)
        ch = 0
        if melody is not None:
            score.add_part(Part("Melody", InstrumentType.MELODY, ch, motif=melody))
            ch += 1
        if bass is not None:
            score.add_part(Part("Bass", InstrumentType.BASS, ch, motif=bass))
            ch += 1
        if counter is not None:
            score.add_part(Part("Counter Melody", InstrumentType.COUNTER_MELODY, ch, motif=counter))
            ch += 1
        if drums is not None:
            score.add_part(Part("Drums", InstrumentType.DRUMS, 9, drum_pattern=drums))
        return score

    @staticmethod
    def quick_band(
        key: Key,
        tempo: Tempo | None = None,
        time_sig: TimeSignature = COMMON_TIME,
        melody: Motif | None = None,
        bass: Motif | None = None,
        drums: DrumPattern | None = None,
    ) -> Score:
        """Build a quick 3+ part band arrangement.

        If bass or drums are not provided, creates minimal placeholders:
        - Bass defaults to root notes from the key
        - Drums defaults to a basic kick-snare pattern
        """
        from .drums import DrumPatternBuilder
        score = Score("Quick Band", key, tempo, time_sig)

        if melody is not None:
            score.add_part(Part("Melody", InstrumentType.MELODY, 0, motif=melody))

        if bass is not None:
            score.add_part(Part("Bass", InstrumentType.BASS, 1, motif=bass))
        else:
            # Minimal bass: root note for 4 beats
            root = Note(key.root, 2)
            from ..core.rhythm import WHOLE
            bass_motif = Motif([MotifNote(root, WHOLE, 90)], "bass:auto")
            score.add_part(Part("Bass", InstrumentType.BASS, 1, motif=bass_motif))

        if drums is not None:
            score.add_part(Part("Drums", InstrumentType.DRUMS, 9, drum_pattern=drums))
        else:
            drum_pat = DrumPatternBuilder.rock(time_sig)
            score.add_part(Part("Drums", InstrumentType.DRUMS, 9, drum_pattern=drum_pat))

        return score

    def __repr__(self) -> str:
        return "ScoreBuilder()"
