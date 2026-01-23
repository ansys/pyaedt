# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from pathlib import Path
import shutil

import pytest

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.modeler.pcb.object_3d_layout import Components3DLayout
from tests import TESTS_LAYOUT_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL

TEST_SUBFOLDER = "layout_edb"
ORIGINAL_PROJECT = "ANSYS-HSD_V1"
ON_CI = os.getenv("ON_CI", "false").lower() == "true"


@pytest.fixture
def aedt_app(add_app_example):
    app = add_app_example(project=ORIGINAL_PROJECT, application=Hfss3dLayout, subfolder=TEST_SUBFOLDER, is_edb=True)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def flipchip(add_app_example):
    app = add_app_example(project="Package", application=Hfss3dLayout, subfolder=TEST_SUBFOLDER, is_edb=True)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def ic_mode_design(add_app_example):
    app = add_app_example(project="ic_mode_design", application=Hfss3dLayout, subfolder=TEST_SUBFOLDER, is_edb=True)
    yield app
    app.close_project(app.project_name, save=False)


""" def test_get_components(aedt_app):
    comp = aedt_app.modeler.components
    assert len(comp) > 0
    assert comp["L10"].object_units == "mm"
    assert comp["L10"].angle == "4.71238898038469"
    comp["L10"].angle = "90deg"
    assert comp["L10"].angle == "90deg"
    comp["L10"].angle = "4.71238898038469"
    assert comp["L10"].location[0] == 105.99999882
    assert comp["L10"].location[1] == 44.0000009
    comp["L10"].location = [1.0, 0.0]
    assert comp["L10"].location[0] == 1.0  # bug in component location
    comp["L10"].location = [105.99999882, 44.0000009]
    assert comp["L10"].placement_layer == "1_Top"
    assert comp["L10"].part == "WE-Coil-PD4-S"
    assert comp["L10"].part_type == "Inductor"
    assert comp["L10"].set_property_value("Angle", "0deg")
    assert comp["L10"].create_clearance_on_component(1e-6)
    assert comp["L10"].absolute_angle == 0.0
    comp["L10"].enabled = False
    assert not comp["L10"].enabled
    comp["L10"].enabled = True
    assert comp["L10"].enabled
    comp["R13"].enabled = False
    assert not comp["R13"].enabled
    comp["R13"].enabled = True
    assert comp["R13"].enabled
    comp["C10"].enabled = False
    assert not comp["C10"].enabled
    comp["C10"].enabled = True

    assert comp["U1"].enabled
    assert comp["J1"].enabled

    r5 = comp["R13"]
    assert r5.model
    assert r5.model.res == "3.57kOhm"
    assert r5.model.cap == "0"
    assert r5.model.ind == "0"
    assert not r5.model.is_parallel


def test_get_geometries(aedt_app):
    line = aedt_app.modeler.geometries["line_209"]
    assert line.edges
    assert isinstance(line.edge_by_point([0, 0]), int)
    assert line.points
    assert line.points
    assert line.is_closed
    poly = aedt_app.modeler.geometries["poly_1872"]
    assert poly.edges
    assert poly.points
    assert poly.bottom_edge_x == 0
    assert poly.bottom_edge_y == 1
    assert poly.top_edge_x == 2
    assert poly.top_edge_y == 3
    assert poly.placement_layer == "1_Top"
    assert poly.obounding_box
    poly.placement_layer = "16_Bottom"
    assert poly.placement_layer == "16_Bottom"
    poly.placement_layer = "1_Top"
    assert poly.net_name == "----"
    assert not poly.negative
    assert not poly.is_void
    assert not poly.lock_position
    assert poly.is_closed
    assert len(aedt_app.modeler.geometries) > 0
    rect = aedt_app.modeler.rectangles["rect_5951"]
    assert rect.point_a
    assert rect.point_b
    assert rect.two_point_description
    assert not rect.center
    rect.two_point_description = False
    assert rect.center
    assert rect.height
    rect.two_point_description = True
    assert rect.point_a
    circle = aedt_app.modeler.circles["circle_5952"]
    assert circle.center
    assert circle.radius
    circle.radius = "2.5mm"
    assert circle.radius == "2.5mm"
    assert aedt_app.modeler.geometries["line_209"].object_units == "mm"


def test_geo_layer(aedt_app):
    assert aedt_app.modeler.geometries["line_209"].placement_layer
    assert len(aedt_app.modeler.layers.drawing_layers) > 0
    assert len(aedt_app.modeler.layers.all_signal_layers) > 0
    assert len(aedt_app.modeler.layers.all_diel_layers) > 0
    assert len(aedt_app.modeler.stackup.all_signal_layers) == len(aedt_app.modeler.stackup.signals)
    assert len(aedt_app.modeler.stackup.all_diel_layers) == len(aedt_app.modeler.stackup.dielectrics)
    assert len(aedt_app.modeler.stackup.stackup_layers) == len(aedt_app.modeler.stackup.drawings)
    assert len(aedt_app.modeler.layers.all_signal_layers) + len(aedt_app.modeler.layers.all_diel_layers) == len(
        aedt_app.modeler.layers.stackup_layers
    )
    assert isinstance(aedt_app.modeler.layers.all_signal_layers[0].name, str)
    assert isinstance(aedt_app.modeler.layers.all_diel_layers[0].name, str)


def test_geo_lock(aedt_app):
    aedt_app.modeler.geometries["line_209"].lock_position = True
    assert aedt_app.modeler.geometries["line_209"].lock_position
    aedt_app.modeler.geometries["line_209"].lock_position = False
    assert not aedt_app.modeler.geometries["line_209"].lock_position


def test_geo_setter(aedt_app):
    aedt_app.modeler.geometries["line_209"].layer = "PWR"
    assert aedt_app.modeler.geometries["line_209"].layer == "PWR"
    aedt_app.modeler.geometries["line_209"].net_name = "VCC"
    assert aedt_app.modeler.geometries["line_209"].net_name == "VCC"


def test_get_pins(aedt_app):
    pins = aedt_app.modeler.pins
    assert len(pins) > 0
    assert pins["L10-1"].object_units == "mm"
    assert pins["L10-1"].componentname == "L10"
    assert pins["L10-1"].is_pin
    assert pins["L10-1"].angle
    assert pins["L10-1"].location[0] != 0
    assert pins["L10-1"].start_layer == "1_Top"
    assert pins["L10-1"].stop_layer == "1_Top"


def test_get_vias(aedt_app):
    vias = aedt_app.modeler.vias
    assert len(vias) > 0
    assert vias["Via1920"].object_units == "mm"
    assert not vias["Via1920"].is_pin
    assert vias["Via1920"].angle == "0deg"
    assert vias["Via1920"].location[0] > 0
    assert vias["Via1920"].start_layer == "1_Top"
    assert vias["Via1920"].stop_layer == "16_Bottom"
    assert vias["Via1920"].holediam == "0.1499997mm"


def test_voids(aedt_app):
    assert len(aedt_app.modeler.voids) > 0
    poly = aedt_app.modeler.polygons["poly_2084"]
    assert len(poly.polygon_voids) > 0


def test_add_mesh_operations(aedt_app):
    aedt_app.create_setup("HFSS")
    setup1 = aedt_app.mesh.assign_length_mesh("HFSS", "PWR", "GND")
    setup2 = aedt_app.mesh.assign_skin_depth("HFSS", "PWR", "GND")
    assert setup1
    assert setup2
    setup1.props["RestrictElem"] = False
    assert setup1.update()
    assert aedt_app.mesh.delete_mesh_operations(
        "HFSS",
        setup1.name,
    )


def test_change_property(aedt_app):
    ports = aedt_app.create_ports_on_component_by_nets("U1", "DDR4_DQS0_P")
    assert aedt_app.modeler.change_property(f"Excitations:{ports[0].name}", "Impedance", "49ohm", "EM Design")


def test_assign_touchstone_model(aedt_app, test_tmp_dir):
    model_path = TESTS_LAYOUT_PATH / "example_models" / TEST_SUBFOLDER / "GRM32_DC0V_25degC_series.s2p"
    file = shutil.copy2(model_path, test_tmp_dir / "GRM32_DC0V_25degC_series.s2p")
    assert aedt_app.modeler.set_touchstone_model(assignment="C217", input_file=str(file), model_name="Test1")


def test_assign_spice_model(aedt_app, file_tmp_root):
    model_path = TESTS_LAYOUT_PATH / "example_models" / TEST_SUBFOLDER / "GRM32ER72A225KA35_25C_0V.sp"
    file = shutil.copy2(model_path, file_tmp_root / "GRM32ER72A225KA35_25C_0V.sp")
    assert aedt_app.modeler.set_spice_model(
        assignment="C1", input_file=file, subcircuit_name="GRM32ER72A225KA35_25C_0V"
    ) """


