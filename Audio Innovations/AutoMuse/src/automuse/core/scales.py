"""Scale definitions covering modes, exotic scales, and world music traditions."""

from __future__ import annotations

from dataclasses import dataclass

from .notes import PitchClass, Note


@dataclass(frozen=True)
class ScaleType:
    """A scale defined by its interval pattern (semitones from root)."""

    name: str
    intervals: tuple[int, ...]

    @property
    def degree_count(self) -> int:
        return len(self.intervals)


# --- Western modes (built on major scale rotations) ---
MAJOR = ScaleType("major", (0, 2, 4, 5, 7, 9, 11))
DORIAN = ScaleType("dorian", (0, 2, 3, 5, 7, 9, 10))
PHRYGIAN = ScaleType("phrygian", (0, 1, 3, 5, 7, 8, 10))
LYDIAN = ScaleType("lydian", (0, 2, 4, 6, 7, 9, 11))
MIXOLYDIAN = ScaleType("mixolydian", (0, 2, 4, 5, 7, 9, 10))
AEOLIAN = ScaleType("aeolian", (0, 2, 3, 5, 7, 8, 10))
LOCRIAN = ScaleType("locrian", (0, 1, 3, 5, 6, 8, 10))

# Aliases
NATURAL_MINOR = ScaleType("natural minor", AEOLIAN.intervals)
IONIAN = ScaleType("ionian", MAJOR.intervals)

# --- Minor variants ---
HARMONIC_MINOR = ScaleType("harmonic minor", (0, 2, 3, 5, 7, 8, 11))
MELODIC_MINOR = ScaleType("melodic minor", (0, 2, 3, 5, 7, 9, 11))

# --- Pentatonic and blues ---
MAJOR_PENTATONIC = ScaleType("major pentatonic", (0, 2, 4, 7, 9))
MINOR_PENTATONIC = ScaleType("minor pentatonic", (0, 3, 5, 7, 10))
BLUES = ScaleType("blues", (0, 3, 5, 6, 7, 10))

# --- Symmetric scales ---
WHOLE_TONE = ScaleType("whole tone", (0, 2, 4, 6, 8, 10))
DIMINISHED_HW = ScaleType("diminished (half-whole)", (0, 1, 3, 4, 6, 7, 9, 10))
DIMINISHED_WH = ScaleType("diminished (whole-half)", (0, 2, 3, 5, 6, 8, 9, 11))
AUGMENTED = ScaleType("augmented", (0, 3, 4, 7, 8, 11))
CHROMATIC = ScaleType("chromatic", tuple(range(12)))

# --- Bebop scales ---
BEBOP_DOMINANT = ScaleType("bebop dominant", (0, 2, 4, 5, 7, 9, 10, 11))
BEBOP_MAJOR = ScaleType("bebop major", (0, 2, 4, 5, 7, 8, 9, 11))
BEBOP_MINOR = ScaleType("bebop minor", (0, 2, 3, 5, 7, 8, 9, 10))

# --- World music ---
PHRYGIAN_DOMINANT = ScaleType("phrygian dominant", (0, 1, 4, 5, 7, 8, 10))
HUNGARIAN_MINOR = ScaleType("hungarian minor", (0, 2, 3, 6, 7, 8, 11))
DOUBLE_HARMONIC = ScaleType("double harmonic", (0, 1, 4, 5, 7, 8, 11))
HIRAJOSHI = ScaleType("hirajoshi", (0, 2, 3, 7, 8))
IN_SCALE = ScaleType("in", (0, 1, 5, 7, 8))
IWATO = ScaleType("iwato", (0, 1, 5, 6, 10))

# Master lookup
SCALE_TYPES: dict[str, ScaleType] = {
    st.name: st for st in [
        MAJOR, DORIAN, PHRYGIAN, LYDIAN, MIXOLYDIAN, AEOLIAN, LOCRIAN,
        NATURAL_MINOR, IONIAN,
        HARMONIC_MINOR, MELODIC_MINOR,
        MAJOR_PENTATONIC, MINOR_PENTATONIC, BLUES,
        WHOLE_TONE, DIMINISHED_HW, DIMINISHED_WH, AUGMENTED, CHROMATIC,
        BEBOP_DOMINANT, BEBOP_MAJOR, BEBOP_MINOR,
        PHRYGIAN_DOMINANT, HUNGARIAN_MINOR, DOUBLE_HARMONIC,
        HIRAJOSHI, IN_SCALE, IWATO,
    ]
}


class Scale:
    """A concrete scale: a root pitch class combined with a scale type."""

    __slots__ = ("_root", "_scale_type")

    def __init__(self, root: PitchClass | str, scale_type: ScaleType | str) -> None:
        if isinstance(root, str):
            root = PitchClass(root)
        if isinstance(scale_type, str):
            key = scale_type.lower().strip()
            if key not in SCALE_TYPES:
                raise ValueError(
                    f"Unknown scale type: {scale_type!r}. "
                    f"Available: {', '.join(sorted(SCALE_TYPES))}"
                )
            scale_type = SCALE_TYPES[key]
        self._root = root
        self._scale_type = scale_type

    @property
    def root(self) -> PitchClass:
        return self._root

    @property
    def scale_type(self) -> ScaleType:
        return self._scale_type

    @property
    def name(self) -> str:
        return f"{self._root.name} {self._scale_type.name}"

    def pitch_classes(self) -> list[PitchClass]:
        return [self._root.transpose(i) for i in self._scale_type.intervals]

    def notes(self, octave: int = 4) -> list[Note]:
        """Generate concrete notes for this scale starting at the given octave."""
        result: list[Note] = []
        base_midi = (octave + 1) * 12 + self._root.value
        for interval in self._scale_type.intervals:
            result.append(Note.from_midi(base_midi + interval))
        return result

    def degree(self, n: int) -> PitchClass:
        """Get the nth scale degree (1-indexed)."""
        if n < 1 or n > len(self._scale_type.intervals):
            raise ValueError(
                f"Degree {n} out of range for {self._scale_type.name} "
                f"(1-{len(self._scale_type.intervals)})"
            )
        return self._root.transpose(self._scale_type.intervals[n - 1])

    def contains(self, pc: PitchClass | str) -> bool:
        if isinstance(pc, str):
            pc = PitchClass(pc)
        return pc in self.pitch_classes()

    def __repr__(self) -> str:
        return f"Scale({self._root.name!r}, {self._scale_type.name!r})"

    def __str__(self) -> str:
        return self.name

    def __len__(self) -> int:
        return len(self._scale_type.intervals)
