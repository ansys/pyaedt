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
m2d_electrostatic = "maxwell_fields_calculator"

test_subfolder = "T45"
TEST_REVIEW_FLAG = True


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, desktop):
        os.environ["PYAEDT_SCRIPT_PORT"] = str(desktop.port)
        os.environ["PYAEDT_SCRIPT_VERSION"] = desktop.aedt_version_id

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