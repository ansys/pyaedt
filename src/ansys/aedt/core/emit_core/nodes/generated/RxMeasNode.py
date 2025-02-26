from ..EmitNode import *

class RxMeasNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

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
    def receive_frequency(self) -> float:
        """Receive Frequency
        "Channel associated with the measurement file."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "        """
        val = self._get_property('Receive Frequency')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    class MeasurementModeOption(Enum):
            AUDIO_SINAD = "Audio SINAD"
            DIGITAL_BER = "Digital BER"
            GPS_CNR = "GPS CNR"

    @property
    def measurement_mode(self) -> MeasurementModeOption:
        """Measurement Mode
        "Defines the mode for the receiver measurement."
        "        """
        val = self._get_property('Measurement Mode')
        val = self.MeasurementModeOption[val]
        return val

    @measurement_mode.setter
    def measurement_mode(self, value: MeasurementModeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Measurement Mode=' + value.value])

    @property
    def sinad_threshold(self) -> float:
        """SINAD Threshold
        "SINAD Threshold used for the receiver measurements."
        "Value should be between 5 and 20."
        """
        val = self._get_property('SINAD Threshold')
        return val

    @sinad_threshold.setter
    def sinad_threshold(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['SINAD Threshold=' + value])

    @property
    def gps_cnr_threshold(self) -> float:
        """GPS CNR Threshold
        "GPS CNR Threshold used for the receiver measurements."
        "Value should be between 15 and 30."
        """
        val = self._get_property('GPS CNR Threshold')
        return val

    @gps_cnr_threshold.setter
    def gps_cnr_threshold(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['GPS CNR Threshold=' + value])

    @property
    def ber_threshold(self) -> float:
        """BER Threshold
        "BER Threshold used for the receiver measurements."
        "Value should be between -12 and -1."
        """
        val = self._get_property('BER Threshold')
        return val

    @ber_threshold.setter
    def ber_threshold(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['BER Threshold=' + value])

    @property
    def default_intended_power(self) -> bool:
        """Default Intended Power
        "Specify the intended signal."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Default Intended Power')
        return val

    @default_intended_power.setter
    def default_intended_power(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Default Intended Power=' + value])

    @property
    def intended_signal_power(self) -> float:
        """Intended Signal Power
        "Specify the power level of the intended signal."
        "Value should be between -140 and -50."
        """
        val = self._get_property('Intended Signal Power')
        return val

    @intended_signal_power.setter
    def intended_signal_power(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Intended Signal Power=' + value])

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Specify the frequency deviation of the intended signal."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be between 1000 and 200000."
        """
        val = self._get_property('Freq. Deviation')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @freq_deviation.setter
    def freq_deviation(self, value : float|str):
        value = self._convert_to_default_units(value, "Frequency Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Freq. Deviation=' + f"{value}"])

    @property
    def modulation_depth(self) -> float:
        """Modulation Depth
        "Specify the modulation depth of the intended signal."
        "Value should be between 10 and 100."
        """
        val = self._get_property('Modulation Depth')
        return val

    @modulation_depth.setter
    def modulation_depth(self, value) -> float:
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Modulation Depth=' + value])

    @property
    def measure_selectivity(self) -> bool:
        """Measure Selectivity
        "Enable/disable the measurement of the receiver's selectivity."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Measure Selectivity')
        return val

    @measure_selectivity.setter
    def measure_selectivity(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Measure Selectivity=' + value])

    @property
    def measure_mixer_products(self) -> bool:
        """Measure Mixer Products
        "Enable/disable the measurement of the receiver's mixer products."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Measure Mixer Products')
        return val

    @measure_mixer_products.setter
    def measure_mixer_products(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Measure Mixer Products=' + value])

    @property
    def max_rf_order(self) -> int:
        """Max RF Order
        "Max RF Order of the mixer products to measure."
        "Value should be greater than 1."
        """
        val = self._get_property('Max RF Order')
        return val

    @max_rf_order.setter
    def max_rf_order(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Max RF Order=' + value])

    @property
    def max_lo_order(self) -> int:
        """Max LO Order
        "Max LO Order of the mixer products to measure."
        "Value should be greater than 1."
        """
        val = self._get_property('Max LO Order')
        return val

    @max_lo_order.setter
    def max_lo_order(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Max LO Order=' + value])

    @property
    def include_if(self) -> bool:
        """Include IF
        "Enable/disable the measurement of the IF channel."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Include IF')
        return val

    @include_if.setter
    def include_if(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Include IF=' + value])

    @property
    def measure_saturation(self) -> bool:
        """Measure Saturation
        "Enable/disable measurement of the receiver's saturation level."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Measure Saturation')
        return val

    @measure_saturation.setter
    def measure_saturation(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Measure Saturation=' + value])

    @property
    def use_ams_limits(self) -> bool:
        """Use AMS Limits
        "Allow AMS to determine the limits for measuring saturation."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Use AMS Limits')
        return val

    @use_ams_limits.setter
    def use_ams_limits(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Use AMS Limits=' + value])

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "Starting frequency for the measurement sweep."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be greater than 1e+06."
        """
        val = self._get_property('Start Frequency')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @start_frequency.setter
    def start_frequency(self, value : float|str):
        value = self._convert_to_default_units(value, "Frequency Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Start Frequency=' + f"{value}"])

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Stopping frequency for the measurement sweep."
        "Units options: Hz, kHz, MHz, GHz, THz."
        "Value should be less than 6e+09."
        """
        val = self._get_property('Stop Frequency')
        val = self._convert_from_default_units(float(val), "Frequency Unit")
        return val

    @stop_frequency.setter
    def stop_frequency(self, value : float|str):
        value = self._convert_to_default_units(value, "Frequency Unit")
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Stop Frequency=' + f"{value}"])

    @property
    def samples(self) -> int:
        """Samples
        "Number of measurement samples for each frequency."
        "Value should be between 2 and 100."
        """
        val = self._get_property('Samples')
        return val

    @samples.setter
    def samples(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Samples=' + value])

    @property
    def exclude_mixer_products_below_noise(self) -> bool:
        """Exclude Mixer Products Below Noise
        "Include/Exclude Mixer Products below the noise."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Exclude Mixer Products Below Noise')
        return val

    @exclude_mixer_products_below_noise.setter
    def exclude_mixer_products_below_noise(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['Exclude Mixer Products Below Noise=' + value])

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oRevisionData.GetEmitNodeProperties(self._result_id,self._node_id,'enabled')

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id,self._node_id,['enabled=' + value])

