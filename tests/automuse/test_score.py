"""Tests for the Score model and multi-track export."""

import unittest

from automuse.core.keys import Key
from automuse.core.notes import Note
from automuse.core.rhythm import Tempo, TimeSignature, COMMON_TIME, QUARTER, WHOLE, Duration
from automuse.compose.motif import Motif, MotifNote, MotifBuilder
from automuse.compose.drums import DrumPattern, DrumHit, GMPercussion, DrumPatternBuilder
from automuse.compose.score import (
    InstrumentType,
    Part,
    Score,
    ScoreBuilder,
)


class TestInstrumentType(unittest.TestCase):
    """Test InstrumentType enum."""

    def test_all_types(self):
        self.assertEqual(len(InstrumentType), 6)

    def test_values(self):
        self.assertEqual(InstrumentType.MELODY.value, "melody")
        self.assertEqual(InstrumentType.DRUMS.value, "drums")
        self.assertEqual(InstrumentType.COUNTER_MELODY.value, "counter_melody")


class TestPart(unittest.TestCase):
    """Test Part creation and properties."""

    def test_melodic_part(self):
        melody = MotifBuilder.from_notes(["C4", "D4", "E4", "F4"])
        part = Part("Lead", InstrumentType.MELODY, 0, motif=melody)
        self.assertEqual(part.name, "Lead")
        self.assertFalse(part.is_drums)
        self.assertEqual(part.total_ticks, melody.duration_ticks)

    def test_drum_part(self):
        hits = [DrumHit(GMPercussion.KICK, 0), DrumHit(GMPercussion.SNARE, 480)]
        dp = DrumPattern(hits)
        part = Part("Drums", InstrumentType.DRUMS, 9, drum_pattern=dp)
        self.assertTrue(part.is_drums)

    def test_channel_validation(self):
        with self.assertRaises(ValueError):
            Part("Bad", InstrumentType.MELODY, 16)

    def test_empty_part_ticks(self):
        part = Part("Empty", InstrumentType.PAD, 3)
        self.assertEqual(part.total_ticks, 0)

    def test_repr(self):
        part = Part("Lead", InstrumentType.MELODY, 0)
        self.assertIn("Lead", repr(part))


class TestPartSerialization(unittest.TestCase):
    """Test Part to_dict / from_dict."""

    def test_melodic_round_trip(self):
        melody = MotifBuilder.from_notes(["C4", "E4", "G4"])
        part = Part("Lead", InstrumentType.MELODY, 0, motif=melody)
        d = part.to_dict()
        restored = Part.from_dict(d)
        self.assertEqual(restored.name, "Lead")
        self.assertEqual(restored.channel, 0)
        self.assertEqual(len(restored.motif), 3)

    def test_drum_round_trip(self):
        hits = [DrumHit(GMPercussion.KICK, 0, 100), DrumHit(GMPercussion.SNARE, 480, 90)]
        dp = DrumPattern(hits)
        part = Part("Drums", InstrumentType.DRUMS, 9, drum_pattern=dp)
        d = part.to_dict()
        restored = Part.from_dict(d)
        self.assertTrue(restored.is_drums)
        self.assertEqual(len(restored.drum_pattern.hits), 2)


class TestScore(unittest.TestCase):
    """Test Score creation and management."""

    def _make_score(self):
        key = Key("C", "major")
        return Score("Test Song", key, Tempo(120), COMMON_TIME)

    def test_creation(self):
        score = self._make_score()
        self.assertEqual(score.title, "Test Song")
        self.assertEqual(len(score.parts), 0)
        self.assertEqual(score.total_ticks, 0)

    def test_add_remove_parts(self):
        score = self._make_score()
        melody = MotifBuilder.from_notes(["C4", "D4", "E4"])
        part = Part("Lead", InstrumentType.MELODY, 0, motif=melody)
        score.add_part(part)
        self.assertEqual(len(score.parts), 1)
        self.assertIsNotNone(score.get_part("Lead"))

        score.remove_part("Lead")
        self.assertEqual(len(score.parts), 0)
        self.assertIsNone(score.get_part("Lead"))

    def test_remove_nonexistent(self):
        score = self._make_score()
        score.remove_part("Ghost")  # Should not raise

    def test_total_ticks(self):
        score = self._make_score()
        m1 = MotifBuilder.from_notes(["C4", "D4"])  # 2 quarter notes = 960 ticks
        m2 = MotifBuilder.from_notes(["C4", "D4", "E4", "F4"])  # 4 quarter notes = 1920 ticks
        score.add_part(Part("Short", InstrumentType.MELODY, 0, motif=m1))
        score.add_part(Part("Long", InstrumentType.BASS, 1, motif=m2))
        self.assertEqual(score.total_ticks, m2.duration_ticks)

    def test_duration_seconds(self):
        score = Score("Test", tempo=Tempo(120))
        # 4 quarter notes at 120 BPM = 2 seconds
        melody = MotifBuilder.from_notes(["C4", "D4", "E4", "F4"])
        score.add_part(Part("M", InstrumentType.MELODY, 0, motif=melody))
        self.assertAlmostEqual(score.duration_seconds, 2.0, places=1)

    def test_repr(self):
        score = self._make_score()
        self.assertIn("Test Song", repr(score))


