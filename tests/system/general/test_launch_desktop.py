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

from ansys.aedt.core import Circuit
from ansys.aedt.core import CircuitNetlist
from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Mechanical
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core import TwinBuilder
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.settings import settings
import pytest

from tests.system.general.conftest import config

settings.lazy_load = False
settings.wait_for_license = True


@pytest.mark.skipif(config["skip_desktop_test"], reason="Desktop tests are not selected by default.")
class TestClass:
    def test_run_desktop_mechanical(self):
        aedtapp = Mechanical()
        assert aedtapp.design_type == "Mechanical"
        assert aedtapp.solution_type == "Steady-State Thermal"
        aedtapp.solution_type = "Modal"
        assert aedtapp.solution_type == "Modal"

    def test_run_desktop_circuit(self):
        aedtapp = Circuit()
        assert aedtapp.design_type == "Circuit Design"
        assert aedtapp.solution_type == "NexximLNA"

    def test_run_desktop_icepak(self):
        aedtapp = Icepak()
        assert aedtapp.design_type == "Icepak"
        assert aedtapp.solution_type == "SteadyState"

    def test_run_desktop_hfss3dlayout(self):
        aedtapp = Hfss3dLayout(ic_mode=True)
        assert aedtapp.design_type == "HFSS 3D Layout Design"
        assert aedtapp.solution_type == "HFSS3DLayout"
        assert aedtapp.ic_mode
        aedtapp.ic_mode = False
        assert not aedtapp.ic_mode

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_run_desktop_twinbuilder(self):
        aedtapp = TwinBuilder()
        assert aedtapp.design_type == "Twin Builder"
        assert aedtapp.solution_type == "TR"

    def test_run_desktop_q2d(self):
        aedtapp = Q2d()
        assert aedtapp.design_type == "2D Extractor"
        assert aedtapp.solution_type == "Open"

    def test_run_desktop_q3d(self):
        aedtapp = Q3d()
        assert aedtapp.design_type == "Q3D Extractor"

    def test_run_desktop_maxwell2d(self):
        aedtapp = Maxwell2d()
        assert aedtapp.design_type == "Maxwell 2D"
        assert aedtapp.solution_type == "Magnetostatic"

    def test_run_desktop_hfss(self):
        aedtapp = Hfss(solution_type="Terminal")
        assert aedtapp.design_type == "HFSS"
        assert "Terminal" in aedtapp.solution_type

    def test_run_desktop_maxwell3d(self):
        aedtapp = Maxwell3d()
        assert aedtapp.design_type == "Maxwell 3D"
        assert aedtapp.solution_type == "Magnetostatic"

    def test_run_desktop_circuit_netlist(self):
        aedtapp = CircuitNetlist()
        assert aedtapp.design_type == "Circuit Netlist"
        assert aedtapp.solution_type == ""

    def test_run_desktop_settings(self):
        aedtapp = Hfss()
        assert aedtapp.desktop_class.disable_optimetrics()
        assert aedtapp.get_registry_key_int("Desktop/Settings/ProjectOptions/EnableLegacyOptimetricsTools") == 0
        assert aedtapp.desktop_class.enable_optimetrics()
        assert aedtapp.get_registry_key_int("Desktop/Settings/ProjectOptions/EnableLegacyOptimetricsTools") == 1
