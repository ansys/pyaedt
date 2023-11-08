from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler


class BaseSimulationSetup(object):
    """Provide base simulation setup.

    Parameters
    ----------
    pedb : :class:`pyaedt.edb.Edb`
        Inherited AEDT object.
    edb_object : :class:`Ansys.Ansoft.Edb.Utility.SIWaveSimulationSetup`,
    :class:`Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings`,
    :class:`Ansys.Ansoft.Edb.Utility.HFSSSimulationSettings`
        Edb object.
    """

    def __init__(self, pedb, edb_setup=None):
        self._pedb = pedb
        self._edb_object = edb_setup
        self._setup_type = ""
        self._setup_type_mapping = {
            "kHFSS": self._pedb.simsetupdata.HFSSSimulationSettings,
            "kPEM": None,
            "kSIwave": self._pedb.simsetupdata.SIwave.SIWSimulationSettings,
            "kLNA": None,
            "kTransient": None,
            "kQEye": None,
            "kVEye": None,
            "kAMI": None,
            "kAnalysisOption": None,
            "kSIwaveDCIR": self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings,
            "kSIwaveEMI": None,
            "kHFSSPI": None,
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }
        if self._edb_object:
            self._name = self._edb_object.GetName()

        self._sweep_list = {}

    @pyaedt_function_handler
    def _create(self, name=None):
        """Create a setup."""
        if not name:
            name = generate_unique_name(self.setup_type)
            self._name = name

        setup_type = self._setup_type_mapping[self._setup_type]
        edb_setup_info = self._pedb.simsetupdata.SimSetupInfo[setup_type]()
        edb_setup_info.Name = name
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @pyaedt_function_handler
    def _set_edb_setup_info(self, edb_setup_info):
        """Create a setup object from setup information object."""
        utility = self._pedb._edb.Utility
        setup_type_mapping = {
            "kHFSS": utility.HFSSSimulationSetup,
            "kPEM": None,
            "kSIwave": utility.SIWaveSimulationSetup,
            "kLNA": None,
            "kTransient": None,
            "kQEye": None,
            "kVEye": None,
            "kAMI": None,
            "kAnalysisOption": None,
            "kSIwaveDCIR": utility.SIWaveDCIRSimulationSetup,
            "kSIwaveEMI": None,
            "kHFSSPI": None,
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }
        setup_utility = setup_type_mapping[self._setup_type]
        return setup_utility(edb_setup_info)

    @pyaedt_function_handler()
    def _update_setup(self):
        """Update setup in EDB."""
        if self._setup_type == "kHFSS":
            mesh_operations = self.get_sim_setup_info.SimulationSettings.MeshOperations
            mesh_operations.Clear()
            for mop in self.mesh_operations.values():
                mesh_operations.Add(mop.mesh_operation)

        if self._name in self._pedb.setups:
            self._pedb.layout.cell.DeleteSimulationSetup(self._name)
        if not self._pedb.layout.cell.AddSimulationSetup(self._edb_object):
            raise Exception("Updating setup {} failed.".format(self._name))
        else:
            return True

    @property
    def enabled(self):
        """Whether the setup is enabled."""
        return self.get_sim_setup_info.SimulationSettings.Enabled

    @enabled.setter
    def enabled(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.Enabled = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def name(self):
        """Name of the setup."""
        return self._edb_object.GetName()

    @name.setter
    def name(self, value):
        self._pedb.layout.cell.DeleteSimulationSetup(self.name)
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.Name = value
        self._name = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def position(self):
        """Position in the setup list."""
        return self.get_sim_setup_info.Position

    @position.setter
    def position(self, value):
        edb_setup_info = self.get_sim_setup_info.SimulationSettings
        edb_setup_info.Position = value
        self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def setup_type(self):
        """Type of the setup."""
        return self.get_sim_setup_info.SimSetupType.ToString()

    @property
    def frequency_sweeps(self):
        """List of frequency sweeps."""
        temp = {}
        for i in list(self.get_sim_setup_info.SweepDataList):
            temp[i.Name] = EdbFrequencySweep(self, None, i.Name, i)
        return temp

    @pyaedt_function_handler
    def _add_frequency_sweep(self, sweep_data):
        """Add a frequency sweep.

        Parameters
        ----------
        sweep_data: EdbFrequencySweep
        """
        self._sweep_list[sweep_data.name] = sweep_data
        edb_setup_info = self.get_sim_setup_info

        if self._setup_type in ["kSIwave", "kHFSS"]:
            for _, v in self._sweep_list.items():
                edb_setup_info.SweepDataList.Add(v._edb_object)

        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @pyaedt_function_handler
    def delete_frequency_sweep(self, sweep_data):
        """Delete a frequency sweep.

        Parameters
        ----------
        sweep_data : EdbFrequencySweep
        """
        name = sweep_data.name
        if name in self._sweep_list:
            self._sweep_list.pop(name)

        fsweep = []
        for k, val in self.frequency_sweeps.items():
            if not k == name:
                fsweep.append(val)
        self.get_sim_setup_info.SweepDataList.Clear()
        for i in fsweep:
            self.get_sim_setup_info.SweepDataList.Add(i._edb_object)
        self._update_setup()
        return True if name in self.frequency_sweeps else False

    @pyaedt_function_handler()
    def add_frequency_sweep(self, name=None, frequency_sweep=None):
        """Add frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the frequency sweep.
        frequency_sweep : list, optional
            List of frequency points.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.simulation_setup_data.EdbFrequencySweep`

        Examples
        --------
        >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
        >>> setup1.add_frequency_sweep(frequency_sweep=[
        ...                           ["linear count", "0", "1kHz", 1],
        ...                           ["log scale", "1kHz", "0.1GHz", 10],
        ...                           ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ...                           ])
        """
        if name in self.frequency_sweeps:
            return False

        if not frequency_sweep:
            frequency_sweep = [["linear scale", "0.1GHz", "10GHz", "0.1GHz"]]
        elif not isinstance(frequency_sweep[0], list):
            frequency_sweep = [frequency_sweep]

        if not name:
            name = generate_unique_name("sweep")
        sweep = EdbFrequencySweep(self, frequency_sweep, name)
        self._add_frequency_sweep(sweep)
        self._update_setup()
        return sweep


class EdbFrequencySweep(object):
    """Manages EDB methods for a frequency sweep.

    Parameters
    ----------
    sim_setup : :class:`pyaedt.edb_core.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`
    name : str, optional
        Name of the frequency sweep.
    edb_sweep_data : :class:`Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings`, optional
        Edb object.
    """

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
            self._edb_sweep_data = self._pedb.simsetupdata.SweepData(self._name)
            self.set_frequencies(frequency_sweep)

    @property
    def _edb_object(self):
        return self._edb_sweep_data

    @property
    def _pedb(self):
        """EDB."""
        return self._sim_setup._pedb

    @pyaedt_function_handler()
    def _update_sweep(self):
        """Update the sweep."""
        self._sim_setup.delete_frequency_sweep(self)
        self._sim_setup._add_frequency_sweep(self)
        return

    @property
    def name(self):
        """Name of the sweep."""
        return self._edb_sweep_data.Name

    @name.setter
    def name(self, value):
        self._edb_sweep_data.Name = value
        self._update_sweep()

    @property
    def sweep_type(self):
        """Sweep type."""
        return

    @property
    def frequencies(self):
        """List of frequency points."""
        return list(self._edb_sweep_data.Frequencies)

    @property
    def adaptive_sampling(self):
        """Whether adaptive sampling is used.

        Returns
        -------
        bool
            ``True`` if adaptive sampling is used, ``False`` otherwise.
        """
        return self._edb_sweep_data.AdaptiveSampling

    @property
    def adv_dc_extrapolation(self):
        """Flag indicating if advanced DC extrapolation is turned on.

        Returns
        -------
        bool
            ``True`` if advanced DC Extrapolation is used, ``False`` otherwise.

        """
        return self._edb_sweep_data.AdvDCExtrapolation

    @property
    def compute_dc_point(self):
        """Flag indication if compute exact dc point is turned on."""
        return self._edb_sweep_data.ComputeDCPoint

    @compute_dc_point.setter
    def compute_dc_point(self, value):
        self._edb_sweep_data.ComputeDCPoint = value
        self._update_sweep()

    @property
    def auto_s_mat_only_solve(self):
        """Flag indication if Auto SMatrix only solve is turned on."""
        return self._edb_sweep_data.AutoSMatOnlySolve

    @property
    def enforce_causality(self):
        """Whether to enforce causality during interpolating sweep.

        Returns
        -------
        bool
            ``True`` if enforce causality is used, ``False`` otherwise.
        """
        return self._edb_sweep_data.EnforceCausality

    @property
    def enforce_dc_and_causality(self):
        """Flag indicating if DC point and causality are enforced.

        Returns
        -------
        bool
            ``True`` if enforce dc point and causality is used, ``False`` otherwise.

        """
        return self._edb_sweep_data.EnforceDCAndCausality

    @property
    def enforce_passivity(self):
        """Whether to enforce passivity during interpolating sweep.

        Returns
        -------
        bool
            ``True`` if enforce passivity is used, ``False`` otherwise.
        """
        return self._edb_sweep_data.EnforcePassivity

    @property
    def freq_sweep_type(self):
        """Sweep type. Options are.

        - ``"kInterpolatingSweep"``
        - ``"kDiscreteSweep"``
        - ``"kBroadbandFastSweep"``

        Returns
        -------
        str
            Sweep type.
        """
        return self._edb_sweep_data.FreqSweepType.ToString()

    @property
    def interpolation_use_full_basis(self):
        """Whether to use Full basis elements.

        Returns
        -------
        bool
            ``True`` if full basis interpolation is used, ``False`` otherwise.
        """
        return self._edb_sweep_data.InterpUseFullBasis

    @property
    def interpolation_use_port_impedance(self):
        """Whether to turn on the port impedance interpolation.

        Returns
        -------
        bool
            ``True`` if port impedance is used, ``False`` otherwise.
        """
        return self._edb_sweep_data.InterpUsePortImpedance

    @property
    def interpolation_use_prop_const(self):
        """Flag indicating if propagation constants are used.

        Returns
        -------
        bool
            ``True`` if propagation constants are used, ``False`` otherwise.
        """
        return self._edb_sweep_data.InterpUsePropConst

    @property
    def interpolation_use_s_matrix(self):
        """Flag indicating if the S matrix is used.

        Returns
        -------
        bool
            ``True`` if S matrix are used, ``False`` otherwise.
        """
        return self._edb_sweep_data.InterpUseSMatrix

    @property
    def max_solutions(self):
        """Number of aximum solutions.

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
            Frequency with units.
        """
        return self._edb_sweep_data.MinFreqSMatOnlySolve

    @property
    def min_solved_freq(self):
        """Minimum solved frequency.

        Returns
        -------
        str
            Frequency with units.
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
        """S-parameter error tolerance for the interpolating sweep.

        Returns
        -------
        float
        """
        return self._edb_sweep_data.RelativeSError

    @property
    def save_fields(self):
        """Flag indicating if the extraction of surface current data is turned on.

        Returns
        -------
        bool
            ``True`` if save fields is enabled, ``False`` otherwise.
        """
        return self._edb_sweep_data.SaveFields

    @property
    def save_rad_fields_only(self):
        """Flag indicating if the saving of only radiated fields is turned on.

        Returns
        -------
        bool
            ``True`` if save radiated field only is used, ``False`` otherwise.

        """
        return self._edb_sweep_data.SaveRadFieldsOnly

    @property
    def use_q3d_for_dc(self):
        """Flag indicating if The Q3D solver is enabled for DC point extraction.

        Returns
        -------
        bool
            ``True`` if Q3d for DC point is used, ``False`` otherwise.
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

    @interpolation_use_full_basis.setter
    def interpolation_use_full_basis(self, value):
        self._edb_sweep_data.InterpUseFullBasis = value
        self._update_sweep()

    @interpolation_use_port_impedance.setter
    def interpolation_use_port_impedance(self, value):
        self._edb_sweep_data.InterpUsePortImpedance = value
        self._update_sweep()

    @interpolation_use_prop_const.setter
    def interpolation_use_prop_const(self, value):
        self._edb_sweep_data.InterpUsePropConst = value
        self._update_sweep()

    @interpolation_use_s_matrix.setter
    def interpolation_use_s_matrix(self, value):
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
        start : str, float, optional
            Start frequency. The default is ``"0.1GHz"``.
        stop : str, float, optional
            Stop frequency. The default is ``"20GHz"``.
        step : str, float, optional
            Step frequency. The default is ``"50MHz"``.

        Returns
        -------
        bool
            ``True`` if correctly executed, ``False`` otherwise.

        """
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
            Step frequency.

        Returns
        -------
        bool
            ``True`` if correctly executed, ``False`` otherwise.

        """
        start = self._sim_setup._pedb.arg_to_dim(start, "Hz")
        stop = self._sim_setup._pedb.arg_to_dim(stop, "Hz")
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetFrequencies(start, stop, count)
        return self._update_sweep()

    @pyaedt_function_handler()
    def set_frequencies_log_scale(self, start="1kHz", stop="0.1GHz", samples=10):
        """Set a log-count frequency sweep.

        Parameters
        ----------
        start : str, float, optional
            Start frequency. The default is ``"1kHz"``.
        stop : str, float, optional
            Stop frequency. The default is ``"0.1GHz"``.
        samples : int, optional
            Step frequency. The default is ``10``.

        Returns
        -------
        bool
            ``True`` if correctly executed, ``False`` otherwise.
        """
        start = self._sim_setup._pedb.arg_to_dim(start, "Hz")
        stop = self._sim_setup._pedb.arg_to_dim(stop, "Hz")
        self._edb_sweep_data.Frequencies = self._edb_sweep_data.SetLogFrequencies(start, stop, samples)
        return self._update_sweep()

    @pyaedt_function_handler()
    def set_frequencies(self, frequency_list=None, update=True):
        """Set frequency list to the sweep frequencies.

        Parameters
        ----------
        frequency_list : list, optional
             List of lists with four elements. The default is ``None``. If provided, each list must contain:
              1 - frequency type (``"linear count"``, ``"log scale"``, or ``"linear scale"``)
              2 - start frequency
              3 - stop frequency
              4 - step frequency or count

        Returns
        -------
        bool
            ``True`` if correctly executed, ``False`` otherwise.

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
        self._edb_sweep_data.Frequencies.Clear()
        for i in temp:
            self._edb_sweep_data.Frequencies.Add(i)
        if update:
            return self._update_sweep()