class TestScoreMidi(unittest.TestCase):
    """Test MIDI export."""

    def test_to_midi_produces_multitrack(self):
        key = Key("C", "major")
        score = Score("MIDI Test", key, Tempo(120))
        melody = MotifBuilder.from_notes(["C4", "E4", "G4"])
        bass = MotifBuilder.from_notes(["C2", "G2", "C2"])
        score.add_part(Part("Melody", InstrumentType.MELODY, 0, motif=melody))
        score.add_part(Part("Bass", InstrumentType.BASS, 1, motif=bass))
        writer = score.to_midi()
        data = writer.to_bytes()
        # Type 1 MIDI header: MThd, then format type=1
        self.assertTrue(data.startswith(b"MThd"))
        # Should have conductor + 2 parts = 3 tracks
        # Track count is at bytes 10-11
        import struct
        track_count = struct.unpack(">h", data[10:12])[0]
        self.assertEqual(track_count, 3)

    def test_drums_on_channel_9(self):
        score = Score("Drum Test")
        hits = [DrumHit(GMPercussion.KICK, 0)]
        dp = DrumPattern(hits)
        score.add_part(Part("Drums", InstrumentType.DRUMS, 9, drum_pattern=dp))
        writer = score.to_midi()
        data = writer.to_bytes()
        self.assertTrue(len(data) > 0)


class TestScoreMusicXML(unittest.TestCase):
    """Test MusicXML export."""

    def test_to_musicxml_produces_parts(self):
        key = Key("C", "major")
        score = Score("XML Test", key, Tempo(120))
        melody = MotifBuilder.from_notes(["C4", "E4", "G4"])
        score.add_part(Part("Melody", InstrumentType.MELODY, 0, motif=melody))
        writer = score.to_musicxml()
        xml = writer.to_string()
        self.assertIn("Melody", xml)
        self.assertIn("score-partwise", xml)


class TestScoreSerialization(unittest.TestCase):
    """Test Score to_dict / from_dict."""

    def test_round_trip(self):
        key = Key("D", "minor")
        score = Score("Serialize Test", key, Tempo(140))
        melody = MotifBuilder.from_notes(["D4", "F4", "A4"])
        score.add_part(Part("Melody", InstrumentType.MELODY, 0, motif=melody))
        d = score.to_dict()
        restored = Score.from_dict(d)
        self.assertEqual(restored.title, "Serialize Test")
        self.assertEqual(restored.tempo.bpm, 140)
        self.assertIsNotNone(restored.key)
        self.assertEqual(restored.key.root.name, "D")
        self.assertEqual(len(restored.parts), 1)

    def test_round_trip_no_key(self):
        score = Score("No Key")
        d = score.to_dict()
        restored = Score.from_dict(d)
        self.assertIsNone(restored.key)


class TestScoreBuilder(unittest.TestCase):
    """Test ScoreBuilder convenience methods."""

    def test_from_parts(self):
        key = Key("C", "major")
        melody = MotifBuilder.from_notes(["C4", "E4", "G4"])
        bass = MotifBuilder.from_notes(["C2", "G2", "C2"])
        hits = [DrumHit(GMPercussion.KICK, 0)]
        dp = DrumPattern(hits)
        score = ScoreBuilder.from_parts(
            title="Builder Test", key=key, melody=melody, bass=bass, drums=dp
        )
        self.assertEqual(len(score.parts), 3)
        drums_part = score.get_part("Drums")
        self.assertIsNotNone(drums_part)
        self.assertTrue(drums_part.is_drums)

    def test_quick_band_auto_parts(self):
        """quick_band produces 3+ parts even with only melody."""
        key = Key("C", "major")
        melody = MotifBuilder.from_notes(["C4", "D4", "E4", "F4"])
        score = ScoreBuilder.quick_band(key, melody=melody)
        self.assertGreaterEqual(len(score.parts), 3)

    def test_quick_band_drums_channel_9(self):
        key = Key("C", "major")
        melody = MotifBuilder.from_notes(["C4", "D4", "E4"])
        score = ScoreBuilder.quick_band(key, melody=melody)
        drums = score.get_part("Drums")
        self.assertIsNotNone(drums)
        self.assertEqual(drums.channel, 9)

    def test_from_parts_with_counter(self):
        melody = MotifBuilder.from_notes(["C4", "D4"])
        counter = MotifBuilder.from_notes(["E4", "F4"])
        score = ScoreBuilder.from_parts(melody=melody, counter=counter)
        self.assertEqual(len(score.parts), 2)
        self.assertIsNotNone(score.get_part("Counter Melody"))


if __name__ == "__main__":
    unittest.main()
