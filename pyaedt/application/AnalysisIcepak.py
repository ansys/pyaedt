import csv
import re

from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from ..application.Analysis import Analysis
from ..modeler.Model3D import Modeler3D
from ..modules.MeshIcepak import IcepakMesh


class FieldAnalysisIcepak(Analysis, object):
    """FieldAnalysisIcepak class.
    
    This class is for 3D field analysis setup in Icepak.

    It is automatically initialized by an appliation call from 
    HFSS, Icepak, Q3D, or Maxwell 3D. See the application function 
    for parameter definitions.

    Parameters
    ----------
    application : str
        Application that is to initialize the call.
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
        case an attempt is made to get an active project. If no 
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in 
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solutiontype : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or 
        nothing is used.
    specified_version: str, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default 
        is ``False``, which launches AEDT in the graphical mode.  
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    release_on_exit : bool, optional
        Whether to release  AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default 
        is ``False``.

    """
    def __init__(self, application, projectname, designname, solutiontype, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        Analysis.__init__(self, application, projectname, designname, solutiontype, setup_name,
                          specified_version, NG, AlwaysNew, release_on_exit, student_version)
        self._modeler = Modeler3D(self)
        self._mesh = IcepakMesh(self)

    @property
    def modeler(self):
        """Modeler object."""
        return self._modeler

    @property
    def mesh(self):
        """Mesh object."""
        return self._mesh

    # @property
    # def post(self):
    #     return self._post

    @aedt_exception_handler
    def apply_icepak_settings(self, ambienttemp=20, gravityDir=5, perform_minimal_val=True, default_fluid="air",
                              default_solid="Al-Extruded", default_surface="Steel-oxidised-surface"):
        """Apply Icepak default design settings.

        Parameters
        ----------
        ambienttemp : int, optional
            Ambient temperature, which can be an integer or a parameter already 
            created in AEDT. The default is 20.
        gravityDir : int, optional
            Gravity direction index in the range ``[0, 5]``. The default is ``5``.
        perform_minimal_val : bool, optional
            Whether to perform minimal validation. The default is ``True``. 
            When ``False``, full validation is performend.
        default_fluid : str, optional
            Default for the type of fluid. The default is ``"Air"``.
        default_solid :
            Default for  the type of solid. The default is ``"Al-Extruded"``.
        default_surface :
            Default for the type of surface. The defaultis ``"Steel-oxidised-surface"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Retrieve a design property value for an object.

        Parameters
        ----------
        objectname : str
            Name of the object.
        property : str
            Name of the design property.
        type : string, optional 
            Type of the property. Options are ``"boundary"``, ``"excitation"``, ``"setup"``,
            and ``"mesh"``. The default is ``None``. 

        Returns
        -------
        type
            Value of the property.
            
        Example
        -------
            
        >>> val = ipk.get_property_value('BoundarySetup:Source1', 'Total Power')

        """
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
        """Copy a list of objects from one design to the active design.

        Parameters
        ----------
        design : str
            Starting application object. For example, ``'hfss1=HFSS3DLayout'``.
        object_list : list, optional
            List of objects to copy. The default is ``None``.
        no_vacuum : bool, optional
            Whether to include vacuum objects for the copied objects. 
            The default is ``True``.
        no_pec :
            Whether to include pec objects for the copied objects. The 
            default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        return True

    @aedt_exception_handler
    def assignmaterial(self, obj, mat):
        """Assign a material to one or more objects. 

        Parameters
        ----------
        obj : str, list
            One or more objects to assign materials to.
        mat : str
            Material to assign. If this material is not present it will be 
            created.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
            for el in obj:
                self.modeler.primitives[el].material_name = mat
            return True
        elif self.materials.checkifmaterialexists(mat):
            Mat = self.materials.material_keys[mat]
            if Mat.is_dielectric():
                arg2.append("SolveInside:="), arg2.append(True)
            else:
                arg2.append("SolveInside:="), arg2.append(False)
            self.modeler.oeditor.AssignMaterial(arg1, arg2)
            self._messenger.add_info_message('Assign Material ' + mat + ' to object ' + selections)
            for el in obj:
                self.modeler.primitives[el].material_name = mat
            return True
        else:
            self._messenger.add_error_message("Material Does Not Exists")
            return False

    @aedt_exception_handler
    def _assign_property_to_mat(self,newmat, val, property):
        """Assign a property to a new material.

        Parameters
        ----------
        newmat : str
            Name of the new material.
        val : 
            Property value to assign.
        property :
           Name of the property.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
    def _create_dataset_from_sherlock(self, material_name, material_string, property_name= "Mass_Density"):
        mats = material_string.split(",")
        mat_temp = [[i.split("@")[0], i.split("@")[1]] for i in mats]
        nominal_id = int(len(mat_temp) / 2)
        nominal_val = float(mat_temp[nominal_id-1][0])
        ds_name= generate_unique_name(property_name)
        self.create_dataset(ds_name,
                            [float(i[1].replace("C", "").replace("K", "").replace("F", "")) for i in mat_temp],
                            [float(i[0]) / nominal_val for i in mat_temp])
        return nominal_val, "$" + ds_name

    @aedt_exception_handler
    def assignmaterial_from_sherlock_files(self, csv_component, csv_material):
        """Assign material to objects in a design based on a CSV files obtained from Sherlock.

        Parameters
        ----------
        csv_component :  str
            Name of the CSV file containing the component properties, including the 
            material name.
        csv_material : str
            Name of the CSV file containing the material properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        all_objs = self.modeler.primitives.object_names
        i = 0
        for mat in material_data["Name"]:
            list_mat_obj = ["COMP_" + rd for rd, md in zip(component_data["Ref Des"], component_data["Material"]) if
                            md == mat]
            list_mat_obj += [rd for rd, md in zip(component_data["Ref Des"], component_data["Material"]) if
                            md == mat]
            list_mat_obj = [mo for mo in list_mat_obj if mo in all_objs]
            if list_mat_obj:
                if not self.materials.checkifmaterialexists(mat.lower()):
                    newmat = self.materials.add_material(mat.lower())
                else:
                    newmat = self.materials[mat.lower()]
                if "Material Density" in material_data:
                    if "@" in material_data["Material Density"][i] and "," in  material_data["Material Density"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(mat, material_data[
                            "Material Density"][i], "Mass_Density")
                        newmat.mass_density = nominal_val
                        newmat.mass_density.thermalmodifier = "pwl({}, Temp)".format(dataset_name)
                    else:
                        value = material_data["Material Density"][i]
                        newmat.mass_density = value
                if "Thermal Conductivity" in material_data:
                    if "@" in material_data["Thermal Conductivity"][i] and "," in  material_data["Thermal Conductivity"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(mat, material_data[
                            "Thermal Conductivity"][i], "Thermal_Conductivity")
                        newmat.thermal_conductivity = nominal_val
                        newmat.thermal_conductivity.thermalmodifier = "pwl({}, Temp)".format(dataset_name)
                    else:
                        value = material_data["Thermal Conductivity"][i]
                        newmat.thermal_conductivity = value
                if "Material CTE" in material_data:
                    if "@" in material_data["Material CTE"][i] and "," in  material_data["Material CTE"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(mat, material_data[
                            "Material CTE"][i], "CTE")
                        newmat.thermal_expansion_coefficient = nominal_val
                        newmat.thermal_expansion_coefficient.thermalmodifier = "pwl({}, Temp)".format(dataset_name)
                    else:
                        value = material_data["Material CTE"][i]
                        newmat.thermal_expansion_coefficient = value
                if "Poisson Ratio" in material_data:
                    if "@" in material_data["Poisson Ratio"][i] and "," in  material_data["Poisson Ratio"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(mat, material_data[
                            "Poisson Ratio"][i], "Poisson_Ratio")
                        newmat.poissons_ratio = nominal_val
                        newmat.poissons_ratio.thermalmodifier = "pwl({}, Temp)".format(dataset_name)
                    else:
                        value = material_data["Poisson Ratio"][i]
                        newmat.poissons_ratio = value
                if "Elastic Modulus" in material_data:
                    if "@" in material_data["Elastic Modulus"][i] and "," in  material_data["Elastic Modulus"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(mat, material_data[
                            "Elastic Modulus"][i], "Youngs_Modulus")
                        newmat.youngs_modulus = nominal_val
                        newmat.youngs_modulus.thermalmodifier = "pwl({}, Temp)".format(dataset_name)
                    else:
                        value = material_data["Elastic Modulus"][i]
                        newmat.youngs_modulus = value
                self.assignmaterial(list_mat_obj, mat)

                for obj_name in list_mat_obj:
                    if not self.modeler.primitives[obj_name].surface_material_name:
                        self.modeler.primitives[obj_name].surface_material_name = "Steel-oxidised-surface"
            i += 1
            all_objs = [ao for ao in all_objs if ao not in list_mat_obj]
        return True

    @aedt_exception_handler
    def get_all_conductors_names(self):
        """Retrieve all conductors in the active design.        
       
        Returns
        -------
        list
            List of conductors.

        """
        cond = [i.lower() for i in list(self.materials.conductors)]
        obj_names = []
        for el, obj in self.modeler.primitives.objects.items():
            if obj.material_name in cond:
                obj_names.append(obj.name)
        return obj_names

    @aedt_exception_handler
    def get_all_dielectrics_names(self):
        """Retrieve all dielectrics in the active design.
                
        Returns
        -------
        list
            List of dielectrics.

        """
        diel = [i.lower() for i in list(self.materials.dielectrics)]
        obj_names = []
        for el, obj in self.modeler.primitives.objects.items():
            if obj.material_name in diel:
                obj_names.append(obj.name)
        return obj_names
