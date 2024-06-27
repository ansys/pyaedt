# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from _unittest.conftest import config

# from ..filtersolutions_resources import resource_path
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.generic.general_methods import is_linux

from ..resources import read_resource_file


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_lumped_c_node_capacitor(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.c_node_capacitor == "0"
        lumpdesign.leads_and_nodes.c_node_capacitor = "1n"
        assert lumpdesign.leads_and_nodes.c_node_capacitor == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("c_node_capacitor.ckt")

    def test_lumped_c_lead_inductor(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.c_lead_inductor == "0"
        lumpdesign.leads_and_nodes.c_lead_inductor = "1n"
        assert lumpdesign.leads_and_nodes.c_lead_inductor == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("c_lead_inductor.ckt")

    def test_lumped_l_node_capacitor(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.l_node_capacitor == "0"
        lumpdesign.leads_and_nodes.l_node_capacitor = "1n"
        assert lumpdesign.leads_and_nodes.l_node_capacitor == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("l_node_capacitor.ckt")

    def test_lumped_l_lead_inductor(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.l_lead_inductor == "0"
        lumpdesign.leads_and_nodes.l_lead_inductor = "1n"
        assert lumpdesign.leads_and_nodes.l_lead_inductor == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("l_lead_inductor.ckt")

    def test_lumped_r_node_capacitor(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.r_node_capacitor == "0"
        lumpdesign.leads_and_nodes.r_node_capacitor = "1n"
        assert lumpdesign.leads_and_nodes.r_node_capacitor == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("r_node_capacitor.ckt")

    def test_lumped_r_lead_inductor(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.r_lead_inductor == "0"
        lumpdesign.leads_and_nodes.r_lead_inductor = "1n"
        assert lumpdesign.leads_and_nodes.r_lead_inductor == "1n"
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("r_lead_inductor.ckt")

    def test_lumped_c_node_compensate(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.c_node_compensate is False
        lumpdesign.leads_and_nodes.c_node_compensate = True
        assert lumpdesign.leads_and_nodes.c_node_compensate
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("c_node_compensate.ckt")

    def test_lumped_l_node_compensate(self):
        lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert lumpdesign.leads_and_nodes.l_node_compensate is False
        lumpdesign.leads_and_nodes.l_node_compensate = True
        assert lumpdesign.leads_and_nodes.l_node_compensate
        assert lumpdesign.topology.circuit_response().splitlines() == read_resource_file("l_node_compensate.ckt")
