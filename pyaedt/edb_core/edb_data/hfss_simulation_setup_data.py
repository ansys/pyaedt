from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler


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

    @pyaedt_function_handler()
    def _update_sweep(self):
        """Update sweep."""
        self._sim_setup._edb_sim_setup_info.SweepDataList.Clear()
        for el in list(self._sim_setup.frequency_sweeps.values()):
            self._sim_setup._edb_sim_setup_info.SweepDataList.Add(el._edb_sweep_data)
        self._sim_setup._edb_sim_setup_info.SweepDataList.Add(self._edb_sweep_data)
        return self._sim_setup._update_setup()

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
        """Use adaptive sampling.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.AdaptiveSampling

    @property
    def adv_dc_extrapolation(self):
        """Turn on advanced DC Extrapolation.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.AdvDCExtrapolation

    @property
    def auto_s_mat_only_solve(self):
        """Auto/Manual SMatrix only solve.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.AutoSMatOnlySolve

    @property
    def enforce_causality(self):
        """Enforce causality during interpolating sweep.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.EnforceCausality

    @property
    def enforce_dc_and_causality(self):
        """Enforce DC point and causality.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.EnforceDCAndCausality

    @property
    def enforce_passivity(self):
        """Enforce passivity during interpolating sweep.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.EnforcePassivity

    @property
    def freq_sweep_type(self):
        """Sweep type (interpolation, discrete or Broadband Fast).

        Returns
        -------
        str
        """
        return self._edb_sweep_data.FreqSweepType.ToString()

    @property
    def interp_use_full_basis(self):
        """Use Full basis.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.InterpUseFullBasis

    @property
    def interp_use_port_impedance(self):
        """Use Port impedance.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.InterpUsePortImpedance

    @property
    def interp_use_prop_const(self):
        """Use propagation constants.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.InterpUsePropConst

    @property
    def interp_use_s_matrix(self):
        """Use S matrix.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.InterpUseSMatrix

    @property
    def max_solutions(self):
        """Max solutions.

        Returns
        -------
        int
        """
        return self._edb_sweep_data.MaxSolutions

    @property
    def min_freq_s_mat_only_solve(self):
        """Minimum frequency SMatrix only solve.

        Returns
        -------
        str
        """
        return self._edb_sweep_data.MinFreqSMatOnlySolve

    @property
    def min_solved_freq(self):
        """Minimum solved frequency.

        Returns
        -------
        str
        """
        return self._edb_sweep_data.MinSolvedFreq

    @property
    def passivity_tolerance(self):
        """Tolerance for passivity enforcement.

        Returns
        -------
        float
        """
        return self._edb_sweep_data.PassivityTolerance

    @property
    def relative_s_error(self):
        """Specify S-parameter error tolerance for interpolating sweep.

        Returns
        -------
        float
        """
        return self._edb_sweep_data.RelativeSError

    @property
    def save_fields(self):
        """Enable or disable extraction of surface current data .

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.SaveFields

    @property
    def save_rad_fields_only(self):
        """Enable or disable save radiated fields only.

        Returns
        -------
        bool
        """
        return self._edb_sweep_data.SaveRadFieldsOnly

    @property
    def use_q3d_for_dc(self):
        """Enable Q3D solver for DC point extraction .

        Returns
        -------
        float
        """
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

    @pyaedt_function_handler()
    def _set_frequencies(self, freq_sweep_string="Linear Step: 0GHz to 20GHz, step=0.05GHz"):
        self._edb_sweep_data.SetFrequencies(freq_sweep_string)
        self._update_sweep()

    @pyaedt_function_handler()
    def set_frequencies_linear_scale(self, start="0.1GHz", stop="20GHz", step="50MHz"):
        """Set a linear scale frequency sweep.

        Parameters
        ----------
        start : str, float
            Start frequency.
        stop : str, float
            Stop frequency.
        step : str, float
            Step frequency

        Returns
        -------
        bool
        """
        start = self._sim_setup._edb.arg_to_dim(start, "Hz")
        stop = self._sim_setup._edb.arg_to_dim(stop, "Hz")
        step = self._sim_setup._edb.arg_to_dim(step, "Hz")
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetFrequencies(start, stop, step)
        return self._update_sweep()

    @pyaedt_function_handler()
    def set_frequencies_linear_count(self, start="1kHz", stop="0.1GHz", count=10):
        """Set a linear count frequency sweep.

        Parameters
        ----------
        start : str, float
            Start frequency.
        stop : str, float
            Stop frequency.
        count : int
            Step frequency

        Returns
        -------
        bool
        """
        start = self._sim_setup._edb.arg_to_dim(start, "Hz")
        stop = self._sim_setup._edb.arg_to_dim(stop, "Hz")
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetFrequencies(start, stop, count)
        return self._update_sweep()

    @pyaedt_function_handler()
    def set_frequencies_log_scale(self, start="1kHz", stop="0.1GHz", samples=10):
        """Set a log count frequency sweep.

        Parameters
        ----------
        start : str, float
            Start frequency.
        stop : str, float
            Stop frequency.
        samples : int
            Step frequency

        Returns
        -------
        bool
        """
        start = self._sim_setup._edb.arg_to_dim(start, "Hz")
        stop = self._sim_setup._edb.arg_to_dim(stop, "Hz")
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetLogFrequencies(start, stop, samples)
        return self._update_sweep()

    @pyaedt_function_handler()
    def set_frequencies(self, frequency_list=None):
        """Set frequency list to the sweep frequencies.

        Parameters
        ----------
        frequency_list : list
            List of lists of 4 elements. Each list has to contain:
              1- freq type ("linear count", "log scale" or "linear scale")
              2- start frequency
              3- stop frequency
              3- step frequency or count

        Returns
        -------
        bool
        """
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
        return self._update_sweep()


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
        """Enabled.

        Returns
        -------
        bool
        """
        return self.mesh_operation.Enabled

    @property
    def mesh_operation_type(self):
        """Mesh operation type.

        Returns
        -------
        int
        """
        return self.mesh_operation.MeshOpType

    @mesh_operation_type.setter
    def mesh_operation_type(self, value):
        self.mesh_operation.MeshOpType = self._mesh_op_mapping[value]

    @property
    def mesh_region(self):
        """Mesh region object.

        Returns
        -------
        object
        """
        return self.mesh_operation.MeshRegion

    @property
    def name(self):
        """Mesh operation Name.

        Returns
        -------
        str
        """
        return self.mesh_operation.Name

    @property
    def nets_layers_list(self):
        """List of nets and layers.

        Returns
        -------
        list
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
        """Refine inside objects.

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

    def __init__(self, parent):
        self._parent = parent

    @property
    def _hfss_port_settings(self):
        return self._parent._edb_sim_setup_info.SimulationSettings.HFSSPortSettings

    @property
    def max_delta_z0(self):
        """Maximum change to Z0 in successive passes.

        Returns
        -------
        float
        """
        return self._hfss_port_settings.MaxDeltaZ0

    @max_delta_z0.setter
    def max_delta_z0(self, value):
        self._hfss_port_settings.MaxDeltaZ0 = value
        self._parent._update_setup()

    @property
    def max_triangles_wave_port(self):
        """Max number of triangles allowed for wave ports.

        Returns
        -------
        int
        """
        return self._hfss_port_settings.MaxTrianglesWavePort

    @max_triangles_wave_port.setter
    def max_triangles_wave_port(self, value):
        self._hfss_port_settings.MaxTrianglesWavePort = value
        self._parent._update_setup()

    @property
    def min_triangles_wave_port(self):
        """Minimum number of triangles allowed for wave ports.

        Returns
        -------
        int
        """
        return self._hfss_port_settings.MinTrianglesWavePort

    @min_triangles_wave_port.setter
    def min_triangles_wave_port(self, value):
        self._hfss_port_settings.MinTrianglesWavePort = value
        self._parent._update_setup()

    @property
    def enable_set_triangles_wave_port(self):
        """Enable setting of min/max mesh limits for wave ports.

        Returns
        -------
        bool
        """
        return self._hfss_port_settings.SetTrianglesWavePort

    @enable_set_triangles_wave_port.setter
    def enable_set_triangles_wave_port(self, value):
        self._hfss_port_settings.SetTrianglesWavePort = value
        self._parent._update_setup()


class HfssSolverSettings(object):
    """Manages EDB methods for hfss solver settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _hfss_solver_settings(self):
        return self._parent._edb_sim_setup_info.SimulationSettings.HFSSSolverSettings

    @property
    def enhanced_low_freq_accuracy(self):
        """Enable legacy low frequency sampling.

        Returns
        -------
        float
        """
        return self._hfss_solver_settings.EnhancedLowFreqAccuracy

    @enhanced_low_freq_accuracy.setter
    def enhanced_low_freq_accuracy(self, value):
        self._hfss_solver_settings.EnhancedLowFreqAccuracy = value
        self._parent._update_setup()

    @property
    def order_basis(self):
        """Get or Specify order of the basis functions for HFSS : 0=Mixed, 1=Zero, 2=1st order, 3=2nd order."""
        return self._hfss_solver_settings.OrderBasis

    @order_basis.setter
    def order_basis(self, value):
        self._hfss_solver_settings.OrderBasis = value
        self._parent._update_setup()

    @property
    def relative_residual(self):
        """Specify the residual used by the iterative solver.

        Returns
        -------
        float
        """
        return self._hfss_solver_settings.RelativeResidual

    @relative_residual.setter
    def relative_residual(self, value):
        self._hfss_solver_settings.RelativeResidual = value
        self._parent._update_setup()

    @property
    def solver_type(self):
        """Get solver type to use (Direct/Iterative/Auto) for HFSS.

        Returns
        -------
        int
        """
        return self._hfss_solver_settings.SolverType

    @property
    def use_shell_elements(self):
        """Enable use of Shell Elements.

        Returns
        -------
        bool
        """
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
        """Adaptive frequency for this setup.

        Returns
        -------
        str
        """
        return self._adaptive_frequency_data.AdaptiveFrequency

    @adaptive_frequency.setter
    def adaptive_frequency(self, value):
        self._adaptive_frequency_data.AdaptiveFrequency = value

    @property
    def max_delta(self):
        """The maximum change of S-parameters between two consecutive passes, which serves as a stopping criteria.

        Returns
        -------
        str
        """
        return self._adaptive_frequency_data.MaxDelta

    @max_delta.setter
    def max_delta(self, value):
        self._adaptive_frequency_data.MaxDelta = str(value)

    @property
    def max_passes(self):
        """The maximum allowed number of mesh refinement cycles.

        Returns
        -------
        int
        """
        return self._adaptive_frequency_data.MaxPasses

    @max_passes.setter
    def max_passes(self, value):
        self._adaptive_frequency_data.MaxPasses = value


