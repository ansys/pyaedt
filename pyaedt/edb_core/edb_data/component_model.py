from pyaedt.edb_core.edb_data.obj_base import ObjBase
from pyaedt.generic.general_methods import pyaedt_function_handler


class Model(ObjBase):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._model_type_mapping = {"PinPairModel": self._pedb.edb_api.cell}

    @property
    def model_type(self):
        return self._edb_object.GetModelType()


class PinPairModel(Model):
    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)

    @pyaedt_function_handler
    def create(self):
        return self._pedb.cell.hierarchy._hierarchy.PinPairModel()

    @property
    def pin_pairs(self):
        return list(self._edb_object.PinPairs)

    @pyaedt_function_handler
    def delete_pin_pair_rlc(self, pin_pair):
        self._edb_object.DeletePinPairRlc(pin_pair)

    @pyaedt_function_handler
    def get_pin_pair_rlc(self):
        return self._edb_object.GetPinPairRlc(self.pin_pairs[0])

    @pyaedt_function_handler
    def set_pin_pair_rlc(self, pin_pair, pin_par_rlc):
        self._edb_object.SetPinPairRlc(pin_pair, pin_par_rlc)
