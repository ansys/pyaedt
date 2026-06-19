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

"""Unit tests for the ``Cable`` straight-wire wire-standard / wire-gauge parsing.

The tests bypass AEDT by mocking ``Cable._cable_properties_parser`` so that the
``Cable`` constructor only exercises the JSON parsing branch under test.
"""

from copy import deepcopy
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.modules.cable_modeling import AWG_WIRE_GAUGES
from ansys.aedt.core.modules.cable_modeling import ISO_WIRE_GAUGES
from ansys.aedt.core.modules.cable_modeling import SUPPORTED_WIRE_STANDARDS
from ansys.aedt.core.modules.cable_modeling import Cable

_EMPTY_LIBRARY = {"CableManager": {"TDSources": None, "Definitions": {}}}


def _build_straight_wire_json(wire_standard: str, wire_gauge: str) -> dict:
    return {
        "Add_Cable": "True",
        "Update_Cable": "False",
        "Remove_Cable": "False",
        "Add_CablesToBundle": "False",
        "Add_Source": "False",
        "Update_Source": "False",
        "Remove_Source": "False",
        "Add_CableHarness": "False",
        "Cable_prop": {
            "CableType": "straight wire",
            "IsJacketTypeInsulation": "False",
            "IsJacketTypeBraidShield": "False",
            "IsJacketTypeNoJacket": "False",
            "UpdatedName": "",
            "CablesToRemove": "",
        },
        "CablesToBundle_prop": {"CablesToAdd": "", "BundleCable": "", "NumberOfCableToAdd": 1},
        "Source_prop": {
            "AddClockSource": "False",
            "UpdateClockSource": "False",
            "AddPwlSource": "False",
            "AddPwlSourceFromFile": "",
            "UpdatePwlSource": "False",
            "UpdatedSourceName": "",
            "SourcesToRemove": "",
        },
        "CableHarness_prop": {},
        "CableManager": {
            "TDSources": {},
            "Definitions": {
                "StWireCable": {
                    "StWireParams": {
                        "WireStandard": wire_standard,
                        "WireGauge": wire_gauge,
                        "CondDiameter": "0.455mm",
                        "CondMaterial": "copper",
                        "InsThickness": "0.2mm",
                        "InsMaterial": "PVC plastic",
                        "InsType": "Thin Wall",
                    },
                    "StWireAttribs": {"Name": "stwire_under_test"},
                }
            },
        },
    }


def _make_app() -> MagicMock:
    app = MagicMock()
    app.toolkit_directory = "."
    app.materials.material_keys.get.return_value = True
    return app


def _make_cable(json_dict: dict) -> Cable:
    app = _make_app()
    with patch.object(Cable, "_cable_properties_parser", return_value=deepcopy(_EMPTY_LIBRARY)):
        return Cable(app, json_dict)


def test_supported_wire_standards_exposes_iso_and_awg() -> None:
    assert SUPPORTED_WIRE_STANDARDS == ("ISO", "AWG")


def test_awg_gauge_list_includes_cat6a_awg25() -> None:
    assert "25" in AWG_WIRE_GAUGES


def test_iso_gauge_list_is_unchanged() -> None:
    assert ISO_WIRE_GAUGES[0] == "0.13"
    assert ISO_WIRE_GAUGES[-1] == "120"


def test_iso_straight_wire_still_parses() -> None:
    cable = _make_cable(_build_straight_wire_json("ISO", "0.13"))
    assert cable.wire_standard == "ISO"
    assert cable.wire_type == "0.13"
    assert cable.conductor_diameter == "0.455mm"
    assert cable.insulation_type == "Thin Wall"


def test_awg_straight_wire_is_accepted() -> None:
    cable = _make_cable(_build_straight_wire_json("AWG", "25"))
    assert cable.wire_standard == "AWG"
    assert cable.wire_type == "25"
    assert cable.conductor_diameter == "0.455mm"
    assert cable.insulation_type == "Thin Wall"


@pytest.mark.parametrize("bad_standard", ["iso", "awg", "metric"])
def test_invalid_wire_standard_is_rejected(bad_standard: str) -> None:
    cable = _make_cable(_build_straight_wire_json(bad_standard, "25"))
    error_call = cable._app.logger.error
    assert error_call.called
    logged = " ".join(str(c.args[0]) for c in error_call.call_args_list)
    assert "Wire standard" in logged or "wire standard" in logged


def test_invalid_awg_gauge_is_rejected() -> None:
    cable = _make_cable(_build_straight_wire_json("AWG", "999"))
    error_call = cable._app.logger.error
    assert error_call.called
    logged = " ".join(str(c.args[0]) for c in error_call.call_args_list)
    assert "Wire gauge" in logged
