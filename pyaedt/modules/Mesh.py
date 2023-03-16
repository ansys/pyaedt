"""
This module contains the `Mesh` class.
"""
from __future__ import absolute_import  # noreorder

from collections import OrderedDict
import os
import shutil

from pyaedt.application.design_solutions import model_names
from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file
from pyaedt.generic.general_methods import MethodNotSupportedError
from pyaedt.generic.general_methods import PropsManager
from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler

meshers = {
    "HFSS": "MeshSetup",
    "Icepak": "MeshRegion",
    "HFSS3DLayout": "MeshSetup",
    "Maxwell 2D": "MeshSetup",
    "Maxwell 3D": "MeshSetup",
    "Q3D Extractor": "MeshSetup",
    "Mechanical": "MeshSetup",
    "2D Extractor": "MeshSetup",
}

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
    "Total Layer Thickness": "Total Layer Thickness",
    "Number of Layers": "Number of Layers",
    "RestrictMaxElemLength": "Restrict Max Element Length",
    "MaxElemLength": "Max Element Length",
    "RestrictLayersNum": "Restrict Layers Number",
    "LayersNum": "Number of layers",
    "Layer Thickness": "Layer Thickness",
}


class MeshProps(OrderedDict):
    """AEDT Mesh Component Internal Parameters."""

    def __setitem__(self, key, value):
        pyaedt_mesh_attr = list(self._pyaedt_mesh.__dict__.keys())
        if key in list(self._pyaedt_mesh.props.keys()):
            OrderedDict.__setitem__(self, key, value)
            if key in ["Edges", "Faces", "Objects"]:
                if "_meshicepak" in pyaedt_mesh_attr or "_mesh3dlayout" in pyaedt_mesh_attr:
                    self._pyaedt_mesh.update_assignment()
                else:
                    self._pyaedt_mesh._mesh.omeshmodule.ReassignOp(self._pyaedt_mesh.name, ["{}:=".format(key), value])
            else:
                if "_meshicepak" in pyaedt_mesh_attr or "_mesh3dlayout" in pyaedt_mesh_attr:
                    self._pyaedt_mesh.update()
                else:
                    mesh_obj = self._pyaedt_mesh._mesh._app.odesign.GetChildObject("Mesh").GetChildObject(
                        self._pyaedt_mesh.name
                    )
                    if key in mesh_props.keys():
                        if key == "SurfaceRepPriority":
                            if value == 0:
                                value = "Normal"
                            else:
                                value = "High"

                        mesh_obj.SetPropValue(mesh_props[key], value)
        else:
            if not "_meshicepak" in pyaedt_mesh_attr or not "_mesh3dlayout" in pyaedt_mesh_attr:
                mesh_obj = self._pyaedt_mesh._mesh._app.odesign.GetChildObject("Mesh").GetChildObject(
                    self._pyaedt_mesh.name
                )
                if key in mesh_obj.GetPropNames() or key.replace(" ", "_") in mesh_obj.GetPropNames():
                    OrderedDict.__setitem__(self, key, value)

    def __init__(self, mesh_object, props):
        OrderedDict.__init__(self)
        if props:
            for key, value in props.items():
                if isinstance(value, (OrderedDict, OrderedDict)):
                    OrderedDict.__setitem__(self, key, MeshProps(mesh_object, value))
                else:
                    OrderedDict.__setitem__(self, key, value)
        self._pyaedt_mesh = mesh_object

    def _setitem_without_update(self, key, value):
        OrderedDict.__setitem__(self, key, value)


