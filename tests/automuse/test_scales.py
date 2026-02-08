"""Tests for scale definitions, construction, and operations."""

import pytest

from automuse.core.notes import PitchClass
from automuse.core.scales import (
    Scale, ScaleType, SCALE_TYPES,
    MAJOR, DORIAN, PHRYGIAN, LYDIAN, MIXOLYDIAN, AEOLIAN, LOCRIAN,
    NATURAL_MINOR, HARMONIC_MINOR, MELODIC_MINOR,
    MAJOR_PENTATONIC, MINOR_PENTATONIC, BLUES,
    WHOLE_TONE, CHROMATIC,
    PHRYGIAN_DOMINANT, HIRAJOSHI,
)


class TestScaleTypes:
    def test_all_registered(self):
        assert len(SCALE_TYPES) >= 25

    def test_major_intervals(self):
        assert MAJOR.intervals == (0, 2, 4, 5, 7, 9, 11)

    def test_natural_minor_equals_aeolian(self):
        assert NATURAL_MINOR.intervals == AEOLIAN.intervals

    def test_chromatic_has_12_notes(self):
        assert len(CHROMATIC.intervals) == 12

    def test_pentatonic_has_5_notes(self):
        assert MAJOR_PENTATONIC.degree_count == 5
        assert MINOR_PENTATONIC.degree_count == 5

    def test_blues_has_6_notes(self):
        assert BLUES.degree_count == 6

    def test_all_modes_have_7_notes(self):
        modes = [MAJOR, DORIAN, PHRYGIAN, LYDIAN, MIXOLYDIAN, AEOLIAN, LOCRIAN]
        for mode in modes:
            assert mode.degree_count == 7, f"{mode.name} should have 7 degrees"


class TestScaleConstruction:
    def test_c_major(self):
        scale = Scale("C", "major")
        names = [str(pc) for pc in scale.pitch_classes()]
        assert names == ["C", "D", "E", "F", "G", "A", "B"]

    def test_d_dorian(self):
        scale = Scale("D", "dorian")
        names = [str(pc) for pc in scale.pitch_classes()]
        # D Dorian: D E F G A B C
        assert names[0] == "D"
        assert len(names) == 7

    def test_a_minor_pentatonic(self):
        scale = Scale("A", "minor pentatonic")
        names = [str(pc) for pc in scale.pitch_classes()]
        assert len(names) == 5
        assert names[0] == "A"

    def test_from_string(self):
        scale = Scale("Bb", "blues")
        assert scale.root == PitchClass("Bb")
        assert scale.scale_type == BLUES

    def test_invalid_scale_type(self):
        with pytest.raises(ValueError, match="Unknown scale type"):
            Scale("C", "nonexistent")

    def test_name(self):
        assert Scale("D", "dorian").name == "D dorian"
        assert Scale("C", "major").name == "C major"

    def test_notes_have_octave(self):
        notes = Scale("C", "major").notes(4)
        assert all(n.octave >= 4 for n in notes)
        assert notes[0].midi == 60  # C4

    def test_degree(self):
        scale = Scale("C", "major")
        assert scale.degree(1) == PitchClass("C")
        assert scale.degree(3) == PitchClass("E")
        assert scale.degree(5) == PitchClass("G")

    def test_degree_out_of_range(self):
        scale = Scale("C", "major")
        with pytest.raises(ValueError):
            scale.degree(0)
        with pytest.raises(ValueError):
            scale.degree(8)

    def test_contains(self):
        c_major = Scale("C", "major")
        assert c_major.contains("C")
        assert c_major.contains("E")
        assert not c_major.contains("C#")
        assert not c_major.contains("Eb")

    def test_len(self):
        assert len(Scale("C", "major")) == 7
        assert len(Scale("C", "chromatic")) == 12
        assert len(Scale("A", "minor pentatonic")) == 5

    def test_exotic_scales_exist(self):
        assert Scale("E", "phrygian dominant")
        assert Scale("A", "hungarian minor")
        assert Scale("D", "hirajoshi")
        assert Scale("C", "whole tone")


class TestScaleTheory:
    def test_modes_are_rotations(self):
        """All 7 modes of C major contain the same pitch classes."""
        c_major_pcs = set(Scale("C", "major").pitch_classes())
        d_dorian_pcs = set(Scale("D", "dorian").pitch_classes())
        e_phrygian_pcs = set(Scale("E", "phrygian").pitch_classes())
        assert c_major_pcs == d_dorian_pcs == e_phrygian_pcs

    def test_harmonic_minor_raised_seventh(self):
        """Harmonic minor raises the 7th degree relative to natural minor."""
        a_nat = Scale("A", "natural minor")
        a_harm = Scale("A", "harmonic minor")
        nat_7 = a_nat.degree(7)
        harm_7 = a_harm.degree(7)
        # Natural minor 7th is G (10 semitones), harmonic is G# (11 semitones)
        assert nat_7.interval_to(harm_7) == 1

    def test_whole_tone_all_whole_steps(self):
        """Whole tone scale has uniform 2-semitone intervals."""
        intervals = WHOLE_TONE.intervals
        for i in range(1, len(intervals)):
            assert intervals[i] - intervals[i - 1] == 2
