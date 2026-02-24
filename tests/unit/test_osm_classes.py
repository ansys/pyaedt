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

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from ansys.aedt.core.modeler.advanced_cad.osm import BuildingsPrep
from ansys.aedt.core.modeler.advanced_cad.osm import RoadPrep
from ansys.aedt.core.modeler.advanced_cad.osm import TerrainPrep


@pytest.fixture
def temp_cad_path(test_tmp_dir):
    """Create a temporary CAD path for testing."""
    cad_dir = test_tmp_dir / "cad"
    cad_dir.mkdir()
    return str(cad_dir)


@pytest.fixture
def sample_terrain_mesh():
    """Create a mock terrain mesh for testing."""
    pv = pytest.importorskip("pyvista")
    terrain = pv.Plane(i_size=200, j_size=200, i_resolution=20, j_resolution=20)
    # Add elevation variation
    terrain.points[:, 2] = np.sin(terrain.points[:, 0] / 30) * 10 + np.cos(terrain.points[:, 1] / 30) * 5
    return terrain


@pytest.fixture
def mock_osmnx_features():
    """Create mock OSM features data for buildings."""
    geopandas = pytest.importorskip("geopandas")
    _ = pytest.importorskip("shapely")
    from shapely.geometry import Polygon

    # Create sample building polygons
    polygons = [
        Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
        Polygon([(20, 20), (30, 20), (30, 30), (20, 30)]),
        Polygon([(50, 50), (70, 50), (70, 70), (50, 70)]),
    ]

    data = {
        "geometry": polygons,
        "building": ["yes", "yes", "yes"],
        "building:levels": [3, 5, 2],
        "height": [9.0, 15.0, 6.0],
    }

    gdf = geopandas.GeoDataFrame(data, crs="EPSG:4326")
    return gdf


@pytest.fixture
def mock_osmnx_roads():
    """Create mock OSM road network data."""
    networkx = pytest.importorskip("networkx")
    geopandas = pytest.importorskip("geopandas")
    _ = pytest.importorskip("shapely")
    from shapely.geometry import LineString

    # Create sample road lines
    lines = [
        LineString([(0, 0), (100, 0)]),
        LineString([(0, 0), (0, 100)]),
        LineString([(50, 50), (150, 50)]),
    ]

    edges_data = {
        "geometry": lines,
        "highway": ["primary", "secondary", "residential"],
    }

    edges_gdf = geopandas.GeoDataFrame(edges_data, crs="EPSG:4326")

    # Create a simple graph
    G = networkx.MultiDiGraph()
    G.add_edge(0, 1, geometry=lines[0])
    G.add_edge(0, 2, geometry=lines[1])
    G.add_edge(3, 4, geometry=lines[2])

    return G, edges_gdf


# Tests for TerrainPrep class


def test_terrain_prep_initialization(temp_cad_path):
    """Test TerrainPrep class initialization."""
    terrain_prep = TerrainPrep(cad_path=temp_cad_path)

    assert terrain_prep.cad_path == temp_cad_path
    assert isinstance(terrain_prep.cad_path, str)


def test_terrain_prep_default_path():
    """Test TerrainPrep with default path."""
    terrain_prep = TerrainPrep()

    assert terrain_prep.cad_path == "./"


def test_terrain_prep_get_elevation():
    """Test get_elevation method returns correct data structure."""
    center_lat_lon = [40.273726, -80.168269]
    max_radius = 100
    grid_size = 20

    all_data, all_lat_lon, all_utm = TerrainPrep.get_elevation(
        center_lat_lon, max_radius=max_radius, grid_size=grid_size
    )

    # Verify return types
    assert isinstance(all_data, np.ndarray)
    assert isinstance(all_lat_lon, np.ndarray)
    assert isinstance(all_utm, np.ndarray)

    # Verify shapes
    expected_samples = int(np.ceil(max_radius * 2 / grid_size))
    assert all_data.shape == (expected_samples, expected_samples)
    assert all_lat_lon.shape == (expected_samples, expected_samples, 2)
    assert all_utm.shape == (expected_samples, expected_samples, 2)

    # Verify data is initialized to zeros (no actual elevation data fetched)
    assert np.all(all_data == 0)


def test_terrain_prep_get_elevation_various_grid_sizes():
    """Test get_elevation with various grid sizes."""
    center_lat_lon = [40.273726, -80.168269]
    max_radius = 100

    for grid_size in [5, 10, 20, 50]:
        all_data, all_lat_lon, all_utm = TerrainPrep.get_elevation(
            center_lat_lon, max_radius=max_radius, grid_size=grid_size
        )

        expected_samples = int(np.ceil(max_radius * 2 / grid_size))
        assert all_data.shape[0] == expected_samples
        assert all_data.shape[1] == expected_samples


