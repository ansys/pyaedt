import copy
import json
import os
from collections import OrderedDict

from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.modeler.Modeler import CoordinateSystem
from pyaedt.modules.Boundary import BoundaryObject
from pyaedt.modules.MaterialLib import Material
from pyaedt.modules.Mesh import MeshOperation


def find_datasets(d, out_list):
    for k, v in d.items():
        if isinstance(v, (dict, OrderedDict)):
            find_datasets(v, out_list)
        else:
            a = copy.deepcopy(v)
            val = a
            if str(type(a)) == r"<type 'List'>":
                val = list(a)
            if "pwl(" in str(val):
                out_list.append(a[a.find("$") : a.find(",")])


class Configurations(object):
    """Configuration Class.
    It enables to export and import configuration options to be applied on a new/existing design.
    """

    def __init__(self, app):
        self._app = app
        self._setups = True
        self._parametrics = True
        self._optimizations = True
        self._boundaries = True
        self._object_properties = True
        self._mesh_operations = True
        self._coordinate_systems = True
        self._skip_if_exists = False
        self._tolerance = 1e-9
        self.export_materials = True

    @property
    def tolerance(self):
        """Get/Set the float value to be used in tolerance for face center matching in boundaries.

        Returns
        -------
        float
        """
        return self._tolerance

    @tolerance.setter
    def tolerance(self, val):
        self._tolerance = val

    @property
    def setups(self):
        """Define if setups have to be exported and imported/created into json file. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.setups = False # Disable the setup export
        """
        return self._setups

    @setups.setter
    def setups(self, val):
        self._setups = val

    @property
    def parametrics(self):
        """Define if parametrics have to be exported and imported/created into json file. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.parametrics = False # Disable the setup export
        """
        return self._parametrics

    @parametrics.setter
    def parametrics(self, val):
        self._parametrics = val

    @property
    def optimizations(self):
        """Define if optimizations have to be exported and imported/created into json file. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.optimizations = False # Disable the setup export
        """
        return self._optimizations

    @optimizations.setter
    def optimizations(self, val):
        self._optimizations = val

    @property
    def boundaries(self):
        """Define if boundaries have to be exported and imported/created into json file. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.boundaries = False # Disable the boundaries export
        """
        return self._boundaries

    @boundaries.setter
    def boundaries(self, val):
        self._boundaries = val

    @property
    def mesh_operations(self):
        """Define if Mesh Operations have to be exported and imported/created into json file. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.mesh_operations = False # Disable the object properties export
        """
        return self._mesh_operations

    @mesh_operations.setter
    def mesh_operations(self, val):
        self._mesh_operations = val

    @property
    def coordinate_systems(self):
        """Define if Coordinate Systems have to be exported and imported/created into json file. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.coordinate_systems = False # Disable the coordinate systems export
        """
        return self._coordinate_systems

    @coordinate_systems.setter
    def coordinate_systems(self, val):
        self._coordinate_systems = val

    @property
    def object_properties(self):
        """Define if object properties have to be exported and imported/created into json file. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.object_properties = False # Disable the object properties export
        """
        return self._object_properties

    @object_properties.setter
    def object_properties(self, val):
        self._object_properties = val

    @property
    def skip_if_exists(self):
        """Define if existing boundaries or properties have to be updated or not. Default is `True`.

        Returns
        -------
        bool

        Examples
        ---------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.configurations.skip_if_exists = False
        """
        return self._skip_if_exists

    @skip_if_exists.setter
    def skip_if_exists(self, val):
        self._skip_if_exists = val

    def _map_dict_value(self, dict_out, key, value):
        if not dict_out.get("mapping"):
            dict_out["mapping"] = {}
        dict_out["mapping"][key] = value

    @pyaedt_function_handler()
    def _map_object(self, props, dict_out):
        if "Objects" in props:
            for object in props["Objects"]:
                if isinstance(object, int):
                    self._map_dict_value(dict_out, object, self._app.modeler.objects[object].name)
        elif "Faces" in props:
            for face in props["Faces"]:
                for object in self._app.modeler.objects.values():
                    for f in object.faces:
                        if f.id == face:
                            self._map_dict_value(dict_out, face, [object.name, f.center])
        elif "Edges" in props:
            for edge in props["Edges"]:
                for object in self._app.modeler.objects.values():
                    for e in object.edges:
                        if e.id == edge:
                            self._map_dict_value(dict_out, edge, [object.name, e.midpoint])

    @pyaedt_function_handler()
    def _convert_objects(self, props, mapping):
        if "Objects" in props:
            new_list = []
            for object in props["Objects"]:
                if isinstance(object, int):
                    try:
                        new_list.append(mapping[str(object)])
                    except:
                        pass
                else:
                    new_list.append(object)
            props["Objects"] = new_list
        elif "Faces" in props:
            new_list = []
            for face in props["Faces"]:
                for f in self._app.modeler[mapping[str(face)][0]].faces:
                    if GeometryOperators.points_distance(f.center, mapping[str(face)][1]) < self.tolerance:
                        new_list.append(f.id)
            props["Faces"] = new_list

        elif "Edges" in props:
            new_list = []
            for edge in props["Edges"]:
                for e in self._app.modeler[mapping[str(edge)][0]].edges:
                    if GeometryOperators.points_distance(e.midpoint, mapping[str(edge)][1]) < self.tolerance:
                        new_list.append(e.id)
            props["Edges"] = new_list

    @pyaedt_function_handler()
    def _update_coordinate_system(self, name, props):
        update = False
        for cs in self._app.modeler.coordinate_systems:
            if cs.name == name:
                if not self.skip_if_exists:
                    cs.props = props
                    cs.update()
                update = True
        if update:
            return
        cs = CoordinateSystem(self._app.modeler, props, name)
        if cs.create():
            self._app.logger.info("Coordinate System {} added.".format(name))
            self._app.modeler.coordinate_systems.append(cs)
        else:
            self._app.logger.warning("Failed to add CS {} ".format(name))

    @pyaedt_function_handler()
    def _update_object(self, name, val):
        if name in self._app.modeler.object_names:
            arg = ["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", name]]]
            arg2 = ["NAME:ChangedProps"]
            if self._app.modeler[name].is3d or self._app.design_type in ["Maxwell 2D", "2D Extractor"]:
                arg2.append(["NAME:Material", "Value:=", chr(34) + val["Material"] + chr(34)])
                arg2.append(["NAME:Solve Inside", "Value:=", val["SolveInside"]])
            arg2.append(["NAME:Model", "Value:=", val["Model"]])
            if val["Group"]:
                arg2.append(["NAME:Group", "Value:=", val["Group"]])
            arg2.append(["NAME:Transparent", "Value:=", val["Transparency"]])
            arg2.append(["NAME:Color", "R:=", val["Color"][0], "G:=", val["Color"][1], "B:=", val["Color"][1]])
            arg2.append(["NAME:Orientation", "Value:=", val["CoordinateSystem"]])
            arg[1].append(arg2)
            self._app.modeler.oeditor.ChangeProperty(arg)

    @pyaedt_function_handler()
    def _update_boundaries(self, name, props):
        update = False
        for bound in self._app.boundaries:
            if bound and bound.name == name:
                if not self.skip_if_exists:
                    bound.props = props
                    bound.update()
                update = True
        if update:
            return
        bound = BoundaryObject(self._app, name, props, props["BoundType"])
        if bound.props.get("Independent", None):
            for b in self._app.boundaries:
                if b.type == "Independent" and b.props.get("ID", 999) == bound.props["Independent"]:
                    bound.auto_update = False
                    bound.props["Independent"] = b.name
                    bound.auto_update = True
        if bound.create():
            self._app.boundaries.append(bound)
            if props["BoundType"] in ["Coil Terminal", "Coil", "CoilTerminal"]:
                winding_name = ""
                for b in self._app.boundaries:
                    if b.props.get("ID", 999) == props.get("ParentBndID", -1):
                        winding_name = b.name
                        break
                if winding_name:
                    self._app.add_winding_coils(winding_name, name)

            self._app.logger.info("Boundary Operation {} added.".format(name))
        else:
            self._app.logger.warning("Failed to add Boundary {} ".format(name))

    @pyaedt_function_handler()
    def _update_mesh(self, name, props):
        update = False
        for mesh_el in self._app.mesh.meshoperations:
            if mesh_el.name == name:
                if not self.skip_if_exists:
                    mesh_el.props = props
                    mesh_el.update()
                update = True
        if update:
            return
        bound = MeshOperation(self._app.mesh, name, props, props["Type"])
        if bound.create():
            self._app.mesh.meshoperations.append(bound)
            self._app.logger.info("mesh Operation {} added.".format(name))
        else:
            self._app.logger.warning("Failed to add Mesh {} ".format(name))

    @pyaedt_function_handler()
    def _update_setup(self, name, props):
        update = False
        for setup_el in self._app.setups:
            if setup_el.name == name:
                if not self.skip_if_exists:
                    setup_el.props = props
                    setup_el.update()
                update = True
        if update:
            return
        if self._app.create_setup(name, props["SetupType"], props):
            self._app.logger.info("Setup {} added.".format(name))
        else:
            self._app.logger.warning("Failed to add Setup {} ".format(name))

    @pyaedt_function_handler()
    def import_config(self, config_file, apply_config=True):
        """Import configuration settings from a json file and apply it to the current design.

        Parameters
        ----------
        config_file : str
            Full path to json file.
        apply_config : bool, optional
            Define if imported json has to be applied to the current design or not.

        Returns
        -------
        dict
            Config dictionary.
        """
        with open(config_file) as json_file:
            dict_in = json.load(json_file)
        if not apply_config:
            return dict_in
        if dict_in.get("variables", None):
            for k, v in dict_in["variables"].items():
                self._app.variable_manager.set_variable(k, v)
        if dict_in.get("postprocessing_variables", None):
            for k, v in dict_in["postprocessing_variables"].items():
                self._app.variable_manager.set_variable(k, v, postprocessing=True)
        if self.export_materials and dict_in.get("datasets", None):
            if "datasets" in list(dict_in.keys()):
                for el, val in dict_in["datasets"].items():
                    numcol = len(val["Coordinates"]["DimUnits"])
                    xunit = val["Coordinates"]["DimUnits"][0]
                    yunit = val["Coordinates"]["DimUnits"][1]
                    zunit = ""

                    new_list = [
                        val["Coordinates"]["Points"][i : i + numcol]
                        for i in range(0, len(val["Coordinates"]["Points"]), numcol)
                    ]
                    xval = new_list[0]
                    yval = new_list[1]
                    zval = None
                    if numcol > 2:
                        zunit = val["Coordinates"]["DimUnits"][2]
                        zval = new_list[2]
                    self._app.create_dataset(
                        el[1:], xunit=xunit, yunit=yunit, zunit=zunit, xlist=xval, ylist=yval, zlist=zval
                    )
        if self.export_materials and dict_in.get("materials", None):
            for el, val in dict_in["materials"].items():
                if el.lower() in list(self._app.materials.material_keys.keys()):
                    newname = generate_unique_name(el)
                    self._app.logger.warning("Material %s already exists. Renaming to %s", el, newname)
                else:
                    newname = el
                newmat = Material(self._app, newname, val)
                newmat.update()
                self._app.materials.material_keys[newname] = newmat
        if self.coordinate_systems and dict_in.get("coordinatesystems", None):
            for name, props in dict_in["coordinatesystems"].items():
                self._update_coordinate_system(name, props)
        if self.object_properties and dict_in.get("objects", None):
            for obj, val in dict_in["objects"].items():
                self._update_object(obj, val)
            self._app.logger.info("Object Properties updated.")
        if self.boundaries and dict_in.get("boundaries", None):
            sort_order = sorted(dict_in["boundaries"], key=lambda x: dict_in["boundaries"][x].get("ID", 999))
            for name in sort_order:
                self._convert_objects(dict_in["boundaries"][name], dict_in["mapping"])
                self._update_boundaries(name, dict_in["boundaries"][name])
        # TODO implement MeshRegion handler
        if self.mesh_operations and dict_in.get("mesh", None):
            for name, props in dict_in["mesh"].items():
                self._convert_objects(props, dict_in["mapping"])
                self._update_mesh(name, props)
        if self.setups and dict_in.get("setups", None):
            for setup, props in dict_in["setups"].items():
                self._update_setup(setup, props)
        return dict_in

    @pyaedt_function_handler()
    def _export_variables(self, dict_out):
        if self._app.variable_manager.independent_variables:
            dict_out["variables"] = {}
        post_vars = self._app.variable_manager.post_processing_variables
        if post_vars:
            dict_out["postprocessing_variables"] = {}
        for k, v in self._app.variable_manager.independent_variables.items():
            if k not in post_vars:
                dict_out["variables"][k] = v.string_value
        for k, v in self._app.variable_manager.dependent_variables.items():
            if k not in post_vars:
                dict_out["variables"][k] = v.expression
        for k, v in post_vars.items():
            try:
                dict_out["postprocessing_variables"][k] = v.expression
            except AttributeError:
                dict_out["postprocessing_variables"][k] = v.string_value

    @pyaedt_function_handler()
    def _export_setups(self, dict_out):
        if self.setups and self._app.setups:
            dict_out["setups"] = {}
            for setup in self._app.setups:
                dict_out["setups"][setup.name] = setup.props

    @pyaedt_function_handler()
    def _export_optimizations(self, dict_out):
        if self.optimizations and self._app.optimizations.setups:
            dict_out["optimizations"] = {}
            for setup in self._app.optimizations.setups:
                dict_out["optimizations"][setup.name] = setup.props
        if self.parametrics and self._app.parametrics.setups:
            dict_out["parametrics"] = {}
            for setup in self._app.parametrics.setups:
                dict_out["parametrics"][setup.name] = setup.props

    @pyaedt_function_handler()
    def _export_boundaries(self, dict_out):
        if self.boundaries and self._app.boundaries:
            dict_out["boundaries"] = {}
            dict_out["mapping"] = {}
            for boundary in self._app.boundaries:
                dict_out["boundaries"][boundary.name] = boundary.props
                self._map_object(boundary.props, dict_out)

    @pyaedt_function_handler()
    def _export_coordinate_systems(self, dict_out):
        if self.coordinate_systems and self._app.modeler.coordinate_systems:
            dict_out["coordinatesystems"] = {}
            for cs in self._app.modeler.coordinate_systems:
                dict_out["coordinatesystems"][cs.name] = cs.props

    @pyaedt_function_handler()
    def _export_objects(self, dict_out):
        if self.object_properties:
            dict_out["objects"] = {}
            for obj, val in self._app.modeler.objects.items():
                dict_out["objects"][val.name] = {}
                if self._app.modeler[val.name].is3d or self._app.design_type in ["Maxwell 2D", "2D Extractor"]:
                    dict_out["objects"][val.name]["Material"] = val.material_name
                    dict_out["objects"][val.name]["SolveInside"] = val.solve_inside
                dict_out["objects"][val.name]["Model"] = val.model
                dict_out["objects"][val.name]["Group"] = val.group_name
                dict_out["objects"][val.name]["Transparency"] = val.transparency
                dict_out["objects"][val.name]["Color"] = val.color
                dict_out["objects"][val.name]["CoordinateSystem"] = val.part_coordinate_system

    @pyaedt_function_handler()
    def _export_mesh(self, dict_out):
        if self.mesh_operations and self._app.mesh.meshoperations:
            dict_out["mesh"] = {}
            for mesh in self._app.mesh.meshoperations:
                dict_out["mesh"][mesh.name] = mesh.props
                self._map_object(mesh.props, dict_out)

    @pyaedt_function_handler()
    def _export_materials(self, dict_out):
        if self.export_materials:
            output_dict = {}
            for el, val in self._app.materials.material_keys.items():
                output_dict[el] = copy.deepcopy(val._props)
            out_list = []
            find_datasets(output_dict, out_list)
            datasets = OrderedDict()
            for ds in out_list:
                if ds in list(self._app.project_datasets.keys()):
                    d = self._app.project_datasets[ds]
                    if d.z:
                        datasets[ds] = OrderedDict(
                            {
                                "Coordinates": OrderedDict(
                                    {
                                        "DimUnits": [d.xunit, d.yunit, d.zunit],
                                        "Points": [val for tup in zip(d.x, d.y, d.z) for val in tup],
                                    }
                                )
                            }
                        )
                    else:
                        datasets[ds] = OrderedDict(
                            {
                                "Coordinates": OrderedDict(
                                    {
                                        "DimUnits": [d.xunit, d.yunit],
                                        "Points": [val for tup in zip(d.x, d.y) for val in tup],
                                    }
                                )
                            }
                        )
            dict_out["materials"] = output_dict
            if datasets:
                dict_out["datasets"] = datasets

    @pyaedt_function_handler()
    def export_config(self, config_file=None):
        """Export current design properties to json file.

        Parameters
        ----------
        config_file : str, optional
            Full path to json file. If `None`, then the config file will be saved in working directory.

        Returns
        -------
        str
            Exported config file.
        """
        if not config_file:
            config_file = os.path.join(self._app.working_directory, generate_unique_name(self._app.design_name))
        dict_out = {}

        self._export_variables(dict_out)
        self._export_setups(dict_out)
        self._export_optimizations(dict_out)
        self._export_boundaries(dict_out)
        self._export_coordinate_systems(dict_out)
        self._export_objects(dict_out)
        self._export_mesh(dict_out)
        self._export_materials(dict_out)
        # update the json if it exists already
        if os.path.exists(config_file):
            with open(config_file, "r") as json_file:
                dict_in = json.load(json_file)
            for k, v in dict_in.items():
                if k not in dict_out:
                    dict_out[k] = v
                elif isinstance(v, dict):
                    for i, j in v.items():
                        if i not in dict_out[k]:
                            dict_out[k][i] = j
        # write the updated json to file
        with open(config_file, "w") as outfile:
            json.dump(dict_out, outfile, indent=4)
            self._app.logger.info("Configuration file {} exported correctly.".format(config_file))
        return config_file


