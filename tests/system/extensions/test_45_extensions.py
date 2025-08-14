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

    def test_04_project_report(self, add_app):
        aedtapp = add_app(
            application=ansys.aedt.core.Hfss,
            project_name=report,
            subfolder=test_subfolder,
        )

        from ansys.aedt.core.extensions.project.create_report import main

        assert main({"is_test": True})

        assert os.path.isfile(os.path.join(aedtapp.working_directory, "AEDT_Results.pdf"))
        aedtapp.close_project(aedtapp.project_name)

    def test_06_project_import_stl(self, add_app, local_scratch):
        aedtapp = add_app(
            application=ansys.aedt.core.Hfss,
            project_name="workflow_stl",
        )

        from ansys.aedt.core.extensions.project.import_nastran import main

        file_path = shutil.copy(
            os.path.join(local_path, "example_models", "T20", "sphere.stl"),
            os.path.join(local_scratch.path, "sphere.stl"),
        )

        assert main(
            {
                "is_test": True,
                "file_path": file_path,
                "lightweight": True,
                "decimate": 0.0,
                "planar": True,
            }
        )

        assert len(aedtapp.modeler.object_list) == 1
        aedtapp.close_project(aedtapp.project_name)

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_07_twinbuilder_convert_circuit(self, add_app):
        aedtapp = add_app(
            application=ansys.aedt.core.TwinBuilder,
            project_name=twinbuilder_circuit,
            subfolder=test_subfolder,
        )

        from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import main

        assert main({"is_test": True})

        aedtapp.close_project()

    @pytest.mark.skipif(
        is_linux,
        reason="Test failing randomly in 2025.2, it must be reviewed.",
    )
    def test_08_configure_a3d(self, local_scratch):
        from ansys.aedt.core.extensions.project.configure_edb import main

        configuration_path = shutil.copy(
            os.path.join(
                extensions_local_path,
                "example_models",
                "T45",
                "ports.json",
            ),
            os.path.join(local_scratch.path, "ports.json"),
        )
        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1.aedb")
        local_scratch.copyfolder(
            os.path.join(
                extensions_local_path,
                "example_models",
                "T45",
                "ANSYS-HSD_V1.aedb",
            ),
            file_path,
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
                    {
                        "project_file": file_path,
                        "file_path_save": configuration_path.replace(".json", "_1.json"),
                    }
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
                    {
                        "project_file": file_path,
                        "file_path_save": configuration_path.replace(".json", "_1.json"),
                    }
                ],
                "siwave_load": [],
                "siwave_export": [],
            },
        )

    def test_15_import_asc(self, local_scratch, add_app):
        aedtapp = add_app("Circuit", application=ansys.aedt.core.Circuit)

        from ansys.aedt.core.extensions.circuit.import_schematic import ImportSchematicData
        from ansys.aedt.core.extensions.circuit.import_schematic import main

        file_path = os.path.join(local_path, "example_models", "T21", "butter.asc")
        assert main(ImportSchematicData(file_extension=file_path))

        file_path = os.path.join(local_path, "example_models", "T21", "netlist_small.cir")
        assert main(ImportSchematicData(file_extension=file_path))

        file_path = os.path.join(local_path, "example_models", "T21", "Schematic1.qcv")
        assert main(ImportSchematicData(file_extension=file_path))

        file_path_invented = os.path.join(local_path, "example_models", "T21", "butter_invented.asc")
        with pytest.raises(Exception) as execinfo:
            main(ImportSchematicData(file_extension=file_path_invented))
            assert execinfo.args[0] == "File does not exist."
        aedtapp.close_project()

    def test_17_choke_designer(self, local_scratch):
        from ansys.aedt.core.extensions.hfss.choke_designer import main

        choke_config = {
            "Number of Windings": {
                "1": True,
                "2": False,
                "3": False,
                "4": False,
            },
            "Layer": {
                "Simple": True,
                "Double": False,
                "Triple": False,
            },
            "Layer Type": {"Separate": True, "Linked": False},
            "Similar Layer": {"Similar": True, "Different": False},
            "Mode": {"Differential": True, "Common": False},
            "Wire Section": {
                "None": False,
                "Hexagon": False,
                "Octagon": False,
                "Circle": True,
            },
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
            "Mid Winding": {
                "Turns": 25,
                "Coil Pit(deg)": 0.1,
                "Occupation(%)": 0,
            },
            "Inner Winding": {
                "Turns": 4,
                "Coil Pit(deg)": 0.1,
                "Occupation(%)": 0,
            },
            "Settings": {"Units": "mm"},
            "Create Component": {"True": True, "False": False},
        }
        extension_args = {
            "is_test": True,
            "choke_config": choke_config,
        }
        assert main(extension_args)

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_18_via_merging(self, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.via_clustering_extension import main

        file_path = os.path.join(local_scratch.path, "test_via_merging.aedb")
        new_file = os.path.join(local_scratch.path, "new_test_via_merging.aedb")
        local_scratch.copyfolder(
            os.path.join(
                extensions_local_path,
                "example_models",
                "T45",
                "test_via_merging.aedb",
            ),
            file_path,
        )
        _input_ = {
            "contour_list": [
                [
                    [0.143, 0.04],
                    [0.1476, 0.04],
                    [0.1476, 0.03618],
                    [0.143, 0.036],
                ]
            ],
            "is_batch": True,
            "start_layer": "TOP",
            "stop_layer": "INT5",
            "design_name": "test",
            "aedb_path": file_path,
            "new_aedb_path": new_file,
            "test_mode": True,
        }
        assert main(_input_)

    def test_fields_distribution(self, add_app, local_scratch):
        from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

        file_path = os.path.join(local_scratch.path, "loss_distribution.csv")

        aedtapp = add_app(
            application=ansys.aedt.core.Maxwell2d,
            subfolder=test_subfolder,
            project_name=fields_distribution,
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

        points_file = os.path.join(
            extensions_local_path,
            "example_models",
            test_subfolder,
            "hv_terminal.pts",
        )
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
            os.path.join(
                extensions_local_path,
                "example_models",
                "T45",
                "ANSYS-HSD_V1.aedb",
            ),
            file_path,
        )

        h3d = add_app(
            file_path,
            application=ansys.aedt.core.Hfss3dLayout,
            just_open=True,
        )
        h3d.save_project()
        app_antipad = BackendAntipad(h3d)
        app_antipad.create(
            selections=["Via79", "Via78"],
            radius="1mm",
            race_track=True,
        )
        h3d.close_project()

    @pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
    def test_layout_design_toolkit_antipad_2(self, add_app, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design_toolkit import BackendAntipad

        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1_antipad_2.aedb")

        local_scratch.copyfolder(
            os.path.join(
                extensions_local_path,
                "example_models",
                "T45",
                "ANSYS-HSD_V1.aedb",
            ),
            file_path,
        )

        h3d = add_app(
            file_path,
            application=ansys.aedt.core.Hfss3dLayout,
            just_open=True,
        )

        h3d.save_project()

        app_antipad = BackendAntipad(h3d)
        app_antipad.create(
            selections=["Via1", "Via2"],
            radius="1mm",
            race_track=False,
        )
        h3d.close_project()

    @pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
    def test_layout_design_toolkit_micro_via(self, add_app, local_scratch):
        from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design_toolkit import BackendMircoVia

        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1_antipad_3.aedb")

        local_scratch.copyfolder(
            os.path.join(
                extensions_local_path,
                "example_models",
                "T45",
                "ANSYS-HSD_V1.aedb",
            ),
            file_path,
        )

        h3d = add_app(
            file_path,
            application=ansys.aedt.core.Hfss3dLayout,
            just_open=True,
        )

        h3d.save_project()

        app_microvia = BackendMircoVia(h3d)
        app_microvia.create(selection=["v40h20-1"], signal_only=True, angle=75)
        h3d.close_project()
