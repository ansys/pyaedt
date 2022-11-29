
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.edb_core.general import convert_py_list_to_net_list

from pyaedt.generic.constants import BasisOrder
from pyaedt.generic.constants import CutoutSubdesignType
from pyaedt.generic.constants import RadiationBoxType
from pyaedt.generic.constants import SolverType
from pyaedt.generic.constants import SweepType


class FreqSweep(object):
    def __init__(self, edb_hfss_sim_setup, name=None, edb_sweep_data=None):
        self._edb_hfss_sim_setup = edb_hfss_sim_setup

        if edb_sweep_data:
            self._edb_sweep_data = edb_sweep_data
            self._name = self._edb_sweep_data.Name
        else:
            if not name:
                self._name = generate_unique_name("sweep")
            else:
                self._name = name

            self._edb_sweep_data = self._edb_hfss_sim_setup._edb.simsetupdata.SweepData(name)

    @property
    def name(self):
        return self._edb_sweep_data.Name

    @name.setter
    def name(self, value):
        self._edb_sweep_data.Name = value

    @property
    def sweep_type(self):
        return

    @property
    def enabled(self):
        return

    @property
    def frequencies(self):
        return list(self._edb_sweep_data.Frequencies)

    @property
    def matrix_conv_entry_list(self):
        return list(self._edb_sweep_data.matrix_conv_entry_list)

    @property
    def options(self):
        settings = self._edb_sweep_data

        return {
            "name": settings.Name,
            "enabled": settings.Enabled,
            "adaptive_sampling": settings.AdaptiveSampling,
            "adv_dc_extrapolation": settings.AdvDCExtrapolation,
            "auto_s_mat_only_solve": settings.AutoSMatOnlySolve,
            "enforce_causality": settings.EnforceCausality,
            "enforce_dc_and_causality": settings.EnforceDCAndCausality,
            "enforce_passivity": settings.EnforcePassivity,
            "frequency_string": settings.FrequencyString,
            "freq_sweep_type": settings.FreqSweepType.ToString(),
            "interp_use_full_basis": settings.InterpUseFullBasis,
            "interp_use_port_impedance": settings.InterpUsePortImpedance,
            "interp_use_prop_const": settings.InterpUsePropConst,
            "interp_use_s_matrix": settings.InterpUseSMatrix,
            "max_solutions": settings.MaxSolutions,
            "min_freq_s_mat_only_solve": settings.MinFreqSMatOnlySolve,
            "min_solved_freq": settings.MinSolvedFreq,
            "passivity_tolerance": settings.PassivityTolerance,
            "relative_s_error": settings.RelativeSError,
            "save_fields": settings.SaveFields,
            "save_rad_fields_only": settings.SaveRadFieldsOnly,
            "use_q3d_for_dc": settings.UseQ3DForDC,
        }

    def apply_frequency_unit(self, def_freq, frequency):

        self._edb_sweep_data.ApplyFrequencyUnit(def_freq, frequency)

    def set_frequencies(self, freq_sweep_string):
        """
        [[LIN, 0.1GHz, 20GHz, 0.05GHz],
        [LINC, 0GHz, 1Hz, 1],
        [DEC, 1kHz, 0.1GHz, 10]]"""
        value = " ".join([" ".join(sweeps) for sweeps in freq_sweep_string])
        self._edb_sweep_data.SetFrequencies(value)


