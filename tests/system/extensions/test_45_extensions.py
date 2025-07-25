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

import pytest

import ansys.aedt.core
from ansys.aedt.core.generic.settings import is_linux
from tests.system.extensions.conftest import local_path as extensions_local_path
from tests.system.general.conftest import local_path

push_project = "push_excitation"
export_3d_project = "export"
twinbuilder_circuit = "TB_test"
report = "report"
m2d_electrostatic = "maxwell_fields_calculator"
fields_distribution = "transformer_loss_distribution"

test_subfolder = "T45"
TEST_REVIEW_FLAG = True


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, desktop):
        os.environ["PYAEDT_SCRIPT_PORT"] = str(desktop.port)
        os.environ["PYAEDT_SCRIPT_VERSION"] = desktop.aedt_version_id

    def test_02_hfss_push(self, add_app):
        aedtapp = add_app(project_name=push_project, subfolder=test_subfolder)

        from ansys.aedt.core.extensions.hfss.push_excitation_from_file import main

        # No choice
        file_path = os.path.join(local_path, "example_models", "T20", "Sinusoidal.csv")
        assert main({"is_test": True, "file_path": file_path, "choice": ""})
        aedtapp.save_project()
        assert not aedtapp.design_datasets

        # Correct choice
        assert main({"is_test": True, "file_path": file_path, "choice": "1:1"})
        aedtapp.save_project()
        assert aedtapp.design_datasets
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_q3d(self, local_scratch, add_app):
        aedtapp = add_app(
            application=ansys.aedt.core.Hfss3dLayout, project_name=export_3d_project, subfolder=test_subfolder
        )

        aedtapp.save_project(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_q3d.aedt"))

        from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import main

        assert main({"is_test": True, "choice": "Export to Q3D"})

        assert os.path.isfile(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_q3d_Q3D.aedt"))
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_Q3D")
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_icepak(self, local_scratch, add_app):
        aedtapp = add_app(
            application=ansys.aedt.core.Hfss3dLayout, project_name=export_3d_project, subfolder=test_subfolder
        )

        aedtapp.save_project(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_icepak.aedt"))

        from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import main

        assert main({"is_test": True, "choice": "Export to Icepak"})

        assert os.path.isfile(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_icepak_IPK.aedt"))
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_IPK")
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_maxwell(self, local_scratch, add_app):
        aedtapp = add_app(
            application=ansys.aedt.core.Hfss3dLayout, project_name=export_3d_project, subfolder=test_subfolder
        )

        aedtapp.save_project(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_maxwell.aedt"))

        from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import main

        assert main({"is_test": True, "choice": "Export to Maxwell 3D"})

        assert os.path.isfile(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_maxwell_M3D.aedt"))
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_M3D")
        aedtapp.close_project(aedtapp.project_name)

    def test_04_project_report(self, add_app):
        aedtapp = add_app(application=ansys.aedt.core.Hfss, project_name=report, subfolder=test_subfolder)

        from ansys.aedt.core.extensions.project.create_report import main

        assert main({"is_test": True})

        assert os.path.isfile(os.path.join(aedtapp.working_directory, "AEDT_Results.pdf"))
        aedtapp.close_project(aedtapp.project_name)

    def test_06_project_import_stl(self, add_app, local_scratch):
        aedtapp = add_app(application=ansys.aedt.core.Hfss, project_name="workflow_stl")

        from ansys.aedt.core.extensions.project.import_nastran import main

        file_path = shutil.copy(
            os.path.join(local_path, "example_models", "T20", "sphere.stl"),
            os.path.join(local_scratch.path, "sphere.stl"),
        )

        assert main({"is_test": True, "file_path": file_path, "lightweight": True, "decimate": 0.0, "planar": True})

        assert len(aedtapp.modeler.object_list) == 1
        aedtapp.close_project(aedtapp.project_name)

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_07_twinbuilder_convert_circuit(self, add_app):
        aedtapp = add_app(
            application=ansys.aedt.core.TwinBuilder, project_name=twinbuilder_circuit, subfolder=test_subfolder
        )

        from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import main

        assert main({"is_test": True})

        aedtapp.close_project()

    def test_08_configure_a3d(self, local_scratch):
        from ansys.aedt.core.extensions.project.configure_edb import main

        configuration_path = shutil.copy(
            os.path.join(extensions_local_path, "example_models", "T45", "ports.json"),
            os.path.join(local_scratch.path, "ports.json"),
        )
        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1.aedb")
        local_scratch.copyfolder(
            os.path.join(extensions_local_path, "example_models", "T45", "ANSYS-HSD_V1.aedb"), file_path
        )

        main(
            is_test=True,
            execute={
                "aedt_load": [
                    {
                        "project_file": file_path,
                        "file_cfg_path": configuration_path,
                        "file_save_path": file_path.replace(".aedb", "_1.aedt"),
                    }
                ],
                "aedt_export": [
                    {"project_file": file_path, "file_path_save": configuration_path.replace(".json", "_1.json")}
                ],
                "active_load": [],
                "active_export": [],
                "siwave_load": [],
                "siwave_export": [],
            },
        )

        main(
            is_test=True,
            execute={
                "aedt_load": [],
                "aedt_export": [],
                "active_load": [
                    {
                        "project_file": file_path,
                        "file_cfg_path": configuration_path,
                        "file_save_path": file_path.replace(".aedb", "_1.aedt"),
                    }
                ],
                "active_export": [
                    {"project_file": file_path, "file_path_save": configuration_path.replace(".json", "_1.json")}
                ],
                "siwave_load": [],
                "siwave_export": [],
            },
        )

    def test_10_push_excitation_3dl(self, local_scratch, desktop):
        from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import main

        project_path = shutil.copy(
            os.path.join(local_path, "example_models", "T41", "test_post_3d_layout_solved_23R2.aedtz"),
            os.path.join(local_scratch.path, "test_post_3d_layout_solved_23R2.aedtz"),
        )

        h3d = ansys.aedt.core.Hfss3dLayout(project_path, version=desktop.aedt_version_id, port=str(desktop.port))

        file_path = os.path.join(local_path, "example_models", "T20", "Sinusoidal.csv")
        assert main({"is_test": True, "file_path": file_path, "choice": ""})
        h3d.save_project()
        assert not h3d.design_datasets

        # Correct choice
        assert main({"is_test": True, "file_path": file_path, "choice": "Port1"})
        h3d.save_project()
        # In 3D Layout datasets are not retrieved
        # assert h3d.design_datasets
        h3d.close_project(h3d.project_name)

    def test_12_export_layout(self, add_app):
        from ansys.aedt.core.extensions.hfss3dlayout.export_layout import main

        app = add_app("ANSYS-HSD_V1", application=ansys.aedt.core.Hfss3dLayout, subfolder=test_subfolder)

        assert main({"is_test": True, "export_ipc": True, "export_configuration": True, "export_bom": True})
        app.close_project()

    def test_13_parametrize_layout(self, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import main

        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1_param.aedb")

        local_scratch.copyfolder(
            os.path.join(extensions_local_path, "example_models", "T45", "ANSYS-HSD_V1.aedb"), file_path
        )

        assert main(
            {
                "is_test": True,
                "aedb_path": file_path,
                "parametrize_layers": True,
                "parametrize_materials": True,
                "parametrize_padstacks": True,
                "parametrize_traces": True,
                "nets_filter": ["GND"],
                "expansion_polygon_mm": 0.1,
                "expansion_void_mm": 0.1,
                "relative_parametric": True,
                "project_name": "new_parametrized",
            }
        )

    def test_15_import_asc(self, local_scratch, add_app):
        aedtapp = add_app("Circuit", application=ansys.aedt.core.Circuit)

        from ansys.aedt.core.extensions.circuit.import_schematic import main

        file_path = os.path.join(local_path, "example_models", "T21", "butter.asc")
        assert main({"is_test": True, "asc_file": file_path})

        file_path = os.path.join(local_path, "example_models", "T21", "netlist_small.cir")
        assert main({"is_test": True, "asc_file": file_path})

        file_path = os.path.join(local_path, "example_models", "T21", "Schematic1.qcv")
        assert main({"is_test": True, "asc_file": file_path})

        file_path_invented = os.path.join(local_path, "example_models", "T21", "butter_invented.asc")
        with pytest.raises(Exception) as execinfo:
            main({"is_test": True, "asc_file": file_path_invented})
            assert execinfo.args[0] == "File does not exist."
        aedtapp.close_project()

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_16_arbitrary_waveport(self, local_scratch):
        import tempfile

        from ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports import main

        file_path = os.path.join(local_scratch.path, "waveport.aedb")

        temp_dir = tempfile.TemporaryDirectory(suffix=".arbitrary_waveport_test")

        local_scratch.copyfolder(
            os.path.join(extensions_local_path, "example_models", "T45", "waveport.aedb"), file_path
        )

        assert main({"is_test": True, "working_path": temp_dir.name, "source_path": file_path, "mounting_side": "top"})

        assert os.path.isfile(os.path.join(temp_dir.name, "wave_port.a3dcomp"))

        temp_dir.cleanup()

    def test_17_choke_designer(self, local_scratch):
        from ansys.aedt.core.extensions.hfss.choke_designer import main

        choke_config = {
            "Number of Windings": {"1": True, "2": False, "3": False, "4": False},
            "Layer": {"Simple": True, "Double": False, "Triple": False},
            "Layer Type": {"Separate": True, "Linked": False},
            "Similar Layer": {"Similar": True, "Different": False},
            "Mode": {"Differential": True, "Common": False},
            "Wire Section": {"None": False, "Hexagon": False, "Octagon": False, "Circle": True},
            "Core": {
                "Name": "Core",
                "Material": "ferrite",
                "Inner Radius": 20,
                "Outer Radius": 30,
                "Height": 10,
                "Chamfer": 0.8,
            },
            "Outer Winding": {
                "Name": "Winding",
                "Material": "copper",
                "Inner Radius": 20,
                "Outer Radius": 30,
                "Height": 10,
                "Wire Diameter": 1.5,
                "Turns": 20,
                "Coil Pit(deg)": 0.1,
                "Occupation(%)": 0,
            },
            "Mid Winding": {"Turns": 25, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
            "Inner Winding": {"Turns": 4, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
            "Settings": {"Units": "mm"},
            "Create Component": {"True": True, "False": False},
        }
        extension_args = {"is_test": True, "choke_config": choke_config}
        assert main(extension_args)

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_18_via_merging(self, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.via_clustering_extension import main

        file_path = os.path.join(local_scratch.path, "test_via_merging.aedb")
        new_file = os.path.join(local_scratch.path, "new_test_via_merging.aedb")
        local_scratch.copyfolder(
            os.path.join(extensions_local_path, "example_models", "T45", "test_via_merging.aedb"), file_path
        )
        _input_ = {
            "contour_list": [[[0.143, 0.04], [0.1476, 0.04], [0.1476, 0.03618], [0.143, 0.036]]],
            "is_batch": True,
            "start_layer": "TOP",
            "stop_layer": "INT5",
            "design_name": "test",
            "aedb_path": file_path,
            "new_aedb_path": new_file,
            "test_mode": True,
        }
        assert main(_input_)

    @pytest.mark.skipif(is_linux, reason="Simulation takes too long in Linux machine.")
    def test_19_shielding_effectiveness(self, add_app, local_scratch):
        aedtapp = add_app(application=ansys.aedt.core.Hfss, project_name="se")

        from ansys.aedt.core.extensions.hfss.shielding_effectiveness import main

        assert not main(
            {
                "is_test": True,
                "sphere_size": 0.01,
                "x_pol": 0.0,
                "y_pol": 0.1,
                "z_pol": 1.0,
                "dipole_type": "Electric",
                "frequency_units": "GHz",
                "start_frequency": 0.1,
                "stop_frequency": 1,
                "points": 5,
                "cores": 4,
            }
        )

        aedtapp.modeler.create_waveguide(origin=[0, 0, 0], wg_direction_axis=0)

        assert main(
            {
                "is_test": True,
                "sphere_size": 0.01,
                "x_pol": 0.0,
                "y_pol": 0.1,
                "z_pol": 1.0,
                "dipole_type": "Electric",
                "frequency_units": "GHz",
                "start_frequency": 0.1,
                "stop_frequency": 0.2,
                "points": 2,
                "cores": 2,
            }
        )

        assert len(aedtapp.post.all_report_names) == 2
        aedtapp.close_project(aedtapp.project_name)

    def test_fields_distribution(self, add_app, local_scratch):
        from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

        file_path = os.path.join(local_scratch.path, "loss_distribution.csv")

        aedtapp = add_app(
            application=ansys.aedt.core.Maxwell2d, subfolder=test_subfolder, project_name=fields_distribution
        )

        assert main(
            {
                "is_test": True,
                "points_file": "",
                "export_file": file_path,
                "export_option": "Ohmic_loss",
                "objects_list": ["hv_terminal"],
                "solution_option": "Setup1 : LastAdaptive",
            }
        )
        assert os.path.isfile(file_path)

        points_file = os.path.join(extensions_local_path, "example_models", test_subfolder, "hv_terminal.pts")
        assert main(
            {
                "is_test": True,
                "points_file": points_file,
                "export_file": file_path,
                "export_option": "Ohmic_loss",
                "objects_list": ["hv_terminal"],
                "solution_option": "Setup1 : LastAdaptive",
            }
        )
        assert os.path.isfile(file_path)

        assert main(
            {
                "is_test": True,
                "points_file": "",
                "export_file": file_path,
                "export_option": "Ohmic_loss",
                "objects_list": ["hv_terminal", "lv_turn1"],
                "solution_option": "Setup1 : LastAdaptive",
            }
        )
        assert os.path.isfile(file_path)

        assert main(
            {
                "is_test": True,
                "points_file": "",
                "export_file": file_path,
                "export_option": "Ohmic_loss",
                "objects_list": "",
                "solution_option": "Setup1 : LastAdaptive",
            }
        )
        assert os.path.isfile(file_path)

        assert main(
            {
                "is_test": True,
                "points_file": "",
                "export_file": file_path,
                "export_option": "SurfaceAcForceDensity",
                "objects_list": ["hv_terminal"],
                "solution_option": "Setup1 : LastAdaptive",
            }
        )
        assert os.path.isfile(file_path)

        file_path = os.path.join(local_scratch.path, "loss_distribution.npy")
        assert main(
            {
                "is_test": True,
                "points_file": "",
                "export_file": file_path,
                "export_option": "SurfaceAcForceDensity",
                "objects_list": ["hv_terminal"],
                "solution_option": "Setup1 : LastAdaptive",
            }
        )
        assert os.path.isfile(file_path)

        aedtapp.close_project(aedtapp.project_name)

    @pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
    def test_layout_design_toolkit_antipad_1(self, add_app, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design_toolkit import BackendAntipad

        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1_antipad_1.aedb")

        local_scratch.copyfolder(
            os.path.join(extensions_local_path, "example_models", "T45", "ANSYS-HSD_V1.aedb"), file_path
        )

        h3d = add_app(file_path, application=ansys.aedt.core.Hfss3dLayout, just_open=True)
        h3d.save_project()
        app_antipad = BackendAntipad(h3d)
        app_antipad.create(selections=["Via79", "Via78"], radius="1mm", race_track=True)
        h3d.close_project()

    @pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
    def test_layout_design_toolkit_antipad_2(self, add_app, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design_toolkit import BackendAntipad

        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1_antipad_2.aedb")

        local_scratch.copyfolder(
            os.path.join(extensions_local_path, "example_models", "T45", "ANSYS-HSD_V1.aedb"), file_path
        )

        h3d = add_app(file_path, application=ansys.aedt.core.Hfss3dLayout, just_open=True)

        h3d.save_project()

        app_antipad = BackendAntipad(h3d)
        app_antipad.create(selections=["Via1", "Via2"], radius="1mm", race_track=False)
        h3d.close_project()

    @pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
    def test_layout_design_toolkit_micro_via(self, add_app, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design_toolkit import BackendMircoVia

        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1_antipad_3.aedb")

        local_scratch.copyfolder(
            os.path.join(extensions_local_path, "example_models", "T45", "ANSYS-HSD_V1.aedb"), file_path
        )

        h3d = add_app(file_path, application=ansys.aedt.core.Hfss3dLayout, just_open=True)

        h3d.save_project()

        app_microvia = BackendMircoVia(h3d)
        app_microvia.create(selection=["v40h20-1"], signal_only=True, angle=75)
        h3d.close_project()

    def test_citcuit_configuration(self, local_scratch):
        from ansys.aedt.core.extensions.circuit.circuit_configuration import main

        file_path = os.path.join(local_scratch.path, "config.aedt")

        configuration_path = shutil.copy(
            os.path.join(extensions_local_path, "example_models", "T45", "circuit_config.json"),
            os.path.join(local_scratch.path, "circuit_config.json"),
        )

        main(
            is_test=True,
            execute={
                "aedt_load": [
                    {
                        "project_file": file_path,
                        "file_cfg_path": configuration_path,
                        "file_save_path": file_path.replace(".aedt", "_1.aedt"),
                    }
                ],
                "aedt_export": [
                    {"project_file": file_path, "file_path_save": configuration_path.replace(".json", "_1.json")}
                ],
                "active_load": [],
                "active_export": [],
            },
        )

        main(
            is_test=True,
            execute={
                "aedt_load": [],
                "aedt_export": [],
                "active_load": [
                    {
                        "project_file": file_path,
                        "file_cfg_path": configuration_path,
                        "file_save_path": file_path.replace(".aedb", "_1.aedt"),
                    }
                ],
                "active_export": [
                    {"project_file": file_path, "file_path_save": configuration_path.replace(".json", "_1.json")}
                ],
            },
        )
