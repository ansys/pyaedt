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

"""The module contains these classes: `Mesh3dLayout` and `Mesh3dLayoutOperation`.

The module provides all functionalities for creating and editing the mesh in the 3D tools.

"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modules.mesh import MeshProps

if TYPE_CHECKING:
    from ansys.aedt.core.application.analysis_3d_layout import FieldAnalysis3DLayout


class Mesh3dLayoutOperation(PyAedtBase):
    """Mesh 3D Layout operation class.

    Parameters
    ----------
    mesh : :class:`ansys.aedt.core.modules.mesh_3d_layout.Mesh3dLayout`
        Mesh object.
    name : str
        Name of the mesh operation.
    props : dict
        Properties of the mesh operation.
    setup : str
        Name of the setup.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss3dLayout
    >>> app = Hfss3dLayout()
    >>> operation = app.mesh.get_mesh_operation("length1", "setup1")

    """

    def __init__(self, mesh: Mesh3dLayout, name: str, props: dict, setup: str) -> None:
        self._mesh: Mesh3dLayout = mesh
        self._app: Any = self._mesh._app
        self._legacy_props = {}
        self._name = name
        self.__operation_type = None

        self.__setup = setup

        if props:
            self._legacy_props = props

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __getitem__(self, key: str) -> Any:
        """Return a setup property by key."""
        return self.props[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a setup property by key."""
        self.props[key] = value

    @property
    def operation_type(self) -> str | None:
        """Retrieve type.

        Returns
        -------
        str
            Type of the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation.operation_type

        """
        if not self.__operation_type:
            self.__operation_type = self.props.get("Type", None)
        return self.__operation_type

    @property
    def setup(self) -> str:
        """Retrieve type.

        Returns
        -------
        str
            Type of the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation.setup

        """
        return self.__setup

    @property
    def props(self) -> MeshProps:
        """Properties of the mesh operation.

        Returns
        -------
        :class:`ansys.aedt.core.generic.props.Props`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation.props

        """
        if self._legacy_props:
            return MeshProps(self, self._legacy_props)

        props = self._get_setup_mesh_operation_props(self._name)

        self._legacy_props = props

        return MeshProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        self.update(props=value)

    @property
    def name(self) -> str:
        """Name of the mesh operation.

        Returns
        -------
        str
           Name of the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation.name

        """
        return self._name

    @name.setter
    def name(self, meshop_name: str) -> None:  # pragma: no cover
        operation_names = self._mesh.operation_names
        if meshop_name in operation_names:
            raise ValueError(f"Name {meshop_name} already assigned in the design.")
        # self._app.change_property(aedt_object=self._app.odesign,
        #                           tab_name="MeshSetupTab",
        #                           property_object=f"SolveSetups:{self.name}",
        #                           property_name="Name",
        #                           property_value=meshop_name)
        # object.__setattr__(self, "_name", meshop_name)
        self._app.logger.warning("AEDT API does not allow renaming mesh operations.")

    @pyaedt_function_handler()
    def create(self) -> Mesh3dLayoutOperation | bool:
        """Create a mesh.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh_3d_layout.Mesh3dLayoutOperation`
            The created mesh operation.

        References
        ----------
        >>> oModule.AddMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> setup = app.create_setup()
        >>> app.modeler.layers.add_layer(layer="Top")
        >>> c1 = app.modeler.create_circle("Top", 0, 5, 40, "mycircle")
        >>> c1.net_name = "GND"
        >>> op1 = app.mesh.assign_length_mesh(setup=setup.name, layer="Top", net="GND")

        """
        self._app.omeshmodule.AddMeshOperation(self.setup, self._get_args())
        return self

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the mesh.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> props = operation.props.to_dict()
        >>> operation.update(props)

        """
        if props is None:
            props = self.props.to_dict()
        else:
            props = dict(props)

        args = self._get_args(props)
        try:
            self._app.omeshmodule.EditMeshOperation(self.setup, self.name, args)
            self._legacy_props = props
        except Exception:  # pragma: no cover
            self._app.logger.error("Mesh operation could not be updated.")
            return False
        return True

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete the mesh operation.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.DeleteMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation.delete()

        """
        self._app.omeshmodule.DeleteMeshOperation(
            self.setup,
            self.name,
        )
        return True

    @pyaedt_function_handler()
    def refresh(self) -> bool:
        """Refresh object.
        Mesh in HFSS 3D Layout API does not have object-oriented capability.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation.refresh()

        """
        self._app.save_project()
        self._legacy_props = {}
        return True

    @pyaedt_function_handler()
    def _get_args(self, props: dict | None = None) -> list:
        """Retrieve arguments.

        Returns
        -------
        list
            List of arguments for the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation._get_args()

        """
        props = self.props if not props else props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def _get_setup_mesh_operation_props(self, name) -> dict:
        """Retrieve setup mesh operation properties.

        Returns
        -------
        dict
            Mesh properties.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> operation = app.mesh.get_mesh_operation("length1", "setup1")
        >>> operation._get_setup_mesh_operation_props()

        """
        meshops = {}
        design_properties = self._app.design_properties
        try:
            if (
                "Setup" in design_properties
                and "Data" in design_properties["Setup"]
                and self.setup in design_properties["Setup"]["Data"]
                and "MeshOps" in design_properties["Setup"]["Data"][self.setup]
            ) and name in design_properties["Setup"]["Data"][self.setup]["MeshOps"]:
                meshops = self._app.design_properties["Setup"]["Data"][self.setup]["MeshOps"][name]
        except Exception:
            self.logger.debug("An error occurred while accessing design mesh operations.")  # pragma: no cover
        return meshops


