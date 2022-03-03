from pyaedt.generic.constants import CutoutSubdesignType, RadiationBoxType, SweepType, BasisOrder

class SimulationConfiguration(object):
    """
    """
    def __init__(self):
        self._generate_solder_balls = True
        self._signal_nets = []
        self._power_nets = []
        self._component_with_coaxial_ports = []
        self._coax_instances = []
        self._coax_solder_ball_diameter = []
        self._keep_anf_ports_and_pin_groups = True
        self._use_default_coax_port_radial_extension = True
        self._trim_reference_size = False
        self._cutout_subdesign_type = CutoutSubdesignType.Conformal
        self._cutout_subdesign_expansion = 0.1
        self._cutout_subdesign_round_corner = True
        self._sweep_interpolating = True
        self._use_q3d_for_dc = False
        self._relative_error = 0.5
        self._use_error_z0 = False
        self._percentage_error_z0 = 1
        self._enforce_causality = True
        self._enforce_passivity = True
        self._passivity_tolerance = 0.0001
        self._sweep_name = 'Sweep1'
        self._radiation_box = RadiationBoxType.ConvexHull
        self._start_frequency = 0.0
        self._stop_freq = 10e9
        self._sweep_type = SweepType.Linear
        self._step_freq = 10e6
        self._mesh_freq = 5e9
        self._max_num_passes = 30
        self._max_mag_delta_s = 0.03
        self._min_num_passes = 1
        self._basis_order = BasisOrder.Mixed
        self._do_lambda_refinement = True
        self._arc_angle = 30
        self._start_azimuth = 0
        self._max_arc_points = 8
        self._use_arc_to_chord_error = True
        self._arc_to_chord_error = 1e-6
        self._defeature_abs_length = 1e-6
        self._defeature_layout = True
        self._minimum_void_surface = 0
        self._max_suf_dev = 1e-3
        self._process_padstack_definitions = False
        self._return_current_distribution = True
        self._ignore_non_functional_pads = True
        self._include_inter_plane_coupling = True
        self._xtalk_threshold = -50
        self._min_void_area = '0.01mm2'
        self._min_pad_area_to_mesh = '0.01mm2'
        self._snap_length_threshold = '2.5um'
        self._dc_min_plane_area_to_mesh = '8mil2'
        self._max_init_mesh_edge_length = '14.5mil'
        self._SignalLayersProperties = []

    @property
    def generate_solder_balls(self):
        return self._generate_solder_balls

    @generate_solder_balls.setter
    def generate_solder_balls(self, value):
        if isinstance(value, bool):
            self._generate_solder_balls = value

    @property
    def signal_nets(self):
        return self._signal_nets

    @signal_nets.setter
    def signal_nets(self, value):
        if isinstance(value, list):
            self._signal_nets = value

    @property
    def power_nets(self):
        return self._power_nets

    @power_nets.setter
    def power_nets(self, value):
        if isinstance(value, list):
            self._power_nets = value

    @property
    def component_with_coaxial_ports(self):
        return self._component_with_coaxial_ports

    @component_with_coaxial_ports.setter
    def component_with_coaxial_ports(self, value):
        if isinstance(value, list):
            self._component_with_coaxial_ports = value

    @property
    def coax_instances(self):
        return self._coax_instances

    @coax_instances.setter
    def coax_instances(self, value):
        if isinstance(value, list):
            self._coax_instances = value

    @property
    def coax_solder_ball_diameter(self):
        return self._coax_solder_ball_diameter

    @coax_solder_ball_diameter.setter
    def coax_solder_ball_diameter(self, value):
        if isinstance(value, list):
            self._coax_solder_ball_diameter = value

    @property
    def keep_anf_ports_and_pin_groups(self):
        return self._keep_anf_ports_and_pin_groups

    @keep_anf_ports_and_pin_groups.setter
    def keep_anf_ports_and_pin_groups(self, value):
        if isinstance(value, bool):
            self._keep_anf_ports_and_pin_groups = value

    @property
    def use_default_coax_port_radial_extension(self):
        return self._use_default_coax_port_radial_extension

    @use_default_coax_port_radial_extension.setter
    def use_default_coax_port_radial_extension(self, value):
        if isinstance(value, bool):
            self._use_default_coax_port_radial_extension = value

    @property
    def trim_reference_size(self):
        return self._trim_reference_size

    @trim_reference_size.setter
    def trim_reference_size(self, value):
        if isinstance(value, bool):
            self._trim_reference_size = value

    @property
    def cutout_subdesign_type(self):
        return self._cutout_subdesign_type

    @cutout_subdesign_type.setter
    def cutout_subdesign_type(self, value):
        if isinstance(value, CutoutSubdesignType):
            self._cutout_subdesign_type = value

    @property
    def cutout_subdesign_expansion(self):
        return self._cutout_subdesign_expansion

    @cutout_subdesign_expansion.setter
    def cutout_subdesign_expansion(self, value):
        if isinstance(value, float):
            self._cutout_subdesign_expansion = value

    @property
    def

