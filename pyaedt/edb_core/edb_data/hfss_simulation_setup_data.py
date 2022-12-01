from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import generate_unique_name


class MeshOperation(object):
    def __init__(self, parent, mesh_operation):
        self._parent = parent
        self.mesh_operation = mesh_operation
        self._mesh_op_mapping = {
            "kMeshSetupBase": self.mesh_operation_type.kMeshSetupBase,
            "kMeshSetupLength": self.mesh_operation_type.kMeshSetupLength,
            "kMeshSetupSkinDepth": self.mesh_operation_type.kMeshSetupSkinDepth,
            "kNumMeshOpTypes": self.mesh_operation_type.kNumMeshOpTypes,
        }

    @property
    def enabled(self):
        """Check if Mesh Operation is Enabled.

        Returns
        -------
        bool
        """
        return self.mesh_operation.Enabled

    @property
    def mesh_operation_type(self):
        """Check if Mesh Operation Type.

        Returns
        -------
        str
        """
        return self.mesh_operation.MeshOpType.ToString()

    @mesh_operation_type.setter
    def mesh_operation_type(self, value):
        self.mesh_operation.MeshOpType = self._mesh_op_mapping[value]

    @property
    def mesh_region(self):
        """Mesh Region.

        Returns
        -------
        str
        """
        return self.mesh_operation.MeshRegion

    @property
    def name(self):
        """Name.

        Returns
        -------
        str
        """
        return self.mesh_operation.Name

    @property
    def nets_layers_list(self):
        """Tuple of layers and net names to which mesh operation is assigned.

        Returns
        -------
        tuple
        """
        return self.mesh_operation.NetsLayersList

    @nets_layers_list.setter
    def nets_layers_list(self, values):
        temp = []
        for net, layers in values.items():
            for l in layers:
                temp.append((net, l, True))
        self.mesh_operation.NetsLayersList = convert_py_list_to_net_list(temp)

    @property
    def refine_inside(self):
        """Refine Inside.

        Returns
        -------
        bool
        """
        return self.mesh_operation.RefineInside

    @enabled.setter
    def enabled(self, value):
        self.mesh_operation.Enabled = value
        self._parent._update_setup()

    @mesh_operation_type.setter
    def mesh_operation_type(self, value):
        self.mesh_operation.MeshOpType = value
        self._parent._update_setup()

    @mesh_region.setter
    def mesh_region(self, value):
        self.mesh_operation.MeshRegion = value
        self._parent._update_setup()

    @name.setter
    def name(self, value):
        self.mesh_operation.Name = value
        self._parent._update_setup()

    @nets_layers_list.setter
    def nets_layers_list(self, value):
        self.mesh_operation.NetsLayersList = value
        self._parent._update_setup()

    @refine_inside.setter
    def refine_inside(self, value):
        self.mesh_operation.RefineInside = value
        self._parent._update_setup()


class HfssPortSettings(object):
    """Manages EDB methods for hfss port settings."""

    def __init__(self, parent, hfss_port_settings):
        self._parent = parent
        self._hfss_port_settings = hfss_port_settings

    @property
    def max_delta_z0(self):
        return self._hfss_port_settings.MaxDeltaZ0

    @max_delta_z0.setter
    def max_delta_z0(self, value):
        self._hfss_port_settings.MaxDeltaZ0 = value
        self._parent._update_setup()

    @property
    def max_triangles_wave_port(self):
        return self._hfss_port_settings.MaxTrianglesWavePort

    @max_triangles_wave_port.setter
    def max_triangles_wave_port(self, value):
        self._hfss_port_settings.MaxTrianglesWavePort = value
        self._parent._update_setup()

    @property
    def min_triangles_wave_port(self):
        return self._hfss_port_settings.MinTrianglesWavePort

    @min_triangles_wave_port.setter
    def min_triangles_wave_port(self, value):
        self._hfss_port_settings.MinTrianglesWavePort = value
        self._parent._update_setup()

    @property
    def enable_set_triangles_wave_port(self):
        return self._hfss_port_settings.SetTrianglesWavePort

    @enable_set_triangles_wave_port.setter
    def enable_set_triangles_wave_port(self, value):
        self._hfss_port_settings.SetTrianglesWavePort = value
        self._parent._update_setup()


