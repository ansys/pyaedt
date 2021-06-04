from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from ..modeler.Model3DLayout import Modeler3DLayout
from ..modules.SetupTemplates import SetupKeys
from ..modules.SolveSetup import Setup3DLayout
from ..modules.Mesh3DLayout import Mesh


class FieldAnalysis3DLayout(Analysis):
    """**AEDT_3DLayout_FieldAnalysis**
    Class for HFSS 3DLayoyt Field Analysis Setup

    It is automatically initialized by Application call (like HFSS,
    Q3D...). Refer to Application function for inputs definition.

    Parameters
    ----------

    Returns
    -------

    """
    def __init__(self, application, projectname, designname, solution_type, setup_name=None):

        Analysis.__init__(self, application, projectname, designname, solution_type, setup_name)
        self.messenger.add_info_message("Analysis Loaded")
        self._modeler = Modeler3DLayout(self)
        self._modeler.primitives.init_padstacks()
        self.messenger.add_info_message("Modeler Loaded")
        self._mesh = Mesh(self)
        #self._post = PostProcessor(self)

    @property
    def oboundary(self):
        """:return: BoundarySetup Module object"""
        return self._odesign.GetModule("Excitations")

    @property
    def mesh(self):
        """ """
        return self._mesh

    @property
    def get_excitations_name(self):
        """:return: BoundarySetup Module object"""
        return list(self.oboundary.GetAllPortsList())

    @property
    def get_all_sparameter_list(self, excitation_names=[]):
        """Get the list of all the SParameter from a list of exctitations. If no excitation is provided it will provide a full list of sparameters
        Example: excitation_names ["1","2"] output ["S(1,1)", "S(1,2)", S(2,2)]

        Parameters
        ----------
        excitation_names :
            list of excitation to include (Default value = [])

        Returns
        -------
        type
            list of strin representing Sparameters of excitations

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
        """Get the list of all the Returnloss from a list of exctitations. If no excitation is provided it will provide a full list of return Losses
        Example: excitation_names ["1","2"] output ["S(1,1)",, S(2,2)]

        Parameters
        ----------
        excitation_names :
            list of excitation to include (Default value = [])
        excitation_name_prefix :
             (Default value = '')

        Returns
        -------
        type
            list of string representing Return Losses of excitations

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
        """Get the list of all the Insertion Losses from two list of exctitations (driver and receiver). Optionally prefix can
        be used to retrieve driver and receiver names.
        Example: excitation_names ["1"] ["2"] output ["S(1,2)"]

        Parameters
        ----------
        trlist :
            list of Drivers to include (Default value = [])
        reclist :
            list of Receiver to include. Number of Driver = Number of Receiver an (Default value = [])
        tx_prefix :
            prefix for TX (eg. "DIE") (Default value = '')
        rx_prefix :
            prefix for RX (eg. "BGA") (Default value = '')

        Returns
        -------
        type
            list of string representing Insertion Losses of excitations

        """
        spar = []
        if not trlist:
            trlist = [i for i in self.get_excitations_name if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.get_excitations_name if rx_prefix in i]
        if len(trlist)!= len(reclist):
            self.messenger.add_error_message("TX and RX should be same length lists")
            return False
        for i, j in zip(trlist, reclist):
            spar.append("S({},{})".format(i, j))
        return spar

    @aedt_exception_handler
    def get_next_xtalk_list(self, trlist=[], tx_prefix=""):
        """Get the list of all the Near End XTalk a list of excitation. Optionally prefix can
        be used to retrieve driver names.
        Example: excitation_names ["1", "2", "3"] output ["S(1,2)", "S(1,3)", "S(2,3)"]

        Parameters
        ----------
        trlist :
            list of Drivers to include (Default value = [])
        tx_prefix :
            prefix for TX (eg. "DIE") (Default value = "")

        Returns
        -------
        type
            list of string representing Near End XTalks

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
        """Get the list of all the Far End XTalk from 2 lists of exctitations. Optionally prefix can
        be used to retrieve driver and receivers names. If skip_same_index_couples is true, the tx and rx with same index
        position will be considered insertion losses and excluded from the list
        Example: excitation_names ["1", "2"] ["3","4"] output ["S(1,4)", "S(2,3)"]

        Parameters
        ----------
        trlist :
            list of Drivers to include (Default value = [])
        tx_prefix :
            prefix for TX (eg. "DIE") (Default value = '')
        reclist :
            list of Receiver to include (Default value = [])
        rx_prefix :
            prefix for RX (eg. "BGA") (Default value = '')
        skip_same_index_couples :
            Boolean ignore TX and RX couple with same index (Default value = True)

        Returns
        -------
        type
            list of string representing Far End XTalks

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
        """ """
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
        """ """
        return self.odesign.GetModule("SolveSetups")

    @property
    def oexcitation(self):
        """ """
        return self.odesign.GetModule("Excitations")

    @property
    def port_list(self):
        """ """
        return self.oexcitation.GetAllPortsList()

    @property
    def oanalysis(self):
        """ """
        return self.odesign.GetModule("SolveSetups")

    @property
    def existing_analysis_setups(self):
        """Return a list of all defined analysis setup names in the maxwell design."""
        oModule = self.odesign.GetModule("SolveSetups")
        setups = list(oModule.GetSetups())
        return setups

    @aedt_exception_handler
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props={}):
        """Create a new Setup.

        Parameters
        ----------
        setupname : str
            optional, name of the new setup (Default value = "MySetupAuto")
        setuptype : SetupTypes
            optional, setup type. if None, default type will be applied
        props :
            optional dictionary of properties with values (Default value = {})

        Returns
        -------
        type
            setup object

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
        """Get an existing Setup.

        Parameters
        ----------
        setupname : str
            name of the setup
        setuptype : SetupTypes
            optional, setup type. if None, default type will be applied

        Returns
        -------
        :class: Setup3DLayout
            setup object

        """
        if setuptype is None:
            setuptype = SetupKeys.defaultSetups[self.solution_type]
        for setup in self.setups:
            if setupname == setup.name:
                return setup
        setup = Setup3DLayout(self, setuptype, setupname, isnewsetup=False)
        self.analysis_setup = setupname
        return setup
