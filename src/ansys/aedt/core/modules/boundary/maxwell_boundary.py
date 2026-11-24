# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.boundary.common import BoundaryCommon
from ansys.aedt.core.modules.boundary.common import BoundaryProps


@dataclass
class MatrixElectric:
    """Matrix assignment for electric solvers.

    Parameters
    ----------
    signal_sources : list
        List of signal source names.
    ground_sources : list, optional
        List of ground source names. The default is an empty list.
    matrix_name : str, optional
        Name of the matrix. The default is ``None``.

    Examples
    --------
    Compute the capacitance matrix of two conductors referenced to a ground plane.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixElectric
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ElectroStatic)
    >>> trace1 = m3d.modeler.create_box([0, 0, 1], [10, 1, 0.1], name="Trace1", material="copper")
    >>> trace2 = m3d.modeler.create_box([0, 3, 1], [10, 1, 0.1], name="Trace2", material="copper")
    >>> plane = m3d.modeler.create_box([0, -2, 0], [10, 8, 0.1], name="Ground", material="copper")
    >>> voltage1 = m3d.assign_voltage([trace1], amplitude=1, name="V_Trace1")
    >>> voltage2 = m3d.assign_voltage([trace2], amplitude=1, name="V_Trace2")
    >>> voltage_gnd = m3d.assign_voltage([plane], amplitude=0, name="V_Ground")
    >>> matrix_args = MatrixElectric(
    ...     signal_sources=[voltage1.name, voltage2.name],
    ...     ground_sources=[voltage_gnd.name],
    ...     matrix_name="CapacitanceMatrix",
    ... )
    >>> matrix = m3d.assign_matrix(matrix_args)
    >>> m3d.release_desktop()

    """

    signal_sources: list
    """Value for signal sources."""
    ground_sources: list = field(default_factory=list)
    """Value for ground sources."""
    matrix_name: str | None = None
    """Value for matrix name."""


@dataclass
class SourceMagnetostatic:
    """Source definition for magnetostatic solver.

    Parameters
    ----------
    name : str
        Name of the source.
    return_path : str, optional
        For Maxwell 2D design types, the `return_path` parameter can be provided.
        If not the default value is "infinite".
        For Maxwell 3D design types, this parameter is ignored.
    turns_number : int, optional
        Number of turns for the source. The default value is ``1``.

    Examples
    --------
    Define a 10-turn coil in a Maxwell 2D magnetostatic design whose current
    returns through a second coil side.

    >>> from ansys.aedt.core import Maxwell2d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell2D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixMagnetostatic
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceMagnetostatic
    >>> m2d = Maxwell2d(version="2026.1", solution_type=SolutionsMaxwell2D.MagnetostaticXY)
    >>> go = m2d.modeler.create_rectangle([0, 0, 0], [2, 5], name="Coil_Go", material="copper")
    >>> back = m2d.modeler.create_rectangle([6, 0, 0], [2, 5], name="Coil_Back", material="copper")
    >>> current_go = m2d.assign_current([go], amplitude=1, name="I_Go")
    >>> current_back = m2d.assign_current([back], amplitude=1, swap_direction=True, name="I_Back")
    >>> source = SourceMagnetostatic(name=current_go.name, return_path=current_back.name, turns_number=10)
    >>> matrix_args = MatrixMagnetostatic(signal_sources=[source], group_sources=[], matrix_name="CoilMatrix")
    >>> matrix = m2d.assign_matrix(matrix_args)
    >>> m2d.release_desktop()

    """

    name: str
    """Value for name."""
    return_path: str = "infinite"
    """Path to return."""
    turns_number: int = 1
    """Value for turns number."""


@dataclass
class GroupSourcesMagnetostatic:
    """Group sources definition for magnetostatic solver.

    Parameters
    ----------
    source_names : list
        List of source names in the group.
    branches_number : int, optional
        Number of branches for the group source.
        The default value is ``1``.
    name : str, optional
        Name of the group source.
        The default value is ``None``.

    Examples
    --------
    Group two coil sides connected in parallel into a single matrix entry.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import GroupSourcesMagnetostatic
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixMagnetostatic
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceMagnetostatic
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
    >>> bar1 = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Bar1", material="copper")
    >>> bar2 = m3d.modeler.create_box([3, 0, 0], [1, 1, 10], name="Bar2", material="copper")
    >>> bar3 = m3d.modeler.create_box([6, 0, 0], [1, 1, 10], name="Bar3", material="copper")
    >>> current1 = m3d.assign_current([bar1.top_face_z], amplitude=1, name="I_Bar1")
    >>> current2 = m3d.assign_current([bar2.top_face_z], amplitude=1, name="I_Bar2")
    >>> current3 = m3d.assign_current([bar3.top_face_z], amplitude=1, name="I_Bar3")
    >>> return1 = m3d.assign_current([bar1.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar1_Out")
    >>> return2 = m3d.assign_current([bar2.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar2_Out")
    >>> return3 = m3d.assign_current([bar3.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar3_Out")
    >>> group = GroupSourcesMagnetostatic(
    ...     source_names=[current1.name, current2.name], branches_number=2, name="ParallelBars"
    ... )
    >>> matrix_args = MatrixMagnetostatic(
    ...     signal_sources=[
    ...         SourceMagnetostatic(name=current1.name),
    ...         SourceMagnetostatic(name=current2.name),
    ...         SourceMagnetostatic(name=current3.name),
    ...     ],
    ...     group_sources=[group],
    ...     matrix_name="InductanceMatrix",
    ... )
    >>> matrix = m3d.assign_matrix(matrix_args)
    >>> m3d.release_desktop()

    """

    source_names: list
    """Value for source names."""
    branches_number: int = 1
    """Value for branches number."""
    name: str | None = None
    """Value for name."""


