# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import json

import pytest

from ansys.aedt.core.application import _get_obj_data


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class."""
    return


SWEEP_LNA_OBJ_DATA = {
    "data_1": ["Sweep_LNA"],
    "data_2": [
        {
            "name": "SimSetup",
            "values": [
                {"name": "DataBlockID", "value": 16},
                {"name": "OptionName", "value": "Default Options"},
                {"name": "AdditionalOptions", "value": ""},
                {"name": "AlterBlockName", "value": ""},
                {"name": "FilterText", "value": ""},
                {"name": "AnalysisEnabled", "value": 1},
                {"name": "HasTDRComp", "value": 0},
                {"name": "OutputQuantities", "values": []},
                {"name": "NoiseOutputQuantities", "values": []},
                {"name": "Name", "value": "Sweep_LNA"},
                {"LinearFrequencyData": [False, 0.1, False, "", False]},
                {
                    "name": "SweepDefinition",
                    "values": [
                        {"name": "Variable", "value": "Freq"},
                        {"name": "Data", "value": "LIN 1GHz 2GHz 0.01GHz 11GHz 12GHz 13.4GHz"},
                        {"name": "OffsetF1", "value": False},
                        {"name": "Synchronize", "value": 0},
                    ],
                },
                {
                    "name": "SweepDefinition",
                    "values": [
                        {"name": "Variable", "value": "Temp"},
                        {"name": "Data", "value": "DEC 20cel 100cel 81"},
                        {"name": "OffsetF1", "value": False},
                        {"name": "Synchronize", "value": 0},
                    ],
                },
            ],
        }
    ],
}


class DummyChild:
    def __init__(self, payload) -> None:
        self._payload = payload

    def GetObjData(self):
        return json.dumps(self._payload)


def test_get_obj_data_collates_duplicate_sweep_definitions() -> None:
    props = _get_obj_data(DummyChild(SWEEP_LNA_OBJ_DATA))

    assert isinstance(props["SweepDefinition"], list)
    assert len(props["SweepDefinition"]) == 2
    assert props["SweepDefinition"][0]["Variable"] == "Freq"
    assert props["SweepDefinition"][0]["Data"] == "LIN 1GHz 2GHz 0.01GHz 11GHz 12GHz 13.4GHz"
    assert props["SweepDefinition"][1]["Variable"] == "Temp"
    assert props["SweepDefinition"][1]["Data"] == "DEC 20cel 100cel 81"
    assert props["LinearFrequencyData"] == [False, 0.1, False, "", False]


def test_get_obj_data_keeps_single_sweep_definition_as_dict() -> None:
    payload = {
        "data_2": [
            {
                "name": "SimSetup",
                "values": [
                    {"name": "Name", "value": "Sweep1"},
                    {
                        "name": "SweepDefinition",
                        "values": [
                            {"name": "Variable", "value": "Freq"},
                            {"name": "Data", "value": "LIN 1GHz 2GHz 0.01GHz"},
                        ],
                    },
                ],
            }
        ]
    }
    props = _get_obj_data(DummyChild(payload))

    assert isinstance(props["SweepDefinition"], dict)
    assert props["SweepDefinition"]["Variable"] == "Freq"
    assert props["SweepDefinition"]["Data"] == "LIN 1GHz 2GHz 0.01GHz"


def test_get_obj_data_returns_empty_for_missing_child() -> None:
    assert _get_obj_data(None) == {}
