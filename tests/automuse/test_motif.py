"""Tests for motif/pattern system."""

import pytest

from automuse.core.notes import Note
from automuse.core.rhythm import QUARTER, HALF, EIGHTH, Duration
from automuse.core.scales import Scale
from automuse.core.keys import Key
from automuse.compose.motif import MotifNote, Motif, MotifBuilder


class TestMotifNote:
    def test_creation(self):
        mn = MotifNote(Note("C", 4), QUARTER, 80)
        assert mn.note == Note("C", 4)
        assert mn.duration == QUARTER
        assert mn.velocity == 80

    def test_default_velocity(self):
        mn = MotifNote(Note("C", 4), QUARTER)
        assert mn.velocity == 80

    def test_invalid_velocity(self):
        with pytest.raises(ValueError):
            MotifNote(Note("C", 4), QUARTER, 128)
        with pytest.raises(ValueError):
            MotifNote(Note("C", 4), QUARTER, -1)

    def test_transpose(self):
        mn = MotifNote(Note("C", 4), QUARTER, 90)
        transposed = mn.transpose(7)
        assert transposed.note == Note("G", 4)
        assert transposed.duration == QUARTER
        assert transposed.velocity == 90

    def test_str(self):
        mn = MotifNote(Note("C", 4), QUARTER, 80)
        assert "C4" in str(mn)


class TestMotif:
    def _c_major_motif(self) -> Motif:
        return MotifBuilder.from_notes(["C4", "E4", "G4", "C5"])

    def test_creation(self):
        m = self._c_major_motif()
        assert len(m) == 4
        assert m[0].note == Note("C", 4)
        assert m[3].note == Note("C", 5)

    def test_duration_ticks(self):
        m = self._c_major_motif()
        assert m.duration_ticks == 4 * QUARTER.ticks

    def test_pitch_classes(self):
        m = self._c_major_motif()
        names = [pc.name for pc in m.pitch_classes]
        assert names == ["C", "E", "G", "C"]

    def test_transpose(self):
        m = self._c_major_motif()
        t = m.transpose(2)
        assert t[0].note == Note("D", 4)
        assert t[1].note == Note("F#", 4)

    def test_invert_default_axis(self):
        m = MotifBuilder.from_notes(["C4", "E4", "G4"])
        inv = m.invert()
        # C4 is axis. E4 is +4 from C4, so inversion is -4 = Ab3
        assert inv[0].note == Note("C", 4)  # axis stays
        assert inv[1].note.midi == Note("C", 4).midi - 4  # Ab3

    def test_invert_custom_axis(self):
        m = MotifBuilder.from_notes(["C4", "E4"])
        inv = m.invert(axis=Note("E", 4))
        # E4 axis. C4 is -4 from E4, inversion is E4+4 = G#4
        assert inv[0].note.midi == Note("E", 4).midi + 4
        assert inv[1].note == Note("E", 4)  # axis stays

    def test_retrograde(self):
        m = self._c_major_motif()
        r = m.retrograde()
        assert r[0].note == Note("C", 5)
        assert r[3].note == Note("C", 4)
        assert len(r) == 4

    def test_augment(self):
        m = self._c_major_motif()
        aug = m.augment(2.0)
        assert aug.duration_ticks == m.duration_ticks * 2

    def test_diminish(self):
        m = self._c_major_motif()
        dim = m.diminish(2.0)
        assert dim.duration_ticks == m.duration_ticks // 2

    def test_diminish_minimum_tick(self):
        m = Motif([MotifNote(Note("C", 4), Duration(1, "tiny"))])
        dim = m.diminish(100.0)
        assert dim[0].duration.ticks >= 1

    def test_in_key_true(self):
        m = self._c_major_motif()
        assert m.in_key(Key("C", "major"))

    def test_in_key_false(self):
        m = MotifBuilder.from_notes(["C4", "E4", "G#4"])
        assert not m.in_key(Key("C", "major"))

    def test_to_notes(self):
        m = self._c_major_motif()
        notes = m.to_notes()
        assert all(isinstance(n, Note) for n in notes)
        assert len(notes) == 4

    def test_empty_motif(self):
        m = Motif([])
        assert len(m) == 0
        assert m.duration_ticks == 0
        inv = m.invert()
        assert len(inv) == 0

    def test_iteration(self):
        m = self._c_major_motif()
        assert len(list(m)) == 4

    def test_str(self):
        m = self._c_major_motif()
        s = str(m)
        assert "C4" in s and "C5" in s


class TestMotifBuilder:
    def test_from_degrees(self):
        scale = Scale("C", "major")
        m = MotifBuilder.from_degrees(scale, [1, 3, 5], octave=4)
        assert m[0].note == Note("C", 4)
        assert m[1].note == Note("E", 4)
        assert m[2].note == Note("G", 4)

    def test_from_degrees_octave_wrap(self):
        scale = Scale("C", "major")
        m = MotifBuilder.from_degrees(scale, [1, 8], octave=4)
        # Degree 8 = degree 1 + one octave
        assert m[1].note.midi == m[0].note.midi + 12

    def test_from_notes(self):
        m = MotifBuilder.from_notes(["C4", "Bb3", "F#5"])
        assert len(m) == 3
        assert m[0].note == Note("C", 4)

    def test_from_intervals(self):
        m = MotifBuilder.from_intervals(Note("C", 4), [4, 3])
        assert m[0].note == Note("C", 4)   # root
        assert m[1].note == Note("E", 4)   # +4 semitones
        assert m[2].note == Note("G", 4)   # +3 more semitones

    def test_custom_duration_and_velocity(self):
        m = MotifBuilder.from_notes(["C4", "E4"], duration=HALF, velocity=100)
        assert m[0].duration == HALF
        assert m[0].velocity == 100