class AdaptiveSettings(object):
    """Manages EDB methods for adaptive settings."""

    def __init__(self, parent):
        self._parent = parent
        self._adapt_type_mapping = {
            "kSingle": self.adaptive_settings.AdaptType.kSingle,
            "kMultiFrequencies": self.adaptive_settings.AdaptType.kMultiFrequencies,
            "kBroadband": self.adaptive_settings.AdaptType.kBroadband,
            "kNumAdaptTypes": self.adaptive_settings.AdaptType.kNumAdaptTypes,
        }

    @property
    def adaptive_settings(self):
        """Adaptive Edb settings.

        Returns
        -------
        object
        """
        return self._parent._edb_sim_setup_info.SimulationSettings.AdaptiveSettings

    @property
    def adaptive_frequency_data_list(self):
        """List of all adaptive Frequency Data.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.AdaptiveFrequencyData`
        """
        return [AdaptiveFrequencyData(i) for i in list(self.adaptive_settings.AdaptiveFrequencyDataList)]

    @property
    def adapt_type(self):
        """Adaptive type.

        Returns
        -------
        str
        """
        return self.adaptive_settings.AdaptType.ToString()

    @adapt_type.setter
    def adapt_type(self, value):
        self.adaptive_settings.AdaptType = self._adapt_type_mapping[value]
        self._parent._update_setup()

    @property
    def basic(self):
        """Basic setting.

        Returns
        -------

        """
        return self.adaptive_settings.Basic

    @basic.setter
    def basic(self, value):
        self.adaptive_settings.Basic = value
        self._parent._update_setup()

    @property
    def do_adaptive(self):
        """Do adpative..

        Returns
        -------
        bool
        """
        return self.adaptive_settings.DoAdaptive

    @property
    def max_refinement(self):
        """Maximum refinement.

        Returns
        -------
        str
        """
        return self.adaptive_settings.MaxRefinement

    @max_refinement.setter
    def max_refinement(self, value):
        self.adaptive_settings.MaxRefinement = value
        self._parent._update_setup()

    @property
    def max_refine_per_pass(self):
        """Maximum refinement per pass.

        Returns
        -------
        str
        """
        return self.adaptive_settings.MaxRefinePerPass

    @max_refine_per_pass.setter
    def max_refine_per_pass(self, value):
        self.adaptive_settings.MaxRefinePerPass = value
        self._parent._update_setup()

    @property
    def min_passes(self):
        """Minimum passes.

        Returns
        -------
        int
        """
        return self.adaptive_settings.MinPasses

    @min_passes.setter
    def min_passes(self, value):
        self.adaptive_settings.MinPasses = value
        self._parent._update_setup()

    @property
    def save_fields(self):
        """Save Fields.

        Returns
        -------
        bool
        """
        return self.adaptive_settings.SaveFields

    @save_fields.setter
    def save_fields(self, value):
        self.adaptive_settings.SaveFields = value
        self._parent._update_setup()

    @property
    def save_rad_field_only(self):
        """Save radiated fields only.

        Returns
        -------
        bool
        """
        return self.adaptive_settings.SaveRadFieldsOnly

    @save_rad_field_only.setter
    def save_rad_field_only(self, value):
        self.adaptive_settings.SaveRadFieldsOnly = value
        self._parent._update_setup()

    @property
    def use_convergence_matrix(self):
        """Use convergence matrix.

        Returns
        -------
        bool
        """
        return self.adaptive_settings.UseConvergenceMatrix

    @use_convergence_matrix.setter
    def use_convergence_matrix(self, value):
        self.adaptive_settings.UseConvergenceMatrix = value
        self._parent._update_setup()

    @property
    def use_max_refinement(self):
        """Use Max refinement.

        Returns
        -------
        bool
        """
        return self.adaptive_settings.UseMaxRefinement

    @use_max_refinement.setter
    def use_max_refinement(self, value):
        self.adaptive_settings.UseMaxRefinement = value
        self._parent._update_setup()

    @pyaedt_function_handler()
    def add_adaptive_frequency_data(self, frequency, max_num_passes=10, max_delta_s=0.02):
        """Add a Frequency Data setup.

        Parameters
        ----------
        frequency : str, float
            Frequency with units or float frequency (in Hz).
        max_num_passes : int, optional
            Maximum number of passes. Default is ``10``.
        max_delta_s : float, optional
            Maximum Delta S. Default is ``0.02``.

        Returns
        -------
        bool
        """
        adaptive_frequency_data = self._parent._edb.simsetupdata.AdaptiveFrequencyData()
        data = AdaptiveFrequencyData(adaptive_frequency_data)
        data.adaptive_frequency = self._parent._edb.arg_with_dim(frequency, "Hz")
        data.max_passes = max_num_passes
        data.max_delta = str(max_delta_s)
        self.adaptive_settings.AdaptiveFrequencyDataList.Add(data._adaptive_frequency_data)
        return self._parent._update_setup()


