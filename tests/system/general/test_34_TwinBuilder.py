# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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
import shutil

from ansys.aedt.core import Desktop
from ansys.aedt.core import TwinBuilder
from ansys.aedt.core.generic.general_methods import is_linux
import pytest

from tests import TESTS_GENERAL_PATH
from tests.system.general.conftest import NONGRAPHICAL
from tests.system.general.conftest import config
from tests.system.general.conftest import desktop_version
from tests.system.general.conftest import new_thread

test_subfolder = "T34"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="TwinBuilderProject", design_name="TwinBuilderDesign1", application=TwinBuilder)
    app.modeler.schematic_units = "mil"
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    examples_list = [
        local_scratch.copyfile(os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "netlist_small.cir")),
        local_scratch.copyfile(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Q2D_ArmouredCableExample.aedt")
        ),
        local_scratch.copyfile(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Q3D_DynamicLink.aedt")
        ),
        local_scratch.copyfile(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "TB_excitation_model.aedt")
        ),
    ]
    return examples_list, None


@pytest.fixture(scope="module", autouse=True)
def desktop():
    d = Desktop(desktop_version, NONGRAPHICAL, new_thread)
    d.disable_autosave()
    d.odesktop.SetDesktopConfiguration("Twin Builder")
    d.odesktop.SetSchematicEnvironment(1)
    yield d
    d.odesktop.SetDesktopConfiguration("All")
    d.odesktop.SetSchematicEnvironment(0)
    d.release_desktop(True, True)


