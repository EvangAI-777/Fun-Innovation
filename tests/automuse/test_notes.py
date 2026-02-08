"""Tests for note and pitch class representation."""

from automuse.core.notes import PitchClass, Note, PITCH_CLASS_NAMES


class TestPitchClass:
    def test_from_name(self):
        pc = PitchClass("C")
        assert pc.value == 0
        assert pc.name == "C"

    def test_all_naturals(self):
        for name in ["C", "D", "E", "F", "G", "A", "B"]:
            pc = PitchClass(name)
            assert pc.name == name

    def test_sharps(self):
        assert PitchClass("C#").value == 1
        assert PitchClass("F#").value == 6
        assert PitchClass("G#").value == 8

    def test_enharmonic_flats(self):
        assert PitchClass("Db").value == PitchClass("C#").value
        assert PitchClass("Eb").value == PitchClass("D#").value
        assert PitchClass("Gb").value == PitchClass("F#").value
        assert PitchClass("Ab").value == PitchClass("G#").value
        assert PitchClass("Bb").value == PitchClass("A#").value

    def test_enharmonic_edge_cases(self):
        assert PitchClass("Cb").value == PitchClass("B").value
        assert PitchClass("E#").value == PitchClass("F").value
        assert PitchClass("B#").value == PitchClass("C").value
        assert PitchClass("Fb").value == PitchClass("E").value

    def test_from_int(self):
        for i in range(12):
            pc = PitchClass(i)
            assert pc.value == i
            assert pc.name == PITCH_CLASS_NAMES[i]

    def test_mod_12(self):
        assert PitchClass(12).value == 0
        assert PitchClass(15).value == 3
        assert PitchClass(-1).value == 11

    def test_transpose(self):
        c = PitchClass("C")
        assert c.transpose(4).name == "E"
        assert c.transpose(7).name == "G"
        assert c.transpose(12) == c

    def test_interval_to(self):
        c = PitchClass("C")
        e = PitchClass("E")
        assert c.interval_to(e) == 4
        assert e.interval_to(c) == 8

    def test_equality(self):
        assert PitchClass("C") == PitchClass(0)
        assert PitchClass("Db") == PitchClass("C#")

    def test_hash(self):
        s = {PitchClass("C"), PitchClass("C"), PitchClass("D")}
        assert len(s) == 2

    def test_invalid_name(self):
        import pytest
        with pytest.raises(ValueError):
            PitchClass("X")


class TestNote:
    def test_creation(self):
        n = Note("C", 4)
        assert str(n) == "C4"
        assert n.midi == 60

    def test_from_midi(self):
        n = Note.from_midi(69)
        assert n.pitch_class == PitchClass("A")
        assert n.octave == 4
        assert n.midi == 69

    def test_parse(self):
        assert Note.parse("C4").midi == 60
        assert Note.parse("A4").midi == 69
        assert Note.parse("Bb3").midi == 58
        assert Note.parse("F#5").midi == 78

    def test_frequency(self):
        a4 = Note("A", 4)
        assert abs(a4.frequency - 440.0) < 0.01
        a5 = Note("A", 5)
        assert abs(a5.frequency - 880.0) < 0.01

    def test_transpose(self):
        c4 = Note("C", 4)
        e4 = c4.transpose(4)
        assert e4.midi == 64

    def test_ordering(self):
        c4 = Note("C", 4)
        e4 = Note("E", 4)
        a3 = Note("A", 3)
        assert a3 < c4 < e4

    def test_equality(self):
        assert Note("C", 4) == Note.from_midi(60)

    def test_octave_range(self):
        low = Note.from_midi(0)
        assert low.octave == -1
        high = Note.from_midi(127)
        assert high.midi == 127

    def test_midi_roundtrip(self):
        for midi_num in [0, 21, 60, 69, 108, 127]:
            n = Note.from_midi(midi_num)
            assert n.midi == midi_num
