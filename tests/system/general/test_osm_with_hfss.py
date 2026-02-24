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

import json
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from ansys.aedt.core import Hfss


@pytest.fixture
def sample_stl_files(test_tmp_dir):
    """Create sample STL files for testing without Internet."""
    import pyvista as pv

    # Create a simple terrain mesh
    terrain = pv.Plane(i_size=100, j_size=100, i_resolution=10, j_resolution=10)

    # Add some elevation variation
    terrain.points[:, 2] = np.sin(terrain.points[:, 0] / 20) * 5 + np.cos(terrain.points[:, 1] / 20) * 3
    terrain_file = test_tmp_dir / "test_terrain.stl"
    terrain.save(str(terrain_file))

    # Create a simple building mesh
    building = pv.Box(bounds=[10, 20, 10, 20, 0, 30])
    building_file = test_tmp_dir / "test_buildings.stl"
    building.save(str(building_file))

    # Create a simple road mesh
    road = pv.Box(bounds=[0, 100, 45, 55, 0, 1])
    road_file = test_tmp_dir / "test_roads.stl"
    road.save(str(road_file))

    return {
        "terrain": {"file": str(terrain_file), "mesh": terrain},
        "buildings": {"file": str(building_file), "mesh": building},
        "roads": {"file": str(road_file), "mesh": road},
    }


def test_import_from_open_street_map(add_app, sample_stl_files, test_tmp_dir):
    """Test OSM import with HFSS using mocked data."""
    # Create HFSS app
    hfss = add_app(application=Hfss, solution_type="SBR+")

    # Mock the OSM preparation classes to use our pre-generated files
    with (
        patch("ansys.aedt.core.modeler.advanced_cad.osm.TerrainPrep") as mock_terrain_class,
        patch("ansys.aedt.core.modeler.advanced_cad.osm.BuildingsPrep") as mock_buildings_class,
        patch("ansys.aedt.core.modeler.advanced_cad.osm.RoadPrep") as mock_roads_class,
    ):
        # Setup terrain mock
        mock_terrain = MagicMock()
        mock_terrain_class.return_value = mock_terrain
        mock_terrain.get_terrain.return_value = {
            "file_name": sample_stl_files["terrain"]["file"],
            "mesh": sample_stl_files["terrain"]["mesh"],
        }

        # Setup buildings mock
        mock_buildings = MagicMock()
        mock_buildings_class.return_value = mock_buildings
        mock_buildings.generate_buildings.return_value = {
            "file_name": sample_stl_files["buildings"]["file"],
            "mesh": sample_stl_files["buildings"]["mesh"],
        }

        # Setup roads mock
        mock_roads = MagicMock()
        mock_roads_class.return_value = mock_roads
        mock_roads.create_roads.return_value = {
            "file_name": sample_stl_files["roads"]["file"],
            "mesh": sample_stl_files["roads"]["mesh"],
        }

        # Call import_from_openstreet_map
        result = hfss.modeler.import_from_openstreet_map(
            latitude_longitude=[40.273726, -80.168269],
            env_name="test_hfss_environment",
            terrain_radius=100,
            include_osm_buildings=True,
            including_osm_roads=True,
            import_in_aedt=True,
            plot_before_importing=False,
            z_offset=0.5,
            road_step=3,
            road_width=10,
            create_lightweight_part=False,
        )

        # Verify the result structure
        assert result is not None
        assert result["name"] == "test_hfss_environment"
        assert result["type"] == "environment"
        assert "parts" in result
        assert "terrain" in result["parts"]
        assert "buildings" in result["parts"]
        assert "roads" in result["parts"]

        # Verify objects were imported to HFSS
        assert len(hfss.modeler.object_names) > 0

        # Verify JSON file was created
        json_file = Path(hfss.working_directory) / "test_hfss_environment.json"
        assert json_file.exists()

        # Verify JSON content
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            assert json_data["name"] == "test_hfss_environment"
            assert json_data["radius"] == 100

        # Verify model units are set to meters
        assert hfss.modeler.model_units == "meter"

        hfss.close_project(save=False)
