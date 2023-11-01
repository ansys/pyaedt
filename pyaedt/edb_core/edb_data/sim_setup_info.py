from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler


class SimSetupInfo:

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def type(self):
        return self._edb_object.SimSetupType

