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
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.scene.coordinate_system import CoordinateSystem
from ansys.aedt.core.perceive_em.visualization.load_mesh import MeshLoader


class Actor:
    def __init__(
        self,
        app,
        parent_node=None,
        input_file=None,
        name="Actor",
    ):
        """
        Initialize an Actor instance.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.perceive_em.core.api_interface.PerceiveEM`
            The Perceive EM application instance.
        parent_node : SceneNode, optional
            The parent scene node to which this actor is attached.
        input_file : str or Path, optional
            Path to a JSON configuration file to initialize the actor.
        name : str, optional
            Name of the actor. The default is ``"Actor"``.
        """
        # Internal properties

        # Perceive EM API
        self._app = app
        self._api = app.api
        self._rss = app.radar_sensor_scenario
        self._logger = app._logger
        self._material_manager = app.material_manager

        # Private properties

        # Perceive EM objects
        self.__parent_node = parent_node
        self.__scene_node = None
        self.__scene_element = None

        # Actor properties
        self.__part_names = []
        self.__parts = {}
        self.__actor_type = "generic"
        # Bounds of actor with all its parts included
        self.__bounds = None
        self.__time = 0.0
        self.__configuration_file = None
        if input_file:
            self.__configuration_file = Path(input_file)

        # Pyvista mesh
        self._mesh = None
        self._mesh_properties = None
        self._pv_actor = None
        self._previous_transform = np.eye(4)

        # Perceive EM node
        # Create node
        self.__scene_node = self._app.scene._add_scene_node(self.parent_node)

        # SceneManager name. This is using Perceive EM API to set the Name of the node
        self.name = name

        # Coordinate System
        self.__coordinate_system = CoordinateSystem(self)

    @property
    @perceive_em_function_handler
    def name(self):
        """Actor name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.name
        """
        return self._api.name(self.scene_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.scene_node, value)

    @property
    def configuration_file(self):
        return self.__configuration_file

    @property
    def time(self):
        """Current simulation time of the actor.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.time
        """
        return self.__time

    @time.setter
    def time(self, value):
        self.__time = value

    @property
    @perceive_em_function_handler
    def parent_name(self):
        """Name of parent node.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.parent_name
        """
        if self.parent_node is not None:
            return self._api.name(self.parent_node)
        else:
            # The actor is part of the main scene
            return self._app.scene.name

    @property
    def parent_node(self):
        """Reference to the parent node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.parent_node
        """
        return self.__parent_node

    @property
    def scene_node(self):
        """The Perceive EM node associated with this actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__scene_node

    @property
    def scene_element(self):
        """The Perceive EM scene element representing this actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_element
        >>> actor.add_part(input_data=input_data)
        >>> actor.scene_element
        """
        return self.__scene_element

    @property
    def part_names(self):
        """Name of all parts associated with this actor.

        Returns
        -------
        list

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.part_names
        >>> actor.add_part(input_data=input_data)
        >>> actor.part_names
        """
        return self.__part_names

    @property
    def mesh(self):
        """Mesh of the actor.

        Returns
        -------
        :class:`pyvista.Polydata`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.mesh
        >>> actor.add_part(input_data=input_data)
        >>> actor.mesh
        """
        return self._mesh

    @property
    def mesh_properties(self):
        """Properties of the mesh.

        Returns
        -------
        dict

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.mesh_properties
        >>> actor.add_part(input_data=input_data)
        >>> actor.mesh_properties
        """
        return self._mesh_properties

    @property
    def parts(self):
        """Dictionary of parts associated with this actor.

        Returns
        -------
        dict

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.parts
        >>> actor.add_part(input_data=input_data)
        >>> actor.parts
        """
        return self.__parts

    @property
    def coordinate_system(self):
        """Coordinate system associated with the actor.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.coordinate_system.CoordinateSystem`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system
        """
        return self.__coordinate_system

    @property
    def bounds(self):
        """Bounding box of the actor including all parts.

        Returns
        -------
        list

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.bounds
        >>> actor.add_part(input_data=input_data)
        >>> actor.bounds
        """
        return self.__bounds

    @property
    def actor_type(self):
        """Type of the actor.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.actor_type
        """
        return self.__actor_type

    @actor_type.setter
    def actor_type(self, value):
        self.__actor_type = value

    def add_part(self, input_file, name=None, material=None, color=None, transparency=None):
        """
        Add a part to the actor.

        Parameters
        ----------
        input_file : str or :class:`pathlib.Path`
            Path to the mesh file to load for the part.
        name : str, optional
            Name of the part. If not provided, a unique name is generated.
        material : str, optional
            Name of the material. The default is to ``"pec"``.
        color : str, optional
            Color of the part. The default is ``"red"``.
        transparency : float, optional
            Transparency value between 0 (opaque) and 1 (fully transparent).

        Returns
        -------
        str
            Name assigned to the added part.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> part = actor.add_part(input_data)
        """
        # Random name of the part
        if name is None or name in self.part_names:
            name = generate_unique_name("part")
            while name in self.part_names:  # pragma: no cover
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
        part_actor._mesh = mesh_loader.mesh

        part_actor._mesh_properties = {"color": mesh_loader.color, "transparency": mesh_loader.transparency}

        # Add element mesh to node
        self._app.scene._set_scene_element(part_actor.scene_node, part_actor.scene_element)

        if hasattr(mesh_loader.mesh, "bounds"):
            self.__update_actor_bounds(mesh_loader.mesh.bounds)

        self.__part_names.append(name)
        self.__parts[name] = part_actor
        return name

    def add_parts_from_json(self, input_file):
        """
        Add multiple parts to the actor from a JSON configuration file.

        Parameters
        ----------
        input_file : str or :class:`pathlib.Path`
            Path to the JSON file containing part definitions.

        Returns
        -------
        dict
            Dictionary loaded from the JSON file describing the parts.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> configuration_file = "configuration.json"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> parts = actor.add_parts_from_json(configuration_file)
        """
        input_file = Path(input_file)
        input_dir = input_file.parent

        actor_dict = read_json(input_file)

        for part_name, part_dict in actor_dict["parts"].items():
            if "file_name" not in part_dict:
                raise Exception(f"Part {part_name} has no file_name.")

            geometry_file = part_dict["file_name"]

            input_file = input_dir / geometry_file

            if not input_file.is_file():  # pragma: no cover
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

    def update(self, time=0.0):
        """
        Update parts.

        Parameters
        ----------
        time : float, optional
            SceneManager time.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.time = time

        self.coordinate_system.update(time=self.time)

        return True

    def __update_actor_bounds(self, part_bounds):
        """
        Update the overall bounding box of the actor with a new part.

        Parameters
        ----------
        part_bounds : list
            List of six float values representing the bounding box of the part.
        """
        if part_bounds is None:
            return
        if self.bounds is None:
            self.__bounds = part_bounds
        else:
            self.__bounds = [
                min(self.bounds[i], part_bounds[i]) if i % 2 == 0 else max(self.bounds[i], part_bounds[i])
                for i in range(6)
            ]
