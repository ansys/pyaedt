# Setup paths for module imports
from _unittest.conftest import scratch_path

# Import required modules
from pyaedt import Maxwell3d
from pyaedt.generic.filesystem import Scratch
import gc
test_project_name = "eddy"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Maxwell3d(solution_type="EddyCurrent")

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_primitive(self):
        self.aedtapp.modeler.model_units = "mm"

        plate_pos = self.aedtapp.modeler.Position(0, 0, 0)
        hole_pos = self.aedtapp.modeler.Position(18, 18, 0)
        # Create plate with hole
        plate = self.aedtapp.modeler.primitives.create_box(
            plate_pos, [294, 294, 19], name="Plate")  # All positions in model units
        hole = self.aedtapp.modeler.primitives.create_box(
            hole_pos, [108, 108, 19], name="Hole")  # All positions in model units
        self.aedtapp.modeler.subtract([plate], [hole])
        plate.material_name = "aluminum"
        assert plate.solve_inside
        assert plate.material_name == "aluminum"

    def test_02_create_coil(self):
        center_hole = self.aedtapp.modeler.Position(119, 25, 49)
        center_coil = self.aedtapp.modeler.Position(94, 0, 49)
        coil_hole = self.aedtapp.modeler.primitives.create_box(center_hole, [150, 150, 100],
                                              name="Coil_Hole")  # All positions in model units
        coil = self.aedtapp.modeler.primitives.create_box(
            center_coil, [200, 200, 100], name="Coil")  # All positions in model units
        self.aedtapp.modeler.subtract([coil], [coil_hole])
        coil.material_name = "Copper"
        coil.solve_inside = True
        p_coil = self.aedtapp.post.volumetric_loss("Coil")
        assert type(p_coil) is str

    def test_03_coordinate_system(self):
        assert self.aedtapp.modeler.create_coordinate_system(
            [200, 100, 0], mode="view", view="XY", name="Coil_CS")

    def test_04_coil_terminal(self):
        self.aedtapp.modeler.section(["Coil"], self.aedtapp.CoordinateSystemPlane.ZXPlane)
        self.aedtapp.modeler.separate_bodies(["Coil_Section1"])
        self.aedtapp.modeler.primitives.delete("Coil_Section1_Separate1")
        assert self.aedtapp.assign_current(["Coil_Section1"], amplitude=2472)
        self.aedtapp.solution_type = "Magnetostatic"
        volt = self.aedtapp.assign_voltage(
            self.aedtapp.modeler.primitives["Coil_Section1"].faces[0].id, amplitude=1)
        assert volt
        assert volt.delete()
        self.aedtapp.solution_type = "EddyCurrent"

    def test_05_winding(self):
        assert self.aedtapp.assign_winding(
            self.aedtapp.modeler.primitives["Coil_Section1"].faces[0].id)

    def test_05_draw_region(self):
        assert self.aedtapp.modeler.create_air_region(*[300] * 6)

    def test_06_eddycurrent(self):
        assert self.aedtapp.eddy_effects_on(['Plate'])

    def test_07_setup(self):
        adaptive_frequency = "200Hz"
        Setup = self.aedtapp.create_setup()
        Setup.props["MaximumPasses"] = 12
        Setup.props["MinimumPasses"] = 2
        Setup.props["MinimumConvergedPasses"] = 1
        Setup.props["PercentRefinement"] = 30
        Setup.props["Frequency"] = adaptive_frequency
        assert Setup.update()
        assert Setup.enable_expression_cache(['CoreLoss'], "Fields", "Phase=\'0deg\' ", True)
        assert Setup.disable()
        assert Setup.enable()
        assert self.aedtapp.setup_ctrlprog(Setup.name)

    def test_22_create_length_mesh(self):
        assert self.aedtapp.mesh.assign_length_mesh(['Plate'])

    def test_23_create_skin_depth(self):
        assert self.aedtapp.mesh.assign_skin_depth(['Plate'], "1mm")

    def test_24_create_curvilinear(self):
        assert self.aedtapp.mesh.assign_curvilinear_elements(['Coil'], "1mm")

    def test_24_create_edge_cut(self):
        assert self.aedtapp.mesh.assign_edge_cut(["Coil"])

    def test_24_density_control(self):
        assert self.aedtapp.mesh.assign_density_control(
            ["Coil"], maxelementlength="2mm", layerNum="3")

    def test_24_density_control(self):
        assert self.aedtapp.mesh.assign_rotational_layer(["Coil"])

    def test_25_assign_initial_mesh(self):
        assert self.aedtapp.mesh.assign_initial_mesh_from_slider(4)

    def test_26_create_udp(self):
        my_udpPairs = []
        mypair = ["DiaGap", "102mm"]
        my_udpPairs.append(mypair)
        mypair = ["Length", "100mm"]
        my_udpPairs.append(mypair)
        mypair = ["Poles", "8"]
        my_udpPairs.append(mypair)
        mypair = ["EmbraceTip", "0.29999999999999999"]
        my_udpPairs.append(mypair)
        mypair = ["EmbraceRoot", "1.2"]
        my_udpPairs.append(mypair)
        mypair = ["ThickTip", "5mm"]
        my_udpPairs.append(mypair)
        mypair = ["ThickRoot", "10mm"]
        my_udpPairs.append(mypair)
        mypair = ["ThickShoe", "8mm"]
        my_udpPairs.append(mypair)
        mypair = ["DepthSlot", "12mm"]
        my_udpPairs.append(mypair)
        mypair = ["ThickYoke", "10mm"]
        my_udpPairs.append(mypair)
        mypair = ["LengthPole", "90mm"]
        my_udpPairs.append(mypair)
        mypair = ["LengthMag", "0mm"]
        my_udpPairs.append(mypair)
        mypair = ["SegAngle", "5deg"]
        my_udpPairs.append(mypair)
        mypair = ["LenRegion", "200mm"]
        my_udpPairs.append(mypair)
        mypair = ["InfoCore", "0"]
        my_udpPairs.append(mypair)

        my_udpName = "MyClawPoleCore"
        udp = self.aedtapp.modeler.primitives.create_udp(udp_dll_name="RMxprt/ClawPoleCore",
                                                          udp_parameters_list=my_udpPairs, upd_library='syslib',
                                                          name=my_udpName, udptye="Solid")
        assert udp

    def test_27_create_udm(self):
        my_udmPairs = []
        mypair = ["ILD Thickness (ILD)", "0.006mm"]
        my_udmPairs.append(mypair)
        mypair = ["Line Spacing (LS)", "0.004mm"]
        my_udmPairs.append(mypair)
        mypair = ["Line Thickness (LT)", "0.005mm"]
        my_udmPairs.append(mypair)
        mypair = ["Line Width (LW)", "0.004mm"]
        my_udmPairs.append(mypair)
        mypair = ["No. of Turns (N)", 2]
        my_udmPairs.append(mypair)
        mypair = ["Outer Diameter (OD)", "0.15mm"]
        my_udmPairs.append(mypair)
        mypair = ["Substrate Thickness", "0.2mm"]
        my_udmPairs.append(mypair)
        mypair = ["Inductor Type",
                  "\"Square,Square,Octagonal,Circular,Square-Differential,Octagonal-Differential,Circular-Differential\""]
        my_udmPairs.append(mypair)
        mypair = ["Underpass Thickness (UT)", "0.001mm"]
        my_udmPairs.append(mypair)
        mypair = ["Via Thickness (VT)", "0.001mm"]
        my_udmPairs.append(mypair)

        assert self.aedtapp.modeler.primitives.create_udm(udmfullname="Maxwell3D/OnDieSpiralInductor.py",
                                                          udm_params_list=my_udmPairs, udm_library='syslib')

    def test_28_assign_torque(self):
        assert self.aedtapp.assign_torque("Coil")

    def test_29_assign_force(self):
        assert self.aedtapp.assign_force("Coil")
