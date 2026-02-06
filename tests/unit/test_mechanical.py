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

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.mechanical import Mechanical


@pytest.fixture
def mechanical_setup():
    """Fixture used to mock the creation of a Mechanical instance."""
    with patch("ansys.aedt.core.mechanical.Mechanical.__init__", lambda x: None):
        mock_instance = MagicMock(spec=Mechanical)
        yield mock_instance


@patch.object(Mechanical, "solution_type", "Dummy")
def test_assign_em_losses_failure_with_wrong_solution_type(mechanical_setup) -> None:
    mechanical = Mechanical()

    with pytest.raises(AEDTRuntimeError):
        assert not mechanical.assign_em_losses()


@patch.object(Mechanical, "solution_type", "Dummy")
def test_assign_uniform_convection_failure_with_wrong_solution_type(mechanical_setup) -> None:
    mechanical = Mechanical()
    mock_assignment = MagicMock()

    with pytest.raises(AEDTRuntimeError):
        assert not mechanical.assign_uniform_convection(mock_assignment)


@patch.object(Mechanical, "solution_type", "Dummy")
def test_assign_uniform_temperature_failure_with_wrong_solution_type(mechanical_setup) -> None:
    mechanical = Mechanical()
    mock_assignment = MagicMock()

    with pytest.raises(AEDTRuntimeError):
        assert not mechanical.assign_uniform_temperature(mock_assignment)


@patch.object(Mechanical, "solution_type", "Dummy")
def test_assign_heat_flux_failure_with_wrong_solution_type(mechanical_setup) -> None:
    mechanical = Mechanical()
    mock_assignment = MagicMock()
    mock_heat_flux_type = MagicMock()
    mock_value = MagicMock()

    with pytest.raises(AEDTRuntimeError):
        assert not mechanical.assign_heat_flux(mock_assignment, mock_heat_flux_type, mock_value)


@patch.object(Mechanical, "solution_type", "Dummy")
def test_assign_heat_generation_failure_with_wrong_solution_type(mechanical_setup) -> None:
    mechanical = Mechanical()
    mock_assignment = MagicMock()
    mock_value = MagicMock()

    with pytest.raises(AEDTRuntimeError):
        assert not mechanical.assign_heat_generation(mock_assignment, mock_value)


@patch.object(Mechanical, "solution_type", "Dummy")
def test_assign_thermal_map_failure_with_wrong_solution_type(mechanical_setup) -> None:
    mechanical = Mechanical()
    mock_assignment = MagicMock()
    mock_value = MagicMock()

    with pytest.raises(AEDTRuntimeError):
        assert not mechanical.assign_thermal_map(mock_assignment, mock_value)
