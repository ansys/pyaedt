import warnings

from pyaedt.edb_core.edb_data.simulation_setup import BaseSimulationSetup
from pyaedt.edb_core.general import convert_netdict_to_pydict
from pyaedt.edb_core.general import convert_pydict_to_netdict
from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.general_methods import pyaedt_function_handler


def _parse_value(v):
    """Parse value in C sharp format."""
    #  duck typing parse of the value 'v'
    if v is None or v == "":
        pv = v
    elif v == "true":
        pv = True
    elif v == "false":
        pv = False
    else:
        try:
            pv = int(v)
        except ValueError:
            try:
                pv = float(v)
            except ValueError:
                if isinstance(v, str) and v[0] == v[-1] == "'":
                    pv = v[1:-1]
                else:
                    pv = v
    return pv


class SettingsBase(object):
    """Provide base settings."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def sim_setup_info(self):
        """EDB internal simulation setup object."""

        return self._parent.get_sim_setup_info

    @pyaedt_function_handler
    def get_configurations(self):
        """Get all attributes.

        Returns
        -------
        dict
        """
        temp = {}
        attrs_list = [i for i in dir(self) if not i.startswith("_")]
        attrs_list = [
            i
            for i in attrs_list
            if i
            not in [
                "get_configurations",
                "sim_setup_info",
                "defaults",
                "si_defaults",
                "pi_defaults",
                "set_dc_slider",
                "set_si_slider",
                "set_pi_slider",
            ]
        ]
        for i in attrs_list:
            temp[i] = self.__getattribute__(i)
        return temp

    @pyaedt_function_handler
    def restore_default(self):
        for k, val in self.defaults.items():
            self.__setattr__(k, val)


class AdvancedSettings(SettingsBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.defaults = {
            "automatic_mesh": True,
            "ignore_non_functional_pads": True,
            "include_coplane_coupling": True,
            "include_fringe_coupling": True,
            "include_infinite_ground": False,
            "include_inter_plane_coupling": False,
            "include_split_plane_coupling": True,
            "include_trace_coupling": True,
            "include_vi_sources": False,
            "infinite_ground_location": "0",
            "max_coupled_lines": 12,
            "mesh_frequency": "4GHz",
            "min_pad_area_to_mesh": "28mm2",
            "min_plane_area_to_mesh": "5e-5mm2",
            "min_void_area": "2mm2",
            "perform_erc": False,
            "return_current_distribution": False,
            "snap_length_threshold": "2.5um",
            "xtalk_threshold": "-34",
        }

        self.si_defaults = {
            "include_coplane_coupling": [False, True, True],
            "include_fringe_coupling": [False, True, True],
            "include_inter_plane_coupling": [False, False, False],
            "include_split_plane_coupling": [False, True, True],
            "max_coupled_lines": [12, 12, 40],
            "return_current_distribution": [False, False, True],
        }

        self.pi_defaults = {
            "include_coplane_coupling": [False, False, True],
            "include_fringe_coupling": [False, True, True],
            "include_split_plane_coupling": [False, False, True],
            "include_trace_coupling": [False, False, True],
            "max_coupled_lines": [12, 12, 40],
        }

    @pyaedt_function_handler
    def set_si_slider(self, value):
        for k, val in self.si_defaults.items():
            self.__setattr__(k, val[value])

    @pyaedt_function_handler
    def set_pi_slider(self, value):
        for k, val in self.pi_defaults.items():
            self.__setattr__(k, val[value])

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
        return self.sim_setup_info.SimulationSettings.AdvancedSettings.MeshFrequency

    @include_inter_plane_coupling.setter
    def include_inter_plane_coupling(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.IncludeInterPlaneCoupling = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @xtalk_threshold.setter
    def xtalk_threshold(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.XtalkThreshold = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @min_void_area.setter
    def min_void_area(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.MinVoidArea = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @min_pad_area_to_mesh.setter
    def min_pad_area_to_mesh(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.MinPadAreaToMesh = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.MinPlaneAreaToMesh = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.SnapLengthThreshold = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @return_current_distribution.setter
    def return_current_distribution(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.ReturnCurrentDistribution = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @ignore_non_functional_pads.setter
    def ignore_non_functional_pads(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.IgnoreNonFunctionalPads = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @include_coplane_coupling.setter
    def include_coplane_coupling(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.IncludeCoPlaneCoupling = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @include_fringe_coupling.setter
    def include_fringe_coupling(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.IncludeFringeCoupling = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @include_split_plane_coupling.setter
    def include_split_plane_coupling(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.IncludeSplitPlaneCoupling = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @include_infinite_ground.setter
    def include_infinite_ground(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.IncludeInfGnd = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @include_trace_coupling.setter
    def include_trace_coupling(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.IncludeTraceCoupling = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @include_vi_sources.setter
    def include_vi_sources(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.IncludeVISources = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @infinite_ground_location.setter
    def infinite_ground_location(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.InfGndLocation = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @max_coupled_lines.setter
    def max_coupled_lines(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.MaxCoupledLines = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @automatic_mesh.setter
    def automatic_mesh(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.MeshAutoMatic = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @perform_erc.setter
    def perform_erc(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.AdvancedSettings.PerformERC = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @mesh_frequency.setter
    def mesh_frequency(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.AdvancedSettings.MeshFrequency = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()


class DCSettings(SettingsBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.defaults = {
            "compute_inductance": False,
            "contact_radius": "0.1mm",
            "use_dc_custom_settings": False,
            "plot_jv": True,
        }
        self.dc_defaults = {
            "dc_slider_position": [0, 1, 2],
        }

    @property
    def compute_inductance(self):
        """Whether to compute Inductance.

        Returns
        -------
        bool
            ``True`` if inductances will be computed, ``False`` otherwise.
        """

        return self.sim_setup_info.SimulationSettings.DCSettings.ComputeInductance

    @compute_inductance.setter
    def compute_inductance(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCSettings.ComputeInductance = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def contact_radius(self):
        """Circuit element contact radius.

        Returns
        -------
        str
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.ContactRadius

    @contact_radius.setter
    def contact_radius(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCSettings.ContactRadius = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def dc_slider_position(self):
        """DC simulation accuracy level slider position. This property only change slider position.

        Options:
        0- ``optimal speed``
        1- ``balanced``
        2- ``optimal accuracy``.
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.DCSliderPos

    @dc_slider_position.setter
    def dc_slider_position(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCSettings.DCSliderPos = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

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

    @use_dc_custom_settings.setter
    def use_dc_custom_settings(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCSettings.UseDCCustomSettings = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @property
    def plot_jv(self):
        """Plot current and voltage distributions.

        Returns
        -------
        bool
            ``True`` if plot JV is used, ``False`` otherwise.
        """
        return self.sim_setup_info.SimulationSettings.DCSettings.PlotJV

    @plot_jv.setter
    def plot_jv(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCSettings.PlotJV = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()


class DCAdvancedSettings(SettingsBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.defaults = {
            "dc_min_void_area_to_mesh": "0.001mm2",
            "max_init_mesh_edge_length": "5mm",
            "dc_min_plane_area_to_mesh": "1.5mm2",
            "num_bondwire_sides": 8,
            "num_via_sides": 8,
            "percent_local_refinement": 20.0,
        }
        self.dc_defaults = {
            "energy_error": [2, 2, 1],
            "max_num_pass": [5, 5, 10],
            "mesh_bondwires": [False, True, True],
            "mesh_vias": [False, True, True],
            "min_num_pass": [1, 1, 3],
            "perform_adaptive_refinement": [False, True, True],
            "refine_bondwires": [False, False, True],
            "refine_vias": [False, False, True],
        }

    @pyaedt_function_handler
    def set_dc_slider(self, value):
        for k, val in self.dc_defaults.items():
            self.__setattr__(k, val[value])

    @property
    def dc_min_void_area_to_mesh(self):
        """DC minimum area below which voids are ignored.

        Returns
        -------
        float
        """
        return self.sim_setup_info.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh

    @property
    def dc_min_plane_area_to_mesh(self):
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

    @dc_min_void_area_to_mesh.setter
    def dc_min_void_area_to_mesh(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @dc_min_plane_area_to_mesh.setter
    def dc_min_plane_area_to_mesh(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCAdvancedSettings.DcMinPlaneAreaToMesh = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @energy_error.setter
    def energy_error(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.DCAdvancedSettings.EnergyError = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @max_init_mesh_edge_length.setter
    def max_init_mesh_edge_length(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.DCAdvancedSettings.MaxInitMeshEdgeLength = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @max_num_pass.setter
    def max_num_pass(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.DCAdvancedSettings.MaxNumPasses = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @min_num_pass.setter
    def min_num_pass(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.DCAdvancedSettings.MinNumPasses = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @mesh_bondwires.setter
    def mesh_bondwires(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.DCAdvancedSettings.MeshBws = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @mesh_vias.setter
    def mesh_vias(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCAdvancedSettings.MeshVias = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @num_bondwire_sides.setter
    def num_bondwire_sides(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCAdvancedSettings.NumBwSides = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @num_via_sides.setter
    def num_via_sides(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCAdvancedSettings.NumViaSides = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @percent_local_refinement.setter
    def percent_local_refinement(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.DCAdvancedSettings.PercentLocalRefinement = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @perform_adaptive_refinement.setter
    def perform_adaptive_refinement(self, value):
        edb_setup_info = self.sim_setup_info

        edb_setup_info.SimulationSettings.DCAdvancedSettings.PerformAdaptiveRefinement = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @refine_bondwires.setter
    def refine_bondwires(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCAdvancedSettings.RefineBws = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()

    @refine_vias.setter
    def refine_vias(self, value):
        edb_setup_info = self.sim_setup_info
        edb_setup_info.SimulationSettings.DCAdvancedSettings.RefineVias = value
        self._parent._edb_object = self._parent._set_edb_setup_info(edb_setup_info)
        self._parent._update_setup()


class SiwaveSYZSimulationSetup(BaseSimulationSetup):
    """Manages EDB methods for SIwave simulation setup.

    Parameters
    ----------
    pedb : :class:`pyaedt.edb.Edb`
        Inherited AEDT object.
    edb_setup : :class:`Ansys.Ansoft.Edb.Utility.SIWaveSimulationSetup`
        Edb object.
    """

    def __init__(self, pedb, edb_setup=None):
        super().__init__(pedb, edb_setup)
        self._edb = self._pedb
        self._setup_type = "kSIwave"
        self._sim_setup_info = None

    @pyaedt_function_handler()
    def create(self, name=None):
        """Create a SIwave SYZ setup.

        Returns
        -------
        :class:`SiwaveDCSimulationSetup`
        """
        self._name = name
        self._create(name)
        self.set_si_slider(1)

        return self

    @pyaedt_function_handler
    def get_configurations(self):
        """Get SIwave SYZ simulation settings.

        Returns
        -------
        dict
            Dictionary of SIwave SYZ simulation settings.
        """
        return {
            "pi_slider_postion": self.pi_slider_position,
            "si_slider_postion": self.si_slider_position,
            "use_custom_settings": self.use_si_settings,
            "use_si_settings": self.use_si_settings,
            "advanced_settings": self.advanced_settings.get_configurations(),
        }

    @property
    def advanced_settings(self):
        """SIwave advanced settings."""
        return AdvancedSettings(self)

    @property
    def get_sim_setup_info(self):
        """Get simulation information from the setup."""
        if self._sim_setup_info:
            return self._sim_setup_info

        edb_setup = self._edb_object
        edb_sim_setup_info = self._pedb.simsetupdata.SimSetupInfo[self._setup_type_mapping[self._setup_type]]()
        edb_sim_setup_info.Name = edb_setup.GetName()

        string = edb_setup.ToString().replace("\t", "").split("\r\n")

        if is_linux:
            string = string[0].split("\n")
        keys = [i.split("=")[0] for i in string if len(i.split("=")) == 2 and "SourceTermsToGround" not in i]
        values = [i.split("=")[1] for i in string if len(i.split("=")) == 2 and "SourceTermsToGround" not in i]
        for val in string:
            if "SourceTermsToGround()" in val:
                break
            elif "SourceTermsToGround" in val:
                sources = {}
                val = val.replace("SourceTermsToGround(", "").replace(")", "").split(",")
                for v in val:
                    source = v.split("=")
                    sources[source[0]] = source[1]
                edb_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(
                    sources
                )
                break
        for k in keys:
            value = _parse_value(values[keys.index(k)])
            setter = None
            if k in dir(edb_sim_setup_info.SimulationSettings):
                setter = edb_sim_setup_info.SimulationSettings
            elif k in dir(edb_sim_setup_info.SimulationSettings.AdvancedSettings):
                setter = edb_sim_setup_info.SimulationSettings.AdvancedSettings

            elif k in dir(edb_sim_setup_info.SimulationSettings.DCAdvancedSettings):
                setter = edb_sim_setup_info.SimulationSettings.DCAdvancedSettings
            elif "DCIRSettings" in dir(edb_sim_setup_info.SimulationSettings) and k in dir(
                edb_sim_setup_info.SimulationSettings.DCIRSettings
            ):
                setter = edb_sim_setup_info.SimulationSettings.DCIRSettings
            elif k in dir(edb_sim_setup_info.SimulationSettings.DCSettings):
                setter = edb_sim_setup_info.SimulationSettings.DCSettings
            elif k in dir(edb_sim_setup_info.SimulationSettings.AdvancedSettings):
                setter = edb_sim_setup_info.SimulationSettings.AdvancedSettings
            if setter:
                try:
                    setter.__setattr__(k, value)
                except TypeError:
                    try:
                        setter.__setattr__(k, str(value))
                    except:
                        pass

        return edb_sim_setup_info

    @pyaedt_function_handler
    def set_pi_slider(self, value):
        """Set SIwave PI simulation accuracy level.

        Options are:

        - ``0``: Optimal speed
        - ``1``:  Balanced
        - ``2``: Optimal accuracy

        .. deprecated:: 0.7.5
           Use :property:`pi_slider_position` property instead.

        """
        warnings.warn("`set_pi_slider` is deprecated. Use `pi_slider_position` property instead.", DeprecationWarning)
        self.pi_slider_position = value

    @pyaedt_function_handler
    def set_si_slider(self, value):
        """Set SIwave SI simulation accuracy level.

        Options are:

        - ``0``: Optimal speed
        - ``1``:  Balanced
        - ``2``: Optimal accuracy```

        .. deprecated:: 0.7.5
           Use :property:`si_slider_position` property instead.

        """
        warnings.warn("`set_si_slider` is deprecated. Use `si_slider_position` property instead.", DeprecationWarning)

        self.si_slider_position = value

    @property
    def pi_slider_position(self):
        """PI solider position. Values are from ``1`` to ``3``."""
        return self.get_sim_setup_info.SimulationSettings.PISliderPos

    @pi_slider_position.setter
    def pi_slider_position(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.PISliderPos = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

        self.use_si_settings = False
        self.use_custom_settings = False
        self.advanced_settings.set_pi_slider(value)

    @property
    def si_slider_position(self):
        """SI slider position. Values are from ``1`` to ``3``."""
        return self.get_sim_setup_info.SimulationSettings.SISliderPos

    @si_slider_position.setter
    def si_slider_position(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.SISliderPos = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

        self.use_si_settings = True
        self.use_custom_settings = False
        self.advanced_settings.set_si_slider(value)

    @property
    def use_custom_settings(self):
        """Custom settings to use.

        Returns
        -------
        bool
        """
        return self.get_sim_setup_info.SimulationSettings.UseCustomSettings

    @use_custom_settings.setter
    def use_custom_settings(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.UseCustomSettings = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()

    @property
    def use_si_settings(self):
        """Whether to use SI Settings.

        Returns
        -------
        bool
        """
        return self.get_sim_setup_info.SimulationSettings.UseSISettings

    @use_si_settings.setter
    def use_si_settings(self, value):
        edb_setup_info = self.get_sim_setup_info
        edb_setup_info.SimulationSettings.UseSISettings = value
        self._edb_object = self._set_edb_setup_info(edb_setup_info)
        self._update_setup()


class SiwaveDCSimulationSetup(SiwaveSYZSimulationSetup):
    """Manages EDB methods for SIwave DC simulation setup.

    Parameters
    ----------
    pedb : :class:`pyaedt.edb.Edb`
        Inherited AEDT object.
    edb_setup : Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings
        EDB object. The default is ``None``.
    """

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._setup_type = "kSIwaveDCIR"
        self._edb = pedb
        self._mesh_operations = {}

    def create(self, name=None):
        """Create a SIwave DCIR setup.


        Returns
        -------
        :class:`SiwaveDCSimulationSetup`
        """
        self._name = name
        self._create(name)
        self.set_dc_slider(1)
        return self

    @pyaedt_function_handler
    def get_configurations(self):
        """Get SIwave DC simulation settings.

        Returns
        -------
        dict
            Dictionary of SIwave DC simulation settings.
        """
        return {
            "dc_settings": self.dc_settings.get_configurations(),
            "dc_advanced_settings": self.dc_advanced_settings.get_configurations(),
        }

    @pyaedt_function_handler
    def set_dc_slider(self, value):
        """Set DC simulation accuracy level.

        Options are:

        - ``0``: Optimal speed
        - ``1``: Balanced
        - ``2``: Optimal accuracy
        """
        self.use_custom_settings = False
        self.dc_settings.dc_slider_position = value
        self.dc_advanced_settings.set_dc_slider(value)

    @property
    def dc_settings(self):
        """SIwave DC setting."""
        return DCSettings(self)

    @property
    def dc_advanced_settings(self):
        """Siwave DC advanced settings.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`
        """
        return DCAdvancedSettings(self)

    @property
    def source_terms_to_ground(self):
        """Dictionary of grounded terminals.

        Returns
        -------
        Dictionary
            {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.

        """
        return convert_netdict_to_pydict(self.get_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround)

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
        self.get_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(
            terminals
        )
        return self._update_setup()
