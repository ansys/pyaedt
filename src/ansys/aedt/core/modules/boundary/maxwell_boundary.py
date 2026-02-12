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
from __future__ import annotations

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.boundary.common import BoundaryCommon
from ansys.aedt.core.modules.boundary.common import BoundaryProps


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
    """

    def __init__(self, app, name, props=None, boundarytype=None):
        self.auto_update = True
        self._app = app
        self._name = name
        self.__props = BoundaryProps(self, props) if props else {}
        self.type = boundarytype
        self._initialize_tree_node()

    @property
    def _child_object(self):
        cc = self._app.odesign.GetChildObject("Parameters")
        child_object = None
        if self._name in cc.GetChildNames():
            child_object = self._app.odesign.GetChildObject("Parameters").GetChildObject(self._name)
        elif self._name in self._app.odesign.GetChildObject("Parameters").GetChildNames():
            child_object = self._app.odesign.GetChildObject("Parameters").GetChildObject(self._name)

        return child_object

    @property
    def props(self):
        """Maxwell parameter data.

        Returns
        -------
        :class:BoundaryProps
        """
        if self.__props:
            return self.__props
        props = self._get_boundary_data(self.name)

        if props:
            self.__props = BoundaryProps(self, props[0])
            self._type = props[1]
        return self.__props

    @property
    def name(self):
        """Boundary Name."""
        if self._child_object:
            self._name = str(self.properties["Name"])
        return self._name

    @name.setter
    def name(self, value) -> None:
        if self._child_object:
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
    def create(self):
        """Create a boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        return self._initialize_tree_node()

    @pyaedt_function_handler()
    def update(self) -> bool:
        """Update the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "Matrix":
            self._app.omaxwell_parameters.EditMatrix(self.name, self._get_args())
        elif self.type == "Force":
            self._app.omaxwell_parameters.EditForce(self.name, self._get_args())
        elif self.type == "Torque":
            self._app.omaxwell_parameters.EditTorque(self.name, self._get_args())
        else:
            return False
        return True


class MaxwellMatrix(MaxwellParameters):
    """Provides methods to interact with matrices in Maxwell.

    This class allows sources in a reduced matrix to be listed, updated, and deleted.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.Maxwell3d`, :class:`ansys.aedt.core.Maxwell2d`
        Parent Maxwell application instance.
    schema : MaxwellMatrix.MatrixElectric, MaxwellMatrix.MatrixMagnetostatic, MaxwellMatrix.MatrixACMagnetic,
    MaxwellMatrix.MatrixACMagneticAPhi, optional
        Schema defining the matrix assignment.
        The default is ``None``.

    Examples
    --------
    Setup a Maxwell 2D model in Electrostatic (valid for all electric solvers).

    >>> from ansys.aedt.core import Maxwell2d
    >>> m2d = Maxwell2d(version="2025.2", solution_type=SolutionsMaxwell2D.ElectroStaticXY)
    >>> rectangle1 = m2d.modeler.create_rectangle([0.5, 1.5, 0], [2.5, 5], name="Sheet1")
    >>> rectangle2 = m2d.modeler.create_rectangle([9, 1.5, 0], [2.5, 5], name="Sheet2")
    >>> rectangle3 = m2d.modeler.create_rectangle([16.5, 1.5, 0], [2.5, 5], name="Sheet3")
    >>> voltage1 = m2d.assign_voltage([rectangle1], amplitude=1, name="Voltage1")
    >>> voltage2 = m2d.assign_voltage([rectangle2], amplitude=1, name="Voltage2")
    >>> voltage3 = m2d.assign_voltage([rectangle3], amplitude=1, name="Voltage3")

    Define matrix assignments by instantiating the MaxwellElectric class.

    >>> matrix_args = MaxwellMatrix.MatrixElectric(
    >>>             signal_sources=[voltage1.name, voltage2.name],
    >>>             ground_sources=[voltage3.name],
    >>>             matrix_name="test_matrix",
    >>>         )

    Assign matrix. The method returns a MaxwellParameters object.

    >>> matrix = m2d.assign_matrix(matrix_args)
    >>> m2d.release_desktop(True, True)
    """

    def __init__(self, app, name, props=None, schema=None):
        """Initialize Maxwell matrix."""
        super().__init__(app, name, props=props, boundarytype="Matrix")
        self._app = app
        self.__reduced_matrices = None
        self._schema = schema

    @property
    def signal_sources(self) -> list[SourceACMagnetic] | None:
        if (
            isinstance(self._schema, MaxwellMatrix.MatrixElectric)
            or isinstance(self._schema, MaxwellMatrix.MatrixMagnetostatic)
            or isinstance(self._schema, MaxwellMatrix.MatrixACMagnetic)
        ):
            return self._schema.signal_sources
        return None

    @property
    def ground_sources(self) -> list[str] | None:
        if isinstance(self._schema, MaxwellMatrix.MatrixElectric):
            return self._schema.ground_sources
        return None

    @property
    def group_sources(self) -> list[GroupSourcesMagnetostatic] | None:
        if isinstance(self._schema, MaxwellMatrix.MatrixMagnetostatic):
            return self._schema.group_sources
        return None

    @property
    def rl_sources(self) -> list[RLSourceACMagneticAPhi] | None:
        if isinstance(self._schema, MaxwellMatrix.MatrixACMagneticAPhi):
            return self._schema.rl_sources
        return None

    @property
    def gc_sources(self) -> list[GCSourceACMagneticAPhi] | None:
        if isinstance(self._schema, MaxwellMatrix.MatrixACMagneticAPhi):
            return self._schema.gc_sources
        return None

    @property
    def reduced_matrices(self) -> list[MaxwellReducedMatrix]:
        """List of reduced matrix groups for the parent matrix.

        Returns
        -------
        list
            List of reduced matrices for the parent matrix.
        """
        if self._app.solution_type in [SolutionsMaxwell3D.EddyCurrent, SolutionsMaxwell3D.ACMagnetic]:
            self.__reduced_matrices = []
            parent_object = self._app.odesign.GetChildObject("Parameters").GetChildObject(self.name)
            child_names = parent_object.GetChildNames()
            for r in child_names:
                reduced_matrix_object = parent_object.GetChildObject(r)
                reduced_operations = reduced_matrix_object.GetChildNames()
                operation_object = []
                for operation_name in reduced_operations:
                    sources = reduced_matrix_object.GetChildObject(operation_name).GetPropValue("Source").split(", ")
                    operation_object.append(MaxwellReducedMatrixOperation(self.name, r, operation_name, sources))
                self.__reduced_matrices.append(MaxwellReducedMatrix(self._app, self, r, operation_object))
        return self.__reduced_matrices

    class MatrixElectric:
        """Matrix assignment for electric solvers."""

        def __init__(self, signal_sources: list, ground_sources: list | None = None, matrix_name: str | None = None):
            self.signal_sources = signal_sources
            self.ground_sources = ground_sources if ground_sources is not None else []
            self.matrix_name = matrix_name

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
        """

        def __init__(self, name: str, return_path: str | None = "infinite", turns_number: int | None = 1):
            self.name = name
            self.return_path = return_path
            self.turns_number = turns_number

    class GroupSourcesMagnetostatic:
        """Group sources definition for magnetostatic solver.

        Parameters
        ----------
        source_names : list
            List of source names in the group.
        branches_number : int, optional
            Number of branches for the group source.
            The default value is ``1``.
        name : str
            Name of the group source.
            The default value is ``None``.
        """

        def __init__(self, source_names: list, branches_number: int | None = 1, name: str | None = None):
            self.source_names = source_names
            self.branches_number = branches_number
            self.name = name

    class MatrixMagnetostatic:
        """Matrix assignment for magnetostatic solver."""

        def __init__(
            self,
            signal_sources: list[MaxwellMatrix.SourceMagnetostatic],
            group_sources: list[MaxwellMatrix.GroupSourcesMagnetostatic],
            matrix_name=None,
        ):
            self.signal_sources = signal_sources
            self.group_sources = group_sources
            self.matrix_name = matrix_name

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
        """

        def __init__(self, name: str, return_path: str | None = "infinite"):
            self.name = name
            self.return_path = return_path

    class MatrixACMagnetic:
        """Matrix assignment for AC Magnetic solver."""

        def __init__(self, signal_sources: list[MaxwellMatrix.SourceACMagnetic], matrix_name: str | None = None):
            self.signal_sources = signal_sources
            self.matrix_name = matrix_name

    class RLSourceACMagneticAPhi:
        """Sources for AC Magnetic A-Phi solver."""

        def __init__(
            self,
            signal_sources: list,
            ground_sources: list,
        ):
            self.signal_sources = signal_sources
            self.ground_sources = ground_sources

    class GCSourceACMagneticAPhi:
        """Sources for AC Magnetic A-Phi solver."""

        def __init__(
            self,
            signal_sources: list,
            ground_sources: list,
        ):
            self.signal_sources = signal_sources
            self.ground_sources = ground_sources

    class MatrixACMagneticAPhi:
        """Matrix assignment for AC Magnetic A-Phi solver."""

        def __init__(
            self,
            rl_sources: list[MaxwellMatrix.RLSourceACMagneticAPhi],
            gc_sources: list[MaxwellMatrix.GCSourceACMagneticAPhi],
            matrix_name: str | None = None,
        ):
            self.rl_sources = rl_sources
            self.gc_sources = gc_sources
            self.matrix_name = matrix_name

    @pyaedt_function_handler()
    def join_series(self, sources, matrix_name=None, join_name=None) -> MaxwellReducedMatrix:
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

        """
        return self._create_matrix_reduction(
            red_type="Series", sources=sources, matrix_name=matrix_name, join_name=join_name
        )

    @pyaedt_function_handler()
    def join_parallel(self, sources, matrix_name=None, join_name=None) -> MaxwellReducedMatrix:
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

        """
        return self._create_matrix_reduction(
            red_type="Parallel", sources=sources, matrix_name=matrix_name, join_name=join_name
        )

    @pyaedt_function_handler()
    def _create_matrix_reduction(self, red_type, sources, matrix_name=None, join_name=None):
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
    >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellMatrix

    >>> m3d = Maxwell3d(version="2025.2", solution_type=SolutionsMaxwell3D.ACMagnetic)

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
    >>> signal_source_1 = MaxwellMatrix.SourceACMagnetic(name=current1.name)
    >>> signal_source_2 = MaxwellMatrix.SourceACMagnetic(name=current2.name)
    >>> signal_source_3 = MaxwellMatrix.SourceACMagnetic(name=current3.name)
    >>> signal_source_4 = MaxwellMatrix.SourceACMagnetic(name=current4.name)

    >>> matrix_args = MaxwellMatrix.MatrixACMagnetic(
    >>>     signal_sources=[signal_source_1, signal_source_2, signal_source_3, signal_source_4],
    >>>     matrix_name="test_matrix",
    >>> )
    >>> matrix = m3d.assign_matrix(matrix_args)

    Join sources in series to create a reduced matrix.
    >>> reduced_matrix = matrix.join_series(
    >>>     sources=["Current1", "Current2"],
    >>>     matrix_name="ReducedMatrix1",
    >>>     join_name="JoinSeries1"
    >>> )
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
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellMatrix

        >>> m3d = Maxwell3d(version="2025.2", solution_type=SolutionsMaxwell3D.ACMagnetic)

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
        >>> signal_source_1 = MaxwellMatrix.SourceACMagnetic(name=current1.name)
        >>> signal_source_2 = MaxwellMatrix.SourceACMagnetic(name=current2.name)
        >>> signal_source_3 = MaxwellMatrix.SourceACMagnetic(name=current3.name)

        >>> matrix_args = MaxwellMatrix.MatrixACMagnetic(
        >>>     signal_sources=[signal_source_1, signal_source_2, signal_source_3],
        >>>     matrix_name="test_matrix",
        >>> )
        >>> matrix = m3d.assign_matrix(matrix_args)

        Join sources in series to create a reduced matrix.
        >>> reduced_matrix = matrix.join_series(
        ...     sources=["Current1", "Current2", "Current3"], matrix_name="ReducedMatrix1"
        ... )

        Get the reduced operation name.
        >>> operation_name = reduced_matrix.operations_reduction[0].name

        Update the name of the join operation.
        >>> join_operation = reduced_matrix.update(
        >>> name=reduced_matrix.operations_reduction[0].name, operation_type="series", new_name="my_op"
        >>> )

        Update the sources of the join operation.
        >>> join_operation_1 = reduced_matrix.update(
        >>> name=join_operation.name, operation_type="series", new_sources=["Current2", "Current3"]
        >>> )
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
        >>> from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellMatrix

        >>> m3d = Maxwell3d(version="2025.2", solution_type=SolutionsMaxwell3D.ACMagnetic)

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
        >>> signal_source_1 = MaxwellMatrix.SourceACMagnetic(name=current1.name)
        >>> signal_source_2 = MaxwellMatrix.SourceACMagnetic(name=current2.name)
        >>> signal_source_3 = MaxwellMatrix.SourceACMagnetic(name=current3.name)

        >>> matrix_args = MaxwellMatrix.MatrixACMagnetic(
        >>>     signal_sources=[signal_source_1, signal_source_2, signal_source_3],
        >>>     matrix_name="test_matrix",
        >>> )
        >>> matrix = m3d.assign_matrix(matrix_args)

        Join sources in series to create a reduced matrix.
        >>> reduced_matrix = matrix.join_series(
        >>> sources = (["Current1", "Current2", "Current3"],)
        >>> matrix_name = ("ReducedMatrix1",)
        >>> join_name = "JoinSeries1"
        >>> )

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
    """Represent a reduced matrix operation in Maxwell (join in series or parallel)."""

    def __init__(self, parent_matrix: str, reduced_matrix: str, name: str, sources: list[str]):
        self.parent_matrix = parent_matrix
        self.reduced_matrix = reduced_matrix
        self.name = name
        self.sources = sources


class MaxwellForce(MaxwellParameters):
    """Initialize Maxwell force."""

    def __init__(self, app, name, props=None):
        super().__init__(app, name, props=props, boundarytype="Force")
        self._app = app


class MaxwellTorque(MaxwellParameters):
    """Initialize Maxwell torque."""

    def __init__(self, app, name, props=None):
        super().__init__(app, name, props=props, boundarytype="Torque")
        self._app = app


class MaxwellLayoutForce(MaxwellParameters):
    """Initialize Maxwell layout force."""

    def __init__(self, app, name, props=None):
        super().__init__(app, name, props=props, boundarytype="LayoutForce")
        self._app = app
