import os
import warnings

import pyaedt.emit_core.EmitConstants as emitConsts
import pyaedt.generic.constants as consts
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
        Name of the revision to create. The default is ``None``, in which case a
        default name is given.

    Examples
    --------
    Create a ``Revision`` instance.

    >>> aedtapp = Emit()
    >>> rev = Revision(results, aedtapp, "Revision 1")
    >>> domain = aedtapp.interaction_domain()
    >>> rev.run(domain)
    """

    def __init__(self, parent_results, emit_obj, name=""):
        design = emit_obj.odesktop.GetActiveProject().GetActiveDesign()
        subfolder = ""
        for f in os.scandir(emit_obj.oproject.GetPath()):
            if os.path.splitext(f.name)[1].lower() in ".aedtresults":
                subfolder = os.path.join(f.path, "EmitDesign1")
        default_behaviour = not os.path.exists(os.path.join(subfolder, "{}.emit".format(name)))
        if default_behaviour:
            print("The most recently generated revision will be used because the revision specified does not exist.")
        if name == "" or default_behaviour:
            # if there are no results yet, add a new Result
            result_files = os.listdir(subfolder)
            if len(result_files) == 0:
                name = design.AddResult()
                full = subfolder + "/{}.emit".format(name)
            else:
                file = max([f for f in os.scandir(subfolder)], key=lambda x: x.stat().st_mtime)
                full = file.path
                name = file.name
        else:
            full = subfolder + "/{}.emit".format(name)
        self.name = name
        """Name of the revision."""

        self.path = full
        """Full path of the revision."""

        self.emit_project = emit_obj
        """Emit project."""

        self.revision_number = design.GetRevision()
        """Unique revision number from the Emit design"""

        self.parent_results = parent_results
        """Parent Results object"""

        # load the revision after creating it
        self.revision_loaded = False
        """``True`` if the revision is loaded and ``False`` if it is not."""
        self._load_revision()

    @pyaedt_function_handler()
    def _load_revision(self):
        """
        Load a specific revision.

        Parameters
        ----------
        path : str
            Path to an AEDT EMIT result directory.
            For example, "Revision 1.emit"

        Examples
        ----------
        >>> aedtapp.results.revision.load_revision()
        """
        if self.revision_loaded:
            print("Specified result already loaded.")
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
        return interaction

    @pyaedt_function_handler()
    def get_max_simultaneous_interferers(self):
        """
        Get the number of maximum simultaneous interferers.

        Returns
        -------
        max_interferers : int
            Maximum number of simultaneous interferers associated with engine

        Examples
        ----------
        >>> max_num = aedtapp.results.current_revision.get_max_simultaneous_interferers()
        """
        self._load_revision()
        engine = self.emit_project._emit_api.get_engine()
        max_interferers = engine.max_simultaneous_interferers
        return max_interferers

    @pyaedt_function_handler()
    def set_max_simultaneous_interferers(self, val):
        """
        Set the number of maximum simultaneous interferers.

        Examples
        ----------
        >>> max_num = aedtapp.results.current_revision.set_max_simultaneous_interferers(3)
        """
        self._load_revision()
        engine = self.emit_project._emit_api.get_engine()
        engine.max_simultaneous_interferers = val

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
            radios = self.emit_project._emit_api.get_radio_names(
                emitConsts.tx_rx_mode().rx, emitConsts.interferer_type().transmitters_and_emitters
            )
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
        interferer_type : interferer_type object
            Type of interferer to return. Options are:
                - transmitters
                - emitters
                - transmitters_and_emitters

        Returns
        -------
        radios:class:`list of str`
            List of interfering systems' names.

        Examples
        ----------
        >>> ix_type = emitConsts.interferer_type().transmitters
        >>> transmitters = aedtapp.results.current_revision.get_interferer_names(ix_type)
        >>> ix_type = emitConsts.interferer_type().emitters
        >>> emitters = aedtapp.results.current_revision.get_interferer_names(ix_type)
        >>> ix_type = emitConsts.interferer_type().transmitters_and_emitters
        >>> both = aedtapp.results.current_revision.get_interferer_names(ix_type)
        """
        if interferer_type is None:
            interferer_type = emitConsts.interferer_type().transmitters_and_emitters
        if self.revision_loaded:
            radios = self.emit_project._emit_api.get_radio_names(emitConsts.tx_rx_mode().tx, interferer_type)
        else:
            radios = None
            self.result_mode_error()
        if len(radios) == 0:
            warnings.warn("No valid radios or emitters in the project.")
            return None
        return radios

    @pyaedt_function_handler()
    def get_band_names(self, radio_name, tx_rx_mode):
        """
        Get a list of all ``tx`` or ``rx`` bands (or waveforms) in
        a given radio/emitter.

        Parameters
        ----------
        radio_name : str
            Name of the radio/emitter.
        tx_rx : tx_rx_mode object
            Specifies whether to get ``tx`` or ``rx`` band names.

        Returns
        -------
        bands:class:`list of str`
            List of ``tx`` or ``rx`` band/waveform names.

        Examples
        ----------
        >>> bands = aedtapp.results.current_revision.get_band_names('Bluetooth', Emit.tx_rx_mode.rx)
        >>> waveforms = aedtapp.results.current_revision.get_band_names('USB_3.x', Emit.tx_rx_mode.tx)
        """
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
        tx_rx : tx_rx_mode object
            Specifies whether to get ``tx`` or ``rx`` radio freqs.
        units : str
            Units for the frequencies.

        Returns
        -------
        freq:class:`list of float`
            List of ``tx`` or ``rx`` radio/emitter frequencies.

        Examples
        ----------
        >>> freqs = aedtapp.results.current_revision.get_active_frequencies(
                'Bluetooth', 'Rx - Base Data Rate', Emit.tx_rx_mode.rx)
        """
        if self.revision_loaded:
            freq = self.emit_project._emit_api.get_active_frequencies(radio_name, band_name, tx_rx_mode)
            # Emit api returns freqs in Hz, convert to user's desired units.
            if not units or units not in emitConsts.EMIT_VALID_UNITS["Frequency"]:
                units = self.emit_project._units["Frequency"]
            freq = consts.unit_converter(freq, "Freq", "Hz", units)
        else:
            freq = None
            self.result_mode_error()
        return freq
