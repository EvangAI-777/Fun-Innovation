"""Standard MIDI file writer -- zero external dependencies.

Writes Type 0 (single track) or Type 1 (multi-track) SMF files
using raw bytes. No mido, no pretty-midi, just struct.
"""

from __future__ import annotations

import struct
from pathlib import Path
from dataclasses import dataclass, field

from automuse.core.notes import Note
from automuse.core.chords import Chord
from automuse.core.rhythm import Tempo, Duration, QUARTER, TimeSignature, COMMON_TIME
from automuse.harmony.progressions import Progression


def _write_varlen(value: int) -> bytes:
    """Encode an integer as a MIDI variable-length quantity."""
    if value < 0:
        raise ValueError(f"Variable-length value must be >= 0, got {value}")
    buf: list[int] = [value & 0x7F]
    value >>= 7
    while value:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    buf.reverse()
    return bytes(buf)


@dataclass
class MidiEvent:
    """A raw MIDI event with absolute tick time."""

    tick: int
    data: bytes


@dataclass
class MidiTrack:
    """A collection of MIDI events forming one track."""

    name: str = ""
    events: list[MidiEvent] = field(default_factory=list)

    def note_on(self, tick: int, note: int, velocity: int = 100, channel: int = 0) -> None:
        self.events.append(MidiEvent(tick, bytes([0x90 | channel, note, velocity])))

    def note_off(self, tick: int, note: int, velocity: int = 0, channel: int = 0) -> None:
        self.events.append(MidiEvent(tick, bytes([0x80 | channel, note, velocity])))

    def add_note(
        self,
        tick: int,
        note: int,
        duration_ticks: int,
        velocity: int = 100,
        channel: int = 0,
    ) -> None:
        self.note_on(tick, note, velocity, channel)
        self.note_off(tick + duration_ticks, note, 0, channel)

    def set_tempo(self, tick: int, tempo: Tempo) -> None:
        us = tempo.us_per_beat
        data = b"\xFF\x51\x03" + struct.pack(">I", us)[1:]
        self.events.append(MidiEvent(tick, data))

    def set_time_signature(self, tick: int, ts: TimeSignature) -> None:
        import math
        denom_power = int(math.log2(ts.denominator))
        # Standard: 24 MIDI clocks per metronome click, 8 32nd notes per beat
        data = bytes([0xFF, 0x58, 0x04, ts.numerator, denom_power, 24, 8])
        self.events.append(MidiEvent(tick, data))

    def set_track_name(self, name: str) -> None:
        encoded = name.encode("ascii", errors="replace")
        data = b"\xFF\x03" + _write_varlen(len(encoded)) + encoded
        self.events.append(MidiEvent(0, data))

    def program_change(self, tick: int, program: int, channel: int = 0) -> None:
        self.events.append(MidiEvent(tick, bytes([0xC0 | channel, program])))

    def _build(self) -> bytes:
        """Serialize this track to raw MIDI bytes."""
        sorted_events = sorted(self.events, key=lambda e: e.tick)
        raw = bytearray()
        last_tick = 0
        for event in sorted_events:
            delta = event.tick - last_tick
            raw.extend(_write_varlen(delta))
            raw.extend(event.data)
            last_tick = event.tick
        # End-of-track meta event
        raw.extend(_write_varlen(0))
        raw.extend(b"\xFF\x2F\x00")
        # Track header
        header = b"MTrk" + struct.pack(">I", len(raw))
        return header + bytes(raw)


class MidiWriter:
    """Builds and writes standard MIDI files."""

    def __init__(self, ppqn: int = 480) -> None:
        self._ppqn = ppqn
        self._tracks: list[MidiTrack] = []

    @property
    def ppqn(self) -> int:
        return self._ppqn

    def add_track(self, name: str = "") -> MidiTrack:
        track = MidiTrack(name=name)
        if name:
            track.set_track_name(name)
        self._tracks.append(track)
        return track

    def write_note(
        self,
        track: MidiTrack,
        note: Note,
        start_tick: int,
        duration: Duration = QUARTER,
        velocity: int = 100,
        channel: int = 0,
    ) -> None:
        track.add_note(start_tick, note.midi, duration.ticks, velocity, channel)

    def write_chord(
        self,
        track: MidiTrack,
        chord: Chord,
        start_tick: int,
        duration: Duration = QUARTER,
        velocity: int = 80,
        octave: int = 4,
        channel: int = 0,
    ) -> None:
        for note in chord.notes(octave):
            track.add_note(start_tick, note.midi, duration.ticks, velocity, channel)

    def write_scale(
        self,
        track: MidiTrack,
        notes: list[Note],
        start_tick: int = 0,
        duration: Duration = QUARTER,
        velocity: int = 100,
        channel: int = 0,
    ) -> int:
        """Write a sequence of notes and return the tick after the last note."""
        tick = start_tick
        for note in notes:
            track.add_note(tick, note.midi, duration.ticks, velocity, channel)
            tick += duration.ticks
        return tick

    def write_progression(
        self,
        track: MidiTrack,
        progression: Progression,
        start_tick: int = 0,
        octave: int = 3,
        velocity: int = 80,
        channel: int = 0,
    ) -> int:
        """Write a chord progression and return the tick after the last chord."""
        tick = start_tick
        for step in progression.steps:
            dur = step.duration
            for note in step.chord.notes(octave):
                track.add_note(tick, note.midi, dur.ticks, velocity, channel)
            tick += dur.ticks
        return tick

    def save(self, path: str | Path) -> Path:
        """Write the MIDI file to disk."""
        path = Path(path)
        n_tracks = len(self._tracks)
        midi_type = 0 if n_tracks <= 1 else 1
        header = b"MThd" + struct.pack(">IHhH", 6, midi_type, n_tracks, self._ppqn)
        with open(path, "wb") as f:
            f.write(header)
            for track in self._tracks:
                f.write(track._build())
        return path

    def to_bytes(self) -> bytes:
        """Return the MIDI file as raw bytes."""
        n_tracks = len(self._tracks)
        midi_type = 0 if n_tracks <= 1 else 1
        header = b"MThd" + struct.pack(">IHhH", 6, midi_type, n_tracks, self._ppqn)
        parts = [header]
        for track in self._tracks:
            parts.append(track._build())
        return b"".join(parts)
