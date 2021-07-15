from collections import OrderedDict

from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Mesh import meshers, MeshOperation


class IcepakMesh(object):
    """IcepakMesh class."""
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
        """MessRegion class.
        
        This class manages Icepak mesh region settings.
        """
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

        @aedt_exception_handler
        def _dim_arg(self, value):
            if type(value) is str:
                try:
                    float(value)
                    val = "{0}{1}".format(value,  self.model_units)
                except:
                    val = value
            else:
                val = "{0}{1}".format(value,  self.model_units)
            return val

        @property
        def autosettings(self):
            """Automatic mesh settings."""
            arg = ["MeshMethod:=", "MesherHD", "UserSpecifiedSettings:=", self.UserSpecifiedSettings, "ComputeGap:=",
                   self.ComputeGap, "MeshRegionResolution:=", self.Level, "MinGapX:=",
                   self._dim_arg(self.MinGapX), "MinGapY:=",
                   self._dim_arg(self.MinGapY) , "MinGapZ:=", self._dim_arg(self.MinGapZ), "Objects:=",
                   self.Objects]
            return arg

        @property
        def manualsettings(self):
            """Manual mesh settings."""
            arg = ["MeshMethod:=", "MesherHD", "UserSpecifiedSettings:=", self.UserSpecifiedSettings, "ComputeGap:=",
                   self.ComputeGap, "MaxElementSizeX:=", self._dim_arg(self.MaxElementSizeX),
                   "MaxElementSizeY:=",
                   self._dim_arg(self.MaxElementSizeY) , "MaxElementSizeZ:=",
                   self._dim_arg(self.MaxElementSizeZ), "MinElementsInGap:=",
                   self.MinElementsInGap,
                   "MinElementsOnEdge:=", self.MinElementsOnEdge, "MaxSizeRatio:=",
                   self.MaxSizeRatio, "NoOGrids:=", self.NoOGrids, "EnableMLM:=", self.EnableMLM, "EnforeMLMType:=",
                   self.EnforeMLMType, "MaxLevels:=", self.MaxLevels, "BufferLayers:=", self.BufferLayers,
                   "UniformMeshParametersType:=", self.UniformMeshParametersType, "StairStepMeshing:=",
                   self.StairStepMeshing, "MinGapX:=",
                   self._dim_arg(self.MinGapX) , "MinGapY:=", self._dim_arg(self.MinGapY),
                   "MinGapZ:=", self._dim_arg(self.MinGapZ), "Objects:=", self.Objects]
            return arg

        @property
        def odesign(self):
            """Instance of a design in a project."""
            return self._parent._odesign

        @aedt_exception_handler
        def update(self):
            """Update mesh region settings with the ones in the object variable.
            
            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.
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
            """Create a new mesh region.
            
            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.
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
        """Instance ofa mesh module in a project."""
        design_type = self.odesign.GetDesignType()
        assert design_type in meshers, "Invalid design type {}".format(design_type)
        return self.odesign.GetModule(meshers[design_type])

    @property
    def boundingdimension(self):
        """Bounding dimension."""
        return self.modeler.get_bounding_dimension()

    @property
    def odesign(self):
        """Instance of a design in a project."""
        return self._parent._odesign

    @property
    def modeler(self):
        """Modeler."""
        return self._parent._modeler

    @aedt_exception_handler
    def _get_design_mesh_operations(self):
        """Retrieve design mesh operations."""
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
        """Retrieve design mesh regions."""
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
        """Assign a given mesh level to objects.

        Parameters
        ----------
        mesh_order : dict
            Dictionary where the key is the object name and the value is 
            the mesh level.
        meshop_name :  str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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
        """Create a custom mesh tailored on a PCB design.

        Parameters
        ----------
        accuracy : int, optional
            Type of the mesh. Options are ``1``, ``2``, and ``3``, which represent 
            respectively a coarse, standard, or very accurate mesh. The default is ``2``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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
        """Create a generic custom mesh for a custom 3D object.

        Parameters
        ----------
        accuracy2 : int
            Type of the mesh. Options are ``1``, ``2``, and ``3``, which represent respectively 
            a coarse, standard, or very accurate mesh. 
        stairStep : bool, optional
            Whether to enable a stair step. The default is ``True``.

        Returns
        -------
         bool
            ``True`` when successful, ``False`` when failed.
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
        """Add priority to objects.

        Parameters
        ----------
        entity_type : int
            Type of the entity. Options are ``1`` and ``2``, which represent respectively
            an object and a component.
        obj_list : list
            List of objects, which can include conductors and dielctrics.
        comp_name : str, optional
            Name of the component. The default is ``None``.
        priority : int, optional
            Level of priority. The default is ``3``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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
    def assign_mesh_region(self, objectlist=[], level=5, name=None):
        """Assign a predefined surface mesh level to an object.

        Parameters
        ----------
        objectlist : list, optional
            List of objects to apply the mesh region to. The default 
            is ``[]``.
        level : int, optional
            Level of the surface mesh. Options are ``1`` through ``5``. The default
            is ``5``.
        name : str, optional
            Name of the mesh region. The default is ``"MeshRegion1"``.

        Returns
        -------
        IcepakMesh.MeshRegion
            Mesh region object.
        """
        if not name:
            name = generate_unique_name("MeshRegion")
        meshregion = self.MeshRegion(self.omeshmodule, self.boundingdimension, self.modeler.model_units)
        meshregion.UserSpecifiedSettings = False
        meshregion.Level = level
        meshregion.name = name
        if not objectlist:
            objectlist = self.modeler.primitives.object_names
        all_objs = self.modeler.primitives.object_names
        meshregion.create()
        objectlist2 = self.modeler.primitives.object_names
        added_obj = [i for i in objectlist2 if i not in all_objs]
        meshregion.Objects = added_obj
        self.meshregions.append(meshregion)
        return meshregion

    @aedt_exception_handler
    def generate_mesh(self, name):
        """Generate the mesh for a given setup name.

        Parameters
        ----------
        name : str
            Name of the design to mesh.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        return self.odesign.GenerateMesh(name) == 0

    @aedt_exception_handler
    def assign_mesh_level_to_group(self, mesh_level, groupName, localMeshParamEn=False,
                                   localMeshParameters="No Local Mesh Parameters", meshop_name=None):
        """Assign a mesh level to a group.

        Parameters
        ----------
        mesh_level : int
            Level of mesh to assign. Options are ``1`` through ``5``.   
        groupName : str
            Name of the group.
        localMeshParamEn : bool, optional
            The default is ``False``.
        localMeshParameters : str, optional
            The default is ``"No Local Mesh Parameters"``.
        meshop_name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        type
            Mesh operation object.
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