@dataclass
class MatrixMagnetostatic:
    """Matrix assignment for magnetostatic solver.

    Parameters
    ----------
    signal_sources : list[SourceMagnetostatic]
        List of signal sources.
    group_sources : list[GroupSourcesMagnetostatic]
        List of group sources.
    matrix_name : str, optional
        Name of the matrix. The default is ``None``.

    Examples
    --------
    Compute the self and mutual inductances of two coils with 20 and 5 turns.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixMagnetostatic
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceMagnetostatic
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
    >>> primary = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Primary", material="copper")
    >>> secondary = m3d.modeler.create_box([4, 0, 0], [1, 1, 10], name="Secondary", material="copper")
    >>> current_p = m3d.assign_current([primary.top_face_z], amplitude=1, name="I_Primary")
    >>> current_s = m3d.assign_current([secondary.top_face_z], amplitude=1, name="I_Secondary")
    >>> return_p = m3d.assign_current([primary.bottom_face_z], amplitude=1, swap_direction=True, name="I_Primary_Out")
    >>> return_s = m3d.assign_current(
    ...     [secondary.bottom_face_z], amplitude=1, swap_direction=True, name="I_Secondary_Out"
    ... )
    >>> matrix_args = MatrixMagnetostatic(
    ...     signal_sources=[
    ...         SourceMagnetostatic(name=current_p.name, turns_number=20),
    ...         SourceMagnetostatic(name=current_s.name, turns_number=5),
    ...     ],
    ...     group_sources=[],
    ...     matrix_name="TransformerMatrix",
    ... )
    >>> matrix = m3d.assign_matrix(matrix_args)
    >>> m3d.release_desktop()

    """

    signal_sources: list[SourceMagnetostatic]
    """Value for signal sources."""
    group_sources: list[GroupSourcesMagnetostatic]
    """Value for group sources."""
    matrix_name: str | None = None
    """Value for matrix name."""


@dataclass
class SourceACMagnetic:
    """Sources for AC Magnetic solver.

    Parameters
    ----------
    name : str
        Name of the source.
    return_path : str, optional
        For Maxwell 2D design types, the `return_path` parameter can be provided.
        If not the default value is "infinite".
        For Maxwell 3D design types, this parameter is ignored.

    Examples
    --------
    Wrap the current excitations of an AC Magnetic design as matrix sources.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagnetic
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)
    >>> bar = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Busbar", material="copper")
    >>> current_in = m3d.assign_current([bar.top_face_z], amplitude=10, name="I_In")
    >>> m3d.assign_current([bar.bottom_face_z], amplitude=10, swap_direction=True, name="I_Out")
    >>> source = SourceACMagnetic(name=current_in.name)
    >>> matrix = m3d.assign_matrix(MatrixACMagnetic(signal_sources=[source], matrix_name="BusbarRL"))
    >>> m3d.release_desktop()

    """

    name: str
    """Value for name."""
    return_path: str = "infinite"
    """Path to return."""


@dataclass
class MatrixACMagnetic:
    """Matrix assignment for AC Magnetic solver.

    Parameters
    ----------
    signal_sources : list[SourceACMagnetic]
        List of signal sources.
    matrix_name : str, optional
        Name of the matrix. The default is ``None``.

    Examples
    --------
    Compute the frequency-dependent R and L matrix of two parallel busbars.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagnetic
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)
    >>> bar1 = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Busbar1", material="copper")
    >>> bar2 = m3d.modeler.create_box([3, 0, 0], [1, 1, 10], name="Busbar2", material="copper")
    >>> current1 = m3d.assign_current([bar1.top_face_z], amplitude=1, name="I_Bar1")
    >>> current2 = m3d.assign_current([bar2.top_face_z], amplitude=1, name="I_Bar2")
    >>> m3d.assign_current([bar1.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar1_Out")
    >>> m3d.assign_current([bar2.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar2_Out")
    >>> matrix_args = MatrixACMagnetic(
    ...     signal_sources=[SourceACMagnetic(name=current1.name), SourceACMagnetic(name=current2.name)],
    ...     matrix_name="BusbarMatrix",
    ... )
    >>> matrix = m3d.assign_matrix(matrix_args)
    >>> m3d.release_desktop()

    """

    signal_sources: list[SourceACMagnetic]
    """Value for signal sources."""
    matrix_name: str | None = None
    """Value for matrix name."""


@dataclass
class RLSourceACMagneticAPhi:
    """RL sources for AC Magnetic A-Phi solver.

    Parameters
    ----------
    signal_sources : list
        List of signal sources.
    ground_sources : list
        List of ground sources.

    Examples
    --------
    Define the terminal pair used to extract the RL matrix of a conductor.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagneticAPhi
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import RLSourceACMagneticAPhi
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagneticAPhi)
    >>> bar = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Conductor", material="copper")
    >>> sink = m3d.assign_current([bar.top_face_z], amplitude=1, name="I_Sink")
    >>> source = m3d.assign_current([bar.bottom_face_z], amplitude=1, swap_direction=True, name="I_Source")
    >>> rl_source = RLSourceACMagneticAPhi(signal_sources=[sink.name], ground_sources=[source.name])
    >>> matrix_args = MatrixACMagneticAPhi(rl_sources=[rl_source], gc_sources=[], matrix_name="RLMatrix")
    >>> matrix = m3d.assign_matrix(matrix_args)
    >>> m3d.release_desktop()

    """

    signal_sources: list
    """Value for signal sources."""
    ground_sources: list
    """Value for ground sources."""


@dataclass
class GCSourceACMagneticAPhi:
    """GC sources for AC Magnetic A-Phi solver.

    Parameters
    ----------
    signal_sources : list
        List of signal sources.
    ground_sources : list
        List of ground sources.

    Examples
    --------
    Define the terminal pair used to extract the GC (conductance and capacitance)
    matrix between two conductors.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import GCSourceACMagneticAPhi
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagneticAPhi
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagneticAPhi)
    >>> signal = m3d.modeler.create_box([0, 0, 1], [10, 1, 0.1], name="Signal", material="copper")
    >>> ground = m3d.modeler.create_box([0, 0, 0], [10, 1, 0.1], name="Ground", material="copper")
    >>> current_sig = m3d.assign_current([signal.top_face_z], amplitude=1, name="I_Signal")
    >>> current_gnd = m3d.assign_current([ground.top_face_z], amplitude=1, name="I_Ground")
    >>> gc_source = GCSourceACMagneticAPhi(signal_sources=[current_sig.name], ground_sources=[current_gnd.name])
    >>> matrix_args = MatrixACMagneticAPhi(rl_sources=[], gc_sources=[gc_source], matrix_name="GCMatrix")
    >>> matrix = m3d.assign_matrix(matrix_args)
    >>> m3d.release_desktop()

    """

    signal_sources: list
    """Value for signal sources."""
    ground_sources: list
    """Value for ground sources."""


