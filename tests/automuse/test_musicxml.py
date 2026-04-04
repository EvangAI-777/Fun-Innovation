"""Tests for MusicXML export."""

import pytest
from pathlib import Path

from automuse.core.notes import Note
from automuse.core.keys import Key
from automuse.core.rhythm import QUARTER, HALF, COMMON_TIME, WALTZ_TIME, TimeSignature
from automuse.core.scales import Scale
from automuse.compose.motif import MotifNote, Motif
from automuse.export.musicxml import MusicXMLWriter, _pitch_to_xml, _ticks_to_duration


class TestPitchConversion:
    def test_natural(self):
        step, alter, octave = _pitch_to_xml(Note("C", 4))
        assert step == "C"
        assert alter == 0
        assert octave == 4

    def test_sharp(self):
        step, alter, octave = _pitch_to_xml(Note("F#", 5))
        assert step == "F"
        assert alter == 1
        assert octave == 5

    def test_different_octaves(self):
        _, _, oct = _pitch_to_xml(Note("A", 3))
        assert oct == 3


class TestDurationConversion:
    def test_quarter(self):
        dur, note_type = _ticks_to_duration(480)
        assert note_type == "quarter"

    def test_half(self):
        dur, note_type = _ticks_to_duration(960)
        assert note_type == "half"

    def test_whole(self):
        dur, note_type = _ticks_to_duration(1920)
        assert note_type == "whole"

    def test_eighth(self):
        dur, note_type = _ticks_to_duration(240)
        assert note_type == "eighth"

    def test_sixteenth(self):
        dur, note_type = _ticks_to_duration(120)
        assert note_type == "16th"


class TestMusicXMLWriter:
    def test_add_part(self):
        w = MusicXMLWriter()
        pid = w.add_part("Piano")
        assert pid == "P1"
        pid2 = w.add_part("Guitar")
        assert pid2 == "P2"

    def test_write_notes_basic(self):
        w = MusicXMLWriter()
        pid = w.add_part()
        notes = [
            MotifNote(Note("C", 4), QUARTER),
            MotifNote(Note("E", 4), QUARTER),
            MotifNote(Note("G", 4), QUARTER),
        ]
        w.write_notes(pid, notes)
        xml = w.to_string()
        assert "<step>C</step>" in xml
        assert "<step>E</step>" in xml
        assert "<step>G</step>" in xml

    def test_write_notes_with_key(self):
        w = MusicXMLWriter()
        pid = w.add_part()
        notes = [MotifNote(Note("C", 4), QUARTER)]
        w.write_notes(pid, notes, key=Key("D", "major"))
        xml = w.to_string()
        assert "<fifths>2</fifths>" in xml  # D major = 2 sharps
        assert "<mode>major</mode>" in xml

    def test_write_notes_with_time_sig(self):
        w = MusicXMLWriter()
        pid = w.add_part()
        notes = [MotifNote(Note("C", 4), QUARTER)]
        w.write_notes(pid, notes, time_sig=WALTZ_TIME)
        xml = w.to_string()
        assert "<beats>3</beats>" in xml
        assert "<beat-type>4</beat-type>" in xml

    def test_write_notes_with_sharps(self):
        w = MusicXMLWriter()
        pid = w.add_part()
        notes = [MotifNote(Note("F#", 4), QUARTER)]
        w.write_notes(pid, notes)
        xml = w.to_string()
        assert "<step>F</step>" in xml
        assert "<alter>1</alter>" in xml

    def test_write_scale(self):
        w = MusicXMLWriter()
        pid = w.add_part()
        w.write_scale(pid, Scale("C", "major"), octave=4)
        xml = w.to_string()
        assert "<step>C</step>" in xml
        assert "<step>B</step>" in xml  # last note of C major

    def test_unknown_part_raises(self):
        w = MusicXMLWriter()
        with pytest.raises(ValueError, match="Unknown part"):
            w.write_notes("P99", [])

    def test_to_string_valid_xml(self):
        w = MusicXMLWriter(title="Test", composer="Tester")
        pid = w.add_part("Melody")
        notes = [MotifNote(Note("A", 4), QUARTER)]
        w.write_notes(pid, notes)
        xml = w.to_string()
        assert "<?xml" in xml
        assert "<score-partwise" in xml
        assert "<work-title>Test</work-title>" in xml
        assert "<software>AutoMuse</software>" in xml
        assert 'type="composer"' in xml
        assert "Tester" in xml

    def test_multi_part(self):
        w = MusicXMLWriter()
        p1 = w.add_part("Melody")
        p2 = w.add_part("Bass")
        w.write_notes(p1, [MotifNote(Note("C", 5), QUARTER)])
        w.write_notes(p2, [MotifNote(Note("C", 2), QUARTER)])
        xml = w.to_string()
        assert 'id="P1"' in xml
        assert 'id="P2"' in xml

    def test_save_to_file(self, tmp_path: Path):
        w = MusicXMLWriter()
        pid = w.add_part()
        w.write_notes(pid, [MotifNote(Note("C", 4), QUARTER)])
        out = w.save(tmp_path / "test.musicxml")
        assert out.exists()
        content = out.read_text()
        assert "<score-partwise" in content

    def test_empty_part(self):
        w = MusicXMLWriter()
        w.add_part()
        xml = w.to_string()
        assert '<measure number="1"' in xml  # empty measure

    def test_dynamics_mapping(self):
        w = MusicXMLWriter()
        pid = w.add_part()
        # Loud note
        w.write_notes(pid, [MotifNote(Note("C", 4), QUARTER, velocity=120)])
        xml = w.to_string()
        assert "<f />" in xml or "<f/>" in xml
