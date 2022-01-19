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

    @aedt_exception_handler
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
        """Plot the model or a substet of objects.

        Parameters
        ----------
        objects : list, optional
            Optional list of objects to plot. If `None` all objects will be exported.
        show : bool, optional
            Show the plot after generation or simply return the
            generated Class for more customization before plot.
        export_path : str, optional
            If available, an image is saved to file. If `None` no image will be saved.
        plot_as_separate_objects : bool, optional
            Plot each object separately. It may require more time to export from AEDT.
        plot_air_objects : bool, optional
            Plot also air and vacuum objects.
        force_opacity_value : float, optional
            Opacity value between 0 and 1 to be applied to all model.
            If `None` aedt opacity will be applied to each object.
        clean_files : bool, optional
            Clean created files after plot. Cache is mainteined into the model object returned.

        Returns
        -------
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
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
            Full path to mesh statistics file. If `None` working_directory will be used.

        Returns
        -------
        str
            File Path.

        References
        ----------

        >>> oDesign.ExportMeshStats
        """
        if not mesh_path:
            mesh_path = os.path.join(self.working_directory, "meshstats.ms")
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
                self.modeler.primitives[el].material_name = mat
                self.modeler.primitives[el].color = self.materials.material_keys[mat].material_appearance
                if Mat.is_dielectric():
                    self.modeler.primitives[el].solve_inside = True
                else:
                    self.modeler.primitives[el].solve_inside = False
            return True
        else:
            self.logger.error("Material does not exist.")
            return False
