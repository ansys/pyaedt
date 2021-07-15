from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from ..modeler.Model3DLayout import Modeler3DLayout
from ..modules.SetupTemplates import SetupKeys
from ..modules.SolveSetup import Setup3DLayout
from ..modules.Mesh3DLayout import Mesh


class FieldAnalysis3DLayout(Analysis):
    """FieldAnalysis3DLayout class.
    
    This class is for 3D field analysis setup in HFSS 3D Layout.

    It is automatically initialized by an application call from this
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
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default 
        is ``False``.
        
    """
    def __init__(self, application, projectname, designname, solution_type, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):

        Analysis.__init__(self, application, projectname, designname, solution_type, setup_name,
                          specified_version, NG, AlwaysNew, release_on_exit, student_version)
        self._messenger.add_info_message("Analysis Loaded")
        self._modeler = Modeler3DLayout(self)
        self._modeler.primitives.init_padstacks()
        self._messenger.add_info_message("Modeler Loaded")
        self._mesh = Mesh(self)
        #self._post = PostProcessor(self)

    @property
    def oboundary(self):
        """Boundary object."""
        return self._odesign.GetModule("Excitations")

    @property
    def mesh(self):
        """Mesh object."""
        return self._mesh

    @property
    def get_excitations_name(self):
        """Excitation names.
        
        Returns
        -------
        type
            BoundarySetup module object.
        
        """
        return list(self.oboundary.GetAllPortsList())

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
            excitation_names = self.get_excitations_name
        spar = []
        k = 0
        for i in excitation_names:
            k = excitation_names.index(i)
            while k < len(excitation_names):
                spar.append("S({},{})".format(i, excitation_names[k]))
                k += 1
        return spar

    @aedt_exception_handler
    def get_all_return_loss_list(self, excitation_names=[], excitation_name_prefix=''):
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
        type
            List of strings representing the return losses of the excitations.
            For example, ``["S(1, 1)", "S(2, 2)"]``. 
       
        """
        if not excitation_names:
            excitation_names = self.get_excitations_name
        if excitation_name_prefix:
            excitation_names = [i for i in excitation_names if excitation_name_prefix.lower() in i.lower()]
        spar = []
        for i in excitation_names:
            spar.append("S({},{})".format(i, i))
        return spar

    @aedt_exception_handler
    def get_all_insertion_loss_list(self, trlist=[], reclist=[], tx_prefix='', rx_prefix=''):
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

        """
        spar = []
        if not trlist:
            trlist = [i for i in self.get_excitations_name if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.get_excitations_name if rx_prefix in i]
        if len(trlist)!= len(reclist):
            self._messenger.add_error_message("TX and RX should be same length lists")
            return False
        for i, j in zip(trlist, reclist):
            spar.append("S({},{})".format(i, j))
        return spar

    @aedt_exception_handler
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

        """
        next = []
        if not trlist:
            trlist = [i for i in self.get_excitations_name if tx_prefix in i]
        for i in trlist:
            k = trlist.index(i)+1
            while k < len(trlist):
                next.append("S({},{})".format(i, trlist[k]))
                k += 1
        return next

    @aedt_exception_handler
    def get_fext_xtalk_list(self, trlist=[], reclist=[], tx_prefix='', rx_prefix='', skip_same_index_couples=True):
        """Retrieve a list of all the far end XTalks from two lists of exctitations (driver and receiver).      
       
        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example, ``["1", "2"]``.
        reclist : list, optional
            List of receiver. The default is ``[]``. For example, ``["3", "4"]``.
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
        list
            List of strings representing the far end XTalks of the excitations.
            For example, ``["S(1, 4)", "S(2, 3)"]``. 
        
        """
        fext = []
        if not trlist:
            trlist = [i for i in self.get_excitations_name if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.get_excitations_name if rx_prefix in i]
        for i in trlist:
            for k in reclist:
                if not skip_same_index_couples or reclist.index(k)!= trlist.index(i):
                    fext.append("S({},{})".format(i, k))
        return fext

    @property
    def modeler(self):
        """Modeler object."""
        return self._modeler

    # @property
    # def mesh(self):
    #     return self._mesh
    #
    # @property
    # def post(self):
    #     return self._post

    @property
    def osolution(self):
        """Solution object."""
        return self.odesign.GetModule("SolveSetups")

    @property
    def oexcitation(self):
        """Excitation object."""
        return self.odesign.GetModule("Excitations")

    @property
    def port_list(self):
        """Port list."""
        return self.oexcitation.GetAllPortsList()

    @property
    def oanalysis(self):
        """Analysis object."""
        return self.odesign.GetModule("SolveSetups")

    @property
    def existing_analysis_setups(self):
        """Retrieve a list of all analysis setup names in the Maxwell design."""
        oModule = self.odesign.GetModule("SolveSetups")
        setups = list(oModule.GetSetups())
        return setups

    @aedt_exception_handler
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
        Setup3DLayout
            Setup object.

        """
        if setuptype is None:
            setuptype = SetupKeys.defaultSetups[self.solution_type]
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

    @aedt_exception_handler
    def get_setup(self, setupname, setuptype=None):
        """Get an existing setup.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        setuptype : SetupTypes, optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.

        Returns
        -------
        :class: Setup3DLayout
            Setup object.

        """
        if setuptype is None:
            setuptype = SetupKeys.defaultSetups[self.solution_type]
        for setup in self.setups:
            if setupname == setup.name:
                return setup
        setup = Setup3DLayout(self, setuptype, setupname, isnewsetup=False)
        self.analysis_setup = setupname
        return setup
