"""MusicXML export -- zero-dependency XML writing for notation software interop."""

from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

from ..core.notes import Note, PitchClass
from ..core.keys import Key
from ..core.rhythm import TimeSignature, Duration, COMMON_TIME
from ..core.scales import Scale
from ..compose.motif import MotifNote, Motif
from ..harmony.progressions import Progression


# Map ticks (480 PPQN) to MusicXML duration values and note types
_TICK_TO_TYPE: list[tuple[int, int, str]] = [
    (1920, 4, "whole"),
    (1440, 3, "half"),        # dotted half
    (960, 2, "half"),
    (720, 3, "quarter"),      # dotted quarter (3 in div-2 units for div=480/4=1)
    (480, 1, "quarter"),
    (360, 3, "eighth"),       # dotted eighth
    (240, 1, "eighth"),
    (120, 1, "16th"),
    (60, 1, "32nd"),
]

# MusicXML divisions = ticks per quarter note / 1
# We use divisions=1 and scale durations to quarter-note multiples
_DIVISIONS = 1  # 1 division per quarter note


def _pitch_to_xml(note: Note) -> tuple[str, int, int]:
    """Convert a Note to MusicXML pitch components (step, alter, octave)."""
    name = note.pitch_class.name
    if len(name) == 1:
        return name, 0, note.octave
    if name.endswith("#"):
        return name[0], 1, note.octave
    if name.endswith("b"):
        return name[0], -1, note.octave
    return name[0], 0, note.octave


def _ticks_to_duration(ticks: int) -> tuple[int, str]:
    """Convert tick duration to (MusicXML duration value, note type)."""
    for tick_val, dur_val, note_type in _TICK_TO_TYPE:
        if ticks >= tick_val:
            return dur_val, note_type
    return 1, "32nd"


def _ticks_to_xml_duration(ticks: int) -> int:
    """Convert ticks to MusicXML duration units (divisions-based)."""
    # With divisions=1, quarter=1, half=2, whole=4, eighth=0.5->1
    # We'll use divisions=480 to keep integer precision
    return ticks


