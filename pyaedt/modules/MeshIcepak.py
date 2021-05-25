from collections import OrderedDict

from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Mesh import meshers, MeshOperation


class IcepakMesh(object):
    """Manage Main Icepak Mesh Functions"""

    def __init__(self, parent):
        self._parent = parent
        self.id = 0
        self._oeditor = self.modeler.oeditor
        self._model_units = self.modeler.model_units
        self.global_mesh_region = self.MeshRegion(self.omeshmodule, self.boundingdimension, self._model_units)
        self.meshoperations = self._get_design_mesh_operations()
        self.meshregions = self._get_design_mesh_regions()
        self._priorities_args = []

    class MeshRegion(object):
        """Class that manage the Mesh Region Settings of Icepak"""

        def __init__(self, meshmodule, dimension, units):
            self.name = "Settings"
            self.meshmodule = meshmodule
            self.model_units = units
            self.UserSpecifiedSettings = False
            self.ComputeGap = True
            self.Level = 3
            self.MaxElementSizeX = str(float(dimension[0]) / 20)
            self.MaxElementSizeY = str(float(dimension[1]) / 20)
            self.MaxElementSizeZ = str(float(dimension[2]) / 20)
            self.MinElementsInGap = "3"
            self.MinElementsOnEdge = "2"
            self.MaxSizeRatio = "2"
            self.NoOGrids = False
            self.EnableMLM = True
            self.EnforeMLMType = "3D"
            self.MaxLevels = "0"
            self.BufferLayers = "0"
            self.UniformMeshParametersType = "Average"
            self.StairStepMeshing = False
            self.DMLMType = "2DMLM_None"
            self.MinGapX = "1"
            self.MinGapY = "1"
            self.MinGapZ = "1"
            self.Objects = ["Region"]
            self.Enable = True

        @property
        def autosettings(self):
            """ """
            arg = ["MeshMethod:=", "MesherHD", "UserSpecifiedSettings:=", self.UserSpecifiedSettings, "ComputeGap:=",
                   self.ComputeGap, "MeshRegionResolution:=", self.Level, "MinGapX:=",
                   str(self.MinGapX) + self.model_units, "MinGapY:=",
                   str(self.MinGapY) + self.model_units, "MinGapZ:=", str(self.MinGapZ) + self.model_units, "Objects:=",
                   self.Objects]
            return arg

        @property
        def manualsettings(self):
            """ """
            arg = ["MeshMethod:=", "MesherHD", "UserSpecifiedSettings:=", self.UserSpecifiedSettings, "ComputeGap:=",
                   self.ComputeGap, "MaxElementSizeX:=", str(self.MaxElementSizeX) + self.model_units,
                   "MaxElementSizeY:=",
                   str(self.MaxElementSizeY) + self.model_units, "MaxElementSizeZ:=",
                   str(self.MaxElementSizeZ) + self.model_units, "MinElementsInGap:=",
                   self.MinElementsInGap,
                   "MinElementsOnEdge:=", self.MinElementsOnEdge, "MaxSizeRatio:=",
                   self.MaxSizeRatio, "NoOGrids:=", self.NoOGrids, "EnableMLM:=", self.EnableMLM, "EnforeMLMType:=",
                   self.EnforeMLMType, "MaxLevels:=", self.MaxLevels, "BufferLayers:=", self.BufferLayers,
                   "UniformMeshParametersType:=", self.UniformMeshParametersType, "StairStepMeshing:=",
                   self.StairStepMeshing, "MinGapX:=",
                   str(self.MinGapX) + self.model_units, "MinGapY:=", str(self.MinGapY) + self.model_units,
                   "MinGapZ:=", str(self.MinGapZ) + self.model_units, "Objects:=", self.Objects]
            return arg

        @property
        def odesign(self):
            """ """
            return self._parent._odesign

        @aedt_exception_handler
        def update(self):
            """Update the Mesh Region Settings with the ones in the object variable
            
            :return: None

            Parameters
            ----------

            Returns
            -------

            """
            if self.name == "Settings":
                args = ["NAME:Settings"]
            else:
                args = ["NAME:" + self.name, "Enable:=", self.Enable]
            if self.UserSpecifiedSettings:
                args += self.manualsettings
            else:
                args += self.autosettings
            if self.name == "Settings":
                self.meshmodule.EditGlobalMeshRegion(args)
            else:
                self.meshmodule.EditMeshRegion(self.name, args)
            return True

        @aedt_exception_handler
        def create(self):
            """Create a new mesh region
            
            
            :return: Bool

            Parameters
            ----------

            Returns
            -------

            """
            assert self.name != "Settings", "Cannot create a new mesh region with this Name"
            args = ["NAME:" + self.name, "Enable:=", self.Enable]
            if self.UserSpecifiedSettings:
                args += self.manualsettings
            else:
                args += self.autosettings

            self.meshmodule.AssignMeshRegion(args)
            return True

    @property
    def omeshmodule(self):
        """ """
        design_type = self.odesign.GetDesignType()
        assert design_type in meshers, "Invalid design type {}".format(design_type)
        return self.odesign.GetModule(meshers[design_type])

    @property
    def boundingdimension(self):
        """ """
        return self.modeler.get_bounding_dimension()

    @property
    def odesign(self):
        """ """
        return self._parent._odesign

    @property
    def modeler(self):
        """ """
        return self._parent._modeler

    @aedt_exception_handler
    def _get_design_mesh_operations(self):
        """ """
        meshops = []
        try:
            for ds in self._parent.design_properties['MeshRegion']['MeshSetup']['MeshOperations']:
                if type(self._parent.design_properties['MeshRegion']['MeshSetup']['MeshOperations'][ds]) is OrderedDict:
                    meshops.append(MeshOperation(self, ds, self._parent.design_properties['MeshRegion']['MeshSetup'][
                        'MeshOperations'][ds], "Icepak"))
        except:
            pass
        return meshops

    @aedt_exception_handler
    def _get_design_mesh_regions(self):
        """ """
        meshops = []
        try:
            for ds in self._parent.design_properties['MeshRegion']['MeshSetup']['MeshRegions']:
                if type(self._parent.design_properties['MeshRegion']['MeshSetup']['MeshRegions'][ds]) is OrderedDict:
                    meshop = self.MeshRegion(self.omeshmodule, self.boundingdimension, self.modeler.model_units)
                    dict_prop = self._parent.design_properties['MeshRegion']['MeshSetup']['MeshRegions'][ds]
                    self.name = ds
                    for el in dict_prop:
                        if el in meshop.__dict__:
                            meshop.__dict__[el] = dict_prop[el]
                    meshops.append(meshop)
        except:
            pass
        return meshops

    @aedt_exception_handler
    def assign_mesh_level(self, mesh_order, meshop_name=None):
        """Assign a specific mesh level to objects

        Parameters
        ----------
        mesh_order :
            Dictionary. Key is object name, value is Mesh Level
        meshop_name :
             (Default value = None)

        Returns
        -------
        type
            Boolean

        """

        level_order = {}
        for obj in mesh_order:
            if mesh_order[obj] not in level_order.keys():
                level_order[mesh_order[obj]] = []
            level_order[mesh_order[obj]].append(obj)
        list_meshops=[]
        for level in level_order:
            if meshop_name:
                meshop_name = generate_unique_name(meshop_name, "L_" + str(level))
            else:
                meshop_name = generate_unique_name("Icepak", "L_" + str(level))
            props = OrderedDict({"Enable": True, "Level": str(level), "Objects": level_order[level]})
            mop = MeshOperation(self, meshop_name, props, "Icepak")
            mop.create()
            self.meshoperations.append(mop)
            list_meshops.append(meshop_name)
        return list_meshops

    @aedt_exception_handler
    def automatic_mesh_pcb(self, accuracy=2):
        """create custom Mesh tailored on PCB Design

        Parameters
        ----------
        accuracy :
            1 coarse, 2 standard, 3 very accurate (Default value = 2)

        Returns
        -------
        type
            Boolean

        """
        xsize = self.boundingdimension[0] / (15 * accuracy * accuracy)
        ysize = self.boundingdimension[1] / (15 * accuracy * accuracy)
        zsize = self.boundingdimension[2] / (10 * accuracy)
        MaxSizeRatio = (1 + (accuracy / 2))
        self.global_mesh_region.MaxElementSizeX = xsize
        self.global_mesh_region.MaxElementSizeY = ysize
        self.global_mesh_region.MaxElementSizeZ = zsize
        self.global_mesh_region.MaxSizeRatio = MaxSizeRatio
        self.global_mesh_region.UserSpecifiedSettings = True
        self.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
        self.global_mesh_region.MaxLevels = 2
        self.global_mesh_region.BufferLayers = 1
        self.global_mesh_region.MinGapX = str(xsize / 10)
        self.global_mesh_region.MinGapY = str(ysize / 10)
        self.global_mesh_region.MinGapZ = str(zsize / 10)
        self.global_mesh_region.update()
        return True

    @aedt_exception_handler
    def automatic_mesh_3D(self, accuracy2, stairStep=True):
        """create custom Mesh generic for custom 3D object

        Parameters
        ----------
        accuracy2 :
            1 standard, 2 accurate, 3 very accurate
        stairStep :
            bool to enable stair step (Default value = True)

        Returns
        -------
        type
            Boolean

        """
        xsize = self.boundingdimension[0] / (10 * accuracy2 * accuracy2)
        ysize = self.boundingdimension[1] / (10 * accuracy2 * accuracy2)
        zsize = self.boundingdimension[2] / (10 * accuracy2)
        self.global_mesh_region.MaxElementSizeX = xsize
        self.global_mesh_region.MaxElementSizeY = ysize
        self.global_mesh_region.MaxElementSizeZ = zsize
        self.global_mesh_region.UserSpecifiedSettings = True
        self.global_mesh_region.MinGapX = str(xsize / 100)
        self.global_mesh_region.MinGapY = str(ysize / 100)
        self.global_mesh_region.MinGapZ = str(zsize / 100)
        self.global_mesh_region.StairStepMeshing = stairStep
        self.global_mesh_region.update()
        return True

    @aedt_exception_handler
    def add_priority(self, entity_type, obj_list, comp_name=None, priority=3):
        """Add Priority to objects:

        Parameters
        ----------
        entity_type :
            1 : Object  2 : Component
        obj_list :
            list of object (it could be a list of conductors and dielctrics)
        comp_name :
            name of component (Default value = None)
        priority :
            Prioririty level. Default value 3

        Returns
        -------
        type
            Boolean

        """
        i = priority
        objects = ", ".join(obj_list)
        args = ["NAME:UpdatePriorityListData"]
        if entity_type == 1:
            prio = ["NAME:PriorityListParameters",
                         "EntityType:=", "Object",
                         "EntityList:=", objects,
                         "PriorityNumber:=", i,
                         "PriorityListType:=", "3D"]
            self._priorities_args.append(prio)
            args += self._priorities_args
        elif entity_type == 2:
            pcblist = self.modeler.oeditor.Get3DComponentInstanceNames(comp_name)
            prio = [
                "NAME:PriorityListParameters",
                "EntityType:=", "Component",
                "EntityList:=", pcblist[0],
                "PriorityNumber:=", i,
                "PriorityListType:=", "3D"
            ]
            self._priorities_args.append(prio)
            args += self._priorities_args
        self.modeler.oeditor.UpdatePriorityList(["NAME:UpdatePriorityListData"])
        self.modeler.oeditor.UpdatePriorityList(args)
        return True

    @aedt_exception_handler
    def assign_mesh_region(self, objectlist=[], level=5, name="MeshRegion1"):
        """Assign a predefined surface mesh level to an object

        Parameters
        ----------
        level :
            level of surface mesh (integer 1 - 5) (Default value = 5)
        objectlist :
            list of object where apply the mesh region (Default value = [])
        name :
            mesh region name (Default value = "MeshRegion1")

        Returns
        -------
        type
            meshregion object

        """
        meshregion = self.MeshRegion(self.omeshmodule, self.boundingdimension, self.modeler.model_units)
        meshregion.UserSpecifiedSettings = False
        meshregion.Level = level
        meshregion.name = name
        if not objectlist:
            objectlist = self.modeler.primitives.get_all_objects_names()
        meshregion.create()
        objectlist2 = self.modeler.primitives.get_all_objects_names()
        added_obj = [i for i in objectlist2 if i not in objectlist]
        meshregion.Objects = added_obj
        self.meshregions.append(meshregion)

        return meshregion

    @aedt_exception_handler
    def generate_mesh(self, name):
        """Generate Mesh for Setup name. Return 0 if mesh failed or 1 if passed

        Parameters
        ----------
        name :
            name of design to be meshed

        Returns
        -------
        type
            Boolean

        """
        return self.odesign.GenerateMesh(name)

    @aedt_exception_handler
    def assign_mesh_level_to_group(self, mesh_level, groupName, localMeshParamEn=False,
                                   localMeshParameters="No Local Mesh Parameters", meshop_name=None):
        """Assign Mesh Level to group

        Parameters
        ----------
        mesh_level :
            level of mesh to apply (int)
        groupName :
            name of the group
        localMeshParamEn :
            Bool (Default value = False)
        localMeshParameters :
            return: meshoperation object (Default value = "No Local Mesh Parameters")
        meshop_name :
             (Default value = None)

        Returns
        -------
        type
            meshoperation object

        """
        if meshop_name:
            for el in self.meshoperations:
                if el.name == meshop_name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("MeshLevel")
        props = OrderedDict({"Enable": True, "Level": mesh_level, "Local Mesh Parameters Enabled": localMeshParamEn,
                             "Groups": [str(groupName)], "Local Mesh Parameters Type": localMeshParameters})
        mop = MeshOperation(self, meshop_name, props, "Icepak")
        mop.create()
        self.meshoperations.append(mop)
        return mop
