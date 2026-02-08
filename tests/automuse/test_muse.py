"""Tests for the Muse conversation engine."""

import tempfile
from pathlib import Path

from automuse.muse.engine import Muse
from automuse.muse.commands import parse_command, Command


class TestCommandParsing:
    def test_recognized_command(self):
        cmd = parse_command("scale C major")
        assert cmd.action == "scale"
        assert cmd.args == ["C", "major"]

    def test_slash_prefix(self):
        cmd = parse_command("/chord Cmaj7")
        assert cmd.action == "chord"
        assert cmd.args == ["Cmaj7"]

    def test_case_insensitive(self):
        cmd = parse_command("HELP")
        assert cmd.action == "help"

    def test_unknown_is_chat(self):
        cmd = parse_command("make something beautiful")
        assert cmd.action == "chat"

    def test_empty(self):
        cmd = parse_command("")
        assert cmd.action == "empty"

    def test_all_actions_recognized(self):
        for action in ["scale", "chord", "key", "progression", "tempo", "time",
                        "play", "export", "analyze", "suggest", "help", "quit",
                        "modulate", "voicing", "transpose"]:
            cmd = parse_command(f"{action} test")
            assert cmd.action == action, f"{action} not recognized"


class TestMuseScale:
    def test_scale_response(self):
        muse = Muse()
        r = muse.respond("scale C major")
        assert "C major" in r
        assert "C" in r and "D" in r and "E" in r

    def test_scale_dorian(self):
        muse = Muse()
        r = muse.respond("scale D dorian")
        assert "D dorian" in r

    def test_scale_missing_args(self):
        muse = Muse()
        r = muse.respond("scale C")
        assert "Usage" in r

    def test_scale_invalid(self):
        muse = Muse()
        r = muse.respond("scale C nonexistent")
        assert "Unknown" in r or "unknown" in r


class TestMuseChord:
    def test_chord_response(self):
        muse = Muse()
        r = muse.respond("chord Cmaj7")
        assert "Cmaj7" in r
        assert "major 7th" in r

    def test_chord_missing_args(self):
        muse = Muse()
        r = muse.respond("chord")
        assert "Usage" in r


class TestMuseKey:
    def test_set_key(self):
        muse = Muse()
        r = muse.respond("key G major")
        assert "G major" in r
        assert muse.key.root.name == "G"
        assert muse.key.quality == "major"

    def test_key_shows_triads(self):
        muse = Muse()
        r = muse.respond("key C major")
        assert "I" in r and "ii" in r and "IV" in r and "V" in r

    def test_key_shows_relative(self):
        muse = Muse()
        r = muse.respond("key C major")
        assert "Relative" in r

    def test_key_missing_args(self):
        muse = Muse()
        r = muse.respond("key")
        assert "Current key" in r


class TestMuseProgression:
    def test_progression_template(self):
        muse = Muse()
        r = muse.respond("progression I-IV-V-I")
        assert "C" in r  # Default key is C major
        assert muse.last_progression is not None

    def test_progression_list(self):
        muse = Muse()
        r = muse.respond("progression")
        assert "Available" in r or "template" in r.lower()

    def test_progression_invalid(self):
        muse = Muse()
        r = muse.respond("progression nonexistent")
        assert "Unknown" in r or "unknown" in r


class TestMuseTempo:
    def test_set_tempo(self):
        muse = Muse()
        r = muse.respond("tempo 140")
        assert "140" in r
        assert muse.tempo.bpm == 140

    def test_tempo_no_args(self):
        muse = Muse()
        r = muse.respond("tempo")
        assert "120" in r  # Default


class TestMuseTimeSignature:
    def test_set_time(self):
        muse = Muse()
        r = muse.respond("time 3/4")
        assert "3/4" in r
        assert muse.time_signature.numerator == 3

    def test_time_no_args(self):
        muse = Muse()
        r = muse.respond("time")
        assert "4/4" in r


