from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import generate_unique_name


class EdbFrequencySweep(object):
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
        if value in [0, "kInterpolatingSweep"]:
            self._edb_sweep_data.FreqSweepType = edb_freq_sweep_type.kInterpolatingSweep
        elif value in [1, "kDiscreteSweep"]:
            self._edb_sweep_data.FreqSweepType = edb_freq_sweep_type.kDiscreteSweep
        elif value in [2, "kBroadbandFastSweep"]:
            self._edb_sweep_data.FreqSweepType = edb_freq_sweep_type.kBroadbandFastSweep
        elif value in [3, "kNumSweepTypes"]:
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
        return self.mesh_operation.Enabled

    @property
    def mesh_operation_type(self):
        return self.mesh_operation.MeshOpType

    @mesh_operation_type.setter
    def mesh_operation_type(self, value):
        self.mesh_operation.MeshOpType = self._mesh_op_mapping[value]

    @property
    def mesh_region(self):
        return self.mesh_operation.MeshRegion

    @property
    def name(self):
        return self.mesh_operation.Name

    @property
    def nets_layers_list(self):
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


class HfssSolverSettings(object):
    """Manages EDB methods for hfss solver settings."""

    def __init__(self, parent, hfss_solver_settings):
        self._parent = parent
        self._hfss_solver_settings = hfss_solver_settings

    @property
    def enhanced_low_freq_accuracy(self):
        return self._hfss_solver_settings.EnhancedLowFreqAccuracy

    @enhanced_low_freq_accuracy.setter
    def enhanced_low_freq_accuracy(self, value):
        self._hfss_solver_settings.EnhancedLowFreqAccuracy = value
        self._parent._update_setup()

    @property
    def order_basis(self):
        """Get order basis"""
        return self._hfss_solver_settings.OrderBasis

    @order_basis.setter
    def order_basis(self, value):
        """OrderBasis: 0=Mixed, 1=Zero, 2=1st order, 3=2nd order"""
        self._hfss_solver_settings.OrderBasis = value
        self._parent._update_setup()

    @property
    def relative_residual(self):
        return self._hfss_solver_settings.RelativeResidual

    @relative_residual.setter
    def relative_residual(self, value):
        self._hfss_solver_settings.RelativeResidual = value
        self._parent._update_setup()

    @property
    def solver_type(self):
        return self._hfss_solver_settings.SolverType

    @property
    def use_shell_elements(self):
        return self._hfss_solver_settings.UseShellElements

    @use_shell_elements.setter
    def use_shell_elements(self, value):
        self._hfss_solver_settings.UseShellElements = value
        self._parent._update_setup()


class AdaptiveFrequencyData(object):
    """Manages EDB methods for adaptive frequency data."""

    def __init__(self, adaptive_frequency_data):
        self._adaptive_frequency_data = adaptive_frequency_data

    @property
    def adaptive_frequency(self):
        return self._adaptive_frequency_data.AdaptiveFrequency

    @adaptive_frequency.setter
    def adaptive_frequency(self, value):
        self._adaptive_frequency_data.AdaptiveFrequency = value

    @property
    def max_delta(self):
        return self._adaptive_frequency_data.MaxDelta

    @max_delta.setter
    def max_delta(self, value):
        self._adaptive_frequency_data.MaxDelta = value

    @property
    def max_passes(self):
        return self._adaptive_frequency_data.MaxPasses

    @max_passes.setter
    def max_passes(self, value):
        self._adaptive_frequency_data.MaxPasses = value


