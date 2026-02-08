"""Tests for time signatures, durations, and tempo."""

import pytest

from automuse.core.rhythm import (
    TimeSignature, Duration, Tempo,
    COMMON_TIME, WALTZ_TIME, SIX_EIGHT, FIVE_FOUR, SEVEN_EIGHT,
    WHOLE, HALF, QUARTER, EIGHTH, SIXTEENTH,
)


class TestTimeSignature:
    def test_common_time(self):
        ts = COMMON_TIME
        assert ts.numerator == 4
        assert ts.denominator == 4
        assert str(ts) == "4/4"

    def test_waltz(self):
        assert WALTZ_TIME.beats_per_bar == 3
        assert WALTZ_TIME.beat_unit == 4

    def test_compound(self):
        assert SIX_EIGHT.is_compound
        assert SIX_EIGHT.feel == "compound (2 groups of 3)"

    def test_simple(self):
        assert not COMMON_TIME.is_compound
        assert COMMON_TIME.feel == "simple"

    def test_irregular(self):
        assert FIVE_FOUR.feel == "irregular"
        assert SEVEN_EIGHT.feel == "irregular"

    def test_ticks_per_bar(self):
        # 4/4 at 480 PPQN = 1920 ticks per bar
        assert COMMON_TIME.ticks_per_bar == 1920
        # 3/4 = 1440
        assert WALTZ_TIME.ticks_per_bar == 1440

    def test_invalid_numerator(self):
        with pytest.raises(ValueError):
            TimeSignature(0, 4)

    def test_invalid_denominator(self):
        with pytest.raises(ValueError):
            TimeSignature(4, 3)  # Not a power of 2

    def test_custom(self):
        ts = TimeSignature(11, 8)
        assert ts.beats_per_bar == 11
        assert ts.feel == "irregular"


class TestDuration:
    def test_standard_values(self):
        assert WHOLE.ticks == 1920
        assert HALF.ticks == 960
        assert QUARTER.ticks == 480
        assert EIGHTH.ticks == 240
        assert SIXTEENTH.ticks == 120

    def test_beats(self):
        assert QUARTER.beats == 1.0
        assert HALF.beats == 2.0
        assert EIGHTH.beats == 0.5

    def test_dotted(self):
        dotted_quarter = QUARTER.dotted()
        assert dotted_quarter.ticks == 720  # 480 + 240
        assert "dotted" in dotted_quarter.name

    def test_triplet(self):
        triplet_quarter = QUARTER.triplet()
        assert triplet_quarter.ticks == 320  # 480 * 2 / 3
        assert "triplet" in triplet_quarter.name


class TestTempo:
    def test_bpm(self):
        t = Tempo(120)
        assert t.bpm == 120

    def test_us_per_beat(self):
        t = Tempo(120)
        assert t.us_per_beat == 500_000  # 60M / 120

    def test_markings(self):
        assert Tempo(30).marking == "Grave"
        assert Tempo(60).marking == "Adagio"
        assert Tempo(80).marking == "Moderato"
        assert Tempo(120).marking == "Allegro"
        assert Tempo(170).marking == "Presto"
        assert Tempo(200).marking == "Prestissimo"

    def test_string(self):
        t = Tempo(120)
        assert "120" in str(t)
        assert "BPM" in str(t)

    def test_invalid(self):
        with pytest.raises(ValueError):
            Tempo(0)
        with pytest.raises(ValueError):
            Tempo(-60)