class TestMuseAnalysis:
    def test_analyze_progression(self):
        muse = Muse()
        muse.respond("progression I-IV-V-I")
        r = muse.respond("analyze")
        assert "tonic" in r or "dominant" in r or "subdominant" in r

    def test_analyze_empty(self):
        muse = Muse()
        r = muse.respond("analyze")
        assert "Nothing" in r


class TestMuseModulation:
    def test_modulate(self):
        muse = Muse()
        r = muse.respond("modulate G major")
        assert "Pivot" in r or "pivot" in r

    def test_modulate_missing_args(self):
        muse = Muse()
        r = muse.respond("modulate")
        assert "Usage" in r


class TestMuseTranspose:
    def test_transpose(self):
        muse = Muse()
        muse.respond("key C major")
        r = muse.respond("transpose 5")
        assert muse.key.root.name == "F"

    def test_transpose_missing_args(self):
        muse = Muse()
        r = muse.respond("transpose")
        assert "Usage" in r


class TestMuseVoicing:
    def test_voicing(self):
        muse = Muse()
        r = muse.respond("voicing Cmaj7 drop 2")
        assert "drop 2" in r
        assert "MIDI" in r

    def test_voicing_no_args(self):
        muse = Muse()
        r = muse.respond("voicing")
        assert "Usage" in r


class TestMuseExport:
    def test_export(self):
        muse = Muse()
        muse.respond("progression I-IV-V-I")
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = f.name
        r = muse.respond(f"export {path}")
        assert "Exported" in r
        assert Path(path).exists()
        Path(path).unlink()

    def test_export_nothing(self):
        muse = Muse()
        r = muse.respond("export")
        assert "Nothing" in r


class TestMuseChat:
    def test_greeting(self):
        muse = Muse()
        r = muse.respond("hello")
        assert "Muse" in r or "C major" in r

    def test_sad_mood(self):
        muse = Muse()
        r = muse.respond("something sad and melancholic")
        assert "minor" in r.lower()

    def test_jazz_mood(self):
        muse = Muse()
        r = muse.respond("let's play some jazz")
        assert "Bb" in r or "jazz" in r.lower()

    def test_blues_mood(self):
        muse = Muse()
        r = muse.respond("give me the blues")
        assert "blues" in r.lower()

    def test_unknown_chat(self):
        muse = Muse()
        r = muse.respond("abcdef random input")
        assert "help" in r.lower() or "key" in r.lower()


class TestMuseSession:
    def test_default_state(self):
        muse = Muse()
        assert muse.key.name == "C major"
        assert muse.tempo.bpm == 120
        assert str(muse.time_signature) == "4/4"

    def test_quit(self):
        muse = Muse()
        r = muse.respond("quit")
        assert r == "SESSION_END"

    def test_help(self):
        muse = Muse()
        r = muse.respond("help")
        assert "scale" in r
        assert "chord" in r
        assert "progression" in r

    def test_play(self):
        muse = Muse()
        r = muse.respond("play")
        assert "Layer 1" in r or "MIDI" in r

    def test_suggest_major(self):
        muse = Muse()
        r = muse.respond("suggest")
        assert "I-IV-V-I" in r or "I-V-vi-IV" in r

    def test_suggest_minor(self):
        muse = Muse()
        muse.respond("key A minor")
        r = muse.respond("suggest")
        assert len(r) > 0

    def test_empty_input(self):
        muse = Muse()
        r = muse.respond("")
        assert "listening" in r.lower()

    def test_full_workflow(self):
        """End-to-end: set key, generate progression, analyze, export."""
        muse = Muse()
        muse.respond("key D minor")
        assert muse.key.name == "D minor"
        muse.respond("tempo 90")
        assert muse.tempo.bpm == 90
        muse.respond("time 3/4")
        assert muse.time_signature.numerator == 3
        r = muse.respond("progression I-IV-V-I")
        assert muse.last_progression is not None
        r = muse.respond("analyze")
        assert "tonic" in r or "subdominant" in r or "dominant" in r
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = f.name
        r = muse.respond(f"export {path}")
        assert Path(path).exists()
        assert Path(path).stat().st_size > 0
        Path(path).unlink()
