"""
Material Library Class
----------------------------------------------------------------


Description
==================================================

This class contains all the functionalities to create and edit materials


================

"""
from __future__ import absolute_import
import os
import xml.etree.ElementTree as ET
from .Material import *
from ..generic.general_methods import aedt_exception_handler


@aedt_exception_handler
def indent(elem, level=0):
    """Creates an Indented structure of the XML

    Parameters
    ----------
    elem :
        
    level :
         (Default value = 0)

    Returns
    -------

    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

class Materials(object):
    """Material Management"""
    @property
    def odefinition_manager(self):
        """ """
        return self._parent._oproject.GetDefinitionManager()

    @property
    def omaterial_manager(self):
        """ """
        return self.odefinition_manager.GetManager("Material")

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def oproject(self):
        """ """
        return self._parent._oproject

    def __init__(self, parent):
        self._parent = parent
        self.material_keys = defaultdict(Material)
        self._load_from_project()
        self.messenger.add_info_message('Successfully loaded project materials !')
        pass

    def __len__(self):
        return len(self.material_keys)

    def __iter__(self):
        return self.material_keys.itervalues()

    @aedt_exception_handler
    def load_from_file(self, filename, project_as_precedence=True):
        """Load materials from file

        Parameters
        ----------
        filename :
            full filename path (xml)
        project_as_precedence :
            bool (Default value = True)

        Returns
        -------
        type
            bool

        """
        mats = self.load_from_xml_full(filename)
        for mat in mats:
            if mat in self.material_keys and project_as_precedence:
                self.messenger.add_warning_message(
                    "Material " + mat + " that was present in the file is already present in the project. Skipping it")
            elif mat in self.material_keys and not project_as_precedence:
                self.material_keys[mat] = mats[mat]
                self.messenger.add_warning_message(
                    "Material " + mat + " that was present in the file is already present in the project. Overwriting it")
            else:
                self.material_keys[mat] = mats[mat]

        return True

    def _load_from_project(self):
        """Load materials from project"""
        mats = self.odefinition_manager.GetProjectMaterialNames()
        for el in mats:
            try:
                self._aedmattolibrary(el)
            except Exception as e:
                self.messenger.add_info_message('aedmattolibrary failed for material {}'.format(el))

    @aedt_exception_handler
    def _aedmattolibrary(self, matname):
        """

        Parameters
        ----------
        matname :
            

        Returns
        -------

        """
        matname = matname.lower()
        matprop = list(self.omaterial_manager.GetData(matname))
        newmat = Material(self._parent)
        newmat.name = matname
        newmat.origin = "Project"
        for el in matprop:
            if type(el) is str:
                if el[:-2] in MatProperties.aedtname:
                    if "pwl" in matprop[matprop.index(el) + 1]:
                        prop = matprop[matprop.index(el) + 1]
                        fddataset = self._read_dataset(prop)
                        newmat.property[el[:-2]].property_value[0].dataset = fddataset
                    else:
                        newmat.property[el[:-2]].property_value[0].value = matprop[matprop.index(el) + 1]
                    newmat.property[el[:-2]].type = "simple"
            elif type(el) is list or type(el) is tuple:
                if el[0] == 'NAME:ModifierData':
                    tlist = list(el[1][3])
                    del tlist[0]
                    for tm in tlist:
                        propth = tm[2]
                        idth = int(tm[4])
                        if tm[8]==True:
                            valth = tm[10]
                            if "pwl" not in valth and "temp" not in valth.lower():
                                fddataset = self._read_dataset(valth)
                            else:
                                fddataset = valth
                            newmat.property[propth].property_value[idth].thermalmodifier = fddataset

                        else:
                            thclosed = ClosedFormTM()
                            thclosed.Tref=tm[10]
                            thclosed.C1=tm[12]
                            thclosed.C2=tm[14]
                            thclosed.TL=tm[16]
                            thclosed.TU=tm[18]
                            thclosed.autocalculation=tm[20]
                            if not thclosed.autocalculation:
                                thclosed.TML=tm[22]
                                thclosed.TMU = tm[24]
                            newmat.property[propth].property_value[idth].thermalmodifier = thclosed


                elif el[0][5:] in MatProperties.aedtname:
                    propertyname = el[0][5:]
                    proparray = el
                    proptype = proparray[2]
                    if proptype == "AnisoProperty":
                        newmat.property[propertyname].set_type("anisotropic")
                        newmat.property[propertyname].type = "anisotropic"
                        i = 0
                        while i < 3:
                            val = proparray[5 + i * 2]
                            if "pwl" in val and "if(" not in val:
                                prop = val
                                fddataset = self._read_dataset(prop)
                                newmat.property[propertyname].property_value[i].dataset = fddataset
                            else:
                                newmat.property[propertyname].property_value[i].value = val
                            i += 1
                    elif proptype == "TensoProperty":
                        newmat.property[propertyname].type = "tensor"
                        # TODO check and add Tensor
                    elif proptype == "nonlinear" and (propertyname == 'permittivity' or propertyname == 'conductivity'):
                        newmat.property[propertyname].type = "nonlinear"
                        ds = Dataset()
                        array = proparray[3]
                        ds.unitx = array[1][1]
                        ds.unity = array[1][2]
                        i =2
                        ds.ds = []
                        while i < len(array):
                            ds.ds.append([array[i][1], array[i][2]])
                            i += 1
                        newmat.property[propertyname].property_value[0].dataset = ds
                    elif proptype == "nonlinear" and propertyname == 'permeability':
                        newmat.property[propertyname].type = "nonlinear"
                        idx = proparray.index("HUnit:=")
                        ds = Dataset()
                        ds.unitx = proparray[idx+1]
                        ds.unity = proparray[idx+3]
                        for p in proparray:
                            if (type(p) is tuple or type(p) is list) and p[0] and "BHCoordinates" in p[0]:
                                i = 2
                                ds.ds = []
                                while i < len(p):
                                    ds.ds.append([p[i][1], p[i][2]])
                                    i += 1
                                newmat.property[propertyname].property_value[0].dataset = ds

                elif el[0] == 'NAME:thermal_material_type':
                    newmat.thermal_material_type = el[4]
        self.material_keys[matname] = newmat
        return True

    @aedt_exception_handler
    def _read_dataset(self, prop):
        """

        Parameters
        ----------
        prop :
            

        Returns
        -------

        """
        start = prop.find("$")
        stop = prop.find(",")
        dsname = prop[start:stop - len(prop)]
        filename = "C:\\Temp\\ds.tab"
        self.oproject.ExportDataset(dsname, filename)
        with open(filename) as f:
            lines = f.readlines()
        i = 1
        dsdata = []
        while i < len(lines):
            a = lines[i].split(' \t')
            dsdata.append([a[0], a[1]])
            i += 1
        fddataset = Dataset()
        fddataset.namex = "Frequency"
        fddataset.unitx = lines[0][2:]
        fddataset.ds = dsdata
        return fddataset

    @aedt_exception_handler
    def checkifmaterialexists(self, mat):
        """Check if Material Exists

        Parameters
        ----------
        mat :
            material name

        Returns
        -------
        type
            True/False

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

    @aedt_exception_handler
    def check_thermal_modifier(self, mat):
        """Check the termal modifier of predefined material

        Parameters
        ----------
        mat :
            material name

        Returns
        -------
        type
            bool

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
            for el in omat.property:
                if omat.property[el].property_value[0].thermalmodifier:
                    return True
        return False

    @aedt_exception_handler
    def check_thermal_modifier_OLD(self, mat):
        """

        Parameters
        ----------
        mat :
            

        Returns
        -------

        """
        mat = mat.lower()
        exists = True
        if mat not in self.material_keys:
            exists = self.checkifmaterialexists(mat)
        if exists:
            omat = self.material_keys[mat]
            for el in omat.property:
                if omat.property[el].property_value[0].thermalmodifier:
                    return True
        return False

    @aedt_exception_handler
    def creatematerial(self, materialname):
        """The function create a new material named materialname and apply defaults value and return the material object
        that allows user to customize the material
        The function will not update the material in

        Parameters
        ----------
        materialname :
            material name

        Returns
        -------
        type
            Material Object

        """
        materialname = materialname.lower()
        self.messenger.add_info_message('Adding New Material material to Project Library: ' + materialname)
        if materialname in self.material_keys:
            self.messenger.add_warning_message(
                "Warning. The material is already in database. Please change name or edit it")
            return self.material_keys[materialname]
        else:
            material = Material(self._parent)
            material.name = materialname
            self.messenger.add_info_message("Material added. Please edit it to update in Desktop")
            self.material_keys[materialname] = material
            return self.material_keys[materialname]

    @aedt_exception_handler
    def creatematerialsurface(self, material_name):
        """The function create a new material surface named args
        material args properties are loaded from the XML file database amat.xml

        Parameters
        ----------
        material_name :
            material name

        Returns
        -------
        type
            Material emissivity

        """
        material_name = material_name.lower()
        self.messenger.add_info_message('Adding New Material Surface to Icepak Project Library: ' + material_name)
        materials = self.material_keys
        if materials is None:
            self.messenger.add_error_message("Error. XML not loaded. Run read_material_from_xml function")
            return
        matsurf = None
        for mat in materials:
            if material_name == mat.GetName():
                matsurf = mat
        defaultEmissivity = "0.8"
        if matsurf:
            defaultEmissivity = str(matsurf.GetParameter("emissivity"))

        arg = []
        arg.append("Name:" + material_name)
        arg.append("CoordinateSystemType:=")
        arg.append("Cartesian")
        arg.append("BulkOrSurfaceType:=")
        arg.append(2)
        arg.append(["NAME:PhysicsTypes", "set:=", ["Thermal"]])
        arg.append(["NAME:PhysicsTypes", "set:=", ["Thermal"]])
        arg.append("surface_emissivity:=")
        arg.append(defaultEmissivity)
        self.omaterial_manager.AddSurfaceMaterial(arg)
        return defaultEmissivity


    def create_mat_project_vars(self, matlist):
        """Create Material Properties variables based on a material list

        Parameters
        ----------
        matlist :
            list of material properties

        Returns
        -------
        type
            matprop

        """
        matprop={}
        for prop in MatProperties.aedtname:
            matprop[prop] = []
            for mat in matlist:
                try:
                    matprop[prop].append(float(mat.property[prop].property_value[0].value))
                except:
                    self.messenger.add_warning_message("Warning. Wrong parsed property. Reset to 0")
                    matprop[prop].append(0)
        return matprop

    @aedt_exception_handler
    def creatematerial_sweeps(self, swargs, matname, enableTM=True):
        """The function create a new material named  made of an array of materials args
        If material needs a dataset (thermal modifier) than a dataset is created
        material args properties are loaded from the XML file database amat.xml
        enableTM: Boolean enable Thermal modifier in material description. At moment unused

        Parameters
        ----------
        swargs :
            list of materials to be merged into single sweep material
        matname :
            name of sweep material
        enableTM :
            bool (Default value = True)

        Returns
        -------
        type
            name of project variable index

        """
        matsweep = []
        matname = matname.lower()
        for args in swargs:
            if args in self.material_keys:
                matsweep.append(self.material_keys[args])
            elif self.checkifmaterialexists(args):
                self._aedmattolibrary(args)
                matsweep.append(self.material_keys[args])

        mat_dict = self.create_mat_project_vars(matsweep)
        newmat = self.creatematerial(matname)
        index = "$ID"+matname
        self._parent[index] = 0
        for el in mat_dict:
            self._parent["$"+matname+el] = mat_dict[el]
            newmat.property[el].property_value[0].value = "$"+matname+el+"["+ index + "]"
            # TODO add Thermal modifier
        newmat.update()
        return index

    @aedt_exception_handler
    def duplicate_material(self, material, new_name):
        """Duplicate Material

        Parameters
        ----------
        material :
            material original name
        new_name :
            target name

        Returns
        -------
        type
            new material object

        """
        newMat = material
        newMat.name = new_name.lower()
        self.material_keys[new_name] = newMat
        return newMat

    @aedt_exception_handler
    def GetConductors(self):
        """Get List of conductors in material database
        
        :return:list of string

        Parameters
        ----------

        Returns
        -------

        """
        data = []
        for key, mat in self.material_keys.items():
            if mat.is_conductor():
                data.append(key)
        return data

    @aedt_exception_handler
    def GetDielectrics(self):
        """Get List of dielectrics in material database
        
        :return:list of string

        Parameters
        ----------

        Returns
        -------

        """
        data = []
        for key, mat in self.material_keys.items():
            if mat.is_dielectric():
                data.append(key)
        return data

    @aedt_exception_handler
    def get_material_list(self):
        """Get List of material database
        
        :return:list of string

        Parameters
        ----------

        Returns
        -------

        """
        data = list(self.material_keys.keys())
        return data

    @aedt_exception_handler
    def get_material_count(self):
        """Get number of materials
        
        :return:number of materials

        Parameters
        ----------

        Returns
        -------

        """
        return len(self.material_keys)

    @aedt_exception_handler
    def get_material(self, szMat):
        """Get material object

        Parameters
        ----------
        szMat :
            material name

        Returns
        -------
        type
            Material object if exists

        """
        szMat = szMat.lower()
        if szMat in self.material_keys:
            return self.material_keys[szMat]
        else:
            return None

    @aedt_exception_handler
    def get_material_properties(self, szMat):
        """Get material dictionary properties

        Parameters
        ----------
        szMat :
            material

        Returns
        -------
        type
            Dictionary of all material properties

        """
        szMat = szMat.lower()
        props = {}
        if szMat in self.material_keys:
            for el in MatProperties.aedtname:
                props[el] = self.material_keys[szMat].property[el].property_value[0].value
            return props
        else:
            return None

    @aedt_exception_handler
    def setup_air_properties(self):
        """Setup Air properties
        
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self.omaterial_manager.EditMaterial("AIR",
                                                ["NAME:AIR", "CoordinateSystemType:=", "Cartesian",
                                                 "BulkOrSurfaceType:=", 1,
                                                 ["NAME:PhysicsTypes", "set:=", ["Thermal"]],
                                                 ["NAME:AttachedData",
                                                  ["NAME:MatAppearanceData", "property_data:=", "appearance_data",
                                                   "Red:=", 230,
                                                   "Green:=", 230,
                                                   "Blue:=", 230,
                                                   "Transparency:=", 0.949999988079071]
                                                  ],
                                                 "thermal_conductivity:=", "0.0261",
                                                 "mass_density:=", "1.1614",
                                                 "specific_heat:=", "1005",
                                                 "thermal_expansion_coeffcient:=", "0.003333",
                                                 ["NAME:thermal_material_type", "property_type:=", "ChoiceProperty",
                                                  "Choice:=", "Fluid"],
                                                 "diffusivity:=", "2.92e-05",
                                                 "molecular_mass:=", "0.028966",
                                                 "viscosity:=", "1.853e-05"])
        return True

    @aedt_exception_handler
    def load_from_xml_full(self, Filename=None):
        """New Function for loading materials from XML. Previous version didn't allow read/write on the same file.

        Parameters
        ----------
        Filename :
            Complete Filename (Default value = None)

        Returns
        -------
        type
            material dictionary

        """
        self.messenger.add_info_message('InitFromXml: Enter')
        o_mat_xml = {}
        i = 0
        if Filename is None:
            # Try and find it in path
            sFilename = 'pyaedt\\misc\\amat.xml'
        else:
            sFilename = Filename
        self.messenger.add_info_message('xml filename: {}'.format(sFilename))
        if os.path.exists(os.path.abspath(sFilename)):
            with open(sFilename) as xml_File:
                cntrl2 = ET.parse(xml_File)
                cntrl3 = cntrl2.getroot()[0]
                tagcntrl = cntrl3.tag
                tagattr = cntrl3.attrib
                if tagcntrl == 'Materials':
                    # first level (e.g. <Materials>)
                    self.messenger.add_info_message('Found Materials in the Database')
                    # Add Material to Database
                    for items in cntrl3:
                        # 2nd level (e.g. <Material name="Aluminum">)
                        szMatName = items.attrib['name'].lower()
                        o_mat_xml[szMatName] = Material(self._parent)
                        o_mat_xml[szMatName].name = szMatName
                        o_mat_xml[szMatName].origin = "XML"
                        for item in items:
                            # 3rd level (e.g. <Property name="Conductivity">)
                            maxids = 0
                            id = 0
                            if 'Behavior' in item.attrib:
                                if item.attrib['Behavior'] == "Isotropic":
                                    beahvior = "simple"
                                elif item.attrib['Behavior'] == "Orthotropic":
                                    beahvior = "anisotropic"
                                    maxids = 2
                                elif item.attrib['Behavior'] == "Tensor":
                                    beahvior = "tensor"
                                    maxids = 8
                            else:
                                beahvior = "simple"
                            if item.attrib['name'] == "Fluid Properties":
                                o_mat_xml[szMatName].thermal_material_type = "Fluid"
                            for data in item:
                                # 4th level (e.g. <Data name="Conductivity" unit="[siemens m^-1]">)
                                if beahvior == "simple":
                                    aedtname = MatProperties.aedtname[MatProperties.fullname.index(data.attrib['name'])]
                                elif beahvior == "anisotropic":
                                    if "direction" in data.attrib['name']:
                                        aedtname = MatProperties.aedtname[
                                            MatProperties.fullname.index(data.attrib['name'][:-12])]
                                    else:
                                        aedtname = MatProperties.aedtname[
                                            MatProperties.fullname.index(data.attrib['name'][:-3])]

                                else:
                                    aedtname = MatProperties.aedtname[
                                        MatProperties.fullname.index(data.attrib['name'][:-3])]

                                if 'unit' in data.attrib:
                                    o_mat_xml[szMatName].property[aedtname].unit = data.attrib['unit']
                                if maxids > (len(o_mat_xml[szMatName].property[aedtname].property_value) - 1):
                                    o_mat_xml[szMatName].property[aedtname].set_type(beahvior)
                                for el in data:
                                    # 5th level e.g. (<Double>1.0</Double> OR <DataSets XName="Temperature" type="Relative" unit="[C]">)
                                    if el.tag == "Double":
                                        o_mat_xml[szMatName].property[aedtname].property_value[id].value = el.text
                                    elif el.tag == "DataSets" and el.attrib['XName'] != "Temperature":
                                        ds = Dataset()
                                        listtoadd = []
                                        for d1 in el:
                                            listtoadd.append([d1.attrib['X'], d1.attrib['Y']])
                                        ds.ds = listtoadd
                                        if 'XName' in el.attrib:
                                            ds.namex = el.attrib['XName']
                                        else:
                                            ds.namex = ""
                                        if 'YName' in el.attrib:
                                            ds.namey = el.attrib['YName']
                                        else:
                                            ds.namey = ""
                                        if 'type' in el.attrib:
                                            ds.type = el.attrib['type']
                                        else:
                                            ds.type = "Absolute"
                                        if 'unit' in el.attrib:
                                            ds.unit = el.attrib['unit']
                                        else:
                                            ds.unit = ""
                                        o_mat_xml[szMatName].property[aedtname].property_value[id].dataset = ds
                                    elif el.tag == "DataSets" and el.attrib['XName'] == "Temperature":
                                        ds = Dataset()
                                        listtoadd = []
                                        for d1 in el:
                                            listtoadd.append([d1.attrib['X'], d1.attrib['Y']])
                                        ds.ds = listtoadd
                                        if 'XName' in el.attrib:
                                            ds.namex = el.attrib['XName']
                                        else:
                                            ds.namex = ""
                                        if 'YName' in el.attrib:
                                            ds.namey = el.attrib['YName']
                                        else:
                                            ds.namey = ""
                                        if 'type' in el.attrib:
                                            ds.type = el.attrib['type']
                                        else:
                                            ds.type = "Relative"
                                        if 'unit' in el.attrib:
                                            ds.unit = el.attrib['unit']
                                        else:
                                            ds.unit = ""
                                        o_mat_xml[szMatName].property[aedtname].property_value[id].thermalmodifier = ds
                                if id == maxids:
                                    id = 0
                                else:
                                    id += 1

                        i += 1
        return o_mat_xml


    @aedt_exception_handler
    def py2xmlFull(self, filename):
        """convert material object to xml

        Parameters
        ----------
        filename :
            name of the file to save

        Returns
        -------

        """
        header = ET.Element('c:Control')
        header.set("schemaVersion", "2.0")
        header.set("xmlns:c", "http://www.ansys.com/control")
        header.set("Editedby", "pyaedt")
        materials = ET.SubElement(header, 'Materials')
        i = 0
        for mat in self.material_keys:
            self.messenger.add_info_message("adding material " + mat)
            material = ET.SubElement(materials, 'Material')
            material.set("name", mat)
            for propname in MatProperties.aedtname:
                xmlproperty = ET.SubElement(material, 'Property')
                xmlproperty.set("name", propname)
                prop = self.material_keys[mat].property[propname]
                if prop.type == "anisotropic":
                    xmlproperty.set("Behavior", "Orthotropic")
                for matdata in prop.property_value:
                    data = ET.SubElement(xmlproperty, 'Data')
                    data.set("name", propname)
                    if prop.unit:
                        data.set("unit", prop.unit)
                    val = ET.SubElement(data, 'Double')
                    val.text = str(matdata.value)

                    if matdata.dataset:
                        ds = matdata.dataset
                        dataset = ET.SubElement(data, 'DataSets')
                        dataset.set("XName", ds.namex)
                        if ds.type:
                            dataset.set("type", ds.type)
                        if ds.unit:
                            dataset.set("unit", ds.unit)
                        if ds.namex:
                            dataset.set("YName", ds.namey)
                        if ds.namez:
                            dataset.set("ZName", ds.namez)
                        for el in ds.ds:
                            datasetvalues = ET.SubElement(dataset, 'DataSet')
                            datasetvalues.set("X", str(el[0]))
                            datasetvalues.set("Y", str(el[1]))
                            if len(el) > 2:
                                datasetvalues.set("Z", str(el[2]))
                    if matdata.thermalmodifier:
                        ds = matdata.thermalmodifier
                        dataset = ET.SubElement(data, 'DataSets')
                        dataset.set("XName", ds.namex)
                        if ds.type:
                            dataset.set("type", ds.type)
                        if ds.unitx:
                            dataset.set("unitx", ds.unit)
                        if ds.unity:
                            dataset.set("unity", ds.unity)
                        if ds.unitz:
                            dataset.set("unitz", ds.uniz)
                        if ds.namex:
                            dataset.set("YName", ds.namey)
                        if ds.namez:
                            dataset.set("ZName", ds.namez)
                        for el in ds.ds:
                            datasetvalues = ET.SubElement(dataset, 'DataSet')
                            datasetvalues.set("X", str(el[0]))
                            datasetvalues.set("Y", str(el[1]))
                            if len(el) > 2:
                                datasetvalues.set("Z", str(el[2]))

            i += 1
        indent(header)
        ET.ElementTree(header).write(filename, encoding='utf-8', xml_declaration=True)
        return True