class DefeatureSettings(object):
    """Manages EDB methods for defeature settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _defeature_settings(self):
        return self._parent._edb_sim_setup_info.SimulationSettings.DefeatureSettings

    @property
    def defeature_abs_length(self):
        """Defeature absolute length.

        Returns
        -------
        str
        """
        return self._defeature_settings.DefeatureAbsLength

    @defeature_abs_length.setter
    def defeature_abs_length(self, value):
        self._defeature_settings.DefeatureAbsLength = value
        self._parent._update_setup()

    @property
    def defeature_ratio(self):
        """Defeature ratio.

        Returns
        -------
        float
        """
        return self._defeature_settings.DefeatureRatio

    @defeature_ratio.setter
    def defeature_ratio(self, value):
        self._defeature_settings.DefeatureRatio = value
        self._parent._update_setup()

    @property
    def healing_option(self):
        """Healing option.

        Returns
        -------

        """
        return self._defeature_settings.HealingOption

    @healing_option.setter
    def healing_option(self, value):
        self._defeature_settings.HealingOption = value
        self._parent._update_setup()

    @property
    def model_type(self):
        """Model type.

        Returns
        -------
        int
        """
        return self._defeature_settings.ModelType

    @model_type.setter
    def model_type(self, value):
        """Model type (General 0 or IC 1)."""
        self._defeature_settings.ModelType = value
        self._parent._update_setup()

    @property
    def remove_floating_geometry(self):
        """Remove floating geometries.

        Returns
        -------
        bool
        """
        return self._defeature_settings.RemoveFloatingGeometry

    @remove_floating_geometry.setter
    def remove_floating_geometry(self, value):
        self._defeature_settings.RemoveFloatingGeometry = value
        self._parent._update_setup()

    @property
    def small_void_area(self):
        """Small voids to remove area.

        Returns
        -------
        str
        """
        return self._defeature_settings.SmallVoidArea

    @small_void_area.setter
    def small_void_area(self, value):
        self._defeature_settings.SmallVoidArea = value
        self._parent._update_setup()

    @property
    def union_polygons(self):
        """Union Polygons.

        Returns
        -------

        """
        return self._defeature_settings.UnionPolygons

    @union_polygons.setter
    def union_polygons(self, value):
        self._defeature_settings.UnionPolygons = value
        self._parent._update_setup()

    @property
    def use_defeature(self):
        """Use Defeature.

        Returns
        -------
        bool
        """
        return self._defeature_settings.UseDefeature

    @use_defeature.setter
    def use_defeature(self, value):
        self._defeature_settings.UseDefeature = value
        self._parent._update_setup()

    @property
    def use_defeature_abs_length(self):
        """Defeature absolute length.

        Returns
        -------
        str
        """
        return self._defeature_settings.UseDefeatureAbsLength

    @use_defeature_abs_length.setter
    def use_defeature_abs_length(self, value):
        self._defeature_settings.UseDefeatureAbsLength = value
        self._parent._update_setup()


class ViaSettings(object):
    """Manages EDB methods for via settings."""

    def __init__(
        self,
        parent,
    ):
        self._parent = parent
        self._via_style_mapping = {
            "k25DViaWirebond": self._via_settings.T25DViaStyle.k25DViaWirebond,
            "k25DViaRibbon": self._via_settings.T25DViaStyle.k25DViaRibbon,
            "k25DViaMesh": self._via_settings.T25DViaStyle.k25DViaMesh,
            "k25DViaField": self._via_settings.T25DViaStyle.k25DViaField,
            "kNum25DViaStyle": self._via_settings.T25DViaStyle.kNum25DViaStyle,
        }

    @property
    def _via_settings(self):
        return self._parent._edb_sim_setup_info.SimulationSettings.ViaSettings

    @property
    def via_density(self):
        """Via density.

        Returns
        -------
        float
        """
        return self._via_settings.ViaDensity

    @via_density.setter
    def via_density(self, value):
        self._via_settings.ViaDensity = value
        self._parent._update_setup()

    @property
    def via_material(self):
        """Via material.

        Returns
        -------
        str
        """
        return self._via_settings.ViaMaterial

    @via_material.setter
    def via_material(self, value):
        self._via_settings.ViaMaterial = value
        self._parent._update_setup()

    @property
    def via_num_sides(self):
        """Via number of sides.

        Returns
        -------
        int
        """
        return self._via_settings.ViaNumSides

    @via_num_sides.setter
    def via_num_sides(self, value):
        self._via_settings.ViaNumSides = value
        self._parent._update_setup()

    @property
    def via_style(self):
        """Via style.

        Returns
        -------
        str
        """
        return self._via_settings.ViaStyle.ToString()

    @via_style.setter
    def via_style(self, value):
        self._via_settings.ViaStyle = self._via_style_mapping[value]
        self._parent._update_setup()


class AdvancedMeshSettings(object):
    """Manages EDB methods for advanced mesh settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _advanced_mesh_settings(self):
        return self._parent._edb_sim_setup_info.SimulationSettings.AdvancedMeshSettings

    @property
    def layer_snap_tol(self):
        """Layer snap tool.

        Returns
        -------

        """
        return self._advanced_mesh_settings.LayerSnapTol

    @layer_snap_tol.setter
    def layer_snap_tol(self, value):
        self._advanced_mesh_settings.LayerSnapTol = value
        self._parent._update_setup()

    @property
    def mesh_display_attributes(self):
        """Mesh display attributes.

        Returns
        -------

        """
        return self._advanced_mesh_settings.MeshDisplayAttributes

    @mesh_display_attributes.setter
    def mesh_display_attributes(self, value):
        self._advanced_mesh_settings.MeshDisplayAttributes = value
        self._parent._update_setup()

    @property
    def replace_3d_triangles(self):
        """Replace 3d triangles.

        Returns
        -------
        bool
        """
        return self._advanced_mesh_settings.Replace3DTriangles

    @replace_3d_triangles.setter
    def replace_3d_triangles(self, value):
        self._advanced_mesh_settings.Replace3DTriangles = value
        self._parent._update_setup()