class HfssSimulationSetup(object):
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

        self._edb_sim_setup = self._edb.edb.Utility.HfssSimulationSetup(self._edb_sim_setup_info)
        if self.name in self._edb.simulation_setups.setups:
            self._edb._active_layout.GetCell().DeleteSimulationSetup(self.name)
        return self._edb._active_layout.GetCell().AddSimulationSetup(self._edb_sim_setup)

    @property
    def frequency_sweeps(self):
        sweep_data_list = {}
        for i in list(self._edb_sim_setup_info.SweepDataList):
            sweep_data_list[i.Name] = FreqSweep(self, i.Name, i)
        return sweep_data_list
    @property
    def name(self):
        return self._name

    @property
    def enabled(self):
        return self._edb_sim_setup_info.SimulationSettings.Enabled

    @enabled.setter
    def enabled(self, value):
        self._edb_sim_setup_info.SimulationSettings.Enabled = value

    @property
    def solver_slider_type(self):
        return self._edb_sim_setup_info.SimulationSettings.TSolveSliderType

    @solver_slider_type.setter
    def solver_slider_type(self, value):
        self._edb_sim_setup_info.SimulationSettings.TSolveSliderType = value

    @property
    def is_auto_setup(self):
        return self._edb_sim_setup_info.SimulationSettings.IsAutoSetup

    @is_auto_setup.setter
    def is_auto_setup(self, value):
        self._edb_sim_setup_info.SimulationSettings.IsAutoSetup = value
    @property
    def setup_type(self):
        return self._edb_sim_setup_info.SimulationSettings.SetupType

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
    def defeature_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.DefeatureSettings
        return {
            "defeature_abs_length": settings.DefeatureAbsLength,
            "defeature_ratio": settings.DefeatureRatio,
            "healing_option": settings.HealingOption,
            "model_type": settings.ModelType,
            "remove_floating_geometry": settings.RemoveFloatingGeometry,
            "small_void_area": settings.SmallVoidArea,
            "union_polygons": settings.UnionPolygons,
            "use_defeature": settings.UseDefeature,
            "use_defeature_abs_length": settings.UseDefeatureAbsLength,
        }

    @defeature_settings.setter
    def defeature_settings(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.DefeatureSettings
        if "defeature_abs_length" in values["DefeatureAbsLength"]:
            settings.DefeatureAbsLength = values["defeature_abs_length"]
        if "defeature_ratio" in values["DefeatureRatio"]:
            settings.DefeatureRatio = values["defeature_ratio"]
        if "healing_option" in values["HealingOption"]:
            settings.HealingOption = values["healing_option"]
        if "model_type" in values["ModelType"]:
            settings.ModelType = values["model_type"]
        if "remove_floating_geometry" in values["RemoveFloatingGeometry"]:
            settings.RemoveFloatingGeometry = values["remove_floating_geometry"]
        if "small_void_area" in values["SmallVoidArea"]:
            settings.SmallVoidArea = values["small_void_area"]
        if "union_polygons" in values["UnionPolygons"]:
            settings.UnionPolygons = values["union_polygons"]
        if "use_defeature" in values["UseDefeature"]:
            settings.UseDefeature = values["use_defeature"]
        if "use_defeature_abs_length" in values["UseDefeatureAbsLength"]:
            settings.UseDefeatureAbsLength = values["use_defeature_abs_length"]

    @property
    def via_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.ViaSettings
        return {
            "t25_d_via_style": settings.T25DViaStyle,
            "via_density": settings.ViaDensity,
            "via_material": settings.ViaMaterial,
            "via_num_sides": settings.ViaNumSides,
            "via_style": settings.ViaStyle,
        }

    @via_settings.setter
    def via_settings(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.ViaSettings
        if "t25_d_via_style" in values["T25DViaStyle"]:
            settings.T25DViaStyle = values["t25_d_via_style"]
        if "via_density" in values["ViaDensity"]:
            settings.ViaDensity = values["via_density"]
        if "via_material" in values["ViaMaterial"]:
            settings.ViaMaterial = values["via_material"]
        if "via_num_sides" in values["ViaNumSides"]:
            settings.ViaNumSides = values["via_num_sides"]
        if "via_style" in values["ViaStyle"]:
            settings.ViaStyle = values["via_style"]

    @property
    def advanced_mesh_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.AdvancedMeshSettings
        return {
            "layer_snap_tol": settings.LayerSnapTol,
            "mesh_display_attributes": settings.MeshDisplayAttributes,
            "replace3_d_triangles": settings.Replace3DTriangles,
        }

    @advanced_mesh_settings.setter
    def advanced_mesh_settings(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.AdvancedMeshSettings
        if "layer_snap_tol" in values["LayerSnapTol"]:
            settings.LayerSnapTol = values["layer_snap_tol"]
        if "mesh_display_attributes" in values["MeshDisplayAttributes"]:
            settings.MeshDisplayAttributes = values["mesh_display_attributes"]
        if "replace3_d_triangles" in values["Replace3DTriangles"]:
            settings.Replace3DTriangles = values["replace3_d_triangles"]

    @property
    def curve_approx_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.CurveApproxSettings
        return {
            "arc_angle": settings.ArcAngle,
            "arc_to_chord_error": settings.ArcToChordError,
            "max_arc_points": settings.MaxArcPoints,
            "start_azimuth": settings.StartAzimuth,
            "use_arc_to_chord_error": settings.UseArcToChordError,
        }

    @curve_approx_settings.setter
    def curve_approx_settings(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.CurveApproxSettings
        if "arc_angle" in values:
            settings.ArcAngle = values["arc_angle"]
        if "arc_to_chord_error" in values:
            settings.ArcToChordError = values["arc_to_chord_error"]
        if "max_arc_points" in values:
            settings.MaxArcPoints = values["max_arc_points"]
        if "start_azimuth" in values:
            settings.StartAzimuth = values["start_azimuth"]
        if "use_arc_to_chord_error" in values:
            settings.UseArcToChordError = values["use_arc_to_chord_error"]

    @property
    def dcr_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.DCRSettings
        return {
            "conduction_max_passes": settings.ConductionMaxPasses,
            "conduction_min_converged_passes": settings.ConductionMinConvergedPasses,
            "Conduction_min_passes": settings.ConductionMinPasses,
            "conduction_per_error": settings.ConductionPerError,
            "conduction_per_refine": settings.ConductionPerRefine,
        }

    @dcr_settings.setter
    def dcr_settings(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.DCRSettings
        if "conduction_max_passes" in values:
            settings.ConductionMaxPasses = values["conduction_max_passes"]
        if "conduction_min_converged_passes" in values:
            settings.ConductionMinConvergedPasses = values["conduction_min_converged_passes"]
        if "Conduction_min_passes" in values:
            settings.ConductionMinPasses = values["Conduction_min_passes"]
        if "conduction_per_error" in values:
            settings.ConductionPerError = values["conduction_per_error"]
        if "conduction_per_refine" in values:
            settings.ConductionPerRefine = values["conduction_per_refine"]

    @property
    def hfss_port_settings(self):
        settings = self._edb_sim_setup_info.SimulationSettings.HFSSPortSettings
        return {
            "max_delta_z0": settings.MaxDeltaZ0,
            "max_triangles_wave_port": settings.MaxTrianglesWavePort,
            "min_triangles_wave_port": settings.MinTrianglesWavePort,
            "set_triangles_wave_port": settings.SetTrianglesWavePort,
        }

    @hfss_port_settings.setter
    def hfss_port_settings(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.HFSSPortSettings
        if "max_delta_z0" in values["MaxDeltaZ0"]:
            settings.MaxDeltaZ0 = values["max_delta_z0"]
        if "max_triangles_wave_port" in values["MaxTrianglesWavePort"]:
            settings.MaxTrianglesWavePort = values["max_triangles_wave_port"]
        if "min_triangles_wave_port" in values["MinTrianglesWavePort"]:
            settings.MinTrianglesWavePort = values["min_triangles_wave_port"]
        if "set_triangles_wave_port" in values["SetTrianglesWavePort"]:
            settings.SetTrianglesWavePort = values["set_triangles_wave_port"]

    @property
    def mesh_operations(self):
        settings = self._edb_sim_setup_info.SimulationSettings.MeshOperations
        mesh_operation_list = []
        for i in list(settings.MeshOperations):
            mesh_operation_list.append({
                "enabled": i.Enabled,
                "max_delta": i.MeshOpType,
                "mesh_region": i.MeshRegion,
                "name": i.Name,
                "nets_layers_list": i.NetsLayersList,
                "refine_inside": i.RefineInside,
            })
        return mesh_operation_list

    @mesh_operations.setter
    def mesh_operations(self, values):
        settings = self._edb_sim_setup_info.SimulationSettings.MeshOperations
        mesh_operation = self._edb.simsetupdata.MeshOperation()
        for i in values:
            mesh_operation.Enabled = i["enabled"]
            mesh_operation.MeshOpType = i["max_delta"]
            mesh_operation.MeshRegion = i["mesh_region"]
            mesh_operation.Name = i["name"]
            mesh_operation.NetsLayersList = i["nets_layers_list"]
            mesh_operation.RefineInside = i["refine_inside"]
            settings.AdaptiveFrequencyDataList.append(mesh_operation)

    def add_frequency_sweep(self, name=None):
        if name in self.frequency_sweeps:
            return False
        if not name:
            name = generate_unique_name("sweep")
        return FreqSweep(self, name)