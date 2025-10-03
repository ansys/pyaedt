# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import math as mathlib
import os
import warnings

import numpy as np

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.general_methods import settings
from ansys.aedt.core.internal.checks import graphics_required

logger = settings.logger

try:
    import osmnx as ox
except ImportError:  # pragma: no cover
    warnings.warn("OpenStreetMap Reader requires osmnx extra package.\nInstall with \n\npip install osmnx")

ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX"


class BuildingsPrep(PyAedtBase):
    """Contains all basic functions needed to generate buildings stl files."""

    def __init__(self, cad_path):
        self.cad_path = cad_path

    @staticmethod
    @pyaedt_function_handler()
    @graphics_required
    def create_building_roof(all_pos):
        """Generate a filled in polygon from outline.

        Includes concave and convex shapes.

        Parameters
        ----------
        all_pos : list

        Returns
        -------
        :class:`pyvista.PolygonData`
        """
        import pyvista as pv
        import vtk

        points = vtk.vtkPoints()
        for each in all_pos:
            points.InsertNextPoint(each[0], each[1], each[2])

        # Create the polygon
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(len(all_pos))  # make a quad
        for n in range(len(all_pos)):
            polygon.GetPointIds().SetId(n, n)

        # Add the polygon to a list of polygons
        polygons = vtk.vtkCellArray()
        polygons.InsertNextCell(polygon)

        # Create a PolyData
        polygonPolyData = vtk.vtkPolyData()
        polygonPolyData.SetPoints(points)
        polygonPolyData.SetPolys(polygons)

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()

        mapper.SetInputData(polygonPolyData)

        triFilter = vtk.vtkTriangleFilter()
        # let's filter the polydata
        triFilter.SetInputData(polygonPolyData)
        triFilter.Update()

        polygonPolyDataFiltered = triFilter.GetOutput()
        roof = pv.PolyData(polygonPolyDataFiltered)
        return roof

    @pyaedt_function_handler()
    @graphics_required
    def generate_buildings(self, center_lat_lon, terrain_mesh, max_radius=500):
        """Generate the buildings stl file.

        Parameters
        ----------
        center_lat_lon : list
            Latitude and longitude.
        terrain_mesh : :class:`pyvista.PolygonData`
            Terrain mesh.
        max_radius : float, int
            Radius around latitude and longitude.

        Returns
        -------
        dict
            Info of generated stl file.
        """
        import pyvista as pv

        # TODO: Remove compatibility with <2.0 when releasing pyaedt v1.0 ?
        try:
            gdf = ox.geometries.geometries_from_point(center_lat_lon, tags={"building": True}, dist=max_radius)
        # NOTE: Handle breaking changes introduced in osmn>=v2.0
        except AttributeError:
            gdf = ox.features.features_from_point(center_lat_lon, tags={"building": True}, dist=max_radius)

        utm_center = convert_latlon_to_utm(center_lat_lon[0], center_lat_lon[1])
        center_offset_x = utm_center[0]
        center_offset_y = utm_center[1]

        if len(gdf) == 0:
            logger.info("No Buildings Exists in Selected Geometry")
            return {"file_name": None, "mesh": None}
        else:
            # TODO: Remove compatibility with <2.0 when releasing pyaedt v1.0 ?
            try:
                gdf_proj = ox.project_gdf(gdf)
            # NOTE: Handle breaking changes introduced in osmn>=v2.0
            except AttributeError:
                gdf_proj = ox.projection.project_gdf(gdf)

            geo = gdf_proj["geometry"]
            try:
                levels = gdf_proj["building:levels"]
                levels = levels.array
            except KeyError:
                levels = [1] * len(geo)
            try:
                height = gdf_proj["height"]
                height = height.array
            except KeyError:
                height = [10] * len(geo)

            temp = [levels, height]
            geo = geo.array

            building_meshes = pv.PolyData()  # empty location where all building meshses are stored

            logger.info("\nGenerating Buildings")
            last_displayed = -1
            for n, _ in enumerate(geo):
                g = geo[n]
                if hasattr(g, "exterior"):
                    outer = g.exterior

                    xpos = np.array(outer.xy[0])
                    ypos = np.array(outer.xy[1])
                    level = levels[n]
                    h = height[n]

                    points = np.zeros((np.shape(outer.xy)[1], 3))
                    points[:, 0] = xpos
                    points[:, 1] = ypos
                    points[:, 0] -= center_offset_x
                    points[:, 1] -= center_offset_y

                    delta_elevation = 0
                    if terrain_mesh:
                        buffer = 50  # additional distance so intersection test is further away than directly on surface
                        bb_terrain = terrain_mesh.bounds
                        start_z = bb_terrain[4] - buffer
                        stop_z = bb_terrain[5] + buffer

                        # The shape files do not have z/elevation position. So for them to align to the
                        # terrain we need to first get the position of the terrain at the xy position of shape file
                        # this will align the buildins so they sit on the terrain no matter the location
                        elevation_on_outline = []

                        # check every point on the building shape for z elevation location
                        for point in points:
                            # shoot ray to look for intersection point
                            start_ray = [point[0], point[1], start_z]
                            stop_ray = [point[0], point[1], stop_z]
                            intersection_point, _ = terrain_mesh.ray_trace(start_ray, stop_ray)
                            if len(intersection_point) != 0:
                                z_surface_location = intersection_point.flatten()[2]
                                elevation_on_outline.append(z_surface_location)
                        # find lowest point on building outline to align location
                        if elevation_on_outline:
                            min_elevation = np.min(elevation_on_outline)
                            max_elevation = np.max(elevation_on_outline)
                            delta_elevation = max_elevation - min_elevation

                            # change z position to minimum elevation of terrain
                            points[:, 2] = min_elevation
                        else:
                            points[:, 2] = start_z

                    num_percent_bins = 40
                    percent = np.round((n + 1) / (len(geo)) * 100, decimals=1)
                    if percent % 10 == 0 and percent != last_displayed:
                        last_displayed = percent
                        perc_done = int(num_percent_bins * percent / 100)
                        perc_left = num_percent_bins - perc_done
                        percent_symbol1 = "." * perc_left
                        percent_symbol2 = "#" * perc_done

                        i = percent_symbol2 + percent_symbol1 + " " + str(percent) + "% "
                        logger.info(f"\rPercent Complete:{i}")

                    # create closed and filled polygon from outline of building
                    roof = self.create_building_roof(points)
                    if np.isnan(float(h)) is False:
                        extrude_h = float(h) * 2
                    elif np.isnan(float(level)) is False:
                        extrude_h = float(level) * 10
                    else:
                        extrude_h = 15.0

                    outline = pv.lines_from_points(points, close=True)

                    vert_walls = outline.extrude([0, 0, extrude_h + delta_elevation], inplace=False)

                    roof_location = np.array([0, 0, extrude_h + delta_elevation])
                    roof.translate(roof_location, inplace=True)

                    building_meshes += vert_walls
                    building_meshes += roof

            el = building_meshes.points[:, 2]

            building_meshes["Elevation"] = el.ravel(order="F")

            file_out = self.cad_path + "\\buildings.stl"
            building_meshes.save(file_out, binary=True)

            return {"file_name": file_out, "mesh": building_meshes, "temp": temp}


