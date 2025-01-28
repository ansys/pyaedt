class Node_SamplingNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def get_sampling_type(self):
        """Sampling Type
        "Sampling to apply to this configuration."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Sampling Type')
    def set_sampling_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Sampling Type=' + value])
    class SamplingTypeOption(Enum):
        (
            SAMPLEALLCHANNELS = "Sample All Channels in Range(s)"
            RANDOMSAMPLING = "Random Sampling"
            UNIFORMSAMPLING = "Uniform Sampling"
        )

    @property
    def get_specify_percentage(self):
        """Specify Percentage
        "Specify the number of channels to simulate via a percentage of the total available band channels."
        "Value should be 'true' or 'false'."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Specify Percentage')
    def set_specify_percentage(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Specify Percentage=' + value])

    @property
    def get_percentage_of_channels(self):
        """Percentage of Channels
        "Percentage of the Band Channels to simulate."
        "Value should be between 1 and 100."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Percentage of Channels')
    def set_percentage_of_channels(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Percentage of Channels=' + value])

    @property
    def get_max__channelsrangeband(self):
        """Max # Channels/Range/Band
        "Maximum number of Band Channels to simulate."
        "Value should be between 1 and 100000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max # Channels/Range/Band')
    def set_max__channelsrangeband(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Max # Channels/Range/Band=' + value])

    @property
    def get_seed(self):
        """Seed
        "Seed for random channel generator."
        "Value should be greater than 0."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Seed')
    def set_seed(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Seed=' + value])

    @property
    def get_total_tx_channels(self):
        """Total Tx Channels
        "Total number of transmit channels this configuration is capable of operating on."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Total Tx Channels')

    @property
    def get_total_rx_channels(self):
        """Total Rx Channels
        "Total number of receive channels this configuration is capable of operating on."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Total Rx Channels')

    @property
    def get_warnings(self):
        """Warnings
        "Warning(s) for this node."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')

