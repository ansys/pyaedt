"""
Material Class
----------------


Description
==================================================

This class contains the data class to create a material library. internal use only

========================================================

"""
from collections import defaultdict, OrderedDict
from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from ..application.DataHandlers import dict2arg, arg2dict

class MatProperties(object):
    """list of constants of all possible materials constant names and how they are mapped to XML
    internalame=named used in script
    xmlname=named used in XML syntax

    Parameters
    ----------

    Returns
    -------

    """
    aedtname =     ['permittivity', 'permeability', 'conductivity', 'dielectric_loss_tangent', 'magnetic_loss_tangent', 'thermal_conductivity', 'mass_density', 'specific_heat', 'thermal_expansion_coefficient', 'youngs_modulus',   'poissons_ratio',   'diffusivity', 'molecular_mass', 'viscosity', 'core_loss_kh', 'core_loss_kc', 'core_loss_ke']
    defaultvalue = [1.0,             1.0,            0,              0,                         0,                       0.01,                      0,              0,               0,                               0,                  0,                  0.8,         0,                   0,                 0,                   0,                      0,                          0]
    defaultunit  = [None,            None,          '[siemens m^-1]', None,                     None,                   '[W m^-1 C^-1]',        '[Kg m^-3]',    '[J Kg^-1 C^-1]', '[C^-1]',                       '[Pa]',             None,               None,               None,               None,               None,           None,                  None,                       None]
    diel_order =   [3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 1]
    cond_order =   [2, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 3]

    @classmethod
    def get_defaultunit(cls, aedtname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        aedtname : str
            aedtname (Default value = None)

        Returns
        -------
        str
            defaultunit if exists

        """
        if aedtname:
            return cls.defaultunit[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: either fullname or catname MUST be defined")


    @classmethod
    def get_defaultvalue(cls, aedtname):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        aedtname : str
             aedtname (Default value = None)

        Returns
        -------
        float
            defaultunit

        """
        if aedtname:
            return cls.defaultvalue[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: either fullname or catname MUST be defined")

class SurfMatProperties(object):
    """list of constants of all possible materials constant names and how they are mapped to XML
    internalame=named used in script
    xmlname=named used in XML syntax

    Parameters
    ----------

    Returns
    -------

    """
    aedtname =     ['surface_emissivity', 'surface_roughness', 'surface_diffuse_absorptance', 'surface_incident_absorptance']
    defaultvalue = [1.0,             0,            0.4,              0.4]
    defaultunit  = [None,            '[m]',          None, None]

    @classmethod
    def get_defaultunit(cls, aedtname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        aedtname : str
            optional aedtname (Default value = None)

        Returns
        -------
        str
            defaultunit if exists

        """
        if aedtname:
            return cls.defaultunit[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: either fullname or catname MUST be defined")


    @classmethod
    def get_defaultvalue(cls, aedtname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        aedtname : str
            optional aedtname (Default value = None)

        Returns
        -------
        float
            defaultunit

        """
        if aedtname:
            return cls.defaultvalue[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: either fullname or catname MUST be defined")


class ClosedFormTM(object):
    """Class to manage Closed Form Terhmal Modifier."""
    Tref = '22cel'
    C1 = 0
    C2 = 0
    TL = '-273.15cel'
    TU = '1000cel'
    autocalculation = True
    TML = 1000
    TMU = 1000

class Dataset(object):
    """Data Class for DataSet Management"""
    ds = []
    unitx = ""
    unity = ""
    unitz = ""
    type = "Absolute"
    namex = ""
    namey = ""
    namez = None

class BasicValue(object):
    value = None
    dataset = None
    thermalmodifier = None



class MatProperty(object):
    """type: simple, anisotropic, tensor"""

    @property
    def _messenger(self):
        return self._parent._messenger

    def __init__(self, parent, name, val=None, thermalmodifier=None):
        self._parent = parent
        self._type = "simple"
        self.name =name
        self._property_value = [BasicValue()]
        self._unit = None
        if val is not None and isinstance(val,(str, float, int)):
            self.value = val
        elif val is not None and val["property_type"] == "AnisoProperty":
            self.type = "anisotropic"
            self.value = [val["component1"],val["component2"], val["component3"]]
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
        return self._type

    @type.setter
    def type(self, type):
        """Set Material Property Type

        Parameters
        ----------
        type :
            simple", "nonlinear", "anisotropic", "tensor"

        Returns
        -------

        """
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
        return self._unit

    @unit.setter
    def unit(self, unit):
        self._unit = unit

    @property
    def data_set(self):
        if len(self._property_value) == 1:
            return self._property_value[0].dataset
        else:
            return [i.dataset for i in self._property_value]

    @property
    def thermalmodifier(self):
        if len(self._property_value) == 1:
            return self._property_value[0].thermalmodifier
        else:
            return [i.thermalmodifier for i in self._property_value]

    def _add_thermal_modifier(self,formula, index):
        if "ModifierData" not in self._parent._props:
            tm = OrderedDict({'Property:': self.name, 'Index:': index, "prop_modifier": "thermal_modifier",
                              "use_free_form": True, "free_form_value": formula})
            self._parent._props["ModifierData"] = OrderedDict({"ThermalModifierData": OrderedDict(
                {"modifier_data": 'thermal_modifier_data',
                 "all_thermal_modifiers": OrderedDict({"one_thermal_modifier": tm})})})
        else:
            for tmname in self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]:
                if isinstance(self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname], list):
                    found = False
                    for tm in self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname]:
                        if self.name == tm['Property:'] and index == tm['Index:']:
                            found = True
                            tm['use_free_form'] = True
                            tm['free_form_value'] = formula
                            tm.pop("Tref", None)
                            tm.pop("C1", None)
                            tm.pop("C2", None)
                            tm.pop("TL", None)
                            tm.pop("TU", None)
                    if not found:
                        tm = OrderedDict({'Property:': self.name, 'Index:': index, "prop_modifier": "thermal_modifier",
                                          "use_free_form": True, "free_form_value": formula})
                        self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].append(tm)
                elif self.name ==self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname][
                            'Property:'] and index ==self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname][
                            'Index:']:
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname]['use_free_form'] = True
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname]['free_form_value'] = formula
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop("Tref", None)
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop("C1", None)
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop("C2", None)
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop("TL", None)
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].pop("TU", None)

                else:
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname] = [
                        self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname]]
                    tm = OrderedDict({'Property:': self.name, 'Index:': index, "prop_modifier": "thermal_modifier",
                                      "use_free_form": True, "free_form_value": formula})
                    self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname].append(tm)
        return self._parent.update()

    def add_thermal_modifier_free_form(self, formula, index=0):
        """
        Add a Thermal modifier to a material Property using an free Form formula

        Parameters
        ----------
        formula : str
            Full Formula to apply
        index : int, Default ``0``

        Returns
        -------
        bool

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss(specified_version="2021.1")
        >>> mat1 = hfss.materials.add_material("new_copper2")
        >>> mat1.aadd_thermal_modifier_free_form("if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))")
        """
        self._property_value[index].thermalmodifier = formula
        return self._add_thermal_modifier(formula, index)


    def add_thermal_modifier_dataset(self, dataset_name, index=0):
        """
        Add a Thermal modifier to a material Property using an existing Dataset

        Parameters
        ----------
        dataset_name : str
            Project Dataset name
        index : int, Default ``0``

        Returns
        -------
        bool

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss(specified_version="2021.1")
        >>> mat1 = hfss.materials.add_material("new_copper2")
        >>> mat1.add_thermal_modifier_dataset("$ds1")
        """

        formula = "pwl({}, Temp)".format(dataset_name)
        self._property_value[index].thermalmodifier = formula
        self._add_thermal_modifier(formula,index)

    def add_thermal_modifier_closed_form(self, tref=22, c1=0.0001, c2=1e-6, tl=-273.15, tu=1000, units="cel",
                                         auto_calc=True, tml=1000, tmu=1000, index=0):
        """
        Add a Thermal modifier to a material Property using Closed Form

        Parameters
        ----------
        tref : float
            Reference Temperature
        c1 : float
        c2 : float
        tl : float
        tu : float
        units : str, Default ``cel``
        auto_calc : bool, Default ``True``
        tml : float
        tmu : float
        index : int, Default ``0``

        Returns
        -------
        bool

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> hfss = Hfss(specified_version="2021.1")
        >>> mat1 = hfss.materials.add_material("new_copper2")
        >>> mat1.permittivity.add_thermal_modifier_closed_form(c1 = 1e-3)
        """

        if index> len(self._property_value):
            self._messenger.add_error_message(
                "Wrong index number. Index must be 0 for simple or nonlinear properties, <=2 for anisotropic materials, <=9 for Tensors")
            return False
        self._property_value[index].thermalmodifier = ClosedFormTM()
        self._property_value[index].thermalmodifier.Tref = str(tref)+units
        self._property_value[index].thermalmodifier.C1 = str(c1)
        self._property_value[index].thermalmodifier.C2 = str(c2)
        self._property_value[index].thermalmodifier.TL = str(tl)+units
        self._property_value[index].thermalmodifier.TU = str(tu)+units
        self._property_value[index].thermalmodifier.autocalculation = auto_calc
        if not auto_calc:
            self._property_value[index].thermalmodifier.TML = tml
            self._property_value[index].thermalmodifier.TMU = tmu
        if auto_calc:
            tm_new = OrderedDict({'Property:': self.name, 'Index:': index, "prop_modifier": "thermal_modifier",
                              "use_free_form": False, "Tref": str(tref) + units,
                              "C1": str(c1), "C2": str(c2), "TL": str(tl) + units, "TU": str(tu) + units,
                              "auto_calculation": True})
        else:
            tm_new = OrderedDict({'Property:': self.name, 'Index:': index, "prop_modifier": "thermal_modifier",
                              "use_free_form": False, "Tref": str(tref) + units,
                              "C1": str(c1), "C2": str(c2), "TL": str(tl) + units, "TU": str(tu) + units,
                              "auto_calculation": False, "TML":str(tml), "TMU":str(tmu)})
        if "ModifierData" not in self._parent._props:
            self._parent._props["ModifierData"] = OrderedDict({"ThermalModifierData": OrderedDict(
                {"modifier_data": 'thermal_modifier_data',
                 "all_thermal_modifiers": OrderedDict({"one_thermal_modifier": tm_new})})})
        else:
            for tmname in self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]:
                tml = self._parent._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][tmname]
                if isinstance(tml,  list):
                    found = False
                    for tm in tml:
                        if self.name == tm['Property:'] and index == tm['Index:']:
                            found = True
                            tm['use_free_form'] = False
                            tm.pop("free_form_value", None)
                            tm['Tref'] = str(tref)+units
                            tm['C1'] = str(c1)
                            tm['C2'] = str(c2)
                            tm['TL'] = str(tl)+units
                            tm['TU'] = str(tu)+units
                            tm["auto_calculation"] = auto_calc
                            if auto_calc:
                                tm["TML"] = tml
                                tm["TMU"] = tmu
                            else:
                                tm.pop("TML", None)
                                tm.pop("TMU", None)
                    if not found:
                        tml.append(tm_new)
                elif self.name == tml['Property:'] and index == tml['Index:']:
                    tml['use_free_form'] = False
                    tml.pop("free_form_value", None)
                    tml['Tref'] = str(tref)+units
                    tml['C1'] = str(c1)
                    tml['C2'] = str(c1)
                    tml['TL'] = str(tl)+units
                    tml['TU'] = str(tl)+units
                    tml['auto_calculation'] = auto_calc
                    if not auto_calc:
                        tml["TML"] = str(tml)
                        tml["TMU"] = str(tmu)
                    else:
                        tml.pop("TML", None)
                        tml.pop("TMU", None)
                else:
                    tml = [tml]
                    tml.append(tm_new)
        return self._parent.update()

