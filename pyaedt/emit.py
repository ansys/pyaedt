from __future__ import absolute_import

import os
import sys
from importlib import import_module

from pyaedt import generate_unique_project_name
from pyaedt.application.AnalysisEmit import FieldAnalysisEmit
from pyaedt.generic.general_methods import pyaedt_function_handler

# global variable used to store module import
mod = None


class Result:
    """
    Provides the ``Result`` object.

    Examples
    --------
    Create an instance of the ``Result`` object.

    >>> aedtapp.results = Result()
    >>> mode = Emit.tx_rx_mode().rx
    >>> radio_RX = aedtapp.results.get_radio_names(mode)
    """

    @pyaedt_function_handler()
    def __init__(self, emit_obj):
        self.__result_loaded = False
        self.emit_api = mod.EmitApi()
        self.revisions_list = []
        self.location = emit_obj.oproject.GetPath()
        self.curr_design = 0

    @pyaedt_function_handler()
    def set_result_loaded(self):
        """
        Set the status of whether the result is loaded to ``True``.

        Returns
        -------

        Examples
        ----------
        >>> aedtapp.results.set_result_loaded():
        """
        self.__result_loaded = True

    @pyaedt_function_handler()
    def get_result_loaded(self):
        """
        Check whether the result is loaded.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        ----------
        >>>  if aedtapp.results.get_result_loaded():
        """
        return self.__result_loaded

    @staticmethod
    def interaction_domain():
        """
        Get a generic interaction domain.

        Returns
        -------
        :class:`InteractionDomain`

        Examples
        ----------
        >>> domain = Result.interaction_domain()
        """
        try:
            interaction_domain = mod.InteractionDomain()
        except NameError:
            raise ValueError(
                "An Emit object must be initialized before any static member of the Result or Emit class is accessed."
            )
        return interaction_domain

    @staticmethod
    def result_mode_error():
        """
        Print the function mode error message.

        Returns
        -------
        """
        print("This function is inaccessible when the Emit object has no revisions.")

    @pyaedt_function_handler()
    def get_radio_names(self, tx_rx):
        """
        Get a list of all ``tx'' or ``rx`` radios in the project.

        Parameters
        ----------
        tx_rx : tx_rx_mode object
            Used for determining whether to get ``rx`` or ``tx`` radio names.

        Returns
        -------
        :class:`list of str`

        Examples
        ----------
        >>> radios = aedtapp.results.get_radio_names(Emit.tx_rx_mode.rx)
        """
        if self.get_result_loaded():
            radios = self.emit_api.radio_names(tx_rx)
        else:
            radios = None
            Emit.result_mode_error()
        return radios

    @pyaedt_function_handler()
    def get_band_names(self, radio_name, tx_rx_mode):
        """
        Get a list of all ``tx`` or ``rx`` bands in a given radio.

        Parameters
        ----------
        radio_name : str
            Name of the radio.
        tx_rx : tx_rx_mode object
            Used for determining whether to get ``rx`` or ``tx`` radio names.

        Returns
        -------
        :class:`list of str`

        Examples
        ----------
        >>> bands = aedtapp.results.get_band_names('Bluetooth', Emit.tx_rx_mode.rx)
        """
        if self.get_result_loaded():
            bands = self.emit_api.band_names(radio_name, tx_rx_mode)
        else:
            bands = None
            Emit.result_mode_error()
        return bands

    @pyaedt_function_handler()
    def get_active_frequencies(self, radio_name, band_name, tx_rx_mode):

        """
        Get a list of active frequencies for a ``tx`` or ``rx`` band in a radio.

        Parameters
        ----------
        radio_name : str
            Name of the radio.
        band_name : str
           Name of the band.
        tx_rx : tx_rx_mode object
            Used for determining whether to get ``rx`` or ``tx`` radio names.

        -------
        :class:`list of float`

        Examples
        ----------
        >>> bands = aedtapp.results.get_band_names('Bluetooth', 'Rx - Base Data Rate', Emit.tx_rx_mode.rx)
        """
        if self.get_result_loaded():
            freq = self.emit_api.active_frequencies(radio_name, band_name, tx_rx_mode)
        else:
            freq = None
            Emit.result_mode_error()
        return freq