def test_terrain_prep_get_terrain(temp_cad_path, sample_terrain_mesh):
    """Test get_terrain method creates STL file."""
    with patch("pyvista.PolyData") as mock_polydata:
        mock_polydata.return_value = sample_terrain_mesh

        terrain_prep = TerrainPrep(cad_path=temp_cad_path)
        center_lat_lon = [40.273726, -80.168269]

        result = terrain_prep.get_terrain(
            center_lat_lon=center_lat_lon,
            max_radius=100,
            grid_size=20,
            buffer_percent=0,
        )

        # Verify return structure
        assert isinstance(result, dict)
        assert "file_name" in result
        assert "mesh" in result

        # Verify file path
        expected_file = str(Path(temp_cad_path) / "terrain.stl")
        assert result["file_name"] == expected_file


def test_terrain_prep_get_terrain_with_buffer(temp_cad_path, sample_terrain_mesh):
    """Test get_terrain with buffer percentage."""
    with patch("pyvista.PolyData") as mock_polydata:
        mock_polydata.return_value = sample_terrain_mesh

        terrain_prep = TerrainPrep(cad_path=temp_cad_path)
        center_lat_lon = [40.273726, -80.168269]

        # Test with 20% buffer
        result = terrain_prep.get_terrain(
            center_lat_lon=center_lat_lon,
            max_radius=100,
            grid_size=20,
            buffer_percent=0.2,
        )

        assert "file_name" in result
        assert "mesh" in result


# Tests for BuildingsPrep class


def test_buildings_prep_initialization(temp_cad_path):
    """Test BuildingsPrep class initialization."""
    buildings_prep = BuildingsPrep(cad_path=temp_cad_path)

    assert buildings_prep.cad_path == temp_cad_path
    assert isinstance(buildings_prep.cad_path, str)


def test_buildings_prep_create_building_roof():
    """Test create_building_roof static method."""
    # Create sample building outline points
    all_pos = np.array(
        [
            [0.0, 0.0, 10.0],
            [10.0, 0.0, 10.0],
            [10.0, 10.0, 10.0],
            [0.0, 10.0, 10.0],
        ]
    )

    with (
        patch("vtk.vtkPoints") as mock_vtkpoints,
        patch("vtk.vtkPolygon") as mock_vtkpolygon,
        patch("vtk.vtkCellArray") as mock_vtkcellarray,
        patch("vtk.vtkPolyData") as mock_vtkpolydata,
        patch("vtk.vtkPolyDataMapper") as mock_vtkpolydatamapper,
        patch("vtk.vtkTriangleFilter") as mock_vtktrifilter,
        patch("pyvista.PolyData") as mock_pv_polydata,
    ):
        # Mock vtk objects
        mock_points = MagicMock()
        mock_vtkpoints.return_value = mock_points

        mock_polygon = MagicMock()
        mock_vtkpolygon.return_value = mock_polygon

        mock_polygons = MagicMock()
        mock_vtkcellarray.return_value = mock_polygons

        mock_polydata = MagicMock()
        mock_vtkpolydata.return_value = mock_polydata

        mock_mapper = MagicMock()
        mock_vtkpolydatamapper.return_value = mock_mapper

        mock_tri_filter = MagicMock()
        mock_vtktrifilter.return_value = mock_tri_filter
        mock_tri_filter.GetOutput.return_value = mock_polydata

        # Mock pyvista
        mock_roof = MagicMock()
        mock_pv_polydata.return_value = mock_roof

        _ = BuildingsPrep.create_building_roof(all_pos)

        # Verify vtk workflow was called
        assert mock_points.InsertNextPoint.call_count == len(all_pos)
        mock_polygon.GetPointIds.assert_called()
        mock_tri_filter.SetInputData.assert_called_once()
        mock_tri_filter.Update.assert_called_once()


def test_buildings_prep_generate_buildings_no_buildings(temp_cad_path, sample_terrain_mesh):
    """Test generate_buildings when no buildings exist."""
    with patch("osmnx.features.features_from_point") as mock_features:
        # Mock empty GeoDataFrame
        mock_gdf = MagicMock()
        mock_gdf.__len__.return_value = 0
        mock_features.return_value = mock_gdf

        buildings_prep = BuildingsPrep(cad_path=temp_cad_path)
        center_lat_lon = [40.273726, -80.168269]

        result = buildings_prep.generate_buildings(
            center_lat_lon=center_lat_lon,
            terrain_mesh=sample_terrain_mesh,
            max_radius=100,
        )

        # Verify empty result
        assert result["file_name"] is None
        assert result["mesh"] is None


