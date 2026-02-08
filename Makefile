.PHONY: test test-geovox test-roblox test-originals test-automuse install clean

GEOVOX_DIR = Minecraft Innovations/GeoVox
AUTOMUSE_DIR = Audio Innovations/AutoMuse

test: test-geovox test-roblox test-originals test-automuse

test-geovox:
	cd "$(GEOVOX_DIR)" && pytest ../../tests/geovox/ -v

test-roblox:
	pytest tests/roblox/ -v

test-originals:
	pytest tests/invalid_request/ -v

test-automuse:
	cd "$(AUTOMUSE_DIR)" && python -m pytest ../../tests/automuse/ -v

install:
	cd "$(GEOVOX_DIR)" && pip install -e ".[all]" pytest
	cd "$(AUTOMUSE_DIR)" && pip install -e . pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
