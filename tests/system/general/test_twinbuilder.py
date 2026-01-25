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

import shutil

import pytest

from ansys.aedt.core import TwinBuilder
from ansys.aedt.core.generic.general_methods import is_linux
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "T34"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=TwinBuilder)
    app.modeler.schematic_units = "mil"
    yield app
    app.close_project(save=False)


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_resistor(aedt_app):
    resistor = aedt_app.modeler.schematic.create_resistor("Resistor1", 10, [0, 0])
    assert resistor.parameters["R"] == "10"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_inductor(aedt_app):
    inductor = aedt_app.modeler.schematic.create_inductor("Inductor1", 1.5, [1000, 0])
    assert inductor.parameters["L"] == "1.5"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_capacitor(aedt_app):
    capacitor = aedt_app.modeler.schematic.create_capacitor("Capacitor1", 7.5, [2000, 0])
    assert capacitor.parameters["C"] == "7.5"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_diode(aedt_app):
    diode = aedt_app.modeler.schematic.create_diode("Diode1")
    assert diode.parameters["VF"] == "0.8V"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_npn(aedt_app):
    name = aedt_app.modeler.schematic.create_npn("NPN")
    # Get component info by part name
    assert name.parameters["VF"] == "0.8V"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_pnp(aedt_app):
    pnp = aedt_app.modeler.schematic.create_pnp("PNP")
    assert pnp.parameters["VF"] == "0.8V"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_import_netlist(aedt_app, test_tmp_dir):
    file_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "netlist_small.cir"
    netlist_file1 = shutil.copy2(file_o, test_tmp_dir / "netlist_small.cir")
    assert aedt_app.create_schematic_from_netlist(str(netlist_file1))


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_set_hmax(aedt_app):
    assert aedt_app.set_hmax("5ms")


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_set_hmin(aedt_app):
    assert aedt_app.set_hmin("0.2ms")


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_set_hmin_alternate(aedt_app):
    assert aedt_app.set_hmin("2s")


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_set_end_time(aedt_app):
    assert aedt_app.set_end_time("5s")


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_catalog(aedt_app):
    comp_catalog = aedt_app.modeler.components.components_catalog
    assert not comp_catalog["Capacitors"]
    assert comp_catalog["Aircraft Electrical VHDLAMS\\Basic:lowpass_filter"].props
    assert comp_catalog["Aircraft Electrical VHDLAMS\\Basic:lowpass_filter"].place("LP1")


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_periodic_pulse_wave(aedt_app):
    waveform = aedt_app.modeler.schematic.create_periodic_waveform_source("P1", "PULSE", 200, 20, 0, 0, [3000, 0])
    assert waveform.parameters["AMPL"] == "200"
    assert waveform.parameters["FREQ"] == "20"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_set_variable(aedt_app):
    aedt_app.variable_manager.set_variable("var_test", expression="123")
    aedt_app["var_test"] = "234"
    assert "var_test" in aedt_app.variable_manager.design_variable_names
    assert aedt_app.variable_manager.design_variables["var_test"].expression == "234"


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_add_dynamic_link(add_app, test_tmp_dir):
    file1_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "Q2D_ArmouredCableExample.aedt"
    dynamic_link = shutil.copy2(file1_o, test_tmp_dir / "Q2D_ArmouredCableExample.aedt")

    file2_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "Q3D_DynamicLink.aedt"
    q3d_dynamic_link = shutil.copy2(file2_o, test_tmp_dir / "Q3D_DynamicLink.aedt")

    tb = add_app(
        application=TwinBuilder,
        project=dynamic_link,
        design="CableSystem",
    )
    assert tb.add_q3d_dynamic_component(
        "Q2D_ArmouredCableExample", "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm"
    )
    assert tb.add_q3d_dynamic_component(
        dynamic_link, "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm"
    )
    with pytest.raises(TypeError):
        assert tb.add_q3d_dynamic_component(
            "Q2D_ArmouredCableExample",
            "2D_Extractor_Cable",
            "MySetupAuto",
            "sweep1",
            "Original",
            model_depth="invalid",
        )
    with pytest.raises(ValueError):
        assert tb.add_q3d_dynamic_component(
            "Q2D_ArmouredCableExample",
            "2D_Extractor_Cable",
            "MySetupAuto",
            "sweep1",
            "invalid",
            model_depth="100mm",
        )
    with pytest.raises(TypeError):
        assert tb.add_q3d_dynamic_component(
            "Q2D_ArmouredCableExample",
            "2D_Extractor_Cable",
            "MySetupAuto",
            "sweep1",
            "Original",
            model_depth="100mm",
            state_space_dynamic_link_type="invalid",
        )
    assert tb.add_q3d_dynamic_component(dynamic_link, "Q3D_MSbend", "Setup1GHz", "MSbX_021GHz", "Original")
    with pytest.raises(ValueError):
        tb.add_q3d_dynamic_component(dynamic_link, "Q3D_MSbend", "Setup1GHz", "sweep1", "Original")
    with pytest.raises(ValueError):
        tb.add_q3d_dynamic_component(dynamic_link, "Q3D_MSbend", "setup", "sweep1", "Original")
    example_project_copy = test_tmp_dir / f"{tb.project_name}_copy.aedt"
    shutil.copyfile(dynamic_link, example_project_copy)
    assert tb.add_q3d_dynamic_component(
        str(example_project_copy),
        "2D_Extractor_Cable",
        "MySetupAuto",
        "sweep1",
        "Original",
        model_depth="100mm",
    )
    assert tb.add_q3d_dynamic_component(str(q3d_dynamic_link), "Q3D_MSbend", "Setup1GHz", "MSbX_021GHz", "Original")
    with pytest.raises(ValueError):
        tb.add_q3d_dynamic_component("", "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm")
    with pytest.raises(ValueError):
        tb.add_q3d_dynamic_component(
            "invalid", "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm"
        )
    # shutil.rmtree(example_project_copy)
    tb.close_project(name=tb.project_name, save=False)


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_add_sml_component(aedt_app, test_tmp_dir):
    file1_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "Thermal_ROM_SML.sml"
    input_file = shutil.copy2(file1_o, test_tmp_dir / "Thermal_ROM_SML.sml")

    pins_names = ["Input1_InternalHeatGeneration", "Input2_HeatFlow", "Output1_Temp1,Output2_Temp2"]
    assert aedt_app.modeler.schematic.create_component_from_sml(
        input_file=str(input_file), model="Thermal_ROM_SML", pins_names=pins_names
    )
    rom1 = aedt_app.modeler.schematic.create_component("ROM1", "", "Thermal_ROM_SML")

    assert aedt_app.modeler.schematic.update_quantity_value(rom1.composed_name, "Input2_HeatFlow", "1")


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_create_subsheet(aedt_app):
    aedt_app.create_subsheet("subsheet", "parentsheet")
    assert "parentsheet" in aedt_app.design_list
    assert len(aedt_app.odesign.GetSubDesigns()) > 0


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Feature not available before 2025R1")
def test_add_excitation_model(add_app, test_tmp_dir):
    file1_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "TB_excitation_model.aedt"
    excitation_model = shutil.copy2(file1_o, test_tmp_dir / "TB_excitation_model.aedt")

    tb = add_app(
        application=TwinBuilder,
        project=excitation_model,
        design="2 simplorer circuit",
    )
    project_name = tb.project_name
    dkp = tb.desktop
    maxwell_app = dkp[[project_name, "1 maxwell busbar"]]

    assert not tb.add_excitation_model(project="invalid", design="1 maxwell busbar")
    assert not tb.add_excitation_model(project=tb.project_path, design="1 maxwell busbar")
    assert not tb.add_excitation_model(project=project_name, design="1 maxwell busbar", excitations={"a": []})

    excitations = {}
    for e in maxwell_app.excitations_by_type["Winding Group"]:
        excitations[e.name] = [1, True, e.props["Type"], False]

    assert not tb.add_excitation_model(project=project_name, design="1 maxwell busbar", excitations=excitations)

    excitations = {}
    for e in maxwell_app.excitations_by_type["Winding Group"]:
        excitations[e.name] = ["20", True, e.props["Type"], False]

    assert tb.add_excitation_model(project=tb.project_file, design="1 maxwell busbar", excitations=excitations)

    assert tb.add_excitation_model(project=project_name, design="1 maxwell busbar", excitations=excitations)

    assert tb.add_excitation_model(
        project=project_name,
        design="1 maxwell busbar",
        excitations=excitations,
        use_default_values=False,
        start="1ms",
        stop="5ms",
    )

    assert tb.add_excitation_model(project=project_name, design="1 maxwell busbar")

    for e in maxwell_app.excitations_by_type["Winding Group"]:
        excitations[e.name] = ["20", True, e.props["Type"], True]

    assert tb.add_excitation_model(project=project_name, design="1 maxwell busbar", excitations=excitations)

    example_project_copy = test_tmp_dir / f"{project_name}_copy.aedt"
    shutil.copyfile(excitation_model, example_project_copy)
    assert tb.add_excitation_model(
        project=str(example_project_copy), design="1 maxwell busbar", excitations=excitations
    )

    # shutil.rmtree(example_project_copy)
    tb.close_project(name=project_name, save=False)
