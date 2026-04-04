"""Command parsing for the Muse conversation interface."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    """A parsed user command."""

    action: str
    args: list[str]
    raw: str


# Recognized command prefixes
ACTIONS = {
    "scale", "chord", "key", "progression", "tempo", "time",
    "play", "export", "analyze", "suggest", "help", "quit",
    "modulate", "voicing", "transpose",
    "melody", "motif", "arrange", "save", "load", "exportxml",
}


def parse_command(text: str) -> Command:
    """Parse user input into a structured command.

    Supports both slash-prefixed (/scale C major) and bare (scale C major) forms.
    """
    text = text.strip()
    if not text:
        return Command(action="empty", args=[], raw=text)

    # Strip leading slash if present
    if text.startswith("/"):
        text = text[1:]

    parts = text.split()
    candidate = parts[0].lower()

    if candidate in ACTIONS:
        return Command(action=candidate, args=parts[1:], raw=text)

    # Not a recognized command -- treat as free-form conversation
    return Command(action="chat", args=parts, raw=text)
