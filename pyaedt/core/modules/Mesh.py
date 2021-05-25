"""
Mesh Library Class
----------------------------------------------------------------

Disclaimer
==================================================

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**


Description
==================================================

This class contains all the functionalities to create and edit mesh in all the 3D Tools



========================================================

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
    def __init__(self, parent, name, props, meshoptype):
        self._parent = parent
        self.name = name
        self.props = props
        self.type = meshoptype

    @aedt_exception_handler
    def _get_args(self):
        props = self.props
        arg = ["NAME:" + self.name]
        dict2arg(props, arg)
        return arg

    @aedt_exception_handler
    def create(self):
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
        self._parent.omeshmodule.DeleteOp([self.name])
        for el in self._parent.meshoperations:
            if el.name == self.name:
                self._parent.meshoperations.remove(el)
        return True


class Mesh(object):
    """""
    Manage Main AEDT Mesh Functions
    AEDTConfig Class Inherited contains all the _desktop Hierarchical calls needed to the class
    """""

    def __init__(self, parent):
        self._parent = parent
        self.id = 0
        self.meshoperations = self._get_design_mesh_operations()
        self.globalmesh = self._get_design_global_mesh()
        pass

    @property
    def omeshmodule(self):
        """

        :return: Mesh Module
        """
        design_type = self.odesign.GetDesignType()
        assert design_type in meshers, "Invalid design type {}".format(design_type)
        return self.odesign.GetModule(meshers[design_type])

    @property
    def messenger(self):
        return self._parent._messenger

    @property
    def odesign(self):
        return self._parent._odesign

    @property
    def modeler(self):
        return self._parent._modeler

    @aedt_exception_handler
    def _get_design_global_mesh(self):
        try:
            return self._parent.design_properties['MeshSetup']['MeshSettings']
        except:
            return OrderedDict()

    @aedt_exception_handler
    def _get_design_mesh_operations(self):
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
        """
        Assign a predefined surface mesh level to an object


        :param names: name of the objects
        :param level: level of surface mesh
        :param meshop_name: optional name
        :return: meshoperation object
        """
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("SurfApprox")
        self.messenger.add_info_message("Assigning Mesh Level " + str(level) + " to " + str(names))
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
        """
        Assign Surface mesh to list of faces


        :param names: list of objects to apply surface mesh
        :param surf_dev: float surface deviation
        :param normal_dev: float normal deviation
        :param aspect_ratio: int aspoect ration
        :param meshop_name: label to apply to boundary
        :return: meshoperation object
        """
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
        """Assign Model Resolution


        :param names: list of objects to defeature
        :param defeature_length: defeaturing length in mm. None for automatic defeature
        :param meshop_name: optional name of meshoperation
        :return: meshoperation object
        """
        if meshop_name:
            for m in self.meshoperations:
                if meshop_name == m.name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("ModelResolution")

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
        """Assign a predefined surface mesh level to an object

        :param level: level of surface mesh (integer 1 - 10)
        :param method: mesher setting "Auto", "AnsoftTAU", "AnsoftClassic"
        :param usedynamicsurface: Boolean
        :param useflexmesh: Boolean
        :param applycurvilinear: Boolean
        :param usefallback: Boolean
        :param usephi: Boolean
        :return: Boolean
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
        """Assign Surface Priority for Tau Mesheron object lists


        :param object_lists: list of objects to apply it
        :param surfpriority: int Surface Priority. Default 0
        :return: meshoperation object
        """
        meshop_name = generate_unique_name("SurfaceRepPriority")
        props = OrderedDict({"Type": "SurfaceRepPriority", "Objects": object_lists, "SurfaceRepPriority": surfpriority})
        mop = MeshOperation(self, meshop_name, props, "SurfaceRepPriority")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
    def generate_mesh(self, name):
        """Generate Mesh for Setup name. Return 0 if mesh failed or 1 if passed
        :param name:  name of design to be meshed
        :return: Bool
        """

        return self.odesign.GenerateMesh(name)


    @aedt_exception_handler
    def delete_mesh_operations(self, mesh_type=None):
        """Remove mesh operations from a design. If type is None, remove all mesh operations

        :param mesh_type: mesh operation type
        :return: Boolean
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
        """
        :param names: object lists. it can be a list of objects names or faces ids
        :param isinside: True if length mesh is inside selection, False if outside
        :param maxlength: maxlength maximum element length. None to disable
        :param maxel: max number of element. None to disable
        :param meshop_name: optional mesh operation name
        :return: meshoperation object
        """
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
            self.messenger.add_error_message("mesh not assigned due to incorrect settings")
            return
        names = self._parent._modeler._convert_list_to_ids(names)

        if type(names[0]) is int and not isinside:
            seltype = "Faces"
        elif type(names[0]) is str:
            seltype = "Objects"
        else:
            seltype = None
        if seltype is None:
            self.messenger.add_error_message("Error in Assigment")
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
        """
        :param names: object lists. it can be a list of objects names or faces ids
        :param skindepth: True if length mesh is inside selection, False if outside
        :param maxelements: maxlength maximum element length. None to disable
        :param triangulation_max_length: maximum surface triangulation length
        :param numlayers: number of layers
        :return: meshoperation object

        """
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
            self.messenger.add_error_message("Error in Assigment")
            return

        props = OrderedDict({"Type": "SkinDepthBased", "Enabled": True, seltype: names,
                             "RestrictElem": restrictlength, "NumMaxElem": str(maxelements), "SkinDepth": skindepth,
                             "SurfTriMaxLength": triangulation_max_length, "NumLayers": numlayers})

        mop = MeshOperation(self, meshop_name, props, "SkinDepthBased")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
    def appy_curvilinear_elements(self, names, enable=True, meshop_name=None):
        """
        :param names: object lists. it can be a list of objects or faces
        :param enable: True if enabled
        :param meshop_name: optional mesh operation name

        :return: meshoperation object

        """
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
            self.messenger.add_error_message("Error in Assigment")
            return
        props = OrderedDict({"Type": "Curvilinear", seltype: names, "Apply": enable})
        mop = MeshOperation(self, meshop_name, props, "Curvilinear")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
    def appy_curvature_extraction(self, names, disable_for_faceted_surf=True, meshop_name=None):
        """
        :param names: object lists. it can be a list of objects or faces
        :param disable_for_faceted_surf: True if enabled
        :param meshop_name: optional mesh operation name

        :return: meshoperation object

        """
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
            self.messenger.add_error_message("Error in Assigment")
            return
        props = OrderedDict(
            {"Type": "CurvatureExtraction", seltype: names, "DisableForFacetedSurfaces": disable_for_faceted_surf})
        mop = MeshOperation(self, meshop_name, props, "CurvatureExtraction")
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
    def assign_rotational_layer(self, names, num_layers=3, total_thickness="1mm", meshop_name=None):
        """
        :param names: object lists.
        :param num_layers: str or int
        :param total_thickness: thickness with units

        :param meshop_name: optional mesh operation name

        :return: meshoperation object

        """
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
        """
        :param names: object lists.
        :param layer_thickness: thickness with units
        :param meshop_name: optional mesh operation name
        :return: meshoperation object

        """
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
        """
        :param names: object lists.
        :param refine_inside: Boolean
        :param maxelementlength: dim wih units. None to disable
        :param layerNum: Number. None to disable
        :param meshop_name: optional mesh operation name
        :return: meshoperation object

        """
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
