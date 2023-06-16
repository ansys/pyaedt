import os

from _unittest.conftest import config

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

# Setup paths for module imports
from _unittest.conftest import BasisTest
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path

# Import required modules
from pyaedt import Hfss3dLayout
from pyaedt import is_ironpython

test_subfolder = "T40"
if config["desktopVersion"] > "2022.2":
    test_project_name = "Galileo_t23_231"
    original_project_name = "Galileo_t23_231"
else:
    test_project_name = "Galileo_t23"
    original_project_name = "Galileo_t23"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(
            self, project_name=original_project_name, application=Hfss3dLayout, subfolder=test_subfolder
        )
        self.design_name = self.aedtapp.design_name
        self.tmp = self.aedtapp.modeler.geometries
        example_project = os.path.join(local_path, "example_models", test_subfolder, "Package.aedb")
        src_file = os.path.join(local_path, "example_models", test_subfolder, "Package.aedt")
        dest_file = os.path.join(self.local_scratch.path, "Package_test_40.aedt")
        self.target_path = os.path.join(self.local_scratch.path, "Package_test_40.aedb")
        self.local_scratch.copyfolder(example_project, self.target_path)
        self.package_file = self.local_scratch.copyfile(src_file, dest_file)

        self.dcir_example_project = BasisTest.add_app(
            self, project_name="Galileo_22r2_dcir", application=Hfss3dLayout, subfolder=test_subfolder
        )

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_get_components(self):
        comp = self.aedtapp.modeler.components
        assert len(comp) > 0
        assert comp["L3A1"].object_units == "mm"
        assert comp["L3A1"].angle == "0deg"
        comp["L3A1"].angle = "90deg"
        assert comp["L3A1"].angle == "90deg"
        comp["L3A1"].angle = "0deg"
        assert comp["L3A1"].location[0] == 58.8772
        assert comp["L3A1"].location[1] == 38.1
        comp["L3A1"].location = [1.0, 0.0]
        assert comp["L3A1"].location[0] == 1.0  # bug in component location
        comp["L3A1"].location = [58.872, 38.1]
        assert comp["L3A1"].placement_layer == "TOP"
        assert comp["L3A1"].part == "A32422-019"
        assert comp["L3A1"].part_type == "Inductor"
        assert comp["L3A1"].set_property_value("Angle", "0deg")
        assert comp["L3A1"].create_clearance_on_component(1e-6)
        assert comp["L3A1"].absolute_angle == 0.0
        comp["L3A1"].enabled = False
        assert not comp["L3A1"].enabled
        comp["L3A1"].enabled = True
        assert comp["L3A1"].enabled
        comp["R13"].enabled = False
        assert not comp["R13"].enabled
        comp["R13"].enabled = True
        assert comp["R13"].enabled
        comp["C3B14"].enabled = False
        assert not comp["C3B14"].enabled
        comp["C3B14"].enabled = True

        assert comp["U3B2"].enabled
        assert comp["J2"].enabled
        assert comp["FB1M1"].enabled

        r5 = comp["R5"]
        assert r5.model
        assert r5.model.res == "100kOhm"
        assert r5.model.cap == "0"
        assert r5.model.ind == "0"
        assert r5.model.is_parallel == False

    def test_02a_get_geometries(self):
        line = self.aedtapp.modeler.geometries["line_1983"]
        assert line.edges
        assert isinstance(line.edge_by_point([0, 0]), int)
        assert line.points
        assert line.points
        assert line.is_closed
        poly = self.aedtapp.modeler.geometries["poly_208"]
        assert poly.edges
        assert poly.points
        assert poly.bottom_edge_x == 1
        assert poly.bottom_edge_y == 7
        assert poly.top_edge_x == 13
        assert poly.top_edge_y == 18
        assert poly.placement_layer == "TOP"
        poly.placement_layer = "BOTTOM"
        assert poly.placement_layer == "BOTTOM"
        poly.placement_layer = "TOP"
        assert poly.net_name == "GND"
        assert not poly.negative
        assert not poly.is_void
        assert not poly.lock_position
        assert poly.is_closed
        assert len(self.aedtapp.modeler.geometries) > 0
        rect = self.aedtapp.modeler.rectangles["rect_30091"]
        assert rect.point_a
        assert rect.point_b
        assert rect.two_point_description
        assert not rect.center
        rect.two_point_description = False
        assert rect.center
        assert rect.height
        rect.two_point_description = True
        assert rect.point_a
        circle = self.aedtapp.modeler.circles["circle_30092"]
        assert circle.center
        assert circle.radius
        circle.radius = "2.5mm"
        assert circle.radius == "2.5mm"

    def test_02b_geo_units(self):
        assert self.aedtapp.modeler.geometries["line_1983"].object_units == "mm"

    def test_02c_geo_layer(self):
        assert self.aedtapp.modeler.geometries["line_1983"].placement_layer
        assert len(self.aedtapp.modeler.layers.drawing_layers) > 0
        assert len(self.aedtapp.modeler.layers.all_signal_layers) > 0
        assert len(self.aedtapp.modeler.layers.all_diel_layers) > 0
        assert len(self.aedtapp.modeler.stackup.all_signal_layers) == len(self.aedtapp.modeler.stackup.signals)
        assert len(self.aedtapp.modeler.stackup.all_diel_layers) == len(self.aedtapp.modeler.stackup.dielectrics)
        assert len(self.aedtapp.modeler.stackup.stackup_layers) == len(self.aedtapp.modeler.stackup.drawings)
        assert len(self.aedtapp.modeler.layers.all_signal_layers) + len(
            self.aedtapp.modeler.layers.all_diel_layers
        ) == len(self.aedtapp.modeler.layers.stackup_layers)
        assert isinstance(self.aedtapp.modeler.layers.all_signal_layers[0].name, str)
        assert isinstance(self.aedtapp.modeler.layers.all_diel_layers[0].name, str)

    def test_02d_geo_lock(self):
        self.aedtapp.modeler.geometries["line_1983"].lock_position = True
        assert self.aedtapp.modeler.geometries["line_1983"].lock_position == True
        self.aedtapp.modeler.geometries["line_1983"].lock_position = False
        assert self.aedtapp.modeler.geometries["line_1983"].lock_position == False

    def test_02e_geo_setter(self):
        self.aedtapp.modeler.geometries["line_1983"].layer = "PWR"
        assert self.aedtapp.modeler.geometries["line_1983"].layer == "PWR"
        self.aedtapp.modeler.geometries["line_1983"].net_name = "VCC"
        assert self.aedtapp.modeler.geometries["line_1983"].net_name == "VCC"

    def test_03_get_pins(self):
        pins = self.aedtapp.modeler.pins
        assert len(pins) > 0
        assert pins["L3A1-1"].object_units == "mm"
        assert pins["L3A1-1"].componentname == "L3A1"
        assert pins["L3A1-1"].is_pin
        assert pins["L3A1-1"].angle == "180deg"
        assert pins["L3A1-1"].location[0] > 0
        assert pins["L3A1-1"].start_layer == "TOP"
        assert pins["L3A1-1"].stop_layer == "TOP"

    def test_03B_get_vias(self):
        vias = self.aedtapp.modeler.vias
        assert len(vias) > 0
        assert vias["via_3795"].object_units == "mm"
        assert not vias["via_3795"].is_pin
        assert vias["via_3795"].angle == "90deg"
        assert vias["via_3795"].location[0] > 0
        assert vias["via_3795"].start_layer == "TOP"
        assert vias["via_3795"].stop_layer == "BOTTOM"
        assert vias["via_3795"].holediam == "10mil"

    def test_03C_voids(self):
        assert len(self.aedtapp.modeler.voids) > 0
        poly = self.aedtapp.modeler.polygons["poly_1345"]
        assert len(poly.polygon_voids) > 0

    def test_04_add_mesh_operations(self):
        self.aedtapp.create_setup("HFSS")
        setup1 = self.aedtapp.mesh.assign_length_mesh("HFSS", "PWR", "GND")
        setup2 = self.aedtapp.mesh.assign_skin_depth("HFSS", "PWR", "GND")
        assert setup1
        assert setup2
        setup1.props["RestrictElem"] = False
        assert setup1.update()
        assert self.aedtapp.mesh.delete_mesh_operations("HFSS", setup1.name)

    def test_05_change_property(self):
        assert self.aedtapp.modeler.change_property("Excitations:J2B3-2", "Impedance", "49ohm", "EM Design")

    def test_06_assign_spice_model(self):
        model_path = os.path.join(self.local_scratch.path, test_project_name + ".aedb", "GRM32ER72A225KA35_25C_0V.sp")
        assert self.aedtapp.modeler.set_spice_model(
            component_name="C3A3", model_path=model_path, subcircuit_name="GRM32ER72A225KA35_25C_0V"
        )

    def test_07_nets(self):
        nets = self.aedtapp.modeler.nets
        assert nets["GND"].name == "GND"
        assert len(nets) > 0
        assert len(nets["GND"].components) > 0

    def test_07a_nets_count(self):
        nets = self.aedtapp.modeler.nets
        power_nets = self.aedtapp.modeler.power_nets
        signal_nets = self.aedtapp.modeler.signal_nets
        no_nets = self.aedtapp.modeler.no_nets
        assert len(nets) == len(power_nets) + len(signal_nets) + len(no_nets)

    def test_08_merge(self):
        tol = 1e-12
        hfss3d = Hfss3dLayout(self.package_file, "FlipChip_TopBot", specified_version=desktop_version)
        brd = Hfss3dLayout(hfss3d.project_name, "Dummy_Board", specified_version=desktop_version)
        comp = brd.modeler.merge_design(hfss3d, rotation=90)
        assert comp.location[0] == 0.0
        assert comp.rotation_axis == "Z"
        comp.rotation_axis = "X"
        assert comp.rotation_axis == "X"
        comp.rotation_axis = "Z"
        comp.rotation_axis_direction = [0, 0, 1.2]
        assert comp.rotation_axis_direction == [0, 0, 1.2]
        assert not comp.is_flipped
        comp.is_flipped = True
        assert comp.is_flipped
        comp.is_flipped = False
        assert comp.location[0] == 0.0
        assert comp.location[1] == 0.0
        assert comp.angle == "90deg"
        comp.location = [0.1, 0.2]
        if config["desktopVersion"] > "2022.2":
            assert (comp.location[0] - 100.0) < tol
            assert (comp.location[1] - 200.0) < tol
        else:
            assert (comp.location[0] - 0.1) < tol
            assert (comp.location[1] - 0.2) < tol
        hfss3d.close_project(save_project=False)

    def test_10_change_stackup(self):
        assert self.aedtapp.modeler.layers.change_stackup_type("Multizone", 4)
        assert len(self.aedtapp.modeler.layers.zones) == 3
        assert self.aedtapp.modeler.layers.change_stackup_type("Overlap")
        assert self.aedtapp.modeler.layers.change_stackup_type("Laminate")
        assert not self.aedtapp.modeler.layers.change_stackup_type("lami")

    @pytest.mark.skipif(config["NonGraphical"], reason="Not running in non-graphical mode")
    def test_11_export_picture(self):
        assert os.path.exists(self.aedtapp.post.export_model_picture(orientation="top"))

    def test_12_objects_by_net(self):
        poly_on_gnd = self.aedtapp.modeler.objects_by_net("GND", "poly")
        assert len(poly_on_gnd) > 0
        assert self.aedtapp.modeler.geometries[poly_on_gnd[0]].net_name == "GND"

    def test_13_objects_by_layer(self):
        lines_on_top = self.aedtapp.modeler.objects_by_layer("TOP", "line")
        assert len(lines_on_top) > 0
        assert self.aedtapp.modeler.geometries[lines_on_top[0]].placement_layer == "TOP"

    def test_14_set_solderball(self):
        assert not self.aedtapp.modeler.components["U3B2"].die_enabled
        assert not self.aedtapp.modeler.components["U3B2"].die_type
        assert self.aedtapp.modeler.components["U3B2"].set_die_type()
        assert self.aedtapp.modeler.components["U3B2"].set_solderball("Cyl")
        assert self.aedtapp.modeler.components["U3B2"].solderball_enabled
        assert self.aedtapp.modeler.components["U3B2"].set_solderball(None)
        assert not self.aedtapp.modeler.components["U3B2"].solderball_enabled
        assert not self.aedtapp.modeler.components["L3A1"].set_solderball(None)
        assert self.aedtapp.modeler.components["J1"].set_solderball("Sph")

    def test_15_3dplacement(self):
        self.aedtapp.insert_design("placement_3d")
        l1 = self.aedtapp.modeler.layers.add_layer("BOTTOM", "signal", thickness="5mil")
        self.aedtapp.modeler.layers.add_layer("diel", "dielectric", thickness="121mil", material="FR4_epoxy")
        self.aedtapp.modeler.layers.add_layer("TOP", "signal", thickness="5mil", isnegative=True)
        tol = 1e-12
        encrypted_model_path = os.path.join(local_path, "example_models", test_subfolder, "SMA_RF_Jack.a3dcomp")
        comp = self.aedtapp.modeler.place_3d_component(
            encrypted_model_path, 1, placement_layer="TOP", component_name="my_connector", pos_x=0.001, pos_y=0.002
        )
        assert (comp.location[0] - 1.017) < tol
        assert (comp.location[1] - 2) < tol
        assert comp.angle == "0deg"
        assert comp.placement_layer == "TOP"
        comp.placement_layer = "bottom"
        assert comp.placement_layer == "BOTTOM"
        comp.angle = "10deg"
        assert comp.angle == "10deg"
        assert comp.component_name == "my_connector"
        assert len(self.aedtapp.modeler.components_3d) == 1

    def test_16_differential_ports(self):
        self.aedtapp.set_active_design(self.design_name)
        pins = self.aedtapp.modeler.components["R3"].pins
        assert self.aedtapp.create_differential_port(pins[0], pins[1], "test_differential", deembed=True)
        assert "test_differential" in self.aedtapp.port_list

    def test_17_ports_on_components_nets(self):
        component = self.aedtapp.modeler.components["J1"]
        nets = [
            self.aedtapp.modeler.pins[i].net_name
            for i in component.pins
            if "GND" not in self.aedtapp.modeler.pins[i].net_name
        ]
        ports_before = len(self.aedtapp.port_list)
        ports = self.aedtapp.create_ports_on_component_by_nets(
            "J1",
            nets,
        )
        assert ports
        ports_after = len(self.aedtapp.port_list)
        assert ports_after - ports_before == len(nets)
        ports[0].name = "port_test"
        assert ports[0].name == "port_test"
        assert ports[0].props["Port"] == "port_test"
        ports[0].props["Port"] = "port_test2"
        assert ports[0].name == "port_test2"

    def test_18_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    @pytest.mark.skipif(is_ironpython, reason="Not Supported.")
    def test_19_dcir(self):
        import pandas as pd

        self.dcir_example_project.analyze()
        assert self.dcir_example_project.get_dcir_solution_data("Siwave_DC_WP9QNY", "RL", "Path Resistance")
        assert self.dcir_example_project.get_dcir_solution_data("Siwave_DC_WP9QNY", "Vias", "Current")
        solution_data = self.dcir_example_project.get_dcir_solution_data("Siwave_DC_WP9QNY", "Sources", "Voltage")
        assert self.dcir_example_project.post.available_report_quantities(is_siwave_dc=True, context="")
        assert self.dcir_example_project.post.create_report(
            self.dcir_example_project.post.available_report_quantities(is_siwave_dc=True, context="RL")[0],
            setup_sweep_name="Siwave_DC_WP9QNY",
            domain="DCIR",
            context="RL",
        )
        assert isinstance(
            self.dcir_example_project.get_dcir_element_data_loop_resistance("Siwave_DC_WP9QNY"), pd.DataFrame
        )
        assert isinstance(
            self.dcir_example_project.get_dcir_element_data_current_source("Siwave_DC_WP9QNY"), pd.DataFrame
        )

    def test_20_change_options(self):
        assert self.aedtapp.change_options()
        assert self.aedtapp.change_options(color_by_net=False)
        assert not self.aedtapp.change_options(color_by_net=None)

    def test_21_show_extent(self):
        assert self.aedtapp.show_extent()
        assert self.aedtapp.show_extent(show=False)
        assert not self.aedtapp.show_extent(show=None)
