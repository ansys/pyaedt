from pyaedt import pyaedt_function_handler
from pyaedt.edb_core.edb_data.obj_base import ObjBase


class Model(ObjBase):

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def model_type(self):
        return self._edb_object.GetModelType()


class PinPairModel(Model):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def pin_pair_rlc(self):
        return self._edb_object.GetPinPairRlc()

    @pin_pair_rlc.setter
    def pin_pair_rlc(self, value):
        self._edb_model.SetPinPairRlc(self._edb_pin_pair, self._pin_pair_rlc)

    @property
    def resistance(self):
        return self.pin_pair_rlc.R.ToDouble()  # pragma: no cover
    
    
    @resistance.setter
    def resistance(self, value):
        self.pin_pair_rlc.R = value
        self._set_comp_prop(self.pin_pair_rlc)  # pragma: no cover
    
    
    @property
    def inductance(self):
        return self.pin_pair_rlc.L.ToDouble()  # pragma: no cover
    
    
    @inductance.setter
    def inductance(self, value):
        self.pin_pair_rlc.L = value
        self._set_comp_prop(self.pin_pair_rlc)  # pragma: no cover
    
    
    @property
    def capacitance(self):
        return self.pin_pair_rlc.C.ToDouble()  # pragma: no cover
    
    
    @capacitance.setter
    def capacitance(self, value):
        self.pin_pair_rlc.C = value
        self._set_comp_prop(self.pin_pair_rlc)  # pragma: no cover



class CommponentProperties(object):
    """."""

    def __init__(self, pedb, component_properties):
        self._pedb = pedb
        self._edb_object = component_properties

    @property
    def model(self):
        return Model(self._edb_object.GetModel())