class MeshOperation(PropsManager, object):
    """MeshOperation class.

    Parameters
    ----------
    mesh : class:`pyaedt.modules.Mesh.Mesh or :class:`pyaedt.modules.MeshIcepak.MeshIcepak`

    """

    def __init__(self, mesh, name, props, meshoptype):
        self._mesh = mesh
        self.props = MeshProps(self, props)
        self.type = meshoptype
        self._name = name

    @pyaedt_function_handler()
    def _get_args(self):
        """Retrieve arguments."""
        props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @property
    def name(self):
        """Name of the mesh operation.

        Returns
        -------
        str
           Name of the mesh operation.

        """
        return self._name

    @name.setter
    def name(self, meshop_name):
        if meshop_name not in self._mesh._app.odesign.GetChildObject("Mesh").GetChildNames():
            self._mesh._app.odesign.GetChildObject("Mesh").GetChildObject(self.name).SetPropValue("Name", meshop_name)
            self._name = meshop_name
        else:
            self._mesh.logger.warning("Name %s already assigned in the design", meshop_name)

    @pyaedt_function_handler()
    def create(self):
        """Create a mesh.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.type == "SurfApproxBased":
            self._mesh.omeshmodule.AssignTrueSurfOp(self._get_args())
        elif self.type == "DefeatureBased":
            self._mesh.omeshmodule.AssignModelResolutionOp(self._get_args())
        elif self.type == "SurfaceRepPriority":
            self._mesh.omeshmodule.AssignSurfPriorityForTauOp(self._get_args())
        elif self.type == "LengthBased":
            self._mesh.omeshmodule.AssignLengthOp(self._get_args())
        elif self.type == "SkinDepthBased":
            self._mesh.omeshmodule.AssignSkinDepthOp(self._get_args())
        elif self.type == "Curvilinear":
            self._mesh.omeshmodule.AssignApplyCurvlinearElementsOp(self._get_args())
        elif self.type == "RotationalLayerMesh":
            self._mesh.omeshmodule.AssignRotationalLayerOp(self._get_args())
        elif self.type == "EdgeCutLayerMesh":
            self._mesh.omeshmodule.AssignEdgeCutLayerOp(self._get_args())
        elif self.type == "DensityControlBased":
            self._mesh.omeshmodule.AssignDensityControlOp(self._get_args())
        elif self.type == "Icepak":
            self._mesh.omeshmodule.AssignMeshOperation(self._get_args())
        elif self.type == "CurvatureExtraction":
            self._mesh.omeshmodule.AssignCurvatureExtractionOp(self._get_args())
        elif self.type == "CylindricalGap":
            self._mesh.omeshmodule.AssignCylindricalGapOp(self._get_args())
        else:
            return False
        return True

    @pyaedt_function_handler()
    def _change_property(self, name, arg):
        """Update properties of the mesh operation.

        Parameters
        ----------
        name : str
            Name of the mesh operation.
        arg : list
            List of the properties to update. For example,
            ``["NAME:ChangedProps", ["NAME:Max Length", "Value:=", "2mm"]]``.

        Returns
        -------
        list
            List of changed properties of the mesh operation.

        """
        arguments = ["NAME:AllTabs", ["NAME:MeshSetupTab", ["NAME:PropServers", "MeshSetup:{}".format(name)], arg]]
        _retry_ntimes(5, self._mesh._app.odesign.ChangeProperty, arguments)

    @pyaedt_function_handler()
    def delete(self):
        """Delete the mesh.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteOp
        """
        self._mesh.omeshmodule.DeleteOp([self.name])
        for el in self._mesh.meshoperations[:]:
            if el.name == self.name:
                self._mesh.meshoperations.remove(el)
        return True


class Mesh(object):
    """Manages AEDT mesh functions for 2D and 3D solvers (HFSS, Maxwell, and Q3D).

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`

    Examples
    --------
    Basic usage demonstrated with an HFSS design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> o = aedtapp.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
    >>> mr1 = aedtapp.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
    """

    def __init__(self, app):
        self._app = app
        self._odesign = self._app.odesign
        self.modeler = self._app.modeler
        self.logger = self._app.logger
        self.id = 0
        self._meshoperations = None
        self._globalmesh = None

    @pyaedt_function_handler()
    def __getitem__(self, partId):
        """Get the object ``Mesh`` for a given mesh operation name.

        Parameters
        ----------
        partId : str
            Mesh operation name.

        Returns
        -------
        :class:`pyaedt.mesh.meshoperations`
            Returns None if the part ID or the object name is not found.

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> o = aedtapp.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = aedtapp.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        >>> mr2 = aedtapp.mesh[mr1.name]
        """

        if partId in self.meshoperation_names:
            mesh_op_selected = [mesh_op for mesh_op in self.meshoperations if mesh_op.name == partId]
            return mesh_op_selected[0]
        return None

    @property
    def meshoperations(self):
        """Return the available mesh operations.

        Returns
        ----------
        List
            List of :class:`pyaedt.modules.Mesh.MeshOperation`
                        List of mesh operation object.

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> o = aedtapp.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = aedtapp.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        >>> mesh_operations_list = aedtapp.mesh.meshoperations
        """
        if self._meshoperations is None:
            self._meshoperations = self._get_design_mesh_operations()
        return self._meshoperations

    @pyaedt_function_handler()
    def _refresh_mesh_operations(self):
        """Refresh all mesh operations."""

        self._meshoperations = self._get_design_mesh_operations()
        return len(self.meshoperations)

    @property
    def meshoperation_names(self):
        """Return the available mesh operation names.

        Returns
        ----------
        List
            List of mesh operation names.

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> o = aedtapp.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> mr1 = aedtapp.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        >>> mr2 = aedtapp.mesh.assign_model_resolution(o, 1e-2, "ModelRes2")
        >>> mesh_operations_names = aedtapp.mesh.meshoperation_names
        """
        if self._app._is_object_oriented_enabled():
            return list(self._app.odesign.GetChildObject("Mesh").GetChildNames())
        return []

    @property
    def initial_mesh_settings(self):
        """Return the global mesh object.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.InitialMeshSettings
        """
        if not self._globalmesh:
            self._globalmesh = self._get_design_global_mesh()
        return self._globalmesh

    @property
    def omeshmodule(self):
        """Aedt Mesh Module.

        References
        ----------

        >>> oDesign.GetModule("MeshSetup")
        """
        return self._app.omeshmodule

    @pyaedt_function_handler()
    def _get_design_global_mesh(self):
        """ """
        props = None
        try:
            props = self._app.design_properties["MeshSetup"]["MeshSettings"]
        except:
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
            _project_dictionary = load_entire_aedt_file(temp_proj)
            try:
                props = _project_dictionary["AnsoftProject"][model_names[self._app.design_type]]["MeshSetup"][
                    "MeshSettings"
                ]
            except:
                pass
            if os.path.exists(temp_proj):
                os.remove(temp_proj)
            if os.path.exists(temp_proj + "results"):
                shutil.rmtree(temp_proj + "results", True)
        if props:
            bound = MeshOperation(self, "MeshSettings", props, "InitialMeshSettings")
            return bound
        return OrderedDict()

    @pyaedt_function_handler()
    def _get_design_mesh_operations(self):
        """ """
        meshops = []
        try:
            for ds in self.meshoperation_names:
                props = {}
                design_mesh = self._app.odesign.GetChildObject("Mesh")
                for i in design_mesh.GetChildObject(ds).GetPropNames():
                    props[i] = design_mesh.GetChildObject(ds).GetPropValue(i)
                if self._app._desktop.GetVersion()[0:6] < "2023.1":
                    if self._app.design_properties:
                        props_parsed = self._app.design_properties["MeshSetup"]["MeshOperations"][ds]
                        if "Edges" in props_parsed.keys():
                            props["Edges"] = props_parsed["Edges"]
                        if "Faces" in props_parsed.keys():
                            props["Faces"] = props_parsed["Faces"]
                        if "Objects" in props_parsed.keys():
                            props["Objects"] = []
                            for comp in props_parsed["Objects"]:
                                props["Objects"].append(comp)
                else:
                    props["Objects"] = []
                    props["Faces"] = []
                    props["Edges"] = []
                    assigned_id = self.omeshmodule.GetMeshOpAssignment(ds)
                    for comp_id in assigned_id:
                        if int(comp_id) in self._app.modeler.objects.keys():
                            props["Objects"].append(self._app.modeler.oeditor.GetObjectNameByID(comp_id))
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

                meshops.append(MeshOperation(self, ds, props, props["Type"]))
        except:
            pass
        return meshops

    @pyaedt_function_handler()
    def assign_surface_mesh(self, names, level, meshop_name=None):
        """Assign a surface mesh level to one or more objects.

        Parameters
        ----------
        names : list
            One or more names of the objects.
        level : int
            Level of the surface mesh. Options are ``1`` through ``10``
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignTrueSurfOp

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> o = aedtapp.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = aedtapp.mesh.assign_surface_mesh(o.id, 3, "Surface")
        """
        names = self.modeler.convert_to_selections(names, True)
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("SurfApprox")
        self.logger.info("Assigning Mesh Level " + str(level) + " to " + str(names))
        names = self._app.modeler.convert_to_selections(names, True)

        if isinstance(names[0], int):
            seltype = "Faces"
        else:
            seltype = "Objects"
        props = OrderedDict(
            {
                "Type": "SurfApproxBased",
                "CurvedSurfaceApproxChoice": "UseSlider",
                seltype: names,
                "SliderMeshSettings": level,
            }
        )
        mop = MeshOperation(self, meshop_name, props, "SurfApproxBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_surface_mesh_manual(self, names, surf_dev=None, normal_dev=None, aspect_ratio=None, meshop_name=None):
        """Assign a surface mesh to a list of faces.

        Parameters
        ----------
        names : list or str or :class:`pyaedt.modeler.elements3d.FacePrimitive`
            List of faces to apply the surface mesh to.
        surf_dev : float or str, optional
            Surface deviation. The default is ``None``. Allowed values are float, number with units or `"inf"`.
        normal_dev : float or str, optional
            Normal deviation. The default is ``None``.
        aspect_ratio : int, optional
            Aspect ratio. The default is ``None``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignTrueSurfOp

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> o = aedtapp.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = self.aedtapp.mesh.assign_surface_mesh_manual(o.id, 1e-6, aspect_ratio=3,
        ... meshop_name="Surface_Manual")
        """
        names = self.modeler.convert_to_selections(names, True)
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("ModelResolution")

        surf_dev_enable = 2
        normal_dev_enable = 2
        aspect_ratio_enable = 2

        if not surf_dev:
            surf_dev_enable = 0
            surf_dev = "0.0001mm"
        elif surf_dev == "inf":
            surf_dev_enable = 1
        if not normal_dev:
            normal_dev_enable = 1
            normal_dev = "1"

        if not aspect_ratio:
            aspect_ratio_enable = 1
            aspect_ratio = "10"

        props = OrderedDict(
            {
                "Type": "SurfApproxBased",
                "Objects": names,
                "CurvedSurfaceApproxChoice": "ManualSettings",
                "SurfDevChoice": surf_dev_enable,
                "SurfDev": surf_dev,
                "NormalDevChoice": normal_dev_enable,
                "NormalDev": normal_dev,
                "AspectRatioChoice": aspect_ratio_enable,
                "AspectRatio": aspect_ratio,
            }
        )

        mop = MeshOperation(self, meshop_name, props, "SurfApproxBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_model_resolution(self, names, defeature_length=None, meshop_name=None):
        """Assign the model resolution.

        Parameters
        ----------
        names : list
            List of objects to defeature.
        defeature_length : float, optional
            Defeaturing length in millimeters. The default is ``None``, in which case
            automatic defeaturing is used.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignModelResolutionOp

        Examples
        --------
        Basic usage demonstrated with an HFSS design:

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> o = aedtapp.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = aedtapp.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        """
        names = self.modeler.convert_to_selections(names, True)
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("ModelResolution")
        for name in names:
            if isinstance(name, int):
                self.logger.error("Mesh Operation Applies to Objects only")
                return False
        if defeature_length is None:
            props = OrderedDict({"Objects": names, "UseAutoLength": True})
        else:
            props = OrderedDict(
                {
                    "Type": "DefeatureBased",
                    "Objects": names,
                    "UseAutoLength": False,
                    "DefeatureLength": str(defeature_length) + "mm",
                }
            )

        mop = MeshOperation(self, meshop_name, props, "DefeatureBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_initial_mesh_from_slider(
        self,
        level=5,
        method="Auto",
        usedynamicsurface=True,
        useflexmesh=False,
        applycurvilinear=False,
        usefallback=True,
        usephi=True,
        automodelresolution=True,
        modelresolutionlength="0.0001mm",
    ):
        """Assign a surface mesh level to an object.

        Parameters
        ----------
        level : int, optional
            Level of the surface mesh. Options are ``1`` through ``10``. The default is ``5.``
        method : str, optional
            Meshing method. Options are ``"Auto"``, ``"AnsoftTAU"``, and ``"AnsoftClassic"``
            The default is ``"Auto"``.
        usedynamicsurface : bool, optional
            Whether to use a dynamic surface. The default is ``True``.
        useflexmesh : bool, optional
            Whether to use a flexible mesh. The default is ``False``.
        applycurvilinear : bool, optional
            Whether to apply curvilinear elements. The default is ``False``.
        usefallback : bool, optional
            Whether to retain as a fallback. The default is ``True``.
        usephi : bool, optional
            Whether to use the Phi mesher for layered geometry.
            The default is ``True``.
        automodelresolution : bool, optional
            Whether to automatically calculate the resolution length
            based on each object's effective thickness. The default is ``True``.
        modelresolutionlength : float, optional
             Resolution thickness with units if ``automodelresolution=False``.
             The default ``"0.0001mm"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.InitialMeshSettings
        """
        if self._app.design_type == "2D Extractor" or self._app.design_type == "Maxwell 2D":
            mesh_methods = ["Auto", "AnsoftClassic"]
        else:
            mesh_methods = ["Auto", "AnsoftTAU", "AnsoftClassic"]
        assert method in mesh_methods

        modelres = ["NAME:GlobalModelRes", "UseAutoLength:=", automodelresolution]
        if not automodelresolution:
            modelres.append("DefeatureLength:=")
            modelres.append(modelresolutionlength)
        surface_appr = [
            "NAME:GlobalSurfApproximation",
            "CurvedSurfaceApproxChoice:=",
            "UseSlider",
            "SliderMeshSettings:=",
            level,
        ]
        if self._app.design_type == "2D Extractor" or self._app.design_type == "Maxwell 2D":
            args = ["NAME:MeshSettings", surface_appr, modelres, "MeshMethod:=", method]
        else:
            args = [
                "NAME:MeshSettings",
                surface_appr,
                ["NAME:GlobalCurvilinear", "Apply:=", applycurvilinear],
                modelres,
                "MeshMethod:=",
                method,
                "UseLegacyFaceterForTauVolumeMesh:=",
                False,
                "DynamicSurfaceResolution:=",
                usedynamicsurface,
                "UseFlexMeshingForTAUvolumeMesh:=",
                useflexmesh,
            ]
        if self._app.design_type == "HFSS":
            args.append("UseAlternativeMeshMethodsAsFallBack:=")
            args.append(usefallback)
            args.append("AllowPhiForLayeredGeometry:=")
            args.append(usephi)
        self.omeshmodule.InitialMeshSettings(args)
        return True

    @pyaedt_function_handler()
    def assign_surf_priority_for_tau(self, object_lists, surfpriority=0):
        """Assign a surface representation priority for the TAU mesh.

        Parameters
        ----------
        object_lists : list
            List of objects to apply a surface representation
            priority to.
        surfpriority : int, optional
            Surface representation priority. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignSurfPriorityForTauOp
        """
        meshop_name = generate_unique_name("SurfaceRepPriority")
        props = OrderedDict({"Type": "SurfaceRepPriority", "Objects": object_lists, "SurfaceRepPriority": surfpriority})
        mop = MeshOperation(self, meshop_name, props, "SurfaceRepPriority")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def generate_mesh(self, name):
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
        """
        return self._odesign.GenerateMesh(name) == 0

    @pyaedt_function_handler()
    def delete_mesh_operations(self, mesh_type=None):
        """Remove mesh operations from a design.

        Parameters
        ----------
        mesh_type : optional
           Type of the mesh operation to delete. The default is ``None``, in which
           case all mesh operations are deleted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteOp
        """

        mesh_op_types = ["Length Based", "Surface Approximation Based"]

        if mesh_type:
            if mesh_type in mesh_op_types:
                mesh_op_types = [mesh_type]

        for mesh_op_type in mesh_op_types:
            opnames = self.omeshmodule.GetOperationNames(mesh_op_type)
            if opnames:
                self.omeshmodule.DeleteOp(opnames)
            for el in self.meshoperations[:]:
                if el.name in opnames:
                    self.meshoperations.remove(el)

        return True

    @pyaedt_function_handler()
    def assign_length_mesh(self, names, isinside=True, maxlength=1, maxel=1000, meshop_name=None):
        """Assign a length for the model resolution.

        Parameters
        ----------
        names : list
            List of object names or face IDs.
        isinside : bool, optional
            Whether the length mesh is inside the selection. The default is ``True``.
        maxlength : str, float, optional
            Maximum element length. The default is ``1``. When ``None``,
            this parameter is disabled.
        maxel : int, optional
            Maximum number of elements. The default is ``1000``. When ``None``, this parameter
            is disabled.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignLengthOp
        """
        names = self.modeler.convert_to_selections(names, True)
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("length")

        if maxlength is None:
            restrictlength = False
        else:
            restrictlength = True
        length = self.modeler.modeler_variable(maxlength)

        if maxel is None:
            restrictel = False
            numel = "1000"
        else:
            restrictel = True
            numel = str(maxel)
        if maxlength is None and maxel is None:
            self.logger.error("mesh not assigned due to incorrect settings")
            return
        names = self._app.modeler.convert_to_selections(names, True)

        if isinstance(names[0], int) and not isinside:
            seltype = "Faces"
        elif isinstance(names[0], str):
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self.logger.error("Error in Assignment")
            return
        props = OrderedDict(
            {
                "Type": "LengthBased",
                "RefineInside": isinside,
                "Enabled": True,
                seltype: names,
                "RestrictElem": restrictel,
                "NumMaxElem": numel,
                "RestrictLength": restrictlength,
                "MaxLength": length,
            }
        )

        mop = MeshOperation(self, meshop_name, props, "LengthBased")
        mop.create()
        for meshop in self.meshoperations[:]:
            if meshop.name == mop.name:
                meshop.delete()
                break
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_skin_depth(
        self, names, skindepth, maxelements=None, triangulation_max_length="0.1mm", numlayers="2", meshop_name=None
    ):
        """Assign a skin depth for the mesh refinement.

        Parameters
        ----------
        names : list
           List of the object names or face IDs.
        skindepth : bool
            Whether the length mesh is inside the selection. The default is ``True``.
        maxelements : int, optional
            Maximum number of elements. The default is ``None``, which means this parameter is disabled.
        triangulation_max_length : str, optional
            Maximum surface triangulation length with units. The default is ``"0.1mm"``.
        numlayers : str, optional
            Number of layers. The default is ``"2"``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignSkinDepthOp
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._app.design_type != "HFSS" and self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("SkinDepth")

        if maxelements is None:
            restrictlength = False
            maxelements = "1000"
        else:
            restrictlength = True
        names = self._app.modeler.convert_to_selections(names, True)

        if isinstance(names[0], int):
            seltype = "Faces"
        elif isinstance(names[0], str):
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self.logger.error("Error in Assignment")
            return

        props = OrderedDict(
            {
                "Type": "SkinDepthBased",
                "Enabled": True,
                seltype: names,
                "RestrictElem": restrictlength,
                "NumMaxElem": str(maxelements),
                "SkinDepth": skindepth,
                "SurfTriMaxLength": triangulation_max_length,
                "NumLayers": numlayers,
            }
        )

        mop = MeshOperation(self, meshop_name, props, "SkinDepthBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_curvilinear_elements(self, names, enable=True, meshop_name=None):
        """Assign curvilinear elements.

        Parameters
        ----------
        names : list
            List of objects or faces.
        enable : bool, optional
            Whether to apply curvilinear elements. The default is ``True``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignApplyCurvlinearElementsOp
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._app.design_type != "HFSS" and self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("CurvilinearElements")
        names = self._app.modeler.convert_to_selections(names, True)

        if isinstance(names[0], int):
            seltype = "Faces"
        elif isinstance(names[0], str):
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self.logger.error("Error in Assignment")
            return
        props = OrderedDict({"Type": "Curvilinear", seltype: names, "Apply": enable})
        mop = MeshOperation(self, meshop_name, props, "Curvilinear")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_curvature_extraction(self, names, disable_for_faceted_surf=True, meshop_name=None):
        """Assign curvature extraction.

         Parameters
         ----------
         names : list
            List of objects or faces.
         disable_for_faceted_surf : bool, optional
            Whether curvature extraction is enabled for faceted surfaces.
            The default is ``True``.
         meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

         Returns
         -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignCurvatureExtractionOp
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._app.solution_type != "SBR+":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("CurvilinearElements")
        names = self._app.modeler.convert_to_selections(names, True)
        if isinstance(names[0], int):
            seltype = "Faces"
        elif isinstance(names[0], str):
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self.logger.error("Error in Assignment")
            return
        props = OrderedDict(
            {"Type": "CurvatureExtraction", seltype: names, "DisableForFacetedSurfaces": disable_for_faceted_surf}
        )
        mop = MeshOperation(self, meshop_name, props, "CurvatureExtraction")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_rotational_layer(self, names, num_layers=3, total_thickness="1mm", meshop_name=None):
        """Assign a rotational layer mesh.

        Parameters
        ----------
        names : list
            List of objects.
        num_layers : int, optional
            Number of layers to create in the radial direction, starting from
            the faces most adjacent to the band. The default is ``3``, which is the maximum.
        total_thickness : str, optional
            Total thickness of all layers with units. The default is ``"1mm"``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignRotationalLayerOp
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("RotationalLayer")
        seltype = "Objects"
        props = OrderedDict(
            {
                "Type": "RotationalLayerMesh",
                seltype: names,
                "Number of Layers": str(num_layers),
                "Total Layer Thickness": total_thickness,
            }
        )

        mop = MeshOperation(self, meshop_name, props, "RotationalLayerMesh")
        mop.create()
        mop.props["Total Layer Thickness"] = total_thickness
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_edge_cut(self, names, layer_thickness="1mm", meshop_name=None):
        """Assign an edge cut layer mesh.

        Parameters
        ----------
        names : list
            List of objects.
        layer_thickness :
            Thickness of the layer with units. The default is ``"1mm"``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignRotationalLayerOp
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("EdgeCut")
        seltype = "Objects"
        props = OrderedDict({"Type": "EdgeCutLayerMesh", seltype: names, "Layer Thickness": layer_thickness})

        mop = MeshOperation(self, meshop_name, props, "EdgeCutLayerMesh")
        mop.create()
        mop.props["Layer Thickness"] = layer_thickness
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def assign_density_control(self, names, refine_inside=True, maxelementlength=None, layerNum=None, meshop_name=None):
        """Assign density control.

        Parameters
        ----------
        names : list
            List of objects.
        refine_inside : bool, optional
            Whether to refine inside objects. The default is ``True``.
        maxelementlength : str, optional
            Maximum element length with units. The default is ``None``,
            which disables this parameter.
        layerNum : int, optional
            Number of layers. The default is ``None``, which disables
            this parameter.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh operation object.

        References
        ----------

        >>> oModule.AssignDensityControlOp
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._app.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("CloneMeshDensity")
        seltype = "Objects"
        if not maxelementlength:
            restr = False
            restrval = "0mm"
        else:
            restr = True
            restrval = maxelementlength
        if not layerNum:
            restrlay = False
            restrlaynum = "1"
        else:
            restrlay = True
            restrlaynum = str(layerNum)
        props = OrderedDict(
            {
                "Type": "DensityControlBased",
                "RefineInside": refine_inside,
                seltype: names,
                "RestrictMaxElemLength": restr,
                "MaxElemLength": restrval,
                "RestrictLayersNum": restrlay,
                "LayersNum": restrlaynum,
            }
        )
        mop = MeshOperation(self, meshop_name, props, "DensityControlBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop
