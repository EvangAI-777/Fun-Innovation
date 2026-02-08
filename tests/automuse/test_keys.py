"""Tests for key signatures, diatonic harmony, and modulation."""

import pytest

from automuse.core.notes import PitchClass
from automuse.core.keys import Key


class TestKeyConstruction:
    def test_c_major(self):
        k = Key("C", "major")
        assert k.root == PitchClass("C")
        assert k.quality == "major"
        assert k.name == "C major"

    def test_a_minor(self):
        k = Key("A", "minor")
        assert k.quality == "minor"

    def test_invalid_quality(self):
        with pytest.raises(ValueError, match="major.*minor"):
            Key("C", "dorian")


class TestKeySignatures:
    def test_c_major_no_accidentals(self):
        assert Key("C", "major").signature == 0

    def test_g_major_one_sharp(self):
        assert Key("G", "major").signature == 1

    def test_f_major_one_flat(self):
        assert Key("F", "major").signature == -1

    def test_a_minor_no_accidentals(self):
        # A minor is relative to C major
        assert Key("A", "minor").signature == 0

    def test_d_major_two_sharps(self):
        assert Key("D", "major").signature == 2


class TestRelativeAndParallel:
    def test_relative_of_c_major(self):
        k = Key("C", "major")
        rel = k.relative()
        assert rel.quality == "minor"
        assert rel.root == PitchClass("A")

    def test_relative_of_a_minor(self):
        k = Key("A", "minor")
        rel = k.relative()
        assert rel.quality == "major"
        assert rel.root == PitchClass("C")

    def test_relative_roundtrip(self):
        k = Key("G", "major")
        assert k.relative().relative() == k

    def test_parallel(self):
        c_major = Key("C", "major")
        c_minor = c_major.parallel()
        assert c_minor.root == PitchClass("C")
        assert c_minor.quality == "minor"

    def test_parallel_roundtrip(self):
        k = Key("Eb", "major")
        assert k.parallel().parallel() == k


class TestDiatonicHarmony:
    def test_c_major_triads(self):
        k = Key("C", "major")
        triads = k.diatonic_triads()
        assert len(triads) == 7
        # I ii iii IV V vi vii°
        romans = [t.roman for t in triads]
        assert romans == ["I", "ii", "iii", "IV", "V", "vi", "vii°"]

    def test_c_major_triad_roots(self):
        k = Key("C", "major")
        triads = k.diatonic_triads()
        roots = [str(t.chord.root) for t in triads]
        assert roots == ["C", "D", "E", "F", "G", "A", "B"]

    def test_a_minor_triads(self):
        k = Key("A", "minor")
        triads = k.diatonic_triads()
        # i ii° III iv v VI VII
        romans = [t.roman for t in triads]
        assert romans[0] == "i"
        assert "°" in romans[1]  # ii° (diminished)
        assert romans[2] == "III"

    def test_diatonic_sevenths(self):
        k = Key("C", "major")
        sevenths = k.diatonic_sevenths()
        assert len(sevenths) == 7
        # Imaj7 ii7 iii7 IVmaj7 V7 vi7 vii7
        assert "7" in sevenths[0].roman

    def test_degrees_match_scale(self):
        k = Key("G", "major")
        triads = k.diatonic_triads()
        scale_pcs = k.scale.pitch_classes()
        for i, triad in enumerate(triads):
            assert triad.chord.root == scale_pcs[i]


class TestModulation:
    def test_pivot_chords_c_to_g(self):
        c = Key("C", "major")
        g = Key("G", "major")
        pivots = c.pivot_chords(g)
        # C and G major share several chords
        assert len(pivots) >= 3

    def test_pivot_chords_symmetric(self):
        c = Key("C", "major")
        f = Key("F", "major")
        pivots_cf = c.pivot_chords(f)
        pivots_fc = f.pivot_chords(c)
        assert len(pivots_cf) == len(pivots_fc)

    def test_distant_keys_fewer_pivots(self):
        c = Key("C", "major")
        fs = Key("F#", "major")
        close = Key("G", "major")
        pivots_far = c.pivot_chords(fs)
        pivots_close = c.pivot_chords(close)
        assert len(pivots_close) >= len(pivots_far)


class TestKeyEquality:
    def test_same_key(self):
        assert Key("C", "major") == Key("C", "major")

    def test_different_root(self):
        assert Key("C", "major") != Key("D", "major")

    def test_different_quality(self):
        assert Key("C", "major") != Key("C", "minor")
