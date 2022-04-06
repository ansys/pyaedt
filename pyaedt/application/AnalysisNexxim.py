import warnings

from pyaedt.application.Analysis import Analysis
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Circuit import ModelerNexxim
from pyaedt.modules.PostProcessor import CircuitPostProcessor
from pyaedt.modules.SolveSetup import SetupCircuit


class FieldAnalysisCircuit(Analysis):
    """FieldCircuitAnalysis class.

    This class is for circuit analysis setup in Nexxim.

    It is automatically initialized by a call from an application,
    such as HFSS or Q3D. See the application function for its
    parameter definitions.

    Parameters
    ----------

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

        self._modeler = ModelerNexxim(self)
        self._modeler.layout.init_padstacks()
        self._post = CircuitPostProcessor(self)

    @property
    def post(self):
        """PostProcessor.

        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.CircuitPostProcessor`
            PostProcessor object.
        """
        return self._post

    @property
    def existing_analysis_sweeps(self):
        """Analysis setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        return self.existing_analysis_setups

    @property
    def existing_analysis_setups(self):
        """Analysis setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        setups = self.oanalysis.GetAllSolutionSetups()
        return setups

    @property
    def nominal_sweep(self):
        """Nominal sweep."""
        if self.existing_analysis_setups:
            return self.existing_analysis_setups[0]
        else:
            return ""

    @property
    def modeler(self):
        """Modeler object."""
        return self._modeler

    @property
    def setup_names(self):
        """Setup names.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        return self.oanalysis.GetAllSolutionSetups()

    @property
    def excitations(self):
        """Get all excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------

        >>> oModule.GetAllPorts
        """
        ports = [p.replace("IPort@", "").split(";")[0] for p in self.modeler.oeditor.GetAllPorts() if "IPort@" in p]
        return ports

    @property
    def get_excitations_name(self):
        """Excitation names.

        .. deprecated:: 0.4.27
           Use :func:`excitations` property instead.

        Returns
        -------
        type
            BoundarySetup Module object

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        warnings.warn("`get_excitations_name` is deprecated. Use `excitations` property instead.", DeprecationWarning)
        return self.excitations

    @property
    def get_all_sparameter_list(self, excitation_names=[]):
        """List of all S parameters for a list of exctitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``[]``, in which case
            the S parameters for all excitations are to be provided.
            For example, ``["1", "2"]``.

        Returns
        -------
        list of str
            List of strings representing the S parameters of the excitations.
            For example, ``"S(1,1)", "S(1,2)", "S(2,2)"``.

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
    def get_all_return_loss_list(self, excitation_names=None, excitation_name_prefix=""):
        """Retrieve a list of all return losses for a list of exctitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``None``, in which case
            the return losses for all excitations are to be provided.
            For example ``["1", "2"]``.
        excitation_name_prefix : string, optional
             Prefix to add to the excitation names. The default is ``""``,

        Returns
        -------
        list of str
            List of strings representing the return losses of the excitations.
            For example ``["S(1, 1)", S(2, 2)]``

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        if excitation_names == None:
            excitation_names = []

        if not excitation_names:
            excitation_names = self.excitations
        if excitation_name_prefix:
            excitation_names = [i for i in excitation_names if excitation_name_prefix.lower() in i.lower()]
        spar = []
        for i in excitation_names:
            spar.append("S({},{})".format(i, i))
        return spar

    @pyaedt_function_handler()
    def get_all_insertion_loss_list(self, trlist=None, reclist=None, tx_prefix="", rx_prefix=""):
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
        list of str
            List of strings representing insertion losses of the excitations.
            For example, ``["S(1,2)"]``.

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        if trlist == None:
            trlist = []
        if reclist == None:
            reclist = []

        spar = []
        if not trlist:
            trlist = [i for i in self.excitations if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.excitations if rx_prefix in i]
        if len(trlist) != len(reclist):
            self.logger.error("The TX and RX lists should be the same length.")
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
            List of drivers. The default is ``[]``. For example,
            ``["1", "2", "3"]``.
        tx_prefix : str, optional
            Prefix to add to driver names. For example, ``"DIE"``.  The default is ``""``.

        Returns
        -------
        list of str
            List of strings representing near end XTalks of the excitations.
            For example, ``["S(1, 2)", "S(1, 3)", "S(2, 3)"]``.

        References
        ----------

        >>> oEditor.GetAllPorts
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
    def get_fext_xtalk_list(self, trlist=None, reclist=None, tx_prefix="", rx_prefix="", skip_same_index_couples=True):
        """Retrieve a list of all the far end XTalks from two lists of exctitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example,
            ``["1", "2"]``.
        reclist : list, optional
            List of receiver. The default is ``[]``. For example,
            ``["3", "4"]``.
        tx_prefix : str, optional
            Prefix for driver names. For example, ``"DIE"``.  The default is ``""``.
        rx_prefix : str, optional
            Prefix for receiver names. For examples, ``"BGA"`` The default is ``""``.
        skip_same_index_couples : bool, optional
            Whether to skip driver and receiver couples with the same index position.
            The default is ``True``, in which case the drivers and receivers
            with the same index position are considered insertion losses and
            excluded from the list.

        Returns
        -------
        list of str
            List of strings representing the far end XTalks of the excitations.
            For example, ``["S(1, 4)", "S(2, 3)"]``.

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        if trlist == None:
            trlist = []
        if reclist == None:
            reclist = []

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

    @pyaedt_function_handler()
    def get_setup(self, setupname):
        """Retrieve the setup from the current design.

        Parameters
        ----------
        setupname : str
            Name of the setup.

        Returns
        -------
        type
            Setup object.

        """
        setup = SetupCircuit(self, self.solution_type, setupname, isnewsetup=False)
        if setup.props:
            self.analysis_setup = setupname
        return setup

    @pyaedt_function_handler()
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props={}):
        """Create a new setup.

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
        SetupCircuit
            Setup object.

        References
        ----------

        >>> oModule.AddLinearNetworkAnalysis
        >>> oModule.AddDCAnalysis
        >>> oModule.AddTransient
        >>> oModule.AddQuickEyeAnalysis
        >>> oModule.AddVerifEyeAnalysis
        >>> oModule.AddAMIAnalysis
        """
        if setuptype is None:
            setuptype = self.solution_type

        name = self.generate_unique_setup_name(setupname)
        setup = SetupCircuit(self, setuptype, name)
        setup.create()
        if props:
            for el in props:
                setup.props._setitem_without_update(el, props[el])
        setup.update()
        self.analysis_setup = name
        self.setups.append(setup)
        return setup

    # @property
    # def mesh(self):
    #     return self._mesh
    #
    # @property
    # def post(self):
    #     return self._post
