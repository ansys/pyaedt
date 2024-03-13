from abc import abstractmethod
from collections import OrderedDict
import warnings

from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings
from pyaedt.modules.Mesh import MeshOperation
from pyaedt.modules.Mesh import meshers


class CommonRegion(object):
    def __init__(self, app):
        self._app = app
        self._padding_type = None  # ["Percentage Offset"] * 6
        self._padding_value = None  # [50] * 6
        self._coordinate_system = None  # "Global"
        self._dir_order = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]

    def _get_object(self):
        if isinstance(self, Region):
            return [
                oo for o, oo in self._app.modeler.objects_by_name.items() if oo.history().command == "CreateRegion"
            ][0]
        else:
            parts = self._app.odesign.GetChildObject("Mesh").GetChildObject(self.name).GetPropValue("Parts")
            return [self._app.modeler[p] for p in parts]

    def _set_region_data(self, value, direction=None, padding_type=True):
        self._update_region_data()
        region = self._get_object()
        create_region = region.history()
        set_type = ["Data", "Type"][int(padding_type)]
        create_region.props["{} Padding {}".format(direction, set_type)] = value

    @property
    def object(self):
        return self._get_object()

    @property
    def name(self):
        try:
            return self._get_object().name
        except AttributeError:
            return None

    @property
    def padding_types(self):
        self._update_region_data()
        return self._padding_type

    @property
    def padding_values(self):
        self._update_region_data()
        return self._padding_value

    @property
    def positive_x_padding_type(self):
        return self._get_region_data("+X")

    @property
    def negative_x_padding_type(self):
        return self._get_region_data("-X")

    @property
    def positive_y_padding_type(self):
        return self._get_region_data("+Y")

    @property
    def negative_y_padding_type(self):
        return self._get_region_data("-Y")

    @property
    def positive_z_padding_type(self):
        return self._get_region_data("+Z")

    @property
    def negative_z_padding_type(self):
        return self._get_region_data("-Z")

    @property
    def positive_x_padding(self):
        return self._get_region_data("+X", False)

    @property
    def negative_x_padding(self):
        return self._get_region_data("-X", False)

    @property
    def positive_y_padding(self):
        return self._get_region_data("+Y", False)

    @property
    def negative_y_padding(self):
        return self._get_region_data("-Y", False)

    @property
    def positive_z_padding(self):
        return self._get_region_data("+Z", False)

    @property
    def negative_z_padding(self):
        return self._get_region_data("-Z", False)

    @padding_types.setter
    def padding_types(self, values):
        for i, direction in enumerate(self._dir_order):
            self._set_region_data(values[i], direction, True)

    @padding_values.setter
    def padding_values(self, values):
        for i, direction in enumerate(self._dir_order):
            self._set_region_data(values[i], direction, False)

    @positive_x_padding_type.setter
    def positive_x_padding_type(self, value):
        self._set_region_data(value, "+X", True)

    @negative_x_padding_type.setter
    def negative_x_padding_type(self, value):
        self._set_region_data(value, "-X", True)

    @positive_y_padding_type.setter
    def positive_y_padding_type(self, value):
        self._set_region_data(value, "+Y", True)

    @negative_y_padding_type.setter
    def negative_y_padding_type(self, value):
        self._set_region_data(value, "-Y", True)

    @positive_z_padding_type.setter
    def positive_z_padding_type(self, value):
        self._set_region_data(value, "+Z", True)

    @negative_z_padding_type.setter
    def negative_z_padding_type(self, value):
        self._set_region_data(value, "-Z", True)

    @positive_x_padding.setter
    def positive_x_padding(self, value):
        self._set_region_data(value, "+X", False)

    @negative_x_padding.setter
    def negative_x_padding(self, value):
        self._set_region_data(value, "-X", False)

    @positive_y_padding.setter
    def positive_y_padding(self, value):
        self._set_region_data(value, "+Y", False)

    @negative_y_padding.setter
    def negative_y_padding(self, value):
        self._set_region_data(value, "-Y", False)

    @positive_z_padding.setter
    def positive_z_padding(self, value):
        self._set_region_data(value, "+Z", False)

    @negative_z_padding.setter
    def negative_z_padding(self, value):
        self._set_region_data(value, "-Z", False)

    def _update_region_data(self):
        region = self._get_object()
        create_region = region.history()
        self._padding_type = []
        self._padding_value = []
        for padding_direction in ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]:
            self._padding_type.append(create_region.props["{} Padding Type".format(padding_direction)])
            self._padding_value.append(create_region.props["{} Padding Data".format(padding_direction)])
            self._coordinate_system = create_region.props["Coordinate System"]

    def _get_region_data(self, direction=None, padding_type=True):
        self._update_region_data()
        idx = self._dir_order.index(direction)
        if padding_type:
            return self._padding_type[idx]
        else:
            return self._padding_value[idx]


