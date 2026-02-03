"""Generate a test heightmap and show how to run it through GeoVox.

Usage:
    python examples/generate_test_terrain.py
    python -m geovox pipeline examples/test_terrain.png -o examples/test_output --sea-level 48
"""

import numpy as np
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required: pip install Pillow")
    raise SystemExit(1)


def main():
    size = 128

    # Overlapping sine waves for natural-looking hills and valleys
    x = np.linspace(0, 4 * np.pi, size)
    z = np.linspace(0, 4 * np.pi, size)
    xx, zz = np.meshgrid(x, z)

    terrain = (
        np.sin(xx) * np.cos(zz) * 0.4
        + np.sin(xx * 0.5 + 1) * np.sin(zz * 0.7 + 2) * 0.3
        + np.sin(xx * 2.1) * np.cos(zz * 1.7) * 0.15
        + np.sin(xx * 0.3 - zz * 0.2) * 0.15
    )

    # Normalize to 0-255
    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
    terrain = (terrain * 255).astype(np.uint8)

    output = Path(__file__).parent / "test_terrain.png"
    Image.fromarray(terrain, mode="L").save(output)

    print(f"Generated {size}x{size} test heightmap: {output}")
    print(f"  Elevation range: {terrain.min()}-{terrain.max()}")
    print()
    print("Run the pipeline:")
    print(f"  python -m geovox preview {output}")
    print(f"  python -m geovox pipeline {output} -o examples/test_output --sea-level 48")


if __name__ == "__main__":
    main()