@dataclass
class MatrixACMagneticAPhi:
    """Matrix assignment for AC Magnetic A-Phi solver.

    Parameters
    ----------
    rl_sources : list[RLSourceACMagneticAPhi]
        List of RL sources.
    gc_sources : list[GCSourceACMagneticAPhi]
        List of GC sources.
    matrix_name : str, optional
        Name of the matrix. The default is ``None``.

    Examples
    --------
    Extract both the RL and the GC matrices of a two-conductor system.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import GCSourceACMagneticAPhi
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagneticAPhi
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import RLSourceACMagneticAPhi
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagneticAPhi)
    >>> box1 = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Conductor1", material="copper")
    >>> box2 = m3d.modeler.create_box([3, 0, 0], [1, 1, 10], name="Conductor2", material="copper")
    >>> top1 = m3d.assign_current([box1.top_face_z], amplitude=1, name="I1_Top")
    >>> top2 = m3d.assign_current([box2.top_face_z], amplitude=1, name="I2_Top")
    >>> bottom1 = m3d.assign_current([box1.bottom_face_z], amplitude=1, swap_direction=True, name="I1_Bottom")
    >>> bottom2 = m3d.assign_current([box2.bottom_face_z], amplitude=1, swap_direction=True, name="I2_Bottom")
    >>> matrix_args = MatrixACMagneticAPhi(
    ...     rl_sources=[RLSourceACMagneticAPhi(signal_sources=[top1.name], ground_sources=[bottom1.name])],
    ...     gc_sources=[GCSourceACMagneticAPhi(signal_sources=[top2.name], ground_sources=[bottom2.name])],
    ...     matrix_name="RLGCMatrix",
    ... )
    >>> matrix = m3d.assign_matrix(matrix_args)
    >>> m3d.release_desktop()

    """

    rl_sources: list[RLSourceACMagneticAPhi]
    """Value for rl sources."""
    gc_sources: list[GCSourceACMagneticAPhi]
    """Value for gc sources."""
    matrix_name: str | None = None
    """Value for matrix name."""


# Type aliases for data classes

# Source types for different solvers
MaxwellSourceSchema = SourceMagnetostatic | SourceACMagnetic | RLSourceACMagneticAPhi | GCSourceACMagneticAPhi
"""Value for maxwell source schema."""
# Group source types
MaxwellGroupSourceSchema = GroupSourcesMagnetostatic
"""Value for maxwell group source schema."""
# All matrix schema types (top-level matrix definitions)
MaxwellMatrixSchema = MatrixElectric | MatrixMagnetostatic | MatrixACMagnetic | MatrixACMagneticAPhi
"""Value for maxwell matrix schema."""