@pytest.mark.skipif(is_linux, reason="Emit API fails on linux.")
class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch, examples):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        self.netlist_file1 = examples[0][0]
        self.dynamic_link = examples[0][1]
        # self.dynamic_link_copy_import = examples[0][2]
        self.q3d_dynamic_link = examples[0][2]
        self.excitation_model = examples[0][3]

    def test_01_create_resistor(self):
        id = self.aedtapp.modeler.schematic.create_resistor("Resistor1", 10, [0, 0])
        assert id.parameters["R"] == "10"

    def test_02_create_inductor(self):
        id = self.aedtapp.modeler.schematic.create_inductor("Inductor1", 1.5, [1000, 0])
        assert id.parameters["L"] == "1.5"

    def test_03_create_capacitor(self):
        id = self.aedtapp.modeler.schematic.create_capacitor("Capacitor1", 7.5, [2000, 0])
        assert id.parameters["C"] == "7.5"

    def test_04_create_diode(self):
        id = self.aedtapp.modeler.schematic.create_diode("Diode1")
        assert id.parameters["VF"] == "0.8V"

    def test_05_create_npn(self):
        name = self.aedtapp.modeler.schematic.create_npn("NPN")
        # Get component info by part name
        assert name.parameters["VF"] == "0.8V"

    def test_06_create_pnp(self):
        id = self.aedtapp.modeler.schematic.create_pnp("PNP")
        assert id.parameters["VF"] == "0.8V"

    def test_07_import_netlist(self):
        self.aedtapp.insert_design("SchematicImport")
        assert self.aedtapp.create_schematic_from_netlist(self.netlist_file1)

    def test_08_set_hmax(self):
        assert self.aedtapp.set_hmax("5ms")

    def test_09_set_hmin(self):
        assert self.aedtapp.set_hmin("0.2ms")

    def test_10_set_hmin(self):
        assert self.aedtapp.set_hmin("2s")

    def test_11_set_end_time(self):
        assert self.aedtapp.set_end_time("5s")

    def test_12_catalog(self):
        comp_catalog = self.aedtapp.modeler.components.components_catalog
        assert not comp_catalog["Capacitors"]
        assert comp_catalog["Aircraft Electrical VHDLAMS\\Basic:lowpass_filter"].props
        assert comp_catalog["Aircraft Electrical VHDLAMS\\Basic:lowpass_filter"].place("LP1")

    def test_13_create_periodic_pulse_wave(self):
        id = self.aedtapp.modeler.schematic.create_periodic_waveform_source("P1", "PULSE", 200, 20, 0, 0, [3000, 0])
        assert id.parameters["AMPL"] == "200"
        assert id.parameters["FREQ"] == "20"

    def test_14_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_15_add_dynamic_link(self, add_app):
        tb = add_app(application=TwinBuilder, project_name=self.dynamic_link, design_name="CableSystem", just_open=True)
        assert tb.add_q3d_dynamic_component(
            "Q2D_ArmouredCableExample", "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm"
        )
        assert tb.add_q3d_dynamic_component(
            self.dynamic_link, "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm"
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
        assert tb.add_q3d_dynamic_component(self.dynamic_link, "Q3D_MSbend", "Setup1GHz", "MSbX_021GHz", "Original")
        with pytest.raises(ValueError):
            tb.add_q3d_dynamic_component(self.dynamic_link, "Q3D_MSbend", "Setup1GHz", "sweep1", "Original")
        with pytest.raises(ValueError):
            tb.add_q3d_dynamic_component(self.dynamic_link, "Q3D_MSbend", "setup", "sweep1", "Original")
        example_project_copy = os.path.join(self.local_scratch.path, tb.project_name + "_copy.aedt")
        shutil.copyfile(self.dynamic_link, example_project_copy)
        assert tb.add_q3d_dynamic_component(
            example_project_copy,
            "2D_Extractor_Cable",
            "MySetupAuto",
            "sweep1",
            "Original",
            model_depth="100mm",
        )
        assert tb.add_q3d_dynamic_component(self.q3d_dynamic_link, "Q3D_MSbend", "Setup1GHz", "MSbX_021GHz", "Original")
        with pytest.raises(ValueError):
            tb.add_q3d_dynamic_component(
                "", "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm"
            )
        with pytest.raises(ValueError):
            tb.add_q3d_dynamic_component(
                "invalid", "2D_Extractor_Cable", "MySetupAuto", "sweep1", "Original", model_depth="100mm"
            )
        # shutil.rmtree(example_project_copy)
        tb.close_project(name=tb.project_name, save=False)

    def test_16_add_sml_component(self, local_scratch):
        self.aedtapp.insert_design("SML")
        input_file = local_scratch.copyfile(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Thermal_ROM_SML.sml")
        )
        pins_names = ["Input1_InternalHeatGeneration", "Input2_HeatFlow", "Output1_Temp1,Output2_Temp2"]
        assert self.aedtapp.modeler.schematic.create_component_from_sml(
            input_file=input_file, model="Thermal_ROM_SML", pins_names=pins_names
        )
        rom1 = self.aedtapp.modeler.schematic.create_component("ROM1", "", "Thermal_ROM_SML")

        assert self.aedtapp.modeler.schematic.update_quantity_value(rom1.composed_name, "Input2_HeatFlow", "1")

    def test_17_create_subsheet(self, local_scratch):
        self.aedtapp.insert_design("SML")
        self.aedtapp.create_subsheet("subsheet", "parentsheet")
        assert "parentsheet" in self.aedtapp.design_list
        assert len(self.aedtapp.odesign.GetSubDesigns()) > 0

    @pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Feature not available before 2025R1")
    def test_18_add_excitation_model(self, add_app):
        tb = add_app(
            application=TwinBuilder,
            project_name=self.excitation_model,
            design_name="2 simplorer circuit",
            just_open=True,
        )
        project_name = tb.project_name
        dkp = tb.desktop_class
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

        example_project_copy = os.path.join(self.local_scratch.path, project_name + "_copy.aedt")
        shutil.copyfile(self.excitation_model, example_project_copy)
        assert tb.add_excitation_model(project=example_project_copy, design="1 maxwell busbar", excitations=excitations)

        # shutil.rmtree(example_project_copy)
        tb.close_project(name=project_name, save=False)
