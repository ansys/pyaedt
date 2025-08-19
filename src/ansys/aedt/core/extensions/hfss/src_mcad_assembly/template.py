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

DATA = {
    "coordinate_system": {
        "GLOBAL_2": {"origin": ["100mm", "0mm", "0mm"], "reference_cs": "Global"},
        "CS_CLAMP": {"origin": ["-130mm", "80mm", "12mm"], "reference_cs": "GLOBAL_2"},
    },
    "assembly": {
        "case": {
            "component_type": "mcad",
            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\Chassi.a3dcomp",
            "reference_coordinate_system": "Global",
            "target_coordinate_system": "GLOBAL_2",
            "arrange": [
                {"operation": "rotate", "axis": "X", "angle": "0deg"},
                {"operation": "move", "vector": ["0mm", "0mm", "0mm"]},
            ],
            "sub_components": {
                "pcb": {
                    "component_type": "ecad",
                    "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\DCDC-Converter-App_main.aedbcomp",
                    "target_coordinate_system": "Guiding_Pin",
                    "layout_coordinate_systems": ["CABLE1_via_65", "CABLE2_via_65", "H0_via_65"],
                    "reference_coordinate_system": "H0_via_65",
                    "arrange": [
                        {"operation": "rotate", "axis": "X", "angle": "0deg"},
                        {"operation": "move", "vector": ["0mm", "0mm", "0mm"]},
                    ],
                    "sub_components": {
                        "cable_1": {
                            "component_type": "mcad",
                            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\Cable_1.a3dcomp",
                            "target_coordinate_system": "CABLE1_via_65",
                        },
                        "cable_2": {
                            "component_type": "mcad",
                            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\Cable_1.a3dcomp",
                            "target_coordinate_system": "CABLE2_via_65",
                        },
                    },
                }
            },
        },
        "clamp_monitor": {
            "component_type": "mcad",
            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\BCI_MONITORING_CLAMP.a3dcomp",
            "reference_coordinate_system": "Global",
            "target_coordinate_system": "CS_CLAMP",
        },
    },
}