class Revision:
    """
    Provides the ``Revision`` object.

    Parameters
    ----------
    Emit_obj :
         ``Emit`` object that this revision is associated with.
    name : str, optional
        Name of the revision to create. The default is ``None``, in which case a
        default name is given.

    Examples
    --------
    Create a ``Revision`` instance.

    >>> aedtapp = Emit()
    >>> rev = Revision(aedtapp, "Revision 1")
    >>> domain = Result.interaction_domain()
    >>> rev.run(domain)
    """

    @pyaedt_function_handler()
    def __init__(self, emit_obj, name=""):
        subfolder = ""
        for f in os.scandir(emit_obj.results.location):
            if os.path.splitext(f.name)[1].lower() in ".aedtresults":
                subfolder = os.path.join(f.path, "EmitDesign1")
        default_behaviour = not os.path.exists(os.path.join(subfolder, "{}.emit".format(name)))
        if default_behaviour:
            print("The most recently generated revision will be used because the revision specified does not exist.")
        if name == "" or default_behaviour:
            file = max([f for f in os.scandir(subfolder)], key=lambda x: x.stat().st_mtime)
            full = file.path
            name = file.name
        else:
            full = subfolder + "/{}.emit".format(name)
        self.name = name
        self.path = full
        self.emit_obj = emit_obj

    @pyaedt_function_handler()
    def run(self, domain):
        """
        Load the revision and then analyze along the given domain.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        :class:`Interaction`
            Interaction object.

        Examples
        ----------
        >>> domain = Result.interaction_domain()
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
        Whether to start the AEDT student version. The default is ``False``.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a server. This parameter works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    machine : str, optional
        Machine name that the Desktop session is to connect to. This
        parameter works only in 2022 R2 and later. The remote server must be
        up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
        If the machine is `"localhost"`, the server starts if it is not present.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

    Examples
    --------
    Create an ``Emit`` instance. You can also choose to define parameters for this instance here.

    >>> from pyaedt import Emit
    >>> aedtapp = Emit()

    Typically, it is desirable to specify a project name, design name, and other parameters.

    >>> aedtapp = Emit(projectname, designame)

    Once an ``Emit`` instance is initialized, you can edit the schematic:

    >>> rad1 = aedtapp.modeler.components.create_component("Bluetooth")
    >>> ant1 = aedtapp.modeler.components.create_component("Antenna")
    >>> if rad1 and ant1:
    >>>     ant1.move_and_connect_to(rad1)

    Once the schematic is generated, the ``Emit`` object can be analyzed to generate
    a revision. Each revision is added as an element of the ``Emit`` object member's
    revisions_list.

    >>> aedtapp.analyze()

    A revision within PyAEDT is analogous to a revision in AEDT. An interaction domain must
    be defined and then used as the input to the run command used on that revision.

    >>> domain = Emit.interaction_domain()
    >>> domain.rx_radio_name = "UE - HandHeld"
    >>> interaction = aedtapp.revisions_list[0].run(domain)

    The output of the run command is an ``interaction`` object. This object summarizes the interaction data
    that is defined in the interaction domain.

    >>> instance = interaction.worst_instance(Emit.result_type().sensitivity)
    >>> val = instance.value(Emit.result_type().sensitivity)
    >>> print("Worst-case sensitivity for Rx '{}' is {}dB.".format(domain.rx_radio_name, val))
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
        if projectname is None:
            projectname = generate_unique_project_name()
        self.__emit_api_enabled = False
        """Constructor for the ``FieldAnalysisEmit`` class"""
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
        desktop_path = self.desktop_install_dir
        path = os.path.join(desktop_path, "Delcross")
        sys.path.append(path)
        if self._aedt_version >= "2023.1":
            global mod
            mod = import_module("EmitApiPython")
            self._emit_api = mod.EmitApi()
            self.results = Result(self)
            self.__emit_api_enabled = True

    @pyaedt_function_handler()
    def __enter__(self):
        return self

    @pyaedt_function_handler()
    def analyze(self):
        """
        Analyze the active design.

        Returns
        -------
        :class:`pyaedt.modules.Revision`
            Revision object.

        Examples
        ----------
        >>> rev = aedtapp.analyze()

        """
        if self.__emit_api_enabled:
            design = self.odesktop.GetActiveProject().GetActiveDesign()
            if not self.results.curr_design == design.getRevision():
                design.AddResult()
                self.results.revisions_list.append(Revision(self))
                self.results.curr_design = design.getRevision()
                print("checkpoint - revision generated successfully")
                return self.results.revisions_list[-1]

    @pyaedt_function_handler()
    def _load_revision(self, path):
        """
        Load a specific revision.

        Parameters
        ----------
        path : str
            Path to an AEDT result file.

        Returns
        -------
        :class:`NoneType`

        Examples
        ----------
        >>> aedtapp._load_revision(path)

        """
        if self.__emit_api_enabled:
            self._emit_api.load_result(path)
            self.results.set_result_loaded()

    @staticmethod
    def result_type():
        """
        Get a result type.

        Returns
        -------
        :class:`result_type`

        Examples
        --------
        >>> Emit.result_type()

        """
        try:
            result = mod.result_type()
        except NameError:
            raise ValueError(
                "An Emit object must be initialized before any static member of the Result or Emit class is accessed."
            )
        return result

    @staticmethod
    def tx_rx_mode():
        """
        Get a ``tx_rx_mode`` object.

        Returns
        -------
        :class:`tx_rx_mode`

        Examples
        --------
        >>> tx_rx = Emit.tx_rx_mode()

        """
        try:
            tx_rx = mod.tx_rx_mode()
        except NameError:
            raise ValueError(
                "An Emit object must be initialized before any static member of the Result or Emit class is accessed."
            )
        return tx_rx

    @pyaedt_function_handler()
    def version(self, detailed=False):
        """
        Get version information.

        Parameters
        ----------
        detailed : bool, optional
            Whether to return a verbose description. The default is ``False``.

        Returns
        -------
        str

        Examples
        --------
        >>> print(aedtapp.version())

        """
        if self.__emit_api_enabled:
            ver = self._emit_api.version(detailed)
            return ver
