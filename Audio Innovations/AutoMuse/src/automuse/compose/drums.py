"""Drum pattern engine -- genre-aware percussion using General MIDI mapping.

Generates rhythmic patterns for MIDI channel 10 (GM percussion). Each pattern
is one bar of DrumHits that can be repeated, varied, and exported alongside
melodic parts in a Score.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import IntEnum

from ..core.rhythm import TimeSignature, Duration, QUARTER, EIGHTH, SIXTEENTH, COMMON_TIME


class GMPercussion(IntEnum):
    """General MIDI percussion note numbers (channel 10)."""

    KICK = 36
    RIMSHOT = 37
    SNARE = 38
    CLAP = 39
    LOW_TOM = 45
    CLOSED_HH = 42
    MID_TOM = 47
    OPEN_HH = 46
    CRASH = 49
    HIGH_TOM = 50
    RIDE = 51
    TAMBOURINE = 54
    COWBELL = 56
    SHAKER = 70


@dataclass(frozen=True, slots=True)
class DrumHit:
    """A single percussion hit at a specific tick within a bar."""

    instrument: GMPercussion
    tick: int
    velocity: int = 100

    def __post_init__(self) -> None:
        if not 0 <= self.velocity <= 127:
            raise ValueError(f"Velocity must be 0-127, got {self.velocity}")
        if self.tick < 0:
            raise ValueError(f"Tick must be >= 0, got {self.tick}")


class DrumPattern:
    """A single bar of drum hits."""

    __slots__ = ("_hits", "_time_sig")

    def __init__(self, hits: list[DrumHit], time_sig: TimeSignature = COMMON_TIME) -> None:
        self._hits = sorted(hits, key=lambda h: (h.tick, h.instrument))
        self._time_sig = time_sig

    @property
    def hits(self) -> list[DrumHit]:
        return list(self._hits)

    @property
    def time_sig(self) -> TimeSignature:
        return self._time_sig

    @property
    def ticks(self) -> int:
        return self._time_sig.ticks_per_bar

    def repeat(self, n: int) -> list[DrumHit]:
        """Repeat pattern for n bars, offsetting ticks."""
        bar_len = self.ticks
        result: list[DrumHit] = []
        for bar in range(n):
            offset = bar * bar_len
            for hit in self._hits:
                result.append(DrumHit(hit.instrument, hit.tick + offset, hit.velocity))
        return result

    def vary(self, probability: float = 0.2, seed: int | None = None) -> DrumPattern:
        """Create a variation with random ghost notes and velocity changes."""
        rng = random.Random(seed)
        new_hits: list[DrumHit] = []
        for hit in self._hits:
            # Keep original hit with slight velocity variation
            vel_shift = rng.randint(-10, 10)
            new_vel = max(30, min(127, hit.velocity + vel_shift))
            new_hits.append(DrumHit(hit.instrument, hit.tick, new_vel))
            # Possibly add a ghost note nearby
            if rng.random() < probability:
                ghost_offset = SIXTEENTH.ticks
                ghost_tick = hit.tick + ghost_offset
                if ghost_tick < self.ticks:
                    new_hits.append(DrumHit(hit.instrument, ghost_tick, max(30, hit.velocity - 30)))
        return DrumPattern(new_hits, self._time_sig)

    def instruments_used(self) -> set[GMPercussion]:
        """Return the set of instruments in this pattern."""
        return {h.instrument for h in self._hits}

    def __len__(self) -> int:
        return len(self._hits)

    def __repr__(self) -> str:
        instruments = ", ".join(i.name for i in sorted(self.instruments_used()))
        return f"DrumPattern({len(self._hits)} hits, {self._time_sig}, [{instruments}])"


class DrumPatternBuilder:
    """Static factory methods for genre-specific drum patterns."""

    @staticmethod
    def rock(time_sig: TimeSignature = COMMON_TIME) -> DrumPattern:
        """Standard rock: kick 1,3; snare 2,4; closed HH eighths."""
        q = QUARTER.ticks
        e = EIGHTH.ticks
        hits: list[DrumHit] = []
        # Kick on beats 1 and 3
        hits.append(DrumHit(GMPercussion.KICK, 0, 110))
        hits.append(DrumHit(GMPercussion.KICK, q * 2, 100))
        # Snare on beats 2 and 4
        hits.append(DrumHit(GMPercussion.SNARE, q, 110))
        hits.append(DrumHit(GMPercussion.SNARE, q * 3, 110))
        # Closed hi-hat on every eighth note
        for i in range(time_sig.beats_per_bar * 2):
            hits.append(DrumHit(GMPercussion.CLOSED_HH, i * e, 80))
        return DrumPattern(hits, time_sig)

    @staticmethod
    def pop(time_sig: TimeSignature = COMMON_TIME) -> DrumPattern:
        """Pop beat: rock base with open HH before snare hits."""
        q = QUARTER.ticks
        e = EIGHTH.ticks
        hits: list[DrumHit] = []
        hits.append(DrumHit(GMPercussion.KICK, 0, 110))
        hits.append(DrumHit(GMPercussion.KICK, q * 2, 100))
        hits.append(DrumHit(GMPercussion.SNARE, q, 110))
        hits.append(DrumHit(GMPercussion.SNARE, q * 3, 110))
        for i in range(time_sig.beats_per_bar * 2):
            tick = i * e
            # Open HH on the eighth before snare hits
            if tick == q - e or tick == q * 3 - e:
                hits.append(DrumHit(GMPercussion.OPEN_HH, tick, 85))
            else:
                hits.append(DrumHit(GMPercussion.CLOSED_HH, tick, 80))
        return DrumPattern(hits, time_sig)

    @staticmethod
    def jazz_ride(time_sig: TimeSignature = COMMON_TIME) -> DrumPattern:
        """Jazz ride pattern: ride cymbal with swing feel, ghost snare."""
        q = QUARTER.ticks
        triplet_q = QUARTER.triplet().ticks  # swing eighth
        hits: list[DrumHit] = []
        # Kick on beat 1
        hits.append(DrumHit(GMPercussion.KICK, 0, 90))
        # Ride pattern: beat + swing eighth (triplet feel)
        for beat in range(time_sig.beats_per_bar):
            tick = beat * q
            hits.append(DrumHit(GMPercussion.RIDE, tick, 95))
            # Swing eighth (2/3 of the way through the beat)
            hits.append(DrumHit(GMPercussion.RIDE, tick + triplet_q * 2, 70))
        # Ghost snare on 2 and 4
        hits.append(DrumHit(GMPercussion.SNARE, q, 50))
        hits.append(DrumHit(GMPercussion.SNARE, q * 3, 50))
        return DrumPattern(hits, time_sig)

    @staticmethod
    def hip_hop(time_sig: TimeSignature = COMMON_TIME) -> DrumPattern:
        """Hip-hop: syncopated kick, snare 2,4, varied hi-hats."""
        q = QUARTER.ticks
        e = EIGHTH.ticks
        s = SIXTEENTH.ticks
        hits: list[DrumHit] = []
        # Syncopated kick: beat 1, and-of-2, beat 3, and-of-4
        hits.append(DrumHit(GMPercussion.KICK, 0, 110))
        hits.append(DrumHit(GMPercussion.KICK, q + e, 95))
        hits.append(DrumHit(GMPercussion.KICK, q * 2, 105))
        hits.append(DrumHit(GMPercussion.KICK, q * 3 + e, 90))
        # Snare on 2 and 4
        hits.append(DrumHit(GMPercussion.SNARE, q, 110))
        hits.append(DrumHit(GMPercussion.SNARE, q * 3, 110))
        # Hi-hats: closed on every sixteenth with open on off-beats
        for i in range(time_sig.beats_per_bar * 4):
            tick = i * s
            if i % 4 == 2:  # open on the "and"
                hits.append(DrumHit(GMPercussion.OPEN_HH, tick, 75))
            else:
                hits.append(DrumHit(GMPercussion.CLOSED_HH, tick, 70))
        return DrumPattern(hits, time_sig)

    @staticmethod
    def edm_four_on_floor(time_sig: TimeSignature = COMMON_TIME) -> DrumPattern:
        """EDM: kick every quarter, clap on 2,4, HH on every sixteenth."""
        q = QUARTER.ticks
        s = SIXTEENTH.ticks
        hits: list[DrumHit] = []
        # Four-on-the-floor kick
        for beat in range(time_sig.beats_per_bar):
            hits.append(DrumHit(GMPercussion.KICK, beat * q, 120))
        # Clap on 2 and 4
        hits.append(DrumHit(GMPercussion.CLAP, q, 110))
        hits.append(DrumHit(GMPercussion.CLAP, q * 3, 110))
        # Closed HH on every sixteenth
        for i in range(time_sig.beats_per_bar * 4):
            hits.append(DrumHit(GMPercussion.CLOSED_HH, i * s, 80))
        return DrumPattern(hits, time_sig)

    @staticmethod
    def bossa_nova(time_sig: TimeSignature = COMMON_TIME) -> DrumPattern:
        """Bossa nova: cross-stick pattern, kick on 1 and and-of-2."""
        q = QUARTER.ticks
        e = EIGHTH.ticks
        hits: list[DrumHit] = []
        # Kick on beat 1 and the "and" of 2
        hits.append(DrumHit(GMPercussion.KICK, 0, 90))
        hits.append(DrumHit(GMPercussion.KICK, q + e, 80))
        # Rimshot (cross-stick) pattern: beats 2, 3-and, 4-and
        hits.append(DrumHit(GMPercussion.RIMSHOT, q, 85))
        hits.append(DrumHit(GMPercussion.RIMSHOT, q * 2 + e, 75))
        hits.append(DrumHit(GMPercussion.RIMSHOT, q * 3 + e, 75))
        # Closed HH on every eighth
        for i in range(time_sig.beats_per_bar * 2):
            hits.append(DrumHit(GMPercussion.CLOSED_HH, i * e, 70))
        return DrumPattern(hits, time_sig)

    @staticmethod
    def waltz(time_sig: TimeSignature | None = None) -> DrumPattern:
        """Waltz: kick on 1, snare on 2,3 (3/4 time)."""
        if time_sig is None:
            from ..core.rhythm import WALTZ_TIME
            time_sig = WALTZ_TIME
        q = QUARTER.ticks
        hits: list[DrumHit] = []
        hits.append(DrumHit(GMPercussion.KICK, 0, 100))
        hits.append(DrumHit(GMPercussion.SNARE, q, 80))
        hits.append(DrumHit(GMPercussion.SNARE, q * 2, 80))
        # Closed HH on every beat
        for beat in range(time_sig.beats_per_bar):
            hits.append(DrumHit(GMPercussion.CLOSED_HH, beat * q, 70))
        return DrumPattern(hits, time_sig)

    @staticmethod
    def shuffle(time_sig: TimeSignature = COMMON_TIME) -> DrumPattern:
        """Shuffle: triplet-based feel with kick/snare and shuffled HH."""
        q = QUARTER.ticks
        triplet = QUARTER.triplet().ticks
        hits: list[DrumHit] = []
        # Kick on 1 and 3
        hits.append(DrumHit(GMPercussion.KICK, 0, 110))
        hits.append(DrumHit(GMPercussion.KICK, q * 2, 100))
        # Snare on 2 and 4
        hits.append(DrumHit(GMPercussion.SNARE, q, 110))
        hits.append(DrumHit(GMPercussion.SNARE, q * 3, 110))
        # Shuffled hi-hat: beat + third triplet (long-short pattern)
        for beat in range(time_sig.beats_per_bar):
            tick = beat * q
            hits.append(DrumHit(GMPercussion.CLOSED_HH, tick, 90))
            hits.append(DrumHit(GMPercussion.CLOSED_HH, tick + triplet * 2, 70))
        return DrumPattern(hits, time_sig)


class DrumFill:
    """Static methods for common drum fills."""

    @staticmethod
    def simple_buildup(length_ticks: int = 1920) -> list[DrumHit]:
        """Ascending tom fill across the given tick length."""
        toms = [GMPercussion.LOW_TOM, GMPercussion.MID_TOM, GMPercussion.HIGH_TOM]
        s = SIXTEENTH.ticks
        num_hits = length_ticks // s
        hits: list[DrumHit] = []
        for i in range(num_hits):
            tom = toms[min(i * len(toms) // num_hits, len(toms) - 1)]
            vel = 80 + (i * 40 // max(num_hits - 1, 1))
            hits.append(DrumHit(tom, i * s, min(127, vel)))
        # Crash on the downbeat after the fill
        hits.append(DrumHit(GMPercussion.CRASH, length_ticks, 120))
        return hits

    @staticmethod
    def snare_roll(length_ticks: int = 960) -> list[DrumHit]:
        """32nd-note snare roll for the given tick length."""
        from ..core.rhythm import THIRTY_SECOND
        step = THIRTY_SECOND.ticks
        hits: list[DrumHit] = []
        tick = 0
        while tick < length_ticks:
            # Crescendo from pp to ff
            progress = tick / max(length_ticks - 1, 1)
            vel = int(50 + progress * 77)
            hits.append(DrumHit(GMPercussion.SNARE, tick, min(127, vel)))
            tick += step
        return hits
