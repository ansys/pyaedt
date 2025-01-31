from ..GenericEmitNode import *
class ReadOnlyRxMeasNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'File')
        key_val_pair = [i for i in props if 'File=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def source_file(self) -> str:
        """Source File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Source File')
        key_val_pair = [i for i in props if 'Source File=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def receive_frequency(self) -> float:
        """Receive Frequency
        "Channel associated with the measurement file."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Receive Frequency')
        key_val_pair = [i for i in props if 'Receive Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def measurement_mode(self):
        """Measurement Mode
        "Defines the mode for the receiver measurement."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measurement Mode')
        key_val_pair = [i for i in props if 'Measurement Mode=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class MeasurementModeOption(Enum):
            AUDIO_SINAD = "Audio SINAD"
            DIGITAL_BER = "Digital BER"
            GPS_CNR = "GPS CNR"

    @property
    def sinad_threshold(self) -> float:
        """SINAD Threshold
        "SINAD Threshold used for the receiver measurements."
        "Value should be between 5 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SINAD Threshold')
        key_val_pair = [i for i in props if 'SINAD Threshold=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def gps_cnr_threshold(self) -> float:
        """GPS CNR Threshold
        "GPS CNR Threshold used for the receiver measurements."
        "Value should be between 15 and 30."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'GPS CNR Threshold')
        key_val_pair = [i for i in props if 'GPS CNR Threshold=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def ber_threshold(self) -> float:
        """BER Threshold
        "BER Threshold used for the receiver measurements."
        "Value should be between -12 and -1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BER Threshold')
        key_val_pair = [i for i in props if 'BER Threshold=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def default_intended_power(self) -> bool:
        """Default Intended Power
        "Specify the intended signal."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Default Intended Power')
        key_val_pair = [i for i in props if 'Default Intended Power=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def intended_signal_power(self) -> float:
        """Intended Signal Power
        "Specify the power level of the intended signal."
        "Value should be between -140 and -50."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Intended Signal Power')
        key_val_pair = [i for i in props if 'Intended Signal Power=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def freq_deviation(self) -> float:
        """Freq. Deviation
        "Specify the frequency deviation of the intended signal."
        "Value should be between 1000 and 200000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Freq. Deviation')
        key_val_pair = [i for i in props if 'Freq. Deviation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def modulation_depth(self) -> float:
        """Modulation Depth
        "Specify the modulation depth of the intended signal."
        "Value should be between 10 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Modulation Depth')
        key_val_pair = [i for i in props if 'Modulation Depth=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def measure_selectivity(self) -> bool:
        """Measure Selectivity
        "Enable/disable the measurement of the receiver's selectivity."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measure Selectivity')
        key_val_pair = [i for i in props if 'Measure Selectivity=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def measure_mixer_products(self) -> bool:
        """Measure Mixer Products
        "Enable/disable the measurement of the receiver's mixer products."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measure Mixer Products')
        key_val_pair = [i for i in props if 'Measure Mixer Products=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def max_rf_order(self) -> int:
        """Max RF Order
        "Max RF Order of the mixer products to measure."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max RF Order')
        key_val_pair = [i for i in props if 'Max RF Order=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def max_lo_order(self) -> int:
        """Max LO Order
        "Max LO Order of the mixer products to measure."
        "Value should be greater than 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max LO Order')
        key_val_pair = [i for i in props if 'Max LO Order=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def include_if(self) -> bool:
        """Include IF
        "Enable/disable the measurement of the IF channel."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include IF')
        key_val_pair = [i for i in props if 'Include IF=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def measure_saturation(self) -> bool:
        """Measure Saturation
        "Enable/disable measurement of the receiver's saturation level."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measure Saturation')
        key_val_pair = [i for i in props if 'Measure Saturation=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def use_ams_limits(self) -> bool:
        """Use AMS Limits
        "Allow AMS to determine the limits for measuring saturation."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use AMS Limits')
        key_val_pair = [i for i in props if 'Use AMS Limits=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def start_frequency(self) -> float:
        """Start Frequency
        "Starting frequency for the measurement sweep."
        "Value should be greater than 1e+06."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start Frequency')
        key_val_pair = [i for i in props if 'Start Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def stop_frequency(self) -> float:
        """Stop Frequency
        "Stopping frequency for the measurement sweep."
        "Value should be less than 6e+09."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop Frequency')
        key_val_pair = [i for i in props if 'Stop Frequency=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def samples(self) -> int:
        """Samples
        "Number of measurement samples for each frequency."
        "Value should be between 2 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Samples')
        key_val_pair = [i for i in props if 'Samples=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def exclude_mixer_products_below_noise(self) -> bool:
        """Exclude Mixer Products Below Noise
        "Include/Exclude Mixer Products below the noise."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Exclude Mixer Products Below Noise')
        key_val_pair = [i for i in props if 'Exclude Mixer Products Below Noise=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

