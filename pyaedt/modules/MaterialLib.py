# -*- coding: utf-8 -*-
"""
This module contains the `Materials` class.
"""
from __future__ import absolute_import  # noreorder

import copy
import json
import os

from pyaedt.generic.DataHandlers import _arg2dict
from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.Material import Material
from pyaedt.modules.Material import MatProperties
from pyaedt.modules.Material import OrderedDict
from pyaedt.modules.Material import SurfaceMaterial


class Materials(object):
    """Contains the AEDT materials database and all methods for creating and editing materials.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited parent object.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> materials = app.materials
    """

    def __init__(self, app):
        self._app = app
        self._color_id = 0
        self.odefinition_manager = self._app.odefinition_manager
        self.omaterial_manager = self._app.omaterial_manager
        self._desktop = self._app.odesktop
        self._oproject = self._app.oproject
        self.logger = self._app.logger
        self.logger.info("Successfully loaded project materials !")
        self.material_keys = self._get_materials()
        self.surface_material_keys = self._get_surface_materials()
        self._load_from_project()
        pass

    def __len__(self):
        return len(self.material_keys)

    def __iter__(self):
        return self.material_keys.itervalues()

    def __getitem__(self, item):
        item = item.lower()
        if item in list(self.material_keys.keys()):
            return self.material_keys[item]
        elif item in list(self.surface_material_keys.keys()):
            return self.surface_material_keys[item]

    @property
    def liquids(self):
        """Return the liquids materials. A liquid is a fluid with density greater or equal to 100Kg/m3.

        Returns
        -------
        list
            List of fluid materials.
        """
        mats = []
        for el, val in self.material_keys.items():
            if val.thermal_material_type == "Fluid" and val.mass_density.value and float(val.mass_density.value) >= 100:
                mats.append(el)
        return mats

    @property
    def gases(self):
        """Return the gas materials. A gas is a fluid with density lower than 100Kg/m3.

        Returns
        -------
        list
            List of all Gas materials.
        """
        mats = []
        for el, val in self.material_keys.items():
            if val.thermal_material_type == "Fluid" and val.mass_density.value and float(val.mass_density.value) < 100:
                mats.append(el)
        return mats

    @pyaedt_function_handler()
    def _get_materials(self):
        """Get materials."""
        mats = {}
        try:
            for ds in self._app.project_properies["AnsoftProject"]["Definitions"]["Materials"]:
                mats[ds.lower()] = Material(
                    self, ds.lower(), self._app.project_properies["AnsoftProject"]["Definitions"]["Materials"][ds]
                )
        except:
            pass
        return mats

    @pyaedt_function_handler()
    def _get_surface_materials(self):
        mats = {}
        try:
            for ds in self._app.project_properies["AnsoftProject"]["Definitions"]["SurfaceMaterials"]:
                mats[ds.lower()] = SurfaceMaterial(
                    self,
                    ds.lower(),
                    self._app.project_properies["AnsoftProject"]["Definitions"]["SurfaceMaterials"][ds],
                )
        except:
            pass
        return mats

    @pyaedt_function_handler()
    def checkifmaterialexists(self, mat):
        """Check if a material exists in AEDT.

        Parameters
        ----------
        mat : str
            Name of the material. If the material exists and is not in the materials database,
            it is added to this database.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDefinitionManager.GetProjectMaterialNames
        >>> oMaterialManager.GetData
        """
        mat = mat.lower()
        lista = [i.lower() for i in list(self.odefinition_manager.GetProjectMaterialNames())]
        if mat in lista:
            return True
        else:
            mattry = self.omaterial_manager.GetData(mat)
            if mattry:
                self._aedmattolibrary(mat)
                return True
            else:
                return False

    @pyaedt_function_handler()
    def check_thermal_modifier(self, mat):
        """Check a material to see if it has any thermal modifiers.

        Parameters
        ----------
        mat : str
            Name of the material. All properties for this material are checked
            for thermal modifiers.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        mat = mat.lower()
        exists = False
        if mat in self.material_keys:
            exists = True
        elif self.checkifmaterialexists(mat):
            self._load_from_project()
            exists = True
        if exists:
            omat = self.material_keys[mat]
            for el in MatProperties.aedtname:
                if omat.__dict__["_" + el].thermalmodifier:
                    return True
        return False

    @pyaedt_function_handler()
    def add_material(self, materialname, props=None):
        """Add a material with default values.

        When the added material object is returned, you can customize
        the material. This method does not update the material.

        Parameters
        ----------
        materialname : str
            Name of the material.
        props : dict, optional
            Material property dictionary. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Material.Material`

        References
        ----------

        >>> oDefinitionManager.AddMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> mat = hfss.materials.add_material("MyMaterial")
        >>> print(mat.conductivity.value)

        >>> oDefinitionManager.GetProjectMaterialNames
        >>> oMaterialManager.GetData

        """
        materialname = materialname.lower()
        self.logger.info("Adding new material to the Project Library: " + materialname)
        if materialname in self.material_keys:
            self.logger.warning("Warning. The material is already in the database. Change or edit the name.")
            return self.material_keys[materialname]
        else:
            material = Material(self, materialname, props)
            material.update()
            self.logger.info("Material has been added. Edit it to update in Desktop.")
            self.material_keys[materialname] = material
            return self.material_keys[materialname]

    @pyaedt_function_handler()
    def add_surface_material(self, material_name, emissivity=None):
        """Add a surface material.

        In AEDT, base properties are loaded from the XML database file ``amat.xml``
        or from the emissivity.

        Parameters
        ----------
        material_name : str
            Name of the surface material.
        emissivity : float, optional
            Emissivity value.

        Returns
        -------
        :class:`pyaedt.modules.SurfaceMaterial`

        References
        ----------

        >>> oDefinitionManager.AddSurfaceMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> mat = hfss.materials.add_surface_material("Steel", 0.85)
        >>> print(mat.emissivity.value)

        """

        materialname = material_name.lower()
        self.logger.info("Adding a surface material to the project library: " + materialname)
        if materialname in self.surface_material_keys:
            self.logger.warning("Warning. The material is already in the database. Change the name or edit it.")
            return self.surface_material_keys[materialname]
        else:
            material = SurfaceMaterial(self._app, materialname)
            if emissivity:
                material.emissivity = emissivity
                material.update()
            self.logger.info("Material has been added. Edit it to update in Desktop.")
            self.surface_material_keys[materialname] = material
            return self.surface_material_keys[materialname]

    @pyaedt_function_handler()
    def _create_mat_project_vars(self, matlist):
        matprop = {}
        tol = 1e-12
        for prop in MatProperties.aedtname:
            matprop[prop] = []
            for mat in matlist:
                try:
                    matprop[prop].append(float(mat.__dict__["_" + prop].value))
                except:
                    self.logger.warning("Warning. Wrong parsed property. Reset to 0")
                    matprop[prop].append(0)
            try:
                a = sum(matprop[prop])
                if a < tol:
                    del matprop[prop]
            except:
                pass
        return matprop

    @pyaedt_function_handler()
    def add_material_sweep(self, swargs, matname):
        """Create a sweep material made of an array of materials.

        If a material needs to have a dataset (thermal modifier), then a
        dataset is created. Material properties are loaded from the XML file
        database ``amat.xml``.

        Parameters
        ----------
        swargs : list
            List of materials to merge into a single sweep material.
        matname : str
            Name of the sweep material.
        enableTM : bool, optional
            Unavailable currently. Whether to enable the thermal modifier.
            The default is ``True``.

        Returns
        -------
        int
            Index of the project variable.

        References
        ----------

        >>> oDefinitionManager.AddMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.materials.add_material("MyMaterial")
        >>> hfss.materials.add_material("MyMaterial2")
        >>> hfss.materials.add_material_sweep(["MyMaterial", "MyMaterial2"], "Sweep_copper")
        """
        matsweep = []
        matname = matname.lower()
        for args in swargs:
            if args.lower() in [i.lower() for i in self.material_keys.keys()]:
                matsweep.append(self.material_keys[args.lower()])
            elif self.checkifmaterialexists(args):
                self._aedmattolibrary(args)
                matsweep.append(self.material_keys[args.lower()])

        mat_dict = self._create_mat_project_vars(matsweep)

        newmat = Material(self, matname)
        index = "$ID" + matname
        self._app[index] = 0
        for el in mat_dict:
            if el in list(mat_dict.keys()):
                self._app["$" + matname + el] = mat_dict[el]
                newmat.__dict__["_" + el].value = "$" + matname + el + "[" + index + "]"
                newmat._update_props(el, "$" + matname + el + "[" + index + "]", False)

        newmat.update()
        self.material_keys[matname] = newmat
        return index

    @pyaedt_function_handler()
    def duplicate_material(self, material, new_name):
        """Duplicate a material.

        Parameters
        ----------
        material : str
            Name of the material.
        new_name : str
            Name for the copy of the material.

        Returns
        -------
        :class:`pyaedt.modules.Material.Material`

        References
        ----------

        >>> oDefinitionManager.AddMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.materials.add_material("MyMaterial")
        >>> hfss.materials.duplicate_material("MyMaterial", "MyMaterial2")

        """
        if material.lower() not in list(self.material_keys.keys()):
            self.logger.error("Material {} is not present".format(material))
            return False
        newmat = Material(self, new_name.lower(), self.material_keys[material.lower()]._props)
        newmat.update()
        self.material_keys[new_name.lower()] = newmat
        return newmat

    @pyaedt_function_handler()
    def duplicate_surface_material(self, material, new_name):
        """Duplicate a surface material.

        Parameters
        ----------
         material : str
            Name of the surface material.
        new_name : str
            Name for the copy of the surface material.

        Returns
        -------
        :class:`pyaedt.modules.SurfaceMaterial`

        References
        ----------

        >>> oDefinitionManager.AddSurfaceMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.materials.add_surface_material("MyMaterial")
        >>> hfss.materials.duplicate_surface_material("MyMaterial", "MyMaterial2")
        """
        if not material.lower() in list(self.surface_material_keys.keys()):
            self.logger.error("Material {} is not present".format(material))
            return False
        newmat = SurfaceMaterial(self, new_name.lower(), self.surface_material_keys[material.lower()]._props)
        newmat.update()
        self.surface_material_keys[new_name.lower()] = newmat
        return newmat

    @pyaedt_function_handler()
    def remove_material(self, material, library="Project"):
        """Remove a material.

        Parameters
        ----------
        material : str
            Name of the material.
        library : str, optional
            Name of the library containing this material.
            The default is ``"Project"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDefinitionManager.RemoveMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> hfss.materials.add_material("MyMaterial")
        >>> hfss.materials.remove_material("MyMaterial")

        """
        mat = material.lower()
        if mat not in list(self.material_keys.keys()):
            self.logger.error("Material {} is not present".format(mat))
            return False
        self.odefinition_manager.RemoveMaterial(mat, True, "", library)
        del self.material_keys[mat]
        return True

    @property
    def conductors(self):
        """Conductors in the material database.

        Returns
        -------
        list
            List of conductors in the material database.

        """
        data = []
        for key, mat in self.material_keys.items():
            if mat.is_conductor():
                data.append(key)
        return data

    @property
    def dielectrics(self):
        """Dielectrics in the material database.

        Returns
        -------
        list
            List of dielectrics in the material database.

        """
        data = []
        for key, mat in self.material_keys.items():
            if mat.is_dielectric():
                data.append(key)
        return data

    def _load_from_project(self):
        mats = self.odefinition_manager.GetProjectMaterialNames()
        for el in mats:
            if el not in list(self.material_keys.keys()):
                try:
                    self._aedmattolibrary(el)
                except Exception as e:
                    self.logger.info("aedmattolibrary failed for material %s", el)

    @pyaedt_function_handler()
    def _aedmattolibrary(self, matname):
        matname = matname.lower()
        props = {}
        _arg2dict(list(_retry_ntimes(20, self.omaterial_manager.GetData, matname)), props)
        values_view = props.values()
        value_iterator = iter(values_view)
        first_value = next(value_iterator)
        newmat = Material(self, matname, first_value)

        self.material_keys[matname] = newmat
        return True

    @pyaedt_function_handler()
    def export_materials_to_file(self, full_json_path):
        """Export all materials to a JSON file.

        Parameters
        ----------
        full_json_path : str
            Full path and name of the JSON file to export to.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

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

        # Data to be written
        output_dict = {}
        for el, val in self.material_keys.items():
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
        json_dict = {}
        json_dict["materials"] = output_dict
        if datasets:
            json_dict["datasets"] = datasets
        if not is_ironpython:
            with open(full_json_path, "w") as fp:
                json.dump(json_dict, fp, indent=4)
        else:
            temp_path = full_json_path.replace(".json", "_temp.json")
            with open(temp_path, "w") as fp:
                json.dump(json_dict, fp, indent=4)
            with open(temp_path, "r") as file:
                filedata = file.read()
            filedata = filedata.replace("True", "true")
            filedata = filedata.replace("False", "false")
            with open(full_json_path, "w") as file:
                file.write(filedata)
            os.remove(temp_path)
        return True

    @pyaedt_function_handler()
    def import_materials_from_file(self, full_json_path):
        """Import and create materials from a JSON file.

        Parameters
        ----------
        full_json_path : str
            Full path and name for the JSON file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        with open(full_json_path, "r") as json_file:
            data = json.load(json_file)

        if "datasets" in list(data.keys()):
            for el, val in data["datasets"].items():
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

        for el, val in data["materials"].items():
            if el.lower() in list(self.material_keys.keys()):
                newname = generate_unique_name(el)
                self.logger.warning("Material %s already exists. Renaming to %s", el, newname)
            else:
                newname = el
            newmat = Material(self, newname, val)
            newmat.update()
            self.material_keys[newname] = newmat
        return True
