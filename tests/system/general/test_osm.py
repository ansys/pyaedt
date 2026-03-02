# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Test OpenStreetMap (OSM) module functionality with real pyvista and osmnx."""

import numpy as np
import pytest

from ansys.aedt.core.modeler.advanced_cad.osm import BuildingsPrep
from ansys.aedt.core.modeler.advanced_cad.osm import RoadPrep
from ansys.aedt.core.modeler.advanced_cad.osm import TerrainPrep


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class."""
    return


@pytest.fixture
def temp_cad_path(tmp_path):
    """Create a temporary CAD path for testing."""
    cad_dir = tmp_path / "cad_files"
    cad_dir.mkdir()
    return str(cad_dir)


# BuildingsPrep tests


def test_buildings_init(temp_cad_path):
    """Test BuildingsPrep initialization."""
    buildings_prep = BuildingsPrep(temp_cad_path)
    assert buildings_prep.cad_path == temp_cad_path


def test_create_building_roof(temp_cad_path):
    """Test building roof creation."""
    buildings_prep = BuildingsPrep(temp_cad_path)

    # Create a simple rectangular roof outline
    all_pos = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [10.0, 10.0, 0.0], [0.0, 10.0, 0.0]])

    roof = buildings_prep.create_building_roof(all_pos)
    assert roof is not None


# RoadPrep tests


def test_road_init(temp_cad_path):
    """Test RoadPrep initialization."""
    road_prep = RoadPrep(temp_cad_path)
    assert road_prep.cad_path == temp_cad_path


def test_create_roads(temp_cad_path):
    """Test road creation with real osmnx data."""
    road_prep = RoadPrep(temp_cad_path)

    location = [40.758, -73.9855]

    # First create terrain to pass as parameter
    terrain_prep = TerrainPrep(temp_cad_path)
    terrain_result = terrain_prep.get_terrain(location, max_radius=100, grid_size=10)

    # Try to create roads in this area with a small radius
    result = road_prep.create_roads(location, terrain_result["mesh"], max_radius=50, road_step=2)

    # Check that the result is a dictionary with expected keys
    assert isinstance(result, dict)
    assert "file_name" in result
    assert "mesh" in result


# TerrainPrep tests


def test_terrain_init(temp_cad_path):
    """Test TerrainPrep initialization."""
    terrain_prep = TerrainPrep(temp_cad_path)
    assert terrain_prep.cad_path == temp_cad_path


def test_terrain_init_default_path():
    """Test TerrainPrep initialization with default path."""
    terrain_prep = TerrainPrep()
    assert terrain_prep.cad_path == "./"


def test_terrain_get_terrain(temp_cad_path):
    """Test terrain generation with real elevation data."""
    terrain_prep = TerrainPrep(temp_cad_path)

    location = [40.7128, -74.0060]

    # Generate terrain for a small area
    result = terrain_prep.get_terrain(location, max_radius=100, grid_size=10)

    # Check that the result is a dictionary with expected keys
    assert isinstance(result, dict)
    assert "file_name" in result
    assert "mesh" in result
    assert result["mesh"] is not None


def test_terrain_get_elevation_basic():
    """Test get_elevation returns correct structure."""
    center_lat_lon = [40.7128, -74.0060]
    max_radius = 100
    grid_size = 10

    all_data, all_lat_lon, all_utm = TerrainPrep.get_elevation(
        center_lat_lon, max_radius=max_radius, grid_size=grid_size
    )

    # Check that arrays are returned
    assert isinstance(all_data, np.ndarray)
    assert isinstance(all_lat_lon, np.ndarray)
    assert isinstance(all_utm, np.ndarray)

    # Check dimensions
    expected_samples = int(np.ceil(max_radius * 2 / grid_size))
    assert all_data.shape == (expected_samples, expected_samples)
    assert all_lat_lon.shape == (expected_samples, expected_samples, 2)
    assert all_utm.shape == (expected_samples, expected_samples, 2)

    # Check that all elevation data is zero (no actual elevation data fetched)
    assert np.all(all_data == 0)


def test_terrain_get_elevation_different_grid_sizes():
    """Test get_elevation with different grid sizes."""
    center_lat_lon = [40.7128, -74.0060]
    max_radius = 50

    # Test with larger grid size
    all_data_5m, _, _ = TerrainPrep.get_elevation(center_lat_lon, max_radius=max_radius, grid_size=5)
    all_data_10m, _, _ = TerrainPrep.get_elevation(center_lat_lon, max_radius=max_radius, grid_size=10)

    # Smaller grid size should result in more samples
    assert all_data_5m.shape[0] > all_data_10m.shape[0]


# File operations tests


def test_buildings_path_handling(temp_cad_path):
    """Test that BuildingsPrep handles paths correctly."""
    buildings_prep = BuildingsPrep(temp_cad_path)
    assert buildings_prep.cad_path == temp_cad_path


def test_road_path_handling(temp_cad_path):
    """Test that RoadPrep handles paths correctly."""
    road_prep = RoadPrep(temp_cad_path)
    assert road_prep.cad_path == temp_cad_path


def test_terrain_path_handling(temp_cad_path):
    """Test that TerrainPrep handles paths correctly."""
    terrain_prep = TerrainPrep(temp_cad_path)
    assert terrain_prep.cad_path == temp_cad_path
