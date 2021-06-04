import csv
import re

from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from ..application.Analysis import Analysis
from ..modeler.Model3D import Modeler3D
from ..modules.MeshIcepak import IcepakMesh


class FieldAnalysisIcepak(Analysis, object):
    """AEDT_Icepak_FieldAnalysis
    Class for 3D Field Analysis Setup (Icepak)

    It is automatically initialized by Application call (like HFSS,
    Q3D...). Refer to Application function for inputs definition

    Parameters
    ----------

    Returns
    -------

    """
    def __init__(self, application, projectname, designname, solutiontype, setup_name=None):
        Analysis.__init__(self, application, projectname, designname, solutiontype, setup_name)
        self._modeler = Modeler3D(self)
        self._mesh = IcepakMesh(self)
        #self._post = PostProcessor(self)
        self.modeler.primitives.refresh()
    @property
    def modeler(self):
        """ """
        return self._modeler

    @property
    def mesh(self):
        """ """
        return self._mesh

    # @property
    # def post(self):
    #     return self._post

    @aedt_exception_handler
    def apply_icepak_settings(self, ambienttemp=20, gravityDir=5, perform_minimal_val=True, default_fluid="air",
                              default_solid="Al-Extruded", default_surface="Steel-oxidised-surface"):
        """Apply Icepak Default Design Settings like Ambient Temperature and Gravity.

        Parameters
        ----------
        ambienttemp :
            Ambient Temperature. It can be an integer or a parameter already created in AEDT (Default value = 20)
        gravityDir :
            Gravity direction index [0, 5] (Default value = 5)
        perform_minimal_val :
            True Perform Minimal validation. False perform Full Validation (Default value = True)
        default_fluid :
            default Fluid ."Air"
        default_solid :
            default Solid ."Al-Extruded"
        default_surface :
            default Surface ."Steel-oxidised-surface"

        Returns
        -------
        type
            True

        """
        if type(ambienttemp) is int:
            AmbientTemp = str(ambienttemp)+"cel"
        else:
            AmbientTemp = ambienttemp

        IceGravity = ["X", "Y", "Z"]
        GVPos = False
        if int(gravityDir) > 2:
            GVPos = True
        GVA = IceGravity[int(gravityDir) - 3]
        self.odesign.SetDesignSettings(
            ["NAME:Design Settings Data", "Perform Minimal validation:=", perform_minimal_val, "Default Fluid Material:=",
             default_fluid, "Default Solid Material:=", default_solid, "Default Surface Material:=", default_surface,
             "AmbientTemperature:=", AmbientTemp, "AmbientPressure:=", "0n_per_meter_sq",
             "AmbientRadiationTemperature:=", AmbientTemp,
             "Gravity Vector CS ID:=", 1, "Gravity Vector Axis:=", GVA, "Positive:=", GVPos],
            ["NAME:Model Validation Settings"])
        return True

    @aedt_exception_handler
    def get_property_value(self, objectname, property, type=None):
        """Get Design Property Value of specific object.

        Parameters
        ----------
        type :
            type of the property. "Boundary", "Excitation", "Setup", "Mesh" (Default value = None)
        objectname :
            param property:
        property :
            

        Returns
        -------
        type
            property value
            
            
            :Example:
            
            val = ipk.get_property_value('BoundarySetup:Source1', 'Total Power')

        """
        #TODO To be improved
        boundary = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        excitation = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        setup = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "General", "Maxwell3D": "General"}
        mesh = {"HFSS": "MeshSetupTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        all = {"HFSS": ["HfssTab", "MeshSetupTab"], "Icepak": ["Icepak"], "Q3D": ["Q3D", "General"], "Maxwell3D" : ["Maxwell3D", "General"]}
        if type == "Boundary":
            propserv = boundary[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, objectname, property)
            return val

        elif type == "Setup":
            propserv = setup[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, objectname, property)
            return val
        elif type == "Excitation":
            propserv = excitation[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, objectname, property)
            return val

        elif type == "Mesh":
            propserv = mesh[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, objectname, property)
            return val
        else:
            propservs = all[self._design_type]
            for propserv in propservs:
                properties = list(self.odesign.GetProperties(propserv, objectname))
                if property in properties:
                    val = self.odesign.GetPropertyValue(propserv, objectname, property)
                    return val
        return None

    @aedt_exception_handler
    def copy_solid_bodies_from(self, design, object_list=None, no_vacuum=True, no_pec=True):
        """Copy all the list of object from one design to active one

        Parameters
        ----------
        design :
            starting application object (examples hfss1= HFSS3DLayout)
        object_list :
            List of object to copy (Default value = None)
        no_vacuum : bool
            define if vacuum objects have to be copied (Default value = True)
        no_pec : bool
            define if pec objects have to be copied (Default value = True)

        Returns
        -------
        type
            True if succeeded

        """
        body_list = design.modeler.solid_bodies
        selection_list = []
        material_properties = design.modeler.primitives.objects
        for body in body_list:
            include_object = True
            if object_list:
                if body not in object_list:
                    include_object = False
            for key, val in material_properties.items():
                if val.name == body:
                    if no_vacuum and val.material_name == 'Vacuum':
                        include_object = False
                    if no_pec and val.material_name == 'pec':
                        include_object = False
            if include_object:
                selection_list.append(body)
        design.modeler.oeditor.Copy(["NAME:Selections", "Selections:=", ','.join(selection_list)])
        self.modeler.oeditor.Paste()
        self.modeler.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def assignmaterial(self, obj, mat):
        """The function assigns Material mat to object obj. If material mat is not present it will be created

        Parameters
        ----------
        obj : str, list
            list of objects to which assign materials
        mat : str
            material to assign

        Returns
        -------
        type
            True if succeeded | False if failed

        """
        mat = mat.lower()
        selections = self.modeler.convert_to_selections(obj)
        arg1 = ["NAME:Selections"]
        arg1.append("Selections:="), arg1.append(selections)
        arg2 = ["NAME:Attributes"]
        arg2.append("MaterialValue:="), arg2.append(chr(34) + mat + chr(34))
        if mat in self.materials.material_keys:
            Mat = self.materials.material_keys[mat]
            Mat.update()
            if Mat.is_dielectric():
                arg2.append("SolveInside:="), arg2.append(True)
            else:
                arg2.append("SolveInside:="), arg2.append(False)
            self.modeler.oeditor.AssignMaterial(arg1, arg2)
            self._messenger.add_info_message('Assign Material ' + mat + ' to object ' + selections)
            self.materials._aedmattolibrary(mat)
            return True
        elif self.materials.checkifmaterialexists(mat):
            Mat = self.materials.material_keys[mat]
            if Mat.is_dielectric():
                arg2.append("SolveInside:="), arg2.append(True)
            else:
                arg2.append("SolveInside:="), arg2.append(False)
            self.modeler.oeditor.AssignMaterial(arg1, arg2)
            self._messenger.add_info_message('Assign Material ' + mat + ' to object ' + selections)
            return True
        else:
            self._messenger.add_error_message("Material Does Not Exists")
            return False

    @aedt_exception_handler
    def _assign_property_to_mat(self,newmat, val, property):
        """

        Parameters
        ----------
        newmat :
            
        val :
            
        property :
            

        Returns
        -------

        """
        try:
            if "@" not in val:
                value = float(val)
                newmat.set_property_value(property, value)

            else:
                value_splitted = val.split(",")
                value_list = [
                    [float(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", a)[0]) for a in
                     d.split("@")] for d in value_splitted]
                val0 = float(value_list[0][0])
                for el in value_list:
                    el.reverse()
                    el[1] = float(el[1])/val0
                newmat.set_property_value(property, val0)
                dataset = newmat.create_thermal_modifier(value_list)
                newmat.set_property_therm_modifier(property, dataset)
            return True
        except:
            return False

    @aedt_exception_handler
    def assignmaterial_from_sherlock_files(self, csv_component, csv_material):
        """Assign material to objects in design based on csv files obtained from Sherlock Tool

        Parameters
        ----------
        csv_component :
            csv containing component properties including material name
        csv_material :
            csv containing material properties

        Returns
        -------
        type
            Bool

        """
        with open(csv_material) as csvfile:
            csv_input = csv.reader(csvfile)
            material_header = next(csv_input)
            data = list(csv_input)
            k = 0
            material_data = {}
            for el in material_header:
                material_data[el] = [i[k] for i in data]
                k += 1
        with open(csv_component) as csvfile:
            csv_input = csv.reader(csvfile)
            component_header = next(csv_input)
            data = list(csv_input)
            k = 0
            component_data = {}
            for el in component_header:
                component_data[el] = [i[k] for i in data]
                k += 1
        all_objs = self.modeler.primitives.get_all_objects_names()
        i = 0
        for mat in material_data["Name"]:
            list_mat_obj = ["COMP_" + rd for rd, md in zip(component_data["Ref Des"], component_data["Material"]) if
                            md == mat]
            list_mat_obj += [rd for rd, md in zip(component_data["Ref Des"], component_data["Material"]) if
                            md == mat]
            list_mat_obj = [mo for mo in list_mat_obj if mo in all_objs]
            if list_mat_obj:
                if not self.materials.checkifmaterialexists(mat):
                    newmat = self.materials.creatematerial(mat)
                    if "Material Density" in material_data:
                        value = material_data["Material Density"][i]
                        self._assign_property_to_mat(newmat, value, newmat.PropName.MassDensity)
                    if "Thermal Conductivity" in material_data:
                        value = material_data["Thermal Conductivity"][i]
                        self._assign_property_to_mat(newmat, value, newmat.PropName.ThermalConductivity)
                    if "Material CTE" in material_data:
                        value = material_data["Material CTE"][i]
                        self._assign_property_to_mat(newmat, value, newmat.PropName.ThermalExpCoeff)
                    if "Poisson Ratio" in material_data:
                        value = material_data["Poisson Ratio"][i]
                        self._assign_property_to_mat(newmat, value, newmat.PropName.PoissonsRatio)
                    if "Elastic Modulus" in material_data:
                        value = material_data["Elastic Modulus"][i]
                        self._assign_property_to_mat(newmat, value, newmat.PropName.YoungsModulus)
                    newmat.update()
                self.assignmaterial(list_mat_obj, mat)
                for o in list_mat_obj:
                    self.modeler.primitives.objects[self.modeler.primitives.get_obj_id(o)].material_name = mat
            i += 1
            all_objs = [ao for ao in all_objs if ao not in list_mat_obj]
        return True

    @aedt_exception_handler
    def get_all_conductors_names(self):
        """Get all conductors in active design
        
        
        :return: objname list

        Parameters
        ----------

        Returns
        -------

        """
        cond = [i.lower() for i in list(self.materials.GetConductors())]
        obj_names = []
        for el in self.modeler.primitives.objects:
            if self.modeler.primitives.objects[el].material_name in cond:
                obj_names.append(self.modeler.primitives.get_obj_name(el))
        return obj_names

    @aedt_exception_handler
    def get_all_dielectrics_names(self):
        """Get all dielectrics in active design
        
        
        :return: objname list

        Parameters
        ----------

        Returns
        -------

        """
        diel = [i.lower() for i in list(self.materials.GetDielectrics())]
        obj_names = []
        for el in self.modeler.primitives.objects:
            if self.modeler.primitives.objects[el].material_name in diel:
                obj_names.append(self.modeler.primitives.get_obj_name(el))
        return obj_names
