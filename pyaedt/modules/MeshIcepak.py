from abc import abstractmethod
from collections import OrderedDict
import warnings

from pyaedt.generic.general_methods import GrpcApiError
from pyaedt.generic.general_methods import _dim_arg
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings
from pyaedt.modules.Mesh import MeshOperation
from pyaedt.modules.Mesh import meshers


class CommonRegion(object):
    def __init__(self, app, name):
        self._app = app
        self._name = name
        self._padding_type = None  # ["Percentage Offset"] * 6
        self._padding_value = None  # [50] * 6
        self._coordinate_system = None  # "Global"
        self._dir_order = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]

    @property
    def padding_types(self):
        """
        Get a list of strings containing thepadding types used,
        one for each direction, in the following order:
        +X, -X, +Y, -Y, +Z, -Z.

        Returns
        -------
        List[str]
        """
        self._update_region_data()
        return self._padding_type

    @property
    def padding_values(self):
        """
        Get a list of padding values (string or float) used,
        one for each direction, in the following order:
        +X, -X, +Y, -Y, +Z, -Z.

        Returns
        -------
        List[Union[str, float]]
        """
        self._update_region_data()
        return self._padding_value

    @property
    def positive_x_padding_type(self):
        """
        Get a string with the padding type used in the +X direction.

        Returns
        -------
        str
        """
        return self._get_region_data("+X")

    @property
    def negative_x_padding_type(self):
        """
        Get a string with the padding type used in the -X direction.

        Returns
        -------
        str
        """
        return self._get_region_data("-X")

    @property
    def positive_y_padding_type(self):
        """
        Get a string with the padding type used in the +Y direction.

        Returns
        -------
        str
        """
        return self._get_region_data("+Y")

    @property
    def negative_y_padding_type(self):
        """
        Get a string with the padding type used in the -Y direction.

        Returns
        -------
        str
        """
        return self._get_region_data("-Y")

    @property
    def positive_z_padding_type(self):
        """
        Get a string with the padding type used in the +Z direction.

        Returns
        -------
        str
        """
        return self._get_region_data("+Z")

    @property
    def negative_z_padding_type(self):
        """
        Get a string with the padding type used in the -Z direction.

        Returns
        -------
        str
        """
        return self._get_region_data("-Z")

    @property
    def positive_x_padding(self):
        """
        Get a string with the padding value used in the +X direction.

        Returns
        -------
        float
        """
        return self._get_region_data("+X", False)

    @property
    def negative_x_padding(self):
        """
        Get a string with the padding value used in the -X direction.

        Returns
        -------
        float
        """
        return self._get_region_data("-X", False)

    @property
    def positive_y_padding(self):
        """
        Get a string with the padding value used in the +Y direction.

        Returns
        -------
        float
        """
        return self._get_region_data("+Y", False)

    @property
    def negative_y_padding(self):
        """
        Get a string with the padding value used in the -Y direction.

        Returns
        -------
        float
        """
        return self._get_region_data("-Y", False)

    @property
    def positive_z_padding(self):
        """
        Get a string with the padding value used in the +Z direction.

        Returns
        -------
        float
        """
        return self._get_region_data("+Z", False)

    @property
    def negative_z_padding(self):
        """
        Get a string with the padding value used in the -Z direction.

        Returns
        -------
        float
        """
        return self._get_region_data("-Z", False)

    @padding_types.setter
    def padding_types(self, values):
        if not isinstance(values, list):
            values = [values] * 6
        for i, direction in enumerate(self._dir_order):
            self._set_region_data(values[i], direction, True)

    @padding_values.setter
    def padding_values(self, values):
        if not isinstance(values, list):
            values = [values] * 6
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

    @property
    def object(self):
        """
        Get the subregion modeler object.

        Returns
        -------
        ::class::modeler.cad.object3d.Object3d
        """
        if isinstance(self, Region):
            return {
                "CreateRegion": oo
                for o, oo in self._app.modeler.objects_by_name.items()
                if oo.history().command == "CreateRegion"
            }.get("CreateRegion", None)
        else:
            return self._app.modeler.objects_by_name.get(self._name, None)

    @property
    def name(self):
        """
        Get the subregion name.

        Returns
        -------
        str
        """
        return self.object.name

    @name.setter
    def name(self, value):
        try:
            self._app.modeler.objects_by_name[self._name].name = value
        except KeyError:
            if self._app.modeler.objects_by_name[value].history().command == "CreateSubRegion":
                self._name = value

    def _set_region_data(self, value, direction=None, padding_type=True):
        self._update_region_data()
        region = self.object
        create_region = region.history()
        set_type = ["Data", "Type"][int(padding_type)]
        create_region.props["{} Padding {}".format(direction, set_type)] = value

    def _update_region_data(self):
        region = self.object
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
        super(Region, self).__init__(app, None)
        try:
            self._update_region_data()
        except AttributeError:
            pass