def test_buildings_prep_generate_buildings_with_data(temp_cad_path, sample_terrain_mesh, mock_osmnx_features):
    """Test generate_buildings with building data."""
    with (
        patch("osmnx.features.features_from_point") as mock_features,
        patch("osmnx.projection.project_gdf") as mock_project,
        patch("pyvista.PolyData") as mock_pv_polydata,
        patch("pyvista.lines_from_points") as mock_lines,
    ):
        # Mock osmnx features
        mock_features.return_value = mock_osmnx_features
        mock_project.return_value = mock_osmnx_features

        # Mock pyvista objects
        mock_polydata = MagicMock()
        mock_polydata.points = np.array([[0, 0, 0]])
        mock_pv_polydata.return_value = mock_polydata
        mock_lines.return_value = mock_polydata

        buildings_prep = BuildingsPrep(cad_path=temp_cad_path)
        center_lat_lon = [40.273726, -80.168269]

        with patch.object(BuildingsPrep, "create_building_roof", return_value=mock_polydata):
            result = buildings_prep.generate_buildings(
                center_lat_lon=center_lat_lon,
                terrain_mesh=None,  # Test without terrain mesh
                max_radius=100,
            )

        # Verify result structure
        assert "file_name" in result
        assert "mesh" in result
        assert "temp" in result

        # Verify file path
        expected_file = str(Path(temp_cad_path) / "buildings.stl")
        assert result["file_name"] == expected_file


# Tests for RoadPrep class


def test_road_prep_initialization(temp_cad_path):
    """Test RoadPrep class initialization."""
    road_prep = RoadPrep(cad_path=temp_cad_path)

    assert road_prep.cad_path == temp_cad_path
    assert isinstance(road_prep.cad_path, str)


def test_road_prep_create_roads(temp_cad_path, sample_terrain_mesh, mock_osmnx_roads):
    """Test create_roads method."""
    graph, edges_gdf = mock_osmnx_roads

    with (
        patch("osmnx.graph_from_point") as mock_graph_from_point,
        patch("osmnx.project_graph") as mock_project_graph,
        patch("osmnx.graph_to_gdfs") as mock_graph_to_gdfs,
        patch("pyvista.PolyData") as mock_pv_polydata,
        patch("pyvista.lines_from_points") as mock_lines,
        patch("pyvista.Circle") as mock_circle,
    ):
        # Mock osmnx graph functions
        mock_graph_from_point.return_value = graph
        mock_project_graph.return_value = graph
        mock_graph_to_gdfs.return_value = (MagicMock(), edges_gdf)

        # Mock pyvista objects
        mock_polydata = MagicMock()
        mock_polydata.points = np.array([[0, 0, 0], [100, 100, 5]])
        mock_pv_polydata.return_value = mock_polydata
        mock_lines.return_value = mock_polydata

        mock_circle_obj = MagicMock()
        mock_circle_obj.delaunay_2d.return_value = mock_polydata
        mock_circle_obj.translate.return_value = mock_polydata
        mock_circle.return_value = mock_circle_obj

        road_prep = RoadPrep(cad_path=temp_cad_path)
        center_lat_lon = [40.273726, -80.168269]

        result = road_prep.create_roads(
            center_lat_lon=center_lat_lon,
            terrain_mesh=sample_terrain_mesh,
            max_radius=500,
            z_offset=0.5,
            road_step=10,
            road_width=5,
        )

        # Verify result structure
        assert isinstance(result, dict)
        assert "file_name" in result
        assert "mesh" in result
        assert "graph" in result

        # Verify file path
        expected_file = str(Path(temp_cad_path) / "roads.stl")
        assert result["file_name"] == expected_file

        # Verify graph_from_point was called correctly
        mock_graph_from_point.assert_called_once_with(center_lat_lon, dist=500, simplify=False, network_type="all")


def test_road_prep_create_roads_custom_parameters(temp_cad_path, sample_terrain_mesh, mock_osmnx_roads):
    """Test create_roads with custom parameters."""
    graph, edges_gdf = mock_osmnx_roads

    with (
        patch("osmnx.graph_from_point") as mock_graph_from_point,
        patch("osmnx.project_graph") as mock_project_graph,
        patch("osmnx.graph_to_gdfs") as mock_graph_to_gdfs,
        patch("pyvista.PolyData") as mock_pv_polydata,
        patch("pyvista.lines_from_points") as mock_lines,
        patch("pyvista.Circle") as mock_circle,
    ):
        mock_graph_from_point.return_value = graph
        mock_project_graph.return_value = graph
        mock_graph_to_gdfs.return_value = (MagicMock(), edges_gdf)

        mock_polydata = MagicMock()
        mock_polydata.points = np.array([[0, 0, 0], [100, 100, 5]])
        mock_pv_polydata.return_value = mock_polydata
        mock_lines.return_value = mock_polydata

        mock_circle_obj = MagicMock()
        mock_circle_obj.delaunay_2d.return_value = mock_polydata
        mock_circle_obj.translate.return_value = mock_polydata
        mock_circle.return_value = mock_circle_obj

        road_prep = RoadPrep(cad_path=temp_cad_path)
        center_lat_lon = [40.273726, -80.168269]

        # Test with custom parameters
        result = road_prep.create_roads(
            center_lat_lon=center_lat_lon,
            terrain_mesh=sample_terrain_mesh,
            max_radius=1000,
            z_offset=2.0,
            road_step=5,
            road_width=8,
        )

        assert "file_name" in result
        assert "mesh" in result
