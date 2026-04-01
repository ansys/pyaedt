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

from ansys.aedt.core.filtersolutions_core.export_to_aedt import SubstrateEr
from ansys.aedt.core.filtersolutions_core.export_to_aedt import SubstrateResistivity
from ansys.aedt.core.filtersolutions_core.export_to_aedt import SubstrateType
from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import config


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.2", reason="Skipped on versions earlier than 2025.2")
class TestClass:
    def test_substrate_type(self, distributed_design):
        assert len(SubstrateType) == 5
        for substrate in SubstrateType:
            distributed_design.substrate.substrate_type = substrate
            assert distributed_design.substrate.substrate_type == substrate

    def test_substrate_er(self, distributed_design):
        assert distributed_design.substrate.substrate_er == SubstrateEr.ALUMINA
        assert len(SubstrateEr) == 17
        with pytest.raises(ValueError) as info:
            distributed_design.substrate.substrate_er = 3.7
        assert str(info.value) == "Invalid substrate input. Must be a SubstrateEr enum member or a string"
        for er in SubstrateEr:
            distributed_design.substrate.substrate_er = er
            assert distributed_design.substrate.substrate_er == er
        distributed_design.substrate.substrate_er = "3.2"
        assert distributed_design.substrate.substrate_er == "3.2"
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_er = ""
            assert info.value.args[0] == "The substrate Er cannot be set to an empty string"

    def test_substrate_resistivity(self, distributed_design):
        assert distributed_design.substrate.substrate_resistivity == SubstrateResistivity.GOLD
        assert len(SubstrateResistivity) == 11
        with pytest.raises(ValueError) as info:
            distributed_design.substrate.substrate_resistivity = 0.02
        assert str(info.value) == "Invalid substrate input. Must be a SubstrateResistivity enum member or a string"
        for resistivity in SubstrateResistivity:
            distributed_design.substrate.substrate_resistivity = resistivity
            assert distributed_design.substrate.substrate_resistivity == resistivity
        distributed_design.substrate.substrate_resistivity = "0.02"
        assert distributed_design.substrate.substrate_resistivity == "0.02"
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_resistivity = ""
            assert info.value.args[0] == "The substrate resistivity cannot be set to an empty string"

    def test_substrate_loss_tangent(self, distributed_design):
        assert distributed_design.substrate.substrate_loss_tangent == SubstrateEr.ALUMINA
        assert len(SubstrateEr) == 17
        with pytest.raises(ValueError) as info:
            distributed_design.substrate.substrate_loss_tangent = 0.0002
        assert str(info.value) == "Invalid substrate input. Must be a SubstrateEr enum member or a string"
        for loss in SubstrateEr:
            distributed_design.substrate.substrate_loss_tangent = loss
            assert distributed_design.substrate.substrate_loss_tangent == loss
        distributed_design.substrate.substrate_loss_tangent = "0.0002"
        assert distributed_design.substrate.substrate_loss_tangent == "0.0002"
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_loss_tangent = ""
            assert info.value.args[0] == "The substrate loss tangent cannot be set to an empty string"

    def test_substrate_conductor_thickness(self, distributed_design):
        assert distributed_design.substrate.substrate_conductor_thickness == "2.54 um"
        distributed_design.substrate.substrate_conductor_thickness = "1.25 um"
        assert distributed_design.substrate.substrate_conductor_thickness == "1.25 um"

    def test_substrate_dielectric_height(self, distributed_design):
        assert distributed_design.substrate.substrate_dielectric_height == "1.27 mm"
        distributed_design.substrate.substrate_dielectric_height = "1.22 mm"
        assert distributed_design.substrate.substrate_dielectric_height == "1.22 mm"

    def test_substrate_unbalanced_lower_dielectric_height(self, distributed_design):
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_unbalanced_lower_dielectric_height = "2.5 mm"
        assert info.value.args[0] == "The Lower Dielectric Height is not available for MICROSTRIP substrate"
        distributed_design.substrate.substrate_type = SubstrateType.STRIPLINE
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_unbalanced_lower_dielectric_height = "2.5 mm"
        assert info.value.args[0] == "The Unbalanced option for STRIPLINE Substrate is not enabled"
        distributed_design.substrate.substrate_unbalanced_stripline_enabled = True
        assert distributed_design.substrate.substrate_unbalanced_lower_dielectric_height == "1.27 mm"
        distributed_design.substrate.substrate_unbalanced_lower_dielectric_height = "5.2 mm"
        assert distributed_design.substrate.substrate_unbalanced_lower_dielectric_height == "5.2 mm"

    def test_substrate_suspend_dielectric_height(self, distributed_design):
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_suspend_dielectric_height = "2.5 mm"
        assert info.value.args[0] == "The Suspend Dielectric Height is not available for MICROSTRIP substrate"
        distributed_design.substrate.substrate_type = SubstrateType.SUSPEND
        assert distributed_design.substrate.substrate_suspend_dielectric_height == "1.27 mm"
        distributed_design.substrate.substrate_suspend_dielectric_height = "3.2 mm"
        assert distributed_design.substrate.substrate_suspend_dielectric_height == "3.2 mm"

    def test_substrate_cover_height(self, distributed_design):
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_cover_height = "2.5 mm"
        assert info.value.args[0] == "The Cover option for MICROSTRIP Substrate is not enabled"
        distributed_design.substrate.substrate_cover_height_enabled = True
        assert distributed_design.substrate.substrate_cover_height == "6.35 mm"
        distributed_design.substrate.substrate_cover_height = "2.5 mm"
        assert distributed_design.substrate.substrate_cover_height == "2.5 mm"

    def test_substrate_unbalanced_stripline_enabled(self, distributed_design):
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_unbalanced_stripline_enabled = True
        assert info.value.args[0] == "The Unbalanced Topolgy is not available for MICROSTRIP substrate"
        distributed_design.substrate.substrate_type = SubstrateType.STRIPLINE
        assert not distributed_design.substrate.substrate_unbalanced_stripline_enabled
        distributed_design.substrate.substrate_unbalanced_stripline_enabled = True
        assert distributed_design.substrate.substrate_unbalanced_stripline_enabled

    def test_substrate_cover_height_enabled(self, distributed_design):
        distributed_design.substrate.substrate_type = SubstrateType.STRIPLINE
        with pytest.raises(RuntimeError) as info:
            distributed_design.substrate.substrate_cover_height_enabled = True
        assert info.value.args[0] == "The Grounded Cover Above Line Topolgy is not available for STRIPLINE substrate"
        distributed_design.substrate.substrate_type = SubstrateType.MICROSTRIP
        assert not distributed_design.substrate.substrate_cover_height_enabled
        distributed_design.substrate.substrate_cover_height_enabled = True
        assert distributed_design.substrate.substrate_cover_height_enabled
