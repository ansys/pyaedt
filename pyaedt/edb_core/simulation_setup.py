from pyaedt.edb_core.edb_data.simulation_setup_data import HfssSimulationSetup
from pyaedt.edb_core.edb_data.simulation_setup_data import SiwaveDCSimulationSetup
from pyaedt.edb_core.edb_data.simulation_setup_data import SiwaveSYZSimulationSetup


class SimulationSetups(object):
    def __init__(self, edb):
        self._edb = edb

    @property
    def setups(self):
        _setups = {}
        for i in list(self._edb._active_layout.GetCell().SimulationSetups):
            if i.GetType() == self._edb.edb.Utility.SimulationSetupType.kHFSS:
                _setups[i.GetName()] = HfssSimulationSetup(self._edb, i.GetName(), i)
            elif i.GetType() == self._edb.edb.Utility.SimulationSetupType.kSIWave:
                _setups[i.GetName()] = SiwaveSYZSimulationSetup(self._edb, i.GetName(), i)
            elif i.GetType() == self._edb.edb.Utility.SimulationSetupType.kSIWaveDCIR:
                _setups[i.GetName()] = SiwaveDCSimulationSetup(self._edb, i.GetName(), i)
        return _setups

    @property
    def hfss_setups(self):
        return {i.name: i for i in self.setups if i.setup_type == "kHFSS"}

    def create_hfss_simulation_setup(self, name=None):
        """

        Parameters
        ----------
        name

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.simulation_setup_data.HfssSimulationSetup`
        """
        if name in self.setups:
            return False
        return HfssSimulationSetup(self._edb, name)

    def create_siwave_syz_setup(self, name=None):
        """

        Parameters
        ----------
        name

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.simulation_setup_data.SiwaveSYZSimulationSetup`
        """
        if name in self.setups:
            return False
        return SiwaveSYZSimulationSetup(self._edb, name)

    def create_siwave_dc_setup(self, name=None):
        """

        Parameters
        ----------
        name

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.simulation_setup_data.SiwaveDCSimulationSetup`
        """
        if name in self.setups:
            return False
        return SiwaveDCSimulationSetup(self._edb, name)
