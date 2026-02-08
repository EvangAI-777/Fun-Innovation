"""Tests for chord progression generation and templates."""

import pytest

from automuse.core.keys import Key
from automuse.core.chords import Chord
from automuse.harmony.progressions import (
    Progression, ProgressionBuilder, COMMON_PROGRESSIONS,
)


class TestProgressionBuilder:
    def test_from_template_i_iv_v_i(self):
        builder = ProgressionBuilder(Key("C", "major"))
        prog = builder.from_template("I-IV-V-I")
        assert len(prog) == 4
        roots = [str(s.chord.root) for s in prog.steps]
        assert roots == ["C", "F", "G", "C"]

    def test_from_template_ii_v_i(self):
        builder = ProgressionBuilder(Key("C", "major"))
        prog = builder.from_template("ii-V-I")
        assert len(prog) == 3
        assert str(prog[0].chord.root) == "D"
        assert str(prog[1].chord.root) == "G"
        assert str(prog[2].chord.root) == "C"

    def test_12_bar_blues(self):
        builder = ProgressionBuilder(Key("E", "major"))
        prog = builder.from_template("12-bar blues")
        assert len(prog) == 12

    def test_pop_progression(self):
        builder = ProgressionBuilder(Key("G", "major"))
        prog = builder.from_template("I-V-vi-IV")
        assert len(prog) == 4

    def test_invalid_template(self):
        builder = ProgressionBuilder(Key("C", "major"))
        with pytest.raises(ValueError, match="Unknown progression template"):
            builder.from_template("nonexistent")

    def test_all_templates_build(self):
        builder = ProgressionBuilder(Key("C", "major"))
        for name in COMMON_PROGRESSIONS:
            prog = builder.from_template(name)
            assert len(prog) > 0, f"Template {name} produced empty progression"

    def test_from_degrees(self):
        builder = ProgressionBuilder(Key("A", "minor"))
        prog = builder.from_degrees([(1, "m"), (4, "m"), (5, "m"), (1, "m")])
        assert len(prog) == 4
        assert str(prog[0].chord.root) == "A"

    def test_from_roman(self):
        builder = ProgressionBuilder(Key("C", "major"))
        prog = builder.from_roman(["I", "IV", "V", "I"])
        assert len(prog) == 4

    def test_available_templates(self):
        templates = ProgressionBuilder.available_templates()
        assert len(templates) >= 5
        assert "I-IV-V-I" in templates
        assert "ii-V-I" in templates

    def test_different_keys(self):
        """Same template in different keys produces different root notes."""
        c_prog = ProgressionBuilder(Key("C", "major")).from_template("I-IV-V-I")
        g_prog = ProgressionBuilder(Key("G", "major")).from_template("I-IV-V-I")
        c_roots = [str(s.chord.root) for s in c_prog.steps]
        g_roots = [str(s.chord.root) for s in g_prog.steps]
        assert c_roots != g_roots
        assert c_roots[0] == "C"
        assert g_roots[0] == "G"


class TestProgression:
    def test_chords_property(self):
        builder = ProgressionBuilder(Key("C", "major"))
        prog = builder.from_template("I-IV-V-I")
        chords = prog.chords
        assert len(chords) == 4
        assert all(isinstance(c, Chord) for c in chords)

    def test_key_property(self):
        key = Key("D", "major")
        builder = ProgressionBuilder(key)
        prog = builder.from_template("I-IV-V-I")
        assert prog.key == key

    def test_string_representation(self):
        builder = ProgressionBuilder(Key("C", "major"))
        prog = builder.from_template("I-IV-V-I")
        s = str(prog)
        assert "|" in s
