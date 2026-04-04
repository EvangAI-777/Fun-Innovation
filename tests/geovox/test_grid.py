"""Tests for the VoxelGrid core data structure."""

import numpy as np

from geovox.core.grid import VoxelGrid


def test_set_and_get():
    g = VoxelGrid()
    g.set(1, 2, 3, 42)
    assert g.get(1, 2, 3) == 42


def test_get_default():
    g = VoxelGrid()
    assert g.get(0, 0, 0) == 0
    assert g.get(0, 0, 0, default="air") == "air"


def test_contains():
    g = VoxelGrid()
    g.set(5, 5, 5, 1)
    assert (5, 5, 5) in g
    assert (0, 0, 0) not in g


def test_len():
    g = VoxelGrid()
    assert len(g) == 0
    g.set(0, 0, 0, 1)
    g.set(1, 0, 0, 2)
    assert len(g) == 2


def test_fill_column():
    g = VoxelGrid()
    g.fill_column(0, 0, 0, 4, "stone")
    assert len(g) == 5
    for y in range(5):
        assert g.get(0, y, 0) == "stone"


def test_bounds_empty():
    g = VoxelGrid()
    assert g.bounds() == ((0, 0, 0), (0, 0, 0))


def test_bounds():
    g = VoxelGrid()
    g.set(1, 2, 3, 1)
    g.set(10, 20, 30, 2)
    assert g.bounds() == ((1, 2, 3), (10, 20, 30))


def test_repr():
    g = VoxelGrid()
    g.set(0, 0, 0, 1)
    r = repr(g)
    assert "VoxelGrid" in r
    assert "1 cells" in r


def test_overwrite():
    g = VoxelGrid()
    g.set(0, 0, 0, "dirt")
    g.set(0, 0, 0, "stone")
    assert g.get(0, 0, 0) == "stone"
    assert len(g) == 1


def test_compute_slope_no_elevation():
    g = VoxelGrid()
    assert g.compute_slope() is None


def test_compute_slope_flat():
    g = VoxelGrid()
    g.metadata["elevation"] = np.ones((5, 5)) * 64.0
    slope = g.compute_slope()
    assert slope is not None
    assert slope.shape == (5, 5)
    np.testing.assert_allclose(slope, 0.0, atol=1e-10)


def test_compute_slope_gradient():
    g = VoxelGrid()
    # Linear ramp: each row increases by 10
    elevation = np.array([
        [0, 0, 0],
        [10, 10, 10],
        [20, 20, 20],
    ], dtype=np.float64)
    g.metadata["elevation"] = elevation
    slope = g.compute_slope()
    assert slope is not None
    # Center cell should have slope ~10 in the z direction
    assert slope[1, 1] > 5.0


def test_compute_slope_stores_in_metadata():
    g = VoxelGrid()
    g.metadata["elevation"] = np.array([[0, 10], [10, 20]], dtype=np.float64)
    slope = g.compute_slope()
    assert "slope" in g.metadata
    assert g.metadata["slope"] is slope