class FreqSweep(object):
    """Manages EDB methods for frequency sweep."""

    def __init__(self, sim_setup, frequency_sweep=None, name=None, edb_sweep_data=None):

        self._sim_setup = sim_setup

        if edb_sweep_data:
            self._edb_sweep_data = edb_sweep_data
            self._name = self._edb_sweep_data.Name
        else:
            if not name:
                self._name = generate_unique_name("sweep")
            else:
                self._name = name
            self._edb_sweep_data = self._sim_setup._edb.simsetupdata.SweepData(self._name)
            self.set_frequencies(frequency_sweep)

    def _update_sweep(self):
        """Update sweep."""
        self._sim_setup._edb_sim_setup_info.SweepDataList.Clear()
        for el in list(self._sim_setup.frequency_sweeps.values()):
            self._sim_setup._edb_sim_setup_info.SweepDataList.Add(el._edb_sweep_data)
        self._sim_setup._edb_sim_setup_info.SweepDataList.Add(self._edb_sweep_data)
        self._sim_setup._update_setup()

    @property
    def name(self):
        """Get name of this sweep."""
        return self._edb_sweep_data.Name

    @name.setter
    def name(self, value):
        """Set name of this sweep"""
        self._edb_sweep_data.Name = value
        self._update_sweep()

    @property
    def sweep_type(self):
        """Get sweep type."""
        return

    @property
    def frequencies(self):
        """Get list of frequencies points."""
        return list(self._edb_sweep_data.Frequencies)

    @property
    def adaptive_sampling(self):
        return self._edb_sweep_data.AdaptiveSampling

    @property
    def adv_dc_extrapolation(self):
        return self._edb_sweep_data.AdvDCExtrapolation

    @property
    def auto_s_mat_only_solve(self):
        return self._edb_sweep_data.AutoSMatOnlySolve

    @property
    def enforce_causality(self):
        return self._edb_sweep_data.EnforceCausality

    @property
    def enforce_dc_and_causality(self):
        return self._edb_sweep_data.EnforceDCAndCausality

    @property
    def enforce_passivity(self):
        return self._edb_sweep_data.EnforcePassivity

    @property
    def freq_sweep_type(self):
        return self._edb_sweep_data.FreqSweepType.ToString()

    @property
    def interp_use_full_basis(self):
        return self._edb_sweep_data.InterpUseFullBasis

    @property
    def interp_use_port_impedance(self):
        return self._edb_sweep_data.InterpUsePortImpedance

    @property
    def interp_use_prop_const(self):
        return self._edb_sweep_data.InterpUsePropConst

    @property
    def interp_use_s_matrix(self):
        return self._edb_sweep_data.InterpUseSMatrix

    @property
    def max_solutions(self):
        return self._edb_sweep_data.MaxSolutions

    @property
    def min_freq_s_mat_only_solve(self):
        return self._edb_sweep_data.MinFreqSMatOnlySolve

    @property
    def min_solved_freq(self):
        return self._edb_sweep_data.MinSolvedFreq

    @property
    def passivity_tolerance(self):
        return self._edb_sweep_data.PassivityTolerance

    @property
    def relative_s_error(self):
        return self._edb_sweep_data.RelativeSError

    @property
    def save_fields(self):
        return self._edb_sweep_data.SaveFields

    @property
    def save_rad_fields_only(self):
        return self._edb_sweep_data.SaveRadFieldsOnly

    @property
    def use_q3d_for_dc(self):
        return self._edb_sweep_data.UseQ3DForDC

    @adaptive_sampling.setter
    def adaptive_sampling(self, value):
        self._edb_sweep_data.AdaptiveSampling = value
        self._update_sweep()

    @adv_dc_extrapolation.setter
    def adv_dc_extrapolation(self, value):
        self._edb_sweep_data.AdvDCExtrapolation = value
        self._update_sweep()

    @auto_s_mat_only_solve.setter
    def auto_s_mat_only_solve(self, value):
        self._edb_sweep_data.AutoSMatOnlySolve = value
        self._update_sweep()

    @enforce_causality.setter
    def enforce_causality(self, value):
        self._edb_sweep_data.EnforceCausality = value
        self._update_sweep()

    @enforce_dc_and_causality.setter
    def enforce_dc_and_causality(self, value):
        self._edb_sweep_data.EnforceDCAndCausality = value
        self._update_sweep()

    @enforce_passivity.setter
    def enforce_passivity(self, value):
        self._edb_sweep_data.EnforcePassivity = value
        self._update_sweep()

    @freq_sweep_type.setter
    def freq_sweep_type(self, value):
        edb_freq_sweep_type = self._edb_sweep_data.TFreqSweepType
        if value == 0 or "kInterpolatingSweep":
            self._edb_sweep_data.FreqSweepType = edb_freq_sweep_type.kInterpolatingSweep
        elif value == 1 or "kDiscreteSweep":
            self._edb_sweep_data.FreqSweepType = edb_freq_sweep_type.kDiscreteSweep
        elif value == 2 or "kBroadbandFastSweep":
            self._edb_sweep_data.FreqSweepType = edb_freq_sweep_type.kBroadbandFastSweep
        elif value == 3 or "kNumSweepTypes":
            self._edb_sweep_data.FreqSweepType = edb_freq_sweep_type.kNumSweepTypes
        self._edb_sweep_data.FreqSweepType.ToString()

    @interp_use_full_basis.setter
    def interp_use_full_basis(self, value):
        self._edb_sweep_data.InterpUseFullBasis = value
        self._update_sweep()

    @interp_use_port_impedance.setter
    def interp_use_port_impedance(self, value):
        self._edb_sweep_data.InterpUsePortImpedance = value
        self._update_sweep()

    @interp_use_prop_const.setter
    def interp_use_prop_const(self, value):
        self._edb_sweep_data.InterpUsePropConst = value
        self._update_sweep()

    @interp_use_s_matrix.setter
    def interp_use_s_matrix(self, value):
        self._edb_sweep_data.InterpUseSMatrix = value
        self._update_sweep()

    @max_solutions.setter
    def max_solutions(self, value):
        self._edb_sweep_data.MaxSolutions = value
        self._update_sweep()

    @min_freq_s_mat_only_solve.setter
    def min_freq_s_mat_only_solve(self, value):
        self._edb_sweep_data.MinFreqSMatOnlySolve = value
        self._update_sweep()

    @min_solved_freq.setter
    def min_solved_freq(self, value):
        self._edb_sweep_data.MinSolvedFreq = value
        self._update_sweep()

    @passivity_tolerance.setter
    def passivity_tolerance(self, value):
        self._edb_sweep_data.PassivityTolerance = value
        self._update_sweep()

    @relative_s_error.setter
    def relative_s_error(self, value):
        self._edb_sweep_data.RelativeSError = value
        self._update_sweep()

    @save_fields.setter
    def save_fields(self, value):
        self._edb_sweep_data.SaveFields = value
        self._update_sweep()

    @save_rad_fields_only.setter
    def save_rad_fields_only(self, value):
        self._edb_sweep_data.SaveRadFieldsOnly = value
        self._update_sweep()

    @use_q3d_for_dc.setter
    def use_q3d_for_dc(self, value):
        self._edb_sweep_data.UseQ3DForDC = value
        self._update_sweep()

    def _set_frequencies(self, freq_sweep_string="Linear Step: 0GHz to 20GHz, step=0.05GHz"):
        self._edb_sweep_data.SetFrequencies(freq_sweep_string)
        self._update_sweep()

    def set_frequencies_linear_scale(self, start="0.1GHz", stop="20GHz", step="50MHz"):
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetFrequencies(start, stop, step)
        self._update_sweep()

    def set_frequencies_linear_count(self, start="1kHz", stop="0.1GHz", count=10):
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetFrequencies(start, stop, count)
        self._update_sweep()

    def set_frequencies_log_scale(self, start="1kHz", stop="0.1GHz", samples=10):
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetLogFrequencies(start, stop, samples)
        self._update_sweep()

    def set_frequencies(self, frequency_list=None):
        if not frequency_list:
            frequency_list = [
                ["linear count", "0", "1kHz", 1],
                ["log scale", "1kHz", "0.1GHz", 10],
                ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
            ]
        temp = []
        for i in frequency_list:
            if i[0] == "linear count":
                temp.extend(list(self._edb_sweep_data.SetFrequencies(i[1], i[2], i[3])))
            elif i[0] == "linear scale":
                temp.extend(list(self._edb_sweep_data.SetFrequencies(i[1], i[2], i[3])))
            elif i[0] == "log scale":
                temp.extend(list(self._edb_sweep_data.SetLogFrequencies(i[1], i[2], i[3])))
            else:
                return False
        for i in temp:
            self._edb_sweep_data.Frequencies.Add(i)
        self._update_sweep()