class RoadPrep(PyAedtBase):
    """Contains all basic functions needed to generate road stl files."""

    def __init__(self, cad_path):
        self.cad_path = cad_path

    @pyaedt_function_handler()
    @graphics_required
    def create_roads(self, center_lat_lon, terrain_mesh, max_radius=1000, z_offset=0, road_step=10, road_width=5):
        """Generate the road stl file.

        Parameters
        ----------
        center_lat_lon : list
            Latitude and longitude.
        terrain_mesh : :class:`pyvista.PolygonData`
            Terrain mesh.
        max_radius : float, int
            Radius around latitude and longitude.
        z_offset : float, optional
            Elevation offset of the road.
        road_step : float, optional
            Road computation steps in meters.
        road_width : float, optional
            Road width in meter.

        Returns
        -------
        dict
            Info of generated stl file.
        """
        import pyvista as pv

        # TODO: Remove compatibility with <2.0 when releasing pyaedt v1.0 ?
        try:
            graph = ox.graph_from_point(
                center_lat_lon, dist=max_radius, simplify=False, network_type="all", clean_periphery=True
            )
        # NOTE: Handle breaking changes introduced in osmn>=v2.0
        except TypeError:
            graph = ox.graph_from_point(center_lat_lon, dist=max_radius, simplify=False, network_type="all")

        g_projected = ox.project_graph(graph)

        utm_center = convert_latlon_to_utm(center_lat_lon[0], center_lat_lon[1])
        center_offset_x = utm_center[0]
        center_offset_y = utm_center[1]

        _, edges = ox.graph_to_gdfs(g_projected)
        lines = []

        buffer = 10  # additional distance so intersection test is further away than directly on surface
        bb_terrain = terrain_mesh.bounds
        start_z = bb_terrain[4] - buffer
        stop_z = bb_terrain[5] + buffer

        line = pv.PolyData()
        road_ends = pv.PolyData()
        # convert each edge into a line
        count = 0
        last_displayed = -1
        for _, row in edges.iterrows():
            count += 1
            num_percent_bins = 40

            percent = np.round((count) / (len(edges)) * 100, decimals=1)
            if percent % 10 == 0 and percent != last_displayed:
                last_displayed = percent
                perc_done = int(num_percent_bins * percent / 100)
                perc_left = num_percent_bins - perc_done
                percent_symbol1 = "." * perc_left
                percent_symbol2 = "#" * perc_done

                i = percent_symbol2 + percent_symbol1 + " " + str(percent) + "% "
                logger.info(f"\rPercent Complete:{i}")

            x_pts = row["geometry"].xy[0]
            y_pts = row["geometry"].xy[1]
            z_pts = np.empty(len(x_pts))
            z_pts.fill(start_z + z_offset)
            for n in range(len(z_pts)):
                x_pts[n] = x_pts[n] - center_offset_x
                y_pts[n] = y_pts[n] - center_offset_y
                start_ray = [x_pts[n], y_pts[n], start_z]
                stop_ray = [x_pts[n], y_pts[n], stop_z]
                points, _ = terrain_mesh.ray_trace(start_ray, stop_ray)
                if len(points) != 0:
                    z_surface_location = points.flatten()[2]
                    z_pts[n] = z_surface_location + z_offset
            pts = np.column_stack((x_pts, y_pts, z_pts))
            # always 2 points, linear interpolate to higher number of points
            dist = np.sqrt(
                np.power(pts[0][0] - pts[1][0], 2)
                + np.power(pts[0][1] - pts[1][1], 2)
                + np.power(pts[0][2] - pts[1][2], 2)
            )
            if dist > road_step:
                num_steps = int(dist / road_step)
                xpos = np.linspace(pts[0][0], pts[1][0], num=num_steps)
                ypos = np.linspace(pts[0][1], pts[1][1], num=num_steps)
                zpos = np.linspace(pts[0][2], pts[1][2], num=num_steps)
                pts = np.column_stack((xpos, ypos, zpos))
            try:
                line += pv.lines_from_points(pts, close=True)
            except ValueError:
                pass
            end_shape = pv.Circle(road_width, resolution=16).delaunay_2d()
            road_ends += end_shape.translate(pts[0], inplace=False)
            end_shape = pv.Circle(road_width, resolution=16).delaunay_2d()
            road_ends += end_shape.translate(pts[-1], inplace=False)
            lines.append(line)

        roads = line.ribbon(width=road_width, normal=[0, 0, 1])
        roads += road_ends
        el = roads.points[:, 2]

        roads["Elevation"] = el.ravel(order="F")
        file_out = os.path.join(self.cad_path + "\\roads.stl")
        roads.save(file_out)
        return {"file_name": file_out, "mesh": roads, "graph": g_projected}


