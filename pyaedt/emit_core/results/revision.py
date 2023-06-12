import warnings

from pyaedt.emit_core.EmitConstants import InterfererType
from pyaedt.emit_core.EmitConstants import TxRxMode

# from pyaedt.generic.general_methods import property
from pyaedt.generic.general_methods import pyaedt_function_handler


class Revision:
    """
    Provides the ``Revision`` object.

    Parameters
    ----------
    parent_results :
        ``Results`` object that this revision is associated with.
    emit_obj :
         ``Emit`` object that this revision is associated with.
    name : str, optional
        Name of the revision to create. The default is ``None``, in which
        case the name of the current design revision is used.

    Raises
    ------
    RuntimeError if the name given is not the name of an existing result set and a current result set already exists.

    Examples
    --------
    Create a ``Revision`` instance.

    >>> aedtapp = Emit()
    >>> rev = Revision(results, aedtapp, "Revision 1")
    >>> domain = aedtapp.interaction_domain()
    >>> rev.run(domain)
    """

    def __init__(self, parent_results, emit_obj, name=None):
        if not name:
            name = emit_obj.odesign.GetCurrentResult()
            if not name:
                name = emit_obj.odesign.AddResult("")
        else:
            if name not in emit_obj.odesign.GetResultList():
                name = emit_obj.odesign.AddResult(name)
        full = emit_obj.odesign.GetResultDirectory(name)

        self.name = name
        """Name of the revision."""

        self.path = full
        """Full path of the revision."""

        self.emit_project = emit_obj
        """Emit project."""

        raw_props = emit_obj.odesign.GetResultProperties(name)
        key = lambda s: s.split("=", 1)[0]
        val = lambda s: s.split("=", 1)[1]
        props = {key(s): val(s) for s in raw_props}

        self.revision_number = int(props["Revision"])
        """Unique revision number from the Emit design"""

        self.timestamp = props["Timestamp"]
        """Unique timestamp for the revision"""

        self.parent_results = parent_results
        """Parent Results object"""

        # load the revision after creating it
        self.revision_loaded = False
        """``True`` if the revision is loaded and ``False`` if it is not."""
        self._load_revision()

    @pyaedt_function_handler()
    def _load_revision(self):
        """
        Load this revision.

        Examples
        ----------
        >>> aedtapp.results.revision.load_revision()
        """
        if self.revision_loaded:
            return
        self.parent_results._unload_revisions()
        self.emit_project._emit_api.load_project(self.path)
        self.revision_loaded = True

    @staticmethod
    def result_mode_error():
        """
        Print the function mode error message.

        Returns
        -------
        """
        print("This function is inaccessible when the revision is not loaded.")

    @pyaedt_function_handler()
    def get_interaction(self, domain):
        """
        Creates a new interaction for a domain.

        Parameters
        ----------
        domain : class:`Emit.InteractionDomain`
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        interaction:class: `Interaction`
            Interaction object.

        Examples
        ----------
        >>> domain = aedtapp.results.interaction_domain()
        >>> rev.get_interaction(domain)

        """
        self._load_revision()
        engine = self.emit_project._emit_api.get_engine()
        if domain.interferer_names and engine.max_simultaneous_interferers != len(domain.interferer_names):
            raise ValueError("The max_simultaneous_interferers must equal the number of interferers in the domain.")
        interaction = engine.get_interaction(domain)
        return interaction

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
        interaction:class: `Interaction`
            Interaction object.

        Examples
        ----------
        >>> domain = aedtapp.results.interaction_domain()
        >>> rev.run(domain)

        """
        self._load_revision()
        engine = self.emit_project._emit_api.get_engine()
        interaction = engine.run(domain)
        # save the revision
        self.emit_project._emit_api.save_project()
        return interaction

    @pyaedt_function_handler()
    def is_domain_valid(self, domain):
        """
        Return ``True`` if the given domain is valid for the current revision.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Examples
        ----------
        >>> domain = aedtapp.interaction_domain()
        >>> aedtapp.results.current_revision.is_domain_valid(domain)
        True
        """
        self._load_revision()
        engine = self.emit_project._emit_api.get_engine()
        return engine.is_domain_valid(domain)

    @pyaedt_function_handler()
    def get_instance_count(self, domain):
        """
        Return the number of instances in the domain for the current revision.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        --------
        count : int
            Number of instances in the domain for the current revision.

        Examples
        ----------
        >>> domain = aedtapp.interaction_domain()
        >>> num_instances = aedtapp.results.current_revision.get_instance_count(domain)
        """
        self._load_revision()
        engine = self.emit_project._emit_api.get_engine()
        return engine.get_instance_count(domain)

    @pyaedt_function_handler()
    def get_receiver_names(self):
        """
        Get a list of all receivers in the project.

        Parameters
        ----------
        None

        Returns
        -------
        radios:class:`list of str`
            List of receiver names.

        Examples
        ----------
        >>> rxs = aedtapp.results.current_revision.get_reciver_names()
        """
        if self.revision_loaded:
            radios = self.emit_project._emit_api.get_radio_names(TxRxMode.RX, InterfererType.TRANSMITTERS_AND_EMITTERS)
        else:
            radios = None
            self.result_mode_error()
        if len(radios) == 0:
            warnings.warn("No valid receivers in the project.")
        return radios

    @pyaedt_function_handler()
    def get_interferer_names(self, interferer_type=None):
        """
        Get a list of all interfering transmitters/emitters in the project.

        Parameters
        ----------
        interferer_type : interferer_type object, optional
            Type of interferer to return. The default is ``None``, in which
            case both transmitters and emitters are returned. Options are:
                - transmitters
                - emitters
                - transmitters_and_emitters

        Returns
        -------
        radios:class:`list of str`
            List of interfering systems' names.

        Examples
        ----------
        >>> transmitters = aedtapp.results.current_revision.get_interferer_names(InterfererType.TRANSMITTERS)
        >>> emitters = aedtapp.results.current_revision.get_interferer_names(InterfererType.EMITTERS)
        >>> both = aedtapp.results.current_revision.get_interferer_names(InterfererType.TRANSMITTERS_AND_EMITTERS)
        """
        if interferer_type is None:
            interferer_type = InterfererType.TRANSMITTERS_AND_EMITTERS
        if self.revision_loaded:
            radios = self.emit_project._emit_api.get_radio_names(TxRxMode.TX, interferer_type)
        else:
            radios = None
            self.result_mode_error()
        if len(radios) == 0:
            warnings.warn("No valid radios or emitters in the project.")
            return None
        return radios

    @pyaedt_function_handler()
    def get_band_names(self, radio_name, tx_rx_mode=None):
        """
        Get a list of all ``tx`` or ``rx`` bands (or waveforms) in
        a given radio/emitter.

        Parameters
        ----------
        radio_name : str
            Name of the radio/emitter.
        tx_rx : :class:`EmitConstants.TxRxMode`, optional
            Specifies whether to get ``tx`` or ``rx`` band names. The default
            is ``None``, in which case the names of all enabled bands are returned.

        Returns
        -------
        bands:class:`list of str`
            List of ``tx`` or ``rx`` band/waveform names.

        Examples
        ----------
        >>> bands = aedtapp.results.current_revision.get_band_names('Bluetooth', TxRxMode.RX)
        >>> waveforms = aedtapp.results.current_revision.get_band_names('USB_3.x', TxRxMode.TX)
        """
        if tx_rx_mode is None:
            tx_rx_mode = TxRxMode.BOTH
        if self.revision_loaded:
            bands = self.emit_project._emit_api.get_band_names(radio_name, tx_rx_mode)
        else:
            bands = None
            self.result_mode_error()
        return bands

    @pyaedt_function_handler()
    def get_active_frequencies(self, radio_name, band_name, tx_rx_mode, units=""):
        """
        Get a list of active frequencies for a ``tx`` or ``rx`` band in a radio/emitter.

        Parameters
        ----------
        radio_name : str
            Name of the radio/emitter.
        band_name : str
           Name of the band.
        tx_rx : :class:`EmitConstants.TxRxMode`
            Specifies whether to get ``tx`` or ``rx`` radio freqs. The default
            is ``None``, in which case both ``tx`` and ``rx`` freqs are returned.
        units : str, optional
            Units for the frequencies. The default is ``None`` which uses the units
            specified globally for the project.

        Returns
        -------
        freqs : List of float
            List of ``tx`` or ``rx`` radio/emitter frequencies.

        Examples
        ----------
        >>> freqs = aedtapp.results.current_revision.get_active_frequencies(
                'Bluetooth', 'Rx - Base Data Rate', TxRxMode.RX)
        """
        if tx_rx_mode is None or tx_rx_mode == TxRxMode.BOTH:
            raise ValueError("The mode type must be specified as either Tx or Rx.")
        if self.revision_loaded:
            freqs = self.emit_project._emit_api.get_active_frequencies(radio_name, band_name, tx_rx_mode, units)
        else:
            freqs = None
            self.result_mode_error()
        return freqs

    @property
    def notes(self):
        """
        Add notes to the revision.

        Examples
        ----------
        >>> aedtapp.results.current_revision.notes = "Added a filter to the WiFi Radio."
        >>> aedtapp.results.current_revision.notes
        'Added a filter to the WiFi Radio.'
        """
        design = self.emit_project.odesign
        return design.GetResultNotes(self.name)

    @notes.setter
    def notes(self, notes):
        self.emit_project.odesign.SetResultNotes(self.name, notes)
        self.emit_project._emit_api.save_project()

    @property
    def max_n_to_1_instances(self):
        """
        The maximum number of instances per band combination allowed to run for N to 1.
        A value of 0 disables N to 1 entirely.
        A value of -1 allows unlimited N to 1 instances.

        Examples
        ----------
        >>> aedtapp.results.current_revision.max_n_to_1_instances = 2**20
        >>> aedtapp.results.current_revision.max_n_to_1_instances
        1048576
        """
        if self.emit_project._aedt_version < "2024.1":  # pragma: no cover
            raise RuntimeError("This function only supported in AEDT version 2024.1 and later.")
        if self.revision_loaded:
            engine = self.emit_project._emit_api.get_engine()
            max_instances = engine.max_n_to_1_instances
        else:  # pragma: no cover
            max_instances = None
        return max_instances

    @max_n_to_1_instances.setter
    def max_n_to_1_instances(self, max_instances):
        if self.emit_project._aedt_version < "2024.1":  # pragma: no cover
            raise RuntimeError("This function only supported in AEDT version 2024.1 and later.")
        if self.revision_loaded:
            engine = self.emit_project._emit_api.get_engine()
            engine.max_n_to_1_instances = max_instances
