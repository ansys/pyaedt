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

from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.boundary.common import BoundaryCommon
from ansys.aedt.core.modules.boundary.common import BoundaryObject
from ansys.aedt.core.modules.boundary.common import BoundaryProps


class FieldSetup(BoundaryCommon, BinaryTreeNode):
    """Manages far field and near field component data and execution.

    Examples
    --------
    In this example the sphere1 returned object is a ``ansys.aedt.core.modules.boundary.hfss_boundary.FarFieldSetup``
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> sphere1 = hfss.insert_infinite_sphere()
    >>> sphere1.props["ThetaStart"] = "-90deg"
    >>> sphere1.props["ThetaStop"] = "90deg"
    >>> sphere1.props["ThetaStep"] = "2deg"
    >>> sphere1.delete()
    """

    def __init__(self, app, component_name, props, component_type):
        self.auto_update = False
        self._app = app
        self.type = component_type
        self._name = component_name
        self.__props = BoundaryProps(self, props) if props else {}
        self.auto_update = True
        self._initialize_tree_node()

    @property
    def _child_object(self):
        """Object-oriented properties.

        Returns
        -------
        class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`

        """
        child_object = None
        design_childs = self._app.get_oo_name(self._app.odesign)

        for category in ["Radiation", "EM Fields"]:
            if category in design_childs:
                cc = self._app.get_oo_object(self._app.odesign, category)
                cc_names = self._app.get_oo_name(cc)
                if self._name in cc_names:
                    child_object = cc.GetChildObject(self._name)
                    break

        return child_object

    @property
    def props(self):
        """Field Properties."""
        if not self.__props and self._app.design_properties:
            if (
                self.type == "FarFieldSphere"
                and self._app.design_properties.get("RadField")
                and self._app.design_properties["RadField"].get("FarFieldSetups")
            ):
                for val in self._app.design_properties["RadField"]["FarFieldSetups"]:
                    if val == self.name:
                        self.__props = self._app.design_properties["RadField"]["FarFieldSetups"][val]
            elif self.type != "FarFieldSphere" and self._app.design_properties["RadField"].get("NearFieldSetups"):
                for val in self._app.design_properties["RadField"]["NearFieldSetups"]:
                    if val == self.name:
                        self.__props = self._app.design_properties["RadField"]["NearFieldSetups"][val]
            self.__props = BoundaryProps(self, self.__props)
        return self.__props

    @property
    def name(self):
        """Boundary Name."""
        if self._child_object:
            self._name = str(self.properties["Name"])
        return self._name

    @name.setter
    def name(self, value):
        if self._child_object:
            try:
                self.properties["Name"] = value
            except KeyError:
                self._app.logger.error("Name %s already assigned in the design", value)

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def create(self):
        """Create a Field Setup Component in HFSS.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "FarFieldSphere":
            self._app.oradfield.InsertInfiniteSphereSetup(self._get_args())
        elif self.type == "NearFieldBox":
            self._app.oradfield.InsertBoxSetup(self._get_args())
        elif self.type == "NearFieldSphere":
            self._app.oradfield.InsertSphereSetup(self._get_args())
        elif self.type == "NearFieldRectangle":
            self._app.oradfield.InsertRectangleSetup(self._get_args())
        elif self.type == "NearFieldLine":
            self._app.oradfield.InsertLineSetup(self._get_args())
        elif self.type == "NearFieldPoints":
            self._app.oradfield.InsertPointListSetup(self._get_args())
        elif self.type == "AntennaOverlay":
            self._app.oradfield.AddAntennaOverlay(self._get_args())
        elif self.type == "FieldSourceGroup":
            self._app.oradfield.AddRadFieldSourceGroup(self._get_args())
        return self._initialize_tree_node()

    @pyaedt_function_handler()
    def update(self):
        """Update the Field Setup in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.type == "FarFieldSphere":
            self._app.oradfield.EditInfiniteSphereSetup(self.name, self._get_args())
        elif self.type == "NearFieldBox":
            self._app.oradfield.EditBoxSetup(self.name, self._get_args())
        elif self.type == "NearFieldSphere":
            self._app.oradfield.EditSphereSetup(self.name, self._get_args())
        elif self.type == "NearFieldRectangle":
            self._app.oradfield.EditRectangleSetup(self.name, self._get_args())
        elif self.type == "NearFieldLine":
            self._app.oradfield.EditLineSetup(self.name, self._get_args())
        elif self.type == "AntennaOverlay":
            self._app.oradfield.EditAntennaOverlay(self.name, self._get_args())
        elif self.type == "FieldSourceGroup":
            self._app.oradfield.EditRadFieldSourceGroup(self._get_args())
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the Field Setup in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._app.oradfield.DeleteSetup([self.name])
        for el in self._app.field_setups:
            if el.name == self.name:
                self._app.field_setups.remove(el)
        return True


