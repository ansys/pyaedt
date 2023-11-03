import warnings

from pyaedt.edb_core.edb_data.simulation_setup import BaseSimulationSetup
from pyaedt.edb_core.edb_data.simulation_setup import EdbFrequencySweep
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
        return self._parent._edb_setup_info

    @property
    def include_inter_plane_coupling(self):
        """Whether to turn on InterPlane Coupling.
        The setter will also enable custom settings.

        Returns
        -------
        bool
            ``True`` if interplane coupling is used, ``False`` otherwise.
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
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MinVoidArea

    @property
    def min_pad_area_to_mesh(self):
        """Minimum void pad area to mesh to include.

        Returns
        -------
        bool
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MinPadAreaToMesh

    @property
    def min_plane_area_to_mesh(self):
        """Minimum plane area to mesh to include.

        Returns
        -------
        bool
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
        """Whether to enable the return current distribution.
        This option is used to accurately model the change of the characteristic impedance
        of transmission lines caused by a discontinuous ground plane. Instead of injecting
        the return current of a trace into a single point on the ground plane,
        the return current for a high impedance trace is spread out.
        The trace return current is not distributed when all traces attached to a node
        have a characteristic impedance less than 75 ohms or if the difference between
        two connected traces is less than 25 ohms.

        Returns
        -------
        bool
            ``True`` if return current distribution is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.ReturnCurrentDistribution

    @property
    def ignore_non_functional_pads(self):
        """Exclude non-functional pads.

        Returns
        -------
        bool
            `True`` if functional pads have to be ignored, ``False`` otherwise.
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
            ``True`` if coplane coupling is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeCoPlaneCoupling

    @property
    def include_fringe_coupling(self):
        """Whether to include the effect of fringe field coupling between stacked cavities.


        Returns
        -------
        bool
            ``True`` if fringe coupling is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeFringeCoupling

    @property
    def include_split_plane_coupling(self):
        """Whether to account for coupling between adjacent parallel plane edges.
        Primarily, two different cases are being considered:
        - Plane edges that form a split.
        - Plane edges that form a narrow trace-like plane.
        The former leads to crosstalk between adjacent planes for which
        a specific coupling model is applied. For the latter, fringing effects
        are considered to model accurately the propagation characteristics
        of trace-like cavities. Further, the coupling between narrow planes is
        also modeled by enabling this feature.

        Returns
        -------
        bool
            ``True`` if split plane coupling is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeSplitPlaneCoupling

    @property
    def include_infinite_ground(self):
        """Whether to Include a ground plane to serve as a voltage reference for traces and planes
        if they are not defined in the layout.

        Returns
        -------
        bool
            ``True`` if infinite ground is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeInfGnd

    @property
    def include_trace_coupling(self):
        """Whether to model coupling between adjacent traces.
        Coupling is considered for parallel and almost parallel trace segments.

        Returns
        -------
        bool
            ``True`` if trace coupling is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeTraceCoupling

    @property
    def include_vi_sources(self):
        """Whether to include the effect of parasitic elements from voltage and
        current sources.

        Returns
        -------
        bool
            ``True`` if vi sources is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.IncludeVISources

    @property
    def infinite_ground_location(self):
        """Elevation of the infinite unconnected ground plane placed under the design.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.InfGndLocation

    @property
    def max_coupled_lines(self):
        """Maximum number of coupled lines to build the new coupled transmission line model.

        Returns
        -------
        int
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MaxCoupledLines

    @property
    def automatic_mesh(self):
        """Whether to automatically pick a suitable mesh refinement frequency,
        depending on drawing size, number of modes, and/or maximum sweep
        frequency.

        Returns
        -------
        bool
            ``True`` if automatic mesh is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MeshAutoMatic

    @property
    def perform_erc(self):
        """Whether to perform an electrical rule check while generating the solver input.
        In some designs, the same net may be divided into multiple nets with separate names.
        These nets are connected at a "star" point. To simulate these nets, the error checking
        for DC shorts must be turned off. All overlapping nets are then internally united
        during simulation.

        Returns
        -------
        bool
            ``True`` if perform erc is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.PerformERC

    @property
    def mesh_frequency(self):
        """Mesh size based on the effective wavelength at the specified frequency.

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
        """EDB internal simulation setup object."""

        return self._parent._edb_setup_info

    @property
    def min_void_area(self):
        """Minimum area below which voids are ignored.

        Returns
        -------
        float
        """
        warnings.warn("`min_void_area` is deprecated. Use `dc_min_void_area` property instead.", DeprecationWarning)
        return self.dc_min_void_area_to_mesh

    @property
    def dc_min_void_area_to_mesh(self):
        """Minimum area below which voids are ignored.

        Returns
        -------
        float
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh

    @property
    def min_plane_area(self):
        """Minimum area below which geometry is ignored.

        Returns
        -------
        float
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinPlaneAreaToMesh

    @property
    def energy_error(self):
        """Energy error.

        Returns
        -------
        float
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.EnergyError

    @property
    def max_init_mesh_edge_length(self):
        """Initial mesh maximum edge length.

        Returns
        -------
        float
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
        """Number of bondwire sides.

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
        """Whether to perform adaptive mesh refinement.

        Returns
        -------
        bool
            ``True`` if adaptive refinement is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.PerformAdaptiveRefinement

    @property
    def refine_bondwires(self):
        """Whether to refine mesh along bondwires.

        Returns
        -------
        bool
            ``True`` if refine bondwires is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineBws

    @property
    def refine_vias(self):
        """Whether to refine mesh along vias.

        Returns
        -------
        bool
            ``True`` if via refinement is used, ``False`` otherwise.

        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.RefineVias

    @property
    def compute_inductance(self):
        """Whether to compute Inductance.

        Returns
        -------
        bool
            ``True`` if inductances will be computed, ``False`` otherwise.
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
        """Whether to use DC custom settings.
        This setting is automatically enabled by other properties when needed.

        Returns
        -------
        bool
            ``True`` if custom dc settings are used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings

    @property
    def plot_jv(self):
        """Plot JV.

        Returns
        -------
        bool
            ``True`` if plot JV is used, ``False`` otherwise.
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
        """DC simulation accuracy level slider position.
        Options:
        0- ``optimal speed``
        1- ``balanced``
        2- ``optimal accuracy``.
        """
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = False
        self.sim_setup_info.SimulationSettings.DCSettings.DCSliderPos = value
        self._parent._update_setup()

    @use_dc_custom_settings.setter
    def use_dc_custom_settings(self, value):
        self.sim_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = value
        self._parent._update_setup()

    @dc_min_void_area_to_mesh.setter
    def dc_min_void_area_to_mesh(self, value):
        self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh = value
        self._parent._update_setup()

    @min_void_area.setter
    def min_void_area(self, value):
        self.dc_min_void_area_to_mesh = value

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