class TerrainPrep(PyAedtBase):
    """Contains all basic functions needed for creating a terrain stl mesh."""

    def __init__(self, cad_path="./"):
        self.cad_path = cad_path

    @pyaedt_function_handler()
    @graphics_required
    def get_terrain(self, center_lat_lon, max_radius=500, grid_size=5, buffer_percent=0):
        """Generate the terrain stl file.

        Parameters
        ----------
        center_lat_lon : list
            Latitude and longitude.
        max_radius : float, int
            Radius around latitude and longitude.
        grid_size : float, optional
            Grid size in meters.
        buffer_percent : float, optional
            Buffer extra size over the radius.


        Returns
        -------
        dict
            Info of generated stl file.
        """
        import pyvista as pv

        utm_center = convert_latlon_to_utm(center_lat_lon[0], center_lat_lon[1])
        logger.info("Generating Terrain")
        max_radius = max_radius * (buffer_percent + 1)
        all_data, _, all_utm = self.get_elevation(
            center_lat_lon,
            max_radius=max_radius,
            grid_size=grid_size,
        )

        all_data = np.nan_to_num(all_data, nan=-32768)
        logger.info("Processing Geometry")
        xyz = []
        for lat_idx in range(all_data.shape[0]):
            for lon_idx in range(all_data.shape[1]):
                latlat_utm_centered = all_utm[lat_idx][lon_idx][0] - utm_center[0]
                lonlon_utm_centered = all_utm[lat_idx][lon_idx][1] - utm_center[1]

                if all_data[lat_idx][lon_idx] != -32768:  # this is missing data, don't add if it doesn't exist
                    xyz.append([latlat_utm_centered, lonlon_utm_centered, all_data[lat_idx][lon_idx]])
        xyz = np.array(xyz)

        file_out = self.cad_path + "/terrain.stl"
        logger.info("saving STL as " + file_out)
        terrain_mesh = pv.PolyData(xyz)
        terrain_mesh = terrain_mesh.delaunay_2d(tol=10 / (2 * max_radius) / 2)
        terrain_mesh = terrain_mesh.smooth(n_iter=100, relaxation_factor=0.04)

        el = terrain_mesh.points[:, 2]

        terrain_mesh["Elevation"] = el.ravel(order="F")

        terrain_mesh.save(file_out)
        return {"file_name": file_out, "mesh": terrain_mesh}

    @staticmethod
    @pyaedt_function_handler()
    def get_elevation(
        center_lat_lon,
        max_radius=500,
        grid_size=3,
    ):
        """Get Elevation map.

        Parameters
        ----------
        center_lat_lon : list
            Latitude and longitude.
        max_radius : float, int
            Radius around latitude and longitude.
        grid_size : float, optional
            Grid size in meters.

        Returns
        -------
        tuple
        """
        latitude = center_lat_lon[0]
        longitude = center_lat_lon[1]

        utm_center = convert_latlon_to_utm(center_lat_lon[0], center_lat_lon[1])

        utm_x_min = utm_center[0] - max_radius
        utm_x_max = utm_center[0] + max_radius

        utm_y_min = utm_center[1] - max_radius
        utm_y_max = utm_center[1] + max_radius

        sample_grid_size = grid_size  # meters
        num_samples = int(np.ceil(max_radius * 2 / sample_grid_size))
        x_samples = np.linspace(utm_x_min, utm_x_max, int(num_samples))
        y_samples = np.linspace(utm_y_min, utm_y_max, int(num_samples))

        all_data = np.zeros((num_samples, num_samples))
        all_utm = np.zeros((num_samples, num_samples, 2))
        all_lat_lon = np.zeros((num_samples, num_samples, 2))
        logger.info("Terrain Points...")
        last_displayed = -1
        for n, x in enumerate(x_samples):
            for m, y in enumerate(y_samples):
                num_percent_bins = 40
                percent_complete = int((n * num_samples + m) / (num_samples * num_samples) * 100)
                if percent_complete % 10 == 0 and percent_complete != last_displayed:
                    last_displayed = percent_complete
                    perc_done = int(num_percent_bins * percent_complete / 100)
                    perc_left = num_percent_bins - perc_done
                    percent_symbol1 = "." * perc_left
                    percent_symbol2 = "#" * perc_done
                    i = percent_symbol2 + percent_symbol1 + " " + str(percent_complete) + "% "
                    logger.info(f"\rPercent Complete:{i}")

                zone_letter = None
                if -80 <= latitude <= 84:
                    zone_letter = ZONE_LETTERS[int(latitude + 80) >> 3]

                zone_number = int((longitude + 180) / 6) + 1
                if 56 <= latitude < 64 and 3 <= longitude < 12:
                    zone_number = 32

                if 72 <= latitude <= 84 and longitude >= 0:
                    if longitude < 9:
                        zone_number = 31
                    elif longitude < 21:
                        zone_number = 33
                    elif longitude < 33:
                        zone_number = 35
                    elif longitude < 42:
                        zone_number = 37
                current_lat_lon = convert_utm_to_latlon(int(x), int(y), zone_number, zone_letter)
                all_lat_lon[n, m] = current_lat_lon
                all_utm[n, m] = [x, y]
        logger.info(str(100) + "% - Done")
        return all_data, all_lat_lon, all_utm


