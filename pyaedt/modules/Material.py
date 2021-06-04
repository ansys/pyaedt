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

    def __init__(self):
        self.type = "simple"
        self.property_value = [BasicValue()]
        self.unit = None

    @aedt_exception_handler
    def set_type(self, type):
        """Set Material Property Type

        Parameters
        ----------
        type :
            simple", "nonlinear", "anisotropic", "tensor"

        Returns
        -------

        """
        self.type = type
        if self.type == "simple":
            self.property_value = [BasicValue()]
        elif self.type == "anisotropic":
            self.property_value = [BasicValue() for i in range(3)]
        elif self.type == "tensor":
            self.property_value = [BasicValue() for i in range(9)]
        elif self.type == "nonlinear":
            self.property_value = [BasicValue()]



class Material(object):
    """Class for Frequency Dependence Datasets"""

    class PropName(object):
        """list of constants of all possible materials constant names and how they are mapped to XML
        internalame=named used in script
        xmlname=named used in XML syntax

        Parameters
        ----------

        Returns
        -------

        """
        (Permittivity, Permeability, Conductivity, DielectricLossTangent, MagneticLossTangent,
         ThermalConductivity, MassDensity, SpecificHeat, ThermalExpCoeff,
         YoungsModulus, PoissonsRatio, Emissivity, Diffusivity, MolecularMass, Viscosity) = (
            'permittivity', 'permeability', 'conductivity', 'dielectric_loss_tangent', 'magnetic_loss_tangent',
            'thermal_conductivity', 'mass_density', 'specific_heat', 'thermal_expansion_coefficient',
            'youngs_modulus', 'poissons_ratio', 'emissivity', 'diffusivity', 'molecular_mass', 'viscosity')

    @property
    def odefinition_manager(self):
        """:return: Definition Manager"""
        return self._parent._oproject.GetDefinitionManager()

    @property
    def _omaterial_manager(self):
        """:return:Material Manager"""
        return self.odefinition_manager.GetManager("Material")

    @property
    def messenger(self):
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
        for el in MatProperties.aedtname:
            self.property[el].property_value[0].value = MatProperties.get_defaultvalue(aedtname=el)
            self.property[el].unit = MatProperties.get_defaultunit(aedtname=el)
            self.property[el].type = "simple"


    def get_number(self, fullname):
        """

        Parameters
        ----------
        fullname :
            

        Returns
        -------

        """
        if fullname in self.property:
            try:
                return float(self.property[fullname].property_value[0].value)
            except:
                ds = self.property[fullname].property_value[0].dataset
                if ds:
                    try:
                        return float(ds.ds[0][1])
                    except:
                        return 0
                return 0

    @aedt_exception_handler
    def get_data(self, fullname):
        """

        Parameters
        ----------
        fullname :
            

        Returns
        -------

        """
        if fullname in self.property:
            return self.property[fullname].type, self.property[fullname].property_value[0].value

    def is_conductor(self):
        """:return: Bool if material is conductor. Material is defined as conductor if cond>=100000"""
        cond = self.get_number('conductivity')
        if cond >= 100000:
            return True
        elif cond == 0:
            try:
                if "Freq" in self.property['conductivity'].property_value[0].value:
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
    def get_unit(self, propertyname):
        """

        Parameters
        ----------
        propertyname :
            str property

        Returns
        -------
        type
            property unit

        """
        if propertyname in self.property:
            return self.property[propertyname].unit
        return None

    @aedt_exception_handler
    def set_property_value(self, PropName, propvalue, idx=0):
        """Set Material Property Value

        Parameters
        ----------
        PropName :
            property
        propvalue :
            value
        idx :
            index. in case of tensor or anysotropic (0 by default)

        Returns
        -------
        type
            True

        """
        prop_conv = PropName.lower().replace(" ","_").replace("'","")
        self.property[prop_conv].property_value[idx].value = propvalue
        return True

    @aedt_exception_handler
    def get_property_value(self, PropertyConstant, idx=0):
        """Get Material Property Value

        Parameters
        ----------
        PropertyConstant :
            property
        idx :
            index. in case of tensor or anysotropic (0 by default)

        Returns
        -------
        type
            property value

        """
        return self.property[PropertyConstant].property_value[idx].value

    @aedt_exception_handler
    def set_property_dataset(self, PropName, dataset, idx=0):
        """Set Material Dataset Value

        Parameters
        ----------
        PropName :
            property
        dataset :
            dataset object
        idx :
            index. in case of tensor or anysotropic (0 by default)

        Returns
        -------

        """
        self.property[PropName].property_value[idx].dataset = dataset
        return True

    @aedt_exception_handler
    def get_property_dataset(self, PropertyConstant, idx=0):
        """Get Material Property Dataset

        Parameters
        ----------
        PropertyConstant :
            property
        idx :
            index. in case of tensor or anysotropic (0 by default)

        Returns
        -------
        type
            dataset object

        """
        return self.property[PropertyConstant].property_value[idx].dataset

    @aedt_exception_handler
    def set_property_therm_modifier(self, PropName, dataset, idx=0):
        """Set Material Property Thermal Modifier

        Parameters
        ----------
        PropName :
            property
        dataset :
            dataset object or list of values. in case list of values is provided, the dataset will be automatically created
        idx :
            index. in case of tensor or anysotropic (0 by default)

        Returns
        -------

        """
        if type(dataset) is list:
            ds = self.create_thermal_modifier(dataset)
        else:
            ds = dataset
        self.property[PropName].property_value[idx].thermalmodifier = ds

    @aedt_exception_handler
    def get_property_therm_modifier(self, PropertyConstant, idx=0):
        """Get Material Property Thermal Modifier Dataset

        Parameters
        ----------
        PropertyConstant :
            property
        idx :
            index. in case of tensor or anysotropic (0 by default)

        Returns
        -------
        type
            thermal modifier object

        """
        return self.property[PropertyConstant].property_value[idx].thermalmodifier

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

    @aedt_exception_handler
    def create_frequency_dataset(self, listtemp_val, unitx="Hz", unity=""):
        """Create a new frequency data set based on a list of values

        Parameters
        ----------
        listtemp_val :
            list of frequency modifiers. Example [[1e9, 58e6], [1.1e9, 57e6], [1.2e9,55e6]]
        unitx :
            unit type. Default Hertz
        unity :
            unit type. Default ""

        Returns
        -------
        type
            tm obhect

        """
        tm = Dataset()
        tm.type = "Absolute"
        tm.namex = "Frequency"
        tm.unitx = unitx
        tm.unity = unity
        tm.ds = listtemp_val
        return tm

    @aedt_exception_handler
    def set_nonlinear_dataset(self, propertyname, listtemp_val, unitx="A_per_meter", unity="tesla"):
        """Create a new nonlinear data set based on a list of values

        Parameters
        ----------
        listtemp_val :
            list of frequency modifiers. Example [[1e9, 58e6], [1.1e9, 57e6], [1.2e9,55e6]]
        unitx :
            unit type. Default A_per_meter
        unity :
            unit type. Default tesla
        propertyname :
            

        Returns
        -------
        type
            Bool

        """
        if len(listtemp_val)<3:
            self.messenger.add_error_message("Dataset has to start from 0 or negative and has to contain at least 3 points")
            return False
        self.property[propertyname].set_type("nonlinear")
        tm = Dataset()
        tm.type = "Absolute"
        tm.namex = "Frequency"
        tm.unitx = unitx
        tm.unity = unity
        tm.ds = listtemp_val
        self.property[propertyname].property_value[0].dataset = tm
        return True

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
        for props in self.property:
            id = 0
            for vals in self.property[props].property_value:
                if vals.thermalmodifier:
                    tms[self.name.replace("-","_") + props + "TH" + str(id)] = [id, props, vals.thermalmodifier]
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
                self.createdatasets(fd, fds[fd][2])

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

        if self.does_material_exists(args):
            self.odefinition_manager.EditMaterial(args,arg)
        else:
            self.odefinition_manager.AddMaterial(arg)
        return True


    @aedt_exception_handler
    def _createTM(self, tms):
        """

        Parameters
        ----------
        tms :
            

        Returns
        -------

        """
        arg2 = ["NAME:ModifierData"]
        arg3 = ["NAME:ThermalModifierData", "modifier_data:=", "thermal_modifier_data"]
        arg4 = ["NAME:all_thermal_modifiers"]
        for tm in tms:
            if type(tms[tm][2]) is Dataset:
                if not self._parent.dataset_exists(tm):
                    self.createdatasets(tm, tms[tm][2])
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
        """

        Parameters
        ----------
        sKey :
            
        dataset :
            

        Returns
        -------

        """
        #TODO Support nonlinear
        return []

    @aedt_exception_handler
    def _creatematrix(self, sKey, mat):
        """

        Parameters
        ----------
        sKey :
            
        mat :
            

        Returns
        -------

        """
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
    def createdatasets(self, name, tm, suffix=""):
        """createdataset(material name, property name, dataset)
        createDataset for material matname with property name

        Parameters
        ----------
        name :
            name of datase to create in aedt
        tm :
            dataset object
        suffix :
            suffix to apply to name (Default value = "")

        Returns
        -------
        type
            Bool

        """

        #arg = []
        name_tmp = name
        if name_tmp == "dielectric_loss_tangent":
            name_tmp = "er_tand"
        if suffix:
            #arg.append("Name:$" + name_tmp.replace(" ", "") + "_" + suffix)
            name_ds = name_tmp.replace(" ", "") + "_" + suffix
        else:
            #arg.append("Name:$" + name_tmp.replace(" ", "") )
            name_ds = name_tmp.replace(" ", "")
        self.messenger.add_info_message('Property Data Set: ' + name_tmp)
        #arg2 = []
        x = []
        y = []
        for ds in tm.ds:
            # arg3 = []
            # arg3.append("NAME:Coordinate")
            # arg3.append("X:="), arg3.append(float(ds[0]))
            # arg3.append("Y:="), arg3.append(float(ds[1]))
            # arg2.append(arg3)
            x.append(float(ds[0]))
            y.append(float(ds[1]))
        i = 1
        x, y = (list(t) for t in zip(*sorted(zip(x, y))))
        # import operator
        # arg2 = sorted(arg2, key=operator.itemgetter(2))
        # arg2.insert(0, "Name:Coordinates")
        # arg.append(arg2)
        # self.oproject.AddDataset(arg)
        self._parent.create_dataset(name_ds, x, y, is_project_dataset=True)
        return True

    @aedt_exception_handler
    def does_material_exists(self, szMat):
        """Check if a material is already defined in the Project

        Parameters
        ----------
        szMat :
            material name

        Returns
        -------
        type
            Bool

        """
        listmatprj = [i.lower() for i in list(self.odefinition_manager.GetProjectMaterialNames())]
        if szMat.lower() in listmatprj:
            return True
        else:
            return False