class CurveApproxSettings(object):
    """Manages EDB methods for curve approx settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _curve_approx_settings(self):
        return self._parent._edb_sim_setup_info.SimulationSettings.CurveApproxSettings

    @property
    def arc_angle(self):
        return self._curve_approx_settings.ArcAngle

    @arc_angle.setter
    def arc_angle(self, value):
        self._curve_approx_settings.ArcAngle = value
        self._parent._update_setup()

    @property
    def arc_to_chord_error(self):
        return self._curve_approx_settings.ArcToChordError

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value):
        self._curve_approx_settings.ArcToChordError = value
        self._parent._update_setup()

    @property
    def max_arc_points(self):
        return self._curve_approx_settings.MaxArcPoints

    @max_arc_points.setter
    def max_arc_points(self, value):
        self._curve_approx_settings.MaxArcPoints = value
        self._parent._update_setup()

    @property
    def start_azimuth(self):
        return self._curve_approx_settings.StartAzimuth

    @start_azimuth.setter
    def start_azimuth(self, value):
        self._curve_approx_settings.StartAzimuth = value
        self._parent._update_setup()

    @property
    def use_arc_to_chord_error(self):
        return self._curve_approx_settings.UseArcToChordError

    @use_arc_to_chord_error.setter
    def use_arc_to_chord_error(self, value):
        self._curve_approx_settings.UseArcToChordError = value
        self._parent._update_setup()


class DcrSettings(object):
    """Manages EDB methods for dcr settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def _dcr_settings(self):
        return self._parent._edb_sim_setup_info.SimulationSettings.DCRSettings

    @property
    def conduction_max_passes(self):
        """Conduction max passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.ConductionMaxPasses

    @conduction_max_passes.setter
    def conduction_max_passes(self, value):
        self._dcr_settings.ConductionMaxPasses = value
        self._parent._update_setup()

    @property
    def conduction_min_converged_passes(self):
        """Conduction min converged passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.ConductionMinConvergedPasses

    @conduction_min_converged_passes.setter
    def conduction_min_converged_passes(self, value):
        self._dcr_settings.ConductionMinConvergedPasses = value
        self._parent._update_setup()

    @property
    def conduction_min_passes(self):
        """Conduction min passes.

        Returns
        -------
        int
        """
        return self._dcr_settings.ConductionMinPasses

    @conduction_min_passes.setter
    def conduction_min_passes(self, value):
        self._dcr_settings.ConductionMinPasses = value
        self._parent._update_setup()

    @property
    def conduction_per_error(self):
        """Conduction error percentage.

        Returns
        -------
        float
        """
        return self._dcr_settings.ConductionPerError

    @conduction_per_error.setter
    def conduction_per_error(self, value):
        self._dcr_settings.ConductionPerError = value
        self._parent._update_setup()

    @property
    def conduction_per_refine(self):
        """Conduction refinement.

        Returns
        -------
        float
        """
        return self._dcr_settings.ConductionPerRefine

    @conduction_per_refine.setter
    def conduction_per_refine(self, value):
        self._dcr_settings.ConductionPerRefine = value
        self._parent._update_setup()


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
        """Edb Internal Simulation Setup Object."""
        return self._edb_sim_setup_info

    @pyaedt_function_handler()
    def _update_setup(self):
        mesh_operations = self._edb_sim_setup_info.SimulationSettings.MeshOperations
        mesh_operations.Clear()
        for mop in self.mesh_operations.values():
            mesh_operations.Add(mop.mesh_operation)

        self._edb_sim_setup = self._edb.edb.Utility.HFSSSimulationSetup(self._edb_sim_setup_info)

        if self._name in self._edb.setups:
            self._edb.active_cell.DeleteSimulationSetup(self._name)
        self._name = self.name
        self._edb.active_cell.AddSimulationSetup(self._edb_sim_setup)
        for i in list(self._edb.active_cell.SimulationSetups):
            if i.GetSimSetupInfo().Name == self._name:
                self._edb_sim_setup_info = i.GetSimSetupInfo()
                return True
        return False

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
        return HfssSolverSettings(self)

    @property
    def adaptive_settings(self):
        """Get adaptive settings."""
        return AdaptiveSettings(self)

    @property
    def defeature_settings(self):
        """Get defeature settings."""
        return DefeatureSettings(self)

    @property
    def via_settings(self):
        """Get via settings."""
        return ViaSettings(self)

    @property
    def advanced_mesh_settings(self):
        """Get advanced mesh settings."""
        return AdvancedMeshSettings(self)

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
        return CurveApproxSettings(self)

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
        return DcrSettings(self)

    @property
    def hfss_port_settings(self):
        """Hfss prot settings."""
        return HfssPortSettings(self)

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

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
    def add_frequency_sweep(self, name=None, frequency_sweep=None):
        """Add frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the frequency sweep.
        frequency_sweep : list, optional

        Returns
        ----------
        :class:`pyaedt.edb_core.edb_data.hfss_simulation_setup_data.EdbFrequencySweep
        """
        if name in self.frequency_sweeps:
            return False
        if not name:
            name = generate_unique_name("sweep")
        return EdbFrequencySweep(self, frequency_sweep, name)

    @pyaedt_function_handler()
    def set_solution_single_frequency(self, frequency="5GHz", max_num_passes=10, max_delta_s=0.02):
        """Set Single Frequency Solution.

        Parameters
        ----------
        frequency : str, float, optional
            Adaptive Frequency. Default is ``5GHz``.
        max_num_passes : int, optional
            Maximum number of passes. Default is ``10``.
        max_delta_s : float, optional
            Maximum Delta S. Default is ``0.02``.

        Returns
        -------
        bool

        """
        self.adaptive_settings.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        self.adaptive_settings.adapt_type = "kSingle"
        return self.adaptive_settings.add_adaptive_frequency_data(frequency, max_num_passes, max_delta_s)

    @pyaedt_function_handler()
    def set_solution_multi_frequencies(self, frequencies=("5GHz", "10GHz"), max_num_passes=10, max_delta_s="0.02"):
        """Set Multi Frequency Solution.

        Parameters
        ----------
        frequencies : list, tuple, optional
            Adaptive Frequencies. Default is ``5GHz``.
        max_num_passes : int, optional
            Maximum number of passes. Default is ``10``.
        max_delta_s : float, optional
            Maximum Delta S. Default is ``0.02``.

        Returns
        -------
        bool

        """
        self.adaptive_settings.adapt_type = "kMultiFrequencies"
        self.adaptive_settings.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        for i in frequencies:
            if not self.adaptive_settings.add_adaptive_frequency_data(i, max_num_passes, max_delta_s):
                return False
        return True

    @pyaedt_function_handler()
    def set_solution_broadband(
        self, low_frequency="5GHz", high_frequency="10GHz", max_num_passes=10, max_delta_s="0.02"
    ):
        """Set Broadband Solution.

        Parameters
        ----------
        low_frequency : str, float, optional
            Lower  Frequency. Default is ``5GHz``.
        high_frequency : str, float, optional
            Higher Frequencys. Default is ``10GHz``.
        max_num_passes : int, optional
            Maximum number of passes. Default is ``10``.
        max_delta_s : float, optional
            Maximum Delta S. Default is ``0.02``.

        Returns
        -------
        bool
        """
        self.adaptive_settings.adapt_type = "kBroadband"
        self.adaptive_settings.adaptive_settings.AdaptiveFrequencyDataList.Clear()
        if not self.adaptive_settings.add_adaptive_frequency_data(low_frequency, max_num_passes, max_delta_s):
            return False
        if not self.adaptive_settings.add_adaptive_frequency_data(high_frequency, max_num_passes, max_delta_s):
            return False
        return True
