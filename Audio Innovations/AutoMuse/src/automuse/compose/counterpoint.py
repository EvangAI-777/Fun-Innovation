"""Counterpoint engine -- generates secondary melodies against a primary melody.

Supports parallel thirds/sixths, contrary motion, oblique motion, and free
counterpoint. Enforces basic voice-leading rules: no parallel fifths/octaves,
no voice crossing, prefer imperfect consonances (3rds, 6ths).
"""

from __future__ import annotations

import random
from enum import Enum

from ..core.notes import Note, PitchClass
from ..core.keys import Key
from ..core.scales import Scale
from .motif import Motif, MotifNote


class CounterpointStyle(Enum):
    """Available counterpoint generation styles."""

    PARALLEL_THIRDS = "parallel_thirds"
    PARALLEL_SIXTHS = "parallel_sixths"
    CONTRARY = "contrary"
    OBLIQUE = "oblique"
    FREE = "free"


class CounterpointConfig:
    """Configuration for counterpoint generation."""

    __slots__ = ("melody", "key", "style", "interval_preference")

    def __init__(
        self,
        melody: Motif,
        key: Key,
        style: CounterpointStyle = CounterpointStyle.PARALLEL_THIRDS,
        interval_preference: int = 3,
    ) -> None:
        self.melody = melody
        self.key = key
        self.style = style
        self.interval_preference = interval_preference


class CounterpointGenerator:
    """Generates countermelodies using various contrapuntal techniques."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def generate(self, config: CounterpointConfig) -> Motif:
        """Create a countermelody from the given config."""
        style_map = {
            CounterpointStyle.PARALLEL_THIRDS: self._gen_parallel,
            CounterpointStyle.PARALLEL_SIXTHS: self._gen_parallel,
            CounterpointStyle.CONTRARY: self._gen_contrary,
            CounterpointStyle.OBLIQUE: self._gen_oblique,
            CounterpointStyle.FREE: self._gen_free,
        }
        handler = style_map[config.style]
        return handler(config)

    # --- Style generators ---

    def _gen_parallel(self, config: CounterpointConfig) -> Motif:
        """Parallel thirds or sixths: transpose each note by diatonic interval."""
        if config.style == CounterpointStyle.PARALLEL_SIXTHS:
            interval = 5  # 6th = 5 scale degrees up (1-indexed: degree+5)
        else:
            interval = 2  # 3rd = 2 scale degrees up

        scale_degrees = self._build_scale_degrees(config.key.scale)
        notes: list[MotifNote] = []
        for mn in config.melody:
            new_note = self._diatonic_transpose(mn.note, scale_degrees, interval)
            notes.append(MotifNote(new_note, mn.duration, mn.velocity))
        return Motif(notes, f"counter:{config.style.value}")

    def _gen_contrary(self, config: CounterpointConfig) -> Motif:
        """Contrary motion: when melody goes up, counter goes down by similar interval."""
        scale_degrees = self._build_scale_degrees(config.key.scale)
        melody_notes = list(config.melody)
        notes: list[MotifNote] = []

        # Start a third above the first note
        first_note = self._diatonic_transpose(melody_notes[0].note, scale_degrees, 2)
        notes.append(MotifNote(first_note, melody_notes[0].duration, melody_notes[0].velocity))

        prev_melody = melody_notes[0].note
        prev_counter = first_note

        for i in range(1, len(melody_notes)):
            mn = melody_notes[i]
            melody_interval = self._scale_degree_distance(prev_melody, mn.note, scale_degrees)

            # Move in opposite direction by similar magnitude
            counter_note = self._diatonic_transpose(prev_counter, scale_degrees, -melody_interval)
            notes.append(MotifNote(counter_note, mn.duration, mn.velocity))

            prev_melody = mn.note
            prev_counter = counter_note

        return Motif(notes, "counter:contrary")

    def _gen_oblique(self, config: CounterpointConfig) -> Motif:
        """Oblique motion: counter holds when melody moves; moves when melody holds."""
        scale_degrees = self._build_scale_degrees(config.key.scale)
        melody_notes = list(config.melody)
        notes: list[MotifNote] = []

        # Start a third above
        current_counter = self._diatonic_transpose(melody_notes[0].note, scale_degrees, 2)
        notes.append(MotifNote(current_counter, melody_notes[0].duration, melody_notes[0].velocity))

        for i in range(1, len(melody_notes)):
            mn = melody_notes[i]
            prev_mn = melody_notes[i - 1]
            melody_moved = mn.note.midi != prev_mn.note.midi

            if melody_moved:
                # Melody moved -> counter holds
                notes.append(MotifNote(current_counter, mn.duration, mn.velocity))
            else:
                # Melody holds -> counter moves (step up or down by one scale degree)
                direction = self._rng.choice([-1, 1])
                current_counter = self._diatonic_transpose(current_counter, scale_degrees, direction)
                notes.append(MotifNote(current_counter, mn.duration, mn.velocity))

        return Motif(notes, "counter:oblique")

    def _gen_free(self, config: CounterpointConfig) -> Motif:
        """Free counterpoint: mix of contrary/oblique with consonance bias."""
        scale_degrees = self._build_scale_degrees(config.key.scale)
        melody_notes = list(config.melody)
        notes: list[MotifNote] = []

        # Start a third above
        current_counter = self._diatonic_transpose(melody_notes[0].note, scale_degrees, 2)
        notes.append(MotifNote(current_counter, melody_notes[0].duration, melody_notes[0].velocity))

        prev_melody = melody_notes[0].note

        for i in range(1, len(melody_notes)):
            mn = melody_notes[i]
            melody_interval = self._scale_degree_distance(prev_melody, mn.note, scale_degrees)

            roll = self._rng.random()
            if roll < 0.4:
                # Contrary motion
                candidate = self._diatonic_transpose(current_counter, scale_degrees, -melody_interval)
            elif roll < 0.65:
                # Oblique: hold
                candidate = current_counter
            elif roll < 0.85:
                # Parallel: move in same direction
                candidate = self._diatonic_transpose(current_counter, scale_degrees, melody_interval)
            else:
                # Consonant leap: find a note a 3rd, 5th, or 6th from melody
                consonant_intervals = [2, 4, 5]  # 3rd, 5th, 6th in scale degrees
                interval = self._rng.choice(consonant_intervals)
                candidate = self._diatonic_transpose(mn.note, scale_degrees, interval)

            # Check for parallel fifths/octaves with previous pair and adjust
            if len(notes) >= 1:
                prev_counter_note = notes[-1].note
                prev_interval = abs(prev_melody.midi - prev_counter_note.midi) % 12
                new_interval = abs(mn.note.midi - candidate.midi) % 12
                # If both are perfect fifths (7) or octaves (0/12), nudge
                if prev_interval in (0, 7) and new_interval == prev_interval:
                    candidate = self._diatonic_transpose(candidate, scale_degrees, 1)

            current_counter = candidate
            notes.append(MotifNote(current_counter, mn.duration, mn.velocity))
            prev_melody = mn.note

        return Motif(notes, "counter:free")

    # --- Diatonic helpers ---

    @staticmethod
    def _build_scale_degrees(scale: Scale) -> list[int]:
        """Build a list of MIDI offsets for one octave of the scale.

        Returns the semitone interval pattern, e.g. [0, 2, 4, 5, 7, 9, 11]
        for a major scale.
        """
        return list(scale.scale_type.intervals)

    @staticmethod
    def _diatonic_transpose(note: Note, scale_degrees: list[int], interval: int) -> Note:
        """Transpose a note by a number of scale degrees (not semitones).

        Positive interval = up, negative = down.
        """
        root_midi = note.midi
        # Find the scale degree closest to this note
        pc_value = note.pitch_class.value
        base_octave = note.octave
        degree_count = len(scale_degrees)

        # Build a reference: which degree is this note nearest to?
        # Scale root of this octave starts at a base MIDI
        # We work relative to the note's pitch class within the scale
        best_degree = 0
        best_dist = 999
        for i, offset in enumerate(scale_degrees):
            dist = abs((pc_value - offset) % 12)
            alt_dist = 12 - dist
            d = min(dist, alt_dist)
            if d < best_dist:
                best_dist = d
                best_degree = i

        # Compute new degree with wrapping
        new_degree = best_degree + interval
        octave_shift = 0
        while new_degree >= degree_count:
            new_degree -= degree_count
            octave_shift += 1
        while new_degree < 0:
            new_degree += degree_count
            octave_shift -= 1

        # Reconstruct MIDI note
        # The scale root pitch class value
        root_pc = scale_degrees[0]  # always 0 for scale-relative
        new_semitone_offset = scale_degrees[new_degree]
        # The note's "scale root" is at (base_octave+1)*12 aligned to the scale root
        # But we need to work from the actual scale root pitch class
        # Simplification: use the original note's octave as anchor
        new_midi = (base_octave + 1 + octave_shift) * 12 + (pc_value - (pc_value % 12)) + new_semitone_offset
        # Correct: anchor to the note's octave MIDI base and the scale degree offset
        # Note octave base MIDI = (octave + 1) * 12
        oct_base = (base_octave + 1 + octave_shift) * 12
        new_midi = oct_base + new_semitone_offset

        return Note.from_midi(new_midi)

    @staticmethod
    def _scale_degree_distance(note_a: Note, note_b: Note, scale_degrees: list[int]) -> int:
        """Count how many scale degrees separate two notes (signed).

        Positive = note_b is higher, negative = note_b is lower.
        """
        degree_count = len(scale_degrees)

        def _find_degree_and_octave(note: Note) -> tuple[int, int]:
            pc = note.pitch_class.value
            octave = note.octave
            best_deg = 0
            best_dist = 999
            for i, offset in enumerate(scale_degrees):
                dist = abs(pc - offset)
                if dist < best_dist:
                    best_dist = dist
                    best_deg = i
            return best_deg, octave

        deg_a, oct_a = _find_degree_and_octave(note_a)
        deg_b, oct_b = _find_degree_and_octave(note_b)

        return (oct_b - oct_a) * degree_count + (deg_b - deg_a)

    # --- Validation ---

    @staticmethod
    def validate(melody: Motif, counter: Motif, key: Key) -> list[str]:
        """Check counterpoint for voice-leading issues.

        Returns a list of warning strings. Empty list = no issues found.
        Checks: parallel fifths/octaves, voice crossing, range, diatonicism.
        """
        issues: list[str] = []
        mel_notes = list(melody)
        ctr_notes = list(counter)

        if len(mel_notes) != len(ctr_notes):
            issues.append(f"Length mismatch: melody={len(mel_notes)}, counter={len(ctr_notes)}")
            return issues

        scale_pcs = set(key.scale.pitch_classes())

        prev_mel_midi: int | None = None
        prev_ctr_midi: int | None = None

        for i, (m, c) in enumerate(zip(mel_notes, ctr_notes)):
            m_midi = m.note.midi
            c_midi = c.note.midi

            # Voice crossing: counter shouldn't go below melody if it started above
            # (or vice versa). We check simple crossing.
            if i == 0:
                counter_above = c_midi >= m_midi
            else:
                if counter_above and c_midi < m_midi:
                    issues.append(f"Voice crossing at position {i}: counter goes below melody")
                elif not counter_above and c_midi > m_midi:
                    issues.append(f"Voice crossing at position {i}: counter goes above melody")

            # Parallel fifths and octaves
            if prev_mel_midi is not None and prev_ctr_midi is not None:
                prev_interval = abs(prev_mel_midi - prev_ctr_midi) % 12
                curr_interval = abs(m_midi - c_midi) % 12

                # Both pairs form a perfect fifth (7 semitones)
                if prev_interval == 7 and curr_interval == 7:
                    # Check parallel (both voices move in same direction)
                    mel_dir = m_midi - prev_mel_midi
                    ctr_dir = c_midi - prev_ctr_midi
                    if mel_dir != 0 and ctr_dir != 0 and (mel_dir > 0) == (ctr_dir > 0):
                        issues.append(f"Parallel fifths at positions {i - 1}-{i}")

                # Both pairs form a unison/octave (0 semitones mod 12)
                if prev_interval == 0 and curr_interval == 0:
                    mel_dir = m_midi - prev_mel_midi
                    ctr_dir = c_midi - prev_ctr_midi
                    if mel_dir != 0 and ctr_dir != 0 and (mel_dir > 0) == (ctr_dir > 0):
                        issues.append(f"Parallel octaves at positions {i - 1}-{i}")

            # Range check: counter shouldn't be more than 2 octaves from melody
            if abs(m_midi - c_midi) > 24:
                issues.append(f"Range violation at position {i}: voices {abs(m_midi - c_midi)} semitones apart")

            # Diatonicism check for counter voice
            if c.note.pitch_class not in scale_pcs:
                issues.append(f"Non-diatonic counter note at position {i}: {c.note}")

            prev_mel_midi = m_midi
            prev_ctr_midi = c_midi

        return issues
