"""Helpers to import modules from the INVALID_REQUEST directory (which has spaces in the path)."""

import importlib.util
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent.parent / "INVALID_REQUEST" / "Python Files"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _PYTHON_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verse_engine = _load("verse_engine", "verse_engine.py")
living_story = _load("living_story", "living_story.py")
