import os

from pyaedt.generic.constants import CutoutSubdesignType, RadiationBoxType, SweepType, BasisOrder


class SimulationConfiguration(object):
    """
    """

    def __init__(self, filename):
        self._filename = filename
        self._setup_name = "Pyaedt_setup"
        self._generate_solder_balls = True
        self._signal_nets = []
        self._power_nets = []
        self._component_with_coaxial_ports = []
        self._coax_instances = []
        self._coax_solder_ball_diameter = []
        self._keep_anf_ports_and_pin_groups = True
        self._use_default_coax_port_radial_extension = True
        self._trim_reference_size = False
        self._cutout_subdesign_type = CutoutSubdesignType.Conformal  # Conformal
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
        self._radiation_box = RadiationBoxType.ConvexHull  # 'ConvexHull'
        self._start_frequency = '0.0GHz'  # 0.0
        self._stop_freq = '10.001GHz'  # 10e9
        self._sweep_type = SweepType.Linear  # 'Linear'
        self._step_freq = '0.040004GHz'  # 10e6
        self._decade_count = 100  # Newly Added
        self._mesh_freq = '3GHz'  # 5e9
        self._max_num_passes = 30
        self._max_mag_delta_s = 0.03
        self._min_num_passes = 1
        self._basis_order = BasisOrder.Mixed  # 'Mixed'
        self._do_lambda_refinement = True
        self._arc_angle = '30deg'  # 30
        self._start_azimuth = 0
        self._max_arc_points = 8
        self._use_arc_to_chord_error = True
        self._arc_to_chord_error = '1um'  # 1e-6
        self._defeature_abs_length = '1um'  # 1e-6
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
        self._min_plane_area_to_mesh = '4mil2'  # Newly Added
        self._dc_min_plane_area_to_mesh = '8mil2'
        self._max_init_mesh_edge_length = '14.5mil'
        self._signalLayersProperties = []
        self._read_cfg()

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
    def setup_name(self):
        return self._setup_name

    @setup_name.setter
    def setup_name(self, value):
        if isinstance(value, str):
            self._setup_name = value

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
        # if isinstance(value, str):
        #     self._cutout_subdesign_type = value

    @property
    def cutout_subdesign_expansion(self):
        return self._cutout_subdesign_expansion

    @cutout_subdesign_expansion.setter
    def cutout_subdesign_expansion(self, value):
        if isinstance(value, float):
            self._cutout_subdesign_expansion = value

    @property
    def cutout_subdesign_round_corner(self):
        return self._cutout_subdesign_round_corner

    @cutout_subdesign_round_corner.setter
    def cutout_subdesign_round_corner(self, value):
        if isinstance(value, bool):
            self._cutout_subdesign_round_corner = value

    @property
    def sweep_interpolating(self):
        return self._sweep_interpolating

    @sweep_interpolating.setter
    def sweep_interpolating(self, value):
        if isinstance(value, bool):
            self._sweep_interpolating = value

    @property
    def use_q3d_for_dc(self):
        return self._use_q3d_for_dc

    @use_q3d_for_dc.setter
    def use_q3d_for_dc(self, value):
        if isinstance(value, bool):
            self._use_q3d_for_dc = value

    @property
    def relative_error(self):
        return self._relative_error

    @relative_error.setter
    def relative_error(self, value):
        if isinstance(value, float):
            self._relative_error = value

    @property
    def use_error_z0(self):
        return self._use_error_z0

    @use_error_z0.setter
    def use_error_z0(self, value):
        if isinstance(value, bool):
            self._use_error_z0 = value

    @property
    def percentage_error_z0(self):
        return self._percentage_error_z0

    @percentage_error_z0.setter
    def percentage_error_z0(self, value):
        if isinstance(value, float):
            self._percentage_error_z0 = value

    @property
    def enforce_causality(self):
        return self._enforce_causality

    @enforce_causality.setter
    def enforce_causality(self, value):
        if isinstance(value, bool):
            self._enforce_causality = value

    @property
    def enforce_passivity(self):
        return self._enforce_passivity

    @enforce_passivity.setter
    def enforce_passivity(self, value):
        if isinstance(value, bool):
            self._enforce_passivity = value

    @property
    def passivity_tolerance(self):
        return self._passivity_tolerance

    @passivity_tolerance.setter
    def passivity_tolerance(self, value):
        if isinstance(value, float):
            self._passivity_tolerance = value

    @property
    def sweep_name(self):
        return self._sweep_name

    @sweep_name.setter
    def sweep_name(self, value):
        if isinstance(value, str):
            self._sweep_name = value

    @property
    def radiation_box(self):
        return self._radiation_box

    @radiation_box.setter
    def radiation_box(self, value):
        if isinstance(value, RadiationBoxType):
            self._radiation_box = value
        # if isinstance(value, str):
        #     self._radiation_box = value

    @property
    def start_frequency(self):
        return self._start_frequency

    @start_frequency.setter
    def start_frequency(self, value):
        if isinstance(value, str):
            self._start_frequency = value

    @property
    def stop_freq(self):
        return self._stop_freq

    @stop_freq.setter
    def stop_freq(self, value):
        if isinstance(value, str):
            self._stop_freq = value

    @property
    def sweep_type(self):
        return self._sweep_type

    @sweep_type.setter
    def sweep_type(self, value):
        if isinstance(value, SweepType):
            self._sweep_type = value
        # if isinstance(value, str):
        #     self._sweep_type = value

    @property
    def step_freq(self):
        return self._step_freq

    @step_freq.setter
    def step_freq(self, value):
        if isinstance(value, str):
            self._step_freq = value

    @property
    def decade_count(self):
        return self._decade_count

    @decade_count.setter
    def decade_count(self, value):
        if isinstance(value, int):
            self._decade_count = value

    @property
    def mesh_freq(self):
        return self._mesh_freq

    @mesh_freq.setter
    def mesh_freq(self, value):
        if isinstance(value, str):
            self._mesh_freq = value

    @property
    def max_num_passes(self):
        return self._max_num_passes

    @max_num_passes.setter
    def max_num_passes(self, value):
        if isinstance(value, int):
            self._max_num_passes = value

    @property
    def max_mag_delta_s(self):
        return self._max_mag_delta_s

    @max_mag_delta_s.setter
    def max_mag_delta_s(self, value):
        if isinstance(value, float):
            self._max_mag_delta_s = value

    @property
    def min_num_passes(self):
        return self._min_num_passes

    @min_num_passes.setter
    def min_num_passes(self, value):
        if isinstance(value, int):
            self._min_num_passes = value

    @property
    def basis_order(self):
        return self._basis_order

    @basis_order.setter
    def basis_order(self, value):
        if isinstance(value, BasisOrder):
            self._basis_order = value
        # if isinstance(value, str):
        #     self._basis_order = value

    @property
    def do_lambda_refinement(self):
        return self._do_lambda_refinement

    @do_lambda_refinement.setter
    def do_lambda_refinement(self, value):
        if isinstance(value, bool):
            self._do_lambda_refinement = value

    @property
    def arc_angle(self):
        return self._arc_angle

    @arc_angle.setter
    def arc_angle(self, value):
        if isinstance(value, str):
            self._arc_angle = value

    @property
    def start_azimuth(self):
        return self._start_azimuth

    @start_azimuth.setter
    def start_azimuth(self, value):
        if isinstance(value, float):
            self._start_azimuth = value

    @property
    def max_arc_points(self):
        return self._max_arc_points

    @max_arc_points.setter
    def max_arc_points(self, value):
        if isinstance(value, int):
            self._max_arc_points = value

    @property
    def use_arc_to_chord_error(self):
        return self._use_arc_to_chord_error

    @use_arc_to_chord_error.setter
    def use_arc_to_chord_error(self, value):
        if isinstance(value, bool):
            self._use_arc_to_chord_error = value

    @property
    def arc_to_chord_error(self):
        return self._arc_to_chord_error

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value):
        if isinstance(value, str):
            self._arc_to_chord_error = value

    @property
    def defeature_abs_length(self):
        return self._defeature_abs_length

    @defeature_abs_length.setter
    def defeature_abs_length(self, value):
        if isinstance(value, str):
            self._defeature_abs_length = value

    @property
    def defeature_layout(self):
        return self._defeature_layout

    @defeature_layout.setter
    def defeature_layout(self, value):
        if isinstance(value, bool):
            self._defeature_layout = value

    @property
    def minimum_void_surface(self):
        return self._minimum_void_surface

    @minimum_void_surface.setter
    def minimum_void_surface(self, value):
        if isinstance(value, float):
            self._minimum_void_surface = value

    @property
    def max_suf_dev(self):
        return self._max_suf_dev

    @max_suf_dev.setter
    def max_suf_dev(self, value):
        if isinstance(value, float):
            self._max_suf_dev = value

    @property
    def process_padstack_definitions(self):
        return self._process_padstack_definitions

    @process_padstack_definitions.setter
    def process_padstack_definitions(self, value):
        if isinstance(value, bool):
            self._process_padstack_definitions = value

    @property
    def return_current_distribution(self):
        return self._return_current_distribution

    @return_current_distribution.setter
    def return_current_distribution(self, value):
        if isinstance(value, bool):
            self._return_current_distribution = value

    @property
    def ignore_non_functional_pads(self):
        return self._ignore_non_functional_pads

    @ignore_non_functional_pads.setter
    def ignore_non_functional_pads(self, value):
        if isinstance(value, bool):
            self._ignore_non_functional_pads = value

    @property
    def include_inter_plane_coupling(self):
        return self._include_inter_plane_coupling

    @include_inter_plane_coupling.setter
    def include_inter_plane_coupling(self, value):
        if isinstance(value, bool):
            self._include_inter_plane_coupling = value

    @property
    def xtalk_threshold(self):
        return self._xtalk_threshold

    @xtalk_threshold.setter
    def xtalk_threshold(self, value):
        if isinstance(value, float):
            self._xtalk_threshold = value

    @property
    def min_void_area(self):
        return self._min_void_area

    @min_void_area.setter
    def min_void_area(self, value):
        if isinstance(value, str):
            self._min_void_area = value

    @property
    def min_pad_area_to_mesh(self):
        return self._min_pad_area_to_mesh

    @min_pad_area_to_mesh.setter
    def min_pad_area_to_mesh(self, value):
        if isinstance(value, str):
            self._min_pad_area_to_mesh = value

    @property
    def snap_length_threshold(self):
        return self._snap_length_threshold

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):
        if isinstance(value, str):
            self._snap_length_threshold = value
    
    @property
    def min_plane_area_to_mesh(self):
        return self._min_plane_area_to_mesh

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):
        if isinstance(value, str):
            self._min_plane_area_to_mesh = value

    @property
    def dc_min_plane_area_to_mesh(self):
        return self._dc_min_plane_area_to_mesh

    @dc_min_plane_area_to_mesh.setter
    def dc_min_plane_area_to_mesh(self, value):
        if isinstance(value, str):
            self._dc_min_plane_area_to_mesh = value

    @property
    def max_init_mesh_edge_length(self):
        return self._max_init_mesh_edge_length

    @max_init_mesh_edge_length.setter
    def max_init_mesh_edge_length(self, value):
        if isinstance(value, str):
            self._max_init_mesh_edge_length = value

    @property
    def signalLayersProperties(self):
        return self._signalLayersProperties

    @signalLayersProperties.setter
    def signalLayersProperties(self, value):
        if isinstance(value, list):
            self._signalLayersProperties = value

    def _get_bool_value(self, value):
        val = value.lower()
        if val in ('y', 'yes', 't', 'true', 'on', '1'):
            return True
        elif val in ('n', 'no', 'f', 'false', 'off', '0'):
            return False
        else:
            raise ValueError("invalid truth value %r" % (val,))

    def _get_list_value(self, value):
        value = value.strip("[]")
        if len(value) == 0:
            return []
        else:
            value = value.split(",")
            if isinstance(value, list):
                prop_values = [i.strip() for i in value]
            else:
                prop_values = [value.strip()]
            return prop_values

    def _read_cfg(self):

        if not os.path.exists(self._filename):
            raise Exception("{} does not exist.".format(self._filename))
        
        try:
            with open(self._filename) as cfg_file:
                cfg_lines = cfg_file.read().split('\n')
                for line in cfg_lines:
                    if line.strip() != "":
                        if line.find("="):
                            i, prop_value = line.strip().split("=")
                            value = prop_value.replace("'", "").strip()
                            if i.startswith("generateSolderBalls"):
                                self.generate_solder_balls = self._get_bool_value(value)
                            elif i.startswith('signalNets'):
                                self.signal_nets = self._get_list_value(value)
                            elif i.startswith("powerNets"):
                                self.power_nets = self._get_list_value(value)
                            elif i.startswith('coax_components'):
                                self.component_with_coaxial_ports = self._get_list_value(value)
                            elif i.startswith('coax_instances'):
                                self.coax_instances = self._get_list_value(value)
                            elif i.startswith('coaxSolderBallsDiams'):
                                self.coax_solder_ball_diameter = self._get_list_value(value)
                            elif i.startswith('KeepANFPortsAndPinGroups'):
                                self.keep_anf_ports_and_pin_groups = self._get_bool_value(value)
                            elif i.startswith('UseDefaultCoaxPortRadialExtentFactor'):
                                self.signal_nets = self._get_bool_value(value)
                            elif i.startswith('TrimRefSize'):
                                self.trim_reference_size = self._get_bool_value(value)
                            elif i.startswith('CutoutSubdesignType'):
                                if value.lower().startswith('conformal'):
                                    self.cutout_subdesign_type = CutoutSubdesignType.Conformal
                                elif value.lower().startswith('boundingbox'):
                                    self.cutout_subdesign_type = CutoutSubdesignType.BoundingBox
                                else:
                                    print("Unprocessed value for CutoutSubdesignType '{0}'".format(value))
                            elif i.startswith('CutoutSubdesignExpansion'):
                                self.cutout_subdesign_expansion = float(value)
                            elif i.startswith('CutoutSubdesignRoundCorners'):
                                self.cutout_subdesign_round_corner = self._get_bool_value(value)
                            elif i.startswith('SweepInterpolating'):
                                self.sweep_interpolating = self._get_bool_value(value)
                            elif i.startswith('UseQ3DForDC'):
                                self.use_q3d_for_dc = self._get_bool_value(value)
                            elif i.startswith('RelativeErrorS'):
                                self.relative_error = float(value)
                            elif i.startswith('UseErrorZ0'):
                                self.use_error_z0 = self._get_bool_value(value)
                            elif i.startswith('PercentErrorZ0'):
                                self.percentage_error_z0 = float(value)
                            elif i.startswith('EnforceCausality'):
                                self.enforce_causality = self._get_bool_value(value)
                            elif i.startswith('EnforcePassivity'):
                                self.enforce_passivity = self._get_bool_value(value)
                            elif i.startswith('PassivityTolerance'):
                                self.passivity_tolerance = float(value)
                            elif i.startswith('SweepName'):
                                self.sweep_name = value
                            elif i.startswith('RadiationBox'):
                                if value.lower().startswith('conformal'):
                                    self.radiation_box = RadiationBoxType.Conformal
                                elif value.lower().startswith('boundingbox'):
                                    self.radiation_box = RadiationBoxType.BoundingBox
                                elif value.lower().startswith('convexhull'):
                                    self.radiation_box = RadiationBoxType.ConvexHull
                                else:
                                    print("Unprocessed value for RadiationBox '{0}'".format(value))
                            elif i.startswith('StartFreq'):
                                self.start_frequency = value
                            elif i.startswith('StopFreq'):
                                self.stop_freq = value
                            elif i.startswith('SweepType'):
                                if value.lower().startswith('linear'):
                                    self.sweep_type = SweepType.Linear
                                elif value.lower().startswith('logcount'):
                                    self.sweep_type = SweepType.LogCount
                                else:
                                    print("Unprocessed value for SweepType '{0}'".format(value))
                            elif i.startswith('StepFreq'):
                                self.step_freq = value
                            elif i.startswith('DecadeCount'):
                                self.decade_count = int(value)
                            elif i.startswith('Mesh_Freq'):
                                self.mesh_freq = value
                            elif i.startswith('MaxNumPasses'):
                                self.max_num_passes = int(value)
                            elif i.startswith('MaxMagDeltaS'):
                                self.max_mag_delta_s = float(value)
                            elif i.startswith('MinNumPasses'):
                                self.min_num_passes = int(value)
                            elif i.startswith('BasisOrder'):
                                if value.lower().startswith('mixed'):
                                    self.basis_order = BasisOrder.Mixed
                                elif value.lower().startswith('zero'):
                                    self.basis_order = BasisOrder.Zero
                                elif value.lower().startswith('first'):  # single
                                    self.basis_order = BasisOrder.single
                                elif value.lower().startswith('second'):  # double
                                    self.basis_order = BasisOrder.Double
                                else:
                                    print("Unprocessed value for BasisOrder '{0}'".format(value))
                            elif i.startswith('DoLambdaRefinement'):
                                self.do_lambda_refinement = self._get_bool_value(value)
                            elif i.startswith('ArcAngle'):
                                self.arc_angle = value
                            elif i.startswith('StartAzimuth'):
                                self.start_azimuth = float(value)
                            elif i.startswith('MaxArcPoints'):
                                self.max_arc_points = int(value)
                            elif i.startswith('UseArcToChordError'):
                                self.use_arc_to_chord_error = self._get_bool_value(value)
                            elif i.startswith('ArcToChordError'):
                                self.arc_to_chord_error = value
                            elif i.startswith('DefeatureAbsLength'):
                                self.defeature_abs_length = value
                            elif i.startswith('DefeatureLayout'):
                                self.defeature_layout = self._get_bool_value(value)
                            elif i.startswith('MinimumVoidSuface'):
                                self.minimum_void_surface = float(value)
                            elif i.startswith('MaxSufDev'):
                                self.max_suf_dev = float(value)
                            elif i.startswith('ProcessPadstackDefinitions'):
                                self.process_padstack_definitions = self._get_bool_value(value)
                            elif i.startswith('ReturnCurrentDistribution'):
                                self.return_current_distribution = self._get_bool_value(value)
                            elif i.startswith('IgnoreNonFunctionalPads'):
                                self.ignore_non_functional_pads = self._get_bool_value(value)
                            elif i.startswith('IncludeInterPlaneCoupling'):
                                self.include_inter_plane_coupling = self._get_bool_value(value)
                            elif i.startswith('XtalkThreshold'):
                                self.xtalk_threshold = float(value)
                            elif i.startswith('MinVoidArea'):
                                self.min_void_area = value
                            elif i.startswith('MinPadAreaToMesh'):
                                self.min_pad_area_to_mesh = value
                            elif i.startswith('SnapLengthThreshold'):
                                self.snap_length_threshold = value
                            elif i.startswith('MinPlaneAreaToMesh'):
                                self.min_plane_area_to_mesh = value
                            elif i.startswith('DcMinPlaneAreaToMesh'):
                                self.dc_min_plane_area_to_mesh = value
                            elif i.startswith('MaxInitMeshEdgeLength'):
                                self.max_init_mesh_edge_length = value
                            elif i.startswith('SignalLayersProperties'):
                                self.signalLayersProperties = self._get_list_value(value)
                        else:
                            print("Unprocessed line in cfg file: {0}".format(line))
                    else:
                        continue
        except EnvironmentError as e:
            print("Error reading cfg file: {}".format(e.message))
            raise