class HfssSimulationSetup(object):
    """Manages EDB methods for hfss simulation setup."""

    def __init__(self, edb, name=None, edb_hfss_sim_setup=None):
        self._edb = edb
        self._name = None
        self._mesh_operations = {}

        if edb_hfss_sim_setup:
            self._edb_sim_setup = edb_hfss_sim_setup
            self._edb_sim_setup_info = edb_hfss_sim_setup.GetSimSetupInfo()
            self._name = self._edb_sim_setup_info.Name
        else:
            self._edb_sim_setup_info = self._edb.simsetupdata.SimSetupInfo[
                self._edb.simsetupdata.HFSSSimulationSettings
            ]()
            if not name:
                self._edb_sim_setup_info.Name = generate_unique_name("hfss")
            else:
                self._edb_sim_setup_info.Name = name
            self._name = name
            self.hfss_solver_settings = {"OrderBasis": 0}

            self._edb_sim_setup = self._edb.edb.Utility.HFSSSimulationSetup(self._edb_sim_setup_info)
            self._update_setup()

    @property
    def edb_sim_setup_info(self):
        return self._edb_sim_setup_info

    def _update_setup(self):
        mesh_operations = self._edb_sim_setup_info.SimulationSettings.MeshOperations
        mesh_operations.Clear()
        for mop in self.mesh_operations.values():
            mesh_operations.Add(mop.mesh_operation)

        self._edb_sim_setup = self._edb.edb.Utility.HFSSSimulationSetup(self._edb_sim_setup_info)

        if self._name in self._edb.setups:
            self._edb._active_layout.GetCell().DeleteSimulationSetup(self._name)
        self._edb._active_layout.GetCell().AddSimulationSetup(self._edb_sim_setup)
        self._name = self.name

    @property
    def frequency_sweeps(self):
        """Get frequency sweep list."""
        sweep_data_list = {}
        for i in list(self._edb_sim_setup_info.SweepDataList):
            sweep_data_list[i.Name] = FreqSweep(self, None, i.Name, i)
        return sweep_data_list

    @property
    def name(self):
        """Get name of this setup."""
        return self._edb_sim_setup_info.Name

    @name.setter
    def name(self, value):
        """Set name of this setup."""
        self._edb_sim_setup_info.Name = value
        self._update_setup()
        self._name = value

    @property
    def solver_slider_type(self):
        """Get solver slider type."""
        return self._edb_sim_setup_info.SimulationSettings.TSolveSliderType

    @solver_slider_type.setter
    def solver_slider_type(self, value):
        """Set solver slider type."""
        self._edb_sim_setup_info.SimulationSettings.TSolveSliderType = value
        self._update_setup()

    @property
    def is_auto_setup(self):
        """Check if auto setup is enabled."""
        return self._edb_sim_setup_info.SimulationSettings.IsAutoSetup

    @is_auto_setup.setter
    def is_auto_setup(self, value):
        """Set auto setup."""
        self._edb_sim_setup_info.SimulationSettings.IsAutoSetup = value
        self._update_setup()

    @property
    def setup_type(self):
        """Get setup type."""
        return self._edb_sim_setup_info.SimulationSettings.SetupType

    @property
    def hfss_solver_settings(self):
        """Get hfss solver settings.
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
            "use_shell_elements": settings.UseShellElements,
        }

    @hfss_solver_settings.setter
    def hfss_solver_settings(self, values):
        """Set hfss solver settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.HFSSSolverSettings
        if "enhanced_low_freq_accuracy" in values:
            settings.EnhancedLowFreqAccuracy = values["enhanced_low_freq_accuracy"]
        if "order_basis" in values:
            settings.OrderBasis = values["order_basis"]
        if "relative_residual" in values:
            settings.RelativeResidual = values["relative_residual"]
        if "use_shell_elements" in values:
            settings.UseShellElements = values["use_shell_elements"]
        self._update_setup()

    @property
    def adaptive_settings(self):
        """Get adaptive settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        adaptive_freq_list = []
        for i in list(settings.AdaptiveFrequencyDataList):
            adaptive_freq_list.append(
                {"adaptive_frequency": i.AdaptiveFrequency, "max_delta": i.MaxDelta, "max_passes": i.MaxPasses}
            )

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
    def adaptive_settings(self, values):
        """Set adaptive settings"""
        edb_adapt_type = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings.AdaptType
        adapt_type = {
            "kSingle": edb_adapt_type.kSingle,
            "kMultiFrequencies": edb_adapt_type.kMultiFrequencies,
            "kBroadband": edb_adapt_type.kBroadband,
            "kNumAdaptTypes": edb_adapt_type.kNumAdaptTypes,
        }
        settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        if "adaptive_frequency_data_list" in values:
            settings.AdaptiveFrequencyDataList.Clear()
            adaptive_frequency_data = self._edb.simsetupdata.AdaptiveFrequencyData()
            for i in values["adaptive_frequency_data_list"]:
                adaptive_frequency_data.AdaptiveFrequency = i["adaptive_frequency"]
                adaptive_frequency_data.MaxDelta = i["max_delta"]
                adaptive_frequency_data.MaxPasses = i["max_passes"]
                settings.AdaptiveFrequencyDataList.Add(adaptive_frequency_data)
        if "adapt_type" in values:
            settings.AdaptType = adapt_type[values["adapt_type"]]
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
        self._update_setup()

    @property
    def defeature_settings(self):
        """Get defeature settings."""
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
        """Set defeature settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.DefeatureSettings
        if "defeature_abs_length" in values:
            settings.DefeatureAbsLength = values["defeature_abs_length"]
        if "defeature_ratio" in values:
            settings.DefeatureRatio = values["defeature_ratio"]
        if "healing_option" in values:
            settings.HealingOption = values["healing_option"]
        if "model_type" in values:
            settings.ModelType = values["model_type"]
        if "remove_floating_geometry" in values:
            settings.RemoveFloatingGeometry = values["remove_floating_geometry"]
        if "small_void_area" in values:
            settings.SmallVoidArea = values["small_void_area"]
        if "union_polygons" in values:
            settings.UnionPolygons = values["union_polygons"]
        if "use_defeature" in values:
            settings.UseDefeature = values["use_defeature"]
        if "use_defeature_abs_length" in values:
            settings.UseDefeatureAbsLength = values["use_defeature_abs_length"]
        self._update_setup()

    @property
    def via_settings(self):
        """Get via settings."""
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
        """Set via settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.ViaSettings
        if "t25_d_via_style" in values:
            settings.T25DViaStyle = values["t25_d_via_style"]
        if "via_density" in values:
            settings.ViaDensity = values["via_density"]
        if "via_material" in values:
            settings.ViaMaterial = values["via_material"]
        if "via_num_sides" in values:
            settings.ViaNumSides = values["via_num_sides"]
        if "via_style" in values:
            settings.ViaStyle = values["via_style"]
        self._update_setup()

    @property
    def advanced_mesh_settings(self):
        """Get advanced mesh settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.AdvancedMeshSettings
        return {
            "layer_snap_tol": settings.LayerSnapTol,
            "mesh_display_attributes": settings.MeshDisplayAttributes,
            "replace3_d_triangles": settings.Replace3DTriangles,
        }

    @advanced_mesh_settings.setter
    def advanced_mesh_settings(self, values):
        """Set advanced mesh settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.AdvancedMeshSettings
        if "layer_snap_tol" in values:
            settings.LayerSnapTol = values["layer_snap_tol"]
        if "mesh_display_attributes" in values:
            settings.MeshDisplayAttributes = values["mesh_display_attributes"]
        if "replace3_d_triangles" in values:
            settings.Replace3DTriangles = values["replace3_d_triangles"]
        self._update_setup()

    @property
    def curve_approx_settings(self):
        """Get curve approx settings."""
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
        """Set curve approx settings."""
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
        self._update_setup()

    @property
    def dcr_settings(self):
        """Get dcr settings."""
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
        """Set dcr settings."""
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
        self._update_setup()

    @property
    def hfss_port_settings(self):
        """Hfss prot settings."""
        hfss_port_settings = self._edb_sim_setup_info.SimulationSettings.HFSSPortSettings
        return HfssPortSettings(self, hfss_port_settings)

    @property
    def mesh_operations(self):
        """Get mesh operations."""
        if self._mesh_operations:
            return self._mesh_operations
        settings = self._edb_sim_setup_info.SimulationSettings.MeshOperations
        self._mesh_operations = {}
        for i in list(settings):
            self._mesh_operations[i.Name] = MeshOperation(self, i)
        return self._mesh_operations

    def add_mesh_operation(
        self,
        mesh_operation_name,
        net_layer_list,
        mesh_operation_type="kMeshSetupLength",
        refine_inside=False,
        mesh_region=None,
    ):
        """Add a new mesh operation to the setup.

        Parameters
        ----------
        mesh_operation_type
        mesh_region
        net_layer_list
            {"A0_N": ["TOP", "PWR"]}
        refine_inside
        mesh_operation_name

        Returns
        -------

        """
        mesh_operation = self._edb.simsetupdata.MeshOperation()
        mesh_operation.enabled = True
        mesh_operation.mesh_operation_type = mesh_operation_type
        mesh_operation.mesh_region = mesh_region
        mesh_operation.name = mesh_operation_name
        mesh_operation.nets_layers_list = net_layer_list
        mesh_operation.refine_inside = refine_inside
        self.mesh_operations[mesh_operation_name] = MeshOperation(self, mesh_operation)
        self._update_setup()

    def add_frequency_sweep(self, name=None, frequency_sweep=None):
        """Add frequency sweep.

        Parameters
        ----------
        name: str, optional
            Name of the frequency sweep.
        frequency_sweep: list, optional

        Returns
        ----------
        pyaedt.edb_core.edb_data.hfss_simulation_setup_data.FreqSweep
        """
        if name in self.frequency_sweeps:
            return False
        if not name:
            name = generate_unique_name("sweep")
        return FreqSweep(self, frequency_sweep, name)
