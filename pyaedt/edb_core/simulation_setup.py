
from pyaedt.edb_core.edb_data.simulation_setup_data import HfssSimulationSetup


class SimulationSetups(object):

    def __init__(self, edb):
        self._edb = edb

    @property
    def setups(self):
        return {i.GetName(): HfssSimulationSetup(self._edb, i.GetName, i) for i in list(self._edb._active_layout.GetCell().SimulationSetups)}

    @property
    def hfss_setups(self):
        return {i.name: i for i in self.setups if i.setup_type == "kHFSS"}

    def create_hfss_simulation_setup(self, name=None):
        if name in self.setups:
            return False
        return HfssSimulationSetup(self._edb, name)
