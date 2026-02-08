"""Note and pitch class representation for AutoMuse."""

from __future__ import annotations

PITCH_CLASS_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

ENHARMONIC_MAP: dict[str, str] = {
    "Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", "Ab": "G#",
    "Bb": "A#", "Cb": "B", "E#": "F", "B#": "C",
    "Dbb": "C", "Ebb": "D", "Fbb": "D#", "Gbb": "F", "Abb": "G",
    "Bbb": "A", "Cbb": "A#",
    "C##": "D", "D##": "E", "E##": "F#", "F##": "G", "G##": "A",
    "A##": "B", "B##": "C#",
}

# Display names that prefer flats for certain contexts
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


class PitchClass:
    """A pitch class (0-11) representing a note name independent of octave."""

    __slots__ = ("_value", "_name")

    def __init__(self, value: int | str) -> None:
        if isinstance(value, str):
            name = value.strip()
            canonical = ENHARMONIC_MAP.get(name, name)
            if canonical not in PITCH_CLASS_NAMES:
                raise ValueError(f"Unknown pitch class: {value!r}")
            self._value = PITCH_CLASS_NAMES.index(canonical)
            self._name = name if name in PITCH_CLASS_NAMES else canonical
        else:
            self._value = value % 12
            self._name = PITCH_CLASS_NAMES[self._value]

    @property
    def value(self) -> int:
        return self._value

    @property
    def name(self) -> str:
        return self._name

    def transpose(self, semitones: int) -> PitchClass:
        return PitchClass((self._value + semitones) % 12)

    def interval_to(self, other: PitchClass) -> int:
        return (other.value - self._value) % 12

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PitchClass):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"PitchClass({self._name!r})"

    def __str__(self) -> str:
        return self._name


class Note:
    """A concrete note with pitch class and octave (MIDI-compatible)."""

    __slots__ = ("_pitch_class", "_octave")

    def __init__(self, pitch_class: PitchClass | str, octave: int = 4) -> None:
        if isinstance(pitch_class, str):
            pitch_class = PitchClass(pitch_class)
        self._pitch_class = pitch_class
        self._octave = octave

    @classmethod
    def from_midi(cls, midi_number: int) -> Note:
        octave = (midi_number // 12) - 1
        pc = PitchClass(midi_number % 12)
        return cls(pc, octave)

    @classmethod
    def parse(cls, text: str) -> Note:
        """Parse a note string like 'C4', 'Bb3', 'F#5'."""
        text = text.strip()
        i = len(text) - 1
        while i >= 0 and (text[i].isdigit() or (i > 0 and text[i] == '-')):
            i -= 1
        name_part = text[: i + 1]
        octave_part = text[i + 1 :]
        octave = int(octave_part) if octave_part else 4
        return cls(PitchClass(name_part), octave)

    @property
    def pitch_class(self) -> PitchClass:
        return self._pitch_class

    @property
    def octave(self) -> int:
        return self._octave

    @property
    def midi(self) -> int:
        return (self._octave + 1) * 12 + self._pitch_class.value

    @property
    def frequency(self) -> float:
        """Concert pitch frequency in Hz (A4 = 440)."""
        return 440.0 * (2.0 ** ((self.midi - 69) / 12.0))

    def transpose(self, semitones: int) -> Note:
        new_midi = self.midi + semitones
        return Note.from_midi(new_midi)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Note):
            return self.midi == other.midi
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.midi)

    def __lt__(self, other: Note) -> bool:
        return self.midi < other.midi

    def __le__(self, other: Note) -> bool:
        return self.midi <= other.midi

    def __repr__(self) -> str:
        return f"Note({self._pitch_class.name!r}, {self._octave})"

    def __str__(self) -> str:
        return f"{self._pitch_class.name}{self._octave}"
