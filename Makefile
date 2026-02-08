.PHONY: test test-geovox test-roblox install clean

GEOVOX_DIR = Minecraft Innovations/GeoVox

test: test-geovox test-roblox

test-geovox:
	cd "$(GEOVOX_DIR)" && pytest ../../tests/geovox/ -v

test-roblox:
	pytest tests/roblox/ -v

install:
	cd "$(GEOVOX_DIR)" && pip install -e ".[all]" pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
