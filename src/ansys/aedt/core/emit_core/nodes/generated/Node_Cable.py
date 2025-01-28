class Node_Cable(GenericEmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        GenericEmitNode.__init__(self, oDesign, result_id, node_id)

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
    def get_filename(self):
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filename')
    def set_filename(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def get_noise_temperature(self):
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Temperature')
    def set_noise_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

    @property
    def get_notes(self):
        """Notes
        "Expand to view/edit notes stored with the project."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
    def set_notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def get_type(self):
        """Type
        "Type of cable to use. Options include: By File (measured or simulated), Constant Loss, or Coaxial Cable."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
    def set_type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
        (
            BYFILE = "By File"
            CONSTANT = "Constant Loss"
            COAXIAL = "Coaxial Cable"
        )

    @property
    def get_length(self):
        """Length
        "Length of cable."
        "Value should be between 0 and 500."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Length')
    def set_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Length=' + value])

    @property
    def get_loss_per_length(self):
        """Loss Per Length
        "Cable loss per unit length (dB/meter)."
        "Value should be between 0 and 20."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Loss Per Length')
    def set_loss_per_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Loss Per Length=' + value])

    @property
    def get_measurement_length(self):
        """Measurement Length
        "Length of the cable used for the measurements."
        "Value should be between 0 and 500."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measurement Length')
    def set_measurement_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measurement Length=' + value])

    @property
    def get_resistive_loss_constant(self):
        """Resistive Loss Constant
        "Coaxial cable resistive loss constant."
        "Value should be between 0 and 2."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Resistive Loss Constant')
    def set_resistive_loss_constant(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Resistive Loss Constant=' + value])

    @property
    def get_dielectric_loss_constant(self):
        """Dielectric Loss Constant
        "Coaxial cable dielectric loss constant."
        "Value should be between 0 and 1."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Dielectric Loss Constant')
    def set_dielectric_loss_constant(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Dielectric Loss Constant=' + value])

    @property
    def get_warnings(self):
        """Warnings
        "Warning(s) for this node."
        """
        return oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Warnings')

