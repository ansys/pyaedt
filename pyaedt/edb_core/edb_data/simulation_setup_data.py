from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.constants import BasisOrder
from pyaedt.generic.constants import CutoutSubdesignType
from pyaedt.generic.constants import RadiationBoxType
from pyaedt.generic.constants import SolverType
from pyaedt.generic.constants import SweepType


class HFSSSimulationSetup(object):
    def __init__(self, edb, name=None, edb_hfss_sim_setup=None):
        self._edb = edb

        if edb_hfss_sim_setup:
            self._edb_sim_setup = edb_hfss_sim_setup
            self._edb_sim_setup_info = edb_hfss_sim_setup.GetSimSetupInfo()
            self._name = self._edb_sim_setup_info.Name
        else:
            if not name:
                self._name = generate_unique_name("hfss")
            else:
                self._name = name

            self._edb_sim_setup_info = self._edb.simsetupdata.SimSetupInfo[
                self._edb.simsetupdata.HFSSSimulationSettings]()

            self.hfss_solver_settings = {"OrderBasis": 0}
            self._update_setup()

    def _update_setup(self):

        self._edb_sim_setup = self._edb.edb.Utility.HFSSSimulationSetup(self._edb_sim_setup_info)
        if self.name in self._edb.simulation_setups.setups:
            self._edb._active_layout.GetCell().DeleteSimulationSetup(self.name)
        return self._edb._active_layout.GetCell().AddSimulationSetup(self._edb_sim_setup)

    @property
    def name(self):
        return self._name

    @property
    def hfss_solver_settings(self):
        """
        EnhancedLowFreqAccuracy: bool
        OrderBasis: 0=Mixed, 1=Zero, 2=1st order, 3=2nd order
        RelativeResidual
        SolverType
        UseShellElements
         
        Returns
        -------

        """
        settings = self._edb_sim_setup_info.SimulationSettings.HFSSSolverSettings
        return {
            "enhanced_low_freq_accuracy": settings.EnhancedLowFreqAccuracy,
            "order_basis": settings.OrderBasis,
            "relative_residual": settings.RelativeResidual,
            "solver_type": settings.SolverType.ToString(),
            "use_shell_elements": settings.UseShellElements
        }

    @hfss_solver_settings.setter
    def hfss_solver_settings(self, values):
        hfss_solver_settings = self._edb_sim_setup_info.SimulationSettings.HFSSSolverSettings
        if "enhanced_low_freq_accuracy" in values:
            hfss_solver_settings.EnhancedLowFreqAccuracy = values["enhanced_low_freq_accuracy"]
        if "order_basis" in values:
            hfss_solver_settings.OrderBasis = values["order_basis"]
        if "RelativeResidual" in values:
            hfss_solver_settings.RelativeResidual = values["RelativeResidual"]
        if "solver_type" in values:
            hfss_solver_settings.SolverType = values["solver_type"]
        if "use_shell_elements" in values:
            hfss_solver_settings.UseShellElements = values["use_shell_elements"]
    
    @property
    def AdaptiveSettings(self):
        return self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
    
    @property
    def DefeatureSettings(self):
        return 
    
    @property
    def ViaSettings(self):
        return

    @property
    def AdvancedMeshSettings(self):
        return

    @property
    def CurveApproxSettings(self):
        return

    @property
    def DCRSettings(self):
        return

    def ss1(self):
        adapt = self._edb.simsetupdata.AdaptiveFrequencyData()
        self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings.AdaptiveFrequencyDataList = convert_py_list_to_net_list(
            [adapt]
        )
        return

    def add_sweep(self):
        sweep = self._edb.simsetupdata.SweepData("sweep1")
        sweep.IsDiscrete = False
        sweep.Frequencies = self._edb.simsetupdata.SweepData.SetFrequencies(
            "1GHz",
            "10GHz",
            "1GHz",
        )

class  SIWaveDCIRSimulationSetup(object):
    def __init__(self):
        pass