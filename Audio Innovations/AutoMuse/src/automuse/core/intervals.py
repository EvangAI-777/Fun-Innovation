"""Musical interval definitions and calculations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Interval:
    """A musical interval defined by semitone distance."""

    semitones: int
    name: str
    short: str

    def __add__(self, other: Interval) -> Interval:
        total = self.semitones + other.semitones
        return Interval(total, f"{self.name}+{other.name}", f"{self.short}+{other.short}")

    def invert(self) -> Interval:
        inv = 12 - (self.semitones % 12)
        return Interval(inv, f"inv({self.name})", f"inv({self.short})")


# Standard intervals
UNISON = Interval(0, "unison", "P1")
MINOR_SECOND = Interval(1, "minor second", "m2")
MAJOR_SECOND = Interval(2, "major second", "M2")
MINOR_THIRD = Interval(3, "minor third", "m3")
MAJOR_THIRD = Interval(4, "major third", "M3")
PERFECT_FOURTH = Interval(5, "perfect fourth", "P4")
TRITONE = Interval(6, "tritone", "TT")
PERFECT_FIFTH = Interval(7, "perfect fifth", "P5")
MINOR_SIXTH = Interval(8, "minor sixth", "m6")
MAJOR_SIXTH = Interval(9, "major sixth", "M6")
MINOR_SEVENTH = Interval(10, "minor seventh", "m7")
MAJOR_SEVENTH = Interval(11, "major seventh", "M7")
OCTAVE = Interval(12, "octave", "P8")

ALL_INTERVALS = [
    UNISON, MINOR_SECOND, MAJOR_SECOND, MINOR_THIRD, MAJOR_THIRD,
    PERFECT_FOURTH, TRITONE, PERFECT_FIFTH, MINOR_SIXTH, MAJOR_SIXTH,
    MINOR_SEVENTH, MAJOR_SEVENTH, OCTAVE,
]

INTERVAL_BY_SEMITONES: dict[int, Interval] = {i.semitones: i for i in ALL_INTERVALS}


def interval_between(semitones: int) -> Interval:
    """Look up the interval for a given semitone distance (mod 12)."""
    s = semitones % 12
    if s in INTERVAL_BY_SEMITONES:
        return INTERVAL_BY_SEMITONES[s]
    return Interval(s, f"{s} semitones", f"{s}st")
