"""Tests for heightmap stitching and grid merge."""

import numpy as np
import pytest

from geovox.ingest.stitch import stitch_heightmaps
from geovox.core.grid import VoxelGrid


class TestStitchHeightmaps:
    def test_single_tile(self):
        data = np.ones((4, 4)) * 5.0
        result = stitch_heightmaps([(data, 0, 0)])
        assert result.shape == (4, 4)
        np.testing.assert_allclose(result, 5.0)

    def test_two_tiles_no_overlap(self):
        a = np.ones((3, 3)) * 1.0
        b = np.ones((3, 3)) * 2.0
        result = stitch_heightmaps([(a, 0, 0), (b, 3, 0)])
        assert result.shape == (3, 6)
        np.testing.assert_allclose(result[:, :3], 1.0)
        np.testing.assert_allclose(result[:, 3:], 2.0)

    def test_vertical_stacking(self):
        a = np.ones((2, 4)) * 10.0
        b = np.ones((2, 4)) * 20.0
        result = stitch_heightmaps([(a, 0, 0), (b, 0, 2)])
        assert result.shape == (4, 4)
        np.testing.assert_allclose(result[:2, :], 10.0)
        np.testing.assert_allclose(result[2:, :], 20.0)

    def test_overlap_average(self):
        a = np.ones((3, 3)) * 10.0
        b = np.ones((3, 3)) * 20.0
        # b overlaps a by 1 column
        result = stitch_heightmaps([(a, 0, 0), (b, 2, 0)], overlap_mode="average")
        assert result.shape == (3, 5)
        np.testing.assert_allclose(result[:, 2], 15.0)  # overlap averaged

    def test_overlap_last(self):
        a = np.ones((3, 3)) * 10.0
        b = np.ones((3, 3)) * 20.0
        result = stitch_heightmaps([(a, 0, 0), (b, 2, 0)], overlap_mode="last")
        assert result.shape == (3, 5)
        np.testing.assert_allclose(result[:, 2], 20.0)  # last wins

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="No tiles"):
            stitch_heightmaps([])

    def test_invalid_mode(self):
        data = np.ones((2, 2))
        with pytest.raises(ValueError, match="overlap_mode"):
            stitch_heightmaps([(data, 0, 0)], overlap_mode="invalid")


class TestVoxelGridMerge:
    def test_basic_merge(self):
        a = VoxelGrid()
        a.set(0, 0, 0, "stone")
        a.set(1, 0, 0, "dirt")

        b = VoxelGrid()
        b.set(0, 0, 0, "grass")

        a.merge(b, offset=(5, 0, 0))
        assert a.get(5, 0, 0) == "grass"
        assert a.get(0, 0, 0) == "stone"
        assert len(a) == 3

    def test_merge_overwrites(self):
        a = VoxelGrid()
        a.set(0, 0, 0, "stone")

        b = VoxelGrid()
        b.set(0, 0, 0, "diamond")

        a.merge(b)
        assert a.get(0, 0, 0) == "diamond"

    def test_merge_with_offset(self):
        a = VoxelGrid()
        b = VoxelGrid()
        b.set(0, 0, 0, "ore")
        b.set(1, 1, 1, "ore")

        a.merge(b, offset=(10, 20, 30))
        assert a.get(10, 20, 30) == "ore"
        assert a.get(11, 21, 31) == "ore"
        assert len(a) == 2