class Region(CommonRegion):
    def __init__(self, app):
        super(Region, self).__init__(app)
        try:
            self._update_region_data()
        except AttributeError:
            pass

    def create(self, padding_types, padding_values, name="Region"):
        self._app.modeler.create_region(padding_values, padding_types, region_name="Region")
        self._update_region_data()


class SubRegion(CommonRegion):
    def __init__(self, app, parts, name=None):
        super(SubRegion, self).__init__(app)
        if name is None:
            name = generate_unique_name("SubRegion")
        self.create(0, "Percentage Offset", name, parts)

    def _get_object(self):
        if self._region and not self._app.modeler.objects_by_name.get(self._region.name, False):
            self._region = None
        return self._region

    def create(self, padding_values, padding_types, region_name, parts):
        if (
            self._region is not None and self._app.modeler.objects_by_name.get(self._region.name, False)
        ) or self._app.modeler.objects_by_name.get(region_name, False):
            raise AttributeError("{} already exists in the design.".format(self._region.name))
        self._region = self._app.modeler.create_subregion(
            padding_values, padding_types, region_name, parts, "SubRegion"
        )
        return True

    def delete(self):
        try:
            self._region.delete()
            self._app.mesh.meshregions.remove(
                [mo for mo in self._app.mesh.meshregions.values() if mo.subregion == self][0]
            )
            return True
        except Exception:
            return False

    @property
    def name(self):
        try:
            return self._region.name
        except Exception:
            return False

    @property
    def parts(self):
        if self._region:
            return {
                obj_name: self._app.modeler[obj_name]
                for obj_name in self._region.history().props["Part Names"].split(",")
            }
        else:
            return {}

    @parts.setter
    def parts(self, parts):
        self._app.modeler.reassign_subregion(self, parts)


