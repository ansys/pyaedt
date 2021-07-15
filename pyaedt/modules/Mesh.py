"""
This module contains the `Mesh` class.
"""

from __future__ import absolute_import
from ..generic.general_methods import aedt_exception_handler, generate_unique_name, MethodNotSupportedError

from ..application.DataHandlers import dict2arg
from collections import OrderedDict

meshers = {"HFSS": "MeshSetup",
           "Icepak": "MeshRegion",
           "HFSS3DLayout": "MeshSetup",
           "Maxwell 2D": "MeshSetup",
           "Maxwell 3D": "MeshSetup",
           "Q3D Extractor": "MeshSetup"}


class MeshOperation(object):
    """MeshOperation class.
    
    Parameters
    ----------
    parent :
    
    name:
    
    props :
    
    meshoptpe :
    
    """
    def __init__(self, parent, name, props, meshoptype):
        self._parent = parent
        self.name = name
        self.props = props
        self.type = meshoptype

    @aedt_exception_handler
    def _get_args(self):
        """Retrieve arguments."""
        props = self.props
        arg = ["NAME:" + self.name]
        dict2arg(props, arg)
        return arg

    @aedt_exception_handler
    def create(self):
        """Create a mesh.
        
        Returns
        -------
        type
        
        """
        if self.type == "SurfApproxBased":
            self._parent.omeshmodule.AssignTrueSurfOp(self._get_args())
        elif self.type == "DefeatureBased":
            self._parent.omeshmodule.AssignModelResolutionOp(self._get_args())
        elif self.type == "SurfaceRepPriority":
            self._parent.omeshmodule.AssignSurfPriorityForTauOp(self._get_args())
        elif self.type == "LengthBased":
            self._parent.omeshmodule.AssignLengthOp(self._get_args())
        elif self.type == "SkinDepthBased":
            self._parent.omeshmodule.AssignSkinDepthOp(self._get_args())
        elif self.type == "Curvilinear":
            self._parent.omeshmodule.AssignApplyCurvlinearElementsOp(self._get_args())
        elif self.type == "RotationalLayerMesh":
            self._parent.omeshmodule.AssignRotationalLayerOp(self._get_args())
        elif self.type == "DensityControlBased":
            self._parent.omeshmodule.AssignDensityControlOp(self._get_args())
        elif self.type == "Icepak":
            self._parent.omeshmodule.AssignMeshOperation(self._get_args())
        elif self.type == "CurvatureExtraction":
            self._parent.omeshmodule.AssignCurvatureExtractionOp(self._get_args())

        else:
            return False

    @aedt_exception_handler
    def update(self):
        """Update the mesh.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
        if self.type == "SurfApproxBased":
            self._parent.omeshmodule.EditTrueSurfOp(self.name, self._get_args())
        elif self.type == "DefeatureBased":
            self._parent.omeshmodule.EditModelResolutionOp(self.name, self._get_args())
        elif self.type == "SurfaceRepPriority":
            self._parent.omeshmodule.EditSurfPriorityForTauOp(self.name, self._get_args())
        elif self.type == "LengthBased":
            self._parent.omeshmodule.EditLengthOp(self.name, self._get_args())
        elif self.type == "SkinDepthBased":
            self._parent.omeshmodule.EditSkinDepthOp(self.name, self._get_args())
        elif self.type == "Curvilinear":
            self._parent.omeshmodule.EditApplyCurvlinearElementsOp(self.name, self._get_args())
        elif self.type == "RotationalLayerMesh":
            self._parent.omeshmodule.EditRotationalLayerOp(self.name, self._get_args())
        elif self.type == "DensityControlBased":
            self._parent.omeshmodule.EditDensityControlOp(self.name, self._get_args())
        elif self.type == "Icepak":
            self._parent.omeshmodule.EditMeshOperation(self.name, self._get_args())
        elif self.type == "CurvatureExtraction":
            self._parent.omeshmodule.EditSBRCurvatureExtractionOp(self.name, self._get_args())
        else:
            return False
        return True

    @aedt_exception_handler
    def delete(self):
        """Delete the mesh.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
        self._parent.omeshmodule.DeleteOp([self.name])
        for el in self._parent.meshoperations:
            if el.name == self.name:
                self._parent.meshoperations.remove(el)
        return True


