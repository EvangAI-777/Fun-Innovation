"""Tests for the counterpoint engine."""

import unittest

from automuse.core.keys import Key
from automuse.core.notes import Note
from automuse.core.rhythm import QUARTER
from automuse.compose.motif import Motif, MotifNote, MotifBuilder
from automuse.compose.counterpoint import (
    CounterpointStyle,
    CounterpointConfig,
    CounterpointGenerator,
)


class TestCounterpointStyle(unittest.TestCase):
    """Test CounterpointStyle enum."""

    def test_all_styles(self):
        self.assertEqual(len(CounterpointStyle), 5)

    def test_values(self):
        self.assertEqual(CounterpointStyle.PARALLEL_THIRDS.value, "parallel_thirds")
        self.assertEqual(CounterpointStyle.CONTRARY.value, "contrary")
        self.assertEqual(CounterpointStyle.FREE.value, "free")


class TestCounterpointConfig(unittest.TestCase):
    """Test CounterpointConfig creation."""

    def test_defaults(self):
        melody = MotifBuilder.from_notes(["C4", "D4", "E4", "F4"])
        key = Key("C", "major")
        cfg = CounterpointConfig(melody, key)
        self.assertEqual(cfg.style, CounterpointStyle.PARALLEL_THIRDS)
        self.assertEqual(cfg.interval_preference, 3)

    def test_custom(self):
        melody = MotifBuilder.from_notes(["C4", "D4", "E4"])
        key = Key("A", "minor")
        cfg = CounterpointConfig(melody, key, CounterpointStyle.CONTRARY, 6)
        self.assertEqual(cfg.style, CounterpointStyle.CONTRARY)
        self.assertEqual(cfg.interval_preference, 6)


class TestCounterpointGenerator(unittest.TestCase):
    """Test counterpoint generation across all styles."""

    def _make_melody(self, note_strs=None):
        if note_strs is None:
            note_strs = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
        return MotifBuilder.from_notes(note_strs)

    def _make_config(self, style=CounterpointStyle.PARALLEL_THIRDS, note_strs=None):
        melody = self._make_melody(note_strs)
        key = Key("C", "major")
        return CounterpointConfig(melody, key, style)

    def test_parallel_thirds_length(self):
        """PARALLEL_THIRDS produces same-length motif."""
        cfg = self._make_config(CounterpointStyle.PARALLEL_THIRDS)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        self.assertEqual(len(counter), len(cfg.melody))

    def test_parallel_thirds_interval(self):
        """PARALLEL_THIRDS maintains roughly a third above each note."""
        cfg = self._make_config(CounterpointStyle.PARALLEL_THIRDS)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        for m, c in zip(cfg.melody, counter):
            interval = abs(c.note.midi - m.note.midi)
            # Diatonic third is 3 or 4 semitones
            self.assertIn(interval, [3, 4], f"{m.note} -> {c.note}: interval {interval}")

    def test_parallel_sixths_length(self):
        """PARALLEL_SIXTHS produces same-length motif."""
        cfg = self._make_config(CounterpointStyle.PARALLEL_SIXTHS)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        self.assertEqual(len(counter), len(cfg.melody))

    def test_parallel_sixths_interval(self):
        """PARALLEL_SIXTHS maintains roughly a sixth above each note."""
        cfg = self._make_config(CounterpointStyle.PARALLEL_SIXTHS)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        for m, c in zip(cfg.melody, counter):
            interval = abs(c.note.midi - m.note.midi)
            # Diatonic sixth is 8 or 9 semitones
            self.assertIn(interval, [8, 9], f"{m.note} -> {c.note}: interval {interval}")

    def test_contrary_length(self):
        """CONTRARY produces same-length motif."""
        cfg = self._make_config(CounterpointStyle.CONTRARY)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        self.assertEqual(len(counter), len(cfg.melody))

    def test_contrary_direction(self):
        """CONTRARY moves opposite direction from melody."""
        cfg = self._make_config(CounterpointStyle.CONTRARY,
                                note_strs=["C4", "E4", "G4", "E4", "C4"])
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        mel = list(cfg.melody)
        ctr = list(counter)
        for i in range(1, len(mel)):
            mel_dir = mel[i].note.midi - mel[i - 1].note.midi
            ctr_dir = ctr[i].note.midi - ctr[i - 1].note.midi
            if mel_dir != 0:
                # When melody moves up, counter should move down (or vice versa)
                self.assertTrue(
                    (mel_dir > 0 and ctr_dir <= 0) or (mel_dir < 0 and ctr_dir >= 0),
                    f"Position {i}: melody dir={mel_dir}, counter dir={ctr_dir}"
                )

    def test_oblique_length(self):
        """OBLIQUE produces same-length motif."""
        cfg = self._make_config(CounterpointStyle.OBLIQUE)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        self.assertEqual(len(counter), len(cfg.melody))

    def test_oblique_holds_when_melody_moves(self):
        """OBLIQUE: counter holds when melody moves."""
        cfg = self._make_config(CounterpointStyle.OBLIQUE,
                                note_strs=["C4", "D4", "E4", "F4"])
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        ctr = list(counter)
        mel = list(cfg.melody)
        # Melody moves C->D, so counter should hold
        if mel[1].note.midi != mel[0].note.midi:
            self.assertEqual(ctr[1].note.midi, ctr[0].note.midi)

    def test_free_length(self):
        """FREE produces same-length motif."""
        cfg = self._make_config(CounterpointStyle.FREE)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        self.assertEqual(len(counter), len(cfg.melody))

    def test_seed_reproducibility(self):
        """Same seed produces identical output."""
        cfg = self._make_config(CounterpointStyle.FREE)
        gen1 = CounterpointGenerator(seed=123)
        gen2 = CounterpointGenerator(seed=123)
        c1 = gen1.generate(cfg)
        c2 = gen2.generate(cfg)
        for n1, n2 in zip(c1, c2):
            self.assertEqual(n1.note.midi, n2.note.midi)

    def test_different_seeds_differ(self):
        """Different seeds produce different output for FREE style."""
        cfg = self._make_config(CounterpointStyle.FREE)
        gen1 = CounterpointGenerator(seed=1)
        gen2 = CounterpointGenerator(seed=999)
        c1 = gen1.generate(cfg)
        c2 = gen2.generate(cfg)
        midis1 = [n.note.midi for n in c1]
        midis2 = [n.note.midi for n in c2]
        self.assertNotEqual(midis1, midis2)

    def test_diatonic_output(self):
        """Generated counterpoint should be diatonic to the key."""
        key = Key("C", "major")
        cfg = CounterpointConfig(self._make_melody(), key, CounterpointStyle.PARALLEL_THIRDS)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        scale_pcs = set(key.scale.pitch_classes())
        for mn in counter:
            self.assertIn(mn.note.pitch_class, scale_pcs, f"{mn.note} not in {key}")

    def test_preserves_durations(self):
        """Counter notes have same durations as melody notes."""
        cfg = self._make_config(CounterpointStyle.PARALLEL_THIRDS)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        for m, c in zip(cfg.melody, counter):
            self.assertEqual(m.duration.ticks, c.duration.ticks)


