import ntpath
import os
import warnings

from pyaedt.generic.general_methods import aedt_exception_handler, _retry_ntimes, is_ironpython
from pyaedt.modeler.Model3D import Modeler3D
from pyaedt.modules.Mesh import Mesh
from pyaedt.application.Analysis import Analysis

if is_ironpython:
    from pyaedt.modules.PostProcessor import PostProcessor
else:
    from pyaedt.modules.AdvancedPostProcessing import PostProcessor


class FieldAnalysis3D(Analysis, object):
    """Manages 3D field analysis setup in HFSS, Maxwell 3D, and Q3D.

    This class is automatically initialized by an application call from one of
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
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    specified_version : str, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    non_graphical : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    close_on_exit : bool, optional
        Whether to release  AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default
        is ``False``.

    """

    def __init__(
        self,
        application,
        projectname,
        designname,
        solution_type,
        setup_name=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=False,
        close_on_exit=False,
        student_version=False,
    ):
        Analysis.__init__(
            self,
            application,
            projectname,
            designname,
            solution_type,
            setup_name,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
        )
        self._osolution = self._odesign.GetModule("Solutions")
        self._oboundary = self._odesign.GetModule("BoundarySetup")
        self._modeler = Modeler3D(self)
        self._mesh = Mesh(self)
        self._post = PostProcessor(self)

    @property
    def osolution(self):
        """Solution Module.

        References
        ----------

        >>> oModule = oDesign.GetModule("Solutions")
        """
        return self._osolution

    @property
    def oboundary(self):
        """Boundary Module.

        References
        ----------

        >>> oModule = oDesign.GetModule("BoundarySetup")
        """
        return self._oboundary

    @property
    def modeler(self):
        """Modeler.

        Returns
        -------
        :class:`pyaedt.modeler.Model3D.Modeler3D`
        """
        return self._modeler

    @property
    def mesh(self):
        """Mesh.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.Mesh`
        """
        return self._mesh

    @property
    def components3d(self):
        """Components 3D.

        Returns
        -------
        dict
            Dictionary of components with their absolute paths.

        """
        components_dict = {}
        syspath = os.path.join(self.syslib, "3DComponents", self._design_type)
        if os.path.exists(syspath):
            listfiles = []
            for root, dirs, files in os.walk(syspath):
                for file in files:
                    if file.endswith(".a3dcomp"):
                        listfiles.append(os.path.join(root, file))
            # listfiles = glob.glob(syspath + "/**/*.a3dcomp", recursive=True)
            for el in listfiles:
                head, tail = ntpath.split(el)
                components_dict[tail[:-8]] = el
        userlib = os.path.join(self.userlib, "3DComponents", self._design_type)
        if os.path.exists(userlib):
            listfiles = []
            for root, dirs, files in os.walk(userlib):
                for file in files:
                    if file.endswith(".a3dcomp"):
                        listfiles.append(os.path.join(root, file))
            # listfiles = glob.glob(userlib + "/**/*.a3dcomp", recursive=True)
            for el in listfiles:
                head, tail = ntpath.split(el)
                components_dict[tail[:-8]] = el
        return components_dict

    @aedt_exception_handler
    def export_mesh_stats(self, setup_name, variation_string="", mesh_path=None):
        """Export mesh statistics to a file.

        Parameters
        ----------
        setup_name :str
            Setup name.
        variation_string : str, optional
            Variation List.
        mesh_path : str, optional
            Full path to mesh statistics file.

        Returns
        -------
        str
            File Path.

        References
        ----------

        >>> oDesign.ExportMeshStats
        """
        if not mesh_path:
            mesh_path = os.path.join(self.project_path, "meshstats.ms")
        self.odesign.ExportMeshStats(setup_name, variation_string, mesh_path)
        return mesh_path

    @aedt_exception_handler
    def get_components3d_vars(self, component3dname):
        """Read the A3DCOMP file and check for variables.

        Parameters
        ----------
        component3dname :
            Name of the 3D component, which must be in the ``syslib`` or ``userlib`` directory. Otherwise,
            you must specify the full absolute path to the AEDCOMP file with the file name and the extension.

        Returns
        -------
        dict
            Dictionary of variables in the A3DCOMP file.

        """
        vars = {}
        if component3dname not in self.components3d:
            if os.path.exists(component3dname):
                with open(component3dname, "rb") as aedt_fh:
                    temp = aedt_fh.read().splitlines()
                _all_lines = []
                for line in temp:
                    try:
                        _all_lines.append(line.decode("utf-8").lstrip("\t"))
                    except UnicodeDecodeError:
                        break
                for line in _all_lines:
                    if "VariableProp(" in line:
                        line_list = line.split("'")
                        vars[line_list[1]] = line_list[len(line_list) - 2]
                return vars
            return False
        with open(self.components3d[component3dname], "rb") as aedt_fh:
            temp = aedt_fh.read().splitlines()
        _all_lines = []
        for line in temp:
            try:
                _all_lines.append(line.decode("utf-8").lstrip("\t"))
            except UnicodeDecodeError:
                break
        for line in _all_lines:
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

        References
        ----------

        >>> oDesign.GetPropertyValue
        """

        boundary = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        excitation = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        setup = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "General", "Maxwell3D": "General"}
        mesh = {"HFSS": "MeshSetupTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        all = {
            "HFSS": ["HfssTab", "MeshSetupTab"],
            "Icepak": ["Icepak"],
            "Q3D": ["Q3D", "General"],
            "Maxwell3D": ["Maxwell3D", "General"],
        }
        if type == "Boundary":
            propserv = boundary[self._design_type]
            val = _retry_ntimes(10, self.odesign.GetPropertyValue, propserv, objectname, property)
            return val
        elif type == "Setup":
            propserv = setup[self._design_type]
            val = _retry_ntimes(10, self.odesign.GetPropertyValue, propserv, objectname, property)
            return val

        elif type == "Excitation":
            propserv = excitation[self._design_type]
            val = _retry_ntimes(10, self.odesign.GetPropertyValue, propserv, objectname, property)
            return val

        elif type == "Mesh":
            propserv = mesh[self._design_type]
            val = _retry_ntimes(10, self.odesign.GetPropertyValue, propserv, objectname, property)
            return val
        else:
            propservs = all[self._design_type]
            for propserv in propservs:
                properties = list(self.odesign.GetProperties(propserv, objectname))
                if property in properties:
                    val = _retry_ntimes(10, self.odesign.GetPropertyValue, propserv, objectname, property)
                    return val
        return None

    # TODO Refactor this
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

        References
        ----------

        >>> oEditor.Copy
        >>> oEditor.Paste
        """
        body_list = design.modeler.primitives.solid_names
        if include_sheets:
            body_list += design.modeler.primitives.sheet_names
        selection_list = []
        material_properties = design.modeler.primitives.objects
        if object_list:
            selection_list = [i for i in object_list if i in body_list]
        else:
            for body in body_list:
                include_object = True
                for key, val in material_properties.items():
                    if val.name == body:
                        if no_vacuum and val.material_name.lower() == "vacuum":
                            include_object = False
                        if no_pec and val.material_name == "pec":
                            include_object = False
                if include_object:
                    selection_list.append(body)
        design.modeler.oeditor.Copy(["NAME:Selections", "Selections:=", ",".join(selection_list)])
        self.modeler.oeditor.Paste()
        self.modeler.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def export3DModel(self, fileName, filePath, fileFormat=".step", object_list=[], removed_objects=[]):
        """Export the 3D model.

        .. deprecated:: 0.5.0
           Use :func:`pyaedt.application.Analysis3D.modeler.export_3d_model` instead.

        Parameters
        ----------
        fileName : str
            Name of the file.
        filePath : str
            Path for the file.
        fileFormat : str, optional
             Format of the file. The default is ``".step"``.
        object_list : list, optional
             List of objects to export. The default is ``[]``.
        removed_objects : list, optional
             The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Export
        """
        warnings.warn("`export3DModel` is deprecated. Use `export_3d_model` instead.", DeprecationWarning)
        return self.export_3d_model(fileName, filePath, fileFormat, object_list, removed_objects)

    @aedt_exception_handler
    def export_3d_model(self, fileName, filePath, fileFormat=".step", object_list=[], removed_objects=[]):
        """Export the 3D model.

        Parameters
        ----------
        fileName : str
            Name of the file.
        filePath : str
            Path for the file.
        fileFormat : str, optional
             Format of the file. The default is ``".step"``.
        object_list : list, optional
             List of objects to export. The default is ``[]``.
        removed_objects : list, optional
             The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Export
        """
        if not object_list:
            allObjects = self.modeler.primitives.object_names
            if removed_objects:
                for rem in removed_objects:
                    allObjects.remove(rem)
            else:
                if "Region" in allObjects:
                    allObjects.remove("Region")
        else:
            allObjects = object_list[:]

        self.logger.info("Exporting {} objects".format(len(allObjects)))
        major = -1
        minor = -1
        # actual version supported by AEDT is 29.0
        if fileFormat in [".step", ".stp", ".sm3", ".sat", ".sab"]:
            major = 29
            minor = 0
        stringa = ",".join(allObjects)
        arg = [
            "NAME:ExportParameters",
            "AllowRegionDependentPartSelectionForPMLCreation:=",
            True,
            "AllowRegionSelectionForPMLCreation:=",
            True,
            "Selections:=",
            stringa,
            "File Name:=",
            os.path.join(filePath, fileName + fileFormat),
            "Major Version:=",
            major,
            "Minor Version:=",
            minor,
        ]

        self.modeler.oeditor.Export(arg)
        return True

    @aedt_exception_handler
    def get_all_sources(self):
        """Retrieve all setup sources.

        Returns
        -------
        list of str
            List of setup sources.

        References
        ----------

        >>> oModule.GetAllSources
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

        References
        ----------

        >>> oModule.SetSourceContexts
        """

        contexts = []
        for i in range(number_of_modes):
            contexts.append([s + ":" + str(i + 1) for s in sources])  # use one based indexing
        self.osolution.SetSourceContexts(contexts)
        return True

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

        References
        ----------

        >>> oEditor.AssignMaterial

        Examples
        --------
        The method :func:`assign_material` is used to assign a material to a list of objects.

        Open a design and create the objects.

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> box1 = hfss.modeler.primitives.create_box([10, 10, 10], [4, 5, 5])
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 0], [2, 3, 4])
        >>> cylinder1 = hfss.modeler.primitives.create_cylinder(cs_axis="X", position=[5, 0, 0], radius=1, height=20)
        >>> cylinder2 = hfss.modeler.primitives.create_cylinder(cs_axis="Z", position=[0, 0, 5], radius=1, height=10)

        Assign the material ``"copper"`` to all the objects.

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
            self.logger.info("Assign Material " + mat + " to object " + selections)
            if isinstance(obj, list):
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
            self.logger.info("Assign Material " + mat + " to object " + selections)
            if isinstance(obj, list):
                for el in obj:
                    self.modeler.primitives[el].material_name = mat
            else:
                self.modeler.primitives[obj].material_name = mat

            return True
        else:
            self.logger.error("Material does not exist.")
            return False

    @aedt_exception_handler
    def get_all_conductors_names(self):
        """Retrieve all conductors in the active design.

        Returns
        -------
        list of str
            List of all conductors.

        References
        ----------

        >>> oEditor.GetObjectsByMaterial
        """
        cond = self.materials.conductors
        cond = [i.lower() for i in cond]
        obj_names = []
        for el in cond:
            obj_names += list(self._modeler.oeditor.GetObjectsByMaterial(el))
        return obj_names

    @aedt_exception_handler
    def get_all_dielectrics_names(self):
        """Retrieve all dielectrics in the active design.

        Returns
        -------
        list of str
           List of all dielectrics.

        References
        ----------

        >>> oEditor.GetObjectsByMaterial
        """
        diel = self.materials.dielectrics
        diel = [i.lower() for i in diel]
        obj_names = []
        for el in diel:
            obj_names += list(self._modeler.oeditor.GetObjectsByMaterial(el))
        return obj_names