class AdaptiveSettings(object):
    """Manages EDB methods for adaptive settings."""

    def __init__(self, parent, adaptive_settings):
        self._parent = parent
        self.adaptive_settings = adaptive_settings
        self._adapt_type_mapping = {
            "kSingle": self.adaptive_settings.AdaptType.kSingle,
            "kMultiFrequencies": self.adaptive_settings.AdaptType.kMultiFrequencies,
            "kBroadband": self.adaptive_settings.AdaptType.kBroadband,
            "kNumAdaptTypes": self.adaptive_settings.AdaptType.kNumAdaptTypes,
        }

    @property
    def adaptive_frequency_data_list(self):
        return [AdaptiveFrequencyData(i) for i in list(self.adaptive_settings.AdaptiveFrequencyDataList)]

    @property
    def adapt_type(self):
        return self.adaptive_settings.AdaptType.ToString()

    @adapt_type.setter
    def adapt_type(self, value):
        self.adaptive_settings.AdaptType = self._adapt_type_mapping[value]
        self._parent._update_setup()

    @property
    def basic(self):
        return self.adaptive_settings.Basic

    @basic.setter
    def basic(self, value):
        self.adaptive_settings.Basic = value
        self._parent._update_setup()

    @property
    def do_adaptive(self):
        return self.adaptive_settings.DoAdaptive

    @do_adaptive.setter
    def do_adaptive(self, value):
        self.adaptive_settings.DoAdaptive = value
        self._parent._update_setup()

    @property
    def max_refinement(self):
        return self.adaptive_settings.MaxRefinement

    @max_refinement.setter
    def max_refinement(self, value):
        self.adaptive_settings.MaxRefinement = value
        self._parent._update_setup()

    @property
    def max_refine_per_pass(self):
        return self.adaptive_settings.MaxRefinePerPass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value):
        self.adaptive_settings.MaxRefinePerPass = value
        self._parent._update_setup()

    @property
    def min_passes(self):
        return self.adaptive_settings.MinPasses

    @min_passes.setter
    def min_passes(self, value):
        self.adaptive_settings.MinPasses = value
        self._parent._update_setup()

    @property
    def save_fields(self):
        return self.adaptive_settings.SaveFields

    @save_fields.setter
    def save_fields(self, value):
        self.adaptive_settings.SaveFields = value
        self._parent._update_setup()

    @property
    def save_rad_field_only(self):
        return self.adaptive_settings.SaveRadFieldsOnly

    @save_rad_field_only.setter
    def save_rad_field_only(self, value):
        self.adaptive_settings.SaveRadFieldsOnly = value
        self._parent._update_setup()

    @property
    def use_convergence_matrix(self):
        return self.adaptive_settings.UseConvergenceMatrix

    @use_convergence_matrix.setter
    def use_convergence_matrix(self, value):
        self.adaptive_settings.UseConvergenceMatrix = value
        self._parent._update_setup()

    @property
    def use_max_refinement(self):
        return self.adaptive_settings.UseMaxRefinement

    @use_max_refinement.setter
    def use_max_refinement(self, value):
        self.adaptive_settings.UseMaxRefinement = value
        self._parent._update_setup()

    def add_adaptive_frequency_data(self, frequency, max_num_passes=10, max_delta_s="0.02"):
        adaptive_frequency_data = self._parent._edb.simsetupdata.AdaptiveFrequencyData()
        data = AdaptiveFrequencyData(adaptive_frequency_data)
        data.adaptive_frequency = frequency
        data.max_passes = max_num_passes
        data.max_delta = max_delta_s
        self.adaptive_settings.AdaptiveFrequencyDataList.Add(data._adaptive_frequency_data)
        return self._parent._update_setup()


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
            self.hfss_solver_settings.order_basis = 0

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
        self._name = self.name
        return self._edb._active_layout.GetCell().AddSimulationSetup(self._edb_sim_setup)

    @property
    def frequency_sweeps(self):
        """Get frequency sweep list."""
        sweep_data_list = {}
        for i in list(self._edb_sim_setup_info.SweepDataList):
            sweep_data_list[i.Name] = EdbFrequencySweep(self, None, i.Name, i)
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
        """Manages EDB methods for hfss solver settings."""
        hfss_solver_settings = self._edb_sim_setup_info.SimulationSettings.HFSSSolverSettings
        return HfssSolverSettings(self, hfss_solver_settings)

    @property
    def adaptive_settings(self):
        """Get adaptive settings."""
        adaptive_settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        return AdaptiveSettings(self, adaptive_settings)

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
        name,
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
        name

        Returns
        -------

        """
        mesh_operation = self._edb.simsetupdata.MeshOperation()
        mesh_operation.enabled = True
        mesh_operation.mesh_operation_type = mesh_operation_type
        mesh_operation.mesh_region = mesh_region
        mesh_operation.name = name
        mesh_operation.nets_layers_list = net_layer_list
        mesh_operation.refine_inside = refine_inside
        self.mesh_operations[name] = MeshOperation(self, mesh_operation)
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
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.EdbFrequencySweep
        """
        if name in self.frequency_sweeps:
            return False
        if not name:
            name = generate_unique_name("sweep")
        return EdbFrequencySweep(self, frequency_sweep, name)

    def set_solution_single_frequency(self, frequency="5GHz", max_num_passes=10, max_delta_s="0.02"):
        adaptive_settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        adaptive_settings.AdaptiveFrequencyDataList.Clear()
        adaptive_settings.adapt_type = "kSingle"
        return self.adaptive_settings.add_adaptive_frequency_data(frequency, max_num_passes, max_delta_s)

    def set_solution_multi_frequencies(self, frequencies=("5GHz", "10GHz"), max_num_passes=10, max_delta_s="0.02"):
        adaptive_settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        adaptive_settings.adapt_type = "kMultiFrequencies"
        adaptive_settings.AdaptiveFrequencyDataList.Clear()
        for i in frequencies:
            if not self.adaptive_settings.add_adaptive_frequency_data(i, max_num_passes, max_delta_s):
                return False
        return True

    def set_solution_broadband(
        self, low_frequency="5GHz", high_frequency="10GHz", max_num_passes=10, max_delta_s="0.02"
    ):
        adaptive_settings = self._edb_sim_setup_info.SimulationSettings.AdaptiveSettings
        adaptive_settings.adapt_type = "kBroadband"
        adaptive_settings.AdaptiveFrequencyDataList.Clear()
        if not self.adaptive_settings.add_adaptive_frequency_data(low_frequency, max_num_passes, max_delta_s):
            return False
        if not self.adaptive_settings.add_adaptive_frequency_data(high_frequency, max_num_passes, max_delta_s):
            return False
        return True