class SubRegion(CommonRegion):
    def __init__(self, app, parts, name=None):
        if name is None:
            name = generate_unique_name("SubRegion")
        super(SubRegion, self).__init__(app, name)
        self.create(0, "Percentage Offset", name, parts)

    def create(self, padding_values, padding_types, region_name, parts):
        """
        Create subregion object.

        Parameters
        ----------
        padding_values : list of str or float
            List of padding values to apply in each direction, in the following order:
            +X, -X, +Y, -Y, +Z, -Z.
        padding_types : list of str
            List of padding types to apply in each direction, in the following order:
            +X, -X, +Y, -Y, +Z, -Z.
        region_name : str
            Name to assign to the subregion.
        parts : list of str
            Parts to be included in the subregion.

         Returns
        -------
        bool
            True if successful, else False
        """
        try:
            if (
                self.object is not None and self._app.modeler.objects_by_name.get(self.object.name, False)
            ) or self._app.modeler.objects_by_name.get(region_name, False):
                self._app.logger.error("{} already exists in the design.".format(self.object.name))
                return False
            if not isinstance(parts, list):
                objects = [parts]
                if not isinstance(objects[0], str):
                    objects = [o.name for o in objects]
            self._app.modeler.create_subregion(padding_values, padding_types, parts, region_name)
            return True
        except:
            return False

    def delete(self):
        """
        Delete the subregion object.

         Returns
        -------
        bool
            True if successful, else False
        """
        try:
            self.object.delete()
            self._app.mesh.meshregions.remove(
                [mo for mo in self._app.mesh.meshregions.values() if mo.subregion == self][0]
            )
            return True
        except Exception:
            return False

    @property
    def parts(self):
        """
        Parts included in the subregion.

         Returns
        -------
        dict
            Dictionary with the part names as keys and ::class::modeler.cad.object3d.Object3d as values.
        """
        if self.object:
            return {
                obj_name: self._app.modeler[obj_name]
                for obj_name in self.object.history().props["Part Names"].split(",")
            }
        else:
            return {}

    @parts.setter
    def parts(self, parts):
        """
        Parts included in the subregion.

        Parameters
        -------
        parts : List[str]
            List of strings containing all the parts that must be included in the subregion.
        """
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

    @pyaedt_function_handler()
    def _dim_arg(self, value):
        if isinstance(value, str):
            return value
        else:
            return _dim_arg(value, getattr(self._mesh_class, "_model_units"))

    def parse_settings(self):
        """
        Parse mesh region settings.

        Returns
        -------
        dict
            List of strings containing all the parts that must be included in the subregion.
        """
        out = []
        for k, v in self.instance_settings.items():
            out.append(k + ":=")
            if k in ["MaxElementSizeX", "MaxElementSizeY", "MaxElementSizeZ", "MinGapX", "MinGapY", "MinGapZ"]:
                v = self._dim_arg(v)
            out.append(v)
        return out

    def _key_in_dict(self, key):
        if self._mesh_class.manual_settings:
            ref_dict = self.manual_mesh_settings
        else:
            ref_dict = self.automatic_mesh_settings
        return key in ref_dict or key in self.common_mesh_settings

    def __getitem__(self, key):
        if key == "Level":
            key = "MeshRegionResolution"
        if self._key_in_dict(key):
            return self.instance_settings[key]
        else:
            raise KeyError("Setting not available.")

    def __setitem__(self, key, value):
        if key == "Level":
            key = "MeshRegionResolution"
        if self._key_in_dict(key):
            if key == "MeshRegionResolution":
                try:
                    value = int(value)
                    if value < 1:
                        self._app.logger.warning(
                            'Minimum resolution value is 1. `"MeshRegionResolution"` has been ' "set to 1."
                        )
                        value = 1
                    if value > 5:
                        self._app.logger.warning(
                            'Maximum resolution value is 5. `"MeshRegionResolution"` has been ' "set to 5."
                        )
                        value = 5
                except TypeError:
                    pass
            self.instance_settings[key] = value
        else:
            self._app.logger.error("Setting not available.")

    def __delitem__(self, key):
        self._app.logger.error("Setting cannot be removed.")

    def __iter__(self):
        return self.instance_settings.__iter__()

    def __len__(self):
        return self.instance_settings.__len__()

    def __contains__(self, x):
        return self.instance_settings.__contains__(x)


