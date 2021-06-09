import glob
import os
import ntpath
from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from ..modeler.Model3D import Modeler3D
from ..modules.Mesh import Mesh


class FieldAnalysis3D(Analysis, object):
    """AEDT_3D_FieldAnalysis

    Class for 3D Field Analysis Setup (HFSS, Maxwell3D, Q3D)

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
        self._mesh = Mesh(self)
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

    @property
    def components3d(self):
        """

        Parameters
        ----------

        Returns
        -------
        type
            :return: Ditcionary of components with their absolute path

        """
        components_dict={}
        syspath = os.path.join(self.syslib, "3DComponents", self._design_type)
        if os.path.exists(syspath):
            listfiles = glob.glob(syspath + "/**/*.a3dcomp", recursive=True)
            for el in listfiles:
                head, tail = ntpath.split(el)
                components_dict[tail[:-8]]= el
        userlib = os.path.join(self.userlib, "3DComponents", self._design_type)
        if os.path.exists(userlib):
            listfiles = glob.glob(userlib + "/**/*.a3dcomp", recursive=True)
            for el in listfiles:
                head, tail = ntpath.split(el)
                components_dict[tail[:-8]]= el
        return components_dict

    @aedt_exception_handler
    def get_components3d_vars(self, component3dname):
        """Read the a3dComp file and check for variables. It polulates a dictionary with default value

        Parameters
        ----------
        component3dname :
            name of 3dcomponent (it has to be in syslib or userlib) or full absolute path to a3dcomp file (with extension)

        Returns
        -------
        type
            vars dictionary

        """
        vars = {}
        if component3dname not in self.components3d:
            if os.path.exists(component3dname):
                with open(component3dname, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines:
                        if "VariableProp(" in line:
                            line_list = line.split("'")
                            vars[line_list[1]] = line_list[len(line_list) - 2]
                return vars
            return False
        with open(self.components3d[component3dname], 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "VariableProp(" in line:
                    line_list = line.split("'")
                    vars[line_list[1]] = line_list[len(line_list) - 2]
        return vars

    @aedt_exception_handler
    def get_property_value(self, objectname, property, type=None):
        """

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

        """

        boundary = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        excitation = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        setup = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "General", "Maxwell3D": "General"}
        mesh = {"HFSS": "MeshSetupTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        all = {"HFSS": ["HfssTab", "MeshSetupTab"], "Icepak": ["Icepak"], "Q3D": ["Q3D", "General"],
               "Maxwell3D": ["Maxwell3D", "General"]}
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
    def copy_solid_bodies_from(self, design, object_list=None, no_vacuum=True, no_pec=True, include_sheets=False):
        """Copy all the list of object from one design to active one

        Parameters
        ----------
        design :
            starting application object (examples hfss1= HFSS3DLayout)
        object_list :
            List of object to copy (Default value = None)
        no_vacuum : bool
            define if vacuum objects have to be copied (Default value = True)
        no_pec :
            define if pec objects have to be copied (Default value = True)
        include_sheets :
            include sheets in the objects that have to be copied (Default value = False)

        Returns
        -------
        type
            True if succeeded

        """
        body_list = design.modeler.solid_bodies
        if include_sheets:
            body_list += design.modeler.primitives.get_all_sheets_names()
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
    def get_all_sources(self):
        """:return:List of all Setup Sources"""
        return list(self.osolution.GetAllSources())

    @aedt_exception_handler
    def set_source_context(self, listofsources, nummodes=1):
        """

        Parameters
        ----------
        listofsources :
            
        nummodes :
             (Default value = 1)

        Returns
        -------

        """
        listforcontext = []
        i = 1
        while i <= nummodes:
            listforcontext.append([s+':'+str(i) for s in listofsources])
            i += 1
        return self.osolution.SetSourceContexts(listforcontext)

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
            if type(obj) is list:
                for el in obj:
                    self.modeler.primitives[el].material_name = mat
            else:
                self.modeler.primitives[obj].material_name = mat
            return True
        elif self.materials.checkifmaterialexists(mat):
            self.materials._aedmattolibrary(mat)
            Mat = self.materials.material_keys[mat]
            if Mat.is_dielectric():
                arg2.append("SolveInside:="), arg2.append(True)
            else:
                arg2.append("SolveInside:="), arg2.append(False)
            self.modeler.oeditor.AssignMaterial(arg1, arg2)
            self._messenger.add_info_message('Assign Material ' + mat + ' to object ' + selections)
            if type(obj) is list:
                for el in obj:
                    self.modeler.primitives[el].material_name = mat
            else:
                self.modeler.primitives[obj].material_name = mat

            return True
        else:
            self._messenger.add_error_message("Material Does Not Exists")
            return False

    @aedt_exception_handler
    def get_all_conductors_names(self):
        """Get all conductors in active design
        
        
        :return: objname list

        Parameters
        ----------

        Returns
        -------

        """
        cond = self.materials.GetConductors()
        cond = [i.lower() for i in cond]
        obj_names = []
        for el in self.modeler.primitives.objects:
            if self.modeler.primitives.objects[el].material_name.lower() in cond:
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
        diel = self.materials.GetDielectrics()
        diel = [i.lower() for i in diel]
        obj_names = []
        for el in self.modeler.primitives.objects:
            if self.modeler.primitives.objects[el].material_name.lower() in diel:
                obj_names.append(self.modeler.primitives.get_obj_name(el))
        return obj_names