class SiwaveSYZSimulationSetup(BaseSimulationSetup, SiwaveAdvancedSettings):
    """Manages EDB methods for SIwave simulation setup."""

    def __init__(self, pedb, edb_setup=None):
        self._setup_type = "kSIwave"
        super().__init__(pedb, edb_setup)
        self._edb = self._pedb

        SiwaveAdvancedSettings.__init__(self, self)

    @pyaedt_function_handler()
    def create(self, name=None):
        self._create(name)

        self.restore_default()
        self.use_si_settings = True
        return self

    def restore_default(self):
        self.si_slider_postion = 1
        self.pi_slider_postion = 1

    @property
    def dc_settings(self):
        """Siwave DC settings.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`
        """
        return SiwaveDCAdvancedSettings(self)

    @property
    def pi_slider_postion(self):
        """PI solider position. Values are from ``1`` to ``3``."""
        return self._edb_object.SimulationSettings.PISliderPos

    @pi_slider_postion.setter
    def pi_slider_postion(self, value):
        if value == 0:
            self.include_coplane_coupling = False
            self.include_inter_plane_coupling = False
            self.include_split_plane_coupling = False
            self.include_fringe_coupling = False
            self.include_trace_coupling = False
            self.max_coupled_lines = 12
        elif value == 1:
            self.include_coplane_coupling = False
            self.include_inter_plane_coupling = False
            self.include_split_plane_coupling = False
            self.include_fringe_coupling = True
            self.include_trace_coupling = False
            self.max_coupled_lines = 12
        else:
            self.include_coplane_coupling = True
            self.include_inter_plane_coupling = False
            self.include_split_plane_coupling = True
            self.include_fringe_coupling = True
            self.include_trace_coupling = True
            self.max_coupled_lines = 40
        self._edb_setup_info.SimulationSettings.UseCustomSettings = False
        self._edb_setup_info.SimulationSettings.PISliderPos = value
        self._update_setup()

    @property
    def si_slider_postion(self):
        """SI solider position. Values are from ``1`` to ``3``."""
        return self._edb_setup_info.SimulationSettings.SISliderPos

    @si_slider_postion.setter
    def si_slider_postion(self, value):
        if value == 0:
            self.include_coplane_coupling = False
            self.include_inter_plane_coupling = False
            self.include_split_plane_coupling = False
            self.include_fringe_coupling = False
            self.include_trace_coupling = True
            self.max_coupled_lines = 12
            self.return_current_distribution = False
        elif value == 1:
            self.include_coplane_coupling = True
            self.include_inter_plane_coupling = False
            self.include_split_plane_coupling = True
            self.include_fringe_coupling = True
            self.include_trace_coupling = True
            self.max_coupled_lines = 12
            self.return_current_distribution = False
        else:
            self.include_coplane_coupling = True
            self.include_inter_plane_coupling = False
            self.include_split_plane_coupling = True
            self.include_fringe_coupling = True
            self.include_trace_coupling = True
            self.max_coupled_lines = 40
            self.return_current_distribution = True
        self._edb_setup_info.SimulationSettings.UseCustomSettings = False
        self._edb_setup_info.SimulationSettings.SISliderPos = value
        self._update_setup()

    @property
    def use_custom_settings(self):
        """Whether to use custom settings.

        Returns
        -------
        bool
        """
        return self._edb_setup_info.SimulationSettings.UseCustomSettings

    @use_custom_settings.setter
    def use_custom_settings(self, value):
        self._edb_setup_info.SimulationSettings.UseCustomSettings = value
        self._update_setup()

    @property
    def use_si_settings(self):
        """Whether to use SI Settings.

        Returns
        -------
        bool
        """
        return self._edb_setup_info.SimulationSettings.UseSISettings

    @use_si_settings.setter
    def use_si_settings(self, value):
        self._edb_setup_info.SimulationSettings.UseCustomSettings = False
        self._edb_setup_info.SimulationSettings.UseSISettings = value
        self._update_setup()


