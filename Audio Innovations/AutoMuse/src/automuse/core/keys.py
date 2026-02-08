"""Key signatures, relative/parallel keys, and modulation paths."""

from __future__ import annotations

from dataclasses import dataclass

from .notes import PitchClass
from .scales import Scale, MAJOR, NATURAL_MINOR, HARMONIC_MINOR, MELODIC_MINOR, ScaleType
from .chords import (
    Chord, MAJOR_TRIAD, MINOR_TRIAD, DIMINISHED_TRIAD, AUGMENTED_TRIAD,
    DOMINANT_7, MAJOR_7, MINOR_7, HALF_DIMINISHED_7, DIMINISHED_7,
    ChordType,
)


# Sharps/flats count for each key (positive = sharps, negative = flats)
KEY_SIGNATURES: dict[str, int] = {
    "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6, "Gb": -6,
    "Db": -5, "Ab": -4, "Eb": -3, "Bb": -2, "F": -1,
}

# Diatonic triad qualities for major keys (by scale degree, 1-indexed)
_MAJOR_TRIAD_PATTERN: list[ChordType] = [
    MAJOR_TRIAD, MINOR_TRIAD, MINOR_TRIAD, MAJOR_TRIAD,
    MAJOR_TRIAD, MINOR_TRIAD, DIMINISHED_TRIAD,
]

# Diatonic seventh qualities for major keys
_MAJOR_7TH_PATTERN: list[ChordType] = [
    MAJOR_7, MINOR_7, MINOR_7, MAJOR_7,
    DOMINANT_7, MINOR_7, HALF_DIMINISHED_7,
]

# Diatonic triad qualities for natural minor keys
_MINOR_TRIAD_PATTERN: list[ChordType] = [
    MINOR_TRIAD, DIMINISHED_TRIAD, MAJOR_TRIAD, MINOR_TRIAD,
    MINOR_TRIAD, MAJOR_TRIAD, MAJOR_TRIAD,
]

# Diatonic seventh qualities for natural minor keys
_MINOR_7TH_PATTERN: list[ChordType] = [
    MINOR_7, HALF_DIMINISHED_7, MAJOR_7, MINOR_7,
    MINOR_7, MAJOR_7, DOMINANT_7,
]

# Roman numeral labels
ROMAN_NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII"]


@dataclass(frozen=True)
class DiatonicChord:
    """A chord built on a scale degree within a key."""

    degree: int
    chord: Chord
    roman: str


class Key:
    """A musical key: root + quality (major/minor) with full diatonic harmony."""

    __slots__ = ("_root", "_quality", "_scale")

    def __init__(self, root: PitchClass | str, quality: str = "major") -> None:
        if isinstance(root, str):
            root = PitchClass(root)
        quality = quality.lower().strip()
        if quality not in ("major", "minor"):
            raise ValueError(f"Key quality must be 'major' or 'minor', got {quality!r}")
        self._root = root
        self._quality = quality
        scale_type = MAJOR if quality == "major" else NATURAL_MINOR
        self._scale = Scale(root, scale_type)

    @property
    def root(self) -> PitchClass:
        return self._root

    @property
    def quality(self) -> str:
        return self._quality

    @property
    def scale(self) -> Scale:
        return self._scale

    @property
    def name(self) -> str:
        return f"{self._root.name} {self._quality}"

    @property
    def signature(self) -> int:
        """Number of sharps (positive) or flats (negative)."""
        root_name = self._root.name
        if self._quality == "minor":
            # Relative major is 3 semitones up
            rel_major = self._root.transpose(3)
            root_name = rel_major.name
        return KEY_SIGNATURES.get(root_name, 0)

    def relative(self) -> Key:
        """Get the relative major/minor key."""
        if self._quality == "major":
            return Key(self._root.transpose(9), "minor")
        return Key(self._root.transpose(3), "major")

    def parallel(self) -> Key:
        """Get the parallel major/minor key (same root, opposite quality)."""
        new_q = "minor" if self._quality == "major" else "major"
        return Key(self._root, new_q)

    def diatonic_triads(self) -> list[DiatonicChord]:
        """Build all diatonic triads for this key."""
        pcs = self._scale.pitch_classes()
        pattern = _MAJOR_TRIAD_PATTERN if self._quality == "major" else _MINOR_TRIAD_PATTERN
        result: list[DiatonicChord] = []
        for i, (pc, ct) in enumerate(zip(pcs, pattern)):
            roman = ROMAN_NUMERALS[i]
            if ct == MINOR_TRIAD or ct == DIMINISHED_TRIAD:
                roman = roman.lower()
            if ct == DIMINISHED_TRIAD:
                roman += "°"
            elif ct == AUGMENTED_TRIAD:
                roman += "+"
            result.append(DiatonicChord(i + 1, Chord(pc, ct), roman))
        return result

    def diatonic_sevenths(self) -> list[DiatonicChord]:
        """Build all diatonic seventh chords for this key."""
        pcs = self._scale.pitch_classes()
        pattern = _MAJOR_7TH_PATTERN if self._quality == "major" else _MINOR_7TH_PATTERN
        result: list[DiatonicChord] = []
        for i, (pc, ct) in enumerate(zip(pcs, pattern)):
            roman = ROMAN_NUMERALS[i]
            if ct in (MINOR_7, HALF_DIMINISHED_7, DIMINISHED_7):
                roman = roman.lower()
            roman += "7"
            result.append(DiatonicChord(i + 1, Chord(pc, ct), roman))
        return result

    def pivot_chords(self, target: Key) -> list[tuple[DiatonicChord, DiatonicChord]]:
        """Find chords common to both keys (pivot chords for modulation)."""
        my_triads = self.diatonic_triads()
        target_triads = target.diatonic_triads()
        pivots: list[tuple[DiatonicChord, DiatonicChord]] = []
        for mine in my_triads:
            for theirs in target_triads:
                if mine.chord == theirs.chord:
                    pivots.append((mine, theirs))
        return pivots

    def __repr__(self) -> str:
        return f"Key({self._root.name!r}, {self._quality!r})"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Key):
            return self._root == other._root and self._quality == other._quality
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._root, self._quality))
