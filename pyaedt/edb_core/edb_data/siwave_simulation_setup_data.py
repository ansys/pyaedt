from pyaedt.edb_core.edb_data.hfss_simulation_setup_data import EdbFrequencySweep
from pyaedt.edb_core.general import convert_netdict_to_pydict
from pyaedt.edb_core.general import convert_pydict_to_netdict
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler


class SiwaveAdvancedSettings(object):
    def __init__(self, parent):
        self._parent = parent

    @property
    def sim_setup_info(self):
        """EDB internal simulation setup object."""
        return self._parent._edb_sim_setup_info

    @property
    def include_inter_plane_coupling(self):
        """Get/Set the InterPlane Coupling.
        The setter will enable custom settings.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeInterPlaneCoupling

    @property
    def xtalk_threshold(self):
        """XTalk threshold.
        The setter enables custom settings.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.XtalkThreshold

    @property
    def min_void_area(self):
        """Minimum void area to include.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MinVoidArea

    @property
    def min_pad_area_to_mesh(self):
        """Minimum void pad area to mesh to include.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MinPadAreaToMesh

    @property
    def min_plane_area_to_mesh(self):
        """Minimum plane area to mesh to include.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MinPlaneAreaToMesh

    @property
    def snap_length_threshold(self):
        """Snapping length threshold.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.SnapLengthThreshold

    @property
    def return_current_distribution(self):
        """Get/Set the Flag to enable return current distribution.
        Accurately model the change of the characteristic impedance of transmission lines caused by
        a discontinuous ground plane.
        Instead of injecting the return current of a trace into a single point on the ground plane,
        the return current for a high impedance trace is now spread out.
        The trace return current is not distributed when all traces attached to a node
        have a characteristic impedance less than 75 ohms, or if the difference between
        two connected traces is less than 25 ohms.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.ReturnCurrentDistribution

    @property
    def ignore_non_functional_pads(self):
        """Exclude non functional pads.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IgnoreNonFunctionalPads

    @property
    def include_coplane_coupling(self):
        """Whether to enable coupling between traces and adjacent plane edges.
        This option provides a model for crosstalk between signal lines and planes.
        Plane edges couple to traces when they are parallel.
        Traces and coplanar edges that are oblique to each other do not overlap
        and cannot be considered for coupling.


        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeCoPlaneCoupling

    @property
    def include_fringe_coupling(self):
        """Include the effect of fringe field coupling between stacked cavities.


        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeFringeCoupling

    @property
    def include_split_plane_coupling(self):
        """Account for coupling between adjacent parallel plane edges.
        Primarily, two different cases are being considered:
        plane edges which form a split and plane edges which form a narrow trace-like plane.
        The former leads to crosstalk between adjacent planes for which a specific coupling model is applied.
        For the latter, fringing effects are considered to model accurately the propagation
        characteristics of trace-like cavities. Further, the coupling between narrow planes is
        also modeled by enabling this feature.


        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeSplitPlaneCoupling

    @property
    def include_infinite_ground(self):
        """Include a ground plane to serve as a voltage reference for traces and planes
        if they are not defined in the layout.


        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeInfGnd

    @property
    def include_trace_coupling(self):
        """Model coupling between adjacent traces.
        Coupling is considered for parallel and almost parallel trace segments.


        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeTraceCoupling

    @property
    def include_vi_sources(self):
        """Include the effect of parasitic elements from voltage and current sources.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeVISources

    @property
    def infinite_ground_location(self):
        """Specify the elevation of the infinite unconnected ground plane to be placed under the design.


        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.InfGndLocation

    @property
    def max_coupled_lines(self):
        """The user can enter the aximum number of coupled lines to build the new coupled transmission line model.


        Returns
        -------
        int
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MaxCoupledLines

    @property
    def automatic_mesh(self):
        """Automatically pick a suitable mesh refinement frequency, depending on drawing size,
        number of modes, and/or maximum sweep frequency.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MeshAutoMatic

    @property
    def perform_erc(self):
        """Perform an electrical rule check while generating the solver input.
        In some designs, the same net may be divided into multiple nets with separate names
        these nets are connected at a "star point".
        To simulate these nets, the error checking for DC shorts needs to be turned off,
        and all overlapping nets are internally united during simulation.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.PerformERC

    @property
    def mesh_frequency(self):
        """Specify the mesh size based on the effective wavelenth at the specified frequency.

        Returns
        -------
        str
        """
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MeshFrequency

    @include_inter_plane_coupling.setter
    def include_inter_plane_coupling(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeInterPlaneCoupling = value
        self._parent._update_setup()

    @xtalk_threshold.setter
    def xtalk_threshold(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.XtalkThreshold = value
        self._parent._update_setup()

    @min_void_area.setter
    def min_void_area(self, value):
        self.sim_setup_info.SimulationSettings.AdvancedSettings.MinVoidArea = value
        self._parent._update_setup()

    @min_pad_area_to_mesh.setter
    def min_pad_area_to_mesh(self, value):
        self.sim_setup_info.SimulationSettings.AdvancedSettings.MinPadAreaToMesh = value
        self._parent._update_setup()

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):
        self.sim_setup_info.SimulationSettings.AdvancedSettings.MinPlaneAreaToMesh = value
        self._parent._update_setup()

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):
        self.sim_setup_info.SimulationSettings.AdvancedSettings.SnapLengthThreshold = value
        self._parent._update_setup()

    @return_current_distribution.setter
    def return_current_distribution(self, value):
        self.sim_setup_info.SimulationSettings.AdvancedSettings.ReturnCurrentDistribution = value
        self._parent._update_setup()

    @ignore_non_functional_pads.setter
    def ignore_non_functional_pads(self, value):
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IgnoreNonFunctionalPads = value
        self._parent._update_setup()

    @include_coplane_coupling.setter
    def include_coplane_coupling(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeCoPlaneCoupling = value
        self._parent._update_setup()

    @include_fringe_coupling.setter
    def include_fringe_coupling(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeFringeCoupling = value
        self._parent._update_setup()

    @include_split_plane_coupling.setter
    def include_split_plane_coupling(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeSplitPlaneCoupling = value
        self._parent._update_setup()

    @include_infinite_ground.setter
    def include_infinite_ground(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeInfGnd = value
        self._parent._update_setup()

    @include_trace_coupling.setter
    def include_trace_coupling(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeTraceCoupling = value
        self._parent._update_setup()

    @include_vi_sources.setter
    def include_vi_sources(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeVISources = value
        self._parent._update_setup()

    @infinite_ground_location.setter
    def infinite_ground_location(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.InfGndLocation = value
        self._parent._update_setup()

    @max_coupled_lines.setter
    def max_coupled_lines(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.MaxCoupledLines = value
        self._parent._update_setup()

    @automatic_mesh.setter
    def automatic_mesh(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.MeshAutoMatic = value
        self._parent._update_setup()

    @perform_erc.setter
    def perform_erc(self, value):
        self.sim_setup_info.SimulationSettings.AdvancedSettings.PerformERC = value
        self._parent._update_setup()

    @mesh_frequency.setter
    def mesh_frequency(self, value):
        self.sim_setup_info.SimulationSettings.UseCustomSettings = True
        self.sim_setup_info.SimulationSettings.AdvancedSettings.MeshFrequency = value
        self._parent._update_setup()


class SiwaveDCAdvancedSettings(object):
    def __init__(self, parent):
        self._parent = parent

    @property
    def sim_setup_info(self):
        """Edb Internal Simulation Setup Object."""

        return self._parent._edb_sim_setup_info

    @property
    def min_void_area(self):
        """The minimum area below which voids are ignored.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh

    @property
    def min_plane_area(self):
        """The minimum area below which geometry is ignored.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinPlaneAreaToMesh

    @property
    def energy_error(self):
        """Energy error.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.EnergyError

    @property
    def max_init_mesh_edge_length(self):
        """Initial mesh maximum edge length.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MaxInitMeshEdgeLength

    @property
    def max_num_pass(self):
        """Maximum number of passes.

        Returns
        -------
        int
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MaxNumPasses

    @property
    def min_num_pass(self):
        """Minimum number of passes.

        Returns
        -------
        int
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MinNumPasses

    @property
    def mesh_bondwires(self):
        """Mesh bondwires.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshBws

    @property
    def mesh_vias(self):
        """Mesh vias.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshVias

    @property
    def num_bondwire_sides(self):
        """Number of Bondwire sides.

        Returns
        -------
        int
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.NumBwSides

    @property
    def num_via_sides(self):
        """Number of via sides.

        Returns
        -------
        int
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.NumViaSides

    @property
    def percent_local_refinement(self):
        """Percentage of local refinement.

        Returns
        -------
        float
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.PercentLocalRefinement

    @property
    def perform_adaptive_refinement(self):
        """Perform adaptive mesh refinement.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.PerformAdaptiveRefinement

    @property
    def refine_bondwires(self):
        """Refine mesh along bondwires.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineBws

    @property
    def refine_vias(self):
        """Refine mesh along vias.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineVias

    @property
    def compute_inductance(self):
        """Whether to compute Inductance.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.ComputeInductance

    @property
    def contact_radius(self):
        """Circuit element contact radius.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.ContactRadius

    @property
    def dc_slider_position(self):
        """Slider position for DC.

        Returns
        -------
        int
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.DCSliderPos

    @property
    def use_dc_custom_settings(self):
        """Use DC custom Settings.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings

    @property
    def plot_jv(self):
        """Plot JV.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.PlotJV

    @plot_jv.setter
    def plot_jv(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.PlotJV = value
        self._parent._update_setup()

    @compute_inductance.setter
    def compute_inductance(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.ComputeInductance = value
        self._parent._update_setup()

    @contact_radius.setter
    def contact_radius(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.ContactRadius = value
        self._parent._update_setup()

    @dc_slider_position.setter
    def dc_slider_position(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = False
        self.sim_setup_info.SimulationSettings.DCSettings.DCSliderPos = value
        self._parent._update_setup()

    @use_dc_custom_settings.setter
    def use_dc_custom_settings(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = value
        self._parent._update_setup()

    @min_void_area.setter
    def min_void_area(self, value):
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh = value
        self._parent._update_setup()

    @min_plane_area.setter
    def min_plane_area(self, value):
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinPlaneAreaToMesh = value
        self._parent._update_setup()

    @energy_error.setter
    def energy_error(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.EnergyError = value
        self._parent._update_setup()

    @max_init_mesh_edge_length.setter
    def max_init_mesh_edge_length(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MaxInitMeshEdgeLength = value
        self._parent._update_setup()

    @max_num_pass.setter
    def max_num_pass(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MaxNumPasses = value
        self._parent._update_setup()

    @min_num_pass.setter
    def min_num_pass(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MinNumPasses = value
        self._parent._update_setup()

    @mesh_bondwires.setter
    def mesh_bondwires(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshBws = value
        self._parent._update_setup()

    @mesh_vias.setter
    def mesh_vias(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshVias = value
        self._parent._update_setup()

    @num_bondwire_sides.setter
    def num_bondwire_sides(self, value):
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshBws = True
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.NumBwSides = value
        self._parent._update_setup()

    @num_via_sides.setter
    def num_via_sides(self, value):
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshVias = True
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.NumViaSides = value
        self._parent._update_setup()

    @percent_local_refinement.setter
    def percent_local_refinement(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.PercentLocalRefinement = value
        self._parent._update_setup()

    @perform_adaptive_refinement.setter
    def perform_adaptive_refinement(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.PerformAdaptiveRefinement = value
        self._parent._update_setup()

    @refine_bondwires.setter
    def refine_bondwires(self, value):
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshBws = True
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineBws = value
        self._parent._update_setup()

    @refine_vias.setter
    def refine_vias(self, value):
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.MeshVias = True
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = True
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineVias = value
        self._parent._update_setup()


class SiwaveSYZSimulationSetup(SiwaveAdvancedSettings, object):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, edb, name=None, edb_siwave_sim_setup=None):
        self._edb = edb
        self._sweep_data_list = {}
        if edb_siwave_sim_setup:
            self._edb_sim_setup_info = edb_siwave_sim_setup
        else:
            self._edb_sim_setup_info = self._edb.simsetupdata.SimSetupInfo[
                self._edb.simsetupdata.SIwave.SIWSimulationSettings
            ]()
            if not name:
                self._edb_sim_setup_info.Name = generate_unique_name("siwave")
            else:
                self._edb_sim_setup_info.Name = name
            self._update_setup()
        SiwaveAdvancedSettings.__init__(self, self)

    @property
    def edb_sim_setup_info(self):
        """Edb Internal Simulation Setup Object."""
        return self._edb_sim_setup_info

    @pyaedt_function_handler()
    def _update_setup(self):
        self._edb_sim_setup = self._edb.edb.Utility.SIWaveSimulationSetup(self._edb_sim_setup_info)
        if self.name in self._edb.setups:
            self._edb._active_layout.GetCell().DeleteSimulationSetup(self.name)
        self._edb._active_layout.GetCell().AddSimulationSetup(self._edb_sim_setup)
        return True

    @property
    def dc_settings(self):
        """Siwave DC Settings.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`
        """
        return SiwaveDCAdvancedSettings(self)

    @property
    def frequency_sweeps(self):
        """Get frequency sweep list."""
        if self._sweep_data_list:
            return self._sweep_data_list
        self._sweep_data_list = {}
        for i in list(self._edb_sim_setup_info.SweepDataList):
            self._sweep_data_list[i.Name] = EdbFrequencySweep(self, None, i.Name, i)
        return self._sweep_data_list

    @property
    def name(self):
        """Get name of this setup."""
        return self._edb_sim_setup_info.Name

    @name.setter
    def name(self, value):
        """Set name of this setup."""
        self._edb_sim_setup_info.Name = value
        self._update_setup()

    @property
    def enabled(self):
        """Check if setup is enabled."""
        return self._edb_sim_setup_info.SimulationSettings.Enabled

    @property
    def pi_slider_postion(self):
        """PI solider position. Values from 1 to 3."""
        return self._edb_sim_setup_info.SimulationSettings.PISliderPos

    @property
    def si_slider_postion(self):
        """SI solider position. Values from 1 to 3."""
        return self._edb_sim_setup_info.SimulationSettings.SISliderPos

    @enabled.setter
    def enabled(self, value):
        self._edb_sim_setup_info.SimulationSettings.Enabled = value
        self._update_setup()

    @pi_slider_postion.setter
    def pi_slider_postion(self, value):
        self._edb_sim_setup_info.SimulationSettings.UseCustomSettings = False
        self._edb_sim_setup_info.SimulationSettings.PISliderPos = value
        self._update_setup()

    @si_slider_postion.setter
    def si_slider_postion(self, value):
        self._edb_sim_setup_info.SimulationSettings.UseCustomSettings = False
        self._edb_sim_setup_info.SimulationSettings.SISliderPos = value
        self._update_setup()

    @property
    def use_custom_settings(self):
        """Use Custom Settings.

        Returns
        -------
        bool
        """
        return self._edb_sim_setup_info.SimulationSettings.UseCustomSettings

    @use_custom_settings.setter
    def use_custom_settings(self, value):
        self._edb_sim_setup_info.SimulationSettings.UseCustomSettings = value
        self._update_setup()

    @property
    def use_si_settings(self):
        """Use SI Settings.

        Returns
        -------
        bool
        """
        return self._edb_sim_setup_info.SimulationSettings.UseSISettings

    @use_si_settings.setter
    def use_si_settings(self, value):
        self._edb_sim_setup_info.SimulationSettings.UseCustomSettings = False
        self._edb_sim_setup_info.SimulationSettings.UseSISettings = value
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
        :class:`pyaedt.edb_core.edb_data.simulation_setup_data.EdbFrequencySweep`
        """
        if name in self.frequency_sweeps:
            return False
        if not name:
            name = generate_unique_name("sweep")
        sweep = EdbFrequencySweep(self, frequency_sweep, name)
        self._sweep_data_list[name] = sweep
        return sweep


class SiwaveDCSimulationSetup(SiwaveDCAdvancedSettings, object):
    """Manages EDB methods for hfss simulation setup."""

    def __init__(self, edb, name=None, edb_siwave_sim_setup=None):
        self._edb = edb
        self._mesh_operations = {}

        if edb_siwave_sim_setup:
            self._edb_sim_setup_info = edb_siwave_sim_setup
        else:
            self._edb_sim_setup_info = self._edb.simsetupdata.SimSetupInfo[
                self._edb.simsetupdata.SIwave.SIWDCIRSimulationSettings
            ]()
            if not name:
                self._edb_sim_setup_info.Name = generate_unique_name("siwave")
            else:
                self._edb_sim_setup_info.Name = name
            self._update_setup()
        SiwaveDCAdvancedSettings.__init__(self, self)

    @property
    def edb_sim_setup_info(self):
        """Edb Internal Simulation Setup Object."""
        return self._edb_sim_setup_info

    @pyaedt_function_handler()
    def _update_setup(self):
        edb_sim_setup = self._edb.edb.Utility.SIWaveDCIRSimulationSetup(self._edb_sim_setup_info)
        if self.name in self._edb.setups:
            self._edb._active_layout.GetCell().DeleteSimulationSetup(self.name)
        self._edb.active_cell.AddSimulationSetup(edb_sim_setup)
        return True

    @property
    def name(self):
        """Get name of this setup."""
        return self._edb_sim_setup_info.Name

    @name.setter
    def name(self, value):
        """Set name of this setup."""
        self._edb_sim_setup_info.Name = value
        self._update_setup()

    @property
    def enabled(self):
        """Check if setup is enabled."""
        return self._edb_sim_setup_info.SimulationSettings.Enabled

    @enabled.setter
    def enabled(self, value):
        self._edb_sim_setup_info.SimulationSettings.Enabled = value
        self._update_setup()

    @property
    def source_terms_to_ground(self):
        """Retrieve the dictionary of grounded terminals.

        Returns
        -------
            Dictionary
            {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.

        """
        return convert_netdict_to_pydict(self._edb_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround)

    @pyaedt_function_handler()
    def add_source_terminal_to_ground(self, source_name, terminal=0):
        """Add a source terminal to ground.

        Parameters
        ----------
        source_name : str,
            Source name.
        terminal : int, optional
            Terminal to assign.  Options are 0 unspecified, 1 negative node, 2 positive one.

        Returns
        -------
        bool

        """
        terminals = self.source_terms_to_ground
        terminals[source_name] = terminal
        self._edb_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(
            terminals
        )
        return self._update_setup()
