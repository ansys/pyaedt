"""
This module contains these Primitives classes: `Polyline` and `Primitives`.
"""
from __future__ import absolute_import  # noreorder

from collections import OrderedDict
import copy
import math
import os
import random
import string
import time
import warnings

from pyaedt.application.Variables import Variable
from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.general_methods import _dim_arg
from pyaedt.generic.general_methods import _uname
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_number
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import settings
from pyaedt.modeler.cad.Modeler import BaseCoordinateSystem
from pyaedt.modeler.cad.Modeler import CoordinateSystem
from pyaedt.modeler.cad.Modeler import FaceCoordinateSystem
from pyaedt.modeler.cad.Modeler import Lists
from pyaedt.modeler.cad.Modeler import Modeler
from pyaedt.modeler.cad.Modeler import ObjectCoordinateSystem
from pyaedt.modeler.cad.components_3d import UserDefinedComponent
from pyaedt.modeler.cad.elements3d import EdgePrimitive
from pyaedt.modeler.cad.elements3d import FacePrimitive
from pyaedt.modeler.cad.elements3d import Plane
from pyaedt.modeler.cad.elements3d import Point
from pyaedt.modeler.cad.elements3d import VertexPrimitive
from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.cad.polylines import Polyline
from pyaedt.modeler.cad.polylines import PolylineSegment
from pyaedt.modeler.geometry_operators import GeometryOperators
from pyaedt.modules.MaterialLib import Material

default_materials = {
    "Icepak": "air",
    "HFSS": "vacuum",
    "Maxwell 3D": "vacuum",
    "Maxwell 2D": "vacuum",
    "2D Extractor": "copper",
    "Q3D Extractor": "copper",
    "HFSS 3D Layout": "copper",
    "Mechanical": "copper",
}

aedt_wait_time = 0.1


