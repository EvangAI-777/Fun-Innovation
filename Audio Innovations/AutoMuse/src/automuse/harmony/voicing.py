"""Chord voicing engine -- voice leading and voicing styles."""

from __future__ import annotations

from enum import Enum

from automuse.core.notes import Note
from automuse.core.chords import Chord


class VoicingStyle(Enum):
    ROOT_POSITION = "root position"
    CLOSE = "close"
    DROP_2 = "drop 2"
    DROP_3 = "drop 3"
    SPREAD = "spread"
    SHELL = "shell"


def voice_chord(
    chord: Chord,
    style: VoicingStyle = VoicingStyle.ROOT_POSITION,
    octave: int = 4,
) -> list[Note]:
    """Voice a chord in the given style at the given octave."""
    base_notes = chord.notes(octave)

    if style == VoicingStyle.ROOT_POSITION:
        return base_notes

    if style == VoicingStyle.CLOSE:
        # All notes within one octave, root position
        return base_notes

    if style == VoicingStyle.DROP_2:
        if len(base_notes) < 4:
            return base_notes
        # Drop the second-from-top note down an octave
        notes = list(base_notes)
        drop = notes[-2].transpose(-12)
        notes[-2] = drop
        notes.sort()
        return notes

    if style == VoicingStyle.DROP_3:
        if len(base_notes) < 4:
            return base_notes
        # Drop the third-from-top note down an octave
        notes = list(base_notes)
        drop = notes[-3].transpose(-12)
        notes[-3] = drop
        notes.sort()
        return notes

    if style == VoicingStyle.SPREAD:
        # Spread notes across two octaves
        notes: list[Note] = []
        for i, note in enumerate(base_notes):
            if i % 2 == 0:
                notes.append(note)
            else:
                notes.append(note.transpose(12))
        notes.sort()
        return notes

    if style == VoicingStyle.SHELL:
        # Root, 3rd (or sus), 7th -- omit 5th and extensions
        if len(base_notes) < 3:
            return base_notes
        # Keep root, second note (quality-defining), and last note
        return [base_notes[0], base_notes[1], base_notes[-1]]

    return base_notes
