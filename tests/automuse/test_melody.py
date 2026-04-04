"""Tests for algorithmic melody generation."""

import pytest

from automuse.core.notes import Note
from automuse.core.rhythm import QUARTER, EIGHTH, HALF, Duration
from automuse.core.scales import Scale
from automuse.core.keys import Key
from automuse.compose.motif import Motif, MotifBuilder
from automuse.compose.melody import MelodyContour, MelodyConfig, MelodyGenerator


class TestMelodyContour:
    def test_all_contours_exist(self):
        assert len(MelodyContour) == 6
        for c in MelodyContour:
            assert isinstance(c.value, str)


class TestMelodyConfig:
    def test_defaults(self):
        scale = Scale("C", "major")
        cfg = MelodyConfig(scale)
        assert cfg.length == 8
        assert cfg.octave == 4
        assert cfg.contour == MelodyContour.ARCH
        assert cfg.step_bias == 0.7
        assert cfg.rest_probability == 0.0
        assert cfg.range_semitones == 12

    def test_step_bias_clamped(self):
        scale = Scale("C", "major")
        cfg = MelodyConfig(scale, step_bias=2.0)
        assert cfg.step_bias == 1.0
        cfg2 = MelodyConfig(scale, step_bias=-0.5)
        assert cfg2.step_bias == 0.0


class TestMelodyGenerator:
    def test_generate_default(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"))
        m = gen.generate(cfg)
        assert len(m) == 8
        assert m.duration_ticks > 0

    def test_generate_length(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"), length=16)
        m = gen.generate(cfg)
        assert len(m) == 16

    def test_seeded_reproducibility(self):
        m1 = MelodyGenerator(seed=123).generate(MelodyConfig(Scale("C", "major")))
        m2 = MelodyGenerator(seed=123).generate(MelodyConfig(Scale("C", "major")))
        assert [mn.note.midi for mn in m1] == [mn.note.midi for mn in m2]

    def test_different_seeds_differ(self):
        m1 = MelodyGenerator(seed=1).generate(MelodyConfig(Scale("C", "major"), length=16))
        m2 = MelodyGenerator(seed=999).generate(MelodyConfig(Scale("C", "major"), length=16))
        # Very unlikely to be identical with different seeds
        midis1 = [mn.note.midi for mn in m1]
        midis2 = [mn.note.midi for mn in m2]
        assert midis1 != midis2

    def test_ascending_contour(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"), length=8, contour=MelodyContour.ASCENDING)
        m = gen.generate(cfg)
        # On average, the melody should trend upward
        midis = [mn.note.midi for mn in m]
        assert midis[-1] >= midis[0]  # end should be higher than start

    def test_descending_contour(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"), length=8, contour=MelodyContour.DESCENDING)
        m = gen.generate(cfg)
        midis = [mn.note.midi for mn in m]
        assert midis[0] >= midis[-1]  # start should be higher than end

    def test_all_contours_generate(self):
        gen = MelodyGenerator(seed=42)
        for contour in MelodyContour:
            cfg = MelodyConfig(Scale("C", "major"), contour=contour)
            m = gen.generate(cfg)
            assert len(m) == 8

    def test_range_enforcement(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"), range_semitones=12)
        m = gen.generate(cfg)
        base_midi = Scale("C", "major").notes(4)[0].midi
        for mn in m:
            assert base_midi <= mn.note.midi <= base_midi + 12

    def test_custom_rhythm_pattern(self):
        gen = MelodyGenerator(seed=42)
        pattern = [QUARTER, EIGHTH, EIGHTH]
        cfg = MelodyConfig(Scale("C", "major"), length=6, rhythm_pattern=pattern)
        m = gen.generate(cfg)
        assert m[0].duration == QUARTER
        assert m[1].duration == EIGHTH
        assert m[2].duration == EIGHTH
        assert m[3].duration == QUARTER  # wraps

    def test_step_bias_all_steps(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"), length=16, step_bias=1.0)
        m = gen.generate(cfg)
        # With step_bias=1.0, all moves should be stepwise (distance 1 in scale)
        assert len(m) == 16

    def test_step_bias_all_skips(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"), length=16, step_bias=0.0)
        m = gen.generate(cfg)
        assert len(m) == 16

    def test_different_scales(self):
        gen = MelodyGenerator(seed=42)
        for scale_name in ["major", "minor pentatonic", "blues", "dorian"]:
            cfg = MelodyConfig(Scale("C", scale_name))
            m = gen.generate(cfg)
            assert len(m) == 8

    def test_generated_melody_in_key(self):
        gen = MelodyGenerator(seed=42)
        cfg = MelodyConfig(Scale("C", "major"), range_semitones=12)
        m = gen.generate(cfg)
        # All notes should be in C major scale
        c_major_pcs = set(Scale("C", "major").pitch_classes())
        for mn in m:
            assert mn.note.pitch_class in c_major_pcs


class TestMelodyDevelopment:
    def _base_motif(self) -> Motif:
        return MotifBuilder.from_notes(["C4", "D4", "E4", "F4"])

    def test_sequence(self):
        gen = MelodyGenerator(seed=42)
        m = self._base_motif()
        developed = gen.develop(m, "sequence")
        # Sequence = transpose by 2 semitones
        assert developed[0].note.midi == m[0].note.midi + 2

    def test_variation(self):
        gen = MelodyGenerator(seed=42)
        m = self._base_motif()
        developed = gen.develop(m, "variation")
        assert len(developed) == len(m)
        # Should be similar but not necessarily identical
        for orig, var in zip(m, developed):
            assert abs(orig.note.midi - var.note.midi) <= 1

    def test_fragmentation(self):
        gen = MelodyGenerator(seed=42)
        m = self._base_motif()
        developed = gen.develop(m, "fragmentation")
        assert len(developed) == 2  # half of 4

    def test_extension(self):
        gen = MelodyGenerator(seed=42)
        m = self._base_motif()
        developed = gen.develop(m, "extension")
        assert len(developed) > len(m)

    def test_unknown_technique(self):
        gen = MelodyGenerator(seed=42)
        with pytest.raises(ValueError, match="Unknown technique"):
            gen.develop(self._base_motif(), "nonexistent")

    def test_develop_empty_motif(self):
        gen = MelodyGenerator(seed=42)
        m = Motif([])
        for technique in ["sequence", "variation", "fragmentation", "extension"]:
            developed = gen.develop(m, technique)
            assert len(developed) == 0
