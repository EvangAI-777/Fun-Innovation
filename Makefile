.PHONY: test install clean

GEOVOX_DIR = Minecraft Innovations/GeoVox

test:
	cd "$(GEOVOX_DIR)" && pytest tests/ -v

install:
	cd "$(GEOVOX_DIR)" && pip install -e ".[all]" pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
