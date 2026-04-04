"""Bass line generator -- creates bass parts from chord progressions.

Generates bass lines in various styles (root, walking, arpeggiated, etc.)
that follow a harmonic progression. Bass lines are returned as Motif objects
for seamless integration with the Score and export pipeline.
"""

from __future__ import annotations

import random
from enum import Enum

from ..core.notes import Note
from ..core.chords import Chord
from ..core.keys import Key
from ..core.scales import Scale
from ..core.rhythm import (
    Duration, TimeSignature, WHOLE, HALF, QUARTER, EIGHTH,
    COMMON_TIME,
)
from ..harmony.progressions import Progression
from .motif import Motif, MotifNote


class BassStyle(Enum):
    """Bass line generation styles."""

    ROOT = "root"
    ROOT_FIFTH = "root_fifth"
    WALKING = "walking"
    ARPEGGIATED = "arpeggiated"
    SYNCOPATED = "syncopated"


class BassConfig:
    """Configuration for bass line generation."""

    __slots__ = ("progression", "key", "octave", "style", "time_sig")

    def __init__(
        self,
        progression: Progression,
        key: Key,
        octave: int = 2,
        style: BassStyle = BassStyle.ROOT,
        time_sig: TimeSignature = COMMON_TIME,
    ) -> None:
        self.progression = progression
        self.key = key
        self.octave = octave
        self.style = style
        self.time_sig = time_sig


