import pyaedt.emit_core.EmitConstants
import pyaedt.generic.constants as consts
from pyaedt.generic.general_methods import pyaedt_function_handler


class Results:
    """
    Provides the ``Results`` object.

    Parameters
    ----------
    emit_obj : emit_obj object
        Emit object used to create the result.

    Examples
    --------
    Create an instance of the ``Result`` object.

    >>> aedtapp.results = Results()
    >>> mode = Emit.tx_rx_mode().rx
    >>> radio_RX = aedtapp.results.get_radio_names(mode)
    """

    def __init__(self, emit_obj):
        print("my class")
        self._result_loaded = False
        """``True`` if the results are loaded and ``False`` if they are not."""

        self.emit_api = emit_obj._emit_api
        """Instance of the Emit api."""

        self.revisions_list = []
        """List of all loaded result revisions."""

        self.location = emit_obj.oproject.GetPath()
        """Path to the current project."""

        self.current_design = 0
        """Initial revision of the Emit design."""

        self.units = emit_obj.units
        """Project units."""

    @property
    def result_loaded(self):
        """
        Check whether the result is loaded.

        Returns
        -------
        bool
            ``True`` if the results are loaded and ``False`` if they are not.
        """
        return self._result_loaded

    @result_loaded.setter
    def result_loaded(self, value):
        self._result_loaded = value

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
        radios:class:`list of str`
            list of tx or or rx radio names

        Examples
        ----------
        >>> radios = aedtapp.results.get_radio_names(Emit.tx_rx_mode.rx)
        """
        if self.result_loaded:
            radios = self.emit_api.get_radio_names(tx_rx)
        else:
            radios = None
            self.result_mode_error()
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
        bands:class:`list of str`
            list of tx or or rx radio band names

        Examples
        ----------
        >>> bands = aedtapp.results.get_band_names('Bluetooth', Emit.tx_rx_mode.rx)
        """
        if self.result_loaded:
            bands = self.emit_api.get_band_names(radio_name, tx_rx_mode)
        else:
            bands = None
            self.result_mode_error()
        return bands

    @pyaedt_function_handler()
    def get_active_frequencies(self, radio_name, band_name, tx_rx_mode, units=""):

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
        units : str
            Units for the frequencies.

        Returns
        -------
        freq:class:`list of float`
            List of tx or or rx radio frequencies.

        Examples
        ----------
        >>> bands = aedtapp.results.get_band_names('Bluetooth', 'Rx - Base Data Rate', Emit.tx_rx_mode.rx)
        """
        if self.result_loaded:
            freq = self.emit_api.get_active_frequencies(radio_name, band_name, tx_rx_mode)
            # Emit api returns freqs in Hz, convert to user's desired units.
            if not units or units not in EmitConstants.EMIT_VALID_UNITS["Frequency"]:
                units = self.units["Frequency"]
            freq = consts.unit_converter(freq, "Freq", "Hz", units)
        else:
            freq = None
            self.result_mode_error()
        return freq
