import os

from pyaedt.application.Analysis import Analysis
from pyaedt.generic.configurations import Configurations3DLayout
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings
from pyaedt.modules.SetupTemplates import SetupKeys
from pyaedt.modules.SolveSetup import Setup3DLayout


class FieldAnalysis3DLayout(Analysis):
    """Manages 3D field analysis setup in HFSS 3D Layout.

    This class is automatically initialized by an application call from this
    3D tool. See the application function for parameter definitions.

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
    specified_version : str, int, float, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``False``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default
        is ``False``.
    aedt_process_id : int, optional
        Only used when ``new_desktop_session = False``, specifies by process ID which instance
        of Electronics Desktop to point PyAEDT at.

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
        machine="",
        port=0,
        aedt_process_id=None,
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
            machine,
            port,
            aedt_process_id,
        )
        self._modeler = None
        self._mesh = None
        self._post = None
        self._configurations = Configurations3DLayout(self)
        if not settings.lazy_load:
            self._modeler = self.modeler
            self._mesh = self.mesh
            self._post = self.post

    @property
    def configurations(self):
        """Property to import and export configuration files.

        Returns
        -------
        :class:`pyaedt.generic.configurations.Configurations`
        """
        return self._configurations

    @property
    def post(self):
        """PostProcessor.

        Returns
        -------
        :class:`pyaedt.modules.AdvancedPostProcessing.PostProcessor`
            PostProcessor object.
        """
        if self._post is None:
            self.logger.reset_timer()
            if is_ironpython:  # pragma: no cover
                from pyaedt.modules.PostProcessor import PostProcessor
            else:
                from pyaedt.modules.AdvancedPostProcessing import PostProcessor
            self._post = PostProcessor(self)
            self.logger.info_timer("Post class has been initialized!")

        return self._post

    @property
    def mesh(self):
        """Mesh.

        Returns
        -------
        :class:`pyaedt.modules.Mesh3DLayout.Mesh3d`
        """
        if self._mesh is None:
            from pyaedt.modules.Mesh3DLayout import Mesh3d

            self._mesh = Mesh3d(self)
        return self._mesh

    @property
    def excitations(self):
        """Excitation names.

        Returns
        -------
        list
            Excitation list. Excitations with multiple modes return one
            excitation for each mode.

        References
        ----------

        >>> oModule.GetExcitations
        """
        return list(self.oboundary.GetAllPortsList())

    @pyaedt_function_handler()
    def change_design_settings(self, settings):
        """Set HFSS 3D Layout Design Settings.

        Parameters
        ----------
        settings : dict
            Dictionary of settings with value to apply.

        Returns
        -------
        bool
        """
        arg = ["NAME:options"]
        for key, value in settings.items():
            arg.append(key + ":=")
            arg.append(value)
        self.odesign.DesignOptions(arg)
        return True

    @pyaedt_function_handler()
    def export_mesh_stats(self, setup_name, variation_string="", mesh_path=None):
        """Export mesh statistics to a file.

        Parameters
        ----------
        setup_name : str
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

        >>> oModule.ExportMeshStats
        """
        if not mesh_path:
            mesh_path = os.path.join(self.working_directory, "meshstats.ms")
        self.odesign.ExportMeshStats(setup_name, variation_string, mesh_path)
        return mesh_path

    @property
    def modeler(self):
        """Modeler object.

        Returns
        -------
        :class:`pyaedt.modeler.modelerpcb.Modeler3DLayout`
        """
        if self._modeler is None:
            self.logger.reset_timer()
            from pyaedt.modeler.modelerpcb import Modeler3DLayout

            self._modeler = Modeler3DLayout(self)
            self.logger.info_timer("Modeler class has been initialized!")

        return self._modeler

    @property
    def port_list(self):
        """Port list.

        References
        ----------

        >>> oModule.GetAllPorts"""
        return self.oexcitation.GetAllPortsList()

    @property
    def existing_analysis_setups(self):
        """Existing analysis setups in the design.

        Returns
        -------
        list
            List of names of all analysis setups in the design.

        References
        ----------

        >>> oModule.GetSetups
        """
        setups = self.oanalysis.GetSetups()
        if setups:
            return list(setups)
        return []

    @pyaedt_function_handler()
    def create_setup(self, setupname="MySetupAuto", setuptype=None, **kwargs):
        """Create a setup.

        Parameters
        ----------
        setupname : str, optional
            Name of the new setup. The default is ``"MySetupAuto"``.
        setuptype : str, optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.
        **kwargs : dict, optional
            Extra arguments for setup settings.
            Available keys depend on the setup chosen. For more
            information, see :doc:`../SetupTemplates3DLayout`.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.Setup3DLayout`

        References
        ----------

        >>> oModule.Add

        Examples
        --------

        >>> from pyaedt import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> app.create_setup(name="Setup1",MeshSizeFactor=2,SingleFrequencyDataList__AdaptiveFrequency="5GHZ")
        """
        if setuptype is None:
            setuptype = self.design_solutions.default_setup
        elif setuptype in SetupKeys.SetupNames:
            setuptype = SetupKeys.SetupNames.index(setuptype)
        name = self.generate_unique_setup_name(setupname)
        setup = Setup3DLayout(self, setuptype, name)
        tmp_setups = self.setups
        setup.create()
        setup.auto_update = False

        if "props" in kwargs:
            for el in kwargs["props"]:
                setup.props[el] = kwargs["props"][el]
        for arg_name, arg_value in kwargs.items():
            if arg_name == "props":
                continue
            if setup[arg_name] is not None:
                setup[arg_name] = arg_value
        setup.auto_update = True
        setup.update()
        self._setups = tmp_setups + [setup]
        return setup

    @pyaedt_function_handler()
    def get_setup(self, setupname, setuptype=None):
        """Retrieve a setup.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        setuptype : SETUPS, optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.Setup3DLayout`
            Setup object.

        """
        if setuptype is None:
            setuptype = self.design_solutions.default_setup
        for setup in self._setups:
            if setupname == setup.name:
                return setup
        setup = Setup3DLayout(self, setuptype, setupname, isnewsetup=False)
        self.active_setup = setupname
        return setup

    @pyaedt_function_handler()
    def delete_setup(self, setupname):
        """Delete a setup.

        Parameters
        ----------
        setupname : str
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Delete

        Examples
        --------
        Create a setup and then delete it.

        >>> import pyaedt
        >>> hfss3dlayout = pyaedt.Hfss3dLayout()
        >>> setup1 = hfss3dlayout.create_setup(name='Setup1')
        >>> hfss3dlayout.delete_setup(setupname='Setup1')
        ...
        PyAEDT INFO: Sweep was deleted correctly.
        """
        if setupname in self.existing_analysis_setups:
            self.osolution.Delete(setupname)
            for s in self.setups:
                if s.name == setupname:
                    self.setups.remove(s)
            return True
        return False
