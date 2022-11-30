from pyaedt.generic.general_methods import generate_unique_name


class MeshOperations(object):
    def __init__(self, parent, mesh_operation):
        self._parent = parent
        self.mesh_operation = mesh_operation

    @property
    def enabled(self):
        return self.mesh_operation.Enabled

    @property
    def mesh_operation_type(self):
        return self.mesh_operation.MeshOpType

    @property
    def mesh_region(self):
        return self.mesh_operation.MeshRegion

    @property
    def name(self):
        return self.mesh_operation.Name

    @property
    def nets_layers_list(self):
        return self.mesh_operation.NetsLayersList

    @property
    def refine_inside(self):
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


class FreqSweep(object):
    """Manages EDB methods for frequency sweep."""

    def __init__(self, hfss_sim_setup, frequency_sweep=None, name=None, edb_sweep_data=None):

        self._hfss_sim_setup = hfss_sim_setup

        if edb_sweep_data:
            self._edb_sweep_data = edb_sweep_data
            self._name = self._edb_sweep_data.Name
        else:
            if not name:
                self._name = generate_unique_name("sweep")
            else:
                self._name = name
            self._edb_sweep_data = self._hfss_sim_setup._edb.simsetupdata.SweepData(self._name)
            self.set_frequencies(frequency_sweep)

    def _update_sweep(self):
        """Update sweep."""
        self._hfss_sim_setup._edb_sim_setup_info.SweepDataList.Add(self._edb_sweep_data)
        self._hfss_sim_setup._update_setup()

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
    def settings(self):
        """Get settings."""
        settings = self._edb_sweep_data

        return {
            "name": settings.Name,
            "adaptive_sampling": settings.AdaptiveSampling,
            "adv_dc_extrapolation": settings.AdvDCExtrapolation,
            "auto_s_mat_only_solve": settings.AutoSMatOnlySolve,
            "enforce_causality": settings.EnforceCausality,
            "enforce_dc_and_causality": settings.EnforceDCAndCausality,
            "enforce_passivity": settings.EnforcePassivity,
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

    @settings.setter
    def settings(self, values):
        """Set settings."""
        edb_freq_sweep_type = self._edb_sweep_data.TFreqSweepType
        freq_sweep_type = {
            "kInterpolatingSweep": edb_freq_sweep_type.kInterpolatingSweep,
            "kDiscreteSweep": edb_freq_sweep_type.kDiscreteSweep,
            "kBroadbandFastSweep": edb_freq_sweep_type.kBroadbandFastSweep,
            "kNumSweepTypes": edb_freq_sweep_type.kNumSweepTypes,
        }
        settings = self._edb_sweep_data
        if "name" in values:
            settings.Name = values["name"]
        if "adaptive_sampling" in values:
            settings.AdaptiveSampling = values["adaptive_sampling"]
        if "adv_dc_extrapolation" in values:
            settings.AdvDCExtrapolation = values["adv_dc_extrapolation"]
        if "auto_s_mat_only_solve" in values:
            settings.AutoSMatOnlySolve = values["auto_s_mat_only_solve"]
        if "enforce_causality" in values:
            settings.EnforceCausality = values["enforce_causality"]
        if "enforce_dc_and_causality" in values:
            settings.EnforceDCAndCausality = values["enforce_dc_and_causality"]
        if "enforce_passivity" in values:
            settings.EnforcePassivity = values["enforce_passivity"]
        if "freq_sweep_type" in values:
            settings.FreqSweepType = freq_sweep_type[values["freq_sweep_type"]]
        if "interp_use_full_basis" in values:
            settings.InterpUseFullBasis = values["interp_use_full_basis"]
        if "interp_use_port_impedance" in values:
            settings.InterpUsePortImpedance = values["interp_use_port_impedance"]
        if "interp_use_prop_const" in values:
            settings.InterpUsePropConst = values["interp_use_prop_const"]
        if "interp_use_s_matrix" in values:
            settings.InterpUseSMatrix = values["interp_use_s_matrix"]
        if "max_solutions" in values:
            settings.MaxSolutions = values["max_solutions"]
        if "min_freq_s_mat_only_solve" in values:
            settings.MinFreqSMatOnlySolve = values["min_freq_s_mat_only_solve"]
        if "min_solved_freq" in values:
            settings.MinSolvedFreq = values["min_solved_freq"]
        if "passivity_tolerance" in values:
            settings.PassivityTolerance = values["passivity_tolerance"]
        if "relative_s_error" in values:
            settings.RelativeSError = values["relative_s_error"]
        if "save_fields" in values:
            settings.SaveFields = values["save_fields"]
        if "save_rad_fields_only" in values:
            settings.SaveRadFieldsOnly = values["save_rad_fields_only"]
        if "use_q3d_for_dc" in values:
            settings.UseQ3DForDC = values["use_q3d_for_dc"]

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
        settings = self._edb_sim_setup_info.AdaptiveSettings.AdaptiveFrequencyDataList
        settings.Clear()
        for mop in self.mesh_operations:
            settings.Add(mop.mesh_operation)
        self._edb_sim_setup = self._edb.edb.Utility.HFSSSimulationSetup(self._edb_sim_setup_info)

        if self._name in self._edb.simulation_setups.setups:
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
        """Get hfss prot settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.HFSSPortSettings
        return {
            "max_delta_z0": settings.MaxDeltaZ0,
            "max_triangles_wave_port": settings.MaxTrianglesWavePort,
            "min_triangles_wave_port": settings.MinTrianglesWavePort,
            "set_triangles_wave_port": settings.SetTrianglesWavePort,
        }

    @hfss_port_settings.setter
    def hfss_port_settings(self, values):
        """Set hfss port settings."""
        settings = self._edb_sim_setup_info.SimulationSettings.HFSSPortSettings
        if "max_delta_z0" in values:
            settings.MaxDeltaZ0 = values["max_delta_z0"]
        if "max_triangles_wave_port" in values:
            settings.MaxTrianglesWavePort = values["max_triangles_wave_port"]
        if "min_triangles_wave_port" in values:
            settings.MinTrianglesWavePort = values["min_triangles_wave_port"]
        if "set_triangles_wave_port" in values:
            settings.SetTrianglesWavePort = values["set_triangles_wave_port"]
        self._update_setup()

    @property
    def mesh_operations(self):
        """Get mesh operations."""
        if self._mesh_operations:
            return self._mesh_operations
        settings = self._edb_sim_setup_info.SimulationSettings.MeshOperations
        self._mesh_operations = {}
        for i in list(settings):
            self._mesh_operations[i.Name] = MeshOperations(self, i)
        return self._mesh_operations

    def add_mesh_operation(self, mesh_operation_type, mesh_region, net_layer_list, refine_inside, mesh_operation_name):
        """Add a new mesh operation to the setup.

        Parameters
        ----------
        mesh_operation_type
        mesh_region
        net_layer_list
        refine_inside
        mesh_operation_name

        Returns
        -------

        """
        mesh_operation = self._edb.simsetupdata.MeshOperation()
        mesh_operation.Enabled = True
        mesh_operation.MeshOpType = mesh_operation_type
        mesh_operation.MeshRegion = mesh_region
        mesh_operation.Name = refine_inside
        mesh_operation.NetsLayersList = net_layer_list
        mesh_operation.RefineInside = mesh_operation_name
        self.mesh_operations[mesh_operation_name] = MeshOperations(self, mesh_operation)
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
        pyaedt.edb_core.edb_data.simulation_setup_data.FreqSweep
        """
        if name in self.frequency_sweeps:
            return False
        if not name:
            name = generate_unique_name("sweep")
        return FreqSweep(self, frequency_sweep, name)
