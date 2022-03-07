import os

from pyaedt.application.Analysis import Analysis
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Model2D import Modeler2D
from pyaedt.modules.Mesh import Mesh

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

    @pyaedt_function_handler()
    def plot(
        self,
        objects=None,
        show=True,
        export_path=None,
        plot_as_separate_objects=True,
        plot_air_objects=True,
        force_opacity_value=None,
        clean_files=False,
    ):
        """Plot the model or a subset of objects.

        Parameters
        ----------
        objects : list, optional
            List of objects to plot. The default is ``None``, in which case all objects
            are exported.
        show : bool, optional
            Whether to show the plot after generation. The default is ``True``. If ``False``,
            the generated class is returned for more customization before showing the plot.
        export_path : str, optional
            Path for the image file to save the plot to. The default is ``None``, in which case
            no image file is saved.
        plot_as_separate_objects : bool, optional
            Whether to plot each object separately. The default is ``True``, which may require
            more time to export from AEDT.
        plot_air_objects : bool, optional
            Whether to also plot air and vacuum objects. The default is ``True``.
        force_opacity_value : float, optional
            Opacity value between 0 and 1 to apply to all of the model. The default is ``None``,
            in which case the AEDT opacity value is applied to each object.
        clean_files : bool, optional
            Whether to clean created files after plot generation. The default is ``False``, in
            which case the cache is maintained into the model object that is returned.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        if is_ironpython:
            self.logger.warning("Plot is available only on CPython")
        elif self._aedt_version < "2021.2":
            self.logger.warning("Plot is supported from AEDT 2021 R2.")
        else:
            return self.post.plot_model_obj(
                objects=objects,
                show=show,
                export_path=export_path,
                plot_as_separate_objects=plot_as_separate_objects,
                plot_air_objects=plot_air_objects,
                force_opacity_value=force_opacity_value,
                clean_files=clean_files,
            )

    @pyaedt_function_handler()
    def export_mesh_stats(self, setup_name, variation_string="", mesh_path=None):
        """Export mesh statistics to a file.

        Parameters
        ----------
        setup_name :str
            Setup name.
        variation_string : str, optional
            Variation list.
        mesh_path : str, optional
            Full path to the mesh statistics file. The default is ``None``, in which
            case the working directory is used.

        Returns
        -------
        str
            File path.

        References
        ----------

        >>> oDesign.ExportMeshStats
        """
        if not mesh_path:
            mesh_path = os.path.join(self.working_directory, "meshstats.ms")
        self.odesign.ExportMeshStats(setup_name, variation_string, mesh_path)
        return mesh_path

    @pyaedt_function_handler()
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
        selections = self.modeler.convert_to_selections(obj, True)

        mat_exists = False
        if mat in self.materials.material_keys:
            mat_exists = True
        if mat_exists or self.materials.checkifmaterialexists(mat):
            Mat = self.materials.material_keys[mat]
            if mat_exists:
                Mat.update()
            self.logger.info("Assign Material " + mat + " to object " + str(selections))
            for el in selections:
                self.modeler[el].material_name = mat
                self.modeler[el].color = self.materials.material_keys[mat].material_appearance
                if Mat.is_dielectric():
                    self.modeler[el].solve_inside = True
                else:
                    self.modeler[el].solve_inside = False
            return True
        else:
            self.logger.error("Material does not exist.")
            return False
