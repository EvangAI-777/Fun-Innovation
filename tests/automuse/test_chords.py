"""Tests for chord construction, parsing, and inversions."""

import pytest

from automuse.core.notes import PitchClass, Note
from automuse.core.chords import (
    Chord, ChordType, CHORD_TYPES,
    MAJOR_TRIAD, MINOR_TRIAD, DIMINISHED_TRIAD, AUGMENTED_TRIAD,
    MAJOR_7, MINOR_7, DOMINANT_7, DIMINISHED_7, HALF_DIMINISHED_7,
    SUS2, SUS4, POWER,
)


class TestChordTypes:
    def test_triad_intervals(self):
        assert MAJOR_TRIAD.intervals == (0, 4, 7)
        assert MINOR_TRIAD.intervals == (0, 3, 7)
        assert DIMINISHED_TRIAD.intervals == (0, 3, 6)
        assert AUGMENTED_TRIAD.intervals == (0, 4, 8)

    def test_seventh_intervals(self):
        assert MAJOR_7.intervals == (0, 4, 7, 11)
        assert MINOR_7.intervals == (0, 3, 7, 10)
        assert DOMINANT_7.intervals == (0, 4, 7, 10)

    def test_sus_chords(self):
        assert SUS2.intervals == (0, 2, 7)
        assert SUS4.intervals == (0, 5, 7)

    def test_power_chord(self):
        assert POWER.intervals == (0, 7)

    def test_chord_types_registry(self):
        assert len(CHORD_TYPES) >= 20
        assert "maj7" in CHORD_TYPES
        assert "m7" in CHORD_TYPES
        assert "dim7" in CHORD_TYPES


class TestChordConstruction:
    def test_c_major(self):
        chord = Chord("C")
        pcs = chord.pitch_classes()
        names = [str(pc) for pc in pcs]
        assert names == ["C", "E", "G"]

    def test_a_minor(self):
        chord = Chord("A", "m")
        pcs = chord.pitch_classes()
        names = [str(pc) for pc in pcs]
        assert names == ["A", "C", "E"]

    def test_g_dominant_7(self):
        chord = Chord("G", "7")
        pcs = chord.pitch_classes()
        assert len(pcs) == 4
        assert pcs[0] == PitchClass("G")
        assert pcs[1] == PitchClass("B")
        assert pcs[3] == PitchClass("F")

    def test_symbol(self):
        assert Chord("C").symbol == "C"
        assert Chord("A", "m").symbol == "Am"
        assert Chord("G", "7").symbol == "G7"
        assert Chord("F", "maj7").symbol == "Fmaj7"

    def test_notes_at_octave(self):
        notes = Chord("C").notes(4)
        assert len(notes) == 3
        assert notes[0] == Note("C", 4)
        assert notes[1] == Note("E", 4)
        assert notes[2] == Note("G", 4)


class TestChordParsing:
    def test_major(self):
        c = Chord.parse("C")
        assert c.root == PitchClass("C")
        assert c.chord_type == MAJOR_TRIAD

    def test_minor(self):
        c = Chord.parse("Am")
        assert c.root == PitchClass("A")
        assert c.chord_type == MINOR_TRIAD

    def test_seventh(self):
        c = Chord.parse("Cmaj7")
        assert c.root == PitchClass("C")
        assert c.chord_type == MAJOR_7

    def test_flat_root(self):
        c = Chord.parse("Bbm7")
        assert c.root == PitchClass("Bb")
        assert c.chord_type == MINOR_7

    def test_sharp_root(self):
        c = Chord.parse("F#dim")
        assert c.root == PitchClass("F#")
        assert c.chord_type == DIMINISHED_TRIAD

    def test_dominant_7(self):
        c = Chord.parse("G7")
        assert c.chord_type == DOMINANT_7

    def test_invalid_quality(self):
        with pytest.raises(ValueError):
            Chord.parse("Cxyz")


class TestChordInversions:
    def test_root_position(self):
        c = Chord("C", inversion=0)
        notes = c.notes(4)
        assert notes[0].pitch_class == PitchClass("C")

    def test_first_inversion(self):
        c = Chord("C", inversion=1)
        notes = c.notes(4)
        # E should be the lowest note
        assert notes[0].pitch_class == PitchClass("E")

    def test_second_inversion(self):
        c = Chord("C", inversion=2)
        notes = c.notes(4)
        # G should be the lowest
        assert notes[0].pitch_class == PitchClass("G")

    def test_inversion_out_of_range(self):
        with pytest.raises(ValueError):
            Chord("C", inversion=3)  # Triad only has inversions 0-2

    def test_seventh_chord_three_inversions(self):
        # 4-note chord allows inversions 0-3
        c = Chord("C", "maj7", inversion=3)
        assert c.inversion == 3

    def test_invert_method(self):
        c = Chord("C")
        c1 = c.invert(1)
        assert c1.inversion == 1
        assert c.inversion == 0  # Original unchanged


class TestChordEquality:
    def test_same_chord(self):
        assert Chord("C") == Chord("C")
        assert Chord("A", "m") == Chord("A", "m")

    def test_different_chord(self):
        assert Chord("C") != Chord("D")
        assert Chord("C") != Chord("C", "m")

    def test_hash(self):
        s = {Chord("C"), Chord("C"), Chord("A", "m")}
        assert len(s) == 2