class MeshRegionCommon(object):
    """
    Manages Icepak mesh region settings.

    Attributes:
        name : str
            Name of the mesh region.
        manual_settings : bool
            Whether to use manual settings or automatic ones.
        settings : ::class::modules.MeshIcepak.MeshSettings
            Dictionary-like object to handle settings
    """

    def __init__(self, units, app, name):
        self.manual_settings = False
        self.settings = MeshSettings(self, app)
        self._name = name
        self._model_units = units
        self._app = app

    @abstractmethod
    def update(self):
        """
        Update the mesh region object.
        """

    @abstractmethod
    def delete(self):
        """
        Delete the mesh region object.
        """

    @abstractmethod
    def create(self):
        """
        Create the mesh region object.
        """

    # backward compatibility
    def __getattr__(self, name):
        if "settings" in self.__dict__ and name in self.__dict__["settings"]:
            return self.__dict__["settings"][name]
        elif name == "UserSpecifiedSettings":
            return self.__dict__["manual_settings"]
        else:
            return self.__dict__[name]

    def __setattr__(self, name, value):
        if "settings" in self.__dict__ and name in self.settings:
            self.settings[name] = value
        elif name == "UserSpecifiedSettings":
            self.__dict__["manual_settings"] = value
        else:
            super(MeshRegionCommon, self).__setattr__(name, value)


class GlobalMeshRegion(MeshRegionCommon):
    def __init__(self, app):
        self.global_region = Region(app)
        super(GlobalMeshRegion, self).__init__(
            app.modeler.model_units,
            app,
            name="Settings",
        )

    @property
    def name(self):
        """
        Mesh region name.
        """
        return "Global"

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
            self._app.omeshmodule.EditGlobalMeshRegion(args)
            return True
        except GrpcApiError:  # pragma : no cover
            return False

    @property
    def Objects(self):
        """
        Get the region object from the modeler.
        """
        return self.global_region.name

    def delete(self):
        """
        Delete the region object in the modeler.
        """
        self.global_region.object.delete()
        self.global_region = None

    def create(self):
        """
        Create the region object in the modeler.
        """
        self.delete()
        self.global_region = Region(self._app)
        self.global_region.create(self.padding_types, self.padding_values)