class Mesh3dLayout(PyAedtBase):
    """Manages mesh operations for HFSS 3D Layout.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.application.analysis_3d_layout.FieldAnalysis3DLayout`

    Examples
    --------
    >>> from ansys.aedt.core import Hfss3dLayout
    >>> app = Hfss3dLayout()
    >>> mesh = app.mesh

    """

    def __init__(self, app: FieldAnalysis3DLayout) -> None:
        self._app: Any = app
        self.logger = self._app.logger

        # Available mesh operations
        self.__operations = SetupDict()

    @property
    def operation_names(self) -> dict[str, str]:
        """Return the available mesh operation names.

        Returns
        -------
        dict
            Operation names.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> mesh_operations_names = app.mesh.operation_names

        """
        setup_names = self._app.setup_names
        operation_names = {}
        if not setup_names:
            return {}
        has_get_mesh_operations = "GetMeshOperations" in dir(self._app.oanalysis)
        for setup in setup_names:
            if has_get_mesh_operations:
                names = self._app.oanalysis.GetMeshOperations(setup)
                if names:
                    operation_names[setup] = names
            else:  # pragma: no cover
                # Mesh operations can not be retrieved from ChildObject
                names = self._get_setup_mesh_operation_names(setup)
                if names:
                    operation_names[setup] = names

        return operation_names

    @property
    def operations(self) -> SetupDict:
        """Return the available mesh operations.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of mesh operations.

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = hfss.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        >>> mesh_operations_list = hfss.mesh.operations

        """
        for setup_name, operations in self.operation_names.items():
            for operation in operations:
                if setup_name not in self.__operations:
                    self.__operations[setup_name] = SetupDict()
                if operation not in self.__operations[setup_name]:
                    self.__operations[setup_name][operation] = Mesh3dLayoutOperation(
                        mesh=self, name=operation, props={}, setup=setup_name
                    )

        operation_names = self.operation_names
        for setup_name in list(self.__operations.keys()):
            if setup_name not in operation_names:
                del self.__operations[setup_name]
            else:
                for operation_name in list(self.__operations[setup_name].keys()):
                    if operation_name not in operation_names[setup_name]:
                        del self.__operations[setup_name][operation_name]

        return self.__operations

    @pyaedt_function_handler()
    def delete_mesh_operations(self, setup: str, name: str) -> bool:
        """Remove mesh operations from a setup.

        Parameters
        ----------
        setup : str
            Name of the setup.
        name : str
            Name of the mesh.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.DeleteMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> app.mesh.delete_mesh_operations(setup="Setup1", name="Length1")

        """
        operation_names = self.operation_names
        if setup in operation_names and name in operation_names[setup]:
            self.operations[setup][name].delete()
        return True

    @pyaedt_function_handler()
    def _get_setup_mesh_operation_names(self, name) -> list:
        """Retrieve setup mesh operations.

        Returns
        -------
        list
            Mesh operation names.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> app.mesh._get_setup_mesh_operation_names(name="Setup1")

        """
        meshops = []
        design_properties = self._app.design_properties
        try:
            if (
                "Setup" in design_properties
                and "Data" in design_properties["Setup"]
                and name in design_properties["Setup"]["Data"]
                and "MeshOps" in design_properties["Setup"]["Data"][name]
            ):
                meshops = list(self._app.design_properties["Setup"]["Data"][name]["MeshOps"])
        except Exception:
            self.logger.debug("An error occurred while accessing design mesh operations.")  # pragma: no cover
        return meshops

    @pyaedt_function_handler()
    def assign_length_mesh(
        self,
        setup: str,
        layer: str,
        net: str,
        is_inside: bool = True,
        maximum_length: int | None = 1,
        maximum_elements: int = 1000,
        name: str | None = None,
    ) -> Mesh3dLayoutOperation | bool:
        """Assign mesh length.

        Parameters
        ----------
        setup : str
            Name of the HFSS setup to apply.
        layer : str
           Name of the layer.
        net : str
           Name of the net.
        is_inside : bool, optional
            Whether the mesh length is inside the selection. The default is ``True``.
        maximum_length : float, optional
            Maximum length of the element. The default is ``1`` When ``None``, this
            parameter is disabled.
        maximum_elements : int, optional
            Maximum number of elements. The default is ``1000``. When ``None``, this
            parameter is disabled.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        type
            Mesh operation object.

        References
        ----------
        >>> oModule.AddMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> setup = app.create_setup()
        >>> app.modeler.layers.add_layer(layer="Top")
        >>> c1 = app.modeler.create_circle("Top", 0, 5, 40, "mycircle")
        >>> c1.net_name = "GND"
        >>> op1 = app.mesh.assign_length_mesh(setup=setup.name, layer="Top", net="GND")

        """
        if not name:
            name = generate_unique_name("Length")
        elif name not in self.operation_names:
            name = generate_unique_name(name)

        if maximum_length is None:
            restrictlength = False
        else:
            restrictlength = True
        length = self._app.modeler.modeler_variable(maximum_length)

        if maximum_elements is None:
            restrictel = False
            numel = "1000"
        else:
            restrictel = True
            numel = str(maximum_elements)

        if maximum_length is None and maximum_elements is None:
            raise AttributeError("Mesh not assigned due to incorrect settings.")

        if isinstance(layer, list) and isinstance(net, list):
            assignment = dict({"MeshEntityInfo": []})
            for lay, n in zip(layer, net):
                meshbody = dict({"Id": -1, "Nam": "", "Layer": lay, "Net": n, "OrigNet": n})
                assignment["MeshEntityInfo"].append(
                    dict({"IsFcSel": False, "EntID": -1, "FcIDs": [], "MeshBody": meshbody, "BBox": []})
                )
        else:
            meshbody = dict({"Id": -1, "Nam": "", "Layer": layer, "Net": net, "OrigNet": net})
            assignment = dict(
                {"MeshEntityInfo": dict({"IsFcSel": False, "EntID": -1, "FcIDs": [], "MeshBody": meshbody, "BBox": []})}
            )
        props = dict(
            {
                "Type": "LengthBased",
                "RefineInside": is_inside,
                "Enabled": True,
                "Assignment": assignment,
                "Region": "",
                "RestrictElem": restrictel,
                "NumMaxElem": numel,
                "RestrictLength": restrictlength,
                "MaxLength": length,
            }
        )

        mop = Mesh3dLayoutOperation(mesh=self, name=name, setup=setup, props=props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_skin_depth(
        self,
        setup: str,
        layer: str,
        net: str,
        skin_depth: int = 1,
        maximum_elements: int | None = None,
        triangulation_max_length: float | int = 0.1,
        layers_number: str = "2",
        name: str | None = None,
    ) -> Mesh3dLayoutOperation | bool:
        """Assign skin depth to the mesh.

        Parameters
        ----------
        setup : str
            Name of the setup.
        layer : str
            Name of the layer.
        net : str
            Name of the net.
        skin_depth : int, optional
            Depth of the skin. The default is ``1``.
        maximum_elements : float, optional
            Maximum element length. The default is ``None``, which disables this parameter.
        triangulation_max_length : float, optional
            Maximum surface triangulation length. The default is ``0.1``.
        layers_number : str, optional
            Number of layers. The default is ``"2"``.
        name : str, optional
             Name of the mesh operation. The default is ``None``.

        Returns
        -------
        type
            Mesh operation object.

        References
        ----------
        >>> oModule.AddMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> setup = app.create_setup()
        >>> app.modeler.layers.add_layer(layer="Top")
        >>> c1 = app.modeler.create_circle("Top", 0, 5, 40, "mycircle")
        >>> c1.net_name = "GND"
        >>> op1 = app.mesh.assign_skin_depth(setup=setup.name, layer="Top", net="GND")

        """
        if not name:
            name = generate_unique_name("SkinDepth")
        elif name not in self.operation_names:
            name = generate_unique_name(name)

        if maximum_elements is None:
            restrictlength = False
            maximum_elements = "1000"
        else:
            restrictlength = True
        skin_depth = self._app.modeler.modeler_variable(skin_depth)

        triangulation_max_length = self._app.modeler.modeler_variable(triangulation_max_length)
        meshbody = dict({"Id": -1, "Nam": "", "Layer": layer, "Net": net, "OrigNet": net})
        assignment = dict(
            {"MeshEntityInfo": dict({"IsFcSel": False, "EntID": -1, "FcIDs": [], "MeshBody": meshbody, "BBox": []})}
        )
        props = dict(
            {
                "Type": "SkinDepthLengthBased",
                "Enabled": True,
                "Assignment": assignment,
                "Region": "",
                "SkinDepth": skin_depth,
                "SurfTriMaxLength": triangulation_max_length,
                "NumLayers": layers_number,
                "RestrictElem": restrictlength,
                "NumMaxElem": maximum_elements,
            }
        )

        mop = Mesh3dLayoutOperation(mesh=self, name=name, setup=setup, props=props)

        return mop.create()

    @pyaedt_function_handler()
    def generate_mesh(self, name: str) -> bool:
        """Generate the mesh for a design.

        Parameters
        ----------
        name : str
            Name of the design.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oDesign.GenerateMesh

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> setup = app.create_setup()
        >>> app.mesh.generate_mesh(setup.name)

        """
        self._app.oanalysis.GenerateMesh([name])
        return True

    @pyaedt_function_handler()
    def get_mesh_operation(self, name: str, setup: str) -> Mesh3dLayoutOperation | None:
        """Get mesh operation.

        Parameters
        ----------
        name : str
            Name of the mesh operation.
        setup : str
            Name of the setup.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell3d
        >>> m3d = Maxwell3d()
        >>> o = m3d.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> op1 = m3d.mesh.assign_length_mesh(assignment=o)
        >>> op2 = m3d.mesh.get_operations(op1.name)

        """
        if setup in self.operation_names and name in self.operation_names[setup]:
            if setup not in self.__operations:
                self.__operations[setup] = SetupDict()
            if name not in self.__operations[setup]:
                self.__operations[setup][name] = Mesh3dLayoutOperation(mesh=self, name=name, props={}, setup=setup)
            return self.__operations[setup][name]
        return None
