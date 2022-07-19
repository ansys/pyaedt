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

test_project_name = "Galileo_t23"
original_project_name = "Galileo_t23"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=original_project_name, application=Hfss3dLayout)
        self.tmp = self.aedtapp.modeler.geometries
        example_project = os.path.join(local_path, "example_models", "Package.aedb")
        src_file = os.path.join(local_path, "example_models", "Package.aedt")
        dest_file = os.path.join(self.local_scratch.path, "Package_test_40.aedt")
        self.target_path = os.path.join(self.local_scratch.path, "Package_test_40.aedb")
        self.local_scratch.copyfolder(example_project, self.target_path)
        self.package_file = self.local_scratch.copyfile(src_file, dest_file)

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
        assert comp["L3A1"].location[0] == 0.0
        comp["L3A1"].location = [1.0, 0.0]
        assert comp["L3A1"].location[0] == 1.0
        comp["L3A1"].location = [0.0, 0.0]
        assert comp["L3A1"].placement_layer == "TOP"
        assert comp["L3A1"].part == "A32422-019"
        assert comp["L3A1"].part_type == "Inductor"
        assert comp["L3A1"].set_property_value("Angle", "0deg")
        assert comp["L3A1"].enabled(False)
        assert comp["L3A1"].enabled(True)
        assert comp["R13"].enabled(False)
        assert comp["R13"].enabled(True)
        assert comp["C3B14"].enabled(False)
        assert comp["C3B14"].enabled(True)
        assert not comp["U3B2"].enabled(False)
        assert not comp["J2"].enabled(False)
        assert not comp["FB1M1"].enabled(False)
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
        assert isinstance(self.aedtapp.modeler.layers.all_signal_layers[0], str)
        assert isinstance(self.aedtapp.modeler.layers.all_diel_layers[0], str)

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
        setup1.props["Enabled"] = False
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

    def test_08_merge(self):
        tol = 1e-12
        hfss3d = Hfss3dLayout(self.package_file, "FlipChip_TopBot", specified_version=desktop_version)
        brd = Hfss3dLayout(hfss3d.project_name, "Dummy_Board", specified_version=desktop_version)
        comp = brd.modeler.merge_design(hfss3d, rotation=90)
        assert comp.location[0] == 0.0
        assert comp.location[1] == 0.0
        assert comp.angle == "90deg"
        comp.location = [0.1, 0.2]
        assert (comp.location[0] - 0.1) < tol
        assert (comp.location[1] - 0.2) < tol
        hfss3d.close_project(saveproject=False)

    @pytest.mark.skipif(os.name != "posix", reason="Not running in non graphical mode. Tested only in Linux machine")
    def test_09_3dplacement(self):  # pragma: no cover
        assert len(self.aedtapp.modeler.components_3d) == 2
        tol = 1e-12
        encrypted_model_path = os.path.join(local_path, "example_models", "connector.a3dcomp")
        comp = self.aedtapp.modeler.place_3d_component(
            encrypted_model_path, 4, placement_layer="TOP", component_name="my_connector", pos_x=0.001, pos_y=0.002
        )
        assert (comp.location[0] - 0.001) < tol
        assert (comp.location[1] - 0.002) < tol
        assert comp.angle == "0deg"
        assert comp.placement_layer == "TOP"
        comp.placement_layer = "bottom"
        assert comp.placement_layer == "BOTTOM"
        comp.angle = "10deg"
        assert comp.angle == "10deg"
        assert comp.component_name == "my_connector"

    def test_10_change_stackup(self):
        assert self.aedtapp.modeler.layers.change_stackup_type("Multizone", 4)
        assert len(self.aedtapp.modeler.layers.zones) == 3
        assert self.aedtapp.modeler.layers.change_stackup_type("Overlap")
        assert self.aedtapp.modeler.layers.change_stackup_type("Laminate")
        assert not self.aedtapp.modeler.layers.change_stackup_type("lami")

    @pytest.mark.skipif(config["NonGraphical"] == True, reason="Not running in non-graphical mode")
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
