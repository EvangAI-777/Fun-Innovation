"""Tests for the drum pattern engine."""

import unittest

from automuse.core.rhythm import COMMON_TIME, WALTZ_TIME, QUARTER, EIGHTH, SIXTEENTH
from automuse.compose.drums import (
    GMPercussion, DrumHit, DrumPattern, DrumPatternBuilder, DrumFill,
)


class TestGMPercussion(unittest.TestCase):
    """Test GM percussion MIDI mapping."""

    def test_kick_value(self):
        self.assertEqual(GMPercussion.KICK, 36)

    def test_snare_value(self):
        self.assertEqual(GMPercussion.SNARE, 38)

    def test_closed_hh_value(self):
        self.assertEqual(GMPercussion.CLOSED_HH, 42)

    def test_ride_value(self):
        self.assertEqual(GMPercussion.RIDE, 51)

    def test_all_unique(self):
        values = [p.value for p in GMPercussion]
        self.assertEqual(len(values), len(set(values)))


class TestDrumHit(unittest.TestCase):
    """Test DrumHit creation and validation."""

    def test_basic_creation(self):
        hit = DrumHit(GMPercussion.KICK, 0, 100)
        self.assertEqual(hit.instrument, GMPercussion.KICK)
        self.assertEqual(hit.tick, 0)
        self.assertEqual(hit.velocity, 100)

    def test_default_velocity(self):
        hit = DrumHit(GMPercussion.SNARE, 480)
        self.assertEqual(hit.velocity, 100)

    def test_invalid_velocity(self):
        with self.assertRaises(ValueError):
            DrumHit(GMPercussion.KICK, 0, 128)

    def test_negative_tick(self):
        with self.assertRaises(ValueError):
            DrumHit(GMPercussion.KICK, -1, 100)


class TestDrumPattern(unittest.TestCase):
    """Test DrumPattern container."""

    def _make_pattern(self):
        hits = [
            DrumHit(GMPercussion.KICK, 0, 110),
            DrumHit(GMPercussion.SNARE, 480, 110),
        ]
        return DrumPattern(hits)

    def test_ticks_common_time(self):
        pattern = self._make_pattern()
        self.assertEqual(pattern.ticks, COMMON_TIME.ticks_per_bar)

    def test_hits_sorted(self):
        hits = [
            DrumHit(GMPercussion.SNARE, 480, 110),
            DrumHit(GMPercussion.KICK, 0, 110),
        ]
        pattern = DrumPattern(hits)
        self.assertEqual(pattern.hits[0].tick, 0)
        self.assertEqual(pattern.hits[1].tick, 480)

    def test_repeat_two_bars(self):
        pattern = self._make_pattern()
        repeated = pattern.repeat(2)
        self.assertEqual(len(repeated), 4)
        bar_ticks = pattern.ticks
        self.assertEqual(repeated[2].tick, bar_ticks)
        self.assertEqual(repeated[3].tick, bar_ticks + 480)

    def test_vary_changes_velocities(self):
        pattern = self._make_pattern()
        varied = pattern.vary(probability=0.0, seed=42)
        # With probability=0, no ghost notes added, but velocities shift
        self.assertEqual(len(varied), len(pattern))

    def test_vary_with_ghosts(self):
        pattern = self._make_pattern()
        varied = pattern.vary(probability=1.0, seed=42)
        # High probability should add ghost notes
        self.assertGreater(len(varied), len(pattern))

    def test_instruments_used(self):
        pattern = self._make_pattern()
        instruments = pattern.instruments_used()
        self.assertIn(GMPercussion.KICK, instruments)
        self.assertIn(GMPercussion.SNARE, instruments)

    def test_len(self):
        pattern = self._make_pattern()
        self.assertEqual(len(pattern), 2)

    def test_repr(self):
        pattern = self._make_pattern()
        r = repr(pattern)
        self.assertIn("DrumPattern", r)
        self.assertIn("2 hits", r)


class TestDrumPatternBuilder(unittest.TestCase):
    """Test genre preset patterns."""

    def _assert_valid_pattern(self, pattern, min_hits=3):
        self.assertIsInstance(pattern, DrumPattern)
        self.assertGreaterEqual(len(pattern), min_hits)
        self.assertGreater(pattern.ticks, 0)

    def test_rock(self):
        pattern = DrumPatternBuilder.rock()
        self._assert_valid_pattern(pattern)
        instruments = pattern.instruments_used()
        self.assertIn(GMPercussion.KICK, instruments)
        self.assertIn(GMPercussion.SNARE, instruments)
        self.assertIn(GMPercussion.CLOSED_HH, instruments)

    def test_pop(self):
        pattern = DrumPatternBuilder.pop()
        self._assert_valid_pattern(pattern)
        instruments = pattern.instruments_used()
        self.assertIn(GMPercussion.OPEN_HH, instruments)

    def test_jazz_ride(self):
        pattern = DrumPatternBuilder.jazz_ride()
        self._assert_valid_pattern(pattern)
        self.assertIn(GMPercussion.RIDE, pattern.instruments_used())

    def test_hip_hop(self):
        pattern = DrumPatternBuilder.hip_hop()
        self._assert_valid_pattern(pattern)

    def test_edm_four_on_floor(self):
        pattern = DrumPatternBuilder.edm_four_on_floor()
        self._assert_valid_pattern(pattern)
        self.assertIn(GMPercussion.CLAP, pattern.instruments_used())

    def test_bossa_nova(self):
        pattern = DrumPatternBuilder.bossa_nova()
        self._assert_valid_pattern(pattern)
        self.assertIn(GMPercussion.RIMSHOT, pattern.instruments_used())

    def test_waltz_default_3_4(self):
        pattern = DrumPatternBuilder.waltz()
        self.assertEqual(pattern.time_sig, WALTZ_TIME)

    def test_shuffle(self):
        pattern = DrumPatternBuilder.shuffle()
        self._assert_valid_pattern(pattern)


class TestDrumFill(unittest.TestCase):
    """Test drum fill generation."""

    def test_simple_buildup(self):
        hits = DrumFill.simple_buildup()
        self.assertGreater(len(hits), 0)
        toms = {h.instrument for h in hits if h.instrument != GMPercussion.CRASH}
        self.assertTrue(toms.issubset({GMPercussion.LOW_TOM, GMPercussion.MID_TOM, GMPercussion.HIGH_TOM}))
        # Last hit should be crash
        self.assertEqual(hits[-1].instrument, GMPercussion.CRASH)

    def test_snare_roll(self):
        hits = DrumFill.snare_roll()
        self.assertGreater(len(hits), 0)
        self.assertTrue(all(h.instrument == GMPercussion.SNARE for h in hits))
        # Crescendo: last hit louder than first
        self.assertGreater(hits[-1].velocity, hits[0].velocity)

    def test_snare_roll_custom_length(self):
        short = DrumFill.snare_roll(480)
        long = DrumFill.snare_roll(1920)
        self.assertGreater(len(long), len(short))


if __name__ == "__main__":
    unittest.main()
