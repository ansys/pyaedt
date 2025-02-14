from ..EmitNode import *

class CustomCouplingNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name,'Csv')

    def rename(self, new_name):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def table_data(self):
        """ Table"
        "Table consists of 2 columns."
        "Frequency: 
        "    Value should be between 1 and 1e+11."
        "Value (dB): 
        "    Value should be between -1000 and 0."
        """
        return self._get_table_data()

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def enabled(self) -> bool:
        """Enabled
        "Enable/Disable coupling."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enabled')
        return val

    @enabled.setter
    def enabled(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enabled=' + value])

    @property
    def antenna_a(self) -> EmitNode:
        """Antenna A
        "First antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property('Antenna A')
        return val

    @antenna_a.setter
    def antenna_a(self, value: EmitNode):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Antenna A=' + value])

    @property
    def antenna_b(self) -> EmitNode:
        """Antenna B
        "Second antenna of the pair to apply the coupling values to."
        "        """
        val = self._get_property('Antenna B')
        return val

    @antenna_b.setter
    def antenna_b(self, value: EmitNode):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Antenna B=' + value])

    @property
    def enable_refinement(self) -> bool:
        """Enable Refinement
        "Enables/disables refined sampling of the frequency domain.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Enable Refinement')
        return val

    @enable_refinement.setter
    def enable_refinement(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Enable Refinement=' + value])

    @property
    def adaptive_sampling(self) -> bool:
        """Adaptive Sampling
        "Enables/disables adaptive refinement the frequency domain sampling.."
        "Value should be 'true' or 'false'."
        """
        val = self._get_property('Adaptive Sampling')
        return val

    @adaptive_sampling.setter
    def adaptive_sampling(self, value: bool):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Adaptive Sampling=' + value])

    @property
    def refinement_domain(self):
        """Refinement Domain
        "Points to use when refining the frequency domain.."
        "        """
        val = self._get_property('Refinement Domain')
        return val

    @refinement_domain.setter
    def refinement_domain(self, value):
        self._oDesign.GetModule('EmitCom').SetEmitNodeProperties(self._result_id,self._node_id,['Refinement Domain=' + value])

