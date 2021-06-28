"""
Material Class
----------------


Description
==================================================

This class contains the data class to create a material library. internal use only

========================================================

"""
from collections import defaultdict
from ..generic.general_methods import aedt_exception_handler

class MatProperties(object):
    """list of constants of all possible materials constant names and how they are mapped to XML
    internalame=named used in script
    xmlname=named used in XML syntax

    Parameters
    ----------

    Returns
    -------

    """
    aedtname =     ['permittivity', 'permeability', 'conductivity', 'dielectric_loss_tangent', 'magnetic_loss_tangent', 'thermal_conductivity', 'mass_density', 'specific_heat', 'thermal_expansion_coefficient', 'youngs_modulus',   'poissons_ratio',   'emissivity', 'diffusivity', 'molecular_mass', 'viscosity', 'core_loss_kh', 'core_loss_kc', 'core_loss_ke']
    fullname =     ['Permittivity', 'Permeability', 'Conductivity', 'Dielectric Loss Tangent', 'Magnetic Loss Tangent', 'Thermal Conductivity', 'Mass Density', 'Specific Heat', 'Thermal Expansion Coefficient', 'Young\'s Modulus', 'Poisson\'s Ratio', 'Emissivity', 'Diffusivity', 'Molecular Mmass', 'Viscosity', 'Hysteresis application Loss', 'Eddy-Current application Loss', 'Excess application Loss']
    catname =      ['Permittivity', 'Permeability', 'Conductivity', 'Dielectric Loss Tangent', 'Magnetic Loss Tangent', 'Thermal Conductivity', 'Mass Density', 'Specific Heat', 'Thermal Expansion Coefficient', 'Elasticity',       'Elasticity',       'Emissivity', 'Fluid Properties', 'Fluid Properties', 'Fluid Properties', 'Hysteresis application Loss', 'Eddy-Current application Loss', 'Excess application Loss']
    defaultvalue = [1.0,             1.0,            0,              0,                         0,                       0.01,                      0,              0,               0,                               0,                  0,                  0.8,         0,                   0,                 0,                   0,                      0,                          0]
    defaultunit  = [None,            None,          '[siemens m^-1]', None,                     None,                   '[W m^-1 C^-1]',        '[Kg m^-3]',    '[J Kg^-1 C^-1]', '[C^-1]',                       '[Pa]',             None,               None,               None,               None,               None,           None,                  None,                       None]
    diel_order =   [3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 1]
    cond_order =   [2, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 3]

    @classmethod
    def get_defaultunit(cls, fullname=None, catname=None, aedtname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        fullname :
            optiona full name of the property (Default value = None)
        catname :
            optional Category name (Default value = None)
        aedtname :
            optional aedtname (Default value = None)

        Returns
        -------
        type
            defaultunit if exists

        """
        if fullname:
            return cls.defaultunit[cls.fullname.index(fullname)]
        elif catname:
            return cls.defaultunit[cls.catname.index(catname)]
        elif aedtname:
            return cls.defaultunit[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_defaultunit: either fullname or catname MUST be defined")

    @classmethod
    def get_aedtname(cls, fullname=None, catname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        fullname :
            optiona full name of the property (Default value = None)
        catname :
            optional Category name (Default value = None)

        Returns
        -------
        type
            aedtname

        """
        if fullname:
            return cls.aedtname[cls.fullname.index(fullname)]
        elif catname:
            return cls.aedtname[cls.catname.index(catname)]
        else:
            raise TypeError("get_aedtname: either fullname or catname MUST be defined")

    @classmethod
    def get_catname(cls, fullname=None, aedtname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        fullname :
            optiona full name of the property (Default value = None)
        aedtname :
            optional aedtname (Default value = None)

        Returns
        -------
        type
            catname

        """
        if fullname:
            return cls.catname[cls.fullname.index(fullname)]
        elif aedtname:
            return cls.catname[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_aedtname: either fullname or aedtname MUST be defined")

    @classmethod
    def get_fullname(cls, catname=None, aedtname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        catname :
            optional Category name (Default value = None)
        aedtname :
            optional aedtname (Default value = None)

        Returns
        -------
        type
            catname

        """
        if catname:
            return cls.fullname[cls.catname.index(catname)]
        elif aedtname:
            return cls.fullname[cls.aedtname.index(aedtname)]
        else:
            raise TypeError("get_aedtname: either fullname or aedtname MUST be defined")


    @classmethod
    def get_defaultvalue(cls, fullname=None, catname=None, aedtname=None):
        """Get the defaultunit for a given fullname or catname

        Parameters
        ----------
        fullname :
            optiona full name of the property (Default value = None)
        catname :
            optional Category name (Default value = None)
        aedtname :
            optional aedtname (Default value = None)

        Returns
        -------
        type
            defaultunit

        """
        if fullname:
            return cls.defaultvalue[cls.fullname.index(fullname)]
        elif catname:
            return cls.defaultvalue[cls.catname.index(catname)]
        elif aedtname:
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
    """ """
    value = None
    dataset = None
    thermalmodifier = None


class MatProperty(object):
    """type: simple, anisotropic, tensor"""

    @property
    def _messenger(self):
        return self._parent._messenger

    def __init__(self, parent, val=None):
        self._parent = parent
        self._type = "simple"
        self._property_value = [BasicValue()]
        self._unit = None
        if val:
            self.value = val

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
            self._property_value = [BasicValue()]
        elif self._type == "anisotropic":
            self._property_value = [BasicValue() for i in range(3)]
        elif self._type == "tensor":
            self._property_value = [BasicValue() for i in range(9)]
        elif self._type == "nonlinear":
            self._property_value = [BasicValue()]

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

                self._property_value[i] = el
                i += 1
        else:
            self._property_value[0] = val

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

    def add_data_set(self, listtemp_val, unitx="Hz", unity="", is_linear=True):
        if not is_linear:
            self.type = "nonlinear"
        if self.type == "simple" or self.type == "nonlinear":
            tm = Dataset()
            tm.type = "Absolute"
            tm.namex = "Frequency"
            tm.unitx = unitx
            tm.unity = unity
            tm.ds = listtemp_val
            self._property_value[0].dataset = tm
        else:
            i=0
            for el in listtemp_val:
                tm = Dataset()
                tm.type = "Absolute"
                tm.namex = "Frequency"
                tm.unitx = unitx
                tm.unity = unity
                tm.ds = el
                self._property_value[i].dataset = tm
                i+=1

    @property
    def thermal_modifier(self):
        if len(self._property_value) == 1:
            return self._property_value[0].thermalmodifier
        else:
            return [i.thermalmodifier for i in self._property_value]


    @thermal_modifier.setter
    def thermal_modifier(self, listtemp_val):
        if self.type == "simple" or self.type == "nonlinear":
            tm = Dataset()
            tm.type = "Relative"
            tm.namex = "Temperature"
            tm.ds = listtemp_val
            self._property_value[0].thermalmodifier = tm
        else:
            i=0
            for el in listtemp_val:
                tm = Dataset()
                tm.type = "Relative"
                tm.namex = "Temperature"
                tm.ds = el
                self._property_value[i].thermalmodifier = tm
                i+=1


    @aedt_exception_handler
    def create_thermal_modifier(self, listtemp_val):
        """Create a new thermal modifier object based on a list of values

        Parameters
        ----------
        listtemp_val :
            list of thermal modifiers. Example [[22, 1], [80, 0.8], [100,0.7]]

        Returns
        -------
        type
            tm object

        """
        tm = Dataset()
        tm.type = "Relative"
        tm.namex = "Temperature"
        tm.ds = listtemp_val
        return tm


class Material(object):
    """Class for Frequency Dependence Datasets"""

    @property
    def odefinition_manager(self):
        """:return: Definition Manager"""
        return self._parent._oproject.GetDefinitionManager()

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

    def __init__(self, parent):
        self._parent = parent
        self.name = ""
        self.origin = ""
        self.property = defaultdict(MatProperty)
        self.thermal_material_type="Solid"
        self._permittivity = MatProperty(MatProperties.get_defaultvalue(aedtname="permittivity"))
        self._permeability = MatProperty(MatProperties.get_defaultvalue(aedtname="permeability"))
        self._conductivity = MatProperty(MatProperties.get_defaultvalue(aedtname="conductivity"))
        self._dielectric_loss_tangent = MatProperty(MatProperties.get_defaultvalue(aedtname="dielectric_loss_tangent"))
        self._magnetic_loss_tangent = MatProperty(MatProperties.get_defaultvalue(aedtname="magnetic_loss_tangent"))
        self._mass_density = MatProperty(MatProperties.get_defaultvalue(aedtname="mass_density"))
        self._specific_heat = MatProperty(MatProperties.get_defaultvalue(aedtname="specific_heat"))
        self._thermal_expansion_coefficient = MatProperty(MatProperties.get_defaultvalue(aedtname="thermal_expansion_coefficient"))
        self._youngs_modulus = MatProperty(MatProperties.get_defaultvalue(aedtname="youngs_modulus"))
        self._poissons_ratio = MatProperty(MatProperties.get_defaultvalue(aedtname="poissons_ratio"))
        self._emissivity = MatProperty(MatProperties.get_defaultvalue(aedtname="emissivity"))
        self._diffusivity = MatProperty(MatProperties.get_defaultvalue(aedtname="diffusivity"))
        self._molecular_mass = MatProperty(MatProperties.get_defaultvalue(aedtname="molecular_mass"))
        self._viscosity = MatProperty(MatProperties.get_defaultvalue(aedtname="viscosity"))
        self._core_loss_kh = MatProperty(MatProperties.get_defaultvalue(aedtname="core_loss_kh"))
        self._core_loss_kc = MatProperty(MatProperties.get_defaultvalue(aedtname="core_loss_kc"))
        self._core_loss_ke = MatProperty(MatProperties.get_defaultvalue(aedtname="core_loss_ke"))

    @property
    def permittivity(self):
        return self._permittivity

    @property
    def permeability(self):
        return self._permeability

    @property
    def conductivity(self):
        return self._conductivity

    @property
    def dielectric_loss_tangent(self):
        return self._dielectric_loss_tangent

    @property
    def magnetic_loss_tangent(self):
        return self._magnetic_loss_tangent

    @property
    def mass_density(self):
        return self._mass_density

    @property
    def specific_heat(self):
        return self._specific_heat

    @property
    def thermal_expansion_coefficient(self):
        return self._thermal_expansion_coefficient

    @property
    def youngs_modulus(self):
        return self._youngs_modulus

    @property
    def poissons_ratio(self):
        return self._poissons_ratio

    @property
    def emissivity(self):
        return self._emissivity

    @property
    def diffusivity(self):
        return self._diffusivity

    @property
    def molecular_mass(self):
        return self._molecular_mass

    @property
    def viscosity(self):
        return self._viscosity

    @property
    def core_loss_kh(self):
        return self._core_loss_kh

    @property
    def core_loss_kc(self):
        return self._core_loss_kc

    @property
    def core_loss_ke(self):
        return self._core_loss_ke

    def is_conductor(self):
        """:return: Bool if material is conductor. Material is defined as conductor if cond>=100000"""
        cond = self.conductivity.value
        if cond >= 100000:
            return True
        elif cond == 0:
            try:
                if "Freq" in self.conductivity.value:
                    return True
            except:
                return False
        else:
            return False

    @aedt_exception_handler
    def is_dielectric(self):
        """:return: Bool if material is dielectric. Material is defined as conductor if cond<100000"""
        return not self.is_conductor()

    @aedt_exception_handler
    def update(self, enableTM=True, enableFM=True):
        """Update material in AEDT

        Parameters
        ----------
        enableTM :
            Boolean, to include Thermal Modifier in AEDT (Default value = True)
        enableFM :
            Boolean, to include Frequency Modifier in AEDT (Default value = True)

        Returns
        -------
        type
            Bool

        """
        args = self.name
        arg = ["Name:" + args]
        tms = {}
        # create the thermal modifier portion for the material definition if its
        # present in the amat xml file
        for mat in MatProperties.aedtname:
            id = 0
            for vals in self.__dict__[mat]._property_value:
                if vals.thermalmodifier:
                    tms[self.name.replace("-","_") + mat + "TH" + str(id)] = [id, mat, vals.thermalmodifier]
            id += 1

        if tms and enableTM:
            arg2 = self._createTM(tms)
            arg.append(arg2)
        # create a material with frequency dependent properties, scans the
        # material parameters to add it to relevant one
        fds = {}
        for props in self.property:
            id = 0
            for vals in self.property[props].property_value:
                if vals.dataset and self.property[props].type != 'nonlinear':
                    fds[self.name.replace("-", "_") + props + "FM" + str(id)] = [id, props, vals.dataset]
            id += 1
        for fd in fds:
            if fds[fd][2].namex == "Frequency" and not enableFM:
                print("Skipping Frequency modifier because disabled")
            elif not self._parent.dataset_exists(fd):
                self._create_dataset_in_aedt(fd, fds[fd][2])

        for sKey in MatProperties.aedtname:
            if self.property[sKey].type == "simple":
                if self.name.replace("-", "_") + sKey + "FM0" in fds and enableFM:
                    arg.append(sKey + ':='), arg.append("pwl($" + self.name.replace("-", "_") + sKey + "FM0" + ",Freq)")
                elif not self.property[sKey].property_value[0].dataset:
                    arg.append(sKey + ':='), arg.append(self.property[sKey].property_value[0].value)
                elif self.property[sKey].property_value[0].dataset.namex != "Frequency":
                    arg2 = self._createnonlinear(sKey, self.property[sKey].property_value[0].dataset)
                    arg.append(arg2)
            elif self.property[sKey].type == "nonlinear":
                if sKey == "conductivity":
                    arg2 = ["NAME:" + sKey, "property_type:=", "nonlinear", "EUnit:=", self.property[sKey].property_value[0].dataset.unitx, "JUnit:=",
                            self.property[sKey].property_value[0].dataset.unity]
                    arg3 = ["NAME:JECoordinates", ["NAME:DimUnits", "", ""]]
                    for coord in self.property[sKey].property_value[0].dataset.ds:
                        arg3.append(["NAME:Coordinate", ["NAME:CoordPoint", coord[0], coord[1]]])
                    arg2.append(arg3)
                    arg.append(arg2)
                if sKey == "permittivity":
                    arg2 = ["NAME:" + sKey, "property_type:=", "nonlinear", "EUnit:=",
                                self.property[sKey].property_value[0].dataset.unitx, "DUnit:=",
                                self.property[sKey].property_value[0].dataset.unity]
                    arg3 = ["NAME:DECoordinates", ["NAME:DimUnits", "", ""]]
                    for coord in self.property[sKey].property_value[0].dataset.ds:
                        arg3.append(["NAME:Coordinate", ["NAME:CoordPoint", coord[0], coord[1]]])
                    arg2.append(arg3)
                    arg.append(arg2)
                if sKey == "permeability":
                    arg2 = ["NAME:" + sKey, "property_type:=", "nonlinear", "HUnit:=",
                            self.property[sKey].property_value[0].dataset.unitx, "BUnit:=",
                            self.property[sKey].property_value[0].dataset.unity, "IsTemperatureDependent:=", False]
                    arg3 = ["NAME:BHCoordinates", ["NAME:DimUnits", "", ""]]
                    for coord in self.property[sKey].property_value[0].dataset.ds:
                        arg3.append(["NAME:Coordinate", ["NAME:CoordPoint", coord[0], coord[1]]])
                    arg2.append(arg3)
                    arg.append(arg2)
            else:
                arg2 = self._creatematrix(sKey, self)
                arg.append(arg2)
        if self.thermal_material_type == "Fluid":
            arg.append(["NAME:thermal_material_type","property_type:=", "ChoiceProperty","Choice:="	, "Fluid"])
            #arg.append("diffusivity:="), arg.append(self.property["diffusivity"].property_value[0].value)
            #arg.append("molecular_mass:="), arg.append(self.property["molecular_mass"].property_value[0].value)
            #arg.append("viscosity:="), arg.append(self.property["viscosity"].property_value[0].value)
            # add a material without freq dependent properties

        if self._does_material_exists(args):
            self.odefinition_manager.EditMaterial(args,arg)
        else:
            self.odefinition_manager.AddMaterial(arg)
        return True

    @aedt_exception_handler
    def _createTM(self, tms):
        arg2 = ["NAME:ModifierData"]
        arg3 = ["NAME:ThermalModifierData", "modifier_data:=", "thermal_modifier_data"]
        arg4 = ["NAME:all_thermal_modifiers"]
        for tm in tms:
            if type(tms[tm][2]) is Dataset:
                if not self._parent.dataset_exists(tm):
                    self._create_dataset_in_aedt(tm, tms[tm][2])
                # print name_temp
                arg4.append(["NAME:one_thermal_modifier", "Property::=", tms[tm][1], "Index::=", tms[tm][0],
                             "prop_modifier:=", "thermal_modifier", "use_free_form:=", True, "free_form_value:=",
                             "pwl($" + tm + ",Temp)"])
            elif type(tms[tm][2]) is ClosedFormTM:
                content = ["NAME:one_thermal_modifier", "Property::=", tms[tm][1], "Index::=", tms[tm][0],
                 "prop_modifier:=", "thermal_modifier", "use_free_form:=", False, "Tref:=", tms[tm][2].Tref, "C1:=",
                 tms[tm][2].C1, "C2:=", tms[tm][2].C2,
                 "TL:=", tms[tm][2].TL,
                 "TU:=", tms[tm][2].TU,
                 "auto_calculation:=", tms[tm][2].auto_calculation]
                if not tms[tm][2].auto_calculation:
                    content.append("TML:=")
                    content.appendtms([tm][2].TML)
                    content.append("TMU:=")
                    content.append(tms[tm][2].TMU)
                arg4.append(content)
            else:
                arg4.append(["NAME:one_thermal_modifier", "Property::=", tms[tm][1], "Index::=", tms[tm][0],
                             "prop_modifier:=", "thermal_modifier", "use_free_form:=", True, "free_form_value:=",
                             tms[tm][2]])

        arg3.append(arg4)
        arg2.append(arg3)
        return arg2

    @aedt_exception_handler
    def _createnonlinear(self,sKey, dataset):
        #TODO Support nonlinear
        return []

    @aedt_exception_handler
    def _creatematrix(self, sKey, mat):
        arg2 = ["NAME:" + sKey]
        if mat.property[sKey].type == "anisotropic":
            arg2.append("property_type:=")
            arg2.append("AnisoProperty")
            arg2.append("unit:=")
            if mat.property[sKey].unit:
                arg2.append(mat.property[sKey].unit)
            else:
                arg2.append("")
        else:
            arg2.append("property_type:=")
            arg2.append("TensorProperty")
            arg2.append("Symmetric:=")
            arg2.append(False)
            arg2.append("unit:=")
            if mat.property[sKey].unit:
                arg2.append(mat.property[sKey].unit)
            else:
                arg2.append("")
        id = 0
        for prop1 in mat.property[sKey].property_value:
            if self._parent.dataset_exists(mat.name + sKey + str(id)):
                arg2.append("component" + str(id + 1) + ':='), arg2.append("pwl($" + mat.name + prop1 + "0" + ",Freq)")
            else:
                arg2.append("component" + str(id + 1) + ':='), arg2.append(mat.property[sKey].property_value[id].value)
        return arg2

    @aedt_exception_handler
    def _create_dataset_in_aedt(self, name, tm, suffix=""):
        name_tmp = name
        if name_tmp == "dielectric_loss_tangent":
            name_tmp = "er_tand"
        if suffix:
            name_ds = name_tmp.replace(" ", "") + "_" + suffix
        else:
            name_ds = name_tmp.replace(" ", "")
        self._messenger.add_info_message('Property Data Set: ' + name_tmp)
        x = []
        y = []
        for ds in tm.ds:
            x.append(float(ds[0]))
            y.append(float(ds[1]))
        i = 1
        x, y = (list(t) for t in zip(*sorted(zip(x, y))))
        self._parent.create_dataset(name_ds, x, y, is_project_dataset=True)
        return True

    @aedt_exception_handler
    def _does_material_exists(self, szMat):
        listmatprj = [i.lower() for i in list(self.odefinition_manager.GetProjectMaterialNames())]
        if szMat.lower() in listmatprj:
            return True
        else:
            return False

