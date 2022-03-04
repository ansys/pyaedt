import os
import warnings

from pyaedt.application.Analysis import Analysis
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Model3DLayout import Modeler3DLayout
from pyaedt.modules.Mesh3DLayout import Mesh3d
from pyaedt.modules.SolveSetup import Setup3DLayout

if is_ironpython:
    from pyaedt.modules.PostProcessor import PostProcessor
else:
    from pyaedt.modules.AdvancedPostProcessing import PostProcessor


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
    specified_version : str, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
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
        self._osolution = self._odesign.GetModule("SolveSetups")
        self._oexcitation = self._odesign.GetModule("Excitations")
        self._oboundary = self._odesign.GetModule("Excitations")
        self.logger.info("Analysis Loaded")
        self._modeler = Modeler3DLayout(self)
        self._modeler.init_padstacks()
        self.logger.info("Modeler Loaded")
        self._mesh = Mesh3d(self)
        self._post = PostProcessor(self)
        # self._post = PostProcessor(self)

    @property
    def osolution(self):
        """Solution Module.

        References
        ----------

        >>> oModule = oDesign.GetModule("SolveSetups")
        """
        return self._osolution

    @property
    def oexcitation(self):
        """Solution Module.

        References
        ----------

        >>> oModule = oDesign.GetModule("Excitations")
        """
        return self._oexcitation

    @property
    def oboundary(self):
        """Boundary Module.

        References
        ----------

        >>> oModule = oDesign.GetModule("Excitations")
        """
        return self._oboundary

    @property
    def mesh(self):
        """Mesh.

        Returns
        -------
        :class:`pyaedt.modules.Mesh3DLayout.Mesh3d`
        """
        return self._mesh

    @property
    def excitations(self):
        """Excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------

        >>> oModule.GetExcitations
        """
        return list(self.oboundary.GetAllPortsList())

    @property
    def get_excitations_name(self):
        """Excitation names.

        .. deprecated:: 0.4.27
           Use :func:`excitations` property instead.

        Returns
        -------
        list
            list of all excitation

        References
        ----------

        >>> oModule.GetAllPortsList
        """
        warnings.warn("`get_excitations_name` is deprecated. Use `excitations` property instead.", DeprecationWarning)
        return self.excitations

    @property
    def get_all_sparameter_list(self, excitation_names=[]):
        """List of all S parameters for a list of excitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``[]``, in which case
            the S parameters for all excitations are to be provided.
            For example, ``["1", "2"]``.

        Returns
        -------
        list
            List of strings representing the S parameters of the excitations.
            For example, ``["S(1, 1)", "S(1, 2)", S(2, 2)]``.

        """
        if not excitation_names:
            excitation_names = self.excitations
        spar = []
        k = 0
        for i in excitation_names:
            k = excitation_names.index(i)
            while k < len(excitation_names):
                spar.append("S({},{})".format(i, excitation_names[k]))
                k += 1
        return spar

    @pyaedt_function_handler()
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

        >>> oModule.ExportMeshStats
        """
        if not mesh_path:
            mesh_path = os.path.join(self.working_directory, "meshstats.ms")
        self.odesign.ExportMeshStats(setup_name, variation_string, mesh_path)
        return mesh_path

    @pyaedt_function_handler()
    def get_all_return_loss_list(self, excitation_names=[], excitation_name_prefix=""):
        """Retrieve a list of all return losses for a list of excitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``[]``, in which case
            the return losses for all excitations are to be provided.
            For example, ``["1", "2"]``.
        excitation_name_prefix : string, optional
             Prefix to add to the excitation names. The default is ``""``.

        Returns
        -------
        list
            List of strings representing the return losses of the excitations.
            For example, ``["S(1, 1)", "S(2, 2)"]``.

        References
        ----------

        >>> oModule.GetAllPorts
        """
        if not excitation_names:
            excitation_names = self.excitations
        if excitation_name_prefix:
            excitation_names = [i for i in excitation_names if excitation_name_prefix.lower() in i.lower()]
        spar = []
        for i in excitation_names:
            spar.append("S({},{})".format(i, i))
        return spar

    @pyaedt_function_handler()
    def get_all_insertion_loss_list(self, trlist=[], reclist=[], tx_prefix="", rx_prefix=""):
        """Retrieve a list of all insertion losses from two lists of excitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example, ``["1"]``.
        reclist : list, optional
            List of receivers. The default is ``[]``. The number of drivers equals
            the number of receivers. For example, ``["2"]``.
        tx_prefix : str, optional
            Prefix to add to driver names. For example, ``"DIE"``. The default is ``""``.
        rx_prefix : str, optional
            Prefix to add to receiver names. For example, ``"BGA"``. The default is ``""``.

        Returns
        -------
        list
            List of strings representing insertion losses of the excitations.
            For example, ``["S(1, 2)"]``.

        References
        ----------

        >>> oModule.GetAllPorts
        """
        spar = []
        if not trlist:
            trlist = [i for i in self.excitations if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.excitations if rx_prefix in i]
        if len(trlist) != len(reclist):
            self.logger.error("The TX and RX lists should be same length.")
            return False
        for i, j in zip(trlist, reclist):
            spar.append("S({},{})".format(i, j))
        return spar

    @pyaedt_function_handler()
    def get_next_xtalk_list(self, trlist=[], tx_prefix=""):
        """Retrieve a list of all the near end XTalks from a list of excitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example, ``["1", "2", "3"]``.
        tx_prefix : str, optional
            Prefix to add to driver names. For example, ``"DIE"``.  The default is ``""``.

        Returns
        -------
        list
            List of strings representing near end XTalks of the excitations.
            For example, ``["S(1, 2)", "S(1, 3)", "S(2, 3)"]``.

        References
        ----------

        >>> oModule.GetAllPorts
        """
        next = []
        if not trlist:
            trlist = [i for i in self.excitations if tx_prefix in i]
        for i in trlist:
            k = trlist.index(i) + 1
            while k < len(trlist):
                next.append("S({},{})".format(i, trlist[k]))
                k += 1
        return next

    @pyaedt_function_handler()
    def get_fext_xtalk_list(self, trlist=[], reclist=[], tx_prefix="", rx_prefix="", skip_same_index_couples=True):
        """Retrieve a list of all the far end XTalks from two lists of exctitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example, ``["1", "2"]``.
        reclist : list, optional
            List of receivers. The default is ``[]``. For example, ``["3", "4"]``.
        tx_prefix : str, optional
            Prefix to add to the driver names. For example, ``"DIE"``.  The default is ``""``.
        rx_prefix : str, optional
            Prefix to add to the receiver names. For examples, ``"BGA"``. The default is ``""``.
        skip_same_index_couples : bool, optional
            Whether to skip driver and receiver couples with the same index position.
            The default is ``True``, in which case the drivers and receivers
            with the same index position are considered insertion losses and
            excluded from the list.

        Returns
        -------
        list
            List of strings representing the far end XTalks of the excitations.
            For example, ``["S(1, 4)", "S(2, 3)"]``.

        References
        ----------

        >>> oModule.GetAllPorts
        """
        fext = []
        if not trlist:
            trlist = [i for i in self.excitations if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.excitations if rx_prefix in i]
        for i in trlist:
            for k in reclist:
                if not skip_same_index_couples or reclist.index(k) != trlist.index(i):
                    fext.append("S({},{})".format(i, k))
        return fext

    @property
    def modeler(self):
        """Modeler object."""
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
        setups = list(self.oanalysis.GetSetups())
        return setups

    @pyaedt_function_handler()
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props={}):
        """Create a setup.

        Parameters
        ----------
        setupname : str, optional
            Name of the new setup. The default is ``"MySetupAuto"``.
        setuptype : str, optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.
        props : dict, optional
            Dictionary of properties with values. The default is ``{}``.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.Setup3DLayout`

        References
        ----------

        >>> oModule.Add
        """
        if setuptype is None:
            setuptype = self.design_solutions.default_setup
        name = self.generate_unique_setup_name(setupname)
        setup = Setup3DLayout(self, setuptype, name)
        setup.create()
        if props:
            for el in props:
                setup.props[el] = props[el]
        setup.update()
        self.analysis_setup = name
        self.setups.append(setup)
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
        for setup in self.setups:
            if setupname == setup.name:
                return setup
        setup = Setup3DLayout(self, setuptype, setupname, isnewsetup=False)
        self.analysis_setup = setupname
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
        >>> setup1 = hfss3dlayout.create_setup(setupname='Setup1')
        >>> hfss3dlayout.delete_setup(setupname='Setup1')
        ...
        pyaedt info: Sweep was deleted correctly.
        """
        if setupname in self.existing_analysis_setups:
            self.osolution.Delete(setupname)
            for s in self.setups:
                if s.name == setupname:
                    self.setups.remove(s)
            return True
        return False
