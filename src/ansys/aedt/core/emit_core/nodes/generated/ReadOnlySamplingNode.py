from ..GenericEmitNode import *
class ReadOnlySamplingNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def sampling_type(self):
        """Sampling Type
        "Sampling to apply to this configuration."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Sampling Type')
        key_val_pair = [i for i in props if 'Sampling Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    class SamplingTypeOption(Enum):
            SAMPLEALLCHANNELS = "Sample All Channels in Range(s)"
            RANDOMSAMPLING = "Random Sampling"
            UNIFORMSAMPLING = "Uniform Sampling"

    @property
    def specify_percentage(self) -> bool:
        """Specify Percentage
        "Specify the number of channels to simulate via a percentage of the total available band channels."
        "Value should be 'true' or 'false'."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Specify Percentage')
        key_val_pair = [i for i in props if 'Specify Percentage=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def percentage_of_channels(self) -> float:
        """Percentage of Channels
        "Percentage of the Band Channels to simulate."
        "Value should be between 1 and 100."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Percentage of Channels')
        key_val_pair = [i for i in props if 'Percentage of Channels=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def max__channelsrangeband(self) -> int:
        """Max # Channels/Range/Band
        "Maximum number of Band Channels to simulate."
        "Value should be between 1 and 100000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Max # Channels/Range/Band')
        key_val_pair = [i for i in props if 'Max # Channels/Range/Band=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def seed(self) -> int:
        """Seed
        "Seed for random channel generator."
        "Value should be greater than 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Seed')
        key_val_pair = [i for i in props if 'Seed=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def total_tx_channels(self) -> int:
        """Total Tx Channels
        "Total number of transmit channels this configuration is capable of operating on."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Total Tx Channels')
        key_val_pair = [i for i in props if 'Total Tx Channels=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def total_rx_channels(self) -> int:
        """Total Rx Channels
        "Total number of receive channels this configuration is capable of operating on."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Total Rx Channels')
        key_val_pair = [i for i in props if 'Total Rx Channels=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')
        key_val_pair = [i for i in props if 'Warnings=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

