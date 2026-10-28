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

"""The module contains the `Mesh` class."""

from __future__ import annotations

import os
import shutil
import sys
from typing import TYPE_CHECKING
from typing import Any

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.data_handlers import _arg2dict
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.props import Props as MeshProps
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.internal.errors import MethodNotSupportedError
from ansys.aedt.core.internal.load_aedt_file import load_keyword_in_aedt_file
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modeler.cad.elements_3d import EdgePrimitive
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive
from ansys.aedt.core.modeler.cad.elements_3d import VertexPrimitive

if TYPE_CHECKING:
    from ansys.aedt.core.application.analysis_3d import FieldAnalysis3D
    from ansys.aedt.core.modeler.cad.object_3d import Object3d
    from ansys.aedt.core.modules.mesh_icepak import IcepakMesh

mesh_props = {
    "CurvedSurfaceApproxChoice": "Curved Mesh Approximation Type",
    "SliderMeshSettings": "Curved Surface Mesh Resolution",
    "SurfDevChoice": "Surface Deviation Choice",
    "SurfDev": "Surface Deviation",
    "NormalDevChoice": "Normal Deviation Choice",
    "NormalDev": "Normal Deviation",
    "AspectRatioChoice": "Aspect Ratio Choice",
    "AspectRatio": "Aspect Ratio",
    "UseAutoLength": "Use Auto Simplify",
    "DefeatureLength": "Model Resolution Length",
    "SurfaceRepPriority": "Surface Representation Priority for TAU",
    "RestrictLength": "Restrict Length",
    "MaxLength": "Max Length",
    "RestrictElem": "Restrict Max Elems",
    "SkinDepth": "Skin Depth",
    "NumLayers": "Num Layers",
    "SurfTriMaxLength": "Max Elem Length",
    "NumMaxElem": "Max Elems",
    "Apply": "Apply Curvilinear Elements",
    "DisableForFacetedSurfaces": "Disable for Faceted Surface",
    "RestrictMaxElemLength": "Restrict Max Element Length",
    "MaxElemLength": "Max Element Length",
    "RestrictLayersNum": "Restrict Layers Number",
    "LayersNum": "Number of layers",
}
"""Mapping from internal mesh property names to AEDT property names."""