class MeshSettings(object):
    automatic_mesh_settings = {"MeshRegionResolution": 3}  # min: 1, max: 5
    common_mesh_settings = {
        "ProximitySizeFunction": True,
        "CurvatureSizeFunction": True,
        "EnableTransition": False,
        "OptimizePCBMesh": True,
        "Enable2DCutCell": False,
        "EnforceCutCellMeshing": False,
        "Enforce2dot5DCutCell": False,
        "StairStepMeshing": False,
    }
    manual_mesh_settings = {
        "MaxElementSizeX": "0.02mm",
        "MaxElementSizeY": "0.02mm",
        "MaxElementSizeZ": "0.03mm",
        "MinElementsInGap": "3",
        "MinElementsOnEdge": "2",
        "MaxSizeRatio": "2",
        "NoOGrids": False,
        "EnableMLM": True,
        "EnforeMLMType": "3D",
        "MaxLevels": "0",
        "BufferLayers": "0",
        "UniformMeshParametersType": "Average",
        "2DMLMType": "2DMLM_None",
        "MinGapX": "1mm",
        "MinGapY": "1mm",
        "MinGapZ": "1mm",
    }
    aedt_20212_args = [
        "ProximitySizeFunction",
        "CurvatureSizeFunction",
        "EnableTransition",
        "OptimizePCBMesh",
        "Enable2DCutCell",
        "EnforceCutCellMeshing",
        "Enforce2dot5DCutCell",
    ]

    def __init__(self, mesh_class, app):
        self._app = app
        self._mesh_class = mesh_class
        self.instance_settings = self.common_mesh_settings.copy()
        self.instance_settings.update(self.manual_mesh_settings.copy())
        self.instance_settings.update(self.automatic_mesh_settings.copy())
        if settings.aedt_version < "2021.2":
            for arg in self.aedt_20212_args:
                del self.instance_settings[arg]

    def parse_settings(self):
        out = []
        for k, v in self.instance_settings:
            out.append(k + ":=")
            out.append(v)
        return out

    def _key_in_dict(self, key):
        if self._mesh_class.manual_settings:
            ref_dict = self.manual_mesh_settings
        else:
            ref_dict = self.automatic_mesh_settings
        if key in ref_dict or key in self.common_mesh_settings:
            return True
        else:
            return False

    def __getitem__(self, key):
        if self._key_in_dict(key):
            return self.instance_settings[key]
        else:
            raise KeyError("Setting not available.")

    def __setitem__(self, key, value):
        if self._key_in_dict(key):
            if self._mesh_class.automatic_mesh_settings and key == "MeshRegionResolution":
                if value < 1:
                    self._app.logger.warning("Minimum resolution value is 1.")
                    value = 1
            if value > 5:
                self._app.logger.warning("Maximum resolution value is 5.")
                value = 5
            self.instance_settings[key] = value
        else:
            self._app.logger.error("Setting not available.")

    def __delitem__(self, key):
        self._app.logger.error("Setting cannot be removed.")

    def __iter__(self):
        return self.instance_settings.__iter__(self)

    def __len__(self):
        return self.instance_settings.__len__(self)

    def __contains__(self, x):
        return self.instance_settings.__contains__(self, x)


