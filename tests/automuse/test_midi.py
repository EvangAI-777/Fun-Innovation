"""Tests for MIDI file generation."""

import struct
import tempfile
from pathlib import Path

from automuse.core.notes import Note
from automuse.core.chords import Chord
from automuse.core.rhythm import Tempo, QUARTER, WHOLE, COMMON_TIME
from automuse.core.keys import Key
from automuse.harmony.progressions import ProgressionBuilder
from automuse.midi.writer import MidiWriter, MidiTrack, _write_varlen


class TestVarlen:
    def test_zero(self):
        assert _write_varlen(0) == b"\x00"

    def test_small(self):
        assert _write_varlen(0x7F) == b"\x7f"

    def test_two_bytes(self):
        assert _write_varlen(0x80) == b"\x81\x00"

    def test_480(self):
        # 480 = 0x1E0 -> variable-length: 0x83 0x60
        result = _write_varlen(480)
        assert len(result) == 2


class TestMidiTrack:
    def test_note_on_off(self):
        track = MidiTrack()
        track.note_on(0, 60, 100, 0)
        track.note_off(480, 60, 0, 0)
        assert len(track.events) == 2

    def test_add_note(self):
        track = MidiTrack()
        track.add_note(0, 60, 480)
        assert len(track.events) == 2  # note_on + note_off

    def test_set_tempo(self):
        track = MidiTrack()
        track.set_tempo(0, Tempo(120))
        assert len(track.events) == 1
        # Check it's a meta event (0xFF 0x51 0x03)
        assert track.events[0].data[:3] == b"\xFF\x51\x03"

    def test_set_time_signature(self):
        track = MidiTrack()
        track.set_time_signature(0, COMMON_TIME)
        assert len(track.events) == 1
        assert track.events[0].data[0:2] == b"\xFF\x58"

    def test_program_change(self):
        track = MidiTrack()
        track.program_change(0, 0, 0)  # Piano on channel 0
        assert len(track.events) == 1
        assert track.events[0].data[0] == 0xC0

    def test_build_produces_bytes(self):
        track = MidiTrack()
        track.add_note(0, 60, 480)
        raw = track._build()
        assert raw[:4] == b"MTrk"
        # Ends with end-of-track marker
        assert raw[-3:] == b"\xFF\x2F\x00"


class TestMidiWriter:
    def test_empty_file(self):
        writer = MidiWriter()
        writer.add_track()
        data = writer.to_bytes()
        assert data[:4] == b"MThd"

    def test_single_note(self):
        writer = MidiWriter()
        track = writer.add_track("Test")
        track.set_tempo(0, Tempo(120))
        writer.write_note(track, Note("C", 4), 0)
        data = writer.to_bytes()
        assert len(data) > 14  # Header + track header + events

    def test_write_chord(self):
        writer = MidiWriter()
        track = writer.add_track()
        writer.write_chord(track, Chord("C"), 0)
        # Should create 3 note pairs (C major triad)
        note_ons = [e for e in track.events if len(e.data) == 3 and (e.data[0] & 0xF0) == 0x90]
        assert len(note_ons) == 3

    def test_write_scale(self):
        writer = MidiWriter()
        track = writer.add_track()
        from automuse.core.scales import Scale
        notes = Scale("C", "major").notes(4)
        end_tick = writer.write_scale(track, notes)
        assert end_tick == 480 * 7  # 7 quarter notes

    def test_write_progression(self):
        writer = MidiWriter()
        track = writer.add_track()
        track.set_tempo(0, Tempo(120))
        builder = ProgressionBuilder(Key("C", "major"))
        prog = builder.from_template("I-IV-V-I")
        end_tick = writer.write_progression(track, prog)
        assert end_tick > 0

    def test_save_to_file(self):
        writer = MidiWriter()
        track = writer.add_track("Export Test")
        track.set_tempo(0, Tempo(120))
        writer.write_note(track, Note("C", 4), 0)
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = Path(f.name)
        writer.save(path)
        assert path.exists()
        assert path.stat().st_size > 0
        # Verify MIDI header
        with open(path, "rb") as f:
            header = f.read(4)
        assert header == b"MThd"
        path.unlink()

    def test_multi_track(self):
        writer = MidiWriter()
        t1 = writer.add_track("Piano")
        t2 = writer.add_track("Bass")
        writer.write_note(t1, Note("C", 4), 0)
        writer.write_note(t2, Note("C", 2), 0)
        data = writer.to_bytes()
        # Type 1 MIDI (multi-track)
        midi_type = struct.unpack(">H", data[8:10])[0]
        assert midi_type == 1
        n_tracks = struct.unpack(">h", data[10:12])[0]
        assert n_tracks == 2

    def test_ppqn(self):
        writer = MidiWriter(ppqn=960)
        assert writer.ppqn == 960
        writer.add_track()
        data = writer.to_bytes()
        ppqn = struct.unpack(">H", data[12:14])[0]
        assert ppqn == 960