class FarFieldSetup(FieldSetup, object):
    """Manages Far Field Component data and execution.

    Examples
    --------
    in this example the sphere1 returned object is a ``ansys.aedt.core.modules.boundary.hfss_boundary.FarFieldSetup``
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> sphere1 = hfss.insert_infinite_sphere()
    >>> sphere1.props["ThetaStart"] = "-90deg"
    >>> sphere1.props["ThetaStop"] = "90deg"
    >>> sphere1.props["ThetaStep"] = "2deg"
    >>> sphere1.delete()
    """

    def __init__(self, app, component_name, props, component_type, units="deg"):
        FieldSetup.__init__(self, app, component_name, props, component_type)
        self.units = units

    @property
    def definition(self):
        """Set/Get the Far Field Angle Definition."""
        return self.props["CSDefinition"]

    @definition.setter
    def definition(self, value):
        actual_value = self.props["CSDefinition"]
        self.props["CSDefinition"] = value
        actual_defs = None
        defs = None
        if actual_value != value and value == "Theta-Phi":
            defs = ["ThetaStart", "ThetaStop", "ThetaStep", "PhiStart", "PhiStop", "PhiStep"]
            actual_defs = [
                "AzimuthStart",
                "AzimuthStop",
                "AzimuthStep",
                "ElevationStart",
                "ElevationStop",
                "ElevationStep",
            ]
        elif actual_value != value and value == "El Over Az":
            defs = ["AzimuthStart", "AzimuthStop", "AzimuthStep", "ElevationStart", "ElevationStop", "ElevationStep"]
            if actual_value == "Theta-Phi":
                actual_defs = ["ThetaStart", "ThetaStop", "ThetaStep", "PhiStart", "PhiStop", "PhiStep"]
            else:
                actual_defs = [
                    "AzimuthStart",
                    "AzimuthStop",
                    "AzimuthStep",
                    "ElevationStart",
                    "ElevationStop",
                    "ElevationStep",
                ]
        elif actual_value != value:
            defs = ["ElevationStart", "ElevationStop", "ElevationStep", "AzimuthStart", "AzimuthStop", "AzimuthStep"]
            if actual_value == "Theta-Phi":
                actual_defs = ["ThetaStart", "ThetaStop", "ThetaStep", "PhiStart", "PhiStop", "PhiStep"]
            else:
                actual_defs = [
                    "ElevationStart",
                    "ElevationStop",
                    "ElevationStep",
                    "AzimuthStart",
                    "AzimuthStop",
                    "AzimuthStep",
                ]
        if actual_defs != defs:
            self.props[defs[0]] = self.props[actual_defs[0]]
            self.props[defs[1]] = self.props[actual_defs[1]]
            self.props[defs[2]] = self.props[actual_defs[2]]
            self.props[defs[3]] = self.props[actual_defs[3]]
            self.props[defs[4]] = self.props[actual_defs[4]]
            self.props[defs[5]] = self.props[actual_defs[5]]
            del self.props[actual_defs[0]]
            del self.props[actual_defs[1]]
            del self.props[actual_defs[2]]
            del self.props[actual_defs[3]]
            del self.props[actual_defs[4]]
            del self.props[actual_defs[5]]
        self.update()

    @property
    def use_custom_radiation_surface(self):
        """Set/Get the Far Field Radiation Surface Enable."""
        return self.props["UseCustomRadiationSurface"]

    @use_custom_radiation_surface.setter
    def use_custom_radiation_surface(self, value):
        self.props["UseCustomRadiationSurface"] = value
        self.update()

    @property
    def custom_radiation_surface(self):
        """Set/Get the Far Field Radiation Surface FaceList."""
        return self.props["CustomRadiationSurface"]

    @custom_radiation_surface.setter
    def custom_radiation_surface(self, value):
        if value:
            self.props["UseCustomRadiationSurface"] = True
            self.props["CustomRadiationSurface"] = value
        else:
            self.props["UseCustomRadiationSurface"] = False
            self.props["CustomRadiationSurface"] = ""
        self.update()

    @property
    def use_local_coordinate_system(self):
        """Set/Get the usage of a custom Coordinate System."""
        return self.props["UseLocalCS"]

    @use_local_coordinate_system.setter
    def use_local_coordinate_system(self, value):
        self.props["UseLocalCS"] = value
        self.update()

    @property
    def local_coordinate_system(self):
        """Set/Get the custom Coordinate System name."""
        try:
            return self.properties["Coordinate System"]
        except Exception:  # pragma: no cover
            return None

    @local_coordinate_system.setter
    def local_coordinate_system(self, value):
        if value:
            self.props["UseLocalCS"] = True
            self.props["CoordSystem"] = value
        else:
            self.props["UseLocalCS"] = False
            self.props["CoordSystem"] = ""
        self.update()

    @property
    def polarization(self):
        """Set/Get the Far Field Polarization."""
        return self.props["Polarization"]

    @polarization.setter
    def polarization(self, value):
        self.props["Polarization"] = value
        self.update()

    @property
    def slant_angle(self):
        """Set/Get the Far Field Slant Angle if Polarization is Set to `Slant`."""
        if self.props["Polarization"] == "Slant":
            return self.props["SlantAngle"]
        else:
            return

    @slant_angle.setter
    def slant_angle(self, value):
        self.props["Polarization"] = "Slant"
        self.props["SlantAngle"] = value
        self.update()

    @property
    def theta_start(self):
        """Set/Get the Far Field Theta Start Angle if Definition is Set to `Theta-Phi`."""
        if "ThetaStart" in self.props:
            return self.props["ThetaStart"]
        else:
            return

    @property
    def theta_stop(self):
        """Set/Get the Far Field Theta Stop Angle if Definition is Set to `Theta-Phi`."""
        if "ThetaStop" in self.props:
            return self.props["ThetaStop"]
        else:
            return

    @property
    def theta_step(self):
        """Set/Get the Far Field Theta Step Angle if Definition is Set to `Theta-Phi`."""
        if "ThetaStep" in self.props:
            return self.props["ThetaStep"]
        else:
            return

    @property
    def phi_start(self):
        """Set/Get the Far Field Phi Start Angle if Definition is Set to `Theta-Phi`."""
        if "PhiStart" in self.props:
            return self.props["PhiStart"]
        else:
            return

    @property
    def phi_stop(self):
        """Set/Get the Far Field Phi Stop Angle if Definition is Set to `Theta-Phi`."""
        if "PhiStop" in self.props:
            return self.props["PhiStop"]
        else:
            return

    @property
    def phi_step(self):
        """Set/Get the Far Field Phi Step Angle if Definition is Set to `Theta-Phi`."""
        if "PhiStep" in self.props:
            return self.props["PhiStep"]
        else:
            return

    @property
    def azimuth_start(self):
        """Set/Get the Far Field Azimuth Start Angle if Definition is Set to `Az Over El` or `El Over Az`."""
        if "AzimuthStart" in self.props:
            return self.props["AzimuthStart"]
        else:
            return

    @property
    def azimuth_stop(self):
        """Set/Get the Far Field Azimuth Stop Angle if Definition is Set to `Az Over El` or `El Over Az`."""
        if "AzimuthStop" in self.props:
            return self.props["AzimuthStop"]
        else:
            return

    @property
    def azimuth_step(self):
        """Set/Get the Far Field Azimuth Step Angle if Definition is Set to `Az Over El` or `El Over Az`."""
        if "AzimuthStep" in self.props:
            return self.props["AzimuthStep"]
        else:
            return

    @property
    def elevation_start(self):
        """Set/Get the Far Field Elevation Start Angle if Definition is Set to `Az Over El` or `El Over Az`."""
        if "ElevationStart" in self.props:
            return self.props["ElevationStart"]
        else:
            return

    @property
    def elevation_stop(self):
        """Set/Get the Far Field Elevation Stop Angle if Definition is Set to `Az Over El` or `El Over Az`."""
        if "ElevationStop" in self.props:
            return self.props["ElevationStop"]
        else:
            return

    @property
    def elevation_step(self):
        """Set/Get the Far Field Elevation Step Angle if Definition is Set to `Az Over El` or `El Over Az`."""
        if "ElevationStep" in self.props:
            return self.props["ElevationStep"]
        else:
            return

    @theta_start.setter
    def theta_start(self, value):
        if "ThetaStart" in self.props:
            self.props["ThetaStart"] = self._app.value_with_units(value, self.units)
            self.update()

    @theta_stop.setter
    def theta_stop(self, value):
        if "ThetaStop" in self.props:
            self.props["ThetaStop"] = self._app.value_with_units(value, self.units)
            self.update()

    @theta_step.setter
    def theta_step(self, value):
        if "ThetaStep" in self.props:
            self.props["ThetaStep"] = self._app.value_with_units(value, self.units)
            self.update()

    @phi_start.setter
    def phi_start(self, value):
        if "PhiStart" in self.props:
            self.props["PhiStart"] = self._app.value_with_units(value, self.units)
            self.update()

    @phi_stop.setter
    def phi_stop(self, value):
        if "PhiStop" in self.props:
            self.props["PhiStop"] = self._app.value_with_units(value, self.units)
            self.update()

    @phi_step.setter
    def phi_step(self, value):
        if "PhiStep" in self.props:
            self.props["PhiStep"] = self._app.value_with_units(value, self.units)
            self.update()

    @azimuth_start.setter
    def azimuth_start(self, value):
        if "AzimuthStart" in self.props:
            self.props["AzimuthStart"] = self._app.value_with_units(value, self.units)
            self.update()

    @azimuth_stop.setter
    def azimuth_stop(self, value):
        if "AzimuthStop" in self.props:
            self.props["AzimuthStop"] = self._app.value_with_units(value, self.units)
            self.update()

    @azimuth_step.setter
    def azimuth_step(self, value):
        if "AzimuthStep" in self.props:
            self.props["AzimuthStep"] = self._app.value_with_units(value, self.units)
            self.update()

    @elevation_start.setter
    def elevation_start(self, value):
        if "ElevationStart" in self.props:
            self.props["ElevationStart"] = self._app.value_with_units(value, self.units)
            self.update()

    @elevation_stop.setter
    def elevation_stop(self, value):
        if "ElevationStop" in self.props:
            self.props["ElevationStop"] = self._app.value_with_units(value, self.units)
            self.update()

    @elevation_step.setter
    def elevation_step(self, value):
        if "ElevationStep" in self.props:
            self.props["ElevationStep"] = self._app.value_with_units(value, self.units)
            self.update()


