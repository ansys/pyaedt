from __future__ import absolute_import
from numpy import result_type
from pyaedt.application.AnalysisEmit import FieldAnalysisEmit
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt import generate_unique_project_name
from pyaedt import settings
from pyaedt.generic.general_methods import pyaedt_function_handler
import sys
import os
supported_versions = [2023.1, 2023.2]
sys.path.append("C:\\Users\\cchandel\\workspace\\build_output\\64Release\\Delcross")
import EmitApiPython
class Revision:
    '''
    Provides the Revision object.

    Parameters
    ----------
    Emit_obj :
        This is the Emit Object to which this revision is associated with.
    name : str, optional
        Name of the Revision which is about to be created. The default is ``None``,
        in which case - a default name is given.
    Examples
    --------
    Create an instance of Emit, you can choose to define any of the parameters of Emit here.
    >>> aedtapp = Emit()
    >>> rev = Revision(aedtapp, "Revision 1")
    >>> eng = aedtapp.get_engine()
    >>> domain = EmitApiPython.InteractionDomain()
    >>> rev.run(domain, eng)
    '''
    @pyaedt_function_handler()
    def __init__(self, Emit_obj, name = ""):
        subfolder =''
        for f in os.scandir(Emit_obj.location):
            if os.path.splitext(f.name)[1].lower() in '.aedtresults':
                subfolder = os.path.join(f.path, "EmitDesign1")
        default_behaviour = not os.path.exists(os.path.join(subfolder, "{}.emit".format(name)))
        if default_behaviour:
            print("The most recent revision that was generated will be used because the revision you specified does not exist.")
        if(name == "" or default_behaviour):
            file = max([f for f in os.scandir(subfolder)], key=lambda x: x.stat().st_mtime)
            full = file.path
            name = file.name
        else:
            full = subfolder + '/{}.emit'.format(name)
        self.name = name
        self.path = full
        self.emit_obj = Emit_obj
    @pyaedt_function_handler()
    def run(self, domain, eng):
        """
        Load the revision, and proceed to analyze along the given domain

        Parameters
        ----------
            domain:
                An InteractionDomain must be defined to constrain the analysis parameters.
            eng: 
                An EmitEngine object from the associated Emit object must be given (temporary solution).
        Returns
        -------
        :class:`Interaction`
            Interaction object.

        References
        ----------
        >>> eng = aedtapp.get_engine()
        >>> domain = EmitApiPython.InteractionDomain()
        >>> rev.run(domain, eng)

        """
        self.emit_obj.load_revision(self.path)
        print("checkpoint - results loaded")
        t = eng.analyze(domain)
        print("checkpoint - interaction generated")
        return t