class MeshOperation(BinaryTreeNode, PyAedtBase):
    """MeshOperation class.

    Parameters
    ----------
    mesh : class:`ansys.aedt.core.modules.mesh.Mesh or :class:`ansys.aedt.core.modules.mesh_icepak.IcepakMesh`
        Mesh object.
    name : str
        Name of the mesh operation.
    props : dict
        Properties of the mesh operation.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> from ansys.aedt.core.modules.mesh import MeshOperation
    >>> hfss = Hfss()
    >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
    >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
    >>> isinstance(surface, MeshOperation)

    """

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __init__(self, mesh: Mesh | IcepakMesh, name: str, props: dict) -> None:
        self._mesh: Mesh | IcepakMesh = mesh
        self._app: Any = self._mesh._app
        self._legacy_props = {}
        self._name = name
        self.__operation_type = None
        self.__child_object = None

        if props:
            self._legacy_props = MeshProps(self, props)

        if name == "InitialMeshSettings":
            self.__operation_type = "InitialMeshSettings"

        if self.__operation_type == "InitialMeshSettings":
            # TODO: Currently AEDT API does not have a way to get InitialMeshSettings props
            self._has_getobject = False
        else:
            self._has_getobject = _has_get_obj_data(self._child_object)

    @pyaedt_function_handler()
    def _initialize_tree_node(self) -> bool:
        if self._child_object:
            BinaryTreeNode.__init__(self, self._name, self._child_object, False, app=self._app)
            return True
        return False

    @property
    def _child_object(self) -> Any | None:
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or None

        """
        if not self.__child_object:
            design_childs = self._app.get_oo_name(self._app.odesign)

            if "Mesh" in design_childs:
                cc = self._app.get_oo_object(self._app.odesign, "Mesh")
                cc_names = self._app.get_oo_name(cc)
                if self._name in cc_names:
                    self.__child_object = self._app.get_oo_object(cc, self._name)
        return self.__child_object

    @property
    def operation_type(self) -> str | None:
        """Retrieve type.

        Returns
        -------
        str
            Type of the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface.operation_type

        """
        if not self.__operation_type:
            self.__operation_type = self.props.get("Type", None)
        return self.__operation_type

    @property
    @deprecated("Use operation_type instead.")
    def type(self) -> str | None:
        """Retrieve type.

        Deprecated. Use :attr:`operation_type` instead.

        Returns
        -------
        str
            Type of the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface.type

        """
        return self.operation_type

    @property
    def assignment(self) -> list:
        """Retrieve assignments.

        Returns
        -------
        list
            List of assigned objects.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface.assignment

        """
        assignments = []
        child_object = self._child_object
        if child_object is not None:
            if "Assignment" in child_object.GetPropNames():
                assignment = getattr(child_object, "Assignment", [])
                if isinstance(assignment, str):
                    assignments = [item.strip() for item in assignment.split(",") if item.strip()]
                elif isinstance(assignment, list):
                    assignments = assignment

        return assignments

    @property
    def props(self) -> MeshProps:
        """Properties of the mesh operation.

        Returns
        -------
        :class:`ansys.aedt.core.generic.props.Props`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface.props

        """
        if self._legacy_props and not self._has_getobject:
            return MeshProps(self, self._legacy_props)

        if self._has_getobject:
            props = _get_obj_data(self._child_object) or {}
        else:
            if self.__operation_type == "InitialMeshSettings":
                return self._get_initial_mesh_settings()

            props = {}
            for key, value in self.properties.items():
                if key in mesh_props.values():
                    key = [k for k, v in mesh_props.items() if v == key][0]
                props[key] = value

            if "Assignment" in props:
                assignment = props["Assignment"]
                if "Face_" in assignment:
                    props["Faces"] = [
                        int(i.replace("Face_", "")) for i in assignment.split("(")[1].split(")")[0].split(",")
                    ]
                elif "Edge_" in assignment:
                    props["Edges"] = [
                        int(i.replace("Edge_", "")) for i in assignment.split("(")[1].split(")")[0].split(",")
                    ]
                else:
                    props["Objects"] = assignment
            elif not (props.get("Edges") or props.get("Faces") or props.get("Objects")):
                props["Objects"] = []
                props["Faces"] = []
                props["Edges"] = []
                assigned_id = []
                if self._app._aedt_version >= "2023.1":
                    # GetMeshOpAssignment is not available in 2022 R2 and earlier versions
                    assigned_id = self._app.omeshmodule.GetMeshOpAssignment(self._name)
                for comp_id in assigned_id:
                    if int(comp_id) in self._app.modeler.objects.keys():
                        props["Objects"].append(self._app.oeditor.GetObjectNameByID(comp_id))
                        continue
                    for comp in self._app.modeler.object_list:
                        faces = comp.faces
                        face_ids = [face.id for face in faces]
                        if int(comp_id) in face_ids:
                            props["Faces"].append(int(comp_id))
                            continue
                        edges = comp.edges
                        edge_ids = [edge.id for edge in edges]
                        if int(comp_id) in edge_ids:
                            props["Edges"].append(int(comp_id))
                            continue

        self._legacy_props = props

        return MeshProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        if self.name != "InitialMeshSettings":
            self.update(props=value)
        else:
            self._app.logger.warning(
                "Initial mesh settings props can not be set.Use assign_initial_mesh_from_slider or assign_initial_mesh."
            )

    @pyaedt_function_handler()
    def _get_initial_mesh_settings(self) -> MeshProps:
        try:
            self._legacy_props = self._app.design_properties["MeshSetup"]["MeshSettings"]
        except Exception:
            temp_name = generate_unique_name("temp_prj")
            temp_proj = os.path.join(self._app.working_directory, temp_name + ".aedt")
            oproject_target = self._app.odesktop.NewProject(temp_name)
            if self._app.solution_type == "Modal":
                sol = "HFSS Modal Network"
            elif self._app.solution_type == "Terminal":
                sol = "HFSS Terminal Network"
            else:
                sol = self._app.solution_type
            oproject_target.InsertDesign(self._app.design_type, temp_name, sol, "")
            oproject_target.SaveAs(temp_proj, True)
            self._app.odesktop.CloseProject(temp_name)
            _project_dictionary = load_keyword_in_aedt_file(temp_proj, "AnsoftProject")
            try:
                self._legacy_props = _project_dictionary["AnsoftProject"][self._app._design_type.model_name][
                    "MeshSetup"
                ]["MeshSettings"]
            except Exception:
                self._app.logger.debug("An error occurred while accessing design global mesh.")  # pragma: no cover
            if os.path.exists(temp_proj):
                os.remove(temp_proj)
            if os.path.exists(temp_proj + "results"):
                shutil.rmtree(temp_proj + "results", True)

        return MeshProps(self, self._legacy_props)

    @pyaedt_function_handler()
    def _get_args(self, props: dict | None = None) -> list:
        """Retrieve arguments.

        Returns
        -------
        list
            List of arguments for the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface._get_args()

        """
        props = self.props if not props else props
        arg = ["NAME:" + self._name]
        _dict2arg(props, arg)
        return arg

    @property
    def name(self) -> str:
        """Name of the mesh operation.

        Returns
        -------
        str
           Name of the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface.name

        """
        child_object = self._child_object
        if child_object is not None and self.operation_type != "InitialMeshSettings":
            self._name = child_object.Name
        return self._name

    @name.setter
    def name(self, meshop_name: str) -> None:
        if isinstance(self._mesh, Mesh):
            operation_names = self._mesh.operation_names
        else:
            operation_names = [operation.name for operation in self._mesh.meshoperations]
        if meshop_name in operation_names:
            raise ValueError(f"Name {meshop_name} already assigned in the design.")
        if self.operation_type != "InitialMeshSettings":
            if "Rename" in dir(self._app.omeshmodule):
                self._app.omeshmodule.Rename(self.name, str(meshop_name))
            elif "RenameOp" in dir(self._app.omeshmodule):
                self._app.omeshmodule.RenameOp(self.name, str(meshop_name))
            else:  # pragma: no cover
                raise AEDTRuntimeError("AEDT API does not support mesh operation rename.")

            self.__child_object = None
            object.__setattr__(self, "_name", meshop_name)
            object.__setattr__(self, "_tree_node_initialized", False)
            object.__setattr__(self, "_props", None)
            object.__setattr__(self, "_children_loaded", False)

    @pyaedt_function_handler()
    def create(self) -> MeshOperation | bool:
        """Create a mesh.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            The created mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")

        """
        if self.operation_type == "SurfApproxBased":
            self._app.omeshmodule.AssignTrueSurfOp(self._get_args())
        elif self.operation_type == "DefeatureBased":
            self._app.omeshmodule.AssignModelResolutionOp(self._get_args())
        elif self.operation_type == "SurfaceRepPriority":
            self._app.omeshmodule.AssignSurfPriorityForTauOp(self._get_args())
        elif self.operation_type == "LengthBased":
            self._app.omeshmodule.AssignLengthOp(self._get_args())
        elif self.operation_type == "SkinDepthBased":
            self._app.omeshmodule.AssignSkinDepthOp(self._get_args())
        elif self.operation_type == "Curvilinear":
            self._app.omeshmodule.AssignApplyCurvlinearElementsOp(self._get_args())
        elif self.operation_type == "RotationalLayerMesh":
            props = self.props.to_dict()
            if "Total Layer Thickness" in props:
                props["Total Layer Thickenss"] = props["Total Layer Thickness"]
                del props["Total Layer Thickness"]
            self._app.omeshmodule.AssignRotationalLayerOp(self._get_args(props))
        elif self.operation_type == "EdgeCutLayerMesh":
            props = self.props.to_dict()
            if "Layer Thickness" in props:
                props["Layer Thickenss"] = props["Layer Thickness"]
                del props["Layer Thickness"]
            self._app.omeshmodule.AssignEdgeCutLayerOp(self._get_args(props))
        elif self.operation_type == "DensityControlBased":
            self._app.omeshmodule.AssignDensityControlOp(self._get_args())
        elif self.operation_type == "Icepak":
            self._app.omeshmodule.AssignMeshOperation(self._get_args())
        elif self.operation_type == "CurvatureExtraction":
            self._app.omeshmodule.AssignCurvatureExtractionOp(self._get_args())
        elif self.operation_type in ["CylindricalGap", "AssignCylindricalGapOp"]:
            self._app.omeshmodule.AssignCylindricalGapOp(self._get_args())
        else:
            return False

        # GetObjData is available for some objects in 2026R1
        self._has_getobject = _has_get_obj_data(self._child_object)
        return self

    @pyaedt_function_handler()
    def update(self, key_name: str | None = None, value: int | None = None, props: dict | None = None) -> bool:
        """Update the mesh.

        Parameters
        ----------
        key_name : str, optional
            Key name to update.
        value : int, optional
            Value to update.
        props : dict, optional
            New properties to update. The  default is ``None``, in which case it uses the current properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.InitialMeshSettings
        >>> oModule.Edit
        >>> oModule.EditTrueSurfOp
        >>> oModule.EditModelResolutionOp
        >>> oModule.EditSurfPriorityOp
        >>> oModule.EditLengthOp
        >>> oModule.EditSkinDepthOp
        >>> oModule.EditApplyCurvlinearElementsOp
        >>> oModule.EditRotationalLayerOp
        >>> oModule.EditDensityControlOp
        >>> oModule.EditEdgeCutLayerOp
        >>> oModule.EditMeshOperation
        >>> oModule.EditCurvatureExtractionOp
        >>> oModule.EditSurfPriorityForTauOp
        >>> oModule.EditCylindricalGapOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10])
        >>> rect = hfss.modeler.create_rectangle(0, [0, 0, 10], [10, 10])
        >>> surface = hfss.mesh.assign_surf_priority_for_tau([box.name, rect.name], 1)
        >>> surface.props["SurfaceRepPriority"] = 0
        >>> surface.update("SurfaceRepPriority", 0)

        """
        # Update using Child Object if available and supported
        if key_name is not None and props is not None:
            raise ValueError("Specify either a property key and value or a properties dictionary, not both.")
        if props is None:
            props = self.props.to_dict()
        else:
            props = dict(props)

        if key_name is not None:
            if key_name not in props:
                raise ValueError(f"Key {key_name} not found in mesh operation properties.")
            props[key_name] = value

        if key_name == "NormalDev":
            # If NormalDev is updated, set NormalDevChoice to 2 (manual)
            props["NormalDevChoice"] = 2
        elif key_name == "AspectRatio":
            # If AspectRatio is updated, set AspectRatioChoice to 2 (manual)
            props["AspectRatioChoice"] = 2
        elif key_name == "SurfDev":
            # If SurfDev is updated, set SurfDevChoice to 2 (manual)
            props["SurfDevChoice"] = 2
        elif key_name == "Total Layer Thickness":
            # If Total Layer Thickness is updated, set Total Layer Thickenss to the new value
            props["Total Layer Thickenss"] = value
            del props["Total Layer Thickness"]
        elif key_name == "Layer Thickness":
            # If Layer Thickness is updated, set Layer Thickenss to the new value
            props["Layer Thickenss"] = value
            del props["Layer Thickness"]
        elif key_name == "SurfaceRepPriority":
            value = 1 if value in [1, "High"] else 0
            props["SurfaceRepPriority"] = value

        return self._update_properties(props)

    def _update_properties(self, props: dict, new_name: str | None = None) -> bool:
        """Send a complete mesh operation property dictionary to AEDT."""
        aedt_props = self._get_args(props)

        if new_name is not None:
            aedt_props[0] = "NAME:" + new_name

        if self.operation_type in ["InitialMeshSettings", "MeshSettings"]:
            self._app.omeshmodule.InitialMeshSettings(aedt_props)
        elif hasattr(self._app.omeshmodule, "Edit"):
            self._app.omeshmodule.Edit(self.name, aedt_props)
        else:  # pragma: no cover
            if self.operation_type in ["SurfApproxBased", "Surface Approximation Based"]:
                self._app.omeshmodule.EditTrueSurfOp(self.name, aedt_props)
            elif self.operation_type == "DefeatureBased":
                self._app.omeshmodule.EditModelResolutionOp(self.name, aedt_props)
            elif self.operation_type == "SurfaceRepPriority":
                self._app.omeshmodule.EditSurfPriorityOp(self.name, aedt_props)
            elif self.operation_type == "LengthBased":
                self._app.omeshmodule.EditLengthOp(self.name, aedt_props)
            elif self.operation_type == "SkinDepthBased":
                self._app.omeshmodule.EditSkinDepthOp(self.name, aedt_props)
            elif self.operation_type == "Curvilinear":
                self._app.omeshmodule.EditApplyCurvlinearElementsOp(self.name, aedt_props)
            elif self.operation_type == "RotationalLayerMesh":
                if "Total Layer Thickness" in props:
                    props["Total Layer Thickenss"] = props["Total Layer Thickness"]
                    del props["Total Layer Thickness"]
                self._app.omeshmodule.EditRotationalLayerOp(self.name, aedt_props)
            elif self.operation_type == "DensityControlBased":
                self._app.omeshmodule.EditDensityControlOp(self.name, aedt_props)
            elif self.operation_type == "EdgeCutLayerMesh":
                props = self.props.to_dict()
                if "Layer Thickness" in props:
                    props["Layer Thickenss"] = props["Layer Thickness"]
                    del props["Layer Thickness"]
                self._app.omeshmodule.EditEdgeCutLayerOp(self.name, aedt_props)
            elif self.operation_type == "Icepak":
                self._app.omeshmodule.EditMeshOperation(self.name, aedt_props)
            elif self.operation_type == "CurvatureExtraction":
                self._app.omeshmodule.EditCurvatureExtractionOp(self.name, aedt_props)
            elif self.operation_type == "CylindricalGap":
                self._app.omeshmodule.EditCylindricalGapOp(self.name, aedt_props)
            else:
                return False

        self._legacy_props = props
        return True

    @pyaedt_function_handler()
    def update_assignment(self, properties: dict | None = None) -> bool:
        """Update the boundary assignment.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.ReassignOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10])
        >>> rect = hfss.modeler.create_rectangle(0, [0, 0, 10], [10, 10])
        >>> surface = hfss.mesh.assign_surf_priority_for_tau([box.name, rect.name], 1)
        >>> properties = surface.props
        >>> surface.update_assignment(properties)

        """
        out = []
        if properties is None:
            properties = self.props.to_dict()
        if "Faces" in properties:
            faces = properties.get("Faces", [])
            faces_out = []
            if not isinstance(faces, list):
                faces = [faces]
            for f in faces:
                if isinstance(f, (EdgePrimitive, FacePrimitive, VertexPrimitive)):
                    faces_out.append(f.id)
                else:
                    faces_out.append(f)
            out += ["Faces:=", faces_out]

        if "Objects" in properties:
            pr = []
            for el in properties.get("Objects", []):
                try:
                    pr.append(self._app.modeler[el].name)
                except (KeyError, AttributeError):
                    self._app.logger.debug(
                        "An error occurred while updating the boundary assignment."
                    )  # pragma: no cover
            out += ["Objects:=", pr]

        if len(out) == 1:
            return False

        self._app.omeshmodule.ReassignOp(self.name, out)

        if not self._has_getobject:
            self._legacy_props = dict(properties)

        return True

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete the mesh.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.DeleteOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10])
        >>> rect = hfss.modeler.create_rectangle(0, [0, 0, 10], [10, 10])
        >>> surface = hfss.mesh.assign_surf_priority_for_tau([box.name, rect.name], 1)
        >>> surface.delete()

        """
        self._app.omeshmodule.DeleteOp([self.name])
        return True


