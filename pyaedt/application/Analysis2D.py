import os

from pyaedt.application.Analysis import Analysis
from pyaedt.modeler.Model2D import Modeler2D
from pyaedt.modules.Mesh import Mesh
from pyaedt.generic.general_methods import aedt_exception_handler, is_ironpython

if is_ironpython:
    from pyaedt.modules.PostProcessor import PostProcessor
else:
    from pyaedt.modules.AdvancedPostProcessing import PostProcessor


class FieldAnalysis2D(Analysis):
    """Manages 2D field analysis setup in Maxwell2D and Q2D.

    This class is automatically initialized by an application call from one of
    the 2D tools. See the application function for parameter definitions.

    Parameters
    ----------
    application : str
        2D application that is to initialize the call.
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
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, which launches AEDT in the graphical mode.
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

        self._modeler = Modeler2D(self)
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
        :class:`pyaedt.modeler.Model2D.Modeler2D`
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

    # @property
    # def post(self):
    #     return self._post

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
    def assign_material(self, obj, mat):
        """Assign a material to one or more objects.

        Parameters
        ----------
        obj : str or list
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