class MusicXMLWriter:
    """Builds MusicXML documents using only stdlib xml.etree.ElementTree."""

    def __init__(self, title: str = "AutoMuse Export", composer: str = "AutoMuse") -> None:
        self._title = title
        self._composer = composer
        self._parts: dict[str, dict] = {}  # id -> {name, instrument, measures}
        self._part_counter = 0
        self._divisions = 480  # match our PPQN

    def add_part(self, name: str = "Piano", instrument: str = "Piano") -> str:
        """Add a part (instrument track) and return its ID."""
        self._part_counter += 1
        part_id = f"P{self._part_counter}"
        self._parts[part_id] = {
            "name": name,
            "instrument": instrument,
            "measures": [],
        }
        return part_id

    def write_notes(
        self,
        part_id: str,
        notes: list[MotifNote],
        key: Key | None = None,
        time_sig: TimeSignature = COMMON_TIME,
    ) -> None:
        """Write a sequence of MotifNotes as a single measure (or multiple measures)."""
        if part_id not in self._parts:
            raise ValueError(f"Unknown part ID: {part_id}")

        ticks_per_bar = time_sig.ticks_per_bar
        current_tick = 0
        current_measure: list[Element] = []
        measure_num = len(self._parts[part_id]["measures"]) + 1

        # Add attributes to first measure
        if measure_num == 1:
            attr = Element("attributes")
            SubElement(attr, "divisions").text = str(self._divisions)
            if key:
                key_elem = SubElement(attr, "key")
                SubElement(key_elem, "fifths").text = str(key.signature)
                SubElement(key_elem, "mode").text = key.quality
            time_elem = SubElement(attr, "time")
            SubElement(time_elem, "beats").text = str(time_sig.numerator)
            SubElement(time_elem, "beat-type").text = str(time_sig.denominator)
            current_measure.append(attr)

        for mn in notes:
            if current_tick >= ticks_per_bar and current_measure:
                self._parts[part_id]["measures"].append(current_measure)
                current_measure = []
                current_tick = 0
                measure_num += 1

            note_elem = Element("note")
            pitch_elem = SubElement(note_elem, "pitch")
            step, alter, octave = _pitch_to_xml(mn.note)
            SubElement(pitch_elem, "step").text = step
            if alter != 0:
                SubElement(pitch_elem, "alter").text = str(alter)
            SubElement(pitch_elem, "octave").text = str(octave)

            SubElement(note_elem, "duration").text = str(mn.duration.ticks)
            _, note_type = _ticks_to_duration(mn.duration.ticks)
            SubElement(note_elem, "type").text = note_type

            if mn.velocity > 0:
                dynamics_elem = SubElement(note_elem, "dynamics")
                # Map velocity 0-127 to roughly ppp-fff
                if mn.velocity < 32:
                    SubElement(dynamics_elem, "pp")
                elif mn.velocity < 64:
                    SubElement(dynamics_elem, "mp")
                elif mn.velocity < 96:
                    SubElement(dynamics_elem, "mf")
                else:
                    SubElement(dynamics_elem, "f")

            current_measure.append(note_elem)
            current_tick += mn.duration.ticks

        if current_measure:
            self._parts[part_id]["measures"].append(current_measure)

    def write_chord_symbols(self, part_id: str, progression: Progression) -> None:
        """Write chord symbols above the staff for a progression."""
        if part_id not in self._parts:
            raise ValueError(f"Unknown part ID: {part_id}")

        measure_elements: list[Element] = []
        for step in progression.steps:
            harmony = Element("harmony")
            root_elem = SubElement(harmony, "root")
            SubElement(root_elem, "root-step").text = step.chord.root.name[0]
            if len(step.chord.root.name) > 1:
                alter = 1 if "#" in step.chord.root.name else -1
                SubElement(root_elem, "root-alter").text = str(alter)

            kind_elem = SubElement(harmony, "kind")
            chord_name = step.chord.chord_type.name.lower()
            if "major" in chord_name and "7" not in chord_name:
                kind_elem.text = "major"
            elif "minor" in chord_name and "7" not in chord_name:
                kind_elem.text = "minor"
            elif "dominant" in chord_name or chord_name == "7":
                kind_elem.text = "dominant"
            elif "diminished" in chord_name:
                kind_elem.text = "diminished"
            elif "augmented" in chord_name:
                kind_elem.text = "augmented"
            else:
                kind_elem.text = "major"

            measure_elements.append(harmony)

        if measure_elements:
            self._parts[part_id]["measures"].append(measure_elements)

    def write_scale(
        self,
        part_id: str,
        scale: Scale,
        octave: int = 4,
        duration: Duration | None = None,
    ) -> None:
        """Write a scale as a sequence of notes."""
        from ..core.rhythm import QUARTER
        dur = duration or QUARTER
        notes = scale.notes(octave)
        motif_notes = [MotifNote(n, dur) for n in notes]
        self.write_notes(part_id, motif_notes)

    def _build_tree(self) -> ElementTree:
        """Build the complete MusicXML document tree."""
        root = Element("score-partwise")
        root.set("version", "4.0")

        # Work element
        work = SubElement(root, "work")
        SubElement(work, "work-title").text = self._title

        # Identification
        ident = SubElement(root, "identification")
        creator = SubElement(ident, "creator")
        creator.set("type", "composer")
        creator.text = self._composer
        encoding = SubElement(ident, "encoding")
        SubElement(encoding, "software").text = "AutoMuse"

        # Part list
        part_list = SubElement(root, "part-list")
        for pid, pdata in self._parts.items():
            score_part = SubElement(part_list, "score-part")
            score_part.set("id", pid)
            SubElement(score_part, "part-name").text = pdata["name"]

        # Parts with measures
        for pid, pdata in self._parts.items():
            part_elem = SubElement(root, "part")
            part_elem.set("id", pid)
            measures = pdata["measures"]
            if not measures:
                # Add empty measure
                measure = SubElement(part_elem, "measure")
                measure.set("number", "1")
            else:
                for i, measure_elems in enumerate(measures):
                    measure = SubElement(part_elem, "measure")
                    measure.set("number", str(i + 1))
                    for elem in measure_elems:
                        measure.append(elem)

        return ElementTree(root)

    def to_string(self) -> str:
        """Return the MusicXML document as a string."""
        tree = self._build_tree()
        indent(tree.getroot(), space="  ")
        import io
        buf = io.BytesIO()
        tree.write(buf, encoding="utf-8", xml_declaration=True)
        return buf.getvalue().decode("utf-8")

    def save(self, path: str | Path) -> Path:
        """Write the MusicXML document to a file."""
        path = Path(path)
        tree = self._build_tree()
        indent(tree.getroot(), space="  ")
        tree.write(str(path), encoding="utf-8", xml_declaration=True)
        return path
