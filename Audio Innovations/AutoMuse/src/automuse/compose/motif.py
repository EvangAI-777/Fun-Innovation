"""Motif and pattern representation -- the atomic unit of composition."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.notes import Note, PitchClass
from ..core.rhythm import Duration, QUARTER
from ..core.scales import Scale
from ..core.keys import Key


@dataclass(frozen=True, slots=True)
class MotifNote:
    """A note-in-time: pitch + duration + velocity."""

    note: Note
    duration: Duration
    velocity: int = 80

    def __post_init__(self) -> None:
        if not 0 <= self.velocity <= 127:
            raise ValueError(f"Velocity must be 0-127, got {self.velocity}")

    def transpose(self, semitones: int) -> MotifNote:
        return MotifNote(self.note.transpose(semitones), self.duration, self.velocity)

    def __str__(self) -> str:
        return f"{self.note} ({self.duration}, v={self.velocity})"


REST_NOTE = None  # Sentinel for rests in motifs


class Motif:
    """An ordered sequence of MotifNote objects -- a reusable musical phrase.

    Supports classical transformations: transpose, invert, retrograde,
    augment, diminish. These are the building blocks of motivic development.
    """

    __slots__ = ("_notes", "_name")

    def __init__(self, notes: list[MotifNote], name: str = "") -> None:
        self._notes = list(notes)
        self._name = name

    @property
    def notes(self) -> list[MotifNote]:
        return list(self._notes)

    @property
    def name(self) -> str:
        return self._name

    @property
    def duration_ticks(self) -> int:
        return sum(mn.duration.ticks for mn in self._notes)

    @property
    def pitch_classes(self) -> list[PitchClass]:
        return [mn.note.pitch_class for mn in self._notes]

    def transpose(self, semitones: int) -> Motif:
        """Shift all pitches by the given number of semitones."""
        return Motif(
            [mn.transpose(semitones) for mn in self._notes],
            f"{self._name} T{semitones}" if self._name else "",
        )

    def invert(self, axis: Note | None = None) -> Motif:
        """Mirror pitches around an axis note (default: first note)."""
        if not self._notes:
            return Motif([], self._name)
        ax = axis if axis is not None else self._notes[0].note
        axis_midi = ax.midi
        inverted: list[MotifNote] = []
        for mn in self._notes:
            interval = mn.note.midi - axis_midi
            new_note = Note.from_midi(axis_midi - interval)
            inverted.append(MotifNote(new_note, mn.duration, mn.velocity))
        return Motif(
            inverted,
            f"{self._name} I" if self._name else "",
        )

    def retrograde(self) -> Motif:
        """Reverse the note order (durations follow their notes)."""
        return Motif(
            list(reversed(self._notes)),
            f"{self._name} R" if self._name else "",
        )

    def augment(self, factor: float = 2.0) -> Motif:
        """Stretch all durations by a factor (>1 = slower)."""
        stretched: list[MotifNote] = []
        for mn in self._notes:
            new_dur = Duration(int(mn.duration.ticks * factor), f"{mn.duration.name} aug")
            stretched.append(MotifNote(mn.note, new_dur, mn.velocity))
        return Motif(stretched, self._name)

    def diminish(self, factor: float = 2.0) -> Motif:
        """Compress all durations by a factor (>1 = faster)."""
        compressed: list[MotifNote] = []
        for mn in self._notes:
            new_ticks = max(1, int(mn.duration.ticks / factor))
            new_dur = Duration(new_ticks, f"{mn.duration.name} dim")
            compressed.append(MotifNote(mn.note, new_dur, mn.velocity))
        return Motif(compressed, self._name)

    def in_key(self, key: Key) -> bool:
        """Check if all pitches are diatonic to the given key."""
        scale_pcs = set(key.scale.pitch_classes())
        return all(mn.note.pitch_class in scale_pcs for mn in self._notes)

    def to_notes(self) -> list[Note]:
        """Extract just the Note objects (pitch + octave, no rhythm/velocity)."""
        return [mn.note for mn in self._notes]

    def __len__(self) -> int:
        return len(self._notes)

    def __getitem__(self, index: int) -> MotifNote:
        return self._notes[index]

    def __iter__(self):
        return iter(self._notes)

    def __repr__(self) -> str:
        name_part = f" {self._name!r}" if self._name else ""
        return f"Motif({len(self._notes)} notes{name_part})"

    def __str__(self) -> str:
        if not self._notes:
            return "(empty motif)"
        note_strs = [str(mn.note) for mn in self._notes]
        return " → ".join(note_strs)


class MotifBuilder:
    """Factory methods for building motifs from various inputs."""

    @staticmethod
    def from_degrees(
        scale: Scale,
        degrees: list[int],
        octave: int = 4,
        duration: Duration = QUARTER,
        velocity: int = 80,
    ) -> Motif:
        """Build a motif from 1-indexed scale degrees."""
        notes: list[MotifNote] = []
        scale_notes = scale.notes(octave)
        degree_count = len(scale_notes)
        for deg in degrees:
            # Handle degrees beyond the scale's range by wrapping octaves
            base_deg = ((deg - 1) % degree_count)
            octave_offset = (deg - 1) // degree_count
            base_note = scale_notes[base_deg]
            note = base_note.transpose(12 * octave_offset)
            notes.append(MotifNote(note, duration, velocity))
        return Motif(notes)

    @staticmethod
    def from_notes(
        note_strings: list[str],
        duration: Duration = QUARTER,
        velocity: int = 80,
    ) -> Motif:
        """Build a motif from note name strings like ['C4', 'E4', 'G4']."""
        notes: list[MotifNote] = []
        for ns in note_strings:
            notes.append(MotifNote(Note.parse(ns), duration, velocity))
        return Motif(notes)

    @staticmethod
    def from_intervals(
        root: Note,
        intervals: list[int],
        duration: Duration = QUARTER,
        velocity: int = 80,
    ) -> Motif:
        """Build a motif from a root note and semitone intervals."""
        notes: list[MotifNote] = [MotifNote(root, duration, velocity)]
        current = root
        for interval in intervals:
            current = current.transpose(interval)
            notes.append(MotifNote(current, duration, velocity))
        return Motif(notes)
