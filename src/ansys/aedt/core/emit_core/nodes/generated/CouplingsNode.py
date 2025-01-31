from ..GenericEmitNode import *
class CouplingsNode(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

    def import_touchstone(self, file_name):
        """Open an Existing S-Matrix Data File"""
        return self._import(file_name,'TouchstoneCoupling')

    def add_custom_coupling(self):
        """Add a new node to define custom coupling between antennas"""
        return self._add_child_node("CustomCouplingNode")

    def add_path_loss_coupling(self):
        """Add a new node to define path loss coupling between antennas"""
        return self._add_child_node("PropagationLossCouplingNode")

    def add_two_ray_path_loss_coupling(self):
        """Add a new node to define two ray ground reflection coupling between antennas"""
        return self._add_child_node("TwoRayPathLossCouplingNode")

    def add_log_distance_coupling(self):
        """Add a new node to define coupling between antennas using the Log Distance model"""
        return self._add_child_node("LogDistanceCouplingNode")

    def add_hata_coupling(self):
        """Add a new node to define coupling between antennas using the Hata COST 231 model"""
        return self._add_child_node("HataCouplingNode")

    def add_walfisch_ikegami_coupling(self):
        """Add a new node to define coupling between antennas using the Walfisch-Ikegami model"""
        return self._add_child_node("WalfischCouplingNode")

    def add_erceg_coupling(self):
        """Add a new node to define coupling between antennas using the Erceg coupling model"""
        return self._add_child_node("ErcegCouplingNode")

    def add_indoor_propagation_coupling(self):
        """Add a new node to define coupling between antennas using the ITU Indoor Propagation model"""
        return self._add_child_node("IndoorPropagationCouplingNode")

    def add__5g_channel_model_coupling(self):
        """Add a new node to define coupling between antennas using the 5G channel coupling model"""
        return self._add_child_node("FiveGChannelModel")

    @property
    def minimum_allowed_coupling(self) -> float:
        """Minimum Allowed Coupling
        "Global minimum allowed coupling value. All computed coupling within this project will be >= this value."
        "Value should be between -1000 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Minimum Allowed Coupling')
        key_val_pair = [i for i in props if 'Minimum Allowed Coupling=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @minimum_allowed_coupling.setter
    def minimum_allowed_coupling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Minimum Allowed Coupling=' + value])

    @property
    def global_default_coupling(self) -> float:
        """Global Default Coupling
        "Default antenna-to-antenna coupling loss value."
        "Value should be between -1000 and 0."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Global Default Coupling')
        key_val_pair = [i for i in props if 'Global Default Coupling=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @global_default_coupling.setter
    def global_default_coupling(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Global Default Coupling=' + value])

    @property
    def antenna_tags(self) -> str:
        """Antenna Tags
        "All tags currently used by all antennas in the project."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Antenna Tags')
        key_val_pair = [i for i in props if 'Antenna Tags=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val

