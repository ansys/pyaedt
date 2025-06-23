# ruff: noqa: E402

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

from pathlib import Path
import warnings

from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available
from ansys.aedt.core.internal.checks import graphics_required
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler

# Check that graphics are available
try:
    check_graphics_available()

    import pyvista as pv

    from ansys.tools.visualization_interface import MeshObjectPlot
    from ansys.tools.visualization_interface import Plotter
    from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


class MeshLoader:
    """
    Class for loading and managing 3D mesh data into a Perceive EM radar simulation environment.

    This class handles reading mesh files, converting them into formats compatible with
    the Perceive EM API, and assigning visualization and simulation properties such as material indices
    and vertex normals. It also supports optional curved surface physics.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.perceive_em.core.api_interface.PerceiveEM`
        Reference to the application context, providing access to the simulation API,
        radar scenario, logger, and material manager.
    """

    def __init__(self, app):
        # Internal properties
        self.app = app
        self._rss = app.radar_sensor_scenario
        self._api = app.api
        self._material_manager = app.material_manager

        # Private properties
        self.__scene_element = None
        self.__mesh = None

        self._logger = app._logger
        self.color = "red"
        self.transparency = None

    @property
    def scene_element(self):
        """
        The internal Perceive EM scene element handle associated with the loaded mesh.

        This element is used by the simulation backend to reference and manage the mesh geometry
        in the radar sensor scenario.
        """
        return self.__scene_element

    @property
    def mesh(self):
        """
        The loaded mesh object used for visualization.

        Returns
        -------
        pyvista.PolyData


        """
        return self.__mesh

    def load_mesh(self, input_file=None, material_index=0, use_curved_physics=False):
        """
        Load a 3D mesh into the Perceive EM environment for visualization and simulation.

        Parameters
        ----------
        input_file : str or Path, optional
            Path to the STL or OBJ file to load. Must be a valid file path.
        material_index : int, optional
            Material index to apply to the mesh for simulation. Default is 0.
        use_curved_physics : bool, optional
            If True, attempts to enable curved surface physics using vertex normals.
            Only supported for certain formats. Default is False.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        h_mesh = None
        mesh = None
        if input_file is not None:
            input_file = Path(input_file)
            if input_file.is_file():
                # Load PyVista mesh which will be used for visualization
                mesh = pv.read(input_file)

                # Load stl or obj file, but ultimately we just need triangles
                perceive_mesh = self._load_triangles_mesh(input_file)
                triangles = perceive_mesh.triangles
                vertices = perceive_mesh.vertices

                # By default, the coating is 0. Setting the correct material coating
                perceive_mesh.coatings += material_index

                # If no vertices, the mesh was not imported correctly into the scene
                if vertices.shape[0] == 0:
                    self._logger.info(f"Mesh is empty: {input_file}")
                    return

                h_mesh = self.app.scene._add_scene_element()

                if not use_curved_physics or perceive_mesh is None:
                    self._set_triangles_mesh(h_mesh, vertices, triangles, material_index)
                    if use_curved_physics:
                        self._logger.warning(
                            "Using Curved Physics Failed, "
                            "check file type and support for surface normals (currently only obj and stl "
                            "supported)"
                        )
                else:
                    self._logger.info("Using curved physics")
                    # this is currently disabled, but we could enable it if we want to use the normals from cad
                    # file to include curvature extraction. cad file must have enormals
                    self._set_triangles_mesh(h_mesh, perceive_mesh)
                    self._set_curved_surface(True)
                    mesh = mesh.compute_normals()
                    normals = mesh.active_normals
                    self._set_vertex_normal(h_mesh, self._rss.VertexNormalFormat.BY_VERTEX_LIST)
            else:
                raise FileNotFoundError(f"File not found: {input_file}")

        self.__scene_element = h_mesh
        self.__mesh = mesh

        return True

    # Internal Perceive EM API objects
    @perceive_em_function_handler
    def _load_triangles_mesh(self, input_file):
        input_file = Path(input_file)
        return self._api.loadTriangleMesh(str(input_file))

    @perceive_em_function_handler
    def _set_triangles_mesh(self, element, vertices, triangles=None, material_index=0):
        return self._api.setTriangles(element, vertices, triangles, material_index)

    @perceive_em_function_handler
    def _set_curved_surface(self, enable=True):
        return self._api.setDoCurvedSurfPhysics(enable)

    @perceive_em_function_handler
    def _set_vertex_normal(self, element, normals):
        return self._api.setVertexNormals(element, self._rss.VertexNormalFormat.BY_VERTEX_LIST, normals)