class Mesh(object):
    """Mesh class.   
    
    This class manages AEDT mesh functions.
    
    Parameters
    ----------
    parent :
    
    """

    def __init__(self, parent):
        self._parent = parent
        self.id = 0
        self.meshoperations = self._get_design_mesh_operations()
        self.globalmesh = self._get_design_global_mesh()
        pass

    @property
    def omeshmodule(self):
        """Mesh module."""
        design_type = self.odesign.GetDesignType()
        assert design_type in meshers, "Invalid design type {}".format(design_type)
        return self.odesign.GetModule(meshers[design_type])

    @property
    def _messenger(self):
        """_messenger."""
        return self._parent._messenger

    @property
    def odesign(self):
        """Design."""
        return self._parent._odesign

    @property
    def modeler(self):
        """Modeler."""
        return self._parent._modeler

    @aedt_exception_handler
    def _get_design_global_mesh(self):
        """ """
        try:
            return self._parent.design_properties['MeshSetup']['MeshSettings']
        except:
            return OrderedDict()

    @aedt_exception_handler
    def _get_design_mesh_operations(self):
        """ """
        meshops = []
        try:
            for ds in self._parent.design_properties['MeshSetup']['MeshOperations']:
                if type(self._parent.design_properties['MeshSetup']['MeshOperations'][ds]) is OrderedDict:
                    meshops.append(MeshOperation(self, ds,
                                                self._parent.design_properties['MeshSetup']['MeshOperations'][ds],
                                                self._parent.design_properties['MeshSetup']['MeshOperations'][ds][
                                                    'Type']))
        except:
            pass
        return meshops

    @aedt_exception_handler
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
        :class:`MeshOperation`
            Mesh operation object.
            
        """
        names = self.modeler.convert_to_selections(names, True)
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("SurfApprox")
        self._messenger.add_info_message("Assigning Mesh Level " + str(level) + " to " + str(names))
        names = self._parent._modeler._convert_list_to_ids(names)

        if type(names[0]) is int:
            seltype = "Faces"
        else:
            seltype = "Objects"
        props = OrderedDict({"Type": "SurfApproxBased", "CurvedSurfaceApproxChoice": "UseSlider", seltype: names,
                             "SliderMeshSettings": level})
        mop = MeshOperation(self, meshop_name, props, "SurfApproxBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @aedt_exception_handler
    def assign_surface_mesh_manual(self, names, surf_dev=None, normal_dev=None, aspect_ratio=None, meshop_name=None):
        """Assign a surface mesh to a list of faces.

        Parameters
        ----------
        names : list
            List of faces to apply the surface mesh to.
        surf_dev : float, optional
            Surface deviation. The default is ``None``.
        normal_dev : float, optional
            Normal deviation. The default is ``None``.
        aspect_ratio : int, optional
            Aspect ratio. The default is ``None``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`MeshOperation`
            Mesh operation object.
            
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
            surf_dev_enable = 1
            surf_dev = "0.001"

        if not normal_dev:
            normal_dev_enable = 1
            normal_dev = "1"

        if not aspect_ratio:
            aspect_ratio_enable = 1
            aspect_ratio = "10"

        props = OrderedDict({"Type": "SurfApproxBased", "Objects": names, "CurvedSurfaceApproxChoice": "ManualSettings",
                             "SurfDevChoice": surf_dev_enable, "SurfDev": surf_dev,
                             "NormalDevChoice": normal_dev_enable,
                             "NormalDev": normal_dev, "AspectRatioChoice": aspect_ratio_enable,
                             "AspectRatio": aspect_ratio})

        mop = MeshOperation(self, meshop_name, props, "SurfApproxBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @aedt_exception_handler
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
        :class:`MeshOperation`
            Mesh operation object.
        
        """
        names = self.modeler.convert_to_selections(names, True)
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("ModelResolution")
        for name in names:
            if type(name) is int:
                self._messenger.add_error_message("Mesh Operation Applies to Objects only")
                return False
        if defeature_length is None:
            props = OrderedDict({"Objects": names, "UseAutoLength": True})
        else:
            props = OrderedDict({"Type": "DefeatureBased", "Objects": names, "UseAutoLength": False,
                                 "DefeatureLength": str(defeature_length) + "mm"})

        mop = MeshOperation(self, meshop_name, props, "DefeatureBased")

        mop.create()
        self.meshoperations.append(mop)
        return mop

    @aedt_exception_handler
    def assign_initial_mesh_from_slider(self, level=5, method='Auto', usedynamicsurface=True, useflexmesh=False,
                                        applycurvilinear=False, usefallback=True, usephi=True, automodelresolution=True, modelresolutionlength="0.0001mm"):
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
            
        """
        if self._parent.design_type == "2D Extractor" or self._parent.design_type == "Maxwell 2D":
            mesh_methods = ["Auto", "AnsoftClassic"]
        else:
            mesh_methods = ["Auto", "AnsoftTAU", "AnsoftClassic"]
        assert method in mesh_methods

        modelres = ["NAME:GlobalModelRes", "UseAutoLength:=", automodelresolution]
        if not automodelresolution:
            modelres.append("DefeatureLength:=")
            modelres.append(modelresolutionlength)
        surface_appr = ["NAME:GlobalSurfApproximation", "CurvedSurfaceApproxChoice:=", "UseSlider",
                        "SliderMeshSettings:=", level]
        if self._parent.design_type == "2D Extractor" or self._parent.design_type == "Maxwell 2D":
            args = ["NAME:MeshSettings", surface_appr, modelres, "MeshMethod:=", method]
        else:
            args = ["NAME:MeshSettings",surface_appr, ["NAME:GlobalCurvilinear", "Apply:=", applycurvilinear],
                    modelres, "MeshMethod:=", method, "UseLegacyFaceterForTauVolumeMesh:=", False,
                    "DynamicSurfaceResolution:=", usedynamicsurface, "UseFlexMeshingForTAUvolumeMesh:=", useflexmesh]
        if self._parent.design_type == "HFSS":
            args.append("UseAlternativeMeshMethodsAsFallBack:=")
            args.append(usefallback)
            args.append("AllowPhiForLayeredGeometry:=")
            args.append(usephi)
        self.omeshmodule.InitialMeshSettings(args)
        return True

    @aedt_exception_handler
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
        :class:`MeshOperation`
            Mesh operation object.
        
        """
        meshop_name = generate_unique_name("SurfaceRepPriority")
        props = OrderedDict({"Type": "SurfaceRepPriority", "Objects": object_lists, "SurfaceRepPriority": surfpriority})
        mop = MeshOperation(self, meshop_name, props, "SurfaceRepPriority")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
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
            
        """
        return self.odesign.GenerateMesh(name) == 0


    @aedt_exception_handler
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
        
        """
        # Type "Area Based" not included since the delete command causes
        # desktop to crash
        # https://tfs.ansys.com:8443/tfs/ANSYS_Development/Portfolio/ACE%20Team/_queries?id=150923
        mesh_op_types = ["Length Based",
                         "Surface Approximation Based"]

        if mesh_type:
            if mesh_type in mesh_op_types:
                mesh_op_types = [mesh_type]

        for mesh_op_type in mesh_op_types:
            opnames = self.omeshmodule.GetOperationNames(mesh_op_type)
            if opnames:
                self.omeshmodule.DeleteOp(opnames)
            for el in self.meshoperations:
                if el.name == opnames:
                    self.meshoperations.remove(el)

        return True


    @aedt_exception_handler
    def assign_length_mesh(self, names, isinside=True, maxlength=1, maxel=1000, meshop_name=None):
        """Assign a length for the model resolution.

        Parameters
        ----------
        names : list
            List of object names or face IDs.
        isinside : bool, optional
            Whether the length mesh is inside the selection. The default is ``True``.
        maxlength : int, optional
            Maximum element length. The default is ``1``. When ``None``, 
            this parameter is disabled.
        maxel : int, optional
            Maximum number of elements. The default is ``1000``. When ``None``, this parameter
            is disabled.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`MeshOperation`
            Mesh operation object.

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
            self._messenger.add_error_message("mesh not assigned due to incorrect settings")
            return
        names = self._parent._modeler._convert_list_to_ids(names)

        if type(names[0]) is int and not isinside:
            seltype = "Faces"
        elif type(names[0]) is str:
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self._messenger.add_error_message("Error in Assignment")
            return
        props = OrderedDict({"Type": "LengthBased", "RefineInside": isinside, "Enabled": True, seltype: names,
                             "RestrictElem": restrictel, "NumMaxElem": numel, "RestrictLength": restrictlength,
                             "MaxLength": length})

        mop = MeshOperation(self, meshop_name, props, "LengthBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
    def assign_skin_depth(self, names, skindepth, maxelements=None, triangulation_max_length="0.1mm", numlayers="2",
                          meshop_name=None):
        """Assign a skin depth for the mesh refinement.

        Parameters
        ----------
        names : list
           List of the object names or face IDs.
        skindepth : bool
            Whether the length mesh is inside the selection. The default is ``True``. 
        maxelements : int, optional
            Maximum number of elements. The default is ``None``, which means
            this parameter is disabled.
        triangulation_max_length : str, optional
            Maximum surface triangulation length with units. The default 
            is ``"0.1mm"`.
        numlayers : str, optional
            Number of layers. The default is ``"2"``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`MeshOperation`
            Mesh operation object.
            
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._parent.design_type != "HFSS" and self._parent.design_type != "Maxwell 3D":
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
        names = self._parent._modeler._convert_list_to_ids(names)

        if type(names[0]) is int:
            seltype = "Faces"
        elif type(names[0]) is str:
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self._messenger.add_error_message("Error in Assignment")
            return

        props = OrderedDict({"Type": "SkinDepthBased", "Enabled": True, seltype: names,
                             "RestrictElem": restrictlength, "NumMaxElem": str(maxelements), "SkinDepth": skindepth,
                             "SurfTriMaxLength": triangulation_max_length, "NumLayers": numlayers})

        mop = MeshOperation(self, meshop_name, props, "SkinDepthBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
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
        :class:`MeshOperation`
            Mesh operation object.
            
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._parent.design_type != "HFSS" and self._parent.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("CurvilinearElements")
        names = self._parent._modeler._convert_list_to_ids(names)

        if type(names[0]) is int:
            seltype = "Faces"
        elif type(names[0]) is str:
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self._messenger.add_error_message("Error in Assignment")
            return
        props = OrderedDict({"Type": "Curvilinear", seltype: names, "Apply": enable})
        mop = MeshOperation(self, meshop_name, props, "Curvilinear")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
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
       :class:`MeshOperation`
            Mesh operation object.
        
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._parent.solution_type != "SBR+":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("CurvilinearElements")
        names = self._parent._modeler._convert_list_to_ids(names)
        if type(names[0]) is int:
            seltype = "Faces"
        elif type(names[0]) is str:
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self._messenger.add_error_message("Error in Assignment")
            return
        props = OrderedDict(
            {"Type": "CurvatureExtraction", seltype: names, "DisableForFacetedSurfaces": disable_for_faceted_surf})
        mop = MeshOperation(self, meshop_name, props, "CurvatureExtraction")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
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
        :class:`MeshOperation`
            Mesh operation object.
            
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._parent.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("RotationalLayer")
        seltype = "Objects"
        props = OrderedDict({"Type": "RotationalLayerMesh", seltype: names, "Number of Layers": str(num_layers),
                             "Total Layer Thickenss": total_thickness})

        mop = MeshOperation(self, meshop_name, props, "RotationalLayerMesh")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
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
        :class:`MeshOperation`
            Mesh operation object.
            
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._parent.design_type != "Maxwell 3D":
            raise MethodNotSupportedError
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("EdgeCut")
        seltype = "Objects"
        props = OrderedDict({"Type": "RotationalLayerMesh", seltype: names, "Layer Thickenss": layer_thickness})

        mop = MeshOperation(self, meshop_name, props, "RotationalLayerMesh")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
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
        :class:`MeshOperation`
            Mesh operation object.
            
        """
        names = self.modeler.convert_to_selections(names, True)

        if self._parent.design_type != "Maxwell 3D":
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
            {"Type": "DensityControlBased", "RefineInside": refine_inside, seltype: names,
             "RestrictMaxElemLength": restr, "MaxElemLength": restrval,
             "RestrictLayersNum": restrlay, "LayersNum": restrlaynum})
        mop = MeshOperation(self, meshop_name, props, "DensityControlBased")
        mop.create()

        self.meshoperations.append(mop)
        return mop
