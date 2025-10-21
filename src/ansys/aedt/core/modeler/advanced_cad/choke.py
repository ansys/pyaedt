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

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
import shutil
import tempfile
from typing import Any
from typing import Dict

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import write_configuration_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

CHOKE_DEFAULT_PARAMETERS = {
    "Number of Windings": {
        "1": True,
        "2": False,
        "3": False,
        "4": False,
    },
    "Layer": {"Simple": True, "Double": False, "Triple": False},
    "Layer Type": {"Separate": True, "Linked": False},
    "Similar Layer": {"Similar": True, "Different": False},
    "Mode": {"Differential": True, "Common": False},
    "Wire Section": {
        "None": False,
        "Hexagon": False,
        "Octagon": False,
        "Circle": True,
    },
    "Core": {
        "Name": "Core",
        "Material": "ferrite",
        "Inner Radius": 20,
        "Outer Radius": 30,
        "Height": 10,
        "Chamfer": 0.8,
    },
    "Outer Winding": {
        "Name": "Winding",
        "Material": "copper",
        "Inner Radius": 20,
        "Outer Radius": 30,
        "Height": 10,
        "Wire Diameter": 1.5,
        "Turns": 20,
        "Coil Pit(deg)": 0.1,
        "Occupation(%)": 0,
    },
    "Mid Winding": {
        "Turns": 25,
        "Coil Pit(deg)": 0.1,
        "Occupation(%)": 0,
    },
    "Inner Winding": {
        "Turns": 4,
        "Coil Pit(deg)": 0.1,
        "Occupation(%)": 0,
    },
    "Settings": {"Units": "mm"},
    "Create Component": {"True": True, "False": False},
}