class TestCounterpointValidation(unittest.TestCase):
    """Test the validation method."""

    def test_valid_counterpoint(self):
        """Parallel thirds in C major should pass validation."""
        key = Key("C", "major")
        melody = MotifBuilder.from_notes(["C4", "D4", "E4", "F4"])
        cfg = CounterpointConfig(melody, key, CounterpointStyle.PARALLEL_THIRDS)
        gen = CounterpointGenerator(seed=42)
        counter = gen.generate(cfg)
        issues = CounterpointGenerator.validate(melody, counter, key)
        self.assertEqual(issues, [])

    def test_catches_parallel_fifths(self):
        """Validation should detect parallel fifths."""
        key = Key("C", "major")
        melody = Motif([
            MotifNote(Note.parse("C4"), QUARTER),
            MotifNote(Note.parse("D4"), QUARTER),
        ])
        # Manually create parallel fifths: C4-G4, D4-A4
        counter = Motif([
            MotifNote(Note.parse("G4"), QUARTER),
            MotifNote(Note.parse("A4"), QUARTER),
        ])
        issues = CounterpointGenerator.validate(melody, counter, key)
        found = any("Parallel fifths" in i for i in issues)
        self.assertTrue(found, f"Expected parallel fifths warning, got: {issues}")

    def test_catches_voice_crossing(self):
        """Validation should detect voice crossing."""
        key = Key("C", "major")
        melody = Motif([
            MotifNote(Note.parse("C4"), QUARTER),
            MotifNote(Note.parse("D4"), QUARTER),
        ])
        # Counter starts above (E4) then goes below melody (C3)
        counter = Motif([
            MotifNote(Note.parse("E4"), QUARTER),
            MotifNote(Note.parse("C3"), QUARTER),
        ])
        issues = CounterpointGenerator.validate(melody, counter, key)
        found = any("Voice crossing" in i for i in issues)
        self.assertTrue(found, f"Expected voice crossing warning, got: {issues}")

    def test_catches_range_violation(self):
        """Validation should detect voices more than 2 octaves apart."""
        key = Key("C", "major")
        melody = Motif([MotifNote(Note.parse("C4"), QUARTER)])
        counter = Motif([MotifNote(Note.parse("C7"), QUARTER)])
        issues = CounterpointGenerator.validate(melody, counter, key)
        found = any("Range violation" in i for i in issues)
        self.assertTrue(found, f"Expected range violation, got: {issues}")

    def test_catches_non_diatonic(self):
        """Validation should detect non-diatonic counter notes."""
        key = Key("C", "major")
        melody = Motif([MotifNote(Note.parse("C4"), QUARTER)])
        # F# is not in C major
        counter = Motif([MotifNote(Note.parse("F#4"), QUARTER)])
        issues = CounterpointGenerator.validate(melody, counter, key)
        found = any("Non-diatonic" in i for i in issues)
        self.assertTrue(found, f"Expected non-diatonic warning, got: {issues}")

    def test_length_mismatch(self):
        """Validation should catch mismatched melody/counter lengths."""
        key = Key("C", "major")
        melody = MotifBuilder.from_notes(["C4", "D4", "E4"])
        counter = MotifBuilder.from_notes(["E4", "F4"])
        issues = CounterpointGenerator.validate(melody, counter, key)
        found = any("Length mismatch" in i for i in issues)
        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
