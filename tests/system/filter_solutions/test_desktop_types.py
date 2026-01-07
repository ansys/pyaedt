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

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import DESKTOP_VERSION


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
# All these tests are skipped because Filter Solutions open AEDT with COM and there is not a close AEDT mechanism.
# A new way based on PyAEDT will be implemented in 2026R1. So all these tests can not be tested for now.
class TestClass:
    def test_lumped_exported_desktop(self, lumped_design):
        schem_name = lumped_design.export_to_aedt.schematic_name
        schem_name_length = len(schem_name)
        app = lumped_design.export_to_aedt.export_design()
        circuit = lumped_design.export_to_aedt.export_design()
        assert isinstance(circuit, Circuit)
        assert circuit.project_name.split()[0][:schem_name_length] == schem_name
        assert circuit.design_name == schem_name
        assert next(iter(circuit.setup_sweeps_names)) == "FS_Advanced Setup"
        variables = circuit.variable_manager.variables
        assert variables["C1"].value == pytest.approx(1.967e-12)
        assert variables["L2"].value == pytest.approx(1.288e-8)
        assert variables["C3"].value == pytest.approx(6.366e-12)
        app.desktop_class.close_desktop()

    def test_distributed_circuit_exported_desktop(self, distributed_design):
        schem_name = distributed_design.export_to_aedt.schematic_name
        schem_name_length = len(schem_name)
        distributed_design.export_to_aedt.insert_circuit_design = True
        app = distributed_design.export_to_aedt.export_design()
        circuit = distributed_design.export_to_aedt.export_design()
        assert isinstance(circuit, Circuit)
        assert circuit.project_name.split()[0][:schem_name_length] == schem_name
        assert circuit.design_name == schem_name
        assert next(iter(circuit.setup_sweeps_names)) == "FS_Advanced Setup"
        variables = circuit.variable_manager.variables
        assert variables["W1"].value == pytest.approx(5.08e-3)
        assert variables["W2"].value == pytest.approx(3.175e-4)
        assert variables["W3"].value == pytest.approx(5.08e-3)
        assert variables["S1"].value == pytest.approx(3.362e-3)
        assert variables["S2"].value == pytest.approx(2.172e-2)
        assert variables["S3"].value == pytest.approx(1.008e-2)
        app.desktop_class.close_desktop()

    def test_distributed_hfss3dl_exported_desktop(self, distributed_design):
        schem_name = distributed_design.export_to_aedt.schematic_name
        schem_name_length = len(schem_name)
        distributed_design.export_to_aedt.insert_hfss_3dl_design = True
        app = distributed_design.export_to_aedt.export_design()
        hfss3dl = distributed_design.export_to_aedt.export_design()
        assert isinstance(hfss3dl, Hfss3dLayout)
        assert hfss3dl.project_name.split()[0][:schem_name_length] == schem_name
        assert hfss3dl.design_name == schem_name
        assert next(iter(hfss3dl.setup_sweeps_names)) == "FS_Advanced Setup"
        variables = hfss3dl.variable_manager.variables
        assert variables["Win"].value == pytest.approx(1.234e-3)
        assert variables["W1"].value == pytest.approx(5.08e-3)
        assert variables["W2"].value == pytest.approx(3.175e-4)
        assert variables["W3"].value == pytest.approx(5.08e-3)
        assert variables["S1"].value == pytest.approx(3.36225452227e-3)
        assert variables["S2"].value == pytest.approx(2.17231965814e-2)
        assert variables["S3"].value == pytest.approx(1.00773795179e-2)
        app.desktop_class.close_desktop()

    def test_distributed_hfss_exported_desktop(self, distributed_design):
        schem_name = distributed_design.export_to_aedt.schematic_name
        schem_name_length = len(schem_name)
        distributed_design.export_to_aedt.insert_hfss_design = True
        app = distributed_design.export_to_aedt.export_design()
        hfss = distributed_design.export_to_aedt.export_design()
        assert isinstance(hfss, Hfss)
        assert hfss.project_name.split()[0][:schem_name_length] == schem_name
        assert hfss.design_name == schem_name
        assert next(iter(hfss.setup_sweeps_names)) == "FS_Advanced_Setup"
        variables = hfss.variable_manager.variables
        assert variables["Win"].value == pytest.approx(1.234e-3)
        assert variables["W1"].value == pytest.approx(5.08e-3)
        assert variables["W2"].value == pytest.approx(3.175e-4)
        assert variables["W3"].value == pytest.approx(5.08e-3)
        assert variables["S1"].value == pytest.approx(3.36225452227e-3)
        assert variables["S2"].value == pytest.approx(2.17231965814e-2)
        assert variables["S3"].value == pytest.approx(1.00773795179e-2)
        app.desktop_class.close_desktop()