class MeshRegionCommon(object):
    """
    Manages Icepak mesh region settings.

    Attributes:
        name : str
            Name of the mesh region.
        manual_settings : bool
            Whether to use manual settings or
    """

    def __init__(self, meshmodule, units, app, name):
        self.name = name
        self.manual_settings = False
        self.settings = MeshSettings(self, app)
        self._meshmodule = meshmodule
        self._model_units = units
        self._app = app

    @pyaedt_function_handler()
    def _dim_arg(self, value):
        from pyaedt.generic.general_methods import _dim_arg

        return _dim_arg(value, self.model_units)

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @property
    def autosettings(self):
        """Automatic mesh settings."""
        arg = [
            "MeshMethod:=",
            "MesherHD",
            "UserSpecifiedSettings:=",
            self.UserSpecifiedSettings,
            "ComputeGap:=",
            self.ComputeGap,
            "MeshRegionResolution:=",
            self.Level,
            "MinGapX:=",
            self._dim_arg(self.MinGapX),
            "MinGapY:=",
            self._dim_arg(self.MinGapY),
            "MinGapZ:=",
            self._dim_arg(self.MinGapZ),
        ]
        if self.SubModels:
            arg.append("SubModels:=")
            arg.append(self.SubModels)
        if self.Objects:
            arg.append("Objects:=")
            arg.append(self.Objects)
        arg.extend(self._new_versions_fields)
        return arg

    @property
    def manualsettings(self):
        """Manual mesh settings."""

        arg = [
            "MeshMethod:=",
            "MesherHD",
            "UserSpecifiedSettings:=",
            self.UserSpecifiedSettings,
            "ComputeGap:=",
            self.ComputeGap,
            "MaxElementSizeX:=",
            self._dim_arg(self.MaxElementSizeX),
            "MaxElementSizeY:=",
            self._dim_arg(self.MaxElementSizeY),
            "MaxElementSizeZ:=",
            self._dim_arg(self.MaxElementSizeZ),
            "MinElementsInGap:=",
            self.MinElementsInGap,
            "MinElementsOnEdge:=",
            self.MinElementsOnEdge,
            "MaxSizeRatio:=",
            self.MaxSizeRatio,
            "NoOGrids:=",
            self.NoOGrids,
            "EnableMLM:=",
            self.EnableMLM,
            "EnforeMLMType:=",
            self.EnforeMLMType,
            "MaxLevels:=",
            self.MaxLevels,
            "BufferLayers:=",
            self.BufferLayers,
            "UniformMeshParametersType:=",
            self.UniformMeshParametersType,
            "StairStepMeshing:=",
            self.StairStepMeshing,
            "2DMLMType:=",
            self.DMLMType,
            "MinGapX:=",
            self._dim_arg(self.MinGapX),
            "MinGapY:=",
            self._dim_arg(self.MinGapY),
            "MinGapZ:=",
            self._dim_arg(self.MinGapZ),
        ]
        if self.SubModels:
            arg.append("SubModels:=")
            arg.append(self.SubModels)
        if self.Objects:
            arg.append("Objects:=")
            arg.append(self.Objects)
        arg.extend(self._new_versions_fields)
        return arg

    @abstractmethod
    def create(self):
        pass

    # backward compatibility
    def __getattr__(self, name):
        if name in self.settings:
            return self.settings[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if hasattr(self.settings, name):
            self.settings[name] = value
        else:
            object.__setattr__(self, name, value)


class GlobalMeshRegion(MeshRegionCommon):
    def __init__(self, app):
        self.global_region = Region(app)
        super(GlobalMeshRegion, self).__init__(
            app.omeshmodule,
            app.modeler.model_units,
            app,
            name="Settings",
        )

    @pyaedt_function_handler
    def update(self):
        """Update mesh region settings with the settings in the object variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditGlobalMeshRegion
        """
        args = ["NAME:Settings"]
        args += self.settings.parse_settings()
        try:
            self.meshmodule.EditGlobalMeshRegion(args)
            return True
        except Exception:  # pragma : no cover
            return False

    @property
    def Objects(self):
        return self.global_region.name

    def delete(self):
        self.global_region.object.delete()
        self.global_region = None

    def create(self, padding_type, padding_value):
        self.delete()
        self.global_region = Region(self._app)
        self.global_region.create(padding_type, padding_value)


class MeshRegion(MeshRegionCommon):
    def __init__(self, app, objects, name=None):
        if name is None:
            name = generate_unique_name("SubRegion")
        super(MeshRegionCommon, self).__init__(
            app.omeshmodule,
            app.modeler.model_units,
            app,
            name,
        )
        self.enable = True
        if settings.aedt_version > "2023.2":
            if not isinstance(objects, list):
                objects = [objects]
            if not isinstance(objects[0], str):
                objects = [o.name for o in objects]
            if not all(o in app.modeler.objects_by_name for o in objects):
                raise AttributeError("Objects specified not found in modeler.")
            self._assignment = SubRegion(app, objects)
        else:
            self._assignment = objects
        self.create()

    def _parse_assignment_value(self, assignment=None):
        if assignment is None:
            assignment = self.assignment
        a = []
        if isinstance(assignment, SubRegion):
            a += ["Objects:=", assignment.name]
        else:
            if any(o in self._app.modeler.object_names for o in assignment):
                obj_assignment = [o for o in assignment if o in self._app.modeler.object_names]
                a += ["Objects:=", obj_assignment]
            if any(o in self._app.oeditor.GetChildNames("SubmodelDefinitions") for o in assignment):
                obj_assignment = [o for o in assignment if o in self._app.oeditor.GetChildNames("SubmodelDefinitions")]
                a += ["Submodels:=", obj_assignment]
        return a

    @pyaedt_function_handler
    def update(self):
        """Update mesh region settings with the settings in the object variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditMeshRegion
        """
        args = ["NAME:" + self.name, "Enable:=", self.enable]
        args += self.settings.parse_settings()
        self._parse_assignment_value()
        try:
            self.meshmodule.EditMeshRegion(args)
            return True
        except Exception:  # pragma : no cover
            return False

    @pyaedt_function_handler()
    def delete(self):
        """Delete the mesh region.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteMeshRegions()
        """
        self.meshmodule.DeleteMeshRegions([self.name])
        self._app.mesh.meshregions.remove(self)
        return True

    @property
    def assignment(self):
        if settings.aedt_version > "2023.2":
            parts = self._app.odesign.GetChildObject("Mesh").GetChildObject(self.name).GetPropValue("Parts")
            sub_regions = self._app.modeler.non_model_objects
            subregion = None
            for sr in sub_regions:
                if "CreateSubRegion" == self._app.modeler[sr].history().command and all(
                    p in self._app.modeler[sr].history().props["Part Names"] for p in parts
                ):
                    subregion = sr
            self._assignment = subregion
            return subregion
        else:
            return self._assignment

    @assignment.setter
    def assignment(self, value):
        arg = ["NAME:Assignment"] + self._parse_assignment_value(value)
        try:
            self._app.omeshmodule.ReassignMeshRegion(self.name, arg)
            self._assignment = value
        except Exception:  # pragma : no cover
            self._app.logger.error("Mesh region reassignment failed.")

    @pyaedt_function_handler()
    def create(self):
        """Create a mesh region.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignMeshRegion
        """
        if self.name == "Settings":
            self._app.logger.error("Cannot create a new mesh region with this Name")
            return False
        args = ["NAME:" + self.name, "Enable:=", self.enable]
        args += self.settings.parse_settings()
        args += self._parse_assignment_value()
        self.meshmodule.AssignMeshRegion(args)
        self._app.mesh.meshregions.append(self)
        self._app.modeler.refresh_all_ids()
        return True

    # backward compatibility
    @property
    def Enable(self):
        warnings.warn(
            "`Enable` is deprecated. Use `enable` instead.",
            DeprecationWarning,
        )
        return self.enable

    @Enable.setter
    def Enable(self, val):
        warnings.warn(
            "`Enable` is deprecated. Use `enable` instead.",
            DeprecationWarning,
        )
        self.enable = val

    @property
    def Objects(self):
        warnings.warn(
            "`Objects` is deprecated. Use `assignment` instead.",
            DeprecationWarning,
        )
        return self.assignment

    @Objects.setter
    def Objects(self, objects):
        warnings.warn(
            "`Objects` is deprecated. Use `assignment` instead.",
            DeprecationWarning,
        )
        self.assignment = objects

    @property
    def Submodels(self):
        warnings.warn(
            "`Submodels` is deprecated. Use `assignment` instead.",
            DeprecationWarning,
        )
        return self.assignment

    @Submodels.setter
    def Submodels(self, objects):
        warnings.warn(
            "`Submodels` is deprecated. Use `assignment` instead.",
            DeprecationWarning,
        )
        self.assignment = objects


class IcepakMesh(object):
    """Manages Icepak meshes.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
    """

    def __init__(self, app):
        self._app = app

        self._odesign = self._app._odesign
        self.modeler = self._app.modeler
        design_type = self._odesign.GetDesignType()
        assert design_type in meshers, "Invalid design type {}".format(design_type)
        self.id = 0
        self._oeditor = self.modeler.oeditor
        self._model_units = self.modeler.model_units
        self.meshoperations = self._get_design_mesh_operations()
        self.meshregions = self._get_design_mesh_regions()
        try:
            self.global_mesh_region = [mo for mo in self.meshregions if isinstance(mo, GlobalMeshRegion)][0]
        except IndexError:
            self.global_mesh_region = GlobalMeshRegion(app)
        self._priorities_args = []

    @property
    def meshregions_dict(self):
        """
        Get mesh regions in the design.

        Returns
        -------
        dict
            Dictionary with mesh region names as keys and mesh region objects as values.
        """
        return {mr.name: mr for mr in self.meshregions}

    @pyaedt_function_handler()
    def _refresh_mesh_operations(self):
        """Refresh all mesh operations."""

        self._meshoperations = self._get_design_mesh_operations()
        return len(self.meshoperations)

    @property
    def omeshmodule(self):
        """Icepak Mesh Module.

        References
        ----------

        >>> oDesign.GetModule("MeshRegion")
        """
        return self._app.omeshmodule

    @property
    def boundingdimension(self):
        """Bounding dimension."""
        return self.modeler.get_bounding_dimension()

    @pyaedt_function_handler()
    def _get_design_mesh_operations(self):
        """Retrieve design mesh operations."""
        meshops = []
        try:
            if settings.aedt_version > "2023.2":
                for ds in self._app.design_properties["MeshRegion"]["MeshSetup"]:
                    if isinstance(self._app.design_properties["MeshRegion"]["MeshSetup"][ds], (OrderedDict, dict)):
                        if self._app.design_properties["MeshRegion"]["MeshSetup"][ds]["DType"] == "OpT":
                            meshops.append(
                                MeshOperation(
                                    self,
                                    ds,
                                    self._app.design_properties["MeshRegion"]["MeshSetup"][ds],
                                    "Icepak",
                                )
                            )
            else:
                for ds in self._app.design_properties["MeshRegion"]["MeshSetup"]["MeshOperations"]:
                    if isinstance(
                        self._app.design_properties["MeshRegion"]["MeshSetup"]["MeshOperations"][ds],
                        (OrderedDict, dict),
                    ):
                        meshops.append(
                            MeshOperation(
                                self,
                                ds,
                                self._app.design_properties["MeshRegion"]["MeshSetup"]["MeshOperations"][ds],
                                "Icepak",
                            )
                        )
        except:
            pass
        return meshops

    @pyaedt_function_handler()
    def _get_design_mesh_regions(self):
        """Retrieve design mesh regions."""
        meshops = []
        try:
            if settings.aedt_version > "2023.2":
                for ds in self._app.design_properties["MeshRegion"]["MeshSetup"]:
                    if isinstance(self._app.design_properties["MeshRegion"]["MeshSetup"][ds], (OrderedDict, dict)):
                        if self._app.design_properties["MeshRegion"]["MeshSetup"][ds]["DType"] == "RegionT":
                            dict_prop = self._app.design_properties["MeshRegion"]["MeshSetup"][ds]
                            if ds == "Global":
                                meshop = GlobalMeshRegion(self._app)
                            else:
                                meshop = MeshRegionCommon(
                                    self.omeshmodule, self.boundingdimension, self.modeler.model_units, self._app, ds
                                )
                            for el in dict_prop:
                                if el in meshop.__dict__:
                                    meshop.__dict__[el] = dict_prop[el]
                            meshops.append(meshop)
            else:
                for ds in self._app.design_properties["MeshRegion"]["MeshSetup"]["MeshRegions"]:
                    if isinstance(
                        self._app.design_properties["MeshRegion"]["MeshSetup"]["MeshRegions"][ds], (OrderedDict, dict)
                    ):
                        dict_prop = self._app.design_properties["MeshRegion"]["MeshSetup"]["MeshRegions"][ds]
                        if ds == "Global":
                            meshop = GlobalMeshRegion(self._app)
                        else:
                            meshop = MeshRegionCommon(
                                self.omeshmodule, self.boundingdimension, self.modeler.model_units, self._app, ds
                            )
                        for el in dict_prop:
                            if el in meshop.__dict__:
                                meshop.__dict__[el] = dict_prop[el]
                        meshops.append(meshop)
        except:
            pass
        return meshops

    @pyaedt_function_handler()
    def assign_mesh_level(self, mesh_order, meshop_name=None):
        """Assign a mesh level to objects.

        Parameters
        ----------
        mesh_order : dict
            Dictionary where the key is the object name and the value is
            the mesh level.
        meshop_name :  str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        list of :class:`pyaedt.modules.Mesh.MeshOperation`
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignMeshOperation
        """
        level_order = {}
        for obj in mesh_order:
            if mesh_order[obj] not in level_order.keys():
                level_order[mesh_order[obj]] = []
            level_order[mesh_order[obj]].append(obj)
        list_meshops = []
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

    @pyaedt_function_handler()
    def assign_mesh_from_file(self, objects, filename, meshop_name=None):
        """Assign a mesh from file to objects.

        Parameters
        ----------
        objects : list
            List of objects to which apply the mesh file.
        filename :  str
            Full path to .msh file.
        meshop_name :  str, optional
            Name of the mesh operations. Default is ``None``.

        Returns
        -------
         :class:`pyaedt.modules.Mesh.MeshOperation`
            Mesh Operation object. ``False`` when failed.

        References
        ----------

        >>> oModule.AssignMeshOperation
        """
        objs = self._app.modeler.convert_to_selections(objects, True)
        if meshop_name:
            meshop_name = generate_unique_name("MeshFile")
        else:
            meshop_name = generate_unique_name("MeshFile")
        props = OrderedDict({"Enable": True, "MaxLevel": str(0), "MinLevel": str(0), "Objects": objs})
        props["Local Mesh Parameters Enabled"] = False
        props["Mesh Reuse Enabled"] = True
        props["Mesh Reuse File"] = filename
        props["Local Mesh Parameters Type"] = "3DPolygon Local Mesh Parameters"
        props["Height count"] = "0"
        props["Top height"] = "0mm"
        props["Top ratio"] = "0"
        props["Bottom height"] = "0mm"
        props["Bottom ratio"] = "0"
        mop = MeshOperation(self, meshop_name, props, "Icepak")
        if mop.create():
            self.meshoperations.append(mop)
            return mop
        return False

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditMeshOperation
        """
        xsize = self.boundingdimension[0] / (15 * accuracy * accuracy)
        ysize = self.boundingdimension[1] / (15 * accuracy * accuracy)
        zsize = self.boundingdimension[2] / (10 * accuracy)
        MaxSizeRatio = 1 + (accuracy / 2)
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

    @pyaedt_function_handler()
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

        References
        ----------

        >>> oModule.EditMeshOperation
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

    @pyaedt_function_handler()
    def add_priority(self, entity_type, obj_list=None, comp_name=None, priority=3):
        """Add priority to objects.

        Parameters
        ----------
        entity_type : int
            Type of the entity. Options are ``1`` and ``2``, which represent respectively
            an object and a component.
        obj_list : list
            List of 3D objects, which can include conductors and dielectrics.
            If the user pass a non 3D object, it will be excluded.
        comp_name : str, optional
            Name of the component. The default is ``None``.
        priority : int, optional
            Level of priority. The default is ``3``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.UpdatePriorityList

        Examples
        --------

        >>> from pyaedt import Icepak
        >>> app = Icepak()
        >>> app.mesh.add_priority(entity_type=1, obj_list=app.modeler.object_names, priority=3)
        >>> app.mesh.add_priority(entity_type=2, comp_name=app.modeler.user_defined_component_names[0], priority=2)
        """
        i = priority

        args = ["NAME:UpdatePriorityListData"]
        if entity_type == 1:
            non_user_defined_component_parts = self._app.modeler.oeditor.GetChildNames()
            new_obj_list = []
            for comp in obj_list:
                if comp != "Region" and comp in non_user_defined_component_parts:
                    new_obj_list.append(comp)
            objects = ", ".join(new_obj_list)
            if not new_obj_list:
                return False
            prio = [
                "NAME:PriorityListParameters",
                "EntityType:=",
                "Object",
                "EntityList:=",
                objects,
                "PriorityNumber:=",
                i,
                "PriorityListType:=",
                ["2D", "3D"][int(self._app.modeler[new_obj_list[0]].is3d)],
            ]
            self._priorities_args.append(prio)
            args += self._priorities_args
        elif entity_type == 2:
            o = self.modeler.user_defined_components[comp_name]
            if (all(part.is3d for part in o.parts.values()) is False) and (
                any(part.is3d for part in o.parts.values()) is True
            ):
                prio_3d = [
                    "NAME:PriorityListParameters",
                    "EntityType:=",
                    "Component",
                    "EntityList:=",
                    comp_name,
                    "PriorityNumber:=",
                    i,
                    "PriorityListType:=",
                    "3D",
                ]
                prio_2d = [
                    "NAME:PriorityListParameters",
                    "EntityType:=",
                    "Component",
                    "EntityList:=",
                    comp_name,
                    "PriorityNumber:=",
                    i,
                    "PriorityListType:=",
                    "2D",
                ]
                self._priorities_args.append(prio_3d)
                self._priorities_args.append(prio_2d)
            elif all(part.is3d for part in o.parts.values()) is True:
                prio_3d = [
                    "NAME:PriorityListParameters",
                    "EntityType:=",
                    "Component",
                    "EntityList:=",
                    comp_name,
                    "PriorityNumber:=",
                    i,
                    "PriorityListType:=",
                    "3D",
                ]
                self._priorities_args.append(prio_3d)
            else:
                prio_2d = [
                    "NAME:PriorityListParameters",
                    "EntityType:=",
                    "Component",
                    "EntityList:=",
                    comp_name,
                    "PriorityNumber:=",
                    i,
                    "PriorityListType:=",
                    "2D",
                ]
                self._priorities_args.append(prio_2d)

            args += self._priorities_args
        self.modeler.oeditor.UpdatePriorityList(["NAME:UpdatePriorityListData"])
        self.modeler.oeditor.UpdatePriorityList(args)
        return True

    @pyaedt_function_handler()
    def assign_mesh_region(self, objectlist=[], level=5, is_submodel=False, name=None, virtual_region=False):
        """Assign a predefined surface mesh level to an object.

        Parameters
        ----------
        objectlist : list, optional
            List of objects to apply the mesh region to. The default
            is ``[]``.
        level : int, optional
            Level of the surface mesh. Options are ``1`` through ``5``. The default
            is ``5``.
        is_submodel : bool
            Define if the object list is made by component models
        name : str, optional
            Name of the mesh region. The default is ``"MeshRegion1"``.
        virtual_region : bool, optional
            Whether to use the virtual mesh region beta feature (available from version 22.2). The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.MeshIcepak.IcepakMesh.MeshRegion`

        References
        ----------

        >>> oModule.AssignMeshRegion
        """
        if not name:
            name = generate_unique_name("MeshRegion")
        meshregion = MeshRegionCommon(self.omeshmodule, self.boundingdimension, self.modeler.model_units, self._app)
        meshregion.UserSpecifiedSettings = False
        meshregion.Level = level
        meshregion.name = name
        meshregion.virtual_region = virtual_region
        if not objectlist:
            objectlist = [i for i in self.modeler.object_names]
        if is_submodel:
            meshregion.SubModels = objectlist
        else:
            meshregion.Objects = objectlist
        all_objs = [i for i in self.modeler.object_names]
        try:
            meshregion.create()
            created = True
        except Exception:  # pragma : no cover
            created = False
        if created:
            objectlist2 = self.modeler.object_names
            added_obj = [i for i in objectlist2 if i not in all_objs]
            if not added_obj:
                added_obj = [i for i in objectlist2 if i not in all_objs or i in objectlist]
            meshregion.Objects = added_obj
            meshregion.SubModels = None

            meshregion.update()
            return meshregion
        else:
            return False

    @pyaedt_function_handler()
    def generate_mesh(self, name=None):
        """Generate the mesh for a given setup name.

        Parameters
        ----------
        name : str, optional
            Name of the design to mesh. Default is ``None`` in which case the first available setup will be selected.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.GenerateMesh
        """
        if name is None:
            name = []
        return self._odesign.GenerateMesh(name) == 0

    @pyaedt_function_handler()
    def assign_mesh_level_to_group(
        self,
        mesh_level,
        groupName,
        localMeshParamEn=False,
        localMeshParameters="No local mesh parameters",
        meshop_name=None,
    ):
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
        :class:`pyaedt.modules.Mesh.MeshOperation`

        References
        ----------

        >>> oModule.AssignMeshOperation
        """
        if meshop_name:
            for el in self.meshoperations:
                if el.name == meshop_name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("MeshLevel")
        props = OrderedDict(
            {
                "Enable": True,
                "Level": mesh_level,
                "Local Mesh Parameters Enabled": localMeshParamEn,
                "Groups": [str(groupName)],
                "Local Mesh Parameters Type": localMeshParameters,
            }
        )
        mop = MeshOperation(self, meshop_name, props, "Icepak")
        mop.create()
        self.meshoperations.append(mop)
        return mop
