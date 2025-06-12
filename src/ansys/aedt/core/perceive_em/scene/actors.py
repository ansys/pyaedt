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

import numpy as np

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.perceive_em.scene.coordinate_system import CoordinateSystem
from ansys.aedt.core.perceive_em.visualization.load_mesh import MeshLoader


class Actor:
    def __init__(
        self,
        app,
        parent_node,
        name="Actor",
    ):
        """Initialize an Actor instance."""
        # Internal properties
        self._app = app
        self._material_manager = app.material_manager

        # Private properties
        self.__name = name
        self.__parent_node = parent_node
        self.__part_names = []
        self.__parts = {}
        self.__bounds = None
        self.__mesh = None
        self.__scene_element = None
        self.__mesh_properties = None
        self.__actor_type = "default"

        # Transform
        self._pv_actor = None
        self._previous_transform = np.eye(4)

        # Perceive EM scene
        h_node = self._app.radar_sensor_scenario.SceneNode()
        if self.parent_node is None:
            self._app.api.addSceneNode(h_node)
        else:
            self._app.api.addSceneNode(h_node, self.parent_node)
        self.__scene_node = h_node

        # Coordinate System
        self.__coordinate_system = CoordinateSystem(self)

    @property
    def name(self):
        return self.__name

    @property
    def parent_node(self):
        return self.__parent_node

    @property
    def scene_node(self):
        return self.__scene_node

    @property
    def scene_element(self):
        return self.__scene_element

    @property
    def mesh_properties(self):
        return self.__mesh_properties

    @property
    def part_names(self):
        return self.__part_names

    @property
    def mesh(self):
        return self.__mesh

    @property
    def parts(self):
        return self.__parts

    @property
    def coordinate_system(self):
        return self.__coordinate_system

    @property
    def bounds(self):
        return self.__bounds

    @property
    def actor_type(self):
        return self.__actor_type

    def add_part(self, input_file=None, name=None, material=None, color=None, transparency=None):
        """
        Add a part to the actor.

        Parameters:
        ------------
        actor : Actor instance
            The actor to be added as a co-parent.
        """
        # Random name of the part
        if name is None:
            name = generate_unique_name("part")

        # Default material is PEC
        if material is None:
            material = "pec"

        # Material must be loaded into _api
        if material not in self._material_manager.material_names:
            self._material_manager.load_material(material)

        if material.lower() == "pec":
            material_index = 0
        else:
            material_index = self._material_manager.materials[material].coating_idx

        if not color:
            color = "red"

        # Part actor
        part_actor = Actor(app=self._app, parent_node=self.scene_node, name=name)

        # Mesh loader object to create the mesh in pyvista and add the part into the scene
        mesh_loader = MeshLoader(self._app)
        mesh_loader.color = color
        mesh_loader.transparency = transparency
        mesh_loader.load_mesh(input_file=input_file, material_index=material_index)

        part_actor.__scene_element = mesh_loader.scene_element
        part_actor.__mesh = mesh_loader.mesh

        part_actor.__mesh_properties = {"color": mesh_loader.color, "transparency": mesh_loader.transparency}

        # Add element mesh to node
        self._app.api.setSceneElement(part_actor.scene_node, part_actor.scene_element)

        if hasattr(mesh_loader.mesh, "bounds"):
            self.__update_actor_bounds(mesh_loader.mesh.bounds)

        self.__part_names.append(name)
        self.__parts[name] = part_actor
        return name

    def add_parts_from_json(self, input_file):
        input_file = Path(input_file)
        input_dir = input_file.parent

        actor_dict = read_json(input_file)

        for part_name, part_dict in actor_dict["parts"].items():
            if "file_name" not in part_dict:
                raise Exception(f"Part {part_name} has no file_name.")

            geometry_file = part_dict["file_name"]

            input_file = input_dir / geometry_file

            if not input_file.is_file():
                raise FileExistsError(f"{input_file} does not exist.")

            material = "pec"
            if "properties" in part_dict and "material" in part_dict["properties"]:
                material = part_dict["properties"]["material"]

            color = None
            if "properties" in part_dict and "color" in part_dict["properties"]:
                color = part_dict["properties"]["color"]

            transparency = None
            if "properties" in part_dict and "transparency" in part_dict["properties"]:
                transparency = part_dict["properties"]["transparency"]

            self.add_part(
                input_file=input_file, name=part_name, material=material, color=color, transparency=transparency
            )
        return actor_dict

    def __update_actor_bounds(self, part_bounds):
        if part_bounds is None:
            return
        if self.bounds is None:
            self.__bounds = part_bounds
        else:
            self.__bounds = [
                min(self.bounds[i], part_bounds[i]) if i % 2 == 0 else max(self.bounds[i], part_bounds[i])
                for i in range(6)
            ]
