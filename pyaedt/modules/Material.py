"""
This module contains these data classes for creating a material library:

* `BasicValue`
* `ClosedFormTM`
* `CommonMaterial`
* `Dataset`
* `MatProperties`
* `MatProperty`
* `Material`
* `SurMatProperties`
* `SufaceMaterial`

"""
from collections import OrderedDict
from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.generic.DataHandlers import _dict2arg


class MatProperties(object):
    """Contains a list of constant names for all materials with
    mappings to their internal XML names.

    Internal names are used in scripts, and XML names are used in the XML syntax.
    """

    aedtname = [
        "permittivity",
        "permeability",
        "conductivity",
        "dielectric_loss_tangent",
        "magnetic_loss_tangent",
        "thermal_conductivity",
        "mass_density",
        "specific_heat",
        "thermal_expansion_coefficient",
        "youngs_modulus",
        "poissons_ratio",
        "diffusivity",
        "molecular_mass",
        "viscosity",
        "core_loss_kh",
        "core_loss_kc",
        "core_loss_ke",
    ]
    defaultvalue = [1.0, 1.0, 0, 0, 0, 0.01, 0, 0, 0, 0, 0, 0.8, 0, 0, 0, 0, 0, 0]
    defaultunit = [
        None,
        None,
        "[siemens m^-1]",
        None,
        None,
        "[W m^-1 C^-1]",
        "[Kg m^-3]",
        "[J Kg^-1 C^-1]",
        "[C^-1]",
        "[Pa]",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    diel_order = [3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 1]
    cond_order = [2, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 3]

    @classmethod
    def get_defaultunit(cls, aedtname=None):
        """Retrieve the default unit for a full name or a category name.

        Parameters
        ----------
        aedtname : str, optional
            AEDT full name or category name. The default is ``None``.

        Returns
        -------
        str
            Default unit if it exists.

        """
        if aedtname:
            return cls.defaultunit[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: Either the full name or category name must be defined.")

    @classmethod
    def get_defaultvalue(cls, aedtname):
        """Retrieve the default value for a full name or a category name.

        Parameters
        ----------
        aedtname : str
             AEDT full name or category name. The default is ``None``.

        Returns
        -------
        float
            Default value if it exists.

        """
        if aedtname:
            return cls.defaultvalue[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: Either the full name or category name must be defined.")


class SurfMatProperties(object):
    """Contains a list of constant names for all surface materials with
    mappings to their internal XML names.

    Internal names are used in scripts, and XML names are used in the XML syntax.

    """

    aedtname = [
        "surface_emissivity",
        "surface_roughness",
        "surface_diffuse_absorptance",
        "surface_incident_absorptance",
    ]
    defaultvalue = [1.0, 0, 0.4, 0.4]
    defaultunit = [None, "[m]", None, None]

    @classmethod
    def get_defaultunit(cls, aedtname=None):
        """Retrieve the default unit for a full name or a category name.

        Parameters
        ----------
        aedtname : str, optional
            AEDT full name or category name. The default is ``None``.

        Returns
        -------
        str
            Default unit if it exists.

        """
        if aedtname:
            return cls.defaultunit[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: either fullname or catname MUST be defined")

    @classmethod
    def get_defaultvalue(cls, aedtname=None):
        """Get the default value for a full name or a category name.

        Parameters
        ----------
        aedtname : str, optional
            AEDT full name or category name. The default is ``None``.

        Returns
        -------
        float
            Default value if it exists.

        """
        if aedtname:
            return cls.defaultvalue[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: Either the full name or category name must be defined.")


class ClosedFormTM(object):
    """Manges closed-form thermal modifiers."""

    Tref = "22cel"
    C1 = 0
    C2 = 0
    TL = "-273.15cel"
    TU = "1000cel"
    autocalculation = True
    TML = 1000
    TMU = 1000


class Dataset(object):
    """Manages datasets."""

    ds = []
    unitx = ""
    unity = ""
    unitz = ""
    type = "Absolute"
    namex = ""
    namey = ""
    namez = None


class BasicValue(object):
    """Manages thermal modifier calculations."""

    value = None
    dataset = None
    thermalmodifier = None


class MatProperty(object):
    """Manages simple, anisotropic, tensor, and non-linear properties.

    Parameters
    ----------
    material : :class:`pyaedt.modules.Material.Material`
        Inherited parent object.
    name : str
        Name of the material property.
    val :
        The default is ``None``.
    thermalmodifier
        The default is ``None``.

    Examples
    --------
    >>>from pyaedt import Hfss
    >>>app = Hfss()
    >>>matproperty = app.materials["copper"].conductivity
    """
    def __init__(self, material, name, val=None, thermalmodifier=None):
        self._material = material
        self.logger = self._material.logger
        self._type = "simple"
        self.name = name
        self._property_value = [BasicValue()]
        self._unit = None
        if val is not None and isinstance(val, (str, float, int)):
            self.value = val
        elif val is not None and val["property_type"] == "AnisoProperty":
            self.type = "anisotropic"
            self.value = [val["component1"], val["component2"], val["component3"]]
        if not isinstance(thermalmodifier, list):
            thermalmodifier = [thermalmodifier]
        for tm in thermalmodifier:
            if tm:
                if tm["use_free_form"]:
                    self._property_value[tm["Index:"]].thermalmodifier = tm["free_form_value"]
                else:
                    self._property_value[tm["Index:"]].thermalmodifier = ClosedFormTM()
                    self._property_value[tm["Index:"]].thermalmodifier.Tref = tm["Tref"]
                    self._property_value[tm["Index:"]].thermalmodifier.C1 = tm["C1"]
                    self._property_value[tm["Index:"]].thermalmodifier.C2 = tm["C2"]
                    self._property_value[tm["Index:"]].thermalmodifier.TL = tm["TL"]
                    self._property_value[tm["Index:"]].thermalmodifier.TU = tm["TU"]
                    self._property_value[tm["Index:"]].thermalmodifier.autocalculation = tm["auto_calculation"]

    @property
    def type(self):
        """Type of the material property.

        Parameters
        ----------
        type : str
            Type of properties. Options are ``simple"``,
            ``"anisotropic",`` ``"tensor"``, and ``"nonlinear",``
        """
        return self._type

    @type.setter
    def type(self, type):
        self._type = type
        if self._type == "simple":
            self._property_value = [self._property_value[0]]
        elif self._type == "anisotropic":
            self._property_value = [self._property_value[0] for i in range(3)]
        elif self._type == "tensor":
            self._property_value = [self._property_value[0] for i in range(9)]
        elif self._type == "nonlinear":
            self._property_value = [self._property_value[0]]

    @property
    def value(self):
        """Value for a material property."""
        if len(self._property_value) == 1:
            return self._property_value[0].value
        else:
            return [i.value for i in self._property_value]

    @value.setter
    def value(self, val):
        if isinstance(val, list):
            i = 0
            for el in val:
                if i >= len(self._property_value):
                    self._property_value.append(BasicValue())

                self._property_value[i].value = el
                i += 1
        else:
            self._property_value[0].value = val

    @property
    def unit(self):
        """Units for a material property value."""
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = unit

    @property
    def data_set(self):
        """Dataset."""
        if len(self._property_value) == 1:
            return self._property_value[0].dataset
        else:
            return [i.dataset for i in self._property_value]

    @property
    def thermalmodifier(self):
        """Thermal modifier."""
        if len(self._property_value) == 1:
            return self._property_value[0].thermalmodifier
        else:
            return [i.thermalmodifier for i in self._property_value]

    @thermalmodifier.setter
    def thermalmodifier(self, thermal_value):
        """Thermal modifier.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        if isinstance(thermal_value, str):
            self._add_thermal_modifier(thermal_value, 0)
        else:
            for i in thermal_value:
                self._add_thermal_modifier(i, thermal_value.index(i))

    def _add_thermal_modifier(self, formula, index):
        """Add a thermal modifier.

        Parameters
        ----------
        formula : str
            Formula to apply.
        index : int
            Value for the index.

        Returns
        -------
        type

        """
        if "ModifierData" not in self._material._props:
            tm = OrderedDict(
                {
                    "Property:": self.name,
                    "Index:": index,
                    "prop_modifier": "thermal_modifier",
                    "use_free_form": True,
                    "free_form_value": formula,
                }
            )
            self._material._props["ModifierData"] = OrderedDict({"ThermalModifierData": OrderedDict(
                {"modifier_data": "thermal_modifier_data",
                 "all_thermal_modifiers": OrderedDict({"one_thermal_modifier": tm}), })})
        else:
            for tmname in self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]:
                if isinstance(
                        self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname],
                        list):
                    found = False
                    for tm in self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][
                        tmname
                    ]:
                        if self.name == tm["Property:"] and index == tm["Index:"]:
                            found = True
                            tm["use_free_form"] = True
                            tm["free_form_value"] = formula
                            tm.pop("Tref", None)
                            tm.pop("C1", None)
                            tm.pop("C2", None)
                            tm.pop("TL", None)
                            tm.pop("TU", None)
                    if not found:
                        tm = OrderedDict(
                            {
                                "Property:": self.name,
                                "Index:": index,
                                "prop_modifier": "thermal_modifier",
                                "use_free_form": True,
                                "free_form_value": formula,
                            }
                        )
                        self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][
                            tmname
                        ].append(tm)
                elif (
                    self.name
                    == self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname][
                        "Property:"
                    ]
                    and index
                    == self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname][
                        "Index:"
                    ]
                ):
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname][
                        "use_free_form"
                    ] = True
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname][
                        "free_form_value"
                    ] = formula
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop(
                        "Tref", None
                    )
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop(
                        "C1", None
                    )
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop(
                        "C2", None
                    )
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop(
                        "TL", None
                    )
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop(
                        "TU", None
                    )

                else:
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname] = [
                        self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname]
                    ]
                    tm = OrderedDict(
                        {
                            "Property:": self.name,
                            "Index:": index,
                            "prop_modifier": "thermal_modifier",
                            "use_free_form": True,
                            "free_form_value": formula,
                        }
                    )
                    self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][
                        tmname].append(tm)
        return self._material.update()

    def add_thermal_modifier_free_form(self, formula, index=0):
        """Add a thermal modifier to a material property using a free-form formula.

        Parameters
        ----------
        formula : str
            Full formula to apply.
        index : int, optional
            Value for the index. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDefinitionManager.EditMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss(specified_version="2021.2")
        >>> mat1 = hfss.materials.add_material("new_copper2")
        >>> mat1.add_thermal_modifier_free_form("if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))")
        """
        self._property_value[index].thermalmodifier = formula
        return self._add_thermal_modifier(formula, index)

    def add_thermal_modifier_dataset(self, dataset_name, index=0):
        """Add a thermal modifier to a material property using an existing dataset.

        Parameters
        ----------
        dataset_name : str
            Name of the project dataset.
        index : int, optional
            Value for the index. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.


        References
        ----------

        >>> oDefinitionManager.EditMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss(specified_version="2021.2")
        >>> mat1 = hfss.materials.add_material("new_copper2")
        >>> mat1.add_thermal_modifier_dataset("$ds1")
        """

        formula = "pwl({}, Temp)".format(dataset_name)
        self._property_value[index].thermalmodifier = formula
        self._add_thermal_modifier(formula, index)

    def add_thermal_modifier_closed_form(
        self, tref=22, c1=0.0001, c2=1e-6, tl=-273.15, tu=1000, units="cel", auto_calc=True, tml=1000, tmu=1000, index=0
    ):
        """Add a thermal modifier to a material property using a closed-form formula.

        Parameters
        ----------
        tref : float, optional
            Reference temperature. The default is ``22``.
        c1 : float, optional
            First coefficient value. The default is ``0.0001``.
        c2 : float, optional
            Second coefficient value. The default is ``1e-6``.
        tl : float, optional
            Lower temperature limit. The default is ``273.15``.
        tu : float, optional
            Upper temperature limit. The default is ``1000``.
        units : str, optional
            Units for the reference temperature. The default
            is ``"cel"``.
        auto_calc : bool, optional
            Whether to calculate the lower and upper
            temperature limits automatically. The default is
            ``True``.
        tml : float, optional
            Lower temperature limit when ``auto_calc=True.``
            The default is ``1000``.
        tmu : float, optional
            Upper temperature limit when ``auto_calc=True.``
            The default is ``1000``.
        index : int, optional
            Value for the index. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDefinitionManager.EditMaterial

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss(specified_version="2021.2")
        >>> mat1 = hfss.materials.add_material("new_copper2")
        >>> mat1.permittivity.add_thermal_modifier_closed_form(c1 = 1e-3)
        """

        if index > len(self._property_value):
            self.logger.error(
                "Wrong index number. Index must be 0 for simple or nonlinear properties,"
                " <=2 for anisotropic materials, <=9 for Tensors"
            )
            return False
        self._property_value[index].thermalmodifier = ClosedFormTM()
        self._property_value[index].thermalmodifier.Tref = str(tref) + units
        self._property_value[index].thermalmodifier.C1 = str(c1)
        self._property_value[index].thermalmodifier.C2 = str(c2)
        self._property_value[index].thermalmodifier.TL = str(tl) + units
        self._property_value[index].thermalmodifier.TU = str(tu) + units
        self._property_value[index].thermalmodifier.autocalculation = auto_calc
        if not auto_calc:
            self._property_value[index].thermalmodifier.TML = tml
            self._property_value[index].thermalmodifier.TMU = tmu
        if auto_calc:
            tm_new = OrderedDict(
                {
                    "Property:": self.name,
                    "Index:": index,
                    "prop_modifier": "thermal_modifier",
                    "use_free_form": False,
                    "Tref": str(tref) + units,
                    "C1": str(c1),
                    "C2": str(c2),
                    "TL": str(tl) + units,
                    "TU": str(tu) + units,
                    "auto_calculation": True,
                }
            )
        else:
            tm_new = OrderedDict(
                {
                    "Property:": self.name,
                    "Index:": index,
                    "prop_modifier": "thermal_modifier",
                    "use_free_form": False,
                    "Tref": str(tref) + units,
                    "C1": str(c1),
                    "C2": str(c2),
                    "TL": str(tl) + units,
                    "TU": str(tu) + units,
                    "auto_calculation": False,
                    "TML": str(tml),
                    "TMU": str(tmu),
                }
            )
        if "ModifierData" not in self._material._props:
            self._material._props["ModifierData"] = OrderedDict(
                {
                    "ThermalModifierData": OrderedDict(
                        {
                            "modifier_data": "thermal_modifier_data",
                            "all_thermal_modifiers": OrderedDict({"one_thermal_modifier": tm_new}),
                        }
                    )
                }
            )
        else:
            for tmname in self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]:
                tml = self._material._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname]
                if isinstance(tml, list):
                    found = False
                    for tm in tml:
                        if self.name == tm["Property:"] and index == tm["Index:"]:
                            found = True
                            tm["use_free_form"] = False
                            tm.pop("free_form_value", None)
                            tm["Tref"] = str(tref) + units
                            tm["C1"] = str(c1)
                            tm["C2"] = str(c2)
                            tm["TL"] = str(tl) + units
                            tm["TU"] = str(tu) + units
                            tm["auto_calculation"] = auto_calc
                            if auto_calc:
                                tm["TML"] = tml
                                tm["TMU"] = tmu
                            else:
                                tm.pop("TML", None)
                                tm.pop("TMU", None)
                    if not found:
                        tml.append(tm_new)
                elif self.name == tml["Property:"] and index == tml["Index:"]:
                    tml["use_free_form"] = False
                    tml.pop("free_form_value", None)
                    tml["Tref"] = str(tref) + units
                    tml["C1"] = str(c1)
                    tml["C2"] = str(c1)
                    tml["TL"] = str(tl) + units
                    tml["TU"] = str(tl) + units
                    tml["auto_calculation"] = auto_calc
                    if not auto_calc:
                        tml["TML"] = str(tml)
                        tml["TMU"] = str(tmu)
                    else:
                        tml.pop("TML", None)
                        tml.pop("TMU", None)
                else:
                    tml = [tml]
                    tml.append(tm_new)
        return self._material.update()


class CommonMaterial(object):
    """Manages datasets with frequency-dependent materials.

    Parameters
    ----------
    materials : :class:`pyaedt.modules.MaterialLib.Materials`

    name : str

    props : dict
        The default is ``None``.

    """
    def __init__(self, materials, name, props=None):
        self._materials = materials
        self.odefinition_manager = self._materials.odefinition_manager
        self._omaterial_manager = self._materials.omaterial_manager

        self._oproject = self._materials._oproject
        self.logger = self._materials.logger
        self.name = name
        self.coordinate_system = ""
        if props:
            self._props = props
        else:
            self._props = OrderedDict()
        if "CoordinateSystemType" in self._props:
            self.coordinate_system = self._props["CoordinateSystemType"]
        else:
            self._props["CoordinateSystemType"] = "Cartesian"
            self.coordinate_system = "Cartesian"
        if "BulkOrSurfaceType" in self._props:
            self.bulkorsurface = self._props["BulkOrSurfaceType"]
        else:
            self._props["BulkOrSurfaceType"] = 1
        if "ModTime" in self._props:
            self._modtime = self._props["ModTime"]
            del self._props["ModTime"]
        if "LibLocation" in self._props:
            self.lib_location = self._props["LibLocation"]
            del self._props["LibLocation"]
        if "ModSinceLib" in self._props:
            self.mod_since_lib = self._props["ModSinceLib"]
            del self._props["ModSinceLib"]

    @aedt_exception_handler
    def _get_args(self, props=None):
        """Retrieve the arguments for a property.

        Parameters
        ----------
        prop : str, optoinal
            Name of the property.  The default is ``None``.
        """
        if not props:
            props = self._props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    def _update_props(self, propname, provpavlue, update_aedt=True):
        """Update properties.

        Parameters
        ----------
        propname : str
            Name of the property.
        provpavlue :
            Value of the property.
        update_aedt : bool, optional
            Whether to update the property in AEDT. The default is ``True``.

        """
        if (
            isinstance(provpavlue, list)
            and self.__dict__["_" + propname].type != "simple"
            and self.__dict__["_" + propname].type != "nonlinear"
        ):
            i = 1
            for val in provpavlue:
                self._props[propname]["component" + str(i)] = str(val)
                i += 1
            if update_aedt:
                return self.update()
        elif isinstance(provpavlue, (str, float, int)):
            self._props[propname] = str(provpavlue)
            if update_aedt:
                return self.update()
        else:
            return False


class Material(CommonMaterial, object):
    """Manages material properties.

    Parameters
    ----------
    materiallib : :class:`pyaedt.modules.MaterialLib.Materials`
        Inherited parent object.
    name : str
        Name of the material.
    props  :
        The default is ``None``.

    Examples
    --------
    >>>from pyaedt import Hfss
    >>>app = Hfss()
    >>>material = app.materials["copper"]
    """

    def __init__(self, materiallib, name, props=None):
        CommonMaterial.__init__(self, materiallib, name, props)
        self.thermal_material_type = "Solid"
        if "thermal_material_type" in self._props:
            self.thermal_material_type = self._props["thermal_material_type"]["Choice"]
        if "PhysicsTypes" in self._props:
            self.physics_type = self._props["PhysicsTypes"]["set"]
        else:
            self.physics_type = ["Electromagnetic", "Thermal", "Structural"]
            self._props["PhysicsTypes"] = OrderedDict({"set": ["Electromagnetic", "Thermal", "Structural"]})
        if "AttachedData" in self._props:
            self._material_appearance = []
            self._material_appearance.append(self._props["AttachedData"]["MatAppearanceData"]["Red"])
            self._material_appearance.append(self._props["AttachedData"]["MatAppearanceData"]["Green"])
            self._material_appearance.append(self._props["AttachedData"]["MatAppearanceData"]["Blue"])
        else:
            self._material_appearance = [128, 128, 128]
            self._props["AttachedData"] = OrderedDict(
                {
                    "MatAppearanceData": OrderedDict(
                        {"property_data": "appearance_data", "Red": 128, "Green": 128, "Blue": 128}
                    )
                }
            )

        for property in MatProperties.aedtname:
            if property in self._props:
                mods = None
                if "ModifierData" in self._props:
                    modifiers = self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]
                    for mod in modifiers:
                        if isinstance(modifiers[mod], list):
                            for one_tm in modifiers[mod]:
                                if one_tm["Property:"] == property:
                                    if mods:
                                        mods = [mods]
                                        mods.append(one_tm)
                                    else:
                                        mods = one_tm
                        else:
                            if modifiers[mod]["Property:"] == property:
                                mods = modifiers[mod]
                self.__dict__["_" + property] = MatProperty(self, property, self._props[property], mods)
            else:
                self.__dict__["_" + property] = MatProperty(
                    self, property, MatProperties.get_defaultvalue(aedtname=property), None
                )
        pass

    @property
    def material_appearance(self):
        """Material Appearance specified as an RGB list.

        Returns
        -------
        list
            Color of the material in RGB.  Values are in the range ``[0, 255]``.

        Examples
        --------
        Create a new material with color ``[0, 153, 153]`` (darker cyan).

        >>> from pyaedt import Hfss
        >>> hfss = Hfss(specified_version="2021.2")
        >>> mat1 = hfss.materials.add_material("new_material")
        >>> rgbcolor = mat1.material_appearance
        >>> mat1.material_appearance = [0, 153, 153]
        """
        return self._material_appearance

    @material_appearance.setter
    def material_appearance(self, rgb):
        if not isinstance(rgb, (list, tuple)):
            raise TypeError("`material_apperance` must be a list or tuple")
        if len(rgb) != 3:
            raise ValueError("`material_appearance` must be three items (RGB)")
        value_int = []
        for rgb_item in rgb:
            rgb_int = int(rgb_item)
            if rgb_int < 0 or rgb_int > 255:
                raise ValueError("RGB value must be between 0 and 255")
            value_int.append(rgb_int)
        self._material_appearance = value_int
        self._props["AttachedData"] = OrderedDict(
            {
                "MatAppearanceData": OrderedDict(
                    {
                        "property_data": "appearance_data",
                        "Red": value_int[0],
                        "Green": value_int[1],
                        "Blue": value_int[2],
                    }
                )
            }
        )

    @property
    def permittivity(self):
        """Permittivity.

        Returns
        -------
        str
            Permittivity of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._permittivity

    @permittivity.setter
    def permittivity(self, value):
        self._permittivity.value = value
        self._update_props("permittivity", value)

    @property
    def permeability(self):
        """Permeability.

        Returns
        -------
        str or float
            Permeability of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._permeability

    @permeability.setter
    def permeability(self, value):

        self._permeability.value = value
        self._update_props("permeability", value)

    @property
    def conductivity(self):
        """Conductivity.

        Returns
        -------
        str or float
            Conductivity of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._conductivity

    @conductivity.setter
    def conductivity(self, value):
        self._conductivity.value = value
        self._update_props("conductivity", value)

    @property
    def dielectric_loss_tangent(self):
        """Dielectric loss tangent.

        Returns
        -------
        str or float
            Dielectric loss tangent of the material.
        """
        return self._dielectric_loss_tangent

    @dielectric_loss_tangent.setter
    def dielectric_loss_tangent(self, value):
        self._dielectric_loss_tangent.value = value
        self._update_props("dielectric_loss_tangent", value)

    @property
    def magnetic_loss_tangent(self):
        """Magnetic loss tangent.

        Returns
        -------
        str or float
            Magnetic loss tangent of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._magnetic_loss_tangent

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        self._magnetic_loss_tangent.value = value
        self._update_props("magnetic_loss_tangent", value)

    @property
    def thermal_conductivity(self):
        """Thermal conductivity.

        Returns
        -------
        str or float
            Thermal conductivity of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._thermal_conductivity

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        self._thermal_conductivity.value = value
        self.physics_type = ["Electromagnetic", "Thermal", "Structural"]
        self._props["PhysicsTypes"] = OrderedDict({"set": ["Electromagnetic", "Thermal", "Structural"]})
        self._update_props("thermal_conductivity", value)

    @property
    def mass_density(self):
        """Mass density.

        Returns
        -------
        str or float
            Mass density of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._mass_density

    @mass_density.setter
    def mass_density(self, value):
        self._mass_density.value = value
        self._update_props("mass_density", value)

    @property
    def specific_heat(self):
        """Specific heat.

        Returns
        -------
        str or float
            Specific heat of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._specific_heat

    @specific_heat.setter
    def specific_heat(self, value):
        self._specific_heat.value = value
        self._update_props("specific_heat", value)

    @property
    def thermal_expansion_coefficient(self):
        """Thermal expansion coefficient.

        Returns
        -------
        str or float
            Thermal expansion coefficient of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._thermal_expansion_coefficient

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        self._thermal_expansion_coefficient.value = value
        self._update_props("thermal_expansion_coefficient", value)

    @property
    def youngs_modulus(self):
        """Young's modulus.

        Returns
        -------
        str or float
            Young's modulus of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._youngs_modulus

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        self._youngs_modulus.value = value
        self.physics_type = ["Electromagnetic", "Thermal", "Structural"]
        self._props["PhysicsTypes"] = OrderedDict({"set": ["Electromagnetic", "Thermal", "Structural"]})
        self._update_props("youngs_modulus", value)

    @property
    def poissons_ratio(self):
        """Poisson's ratio.

        Returns
        -------
        str or float
            Poisson's ratio of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._poissons_ratio

    @poissons_ratio.setter
    def poissons_ratio(self, value):
        self._poissons_ratio.value = value
        self.physics_type = ["Electromagnetic", "Thermal", "Structural"]
        self._props["PhysicsTypes"] = OrderedDict({"set": ["Electromagnetic", "Thermal", "Structural"]})
        self._update_props("poissons_ratio", value)

    @property
    def diffusivity(self):
        """Diffusivity.

        Returns
        -------
        str or float
            Diffusivity of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._diffusivity

    @diffusivity.setter
    def diffusivity(self, value):
        self._diffusivity.value = value
        self._update_props("diffusivity", value)

    @property
    def molecular_mass(self):
        """Molecular mass.

        Returns
        -------
        str or float
            Molecular mass of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._molecular_mass

    @molecular_mass.setter
    def molecular_mass(self, value):
        self._molecular_mass.value = value
        self._update_props("molecular_mass", value)

    @property
    def viscosity(self):
        """Viscosity.

        Returns
        -------
        str or float
            Viscosity of the material.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._viscosity

    @viscosity.setter
    def viscosity(self, value):
        self._viscosity.value = value
        self._update_props("viscosity", value)

    @property
    def core_loss_kh(self):
        """Core loss in kilohertz.

        Returns
        -------
        str or float
            Core loss of the material in kilohertz.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._core_loss_kh

    @core_loss_kh.setter
    def core_loss_kh(self, value):
        self._core_loss_kh.value = value
        self._update_props("core_loss_kh", value)

    @property
    def core_loss_kc(self):
        """Core loss in kilocalories.

        Returns
        -------
        str or float
            Core loss of the material in kilocalories.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._core_loss_kc

    @core_loss_kc.setter
    def core_loss_kc(self, value):
        self._core_loss_kc.value = value
        self._update_props("core_loss_kc", value)

    @property
    def core_loss_ke(self):
        """Core loss in kinetic energy.

        Returns
        -------
        type
            Core loss of the material in kinetic energy.

        References
        ----------

        >>> oDefinitionManager.EditMaterial
        """
        return self._core_loss_ke

    @core_loss_ke.setter
    def core_loss_ke(self, value):
        self._core_loss_ke.value = value
        self._update_props("core_loss_ke", value)

    def is_conductor(self, threshold=100000):
        """Check if the material is a conductor.

        Parameters
        ----------
        threshold : float, optional
            Threshold to define if a material is a conductor. The
            default is ``100000``. If the conductivity is equal to or
            greater than the threshold, the material is
            considered a conductor.

        Returns
        -------
        bool
            ``True`` when the material is a condutor, ``False`` otherwise.

        """
        cond = self.conductivity.value
        if not cond:
            return False
        if "Freq" in str(cond):
            return True
        try:
            if float(cond) >= threshold:
                return True
        except:
            return False
        return False

    @aedt_exception_handler
    def is_dielectric(self, threshold=100000):
        """Check if the material is dielectric.

        Parameters
        ----------
        threshold : float, optional
            Threshold to define if a material is dielectric. The
            default is ``100000``. If the conductivity is equal to or
            greater than the threshold, the material is
            considered dielectric.

        Returns
        -------
        bool
            ``True`` when the material is dielectric, ``False`` otherwise.
        """
        return not self.is_conductor(threshold)

    @aedt_exception_handler
    def update(self):
        """Update the material in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDefinitionManager.AddMaterial
        >>> oDefinitionManager.EditMaterial
        """

        args = self._get_args()
        if self._does_material_exists(self.name):
            self.odefinition_manager.EditMaterial(self.name, args)
        else:
            self.odefinition_manager.AddMaterial(args)
        return True

    @aedt_exception_handler
    def _does_material_exists(self, material_name):
        listmatprj = [i.lower() for i in list(self.odefinition_manager.GetProjectMaterialNames())]
        if material_name.lower() in listmatprj:
            return True
        else:
            return False


class SurfaceMaterial(CommonMaterial, object):
    """Manages surface material properties.

    Parameters
    ----------
    materiallib : :class:`pyaedt.modules.MaterialLib.Materials`
        Inherited parent object.
    name : str
        Name of the surface material
    props :
        The default is ``None``.
    """

    def __init__(self, materiallib, name, props=None):
        CommonMaterial.__init__(self, materiallib, name, props)
        self.surface_clarity_type = "Opaque"
        if "surface_clarity_type" in self._props:
            self.surface_clarity_type = self._props["surface_clarity_type"]["Choice"]
        if "PhysicsTypes" in self._props:
            self.physics_type = self._props["PhysicsTypes"]["set"]
        else:
            self.physics_type = ["Thermal"]
        for property in SurfMatProperties.aedtname:
            if property in self._props:
                mods = None
                if "ModifierData" in self._props:
                    modifiers = self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]
                    for mod in modifiers:
                        if isinstance(modifiers[mod], list):
                            for one_tm in modifiers[mod]:
                                if one_tm["Property:"] == property:
                                    if mods:
                                        mods = [mods]
                                        mods.append(one_tm)
                                    else:
                                        mods = one_tm
                        else:
                            if modifiers[mod]["Property:"] == property:
                                mods = modifiers[mod]
                self.__dict__["_" + property] = MatProperty(self, property, self._props[property], mods)
            else:
                self.__dict__["_" + property] = MatProperty(
                    self, property, SurfMatProperties.get_defaultvalue(aedtname=property)
                )
        pass

    @property
    def emissivity(self):
        """Emissivity.

        Returns
        -------
        str or float
            Emissivity of the surface material.

        References
        ----------

        >>> oDefinitionManager.EditSurfaceMaterial
        """
        return self._surface_emissivity

    @emissivity.setter
    def emissivity(self, value):

        self._surface_emissivity.value = value
        self._update_props("surface_emissivity", value)

    @property
    def surface_diffuse_absorptance(self):
        """Surface diffuse absorptance.

        Returns
        -------
        str or float
            Surface diffuse absorptance of the surface material.

        References
        ----------

        >>> oDefinitionManager.EditSurfaceMaterial
        """
        return self._surface_diffuse_absorptance

    @surface_diffuse_absorptance.setter
    def surface_diffuse_absorptance(self, value):

        self._surface_diffuse_absorptance.value = value
        self._update_props("surface_diffuse_absorptance", value)

    @property
    def surface_incident_absorptance(self):
        """Surface incident absorptance.

        Returns
        -------
        str or float
            Surface incident absorptance of the surface material.

        References
        ----------

        >>> oDefinitionManager.EditSurfaceMaterial
        """
        return self._surface_incident_absorptance

    @surface_incident_absorptance.setter
    def surface_incident_absorptance(self, value):

        self._surface_incident_absorptance.value = value
        self._update_props("surface_incident_absorptance", value)

    @property
    def surface_roughness(self):
        """Surface roughness.

        Returns
        -------
        str or float
            Surface roughness of the surface material.

        References
        ----------

        >>> oDefinitionManager.EditSurfaceMaterial
        """
        return self._surface_roughness

    @surface_roughness.setter
    def surface_roughness(self, value):
        self._surface_roughness.value = value
        self._update_props("surface_roughness", value)

    @aedt_exception_handler
    def update(self):
        """Update the surface material in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDefinitionManager.DoesSurfaceMaterialExist
        >>> oDefinitionManager.AddSurfaceMaterial
        >>> oDefinitionManager.EditSurfaceMaterial
        """
        args = self._get_args()
        if self._does_material_exists(self.name):
            self.odefinition_manager.EditSurfaceMaterial(self.name, args)
        else:
            self.odefinition_manager.AddSurfaceMaterial(args)
        return True

    @aedt_exception_handler
    def _does_material_exists(self, szMat):
        a = self.odefinition_manager.DoesSurfaceMaterialExist(szMat)
        if a != 0:
            return True
        return False
