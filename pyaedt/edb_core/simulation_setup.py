
from pyaedt.edb_core.edb_data.simulation_setup_data import HFSSSimulationSetup
from pyaedt.edb_core.edb_data.simulation_setup_data import SIWaveDCIRSimulationSetup


class SimulationSetups(object):

    def __init__(self, edb):
        self._edb = edb

    @property
    def setups(self):
        return {i.GetName(): HFSSSimulationSetup(self._edb, i.GetName, i) for i in list(self._edb._active_layout.GetCell().SimulationSetups)}

    def create_hfss_simulation_setup(self):
        return HFSSSimulationSetup(self._edb)

    @property
    def create_siwave_dcir_simulation_setup(self):
        return SIWaveDCIRSimulationSetup()