class GeometryModeler(Modeler):
    """Manages the main AEDT Modeler functionalities for geometry-based designs.

    Parameters
    ----------
    app :
        Inherited parent object.
    is3d : bool, optional
        Whether the model is 3D. The default is ``True``.
    """

    @pyaedt_function_handler()
    def __getitem__(self, partId):
        """Get the object ``Object3D`` for a given object ID or object name.

        Parameters
        ----------
        partId : int or str
            Object ID or object name from the 3D modeler.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            Returns ``None`` if the part ID or the object name is not found.

        """
        if isinstance(partId, (int, str)) and not (
            partId in self.objects or partId in self._object_names_to_ids or partId in self.user_defined_components
        ):
            self.refresh_all_ids()
        if isinstance(partId, int):
            if partId in self.objects:
                return self.objects[partId]
        elif partId in self._object_names_to_ids:
            return self.objects[self._object_names_to_ids[partId]]
        elif partId in self.user_defined_components:
            return self.user_defined_components[partId]
        elif isinstance(partId, Object3d) or isinstance(partId, UserDefinedComponent):
            return partId
        return None

    def __init__(self, app, is3d=True):
        self._app = app
        Modeler.__init__(self, app)
        # TODO Refactor this as a dictionary with names as key
        self._coordinate_systems = []
        self._user_lists = []
        self._planes = []
        self._is3d = is3d
        self._solids = []
        self._sheets = []
        self._lines = []
        self._points = []
        self._unclassified = []
        self._all_object_names = []
        self.objects = {}
        self.user_defined_components = {}
        self._object_names_to_ids = {}
        self.points = {}
        self.refresh()

    class Position:
        """Position.

        Parameters
        ----------
        args : list or int
            Position of the item as either a list of the ``[x, y, z]`` coordinates
            or three separate values. If no or insufficient arguments
            are specified, ``0`` is applied.

        """

        @pyaedt_function_handler()
        def __getitem__(self, item):
            if item == 0:
                return self.X
            elif item == 1:
                return self.Y
            elif item == 2:
                return self.Z
            else:
                raise IndexError

        @pyaedt_function_handler()
        def __setitem__(self, item, value):
            if item == 0:
                self.X = value
            elif item == 1:
                self.Y = value
            elif item == 2:
                self.Z = value

        def __len__(self):
            return 3

        def __init__(self, *args):
            if len(args) == 1 and type(args[0]) is list:
                try:
                    self.X = args[0][0]
                except:
                    self.X = 0
                try:
                    self.Y = args[0][1]
                except:
                    self.Y = 0
                try:
                    self.Z = args[0][2]
                except:
                    self.Z = 0
            else:
                try:
                    self.X = args[0]
                except:
                    self.X = 0
                try:
                    self.Y = args[1]
                except:
                    self.Y = 0
                try:
                    self.Z = args[2]
                except:
                    self.Z = 0

    class SweepOptions(object):
        """Manages sweep options.

        Parameters
        ----------
        draftType : str, optional
            Type of the draft. Options are ``"Round"``, ``"Natural"``,
            and ``"Extended"``. The default is ``"Round"``.
        draftAngle : str, optional
            Draft angle with units. The default is ``"0deg"``.
        twistAngle : str, optional
            Twist angle with units. The default is ``"0deg"``.

        """

        @pyaedt_function_handler()
        def __init__(self, draftType="Round", draftAngle="0deg", twistAngle="0deg"):
            self.DraftType = draftType
            self.DraftAngle = draftAngle
            self.TwistAngle = twistAngle

    @property
    def _design_properties(self):
        return self._app.design_properties

    @property
    def _odefinition_manager(self):
        return self._app.odefinition_manager

    @property
    def _omaterial_manager(self):
        return self._app.omaterial_manager

    @property
    def coordinate_systems(self):
        """Coordinate systems."""
        if settings.aedt_version > "2022.2":
            cs_names = [i for i in self.oeditor.GetChildNames("CoordinateSystems") if i != "Global"]
            for cs_name in cs_names:
                props = {}
                local_names = [i.name for i in self._coordinate_systems]
                if cs_name not in local_names:
                    if self.oeditor.GetChildObject(cs_name).GetPropValue("Type") == "Relative":
                        self._coordinate_systems.append(CoordinateSystem(self, props, cs_name))
                    elif self.oeditor.GetChildObject(cs_name).GetPropValue("Type") == "Face":
                        self._coordinate_systems.append(FaceCoordinateSystem(self, props, cs_name))
                    elif self.oeditor.GetChildObject(cs_name).GetPropValue("Type") == "Object":
                        self._coordinate_systems.append(ObjectCoordinateSystem(self, props, cs_name))
            return self._coordinate_systems
        if not self._coordinate_systems:
            self._coordinate_systems = self._get_coordinates_data()
        return self._coordinate_systems

    @property
    def user_lists(self):
        """User lists."""
        if not self._user_lists:
            self._user_lists = self._get_lists_data()
        return self._user_lists

    @property
    def planes(self):
        """Planes."""
        if not self._planes:
            self._planes = self._get_planes_data()
        return self._planes

    @property
    def oeditor(self):
        """AEDT ``oEditor`` module.

        References
        ----------

        >>> oEditor = oDesign.SetActiveEditor("3D Modeler")"""

        return self._app.oeditor

    @property
    def materials(self):
        """Material library used in the project.

        Returns
        -------
        :class:`pyaedt.modules.MaterialLib.Materials`

        """
        return self._app.materials

    @property
    def model_units(self):
        """Model units as a string. For example, ``"mm"``.

        References
        ----------

        >>> oEditor.GetModelUnits
        >>> oEditor.SetModelUnits
        """
        return self.oeditor.GetModelUnits()

    @model_units.setter
    def model_units(self, units):
        assert units in AEDT_UNITS["Length"], "Invalid units string {0}.".format(units)
        self.oeditor.SetModelUnits(["NAME:Units Parameter", "Units:=", units, "Rescale:=", False])

    @property
    def selections(self):
        """Selections.

        References
        ----------

        >>> oEditor.GetSelections
        """
        return self.oeditor.GetSelections()

    @property
    def obounding_box(self):
        """Bounding box.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        return self.oeditor.GetModelBoundingBox()

    @property
    def dimension(self):
        """Dimensions.

        Returns
        -------
        str
            Dimensionality, which is either ``"2D"`` or ``"3D"``.

        References
        ----------

        >>> oDesign.Is2D
        """
        try:
            if self._odesign.Is2D():
                return "2D"
            else:
                return "3D"
        except:
            if self.design_type == "2D Extractor":
                return "2D"
            else:
                return "3D"

    @property
    def design_type(self):
        """Design type.

        References
        ----------

        >>> oDesign.GetDesignType
        """
        return self._app.design_type

    @property
    def geometry_mode(self):
        """Geometry mode.

        References
        ----------

        >>> oDesign.GetGeometryMode"""
        return self._odesign.GetGeometryMode()

    @property
    def solid_bodies(self):
        """List of object names.

        .. note::
            Non-model objects are also returned.

        Returns
        -------
        list os str
            List of object names with the object name as the key.

        References
        ----------

        >>> oEditor.GetObjectsInGroup
        """
        if self.dimension == "3D":
            objects = self.oeditor.GetObjectsInGroup("Solids")
        else:
            objects = self.oeditor.GetObjectsInGroup("Sheets")
        return list(objects)

    @property
    def _modeler(self):
        return self

    @property
    def solid_objects(self):
        """List of all solid objects.

        Returns
        -------
        list of :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.
        """
        # self._refresh_solids()
        return [self[name] for name in self.solid_names if self[name]]

    @property
    def sheet_objects(self):
        """List of all sheet objects.

        Returns
        -------
        list of :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.
        """
        # self._refresh_sheets()
        return [self[name] for name in self.sheet_names if self[name]]

    @property
    def line_objects(self):
        """List of all line objects.

        Returns
        -------
        list of :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.
        """
        # self._refresh_lines()
        return [self[name] for name in self.line_names if self[name]]

    @property
    def point_objects(self):
        """List of points objects.

        Returns
        -------
        list of :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.
        """
        # self._refresh_points()
        return [self.points[name] for name in self.point_names]

    @property
    def unclassified_objects(self):
        """List of all unclassified objects.

        Returns
        -------
        list of :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.
        """
        # self._refresh_unclassified()
        return [self[name] for name in self.unclassified_names if name is not None]

    @property
    def object_list(self):
        """List of all objects.

        Returns
        -------
        list of :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.
        """
        self._refresh_object_types()
        return [self[name] for name in self._all_object_names if name is not None and name not in self.point_names]

    @property
    def solid_names(self):
        """List of the names of all solid objects.

        Returns
        -------
        List
        """
        self._refresh_solids()
        return self._solids

    @property
    def sheet_names(self):
        """List of the names of all sheet objects.

        Returns
        -------
        str
        """
        self._refresh_sheets()
        return self._sheets

    @property
    def line_names(self):
        """List of the names of all line objects.

        Returns
        -------
        str
        """
        self._refresh_lines()
        return self._lines

    @property
    def unclassified_names(self):
        """List of the names of all unclassified objects.

        Returns
        -------
        str
        """
        self._refresh_unclassified()
        return self._unclassified

    @property
    def object_names(self):
        """List of the names of all objects.

        Returns
        -------
        str
        """
        self._refresh_object_types()
        return [i for i in self._all_object_names if i not in self._unclassified and i not in self._points]

    @property
    def point_names(self):
        """List of the names of all points.

        Returns
        -------
        str
        """
        self._refresh_points()
        return self._points

    @property
    def user_defined_component_names(self):
        """List of the names of all 3D component objects.

        References
        ----------

        >>> oEditor.Get3DComponentDefinitionNames
        >>> oEditor.Get3DComponentInstanceNames
        """
        obs3d = []
        try:
            comps3d = self.oeditor.Get3DComponentDefinitionNames()
            for comp3d in comps3d:
                obs3d += list(self.oeditor.Get3DComponentInstanceNames(comp3d))
            udm = []
            if "UserDefinedModels" in self.oeditor.GetChildTypes():
                try:
                    udm = list(self.oeditor.GetChildNames("UserDefinedModels"))
                except:  # pragma: no cover
                    udm = []
            obs3d = list(set(udm + obs3d))
            new_obs3d = copy.deepcopy(obs3d)
            if self.user_defined_components:
                existing_components = list(self.user_defined_components.keys())
                new_obs3d = [i for i in obs3d if i]
                for _, value in enumerate(existing_components):
                    if value not in new_obs3d:
                        new_obs3d.append(value)

        except Exception as e:
            new_obs3d = []
        return new_obs3d

    @property
    def layout_component_names(self):
        """List of the names of all Layout component objects.

        Returns
        -------
        list
            Layout component names.
        """
        lc_names = []
        if self.user_defined_components:
            for name, value in self.user_defined_components.items():
                if value.layout_component:
                    lc_names.append(name)
        return lc_names

    @property
    def _oproject(self):
        """Project."""
        return self._app.oproject

    @property
    def _odesign(self):
        """Design."""
        return self._app._odesign

    @property
    def _materials(self):
        """Material Manager that is used to manage materials in the project.

        Returns
        -------
        :class:`pyaedt.modules.MaterialLib.Materials`
            Material Manager that is used to manage materials in the project.
        """
        return self._app.materials

    @property
    def defaultmaterial(self):
        """Default material."""
        return default_materials[self._app._design_type]

    @property
    def logger(self):
        """Logger."""
        return self._app.logger

    @property
    def version(self):
        """Version."""
        return self._app._aedt_version

    @property
    def model_objects(self):
        """List of the names of all model objects."""
        return self._get_model_objects(model=True)

    @property
    def non_model_objects(self):
        """List of objects of all non-model objects."""
        return list(self.oeditor.GetObjectsInGroup("Non Model"))

    @property
    def model_consistency_report(self):
        """Summary of detected inconsistencies between the AEDT modeler and PyAEDT structures.

        Returns
        -------
        dict

        """
        obj_names = self.object_names
        missing = []
        for name in obj_names:
            if name not in self._object_names_to_ids:
                missing.append(name)
        non_existent = []
        for name in self._object_names_to_ids:
            if name not in obj_names and name not in self.unclassified_names:
                non_existent.append(name)
        report = {"Missing Objects": missing, "Non-Existent Objects": non_existent}
        return report

    @property
    def objects_by_name(self):
        """Object dictionary organized by name.

        Returns
        -------
        dict
        """
        obj_dict = {}
        for _, v in self.objects.items():
            obj_dict[v._m_name] = v
        return obj_dict

    @pyaedt_function_handler()
    def refresh(self):
        """Refresh this object."""
        self._solids = []
        self._sheets = []
        self._lines = []
        self._points = []
        self._unclassified = []
        self._all_object_names = []
        self.objects = {}
        self.user_defined_components = {}
        self._object_names_to_ids = {}
        self._currentId = 0
        self._refresh_object_types()
        self._refresh_all_ids_from_aedt_file()
        self.refresh_all_ids()

    @pyaedt_function_handler()
    def _get_commands(self, name):
        try:
            return self.oeditor.GetChildObject(name).GetChildNames()
        except:
            return []

    @pyaedt_function_handler()
    def _create_user_defined_component(self, name):
        if name not in list(self.user_defined_components.keys()):
            native_component_properties = self._get_native_component_properties(name)
            if native_component_properties:
                component_type = native_component_properties["NativeComponentDefinitionProvider"]["Type"]
                o = UserDefinedComponent(self, name, native_component_properties, component_type)
            else:
                o = UserDefinedComponent(self, name)
            self.user_defined_components[name] = o
        else:
            o = self.user_defined_components[name]
        return o

    @pyaedt_function_handler()
    def _create_point(self, name):
        point = Point(self, name)
        self.refresh_all_ids()

        return point

    @pyaedt_function_handler()
    def _refresh_all_ids_from_aedt_file(self):
        if not self._design_properties or "ModelSetup" not in self._design_properties:
            return False

        try:
            groups = self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["Groups"]["Group"]
        except KeyError:
            groups = []
        if not isinstance(groups, list):
            groups = [groups]
        try:
            self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["ToplevelParts"]["GeometryPart"]
        except KeyError:
            return 0
        for el in self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["ToplevelParts"][
            "GeometryPart"
        ]:
            if isinstance(el, (OrderedDict, dict)):
                attribs = el["Attributes"]
                operations = el.get("Operations", None)
            else:
                attribs = self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["ToplevelParts"][
                    "GeometryPart"
                ]["Attributes"]
                operations = self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"][
                    "ToplevelParts"
                ]["GeometryPart"]["Operations"]
            if attribs["Name"] in self._all_object_names:
                pid = 0

                if operations and isinstance(operations.get("Operation", None), (OrderedDict, dict)):
                    try:
                        pid = operations["Operation"]["ParentPartID"]
                    except:  # pragma: no cover
                        pass
                elif operations and isinstance(operations.get("Operation", None), list):
                    try:
                        pid = operations["Operation"][0]["ParentPartID"]
                    except:
                        pass
                o = self._create_object(name=attribs["Name"], pid=pid, use_cached=True)
                o._part_coordinate_system = attribs["PartCoordinateSystem"]
                if "NonModel" in attribs["Flags"]:
                    o._model = False
                else:
                    o._model = True
                if "Wireframe" in attribs["Flags"]:
                    o._wireframe = True
                else:
                    o._wireframe = False
                groupname = ""
                for group in groups:
                    if attribs["GroupId"] == group["GroupID"]:
                        groupname = group["Attributes"]["Name"]

                o._m_groupName = groupname
                try:
                    o._color = tuple(int(x) for x in attribs["Color"][1:-1].split(" "))
                except:
                    o._color = None
                o._surface_material = attribs.get("SurfaceMaterialValue", None)
                if o._surface_material:
                    o._surface_material = o._surface_material[1:-1].lower()
                if "MaterialValue" in attribs:
                    o._material_name = attribs["MaterialValue"][1:-1].lower()

                o._is_updated = True
        return len(self.objects)

    @pyaedt_function_handler()
    def cleanup_objects(self):
        """Clean up objects that no longer exist in the modeler because
        they were removed by previous operations.

        This method also updates object IDs that may have changed via
        a modeler operation such as :func:`pyaedt.modeler.Model3D.Modeler3D.unite`
        or :func:`pyaedt.modeler.Model2D.Modeler2D.unite`.

        Returns
        -------
        dict
           Dictionary of updated object IDs.

        """
        new_object_dict = {}
        new_object_id_dict = {}
        new_points_dict = {}

        all_objects = self.object_names
        all_unclassified = self.unclassified_names
        all_objs = all_objects + all_unclassified
        for old_id, obj in self.objects.items():
            if obj.name in all_objs:
                # Check if ID can change in boolean operations
                # updated_id = obj.id  # By calling the object property we get the new id
                new_object_id_dict[obj.name] = old_id
                new_object_dict[old_id] = obj
        for old_id, obj in self.points.items():
            if obj.name in self._points:
                new_points_dict[obj.name] = obj
        self.objects = new_object_dict
        self._object_names_to_ids = new_object_id_dict
        self.points = new_points_dict

    @pyaedt_function_handler()
    def find_new_objects(self):
        """Find any new objects in the modeler that were created
        by previous operations.

        Returns
        -------
        dict
            Dictionary of new objects.

        """
        new_objects = []
        for obj_name in self.object_names:
            if obj_name not in self._object_names_to_ids:
                new_objects.append(obj_name)
        return new_objects

    @pyaedt_function_handler()
    def add_new_objects(self):
        """Add objects that have been created in the modeler by
        previous operations.

        Returns
        -------
        list
            List of added objects.

        """
        # TODO: Need to improve documentation for this method.
        added_objects = []

        for obj_name in self.object_names:
            if obj_name not in self._object_names_to_ids:
                self._create_object(obj_name)
                added_objects.append(obj_name)
        for obj_name in self.unclassified_names:
            if obj_name not in self._object_names_to_ids:
                self._create_object(obj_name)
                added_objects.append(obj_name)
        for obj_name in self.point_names:
            if obj_name not in self.points.keys():
                self._create_object(obj_name)
                added_objects.append(obj_name)
        return added_objects

    @pyaedt_function_handler()
    def add_new_user_defined_component(self):
        """Add 3D components and user-defined models that have been created in the modeler by
        previous operations.

        Returns
        -------
        list
            List of added components.

        """
        added_component = []
        for comp_name in self.user_defined_component_names:
            if comp_name not in self.user_defined_components:
                self._create_user_defined_component(comp_name)
            added_component.append(comp_name)
        return added_component

    # TODO Eliminate this - check about import_3d_cad
    # Should no longer be a problem
    @pyaedt_function_handler()
    def refresh_all_ids(self):
        """Refresh all IDs."""

        self.add_new_objects()
        self.add_new_user_defined_component()
        self.cleanup_objects()

        return len(self.objects)

    @pyaedt_function_handler()
    def get_objects_by_material(self, materialname=None):
        """Get a list of objects either of a specified material or classified by material.

        Parameters
        ----------
        materialname : str
            Name of the material. The default is ``None``.

        Returns
        -------
        list of class:`pyaedt.modeler.cad.object3d.Object3d`
            If a material name is not provided, the method returns
            a list of dictionaries where keys are material names
            of conductors, dielectrics, gases, and liquids respectively
            in the design and values are objects assigned to these materials.
            If a material name is provided, the method returns a list
            of objects assigned to the material.

        References
        ----------

        >>> oEditor.GetObjectsByMaterial

        """
        obj_lst = []
        if materialname is not None:
            for obj in self.object_list:
                if obj and ("[" in obj.material_name or "(" in obj.material_name) and obj.object_type == "Solid":
                    material = (
                        self._app.odesign.GetChildObject("3D Modeler")
                        .GetChildObject(obj.name)
                        .GetPropEvaluatedValue("Material")
                        .lower()
                    )
                    if materialname.lower() == material:
                        obj_lst.append(obj)
                elif obj and (obj.material_name == materialname or obj.material_name == materialname.lower()):
                    obj_lst.append(obj)
        else:
            obj_lst = [
                self._get_object_dict_by_material(self.materials.conductors),
                self._get_object_dict_by_material(self.materials.dielectrics),
                self._get_object_dict_by_material(self.materials.gases),
                self._get_object_dict_by_material(self.materials.liquids),
            ]
        return obj_lst

    @pyaedt_function_handler()
    def _get_coordinates_data(self):  # pragma: no cover
        coord = []
        id2name = {1: "Global"}
        name2refid = {}
        if self._design_properties and "ModelSetup" in self._design_properties:
            cs = self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["CoordinateSystems"]
            for ds in cs:
                try:
                    if isinstance(cs[ds], (OrderedDict, dict)):
                        if cs[ds]["OperationType"] == "CreateRelativeCoordinateSystem":
                            props = cs[ds]["RelativeCSParameters"]
                            name = cs[ds]["Attributes"]["Name"]
                            cs_id = cs[ds]["ID"]
                            id2name[cs_id] = name
                            name2refid[name] = cs[ds]["ReferenceCoordSystemID"]
                            coord.append(CoordinateSystem(self, props, name))
                            if "ZXZ" in props["Mode"]:
                                coord[-1].mode = "zxz"
                            elif "ZYZ" in props["Mode"]:
                                coord[-1].mode = "zyz"
                            else:
                                coord[-1].mode = "axis"
                        elif cs[ds]["OperationType"] == "CreateFaceCoordinateSystem":
                            name = cs[ds]["Attributes"]["Name"]
                            cs_id = cs[ds]["ID"]
                            id2name[cs_id] = name
                            op_id = cs[ds]["PlaceHolderOperationID"]
                            geometry_part = self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"][
                                "ToplevelParts"
                            ]["GeometryPart"]
                            if isinstance(geometry_part, (OrderedDict, dict)):
                                op = geometry_part["Operations"]["FaceCSHolderOperation"]
                                if isinstance(op, (OrderedDict, dict)):
                                    if op["ID"] == op_id:
                                        props = op["FaceCSParameters"]
                                        coord.append(FaceCoordinateSystem(self, props, name))
                                elif isinstance(op, list):
                                    for iop in op:
                                        if iop["ID"] == op_id:
                                            props = iop["FaceCSParameters"]
                                            coord.append(FaceCoordinateSystem(self, props, name))
                                            break
                            elif isinstance(geometry_part, list):
                                for gp in geometry_part:
                                    op = gp["Operations"]["FaceCSHolderOperation"]
                                    if isinstance(op, (OrderedDict, dict)):
                                        if op["ID"] == op_id:
                                            props = op["FaceCSParameters"]
                                            coord.append(FaceCoordinateSystem(self, props, name))
                                    elif isinstance(op, list):
                                        for iop in op:
                                            if iop["ID"] == op_id:
                                                props = iop["FaceCSParameters"]
                                                coord.append(FaceCoordinateSystem(self, props, name))
                                                break
                    elif isinstance(cs[ds], list):
                        for el in cs[ds]:
                            if el["OperationType"] == "CreateRelativeCoordinateSystem":
                                props = el["RelativeCSParameters"]
                                name = el["Attributes"]["Name"]
                                cs_id = el["ID"]
                                id2name[cs_id] = name
                                name2refid[name] = el["ReferenceCoordSystemID"]
                                coord.append(CoordinateSystem(self, props, name))
                                if "ZXZ" in props["Mode"]:
                                    coord[-1].mode = "zxz"
                                elif "ZYZ" in props["Mode"]:
                                    coord[-1].mode = "zyz"
                                else:
                                    coord[-1].mode = "axis"
                            elif el["OperationType"] == "CreateFaceCoordinateSystem":
                                name = el["Attributes"]["Name"]
                                cs_id = el["ID"]
                                id2name[cs_id] = name
                                op_id = el["PlaceHolderOperationID"]
                                geometry_part = self._design_properties["ModelSetup"]["GeometryCore"][
                                    "GeometryOperations"
                                ]["ToplevelParts"]["GeometryPart"]
                                if isinstance(geometry_part, (OrderedDict, dict)):
                                    op = geometry_part["Operations"]["FaceCSHolderOperation"]
                                    if isinstance(op, (OrderedDict, dict)):
                                        if op["ID"] == op_id:
                                            props = op["FaceCSParameters"]
                                            coord.append(FaceCoordinateSystem(self, props, name))
                                    elif isinstance(op, list):
                                        for iop in op:
                                            if iop["ID"] == op_id:
                                                props = iop["FaceCSParameters"]
                                                coord.append(FaceCoordinateSystem(self, props, name))
                                                break
                                elif isinstance(geometry_part, list):
                                    for gp in geometry_part:
                                        try:
                                            op = gp["Operations"]["FaceCSHolderOperation"]
                                        except KeyError:
                                            continue
                                        if isinstance(op, (OrderedDict, dict)):
                                            if op["ID"] == op_id:
                                                props = op["FaceCSParameters"]
                                                coord.append(FaceCoordinateSystem(self, props, name))
                                        elif isinstance(op, list):
                                            for iop in op:
                                                if iop["ID"] == op_id:
                                                    props = iop["FaceCSParameters"]
                                                    coord.append(FaceCoordinateSystem(self, props, name))
                                                    break
                except:
                    pass
            for cs in coord:
                if isinstance(cs, CoordinateSystem):
                    try:
                        cs._ref_cs = id2name[name2refid[cs.name]]
                    except:
                        pass
        coord.reverse()
        return coord

    def _get_lists_data(self):
        """Retrieve user object list data.

        Returns
        -------
        [Dict with List information]
        """
        design_lists = []
        if self._design_properties and self._design_properties.get("ModelSetup", None):
            key1 = "GeometryOperations"
            key2 = "GeometryEntityLists"
            key3 = "GeometryEntityListOperation"
            try:
                entity_list = self._design_properties["ModelSetup"]["GeometryCore"][key1][key2]
                if entity_list:
                    geom_entry = copy.deepcopy(entity_list[key3])
                    if isinstance(geom_entry, (dict, OrderedDict)):
                        geom_entry = [geom_entry]
                    for data in geom_entry:
                        props = {}
                        name = data["Attributes"]["Name"]
                        props["ID"] = data["ID"]
                        props["Type"] = data["GeometryEntityListParameters"]["EntityType"]
                        if props["Type"] == "Object":
                            name_list = []
                            for element in data["GeometryEntityListParameters"]["EntityList"]:
                                element_name = self.oeditor.GetObjectNameByID(int(element))
                                name_list.append(element_name)
                            props["List"] = name_list
                        else:
                            props["List"] = data["GeometryEntityListParameters"]["EntityList"]
                        design_lists.append(Lists(self, props, name))
            except:
                self.logger.info("Lists were not retrieved from AEDT file")
        return design_lists

    def _get_planes_data(self):
        """Get the plane's data.

        Returns
        -------
        [Dict with List information]
        """
        try:
            return {
                plane_name: self.oeditor.GetChildObject(plane_name)
                for plane_name in self.oeditor.GetChildNames("Planes")
            }
        except TypeError:
            return {}

    def __get__(self, instance, owner):
        self._app = instance
        return self

    @pyaedt_function_handler()
    def fit_all(self):
        """Fit all.

        References
        ----------

        >>> oEditor.FitAll

        Examples
        --------

        >>> from pyaedt import hfss
        >>> hfss = Hfss()
        >>> point_object = hfss.modeler.fit_all
        """
        self.oeditor.FitAll()

    @pyaedt_function_handler()
    def _find_perpendicular_points(self, face):
        if isinstance(face, str):
            vertices = [i.position for i in self[face].vertices]
        else:
            vertices = []
            for vertex in list(self.oeditor.GetVertexIDsFromFace(face)):
                vertices.append([float(i) for i in list(self.oeditor.GetVertexPosition(vertex))])
        assert len(vertices) > 2, "Automatic A-B Assignment can be done only on face with more than 2 vertices."
        origin = vertices[0]
        a_end = []
        b_end = []
        tol = 1e-10
        for v in vertices[1:]:
            edge1 = GeometryOperators.v_points(origin, v)
            for v2 in vertices[1:]:
                if v2 != v:
                    edge2 = GeometryOperators.v_points(origin, v2)
                    if abs(GeometryOperators.v_dot(edge1, edge2)) < tol:
                        a_end = v
                        b_end = v2
                        break
            if a_end:
                break
        if not a_end:
            a_end = vertices[1]
            b_end = vertices[2]
            return False, (origin, a_end, b_end)
        return True, (origin, a_end, b_end)

    @pyaedt_function_handler()
    def cover_lines(self, selection):
        """Cover closed lines and transform them to a sheet.

        Parameters
        ----------
        selection : str, int
            Polyline object to cover.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CoverLines
        """
        obj_to_cover = self.convert_to_selections(selection, False)
        self.oeditor.CoverLines(["NAME:Selections", "Selections:=", obj_to_cover, "NewPartsModelFlag:=", "Model"])
        return True

    @pyaedt_function_handler()
    def cover_faces(self, selection):
        """Cover a face.

        Parameters
        ----------
        selection : str, int
            Sheet object to cover.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CoverLines
        """
        obj_to_cover = self.convert_to_selections(selection, False)
        self.oeditor.CoverSurfaces(["NAME:Selections", "Selections:=", obj_to_cover, "NewPartsModelFlag:=", "Model"])
        return True

    @pyaedt_function_handler()
    def create_coordinate_system(
        self,
        origin=None,
        reference_cs="Global",
        name=None,
        mode="axis",
        view="iso",
        x_pointing=None,
        y_pointing=None,
        psi=0,
        theta=0,
        phi=0,
        u=None,
    ):
        """Create a coordinate system.

        Parameters
        ----------
        origin : list, optional
            List of ``[x, y, z]`` coordinates for the origin of the
            coordinate system.  The default is ``None``, in which case
            ``[0, 0, 0]`` is used.
        reference_cs : str, optional
            Name of the reference coordinate system. The default is
            ``"Global"``.
        name : str, optional
            Name of the coordinate system. The default is ``None``.
        mode : str, optional
            Definition mode. Options are ``"axis"``, ``"axisrotation"``,
            ``"view"``, ``"zxz"``, and ``"zyz"`` The default
            is ``"axis"``.  You can also use the ``pyaedt.generic.constants.CSMODE``
            enumerator.

            * If ``mode="axis"``, specify the ``x_pointing`` and ``y_pointing`` parameters.
            * If ``mode="axisrotation"``, specify the ``theta`` and ``u`` parameters.
            * If ``mode="view"``, specify the ``view`` parameter.
            * If ``mode="zxz"`` or ``mode="zyz"``, specify the ``phi``, ``theta``,
              and ``psi`` parameters.


            Parameters not needed by the specified mode are ignored.
            The default mode, ``"axis"``, is a coordinate system parallel to the
            global coordinate system centered in the global origin.

        view : str, int optional
            View for the coordinate system if ``mode="view"``. Options
            are ``"iso"``, ``None``, ``"XY"``, ``"XZ"``, and ``"XY"``. The
            default is ``"iso"``. the ``"rotate"`` option is obsolete. You can
            also use the ``pyaedt.generic.constants.VIEW`` enumerator.

            .. note::
              For backward compatibility, ``mode="view"`` and ``view="rotate"`` are the same as
              ``mode="axis"``. Because the "rotate" option in the "view" mode is obsolete, use
              ``mode="axis"`` instead.

        x_pointing : list, optional
            List of the ``[x, y, z]`` coordinates specifying the X axis
            pointing in the global coordinate system if ``mode="axis"``.
            The default is ``[1, 0, 0]``.
        y_pointing : list, optional
            List of the ``[x, y, z]`` coordinates specifying the Y axis
            pointing in the global coordinate system if ``mode="axis"``.
            The default is ``[0, 1, 0]``.
        phi : float, optional
            Euler angle phi in degrees if ``mode="zxz"`` or ``mode="zyz"``.
            The default is ``0``.
        theta : float, optional
            Euler angle theta or rotation angle in degrees if ``mode="zxz"``,
            ``mode="zyz"``, or ``mode="axisrotation"``. The default is ``0``.
        psi : float, optional
            Euler angle psi in degrees if ``mode="zxz"`` or ``mode="zyz"``.
            The default is ``0``.
        u : list
            List of the ``[ux, uy, uz]`` coordinates for the rotation axis
            if ``mode="zxz"``. The default is ``[1, 0, 0]``.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.CoordinateSystem`
            Created coordinate system.

        References
        ----------

        >>> oEditor.CreateRelativeCS
        """
        if name:
            cs_names = [i.name for i in self.coordinate_systems]
            if name in cs_names:
                raise AttributeError("A coordinate system with the specified name already exists.")

        cs = CoordinateSystem(self)
        if cs:
            result = cs.create(
                origin=origin,
                reference_cs=reference_cs,
                name=name,
                mode=mode,
                view=view,
                x_pointing=x_pointing,
                y_pointing=y_pointing,
                phi=phi,
                theta=theta,
                psi=psi,
                u=u,
            )
            if result:
                return cs
        return False

    @pyaedt_function_handler()
    def create_face_coordinate_system(
        self, face, origin, axis_position, axis="X", name=None, offset=None, rotation=0, always_move_to_end=True
    ):
        """Create a face coordinate system.

        The face coordinate has always the Z axis parallel to face normal.
        The X and Y axis lie on the face plane.

        Parameters
        ----------
        face : int, FacePrimitive
            Face where the coordinate system is defined.
        origin : int, FacePrimitive, EdgePrimitive, VertexPrimitive
            Coordinate system origin. The origin must belong to the face where the
            coordinate system is defined.

            - If a face is specified, the origin is placed on the face center. It must be
              the same as the ``face`` parameter.
            - If an edge is specified, the origin is placed on the edge midpoint.
            - If a vertex is specified, the origin is placed on the vertex.

        axis_position : int, FacePrimitive, EdgePrimitive, VertexPrimitive
            Specify where the X or Y axis is pointing. The position must belong to the face where the
            coordinate system is defined.
            Select which axis is considered with the option ``axis``.
            If a face is specified, the position is placed on the face center. It must be the same as ``face``.
            If an edge is specified, the position is placed on the edce midpoint.
            If a vertex is specified, the position is placed on the vertex.
        axis : str, optional
            Select which axis is considered for positioning. Possible values are ``"X"`` and ``"Y"``.
            The default is ``"X"``.
        name : str, optional
            Name of the coordinate system. The default is ``None``.
        offset : list, optional
            List of the ``[x, y]`` coordinates specifying the offset of the coordinate system origin.
            The offset specified in the face coordinate system reference.
            The default is ``[0, 0]``.
        rotation : float, optional
            Rotation angle of the coordinate system around its Z axis. Angle is in degrees.
            The default is ``0``.
        always_move_to_end : bool, optional
            If ``True`` the Face Coordinate System creation operation will always be moved to the end of subsequent
            objects operation. This will guarantee that the coordinate system will remain solidal with the object
            face. If ``False`` the option "Always Move CS to End" is set to off. The default is ``True``.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.FaceCoordinateSystem`

        """

        if name:
            cs_names = [i.name for i in self.coordinate_systems]
            if name in cs_names:  # pragma: no cover
                raise AttributeError("A coordinate system with the specified name already exists!")

        cs = FaceCoordinateSystem(self)
        if cs:
            result = cs.create(
                face=face,
                origin=origin,
                axis_position=axis_position,
                axis=axis,
                name=name,
                offset=offset,
                rotation=rotation,
                always_move_to_end=always_move_to_end,
            )

            if result:
                return cs
        return False

    @pyaedt_function_handler()
    def create_object_coordinate_system(
        self, obj, origin, x_axis, y_axis, move_to_end=True, reverse_x_axis=False, reverse_y_axis=False, name=None
    ):
        """Create an object coordinate system.

        Parameters
        ----------
        obj : str, :class:`pyaedt.modeler.cad.object3d.Object3d`
            Object to attach the object coordinate system to.
        origin : int, VertexPrimitive, EdgePrimitive, FacePrimitive, list
            Refer to the origin where the object coordinate system is anchored.
            It can be:

             - int in which case it refers to the entity Id.
             - VertexPrimitive, EdgePrimitive, FacePrimitive in which case it refers to the entity type.
             - list in which case it refers to the origin coordinate system ``[x, y, z]``.

        x_axis : int, VertexPrimitive, EdgePrimitive, FacePrimitive, list
            Entity that the x axis of the object coordinate system points to.
            It can be:

             - int in which case it refers to the entity Id.
             - VertexPrimitive, EdgePrimitive, FacePrimitive in which case it refers to the entity type.
             - list in which case it refers to the point coordinate system ``[x, y, z]`` that the x axis points to.

        y_axis : int, VertexPrimitive, EdgePrimitive, FacePrimitive, list
            Entity that the y axis of the object coordinate system points to.
            It can be:

             - int in which case it refers to the entity Id.
             - VertexPrimitive, EdgePrimitive, FacePrimitive in which case it refers to the entity type.
             - list in which case it refers to the point coordinate system ``[x, y, z]`` that the y axis points to.

        move_to_end : bool, optional
            If ``True`` the Coordinate System creation operation will always be moved to the end of subsequent
            objects operation. This will guarantee that the coordinate system will remain solidal with the object
            face. If ``False`` the option "Always Move CS to End" is set to off. The default is ``True``.
        reverse_x_axis : bool, optional
            Whether the x-axis is in the reverse direction.
            The default is ``False``.
        reverse_y_axis : bool, optional
            Whether the y-axis is in the reverse direction.
            The default is ``False``.
        name : str, optional
            Name of the coordinate system. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if name:
            cs_names = [i.name for i in self.coordinate_systems]
            if name in cs_names:  # pragma: no cover
                raise AttributeError("A coordinate system with the specified name already exists.")

        cs = ObjectCoordinateSystem(self, name=name)
        if cs:
            result = cs.create(
                obj=obj,
                origin=origin,
                x_axis=x_axis,
                y_axis=y_axis,
                move_to_end=move_to_end,
                reverse_x_axis=reverse_x_axis,
                reverse_y_axis=reverse_y_axis,
            )

            if result:
                return cs
        return False

    @pyaedt_function_handler()
    def global_to_cs(self, point, ref_cs):
        """Transform a point from the global coordinate system to another coordinate system.

        Parameters
        ----------
        point : list
            List of the ``[x, y, z]`` coordinates to transform.
        ref_cs : str, CoordinateSystem
            Name of the destination reference system. The ``CoordinateSystem`` object can also be
            used.

        Returns
        -------
        list
            List of the transformed ``[x, y, z]`` coordinates.

        """
        if type(point) is not list or len(point) != 3:
            raise AttributeError("Point must be in format [x, y, z].")
        try:
            point = [float(i) for i in point]
        except:
            raise AttributeError("Point must be in format [x, y, z].")
        if isinstance(ref_cs, BaseCoordinateSystem):
            ref_cs_name = ref_cs.name
        elif isinstance(ref_cs, str):
            ref_cs_name = ref_cs
        else:
            raise AttributeError("ref_cs must be either a string or a CoordinateSystem object.")
        if ref_cs_name == "Global":
            return point
        cs_names = [i.name for i in self.coordinate_systems]
        if ref_cs_name not in cs_names:
            raise AttributeError("Specified coordinate system does not exist in the design.")

        def get_total_transformation(p, cs):
            idx = cs_names.index(cs)
            q = self.coordinate_systems[idx].quaternion
            ox = GeometryOperators.parse_dim_arg(
                self.coordinate_systems[idx].props["OriginX"],
                self.model_units,
                variable_manager=self._app.variable_manager,
            )
            oy = GeometryOperators.parse_dim_arg(
                self.coordinate_systems[idx].props["OriginY"],
                self.model_units,
                variable_manager=self._app.variable_manager,
            )
            oz = GeometryOperators.parse_dim_arg(
                self.coordinate_systems[idx].props["OriginZ"],
                self.model_units,
                variable_manager=self._app.variable_manager,
            )
            o = [ox, oy, oz]
            refcs = self.coordinate_systems[idx].ref_cs
            if refcs == "Global":
                p1 = p
            else:
                p1 = get_total_transformation(p, refcs)
            p2 = GeometryOperators.q_rotation_inv(GeometryOperators.v_sub(p1, o), q)
            return p2

        p = get_total_transformation(point, ref_cs_name)
        return [round(p[i], 13) for i in range(3)]

    @pyaedt_function_handler()
    def set_working_coordinate_system(self, name):
        """Set the working coordinate system to another coordinate system.

        Parameters
        ----------
        name : str, FaceCoordinateSystem, CoordinateSystem
            Name of the coordinate system or ``CoordinateSystem`` object to set as the working
            coordinate system.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SetWCS
        """
        if isinstance(name, BaseCoordinateSystem):
            self.oeditor.SetWCS(
                ["NAME:SetWCS Parameter", "Working Coordinate System:=", name.name, "RegionDepCSOk:=", False]
            )
        else:
            self.oeditor.SetWCS(
                ["NAME:SetWCS Parameter", "Working Coordinate System:=", name, "RegionDepCSOk:=", False]
            )
        return True

    @pyaedt_function_handler()
    def invert_cs(self, coordinate_system, to_global=False):
        """Get the inverse translation and the conjugate quaternion of the input coordinate system.

        By defining a new coordinate system with this information, the reference coordinate system
        of the input coordinate system is obtained.

        Parameters
        ----------
        coordinate_system : str, CoordinateSystem
            Name of the destination reference system. A ``CoordinateSystem`` object can also be
            used.
        to_global : bool, optional
            Whether to compute the inverse transformation of the input coordinate system with
            respect to the global coordinate system. The default is ``False``.

        Returns
        -------
        list
            Origin coordinates.
        list
            Quaternion.
        """
        if isinstance(coordinate_system, BaseCoordinateSystem):
            cs = coordinate_system
        elif isinstance(coordinate_system, str):
            cs_names = [i.name for i in self.coordinate_systems]
            if coordinate_system not in cs_names:  # pragma: no cover
                raise AttributeError("Specified coordinate system does not exist in the design.")
            cs = self.coordinate_systems[cs_names.index(coordinate_system)]
        else:  # pragma: no cover
            raise AttributeError("coordinate_system must either be a string or a CoordinateSystem object.")

        if to_global:
            o, q = self.reference_cs_to_global(coordinate_system)
            o = GeometryOperators.v_prod(-1, GeometryOperators.q_rotation(o, q))
            q = [q[0], -q[1], -q[2], -q[3]]
        else:
            q = cs.quaternion
            q = [q[0], -q[1], -q[2], -q[3]]
            o = GeometryOperators.v_prod(-1, GeometryOperators.q_rotation(cs.origin, q))
        return o, q

    @pyaedt_function_handler()
    def reference_cs_to_global(self, coordinate_system):
        """Get the origin and quaternion defining the coordinate system in the global coordinates.

        Parameters
        ----------
        coordinate_system : str, CoordinateSystem
            Name of the destination reference system. The ``CoordinateSystem`` object can also be used.

        Returns
        -------
        list
            Origin coordinates.
        list
            Quaternion.
        """
        cs_names = [i.name for i in self.coordinate_systems]
        if isinstance(coordinate_system, BaseCoordinateSystem):
            cs = coordinate_system
        elif isinstance(coordinate_system, str):
            if coordinate_system not in cs_names:  # pragma: no cover
                raise AttributeError("Specified coordinate system does not exist in the design.")
            cs = self.coordinate_systems[cs_names.index(coordinate_system)]
        else:  # pragma: no cover
            raise AttributeError("coordinate_system must either be a string or a CoordinateSystem object.")
        quaternion = cs.quaternion
        origin = cs.origin
        ref_cs_name = cs.ref_cs
        while ref_cs_name != "Global":
            ref_cs = self.coordinate_systems[cs_names.index(ref_cs_name)]
            quaternion_ref = ref_cs.quaternion
            quaternion = GeometryOperators.q_prod(quaternion_ref, quaternion)
            origin_ref = ref_cs.origin
            origin = GeometryOperators.v_sum(origin_ref, GeometryOperators.q_rotation(origin, quaternion_ref))
            ref_cs_name = ref_cs.ref_cs
        return origin, quaternion

    @pyaedt_function_handler()
    def duplicate_coordinate_system_to_global(self, coordinate_system):
        """Create a duplicate coordinate system referenced to the global coordinate system.

        Having this coordinate system referenced to the global coordinate
        system removes all nested coordinate system dependencies.

        Parameters
        ----------
        coordinate_system : str, CoordinateSystem
            Name of the destination reference system. The ``CoordinateSystem`` object can also be used.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.CoordinateSystem`
            Created coordinate system.

        References
        ----------

        >>> oEditor.CreateRelativeCS
        """
        cs_names = [i.name for i in self.coordinate_systems]
        if isinstance(coordinate_system, BaseCoordinateSystem):
            cs = coordinate_system
        elif isinstance(coordinate_system, str):
            if coordinate_system not in cs_names:  # pragma: no cover
                raise AttributeError("Specified coordinate system does not exist in the design.")
            cs = self.coordinate_systems[cs_names.index(coordinate_system)]
        else:  # pragma: no cover
            raise AttributeError("coordinate_system must either be a string or a CoordinateSystem object.")
        if isinstance(cs, CoordinateSystem):
            o, q = self.reference_cs_to_global(coordinate_system)
            x, y, _ = GeometryOperators.quaternion_to_axis(q)
            reference_cs = "Global"
            name = cs.name + "_RefToGlobal"
            if name in cs_names:
                name = cs.name + generate_unique_name("_RefToGlobal")
            cs = CoordinateSystem(self)
            if cs:
                result = cs.create(
                    origin=o,
                    reference_cs=reference_cs,
                    name=name,
                    mode="axis",
                    x_pointing=x,
                    y_pointing=y,
                )
                if result:
                    return cs
        elif isinstance(cs, FaceCoordinateSystem):
            name = cs.name + "_RefToGlobal"
            if name in cs_names:
                name = cs.name + generate_unique_name("_RefToGlobal")
            face_cs = FaceCoordinateSystem(self, props=cs.props, name=name, face_id=cs.props["FaceID"])
            obj = [obj for obj in self.object_list for face in obj.faces if face.id == face_cs.props["FaceID"]][0]
            face = [face for face in obj.faces if face.id == face_cs.props["FaceID"]][0]
            if face_cs.props["Origin"]["PositionType"] == "FaceCenter":
                origin = face
            elif face_cs.props["Origin"]["PositionType"] == "EdgeCenter":
                origin = [edge for edge in face.edges if edge.id == face_cs.props["Origin"]["EntityID"]][0]
            elif face_cs.props["Origin"]["PositionType"] == "OnVertex":
                edge = [
                    edge
                    for edge in face.edges
                    for vertex in edge.vertices
                    if vertex.id == face_cs.props["Origin"]["EntityID"]
                ][0]
                origin = [v for v in edge.vertices if v.id == face_cs.props["Origin"]["EntityID"]][0]
            if face_cs.props["AxisPosn"]["PositionType"] == "EdgeCenter":
                axis_position = [edge for edge in face.edges if edge.id == face_cs.props["AxisPosn"]["EntityID"]][0]
            elif face_cs.props["AxisPosn"]["PositionType"] == "OnVertex":
                edge = [
                    edge
                    for edge in face.edges
                    for vertex in edge.vertices
                    if vertex.id == face_cs.props["AxisPosn"]["EntityID"]
                ][0]
                axis_position = [v for v in edge.vertices if v.id == face_cs.props["AxisPosn"]["EntityID"]][0]
            if face_cs:
                result = face_cs.create(
                    face=face,
                    origin=origin,
                    axis_position=axis_position,
                    axis=face_cs.props["WhichAxis"],
                    name=name,
                    offset=[face_cs["XOffset"], face_cs["YOffset"]],
                    rotation=decompose_variable_value(face_cs["ZRotationAngle"])[0],
                    always_move_to_end=face_cs["MoveToEnd"],
                )
                if result:
                    return face_cs
        elif isinstance(cs, ObjectCoordinateSystem):
            name = cs.name + "_RefToGlobal"
            if name in cs_names:
                name = cs.name + generate_unique_name("_RefToGlobal")
            obj_cs = ObjectCoordinateSystem(self, props=cs.props, name=name, entity_id=cs.entity_id)
            objs_by_name_list = [obj for obj in self.object_list if obj.part_coordinate_system == cs.name]
            objs_by_id_list = [o for o in self.object_list if o.id == cs.entity_id]
            if objs_by_name_list:
                obj = objs_by_name_list[0]
            elif objs_by_id_list:
                obj = [o for o in self.object_list if o.id == cs.entity_id][0]
            if cs.props["Origin"]["PositionType"] != "AbsolutePosition":
                if cs.props["Origin"]["PositionType"] == "FaceCenter":
                    origin = [f for f in obj.faces if f.id == cs.props["Origin"]["EntityID"]][0]
                elif (
                    cs.props["Origin"]["PositionType"] == "EdgeCenter"
                    or cs.props["Origin"]["PositionType"] == "ArcCenter"
                ):
                    origin = [e for e in obj.edges if e.id == cs.props["Origin"]["EntityID"]][0]
                elif cs.props["Origin"]["PositionType"] == "OnVertex":
                    origin = [v for v in obj.vertices if v.id == cs.props["Origin"]["EntityID"]][0]
            else:
                origin = [
                    cs.props["Origin"]["XPosition"],
                    cs.props["Origin"]["YPosition"],
                    cs.props["Origin"]["ZPosition"],
                ]
            if "xAxisPos" in cs.props:
                if cs.props["xAxisPos"]["PositionType"] == "FaceCenter":
                    x_axis = [f for f in obj.faces if f.id == cs.props["xAxisPos"]["EntityID"]][0]
                elif (
                    cs.props["xAxisPos"]["PositionType"] == "EdgeCenter"
                    or cs.props["xAxisPos"]["PositionType"] == "ArcCenter"
                ):
                    x_axis = [e for e in obj.edges if e.id == cs.props["xAxisPos"]["EntityID"]][0]
                elif cs.props["xAxisPos"]["PositionType"] == "OnVertex":
                    x_axis = [v for v in obj.vertices if v.id == cs.props["xAxisPos"]["EntityID"]][0]
            elif "xAxis" in cs.props:
                x_axis = [
                    cs.props["xAxis"]["xDirection"],
                    cs.props["xAxis"]["yDirection"],
                    cs.props["xAxis"]["zDirection"],
                ]
            if "yAxisPos" in cs.props:
                if cs.props["yAxisPos"]["PositionType"] == "FaceCenter":
                    y_axis = [f for f in obj.faces if f.id == cs.props["yAxisPos"]["EntityID"]][0]
                elif (
                    cs.props["yAxisPos"]["PositionType"] == "EdgeCenter"
                    or cs.props["yAxisPos"]["PositionType"] == "ArcCenter"
                ):
                    y_axis = [e for e in obj.edges if e.id == cs.props["yAxisPos"]["EntityID"]][0]
                elif cs.props["yAxisPos"]["PositionType"] == "OnVertex":
                    y_axis = [v for v in obj.vertices if v.id == cs.props["yAxisPos"]["EntityID"]][0]
            elif "yAxis" in cs.props:
                y_axis = [
                    cs.props["yAxis"]["xDirection"],
                    cs.props["yAxis"]["yDirection"],
                    cs.props["yAxis"]["zDirection"],
                ]
            if obj_cs:
                result = obj_cs.create(
                    obj=obj,
                    origin=origin,
                    x_axis=x_axis,
                    y_axis=y_axis,
                    move_to_end=cs.props["MoveToEnd"],
                    reverse_x_axis=cs.props["ReverseXAxis"],
                    reverse_y_axis=cs.props["ReverseYAxis"],
                )
                if result:
                    return obj_cs
        return False

    @pyaedt_function_handler()
    def set_objects_deformation(self, objects):
        """Assign deformation objects to a Workbench link.

        Parameters
        ----------
        objects : list
            List of the deformation objects to assign to the Workbench link.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetObjectDeformation
        """
        self.logger.info("Enabling deformation feedback")
        try:
            self._odesign.SetObjectDeformation(["EnabledObjects:=", objects])
        except:
            self.logger.error("Failed to enable the deformation dependence")
            return False
        else:
            self.logger.info("Successfully enabled deformation feedback")
            return True

    @pyaedt_function_handler()
    def set_objects_temperature(self, objects, ambient_temp=22, create_project_var=False):
        """Assign temperatures to objects.

        The materials assigned to the objects must have a thermal modifier.

        Parameters
        ----------
        objects : list
            List of objects.
        ambient_temp : float, optional
            Ambient temperature. The default is ``22``.
        create_project_var : bool, optional
            Whether to create a project variable for the ambient temperature.
            The default is ``False``. If ``True,`` ``$AmbientTemp`` is created.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetObjectTemperature
        """
        self.logger.info("Set model temperature and enabling Thermal Feedback")
        if create_project_var:
            self._app.variable_manager["$AmbientTemp"] = str(ambient_temp) + "cel"
            var = "$AmbientTemp"
        else:
            var = str(ambient_temp) + "cel"
        vargs1 = [
            "NAME:TemperatureSettings",
            "IncludeTemperatureDependence:=",
            True,
            "EnableFeedback:=",
            True,
            "Temperatures:=",
        ]
        vargs2 = []
        for obj in objects:
            mat = self[obj].material_name
            th = self._app.materials.check_thermal_modifier(mat)
            if th:
                vargs2.append(obj)
                vargs2.append(var)
        if not vargs2:
            return False
        else:
            vargs1.append(vargs2)
        try:
            self._odesign.SetObjectTemperature(vargs1)
        except:
            self.logger.error("Failed to enable the temperature dependence")
            return False
        else:
            self.logger.info("Assigned Objects Temperature")
            return True

    @pyaedt_function_handler()
    def _create_sheet_from_object_closest_edge(self, startobj, endobject, axisdir, portonplane):
        """Create a sheet from the edge closest to the object.

        Parameters
        ----------
        startobj : str
            Name of the starting object.
        endobject : str
            Name of the ending object.
        axisdir : int
           Axis direction. Options are ``0`` through ``5``.
        portonplane : bool
            Whether edges are to be on the plane orthogonal to the axis
            direction.

        Returns
        -------
        str
            Name of the sheet.
        list
            List of float values of the first edge midpoint.
            Point in ``[x, y, z]`` coordinates.
        list
            List of float values of the second edge midpoint.
            Point in ``[x, y, z]`` coordinates.

        """
        out, parallel = self.find_closest_edges(startobj, endobject, axisdir)
        port_edges = self.get_equivalent_parallel_edges(out, portonplane, axisdir, startobj, endobject)
        if port_edges is None or port_edges is False:
            port_edges = []
            for e in out:
                edge = self.create_object_from_edge(e)
                port_edges.append(edge)
        edge_0 = port_edges[0].edges[0]
        edge_1 = port_edges[1].edges[0]
        sheet_name = port_edges[0].name
        point0 = edge_0.midpoint
        point1 = edge_1.midpoint
        self.connect(port_edges)
        return sheet_name, point0, point1

    @pyaedt_function_handler()
    def find_point_around(self, objectname, startposition, offset, plane):
        """Find the point around an object.

        Parameters
        ----------
        objectname : str
            Name of the object.
        startposition : list
            List of the ``[x, y, z]`` coordinates for the starting
            position of the object.
        offset :
            Offset to apply.
        plane : str
            Coordinate plane of the arc. Choices are ``"YZ"``,
            ``"ZX"``, and ``"XY"``.


        Returns
        -------
        list
            List of the ``[x, y, z]`` coordinates for the point.

        """
        position = [0, 0, 0]
        angle = 0
        if plane == 0:
            while angle <= 360:
                position[0] = startposition[0] + offset * math.cos(math.pi * angle / 180)
                position[1] = startposition[1] + offset * math.sin(math.pi * angle / 180)
                if objectname in self.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        elif plane == 1:
            while angle <= 360:
                position[1] = startposition[1] + offset * math.cos(math.pi * angle / 180)
                position[2] = startposition[2] + offset * math.sin(math.pi * angle / 180)
                if objectname in self.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        elif plane == 2:
            while angle <= 360:
                position[0] = startposition[0] + offset * math.cos(math.pi * angle / 180)
                position[2] = startposition[2] + offset * math.sin(math.pi * angle / 180)
                if objectname in self.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        return position

    @pyaedt_function_handler()
    def create_sheet_to_ground(self, objectname, groundname=None, axisdir=0, sheet_dim=1):
        """Create a sheet between an object and a ground plane.

        The ground plane must be bigger than the object and perpendicular
        to one of the three axes.

        Parameters
        ----------
        objectname : str
            Name of the object.
        groundname : str, optional
            Name of the ground. The default is ``None``, in which case the
            bounding box is used.
        axisdir : int, optional
            Axis direction. Options are ``0`` through ``5``. The default is ``0``.
        sheet_dim : optional
            Sheet dimension in millimeters. The default is ``1``.

        Returns
        -------
        int
            ID of the sheet created.

        References
        ----------

        >>> oEditor.CreatePolyline
        """
        if axisdir > 2:
            obj_cent = [-1e6, -1e6, -1e6]
        else:
            obj_cent = [1e6, 1e6, 1e6]
        face_ob = None
        for face in self[objectname].faces:
            center = face.center
            if not center:
                continue
            if axisdir > 2 and center[axisdir - 3] > obj_cent[axisdir - 3]:
                obj_cent = center
                face_ob = face
            elif axisdir <= 2 and center[axisdir] < obj_cent[axisdir]:
                obj_cent = center
                face_ob = face
        vertex = face_ob.vertices
        start = vertex[0].position

        if not groundname:
            gnd_cent = []
            bounding = self.get_model_bounding_box()
            if axisdir < 3:
                for i in bounding[0:3]:
                    gnd_cent.append(float(i))
            else:
                for i in bounding[3:]:
                    gnd_cent.append(float(i))
        else:
            ground_plate = self[groundname]
            if axisdir > 2:
                gnd_cent = [1e6, 1e6, 1e6]
            else:
                gnd_cent = [-1e6, -1e6, -1e6]
            face_gnd = ground_plate.faces
            for face in face_gnd:
                center = face.center
                if not center:
                    continue
                if axisdir > 2 and center[axisdir - 3] < gnd_cent[axisdir - 3]:
                    gnd_cent = center
                elif axisdir <= 2 and center[axisdir] > gnd_cent[axisdir]:
                    gnd_cent = center

        axisdist = obj_cent[divmod(axisdir, 3)[1]] - gnd_cent[divmod(axisdir, 3)[1]]
        if axisdir < 3:
            axisdist = -axisdist

        if divmod(axisdir, 3)[1] == 0:
            cs = self._app.PLANE.YZ
            vector = [axisdist, 0, 0]
        elif divmod(axisdir, 3)[1] == 1:
            cs = self._app.PLANE.ZX
            vector = [0, axisdist, 0]
        elif divmod(axisdir, 3)[1] == 2:
            cs = self._app.PLANE.XY
            vector = [0, 0, axisdist]

        offset = self.find_point_around(objectname, start, sheet_dim, cs)
        p1 = self.create_polyline([start, offset])
        p2 = p1.clone().move(vector)
        self.connect([p1, p2])

        return p1

    @pyaedt_function_handler()
    def _get_faceid_on_axis(self, objname, axisdir):
        """Get the ID of the face on the axis.

        Parameters
        ----------
        objname : str
            Name of the object.
        axisdir : int
            Axis direction. Options are ``1`` through ``5``.

        Returns
        -------
        int
            ID of the face.

        """
        faces = self.get_object_faces(objname)
        face = None
        center = None
        for f in faces:
            try:
                c = self.get_face_center(f)
                if not face and c:
                    face = f
                    center = c
                elif axisdir < 3 and c[axisdir] < center[axisdir]:
                    face = f
                    center = c
                elif axisdir > 2 and c[axisdir - 3] > center[axisdir - 3]:
                    face = f
                    center = c
            except:
                pass
        return face

    @pyaedt_function_handler()
    def _create_microstrip_sheet_from_object_closest_edge(self, startobj, endobject, axisdir, vfactor=3, hfactor=5):
        def duplicate_and_unite(sheet_name, array1, array2, dup_factor):
            status, list = self.duplicate_along_line(sheet_name, array1, dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, array2, dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)

        tol = 1e-6
        out, parallel = self.find_closest_edges(startobj, endobject, axisdir)
        port_edges = self.get_equivalent_parallel_edges(out, True, axisdir, startobj, endobject)
        if port_edges is None:
            return False
        sheet_name = port_edges[0].name
        point0 = port_edges[0].edges[0].midpoint
        point1 = port_edges[1].edges[0].midpoint
        len = port_edges[0].edges[0].length
        vect = GeometryOperators.v_points(point1, point0)
        l1 = out[0].length
        l2 = out[1].length
        if l1 < l2:
            vect_t = [i * (vfactor - 1) for i in vect]
            self.move(port_edges[0], vect_t)
        else:
            vect_t = [i * (1 - vfactor) for i in vect]
            self.move(port_edges[1], vect_t)

        self.connect(port_edges)
        list_unite = [sheet_name]
        dup_factor = divmod((hfactor + 1), 2)[0]
        coeff = float(hfactor - 1) / 2 / dup_factor

        if divmod(axisdir, 3)[1] == 0 and abs(vect[1]) < tol:
            duplicate_and_unite(sheet_name, [0, len * coeff, 0], [0, -len * coeff, 0], dup_factor)
        elif divmod(axisdir, 3)[1] == 0 and abs(vect[2]) < tol:
            duplicate_and_unite(sheet_name, [0, 0, len * coeff], [0, 0, -len * coeff], dup_factor)
        elif divmod(axisdir, 3)[1] == 1 and abs(vect[0]) < tol:
            duplicate_and_unite(sheet_name, [len * coeff, 0, 0], [-len * coeff, 0, 0], dup_factor)
        elif divmod(axisdir, 3)[1] == 1 and abs(vect[2]) < tol:
            duplicate_and_unite(sheet_name, [0, 0, len * coeff], [0, 0, -len * coeff], dup_factor)
        elif divmod(axisdir, 3)[1] == 2 and abs(vect[0]) < tol:
            duplicate_and_unite(sheet_name, [len * coeff, 0, 0], [-len * coeff, 0, 0], dup_factor)
        elif divmod(axisdir, 3)[1] == 2 and abs(vect[1]) < tol:
            duplicate_and_unite(sheet_name, [0, len * coeff, 0], [0, -len * coeff, 0], dup_factor)

        return sheet_name, point0, point1

    @pyaedt_function_handler()
    def get_boundaries_name(self):
        """Retrieve all boundary names.

        Returns
        -------
        list
            List of boundary names. Boundaries with multiple modes will return one
            boundary for each mode.

        References
        ----------

        >>> oModule.GetBoundaries
        """
        if self._app.design_type == "Icepak":
            return list(self._app.odesign.GetChildObject("Thermal").GetChildNames())
        else:
            return list(self._app.odesign.GetChildObject("Boundaries").GetChildNames())

    @pyaedt_function_handler()
    def set_object_model_state(self, obj_list, model=True):
        """Set a list of objects to either models or non-models.

        Parameters
        ----------
        obj_list : list
            List of objects IDs or names.
        model : bool, optional
            Whether to set the objects as models. The default is ``True``.
            If ``False``, the objects are set as non-models.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        selections = self.convert_to_selections(obj_list, True)
        arguments = [
            "NAME:AllTabs",
            [
                "NAME:Geometry3DAttributeTab",
                ["NAME:PropServers"] + selections,
                ["NAME:ChangedProps", ["NAME:Model", "Value:=", model]],
            ],
        ]
        self._modeler.oeditor.ChangeProperty(arguments)
        return True

    @pyaedt_function_handler()
    def get_objects_in_group(self, group):
        """Retrieve a list of objects belonging to a group.

        Parameters
        ----------
        group : str
            Name of the group.

        Returns
        -------
        list
            List of objects belonging to the group.

        References
        ----------

        >>> oEditor.GetObjectsInGroup
        """
        if type(group) is not str:
            raise ValueError("Group name must be a string")
        group_objs = list(self.oeditor.GetObjectsInGroup(group))
        if not group_objs:
            return None
        return group_objs

    @pyaedt_function_handler()
    def get_group_bounding_box(self, group):
        """Retrieve the bounding box of a group.

        Parameters
        ----------
        group : str
            Name of the group.

        Returns
        -------
        list
            List of six float values representing the bounding box
            in the form ``[min_x, min_y, min_z, max_x, max_y, max_z]``.

        References
        ----------

        >>> oEditor.GetObjectsInGroup
        >>> oEditor.GetModelBoundingBox
        """
        if type(group) is not str:
            raise ValueError("Group name must be a string")
        group_objs = list(self.oeditor.GetObjectsInGroup(group))
        if not group_objs:
            return None
        all_objs = self.object_names
        objs_to_unmodel = [i for i in all_objs if i not in group_objs]
        if objs_to_unmodel:
            vArg1 = ["NAME:Model", "Value:=", False]
            self._change_geometry_property(vArg1, objs_to_unmodel)
            bounding = self.get_model_bounding_box()
            self._odesign.Undo()
        else:
            bounding = self.get_model_bounding_box()
        return bounding

    @pyaedt_function_handler()
    def convert_to_selections(self, object_id, return_list=False):
        """Convert modeler objects.

        This method converts modeler object or IDs to the corresponding
        output according to the following scheme:

        ====================  ===========================
          ``object_id``          Return value
        ====================  ===========================

         ``int``                 object name (str)
          ``Object3D``           object name (str)
          ``FacePrimitive``      int, face ID
          ``EdgePrimitive``      int, edge ID
          ``str``                return the same ``str``


        - If ``object_id`` is a list, a list is returned according
        to the table. If ``object_id`` is a single value, a list
        of ``length == 1`` is returned (default).

        - If the second argument, ``return_list``, is set to `False` (default), a
        string is returned with elements separated by a comma (,)".


        Parameters
        ----------
        object_id : str, int, list
            One or more object IDs whose name will be returned. A list can contain
            both strings (object names) and integers (object IDs).
        return_list : bool, option
            Whether to return a list of the selections. The default is
            ``False``, in which case a string of the selections is returned.
            If ``True``, a list of the selections is returned.

        Returns
        -------
        str or list
           Name of the objects corresponding to the one or more object IDs passed as arguments.

        """
        if not isinstance(object_id, list):
            object_id = [object_id]
        objnames = []
        for el in object_id:
            if isinstance(el, int) and el in self.objects:
                objnames.append(self.objects[el].name)
            elif isinstance(el, int):
                objnames.append(el)
            elif isinstance(el, Object3d):
                objnames.append(el.name)
            elif isinstance(el, FacePrimitive) or isinstance(el, EdgePrimitive) or isinstance(el, VertexPrimitive):
                objnames.append(el.id)
            elif isinstance(el, str):
                objnames.append(el)
        if return_list:
            return objnames
        else:
            return ",".join([str(i) for i in objnames])

    @pyaedt_function_handler()
    def split(self, objects, plane=None, sides="Both", tool=None, split_crossing_objs=False, delete_invalid_objs=True):
        """Split a list of objects.
        In case of 3D design possible splitting options are plane, Face Primitive, Edge Primitive or Polyline.
        In case of 2D design possible splitting option is plane.

        Parameters
        ----------
        objects : str, int, or list
            One or more objects to split. A list can contain
            both strings (object names) and integers (object IDs).
        plane : str, optional
            Coordinate plane of the cut or the Application.PLANE object.
            The default value is ``None``.
            Choices for the coordinate plane are ``"XY"``, ``"YZ"``, and ``"ZX"``.
            If plane or tool parameter are not provided the method returns ``False``.
        sides : str, optional
            Which side to keep. The default is ``"Both"``, in which case
            all objects are kept after the split. Options are ``"Both"``,
            ``"NegativeOnly"``, and ``"PositiveOnly"``.
        tool : str, int, :class:`pyaedt.modeler.cad.elements3d.FacePrimitive`or
                :class:`pyaedt.modeler.cad.elements3d.EdgePrimitive`, optional
            For 3D design types is the name, ID, face, edge or polyline used to split the objects.
            For 2D design types is the name of the plane used to split the objects.
            The default value is ``None``.
            If plane or tool parameter are not provided the method returns ``False``.
        split_crossing_objs : bool, optional
            Whether to split crossing plane objects.
            The default is ``False``.
        delete_invalid_objs : bool, optional
            Whether to delete invalid objects.
            The default is ``True``.

        Returns
        -------
        list of str
            List of split object names.

        References
        ----------

        >>> oEditor.Split
        """
        if plane is None and not tool or plane and tool:
            self.logger.info("One method to split the objects has to be defined.")
            return False
        objects = self.convert_to_selections(objects)
        all_objs = [i for i in self.object_names]
        selections = []
        planes = "Dummy"
        tool_type = "PlaneTool"
        tool_entity_id = -1
        if self._is3d:
            obj_name = None
            obj = []
            if plane is not None and not tool:
                tool_type = "PlaneTool"
                tool_entity_id = -1
                planes = GeometryOperators.cs_plane_to_plane_str(plane)
                selections = ["NAME:Selections", "Selections:=", objects, "NewPartsModelFlag:=", "Model"]
            elif tool and plane is None:
                if isinstance(tool, str):
                    obj = [f for f in self.object_list if f.name == tool][0]
                    obj_name = obj.name
                    if isinstance(obj, Object3d) and obj.object_type != "Line":
                        obj = obj.faces[0]
                        tool_type = "FaceTool"
                    elif obj.object_type == "Line":
                        obj = obj.edges[0]
                        tool_type = "EdgeTool"
                elif isinstance(tool, int):
                    # check whether tool it's an object Id
                    if tool in self.objects.keys():
                        obj = self.objects[tool]
                    else:
                        # check whether tool is an ID of an object face
                        objs = [o for o in self.object_list for f in o.faces if f.id == tool]
                        if objs:
                            obj = objs[0]
                        else:
                            self.logger.info("Tool must be a sheet object or a face of an object.")
                            return False
                    if isinstance(obj, FacePrimitive) or isinstance(obj, Object3d) and obj.object_type != "Line":
                        obj_name = obj.name
                        obj = obj.faces[0]
                        tool_type = "FaceTool"
                    elif obj.object_type == "Line":
                        obj_name = obj.name
                        obj = obj.edges[0]
                        tool_type = "EdgeTool"
                elif isinstance(tool, FacePrimitive):
                    for o in self.object_list:
                        for f in o.faces:
                            if f.id == tool.id:
                                obj_name = o.name
                                obj = f
                    tool_type = "FaceTool"
                elif isinstance(tool, EdgePrimitive):
                    for o in self.object_list:
                        for e in o.edges:
                            if e.id == tool.id:
                                obj_name = o.name
                                obj = e
                    tool_type = "EdgeTool"
                elif isinstance(tool, Polyline) or tool.object_type != "Line":
                    for o in self.object_list:
                        if o.name == tool.name:
                            obj_name = tool.name
                            obj = o.edges[0]
                    tool_type = "EdgeTool"
                else:
                    self.logger.error("Face tool part has to be provided as a string (name) or an int (face id).")
                    return False
                planes = "Dummy"
                tool_type = tool_type
                tool_entity_id = obj.id
                selections = [
                    "NAME:Selections",
                    "Selections:=",
                    objects,
                    "NewPartsModelFlag:=",
                    "Model",
                    "ToolPart:=",
                    obj_name,
                ]
        else:
            if plane is None and tool or not plane:
                self.logger.info("For 2D design types only planes can be defined.")
                return False
            elif plane is not None:
                tool_type = "PlaneTool"
                tool_entity_id = -1
                planes = GeometryOperators.cs_plane_to_plane_str(plane)
                selections = ["NAME:Selections", "Selections:=", objects, "NewPartsModelFlag:=", "Model"]
        self.oeditor.Split(
            selections,
            [
                "NAME:SplitToParameters",
                "SplitPlane:=",
                planes,
                "WhichSide:=",
                sides,
                "ToolType:=",
                tool_type,
                "ToolEntityID:=",
                tool_entity_id,
                "SplitCrossingObjectsOnly:=",
                split_crossing_objs,
                "DeleteInvalidObjects:=",
                delete_invalid_objs,
            ],
        )
        self.refresh_all_ids()
        return [objects] + [i for i in self.object_names if i not in all_objs]

    @pyaedt_function_handler()  # TODO: Deprecate this and add duplicate as an option in the mirror method.
    def duplicate_and_mirror(
        self,
        objid,
        position,
        vector,
        is_3d_comp=False,
        duplicate_assignment=True,
    ):
        """Duplicate and mirror a selection.

        Parameters
        ----------
        objid : str, int, or  Object3d
            Name or ID of the object.
        position : float
            List of the ``[x, y, z]`` coordinates or
            Application.Position object for the selection.
        vector : float
            List of the ``[x1, y1, z1]`` coordinates or
            Application.Position object for the vector.
        is_3d_comp : bool, optional
            If ``True``, the method will try to return the duplicated list of 3dcomponents. The default is ``False``.
        duplicate_assignment : bool, optional
            If True, the method duplicates selection assignments. The default value is ``True``.

        Returns
        -------
        list
            List of objects created or an empty list.

        References
        ----------

        >>> oEditor.DuplicateMirror
        """
        return self.mirror(
            objid, position, vector, duplicate=True, is_3d_comp=is_3d_comp, duplicate_assignment=duplicate_assignment
        )
        # selections = self.convert_to_selections(objid)

    @pyaedt_function_handler()
    def mirror(self, objid, position, vector, duplicate=False, is_3d_comp=False, duplicate_assignment=True):
        """Mirror a selection.

        Parameters
        ----------
        objid : str, int, or Object3d
            Name or ID of the object.
        position : int or float
            List of the ``[x, y, z]`` coordinates or the
            ``Application.Position`` object for the selection.
        duplicate : bool, optional
            Whether if duplicate the object before mirror or not. Default is ``False``.
        is_3d_comp : bool, optional
            Whether the component is 3D. The default is ``False``. If ``True``, the method
            tries to return the duplicated list of 3D components.
        vector : float
            List of the ``[x1, y1, z1]`` coordinates or
            the ``Application.Position`` object for the vector.
        duplicate_assignment : bool, optional
            Whether to duplicate selection assignments. The default is ``True``.

        Returns
        -------
        bool, list
            List of objects created or ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Mirror
        >>> oEditor.DuplicateMirror
        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self._pos_with_arg(position)
        Xnorm, Ynorm, Znorm = self._pos_with_arg(vector)
        if duplicate:
            vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
            vArg2 = ["NAME:DuplicateToMirrorParameters"]
            vArg2.append("DuplicateMirrorBaseX:="), vArg2.append(Xpos)
            vArg2.append("DuplicateMirrorBaseY:="), vArg2.append(Ypos)
            vArg2.append("DuplicateMirrorBaseZ:="), vArg2.append(Zpos)
            vArg2.append("DuplicateMirrorNormalX:="), vArg2.append(Xnorm)
            vArg2.append("DuplicateMirrorNormalY:="), vArg2.append(Ynorm)
            vArg2.append("DuplicateMirrorNormalZ:="), vArg2.append(Znorm)
            vArg3 = ["NAME:Options", "DuplicateAssignments:=", duplicate_assignment]
            if is_3d_comp:
                orig_3d = [i for i in self.user_defined_component_names]
            added_objs = self.oeditor.DuplicateMirror(vArg1, vArg2, vArg3)
            self.add_new_objects()
            if is_3d_comp:
                added_3d_comps = [i for i in self.user_defined_component_names if i not in orig_3d]
                if added_3d_comps:
                    self.logger.info("Found 3D Components Duplication")
                    return added_3d_comps
            return added_objs
        else:
            vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
            vArg2 = ["NAME:MirrorParameters"]
            vArg2.append("MirrorBaseX:="), vArg2.append(Xpos)
            vArg2.append("MirrorBaseY:="), vArg2.append(Ypos)
            vArg2.append("MirrorBaseZ:="), vArg2.append(Zpos)
            vArg2.append("MirrorNormalX:="), vArg2.append(Xnorm)
            vArg2.append("MirrorNormalY:="), vArg2.append(Ynorm)
            vArg2.append("MirrorNormalZ:="), vArg2.append(Znorm)

            self.oeditor.Mirror(vArg1, vArg2)
            return True

    @pyaedt_function_handler()
    def move(self, objid, vector):
        """Move objects from a list.

        Parameters
        ----------
        objid : list, Position object
            List of object IDs.
        vector : list
            Vector of the direction move. It can be a list of the ``[x, y, z]``
            coordinates or a Position object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Move
        """
        Xvec, Yvec, Zvec = self._pos_with_arg(vector)
        szSelections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", szSelections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:TranslateParameters"]
        vArg2.append("TranslateVectorX:="), vArg2.append(Xvec)
        vArg2.append("TranslateVectorY:="), vArg2.append(Yvec)
        vArg2.append("TranslateVectorZ:="), vArg2.append(Zvec)

        if self.oeditor is not None:
            self.oeditor.Move(vArg1, vArg2)
        return True

    @pyaedt_function_handler()
    def duplicate_around_axis(
        self,
        objid,
        cs_axis,
        angle=90,
        nclones=2,
        create_new_objects=True,
        is_3d_comp=False,
        duplicate_assignment=True,
    ):
        """Duplicate a selection around an axis.

        Parameters
        ----------
        objid : list, str, int, Object3d or UserDefinedComponent
            Name or ID of the object.
        cs_axis :
            Coordinate system axis or the Application.AXIS object.
        angle : float, optional
            Angle rotation in degees. The default is ``90``.
        nclones : int, optional
            Number of clones. The default is ``2``.
        create_new_objects :
            Whether to create the copies as new objects. The
            default is ``True``.
        is_3d_comp : bool, optional
            If ``True``, the method will try to return the duplicated list of 3dcomponents. The default is ``False``.
        duplicate_assignment : bool, optional
            If True, the method duplicates selection assignments. The default value is ``True``.

        Returns
        -------
        tuple

        References
        ----------

        >>> oEditor.DuplicateAroundAxis
        """
        selections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = [
            "NAME:DuplicateAroundAxisParameters",
            "CreateNewObjects:=",
            create_new_objects,
            "WhichAxis:=",
            GeometryOperators.cs_axis_str(cs_axis),
            "AngleStr:=",
            self._arg_with_dim(angle, "deg"),
            "Numclones:=",
            str(nclones),
        ]
        vArg3 = ["NAME:Options", "DuplicateAssignments:=", duplicate_assignment]
        added_objs = self.oeditor.DuplicateAroundAxis(vArg1, vArg2, vArg3)
        self._duplicate_added_objects_tuple()
        if is_3d_comp:
            return self._duplicate_added_components_tuple()
        return True, list(added_objs)

    def _duplicate_added_objects_tuple(self):
        added_objects = self.add_new_objects()
        if added_objects:
            return True, added_objects
        else:
            return False, []

    def _duplicate_added_components_tuple(self):
        added_component = self.add_new_user_defined_component()
        if added_component:
            return True, added_component
        else:
            return False, []

    @pyaedt_function_handler()
    def duplicate_along_line(
        self,
        objid,
        vector,
        nclones=2,
        attachObject=False,
        is_3d_comp=False,
        duplicate_assignment=True,
    ):
        """Duplicate a selection along a line.

        Parameters
        ----------
        objid : list, str, int, :class:`pyaedt.modeler.Object3d.Object3d`
            Name or ID of the object.
        vector : list
            List of ``[x1,y1,z1]`` coordinates or the Application.Position object for
            the vector.
        attachObject : bool, optional
            The default is ``False``.
        nclones : int, optional
            Number of clones. The default is ``2``.
        is_3d_comp : bool, optional
            If True, the method will try to return the duplicated list of 3dcomponents. The default is ``False``.
        duplicate_assignment : bool, optional
            If True, the method duplicates selection assignments. The default value is ``True``.

        Returns
        -------
        tuple

        References
        ----------

        >>> oEditor.DuplicateAlongLine
        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self._pos_with_arg(vector)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:DuplicateToAlongLineParameters"]
        vArg2.append("CreateNewObjects:="), vArg2.append(not attachObject)
        vArg2.append("XComponent:="), vArg2.append(Xpos)
        vArg2.append("YComponent:="), vArg2.append(Ypos)
        vArg2.append("ZComponent:="), vArg2.append(Zpos)
        vArg2.append("Numclones:="), vArg2.append(str(nclones))
        vArg3 = ["NAME:Options", "DuplicateAssignments:=", duplicate_assignment]
        self.oeditor.DuplicateAlongLine(vArg1, vArg2, vArg3)
        if is_3d_comp:
            return self._duplicate_added_components_tuple()
        if attachObject:
            return True, []
        return self._duplicate_added_objects_tuple()

    @pyaedt_function_handler()
    def thicken_sheet(self, objid, thickness, bBothSides=False):
        """Thicken the sheet of the selection.

        Parameters
        ----------
        objid : list, str, int, :class:`pyaedt.modeler.Object3d.Object3d`
            Name or ID of the object.
        thickness : float, str
            Amount to thicken the sheet by.
        bBothSides : bool, optional
            Whether to thicken the sheet on both side. The default is ``False``.

        Returns
        -------
        pyaedt.modeler.cad.object3d.Object3d

        References
        ----------

        >>> oEditor.ThickenSheet
        """
        selections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:SheetThickenParameters"]
        vArg2.append("Thickness:="), vArg2.append(self._arg_with_dim(thickness))
        vArg2.append("BothSides:="), vArg2.append(bBothSides)

        self.oeditor.ThickenSheet(vArg1, vArg2)

        if isinstance(objid, list):
            obj_list = []
            for objl in objid:
                obj_list.append(self.update_object(objl))
            return obj_list
        return self.update_object(objid)

    @pyaedt_function_handler()
    def sweep_along_normal(self, obj_name, face_id, sweep_value=0.1):
        """Sweep the selection along the vector.

        Parameters
        ----------
        obj_name : list, str, int, :class:`pyaedt.modeler.Object3d.Object3d`
            Name or ID of the object.
        face_id : int or list
            Face or list of faces to sweep.
        sweep_value : float, optional
            Sweep value. The default is ``0.1``.

        Returns
        -------
        pyaedt.modeler.cad.object3d.Object3d

        References
        ----------

        >>> oEditor.SweepFacesAlongNormal
        """
        if not isinstance(face_id, list):
            face_id = [face_id]
        selections = self.convert_to_selections(obj_name)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:Parameters"]
        vArg2.append(
            [
                "NAME:SweepFaceAlongNormalToParameters",
                "FacesToDetach:=",
                face_id,
                "LengthOfSweep:=",
                self._arg_with_dim(sweep_value),
            ]
        )

        objs = self._all_object_names
        self.oeditor.SweepFacesAlongNormal(vArg1, vArg2)
        self.cleanup_objects()
        objs2 = self._all_object_names
        obj = [i for i in objs2 if i not in objs]
        for el in obj:
            self._create_object(el)
        if obj:
            if len(obj) > 1:
                return [self.update_object(self[o]) for o in obj]
            else:
                return self.update_object(self[obj[0]])
        return False

    @pyaedt_function_handler()
    def sweep_along_vector(self, objid, sweep_vector, draft_angle=0, draft_type="Round"):
        """Sweep the selection along a vector.

        Parameters
        ----------
        objid : list, str, int, :class:`pyaedt.modeler.Object3d.Object3d`
            Name or ID of the object.
        sweep_vector : float
            List of ``[x1, y1, z1]`` coordinates or Application.Position object for
            the vector.
        draft_angle : float, optional
            Draft angle in degrees. The default is ``0``.
        draft_type : str
            Type of the draft. Options are ``"Round"``, ``"Natural"``,
            and ``"Extended"``. The default is ``"Round"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SweepAlongVector
        """
        selections = self.convert_to_selections(objid)
        vectorx, vectory, vectorz = self._pos_with_arg(sweep_vector)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:VectorSweepParameters"]
        vArg2.append("DraftAngle:="), vArg2.append(self._arg_with_dim(draft_angle, "deg"))
        vArg2.append("DraftType:="), vArg2.append(GeometryOperators.draft_type_str(draft_type))
        vArg2.append("SweepVectorX:="), vArg2.append(vectorx)
        vArg2.append("SweepVectorY:="), vArg2.append(vectory)
        vArg2.append("SweepVectorZ:="), vArg2.append(vectorz)

        self.oeditor.SweepAlongVector(vArg1, vArg2)

        return self.update_object(objid)

    @pyaedt_function_handler()
    def sweep_along_path(
        self, objid, sweep_object, draft_angle=0, draft_type="Round", is_check_face_intersection=False, twist_angle=0
    ):
        """Sweep the selection along a path.

        Parameters
        ----------
        objid : list, str, int, :class:`pyaedt.modeler.Object3d.Object3d`
            Name or ID of the object.
        sweep_object : str, int
            Name or ID of the sweep.
        draft_angle : float, optional
            Draft angle in degrees. The default is ``0``.
        draft_type : str
            Type of the draft. Options are ``"Round"``, ``"Natural"``,
            and ``"Extended"``. The default is ``"Round"``.
        is_check_face_intersection : bool, optional
            The default is ``False``.
        twist_angle : float, optional
           Twist angle in degrees. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SweepAlongPath
        """
        selections = self.convert_to_selections(objid) + "," + self.convert_to_selections(sweep_object)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:PathSweepParameters"]
        vArg2.append("DraftAngle:="), vArg2.append(self._arg_with_dim(draft_angle, "deg"))
        vArg2.append("DraftType:="), vArg2.append(GeometryOperators.draft_type_str(draft_type))
        vArg2.append("CheckFaceFaceIntersection:="), vArg2.append(is_check_face_intersection)
        vArg2.append("TwistAngle:="), vArg2.append(str(twist_angle) + "deg")

        self.oeditor.SweepAlongPath(vArg1, vArg2)

        return self.update_object(objid)

    @pyaedt_function_handler()
    def sweep_around_axis(self, objid, cs_axis, sweep_angle=360, draft_angle=0, number_of_segments=0):
        """Sweep the selection around the axis.

        Parameters
        ----------
        objid : list, str, int, :class:`pyaedt.modeler.Object3d.Object3d`
            Name or ID of the object.
        cs_axis :
            Coordinate system axis or the Application.AXIS object.
        sweep_angle : float
            Sweep angle in degrees. The default is ``360``.
        draft_angle : float
            Draft angle in degrees. The default is ``0``.
        number_of_segments : int, optional
            Number of segments of the sweep operation. Default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SweepAroundAxis
        """
        selections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = [
            "NAME:AxisSweepParameters",
            "DraftAngle:=",
            self._arg_with_dim(draft_angle, "deg"),
            "DraftType:=",
            "Round",
            "CheckFaceFaceIntersection:=",
            False,
            "SweepAxis:=",
            GeometryOperators.cs_axis_str(cs_axis),
            "SweepAngle:=",
            self._arg_with_dim(sweep_angle, "deg"),
            "NumOfSegments:=",
            str(number_of_segments),
        ]

        self.oeditor.SweepAroundAxis(vArg1, vArg2)

        return self.update_object(objid)

    @pyaedt_function_handler()
    def section(self, object_list, plane, create_new=True, section_cross_object=False):
        """Section the selection.

        Parameters
        ----------
        object_list : list, str, int, or  :class:`pyaedt.modeler.Object3d.Object3d`
            One or more objects to section.
        plane : str
            Coordinate plane or Application.PLANE object.
            Choices for the coordinate plane are ``"XY"``, ``"YZ"``, and ``"ZX"``.'
        create_new : bool, optional
            The default is ``True``, but this parameter has no effect.
        section_cross_object : bool, optional
            The default is ``False``, but this parameter has no effect.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Section
        """
        section_plane = GeometryOperators.cs_plane_to_plane_str(plane)

        selections = self.convert_to_selections(object_list)

        self.oeditor.Section(
            ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"],
            [
                "NAME:SectionToParameters",
                "CreateNewObjects:=",
                create_new,
                "SectionPlane:=",
                section_plane,
                "SectionCrossObject:=",
                section_cross_object,
            ],
        )
        self.refresh_all_ids()
        return True

    @pyaedt_function_handler()
    def separate_bodies(self, object_list, create_group=False):
        """Separate bodies of the selection.

        Parameters
        ----------
        object_list : list
            List of objects to separate.
        create_group : bool, optional
            Whether to create a group. The default is ``False``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d, bool
            3D object.
            ``False`` when failed.

        References
        ----------

        >>> oEditor.SeparateBody
        """
        try:
            selections = self.convert_to_selections(object_list)
            all_objs = [i for i in self.object_names]
            self.oeditor.SeparateBody(
                ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"],
                ["CreateGroupsForNewObjects:=", create_group],
            )
            self.refresh_all_ids()
            new_objects_list_names = [selections] + [i for i in self.object_names if i not in all_objs]
            new_objects_list = []
            for obj in self.object_list:
                for new_obj in new_objects_list_names:
                    if obj.name == new_obj:
                        new_objects_list.append(obj)
            return new_objects_list
        except:
            return False

    @pyaedt_function_handler()
    def rotate(self, objid, cs_axis, angle=90.0, unit="deg"):
        """Rotate the selection.

        Parameters
        ----------
        objid :  list, str, int, or  :class:`pyaedt.modeler.Object3d.Object3d`
             ID of the object.
        cs_axis
            Coordinate system axis or the Application.AXIS object.
        angle : float
            Angle of rotation. The units, defined by ``unit``, can be either
            degrees or radians. The default is ``90.0``.
        unit : text, optional
             Units for the angle. Options are ``"deg"`` or ``"rad"``.
             The default is ``"deg"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Rotate
        """
        selections = self.convert_to_selections(objid)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:RotateParameters"]
        vArg2.append("RotateAxis:="), vArg2.append(GeometryOperators.cs_axis_str(cs_axis))
        vArg2.append("RotateAngle:="), vArg2.append(self._arg_with_dim(angle, unit))

        if self.oeditor is not None:
            self.oeditor.Rotate(vArg1, vArg2)

        return True

    @pyaedt_function_handler()
    def subtract(self, blank_list, tool_list, keep_originals=True, **kwargs):
        """Subtract objects.

        Parameters
        ----------
        blank_list : str, Object3d, int or List of str, int and Object3d.
            List of objects to subtract from. The list can be of
            either :class:`pyaedt.modeler.Object3d.Object3d` objects or object IDs.
        tool_list : list
            List of objects to subtract. The list can be of
            either Object3d objects or object IDs.
        keep_originals : bool, optional
            Whether to keep the original objects. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Subtract
        """
        if "keepOriginals" in kwargs:
            warnings.warn("keepOriginals has been deprecated. use keep_originals.", DeprecationWarning)
            keep_originals = kwargs["keepOriginals"]
        szList = self.convert_to_selections(blank_list)
        szList1 = self.convert_to_selections(tool_list)

        vArg1 = ["NAME:Selections", "Blank Parts:=", szList, "Tool Parts:=", szList1]
        vArg2 = ["NAME:SubtractParameters", "KeepOriginals:=", keep_originals]

        self.oeditor.Subtract(vArg1, vArg2)
        if not keep_originals:
            self.cleanup_objects()

        return True

    @pyaedt_function_handler()
    def imprint(self, blank_list, tool_list, keep_originals=True):
        """Imprin an object list on another object list.

        Parameters
        ----------
        blank_list : list of Object3d or list of int
            List of objects to imprint from. The list can be of
            either :class:`pyaedt.modeler.Object3d.Object3d` objects or object IDs.
        tool_list : list of Object3d or list of int
            List of objects to imprint. The list can be of
            either Object3d objects or object IDs.
        keep_originals : bool, optional
            Whether to keep the original objects. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Imprint
        """
        szList = self.convert_to_selections(blank_list)
        szList1 = self.convert_to_selections(tool_list)

        vArg1 = ["NAME:Selections", "Blank Parts:=", szList, "Tool Parts:=", szList1]
        vArg2 = ["NAME:ImprintParameters", "KeepOriginals:=", keep_originals]

        self.oeditor.Imprint(vArg1, vArg2)
        if not keep_originals:
            self.cleanup_objects()
        return True

    @pyaedt_function_handler()
    def _imprint_projection(self, tool_list, keep_originals=True, normal=True, vector_direction=None, distance="1mm"):
        szList1 = self.convert_to_selections(tool_list)

        varg1 = ["NAME:Selections", "Selections:=", szList1]
        varg2 = [
            "NAME:ImprintProjectionParameters",
            "KeepOriginals:=",
            keep_originals,
            "NormalProjection:=",
            normal,
        ]
        if not normal:
            varg2.append("Distance:=")
            varg2.append(self._app.value_with_units(distance))
            varg2.append("DirectionX:=")
            varg2.append(self._app.value_with_units(vector_direction[0]))
            varg2.append("DirectionY:=")
            varg2.append(self._app.value_with_units(vector_direction[1]))
            varg2.append("DirectionZ:=")
            varg2.append(self._app.value_with_units(vector_direction[2]))

        self.oeditor.ImprintProjection(varg1, varg2)
        if not keep_originals:
            self.cleanup_objects()
        return True

    @pyaedt_function_handler
    def imprint_normal_projection(
        self,
        tool_list,
        keep_originals=True,
    ):
        """Imprint the normal projection of objects over a sheet.

        Parameters
        ----------
        tool_list : list
            List of objects to imprint. The list can be of
            either Object3d objects or object IDs.
        keep_originals : bool, optional
            Whether to keep the original objects. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ImprintProjection
        """
        return self._imprint_projection(tool_list, keep_originals, True)

    @pyaedt_function_handler
    def imprint_vector_projection(
        self,
        tool_list,
        vector_points,
        distance,
        keep_originals=True,
    ):
        """Imprint the projection of objects over a sheet with a specified vector and distance.

        Parameters
        ----------
        tool_list : list
            List of objects to imprint. The list can be of
            either Object3d objects or object IDs.
        vector_points : list
            List of [x,y,z] vector projection.
        distance : str, int
            Distance of Projection.
        keep_originals : bool, optional
            Whether to keep the original objects. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ImprintProjection
        """
        return self._imprint_projection(tool_list, keep_originals, False, vector_points, distance)

    @pyaedt_function_handler()
    def purge_history(self, theList):
        """Purge history objects from object names.

        Parameters
        ----------
        theList : list
            List of object names to purge.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.PurgeHistory
        """
        szList = self.convert_to_selections(theList)

        vArg1 = ["NAME:Selections", "Selections:=", szList, "NewPartsModelFlag:=", "Model"]

        self.oeditor.PurgeHistory(vArg1)
        return True

    @pyaedt_function_handler()
    def get_model_bounding_box(self):
        """Retrieve the model bounding box.


        Returns
        -------
        List
            List of six float values representing the bounding box
            in the form ``[min_x, min_y, min_z, max_x, max_y, max_z]``.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        bb = list(self.oeditor.GetModelBoundingBox())
        bound = [float(b) for b in bb]
        return bound

    @pyaedt_function_handler()
    def unite(self, unite_list, purge=False, keep_originals=False):
        """Unite objects from a list.

        Parameters
        ----------
        unite_list : list
            List of objects.
        purge : bool, optional
            Purge history after unite. Default is False.
        keep_originals : bool, optional
            Keep original objects used for the operation. Default is False.

        Returns
        -------
        str
            The united object that is the first in the list.

        References
        ----------

        >>> oEditor.Unite
        """
        slice = min(100, len(unite_list))
        num_objects = len(unite_list)
        remaining = num_objects
        objs_groups = []
        while remaining > 1:
            objs = unite_list[:slice]
            szSelections = self.convert_to_selections(objs)
            vArg1 = ["NAME:Selections", "Selections:=", szSelections]
            vArg2 = ["NAME:UniteParameters", "KeepOriginals:=", keep_originals]
            if settings.aedt_version > "2022.2":
                vArg2.append("TurnOnNBodyBoolean:=")
                vArg2.append(True)
            self.oeditor.Unite(vArg1, vArg2)
            if szSelections.split(",")[0] in self.unclassified_names:
                self.logger.error("Error in uniting objects.")
                self._odesign.Undo()
                self.cleanup_objects()
                return False
            elif purge:
                self.purge_history(objs[0])
            objs_groups.append(objs[0])
            remaining -= slice
            if remaining > 0:
                unite_list = unite_list[slice:]
        if remaining > 0:
            objs_groups.extend(unite_list)
        self.cleanup_objects()
        if len(objs_groups) > 1:
            return self.unite(objs_groups, purge=purge)
        self.logger.info("Union of {} objects has been executed.".format(num_objects))
        return self.convert_to_selections(unite_list[0], False)

    @pyaedt_function_handler()
    def clone(self, objid):
        """Clone objects from a list of object IDs.

        Parameters
        ----------
        objid : list
            List of object IDs.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        List
            List of names of objects cloned when successful.

        References
        ----------

        >>> oEditor.Copy
        >>> oEditor.Paste
        """
        self.copy(objid)
        new_objects = self.paste()
        return True, new_objects

    @pyaedt_function_handler()
    def copy(self, object_list):
        """Copy objects to the clipboard.

            Parameters
            ----------
            object_list : list
                List of objects (IDs or names).

            Returns
            -------
            list
                List of names of the objects copied when successful.

        References
        ----------

        >>> oEditor.Copy
        """
        # convert to string

        try:
            selections = self.convert_to_selections(object_list)
            vArg1 = ["NAME:Selections", "Selections:=", selections]
            self.oeditor.Copy(vArg1)
            return selections
        except AttributeError:
            self.logger.error("Unable to copy selections to clipboard.")
            return None

    @pyaedt_function_handler()
    def paste(self):
        """Paste objects from the clipboard.

        Returns
        -------
        list
            List of passed objects.

        References
        ----------

        >>> oEditor.Paste
        """
        self.oeditor.Paste()
        new_objects = self.add_new_objects()
        return new_objects

    @pyaedt_function_handler()
    def intersect(self, theList, keep_originals=False, **kwargs):
        """Intersect objects from a list.

        Parameters
        ----------
        theList : list
            List of objects.
        keep_originals : bool, optional
            Whether to keep the original object. The default is ``False``.

        Returns
        -------
        str
            Retrieve the resulting 3D Object when succeeded.

        References
        ----------

        >>> oEditor.Intersect
        """
        if "keeporiginal" in kwargs:
            warnings.warn("keeporiginal has been deprecated. use keep_originals.", DeprecationWarning)
            keep_originals = kwargs["keeporiginal"]
        unclassified = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        szSelections = self.convert_to_selections(theList)

        vArg1 = ["NAME:Selections", "Selections:=", szSelections]
        vArg2 = ["NAME:IntersectParameters", "KeepOriginals:=", keep_originals]

        self.oeditor.Intersect(vArg1, vArg2)
        unclassified1 = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        if unclassified != unclassified1:
            self._odesign.Undo()
            self.logger.error("Error in intersection. Reverting Operation")
            return
        self.cleanup_objects()
        self.logger.info("Intersection Succeeded")
        return self.convert_to_selections(theList[0], False)

    @pyaedt_function_handler()
    def connect(self, theList):
        """Connect objects from a list.

        Parameters
        ----------
        theList : list
            List of objects.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d, bool
            3D object.
            ``False`` when failed.

        References
        ----------

        >>> oEditor.Connect
        """
        try:
            unclassified_before = list(self.unclassified_names)
            szSelections = self.convert_to_selections(theList)
            szSelections_list = szSelections.split(",")
            vArg1 = ["NAME:Selections", "Selections:=", szSelections]

            self.oeditor.Connect(vArg1)
            if unclassified_before != self.unclassified_names:
                self._odesign.Undo()
                self.logger.error("Error in connection. Reverting Operation")
                return False

            self.cleanup_objects()
            self.logger.info("Connection Correctly created")

            self.refresh_all_ids()
            objects_list_after_connection = [
                obj
                for obj in self.object_list
                for sel in set(szSelections_list).intersection(self.object_names)
                if obj.name == sel
            ]
            return objects_list_after_connection
        except:
            return False

    @pyaedt_function_handler()
    def chassis_subtraction(self, chassis_part):
        """Subtract all non-vacuum objects from the main chassis object.

        Parameters
        ----------
        chassis_part : str
            Name of the main chassis object.

        References
        ----------

        >>> oEditor.Subtract
        """
        self.logger.info("Subtract all objects from Chassis object - exclude vacuum objs")
        mat_names = self._omaterial_manager.GetNames()
        num_obj_start = self.oeditor.GetNumObjects()
        blank_part = chassis_part
        # in main code this object will need to be determined automatically eg by name such as chassis or sheer size
        self.logger.info("Blank Part in Subtraction = " + str(blank_part))
        """
        check if blank part exists, if not, skip subtraction
        """
        tool_parts = list(self.oeditor.GetObjectsInGroup("Solids"))
        tool_parts.remove(blank_part)
        for mat in mat_names:
            if str(mat).lower() == "vacuum":
                objnames = self.oeditor.GetObjectsByMaterial(mat)
                for obj in objnames:
                    tool_parts.remove(obj)
                # tool_parts_final=list(set(tool_parts).difference(set(objnames)))
        tool_parts = ",".join(tool_parts)
        num_obj_end = self.oeditor.GetNumObjects()
        self.subtract(blank_part, tool_parts, True)

        self.logger.info("Subtraction Objs - Initial: " + str(num_obj_start) + "  ,  Final: " + str(num_obj_end))

    @pyaedt_function_handler()
    def _offset_on_plane(self, i, offset):
        """Offset the object on a plane.

        Parameters
        ----------
        i :

        offset :
            Offset to apply.

        Returns
        -------
        tuple
           Position of object after offset is applied.

        """
        if i > 7:
            off1 = 0
        elif i % 4 == 0 or i % 4 == 1:
            off1 = offset
        else:
            off1 = -offset
        if 3 < i < 8:
            off2 = 0
        elif i % 2 == 0:
            off2 = offset
        else:
            off2 = -offset
        if i < 4:
            off3 = 0
        elif i != 4 and i != 7 and i != 8 and i != 11:
            off3 = -offset
        else:
            off3 = +offset
        return off1, off2, off3

    @pyaedt_function_handler()
    def check_plane(self, obj, faceposition, offset=1):
        """Check for the plane that is defined as the face for an object.

        Parameters
        ----------
        obj : str
            Name of the object.
        faceposition : list
            List of the ``[x, y, z]`` coordinates for the position of the face.
        offset : optional
            Offset to apply. The default is ``1``.

        Returns
        -------
        str
            Name of the plane. It can be "XY", "XZ" or "YZ".

        """

        Xvec, Yvec, Zvec = self._pos_with_arg(faceposition)

        if isinstance(obj, int):
            obj = self.objects[obj].name
        plane = None
        found = False
        i = 0
        while not found:
            off1, off2, off3 = self._offset_on_plane(i, offset)
            vArg1 = ["NAME:FaceParameters"]
            vArg1.append("BodyName:="), vArg1.append(obj)
            vArg1.append("XPosition:="), vArg1.append(Xvec + "+" + self._arg_with_dim(off1))
            vArg1.append("YPosition:="), vArg1.append(Yvec + "+" + self._arg_with_dim(off2))
            vArg1.append("ZPosition:="), vArg1.append(Zvec + "+" + self._arg_with_dim(off3))
            try:
                face_id = self.oeditor.GetFaceByPosition(vArg1)
                if i < 4:
                    plane = "XY"
                elif i < 8:
                    plane = "XZ"
                else:
                    plane = "YZ"
                found = True
            except:
                i = i + 1
                if i > 11:
                    found = True

        return plane

    @pyaedt_function_handler()
    def get_matched_object_name(self, search_string):
        """Retrieve the name of the matched object.

        Parameters
        ----------
        search_string : str
            Text string to search for.


        Returns
        -------
        str
            Name of the matched object.

        References
        ----------

        >>> oEditor.GetMatchedObjectName
        """
        return self.oeditor.GetMatchedObjectName(search_string)

    @pyaedt_function_handler()
    def clean_objects_name(self, main_part_name):
        """Clean the names of the objects for a main part.

        Parameters
        ----------
        main_part_name : str
            Name of the main part.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.RenamePart
        """
        # import os.path
        # (CADPath, CADFilename) = os.path.split(CADFile)
        # (CADName, CADExt) = os.path.splitext(CADFilename)
        CADSuffix = main_part_name + "_"
        objNames = self.oeditor.GetMatchedObjectName(CADSuffix + "*")
        for name in objNames:
            RenameArgs = {}
            RenameArgs["NAME"] = "Rename Data"
            RenameArgs["Old Name"] = name
            RenameArgs["New Name"] = name.replace(CADSuffix, "")
            self.oeditor.RenamePart(RenameArgs)
        return True

    @pyaedt_function_handler()
    def create_airbox(self, offset=0, offset_type="Absolute", defname="AirBox_Auto"):
        """Create an airbox that is as big as the bounding extension of the project.

        Parameters
        ----------
        offset :
            Double offset value to apply on the airbox faces versus the bounding box.
            The default is ``0``.
        offset_type : str
            Type of the offset. Options are ``"Absolute"`` and ``"Relative"``.
            The default is ``"Absolute"``. If ``"Relative"``, the offset input
            is between 0 and 100.
        defname : str, optional
            Name of the airbox. The default is ``"AirBox_Auto"``.

        Returns
        -------
        int
            ID of the airbox created.

        References
        ----------

        >>> oEditor.CreateBox
        """
        self.logger.info("Adding Airbox to the Bounding ")

        bound = self.get_model_bounding_box()
        if offset_type == "Absolute":
            offset1 = offset2 = offset3 = offset
        else:
            offset1 = (bound[3] - bound[0]) * offset / 100
            offset2 = (bound[4] - bound[1]) * offset / 100
            offset3 = (bound[5] - bound[2]) * offset / 100
        startpos = self.Position(bound[0] - offset1, bound[1] - offset2, bound[2] - offset3)

        dim = []
        dim.append(bound[3] - bound[0] + 2 * offset1)
        dim.append(bound[4] - bound[1] + 2 * offset2)
        dim.append(bound[5] - bound[2] + 2 * offset3)
        airid = self.create_box(startpos, dim, defname)
        return airid

    @pyaedt_function_handler()
    def create_air_region(self, x_pos=0, y_pos=0, z_pos=0, x_neg=0, y_neg=0, z_neg=0, is_percentage=True):
        """Create an air region.

        Parameters
        ----------
        x_pos : float or str, optional
            If float, padding in the +X direction in modeler units.
            If str, padding with units in the +X direction.
            The default is ``0``.
        y_pos : float or str, optional
            If float, padding in the +Y direction in modeler units.
            If str, padding with units in the +Y direction.
            The default is ``0``.
        z_pos : float or str, optional
            If float, padding in the +Z direction in modeler units.
            If str, padding with units in the +Z direction.
            The default is ``0``.
        x_neg : float or str, optional
            If float, padding in the -X direction in modeler units.
            If str, padding with units in the -X direction.
            The default is ``0``.
        y_neg : float or str, optional
            If float, padding in the -Y direction in modeler units.
            If str, padding with units in the -Y direction.
            The default is ``0``.
        z_neg : float or str, optional
            If float, padding in the -Z direction in modeler units.
            If str, padding with units in the -Z direction.
            The default is ``0``.
        is_percentage : bool, optional
            Region definition in percentage or absolute value. The default is `True``.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateRegion
        """
        return self.create_region([x_pos, y_pos, z_pos, x_neg, y_neg, z_neg], is_percentage)

    @pyaedt_function_handler()
    def edit_region_dimensions(self, listvalues):
        """Modify the dimensions of the region.

        Parameters
        ----------
        listvalues : list
            List of the padding percentages along all six directions in
            the form ``[+X, -X, +Y, -Y, +Z, -Z]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        arg2 = ["NAME:Geometry3DCmdTab", ["NAME:PropServers", "Region:CreateRegion:1"]]
        arg3 = ["NAME:ChangedProps"]
        p = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        for label, value in zip(p, listvalues):
            padding = []
            padding.append("NAME:" + label + " Padding Data")
            padding.append("Value:=")
            padding.append(str(value))
            arg3.append(padding)
        arg2.append(arg3)
        arg.append(arg2)
        self.oeditor.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def create_face_list(self, face_list, name=None):
        """Create a list of faces given a list of face ID or a list of objects.

        Parameters
        ----------
        face_list : list
            List of face ID or list of objects

        name : str, optional
           Name of the new list.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.Lists`
            List object when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateEntityList
        """
        if name:
            for i in self.user_lists:
                if i.name == name:
                    self.logger.warning("A List with the specified name already exists!")
                    return i
        face_list = self.convert_to_selections(face_list, True)
        user_list = Lists(self)
        list_type = "Face"
        if user_list:
            result = user_list.create(
                object_list=face_list,
                name=name,
                type=list_type,
            )
            if result:
                return user_list
            else:
                self._app.logger.error("Wrong object definition. Review object list and type")
                return False
        else:
            self._app.logger.error("User list object could not be created")
            return False

    @pyaedt_function_handler()
    def create_object_list(self, object_list, name=None):
        """Create an object list given a list of object names.

        Parameters
        ----------
        object_list : list
            List of object names.
        name : str, optional
            Name of the new object list.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.Lists`
            List object when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateEntityList
        """
        if name:
            for i in self.user_lists:
                if i.name == name:
                    self.logger.warning("A List with the specified name already exists!")
                    return i
        object_list = self.convert_to_selections(object_list, True)
        user_list = Lists(self)
        list_type = "Object"
        if user_list:
            result = user_list.create(
                object_list=object_list,
                name=name,
                type=list_type,
            )
            if result:
                return user_list
            else:
                self._app.logger.error("Wrong object definition. Review object list and type")
                return False
        else:
            self._app.logger.error("User list object could not be created")
            return False

    @pyaedt_function_handler()
    def generate_object_history(self, objectname):
        """Generate history for the object.

        Parameters
        ----------
        objectname : str
            Name of the history object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.GenerateHistory
        """
        objectname = self.convert_to_selections(objectname)
        self.oeditor.GenerateHistory(
            ["NAME:Selections", "Selections:=", objectname, "NewPartsModelFlag:=", "Model", "UseCurrentCS:=", True]
        )
        self.cleanup_objects()
        return True

    @pyaedt_function_handler()
    def create_faceted_bondwire_from_true_surface(self, bondname, bond_direction, min_size=0.2, numberofsegments=8):
        """Create a faceted bondwire from an existing true surface bondwire.

        Parameters
        ----------
        bondname : str
            Name of the bondwire to replace.
        bond_direction : list
            List of the ``[x, y, z]`` coordinates for the axis direction
            of the bondwire. For example, ``[0, 1, 2]``.
        min_size : float
            Minimum size of the subsegment of the new polyline. The default is ``0.2``.
        numberofsegments : int, optional
            Number of segments. The default is ``8``.

        Returns
        -------
        str
            Name of the bondwire created.
        """
        old_bondwire = self.get_object_from_name(bondname)
        if not old_bondwire:
            return False
        edges = old_bondwire.edges
        faces = old_bondwire.faces
        centers = []
        for el in faces:
            center = el.center
            if center:
                centers.append(center)
        edgelist = []
        verlist = []
        for el in edges:
            ver = el.vertices
            if len(ver) < 2:
                continue
            p1 = ver[0].position
            p2 = ver[1].position
            p3 = [abs(i - j) for i, j in zip(p1, p2)]

            dir = p3.index(max(p3))
            if dir == bond_direction:
                edgelist.append(el)
                verlist.append([p1, p2])
        if not edgelist:
            self.logger.error("No edges found specified direction. Check again")
            return False
        connected = [edgelist[0]]
        tol = 1e-6
        for edge in edgelist[1:]:
            ver = edge.vertices
            p1 = ver[0].position
            p2 = ver[1].position
            for el in connected:
                ver1 = el.vertices
                p3 = ver1[0].position
                p4 = ver1[1].position
                dist = GeometryOperators.points_distance(p1, p3)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p1, p4)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p2, p3)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p2, p4)
                if dist < tol:
                    connected.append(edge)
                    break
        new_edges = []
        for edge in connected:
            edge_object = self.create_object_from_edge(edge)
            new_edges.append(edge_object)

        self.unite(new_edges)
        self.generate_object_history(new_edges[0])
        self.convert_segments_to_line(new_edges[0].name)

        edges = new_edges[0].edges
        i = 0
        edge_to_delete = []
        first_vert = None
        for edge in edges:
            ver = edge.vertices
            p1 = ver[0].position
            p2 = ver[1].position
            if not first_vert:
                first_vert = p1
            dist = GeometryOperators.points_distance(p1, p2)
            if dist < min_size:
                edge_to_delete.append(i)
            i += 1

        rad = 1e6
        move_vector = None
        for fc in centers:
            dist = GeometryOperators.points_distance(fc, first_vert)
            if dist < rad:
                rad = dist
                move_vector = GeometryOperators.v_sub(fc, first_vert)

        P = self.get_existing_polyline(object=new_edges[0])

        if edge_to_delete:
            P.remove_edges(edge_to_delete)

        angle = math.pi * (180 - 360 / numberofsegments) / 360

        status = P.set_crosssection_properties(
            type="Circle", num_seg=numberofsegments, width=(rad * (2 - math.sin(angle))) * 2
        )
        if status:
            self.move(new_edges[0], move_vector)
            old_bondwire.model = False
            return new_edges[0]
        else:
            return False

    @pyaedt_function_handler()
    def get_entitylist_id(self, name):
        """Retrieve the ID of an entity list.

        Parameters
        ----------
        name : str
            Name of the entity list.

        Returns
        -------
        int
            ID of the entity list.

        References
        ----------

        >>> oEditor.GetEntityListIDByName
        """
        id = self.oeditor.GetEntityListIDByName(name)
        return id

    @pyaedt_function_handler()
    def create_outer_facelist(self, externalobjects, name="outer_faces"):
        """Create a face list from a list of outer objects.

        Parameters
        ----------
        externalobjects : list
            List of outer objects.
        name : str, optional
            Name of the new list. The default is ``"outer_faces"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        list2 = self.select_allfaces_fromobjects(externalobjects)  # find ALL faces of outer objects
        self.create_face_list(list2, name)
        self.logger.info("Extfaces of thermal model = " + str(len(list2)))
        return True

    @pyaedt_function_handler()
    def explicitly_subtract(self, diellist, metallist):
        """Explicitly subtract all elements in a SolveInside list and a SolveSurface list.

        Parameters
        ----------
        diellist : list
            List of dielectrics.
        metallist : list
            List of metals.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Subtract
        >>> oEditor.PurgeHistory
        """
        self.logger.info("Creating explicit subtraction between objects.")
        for el in diellist:
            list1 = el
            list2 = ""
            for el1 in metallist:
                list2 = list2 + el1 + ","
            for el1 in diellist:
                if el1 is not el:
                    list2 = list2 + el1 + ","
            if list2:
                list2 = list2[:-1]
                self.subtract(list1, list2, True)
                self.purge_history(list1)
                self.purge_history(list2)
        for el in metallist:
            list1 = el
            list2 = ""
            for el1 in metallist:
                if el1 is not el:
                    list2 = list2 + el1 + ","
            if list2:
                list2 = list2[:-1]
                self.subtract(list1, list2, True)
                self.purge_history(list1)
                self.purge_history(list2)
        self.logger.info("Explicit subtraction is completed.")
        return True

    @pyaedt_function_handler()
    def find_port_faces(self, port_sheets):
        """Find the vacuums given a list of input sheets.

        Starting from a list of input sheets, this method creates a list of output sheets
        that represent the blank parts (vacuums) and the tool parts of all the intersections
        of solids on the sheets. After a vacuum on a sheet is found, a port can be
        created on it.

        Parameters
        ----------
        port_sheets : list
            List of input sheets names.

        Returns
        -------
        List
            List of output sheets (`2x len(port_sheets)`).

        """
        faces = []
        solids = [s for s in self.solid_objects if s.material_name not in ["vacuum", "air"] and s.model]
        for sheet_name in port_sheets:
            sheet = self[sheet_name]  # get the sheet object
            _, cloned = self.clone(sheet)
            cloned = self[cloned[0]]
            cloned.subtract(solids)
            sheet.subtract(cloned)
            cloned.name = sheet.name + "_Face1Vacuum"
            faces.append(sheet.name)
            faces.append(cloned.name)
        return faces

    @pyaedt_function_handler()
    def get_line_ids(self):
        """Create a dictionary of object IDs for the lines in the design with the line name as the key."""
        line_ids = {}
        line_list = list(self.oeditor.GetObjectsInGroup("Lines"))
        for line_object in line_list:
            # TODO Problem with GetObjectIDByName
            try:
                line_ids[line_object] = str(self.oeditor.GetObjectIDByName(line_object))
            except:
                self.logger.warning("Line {} has an invalid ID!".format(line_object))
        return line_ids

    @pyaedt_function_handler()
    def get_bounding_dimension(self):
        """Retrieve the dimension array of the bounding box.

        Returns
        -------
        list
            List of three float values representing the bounding box dimensions
            in the form ``[dim_x, dim_y, dim_z]``.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        oBoundingBox = list(self.oeditor.GetModelBoundingBox())
        dimensions = []
        dimensions.append(abs(float(oBoundingBox[0]) - float(oBoundingBox[3])))
        dimensions.append(abs(float(oBoundingBox[1]) - float(oBoundingBox[4])))
        dimensions.append(abs(float(oBoundingBox[2]) - float(oBoundingBox[5])))
        return dimensions

    @pyaedt_function_handler()
    def get_object_name_from_edge_id(self, edge_id):
        """Retrieve the object name for a predefined edge ID.

        Parameters
        ----------
        edge_id : int
            ID of the edge.

        Returns
        -------
        str
            Name of the edge if it exists, ``False`` otherwise.

        References
        ----------

        >>> oEditor.GetEdgeIDsFromObject
        """
        for object in list(self._object_names_to_ids.keys()):
            try:
                oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(object)
                if str(edge_id) in oEdgeIDs:
                    return object
            except:
                return False
        return False

    @pyaedt_function_handler()
    def get_solving_volume(self):
        """Generate a mesh for a setup.

        Returns
        -------
        int
            ``1`` when successful, ``0`` when failed.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        bound = self.get_model_bounding_box()
        volume = abs(bound[3] - bound[0]) * abs(bound[4] - bound[1]) * abs(bound[5] - bound[2])
        volume = str(round(volume, 0))
        return volume

    @pyaedt_function_handler()
    def vertex_data_of_lines(self, txtfilter=None):
        """Generate a dictionary of line vertex data for all lines contained within the design.

        Parameters
        ----------
        txtfilter : str, optional
            Text string for filtering. The default is ``None``. When a text string is specified,
            line data is generated only if this text string is contained within the line name.

        Returns
        -------
        dict
            Dictionary of the line name with a list of vertex positions in either 2D or 3D.

        """
        line_data = {}
        lines = self.get_line_ids()
        if txtfilter is not None:
            lines = [n for n in lines if txtfilter in n]
        for x in lines:
            line_data[x] = self.get_vertices_of_line(x)

        return line_data

    @pyaedt_function_handler()
    def get_vertices_of_line(self, sLineName):
        """Generate a list of vertex positions for a line object from AEDT in model units.

        Parameters
        ----------
        sLineName : str
            Name of the line object in AEDT.

        Returns
        -------
        list
            List of the ``[x, y, (z)]`` coordinates for the 2D or 3D line object.

        References
        ----------

        >>> oEditor.GetVertexIDsFromObject
        """
        position_list = []

        # Get all vertices in the line
        vertices_on_line = self.oeditor.GetVertexIDsFromObject(sLineName)

        if settings.aedt_version > "2022.2":
            vertices_on_line = vertices_on_line[::-1]

        for x in vertices_on_line:
            pos = self.oeditor.GetVertexPosition(x)
            if self.design_type == "Maxwell 2D":
                if self.geometry_mode == "XY":
                    position_list.append([float(pos[0]), float(pos[1])])
                else:
                    position_list.append([float(pos[0]), float(pos[2])])
            else:
                position_list.append([float(pos[0]), float(pos[1]), float(pos[2])])

        return position_list

    @pyaedt_function_handler()
    def import_3d_cad(
        self,
        filename,
        healing=False,
        refresh_all_ids=True,
        import_materials=False,
        create_lightweigth_part=False,
        group_by_assembly=False,
        create_group=True,
        separate_disjoints_lumped_object=False,
        import_free_surfaces=False,
        point_coicidence_tolerance=1e-6,
    ):
        """Import a CAD model.

        Parameters
        ----------
        filename : str
            Full path and name of the CAD file.
        healing : bool, optional
            Whether to perform healing. The default is ``False``, in which
            case healing is not performed.
        healing : int, optional
            Whether to perform healing. The default is ``0``, in which
            case healing is not performed.
        refresh_all_ids : bool, optional
            Whether to refresh all IDs after the CAD file is loaded. The
            default is ``True``. Refreshing IDs can take a lot of time in
            a big project.
        import_materials : bool optional
            Either to import material names from the file or not if presents.
        create_lightweigth_part : bool ,optional
            Either to import lightweight or not.
        group_by_assembly : bool, optional
            Either import by sub-assembly or individual parts. The default is ``False``.
        create_group : bool, optional
            Either to create a new group of imported objects. The default is ``True``.
        separate_disjoints_lumped_object : bool, optional
            Either to automatically separate disjoint parts. The default is ``False``.
        import_free_surfaces : bool, optional
            Either to import free surfaces parts. The default is ``False``.
        point_coicidence_tolerance : float, optional
            Tolerance on point. Default is ``1e-6``.

        Returns
        -------
         bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Import
        """

        if str(healing) in ["0", "1"]:
            warnings.warn(
                "Assigning `0` or `1` to `healing` option is deprecated. Assign `True` or `False` instead.",
                DeprecationWarning,
            )
        vArg1 = ["NAME:NativeBodyParameters"]
        vArg1.append("HealOption:="), vArg1.append(int(healing))
        vArg1.append("Options:="), vArg1.append("-1")
        vArg1.append("FileType:="), vArg1.append("UnRecognized")
        vArg1.append("MaxStitchTol:="), vArg1.append(-1)
        vArg1.append("ImportFreeSurfaces:="), vArg1.append(import_free_surfaces)
        vArg1.append("GroupByAssembly:="), vArg1.append(group_by_assembly)
        vArg1.append("CreateGroup:="), vArg1.append(create_group)
        vArg1.append("STLFileUnit:="), vArg1.append("Auto")
        vArg1.append("MergeFacesAngle:="), vArg1.append(-1)
        vArg1.append("PointCoincidenceTol:="), vArg1.append(point_coicidence_tolerance)
        vArg1.append("CreateLightweightPart:="), vArg1.append(create_lightweigth_part)
        vArg1.append("ImportMaterialNames:="), vArg1.append(import_materials)
        vArg1.append("SeparateDisjointLumps:="), vArg1.append(separate_disjoints_lumped_object)
        vArg1.append("SourceFile:="), vArg1.append(filename)
        self.oeditor.Import(vArg1)
        if refresh_all_ids:
            self.refresh_all_ids()
        self.logger.info("Step file {} imported".format(filename))
        return True

    @pyaedt_function_handler()
    def import_spaceclaim_document(self, SCFile):
        """Import a SpaceClaim document.

        Parameters
        ----------
        SCFile :
            Full path and name of the SpaceClaim file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateUserDefinedModel
        """
        environlist = os.environ
        latestversion = ""
        for l in environlist:
            if "AWP_ROOT" in l:
                if l > latestversion:
                    latestversion = l
        if not latestversion:
            self.logger.error("SpaceClaim is not found.")
        else:
            scdm_path = os.path.join(os.environ[latestversion], "scdm")
        self.oeditor.CreateUserDefinedModel(
            [
                "NAME:UserDefinedModelParameters",
                [
                    "NAME:Definition",
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "GeometryFilePath",
                        "Value:=",
                        '"' + SCFile + '"',
                        "DataType:=",
                        "String",
                        "PropType2:=",
                        0,
                        "PropFlag2:=",
                        1,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "IsSpaceClaimLinkUDM",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                ],
                [
                    "NAME:Options",
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Solid Bodies",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Surface Bodies",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Parameters",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Parameter Key",
                        "Value:=",
                        '""',
                        "DataType:=",
                        "String",
                        "PropType2:=",
                        0,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Named Selections",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Rendering Attributes",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Material Assignment",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Import suppressed for physics objects",
                        "Value:=",
                        "0",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Explode Multi-Body Parts",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "SpaceClaim Installation Path",
                        "Value:=",
                        '"' + scdm_path + '"',
                        "DataType:=",
                        "String",
                        "PropType2:=",
                        0,
                        "PropFlag2:=",
                        8,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Smart CAD Update",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                ],
                ["NAME:GeometryParams"],
                "DllName:=",
                "SCIntegUDM",
                "Library:=",
                "installLib",
                "Version:=",
                "2.0",
                "ConnectionID:=",
                "",
            ]
        )
        self.refresh_all_ids()
        return True

    @pyaedt_function_handler()
    def modeler_variable(self, value):
        """Modeler variable.

        Parameters
        ----------
        value :


        Returns
        -------

        """
        if isinstance(value, str):
            return value
        else:
            return str(value) + self.model_units

    @pyaedt_function_handler()
    def break_spaceclaim_connection(self):  # TODO: Need to change this name. Don't use "break".
        """Disconnect from the running SpaceClaim instance.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.BreakUDMConnection
        """
        args = ["NAME:Selections", "Selections:=", "SpaceClaim1"]
        self.oeditor.BreakUDMConnection(args)
        return True

    @pyaedt_function_handler()
    def load_scdm_in_hfss(self, SpaceClaimFile):
        """Load a SpaceClaim file in HFSS.

        Parameters
        ----------
        SpaceClaimFile : str
            Full path and name of the SpaceClaim file.


        Returns
        -------
         bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateUserDefinedModel
        >>> oEditor.BreakUDMConnection
        """
        self.import_spaceclaim_document(SpaceClaimFile)
        self.break_spaceclaim_connection()
        return True

    @pyaedt_function_handler()
    def get_faces_from_materials(self, mats):
        """Select all outer faces given a list of materials.

        Parameters
        ----------
        mats : list
            List of materials to include in the search for outer
            faces.

        Returns
        -------
        list
            List of all outer faces of the specified materials.

        References
        ----------

        >>> oEditor.GetObjectsByMaterial
        >>> oEditor.GetFaceIDs
        """
        self.logger.info("Selecting outer faces.")

        sel = []
        objs = []
        if type(mats) is str:
            mats = [mats]
        for mat in mats:
            objs.extend(list(self.oeditor.GetObjectsByMaterial(mat.lower())))

            for i in objs:
                oFaceIDs = self.oeditor.GetFaceIDs(i)

                for face in oFaceIDs:
                    sel.append(int(face))
        return sel

    @pyaedt_function_handler()
    def scale(self, obj_list, x=2.0, y=2.0, z=2.0):
        """Scale a list of objects.

        Parameters
        ----------
        obj_list : list
            List of objects IDs or names.
        x : float, optional
            Scale factor for X.
        y : float, optional
            Scale factor for Y.
        z : float, optional
            Scale factor for Z.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Scale
        """
        selections = self.convert_to_selections(obj_list, True)
        arg1 = ["NAME:Selections", "Selections:=", ", ".join(selections), "NewPartsModelFlag:=", "Model"]
        arg2 = ["NAME:ScaleParameters", "ScaleX:=", str(x), "ScaleY:=", str(y), "ScaleZ:=", str(z)]
        self.oeditor.Scale(arg1, arg2)
        return True

    @pyaedt_function_handler()
    def select_allfaces_fromobjects(self, elements):
        """Select all outer faces given a list of objects.

        Parameters
        ----------
        elements : list
            List of objects to include in the search for outer faces.

        Returns
        -------
        List
            List of outer faces in the given list of objects.

        References
        ----------

        >>> oEditor.GetFaceIDs
        """
        self.logger.info("Selecting outer faces.")

        sel = []

        for i in elements:
            oFaceIDs = self.oeditor.GetFaceIDs(i)

            for face in oFaceIDs:
                sel.append(int(face))
        return sel

    @pyaedt_function_handler()
    def setunassigned_mats(self):
        """Find unassagned objects and set them to non-model.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SetPropertyValue
        """
        oObjects = list(self.oeditor.GetObjectsInGroup("Solids"))
        for obj in oObjects:
            pro = self.oeditor.GetPropertyValue("Geometry3DAttributeTab", obj, "Material")
            if pro == '""':
                self.oeditor.SetPropertyValue("Geometry3DAttributeTab", obj, "Model", False)
        return True

    @pyaedt_function_handler()
    def automatic_thicken_sheets(self, inputlist, value, internalExtr=True, internalvalue=1):
        """Create thickened sheets for a list of input faces.

        This method automatically checks the direction in which to thicken the sheets.

        Parameters
        ----------
        inputlist : list
            List of faces.
        value : float
            Value in millimeters to thicken the sheets.
        internalExtr : bool, optional
            Whether to extrude sheets internally. The default is ``True``.
        internalvalue : float, optional
            Value in millimeters to thicken the sheets internally (vgoing into the model).
            The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ThickenSheet
        """
        aedt_bounding_box = self.get_model_bounding_box()
        directions = {}
        inputlist = self.convert_to_selections(inputlist, True)
        for el in inputlist:
            objID = self.oeditor.GetFaceIDs(el)
            faceCenter = self.oeditor.GetFaceCenter(int(objID[0]))
            directionfound = False
            l = 10
            while not directionfound:
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", str(l) + "mm", "BothSides:=", False],
                )
                aedt_bounding_box2 = self.get_model_bounding_box()
                self._odesign.Undo()
                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "External"
                    directionfound = True
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", "-" + str(l) + "mm", "BothSides:=", False],
                )
                aedt_bounding_box2 = self.get_model_bounding_box()

                self._odesign.Undo()

                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "Internal"
                    directionfound = True
                else:
                    l = l + 10
        for el in inputlist:
            objID = self.oeditor.GetFaceIDs(el)
            faceCenter = self.oeditor.GetFaceCenter(int(objID[0]))
            if directions[el] == "Internal":
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", "-" + str(value) + "mm", "BothSides:=", False],
                )
            else:
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", str(value) + "mm", "BothSides:=", False],
                )
            if internalExtr:
                objID2 = self.oeditor.GetFaceIDs(el)
                for fid in objID2:
                    try:
                        faceCenter2 = self.oeditor.GetFaceCenter(int(fid))
                        if faceCenter2 == faceCenter:
                            self.oeditor.MoveFaces(
                                ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                                [
                                    "NAME:Parameters",
                                    [
                                        "NAME:MoveFacesParameters",
                                        "MoveAlongNormalFlag:=",
                                        True,
                                        "OffsetDistance:=",
                                        str(internalvalue) + "mm",
                                        "MoveVectorX:=",
                                        "0mm",
                                        "MoveVectorY:=",
                                        "0mm",
                                        "MoveVectorZ:=",
                                        "0mm",
                                        "FacesToMove:=",
                                        [int(fid)],
                                    ],
                                ],
                            )
                    except:
                        self.logger.info("done")
                        # self.modeler_oproject.ClearMessages()
        return True

    @pyaedt_function_handler()
    def move_face(self, faces, offset=1.0):
        """Move an input face or a list of input faces of a specific object.

        This method moves a face or a list of faces which belong to the same solid.

        Parameters
        ----------
        faces : list
            List of Face ID or List of :class:`pyaedt.modeler.Object3d.FacePrimitive` object or mixed.
        offset : float, optional
             Offset to apply in model units. The default is ``1.0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.MoveFaces

        """
        face_selection = self.convert_to_selections(faces, True)
        selection = {}
        for f in face_selection:
            if self.oeditor.GetObjectNameByFaceID(f) in selection:
                selection[self.oeditor.GetObjectNameByFaceID(f)].append(f)
            else:
                selection[self.oeditor.GetObjectNameByFaceID(f)] = [f]

        arg1 = [
            "NAME:Selections",
            "Selections:=",
            self.convert_to_selections(list(selection.keys()), False),
            "NewPartsModelFlag:=",
            "Model",
        ]
        arg2 = ["NAME:Parameters"]
        for el in list(selection.keys()):
            arg2.append(
                [
                    "NAME:MoveFacesParameters",
                    "MoveAlongNormalFlag:=",
                    True,
                    "OffsetDistance:=",
                    str(offset) + self.model_units,
                    "MoveVectorX:=",
                    "0mm",
                    "MoveVectorY:=",
                    "0mm",
                    "MoveVectorZ:=",
                    "0mm",
                    "FacesToMove:=",
                    selection[el],
                ]
            )
        self.oeditor.MoveFaces(arg1, arg2)
        return True

    @pyaedt_function_handler()
    def move_edge(self, edges, offset=1.0):
        """Move an input edge or a list of input edges of a specific object.

        This method moves an edge or a list of edges which belong to the same solid.

        Parameters
        ----------
        edges : list
            List of Edge ID or List of :class:`pyaedt.modeler.Object3d.EdgePrimitive` object or mixed.
        offset : float, optional
             Offset to apply in model units. The default is ``1.0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.MoveEdges

        """
        edge_selection = self.convert_to_selections(edges, True)
        selection = {}
        for f in edge_selection:
            if self.oeditor.GetObjectNameByEdgeID(f) in selection:
                selection[self.oeditor.GetObjectNameByEdgeID(f)].append(f)
            else:
                selection[self.oeditor.GetObjectNameByEdgeID(f)] = [f]

        arg1 = [
            "NAME:Selections",
            "Selections:=",
            self.convert_to_selections(list(selection.keys()), False),
            "NewPartsModelFlag:=",
            "Model",
        ]
        arg2 = ["NAME:Parameters"]
        for el in list(selection.keys()):
            arg2.append(
                [
                    "NAME:MoveEdgesParameters",
                    "MoveAlongNormalFlag:=",
                    True,
                    "OffsetDistance:=",
                    str(offset) + self.model_units,
                    "MoveVectorX:=",
                    "0mm",
                    "MoveVectorY:=",
                    "0mm",
                    "MoveVectorZ:=",
                    "0mm",
                    "EdgesToMove:=",
                    selection[el],
                ]
            )
        self.oeditor.MoveEdges(arg1, arg2)
        return True

    @pyaedt_function_handler()
    def create_group(self, objects=None, components=None, groups=None, group_name=None):
        """Group objects or groups into one group.

        At least one between ``objects``, ``components``, ``groups`` has to be defined.

        Parameters
        ----------
        objects : list, optional
            List of objects. The default is ``None``, in which case a group
            with all objects is created.
        components : list, optional
            List of 3d components to group. The default is ``None``.
        groups : list, optional
            List of groups. The default is ``None``.
        group_name : str, optional
            Name of the new group. The default is ``None``.
            It is not possible to choose the name but a name is
            assigned automatically.

        Returns
        -------
        str
           Name assigned to the new group.

        References
        ----------

        >>> oEditor.CreateGroup
        """
        if components is None and groups is None and objects is None:
            raise AttributeError("At least one between ``objects``, ``components``, ``groups`` has to be defined.")

        all_objects = self.object_names
        if objects:
            object_selection = self.convert_to_selections(objects, return_list=False)
        else:
            object_selection = ""
        if groups:
            group_selection = self.convert_to_selections(groups, return_list=False)
        else:
            group_selection = ""
        if components:
            component_selection = self.convert_to_selections(components, return_list=False)
        else:
            component_selection = ""

        arg = [
            "NAME:GroupParameter",
            "ParentGroupID:=",
            "Model",
            "Parts:=",
            object_selection,
            "SubmodelInstances:=",
            component_selection,
            "Groups:=",
            group_selection,
        ]
        assigned_name = self.oeditor.CreateGroup(arg)
        if group_name and group_name not in all_objects:
            self.oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Attributes",
                        ["NAME:PropServers", assigned_name],
                        ["NAME:ChangedProps", ["NAME:Name", "Value:=", group_name]],
                    ],
                ]
            )
            return group_name
        else:
            return assigned_name

    @pyaedt_function_handler()
    def ungroup(self, groups):
        """Ungroup one or more groups.

        Parameters
        ----------
        groups : list
            List of group names.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Ungroup
        """
        group_list = self.convert_to_selections(groups, return_list=True)
        arg = ["Groups:=", group_list]
        self.oeditor.Ungroup(arg)
        return True

    @pyaedt_function_handler()
    def flatten_assembly(self):
        """Flatten the assembly, removing all group trees.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.FlattenGroup
        """
        self.oeditor.FlattenGroup(["Groups:=", ["Model"]])
        return True

    @pyaedt_function_handler()
    def wrap_sheet(self, sheet_name, object_name, imprinted=False):
        """Execute the sheet wrapping around an object.
        If wrapping produces an unclassified operation it will be reverted.

        Parameters
        ----------
        sheet_name : str, :class:`pyaedt.modeler.Object3d.Object3d`
            Sheet name or sheet object.
        object_name : str, :class:`pyaedt.modeler.Object3d.Object3d`
            Object name or solid object.
        imprinted : bool, optional
            Either if imprint or not over the sheet. Default is ``False``.

        Returns
        -------
        bool
            Command execution status.
        """
        sheet_name = self.convert_to_selections(sheet_name, False)
        object_name = self.convert_to_selections(object_name, False)

        if sheet_name not in self.sheet_names:
            self.logger.error("{} is not a valid sheet.".format(sheet_name))
            return False
        if object_name not in self.solid_names:
            self.logger.error("{} is not a valid solid body.".format(object_name))
            return False
        unclassified = [i for i in self.unclassified_objects]
        self.oeditor.WrapSheet(
            ["NAME:Selections", "Selections:=", "{},{}".format(sheet_name, object_name)],
            ["NAME:WrapSheetParameters", "Imprinted:=", imprinted],
        )
        is_unclassified = [i for i in self.unclassified_objects if i not in unclassified]
        if is_unclassified:
            self.logger.error("Failed to Wrap sheet. Reverting to original objects.")
            self._odesign.Undo()
            return False
        if imprinted:
            self.cleanup_objects()
        return True

    @pyaedt_function_handler()
    def heal_objects(
        self,
        input_objects_list,
        auto_heal=True,
        tolerant_stitch=True,
        simplify_geometry=True,
        tighten_gaps=True,
        heal_to_solid=False,
        stop_after_first_stitch_error=False,
        max_stitch_tolerance=0.001,
        explode_and_stitch=True,
        geometry_simplification_tolerance=1,
        maximum_generated_radius=1,
        simplify_type=0,
        tighten_gaps_width=0.00001,
        remove_silver_faces=True,
        remove_small_edges=True,
        remove_small_faces=True,
        silver_face_tolerance=1,
        small_edge_tolerance=1,
        small_face_area_tolerance=1,
        bounding_box_scale_factor=0,
        remove_holes=True,
        remove_chamfers=True,
        remove_blends=True,
        hole_radius_tolerance=1,
        chamfer_width_tolerance=1,
        blend_radius_tolerance=1,
        allowable_surface_area_change=5,
        allowable_volume_change=5,
    ):
        """Repair invalid geometry entities for the selected objects within the specified tolerance settings.

        Parameters
        ----------
        input_objects_list : str
            List of object names to analyze.
        auto_heal : bool, optional
            Auto heal option. Default value is ``True``.
        tolerant_stitch : bool, optional
            Tolerant stitch for manual healing. The default is ``True``.
        simplify_geometry : bool, optional
            Simplify geometry for manual healing. The default is ``True``.
        tighten_gaps : bool, optional
            Tighten gaps for manual healing. The default is ``True``.
        heal_to_solid : bool, optional
            Heal to solid for manual healing. The default is ``False``.
        stop_after_first_stitch_error : bool, optional
            Stop after first stitch error for manual healing. The default is ``False``.
        max_stitch_tolerance : float, str, optional
            Max stitch tolerance for manual healing. The default is ``0.001``.
        explode_and_stitch : bool, optional
            Explode and stitch for manual healing. The default is ``True``.
        geometry_simplification_tolerance : float, str, optional
            Geometry simplification tolerance for manual healing in mm. The default is ``1``.
        maximum_generated_radius : float, str, optional
            Maximum generated radius for manual healing in mm. The default is ``1``.
        simplify_type : int, optional
            Simplify type for manual healing. The default is ``0`` which refers to ``Curves``.
            Other available values are ``1`` for ``Surfaces`` and ``2`` for ``Both``.
        tighten_gaps_width : float, str, optional
            Tighten gaps width for manual healing in mm. The default is ``0.00001``.
        remove_silver_faces : bool, optional
            Remove silver faces for manual healing. The default is ``True``.
        remove_small_edges : bool, optional
            Remove small edges faces for manual healing. The default is ``True``.
        remove_small_faces : bool, optional
            Remove small faces for manual healing. The default is ``True``.
        silver_face_tolerance : float, str, optional
            Silver face tolerance for manual healing in mm. The default is ``1``.
        small_edge_tolerance : float, str, optional
            Silver face tolerance for manual healing in mm. The default is ``1``.
        small_face_area_tolerance : float, str, optional
            Silver face tolerance for manual healing in mm^2. The default is ``1``.
        bounding_box_scale_factor : int, optional
            Bounding box scaling factor for manual healing. The default is ``0``.
        remove_holes : bool, optional
            Remove holes for manual healing. The default is ``True``.
        remove_chamfers : bool, optional
            Remove chamfers for manual healing. The default is``True``.
        remove_blends : bool, optional
            Remove blends for manual healing. The default is ``True``.
        hole_radius_tolerance : float, str, optional
            Hole radius tolerance for manual healing in mm. The default is ``1``.
        chamfer_width_tolerance : float, str, optional
            Chamfer width tolerance for manual healing in mm. The default is ``1``.
        blend_radius_tolerance : float, str, optional
            Blend radius tolerance for manual healing in mm. The default is ``1``.
        allowable_surface_area_change : float, str, optional
            Allowable surface area for manual healing in mm. The default is ``1``.
        allowable_volume_change : float, str, optional
            Allowable volume change for manual healing in mm. The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not input_objects_list:
            self.logger.error("Provide an object name or a list of object names as a string.")
            return False
        elif not isinstance(input_objects_list, str):
            self.logger.error("Provide an object name or a list of object names as a string.")
            return False
        elif "," in input_objects_list:
            input_objects_list = input_objects_list.strip()
            if ", " in input_objects_list:
                input_objects_list_split = input_objects_list.split(", ")
            else:
                input_objects_list_split = input_objects_list.split(",")
            for obj in input_objects_list_split:
                if obj not in self.object_names:
                    self.logger.error("Provide an object name or a list of object names that exists in current design.")
                    return False
            objects_selection = ",".join(input_objects_list_split)
        else:
            objects_selection = input_objects_list

        if simplify_type not in [0, 1, 2]:
            self.logger.error("Invalid simplify type.")
            return False

        selections_args = ["NAME:Selections", "Selections:=", objects_selection, "NewPartsModelFlag:=", "Model"]
        healing_parameters = [
            "NAME:ObjectHealingParameters",
            "Version:=",
            1,
            "AutoHeal:=",
            auto_heal,
            "TolerantStitch:=",
            tolerant_stitch,
            "SimplifyGeom:=",
            simplify_geometry,
            "TightenGaps:=",
            tighten_gaps,
            "HealToSolid:=",
            heal_to_solid,
            "StopAfterFirstStitchError:=",
            stop_after_first_stitch_error,
            "MaxStitchTol:=",
            max_stitch_tolerance,
            "ExplodeAndStitch:=",
            explode_and_stitch,
            "GeomSimplificationTol:=",
            geometry_simplification_tolerance,
            "MaximumGeneratedRadiusForSimplification:=",
            maximum_generated_radius,
            "SimplifyType:=",
            simplify_type,
            "TightenGapsWidth:=",
            tighten_gaps_width,
            "RemoveSliverFaces:=",
            remove_silver_faces,
            "RemoveSmallEdges:=",
            remove_small_edges,
            "RemoveSmallFaces:=",
            remove_small_faces,
            "SliverFaceTol:=",
            silver_face_tolerance,
            "SmallEdgeTol:=",
            small_edge_tolerance,
            "SmallFaceAreaTol:=",
            small_face_area_tolerance,
            "SpikeTol:=",
            -1,
            "GashWidthBound:=",
            -1,
            "GashAspectBound:=",
            -1,
            "BoundingBoxScaleFactor:=",
            bounding_box_scale_factor,
            "RemoveHoles:=",
            remove_holes,
            "RemoveChamfers:=",
            remove_chamfers,
            "RemoveBlends:=",
            remove_blends,
            "HoleRadiusTol:=",
            hole_radius_tolerance,
            "ChamferWidthTol:=",
            chamfer_width_tolerance,
            "BlendRadiusTol:=",
            blend_radius_tolerance,
            "AllowableSurfaceAreaChange:=",
            allowable_surface_area_change,
            "AllowableVolumeChange:=",
            allowable_volume_change,
        ]
        self.oeditor.HealObject(selections_args, healing_parameters)
        return True

    @pyaedt_function_handler()
    def simplify_objects(
        self,
        input_objects_list,
        simplify_type="Polygon Fit",
        extrusion_axis="Auto",
        clean_up=True,
        allow_splitting=True,
        separate_bodies=True,
        clone_body=True,
        generate_primitive_history=False,
        interior_points_on_arc=5,
        length_threshold_percentage=25,
        create_group_for_new_objects=False,
    ):
        """Simplify command to converts complex objects into simpler primitives which are easy to mesh and solve.

        Parameters
        ----------
        input_objects_list : str
            List of object names to simplify.
        simplify_type : str, optional
            Simplify type. The default is ``"Polygon Fit"``. Options are
            ``"Bounding Box"``, ``"Polygon Fit"``, and ``"Primitive Fit"`.
        extrusion_axis : str, optional
            Extrusion axis. The default is ``"Auto"``.
            Options are ``"Auto"``, ``"X"``, ``"Y"``, and ``"Z"``.
        clean_up : bool, optional
            Whether to clean up. The default is ``True``.
        allow_splitting : bool, optional
            Whether to allow splitting. The default is ``True``.
        separate_bodies : bool, optional
            Whether to separate bodies. The default is ``True``.
        clone_body : bool, optional
            Whether to clone the body. The default is ``True``.
        generate_primitive_history : bool, optional
            Whether to generate primitive history. The default is ``False``.
            If ``True``, the history for the selected objects is purged.
            ```
        interior_points_on_arc : float, optional
            Number points on curve. The default is ``5``.
        length_threshold_percentage : float, optional
            Length threshold percentage. The default is ``25``.
        create_group_for_new_objects : bool, optional
            Create group for new objects. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not input_objects_list:
            self.logger.error("Provide an object name or a list of object names as a string.")
            return False
        elif not isinstance(input_objects_list, str):
            self.logger.error("Provide an object name or a list of object names as a string.")
            return False
        elif "," in input_objects_list:
            input_objects_list = input_objects_list.strip()
            if ", " in input_objects_list:
                input_objects_list_split = input_objects_list.split(", ")
            else:
                input_objects_list_split = input_objects_list.split(",")
            for obj in input_objects_list_split:
                if obj not in self.object_names:
                    self.logger.error("Provide an object name or a list of object names that exists in current design.")
                    return False
            objects_selection = ",".join(input_objects_list_split)
        else:
            objects_selection = input_objects_list

        if simplify_type not in ["Polygon Fit", "Primitive Fit", "Bounding Box"]:
            self.logger.error("Invalid simplify type.")
            return False

        if extrusion_axis not in ["Auto", "X", "Y", "Z"]:
            self.logger.error("Invalid extrusion axis.")
            return False

        selections_args = ["NAME:Selections", "Selections:=", objects_selection, "NewPartsModelFlag:=", "Model"]
        simplify_parameters = [
            "NAME:SimplifyParameters",
            "Type:=",
            simplify_type,
            "ExtrusionAxis:=",
            extrusion_axis,
            "Cleanup:=",
            clean_up,
            "Splitting:=",
            allow_splitting,
            "SeparateBodies:=",
            separate_bodies,
            "CloneBody:=",
            clone_body,
            "Generate Primitive History:=",
            generate_primitive_history,
            "NumberPointsCurve:=",
            interior_points_on_arc,
            "LengthThresholdCurve:=",
            length_threshold_percentage,
        ]
        groups_for_new_object = ["CreateGroupsForNewObjects:=", create_group_for_new_objects]

        try:
            self.oeditor.Simplify(selections_args, simplify_parameters, groups_for_new_object)
            return True
        except:
            self.logger.error("Simplify objects failed.")
            return False

    @pyaedt_function_handler
    def get_face_by_id(self, id):
        """Get the face object given its ID.

        Parameters
        ----------
        id : int
            ID of the face to retrieve.

        Returns
        -------
        modeler.cad.elements3d.FacePrimitive
            Face object.

        """
        obj = [o for o in self.object_list for face in o.faces if face.id == id]
        if obj:
            face_obj = [face for face in obj[0].faces if face.id == id][0]
            return face_obj
        else:
            return False

    @pyaedt_function_handler()
    def create_point(self, position, name=None, color="(143 175 143)"):
        """Create a point.

        Parameters
        ----------
        position : list
            List of ``[x, y, z]`` coordinates. Note, The list can be empty or contain less than 3 elements.
        name : str, optional
            Name of the point. The default is ``None``, in which case the
            default name is assigned.
        color : str, optional
            String exposing 3 int values such as "(value1 value2 value3)". Default value is ``"(143 175 143)"``.

        Returns
        -------
        :class:`pyaedt.modeler.elements3d.Point`
            Point object.

        References
        ----------

        >>> oEditor.CreateBox

        Examples
        --------

        >>> from pyaedt import hfss
        >>> hfss = Hfss()
        >>> point_object = hfss.modeler.primivites.create_point([0,0,0], name="mypoint")

        """
        x_position, y_position, z_position = self._pos_with_arg(position)

        if not name:
            unique_name = "".join(random.sample(string.ascii_uppercase + string.digits, 6))
            name = "NewPoint_" + unique_name

        parameters = ["NAME:PointParameters"]
        parameters.append("PointX:="), parameters.append(x_position)
        parameters.append("PointY:="), parameters.append(y_position)
        parameters.append("PointZ:="), parameters.append(z_position)

        attributes = ["NAME:Attributes"]
        attributes.append("Name:="), attributes.append(name)
        attributes.append("Color:="), attributes.append(color)

        self.oeditor.CreatePoint(parameters, attributes)
        self._refresh_points()
        return self._create_object(name)

    @pyaedt_function_handler()
    def create_plane(
        self,
        name=None,
        plane_base_x="0mm",
        plane_base_y="0mm",
        plane_base_z="0mm",
        plane_normal_x="0mm",
        plane_normal_y="0mm",
        plane_normal_z="0mm",
        color="(143 175 143)",
    ):
        """Create a plane.

        Parameters
        ----------
        name : str, optional
            Name of the plane. The default is ``None``, in which case the
            default name is assigned.
        plane_base_x : str
            X coordinate of the plane base. The default value is ``"0mm"``.
        plane_base_y : str
            Y coordinate of the plane base. The default value is ``"0mm"``.
        plane_base_z : str
            Z coordinate of the plane base. The default value is ``"0mm"``.
        plane_normal_x : str
            X coordinate of the normal plane. The default value is ``"0mm"``.
        plane_normal_y : str
            Y coordinate of the normal plane. The default value is ``"0mm"``.
        plane_normal_z : str
            Z coordinate of the normal plane. The default value is ``"0mm"``.
        color : str, optional
            String exposing the three integer values for the color of the plane. The
            default value is ``"(143 175 143)"``.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives.Plane`
            Planes object.

        References
        ----------

        >>> oEditor.CreateBox

        Examples
        --------
        Create a new plane.
        >>> from pyaedt import hfss
        >>> hfss = Hfss()
        >>> plane_object = hfss.modeler.primivites.create_plane(plane_base_y="-0.8mm", plane_normal_x="-0.7mm",
        ...                name="myplane")

        """

        if not name:
            unique_name = "".join(random.sample(string.ascii_uppercase + string.digits, 6))
            name = "Plane_" + unique_name

        parameters = ["NAME:PlaneParameters"]
        parameters.append("PlaneBaseX:="), parameters.append(plane_base_x)
        parameters.append("PlaneBaseY:="), parameters.append(plane_base_y)
        parameters.append("PlaneBaseZ:="), parameters.append(plane_base_z)
        parameters.append("PlaneNormalX:="), parameters.append(plane_normal_x)
        parameters.append("PlaneNormalY:="), parameters.append(plane_normal_y)
        parameters.append("PlaneNormalZ:="), parameters.append(plane_normal_z)

        attributes = ["NAME:Attributes"]
        attributes.append("Name:="), attributes.append(name)
        attributes.append("Color:="), attributes.append(color)

        self.oeditor.CreateCutplane(parameters, attributes)
        # self._refresh_planes()
        self.planes[name] = None
        plane = self._create_object(name)
        self.planes[name] = plane
        return plane

    @pyaedt_function_handler()
    def _change_component_property(self, vPropChange, names_list):
        names = self.convert_to_selections(names_list, True)
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        vPropServers = ["NAME:PropServers"]
        for el in names:
            vPropServers.append(el)
        vGeo3d = ["NAME:General", vPropServers, vChangedProps]
        vOut = ["NAME:AllTabs", vGeo3d]
        self.oeditor.ChangeProperty(vOut)
        return True

    @pyaedt_function_handler()
    def _change_geometry_property(self, vPropChange, names_list):
        names = self.convert_to_selections(names_list, True)
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        vPropServers = ["NAME:PropServers"]
        for el in names:
            vPropServers.append(el)
        vGeo3d = ["NAME:Geometry3DAttributeTab", vPropServers, vChangedProps]
        vOut = ["NAME:AllTabs", vGeo3d]
        self.oeditor.ChangeProperty(vOut)
        if "NAME:Name" in vPropChange:
            self.cleanup_objects()
        return True

    @pyaedt_function_handler()
    def _change_point_property(self, vPropChange, names_list):
        names = self.convert_to_selections(names_list, True)
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        vPropServers = ["NAME:PropServers"]
        for el in names:
            vPropServers.append(el)
        vGeo3d = ["NAME:Geometry3DPointTab", vPropServers, vChangedProps]
        vOut = ["NAME:AllTabs", vGeo3d]
        self.oeditor.ChangeProperty(vOut)
        if "NAME:Name" in vPropChange:
            self.cleanup_objects()
        return True

    @pyaedt_function_handler()
    def _change_plane_property(self, vPropChange, names_list):
        names = self.convert_to_selections(names_list, True)
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        vPropServers = ["NAME:PropServers"]
        for el in names:
            vPropServers.append(el)
        vGeo3d = ["NAME:Geometry3DPlaneTab", vPropServers, vChangedProps]
        vOut = ["NAME:AllTabs", vGeo3d]
        self.oeditor.ChangeProperty(vOut)
        if "NAME:Name" in vPropChange:
            self.cleanup_objects()
        return True

    @pyaedt_function_handler()
    def update_object(self, obj):
        """Update any :class:`pyaedt.modeler.Object3d.Object3d` derivatives
        that have potentially been modified by a modeler operation.

        Parameters
        ----------
        obj : int, str, or :class:`pyaedt.modeler.Object3d.Object3d`
            Object to be updated after a modeler operation.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
           Updated 3D object.

        """
        o = self._resolve_object(obj)
        name = o.name

        del self.objects[self._object_names_to_ids[name]]
        del self._object_names_to_ids[name]
        o = self._create_object(name)
        return o

    @pyaedt_function_handler()
    def value_in_object_units(self, value):
        """Convert one or more strings for numerical lengths to floating point values.

        Parameters
        ----------
        value : str or list of str
            One or more strings for numerical lengths. For example, ``"10mm"``
            or ``["10mm", "12mm", "14mm"]``. When a list is given, the entire
            list is converted.

        Returns
        -------
        List of floats
            Defined in model units :attr:`pyaedt.modeler.model_units`.

        """
        # Convert to a list if a scalar is presented

        scalar = False
        if not isinstance(value, list):
            value = [value]
            scalar = True

        numeric_list = []
        for element in value:
            if is_number(element):
                num_val = element
            elif isinstance(element, str):
                # element is an existing variable
                si_value = self._app.evaluate_expression(element)
                v = Variable("{}meter".format(si_value))
                v.rescale_to(self.model_units)
                num_val = v.numeric_value
            else:
                raise TypeError("Inputs to value_in_object_units must be strings or numbers.")

            numeric_list.append(num_val)

        if scalar:
            return numeric_list[0]
        else:
            return numeric_list

    @pyaedt_function_handler()
    def does_object_exists(self, obj_to_check):
        """Check to see if an object exists.

        Parameters
        ----------
        obj_to_check : str, int
            Object name or object ID.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if isinstance(obj_to_check, int) and obj_to_check in self.objects:
            return True
        elif obj_to_check in self.objects_by_name:
            return True
        else:
            return False

    @pyaedt_function_handler()
    def create_region(self, pad_percent=300, is_percentage=True):
        """Create an air region.

        Parameters
        ----------
        pad_percent : float, str, list of floats or list of str, optional
            Same padding is applied if not a list. The default is ``300``.
            If a list of floats or str, interpret as adding for ``["+X", "+Y", "+Z", "-X", "-Y", "-Z"]``.
        is_percentage : bool, optional
            Region definition in percentage or absolute value. The default is `True``.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            Region object.

        References
        ----------

        >>> oEditor.CreateRegion
        """
        return self._create_region(pad_percent=pad_percent, is_percentage=is_percentage)

    @pyaedt_function_handler()
    def _create_region(self, pad_percent=300, is_percentage=True):
        """Create an air region.

        Parameters
        ----------
        pad_percent : float, str, list of floats or list of str, optional
            Same padding is applied if not a list. The default is ``300``.
            If a list of floats or str, interpret as adding for ``["+X", "+Y", "+Z", "-X", "-Y", "-Z"]``.
        is_percentage : bool, optional
            Region definition in percentage or absolute value. The default is `True``.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            Region object.

        References
        ----------

        >>> oEditor.CreateRegion
        """
        if "Region" in self.object_names:
            return None
        if not isinstance(pad_percent, list):
            pad_percent = [pad_percent] * 6

        arg = ["NAME:RegionParameters"]

        # TODO: Can the order be updated to match the UI?
        p = ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]
        i = 0
        for pval in p:
            region_type = "Percentage Offset"
            if not is_percentage:
                region_type = "Absolute Offset"
            pvalstr = str(pval) + "PaddingType:="
            qvalstr = str(pval) + "Padding:="
            arg.append(pvalstr)
            arg.append(region_type)
            arg.append(qvalstr)
            if isinstance(pad_percent[i], str):
                units = decompose_variable_value(pad_percent[i])[1]
                if not units and pad_percent[i].isnumeric():
                    if not is_percentage:
                        units = self.model_units
                        pad_percent[i] += units
                elif is_percentage:
                    self.logger.error("Percentage input must not have units")
                    return False
            elif not is_percentage:
                units = self.model_units
                pad_percent[i] = str(pad_percent[i])
                pad_percent[i] += units
            arg.append(str(pad_percent[i]))
            i += 1
        arg2 = [
            "NAME:Attributes",
            "Name:=",
            "Region",
            "Flags:=",
            "Wireframe#",
            "Color:=",
            "(143 175 143)",
            "Transparency:=",
            0.75,
            "PartCoordinateSystem:=",
            "Global",
            "UDMId:=",
            "",
            "MaterialValue:=",
            '"air"',
            "SurfaceMaterialValue:=",
            '""',
            "SolveInside:=",
            True,
            "IsMaterialEditable:=",
            True,
            "UseMaterialAppearance:=",
            False,
            "IsLightweight:=",
            False,
        ]
        self.oeditor.CreateRegion(arg, arg2)
        return self._create_object("Region")

    @pyaedt_function_handler()
    def create_object_from_edge(self, edge, non_model=False):
        """Create an object from one or multiple edges.

        Parameters
        ----------
        edge : list, int or :class:`pyaedt.modeler.Object3d.FacePrimitive`
            Face ID or :class:`pyaedt.modeler.Object3d.FacePrimitive` object or Face List.
        non_model : bool, optional
            Either if create the new object as model or non-model. The default is `False`.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d` or list of :class:`pyaedt.modeler.Object3d.Object3d`
            3D objects.

        References
        ----------

        >>> oEditor.CreateObjectFromFaces
        """
        edge_ids = self.convert_to_selections(edge, True)
        objs = OrderedDict()
        for edge_id in edge_ids:
            obj_name = self._find_object_from_edge_id(edge_id)
            if obj_name not in objs:
                objs[obj_name] = [edge_id]
            else:
                objs[obj_name].append(edge_id)

        if objs:
            varg1 = ["NAME:Selections"]
            varg1.append("Selections:="), varg1.append(self.convert_to_selections(list(objs.keys()), False))
            varg1.append("NewPartsModelFlag:="), varg1.append("Model" if not non_model else "NonModel")
            varg3 = ["NAME:Parameters"]
            for val in list(objs.values()):
                varg2 = ["NAME:BodyFromEdgeToParameters"]
                varg2.append("Edges:="), varg2.append(val)
                varg3.append(varg2)
            new_object_name = self.oeditor.CreateObjectFromEdges(varg1, varg3, ["CreateGroupsForNewObjects:=", False])
            new_objects = []
            for new_object in new_object_name:
                new_objects.append(self._create_object(new_object))
            if len(new_objects) > 1:
                return new_objects
            else:
                return new_objects[0]
        self.logger.error("Error creating object from edges.")
        return

    @pyaedt_function_handler()
    def create_object_from_face(self, face, non_model=False):
        """Create an object from one or multiple face.

        Parameters
        ----------
        face : list, int or :class:`pyaedt.modeler.Object3d.FacePrimitive`
            Face ID or :class:`pyaedt.modeler.Object3d.FacePrimitive` object or Face List.
        non_model : bool, optional
            Either if create the new object as model or non-model. Default is `False`.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d` or list of :class:`pyaedt.modeler.Object3d.Object3d`
            3D objects.

        References
        ----------

        >>> oEditor.CreateObjectFromFaces
        """
        face_ids = self.convert_to_selections(face, True)
        objs = OrderedDict()
        for face_id in face_ids:
            obj_name = self._find_object_from_face_id(face_id)
            if obj_name not in objs:
                objs[obj_name] = [face_id]
            else:
                objs[obj_name].append(face_id)

        if objs:
            varg1 = ["NAME:Selections"]
            varg1.append("Selections:="), varg1.append(self.convert_to_selections(list(objs.keys()), False))
            varg1.append("NewPartsModelFlag:="), varg1.append("Model" if not non_model else "NonModel")
            varg3 = ["NAME:Parameters"]
            for val in list(objs.values()):
                varg2 = ["NAME:BodyFromFaceToParameters"]
                varg2.append("FacesToDetach:="), varg2.append(val)
                varg3.append(varg2)
            new_object_name = self.oeditor.CreateObjectFromFaces(varg1, varg3, ["CreateGroupsForNewObjects:=", False])
            new_objects = []
            for new_object in new_object_name:
                new_objects.append(self._create_object(new_object))
            if len(new_objects) > 1:
                return new_objects
            else:
                return new_objects[0]
        self.logger.error("Error creating object from faces.")
        return

    @pyaedt_function_handler()
    def polyline_segment(self, type, num_seg=0, num_points=0, arc_angle=0, arc_center=None, arc_plane=None):
        """New segment of a polyline.

        Parameters
        ----------
        type : str
            Type of the object. Choices are ``"Line"``, ``"Arc"``, ``"Spline"``,
            and ``"AngularArc"``.
        num_seg : int, optional
            Number of segments for the types ``"Arc"``, ``"Spline"``, and
            ``"AngularArc"``.  The default is ``0``. For the type
            ``Line``, this parameter is ignored.
        num_points : int, optional
            Number of control points for the type ``Spline``. For other
            types, this parameter
            is defined automatically.
        arc_angle : float or str, optional
            Sweep angle in radians or a valid value string. For example,
            ``"35deg"`` or ``"Specific
            to type AngularArc"``.
        arc_center : list or str, optional
            List of values in model units or a valid value string. For
            example, a list of ``[x, y, z]`` coordinates or ``"Specific to
            type AngularArc"``.
        arc_plane : str, int optional
            Plane in which the arc sweep is performed in the active
            coordinate system ``"XY"``, ``"YZ"`` or ``"ZX"``. The default is
            ``None``, in which case the plane is determined automatically
            by the first coordinate for which the starting point and
            center point have the same value.

        Returns
        -------
        :class:`pyaedt.modeler.polylines.PolylineSegment`
        """
        return PolylineSegment(
            segment_type=type,
            num_seg=num_seg,
            num_points=num_points,
            arc_angle=arc_angle,
            arc_center=arc_center,
            arc_plane=arc_plane,
        )

    @pyaedt_function_handler()
    def create_polyline(
        self,
        position_list,
        segment_type=None,
        cover_surface=False,
        close_surface=False,
        name=None,
        matname=None,
        xsection_type=None,
        xsection_orient=None,
        xsection_width=1,
        xsection_topwidth=1,
        xsection_height=1,
        xsection_num_seg=0,
        xsection_bend_type=None,
        non_model=False,
    ):
        """Draw a polyline object in the 3D modeler.

        This method retrieves the
        :class:`pyaedt.modeler.Primitives.Polyline` object, which has
        additional methods for manipulating the polyline. For example,
        you can use
        :func:`pyaedt.modeler.Primitives.Polyline.insert_segment` to
        insert a segment or
        :attr:`pyaedt.modeler.Primitives.Polyline.id` to retrieve the
        ID of the polyline object.

        Parameters
        ----------
        position_list : list
            Array of positions of each point of the polyline.  A
            position is a list of 2D or 3D coordinates. Position
            coordinate values can be numbers or valid AEDT string
            expressions. For example, ``[0, 1, 2]``, ``["0mm", "5mm",
            "1mm"]``, or ``["x1", "y1", "z1"]``.
        segment_type : str or PolylineSegment or list, optional
            The default behavior is to connect all points as
            ``"Line"`` segments. The default is ``None``.
            Use a ``"PolylineSegment"``, for ``"Line"``, ``"Arc"``, ``"Spline"``,
            or ``"AngularArc"``.
            A list of segment types (str or :class:`pyaedt.modeler.Primitives.PolylineSegment`) is
            valid for a compound polyline.
        cover_surface : bool, optional
            The default is ``False``.
        close_surface : bool, optional
            The default is ``False``, which automatically joins the
            starting and ending points.
        name : str, optional
            Name of the polyline. The default is ``None``.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the
            default material is assigned.
        xsection_type : str, optional
            Type of the cross-section. Options are ``"Line"``, ``"Circle"``,
            ``"Rectangle"``, and ``"Isosceles Trapezoid"``. The default is ``None``.
        xsection_orient : str, optional
            Direction of the normal vector to the width of the cross-section.
            Options are ``"X"``, ``"Y"``, ``"Z"``, and ``"Auto"``. The default is
            ``None``, which sets the direction to ``"Auto"``.
        xsection_width : float or str, optional
            Width or diameter of the cross-section for all  types. The
            default is ``1``.
        xsection_topwidth : float or str, optional
            Top width of the cross-section for type ``"Isosceles Trapezoid"`` only.
            The default is ``1``.
        xsection_height : float or str
            Height of the cross-section for type ``"Rectangle"`` or ``"Isosceles
            Trapezoid"`` only. The default is ``1``.
        xsection_num_seg : int, optional
            Number of segments in the cross-section surface for type ``"Circle"``,
            ``"Rectangle"``, or ``"Isosceles Trapezoid"``. The default is ``0``. The
            value must be ``0`` or greater than ``2``.
        xsection_bend_type : str, optional
            Type of the bend for the cross-section. The default is
            ``None``, in which case the bend type is set to
            ``"Corner"``. For the type ``"Circle"``, the bend type
            should be set to ``"Curved"``.
        non_model : bool, optional
            Either if the polyline will be created as model or unmodel object.

        Returns
        -------
        pyaedt.modeler.polylines.Polyline
           Polyline object.

        References
        ----------

        >>> oEditor.CreatePolyline

        Examples
        --------
        Set up the desktop environment.

        >>> from pyaedt.modeler.cad.polylines import PolylineSegment
        >>> from pyaedt import Desktop
        >>> from pyaedt import Maxwell3d
        >>> desktop=Desktop(specified_version="2021.2", new_desktop_session=False)
        >>> aedtapp = Maxwell3d()
        >>> aedtapp.modeler.model_units = "mm"
        >>> modeler = aedtapp.modeler

        Define some test data points.

        >>> test_points = [["0mm", "0mm", "0mm"], ["100mm", "20mm", "0mm"],
        ...                ["71mm", "71mm", "0mm"], ["0mm", "100mm", "0mm"]]

        The default behavior assumes that all points are to be
        connected by line segments.  Optionally specify the name.

        >>> P1 = modeler.create_polyline(test_points, name="PL_line_segments")

        Specify that the first segment is a line and the last three
        points define a three-point arc.

        >>> P2 = modeler.create_polyline(test_points, segment_type=["Line", "Arc"], name="PL_line_plus_arc")

        Redraw the 3-point arc alone from the last three points and
        additionally specify five segments using ``PolylineSegment``.

        >>> P3 = modeler.create_polyline(test_points[1:],
        ...                               segment_type=PolylineSegment(segment_type="Arc", num_seg=7),
        ...                               name="PL_segmented_arc")

        Specify that the four points form a spline and add a circular
        cross-section with a diameter of 1 mm.

        >>> P4 = modeler.create_polyline(test_points, segment_type="Spline", name="PL_spline",
        ...                               xsection_type="Circle", xsection_width="1mm")

        Use the `PolylineSegment` object to specify more detail about
        the individual segments.  Create a center point arc starting
        from the position ``test_points[1]``, rotating about the
        center point position ``test_points[0]`` in the XY plane.

        >>> start_point = test_points[1]
        >>> center_point = test_points[0]
        >>> segment_def = PolylineSegment(segment_type="AngularArc", arc_center=center_point,
        ...                                arc_angle="90deg", arc_plane="XY")
        >>> modeler.create_polyline(start_point, segment_type=segment_def, name="PL_center_point_arc")

        Create a spline using a list of variables for the coordinates of the points.

        >>> x0, y0, z0 = "0", "0", "1"
        >>> x1, y1, z1 = "1", "3", "1"
        >>> x2, y2, z2 = "2", "2", "1"
        >>> P5 = modeler.create_polyline(position_list = [[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]],
        ...                                 segment_type="Spline", name="polyline_with_variables")

        """
        new_polyline = Polyline(
            primitives=self,
            position_list=position_list,
            segment_type=segment_type,
            cover_surface=cover_surface,
            close_surface=close_surface,
            name=name,
            matname=matname,
            xsection_type=xsection_type,
            xsection_orient=xsection_orient,
            xsection_width=xsection_width,
            xsection_topwidth=xsection_topwidth,
            xsection_height=xsection_height,
            xsection_num_seg=xsection_num_seg,
            xsection_bend_type=xsection_bend_type,
            non_model=non_model,
        )
        return new_polyline

    @pyaedt_function_handler()
    def create_spiral_on_face(self, face, poly_width, filling_factor=1.5):
        """Create a Spiral Polyline inside a face.

        Parameters
        ----------
        face : int or str or :class:`pyaedt.modeler.elements3d.FacePrimitive`
        poly_width : float
        filling_factor : float

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Polyline`
        """
        # fmt: off
        if isinstance(face, FacePrimitive):
            face_id = face.id
        elif isinstance(face, int):
            face_id = face
        else:
            face_id = self.get_object_faces(face)[0]

        vertices = self.get_face_vertices(face_id)
        vertex_coordinates = []
        for v in vertices:
            vertex_coordinates.append(self.get_vertex_position(v))

        centroid = self.get_face_center(face_id)

        segments_lengths = []
        for vc in vertex_coordinates:
            segments_lengths.append(GeometryOperators.points_distance(vc, centroid))

        n = math.floor(min(segments_lengths) / (poly_width * filling_factor))

        if n % 2 == 0:
            n_points = int(n / 2 - 1)
        else:
            n_points = int((n - 1) / 2)

        if n_points < 1:
            raise Exception

        inner_points = []
        for vc in vertex_coordinates:
            temp = [[] for i in range(n_points)]
            for i in range(3):  # loop for x, y, z
                delta = (centroid[i] - vc[i]) / (n_points + 1)
                for j in range(1, n_points + 1):
                    temp[j - 1].append(vc[i] + delta * j)
            inner_points.append(temp)

        poly_points_list = []
        for p in range(n_points):
            for v in inner_points:
                poly_points_list.append(v[p])

        del poly_points_list[-1]

        # fmt: on
        return self.create_polyline(poly_points_list, xsection_type="Line", xsection_width=poly_width)

    @pyaedt_function_handler()
    def get_existing_polyline(self, object):
        """Retrieve a polyline object to manipulate it.

        Parameters
        ----------
        src_object : :class:`pyaedt.modeler.cad.object3d.Object3d`
            An existing polyline object in the 3D Modeler.

        Returns
        -------
        Polyline
        """
        return Polyline(self, src_object=object)

    @pyaedt_function_handler()
    def create_udp(self, udp_dll_name, udp_parameters_list, upd_library="syslib", name=None):
        """Create a user-defined primitive (UDP).

        Parameters
        ----------
        udp_dll_name : str
            Name of the UDP DLL or Python file. The default for the file format
            is ``".dll"``.
        udp_parameters_list :
            List of the UDP parameters.
        upd_library : str, optional
            Name of the UDP library. The default is ``"syslib"``.
        name : str, optional
            Name of the component. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            UDP object created.

        References
        ----------

        >>> oEditor.CreateUserDefinedPart

        Examples
        --------
        >>> my_udp = self.aedtapp.modeler.create_udp(udp_dll_name="RMxprt/ClawPoleCore",
        ...                                          udp_parameters_list=my_udpPairs,
        ...                                          upd_library="syslib")
        <class 'pyaedt.modeler.Object3d.Object3d'>

        """
        if ".dll" not in udp_dll_name and ".py" not in udp_dll_name:
            vArg1 = [
                "NAME:UserDefinedPrimitiveParameters",
                "DllName:=",
                udp_dll_name + ".dll",
                "Library:=",
                upd_library,
            ]
        else:
            vArg1 = ["NAME:UserDefinedPrimitiveParameters", "DllName:=", udp_dll_name, "Library:=", upd_library]

        vArgParamVector = ["NAME:ParamVector"]

        for pair in udp_parameters_list:
            if isinstance(pair, list):
                vArgParamVector.append(["NAME:Pair", "Name:=", pair[0], "Value:=", pair[1]])

            else:
                vArgParamVector.append(["NAME:Pair", "Name:=", pair.Name, "Value:=", pair.Value])

        vArg1.append(vArgParamVector)
        if name:
            obj_name = name
        else:
            obj_name, ext = os.path.splitext(os.path.basename(udp_dll_name))
        vArg2 = self._default_object_attributes(name=obj_name)
        obj_name = self.oeditor.CreateUserDefinedPart(vArg1, vArg2)
        return self._create_object(obj_name)

    @pyaedt_function_handler()
    def update_udp(self, object_name, operation_name, udp_parameters_list):
        """Update an existing geometrical object that was originally created using a user-defined primitive (UDP).

        Parameters
        ----------
        object_name : str
            Name of the object to update.
        operation_name : str
            Name of the operation used to create the object.
        udp_parameters_list : list
            List of the UDP parameters to update and their value.

        Returns
        -------
        bool
            ``True`` when successful.

        References
        ----------

        >>> oEditor.CreateUserDefinedPart

        Examples
        --------
        >>> self.aedtapp.modeler.update_udp(object_name="ClawPoleCore",
        ...                                 operation_name="CreateUserDefinedPart",
        ...                                 udp_parameters_list=[["Length","110mm"], ["DiaGap","125mm"]])
        True

        """

        vArg1 = ["NAME:AllTabs"]

        prop_servers = ["NAME:PropServers"]
        prop_servers.append("{0}:{1}:1".format(object_name, operation_name))

        cmd_tab = ["NAME:Geometry3DCmdTab"]
        cmd_tab.append(prop_servers)

        changed_props = ["NAME:ChangedProps"]

        for pair in udp_parameters_list:
            if isinstance(pair, list):
                changed_props.append(["NAME:{0}".format(pair[0]), "Value:=", pair[1]])
            else:
                changed_props.append(["NAME:", pair.Name, "Value:=", pair.Value])

        cmd_tab.append(changed_props)
        vArg1.append(cmd_tab)
        self.oeditor.ChangeProperty(vArg1)
        return True

    @pyaedt_function_handler()
    def delete(self, objects=None):
        """Delete objects or groups.

        Parameters
        ----------
        objects : list, optional
            List of objects or group names. The default is ``None``,
            in which case all objects are deleted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Delete

        """
        if objects is None:
            objects = self.object_names
        objects = self._modeler.convert_to_selections(objects, return_list=True)
        for el in objects:
            if el not in self.object_names and not list(self.oeditor.GetObjectsInGroup(el)):
                objects.remove(el)
        if not objects:
            self.logger.warning("No objects to delete")
            return False
        slice = min(100, len(objects))
        num_objects = len(objects)
        remaining = num_objects
        while remaining > 0:
            objs = objects[:slice]
            objects_str = self._modeler.convert_to_selections(objs, return_list=False)
            arg = ["NAME:Selections", "Selections:=", objects_str]
            try:
                self.oeditor.Delete(arg)
            except:
                self.logger.warning("Failed to delete {}.".format(objects_str))
            remaining -= slice
            if remaining > 0:
                objects = objects[slice:]

        self._refresh_object_types()

        if len(objects) > 0:
            self.cleanup_objects()
            self.logger.info("Deleted {} Objects: {}.".format(num_objects, objects_str))
        return True

    @pyaedt_function_handler()
    def delete_objects_containing(self, contained_string, case_sensitive=True):
        """Delete all objects with a given prefix.

        Parameters
        ----------
        contained_string : str
            Prefix in the names of the objects to delete.
        case_sensitive : bool, optional
            Whether the prefix is case sensitive. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Delete

        """
        objnames = self._object_names_to_ids
        num_del = 0
        for el in objnames:
            if case_sensitive:
                if contained_string in el:
                    self.delete(el)
                    num_del += 1
            else:
                if contained_string.lower() in el.lower():
                    self.delete(el)
                    num_del += 1
        self.logger.info("Deleted %s objects", num_del)
        return True

    @pyaedt_function_handler()
    def get_obj_id(self, objname):
        """Return the object ID from an object name.

        Parameters
        ----------
        objname : str
            Name of the object.

        Returns
        -------
        int
            Object ID.

        """
        if objname in self._object_names_to_ids:
            return self._object_names_to_ids[objname]
        return None

    @pyaedt_function_handler()
    def get_object_from_name(self, objname):
        """Return the object from an object name.

        Parameters
        ----------
        objname : str
            Name of the object.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object returned.

        """
        if objname in self._object_names_to_ids:
            object_id = self.get_obj_id(objname)
            return self.objects[object_id]

    @pyaedt_function_handler()
    def get_objects_w_string(self, stringname, case_sensitive=True):
        """Retrieve all objects with a given string in their names.

        Parameters
        ----------
        stringname : str
            String to search object names for.
        case_sensitive : bool, optional
            Whether the string is case-sensitive. The default is ``True``.

        Returns
        -------
        list
            List of object names with the given string.

        """
        list_objs = []
        for name in list(self.objects_by_name.keys()):
            if case_sensitive:
                if stringname in name:
                    list_objs.append(name)
            else:
                if stringname.lower() in name.lower():
                    list_objs.append(name)
        return list_objs

    @pyaedt_function_handler()
    def find_closest_edges(self, start_obj, end_obj, port_direction=0):
        """Retrieve the two closest edges that are not perpendicular for two objects.

        Parameters
        ----------
        start_obj : str
            Name of the starting object.
        end_obj : str
            Name of the ending object.
        port_direction : str, optional
            Direction of the port to which to give edges precedence when more than two couples
            are at the same distance. For example, for a coax or microstrip, precedence is given
            to the edges that are on the given axis direction, such as ``"XNeg"``. Options are
            ``"XNeg"``, ``"XPos"``, ``"YNeg"``, ``"YPos`"``, ``"ZNeg"``, and ``"ZPos"``.
            The default is ``0``.

        Returns
        -------
        list
            List with two edges if present.

        """
        start_obj = self._resolve_object(start_obj)
        end_obj = self._resolve_object(end_obj)
        edge_start_list = None
        edge_stop_list = None
        if port_direction == 0:
            if start_obj.bottom_face_x:
                edge_start_list = start_obj.bottom_face_x.edges
            if end_obj.bottom_face_x:
                edge_stop_list = end_obj.bottom_face_x.edges
        elif port_direction == 3:
            if start_obj.top_face_x:
                edge_start_list = start_obj.top_face_x.edges
            if end_obj.top_face_x:
                edge_stop_list = end_obj.top_face_x.edges
        elif port_direction == 1:
            if start_obj.bottom_face_y:
                edge_start_list = start_obj.bottom_face_y.edges
            if end_obj.bottom_face_y:
                edge_stop_list = end_obj.bottom_face_y.edges
        elif port_direction == 4:
            if start_obj.top_face_y:
                edge_start_list = start_obj.top_face_y.edges
            if end_obj.top_face_y:
                edge_stop_list = end_obj.top_face_y.edges
        elif port_direction == 2:
            if start_obj.bottom_face_z:
                edge_start_list = start_obj.bottom_face_z.edges
            if end_obj.bottom_face_z:
                edge_stop_list = end_obj.bottom_face_z.edges
        elif port_direction == 5:
            if start_obj.top_face_z:
                edge_start_list = start_obj.top_face_z.edges
            if end_obj.top_face_z:
                edge_stop_list = end_obj.top_face_z.edges
        if not edge_start_list:
            edge_start_list = start_obj.edges
        if not edge_stop_list:
            edge_stop_list = end_obj.edges
        mindist = 1e6
        tol = 1e-12
        pos_tol = 1e-6
        edge_list = []
        actual_point = None
        is_parallel = False
        for el in edge_start_list:
            vertices_i = el.vertices
            if not vertices_i:
                for f in start_obj.faces:
                    if len(f.edges) == 1:
                        edges_ids = [i.id for i in f.edges]
                        if el.id in edges_ids:
                            vertices_i.append(f.center)
                            break
            vertex1_i = None
            vertex2_i = None
            if len(vertices_i) == 2:  # normal segment edge
                vertex1_i = vertices_i[0].position
                vertex2_i = vertices_i[1].position
                start_midpoint = el.midpoint
            elif len(vertices_i) == 1:
                if isinstance(vertices_i[0], list):
                    start_midpoint = vertices_i[0]
                else:
                    start_midpoint = vertices_i[0].position
            else:
                continue
            for el1 in edge_stop_list:
                vertices_j = el1.vertices
                if not vertices_j:
                    for f in end_obj.faces:
                        if len(f.edges) == 1:
                            edges_ids = [i.id for i in f.edges]
                            if el1.id in edges_ids:
                                vertices_j.append(f.center)
                                break
                vertex1_j = None
                vertex2_j = None
                if len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = vertices_j[0].position
                    vertex2_j = vertices_j[1].position
                    end_midpoint = el1.midpoint
                elif len(vertices_j) == 1:
                    if isinstance(vertices_j[0], list):
                        end_midpoint = vertices_j[0]
                    else:
                        end_midpoint = vertices_j[0].position
                else:
                    continue

                parallel_edges = False
                vect = None
                if vertex1_i and vertex1_j:
                    if (
                        abs(
                            GeometryOperators._v_dot(
                                GeometryOperators.v_points(vertex1_i, vertex2_i),
                                GeometryOperators.v_points(vertex1_j, vertex2_j),
                            )
                        )
                        < tol
                    ):
                        continue  # skip perperndicular edges
                    if GeometryOperators.is_parallel(vertex1_i, vertex2_i, vertex1_j, vertex2_j):
                        parallel_edges = True
                    vert_dist_sum = GeometryOperators.arrays_positions_sum(
                        [vertex1_i, vertex2_i], [vertex1_j, vertex2_j]
                    )
                    vect = GeometryOperators.distance_vector(start_midpoint, vertex1_j, vertex2_j)
                else:
                    vert_dist_sum = GeometryOperators.arrays_positions_sum([start_midpoint], [end_midpoint])

                # dist = abs(_v_norm(vect))

                if parallel_edges:
                    pd1 = GeometryOperators.points_distance(vertex1_i, vertex2_i)
                    pd2 = GeometryOperators.points_distance(vertex1_j, vertex2_j)

                    if pd1 < pd2 and not GeometryOperators.is_projection_inside(
                        vertex1_i, vertex2_i, vertex1_j, vertex2_j
                    ):
                        continue
                    elif pd1 >= pd2 and not GeometryOperators.is_projection_inside(
                        vertex1_j, vertex2_j, vertex1_i, vertex2_i
                    ):
                        continue

                if actual_point is None:
                    edge_list = [el, el1]
                    is_parallel = parallel_edges
                    actual_point = GeometryOperators.find_point_on_plane([start_midpoint, end_midpoint], port_direction)
                    mindist = vert_dist_sum
                else:
                    new_point = GeometryOperators.find_point_on_plane([start_midpoint, end_midpoint], port_direction)
                    if (port_direction <= 2 and new_point - actual_point < 0) or (
                        port_direction > 2 and actual_point - new_point < 0
                    ):
                        edge_list = [el, el1]
                        is_parallel = parallel_edges
                        actual_point = new_point
                        mindist = vert_dist_sum
                    elif port_direction <= 2 and new_point - actual_point < tol and vert_dist_sum - mindist < pos_tol:
                        edge_list = [el, el1]
                        is_parallel = parallel_edges
                        actual_point = new_point
                        mindist = vert_dist_sum
                    elif port_direction > 2 and actual_point - new_point < tol and vert_dist_sum - mindist < pos_tol:
                        edge_list = [el, el1]
                        is_parallel = parallel_edges
                        actual_point = new_point
                        mindist = vert_dist_sum
        return edge_list, is_parallel

    @pyaedt_function_handler()
    def get_equivalent_parallel_edges(self, edgelist, portonplane=True, axisdir=0, startobj="", endobject=""):
        """Create two new edges that are parallel and equal to the smallest edge given a parallel couple of edges.

        Parameters
        ----------
        edgelist : list
            List of two parallel edges.
        portonplane : bool, optional
            Whether edges are to be on the plane orthogonal to the axis direction.
            The default is ``True``.
        axisdir : int, optional
            Axis direction. Choices are ``0`` through ``5``. The default is ``0``.
        startobj : str, optional
             Name of the starting object. The default is ``""``.
        endobject : str, optional
             Name of the ending object. The default is ``""``.

        Returns
        -------
        list
            List of two created edges.

        """
        if isinstance(edgelist[0], str):
            edgelist[0] = self.get_object_from_name(edgelist[0])
        if isinstance(edgelist[1], str):
            edgelist[1] = self.get_object_from_name(edgelist[1])

        l1 = edgelist[0].length
        l2 = edgelist[1].length
        if l1 < l2:
            orig_edge = edgelist[0]
            dest_edge = edgelist[1]
        else:
            orig_edge = edgelist[1]
            dest_edge = edgelist[0]

        first_edge = self.create_object_from_edge(orig_edge)
        second_edge = self.create_object_from_edge(orig_edge)
        ver1 = orig_edge.vertices
        ver2 = dest_edge.vertices
        if len(ver2) == 2:
            p = ver1[0].position
            a1 = ver2[0].position
            a2 = ver2[1].position
            vect = GeometryOperators.distance_vector(p, a1, a2)
            if portonplane:
                vect[divmod(axisdir, 3)[1]] = 0
            # TODO: can we avoid this translate operation - is there another way to check ?
            self.move(second_edge, vect)
            p_check = second_edge.vertices[0].position
            p_check2 = second_edge.vertices[1].position
        # elif len(ver2) == 1:  # for circular edges with one vertex
        #     p_check = first_edge.vertices[0].position
        #     p_check2 = second_edge.vertices[0].position
        else:
            self.delete(first_edge)
            self.delete(second_edge)
            return False

        obj_check = self.get_bodynames_from_position(p_check)
        obj_check2 = self.get_bodynames_from_position(p_check2)
        # if (startobj in obj_check and endobject in obj_check2) or (startobj in obj_check2 and endobject in obj_check):
        if (startobj in obj_check or endobject in obj_check) and (startobj in obj_check2 or endobject in obj_check2):
            if l1 < l2:
                return_edges = [first_edge, second_edge]
            else:
                return_edges = [second_edge, first_edge]
            return return_edges
        else:
            self.delete(second_edge)
            self.delete(first_edge)
            return None

    @pyaedt_function_handler()
    def get_object_faces(self, partId):
        """Retrieve the face IDs of a given object ID or object name.

        Parameters
        ----------
        partId : int or str
            Object ID or object name.

        Returns
        -------
        List
            List of faces IDs.

        References
        ----------

        >>> oEditor.GetFaceIDs

        """
        oFaceIDs = []
        if isinstance(partId, str) and partId in self._object_names_to_ids:
            oFaceIDs = self.oeditor.GetFaceIDs(partId)
            oFaceIDs = [int(i) for i in oFaceIDs]
        elif partId in self.objects:
            o = self.objects[partId]
            name = o.name
            oFaceIDs = self.oeditor.GetFaceIDs(name)
            oFaceIDs = [int(i) for i in oFaceIDs]
        return oFaceIDs

    @pyaedt_function_handler()
    def get_object_edges(self, partId):
        """Retrieve the edge IDs of a given object ID or object name.

        Parameters
        ----------
        partId : int or str
            Object ID or object name.

        Returns
        -------
        List
            List of edge IDs.

        References
        ----------

        >>> oEditor.GetEdgeIDsFromObject

        """
        oEdgeIDs = []
        if isinstance(partId, str) and partId in self._object_names_to_ids:
            oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(partId)
            oEdgeIDs = [int(i) for i in oEdgeIDs]
        elif partId in self.objects:
            o = self.objects[partId]
            oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(o.name)
            oEdgeIDs = [int(i) for i in oEdgeIDs]
        return oEdgeIDs

    @pyaedt_function_handler()
    def get_face_edges(self, partId):
        """Retrieve the edge IDs of a given face name or face ID.

        Parameters
        ----------
        partId : int or str
            Object ID or object name.

        Returns
        -------
        List
            List of edge IDs.

        References
        ----------

        >>> oEditor.GetEdgeIDsFromFace

        """
        oEdgeIDs = self.oeditor.GetEdgeIDsFromFace(partId)
        oEdgeIDs = [int(i) for i in oEdgeIDs]
        return oEdgeIDs

    @pyaedt_function_handler()
    def get_object_vertices(self, partID):
        """Retrieve the vertex IDs of a given object name or object ID.

        Parameters
        ----------
        partID : int or str
            Object ID or object name.

        Returns
        -------
        List
            List of vertex IDs.

        References
        ----------

        >>> oEditor.GetVertexIDsFromObject

        """
        oVertexIDs = []
        if isinstance(partID, str) and partID in self._object_names_to_ids:
            oVertexIDs = self.oeditor.GetVertexIDsFromObject(partID)
            oVertexIDs = [int(i) for i in oVertexIDs]
        elif partID in self.objects:
            o = self.objects[partID]
            oVertexIDs = self.oeditor.GetVertexIDsFromObject(o.name)
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @pyaedt_function_handler()
    def get_face_vertices(self, face_id):
        """Retrieve the vertex IDs of a given face ID or face name.

        Parameters
        ----------
        face_id : int or str
            Object ID or object name, which is available
            using the methods :func:`pyaedt.modeler.Primitives3D.Primitives3D.get_object_vertices`
            or :func:`pyaedt.modeler.Primitives2D.Primitives2D.get_object_vertices`.

        Returns
        -------
        List
            List of vertex IDs.

        References
        ----------

        >>> oEditor.GetVertexIDsFromFace

        """
        try:
            oVertexIDs = self.oeditor.GetVertexIDsFromFace(face_id)
        except:
            oVertexIDs = []
        else:
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @pyaedt_function_handler()
    def get_edge_length(self, edgeID):
        """Get the length of an edge.

        Parameters
        ----------
        edgeID : int
            ID of the edge.

        Returns
        -------
        type
            Edge length.

        """
        vertexID = self.get_edge_vertices(edgeID)
        pos1 = self.get_vertex_position(vertexID[0])
        if len(vertexID) < 2:
            return 0
        pos2 = self.get_vertex_position(vertexID[1])
        length = GeometryOperators.points_distance(pos1, pos2)
        return length

    @pyaedt_function_handler()
    def get_edge_vertices(self, edgeID):
        """Retrieve the vertex IDs of a given edge ID or edge name.

        Parameters
        ----------
        edgeID : int, str
            Object ID or object name, which is available using the
            methods :func:`pyaedt.modeler.Primitives3D.Primitives3D.get_object_vertices`
            or :func:`pyaedt.modeler.Primitives2D.Primitives2D.get_object_vertices`.

        Returns
        -------
        List
            List of vertex IDs.

        References
        ----------

        >>> oEditor.GetVertexIDsFromEdge

        """
        try:
            oVertexIDs = self.oeditor.GetVertexIDsFromEdge(edgeID)
        except:
            oVertexIDs = []
        else:
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @pyaedt_function_handler()
    def get_vertex_position(self, vertex_id):
        """Retrieve a vector of vertex coordinates.

        Parameters
        ----------
        vertex_id : int or str
            ID or name of the vertex.

        Returns
        -------
        List
            List of ``[x, y, z]`` coordinates indicating the position.

        References
        ----------

        >>> oEditor.GetVertexPosition

        """
        try:
            pos = self.oeditor.GetVertexPosition(vertex_id)
        except:
            position = []
        else:
            position = [float(i) for i in pos]
        return position

    @pyaedt_function_handler()
    def get_face_area(self, face_id):
        """Retrieve the area of a given face ID.

        Parameters
        ----------
        face_id : int
            ID of the face.

        Returns
        -------
        float
            Value for the face area.

        References
        ----------

        >>> oEditor.GetFaceArea

        """

        area = self.oeditor.GetFaceArea(face_id)
        return area

    @pyaedt_function_handler()
    def get_face_center(self, face_id):
        """Retrieve the center position for a given planar face ID.

        Parameters
        ----------
        face_id : int
            ID of the face.

        Returns
        -------
        List
            A list of ``[x, y, z]`` coordinates for the
            planar face center position.

        References
        ----------

        >>> oEditor.GetFaceCenter

        """
        try:
            c = self.oeditor.GetFaceCenter(face_id)
        except:
            self.logger.warning("Non Planar Faces doesn't provide any Face Center")
            return False
        center = [float(i) for i in c]
        return center

    @pyaedt_function_handler()
    def get_mid_points_on_dir(self, sheet, axisdir):
        """Retrieve midpoints on a given axis direction.

        Parameters
        ----------
        sheet :

        axisdir : int
            Axis direction. Choices are ``0`` through ``5``.

        Returns
        -------
        type

        """
        edgesid = self.get_object_edges(sheet)
        id_ = divmod(axisdir, 3)[1]
        midpoint_array = []
        for ed in edgesid:
            midpoint_array.append(self.get_edge_midpoint(ed))
        point0 = []
        point1 = []
        for el in midpoint_array:
            if not point0:
                point0 = el
                point1 = el
            elif axisdir < 3 and el[id_] < point0[id_] or axisdir > 2 and el[id_] > point0[id_]:
                point0 = el
            elif axisdir < 3 and el[id_] > point1[id_] or axisdir > 2 and el[id_] < point1[id_]:
                point1 = el
        return point0, point1

    @pyaedt_function_handler()
    def get_edge_midpoint(self, partID):
        """Retrieve the midpoint coordinates of a given edge ID or edge name.

        Parameters
        ----------
        partID : int or str
            Object ID  or object name.

        Returns
        -------
        list
            List of midpoint coordinates. If the edge is not a segment with
            two vertices, an empty list is returned.
        """

        if isinstance(partID, str) and partID in self._object_names_to_ids:
            partID = self._object_names_to_ids[partID]

        if partID in self.objects and self.objects[partID].object_type == "Line":
            vertices = self.get_object_vertices(partID)
        else:
            try:
                vertices = self.get_edge_vertices(partID)
            except:
                vertices = []
        if len(vertices) == 2:
            vertex1 = self.get_vertex_position(vertices[0])
            vertex2 = self.get_vertex_position(vertices[1])
            midpoint = GeometryOperators.get_mid_point(vertex1, vertex2)
            return list(midpoint)
        elif len(vertices) == 1:
            return list(self.get_vertex_position(vertices[0]))
        else:
            return

    @pyaedt_function_handler()
    def get_bodynames_from_position(self, position, units=None, include_non_model=True):
        """Retrieve the names of the objects that are in contact with a given point.

        Parameters
        ----------
        position : list
            List of ``[x, y, z]`` coordinates for the point.
        units : str, optional
            Units, such as ``"m"``. The default is ``None``, in which case the
            model units are used.
        include_non_model : bool, optional
            Either if include or not non model objects.

        Returns
        -------
        list
            List of object names.

        References
        ----------

        >>> oEditor.GetBodyNamesByPosition

        """
        if not isinstance(position, (self.Position, list)):
            # self.logger.error("A list of point has to be provided")
            return []
        XCenter, YCenter, ZCenter = self._pos_with_arg(position, units)
        vArg1 = ["NAME:Parameters"]
        vArg1.append("XPosition:="), vArg1.append(XCenter)
        vArg1.append("YPosition:="), vArg1.append(YCenter)
        vArg1.append("ZPosition:="), vArg1.append(ZCenter)
        list_of_bodies = list(self.oeditor.GetBodyNamesByPosition(vArg1))
        if not include_non_model:
            non_models = [i for i in self.non_model_objects]
            list_of_bodies = [i for i in list_of_bodies if i not in non_models]
        return list_of_bodies

    @pyaedt_function_handler()
    def get_edgeid_from_position(self, position, obj_name=None, units=None):
        """Get an edge ID from a position.

        Parameters
        ----------
        position : list
            List of ``[x, y, z]`` coordinates for the position.
        obj_name : str, optional
            Name of the object. The default is ``None``, in which case all
            objects are searched.
        units : str, optional
            Units for the position, such as ``"m"``. The default is ``None``,
            in which case the model units are used.

        Returns
        -------
        type
            Edge ID of the first object touching this position.
        """
        if isinstance(obj_name, str):
            object_list = [obj_name]
        else:
            object_list = self.object_names

        edgeID = -1
        XCenter, YCenter, ZCenter = self._pos_with_arg(position, units)

        vArg1 = ["NAME:EdgeParameters"]
        vArg1.append("BodyName:="), vArg1.append("")
        vArg1.append("XPosition:="), vArg1.append(XCenter)
        vArg1.append("YPosition:="), vArg1.append(YCenter)
        vArg1.append("ZPosition:="), vArg1.append(ZCenter)
        for obj in object_list:
            vArg1[2] = obj
            try:
                edgeID = int(self.oeditor.GetEdgeByPosition(vArg1))
                return edgeID
            except:
                pass

    @pyaedt_function_handler()
    def get_edgeids_from_vertexid(self, vertexid, obj_name):
        """Retrieve edge IDs for a vertex ID.

        Parameters
        ----------
        vertexid : int
            Vertex ID.
        obj_name :
            Name of the object.

        Returns
        -------
        List
            List of edge IDs for the vertex ID.

        References
        ----------

        >>> oEditor.GetEdgeIDsFromObject
        >>> oEditor.GetVertexIDsFromEdge

        """
        edgeID = []
        edges = self.get_object_edges(obj_name)
        for edge in edges:
            vertices = self.get_edge_vertices(edge)
            if vertexid in vertices:
                edgeID.append(edge)

        return edgeID

    @pyaedt_function_handler()
    def get_faceid_from_position(self, position, obj_name=None, units=None):
        """Retrieve a face ID from a position.

        Parameters
        ----------
        position : list
            List of ``[x, y, z]`` coordinates for the position.
        obj_name : str, optional
            Name of the object. The default is ``None``, in which case all
            objects are searched.
        units : str, optional
            Units, such as ``"m"``. The default is ``None``, in which case the
            model units are used.

        Returns
        -------
        int
            Face ID of the first object touching this position.

        References
        ----------

        >>> oEditor.GetFaceByPosition

        """
        if isinstance(obj_name, str):
            object_list = [obj_name]
        else:
            object_list = self.object_names

        XCenter, YCenter, ZCenter = self._pos_with_arg(position, units)
        vArg1 = ["NAME:FaceParameters"]
        vArg1.append("BodyName:="), vArg1.append("")
        vArg1.append("XPosition:="), vArg1.append(XCenter)
        vArg1.append("YPosition:="), vArg1.append(YCenter)
        vArg1.append("ZPosition:="), vArg1.append(ZCenter)
        for obj in object_list:
            vArg1[2] = obj
            try:
                face_id = self.oeditor.GetFaceByPosition(vArg1)
                return face_id
            except:
                # Not Found, keep looking
                pass

    @pyaedt_function_handler()
    def get_edges_on_bounding_box(self, sheets, return_colinear=True, tol=1e-6):
        """Retrieve the edges of the sheets passed in the input that are lying on the bounding box.

        This method creates new lines for the detected edges and returns the IDs of these lines.
        If required, only colinear edges are returned.

        Parameters
        ----------
        sheets : int, str, or list
            ID or name for one or more sheets.
        return_colinear : bool, optional
            Whether to return only colinear edges. The default is ``True``.
            If ``False``, all edges on the bounding box are returned.
        tol : float, optional
            Geometric tolerance. The default is ``1e-6``.

        Returns
        -------
        list
            List of edge IDs lying on the bounding box.

        """
        port_sheets = self._modeler.convert_to_selections(sheets, return_list=True)
        bb = self._modeler.get_model_bounding_box()

        candidate_edges = []
        for p in port_sheets:
            edges = self[p].edges
            for edge in edges:
                vertices = edge.vertices
                v_flag = False
                for vertex in vertices:
                    v = vertex.position
                    xyz_flag = 0
                    if abs(v[0] - bb[0]) < tol or abs(v[0] - bb[3]) < tol:
                        xyz_flag += 1
                    if abs(v[1] - bb[1]) < tol or abs(v[1] - bb[4]) < tol:
                        xyz_flag += 1
                    if abs(v[2] - bb[2]) < tol or abs(v[2] - bb[5]) < tol:
                        xyz_flag += 1
                    if xyz_flag >= 2:
                        v_flag = True
                    else:
                        v_flag = False
                        break
                if v_flag:
                    candidate_edges.append(edge)

        if not return_colinear:
            return candidate_edges

        selected_edges = []
        for i, edge_i in enumerate(candidate_edges[:-1]):
            vertex1_i = edge_i.vertices[0].position
            midpoint_i = edge_i.midpoint
            for j, edge_j in enumerate(candidate_edges[i + 1 :]):
                midpoint_j = edge_j.midpoint
                area = GeometryOperators.get_triangle_area(midpoint_i, midpoint_j, vertex1_i)
                if area < tol**2:
                    selected_edges.extend([edge_i, edge_j])
                    break
        selected_edges = list(set(selected_edges))

        for edge in selected_edges:
            self.create_object_from_edge(edge)
            time.sleep(aedt_wait_time)

        return selected_edges

    @pyaedt_function_handler()
    def get_edges_for_circuit_port_from_sheet(
        self, sheet, XY_plane=True, YZ_plane=True, XZ_plane=True, allow_perpendicular=False, tol=1e-6
    ):
        """Retrieve two edge IDs that are suitable for a circuit port from a sheet.

        One edge belongs to the sheet passed in the input, and the second edge
        is the closest edge's coplanar to the first edge (aligned to the XY, YZ,
        or XZ plane). This method creates new lines for the detected edges and returns
        the IDs of these lines.

        This method accepts one or more sheet objects as input,
        while the method :func:`Primitives.get_edges_for_circuit_port`
        accepts a face ID.

        Parameters
        ----------
        sheet : int, str, or list
            ID or name for one or more sheets.
        XY_plane : bool, optional
            Whether the edge's pair are to be on the XY plane.
            The default is ``True``.
        YZ_plane : bool, optional
            Whether the edge's pair are to be on the YZ plane.
            The default is ``True``.
        XZ_plane : bool, optional
            Whether the edge's pair are to be on the XZ plane.
            The default is ``True``.
        allow_perpendicular : bool, optional
            Whether the edge's pair are to be perpendicular.
            The default is ``False``.
        tol : float, optional
            Geometric tolerance. The default is ``1e-6``.

        Returns
        -------
        list
            List of edge IDs.

        """
        tol2 = tol**2
        port_sheet = self._modeler.convert_to_selections(sheet, return_list=True)
        if len(port_sheet) > 1:
            return []
        else:
            port_sheet = port_sheet[0]
        port_edges = self.get_object_edges(port_sheet)

        # find the bodies to exclude
        port_sheet_midpoint = self.get_face_center(self.get_object_faces(port_sheet)[0])
        point = self._modeler.Position(*port_sheet_midpoint)
        list_of_bodies = self.get_bodynames_from_position(point)

        # select all edges
        all_edges = []
        solids = [s for s in self.solid_names if s not in list_of_bodies]
        for solid in solids:
            edges = self.get_object_edges(solid)
            all_edges.extend(edges)
        all_edges = list(set(all_edges))  # remove duplicates

        # select edges coplanar to port edges (aligned to XY, YZ, or XZ plane)
        ux = [1.0, 0.0, 0.0]
        uy = [0.0, 1.0, 0.0]
        uz = [0.0, 0.0, 1.0]
        midpoints = {}
        candidate_edges = []
        for ei in port_edges:
            vertices_i = self.get_edge_vertices(ei)
            if len(vertices_i) == 1:  # maybe a circle
                vertex1_i = self.get_vertex_position(vertices_i[0])
                area_i = self.get_face_area(self.get_object_faces(port_sheet)[0])
                if area_i is None or area_i < tol2:  # degenerated face
                    continue
                center_i = self.get_face_center(self.get_object_faces(port_sheet)[0])
                if not center_i:  # non planar face
                    continue
                radius_i = GeometryOperators.points_distance(vertex1_i, center_i)
                area_i_eval = math.pi * radius_i**2
                if abs(area_i - area_i_eval) < tol2:  # it is a circle
                    vertex2_i = center_i
                    midpoints[ei] = center_i
                else:  # not a circle
                    continue
            elif len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                midpoints[ei] = self.get_edge_midpoint(ei)
            else:  # undetermined edge --> skip
                continue
            for ej in all_edges:
                vertices_j = self.get_edge_vertices(ej)
                if len(vertices_j) == 1:  # edge is an arc, not supported
                    continue
                elif len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                else:  # undetermined edge --> skip
                    continue

                if (
                    not allow_perpendicular
                    and abs(
                        GeometryOperators._v_dot(
                            GeometryOperators.v_points(vertex1_i, vertex2_i),
                            GeometryOperators.v_points(vertex1_j, vertex2_j),
                        )
                    )
                    < tol
                ):
                    continue

                normal1 = GeometryOperators.v_cross(
                    GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_i, vertex1_j)
                )
                normal1_norm = GeometryOperators.v_norm(normal1)
                if YZ_plane and abs(abs(GeometryOperators._v_dot(normal1, ux)) - normal1_norm) < tol:
                    pass
                elif XZ_plane and abs(abs(GeometryOperators._v_dot(normal1, uy)) - normal1_norm) < tol:
                    pass
                elif XY_plane and abs(abs(GeometryOperators._v_dot(normal1, uz)) - normal1_norm) < tol:
                    pass
                else:
                    continue

                vec1 = GeometryOperators.v_points(vertex1_i, vertex2_j)
                if abs(GeometryOperators._v_dot(normal1, vec1)) < tol2:  # the 4th point is coplanar
                    candidate_edges.append(ej)

        minimum_distance = tol**-1
        selected_edges = []
        for ei in midpoints:
            midpoint_i = midpoints[ei]
            for ej in candidate_edges:
                midpoint_j = self.get_edge_midpoint(ej)
                d = GeometryOperators.points_distance(midpoint_i, midpoint_j)
                if d < minimum_distance:
                    minimum_distance = d
                    selected_edges = [ei, ej]

        if selected_edges:
            new_edge1 = self.create_object_from_edge(selected_edges[0])
            time.sleep(aedt_wait_time)
            new_edge2 = self.create_object_from_edge(selected_edges[1])
            return selected_edges
        else:
            return []

    @pyaedt_function_handler()
    def get_edges_for_circuit_port(
        self, face_id, XY_plane=True, YZ_plane=True, XZ_plane=True, allow_perpendicular=False, tol=1e-6
    ):
        """Retrieve two edge IDs suitable for the circuit port.

        One edge belongs to the face ID passed in the input, and the second edge
        is the closest edge's coplanar to the first edge (aligned to the XY, YZ,
        or XZ plane). This method creates new lines for the detected edges and returns
        the IDs of these lines.

        This method accepts a face ID in the input, while the `get_edges_for_circuit_port_from_port`
        method accepts one or more sheet objects.

        Parameters
        ----------
        face_id :
            ID of the face.
        XY_plane : bool, optional
            Whether the edge's pair are to be on the XY plane.
            The default is ``True``.
        YZ_plane : bool, optional
            Whether the edge's pair are to be on the YZ plane.
            The default is ``True``.
        XZ_plane : bool, optional
            Whether the edge's pair are to be on the XZ plane.
            The default is ``True``.
        allow_perpendicular : bool, optional
            Whether the edge's pair are to be perpendicular.
            The default is ``False``.
        tol : float, optional
            Geometric tolerance. The default is ``1e-6``.

        Returns
        -------
        list
            List of edge IDs.

        """
        tol2 = tol**2

        port_edges = self.get_face_edges(face_id)

        # find the bodies to exclude
        port_sheet_midpoint = self.get_face_center(face_id)
        point = self._modeler.Position(port_sheet_midpoint)
        list_of_bodies = self.get_bodynames_from_position(point)

        # select all edges
        all_edges = []
        solids = [s for s in self.solid_names if s not in list_of_bodies]
        for solid in solids:
            edges = self.get_object_edges(solid)
            all_edges.extend(edges)
        all_edges = list(set(all_edges))  # remove duplicates

        # select edges coplanar to port edges (aligned to XY, YZ, or XZ plane)
        ux = [1.0, 0.0, 0.0]
        uy = [0.0, 1.0, 0.0]
        uz = [0.0, 0.0, 1.0]
        midpoints = {}
        candidate_edges = []
        for ei in port_edges:
            vertices_i = self.get_edge_vertices(ei)
            if len(vertices_i) == 1:  # maybe a circle
                vertex1_i = self.get_vertex_position(vertices_i[0])
                area_i = self.get_face_area(face_id)
                if area_i is None or area_i < tol2:  # degenerated face
                    continue
                center_i = self.get_face_center(face_id)
                if not center_i:  # non planar face
                    continue
                radius_i = GeometryOperators.points_distance(vertex1_i, center_i)
                area_i_eval = math.pi * radius_i**2
                if abs(area_i - area_i_eval) < tol2:  # it is a circle
                    vertex2_i = center_i
                    midpoints[ei] = center_i
                else:  # not a circle
                    continue
            elif len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                midpoints[ei] = self.get_edge_midpoint(ei)
            else:  # undetermined edge --> skip
                continue
            for ej in all_edges:
                vertices_j = self.get_edge_vertices(ej)
                if len(vertices_j) == 1:  # edge is an arc, not supported
                    continue
                elif len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                else:  # undetermined edge --> skip
                    continue

                if (
                    not allow_perpendicular
                    and abs(
                        GeometryOperators._v_dot(
                            GeometryOperators.v_points(vertex1_i, vertex2_i),
                            GeometryOperators.v_points(vertex1_j, vertex2_j),
                        )
                    )
                    < tol
                ):
                    continue

                normal1 = GeometryOperators.v_cross(
                    GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_i, vertex1_j)
                )
                normal1_norm = GeometryOperators.v_norm(normal1)
                if YZ_plane and abs(abs(GeometryOperators._v_dot(normal1, ux)) - normal1_norm) < tol:
                    pass
                elif XZ_plane and abs(abs(GeometryOperators._v_dot(normal1, uy)) - normal1_norm) < tol:
                    pass
                elif XY_plane and abs(abs(GeometryOperators._v_dot(normal1, uz)) - normal1_norm) < tol:
                    pass
                else:
                    continue

                vec1 = GeometryOperators.v_points(vertex1_i, vertex2_j)
                if abs(GeometryOperators._v_dot(normal1, vec1)) < tol2:  # the 4th point is coplanar
                    candidate_edges.append(ej)

        minimum_distance = tol**-1
        selected_edges = []
        for ei in midpoints:
            midpoint_i = midpoints[ei]
            for ej in candidate_edges:
                midpoint_j = self.get_edge_midpoint(ej)
                d = GeometryOperators.points_distance(midpoint_i, midpoint_j)
                if d < minimum_distance:
                    minimum_distance = d
                    selected_edges = [ei, ej]

        if selected_edges:
            new_edge1 = self.create_object_from_edge(selected_edges[0])
            time.sleep(aedt_wait_time)
            new_edge2 = self.create_object_from_edge(selected_edges[1])
            return selected_edges
        else:
            return []

    @pyaedt_function_handler()
    def get_closest_edgeid_to_position(self, position, units=None):
        """Get the edge ID closest to a given position.

        Parameters
        ----------
        position : list
            List of ``[x,y,z]`` coordinates for the position.
        units :
            Units for the position, such as ``"m"``. The default is ``None``, which means the model units are used.

        Returns
        -------
        int
            Edge ID of the edge closest to this position.

        """
        if isinstance(position, list):
            position = self.Position(position)

        bodies = self.get_bodynames_from_position(position, units)
        # the function searches in all bodies, not efficient
        face_id = self.get_faceid_from_position(position, obj_name=bodies[0], units=units)
        edges = self.get_face_edges(face_id)
        distance = 1e6
        selected_edge = None
        for edge in edges:
            midpoint = self.get_edge_midpoint(edge)
            if self.model_units == "mm" and units == "meter":
                midpoint = [i / 1000 for i in midpoint]
            elif self.model_units == "meter" and units == "mm":
                midpoint = [i * 1000 for i in midpoint]
            d = GeometryOperators.points_distance(midpoint, [position.X, position.Y, position.Z])
            if d < distance:
                selected_edge = int(edge)
                distance = d
        return selected_edge

    @pyaedt_function_handler()
    def _resolve_object(self, object):
        if isinstance(object, Object3d):
            return object
        else:
            return self[object]

    @pyaedt_function_handler()
    def _get_model_objects(self, model=True):
        """Retrieve all model objects.

        Parameters
        ----------
        model : bool, optional
            Whether to retrieve all model objects. The default is ``True``. When ``False``,
            all non-model objects are retrieved.

        Returns
        -------
        list
            List of retrieved objects.

        """
        list_objs = []
        for id, obj in self.objects.items():
            if obj.model == model:
                list_objs.append(obj.name)
        return list_objs

    @pyaedt_function_handler()
    def _check_material(self, matname, defaultmatname, threshold=100000):
        """Check for a material name.

        If a material name exists, it is assigned. Otherwise, the material
        specified as the default is assigned.

        Parameters
        ----------
        matname : str
            Name of the material.
        defaultmatname : str
            Name of the default material to assign if ``metname`` does not exist.
        threshold : float
            Threshold conductivity in S/m to distinguish dielectric from conductor.
            The default value is ``100000``.

        Returns
        -------
        (str, bool)
            Material name, Boolean True if the material is a dielectric, otherwise False.

        """

        # Note: Material.is_dielectric() does not work if the conductivity
        # value is an expression.
        if isinstance(matname, Material):
            if self._app._design_type == "HFSS":
                return matname.name, matname.is_dielectric(threshold)
            else:
                return matname.name, True
        if matname:
            if self._app.materials[matname]:
                if self._app._design_type == "HFSS":
                    return self._app.materials[matname].name, self._app.materials[matname].is_dielectric(threshold)
                else:
                    return self._app.materials[matname].name, True
            else:
                self.logger.warning("Material %s doesn not exists. Assigning default material", matname)
        if self._app._design_type == "HFSS":
            return defaultmatname, self._app.materials.material_keys[defaultmatname].is_dielectric(threshold)
        else:
            return defaultmatname, True

    @pyaedt_function_handler()
    def _refresh_solids(self):
        try:
            test = self.oeditor.GetObjectsInGroup("Solids")
        except (TypeError, AttributeError):
            test = []
        if test is False:
            assert False, "Get Solids is failing"
        elif test is True or test is None:
            self._solids = []  # In IronPython True is returned when no sheets are present
        else:
            self._solids = list(test)
        self._all_object_names = self._solids + self._sheets + self._lines + self._points

    @pyaedt_function_handler()
    def _refresh_sheets(self):
        try:
            test = self.oeditor.GetObjectsInGroup("Sheets")
        except (TypeError, AttributeError):
            test = []
        if test is False:
            assert False, "Get Sheets is failing"
        elif test is True or test is None:
            self._sheets = []  # In IronPython True is returned when no sheets are present
        else:
            self._sheets = list(test)
        self._all_object_names = self._solids + self._sheets + self._lines + self._points

    @pyaedt_function_handler()
    def _refresh_lines(self):
        try:
            test = self.oeditor.GetObjectsInGroup("Lines")
        except (TypeError, AttributeError):
            test = []
        if test is False:
            assert False, "Get Lines is failing"
        elif test is True or test is None:
            self._lines = []  # In IronPython True is returned when no lines are present
        else:
            self._lines = list(test)
        self._all_object_names = self._solids + self._sheets + self._lines + self._points

    @pyaedt_function_handler()
    def _refresh_points(self):
        try:
            test = self.oeditor.GetPoints()
        except (TypeError, AttributeError):
            test = []
        if test is False:
            assert False, "Get Points is failing"
        elif test is True or test is None:
            self._points = []  # In IronPython True is returned when no points are present
        else:
            self._points = list(test)
        self._all_object_names = self._solids + self._sheets + self._lines + self._points

    @pyaedt_function_handler()
    def _refresh_planes(self):
        self._planes = {}
        try:
            self._planes = {
                plane_name: self.oeditor.GetChildObject(plane_name)
                for plane_name in self.oeditor.GetChildNames("Planes")
            }
        except (TypeError, AttributeError):
            self._planes = {}
        self._all_object_names = self._solids + self._sheets + self._lines + self._points + list(self._planes.keys())

    @pyaedt_function_handler()
    def _refresh_unclassified(self):
        try:
            test = self.oeditor.GetObjectsInGroup("Unclassified")
        except (TypeError, AttributeError):
            test = []
        if test is None or test is False:
            self._unclassified = []
            self.logger.debug("Unclassified is failing")
        elif test is True:
            self._unclassified = []  # In IronPython True is returned when no unclassified are present
        else:
            self._unclassified = list(test)

    @pyaedt_function_handler()
    def _refresh_object_types(self):
        self._refresh_solids()
        self._refresh_sheets()
        self._refresh_lines()
        self._refresh_points()
        self._refresh_planes()
        self._refresh_unclassified()
        self._all_object_names = self._solids + self._sheets + self._lines + self._points + self._unclassified

    @pyaedt_function_handler()
    def _create_object(self, name, pid=0, use_cached=False, **kwargs):
        if use_cached:
            line_names = self._lines
        else:
            line_names = self.line_names
        if name in self._points:
            o = Point(self, name)
            self.points[name] = o
        elif name in self.planes.keys():
            o = Plane(self, name)
            self.planes[name] = o
        elif name in line_names:
            o = Object3d(self, name)
            if pid:
                new_id = pid
            else:
                new_id = o.id
            o = self.get_existing_polyline(o)
            self.objects[new_id] = o
            self._object_names_to_ids[o.name] = new_id
        else:
            o = Object3d(self, name)
            commands = self._get_commands(name)
            if commands and commands[0].startswith("CreatePolyline"):
                o = self.get_existing_polyline(o)
            if pid:
                new_id = pid
            else:
                new_id = o.id
            self.objects[new_id] = o
            self._object_names_to_ids[o.name] = new_id

        #  Set properties from kwargs.
        if len(kwargs) > 0:
            props = [
                attr
                for attr in dir(o)
                if isinstance(getattr(type(o), attr, None), property)  # Get a list of settable properties.
                and getattr(type(o), attr).fset is not None
            ]
            for k, val in kwargs.items():
                if k in props:  # Only try to set valid properties.
                    try:
                        setattr(o, k, val)
                    except:
                        self.logger.warning("Unable to assign " + str(k) + " to object " + o.name + ".")
                else:
                    self.logger.error("'" + str(k) + "' is not a valid property of the primitive ")
        return o

    @pyaedt_function_handler()
    def _default_object_attributes(self, name=None, matname=None, flags=""):
        if not matname:
            matname = self.defaultmaterial

        material, is_dielectric = self._check_material(matname, self.defaultmaterial)

        solve_inside = True if is_dielectric else False

        if not name:
            name = _uname()
        try:
            color = str(tuple(self._app.materials.material_keys[material].material_appearance)).replace(",", " ")
        except:
            color = "(132 132 193)"
        if material in ["vacuum", "air", "glass", "water_distilled", "water_fresh", "water_sea"]:
            transparency = 0.8
        else:
            transparency = 0.2
        args = [
            "NAME:Attributes",
            "Name:=",
            name,
            "Flags:=",
            flags,
            "Color:=",
            color,
            "Transparency:=",
            transparency,
            "PartCoordinateSystem:=",
            "Global",
            "SolveInside:=",
            solve_inside,
        ]

        if self.version >= "2019.3":
            args += [
                "MaterialValue:=",
                chr(34) + material + chr(34),
                "UDMId:=",
                "",
                "SurfaceMaterialValue:=",
                chr(34) + "Steel-oxidised-surface" + chr(34),
            ]
        else:
            args += ["MaterialName:=", material]

        if self.version >= "2021.2":
            args += [
                "ShellElement:=",
                False,
                "ShellElementThickness:=",
                "0mm",
                "IsMaterialEditable:=",
                True,
                "UseMaterialAppearance:=",
                False,
                "IsLightweight:=",
                False,
            ]

        return args

    @pyaedt_function_handler()
    def _crosssection_arguments(self, type, orient, width, topwidth, height, num_seg, bend_type=None):
        """Generate the properties array for the polyline cross-section."""
        arg_str = ["NAME:PolylineXSection"]

        # Set the default section type to "None"
        section_type = type
        if not section_type:
            section_type = "None"

        # Set the default orientation to "Auto"
        section_orient = orient
        if not section_orient:
            section_orient = "Auto"

        # Set the default bend-type to "Corner"
        section_bend = bend_type
        if not section_bend:
            section_bend = "Corner"

        # Ensure number-of segments is valid
        if num_seg:
            assert num_seg > 2, "Number of segments for a cross-section must be 0 or greater than 2."

        model_units = self.model_units
        arg_str += ["XSectionType:=", section_type]
        arg_str += ["XSectionOrient:=", section_orient]
        arg_str += ["XSectionWidth:=", _dim_arg(width, model_units)]
        arg_str += ["XSectionTopWidth:=", _dim_arg(topwidth, model_units)]
        arg_str += ["XSectionHeight:=", _dim_arg(height, model_units)]
        arg_str += ["XSectionNumSegments:=", "{}".format(num_seg)]
        arg_str += ["XSectionBendType:=", section_bend]

        return arg_str

    @pyaedt_function_handler()
    def _arg_with_dim(self, value, units=None):
        if units is None:
            units = self.model_units
        if type(value) is str:
            try:
                float(value)
                val = "{0}{1}".format(value, units)
            except:
                val = value
        else:
            val = "{0}{1}".format(value, units)
        return val

    @pyaedt_function_handler()
    def _pos_with_arg(self, pos, units=None):
        xpos = self._arg_with_dim(pos[0], units)
        if len(pos) < 2:
            ypos = self._arg_with_dim(0, units)
        else:
            ypos = self._arg_with_dim(pos[1], units)
        if len(pos) < 3:
            zpos = self._arg_with_dim(0, units)
        else:
            zpos = self._arg_with_dim(pos[2], units)

        return xpos, ypos, zpos

    @pyaedt_function_handler()
    def _str_list(self, theList):
        szList = ""
        for id in theList:
            o = self.objects[id]
            if len(szList):
                szList += ","
            szList += str(o.name)

        return szList

    @pyaedt_function_handler()
    def _find_object_from_edge_id(self, lval):
        objList = []
        objListSheets = self.sheet_names
        if len(objListSheets) > 0:
            objList.extend(objListSheets)
        objListSolids = self.solid_names
        if len(objListSolids) > 0:
            objList.extend(objListSolids)
        for obj in objList:
            val = self.oeditor.GetEdgeIDsFromObject(obj)
            if not (isinstance(val, bool)) and str(lval) in list(val):
                return obj
        return None

    @pyaedt_function_handler()
    def _find_object_from_face_id(self, lval):
        if self.oeditor is not None:
            objList = []
            objListSheets = self.sheet_names
            if len(objListSheets) > 0:
                objList.extend(objListSheets)
            objListSolids = self.solid_names
            if len(objListSolids) > 0:
                objList.extend(objListSolids)
            for obj in objList:
                face_ids = list(self.oeditor.GetFaceIDs(obj))
                if str(lval) in face_ids:
                    return obj

        return None

    @pyaedt_function_handler()
    def _get_native_component_properties(self, name):
        """Get properties of native component.

        Returns
        -------
        list
           List of names for native components.
        """
        native_comp_properties = None
        comps3d = self.oeditor.Get3DComponentDefinitionNames()
        component_name = None
        for comp3d in comps3d:
            if name in self.oeditor.Get3DComponentInstanceNames(comp3d):
                component_name = comp3d
                break
        if self._design_properties and self._design_properties.get("ModelSetup", None) and component_name:
            try:
                native_comp_entry = self._design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"][
                    "SubModelDefinitions"
                ]["NativeComponentDefinition"]
                if native_comp_entry:
                    if isinstance(native_comp_entry, (dict, OrderedDict)):
                        native_comp_entry = [native_comp_entry]
                    for data in native_comp_entry:
                        native_comp_name = data["SubmodelDefinitionName"]
                        if native_comp_name == component_name:
                            native_comp_properties = data
                            break
            except:
                return native_comp_properties

        return native_comp_properties

    @pyaedt_function_handler
    def _get_object_dict_by_material(self, material):
        obj_dict = {}
        for mat in material:
            objs = []
            for obj in self.object_list:
                if obj and ("[" in obj.material_name or "(" in obj.material_name):
                    if (
                        mat
                        == self._app.odesign.GetChildObject("3D Modeler")
                        .GetChildObject(obj.name)
                        .GetPropEvaluatedValue("Material")
                        .lower()
                    ):
                        objs.append(obj)
                elif obj and (obj.material_name == mat or obj.material_name == mat.lower()):
                    objs.append(obj)
            obj_dict[mat] = objs
        return obj_dict

    @pyaedt_function_handler()
    def convert_segments_to_line(self, object_name):
        """Convert a CreatePolyline list of segments to lines.

        This method applies to splines and 3-point arguments.

        Parameters
        ----------
        object_name : int, str, or :class:`pyaedt.modeler.cad.object3d.Object3d`
            Specified for the object.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` if it fails.

        References
        ----------

        >>> oEditor.ChangeProperty

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> edge_object = aedtapp.modeler.create_object_from_edge("my_edge")
        >>> aedtapp.modeler.generate_object_history(edge_object)
        >>> aedtapp.modeler.convert_segments_to_line(edge_object.name)

        """
        this_object = self._resolve_object(object_name)
        edges = this_object.edges
        for i in reversed(range(len(edges))):
            self.oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Geometry3DPolylineTab",
                        ["NAME:PropServers", this_object.name + ":CreatePolyline:1:Segment" + str(i)],
                        ["NAME:ChangedProps", ["NAME:Segment Type", "Value:=", "Line"]],
                    ],
                ]
            )
        return True
