"""Tests for heightmap preprocessing functions."""

import numpy as np
import pytest

from geovox.ingest.preprocess import smooth_heightmap, crop_heightmap, resample_heightmap


class TestSmoothHeightmap:
    def test_flat_unchanged(self):
        data = np.ones((5, 5), dtype=np.float64) * 10.0
        result = smooth_heightmap(data, kernel_size=3)
        np.testing.assert_allclose(result, 10.0)

    def test_smooths_spike(self):
        data = np.zeros((5, 5), dtype=np.float64)
        data[2, 2] = 9.0
        result = smooth_heightmap(data, kernel_size=3)
        assert result[2, 2] < 9.0
        assert result[2, 2] == 1.0  # 9/9 = 1.0

    def test_preserves_shape(self):
        data = np.random.rand(10, 15)
        result = smooth_heightmap(data, kernel_size=5)
        assert result.shape == (10, 15)

    def test_invalid_kernel_size(self):
        data = np.ones((3, 3))
        with pytest.raises(ValueError, match="positive odd"):
            smooth_heightmap(data, kernel_size=4)
        with pytest.raises(ValueError, match="positive odd"):
            smooth_heightmap(data, kernel_size=0)

    def test_rejects_3d(self):
        with pytest.raises(ValueError, match="2D"):
            smooth_heightmap(np.ones((3, 3, 3)))


class TestCropHeightmap:
    def test_basic_crop(self):
        data = np.arange(25).reshape(5, 5).astype(float)
        result = crop_heightmap(data, x=1, z=1, width=3, height=3)
        assert result.shape == (3, 3)
        assert result[0, 0] == 6.0  # data[1, 1]
        assert result[2, 2] == 18.0  # data[3, 3]

    def test_full_crop(self):
        data = np.ones((4, 6))
        result = crop_heightmap(data, x=0, z=0, width=6, height=4)
        assert result.shape == (4, 6)

    def test_out_of_bounds(self):
        data = np.ones((5, 5))
        with pytest.raises(ValueError, match="out of bounds"):
            crop_heightmap(data, x=3, z=0, width=5, height=5)

    def test_returns_copy(self):
        data = np.ones((5, 5))
        result = crop_heightmap(data, x=0, z=0, width=3, height=3)
        result[0, 0] = 99.0
        assert data[0, 0] == 1.0


class TestResampleHeightmap:
    def test_same_size(self):
        data = np.arange(9).reshape(3, 3).astype(float)
        result = resample_heightmap(data, 3, 3)
        np.testing.assert_allclose(result, data)

    def test_upscale(self):
        data = np.array([[0.0, 10.0], [10.0, 20.0]])
        result = resample_heightmap(data, 3, 3)
        assert result.shape == (3, 3)
        assert result[0, 0] == 0.0
        assert result[0, 2] == 10.0
        assert result[2, 0] == 10.0
        assert result[2, 2] == 20.0
        # Center is bilinear interpolation of all 4 corners
        assert result[1, 1] == pytest.approx(10.0)

    def test_downscale(self):
        data = np.ones((10, 10)) * 5.0
        result = resample_heightmap(data, 3, 3)
        assert result.shape == (3, 3)
        np.testing.assert_allclose(result, 5.0)

    def test_invalid_target(self):
        data = np.ones((3, 3))
        with pytest.raises(ValueError, match="positive"):
            resample_heightmap(data, 0, 5)

    def test_preserves_corners(self):
        data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
        result = resample_heightmap(data, 5, 5)
        assert result[0, 0] == pytest.approx(1.0)
        assert result[0, -1] == pytest.approx(3.0)
        assert result[-1, 0] == pytest.approx(7.0)
        assert result[-1, -1] == pytest.approx(9.0)
