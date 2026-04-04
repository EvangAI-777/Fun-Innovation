"""Tests for arrangement model and song structure."""

import pytest

from automuse.core.keys import Key
from automuse.core.rhythm import TimeSignature, Tempo, COMMON_TIME, WALTZ_TIME
from automuse.compose.arrangement import (
    SectionType, Section, Arrangement, ArrangementTemplates,
)


class TestSectionType:
    def test_all_types(self):
        assert len(SectionType) == 9
        assert SectionType.INTRO.value == "intro"
        assert SectionType.CHORUS.value == "chorus"
        assert SectionType.BREAKDOWN.value == "breakdown"


class TestSection:
    def test_creation(self):
        s = Section(SectionType.VERSE, 8)
        assert s.section_type == SectionType.VERSE
        assert s.bars == 8
        assert s.label == "Verse"

    def test_custom_label(self):
        s = Section(SectionType.VERSE, 8, label="Verse 2")
        assert s.label == "Verse 2"

    def test_key_override(self):
        s = Section(SectionType.BRIDGE, 8, key=Key("G", "major"))
        assert s.key == Key("G", "major")

    def test_ticks_4_4(self):
        s = Section(SectionType.VERSE, 4)
        assert s.ticks(COMMON_TIME) == 4 * COMMON_TIME.ticks_per_bar

    def test_ticks_3_4(self):
        s = Section(SectionType.VERSE, 4)
        assert s.ticks(WALTZ_TIME) == 4 * WALTZ_TIME.ticks_per_bar

    def test_to_dict(self):
        s = Section(SectionType.CHORUS, 8, key=Key("D", "minor"), label="Chorus 1")
        d = s.to_dict()
        assert d["type"] == "chorus"
        assert d["bars"] == 8
        assert d["key"] == "D minor"
        assert d["label"] == "Chorus 1"

    def test_from_dict(self):
        d = {"type": "verse", "bars": 8, "label": "Verse 1", "key": "C major"}
        s = Section.from_dict(d)
        assert s.section_type == SectionType.VERSE
        assert s.bars == 8
        assert s.key == Key("C", "major")

    def test_from_dict_no_key(self):
        d = {"type": "intro", "bars": 4, "label": "Intro", "key": None}
        s = Section.from_dict(d)
        assert s.key is None

    def test_str(self):
        s = Section(SectionType.VERSE, 8)
        assert "Verse" in str(s) and "8" in str(s)


class TestArrangement:
    def _basic_arrangement(self) -> Arrangement:
        arr = Arrangement("Test Song", Key("C", "major"), Tempo(120))
        arr.add_section(Section(SectionType.INTRO, 4))
        arr.add_section(Section(SectionType.VERSE, 8))
        arr.add_section(Section(SectionType.CHORUS, 8))
        return arr

    def test_creation(self):
        arr = self._basic_arrangement()
        assert arr.title == "Test Song"
        assert arr.key == Key("C", "major")
        assert arr.tempo == Tempo(120)

    def test_sections(self):
        arr = self._basic_arrangement()
        assert len(arr.sections) == 3

    def test_total_bars(self):
        arr = self._basic_arrangement()
        assert arr.total_bars == 4 + 8 + 8

    def test_total_ticks(self):
        arr = self._basic_arrangement()
        expected = 20 * COMMON_TIME.ticks_per_bar
        assert arr.total_ticks == expected

    def test_duration_seconds(self):
        arr = Arrangement("Test", Key("C", "major"), Tempo(120))
        arr.add_section(Section(SectionType.VERSE, 4))
        # 4 bars * 4 beats/bar = 16 beats at 120 BPM = 8 seconds
        assert arr.duration_seconds == pytest.approx(8.0)

    def test_section_map(self):
        arr = self._basic_arrangement()
        sm = arr.section_map
        assert "Intro" in sm and "Verse" in sm and "Chorus" in sm
        assert "|" in sm

    def test_empty_section_map(self):
        arr = Arrangement("Empty", Key("C", "major"), Tempo(120))
        assert "empty" in arr.section_map

    def test_insert_section(self):
        arr = self._basic_arrangement()
        arr.insert_section(1, Section(SectionType.INTERLUDE, 4))
        assert arr.sections[1].section_type == SectionType.INTERLUDE
        assert len(arr.sections) == 4

    def test_remove_section(self):
        arr = self._basic_arrangement()
        removed = arr.remove_section(0)
        assert removed.section_type == SectionType.INTRO
        assert len(arr.sections) == 2

    def test_to_dict_from_dict_roundtrip(self):
        arr = self._basic_arrangement()
        d = arr.to_dict()
        arr2 = Arrangement.from_dict(d)
        assert arr2.title == "Test Song"
        assert arr2.key == Key("C", "major")
        assert arr2.tempo.bpm == 120
        assert len(arr2.sections) == 3
        assert arr2.sections[0].section_type == SectionType.INTRO

    def test_to_dict_structure(self):
        arr = self._basic_arrangement()
        d = arr.to_dict()
        assert d["title"] == "Test Song"
        assert d["key"] == "C major"
        assert d["tempo"] == 120
        assert d["time_sig"] == "4/4"
        assert len(d["sections"]) == 3


class TestArrangementTemplates:
    def test_pop(self):
        sections = ArrangementTemplates.pop()
        assert len(sections) == 8
        assert sections[0].section_type == SectionType.INTRO
        assert sections[-1].section_type == SectionType.OUTRO
        total_bars = sum(s.bars for s in sections)
        assert total_bars == 56

    def test_verse_chorus(self):
        sections = ArrangementTemplates.verse_chorus()
        assert len(sections) == 4
        types = [s.section_type for s in sections]
        assert types == [SectionType.VERSE, SectionType.CHORUS, SectionType.VERSE, SectionType.CHORUS]

    def test_aaba(self):
        sections = ArrangementTemplates.aaba()
        assert len(sections) == 4
        total_bars = sum(s.bars for s in sections)
        assert total_bars == 32

    def test_blues_12bar(self):
        sections = ArrangementTemplates.blues_12bar()
        total_bars = sum(s.bars for s in sections)
        assert total_bars == 12

    def test_through_composed(self):
        sections = ArrangementTemplates.through_composed()
        assert len(sections) == 4
        labels = [s.label for s in sections]
        assert labels == ["A", "B", "C", "D"]
