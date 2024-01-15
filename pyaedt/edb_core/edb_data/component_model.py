from pyaedt.edb_core.edb_data.obj_base import ObjBase
from pyaedt.generic.general_methods import pyaedt_function_handler


class Model(ObjBase):
    """Manages component model class."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._model_type_mapping = {"PinPairModel": self._pedb.edb_api.cell}

    @property
    def model_type(self):
        """Component model type."""
        return self._edb_object.GetModelType()


class PinPairModel(Model):
    """Manages pin pair model class."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)

    @property
    def pin_pairs(self):
        """List of pin pair definitions."""
        return list(self._edb_object.PinPairs)

    @pyaedt_function_handler
    def delete_pin_pair_rlc(self, pin_pair):
        """Delete a pin pair definition.

        Parameters
        ----------
        pin_pair: Ansys.Ansoft.Edb.Utility.PinPair

        Returns
        -------
        bool
        """
        return self._edb_object.DeletePinPairRlc(pin_pair)

    @pyaedt_function_handler
    def set_pin_pair_rlc(self, pin_pair, pin_par_rlc):
        """Set resistance, inductance, capacitance to a pin pair definition.

        Parameters
        ----------
        pin_pair: Ansys.Ansoft.Edb.Utility.PinPair
        pin_par_rlc: Ansys.Ansoft.Edb.Utility.Rlc

        Returns
        -------
        bool
        """
        return self._edb_object.SetPinPairRlc(pin_pair, pin_par_rlc)
