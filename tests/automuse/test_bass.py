"""Tests for the bass line generator."""

import unittest

from automuse.core.keys import Key
from automuse.core.rhythm import COMMON_TIME, WHOLE, QUARTER, EIGHTH
from automuse.harmony.progressions import ProgressionBuilder
from automuse.compose.bass import BassStyle, BassConfig, BassGenerator
from automuse.compose.motif import Motif


class TestBassStyle(unittest.TestCase):
    """Test BassStyle enum."""

    def test_all_styles(self):
        self.assertEqual(len(BassStyle), 5)

    def test_values(self):
        self.assertEqual(BassStyle.ROOT.value, "root")
        self.assertEqual(BassStyle.WALKING.value, "walking")


class TestBassConfig(unittest.TestCase):
    """Test BassConfig creation."""

    def _make_config(self, style=BassStyle.ROOT):
        key = Key("C", "major")
        prog = ProgressionBuilder(key).from_template("I-IV-V-I")
        return BassConfig(prog, key, octave=2, style=style)

    def test_defaults(self):
        key = Key("C", "major")
        prog = ProgressionBuilder(key).from_template("I-IV-V-I")
        config = BassConfig(prog, key)
        self.assertEqual(config.octave, 2)
        self.assertEqual(config.style, BassStyle.ROOT)
        self.assertEqual(config.time_sig, COMMON_TIME)


class TestBassGenerator(unittest.TestCase):
    """Test bass line generation for each style."""

    def _gen(self, style, template="I-IV-V-I", key_name="C", quality="major", seed=42):
        key = Key(key_name, quality)
        prog = ProgressionBuilder(key).from_template(template)
        config = BassConfig(prog, key, octave=2, style=style)
        gen = BassGenerator(seed=seed)
        return gen.generate(config), prog

    def test_root_returns_motif(self):
        motif, prog = self._gen(BassStyle.ROOT)
        self.assertIsInstance(motif, Motif)

    def test_root_one_note_per_chord(self):
        motif, prog = self._gen(BassStyle.ROOT)
        self.assertEqual(len(motif), len(prog))

    def test_root_notes_match_chord_roots(self):
        motif, prog = self._gen(BassStyle.ROOT)
        for mn, step in zip(motif, prog.steps):
            self.assertEqual(mn.note.pitch_class, step.chord.root)

    def test_root_fifth_two_notes_per_chord(self):
        motif, prog = self._gen(BassStyle.ROOT_FIFTH)
        self.assertEqual(len(motif), len(prog) * 2)

    def test_root_fifth_starts_on_root(self):
        motif, prog = self._gen(BassStyle.ROOT_FIFTH)
        # First note of each pair should be chord root
        for i, step in enumerate(prog.steps):
            self.assertEqual(motif[i * 2].note.pitch_class, step.chord.root)

    def test_walking_uses_quarter_notes(self):
        motif, _ = self._gen(BassStyle.WALKING)
        for mn in motif:
            self.assertEqual(mn.duration, QUARTER)

    def test_walking_length(self):
        motif, prog = self._gen(BassStyle.WALKING)
        # Each chord gets duration/quarter beats of notes
        expected = sum(step.duration.ticks // QUARTER.ticks for step in prog.steps)
        self.assertEqual(len(motif), expected)

    def test_arpeggiated_uses_eighth_notes(self):
        motif, _ = self._gen(BassStyle.ARPEGGIATED)
        for mn in motif:
            self.assertEqual(mn.duration, EIGHTH)

    def test_arpeggiated_length(self):
        motif, prog = self._gen(BassStyle.ARPEGGIATED)
        expected = sum(step.duration.ticks // EIGHTH.ticks for step in prog.steps)
        self.assertEqual(len(motif), expected)

    def test_syncopated_returns_motif(self):
        motif, _ = self._gen(BassStyle.SYNCOPATED)
        self.assertIsInstance(motif, Motif)
        self.assertGreater(len(motif), 0)

    def test_bass_range(self):
        """All generated notes should be in bass range (octave 1-3)."""
        for style in BassStyle:
            motif, _ = self._gen(style)
            for mn in motif:
                self.assertGreaterEqual(mn.note.octave, 1, f"Too low for {style}")
                self.assertLessEqual(mn.note.octave, 3, f"Too high for {style}")

    def test_seed_reproducibility(self):
        m1, _ = self._gen(BassStyle.WALKING, seed=123)
        m2, _ = self._gen(BassStyle.WALKING, seed=123)
        notes1 = [mn.note.midi for mn in m1]
        notes2 = [mn.note.midi for mn in m2]
        self.assertEqual(notes1, notes2)

    def test_different_seeds_differ(self):
        m1, _ = self._gen(BassStyle.WALKING, seed=1)
        m2, _ = self._gen(BassStyle.WALKING, seed=999)
        notes1 = [mn.note.midi for mn in m1]
        notes2 = [mn.note.midi for mn in m2]
        self.assertNotEqual(notes1, notes2)

    def test_minor_key(self):
        motif, _ = self._gen(BassStyle.ROOT, key_name="A", quality="minor")
        self.assertIsInstance(motif, Motif)
        self.assertGreater(len(motif), 0)

    def test_motif_name(self):
        for style in BassStyle:
            motif, _ = self._gen(style)
            self.assertIn("bass:", motif.name)


if __name__ == "__main__":
    unittest.main()