class SiwaveDCSimulationSetup(SiwaveSYZSimulationSetup, SiwaveDCAdvancedSettings):
    """Manages EDB methods for HFSS simulation setup."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._edb = pedb
        self._mesh_operations = {}
        self._edb_setup_info = self._edb.simsetupdata.SimSetupInfo[
            self._edb.simsetupdata.SIwave.SIWDCIRSimulationSettings
        ]()

        SiwaveDCAdvancedSettings.__init__(self, self)

    def create(self, name=None):
        self._create(name)
        self.restore_default()
        self.use_si_settings = False
        return self

    @property
    def source_terms_to_ground(self):
        """Dictionary of grounded terminals.

        Returns
        -------
        Dictionary
            {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.

        """
        return convert_netdict_to_pydict(self._edb_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround)

    @pyaedt_function_handler()
    def add_source_terminal_to_ground(self, source_name, terminal=0):
        """Add a source terminal to ground.

        Parameters
        ----------
        source_name : str,
            Source name.
        terminal : int, optional
            Terminal to assign. Options are:

             - 0=Unspecified
             - 1=Negative node
             - 2=Positive none

        Returns
        -------
        bool

        """
        terminals = self.source_terms_to_ground
        terminals[source_name] = terminal
        self._edb_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(terminals)
        return self._update_setup()
