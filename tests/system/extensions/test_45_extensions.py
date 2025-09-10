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
