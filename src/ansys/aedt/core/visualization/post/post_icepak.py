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

"""
This module contains the `PostProcessor` class.

It contains all advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.
"""

import ast
import csv
import os
import re
from typing import Literal
from typing import Optional
from typing import Tuple

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import decompose_variable_value
from ansys.aedt.core.internal.checks import min_aedt_version
from ansys.aedt.core.visualization.post.field_summary import TOTAL_QUANTITIES
from ansys.aedt.core.visualization.post.field_summary import FieldSummary
from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D


class PostProcessorIcepak(PostProcessor3D, PyAedtBase):
    """Manages the specific Icepak postprocessing functions.

    .. note::
       Some functionalities are available only when AEDT is running in the graphical mode.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.application.analysis_3d.FieldAnalysis3D`
        Inherited parent object. The parent object must provide the members
        `_modeler`, `_desktop`, `_odesign`, and `logger`.

    """

    def __init__(self, app):
        PostProcessor3D.__init__(self, app)

    @pyaedt_function_handler()
    def create_field_summary(self):
        """
        Create field summary object.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.field_summary.FieldSummary`

        """
        return FieldSummary(self._app)

    @pyaedt_function_handler(timestep="time_step", design_variation="variation")
    def get_fans_operating_point(self, export_file=None, setup_name=None, time_step=None, variation=None):
        """Get the operating point of the fans in the design.

        Parameters
        ----------
        export_file : str, optional
            Name of the file to save the operating point of the fans to. The default is
            ``None``, in which case the filename is automatically generated.
        setup_name : str, optional
            Setup name to determine the operating point of the fans. The default is
            ``None``, in which case the first available setup is used.
        time_step : str, optional
            Time, with units, at which to determine the operating point of the fans. The default
            is ``None``, in which case the first available timestep is used. This parameter is
            only relevant in transient simulations.
        variation : str, optional
            Design variation to determine the operating point of the fans from. The default is
            ``None``, in which case the nominal variation is used.

        Returns
        -------
        list
            First element of the list is the CSV filename. The second and third elements
            are the quantities with units describing the operating point of the fans.
            The fourth element is a dictionary with the names of the fan instances
            as keys and lists with volumetric flow rates and pressure rise floats associated
            with the operating point as values.

        References
        ----------
        >>> oModule.ExportFanOperatingPoint

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> ipk = Icepak()
        >>> ipk.create_fan()
        >>> filename, vol_flow_name, p_rise_name, op_dict = ipk.get_fans_operating_point()
        """
        if export_file is None:
            path = self._app.temp_directory
            base_name = f"{self._app.project_name}_{self._app.design_name}_FanOpPoint"
            export_file = os.path.join(path, base_name + ".csv")
            while os.path.exists(export_file):
                file_name = generate_unique_name(base_name)
                export_file = os.path.join(path, file_name + ".csv")
        if setup_name is None:
            setup_name = f"{self._app.get_setups()[0]} : {self._app.solution_type}"
        if time_step is None:
            time_step = ""
            if self._app.solution_type == "Transient":
                self._app.logger.warning("No timestep is specified. First timestep is exported.")
        else:
            if not self._app.solution_type == "Transient":
                self._app.logger.warning("Simulation is steady-state. Timestep argument is ignored.")
                time_step = ""
        if variation is None:
            variation = ""
        self._app.osolution.ExportFanOperatingPoint(
            [
                "SolutionName:=",
                setup_name,
                "DesignVariationKey:=",
                variation,
                "ExportFilePath:=",
                export_file,
                "Overwrite:=",
                True,
                "TimeStep:=",
                time_step,
            ]
        )
        with open_file(export_file, "r") as f:
            reader = csv.reader(f)
            for line in reader:
                if "Fan Instances" in line:
                    vol_flow = line[1]
                    p_rise = line[2]
                    break
            var = {line[0]: [float(line[1]), float(line[2])] for line in reader}
        return [export_file, vol_flow, p_rise, var]

    @pyaedt_function_handler
    def _parse_field_summary_content(self, fs, setup_name, design_variation, quantity_name):
        content = fs.get_field_summary_data(setup=setup_name, variation=design_variation)
        pattern = r"\[([^]]*)\]"
        match = re.search(pattern, content["Quantity"][0])
        if match:
            content["Unit"] = [match.group(1)]
        else:  # pragma: no cover
            content["Unit"] = [None]

        if quantity_name in TOTAL_QUANTITIES:
            return {i: content[i][0] for i in ["Total", "Unit"]}
        return {i: content[i][0] for i in ["Min", "Max", "Mean", "Stdev", "Unit"]}

    @pyaedt_function_handler(faces_list="faces", quantity_name="quantity", design_variation="variation")
    def evaluate_faces_quantity(
        self, faces, quantity, side="Default", setup_name=None, variations=None, ref_temperature="", time="0s"
    ):
        """Export the field surface output.

        Parameters
        ----------
        faces : list
            List of faces to apply.
        quantity : str
            Name of the quantity to export.
        side : str, optional
            Which side of the mesh face to use. The default is ``Default``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature : str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.
        time : str, optional
            Timestep to get the data from. Default is ``"0s"``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:

            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------
        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        facelist_name = generate_unique_name(quantity)
        self._app.modeler.create_face_list(faces, facelist_name)
        fs = self.create_field_summary()
        fs.add_calculation(
            "Object", "Surface", facelist_name, quantity, side=side, ref_temperature=ref_temperature, time=time
        )
        out = self._parse_field_summary_content(fs, setup_name, variations, quantity)
        self._app.oeditor.Delete(["NAME:Selections", "Selections:=", facelist_name])
        return out

    @pyaedt_function_handler(boundary_name="boundary", quantity_name="quantity", design_variation="variations")
    def evaluate_boundary_quantity(
        self,
        boundary,
        quantity,
        side="Default",
        volume=False,
        setup_name=None,
        variations=None,
        ref_temperature="",
        time="0s",
    ):
        """Export the field output on a boundary.

        Parameters
        ----------
        boundary : str
            Name of boundary to perform the computation on.
        quantity : str
            Name of the quantity to export.
        side : str, optional
            Side of the mesh face to use. The default is ``"Default"``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        volume : bool, optional
            Whether to compute the quantity on the volume or on the surface.
            The default is ``False``, in which case the quantity will be evaluated
            only on the surface .
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature : str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.
        time : str, optional
            Timestep to get the data from. Default is ``"0s"``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:
            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------
        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        fs = self.create_field_summary()
        fs.add_calculation(
            "Boundary",
            ["Surface", "Volume"][int(volume)],
            boundary,
            quantity,
            side=side,
            ref_temperature=ref_temperature,
            time=time,
        )
        return self._parse_field_summary_content(fs, setup_name, variations, quantity)

    @pyaedt_function_handler(monitor_name="monitor", quantity_name="quantity", design_variation="variations")
    @min_aedt_version("2024.1")
    def evaluate_monitor_quantity(
        self, monitor, quantity, side="Default", setup_name=None, variations=None, ref_temperature="", time="0s"
    ):
        """Export monitor field output.

        Parameters
        ----------
        monitor : str
            Name of monitor to perform the computation on.
        quantity : str
            Name of the quantity to export.
        side : str, optional
            Side of the mesh face to use. The default is ``"Default"``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature : str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.
        time : str, optional
            Timestep to get the data from. Default is ``"0s"``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:

            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------
        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        if self._app.monitor.face_monitors.get(monitor, None):
            field_type = "Surface"
        elif self._app.monitor.point_monitors.get(monitor, None):
            field_type = "Volume"
        else:
            raise AttributeError(f"Monitor {monitor} is not found in the design.")
        fs = self.create_field_summary()
        fs.add_calculation(
            "Monitor", field_type, monitor, quantity, side=side, ref_temperature=ref_temperature, time=time
        )
        return self._parse_field_summary_content(fs, setup_name, variations, quantity)

    @pyaedt_function_handler(design_variation="variations")
    def evaluate_object_quantity(
        self,
        object_name,
        quantity_name,
        side="Default",
        volume=False,
        setup_name=None,
        variations=None,
        ref_temperature="",
        time="0s",
    ):
        """Export the field output on or in an object.

        Parameters
        ----------
        object_name : str
            Name of object to perform the computation on.
        quantity_name : str
            Name of the quantity to export.
        side : str, optional
            Side of the mesh face to use. The default is ``"Default"``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        volume : bool, optional
            Whether to compute the quantity on the volume or on the surface. The default is ``False``.
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature : str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.
        time : str, optional
            Timestep to get the data from. Default is ``"0s"``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:

            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------
        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        fs = self.create_field_summary()
        fs.add_calculation(
            "Object",
            ["Surface", "Volume"][int(volume)],
            object_name,
            quantity_name,
            side=side,
            ref_temperature=ref_temperature,
            time=time,
        )
        return self._parse_field_summary_content(fs, setup_name, variations, quantity_name)

    def get_temperature_extremum(
        self,
        assignment: str,
        max_min: Literal["Max", "Min"],
        location: Literal["Surface", "Volume"],
        setup: Optional[str] = None,
        time: Optional[str] = None,
    ) -> Tuple[Tuple[float, float, float], float]:
        """Calculate the position and value of the temperature maximum or minimum.

        Parameters
        ----------
            assignment : str
                The name of the object to calculate the temperature extremum for.
            max_min : Literal["Max", "Min"]
                "Max" for maximum, "Min" for minimum.
            location : Literal["Surface", "Volume"]
                "Surface" for surface, "Volume" for volume.
            time : Optional[str]
                Time at which to retrieve results if setup is transient. Default is `None`.
            setup : Optional[str]
                The name of the setup to use. If `None`, the first available setup is used. Default is `None`.

        Returns
        -------
            Tuple[Tuple[float, float, float], float]
            A tuple containing:

              - A tuple of three floats representing the (x, y, z) coordinates of the maximum point.
              - A float representing the value associated with the maximum point.
        """
        return self.get_field_extremum(assignment, max_min, location, "Temp", setup, {"Time": time})

    @pyaedt_function_handler()
    def power_budget(self, units="W", temperature=22, output_type="component"):
        """Power budget calculation.

        Parameters
        ----------
        units : str, optional
            Output power units. The default is ``"W"``.
        temperature : float, optional
            Temperature to calculate the power. The default is ``22``.
        output_type : str, optional
            Output data presentation. The default is ``"component"``.
            The options are ``"component"``, or ``"boundary"``.
            ``"component"`` returns the power based on each component.
            ``"boundary"`` returns the power based on each boundary.

        Returns
        -------
        dict, float
            Dictionary with the power introduced on each boundary and total power.

        References
        ----------
        >>> oEditor.ChangeProperty
        """
        available_bcs = self._app.boundaries
        power_dict = {}
        power_dict_obj = {}
        group_hierarchy = {}

        groups = list(self._app.oeditor.GetChildNames("Groups"))
        self._app.modeler.add_new_user_defined_component()
        for g in groups:
            g1 = self._app.oeditor.GetChildObject(g)
            if g1:
                group_hierarchy[g] = list(g1.GetChildNames())

        def multiplier_from_dataset(expression, valuein):
            multiplier = 0
            if expression in self._app.design_datasets:
                dataset = self._app.design_datasets[expression]
            elif expression in self._app.project_datasets:
                dataset = self._app.design_datasets[expression]
            else:
                return multiplier
            if valuein >= max(dataset.x):
                multiplier = dataset.y[-1]
            elif valuein <= min(dataset.x):
                multiplier = dataset.y[0]
            else:
                start_x = 0
                start_y = 0
                end_x = 0
                end_y = 0
                for i, y in enumerate(dataset.x):
                    if y > valuein:
                        start_x = dataset.x[i - 1]
                        start_y = dataset.y[i - 1]
                        end_x = dataset.x[i]
                        end_y = dataset.y[i]
                if end_x - start_x == 0:
                    multiplier = 0
                else:
                    multiplier = start_y + (valuein - start_x) * ((end_y - start_y) / (end_x - start_x))
            return multiplier

        def extract_dataset_info(boundary_obj, units_input="W", boundary="Power"):
            if boundary == "Power":
                prop = "Total Power Variation Data"
            else:
                prop = "Surface Heat Variation Data"
                units_input = "irrad_W_per_m2"
            value_bound = ast.literal_eval(boundary_obj.props[prop]["Variation Value"])[0]
            expression = ast.literal_eval(boundary_obj.props[prop]["Variation Value"])[1]
            value = list(decompose_variable_value(value_bound))
            if isinstance(value[0], str):
                new_value = self._app[value[0]]
                value = list(decompose_variable_value(new_value))
            value = unit_converter(
                value[0],
                unit_system=boundary,
                input_units=value[1],
                output_units=units_input,
            )
            expression = expression.split(",")[0].split("(")[1]
            return value, expression

        if not available_bcs:
            self.logger.warning("No boundaries defined")
            return True
        for bc_obj in available_bcs:
            if bc_obj.type == "Solid Block" or bc_obj.type == "Block":
                n = len(bc_obj.props["Objects"])
                if "Total Power Variation Data" not in bc_obj.props:
                    mult = 1
                    power_value = list(decompose_variable_value(bc_obj.props["Total Power"]))
                    power_value = unit_converter(
                        power_value[0], unit_system="Power", input_units=power_value[1], output_units=units
                    )

                else:
                    power_value, exp = extract_dataset_info(bc_obj, units_input=units, boundary="Power")
                    mult = multiplier_from_dataset(exp, temperature)

                for objs in bc_obj.props["Objects"]:
                    obj_name = self._app.modeler[objs].name
                    power_dict_obj[obj_name] = power_value * mult

                power_dict[bc_obj.name] = power_value * n * mult

            elif bc_obj.type == "SourceIcepak":
                if bc_obj.props["Thermal Condition"] == "Total Power":
                    n = 0
                    if "Faces" in bc_obj.props:
                        n += len(bc_obj.props["Faces"])
                    elif "Objects" in bc_obj.props:
                        n += len(bc_obj.props["Objects"])

                    if "Total Power Variation Data" not in bc_obj.props:
                        mult = 1
                        power_value = list(decompose_variable_value(bc_obj.props["Total Power"]))
                        power_value = unit_converter(
                            power_value[0], unit_system="Power", input_units=power_value[1], output_units=units
                        )
                    else:
                        power_value, exp = extract_dataset_info(bc_obj, units_input=units, boundary="Power")
                        mult = multiplier_from_dataset(exp, temperature)

                    if "Objects" in bc_obj.props:
                        for objs in bc_obj.props["Objects"]:
                            obj_name = self._app.modeler[objs].name
                            power_dict_obj[obj_name] = power_value * mult

                    elif "Faces" in bc_obj.props:
                        for facs in bc_obj.props["Faces"]:
                            obj_name = self._app.modeler.oeditor.GetObjectNameByFaceID(facs) + "_FaceID" + str(facs)
                            power_dict_obj[obj_name] = power_value * mult

                    power_dict[bc_obj.name] = power_value * n * mult

                elif bc_obj.props["Thermal Condition"] == "Surface Flux":
                    if "Surface Heat Variation Data" not in bc_obj.props:
                        mult = 1
                        heat_value = list(decompose_variable_value(bc_obj.props["Surface Heat"]))
                        if isinstance(heat_value[0], str):
                            new_value = self._app[heat_value[0]]
                            heat_value = list(decompose_variable_value(new_value))
                        heat_value = unit_converter(
                            heat_value[0],
                            unit_system="SurfaceHeat",
                            input_units=heat_value[1],
                            output_units="irrad_W_per_m2",
                        )
                    else:
                        mult = 1
                        if bc_obj.props["Surface Heat Variation Data"]["Variation Type"] == "Temp Dep":
                            heat_value, exp = extract_dataset_info(bc_obj, boundary="SurfaceHeat")
                            mult = multiplier_from_dataset(exp, temperature)
                        else:
                            heat_value = 0

                    power_value = 0.0
                    if "Faces" in bc_obj.props:
                        for component in bc_obj.props["Faces"]:
                            area = self._app.modeler.get_face_area(component)
                            area = unit_converter(
                                area,
                                unit_system="Area",
                                input_units=self._app.modeler.model_units + "2",
                                output_units="m2",
                            )
                            power_value += heat_value * area * mult
                    elif "Objects" in bc_obj.props:
                        for component in bc_obj.props["Objects"]:
                            object_assigned = self._app.modeler[component]
                            for f in object_assigned.faces:
                                area = unit_converter(
                                    f.area,
                                    unit_system="Area",
                                    input_units=self._app.modeler.model_units + "2",
                                    output_units="m2",
                                )
                                power_value += heat_value * area * mult

                    power_value = unit_converter(power_value, unit_system="Power", input_units="W", output_units=units)

                    if "Objects" in bc_obj.props:
                        for objs in bc_obj.props["Objects"]:
                            obj_name = self._app.modeler[objs].name
                            power_dict_obj[obj_name] = power_value

                    elif "Faces" in bc_obj.props:
                        for facs in bc_obj.props["Faces"]:
                            obj_name = self._app.modeler.oeditor.GetObjectNameByFaceID(facs) + "_FaceID" + str(facs)
                            power_dict_obj[obj_name] = power_value

                    power_dict[bc_obj.name] = power_value

            elif bc_obj.type == "Network":
                nodes = bc_obj.props["Nodes"]
                power_value = 0
                for node in nodes:
                    if "Power" in nodes[node]:
                        value = nodes[node]["Power"]
                        value = list(decompose_variable_value(value))
                        value = unit_converter(value[0], unit_system="Power", input_units=value[1], output_units=units)
                        power_value += value

                obj_name = self._app.modeler.oeditor.GetObjectNameByFaceID(bc_obj.props["Faces"][0])
                for facs in bc_obj.props["Faces"]:
                    obj_name += "_FaceID" + str(facs)
                power_dict_obj[obj_name] = power_value

                power_dict[bc_obj.name] = power_value

            elif bc_obj.type == "Conducting Plate":
                n = 0
                if "Faces" in bc_obj.props:
                    n += len(bc_obj.props["Faces"])
                elif "Objects" in bc_obj.props:
                    n += len(bc_obj.props["Objects"])

                if "Total Power Variation Data" not in bc_obj.props:
                    mult = 1
                    power_value = list(decompose_variable_value(bc_obj.props["Total Power"]))
                    power_value = unit_converter(
                        power_value[0], unit_system="Power", input_units=power_value[1], output_units=units
                    )

                else:
                    power_value, exp = extract_dataset_info(bc_obj, units_input=units, boundary="Power")
                    mult = multiplier_from_dataset(exp, temperature)

                if "Objects" in bc_obj.props:
                    for objs in bc_obj.props["Objects"]:
                        obj_name = self._app.modeler[objs].name
                        power_dict_obj[obj_name] = power_value * mult

                elif "Faces" in bc_obj.props:
                    for facs in bc_obj.props["Faces"]:
                        obj_name = self._app.modeler.oeditor.GetObjectNameByFaceID(facs) + "_FaceID" + str(facs)
                        power_dict_obj[obj_name] = power_value * mult

                power_dict[bc_obj.name] = power_value * n * mult

            elif bc_obj.type == "Stationary Wall":
                if bc_obj.props["External Condition"] == "Heat Flux":
                    mult = 1
                    heat_value = list(decompose_variable_value(bc_obj.props["Heat Flux"]))
                    heat_value = unit_converter(
                        heat_value[0],
                        unit_system="SurfaceHeat",
                        input_units=heat_value[1],
                        output_units="irrad_W_per_m2",
                    )

                    power_value = 0.0
                    if "Faces" in bc_obj.props:
                        for component in bc_obj.props["Faces"]:
                            area = self._app.modeler.get_face_area(component)
                            area = unit_converter(
                                area,
                                unit_system="Area",
                                input_units=self._app.modeler.model_units + "2",
                                output_units="m2",
                            )
                            power_value += heat_value * area * mult
                    if "Objects" in bc_obj.props:
                        for component in bc_obj.props["Objects"]:
                            object_assigned = self._app.modeler[component]
                            for f in object_assigned.faces:
                                area = unit_converter(
                                    f.area,
                                    unit_system="Area",
                                    input_units=self._app.modeler.model_units + "2",
                                    output_units="m2",
                                )
                                power_value += heat_value * area * mult

                    power_value = unit_converter(power_value, unit_system="Power", input_units="W", output_units=units)

                    if "Objects" in bc_obj.props:
                        for objs in bc_obj.props["Objects"]:
                            obj_name = self._app.modeler[objs].name
                            power_dict_obj[obj_name] = power_value

                    elif "Faces" in bc_obj.props:
                        for facs in bc_obj.props["Faces"]:
                            obj_name = self._app.modeler.oeditor.GetObjectNameByFaceID(facs) + "_FaceID" + str(facs)
                            power_dict_obj[obj_name] = power_value

                    power_dict[bc_obj.name] = power_value

            elif bc_obj.type == "Resistance":
                n = len(bc_obj.props["Objects"])
                mult = 1
                power_value = list(decompose_variable_value(bc_obj.props["Thermal Power"]))
                power_value = unit_converter(
                    power_value[0], unit_system="Power", input_units=power_value[1], output_units=units
                )

                for objs in bc_obj.props["Objects"]:
                    obj_name = self._app.modeler[objs].name
                    power_dict_obj[obj_name] = power_value * mult

                power_dict[bc_obj.name] = power_value * n * mult

            elif bc_obj.type == "Blower":
                power_value = list(decompose_variable_value(bc_obj.props["Blower Power"]))
                power_value = unit_converter(
                    power_value[0], unit_system="Power", input_units=power_value[1], output_units=units
                )

                obj_name = bc_obj.name
                power_dict_obj[obj_name] = power_value

                power_dict[bc_obj.name] = power_value

        for native_comps in self._app.modeler.user_defined_components.keys():
            if hasattr(self._app.modeler.user_defined_components[native_comps], "native_properties"):
                native_key = "NativeComponentDefinitionProvider"
                if native_key in self._app.modeler.user_defined_components[native_comps].native_properties:
                    power_key = self._app.modeler.user_defined_components[native_comps].native_properties[native_key]
                else:
                    power_key = self._app.modeler.user_defined_components[native_comps].native_properties
                power_value = None
                if "Power" in power_key:
                    power_value = list(decompose_variable_value(power_key["Power"]))
                elif "HubPower" in power_key:
                    power_value = list(decompose_variable_value(power_key["HubPower"]))

                if power_value:
                    power_value = unit_converter(
                        power_value[0], unit_system="Power", input_units=power_value[1], output_units=units
                    )

                    power_dict_obj[native_comps] = power_value
                    power_dict[native_comps] = power_value

        for group in reversed(list(group_hierarchy.keys())):
            for comp in group_hierarchy[group]:
                for power_comp in list(power_dict_obj.keys())[:]:
                    if power_comp.find(comp) >= 0:
                        if group not in power_dict_obj.keys():
                            power_dict_obj[group] = 0.0
                        power_dict_obj[group] += power_dict_obj[power_comp]

        if output_type == "boundary":
            for comp, value in power_dict.items():
                if round(value, 3) != 0.0:
                    self.logger.info(f"The power of {comp} is {str(round(value, 3))} {units}")
            self.logger.info(f"The total power is {str(round(sum(power_dict.values()), 3))} {units}")
            return power_dict, sum(power_dict.values())

        elif output_type == "component":  # pragma: no cover
            for comp, value in power_dict_obj.items():
                if round(value, 3) != 0.0:
                    self.logger.info(f"The power of {comp} is {str(round(value, 3))} {units}")
            self.logger.info(f"The total power is {str(round(sum(power_dict_obj.values()), 3))} {units}")
            return power_dict_obj, sum(power_dict_obj.values())

        else:  # pragma: no cover
            for comp, value in power_dict.items():
                if round(value, 3) != 0.0:
                    self.logger.info(f"The power of {comp} is {str(round(value, 3))} {units}")
            self.logger.info(f"The total power is {str(round(sum(power_dict.values()), 3))} {units}")
            for comp, value in power_dict_obj.items():
                if round(value, 3) != 0.0:
                    self.logger.info(f"The power of {comp} is {str(round(value, 3))} {units}")
            self.logger.info(f"The total power is {str(round(sum(power_dict_obj.values()), 3))} {units}")
            return power_dict_obj, sum(power_dict_obj.values()), power_dict, sum(power_dict.values())
