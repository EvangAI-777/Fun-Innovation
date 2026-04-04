"""Song structure and arrangement model."""

from __future__ import annotations

from enum import Enum

from ..core.keys import Key
from ..core.rhythm import TimeSignature, Tempo, COMMON_TIME
from ..harmony.progressions import Progression
from .motif import Motif


class SectionType(Enum):
    """Standard song section types."""

    INTRO = "intro"
    VERSE = "verse"
    PRE_CHORUS = "pre-chorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"
    SOLO = "solo"
    INTERLUDE = "interlude"
    BREAKDOWN = "breakdown"


class Section:
    """A section of a song (verse, chorus, bridge, etc.)."""

    __slots__ = ("_section_type", "_bars", "_key", "_progression", "_melody", "_label")

    def __init__(
        self,
        section_type: SectionType,
        bars: int = 8,
        key: Key | None = None,
        progression: Progression | None = None,
        melody: Motif | None = None,
        label: str = "",
    ) -> None:
        self._section_type = section_type
        self._bars = bars
        self._key = key
        self._progression = progression
        self._melody = melody
        self._label = label or section_type.value.title()

    @property
    def section_type(self) -> SectionType:
        return self._section_type

    @property
    def bars(self) -> int:
        return self._bars

    @property
    def key(self) -> Key | None:
        return self._key

    @property
    def progression(self) -> Progression | None:
        return self._progression

    @property
    def melody(self) -> Motif | None:
        return self._melody

    @property
    def label(self) -> str:
        return self._label

    def ticks(self, time_sig: TimeSignature = COMMON_TIME) -> int:
        return self._bars * time_sig.ticks_per_bar

    def to_dict(self) -> dict:
        return {
            "type": self._section_type.value,
            "bars": self._bars,
            "label": self._label,
            "key": self._key.name if self._key else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Section:
        key = None
        if data.get("key"):
            parts = data["key"].split()
            key = Key(parts[0], parts[1] if len(parts) > 1 else "major")
        return cls(
            section_type=SectionType(data["type"]),
            bars=data["bars"],
            key=key,
            label=data.get("label", ""),
        )

    def __repr__(self) -> str:
        return f"Section({self._section_type.value!r}, {self._bars} bars)"

    def __str__(self) -> str:
        return f"{self._label} ({self._bars})"


class Arrangement:
    """A full song structure: ordered sections with key, tempo, and time signature."""

    __slots__ = ("_title", "_key", "_tempo", "_time_sig", "_sections")

    def __init__(
        self,
        title: str,
        key: Key,
        tempo: Tempo,
        time_sig: TimeSignature = COMMON_TIME,
    ) -> None:
        self._title = title
        self._key = key
        self._tempo = tempo
        self._time_sig = time_sig
        self._sections: list[Section] = []

    @property
    def title(self) -> str:
        return self._title

    @property
    def key(self) -> Key:
        return self._key

    @property
    def tempo(self) -> Tempo:
        return self._tempo

    @property
    def time_sig(self) -> TimeSignature:
        return self._time_sig

    @property
    def sections(self) -> list[Section]:
        return list(self._sections)

    def add_section(self, section: Section) -> None:
        self._sections.append(section)

    def insert_section(self, index: int, section: Section) -> None:
        self._sections.insert(index, section)

    def remove_section(self, index: int) -> Section:
        return self._sections.pop(index)

    @property
    def total_bars(self) -> int:
        return sum(s.bars for s in self._sections)

    @property
    def total_ticks(self) -> int:
        return sum(s.ticks(self._time_sig) for s in self._sections)

    @property
    def duration_seconds(self) -> float:
        total_beats = self.total_bars * self._time_sig.beats_per_bar
        return total_beats * 60.0 / self._tempo.bpm

    @property
    def section_map(self) -> str:
        if not self._sections:
            return "(empty arrangement)"
        return " | ".join(str(s) for s in self._sections)

    def to_dict(self) -> dict:
        return {
            "title": self._title,
            "key": self._key.name,
            "tempo": self._tempo.bpm,
            "time_sig": str(self._time_sig),
            "sections": [s.to_dict() for s in self._sections],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Arrangement:
        key_parts = data["key"].split()
        key = Key(key_parts[0], key_parts[1] if len(key_parts) > 1 else "major")
        ts_parts = data["time_sig"].split("/")
        time_sig = TimeSignature(int(ts_parts[0]), int(ts_parts[1]))
        arr = cls(data["title"], key, Tempo(data["tempo"]), time_sig)
        for sd in data.get("sections", []):
            arr.add_section(Section.from_dict(sd))
        return arr

    def __repr__(self) -> str:
        return f"Arrangement({self._title!r}, {len(self._sections)} sections)"

    def __str__(self) -> str:
        return f"{self._title}: {self.section_map}"


class ArrangementTemplates:
    """Factory methods for common song forms."""

    @staticmethod
    def pop() -> list[Section]:
        return [
            Section(SectionType.INTRO, 4),
            Section(SectionType.VERSE, 8, label="Verse 1"),
            Section(SectionType.CHORUS, 8, label="Chorus 1"),
            Section(SectionType.VERSE, 8, label="Verse 2"),
            Section(SectionType.CHORUS, 8, label="Chorus 2"),
            Section(SectionType.BRIDGE, 8),
            Section(SectionType.CHORUS, 8, label="Chorus 3"),
            Section(SectionType.OUTRO, 4),
        ]

    @staticmethod
    def verse_chorus() -> list[Section]:
        return [
            Section(SectionType.VERSE, 8, label="Verse 1"),
            Section(SectionType.CHORUS, 8, label="Chorus 1"),
            Section(SectionType.VERSE, 8, label="Verse 2"),
            Section(SectionType.CHORUS, 8, label="Chorus 2"),
        ]

    @staticmethod
    def aaba() -> list[Section]:
        """Jazz standard 32-bar form."""
        return [
            Section(SectionType.VERSE, 8, label="A1"),
            Section(SectionType.VERSE, 8, label="A2"),
            Section(SectionType.BRIDGE, 8, label="B"),
            Section(SectionType.VERSE, 8, label="A3"),
        ]

    @staticmethod
    def blues_12bar() -> list[Section]:
        return [
            Section(SectionType.VERSE, 4, label="I"),
            Section(SectionType.VERSE, 2, label="IV"),
            Section(SectionType.VERSE, 2, label="I'"),
            Section(SectionType.VERSE, 2, label="V-IV"),
            Section(SectionType.VERSE, 2, label="I-V"),
        ]

    @staticmethod
    def through_composed() -> list[Section]:
        return [
            Section(SectionType.VERSE, 8, label="A"),
            Section(SectionType.VERSE, 8, label="B"),
            Section(SectionType.BRIDGE, 8, label="C"),
            Section(SectionType.VERSE, 8, label="D"),
        ]
