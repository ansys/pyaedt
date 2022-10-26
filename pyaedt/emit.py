from __future__ import absolute_import
from pyaedt.application.AnalysisEmit import FieldAnalysisEmit
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt import generate_unique_project_name
import sys
import os

sys.path.append("C:\\Users\\cchandel\\workspace\\build_output\\64Release\\Delcross")
import EmitApiPython
class Result:
    @pyaedt_function_handler()
    def __init__(self, api):
        self.__result_loaded = False
        self.__emit_api_python = api
        self.revisions_list = []
    @pyaedt_function_handler()
    def set_result_loaded(self):
        self.__result_loaded = True
    @pyaedt_function_handler()
    def get_result_loaded(self):
       return self.__result_loaded
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
        >>> domain = Result.interaction_domain()
        """
        interaction_domain = EmitApiPython.InteractionDomain()
        return interaction_domain

    @pyaedt_function_handler()
    def get_radio_names(self, tx_rx):
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
        >>> radios = aedtapp.results.get_radio_names(Emit.tx_rx_mode.rx)

        """
        if self.get_result_loaded():
            radios = self.__emit_api_python.radio_names(tx_rx)
        else:
            radios = None
            Emit.result_mode_error()
        return radios
    @pyaedt_function_handler()
    def get_band_names(self, radio_name, tx_rx_mode):
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
        >>> bands = aedtapp.results.get_band_names('Bluetooth', Emit.tx_rx_mode.rx)
        """
        if self.get_result_loaded():
            bands = self.__emit_api_python.band_names(radio_name, tx_rx_mode)
        else:
            bands = None
            Emit.result_mode_error()
        return bands
    @pyaedt_function_handler()
    def get_active_frequencies (self, radio_name, band_name, tx_rx_mode):

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
        >>> bands = aedtapp.results.get_band_names('Bluetooth', 'Rx - Base Data Rate', Emit.tx_rx_mode.rx)
        """
        if self.get_result_loaded():
            freq = self.__emit_api_python.active_frequencies(radio_name, band_name, tx_rx_mode)
        else:
            freq = None
            Emit.result_mode_error()
        return freq

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
    >>> domain = Results.interaction_domain()
    >>> rev.run(domain)
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
    def run(self, domain):
        """
        Load the revision, and proceed to analyze along the given domain

        Parameters
        ----------
            domain:
                An InteractionDomain must be defined to constrain the analysis parameters.
        Returns
        -------
        :class:`Interaction`
            Interaction object.

        References
        ----------
        >>> domain = Results.interaction_domain()
        >>> rev.run(domain)

        """
        self.emit_obj._load_revision(self.path)
        eng = self.emit_obj._emit_api.get_engine()
        interaction = eng.analyze(domain)
        return interaction
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
    >>> domain = Result.interaction_domain()
    >>> domain.rx_radio_name = "UE - HandHeld"
    >>> interaction = aedtapp.results.revisions_list[0].run(domain)

    The output of the run command is an interaction type object. An interaction summarizes the interaction data
    of whatever was defined in the interaction domain.
    >>> instance = interaction.worst_instance(Emit.result_type().sensitivity)
    >>> val = instance.value(Emit.result_type().sensitivity)
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
        self.results = Result(self._emit_api)
        self.location =""
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
        if(self._aedt_version < 2023.1):
           raise ValueError("This version of AEDT is unsupported for PYAEDT.")
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
        >>> rev = aedtapp.analyze()

        """
        design = self.odesktop.GetActiveProject().GetActiveDesign()
        if(not self.curr_design == design.getRevision()):
            design.AddResult()
            self.location = self.oproject.GetPath()
            self.results.revisions_list.append(Revision(self))
            self.curr_design = design.getRevision()
            print("checkpoint - revision generated successfully")
            return self.results.revisions_list[-1]

    @pyaedt_function_handler()
    def _load_revision(self, path) :
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
        >>> aedtapp._load_revision(path)

        """
        self._emit_api.load_result(path)
        self.results.set_result_loaded()

    def result_mode_error():
        """ prints error message"""
        print("This function is inaccessible when the Emit object has no revisions")

    @pyaedt_function_handler()
    def result_type(): 
        """
        Return a result_type object.

        Parameters
        ----------

        Returns
        -------
        :class:`result_type`

        References
        ----------
        >>> Emit.result_type()

        """
        result = EmitApiPython.result_type()
        return result
    @pyaedt_function_handler()
    def tx_rx_mode(): 
        """
        Return tx_rx_mode object.

        Parameters
        ----------

        Returns
        -------
        :class:`tx_rx_mode`

        References
        ----------
        >>> tx_rx = Emit.tx_rx_mode()

        """
        tx_rx = EmitApiPython.tx_rx_mode()
        return tx_rx 
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