@pyaedt_function_handler()
def convert_latlon_to_utm(latitude: float, longitude: float, zone_letter: str = None, zone_number: int = None) -> tuple:
    """Convert latitude and longitude to UTM (Universal Transverse Mercator) coordinates.

    Parameters
    ----------
    latitude : float
        Latitude value in decimal degrees.
    longitude : float
        Longitude value in decimal degrees.
    zone_letter: str, optional
        UTM zone designators. The default is ``None``. The valid zone letters are ``"CDEFGHJKLMNPQRSTUVWXX"``
    zone_number: int, optional
        Global map numbers of a UTM zone numbers map. The default is ``None``.

    Notes
    -----
    .. [1] https://mapref.org/UTM-ProjectionSystem.html

    Returns
    -------
    tuple
        Tuple containing UTM East coordinate, North coordinate, zone letter, and zone number.
    """
    if latitude < -80.0 or latitude > 84.0:
        raise ValueError("Latitude out of range: must be between -80 degrees and 84 degrees.")
    if longitude < -180.0 or longitude > 180.0:
        raise ValueError("Longitude out of range: must be between -180 degrees and 180 degrees.")
    if zone_letter is not None and zone_letter.upper() not in ZONE_LETTERS:
        raise ValueError("Zone letter out of range.")

    # Constant values
    # Scale factor for UTM (Universal Transverse Mercator) projection
    K0 = 0.9996

    # Eccentricity of the Earth's ellipsoid
    E = 0.00669438
    E2 = E * E
    E3 = E2 * E
    E_P2 = E / (1.0 - E)

    SQRT_E = mathlib.sqrt(1 - E)
    _E = (1 - SQRT_E) / (1 + SQRT_E)
    _E2 = _E * _E
    _E3 = _E2 * _E

    # Meridional arc constants for UTM projection
    M1 = 1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256
    M2 = 3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024
    M3 = 15 * E2 / 256 + 45 * E3 / 1024
    M4 = 35 * E3 / 3072

    # Radius of the Earth in meters
    R = 6378137

    lat_rad = mathlib.radians(latitude)
    lon_rad = mathlib.radians(longitude)

    lat_sin = mathlib.sin(lat_rad)
    lat_cos = mathlib.cos(lat_rad)

    lat_tan = lat_sin / lat_cos
    lat_tan2 = lat_tan**2
    lat_tan4 = lat_tan2**2

    if zone_number is None:
        zone_number = int((longitude + 180) / 6) + 1
        if 56 <= latitude < 64 and 3 <= longitude < 12:
            zone_number = 32

        if 72 <= latitude <= 84 and longitude >= 0:
            if longitude < 9:
                zone_number = 31
            elif longitude < 21:
                zone_number = 33
            elif longitude < 33:
                zone_number = 35
            elif longitude < 42:
                zone_number = 37

    if zone_letter is None and -80 <= latitude <= 84:
        zone_letter = ZONE_LETTERS[int(latitude + 80) >> 3]

    central_lon_rad = mathlib.radians((zone_number - 1) * 6 - 180 + 3)

    n = R / mathlib.sqrt(1 - E * lat_sin**2)
    c = E_P2 * lat_cos**2

    a = lat_cos * ((lon_rad - central_lon_rad + mathlib.pi) % (2 * mathlib.pi) - mathlib.pi)
    a2, a3, a4, a5, a6 = a**2, a**3, a**4, a**5, a**6

    m = R * (
        M1 * lat_rad - M2 * mathlib.sin(2 * lat_rad) + M3 * mathlib.sin(4 * lat_rad) - M4 * mathlib.sin(6 * lat_rad)
    )

    easting = (
        K0 * n * (a + (a3 / 6) * (1 - lat_tan2 + c) + (a5 / 120) * (5 - 18 * lat_tan2 + lat_tan4 + 72 * c - 58 * E_P2))
        + 500000
    )

    northing = K0 * (
        m
        + n
        * lat_tan
        * (
            a2 / 2
            + (a4 / 24) * (5 - lat_tan2 + 9 * c + 4 * c**2)
            + (a6 / 720) * (61 - 58 * lat_tan2 + lat_tan4 + 600 * c - 330 * E_P2)
        )
    )

    if latitude < 0:
        # Southern hemisphere adjustment
        northing += 10000000

    return easting, northing, zone_letter, zone_number


