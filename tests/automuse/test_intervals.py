"""Tests for interval definitions and arithmetic."""

from automuse.core.intervals import (
    Interval, UNISON, MINOR_SECOND, MAJOR_SECOND, MINOR_THIRD, MAJOR_THIRD,
    PERFECT_FOURTH, TRITONE, PERFECT_FIFTH, MINOR_SIXTH, MAJOR_SIXTH,
    MINOR_SEVENTH, MAJOR_SEVENTH, OCTAVE, ALL_INTERVALS, interval_between,
)


class TestIntervalConstants:
    def test_semitone_values(self):
        expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        actual = [i.semitones for i in ALL_INTERVALS]
        assert actual == expected

    def test_all_have_names(self):
        for interval in ALL_INTERVALS:
            assert interval.name
            assert interval.short

    def test_unison(self):
        assert UNISON.semitones == 0
        assert UNISON.short == "P1"

    def test_octave(self):
        assert OCTAVE.semitones == 12
        assert OCTAVE.short == "P8"

    def test_tritone(self):
        assert TRITONE.semitones == 6


class TestIntervalArithmetic:
    def test_add(self):
        result = MAJOR_THIRD + MINOR_THIRD
        assert result.semitones == 7  # Perfect fifth

    def test_invert(self):
        assert MAJOR_THIRD.invert().semitones == 8  # Minor sixth
        assert PERFECT_FIFTH.invert().semitones == 5  # Perfect fourth
        assert MINOR_SECOND.invert().semitones == 11  # Major seventh
        assert UNISON.invert().semitones == 12  # Unison inverts to octave

    def test_lookup(self):
        assert interval_between(4) == MAJOR_THIRD
        assert interval_between(7) == PERFECT_FIFTH
        assert interval_between(16).semitones == 4  # Mod 12

    def test_unknown_interval(self):
        # All semitone distances 0-12 are covered, so this tests the mod behavior
        result = interval_between(15)
        assert result.semitones == 3