class MaxwellParameters(BoundaryCommon, BinaryTreeNode, PyAedtBase):
    """Manages parameters data and execution.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.maxwell.Maxwell3d`, :class:`ansys.aedt.core.maxwell.Maxwell2d`
        Either ``Maxwell3d`` or ``Maxwell2d`` application.
    name : str
        Name of the boundary.
    props : dict, optional
        Properties of the boundary.
    boundarytype : str, optional
        Type of the boundary.

    Examples
    --------
    ``MaxwellParameters`` is the base class of the objects returned by
    :meth:`ansys.aedt.core.maxwell.Maxwell.assign_force`,
    :meth:`ansys.aedt.core.maxwell.Maxwell.assign_torque`, and
    :meth:`ansys.aedt.core.maxwell.Maxwell.assign_matrix`.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
    >>> plate = m3d.modeler.create_box([0, 0, 0], [10, 10, 1], name="Plate", material="iron")
    >>> force = m3d.assign_force([plate.name], force_name="Force_Plate")
    >>> force.type
    'Force'
    >>> m3d.release_desktop()

    """

    def __init__(self, app, name, props=None, boundarytype=None) -> None:
        self.auto_update = True
        self._app = app
        self._name = name
        self._legacy_props = {}
        self._type = boundarytype

        if props:
            self._legacy_props = props
            self._has_getobject = False
        else:
            self._has_getobject = _has_get_obj_data(self.child_object)

    @pyaedt_function_handler()
    def _initialize_tree_node(self) -> bool:
        aedt_object = self._resolve_aedt_object()
        if aedt_object:
            BinaryTreeNode.__init__(self, self._name, aedt_object, False, app=self._app, auto_update=self.auto_update)
            return True
        return False

    def _resolve_aedt_object(self):
        """Find the AEDT object associated with the Maxwell parameter."""
        cc = self._app.get_oo_object(self._app.odesign, "Parameters")
        if self._name in self._app.get_oo_name(self._app.odesign, "Parameters"):
            return self._app.get_oo_object(cc, self._name)
        return None

    def update_property(self, prop_name: str, prop_value: str) -> bool:
        old_name = self._name
        result = super().update_property(prop_name, prop_value)
        if prop_name == "Name" and self._name != old_name:
            self._invalidate_tree_node()
            if self._app._boundaries.get(old_name) is self:
                self._app._boundaries.pop(old_name)
                self._app._boundaries[self._name] = self
        return result

    @property
    def props(self) -> BoundaryProps:
        """Maxwell parameter data.

        Returns
        -------
        :class:BoundaryProps

        Examples
        --------
        Read the reference coordinate system of a force and make it a Lorentz force.
        Setting a property updates the parameter in AEDT.

        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
        >>> plate = m3d.modeler.create_box([0, 0, 0], [10, 10, 1], name="Plate", material="copper")
        >>> force = m3d.assign_force([plate.name], force_name="Force_Plate")
        >>> force.props["Reference CS"]
        'Global'
        >>> force.props["Is Virtual"] = False
        >>> m3d.release_desktop()

        """
        if self._legacy_props and not self._has_getobject:
            return BoundaryProps(self, self._legacy_props)

        boundary_data = None
        if self._has_getobject:
            props = _get_obj_data(self.child_object)
        else:
            boundary_data = self._get_boundary_data(self.name)
            props = boundary_data[0] if boundary_data else {}

        if props:
            self._legacy_props = props
            if self._has_getobject:
                child_object = self.child_object
                boundary_type = child_object.Type if "Type" in dir(child_object) else props.get("Type")
                boundary_type = boundary_type or props.get("BoundType")
            else:
                boundary_type = boundary_data[1]
            if boundary_type:
                self._type = boundary_type
        return BoundaryProps(self, self._legacy_props)

    @property
    def type(self) -> str | None:
        """Maxwell parameter type."""
        if not self._type:
            props = self.props
            self._type = self._type or props.get("Type") or props.get("BoundType") or props.get("MaxwellParameterType")
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @property
    def name(self) -> str:
        """Boundary Name.

        Examples
        --------
        Rename a torque parameter.

        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
        >>> rotor = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=5, height=10, name="Rotor")
        >>> torque = m3d.assign_torque([rotor.name], axis="Z")
        >>> torque.name = "Torque_Rotor"
        >>> torque.name
        'Torque_Rotor'
        >>> m3d.release_desktop()

        """
        if self.child_object:
            name = self._get_property_value("Name")
            if name is not None:
                self._name = str(name)
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if self.child_object:
            try:
                self.properties["Name"] = value
            except KeyError:
                self._app.logger.error("Name %s already assigned in the design", value)

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve arguments.

        Parameters
        ----------
        props :
            The default is ``None``.

        Returns
        -------
        list
            List of boundary properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def create(self) -> MaxwellParameters | bool:
        """Create a boundary.

        Returns
        -------
        MaxwellParameters or bool
            The created parameter when successful, ``False`` when failed.

        Examples
        --------
        This method is called by the ``assign_*`` methods of the Maxwell application.
        Call it directly only when building a parameter from a property dictionary.

        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellForce
        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
        >>> plate = m3d.modeler.create_box([0, 0, 0], [10, 10, 1], name="Plate", material="iron")
        >>> props = {"Name": "Force_Plate", "Reference CS": "Global", "Is Virtual": True, "Objects": [plate.name]}
        >>> force = MaxwellForce(m3d, "Force_Plate", props=props)
        >>> created_force = force.create()
        >>> m3d.release_desktop()

        """
        if self.type == "Matrix":
            self._app.omaxwell_parameters.AssignMatrix(self._get_args())
        elif self.type == "Torque":
            self._app.omaxwell_parameters.AssignTorque(self._get_args())
        elif self.type == "Force":
            self._app.omaxwell_parameters.AssignForce(self._get_args())
        elif self.type == "LayoutForce":
            self._app.omaxwell_parameters.AssignLayoutForce(self._get_args())
        else:
            return False
        self._has_getobject = _has_get_obj_data(self.child_object)
        return self

    def delete(self) -> bool:
        old_name = self.name
        if not super().delete():
            return False
        self._invalidate_tree_node()
        if self._app._boundaries.get(old_name) is self:
            self._app._boundaries.pop(old_name)
        return True

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the boundary.

        Parameters
        ----------
        props : dict, optional
            Complete properties to apply. If omitted, the current properties are used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        Change several torque properties and push them to AEDT in a single call.

        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
        >>> rotor = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=5, height=10, name="Rotor")
        >>> torque = m3d.assign_torque([rotor.name], axis="Z", torque_name="Torque_Rotor")
        >>> props = torque.props.to_dict()
        >>> props["Axis"] = "X"
        >>> props["Is Positive"] = False
        >>> torque.update(props)
        True
        >>> m3d.release_desktop()

        """
        if props is None:
            props = self.props.to_dict()
        args = self._get_args(props)
        if self.type == "Matrix":
            self._app.omaxwell_parameters.EditMatrix(self.name, args)
        elif self.type == "Force":
            self._app.omaxwell_parameters.EditForce(self.name, args)
        elif self.type == "Torque":
            self._app.omaxwell_parameters.EditTorque(self.name, args)
        else:
            return False
        if not self._has_getobject:
            self._legacy_props = props
        return True


class MaxwellMatrix(MaxwellParameters):
    """Provides methods to interact with matrices in Maxwell.

    This class allows sources in a reduced matrix to be listed, updated, and deleted.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.Maxwell3d`, :class:`ansys.aedt.core.Maxwell2d`
        Parent Maxwell application instance.
    schema : MaxwellMatrixSchema, optional
        Schema defining the matrix assignment. Can be one of:
        ``MatrixElectric``, ``MatrixMagnetostatic``, ``MatrixACMagnetic``, or
        ``MatrixACMagneticAPhi``.
        The default is ``None``.

    Examples
    --------
    Setup a Maxwell 2D model in Electrostatic (valid for all electric solvers).

    >>> from ansys.aedt.core import Maxwell2d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell2D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixElectric
    >>> m2d = Maxwell2d(version="2026.1", solution_type=SolutionsMaxwell2D.ElectroStaticXY)
    >>> rectangle1 = m2d.modeler.create_rectangle([0.5, 1.5, 0], [2.5, 5], name="Sheet1")
    >>> rectangle2 = m2d.modeler.create_rectangle([9, 1.5, 0], [2.5, 5], name="Sheet2")
    >>> rectangle3 = m2d.modeler.create_rectangle([16.5, 1.5, 0], [2.5, 5], name="Sheet3")
    >>> voltage1 = m2d.assign_voltage([rectangle1], amplitude=1, name="Voltage1")
    >>> voltage2 = m2d.assign_voltage([rectangle2], amplitude=1, name="Voltage2")
    >>> voltage3 = m2d.assign_voltage([rectangle3], amplitude=1, name="Voltage3")

    Define matrix assignments by instantiating the MatrixElectric class.

    >>> matrix_args = MatrixElectric(
    ...     signal_sources=[voltage1.name, voltage2.name],
    ...     ground_sources=[voltage3.name],
    ...     matrix_name="test_matrix",
    ... )

    Assign matrix. The method returns a MaxwellParameters object.

    >>> matrix = m2d.assign_matrix(matrix_args)
    >>> m2d.release_desktop(True, True)

    """

    def __init__(self, app, name, props=None, schema: MaxwellMatrixSchema | None = None) -> None:
        """Initialize Maxwell matrix.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.Maxwell3d`, :class:`ansys.aedt.core.Maxwell2d`
            Parent Maxwell application instance.
        name : str
            Name of the matrix.
        props : dict, optional
            Properties dictionary. The default is ``None``.
        schema : MaxwellMatrixSchema, optional
            Schema defining the matrix assignment. The default is ``None``.
        """
        super().__init__(app, name, props=props, boundarytype="Matrix")
        self._app = app
        self.__reduced_matrices = None
        self._schema = schema

    @property
    def signal_sources(self) -> list[SourceACMagnetic] | None:
        """Retrieve signal sources.

        Examples
        --------
        >>> matrix.signal_sources  # doctest: +SKIP

        """
        if (
            isinstance(self._schema, MatrixElectric)
            or isinstance(self._schema, MatrixMagnetostatic)
            or isinstance(self._schema, MatrixACMagnetic)
        ):
            return self._schema.signal_sources
        return None

    @property
    def ground_sources(self) -> list[str] | None:
        """Retrieve ground sources.

        Examples
        --------
        >>> matrix.ground_sources  # doctest: +SKIP

        """
        if isinstance(self._schema, MatrixElectric):
            return self._schema.ground_sources
        return None

    @property
    def group_sources(self) -> list[GroupSourcesMagnetostatic] | None:
        """Retrieve group sources.

        Examples
        --------
        >>> matrix.group_sources  # doctest: +SKIP

        """
        if isinstance(self._schema, MatrixMagnetostatic):
            return self._schema.group_sources
        return None

    @property
    def rl_sources(self) -> list[RLSourceACMagneticAPhi] | None:
        """Retrieve rl sources.

        Examples
        --------
        >>> matrix.rl_sources  # doctest: +SKIP

        """
        if isinstance(self._schema, MatrixACMagneticAPhi):
            return self._schema.rl_sources
        return None

    @property
    def gc_sources(self) -> list[GCSourceACMagneticAPhi] | None:
        """Retrieve gc sources.

        Examples
        --------
        >>> matrix.gc_sources  # doctest: +SKIP

        """
        if isinstance(self._schema, MatrixACMagneticAPhi):
            return self._schema.gc_sources
        return None

    @property
    def reduced_matrices(self) -> list[MaxwellReducedMatrix]:
        """List of reduced matrix groups for the parent matrix.

        Returns
        -------
        list
            List of reduced matrices for the parent matrix.

        Examples
        --------
        List the reduced matrices and their join operations.

        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagnetic
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic
        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)
        >>> bar1 = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Bar1", material="copper")
        >>> bar2 = m3d.modeler.create_box([3, 0, 0], [1, 1, 10], name="Bar2", material="copper")
        >>> current1 = m3d.assign_current([bar1.top_face_z], amplitude=1, name="I_Bar1")
        >>> current2 = m3d.assign_current([bar2.top_face_z], amplitude=1, name="I_Bar2")
        >>> m3d.assign_current([bar1.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar1_Out")
        >>> m3d.assign_current([bar2.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar2_Out")
        >>> matrix = m3d.assign_matrix(
        ...     MatrixACMagnetic(signal_sources=[SourceACMagnetic(current1.name), SourceACMagnetic(current2.name)])
        ... )
        >>> matrix.join_series(sources=[current1.name, current2.name], matrix_name="SeriesBars", join_name="Series")
        >>> [(r.name, [op.name for op in r.operations_reduction]) for r in matrix.reduced_matrices]
        [('SeriesBars', ['Series'])]
        >>> m3d.release_desktop()

        """
        if self._app.solution_type in [SolutionsMaxwell3D.EddyCurrent, SolutionsMaxwell3D.ACMagnetic]:
            self.__reduced_matrices = []
            parent_object = self._app.get_oo_object(self._app.get_oo_object(self._app.odesign, "Parameters"), self.name)
            child_names = self._app.get_oo_name(parent_object)
            for r in child_names:
                reduced_matrix_object = self._app.get_oo_object(parent_object, r)
                reduced_operations = self._app.get_oo_name(reduced_matrix_object)
                operation_object = []
                for operation_name in reduced_operations:
                    sources = self._app.get_oo_property_value(reduced_matrix_object, operation_name, "Source").split(
                        ", "
                    )
                    operation_object.append(MaxwellReducedMatrixOperation(self.name, r, operation_name, sources))
                self.__reduced_matrices.append(MaxwellReducedMatrix(self._app, self, r, operation_object))
        return self.__reduced_matrices

    @pyaedt_function_handler()
    def join_series(self, sources: list, matrix_name: str = None, join_name: str = None) -> MaxwellReducedMatrix:
        """Create matrix reduction by joining sources in series.

        Parameters
        ----------
        sources : list
            Sources to be included in matrix reduction.
        matrix_name :  str, optional
            Reduced matrix name.
        join_name : str, optional
            Name of the Join operation.

        Returns
        -------
        MaxwellReducedMatrix
            Reduced matrix object.

        Examples
        --------
        Compute the equivalent impedance of two busbars connected in series.

        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagnetic
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic
        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)
        >>> bar1 = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Bar1", material="copper")
        >>> bar2 = m3d.modeler.create_box([3, 0, 0], [1, 1, 10], name="Bar2", material="copper")
        >>> current1 = m3d.assign_current([bar1.top_face_z], amplitude=1, name="I_Bar1")
        >>> current2 = m3d.assign_current([bar2.top_face_z], amplitude=1, name="I_Bar2")
        >>> m3d.assign_current([bar1.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar1_Out")
        >>> m3d.assign_current([bar2.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar2_Out")
        >>> matrix = m3d.assign_matrix(
        ...     MatrixACMagnetic(signal_sources=[SourceACMagnetic(current1.name), SourceACMagnetic(current2.name)])
        ... )
        >>> reduced = matrix.join_series(
        ...     sources=[current1.name, current2.name], matrix_name="SeriesBars", join_name="Series_1_2"
        ... )
        >>> reduced.name
        'SeriesBars'
        >>> m3d.release_desktop()

        """
        return self._create_matrix_reduction(
            red_type="Series", sources=sources, matrix_name=matrix_name, join_name=join_name
        )

    @pyaedt_function_handler()
    def join_parallel(self, sources: list, matrix_name: str = None, join_name: str = None) -> MaxwellReducedMatrix:
        """Create matrix reduction by joining sources in parallel.

        Parameters
        ----------
        sources : list
            Sources to be included in matrix reduction.
        matrix_name :  str, optional
            Reduced matrix name.
        join_name : str, optional
            Name of the Join operation.

        Returns
        -------
        MaxwellReducedMatrix
            Reduced matrix object.

        Examples
        --------
        Compute the equivalent impedance of two busbars connected in parallel.

        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagnetic
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic
        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)
        >>> bar1 = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Bar1", material="copper")
        >>> bar2 = m3d.modeler.create_box([3, 0, 0], [1, 1, 10], name="Bar2", material="copper")
        >>> current1 = m3d.assign_current([bar1.top_face_z], amplitude=1, name="I_Bar1")
        >>> current2 = m3d.assign_current([bar2.top_face_z], amplitude=1, name="I_Bar2")
        >>> m3d.assign_current([bar1.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar1_Out")
        >>> m3d.assign_current([bar2.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar2_Out")
        >>> matrix = m3d.assign_matrix(
        ...     MatrixACMagnetic(signal_sources=[SourceACMagnetic(current1.name), SourceACMagnetic(current2.name)])
        ... )
        >>> reduced = matrix.join_parallel(
        ...     sources=[current1.name, current2.name], matrix_name="ParallelBars", join_name="Parallel_1_2"
        ... )
        >>> reduced.name
        'ParallelBars'
        >>> m3d.release_desktop()

        """
        return self._create_matrix_reduction(
            red_type="Parallel", sources=sources, matrix_name=matrix_name, join_name=join_name
        )

    @pyaedt_function_handler()
    def _create_matrix_reduction(
        self, red_type: str, sources: list, matrix_name: str = None, join_name: str = None
    ) -> MaxwellReducedMatrix:
        if self._app.solution_type not in [SolutionsMaxwell3D.EddyCurrent, SolutionsMaxwell3D.ACMagnetic]:
            raise AEDTRuntimeError(r"Matrix reduction is available only in Eddy Current\AC Magnetic solver.")
        if not matrix_name:
            matrix_name = generate_unique_name("ReducedMatrix", n=3)
        if not join_name:
            join_name = generate_unique_name("Join" + red_type, n=3)
        self._app.omaxwell_parameters.AddReduceOp(
            self.name,
            matrix_name,
            ["NAME:" + join_name, "Type:=", "Join in " + red_type, "Sources:=", ",".join(sources)],
        )
        reduced_matrix = next(m for m in self.reduced_matrices if m.name == matrix_name)
        return reduced_matrix


class MaxwellReducedMatrix:
    """Provides methods to interact with reduced matrices in Maxwell.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.Maxwell3d`, :class:`ansys.aedt.core.Maxwell2d`
        Parent Maxwell application instance.
    parent_matrix : MaxwellMatrix
        Parent matrix object.
    name : str
        Name of the reduced matrix.
    operations_reduction : list[MaxwellReducedMatrixOperation], MaxwellReducedMatrixOperation, optional
        List of reduced matrix operations or a single reduced matrix operation.
        The default is ``None``.

    Examples
    --------
    Create a Maxwell 3D model in AC Magnetic solver.
    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic, MatrixACMagnetic

    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)

    >>> box1 = m3d.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5], material="copper")
    >>> box2 = m3d.modeler.create_box([9, 1.5, 0.5], [2.5, 5, 5], material="copper")
    >>> box3 = m3d.modeler.create_box([16.5, 1.5, 0.5], [2.5, 5, 5], material="copper")
    >>> box4 = m3d.modeler.create_box([20, 1.5, 0.5], [2.5, 5, 5], material="copper")

    >>> current1 = m3d.assign_current([box1.top_face_z], amplitude=1, name="Current1")
    >>> current2 = m3d.assign_current([box2.top_face_z], amplitude=1, name="Current2")
    >>> current3 = m3d.assign_current([box3.top_face_z], amplitude=1, name="Current3")
    >>> current4 = m3d.assign_current([box4.top_face_z], amplitude=1, name="Current4")
    >>> m3d.assign_current([box1.bottom_face_z], amplitude=1, name="Current5", swap_direction=True)
    >>> m3d.assign_current([box2.bottom_face_z], amplitude=1, name="Current6", swap_direction=True)
    >>> m3d.assign_current([box3.bottom_face_z], amplitude=1, name="Current7", swap_direction=True)
    >>> m3d.assign_current([box4.bottom_face_z], amplitude=1, name="Current8", swap_direction=True)

    Assign matrix.
    >>> signal_source_1 = SourceACMagnetic(name=current1.name)
    >>> signal_source_2 = SourceACMagnetic(name=current2.name)
    >>> signal_source_3 = SourceACMagnetic(name=current3.name)
    >>> signal_source_4 = SourceACMagnetic(name=current4.name)

    >>> matrix_args = MatrixACMagnetic(
    ...     signal_sources=[signal_source_1, signal_source_2, signal_source_3, signal_source_4],
    ...     matrix_name="test_matrix",
    ... )
    >>> matrix = m3d.assign_matrix(matrix_args)

    Join sources in series to create a reduced matrix.
    >>> reduced_matrix = matrix.join_series(
    ...     sources=["Current1", "Current2"], matrix_name="ReducedMatrix1", join_name="JoinSeries1"
    ... )
    >>> m3d.release_desktop(True, True)

    """

    def __init__(
        self,
        app,
        parent_matrix: MaxwellMatrix,
        name: str,
        operations_reduction: list[MaxwellReducedMatrixOperation] | MaxwellReducedMatrixOperation | None = None,
    ):
        self._app = app
        self.parent_matrix = parent_matrix
        self.name = name
        if operations_reduction is None:
            self.operations_reduction: list[MaxwellReducedMatrixOperation] = []
        elif isinstance(operations_reduction, MaxwellReducedMatrixOperation):
            self.operations_reduction = [operations_reduction]
        else:
            self.operations_reduction = operations_reduction

    @pyaedt_function_handler()
    def update(
        self, name: str, operation_type: str, new_name: str | None = None, new_sources: list | None = None
    ) -> MaxwellReducedMatrixOperation:
        """Update the reduced matrix.

        Parameters
        ----------
        name : str
            Name of the reduced matrix operation.
        operation_type : str
            Source type, which can be ``Series`` or ``Parallel``.
        new_name : str, optional
            New name of the reduced matrix.
            The default value is the current name.
        new_sources : list, optional
            List of sources to include in the matrix reduction.
            The default values are the sources included already in the reduced matrix operation.

        Returns
        -------
        MaxwellReducedMatrixOperation
            Updated reduced matrix operation object.

        Examples
        --------
        Create a Maxwell 3D model in AC Magnetic solver.
        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic, MatrixACMagnetic

        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)

        Assign a matrix and create a reduced matrix by joining sources in series.
        >>> box1 = m3d.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5], material="copper")
        >>> box2 = m3d.modeler.create_box([9, 1.5, 0.5], [2.5, 5, 5], material="copper")
        >>> box3 = m3d.modeler.create_box([16.5, 1.5, 0.5], [2.5, 5, 5], material="copper")

        >>> current1 = m3d.assign_current([box1.top_face_z], amplitude=1, name="Current1")
        >>> current2 = m3d.assign_current([box2.top_face_z], amplitude=1, name="Current2")
        >>> current3 = m3d.assign_current([box3.top_face_z], amplitude=1, name="Current3")
        >>> m3d.assign_current([box1.bottom_face_z], amplitude=1, name="Current4", swap_direction=True)
        >>> m3d.assign_current([box2.bottom_face_z], amplitude=1, name="Current5", swap_direction=True)
        >>> m3d.assign_current([box3.bottom_face_z], amplitude=1, name="Current6", swap_direction=True)

        Assign matrix.
        >>> signal_source_1 = SourceACMagnetic(name=current1.name)
        >>> signal_source_2 = SourceACMagnetic(name=current2.name)
        >>> signal_source_3 = SourceACMagnetic(name=current3.name)

        >>> matrix_args = MatrixACMagnetic(
        ...     signal_sources=[signal_source_1, signal_source_2, signal_source_3],
        ...     matrix_name="test_matrix",
        ... )
        >>> matrix = m3d.assign_matrix(matrix_args)

        Join sources in series to create a reduced matrix.
        >>> reduced_matrix = matrix.join_series(
        ...     sources=["Current1", "Current2", "Current3"], matrix_name="ReducedMatrix1"
        ... )

        Get the reduced operation name.
        >>> operation_name = reduced_matrix.operations_reduction[0].name

        Update the name of the join operation.
        >>> join_operation = reduced_matrix.update(
        ...     name=reduced_matrix.operations_reduction[0].name, operation_type="series", new_name="my_op"
        ... )

        Update the sources of the join operation.
        >>> join_operation_1 = reduced_matrix.update(
        ...     name=join_operation.name, operation_type="series", new_sources=["Current2", "Current3"]
        ... )
        >>> m3d.release_desktop(True, True)

        """
        if operation_type.lower() not in ["series", "parallel"]:
            raise AEDTRuntimeError("Join type not valid.")
        if name not in [op.name for op in self.operations_reduction]:
            raise AEDTRuntimeError("Reduction operation name not valid.")
        operation = next(op for op in self.operations_reduction if op.name == name)
        if new_name:
            operation.name = new_name
        if new_sources:
            operation.sources = new_sources
        args = [
            "NAME:" + operation.name,
            "Type:=",
            "Join in " + operation_type,
            "Sources:=",
            ",".join(operation.sources) if not new_sources else ",".join(new_sources),
        ]

        self._app.omaxwell_parameters.EditReduceOp(self.parent_matrix.name, self.name, name, args)
        return MaxwellReducedMatrixOperation(self.parent_matrix.name, self.name, operation.name, operation.sources)

    @pyaedt_function_handler()
    def delete(self, name: str) -> bool:
        """Delete a specific reduction operation.

        Parameters
        ----------
        name : string
            Name of the operation to delete.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        Create a Maxwell 3D model in AC Magnetic solver.
        >>> from ansys.aedt.core import Maxwell3d
        >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic, MatrixACMagnetic

        >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)

        Assign a matrix and create a reduced matrix by joining sources in series.
        >>> box1 = m3d.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5], material="copper")
        >>> box2 = m3d.modeler.create_box([9, 1.5, 0.5], [2.5, 5, 5], material="copper")
        >>> box3 = m3d.modeler.create_box([16.5, 1.5, 0.5], [2.5, 5, 5], material="copper")

        >>> current1 = m3d.assign_current([box1.top_face_z], amplitude=1, name="Current1")
        >>> current2 = m3d.assign_current([box2.top_face_z], amplitude=1, name="Current2")
        >>> current3 = m3d.assign_current([box3.top_face_z], amplitude=1, name="Current3")
        >>> m3d.assign_current([box1.bottom_face_z], amplitude=1, name="Current4", swap_direction=True)
        >>> m3d.assign_current([box2.bottom_face_z], amplitude=1, name="Current5", swap_direction=True)
        >>> m3d.assign_current([box3.bottom_face_z], amplitude=1, name="Current6", swap_direction=True)

        Assign matrix.
        >>> signal_source_1 = SourceACMagnetic(name=current1.name)
        >>> signal_source_2 = SourceACMagnetic(name=current2.name)
        >>> signal_source_3 = SourceACMagnetic(name=current3.name)

        >>> matrix_args = MatrixACMagnetic(
        ...     signal_sources=[signal_source_1, signal_source_2, signal_source_3],
        ...     matrix_name="test_matrix",
        ... )
        >>> matrix = m3d.assign_matrix(matrix_args)

        Join sources in series to create a reduced matrix.
        >>> reduced_matrix = matrix.join_series(
        ...     sources=["Current1", "Current2", "Current3"],
        ...     matrix_name="ReducedMatrix1",
        ...     join_name="JoinSeries1",
        ... )

        Delete the reduction operation.
        >>> reduced_matrix.delete(name="JoinSeries1")
        >>> m3d.release_desktop(True, True)

        """
        if name not in [op.name for op in self.operations_reduction]:
            raise AEDTRuntimeError("Reduction operation name not valid.")
        self._app.omaxwell_parameters.DeleteReduceOp(self.parent_matrix.name, self.name, name)
        operation = next(op for op in self.operations_reduction if op.name == name)
        self.operations_reduction.remove(operation)
        return True


class MaxwellReducedMatrixOperation:
    """Represent a reduced matrix operation in Maxwell (join in series or parallel).

    Examples
    --------
    Instances are created by :meth:`MaxwellMatrix.join_series` and
    :meth:`MaxwellMatrix.join_parallel` and are available through
    :attr:`MaxwellReducedMatrix.operations_reduction`.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagnetic
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import SourceACMagnetic
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.ACMagnetic)
    >>> bar1 = m3d.modeler.create_box([0, 0, 0], [1, 1, 10], name="Bar1", material="copper")
    >>> bar2 = m3d.modeler.create_box([3, 0, 0], [1, 1, 10], name="Bar2", material="copper")
    >>> current1 = m3d.assign_current([bar1.top_face_z], amplitude=1, name="I_Bar1")
    >>> current2 = m3d.assign_current([bar2.top_face_z], amplitude=1, name="I_Bar2")
    >>> m3d.assign_current([bar1.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar1_Out")
    >>> m3d.assign_current([bar2.bottom_face_z], amplitude=1, swap_direction=True, name="I_Bar2_Out")
    >>> matrix = m3d.assign_matrix(
    ...     MatrixACMagnetic(signal_sources=[SourceACMagnetic(current1.name), SourceACMagnetic(current2.name)])
    ... )
    >>> reduced = matrix.join_series(sources=[current1.name, current2.name], join_name="Series_1_2")
    >>> operation = reduced.operations_reduction[0]
    >>> operation.name, operation.sources
    ('Series_1_2', ['I_Bar1', 'I_Bar2'])
    >>> m3d.release_desktop()

    """

    def __init__(self, parent_matrix: str, reduced_matrix: str, name: str, sources: list[str]) -> None:
        self.parent_matrix = parent_matrix
        self.reduced_matrix = reduced_matrix
        self.name = name
        self.sources = sources


class MaxwellForce(MaxwellParameters):
    """Initialize Maxwell force.

    Examples
    --------
    Compute the attraction force exerted by a permanent magnet on an iron plate.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Magnetostatic)
    >>> magnet = m3d.modeler.create_box([0, 0, 0], [10, 10, 2], name="Magnet", material="NdFe35")
    >>> plate = m3d.modeler.create_box([0, 0, 3], [10, 10, 1], name="Plate", material="iron")
    >>> force = m3d.assign_force([plate.name], is_virtual=True, force_name="Force_Plate")
    >>> force.props["Objects"]
    ['Plate']
    >>> m3d.release_desktop()

    """

    def __init__(self, app, name, props=None) -> None:
        super().__init__(app, name, props=props, boundarytype="Force")
        self._app = app


class MaxwellTorque(MaxwellParameters):
    """Initialize Maxwell torque.

    Examples
    --------
    Compute the torque about the Z axis acting on a motor rotor.

    >>> from ansys.aedt.core import Maxwell3d
    >>> from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
    >>> m3d = Maxwell3d(version="2026.1", solution_type=SolutionsMaxwell3D.Transient)
    >>> rotor = m3d.modeler.create_cylinder(
    ...     orientation="Z", origin=[0, 0, 0], radius=20, height=50, name="Rotor", material="steel_1008"
    ... )
    >>> torque = m3d.assign_torque([rotor.name], axis="Z", is_positive=True, torque_name="Torque_Rotor")
    >>> torque.props["Axis"]
    'Z'
    >>> m3d.release_desktop()

    """

    def __init__(self, app, name, props=None) -> None:
        super().__init__(app, name, props=props, boundarytype="Torque")
        self._app = app


class MaxwellLayoutForce(MaxwellParameters):
    """Initialize Maxwell layout force.

    Examples
    --------
    Compute the force on the ``GND`` net of a PCB layout component in a
    Transient A-Phi design. The design must already contain the layout
    component ``"LC1_1"``.

    >>> from ansys.aedt.core import Maxwell3d
    >>> m3d = Maxwell3d(version="2026.1", project="pcb_layout.aedt", design="TransientAPhi")
    >>> net_layers = {"GND": ["TOP", "BOTTOM"], "PWR": ["L2"]}
    >>> layout_force = m3d.assign_layout_force(net_layers=net_layers, component_name="LC1_1", force_name="Force_PCB")
    >>> layout_force.type
    'LayoutForce'
    >>> m3d.release_desktop()

    """

    def __init__(self, app, name, props=None) -> None:
        super().__init__(app, name, props=props, boundarytype="LayoutForce")
        self._app = app
