from ..GenericEmitNode import *
class Cable(GenericEmitNode):
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
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Filename')
        key_val_pair = [i for i in props if 'Filename=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @filename.setter
    def filename(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Filename=' + value])

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Noise Temperature')
        key_val_pair = [i for i in props if 'Noise Temperature=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @noise_temperature.setter
    def noise_temperature(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Noise Temperature=' + value])

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Notes')
        key_val_pair = [i for i in props if 'Notes=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @notes.setter
    def notes(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Notes=' + value])

    @property
    def type(self):
        """Type
        "Type of cable to use. Options include: By File (measured or simulated), Constant Loss, or Coaxial Cable."
        "        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Type')
        key_val_pair = [i for i in props if 'Type=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @type.setter
    def type(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Type=' + value])
    class TypeOption(Enum):
            BYFILE = "By File"
            CONSTANT = "Constant Loss"
            COAXIAL = "Coaxial Cable"

    @property
    def length(self) -> float:
        """Length
        "Length of cable."
        "Value should be between 0 and 500."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Length')
        key_val_pair = [i for i in props if 'Length=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @length.setter
    def length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Length=' + value])

    @property
    def loss_per_length(self) -> float:
        """Loss Per Length
        "Cable loss per unit length (dB/meter)."
        "Value should be between 0 and 20."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Loss Per Length')
        key_val_pair = [i for i in props if 'Loss Per Length=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @loss_per_length.setter
    def loss_per_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Loss Per Length=' + value])

    @property
    def measurement_length(self) -> float:
        """Measurement Length
        "Length of the cable used for the measurements."
        "Value should be between 0 and 500."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Measurement Length')
        key_val_pair = [i for i in props if 'Measurement Length=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @measurement_length.setter
    def measurement_length(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Measurement Length=' + value])

    @property
    def resistive_loss_constant(self) -> float:
        """Resistive Loss Constant
        "Coaxial cable resistive loss constant."
        "Value should be between 0 and 2."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Resistive Loss Constant')
        key_val_pair = [i for i in props if 'Resistive Loss Constant=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @resistive_loss_constant.setter
    def resistive_loss_constant(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Resistive Loss Constant=' + value])

    @property
    def dielectric_loss_constant(self) -> float:
        """Dielectric Loss Constant
        "Coaxial cable dielectric loss constant."
        "Value should be between 0 and 1."
        """
        props = oDesign.GetModule('EmitCom').GetProperties(self._result_id,self._node_id,'Dielectric Loss Constant')
        key_val_pair = [i for i in props if 'Dielectric Loss Constant=' in i]
        if len(key_val_pair) != 1:
            return ''
        val = key_val_pair[1].split('=')[1]
        return val
    @dielectric_loss_constant.setter
    def dielectric_loss_constant(self, value):
        oDesign.GetModule('EmitCom').SetProperties(self._result_id,self._node_id,['Dielectric Loss Constant=' + value])

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

