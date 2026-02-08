"""Time signatures, tempo, and duration primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TimeSignature:
    """A time signature (e.g. 4/4, 3/4, 7/8)."""

    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if self.numerator < 1:
            raise ValueError(f"Numerator must be >= 1, got {self.numerator}")
        if self.denominator < 1 or (self.denominator & (self.denominator - 1)):
            raise ValueError(
                f"Denominator must be a power of 2, got {self.denominator}"
            )

    @property
    def beats_per_bar(self) -> int:
        return self.numerator

    @property
    def beat_unit(self) -> int:
        return self.denominator

    @property
    def ticks_per_bar(self) -> int:
        """Bar length in ticks at 480 PPQN."""
        quarter_note_ticks = 480
        beat_ticks = quarter_note_ticks * 4 // self.denominator
        return beat_ticks * self.numerator

    @property
    def is_compound(self) -> bool:
        return self.numerator > 3 and self.numerator % 3 == 0

    @property
    def feel(self) -> str:
        if self.is_compound:
            return f"compound ({self.numerator // 3} groups of 3)"
        if self.numerator in (2, 3, 4):
            return "simple"
        return "irregular"

    def __str__(self) -> str:
        return f"{self.numerator}/{self.denominator}"


# Common time signatures
COMMON_TIME = TimeSignature(4, 4)
WALTZ_TIME = TimeSignature(3, 4)
CUT_TIME = TimeSignature(2, 2)
SIX_EIGHT = TimeSignature(6, 8)
FIVE_FOUR = TimeSignature(5, 4)
SEVEN_EIGHT = TimeSignature(7, 8)
ELEVEN_EIGHT = TimeSignature(11, 8)
TWELVE_EIGHT = TimeSignature(12, 8)


@dataclass(frozen=True, slots=True)
class Duration:
    """A note duration in ticks (480 PPQN = quarter note)."""

    ticks: int
    name: str

    @property
    def beats(self) -> float:
        return self.ticks / 480.0

    def dotted(self) -> Duration:
        return Duration(self.ticks + self.ticks // 2, f"dotted {self.name}")

    def triplet(self) -> Duration:
        return Duration(self.ticks * 2 // 3, f"{self.name} triplet")

    def __str__(self) -> str:
        return self.name


# Standard durations at 480 PPQN
WHOLE = Duration(1920, "whole")
HALF = Duration(960, "half")
QUARTER = Duration(480, "quarter")
EIGHTH = Duration(240, "eighth")
SIXTEENTH = Duration(120, "sixteenth")
THIRTY_SECOND = Duration(60, "thirty-second")


@dataclass(frozen=True, slots=True)
class Tempo:
    """A tempo marking in BPM."""

    bpm: float

    def __post_init__(self) -> None:
        if self.bpm <= 0:
            raise ValueError(f"BPM must be positive, got {self.bpm}")

    @property
    def us_per_beat(self) -> int:
        """Microseconds per beat (for MIDI tempo events)."""
        return int(60_000_000 / self.bpm)

    @property
    def marking(self) -> str:
        bpm = self.bpm
        if bpm < 40:
            return "Grave"
        if bpm < 55:
            return "Largo"
        if bpm < 65:
            return "Adagio"
        if bpm < 73:
            return "Andante"
        if bpm < 86:
            return "Moderato"
        if bpm < 98:
            return "Andante moderato"
        if bpm < 109:
            return "Allegretto"
        if bpm < 132:
            return "Allegro"
        if bpm < 140:
            return "Vivace"
        if bpm < 178:
            return "Presto"
        return "Prestissimo"

    def __str__(self) -> str:
        return f"{self.bpm} BPM ({self.marking})"