class CommonMaterial(object):
    """Class for Frequency Dependence Datasets"""

    @property
    def odefinition_manager(self):
        """:return: Definition Manager"""
        return self._parent.oproject.GetDefinitionManager()

    @property
    def _omaterial_manager(self):
        """:return:Material Manager"""
        return self.odefinition_manager.GetManager("Material")

    @property
    def _messenger(self):
        """ """
        return self._parent._messenger

    @property
    def oproject(self):
        """ """
        return self._parent._oproject

    @property
    def desktop(self):
        """ """
        return self._parent._desktop

    def __init__(self, parent, name, props=None):
        self._parent = parent
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
        if not props:
            props = self._props
        arg = ["NAME:" + self.name]
        dict2arg(props, arg)
        return arg

    def _update_props(self, propname, provpavlue, update_aedt=True):
        if isinstance(provpavlue, list) and self.__dict__["_"+propname].type != "simple" and self.__dict__["_"+propname].type != "nonlinear":
                i=1
                for val in provpavlue:
                    self._props[propname]["component"+str(i)] = str(val)
                    i += 1
                if update_aedt:
                    return self.update()
        elif  isinstance(provpavlue, (str, float, int)):
            self._props[propname] = str(provpavlue)
            if update_aedt:
                return self.update()
        else:
            return False


