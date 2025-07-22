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

import toml

# @patch("tkinter.filedialog.asksaveasfilename")
# def test_via_design_examples_success(mock_asksaveasfilename, tmp_path):
#     """Test the examples provided in the via design extension."""
#     extension = ViaDesignExtension(withdraw=True)

#     for example in EXPORT_EXAMPLES:
#         example_name = example.toml_file_path.stem
#         button = extension.root.nametowidget(f".!notebook.!frame.button_{example_name}")
#         path = tmp_path / f"{example_name}.toml"
#         mock_asksaveasfilename.return_value = path
#         button.invoke()
#         assert path.is_file()

#     extension.root.destroy()


# @patch("tkinter.filedialog.askopenfilename")
# def test_via_design_create_design_from_example(mock_askopenfilename):
#     """Test the creation of a design from examples in the via design extension."""
#     extension = ViaDesignExtension(withdraw=True)

#     for example in EXPORT_EXAMPLES:
#         mock_askopenfilename.return_value = example.toml_file_path
#         button = extension._widgets["create_design"]
#         print(f"Invoking button {button} for example")
#         button.invoke()
#         with example.toml_file_path.open("r") as f:
#             data = toml.load(f)
#         assert data["title"] == extension.active_project_name

#     extension.root.destroy()


def test_custom():
    from pathlib import Path

    from pyedb.extensions.via_design_backend import ViaDesignBackend

    from ansys.aedt.core.extensions.misc import get_aedt_version
    from ansys.aedt.core.extensions.misc import get_port
    from ansys.aedt.core.extensions.misc import get_process_id
    from ansys.aedt.core.extensions.misc import is_student
    from ansys.aedt.core.hfss3dlayout import Hfss3dLayout

    PORT = get_port()
    VERSION = get_aedt_version()
    AEDT_PROCESS_ID = get_process_id()
    IS_STUDENT = is_student()

    current_file = Path(__file__).resolve()
    create_design_path = (
        current_file.parents[3]
        / "src"
        / "ansys"
        / "aedt"
        / "core"
        / "extensions"
        / "project"
        / "resources"
        / "via_design"
        / "pcb_rf.toml"
    )
    assert create_design_path.exists()

    dict_config = toml.load(create_design_path)
    print(f"Loaded configuration: {dict_config}")
    stacked_vias = dict_config.pop("stacked_vias")
    print(f"Stacked vias: {stacked_vias}")
    for param_name, param_value in dict_config["signals"].items():
        stacked_vias_name = param_value["stacked_vias"]
        dict_config["signals"][param_name]["stacked_vias"] = stacked_vias[stacked_vias_name]
    print(f"Signals after processing: {dict_config['signals']}")
    for param_name, param_value in dict_config["differential_signals"].items():
        stacked_vias_name = param_value["stacked_vias"]
        dict_config["differential_signals"][param_name]["stacked_vias"] = stacked_vias[stacked_vias_name]
    print(f"Differential signals after processing: {dict_config['differential_signals']}")

    backend = ViaDesignBackend(dict_config)
    print("Created via design backend.")
    Hfss3dLayout(
        project=backend.app.edbpath,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )
    print("Created Hfss3dLayout instance.")