class Emit(FieldAnalysisEmit, object):
    """Provides the Emit application interface.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which case
        an attempt is made to get an active project. If no projects are
        present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in which case
        an attempt is made to get an active design. If no designs are
        present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is ``None``, in which
        case the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active setup is used or the latest installed version is
        used.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    machine : str, optional
        Machine name to which the oDesktop session is to connect to. This
        parameter works only in 2022 R2 and later. The remote server must be
        up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
        If the machine is `"localhost"`, the server starts if it is not present.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

    Examples
    --------
    Create an instance of Emit, you can choose to define any of the parameters of Emit here.
    >>> from pyaedt import Emit
    >>> aedtapp = Emit()

    Typically, it is desireable to specify a projectname, a designname and other parameters as well
    >>> aedtapp = Emit(projectname, designame)

    Once an instance of Emit is initialized, the schematic can be edited as shown below
    >>> rad1 = aedtapp.modeler.components.create_component("Bluetooth")
    >>> ant1 = aedtapp.modeler.components.create_component("Antenna")
    >>> if rad1 and ant1:
    >>>     ant1.move_and_connect_to(rad1)

    Once the schematic is generated, the Emit object can be analyzed to generate a Revision
    Each Revision is added as an element of the Emit Object member revisions_list
    >>> aedtapp.analyze()

    A Revision within PYAEDT is analogous to a Revision in AEDT. An Interaction Domain must defined
    and then used as the input to the run command used on that Revision.
    >>> domain = Emit.interaction_domain()
    >>> domain.rx_radio_name = "UE - HandHeld"
    >>> interaction = aedtapp.revisions_list[0].run(domain)

    The output of the run command is an interaction type object. An interaction summarizes the interaction data
    of whatever was defined in the interaction domain.
    >>> instance = interaction.worst_instance(Emit.result_type('sensitivity'))
    >>> val = instance.value(Emit.result_type('sensitivity'))
    >>> print("Worst-case Sensitivity for Rx '{}' is {}dB".format(domain.rx_radio_name, val))
    """
    def __init__(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=True,
        close_on_exit=True,
        student_version=False,
        machine="",
        port=0,
        aedt_process_id=None,
    ):
        if(projectname == None):
            projectname = generate_unique_project_name()
        self._emit_api = EmitApiPython.EmitApi()
        self._result_loaded = False
        self.location =""
        self.revisions_list = []
        self.curr_design = 0
        """Constructor."""
        FieldAnalysisEmit.__init__(
            self,
            "EMIT",
            projectname,
            designname,
            solution_type,
            setup_name,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
            machine=machine,
            port=port,
            aedt_process_id=aedt_process_id,
        )
        #if(self._aedt_version not in supported_versions):
        #   raise ValueError("This version of AEDT is unsupported for PYAEDT.")
    @pyaedt_function_handler() 
    def __enter__(self):
        return self
    @pyaedt_function_handler()
    def analyze(self):
        """
        Analyze the Active Design.

        Parameters
        ----------

        Returns
        -------
        :class:`pyaedt.modules.Revision`
            Revision object.

        References
        ----------
        >>> aedtapp.analyze()

        """
        design = self.odesktop.GetActiveProject().GetActiveDesign()
        if(not self.curr_design == design.getRevision()):
            design.AddResult()
            self.location = self.oproject.GetPath()
            self.revisions_list.append(Revision(self))
            self.curr_design = design.getRevision()
            print("checkpoint - revision generated successfully")
            return self.revisions_list[-1]

    @pyaedt_function_handler()
    def load_revision(self, path) :
        """
        Load a specific revision.

        Parameters
        ----------
        path:
            Path to a .aedtresult file

        Returns
        -------
        :class:`NoneType`

        References
        ----------
        >>> aedtapp.load_revision(path)

        """
        self._emit_api.load_result(path)
        self._result_loaded = True
    def result_mode_error():
        """ prints error message"""
        print("This function is inaccessible when the Emit object has no revisions")
    @pyaedt_function_handler()
    def interaction_domain():
        """
        Return a generic interaction domain.

        Parameters
        ----------
       
        Returns
        -------
        :class:`InteractionDomain`

        References
        ----------
        >>> Emit.interaction_domain()
        """
        interaction_domain = EmitApiPython.InteractionDomain()
        return interaction_domain
    @pyaedt_function_handler()
    def result_type(mode =''): 
        """
        Return a result_type object or a specific type based on input.

        Parameters
        ----------
        mode:
            Type of result_type object, options include: "emi", "desense", "sensitivity". Default is ''.

        Returns
        -------
        :class:`result_type`

        References
        ----------
        >>> Emit.result_type("emi")

        """
        result_t = EmitApiPython.result_type
        if mode == 'emi':
            result_t = EmitApiPython.result_type.emi
        elif mode == 'desense':
             result_t = EmitApiPython.result_type.desense
        elif mode == 'sensitivity':
             result_t = EmitApiPython.result_type.sensitivity 
        return result_t
    @pyaedt_function_handler()
    def tx_rx_mode(mode = ''): 
        """
        Return tx_rx_mode object or a specific mode based on input.

        Parameters
        ----------
        mode: str, option
            Type of tx_rx_mode object, options include: "tx", "rx". Default is ''.

        Returns
        -------
        :class:`tx_rx_mode`

        References
        ----------
        >>> Emit.tx_rx_mode("tx")

        """
        tx_rx_m = EmitApiPython.tx_rx_mode
        if mode == 'tx':
            tx_rx_m = EmitApiPython.tx_rx_mode.tx
        elif mode == 'rx':
             tx_rx_m = EmitApiPython.tx_rx_mode.rx
        return tx_rx_m
    @pyaedt_function_handler()   
    def copyright(self):
        """
        Return copyright info.

        Parameters
        ----------

        Returns
        -------
        :class:`str`

        References
        ----------
        >>> print(aedtapp.copyright())

        """
        copyright = self._emit_api.copyright()
        return copyright
    @pyaedt_function_handler()
    def version(self, detailed = False):
        """
        Return version info.

        Parameters
        ----------
        detailed: bool, optional
            verbose or not, default is False.
        Returns
        -------
        :class:`str`

        References
        ----------
        >>> print(aedtapp.version())

        """
        ver = self._emit_api.version(detailed)
        return ver       
    @pyaedt_function_handler()
    def get_engine(self):
        """
        Return the engine.

        Parameters
        ----------
        
        Returns
        -------
        :class:`EmitEngine`

        References
        ----------
        >>> eng = aedtapp.get_engine()

        """
        if self._result_loaded:
            engine = self._emit_api.get_engine()
        else:
            engine = None
            Emit.result_mode_error()
        return engine 
    @pyaedt_function_handler()
    def get_radios(self, tx_rx):
        """
       Return a list of all tx/rx radios in the project.

        Parameters
        ----------
        tx_rx: tx_rx_mode object
            Used for determining whether to get rx or tx radio names
        -------
        :class:`list of str`

        References
        ----------
        >>> radios = aedtapp.get_radios(Emit.tx_rx_mode.rx)

        """
        if self._result_loaded:
            radios = self._emit_api.radio_names(tx_rx)
        else:
            radios = None
            Emit.result_mode_error()
        return radios
    @pyaedt_function_handler()
    def get_bands(self, radio_name, tx_rx_mode):
        """
        Return a list of all tx/rx bands in a given radio.

        Parameters
        ----------
        radio_name: str
            Used to select a specific radio
        tx_rx: tx_rx_mode object
            Used for determining whether to get rx or tx radio names
        -------
        :class:`list of str`

        References
        ----------
        >>> bands = aedtapp.get_bands('Bluetooth', Emit.tx_rx_mode.rx)
        """
        if self._result_loaded:
            bands = self._emit_api.band_names(radio_name, tx_rx_mode)
        else:
            bands = None
            Emit.result_mode_error()
        return bands
    @pyaedt_function_handler()
    def get_band_frequencies(self, radio_name, band_name, tx_rx_mode):

        """
        Return a list of active frequencies for the selected tx/rx band in the selected radio.

        Parameters
        ----------
        radio_name: str
            Used to select a specific radio
        band_name: str
            Used to select a specific band
        tx_rx: tx_rx_mode object
            Used for determining whether to get rx or tx radio names
        -------
        :class:`list of float`

        References
        ----------
        >>> bands = aedtapp.get_bands('Bluetooth', 'Rx - Base Data Rate', Emit.tx_rx_mode.rx)
        """
        if self._result_loaded:
            freq = self._emit_api.active_frequencies(radio_name, band_name, tx_rx_mode)
        else:
            freq = None
            Emit.result_mode_error()
        return freq

