from ..EmitNode import *

class ReadOnlyTxMeasNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def file(self) -> str:
        """File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        val = self._get_property('File')
        return val

    @property
    def source_file(self) -> str:
        """Source File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        val = self._get_property('Source File')
        return val

    @property
    def transmit_frequency(self) -> float:
        """Transmit Frequency
        "Channel associated with the measurement file."
        "        """
        val = self._get_property('Transmit Frequency')
        return val

    @property
    def use_ams_limits(self) -> bool:
        """Use AMS Limits
        "Allow AMS to define the frequency limits for the measurements."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use AMS Limits')
        return val

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "Starting frequency for the measurement sweep."
        "Value should be greater than 1e+06."
        """
        val = self._get_property('Start Frequency')
        return val

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Stopping frequency for the measurement sweep."
        "Value should be less than 6e+09."
        """
        val = self._get_property('Stop Frequency')
        return val

    @property
    def exclude_harmonics_below_noise(self) -> bool:
        """Exclude Harmonics Below Noise
        "Include/Exclude Harmonics below the noise."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Exclude Harmonics Below Noise')
        return val