class BassGenerator:
    """Generates bass lines from chord progressions."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def generate(self, config: BassConfig) -> Motif:
        """Generate a bass line matching the progression."""
        style_map = {
            BassStyle.ROOT: self._gen_root,
            BassStyle.ROOT_FIFTH: self._gen_root_fifth,
            BassStyle.WALKING: self._gen_walking,
            BassStyle.ARPEGGIATED: self._gen_arpeggiated,
            BassStyle.SYNCOPATED: self._gen_syncopated,
        }
        handler = style_map[config.style]
        return handler(config)

    def _gen_root(self, config: BassConfig) -> Motif:
        """Whole-note roots, one per chord."""
        notes: list[MotifNote] = []
        for step in config.progression.steps:
            root = self._root_note(step.chord, config.octave)
            notes.append(MotifNote(root, step.duration, 90))
        return Motif(notes, "bass:root")

    def _gen_root_fifth(self, config: BassConfig) -> Motif:
        """Alternating root and fifth, half notes."""
        notes: list[MotifNote] = []
        for step in config.progression.steps:
            root = self._root_note(step.chord, config.octave)
            fifth = self._fifth_note(step.chord, config.octave)
            half_dur = Duration(step.duration.ticks // 2, "half")
            notes.append(MotifNote(root, half_dur, 90))
            notes.append(MotifNote(fifth, half_dur, 80))
        return Motif(notes, "bass:root_fifth")

    def _gen_walking(self, config: BassConfig) -> Motif:
        """Quarter-note walking bass through chord tones and passing tones."""
        notes: list[MotifNote] = []
        scale = config.key.scale
        steps = config.progression.steps
        for i, step in enumerate(steps):
            chord_tones = self._chord_tones(step.chord, config.octave)
            beats = step.duration.ticks // QUARTER.ticks
            # Target: root of next chord (or current root if last)
            if i + 1 < len(steps):
                target = self._root_note(steps[i + 1].chord, config.octave)
            else:
                target = chord_tones[0]

            for beat in range(beats):
                if beat == 0:
                    # Always start on chord root
                    note = chord_tones[0]
                elif beat == beats - 1 and i + 1 < len(steps):
                    # Approach note: chromatic or scale step to target
                    note = self._approach_note(target, scale, config.octave)
                else:
                    # Pick a chord tone or passing tone
                    if self._rng.random() < 0.6 and len(chord_tones) > 1:
                        note = self._rng.choice(chord_tones[1:])
                    else:
                        note = self._passing_tone(chord_tones[0], target, scale, config.octave)
                notes.append(MotifNote(note, QUARTER, 85))
        return Motif(notes, "bass:walking")

    def _gen_arpeggiated(self, config: BassConfig) -> Motif:
        """Eighth-note arpeggios through chord tones."""
        notes: list[MotifNote] = []
        for step in config.progression.steps:
            chord_tones = self._chord_tones(step.chord, config.octave)
            eighths = step.duration.ticks // EIGHTH.ticks
            for i in range(eighths):
                tone = chord_tones[i % len(chord_tones)]
                notes.append(MotifNote(tone, EIGHTH, 80))
        return Motif(notes, "bass:arpeggiated")

    def _gen_syncopated(self, config: BassConfig) -> Motif:
        """Rhythmically displaced root patterns (funk/pop feel)."""
        notes: list[MotifNote] = []
        e = EIGHTH.ticks
        for step in config.progression.steps:
            root = self._root_note(step.chord, config.octave)
            fifth = self._fifth_note(step.chord, config.octave)
            total = step.duration.ticks
            # Syncopation: eighth, eighth rest (skip), dotted quarter, eighth
            # Pattern: hit - skip - hit - hit
            tick_used = 0
            # Beat 1: root eighth
            notes.append(MotifNote(root, EIGHTH, 100))
            tick_used += e
            # Beat 1-and: root eighth (anticipation)
            notes.append(MotifNote(root, EIGHTH, 70))
            tick_used += e
            # Remaining: split between fifth and root
            remaining = total - tick_used
            if remaining >= e * 2:
                mid_dur = Duration(remaining - e, "synco-hold")
                notes.append(MotifNote(fifth, mid_dur, 85))
                notes.append(MotifNote(root, EIGHTH, 95))
            elif remaining > 0:
                notes.append(MotifNote(fifth, Duration(remaining, "synco-tail"), 85))
        return Motif(notes, "bass:syncopated")

    # --- Helpers ---

    @staticmethod
    def _root_note(chord: Chord, octave: int) -> Note:
        """Get the root note of a chord at the given octave."""
        return Note(chord.root, octave)

    @staticmethod
    def _fifth_note(chord: Chord, octave: int) -> Note:
        """Get the fifth of a chord at the given octave."""
        chord_notes = chord.notes(octave)
        # Fifth is typically the 3rd element (index 2) for triads
        if len(chord_notes) >= 3:
            return chord_notes[2]
        # Fallback: transpose root up 7 semitones
        return Note(chord.root, octave).transpose(7)

    @staticmethod
    def _chord_tones(chord: Chord, octave: int) -> list[Note]:
        """Get all chord tones at the given octave."""
        return chord.notes(octave)

    def _passing_tone(self, current: Note, target: Note, scale: Scale, octave: int) -> Note:
        """Find a scale-aware passing tone between current and target."""
        scale_notes = self._scale_notes_in_range(scale, octave)
        if not scale_notes:
            return current

        mid_midi = (current.midi + target.midi) // 2
        # Find nearest scale tone to midpoint
        best = min(scale_notes, key=lambda n: abs(n.midi - mid_midi))
        return best

    def _approach_note(self, target: Note, scale: Scale, octave: int) -> Note:
        """Chromatic or scale approach to target note."""
        # Half step below target (chromatic approach)
        approach = target.transpose(-1)
        # Check if a scale tone is a whole step below (diatonic approach)
        scale_notes = self._scale_notes_in_range(scale, octave)
        for sn in scale_notes:
            if sn.midi == target.midi - 2:
                # 50/50 chromatic vs diatonic
                if self._rng.random() < 0.5:
                    return sn
                break
        return approach

    @staticmethod
    def _scale_notes_in_range(scale: Scale, octave: int) -> list[Note]:
        """Get scale notes spanning the bass range."""
        notes: list[Note] = []
        for oct in (octave, octave + 1):
            notes.extend(scale.notes(oct))
        return notes