class MeshRegion(MeshRegionCommon):
    def __init__(self, app, objects=None, name=None, **kwargs):
        if name is None:
            name = generate_unique_name("MeshRegion")
        super(MeshRegion, self).__init__(
            app.modeler.model_units,
            app,
            name,
        )
        self.enable = True
        if settings.aedt_version > "2023.2" and objects is not None:
            if not isinstance(objects, list):
                objects = [objects]
            if (
                objects[0] not in self._app.modeler.user_defined_components
                and self._app.modeler[objects[0]].history().command == "CreateSubRegion"
            ):
                self._assignment = objects[0]
            else:
                self._assignment = SubRegion(app, objects)
        else:
            self._assignment = objects
        if self._assignment is not None:
            self.create()
        # backward compatibility
        if any(i in kwargs for i in ["dimension", "meshmodule", "unit"]):
            warnings.warn(
                "``MeshRegion`` initialization changed. ``meshmodule``, ``dimension``, ``unit`` "
                "arguments are not supported anymore.",
                DeprecationWarning,
            )
            if "dimension" in kwargs:
                self.manual_settings = True
                self.settings["MaxElementSizeX"] = float(kwargs["dimension"][0]) / 20
                self.settings["MaxElementSizeY"] = float(kwargs["dimension"][1]) / 20
                self.settings["MaxElementSizeZ"] = float(kwargs["dimension"][2]) / 20

    def _parse_assignment_value(self, assignment=None):
        if assignment is None:
            assignment = self.assignment
        a = []
        if isinstance(assignment, SubRegion):
            a += ["Objects:=", [assignment.name]]
        else:
            if any(o in self._app.modeler.object_names for o in assignment):
                obj_assignment = [o for o in assignment if o in self._app.modeler.object_names]
                a += ["Objects:=", obj_assignment]
            if any(o in self._app.modeler.user_defined_components for o in assignment):
                obj_assignment = [o for o in assignment if o in self._app.modeler.user_defined_components]
                a += ["Submodels:=", obj_assignment]
        return a

    @property
    def name(self):
        """
        Name of the mesh region.

        Returns
        -------
        str
        """
        return self._name

    @name.setter
    def name(self, value):
        self._app.odesign.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Icepak",
                    ["NAME:PropServers", "MeshRegion:{}".format(self.name)],
                    ["NAME:ChangedProps", ["NAME:Name", "Value:=", value]],
                ],
            ]
        )
        self._app.modeler.refresh()
        self._name = value
        if isinstance(self.assignment, SubRegion):
            self._assignment = self.assignment

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
        args += self._parse_assignment_value()
        args += ["UserSpecifiedSettings:=", not self.manual_settings]
        try:
            self._app.omeshmodule.EditMeshRegion(self.name, args)
            return True
        except GrpcApiError:  # pragma : no cover
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
        self._app.omeshmodule.DeleteMeshRegions([self.name])
        self._app.mesh.meshregions.remove(self)
        return True

    @property
    def assignment(self):
        """
        List of objects included in mesh region.

        Returns
        -------
        list
        """
        if isinstance(self._assignment, SubRegion):
            # try to update name
            try:
                parts = self._app.odesign.GetChildObject("Mesh").GetChildObject(self.name).GetPropValue("Parts")
                if not isinstance(parts, list):
                    parts = [parts]
                sub_regions = self._app.modeler.non_model_objects
                for sr in sub_regions:
                    p1 = []
                    p2 = []
                    if "Part Names" in self._app.modeler[sr].history().props:
                        p1 = self._app.modeler[sr].history().props.get("Part Names", None)
                        if not isinstance(p1, list):
                            p1 = [p1]
                    elif "Submodel Names" in self._app.modeler[sr].history().props:
                        p2 = self._app.modeler[sr].history().props.get("Submodel Names", None)
                        if not isinstance(p2, list):
                            p2 = [p2]
                    p1 += p2
                    if "CreateSubRegion" == self._app.modeler[sr].history().command and all(p in p1 for p in parts):
                        self._assignment.name = sr
            except GrpcApiError:
                pass
            return self._assignment
        elif isinstance(self._assignment, list):
            return self._assignment
        else:
            return [self._assignment]

    @assignment.setter
    def assignment(self, value):
        arg = ["NAME:Assignment"] + self._parse_assignment_value(value)
        try:
            self._app.omeshmodule.ReassignMeshRegion(self.name, arg)
            self._assignment = value
        except GrpcApiError:  # pragma : no cover
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
        args += ["UserSpecifiedSettings:=", not self.manual_settings]
        args += self._parse_assignment_value()
        self._app.omeshmodule.AssignMeshRegion(args)
        self._app.mesh.meshregions.append(self)
        self._app.modeler.refresh_all_ids()
        self._assignment = self.assignment
        return True

    # backward compatibility
    @property
    def Enable(self):
        """
        Get whether the mesh region is enabled.

        Returns
        -------
        book
        """
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
        """
        List of objects included in mesh region.

        Returns
        -------
        list
        """
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
        """
        List of objects included in mesh region.

        Returns
        -------
        list
        """
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
        except Exception as e:
            self._app.logger.error(e)

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
                                meshop = MeshRegion(self._app, None, ds)
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
                            meshop = MeshRegion(self._app, None, ds)
                        for el in dict_prop:
                            if el in meshop.__dict__:
                                meshop.__dict__[el] = dict_prop[el]
                        meshops.append(meshop)
        except Exception as e:
            self._app.logger.error(e)

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

        .. deprecated:: 0.8.14

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
        warnings.warn("This method was deprecated in version 8.14.", DeprecationWarning)
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
    def assign_mesh_region(self, objectlist=None, level=5, name=None, **kwargs):
        """Assign a predefined surface mesh level to an object.

        Parameters
        ----------
        objectlist : list, optional
            List of objects to apply the mesh region to. The default
            is ``None``, in which case all objects are selected.
        level : int, optional
            Level of the surface mesh. Options are ``1`` through ``5``. The default
            is ``5``.
        name : str, optional
            Name of the mesh region. The default is ``"MeshRegion1"``.

        Returns
        -------
        :class:`pyaedt.modules.MeshIcepak.IcepakMesh.MeshRegion`

        References
        ----------

        >>> oModule.AssignMeshRegion
        """
        if not name:
            name = generate_unique_name("MeshRegion")
        if objectlist is None:
            objectlist = [i for i in self.modeler.object_names]
        meshregion = MeshRegion(self._app, objectlist, name)
        meshregion.manual_settings = False
        meshregion.Level = level
        all_objs = [i for i in self.modeler.object_names]
        created = bool(meshregion)
        if created:
            if settings.aedt_version < "2024.1":
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