class NearFieldSetup(FieldSetup, object):
    """Manages Near Field Component data and execution.

    Examples
    --------
    In this example the rectangle1 returned object is a
    ``ansys.aedt.core.modules.boundary.hfss_boundary.NearFieldSetup``

    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> rectangle1 = hfss.insert_near_field_rectangle()
    """

    def __init__(self, app, component_name, props, component_type):
        FieldSetup.__init__(self, app, component_name, props, component_type)


class WavePortObject(BoundaryObject):
    """Manages HFSS Wave Port boundary objects.

    This class provides specialized functionality for wave port
    boundaries in HFSS, including analytical alignment settings.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> wave_port = hfss.wave_port(
        ...
    ... )
    >>> wave_port.set_analytical_alignment(True)
    """

    def __init__(self, app, name, props, btype):
        """Initialize a wave port boundary object.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.application.analysis_3d.FieldAnalysis3D`
            The AEDT application instance.
        name : str
            Name of the boundary.
        props : dict
            Dictionary of boundary properties.
        btype : str
            Type of the boundary.
        """
        super().__init__(app, name, props, btype)

    @pyaedt_function_handler()
    def set_analytical_alignment(
        self, u_axis_line=None, analytic_reverse_v=False, coordinate_system="Global", alignment_group=None
    ):
        """Set the analytical alignment property for the wave port.

        Parameters
        ----------
        u_axis_line : list
            List containing start and end points for the U-axis line.
            Format: [[x1, y1, z1], [x2, y2, z2]]
        analytic_reverse_v : bool, optional
            Whether to reverse the V direction. Default is False.
        coordinate_system : str, optional
            Coordinate system to use. Default is "Global".
        alignment_group : int, list or None, optional
            Alignment group number(s) for the wave port. If None, the default group is used.
            If a single integer is provided, it is applied to all modes.

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.

        Examples
        --------
        >>> u_line = [[0, 0, 0], [1, 0, 0]]
        >>> wave_port.set_analytical_alignment(u_line, analytic_reverse_v=True)
        True
        """
        try:
            # Go through all modes and set the alignment group if provided
            if alignment_group is None:
                alignment_group = [0] * len(self.props["Modes"])
            elif isinstance(alignment_group, int):
                alignment_group = [alignment_group] * len(self.props["Modes"])
            elif not (isinstance(alignment_group, list) and all(isinstance(x, (int, float)) for x in alignment_group)):
                raise ValueError("alignment_group must be a list of numbers or None.")
            if len(alignment_group) != len(self.props["Modes"]):
                raise ValueError("alignment_group length must match the number of modes.")
            if not (
                isinstance(u_axis_line, list)
                and len(u_axis_line) == 2
                and all(isinstance(pt, list) and len(pt) == 3 for pt in u_axis_line)
            ):
                raise ValueError("u_axis_line must be a list of two 3-element lists.")
            if not isinstance(analytic_reverse_v, bool):
                raise ValueError("analytic_reverse_v must be a boolean.")
            if not isinstance(coordinate_system, str):
                raise ValueError("coordinate_system must be a string.")

            for i, mode_key in enumerate(self.props["Modes"]):
                self.props["Modes"][mode_key]["AlignmentGroup"] = i
            analytic_u_line = {}
            analytic_u_line["Coordinate System"] = coordinate_system
            analytic_u_line["Start"] = [str(i) + self._app.modeler.model_units for i in u_axis_line[0]]
            analytic_u_line["End"] = [str(i) + self._app.modeler.model_units for i in u_axis_line[1]]
            self.props["AnalyticULine"] = analytic_u_line
            self.props["AnalyticReverseV"] = analytic_reverse_v
            self.props["UseAnalyticAlignment"] = True
            return self.update()
        except Exception as e:
            self._app.logger.error(f"Failed to set analytical alignment: {str(e)}")
            return False

    @pyaedt_function_handler()
    def set_alignment_integration_line(self, integration_lines=None, coordinate_system="Global", alignment_groups=None):
        """Set the integration line alignment property for the wave port modes.

        This method configures integration lines for wave port modes,
        which are used for modal excitation and field calculation. At
        least the first 2 modes should have integration lines defined,
        and at least 1 alignment group should exist.

        Parameters
        ----------
        integration_lines : list of lists, optional
            List of integration lines for each mode. Each integration
            line is defined as [[start_x, start_y, start_z],
            [end_x, end_y, end_z]]. If None, integration lines will
            be disabled for all modes.
            Format: [[[x1, y1, z1], [x2, y2, z2]], [[x3, y3, z3], ...]]
        coordinate_system : str, optional
            Coordinate system to use for the integration lines.
            Default is "Global".
        alignment_groups : list of int, optional
            Alignment group numbers for each mode. If None, default
            groups will be assigned. At least one alignment group
            should exist. If a single integer is provided, it will be
            applied to all modes with integration lines.

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.

        Examples
        --------
        >>> # Define integration lines for first two modes
        >>> int_lines = [
        ...     [[0, 0, 0], [10, 0, 0]],  # Mode 1 integration line
        ...     [[0, 0, 0], [0, -9, 0]],  # Mode 2 integration line
        ... ]
        >>> # Mode 1 in group 1, Mode 2 in group 0
        >>> alignment_groups = [1, 0]
        >>> wave_port.set_alignment_integration_line(int_lines, "Global", alignment_groups)
        True

        >>> # Disable integration lines for all modes
        >>> wave_port.set_alignment_integration_line()
        True
        """
        try:
            num_modes = len(self.props["Modes"])

            if integration_lines is None:
                # Disable integration lines for all modes
                for mode_key in self.props["Modes"]:
                    self.props["Modes"][mode_key]["UseIntLine"] = False
                    if "IntLine" in self.props["Modes"][mode_key]:
                        del self.props["Modes"][mode_key]["IntLine"]
                return self.update()

            # Validate integration_lines parameter
            if not isinstance(integration_lines, list):
                raise ValueError("integration_lines must be a list of integration line definitions.")

            # Ensure at least the first 2 modes have integration lines
            if len(integration_lines) < min(2, num_modes):
                raise ValueError("At least the first 2 modes should have integration lines defined.")

            # Validate each integration line format
            for i, line in enumerate(integration_lines):
                if not (
                    isinstance(line, list)
                    and len(line) == 2
                    and all(isinstance(pt, list) and len(pt) == 3 for pt in line)
                ):
                    raise ValueError(
                        f"Integration line {i + 1} must be a list of two 3-element lists [[x1,y1,z1], [x2,y2,z2]]."
                    )

            # Validate coordinate_system
            if not isinstance(coordinate_system, str):
                raise ValueError("coordinate_system must be a string.")

            # Handle alignment_groups parameter
            if alignment_groups is None:
                # Default: modes with integration lines get group 1,
                # others get group 0
                alignment_groups = [1 if i < len(integration_lines) else 0 for i in range(num_modes)]
            elif isinstance(alignment_groups, int):
                # Single group for modes with integration lines
                alignment_groups = [(alignment_groups if i < len(integration_lines) else 0) for i in range(num_modes)]
            elif isinstance(alignment_groups, list):
                # Validate alignment_groups list
                if not all(isinstance(x, (int, float)) for x in alignment_groups):
                    raise ValueError("alignment_groups must be a list of integers.")
                # Extend or truncate to match number of modes
                if len(alignment_groups) < num_modes:
                    alignment_groups.extend([0] * (num_modes - len(alignment_groups)))
                elif len(alignment_groups) > num_modes:
                    alignment_groups = alignment_groups[:num_modes]
            else:
                raise ValueError("alignment_groups must be an integer, list of integers, or None.")

            # Ensure at least one alignment group exists (non-zero)
            if all(group == 0 for group in alignment_groups[: len(integration_lines)]):
                self._app.logger.warning(
                    "No non-zero alignment groups defined. Setting first mode to alignment group 1."
                )
                if len(alignment_groups) > 0:
                    alignment_groups[0] = 1

            # Configure each mode

            mode_keys = list(self.props["Modes"].keys())
            for i, mode_key in enumerate(mode_keys):
                # Set alignment group
                self.props["Modes"][mode_key]["AlignmentGroup"] = alignment_groups[i]
                if i < len(integration_lines):
                    # Mode has an integration line

                    # Create IntLine structure
                    int_line = {
                        "Coordinate System": coordinate_system,
                        "Start": [f"{coord}{self._app.modeler.model_units}" for coord in integration_lines[i][0]],
                        "End": [f"{coord}{self._app.modeler.model_units}" for coord in integration_lines[i][1]],
                    }
                    self.props["Modes"][mode_key]["IntLine"] = int_line
                    self.props["Modes"][mode_key]["UseIntLine"] = True
                else:
                    # Mode does not have an integration line
                    self.props["Modes"][mode_key]["UseIntLine"] = False
                    if "IntLine" in self.props["Modes"][mode_key]:
                        del self.props["Modes"][mode_key]["IntLine"]
            self.props["UseLineModeAlignment"] = True
            return self.update()
        except Exception as e:
            self._app.logger.error(f"Failed to set integration line alignment: {str(e)}")
            return False

    @pyaedt_function_handler()
    def set_polarity_integration_line(
        self, integration_lines=None, coordinate_system="Global"
    ):
        """Set polarity integration lines for the wave port modes.

        This method configures integration lines for wave port modes
        with polarity alignment. When integration lines are provided,
        they are used to define the field polarization direction for
        each mode. The alignment mode is set to polarity
        (UseLineModeAlignment=False).

        Parameters
        ----------
        integration_lines : list of lists, optional
            List of integration lines for each mode. Each integration
            line is defined as [[start_x, start_y, start_z],
            [end_x, end_y, end_z]]. If None, integration lines will
            be disabled for all modes.
            Format: [[[x1, y1, z1], [x2, y2, z2]], [[x3, y3, z3], ...]]
        coordinate_system : str, optional
            Coordinate system to use for the integration lines.
            Default is "Global".

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.

        Examples
        --------
        >>> # Define integration lines for modes
        >>> int_lines = [
        ...     [[0, 0, 0], [10, 0, 0]],  # Mode 1 integration line
        ...     [[0, 0, 0], [0, 10, 0]],  # Mode 2 integration line
        ... ]
        >>> wave_port.set_polarity_integration_line(
        ...     int_lines, "Global"
        ... )
        True

        >>> # Disable integration lines for all modes
        >>> wave_port.set_polarity_integration_line()
        True
        """
        try:
            # Set UseLineModeAlignment to False for polarity mode
            self.props["UseLineModeAlignment"] = False
            self.props["UseAnalyticAlignment"] = False

            if integration_lines is None:
                return self.update()

            # Normalize integration_lines to handle single mode case
            if not isinstance(integration_lines, list):
                raise ValueError(
                    "integration_lines must be a list of integration line definitions."
                )

            # If not a list of lists, assume it's a single integration
            # line for first mode
            if (
                len(integration_lines) > 0
                and not isinstance(integration_lines[0], list)
            ):
                integration_lines = [integration_lines]
            elif (
                len(integration_lines) > 0
                and len(integration_lines[0]) == 2
                and isinstance(integration_lines[0][0], (int, float))
            ):
                integration_lines = [integration_lines]

            # Validate each integration line format
            for i, line in enumerate(integration_lines):
                if not (
                    isinstance(line, list)
                    and len(line) == 2
                    and all(
                        isinstance(pt, list) and len(pt) == 3
                        for pt in line
                    )
                ):
                    raise ValueError(
                        f"Integration line {i + 1} must be a list of two 3-element lists [[x1,y1,z1], [x2,y2,z2]]."
                    )

            # Validate coordinate_system
            if not isinstance(coordinate_system, str):
                raise ValueError(
                    "coordinate_system must be a string."
                )

            # Configure each mode
            mode_keys = list(self.props["Modes"].keys())
            for i, mode_key in enumerate(mode_keys):
                # Set AlignmentGroup to 0 for polarity mode
                mode_props = self.props["Modes"][mode_key]
                mode_props["AlignmentGroup"] = 0

                if i < len(integration_lines):
                    # Mode has an integration line
                    start = [
                        (
                            str(coord) + self._app.modeler.model_units
                            if isinstance(coord, (int, float))
                            else coord
                        )
                        for coord in integration_lines[i][0]
                    ]
                    stop = [
                        (
                            str(coord) + self._app.modeler.model_units
                            if isinstance(coord, (int, float))
                            else coord
                        )
                        for coord in integration_lines[i][1]
                    ]

                    # Create IntLine structure
                    int_line = {
                        "Coordinate System": coordinate_system,
                        "Start": start,
                        "End": stop,
                    }
                    mode_props["IntLine"] = int_line
                    mode_props["UseIntLine"] = True
                else:
                    # Mode does not have an integration line
                    mode_props["UseIntLine"] = False
                    if "IntLine" in mode_props:
                        del mode_props["IntLine"]

            return self.update()
        except Exception as e:
            self._app.logger.error(
                f"Failed to set polarity integration lines: {str(e)}"
            )
            return False

    @property
    def filter_modes_reporter(self):
        """Get the reporter filter setting for each mode.

        Returns
        -------
        list of bool
            List of boolean values indicating whether each mode is
            filtered in the reporter.
        """
        return self.props["ReporterFilter"]

    @filter_modes_reporter.setter
    def filter_modes_reporter(self, value):
        """Set the reporter filter setting for wave port modes.

        Parameters
        ----------
        value : bool or list of bool
            Boolean value(s) to set for the reporter filter. If a
            single boolean is provided, it will be applied to all
            modes. If a list is provided, it must match the number
            of modes.

        Examples
        --------
        >>> # Set all modes to be filtered
        >>> wave_port.filter_modes_reporter = True

        >>> # Set specific filter values for each mode
        >>> wave_port.filter_modes_reporter = [True, False, True]
        """
        try:
            num_modes = len(self.props["Modes"])
            show_reporter_filter = True
            if isinstance(value, bool):
                # Single boolean value - apply to all modes
                filter_values = [value] * num_modes
                # In case all values are the same, we hide the Reporter Filter
                show_reporter_filter = False
            elif isinstance(value, list):
                # List of boolean values
                if not all(isinstance(v, bool) for v in value):
                    raise ValueError(
                        "All values in the list must be boolean."
                    )
                if len(value) != num_modes:
                    raise ValueError(
                        f"List length ({len(value)}) must match the "
                        f"number of modes ({num_modes})."
                    )
                filter_values = value
            else:
                raise ValueError(
                    "Value must be a boolean or a list of booleans."
                )
            self.props["ShowReporterFilter"] = show_reporter_filter
            # Apply the filter values to each mode
            self.props["ReporterFilter"] = filter_values

            self.update()
        except Exception as e:
            self._app.logger.error(
                f"Failed to set filter modes reporter: {str(e)}"
            )
            raise

    @property
    def specify_wave_direction(self):
        """Get the 'Specify Wave Direction' property.

        Returns
        -------
        bool
            Whether the wave direction is specified.
        """
        return self.properties["Specify Wave Direction"]

    @specify_wave_direction.setter
    def specify_wave_direction(self, value):
        """Set the 'Specify Wave Direction' property.

        Parameters
        ----------
        value : bool
            Whether to specify the wave direction.
        """
        if value == self.properties["Specify Wave Direction"]:
            return value
        self.properties["Specify Wave Direction"] = value
        self.update()