class ConfigurationsIcepak(Configurations):
    """Configuration Class.
    It enables to export and import configuration options to be applied on a new/existing design.
    """

    def __init__(self, app):
        Configurations.__init__(self, app)

    @pyaedt_function_handler()
    def _update_object(self, name, val):
        if name in self._app.modeler.object_names:
            arg = ["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", name]]]
            arg2 = ["NAME:ChangedProps"]
            arg2.append(["NAME:Material", "Value:=", chr(34) + val["Material"] + chr(34)])
            arg2.append(["NAME:Solve Inside", "Value:=", val["SolveInside"]])
            arg2.append(
                [
                    "NAME:Surface Material",
                    "Value:=",
                    chr(34) + val.get("SurfaceMaterial", "Steel-oxidised-surface") + chr(34),
                ]
            )
            arg2.append(["NAME:Model", "Value:=", val["Model"]])
            if val["Group"]:
                arg2.append(["NAME:Group", "Value:=", val["Group"]])
            arg2.append(["NAME:Transparent", "Value:=", val["Transparency"]])
            arg2.append(["NAME:Color", "R:=", val["Color"][0], "G:=", val["Color"][1], "B:=", val["Color"][1]])
            arg2.append(["NAME:Orientation", "Value:=", val["CoordinateSystem"]])
            arg[1].append(arg2)
            self._app.modeler.oeditor.ChangeProperty(arg)

    @pyaedt_function_handler()
    def _update_mesh(self, name, props):
        update = False
        for mesh_el in self._app.mesh.meshoperations:
            if mesh_el.name == name:
                if not self.skip_if_exists:
                    mesh_el.props = props
                    mesh_el.update()
                update = True
        if update:
            return
        bound = MeshOperation(self._app.mesh, name, props, props["Type"])
        if bound.create():
            self._app.mesh.meshoperations.append(bound)
            self._app.logger.info("mesh Operation {} added.".format(name))
        else:
            self._app.logger.warning("Failed to add Mesh {} ".format(name))

    @pyaedt_function_handler()
    def import_config(self, config_file, apply_config=True):
        """Import configuration settings from a json file and apply it to the current design.

        Parameters
        ----------
        config_file : str
            Full path to json file.
        apply_config : bool, optional
            Define if imported json has to be applied to the current design or not.

        Returns
        -------
        dict
            Config dictionary.
        """
        with open(config_file) as json_file:
            dict_in = json.load(json_file)
        if not apply_config:
            return dict_in
        if self.export_materials and dict_in.get("datasets", None):
            if "datasets" in list(dict_in.keys()):
                for el, val in dict_in["datasets"].items():
                    numcol = len(val["Coordinates"]["DimUnits"])
                    xunit = val["Coordinates"]["DimUnits"][0]
                    yunit = val["Coordinates"]["DimUnits"][1]
                    zunit = ""

                    new_list = [
                        val["Coordinates"]["Points"][i : i + numcol]
                        for i in range(0, len(val["Coordinates"]["Points"]), numcol)
                    ]
                    xval = new_list[0]
                    yval = new_list[1]
                    zval = None
                    if numcol > 2:
                        zunit = val["Coordinates"]["DimUnits"][2]
                        zval = new_list[2]
                    self._app.create_dataset(
                        el[1:], xunit=xunit, yunit=yunit, zunit=zunit, xlist=xval, ylist=yval, zlist=zval
                    )
        if self.export_materials and dict_in.get("materials", None):
            for el, val in dict_in["materials"].items():
                if el.lower() in list(self._app.materials.material_keys.keys()):
                    newname = generate_unique_name(el)
                    self._app.logger.warning("Material %s already exists. Renaming to %s", el, newname)
                else:
                    newname = el
                newmat = Material(self._app, newname, val)
                newmat.update()
                self._app.materials.material_keys[newname] = newmat
        if self.coordinate_systems and dict_in.get("coordinatesystems", None):
            for name, props in dict_in["coordinatesystems"].items():
                self._update_coordinate_system(name, props)
        if self.object_properties and dict_in.get("objects", None):
            for obj, val in dict_in["objects"].items():
                self._update_object(obj, val)
            self._app.logger.info("Object Properties updated.")
        if self.boundaries and dict_in.get("boundaries", None):
            sort_order = sorted(dict_in["boundaries"], key=lambda x: dict_in["boundaries"][x].get("ID", 999))
            for name in sort_order:
                self._convert_objects(dict_in["boundaries"][name], dict_in["mapping"])
                self._update_boundaries(name, dict_in["boundaries"][name])
        if self.mesh_operations and dict_in.get("mesh", None):
            for name, props in dict_in["mesh"].items():
                self._convert_objects(props, dict_in["mapping"])
                self._update_mesh(name, props)
        if self.setups and dict_in.get("setups", None):
            for setup, props in dict_in["setups"].items():
                self._update_setup(setup, props)
        return dict_in

    @pyaedt_function_handler()
    def _export_objects(self, dict_out):
        if self.object_properties:
            dict_out["objects"] = {}
            for obj, val in self._app.modeler.objects.items():
                dict_out["objects"][val.name] = {}
                dict_out["objects"][val.name]["SurfaceMaterial"] = val.surface_material_name
                dict_out["objects"][val.name]["Material"] = val.material_name
                dict_out["objects"][val.name]["SolveInside"] = val.solve_inside
                dict_out["objects"][val.name]["Model"] = val.model
                dict_out["objects"][val.name]["Group"] = val.group_name
                dict_out["objects"][val.name]["Transparency"] = val.transparency
                dict_out["objects"][val.name]["Color"] = val.color
                dict_out["objects"][val.name]["CoordinateSystem"] = val.part_coordinate_system

    @pyaedt_function_handler()
    def _export_mesh(self, dict_out):
        # if self.mesh_operations and self._app.mesh.meshregions:
        #     dict_out["mesh"] = {}
        #     for mesh in self._app.mesh.meshoperations:
        #         dict_out["mesh"][mesh.name] = mesh.props
        #         self._map_object(mesh.props, dict_out)
        pass
