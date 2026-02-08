"""Chord progression generation and common patterns."""

from __future__ import annotations

from dataclasses import dataclass, field

from automuse.core.notes import PitchClass
from automuse.core.chords import Chord, ChordType, MAJOR_TRIAD, MINOR_TRIAD, DOMINANT_7
from automuse.core.keys import Key
from automuse.core.rhythm import Duration, WHOLE


@dataclass
class ProgressionStep:
    """A single step in a chord progression."""

    chord: Chord
    duration: Duration = field(default_factory=lambda: WHOLE)
    roman: str = ""


class Progression:
    """An ordered sequence of chords forming a harmonic progression."""

    __slots__ = ("_steps", "_key")

    def __init__(self, steps: list[ProgressionStep], key: Key | None = None) -> None:
        self._steps = list(steps)
        self._key = key

    @property
    def steps(self) -> list[ProgressionStep]:
        return list(self._steps)

    @property
    def key(self) -> Key | None:
        return self._key

    @property
    def chords(self) -> list[Chord]:
        return [s.chord for s in self._steps]

    def __len__(self) -> int:
        return len(self._steps)

    def __getitem__(self, index: int) -> ProgressionStep:
        return self._steps[index]

    def __repr__(self) -> str:
        romans = [s.roman or s.chord.symbol for s in self._steps]
        return f"Progression([{', '.join(romans)}])"

    def __str__(self) -> str:
        return " | ".join(s.roman or str(s.chord) for s in self._steps)


# Common progression templates as (degree, quality) pairs (1-indexed degrees)
COMMON_PROGRESSIONS: dict[str, list[tuple[int, str]]] = {
    "I-IV-V-I": [(1, ""), (4, ""), (5, ""), (1, "")],
    "I-V-vi-IV": [(1, ""), (5, ""), (6, "m"), (4, "")],
    "ii-V-I": [(2, "m7"), (5, "7"), (1, "maj7")],
    "I-vi-IV-V": [(1, ""), (6, "m"), (4, ""), (5, "")],
    "12-bar blues": [
        (1, "7"), (1, "7"), (1, "7"), (1, "7"),
        (4, "7"), (4, "7"), (1, "7"), (1, "7"),
        (5, "7"), (4, "7"), (1, "7"), (5, "7"),
    ],
    "vi-IV-I-V": [(6, "m"), (4, ""), (1, ""), (5, "")],
    "I-V-vi-iii-IV-I-IV-V": [
        (1, ""), (5, ""), (6, "m"), (3, "m"),
        (4, ""), (1, ""), (4, ""), (5, ""),
    ],
    "i-bVI-bIII-bVII": [(1, "m"), (6, ""), (3, ""), (7, "")],
    "ii-V-I turnaround": [(2, "m7"), (5, "7"), (1, "maj7")],
    "I-bVII-IV-I": [(1, ""), (7, ""), (4, ""), (1, "")],
}

ROMAN_MAP = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII",
}


class ProgressionBuilder:
    """Build progressions from templates, degree lists, or custom chords."""

    def __init__(self, key: Key) -> None:
        self._key = key

    def from_template(self, name: str) -> Progression:
        """Build a progression from a named template."""
        if name not in COMMON_PROGRESSIONS:
            raise ValueError(
                f"Unknown progression template: {name!r}. "
                f"Available: {', '.join(sorted(COMMON_PROGRESSIONS))}"
            )
        template = COMMON_PROGRESSIONS[name]
        return self.from_degrees(template)

    def from_degrees(self, degrees: list[tuple[int, str]]) -> Progression:
        """Build a progression from (degree, quality) pairs."""
        scale_pcs = self._key.scale.pitch_classes()
        steps: list[ProgressionStep] = []
        for degree, quality in degrees:
            idx = (degree - 1) % 7
            root = scale_pcs[idx]
            chord = Chord(root, quality) if quality else Chord(root)
            roman = ROMAN_MAP.get(degree, str(degree))
            if quality and ("m" in quality.lower() or "dim" in quality.lower()):
                roman = roman.lower()
            if quality:
                roman += quality
            steps.append(ProgressionStep(chord=chord, roman=roman))
        return Progression(steps, self._key)

    def from_roman(self, numerals: list[str]) -> Progression:
        """Build a progression from Roman numeral analysis strings."""
        diatonic = {dc.roman: dc for dc in self._key.diatonic_triads()}
        diatonic_7 = {dc.roman: dc for dc in self._key.diatonic_sevenths()}
        steps: list[ProgressionStep] = []
        for numeral in numerals:
            if numeral in diatonic:
                dc = diatonic[numeral]
                steps.append(ProgressionStep(chord=dc.chord, roman=dc.roman))
            elif numeral in diatonic_7:
                dc = diatonic_7[numeral]
                steps.append(ProgressionStep(chord=dc.chord, roman=dc.roman))
            else:
                raise ValueError(
                    f"Unknown Roman numeral {numeral!r} in key {self._key.name}. "
                    f"Available: {', '.join(sorted(diatonic))}"
                )
        return Progression(steps, self._key)

    @staticmethod
    def available_templates() -> list[str]:
        return sorted(COMMON_PROGRESSIONS.keys())
