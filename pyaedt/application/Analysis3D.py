import os
import ntpath
import warnings

from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from ..modeler.Model3D import Modeler3D
from ..modules.Mesh import Mesh


class FieldAnalysis3D(Analysis, object):
    """FieldAnalysis3D class.

    This class is for 3D field analysis setup in HFSS, Maxwell 3D, and Q3D.

    It is automatically initialized by an application call from one of
    the 3D tools. See the application function for parameter definitions.

    Parameters
    ----------
    application : str
        3D application that is to initialize the call.
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
        self._mesh = Mesh(self)



    @property
    def modeler(self):
        """Modeler object.

        Returns
        -------
        :class:`modeler.Model3D.Modeler3D`
            Modeler Object
        """
        return self._modeler

    @property
    def mesh(self):
        """Mesh object.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.Mesh`
        """
        return self._mesh

    @property
    def components3d(self):
        """Components 3D object.

        Returns
        -------
        dict
            Dictionary of components with their absolute paths.

        """
        components_dict={}
        syspath = os.path.join(self.syslib, "3DComponents", self._design_type)
        if os.path.exists(syspath):
            listfiles = []
            for root, dirs, files in os.walk(syspath):
                for file in files:
                    if file.endswith(".a3dcomp"):
                        listfiles.append(os.path.join(root, file))
            #listfiles = glob.glob(syspath + "/**/*.a3dcomp", recursive=True)
            for el in listfiles:
                head, tail = ntpath.split(el)
                components_dict[tail[:-8]]= el
        userlib = os.path.join(self.userlib, "3DComponents", self._design_type)
        if os.path.exists(userlib):
            listfiles = []
            for root, dirs, files in os.walk(userlib):
                for file in files:
                    if file.endswith(".a3dcomp"):
                        listfiles.append(os.path.join(root, file))
            #listfiles = glob.glob(userlib + "/**/*.a3dcomp", recursive=True)
            for el in listfiles:
                head, tail = ntpath.split(el)
                components_dict[tail[:-8]]= el
        return components_dict

    @aedt_exception_handler
    def get_components3d_vars(self, component3dname):
        """Read the A3DCOMP file and check for variables. 

        Parameters
        ----------
        component3dname :
            Name of the 3D component, which must be in the ``syslib`` or ``userlib`` directory or the 
            full absolute path to the AEDCOMP file with the extension.

        Returns
        -------
        dict
            Dictionary of variables in the A3DCOMP file.

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
        """Retrieve a property value.

        Parameters
        ----------
        objectname : str
            Name of the object.
        property : str
            Name of the property,
        type : str, optional
            Type of the property. Options are ``"boundary"``, ``"excitation"``, 
            ``"setup",`` and ``"mesh"``. The default is ``None``.    

        Returns
        -------
        type
            Value of the property.

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

    #TODO Refactor this
    @aedt_exception_handler
    def copy_solid_bodies_from(self, design, object_list=None, no_vacuum=True, no_pec=True, include_sheets=False):
        """Copy a list of objects from one design to the active design.

        Parameters
        ----------
        design :
            Starting application object. For example, ``hfss1= HFSS3DLayout``.
        object_list : list, optional
            List of objects to copy. The default is ``None``.
        no_vacuum : bool, optional
            Whether to include vacuum objects for the copied objects. 
            The default is ``True``.
        no_pec :
            Whether to include pec objects for the copied objects. The 
            default is ``True``.
        include_sheets :
            Whether to include sheets for the copied objects. The 
            default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        body_list = design.modeler.primitives.solid_names
        if include_sheets:
            body_list += design.modeler.primitives.sheet_names
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
    def get_all_sources(self):
        """Retrieve all setup sources.

        Returns
        -------
        list
            List of setup sources.
        """
        return list(self.osolution.GetAllSources())

    @aedt_exception_handler
    def set_source_context(self, sources, number_of_modes=1):
        """Set the source context.

        Parameters
        ----------
        sources : list
            List of source names.
        number_of_modes : int, optional
            Number of modes. The  default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """

        contexts = []
        for i in range(number_of_modes):
            contexts.append([s + ':' + str(i + 1) for s in sources])  # use one based indexing
        self.osolution.SetSourceContexts(contexts)
        return True

    @aedt_exception_handler
    def assignmaterial(self, obj, mat):
        """Assign a material to one or more objects.

        .. deprecated:: 0.3.1
           Use :func:`FieldAnalysis3D.assign_material` instead.

        """
        warnings.warn('assignmaterial is deprecated.  Please use assign_material instead.',
                      DeprecationWarning)
        self.assign_material(obj, mat)

    @aedt_exception_handler
    def assign_material(self, obj, mat):
        """Assign a material to one or more objects.

        Parameters
        ----------
        obj : str, list
            One or more objects to assign materials to.
        mat : str
            Material to assign. If this material is not present, it will be
            created.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        The method assign_material is useful to assign a material to a list of objects.

        Open a design and create the objects.

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> box1 = hfss.modeler.primitives.create_box([10, 10, 10], [4, 5, 5])
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 0], [2, 3, 4])
        >>> cylinder1 = hfss.modeler.primitives.create_cylinder(cs_axis="X", position=[5, 0, 0], radius=1, height=20)
        >>> cylinder2 = hfss.modeler.primitives.create_cylinder(cs_axis="Z", position=[0, 0, 5], radius=1, height=10)

        Assign the material "copper" to all the objects.

        >>> objects_list = [box1, box2, cylinder1, cylinder2]
        >>> hfss.assign_material(objects_list, "copper")

        The method also accepts a list of object names.

        >>> obj_names_list = [box1.name, box2.name, cylinder1.name, cylinder2.name]
        >>> hfss.assign_material(obj_names_list, "aluminum")
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
        """Retrieve all conductors in the active design.
                
        Returns
        -------
        list
            List of all conductors.

        """
        cond = self.materials.conductors
        cond = [i.lower() for i in cond]
        obj_names = []
        for el, obj in self.modeler.primitives.objects.items():
            if obj.object_type == "Solid":
                if obj.material_name.lower() in cond:
                    obj_names.append(obj.name)
        return obj_names

    @aedt_exception_handler
    def get_all_dielectrics_names(self):
        """Retrieve all dielectrics in the active design.
              
        Returns
        -------
        List
           List of all dielectrics.

        """
        diel = self.materials.dielectrics
        diel = [i.lower() for i in diel]
        obj_names = []
        for name in self.modeler.primitives.solid_names:
            id = self.modeler.primitives.object_id_dict[name]
            obj = self.modeler.primitives.objects[id]
            if obj.material_name.lower() in diel:
                obj_names.append(obj.name)
        return obj_names
