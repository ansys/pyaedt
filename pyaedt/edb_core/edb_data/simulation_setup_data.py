
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
        settings = self._edb_sim_setup_info.SimulationSettings.HFSSSolverSettings
        if "enhanced_low_freq_accuracy" in values:
            settings.EnhancedLowFreqAccuracy = values["enhanced_low_freq_accuracy"]
        if "order_basis" in values:
            settings.OrderBasis = values["order_basis"]
        if "RelativeResidual" in values:
            settings.RelativeResidual = values["RelativeResidual"]
        if "solver_type" in values:
            settings.SolverType = values["solver_type"]
        if "use_shell_elements" in values:
            settings.UseShellElements = values["use_shell_elements"]
    
    @property
    def adaptive_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        adaptive_freq_list = []
        for i in list(settings.AdaptiveFrequencyDataList):
            adaptive_freq_list.append({
                "adaptive_frequency": i.AdaptiveFrequency,
                "max_delta": i.MaxDelta,
                "max_passes": i.MaxPasses
            })

        return {
            "adaptive_frequency_data_list": adaptive_freq_list,
            "adapt_type": settings.AdaptType.ToString(),
            "basic": settings.Basic,
            "do_adaptive": settings.DoAdaptive,
            "max_refinement": settings.MaxRefinement,
            "max_refine_per_pass": settings.MaxRefinePerPass,
            "min_passes": settings.MinPasses,
            "save_fields": settings.SaveFields,
            "save_rad_field_only": settings.SaveRadFieldsOnly,
            "use_convergence_matrix": settings.UseConvergenceMatrix,
            "use_max_refinement": settings.UseMaxRefinement,
        }

    @adaptive_settings.setter
    def adaptive_settngs(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        if "adaptive_frequency_data_list" in values:
            adaptive_frequency_data = self._edb.simsetupdata.AdaptiveFrequencyData()
            for i in values["adaptive_frequency_data_list"]:
                adaptive_frequency_data.AdaptiveFrequency = i["adaptive_frequency"]
                adaptive_frequency_data.MaxDelta = i["max_delta"]
                adaptive_frequency_data.MaxPasses = i["max_passes"]
                settings.AdaptiveFrequencyDataList.append(adaptive_frequency_data)
        if "adapt_type" in values:
            settings.AdaptType = values["adapt_type"]
        if "basic" in values:
            settings.Basic = values["basic"]
        if "do_adaptive" in values:
            settings.DoAdaptive = values["do_adaptive"]
        if "max_refinement" in values:
            settings.MaxRefinement = values["max_refinement"]
        if "max_refine_per_pass" in values:
            settings.MaxRefinePerPass = values["max_refine_per_pass"]
        if "min_passes" in values:
            settings.MinPasses = values["min_passes"]
        if "save_fields" in values:
            settings.SaveFields = values["save_fields"]
        if "save_rad_field_only" in values:
            settings.SaveRadFieldsOnly = values["save_rad_field_only"]
        if "use_convergence_matrix" in values:
            settings.UseConvergenceMatrix = values["use_convergence_matrix"]
        if "use_max_refinement" in values:
            settings.UseMaxRefinement = values["use_max_refinement"]
    @property
    def DefeatureSettings(self):
        return 
    
    @property
    def ViaSettings(self):
        return

    @property
    def advanced_mesh_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.AdvancedMeshSettings
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