class Mesh(PyAedtBase):
    """Manages AEDT mesh functions for 2D and 3D solvers (HFSS, Maxwell, and Q3D).

    Parameters
    ----------
    app : :class:`ansys.aedt.core.application.analysis_3d.FieldAnalysis3D`

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> cylinder = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
    >>> model_resolution = hfss.mesh.assign_model_resolution(cylinder, 1e-4, "ModelRes1")

    """

    def __init__(self, app: FieldAnalysis3D) -> None:
        app.logger.reset_timer()
        self._app: Any = app
        self.logger = self._app.logger

        self._odesign = self._app.odesign

        # Available mesh operations
        self.__operations = SetupDict()
        self.__initial_mesh_settings = None
        self.__child_object = None

        app.logger.info_timer("Mesh class has been initialized!")

    @pyaedt_function_handler()
    def __getitem__(self, part_id) -> MeshOperation | None:
        """Get the object ``Mesh`` for a given mesh operation name.

        Parameters
        ----------
        part_id : str
            Mesh operation name.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Returns None if the part ID or the object name is not found.

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> cylinder = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = hfss.mesh.assign_model_resolution(cylinder, 1e-4, "ModelRes1")
        >>> mr2 = hfss.mesh[mr1.name]

        """
        if part_id.lower() == "initialmeshsettings":
            return self.initial_mesh_settings

        if part_id not in self.operation_names:
            return None

        if part_id not in self.__operations:
            self.__operations[part_id] = MeshOperation(mesh=self, name=part_id, props={})

        return self.__operations[part_id]

    @property
    @deprecated("Use modeler from PyAEDT application instead.")
    def _modeler(self):
        return self._app.modeler

    @property
    def _child_object(self) -> object | None:
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or None

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> app.mesh._child_object.GetChildNames()

        """
        if not self.__child_object:
            design_childs = self._app.get_oo_name(self._app.odesign)

            if "Mesh" in design_childs:
                self.__child_object = self._app.get_oo_object(self._app.odesign, "Mesh")
        return self.__child_object

    @property
    @deprecated("Use operation_names instead.")
    def meshoperation_names(self) -> list[str]:
        """Return the available mesh operation names.

        Deprecated. Use :attr:`operation_names` instead.

        Returns
        -------
        List
            List of mesh operation names.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = hfss.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        >>> mr2 = hfss.mesh.assign_model_resolution(o, 1e-2, "ModelRes2")
        >>> mesh_operations_names = hfss.mesh.meshoperation_names

        """
        return self.operation_names

    @property
    def operation_names(self) -> list[str]:
        """Return the available mesh operation names.

        Returns
        -------
        List
            List of mesh operation names.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = hfss.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        >>> mr2 = hfss.mesh.assign_model_resolution(o, 1e-2, "ModelRes2")
        >>> mesh_operations_names = hfss.mesh.operation_names

        """
        if self._app._is_object_oriented_enabled():
            return list(self._app.get_oo_name(self._app.odesign, "Mesh"))
        return []

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
        for operation in self.operation_names:
            if operation not in self.__operations:
                self.__operations[operation] = MeshOperation(mesh=self, name=operation, props={})

        active_names = set(self.operation_names)
        for setup_name in list(self.__operations):
            if setup_name not in active_names:
                del self.__operations[setup_name]

        return self.__operations

    @property
    def initial_mesh_settings(self) -> MeshOperation:
        """Return the global mesh object.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.InitialMeshSettings

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> hfss.mesh.initial_mesh_settings

        """
        if not self.__initial_mesh_settings:
            self.__initial_mesh_settings = MeshOperation(mesh=self, name="InitialMeshSettings", props={})
        return self.__initial_mesh_settings

    @property
    @deprecated("Use operations instead.")
    def meshoperations(self) -> SetupDict:
        """Return the available mesh operations.

        Deprecated. Use :attr:`operations` instead.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            List of mesh operation object.

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = hfss.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        >>> mesh_operations_list = hfss.mesh.meshoperations

        """
        return self.operations

    @property
    @deprecated("Use omeshmodule from application instead.")
    def omeshmodule(self):
        """AEDT Mesh Module.

        References
        ----------
        >>> oDesign.GetModule("MeshSetup")

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> hfss.omeshmodule

        """
        return

    @pyaedt_function_handler()
    @deprecated("Use operations instead.")
    def _refresh_mesh_operations(self):
        """Refresh all mesh operations."""
        return len(self.operations)

    @pyaedt_function_handler()
    @deprecated("Use operations instead.")
    def _get_design_mesh_operations(self):
        return self.operations

    @pyaedt_function_handler()
    def assign_initial_mesh_from_slider(
        self,
        level: int = 5,
        method: str = "Auto",
        dynamic_surface: bool = True,
        flex_mesh: bool = False,
        curvilinear: bool = False,
        fallback: bool = True,
        phi: bool = True,
        auto_model_resolution: bool = True,
        model_resolution_length: str = "0.0001mm",
    ) -> bool:
        """Assign a surface mesh level to an object.

        Parameters
        ----------
        level : int, optional
            Level of the surface mesh. Options are ``1`` through ``10``. The default is ``5``.
        method : str, optional
            Meshing method. Options are ``"Auto"``, ``"AnsoftTAU"``, and ``"AnsoftClassic"``
            The default is ``"Auto"``.
        dynamic_surface : bool, optional
            Whether to use dynamic surface resolution. The default is ``True``.
        flex_mesh : bool, optional
            Whether to use flexible mesh for TAU volume mesh. The default is ``False``.
        curvilinear : bool, optional
            Whether to apply curvilinear elements. The default is ``False``.
        fallback : bool, optional
            Whether to retain as a fallback. The default is ``True``.
        phi : bool, optional
            Whether to use the Phi mesher for layered geometry.
            The default is ``True``.
        auto_model_resolution : bool, optional
            Whether to automatically calculate the resolution length
            based on each object's effective thickness. The default is ``True``.
        model_resolution_length : float, optional
             Resolution thickness with units if ``automodelresolution=False``.
             The default ``"0.0001mm"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.InitialMeshSettings

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> hfss.mesh.assign_initial_mesh_from_slider()

        """
        if self._app.design_type in ["2D Extractor", "Maxwell 2D"]:
            mesh_methods = ["Auto", "AnsoftClassic"]
        else:
            mesh_methods = ["Auto", "AnsoftTAU", "AnsoftClassic"]
        if method not in mesh_methods:
            raise ValueError(f"Invalid mesh method {method}")

        modelres = ["NAME:GlobalModelRes", "UseAutoLength:=", auto_model_resolution]
        if not auto_model_resolution:
            modelres += ["DefeatureLength:=", model_resolution_length]
        surface_appr: list[Any] = [
            "NAME:GlobalSurfApproximation",
            "CurvedSurfaceApproxChoice:=",
            "UseSlider",
            "SliderMeshSettings:=",
            level,
        ]

        if self._app.design_type in ["2D Extractor", "Maxwell 2D"]:
            args: list[Any] = ["NAME:MeshSettings", surface_appr, modelres, "MeshMethod:=", method]
        else:
            args = [
                "NAME:MeshSettings",
                surface_appr,
                ["NAME:GlobalCurvilinear", "Apply:=", curvilinear],
                modelres,
                "MeshMethod:=",
                method,
                "UseLegacyFaceterForTauVolumeMesh:=",
                False,
                "DynamicSurfaceResolution:=",
                dynamic_surface,
                "UseFlexMeshingForTAUvolumeMesh:=",
                flex_mesh,
            ]
        if self._app.design_type == "HFSS":
            args += ["UseAlternativeMeshMethodsAsFallBack:=", fallback, "AllowPhiForLayeredGeometry:=", phi]
        self._app.omeshmodule.InitialMeshSettings(args)

        # Change properties, because they are not refreshed due to API limitation
        new_props: dict[str, Any] = {}
        _arg2dict(args, new_props)
        if "MeshSettings" in new_props:
            self.initial_mesh_settings._legacy_props = new_props["MeshSettings"]
        return True

    @pyaedt_function_handler()
    def assign_initial_mesh(
        self,
        method: str = "Auto",
        surface_deviation: float | int | str | None = None,
        normal_deviation: float | int | str | None = None,
        aspect_ratio: float | int | str | None = None,
        flex_mesh: bool = False,
        curvilinear: bool = False,
        fallback: bool = True,
        phi: bool = True,
        auto_model_resolution: bool = True,
        model_resolution_length: str = "0.0001mm",
    ) -> bool:
        """Assign a surface mesh level to an object.

        Parameters
        ----------
        method : str, optional
            Meshing method. Options are ``"Auto"``, ``"AnsoftTAU"``, and ``"AnsoftClassic"``
            The default is ``"Auto"``.
        surface_deviation : float, int, or str, optional
             Surface deviation.
             The default is ``None``, in which case the default value is assigned.
        normal_deviation : float, int, or str, optional
             Normal deviation.
             The default is ``None``, in which case the default value is assigned.
        aspect_ratio : float, int, or str, optional
             Aspect ratio.
             The default is ``None``, in which case the default value is assigned.
        flex_mesh : bool, optional
            Whether to use flexible mesh for TAU volume mesh. The default is ``False``.
        curvilinear : bool, optional
            Whether to apply curvilinear elements. The default is ``False``.
        fallback : bool, optional
            Whether to retain as a fallback. The default is ``True``.
        phi : bool, optional
            Whether to use the Phi mesher for layered geometry.
            The default is ``True``.
        auto_model_resolution : bool, optional
            Whether to automatically calculate the resolution length
            based on each object's effective thickness. The default is ``True``.
        model_resolution_length : float or str, optional
             Resolution thickness with units if ``automodelresolution=False``.
             The default ``"0.0001mm"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.InitialMeshSettings

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> hfss.mesh.assign_initial_mesh()

        """
        if self._app.design_type in ["2D Extractor", "Maxwell 2D"]:
            mesh_methods = ["Auto", "AnsoftClassic"]
        else:
            mesh_methods = ["Auto", "AnsoftTAU", "AnsoftClassic"]
        if method not in mesh_methods:
            raise ValueError(f"Invalid mesh method {method}")

        modelres = ["NAME:GlobalModelRes", "UseAutoLength:=", auto_model_resolution]
        if not auto_model_resolution:
            modelres.append("DefeatureLength:=")
            modelres.append(model_resolution_length)

        surface_appr: list[Any] = [
            "NAME:GlobalSurfApproximation",
            "CurvedSurfaceApproxChoice:=",
            "ManualSettings",
            "SurfDevChoice:=",
        ]

        if not surface_deviation:
            surface_appr.append(0)
        else:
            surface_appr += [2, "SurfDev:=", surface_deviation]

        surface_appr.append("NormalDevChoice:=")
        if not normal_deviation:
            surface_appr.append(1)
        else:
            surface_appr += [2, "NormalDev:=", normal_deviation]

        surface_appr.append("AspectRatioChoice:=")
        if not aspect_ratio:
            surface_appr.append(1)
        else:
            surface_appr += [2, "AspectRatio:=", aspect_ratio]

        if self._app.design_type in ["2D Extractor", "Maxwell 2D"]:
            args: list[Any] = ["NAME:MeshSettings", surface_appr, modelres, "MeshMethod:=", method]
        else:
            args = [
                "NAME:MeshSettings",
                surface_appr,
                ["NAME:GlobalCurvilinear", "Apply:=", curvilinear],
                modelres,
                "MeshMethod:=",
                method,
                "UseLegacyFaceterForTauVolumeMesh:=",
                False,
                "DynamicSurfaceResolution:=",
                False,
                "UseFlexMeshingForTAUvolumeMesh:=",
                flex_mesh,
            ]
        if self._app.design_type == "HFSS":
            args += ["UseAlternativeMeshMethodsAsFallBack:=", fallback, "AllowPhiForLayeredGeometry:=", phi]
        self._app.omeshmodule.InitialMeshSettings(args)

        # Change properties, because they are not refreshed due to API limitation
        new_props: dict[str, Any] = {}
        _arg2dict(args, new_props)
        if "MeshSettings" in new_props:
            self.initial_mesh_settings._legacy_props = new_props["MeshSettings"]

        return True

    @pyaedt_function_handler()
    def assign_model_resolution(
        self,
        assignment: str | list | Object3d,
        defeature_length: float | int | str | None = None,
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign the model resolution.

        Parameters
        ----------
        assignment : str, list, or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of objects to defeature.
        defeature_length : float, int or str, optional
            Defeaturing length in millimeters, user can introduce the value with units.
            The default is ``None``, in which case automatic defeaturing is used.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignModelResolutionOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")

        """
        assignment = self._app.modeler.convert_to_selections(assignment, True)

        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("ModelResolution")

        for assignment_name in assignment:
            if isinstance(assignment_name, int):
                raise ValueError("Mesh operation applies to objects only.")

        if defeature_length is None:
            props = dict({"Objects": assignment, "UseAutoLength": True})
        else:
            if not isinstance(defeature_length, str):
                defeature_length = str(defeature_length) + "mm"

            props: dict[str, Any] = dict(
                {
                    "Type": "DefeatureBased",
                    "Objects": assignment,
                    "UseAutoLength": False,
                    "DefeatureLength": defeature_length,
                }
            )

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_surface_mesh(
        self, assignment: list | str | int | Object3d, level: int, name: str | None = None
    ) -> MeshOperation | bool:
        """Assign a surface mesh level to one or more objects.

        Parameters
        ----------
        assignment : list, int, str, or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            One or more names of the objects.
        level : int
            Level of the surface mesh. Options are ``1`` through ``10``
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignTrueSurfOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")

        """
        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("SurfApprox")

        props: dict[str, Any] = dict(
            {
                "Type": "SurfApproxBased",
                "CurvedSurfaceApproxChoice": "UseSlider",
                "Objects": [],
                "Faces": [],
                "SliderMeshSettings": level,
            }
        )

        assignment = self._app.modeler.convert_to_selections(assignment, True)

        for sel in assignment:
            if isinstance(sel, str):
                props["Objects"].append(sel)
            elif isinstance(sel, int):
                props["Faces"].append(sel)

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_surface_mesh_manual(
        self,
        assignment: list | int | str | Object3d,
        surface_deviation: float | int | str | None = None,
        normal_dev: float | int | str | None = None,
        aspect_ratio: int | None = None,
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign a surface mesh to a list of faces.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.elements_3d.FacePrimitive`
            List of faces to apply the surface mesh to.
        surface_deviation : float, int, or str, optional
            Surface deviation. The default is ``None``. You can specify a float value, a number with units, or `"inf"`.
        normal_dev : float, int or str, optional
            Normal deviation. The default is ``None``.
        aspect_ratio : int, optional
            Aspect ratio. The default is ``None``.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignTrueSurfOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh_manual(o.id, 1e-6, aspect_ratio=3, name="Surface_Manual")

        """
        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("ModelResolution")

        surf_dev_enable = 2
        normal_dev_enable = 2
        aspect_ratio_enable = 2

        if not surface_deviation:
            surf_dev_enable = 0
            surface_deviation = "0.0001mm"
        elif surface_deviation == "inf":
            surf_dev_enable = 1
        if not normal_dev:
            normal_dev_enable = 1
            normal_dev = 1

        if not aspect_ratio:
            aspect_ratio_enable = 1
            aspect_ratio = 10

        props: dict[str, Any] = dict(
            {
                "Type": "SurfApproxBased",
                "Objects": [],
                "Faces": [],
                "CurvedSurfaceApproxChoice": "ManualSettings",
                "SurfDevChoice": surf_dev_enable,
                "SurfDev": str(surface_deviation),
                "NormalDevChoice": normal_dev_enable,
                "NormalDev": str(normal_dev),
                "AspectRatioChoice": aspect_ratio_enable,
                "AspectRatio": str(aspect_ratio),
            }
        )

        assignment = self._app.modeler.convert_to_selections(assignment, True)

        for sel in assignment:
            if isinstance(sel, str):
                props["Objects"].append(sel)
            elif isinstance(sel, int):
                props["Faces"].append(sel)

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_surf_priority_for_tau(
        self,
        assignment: list | str | Object3d,
        surface_priority: int = 0,
    ) -> MeshOperation | bool:
        """Assign a surface representation priority for the TAU mesh.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of objects to apply a surface representation priority to.
        surface_priority : int, optional
            Surface representation priority. The default is ``0``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignSurfPriorityForTauOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> hfss.mesh.assign_surf_priority_for_tau(assignment=o)

        """
        meshop_name = generate_unique_name("SurfaceRepPriority")

        props: dict[str, Any] = dict(
            {"Type": "SurfaceRepPriority", "Objects": [], "Faces": [], "SurfaceRepPriority": surface_priority}
        )

        assignment = self._app.modeler.convert_to_selections(assignment, True)

        for sel in assignment:
            if isinstance(sel, str):
                props["Objects"].append(sel)
            elif isinstance(sel, int):
                props["Faces"].append(sel)

        mop = MeshOperation(self, meshop_name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_curvature_extraction(
        self,
        assignment: list | str | Object3d,
        disabled_for_faceted: bool = True,
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign curvature extraction.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of objects or faces.
        disabled_for_faceted : bool, optional
            Whether curvature extraction is enabled for faceted surfaces. The default is ``True``.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignCurvatureExtractionOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> hfss.solution_type = "SBR+"
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> hfss.mesh.assign_curvature_extraction(assignment=o)

        """
        if self._app.solution_type != "SBR+":
            raise MethodNotSupportedError
        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("CurvilinearElements")

        props: dict[str, Any] = dict(
            {
                "Type": "CurvatureExtraction",
                "Objects": [],
                "Faces": [],
                "DisableForFacetedSurfaces": disabled_for_faceted,
            }
        )

        assignment = self._app.modeler.convert_to_selections(assignment, True)

        for sel in assignment:
            if isinstance(sel, str):
                props["Objects"].append(sel)
            elif isinstance(sel, int):
                props["Faces"].append(sel)

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_length_mesh(
        self,
        assignment: list | str | Object3d,
        inside_selection: bool = True,
        maximum_length: int = 1,
        maximum_elements: int = 1000,
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign a length for the model resolution.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of object names or face IDs.
        inside_selection : bool, optional
            Whether the length mesh is inside the selection. The default is ``True``.
        maximum_length : str, float, optional
            Maximum element length. The default is ``1``. When ``None``,
            this parameter is disabled.
        maximum_elements : int, optional
            Maximum number of elements. The default is ``1000``. When ``None``, this parameter
            is disabled.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignLengthOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> hfss.mesh.assign_length_mesh(assignment=o)

        """
        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("length")

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
            raise ValueError("Maximum length and maximum elements are not specified.")

        props: dict[str, Any] = dict(
            {
                "Type": "LengthBased",
                "RefineInside": inside_selection,
                "Enabled": True,
                "Objects": [],
                "Faces": [],
                "RestrictElem": restrictel,
                "NumMaxElem": numel,
                "RestrictLength": restrictlength,
                "MaxLength": length,
            }
        )

        assignment = self._app.modeler.convert_to_selections(assignment, True)

        for sel in assignment:
            if isinstance(sel, str):
                props["Objects"].append(sel)
            elif isinstance(sel, int) and not inside_selection:
                props["Faces"].append(sel)

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_skin_depth(
        self,
        assignment: list | str | Object3d | EdgePrimitive,
        skin_depth: str = "0.2mm",
        maximum_elements: int | None = None,
        triangulation_max_length: str = "0.1mm",
        layers_number: str = "2",
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign a skin depth for the mesh refinement.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
           List of the object names, face IDs or edges IDs for Maxwell 2D design.
        skin_depth : str, float, optional
            Skin depth value.
            It can be either provided as a float or as a string.
            The default is ``"0.2mm"``.
        maximum_elements : int, optional
            Maximum number of elements. The default is ``None``, which means this parameter is disabled.
        triangulation_max_length : str, optional
            Maximum surface triangulation length with units. The default is ``"0.1mm"``.
        layers_number : str, optional
            Number of layers. The default is ``"2"``.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignSkinDepthOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> hfss.mesh.assign_skin_depth(assignment=o)

        """
        assignment = self._app.modeler.convert_to_selections(assignment, True)

        if self._app.design_type not in ["HFSS", "Maxwell 3D", "Maxwell 2D"]:
            raise MethodNotSupportedError

        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("SkinDepth")

        if self._app.design_type == "Maxwell 2D":
            props = dict(
                {
                    "Type": "SkinDepthBased",
                    "Edges": assignment,
                    "SkinDepth": skin_depth,
                    "NumLayers": layers_number,
                }
            )
        else:
            if maximum_elements is None:
                restrictlength = False
                maximum_elements = 1000
            else:
                restrictlength = True

            props: dict[str, Any] = dict(
                {
                    "Type": "SkinDepthBased",
                    "Enabled": True,
                    "Objects": [],
                    "Faces": [],
                    "RestrictElem": restrictlength,
                    "NumMaxElem": str(maximum_elements),
                    "SkinDepth": skin_depth,
                    "SurfTriMaxLength": triangulation_max_length,
                    "NumLayers": layers_number,
                }
            )

            for sel in assignment:
                if isinstance(sel, str):
                    props["Objects"].append(sel)
                elif isinstance(sel, int):
                    props["Faces"].append(sel)

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_curvilinear_elements(
        self, assignment: list | str | Object3d, enable: bool = True, name: str | None = None
    ) -> MeshOperation | bool:
        """Assign curvilinear elements.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of objects or faces.
        enable : bool, optional
            Whether to apply curvilinear elements. The default is ``True``.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignApplyCurvlinearElementsOp

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> hfss.mesh.assign_curvilinear_elements(assignment=o)

        """
        if self._app.design_type != "HFSS" and self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError

        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("CurvilinearElements")

        props: dict[str, Any] = dict({"Type": "Curvilinear", "Objects": [], "Faces": [], "Apply": enable})

        assignment = self._app.modeler.convert_to_selections(assignment, True)

        for sel in assignment:
            if isinstance(sel, str):
                props["Objects"].append(sel)
            elif isinstance(sel, int):
                props["Faces"].append(sel)

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_rotational_layer(
        self,
        assignment: list | str | Object3d,
        layers_number: int = 3,
        total_thickness: str = "1mm",
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign a rotational layer mesh.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of objects.
        layers_number : int, optional
            Number of layers to create in the radial direction, starting from
            the faces most adjacent to the band. The default is ``3``, which is the maximum.
        total_thickness : str, optional
            Total thickness of all layers with units. The default is ``"1mm"``.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignRotationalLayerOp

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell3d
        >>> app = Maxwell3d()
        >>> box = app.modeler.create_box([0, 0, 0], [10, 10, 10])
        >>> app.mesh.assign_rotational_layer(assignment=box)

        """
        assignment = self._app.modeler.convert_to_selections(assignment, True)

        if self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError

        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("RotationalLayer")

        seltype = "Objects"
        props = dict(
            {
                "Type": "RotationalLayerMesh",
                seltype: assignment,
                "Number of Layers": str(layers_number),
                "Total Layer Thickness": total_thickness,
            }
        )

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_edge_cut(
        self, assignment: list | str | Object3d, layer_thickness: str = "1mm", name: str | None = None
    ) -> MeshOperation | bool:
        """Assign an edge cut layer mesh.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of objects.
        layer_thickness : str, optional
            Thickness of the layer with units. The default is ``"1mm"``.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignRotationalLayerOp

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell3d
        >>> app = Maxwell3d()
        >>> box = app.modeler.create_box([0, 0, 0], [10, 10, 10])
        >>> app.mesh.assign_edge_cut(assignment=box)

        """
        assignment = self._app.modeler.convert_to_selections(assignment, True)

        if self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError

        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("EdgeCut")

        seltype = "Objects"
        props = dict({"Type": "EdgeCutLayerMesh", seltype: assignment, "Layer Thickness": layer_thickness})

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_density_control(
        self,
        assignment: list | str | Object3d,
        refine_inside: bool = True,
        maximum_element_length: str | None = None,
        layers_number: int | None = None,
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign density control.

        Parameters
        ----------
        assignment : list or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            List of objects.
        refine_inside : bool, optional
            Whether to refine inside objects. The default is ``True``.
        maximum_element_length : str, optional
            Maximum element length with units. The default is ``None``,
            which disables this parameter.
        layers_number : int, optional
            Number of layers. The default is ``None``, which disables
            this parameter.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh operation object.

        References
        ----------
        >>> oModule.AssignDensityControlOp

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell3d
        >>> app = Maxwell3d()
        >>> box = app.modeler.create_box([0, 0, 0], [10, 10, 10])
        >>> app.mesh.assign_density_control(assignment=box)

        """
        assignment = self._app.modeler.convert_to_selections(assignment, True)

        if self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError

        if name and name in self.operation_names:
            name = generate_unique_name(name)
        else:
            name = generate_unique_name("CloneMeshDensity")

        seltype = "Objects"

        if not maximum_element_length:
            restr = False
            restrval = "0mm"
        else:
            restr = True
            restrval = maximum_element_length

        if not layers_number:
            restrlay = False
            restrlaynum = "1"
        else:
            restrlay = True
            restrlaynum = str(layers_number)

        props = dict(
            {
                "Type": "DensityControlBased",
                "RefineInside": refine_inside,
                seltype: assignment,
                "RestrictMaxElemLength": restr,
                "MaxElemLength": restrval,
                "RestrictLayersNum": restrlay,
                "LayersNum": restrlaynum,
            }
        )
        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_cylindrical_gap(
        self,
        entity: list | str | Object3d,
        name: str | None = None,
        band_mapping_angle: float | None = None,
        clone_mesh: bool = False,
        moving_side_layers: int = 1,
        static_side_layers: int = 1,
    ) -> MeshOperation | bool:
        """Assign a cylindrical gap for a 2D or 3D design to enable a clone mesh and associated band mapping angle.

        Parameters
        ----------
        entity : int or str or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            Object to assign cylindrical gap to.
        name : str, optional
            Name of the mesh. The default is ``None``, in which
            case the default name is used.
        clone_mesh : bool, optional
            Whether to clone the mesh. This parameter is valid only for 3D design.
            The default is ``False``. If ``True``, the solid bodies adjacent to the band
            are detected to identify the clone object.
        band_mapping_angle : int, optional
            Band mapping angle in degrees.
            The recommended band mapping angle (the angle the rotor rotates in one time step) typically
            equals the rotational speed multiplied by the time step.
            The band mapping angle must be between 0.0005 and 3 degrees.
            The default is ``None``.

            - For a 2D design, if a value is provided, the option ``Use band mapping angle``
              is automatically enabled.
            - For a 3D design, the ``Clone Mesh`` option has to be enabled first.
        moving_side_layers : int, optional
            Number of mesh layers on the moving side.
            The valid ranges are integers greater or equal to 1.
            This parameter is valid only for a 3D design.
            The default is ``1``.
        static_side_layers : int, optional
            Number of mesh layers on the static side.
            The valid ranges are integers greater than or equal to 1.
            This parameter is valid only for a 3D design.
            The default is ``1``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation` or bool
            Mesh operation object or ``False`` if it fails.

        References
        ----------
        >>> oModule.AssignCylindricalGapOp

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell3d
        >>> app = Maxwell3d()
        >>> box = app.modeler.create_box([0, 0, 0], [10, 10, 10])
        >>> app.mesh.assign_cylindrical_gap(entity=box)

        """
        if self._app.design_type != "Maxwell 2D" and self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError

        entity = self._app.modeler.convert_to_selections(entity, True)
        if len(entity) > 1:
            raise ValueError("Cylindrical gap treatment cannot be assigned to multiple objects.")

        ops = []
        for _, op in self.operations.items():
            if op.operation_type in ["Cylindrical Gap Based", "CylindricalGap"]:
                ops.append(op)

        if len(ops) > 0:
            raise ValueError("Cylindrical gap treatment cannot be assigned to multiple objects.")

        if band_mapping_angle and band_mapping_angle > 3:
            raise ValueError("Band mapping angle must be between 0.0005 and 3 deg.")

        if not name:
            name = generate_unique_name("CylindricalGap")

        if self._app.design_type == "Maxwell 3D":
            if moving_side_layers < 1:
                raise ValueError("Moving side layers must be an integer greater or equal to 1.")

            if static_side_layers < 1:
                raise ValueError("Static side layers must be an integer greater or equal to 1.")

            if clone_mesh and not band_mapping_angle:
                band_mapping_angle = 3

            props = dict(
                {
                    "Type": "AssignCylindricalGapOp",
                    "Objects": entity,
                    "CloneMesh": clone_mesh,
                    "BandMappingAngle": str(band_mapping_angle) + "deg",
                    "MovingSideLayers": moving_side_layers,
                    "StaticSideLayers": static_side_layers,
                }
            )
        elif self._app.design_type == "Maxwell 2D":
            if band_mapping_angle:
                use_band_mapping_angle = True
            else:
                use_band_mapping_angle = False
                band_mapping_angle = 3
            props = dict(
                {
                    "Type": "AssignCylindricalGapOp",
                    "Objects": entity,
                    "UseBandMappingAngle": use_band_mapping_angle,
                    "BandMappingAngle": str(band_mapping_angle) + "deg",
                }
            )

        mesh_operation = MeshOperation(self, name, props)

        return mesh_operation.create()

    @pyaedt_function_handler()
    def generate_mesh(self, name: str) -> bool:
        """Generate the mesh for a design.

        Parameters
        ----------
        name : str
            Name of the simulation setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oDesign.GenerateMesh

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell3d
        >>> m3d = Maxwell3d()
        >>> m3d.create_setup(name="Setup1")
        >>> o = m3d.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> m3d.mesh.assign_length_mesh(assignment=o)
        >>> m3d.mesh.generate_mesh("Setup1")

        """
        return self._odesign.GenerateMesh(name) == 0

    @pyaedt_function_handler()
    def delete_mesh_operations(self, mesh_type: str | list[str] | None = None) -> bool:
        """Remove mesh operations from a design.
        This method only works for ``"Length Based"``, and ``"Surface Approximation Based"``.

        Parameters
        ----------
        mesh_type : str, list[str], optional
           Type of the mesh operation to delete. The default is ``None``, in which
           case all mesh operations are deleted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.DeleteOp

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell3d
        >>> m3d = Maxwell3d()
        >>> o = m3d.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> m3d.mesh.assign_length_mesh(assignment=o)
        >>> m3d.mesh.delete_mesh_operations()

        """
        # This method only works for the following mesh operations
        mesh_op_types_compatible = ["Length Based", "Surface Approximation Based"]

        mesh_op_types = mesh_type

        if isinstance(mesh_op_types, str) and mesh_op_types in mesh_op_types_compatible:
            mesh_op_types = [mesh_type]
        elif not mesh_op_types:
            mesh_op_types = []
            for _, m in self.operations.items():
                if m.operation_type and m.operation_type in mesh_op_types_compatible:
                    mesh_op_types.append(m.operation_type)

        for mesh_op_type in mesh_op_types:
            if mesh_op_type not in mesh_op_types_compatible:
                raise ValueError(f"{mesh_op_type} is not a valid mesh type.")
            opnames = self._app.omeshmodule.GetOperationNames(mesh_op_type)
            if opnames:
                self._app.omeshmodule.DeleteOp(opnames)
        return True