def test_nets(aedt_app, test_tmp_dir):
    nets = aedt_app.modeler.nets
    assert nets["GND"].name == "GND"
    assert len(nets) > 0
    assert len(nets["GND"].components) > 0
    local_png1 = test_tmp_dir / "test1.png"
    nets["AVCC_1V3"].plot(save_plot=str(local_png1), show=False)
    assert local_png1.is_file()

""" 
def test_nets_count(aedt_app):
    nets = aedt_app.modeler.nets
    power_nets = aedt_app.modeler.power_nets
    signal_nets = aedt_app.modeler.signal_nets
    no_nets = aedt_app.modeler.no_nets
    assert len(nets) == len(power_nets) + len(signal_nets) + len(no_nets)


@pytest.mark.skipif(NON_GRAPHICAL, reason="Not running in non-graphical mode")
def test_merge(flipchip):
    tol = 1e-12
    brd = Hfss3dLayout(project=flipchip.project_name, design="Dummy_Board")
    comp = brd.modeler.merge_design(flipchip, rotation=90)
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
    assert (comp.location[0] - 0.1) < tol
    assert (comp.location[1] - 0.2) < tol


@pytest.mark.skipif(ON_CI, reason="Lead to logger issues on CI runners")
def test_change_stackup(add_app):
    app = add_app(application=Hfss3dLayout)
    app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness="0.035mm",
        elevation="1.035mm",
        material="copper",
    )
    app.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )

    if NON_GRAPHICAL:
        assert app.modeler.layers.change_stackup_type("Multizone", 4)
        assert len(app.modeler.layers.zones) == 3
    assert app.modeler.layers.change_stackup_type("Overlap")
    assert app.modeler.layers.change_stackup_type("Laminate")
    assert not app.modeler.layers.change_stackup_type("lami")
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(NON_GRAPHICAL, reason="Not running in non-graphical mode")
def test_export_picture(aedt_app):
    picture = aedt_app.post.export_model_picture(orientation="top")
    assert Path(picture).is_file()


def test_objects_by_net(aedt_app):
    poly_on_gnd = aedt_app.modeler.objects_by_net("GND", "poly")
    assert len(poly_on_gnd) > 0
    assert aedt_app.modeler.geometries[poly_on_gnd[0]].net_name == "GND"


def test_objects_by_layer(aedt_app):
    lines_on_top = aedt_app.modeler.objects_by_layer("1_Top", "line")
    assert len(lines_on_top) > 0
    assert aedt_app.modeler.geometries[lines_on_top[0]].placement_layer == "1_Top"


def test_set_solderball(aedt_app):
    assert not aedt_app.modeler.components["U1"].die_enabled
    assert not aedt_app.modeler.components["U1"].die_type
    assert aedt_app.modeler.components["U1"].set_die_type()
    assert aedt_app.modeler.components["U1"].set_solderball("Cyl")
    assert aedt_app.modeler.components["U1"].solderball_enabled
    assert aedt_app.modeler.components["U1"].set_solderball(None)
    assert not aedt_app.modeler.components["U1"].solderball_enabled
    assert not aedt_app.modeler.components["L10"].set_solderball(None)
    assert aedt_app.modeler.components["J1"].set_solderball("Sph")


def test_3dplacement(aedt_app):
    aedt_app.insert_design("placement_3d")
    aedt_app.modeler.layers.add_layer("BOTTOM", "signal")
    aedt_app.modeler.layers.add_layer("diel", "dielectric")
    aedt_app.modeler.layers.add_layer("TOP", "signal")
    tol = 1e-12
    encrypted_model_path = TESTS_LAYOUT_PATH / "example_models" / TEST_SUBFOLDER / "SMA_RF_Jack.a3dcomp"
    comp = aedt_app.modeler.place_3d_component(
        str(encrypted_model_path), 1, placement_layer="TOP", component_name="my_connector", pos_x=0.001, pos_y=0.002
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
    assert len(aedt_app.modeler.components_3d) == 1
    comp2 = aedt_app.modeler.place_3d_component(
        encrypted_model_path, 1, component_name="my_connector2", pos_x=0.001, pos_y=0.002, pos_z=1
    )
    assert comp2.location[2] == 1.0


def test_differential_ports(aedt_app):
    pins = list(aedt_app.modeler.components["R3"].pins.keys())
    assert aedt_app.create_differential_port(pins[0], pins[1], "test_differential", deembed=True)
    assert "test_differential" in aedt_app.port_list


def test_ports_on_components_nets(aedt_app):
    component = aedt_app.modeler.components["J1"]
    nets = [
        aedt_app.modeler.pins[i].net_name
        for i in component.pins
        if "GND" not in aedt_app.modeler.pins[i].net_name and aedt_app.modeler.pins[i].net_name != ""
    ]
    ports_before = len(aedt_app.port_list)
    ports = aedt_app.create_ports_on_component_by_nets("J1", nets)
    assert ports
    ports_after = len(aedt_app.port_list)
    assert ports_after - ports_before == len(nets)
    ports[0].name = "port_test"
    assert ports[0].name == "port_test"
    assert ports[0].props["Port"] == "port_test"
    ports[0].props["Port"] = "port_test2"
    assert ports[0].name == "port_test2"


def test_set_variable(aedt_app):
    aedt_app.variable_manager.set_variable("var_test", expression="123")
    aedt_app["var_test"] = "234"
    assert "var_test" in aedt_app.variable_manager.design_variable_names
    assert aedt_app.variable_manager.design_variables["var_test"].expression == "234"


def test_change_options(aedt_app):
    assert aedt_app.change_options()
    assert aedt_app.change_options(color_by_net=False)
    assert not aedt_app.change_options(color_by_net=None)


def test_show_extent(aedt_app):
    assert aedt_app.show_extent()
    assert aedt_app.show_extent(show=False)
    assert not aedt_app.show_extent(show=None)


def test_change_design_settings(aedt_app):
    assert aedt_app.get_oo_property_value(aedt_app.odesign, "Design Settings", "DCExtrapolation") == "Standard"
    assert aedt_app.change_design_settings({"UseAdvancedDCExtrap": True})
    assert aedt_app.get_oo_property_value(aedt_app.odesign, "Design Settings", "DCExtrapolation") == "Advanced"


def test_dissolve_element(aedt_app):
    comp = aedt_app.modeler.components["D1"]
    pins = {name: pin for name, pin in comp.pins.items() if name in ["D1-1", "D1-2", "D1-7"]}
    aedt_app.dissolve_component("D1")
    comp = aedt_app.modeler.create_component_on_pins(list(pins.keys()))
    nets = [
        list(pins.values())[0].net_name,
        list(pins.values())[1].net_name,
    ]
    assert aedt_app.create_ports_on_component_by_nets(comp.name, nets)
    assert aedt_app.create_pec_on_component_by_nets(comp.name, "GND")


@pytest.mark.skipif(DESKTOP_VERSION <= "2024.1", reason="Introduced in 2024R1")
def test_open_ic_mode_design(ic_mode_design):
    assert ic_mode_design.ic_mode


def test_set_port_properties(aedt_app):
    component: Components3DLayout = aedt_app.modeler.components["Q1"]
    assert component.port_properties == ("0", True, "0", "0")
    new_values = ("10um", False, "0um", "0um")
    component.port_properties = new_values
    assert component.port_properties == new_values


def test_set_port_properties_on_ic_component(aedt_app):
    component: Components3DLayout = aedt_app.modeler.components["U10"]
    original_die_properties = component.die_properties
    assert component.port_properties == ("0", True, "0", "0")
    new_values = ("10um", False, "0um", "0um")
    component.port_properties = new_values
    assert component.port_properties == new_values
    assert component.die_properties == original_die_properties


def test_get_properties_on_rlc_component(aedt_app):
    component: Components3DLayout = aedt_app.modeler.components["C1"]
    assert component.die_properties is None
    assert component.port_properties is None


def test_set_port_properties_on_rlc_component(aedt_app):
    component: Components3DLayout = aedt_app.modeler.components["C1"]
    component.port_properties = ("10um", False, "0um", "0um")
    assert component.port_properties is None


def test_import_table(aedt_app):
    file_header = TESTS_LAYOUT_PATH / "example_models" / TEST_SUBFOLDER / "table_header.csv"
    file_invented = "invented.csv"

    assert not aedt_app.import_table(file_header, column_separator="dummy")
    assert not aedt_app.import_table(file_invented)

    table = aedt_app.import_table(file_header)
    assert table in aedt_app.existing_analysis_sweeps

    assert not aedt_app.delete_imported_data("invented")

    assert aedt_app.delete_imported_data(table)
    assert table not in aedt_app.existing_analysis_sweeps


def test_ports_on_nets(aedt_app):
    nets = ["DDR4_DQ0", "DDR4_DQ1"]
    ports_before = len(aedt_app.port_list)
    ports = aedt_app.create_ports_by_nets(nets)
    assert ports
    ports_after = len(aedt_app.port_list)
    assert ports_after - ports_before == len(nets) * 2
    ports[0].name = "port_test"
    assert ports[0].name == "port_test"
    assert ports[0].props["Port"] == "port_test"
    ports[0].props["Port"] = "port_test2"
    assert ports[0].name == "port_test2"
 """