@dataclass
class Choke(PyAedtBase):
    """Class to create chokes in AEDT.

    Parameters
    ----------
    name : str, optional
        Name of the choke. The default is ``"Choke"``.
    number_of_windings : Dict[str, bool], optional
        Number of windings configuration.
    layer : Dict[str, bool], optional
        Layer configuration.
    layer_type : Dict[str, bool], optional
        Layer type configuration.
    similar_layer : Dict[str, bool], optional
        Similar layer configuration.
    mode : Dict[str, bool], optional
        Mode configuration.
    wire_section : Dict[str, bool], optional
        Wire section configuration.
    core : Dict[str, Any], optional
        Core configuration.
    outer_winding : Dict[str, Any], optional
        Outer winding configuration.
    mid_winding : Dict[str, Any], optional
        Mid winding configuration.
    inner_winding : Dict[str, Any], optional
        Inner winding configuration.
    settings : Dict[str, Any], optional
        Settings configuration.
    create_component : Dict[str, bool], optional
        Create component configuration.

    Examples
    --------
    Create a basic choke with default parameters:

    >>> from ansys.aedt.core.modeler.advanced_cad.choke import Choke
    >>> choke = Choke()
    >>> choke.name = "my_choke"

    Create a choke with custom core dimensions:

    >>> choke = Choke()
    >>> choke.core["Inner Radius"] = 15
    >>> choke.core["Outer Radius"] = 25
    >>> choke.core["Height"] = 12
    >>> choke.core["Material"] = "ferrite"

    Create a choke with custom winding configuration:

    >>> choke = Choke()
    >>> choke.outer_winding["Wire Diameter"] = 2.0
    >>> choke.outer_winding["Turns"] = 30
    >>> choke.outer_winding["Material"] = "copper"

    Configure number of windings:

    >>> choke = Choke()
    >>> # Set to 2 windings
    >>> choke.number_of_windings = {"1": False, "2": True, "3": False, "4": False}

    Set wire section type:

    >>> choke = Choke()
    >>> # Use hexagonal wire section
    >>> choke.wire_section = {"None": False, "Hexagon": True, "Octagon": False, "Circle": False}

    Create choke in HFSS application:

    >>> import ansys.aedt.core as pyaedt
    >>> hfss = pyaedt.Hfss()
    >>> choke = Choke()
    >>> objects = choke.create_choke(app=hfss)
    >>> ground = choke.create_ground(app=hfss)
    >>> mesh = choke.create_mesh(app=hfss)
    >>> ports = choke.create_ports(ground, app=hfss)

    Load choke configuration from JSON file:

    >>> from ansys.aedt.core.generic.file_utils import read_json
    >>> config_data = read_json("choke_config.json")
    >>> choke = Choke.from_dict(config_data)

    Export choke configuration to JSON file:

    >>> choke = Choke()
    >>> choke.export_to_json("my_choke_config.json")

    Create a differential mode choke:

    >>> choke = Choke()
    >>> choke.mode = {"Differential": True, "Common": False}
    >>> choke.layer_type = {"Separate": True, "Linked": False}

    Create a triple layer choke:

    >>> choke = Choke()
    >>> choke.layer = {"Simple": False, "Double": False, "Triple": True}
    >>> choke.inner_winding["Turns"] = 10
    >>> choke.mid_winding["Turns"] = 15
    >>> choke.outer_winding["Turns"] = 20
    """

    name: str = "choke"
    number_of_windings: Dict[str, bool] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Number of Windings"])
    layer: Dict[str, bool] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Layer"])
    layer_type: Dict[str, bool] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Layer Type"])
    similar_layer: Dict[str, bool] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Similar Layer"])
    mode: Dict[str, bool] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Mode"])
    wire_section: Dict[str, bool] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Wire Section"])
    core: Dict[str, Any] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Core"])
    outer_winding: Dict[str, Any] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Outer Winding"])
    mid_winding: Dict[str, Any] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Mid Winding"])
    inner_winding: Dict[str, Any] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Inner Winding"])
    settings: Dict[str, Any] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Settings"])
    create_component: Dict[str, bool] = field(default_factory=lambda: CHOKE_DEFAULT_PARAMETERS["Create Component"])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Choke":
        """Create a Choke instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing choke configuration data.

        Returns
        -------
        Choke
            Choke instance created from the dictionary.
        """
        return cls(
            number_of_windings=data["Number of Windings"],
            layer=data["Layer"],
            layer_type=data["Layer Type"],
            similar_layer=data["Similar Layer"],
            mode=data["Mode"],
            wire_section=data["Wire Section"],
            core=data["Core"],
            outer_winding=data["Outer Winding"],
            mid_winding=data["Mid Winding"],
            inner_winding=data["Inner Winding"],
            settings=data["Settings"],
            create_component=data["Create Component"],
        )

    @property
    def choke_parameters(self) -> dict:
        """Get the choke parameters as a dictionary

        Returns
        -------
        dict
            Dictionary of choke parameters.
        """
        return {
            "Number of Windings": self.number_of_windings,
            "Layer": self.layer,
            "Layer Type": self.layer_type,
            "Similar Layer": self.similar_layer,
            "Mode": self.mode,
            "Wire Section": self.wire_section,
            "Core": self.core,
            "Outer Winding": self.outer_winding,
            "Mid Winding": self.mid_winding,
            "Inner Winding": self.inner_winding,
            "Settings": self.settings,
            "Create Component": self.create_component,
        }

    def export_to_json(self, file_path: str) -> bool:
        """Export choke configuration to JSON file.

        Parameters
        ----------
        file_path : str
            Path to the JSON file to save the configuration.

        Returns
        -------
        bool
            True if export was successful, False otherwise.

        Raises
        ------
        Exception
            If there's an error during file writing.
        """
        try:
            write_configuration_file(self.choke_parameters, file_path)
            return True
        except Exception as e:
            raise Exception(f"Failed to export configuration: {str(e)}")

    @pyaedt_function_handler()
    def create_choke(self, app=None):
        """Create a choke.

        Returns
        -------
        list
            List of objects created.
        """
        # Create temporary directory for JSON file
        temp_dir = Path(tempfile.mkdtemp())
        json_path = temp_dir / "choke_params.json"
        write_configuration_file(self.choke_parameters, str(json_path))
        # Verify parameters
        _ = app.modeler.check_choke_values(str(json_path), create_another_file=False)
        # Create choke geometry
        list_object = app.modeler.create_choke(str(json_path))
        shutil.rmtree(temp_dir, ignore_errors=True)
        self.list_object = list_object
        return list_object

    @pyaedt_function_handler()
    def create_ground(self, app):
        """Create the ground plane.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.cad.object3d.Object3d`
            Ground object.
        """
        first_winding_list = self.list_object[2]
        ground_radius = 1.2 * self.outer_winding["Outer Radius"]
        ground_position = [0, 0, first_winding_list[1][0][2] - 2]
        ground = app.modeler.create_circle(
            "XY",
            ground_position,
            ground_radius,
            name="GND",
            material="copper",
        )
        app.assign_finite_conductivity(ground.name, is_infinite_ground=True)
        ground.transparency = 0.9
        return ground

    @pyaedt_function_handler()
    def create_mesh(self, app):
        """Create the mesh.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh_helpers.MeshOperation`
            Mesh operation object.
        """
        first_winding_list = self.list_object[2]
        ground_radius = 1.2 * self.outer_winding["Outer Radius"]
        cylinder_height = 2.5 * self.outer_winding["Height"]
        cylinder_position = [0, 0, first_winding_list[1][0][2] - 4]
        mesh_operation_cylinder = app.modeler.create_cylinder(
            "XY",
            cylinder_position,
            ground_radius,
            cylinder_height,
            num_sides=36,
            name="mesh_cylinder",
        )
        mesh = app.mesh.assign_length_mesh(
            [mesh_operation_cylinder],
            maximum_length=15,
            maximum_elements=None,
            name="choke_mesh",
        )
        return mesh

    @pyaedt_function_handler()
    def create_ports(self, ground, app):
        """Create the ports.

        Parameters
        ----------
        ground : :class:`ansys.aedt.core.modeler.cad.object3d`
            Ground object.

        Returns
        -------
        list
            List of ports.
        """
        first_winding_list = self.list_object[2]
        second_winding_list = self.list_object[3] if len(self.list_object) > 3 else None
        port_position_list = [
            [
                first_winding_list[1][0][0],
                first_winding_list[1][0][1],
                first_winding_list[1][0][2] - 1,
            ],
            [
                first_winding_list[1][-1][0],
                first_winding_list[1][-1][1],
                first_winding_list[1][-1][2] - 1,
            ],
        ]
        if second_winding_list:  # pragma: no cover
            port_position_list.extend(
                [
                    [
                        second_winding_list[1][0][0],
                        second_winding_list[1][0][1],
                        second_winding_list[1][0][2] - 1,
                    ],
                    [
                        second_winding_list[1][-1][0],
                        second_winding_list[1][-1][1],
                        second_winding_list[1][-1][2] - 1,
                    ],
                ]
            )
        wire_diameter = self.outer_winding["Wire Diameter"]
        port_dimension_list = [2, wire_diameter]
        ports = []
        for i, position in enumerate(port_position_list):
            sheet = app.modeler.create_rectangle(
                "XZ",
                position,
                port_dimension_list,
                name=f"sheet_port_{i + 1}",
            )
            sheet.move([-wire_diameter / 2, 0, -1])
            port = app.lumped_port(
                assignment=sheet.name,
                name=f"port_{i + 1}",
                reference=[ground],
            )
            ports.append(port)
        return ports
