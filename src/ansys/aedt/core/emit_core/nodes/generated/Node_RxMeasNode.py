class Node_RxMeasNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def get_file(self):
        """File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'File')

    @property
    def get_source_file(self):
        """Source File
        "Name of the measurement source."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Source File')

    @property
    def get_receive_frequency(self):
        """Receive Frequency
        "Channel associated with the measurement file."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Receive Frequency')

    @property
    def get_measurement_mode(self):
        """Measurement Mode
        "Defines the mode for the receiver measurement."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measurement Mode')
    def set_measurement_mode(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measurement Mode=' + value])
    class MeasurementModeOption(Enum):
        (
            AUDIO_SINAD = "Audio SINAD"
            DIGITAL_BER = "Digital BER"
            GPS_CNR = "GPS CNR"
        )

    @property
    def get_sinad_threshold(self):
        """SINAD Threshold
        "SINAD Threshold used for the receiver measurements."
        "Value should be between 5 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'SINAD Threshold')
    def set_sinad_threshold(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['SINAD Threshold=' + value])

    @property
    def get_gps_cnr_threshold(self):
        """GPS CNR Threshold
        "GPS CNR Threshold used for the receiver measurements."
        "Value should be between 15 and 30."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'GPS CNR Threshold')
    def set_gps_cnr_threshold(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['GPS CNR Threshold=' + value])

    @property
    def get_ber_threshold(self):
        """BER Threshold
        "BER Threshold used for the receiver measurements."
        "Value should be between -12 and -1."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'BER Threshold')
    def set_ber_threshold(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['BER Threshold=' + value])

    @property
    def get_default_intended_power(self):
        """Default Intended Power
        "Specify the intended signal."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Default Intended Power')
    def set_default_intended_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Default Intended Power=' + value])

    @property
    def get_intended_signal_power(self):
        """Intended Signal Power
        "Specify the power level of the intended signal."
        "Value should be between -140 and -50."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Intended Signal Power')
    def set_intended_signal_power(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Intended Signal Power=' + value])

    @property
    def get_freq_deviation(self):
        """Freq. Deviation
        "Specify the frequency deviation of the intended signal."
        "Value should be between 1000 and 200000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Freq. Deviation')
    def set_freq_deviation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Freq. Deviation=' + value])

    @property
    def get_modulation_depth(self):
        """Modulation Depth
        "Specify the modulation depth of the intended signal."
        "Value should be between 10 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Modulation Depth')
    def set_modulation_depth(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Modulation Depth=' + value])

    @property
    def get_measure_selectivity(self):
        """Measure Selectivity
        "Enable/disable the measurement of the receiver's selectivity."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measure Selectivity')
    def set_measure_selectivity(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measure Selectivity=' + value])

    @property
    def get_measure_mixer_products(self):
        """Measure Mixer Products
        "Enable/disable the measurement of the receiver's mixer products."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measure Mixer Products')
    def set_measure_mixer_products(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measure Mixer Products=' + value])

    @property
    def get_max_rf_order(self):
        """Max RF Order
        "Max RF Order of the mixer products to measure."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max RF Order')
    def set_max_rf_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max RF Order=' + value])

    @property
    def get_max_lo_order(self):
        """Max LO Order
        "Max LO Order of the mixer products to measure."
        "Value should be between 1 and unbounded."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max LO Order')
    def set_max_lo_order(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max LO Order=' + value])

    @property
    def get_include_if(self):
        """Include IF
        "Enable/disable the measurement of the IF channel."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Include IF')
    def set_include_if(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Include IF=' + value])

    @property
    def get_measure_saturation(self):
        """Measure Saturation
        "Enable/disable measurement of the receiver's saturation level."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measure Saturation')
    def set_measure_saturation(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measure Saturation=' + value])

    @property
    def get_use_ams_limits(self):
        """Use AMS Limits
        "Allow AMS to determine the limits for measuring saturation."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Use AMS Limits')
    def set_use_ams_limits(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Use AMS Limits=' + value])

    @property
    def get_start_frequency(self):
        """Start Frequency
        "Starting frequency for the measurement sweep."
        "Value should be greater than 1e6."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Start Frequency')
    def set_start_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Start Frequency=' + value])

    @property
    def get_stop_frequency(self):
        """Stop Frequency
        "Stopping frequency for the measurement sweep."
        "Value should be less than 6e9."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Stop Frequency')
    def set_stop_frequency(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Stop Frequency=' + value])

    @property
    def get_samples(self):
        """Samples
        "Number of measurement samples for each frequency."
        "Value should be between 2 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Samples')
    def set_samples(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Samples=' + value])

    @property
    def get_exclude_mixer_products_below_noise(self):
        """Exclude Mixer Products Below Noise
        "Include/Exclude Mixer Products below the noise."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Exclude Mixer Products Below Noise')
    def set_exclude_mixer_products_below_noise(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Exclude Mixer Products Below Noise=' + value])

    @property
    def get_enabled(self):
        """Enabled state for this node."""
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'enabled')
    def set_enabled(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['enabled=' + value])

