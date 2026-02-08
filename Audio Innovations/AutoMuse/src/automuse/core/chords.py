"""Chord types, construction, voicings, and inversions."""

from __future__ import annotations

from dataclasses import dataclass

from .notes import PitchClass, Note


@dataclass(frozen=True)
class ChordType:
    """A chord quality defined by intervals from root (in semitones)."""

    name: str
    symbol: str
    intervals: tuple[int, ...]


# --- Triads ---
MAJOR_TRIAD = ChordType("major", "", (0, 4, 7))
MINOR_TRIAD = ChordType("minor", "m", (0, 3, 7))
DIMINISHED_TRIAD = ChordType("diminished", "dim", (0, 3, 6))
AUGMENTED_TRIAD = ChordType("augmented", "aug", (0, 4, 8))
SUS2 = ChordType("sus2", "sus2", (0, 2, 7))
SUS4 = ChordType("sus4", "sus4", (0, 5, 7))

# --- Seventh chords ---
MAJOR_7 = ChordType("major 7th", "maj7", (0, 4, 7, 11))
MINOR_7 = ChordType("minor 7th", "m7", (0, 3, 7, 10))
DOMINANT_7 = ChordType("dominant 7th", "7", (0, 4, 7, 10))
DIMINISHED_7 = ChordType("diminished 7th", "dim7", (0, 3, 6, 9))
HALF_DIMINISHED_7 = ChordType("half-diminished 7th", "m7b5", (0, 3, 6, 10))
MINOR_MAJOR_7 = ChordType("minor-major 7th", "mMaj7", (0, 3, 7, 11))
AUGMENTED_7 = ChordType("augmented 7th", "aug7", (0, 4, 8, 10))
AUGMENTED_MAJOR_7 = ChordType("augmented major 7th", "augMaj7", (0, 4, 8, 11))

# --- Extended chords ---
DOMINANT_9 = ChordType("dominant 9th", "9", (0, 4, 7, 10, 14))
MAJOR_9 = ChordType("major 9th", "maj9", (0, 4, 7, 11, 14))
MINOR_9 = ChordType("minor 9th", "m9", (0, 3, 7, 10, 14))
DOMINANT_11 = ChordType("dominant 11th", "11", (0, 4, 7, 10, 14, 17))
DOMINANT_13 = ChordType("dominant 13th", "13", (0, 4, 7, 10, 14, 17, 21))

# --- Added-tone chords ---
ADD9 = ChordType("add9", "add9", (0, 4, 7, 14))
MINOR_ADD9 = ChordType("minor add9", "madd9", (0, 3, 7, 14))
SIX = ChordType("6th", "6", (0, 4, 7, 9))
MINOR_SIX = ChordType("minor 6th", "m6", (0, 3, 7, 9))

# --- Power chord ---
POWER = ChordType("power", "5", (0, 7))

CHORD_TYPES: dict[str, ChordType] = {}

for _ct in [
    MAJOR_TRIAD, MINOR_TRIAD, DIMINISHED_TRIAD, AUGMENTED_TRIAD, SUS2, SUS4,
    MAJOR_7, MINOR_7, DOMINANT_7, DIMINISHED_7, HALF_DIMINISHED_7,
    MINOR_MAJOR_7, AUGMENTED_7, AUGMENTED_MAJOR_7,
    DOMINANT_9, MAJOR_9, MINOR_9, DOMINANT_11, DOMINANT_13,
    ADD9, MINOR_ADD9, SIX, MINOR_SIX, POWER,
]:
    CHORD_TYPES[_ct.name] = _ct
    CHORD_TYPES[_ct.symbol] = _ct

# Common aliases
CHORD_TYPES["maj"] = MAJOR_TRIAD
CHORD_TYPES["min"] = MINOR_TRIAD
CHORD_TYPES["M"] = MAJOR_TRIAD
CHORD_TYPES["M7"] = MAJOR_7


class Chord:
    """A concrete chord: root + chord type, with optional inversion."""

    __slots__ = ("_root", "_chord_type", "_inversion")

    def __init__(
        self,
        root: PitchClass | str,
        chord_type: ChordType | str = MAJOR_TRIAD,
        inversion: int = 0,
    ) -> None:
        if isinstance(root, str):
            root = PitchClass(root)
        if isinstance(chord_type, str):
            key = chord_type.strip()
            if key not in CHORD_TYPES:
                raise ValueError(
                    f"Unknown chord type: {chord_type!r}. "
                    f"Available: {', '.join(sorted(set(CHORD_TYPES)))}"
                )
            chord_type = CHORD_TYPES[key]
        if inversion < 0 or inversion >= len(chord_type.intervals):
            raise ValueError(
                f"Inversion {inversion} out of range for {chord_type.name} "
                f"(0-{len(chord_type.intervals) - 1})"
            )
        self._root = root
        self._chord_type = chord_type
        self._inversion = inversion

    @classmethod
    def parse(cls, symbol: str) -> Chord:
        """Parse a chord symbol like 'Cmaj7', 'Bbm', 'F#dim7'."""
        symbol = symbol.strip()
        # Extract root note (1-2 chars: letter + optional accidental)
        if len(symbol) >= 2 and symbol[1] in "#b":
            root_str = symbol[:2]
            quality_str = symbol[2:]
        else:
            root_str = symbol[:1]
            quality_str = symbol[1:]
        root = PitchClass(root_str)
        if not quality_str:
            quality_str = ""  # Major triad
        return cls(root, quality_str)

    @property
    def root(self) -> PitchClass:
        return self._root

    @property
    def chord_type(self) -> ChordType:
        return self._chord_type

    @property
    def inversion(self) -> int:
        return self._inversion

    @property
    def symbol(self) -> str:
        return f"{self._root.name}{self._chord_type.symbol}"

    def pitch_classes(self) -> list[PitchClass]:
        pcs = [self._root.transpose(i) for i in self._chord_type.intervals]
        # Apply inversion by rotating
        return pcs[self._inversion :] + pcs[: self._inversion]

    def notes(self, octave: int = 4) -> list[Note]:
        """Generate concrete notes starting at the given octave."""
        base_midi = (octave + 1) * 12 + self._root.value
        raw = [base_midi + i for i in self._chord_type.intervals]
        # Apply inversion: move first N notes up an octave
        for i in range(self._inversion):
            raw[i] += 12
        raw.sort()
        return [Note.from_midi(m) for m in raw]

    def invert(self, n: int) -> Chord:
        return Chord(self._root, self._chord_type, n)

    def __repr__(self) -> str:
        inv = f", inv={self._inversion}" if self._inversion else ""
        return f"Chord({self._root.name!r}, {self._chord_type.name!r}{inv})"

    def __str__(self) -> str:
        inv = f"/{self.pitch_classes()[0].name}" if self._inversion else ""
        return f"{self.symbol}{inv}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Chord):
            return (
                self._root == other._root
                and self._chord_type == other._chord_type
                and self._inversion == other._inversion
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._root, self._chord_type, self._inversion))