class Material(CommonMaterial, object):
    """Class for Material Properties"""

    def __init__(self, parent, name, props=None):
        CommonMaterial.__init__(self, parent, name, props)
        self.thermal_material_type = "Solid"
        if "thermal_material_type" in self._props:
            self.thermal_material_type = self._props["thermal_material_type"]["Choice"]
        if "PhysicsTypes" in self._props:
            self.physics_type = self._props["PhysicsTypes"]["set"]
        else:
            self.physics_type = ['Electromagnetic', 'Thermal', 'Structural']
            self._props["PhysicsTypes"]=OrderedDict({"set":['Electromagnetic', 'Thermal', 'Structural']})

        for property in MatProperties.aedtname:
            if property in self._props:
                mods = None
                if "ModifierData" in self._props:
                    for mod in self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]:
                        if isinstance(self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][mod],
                                      list):
                            for one_tm in self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][
                                mod]:
                                if one_tm["Property:"] == property:
                                    if mods:
                                        mods = [mods]
                                        mods.append(one_tm)
                                    else:
                                        mods = one_tm
                        else:
                            if self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][mod][
                                "Property:"] == property:
                                mods = self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][mod]
                self.__dict__["_" + property] = MatProperty(self, property, self._props[property], mods)
            else:
                self.__dict__["_" + property] = MatProperty(self, property,
                                                            MatProperties.get_defaultvalue(aedtname=property), None)
        pass

    @property
    def permittivity(self):
        """

        Returns
        -------
        MatProperty
            Permittivity Value of the material
        """
        return self._permittivity

    @permittivity.setter
    def permittivity(self, value):

        self._permittivity.value = value
        self._update_props("permittivity", value)

    @property
    def permeability(self):
        """

        Returns
        -------
        MatProperty
            Permeability Value of the material
        """
        return self._permeability

    @permeability.setter
    def permeability(self, value):

        self._permeability.value = value
        self._update_props("permeability", value)

    @property
    def conductivity(self):
        """

        Returns
        -------
        MatProperty
            Conductivity Value of the material
        """
        return self._conductivity

    @conductivity.setter
    def conductivity(self, value):
        self._conductivity.value = value
        self._update_props("conductivity", value)

    @property
    def dielectric_loss_tangent(self):
        """

        Returns
        -------
        MatProperty
            Dielectric Loss Tangent Value of the material
        """
        return self._dielectric_loss_tangent

    @dielectric_loss_tangent.setter
    def dielectric_loss_tangent(self, value):

        self._dielectric_loss_tangent.value = value
        self._update_props("dielectric_loss_tangent", value)

    @property
    def magnetic_loss_tangent(self):
        """

        Returns
        -------
        MatProperty
            Magnetic Loss Tangent Value of the material
        """
        return self._magnetic_loss_tangent

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):

        self._magnetic_loss_tangent.value = value
        self._update_props("magnetic_loss_tangent", value)
    @property
    def thermal_conductivity(self):
        """

        Returns
        -------
        MatProperty
            Thermal Conductivity Value of the material

        """
        return self._thermal_conductivity

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):

        self._thermal_conductivity.value = value
        self._update_props("thermal_conductivity", value)

    @property
    def mass_density(self):
        """

        Returns
        -------
        MatProperty
            Mass Density Value of the material

        """
        return self._mass_density

    @mass_density.setter
    def mass_density(self, value):

        self._mass_density.value = value
        self._update_props("mass_density", value)

    @property
    def specific_heat(self):
        """

        Returns
        -------
        MatProperty
            Specific Heat Value of the material

        """
        return self._specific_heat

    @specific_heat.setter
    def specific_heat(self, value):

        self._specific_heat.value = value
        self._update_props("specific_heat", value)

    @property
    def thermal_expansion_coefficient(self):
        """

        Returns
        -------
        MatProperty
            Thermal Expansion Coefficient  of the material

        """
        return self._thermal_expansion_coefficient

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):

        self._thermal_expansion_coefficient.value = value
        self._update_props("thermal_expansion_coefficient", value)

    @property
    def youngs_modulus(self):
        """

        Returns
        -------
        MatProperty
            Youngs Modulus  of the material

        """
        return self._youngs_modulus

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        self._youngs_modulus.value = value
        self._update_props("youngs_modulus", value)

    @property
    def poissons_ratio(self):
        """

        Returns
        -------
        MatProperty
            Poisson Ratio's of the material
        """
        return self._poissons_ratio

    @poissons_ratio.setter
    def poissons_ratio(self, value):
        self._poissons_ratio.value = value
        self._update_props("poissons_ratio", value)

    @property
    def diffusivity(self):
        return self._diffusivity

    @diffusivity.setter
    def diffusivity(self, value):
        self._diffusivity.value = value
        self._update_props("diffusivity", value)

    @property
    def molecular_mass(self):
        return self._molecular_mass

    @molecular_mass.setter
    def molecular_mass(self, value):
        self._molecular_mass.value = value
        self._update_props("molecular_mass", value)

    @property
    def viscosity(self):
        return self._viscosity

    @viscosity.setter
    def viscosity(self, value):
        self._viscosity.value = value
        self._update_props("viscosity", value)

    @property
    def core_loss_kh(self):
        return self._core_loss_kh

    @core_loss_kh.setter
    def core_loss_kh(self, value):
        self._core_loss_kh.value = value
        self._update_props("core_loss_kh", value)

    @property
    def core_loss_kc(self):
        return self._core_loss_kc

    @core_loss_kc.setter
    def core_loss_kc(self, value):
        self._core_loss_kc.value = value
        self._update_props("core_loss_kc", value)

    @property
    def core_loss_ke(self):
        return self._core_loss_ke

    @core_loss_ke.setter
    def core_loss_ke(self, value):
        self._core_loss_ke.value = value
        self._update_props("core_loss_ke", value)

    def is_conductor(self, threshold=100000):
        """Check if material is conductor

        Parameters
        ----------
        threshold : float
            Threshold to define if material is condcutor or not. Default is ``100000``

        Returns
        -------
        bool
            ``True`` if material is conductor.   Material is defined as conductor if cond>=100000. Threshold can be modified
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
        """Check if material is dielectric

        Parameters
        ----------
        threshold : float
            Threshold to define if material is dielectric. Default conductivitivy value is ``100000``

        Returns
        -------
        bool
            ``True`` if material is dielectric.   Material is defined as conductor if conductivity>=100000.
            Threshold can be modified
        """
        return not self.is_conductor()

    @aedt_exception_handler
    def update(self):
        """Update material in AEDT


        Returns
        -------
        bool
            ``True`` if succeeded

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

    def __init__(self, parent, name, props=None):
        CommonMaterial.__init__(self,parent, name, props)
        self.surface_clarity_type = "Opaque"
        if "surface_clarity_type" in self._props:
            self.surface_clarity_type = self._props["surface_clarity_type"]["Choice"]
        if "PhysicsTypes" in self._props:
            self.physics_type = self._props["PhysicsTypes"]["set"]
        else:
            self.physics_type = ['Thermal']
        for property in SurfMatProperties.aedtname:
            if property in self._props:
                mods = None
                if "ModifierData" in self._props:
                    for mod in self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"]:
                        if isinstance(self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][mod],
                                      list):
                            for one_tm in self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][
                                mod]:
                                if one_tm["Property:"] == property:
                                    if mods:
                                        mods = [mods]
                                        mods.append(one_tm)
                                    else:
                                        mods = one_tm
                        else:
                            if self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][mod][
                                "Property:"] == property:
                                mods = self._props["ModifierData"]["ThermalModifierData"]["all_thermal_modifiers"][mod]
                self.__dict__["_" + property] = MatProperty(self, property, self._props[property], mods)
            else:
                self.__dict__["_" + property] = MatProperty(self, property, SurfMatProperties.get_defaultvalue(aedtname=property))
        pass

    @property
    def emissivity(self):
        return self._surface_emissivity

    @emissivity.setter
    def emissivity(self, value):

        self._surface_emissivity.value = value
        self._update_props("surface_emissivity", value)

    @property
    def surface_diffuse_absorptance(self):
        return self._surface_diffuse_absorptance

    @surface_diffuse_absorptance.setter
    def surface_diffuse_absorptance(self, value):

        self._surface_diffuse_absorptance.value = value
        self._update_props("surface_diffuse_absorptance", value)

    @property
    def surface_incident_absorptance(self):
        return self._surface_incident_absorptance

    @surface_incident_absorptance.setter
    def surface_incident_absorptance(self, value):

        self._surface_incident_absorptance.value = value
        self._update_props("surface_incident_absorptance", value)

    @property
    def surface_roughness(self):
        return self._surface_roughness

    @surface_roughness.setter
    def surface_roughness(self, value):

        self._surface_roughness.value = value
        self._update_props("surface_roughness", value)

    @aedt_exception_handler
    def update(self):
        """Update material in AEDT


        Returns
        -------
        type
            Bool

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
        if a!=0:
            return True
        return False
