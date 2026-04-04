"""Algorithmic melody generation from music theory primitives."""

from __future__ import annotations

import random
from enum import Enum

from ..core.notes import Note
from ..core.rhythm import Duration, QUARTER, EIGHTH
from ..core.scales import Scale
from ..core.keys import Key
from .motif import Motif, MotifNote, MotifBuilder


class MelodyContour(Enum):
    """Shapes that guide pitch selection over time."""

    ASCENDING = "ascending"
    DESCENDING = "descending"
    ARCH = "arch"
    VALLEY = "valley"
    STATIC = "static"
    WAVE = "wave"


class MelodyConfig:
    """Configuration for melody generation."""

    __slots__ = (
        "scale", "octave", "length", "contour", "step_bias",
        "rest_probability", "rhythm_pattern", "range_semitones",
    )

    def __init__(
        self,
        scale: Scale,
        octave: int = 4,
        length: int = 8,
        contour: MelodyContour = MelodyContour.ARCH,
        step_bias: float = 0.7,
        rest_probability: float = 0.0,
        rhythm_pattern: list[Duration] | None = None,
        range_semitones: int = 12,
    ) -> None:
        self.scale = scale
        self.octave = octave
        self.length = length
        self.contour = contour
        self.step_bias = max(0.0, min(1.0, step_bias))
        self.rest_probability = max(0.0, min(1.0, rest_probability))
        self.rhythm_pattern = rhythm_pattern
        self.range_semitones = range_semitones


def _contour_direction(contour: MelodyContour, position: float) -> float:
    """Return a value from -1 (descending) to +1 (ascending) based on contour and position (0-1)."""
    if contour == MelodyContour.ASCENDING:
        return 0.8
    if contour == MelodyContour.DESCENDING:
        return -0.8
    if contour == MelodyContour.ARCH:
        return 1.0 - 2.0 * position  # +1 at start, -1 at end
    if contour == MelodyContour.VALLEY:
        return -1.0 + 2.0 * position  # -1 at start, +1 at end
    if contour == MelodyContour.STATIC:
        return 0.0
    # WAVE: oscillate
    import math
    return math.sin(position * 2 * math.pi)


class MelodyGenerator:
    """Algorithmic melody engine driven by scale, contour, and step probability."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def generate(self, config: MelodyConfig) -> Motif:
        """Generate a melody following the given configuration."""
        scale_notes = config.scale.notes(config.octave)
        degree_count = len(scale_notes)
        if degree_count == 0:
            return Motif([])

        # Start at a musically sensible degree based on contour
        if config.contour == MelodyContour.DESCENDING:
            current_degree = degree_count - 1
        elif config.contour == MelodyContour.VALLEY:
            current_degree = degree_count // 2
        else:
            current_degree = 0

        # Build extended scale for range (multiple octaves)
        min_midi = scale_notes[0].midi
        max_midi = min_midi + config.range_semitones
        extended: list[Note] = []
        for oct_offset in range(3):  # up to 3 octaves
            for sn in scale_notes:
                n = sn.transpose(12 * oct_offset)
                if min_midi <= n.midi <= max_midi:
                    extended.append(n)
        if not extended:
            extended = list(scale_notes)

        # Map current_degree to extended index
        current_idx = min(current_degree, len(extended) - 1)

        motif_notes: list[MotifNote] = []
        for i in range(config.length):
            position = i / max(config.length - 1, 1)
            direction = _contour_direction(config.contour, position)

            # Pick rhythm
            if config.rhythm_pattern:
                dur = config.rhythm_pattern[i % len(config.rhythm_pattern)]
            else:
                dur = QUARTER

            # Decide step vs skip
            if self._rng.random() < config.step_bias:
                step = 1  # stepwise
            else:
                step = self._rng.randint(2, 3)  # skip

            # Apply direction
            if direction > 0:
                move = step if self._rng.random() < (0.5 + direction * 0.4) else -step
            elif direction < 0:
                move = -step if self._rng.random() < (0.5 + abs(direction) * 0.4) else step
            else:
                move = self._rng.choice([-step, step])

            new_idx = current_idx + move
            new_idx = max(0, min(len(extended) - 1, new_idx))
            current_idx = new_idx

            note = extended[current_idx]
            motif_notes.append(MotifNote(note, dur, velocity=self._rng.randint(60, 100)))

        return Motif(motif_notes)

    def develop(self, motif: Motif, technique: str) -> Motif:
        """Apply a development technique to an existing motif.

        Techniques:
            sequence    -- repeat at a different pitch level (+2 scale steps)
            variation   -- small random pitch alterations (+-1 semitone)
            fragmentation -- use only the first half of the motif
            extension   -- repeat last few notes with variation
        """
        if not motif.notes:
            return Motif([])

        if technique == "sequence":
            return motif.transpose(2)

        if technique == "variation":
            varied: list[MotifNote] = []
            for mn in motif:
                offset = self._rng.choice([-1, 0, 0, 0, 1])  # mostly unchanged
                varied.append(mn.transpose(offset))
            return Motif(varied)

        if technique == "fragmentation":
            half = max(1, len(motif) // 2)
            return Motif(motif.notes[:half])

        if technique == "extension":
            tail_len = max(1, len(motif) // 3)
            tail = motif.notes[-tail_len:]
            extended_notes: list[MotifNote] = []
            for mn in tail:
                offset = self._rng.choice([-1, 0, 1])
                extended_notes.append(mn.transpose(offset))
            return Motif(motif.notes + extended_notes)

        raise ValueError(
            f"Unknown technique: {technique!r}. "
            f"Available: sequence, variation, fragmentation, extension"
        )
