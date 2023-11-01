from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.edb_core.edb_data.hfss_simulation_setup_data import EdbFrequencySweep


class SimSetupInfo(object):

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._edb_object = edb_object
        self._name = ""

    @property
    def name(self):
        return self._edb_object.Name

    @name.setter
    def name(self, value):
        self._edb_object.Name = value
        self._name = value

    @property
    def setup_type(self):
        return self._edb_object.SimSetupType

    @property
    def frequency_sweeps(self):
        """Get frequency sweep list."""
        temp = {}
        for i in list(self._edb_object.SweepDataList):
            temp[i.Name] = EdbFrequencySweep(self, None, i.Name, i)
        return temp