@pyaedt_function_handler()
def convert_utm_to_latlon(
    east: int, north: float, zone_number: int, zone_letter: str = None, northern: bool = None
) -> tuple:
    """Convert UTM (Universal Transverse Mercator) coordinates to latitude and longitude.

    Parameters
    ----------
    east : int
        East value of UTM coordinates.
    north : int
        North value of UTM coordinates.
    zone_number: int, optional
        Global map numbers of a UTM zone numbers map.
    zone_letter: str, optional
        UTM zone designators. The default is ``None``. The valid zone letters are ``"CDEFGHJKLMNPQRSTUVWXX"``
    northern: bool, optional
        Indicates whether the UTM coordinates are in the Northern Hemisphere. If ``True``, the coordinates
        are treated as being north of the equator, if ``False``, they are treated as being south of the equator.
        The default is ``None`` in which case the method determines the hemisphere using ``zone_letter``.

    Notes
    -----
    .. [1] https://mapref.org/UTM-ProjectionSystem.html

    Returns
    -------
    tuple
        Tuple containing latitude and longitude.
    """
    if not zone_letter and northern is None:
        raise ValueError("Set either zone_letter or northern.")

    if zone_letter and northern is not None:
        raise ValueError("Set either zone_letter or north, but not both.")

    if zone_letter:
        zone_letter = zone_letter.upper()
        northern = zone_letter >= "N"

    x = east - 500000
    y = north

    if not northern:
        y -= 10000000

    # Constant values
    # Scale factor for UTM (Universal Transverse Mercator) projection
    K0 = 0.9996
    # Radius of the Earth in meters
    R = 6378137

    # Eccentricity of the Earth's ellipsoid
    E = 0.00669438
    E2 = E * E
    E3 = E2 * E
    E_P2 = E / (1.0 - E)

    SQRT_E = mathlib.sqrt(1 - E)
    _E = (1 - SQRT_E) / (1 + SQRT_E)
    _E2 = _E * _E
    _E3 = _E2 * _E
    _E4 = _E3 * _E
    _E5 = _E4 * _E

    # Meridional arc constants for UTM projection
    M1 = 1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256

    P2 = 3.0 / 2 * _E - 27.0 / 32 * _E3 + 269.0 / 512 * _E5
    P3 = 21.0 / 16 * _E2 - 55.0 / 32 * _E4
    P4 = 151.0 / 96 * _E3 - 417.0 / 128 * _E5
    P5 = 1097.0 / 512 * _E4

    m = y / K0
    mu = m / (R * M1)

    p_rad = (
        mu + P2 * mathlib.sin(2 * mu) + P3 * mathlib.sin(4 * mu) + P4 * mathlib.sin(6 * mu) + P5 * mathlib.sin(8 * mu)
    )

    p_sin = mathlib.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = mathlib.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = mathlib.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = E_P2 * p_cos**2
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (
        p_rad
        - (p_tan / r) * (d2 / 2 - d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2))
        + d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2)
    )

    longitude = (
        d - d3 / 6 * (1 + 2 * p_tan2 + c) + d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)
    ) / p_cos

    longitude_temp = longitude + mathlib.radians((zone_number - 1) * 6 - 180 + 3)
    longitude = (longitude_temp + mathlib.pi) % (2 * mathlib.pi) - mathlib.pi

    return mathlib.degrees(latitude), mathlib.degrees(longitude)
