"""Harmonic analysis -- identify chord functions and progressions."""

from __future__ import annotations

from dataclasses import dataclass

from automuse.core.chords import Chord
from automuse.core.keys import Key
from automuse.harmony.progressions import Progression


@dataclass(frozen=True)
class ChordAnalysis:
    """Analysis result for a single chord within a key context."""

    chord: Chord
    roman: str
    function: str  # tonic, subdominant, dominant


_FUNCTION_MAP_MAJOR = {
    1: "tonic",
    2: "subdominant",
    3: "tonic",
    4: "subdominant",
    5: "dominant",
    6: "tonic",
    7: "dominant",
}

_FUNCTION_MAP_MINOR = {
    1: "tonic",
    2: "subdominant",
    3: "tonic",
    4: "subdominant",
    5: "dominant",
    6: "subdominant",
    7: "dominant",
}


def analyze_chord_in_key(chord: Chord, key: Key) -> ChordAnalysis | None:
    """Analyze a single chord's function within a key."""
    diatonic = key.diatonic_triads()
    for dc in diatonic:
        if dc.chord.root == chord.root:
            func_map = (
                _FUNCTION_MAP_MAJOR
                if key.quality == "major"
                else _FUNCTION_MAP_MINOR
            )
            return ChordAnalysis(
                chord=chord,
                roman=dc.roman,
                function=func_map[dc.degree],
            )
    return None


def analyze_progression(progression: Progression) -> list[ChordAnalysis]:
    """Analyze each chord in a progression, using its key context."""
    key = progression.key
    if key is None:
        return [
            ChordAnalysis(chord=s.chord, roman=s.roman or "?", function="unknown")
            for s in progression.steps
        ]
    results: list[ChordAnalysis] = []
    for step in progression.steps:
        analysis = analyze_chord_in_key(step.chord, key)
        if analysis:
            results.append(analysis)
        else:
            results.append(
                ChordAnalysis(
                    chord=step.chord,
                    roman=step.roman or "?",
                    function="chromatic",
                )
            )
    return results
