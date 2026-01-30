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
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.maxwell import Maxwell3d
from ansys.aedt.core.mechanical import Mechanical


@pytest.fixture
def mechanical():
    """Fixture used to mock the creation of a Mechanical instance."""
    with patch("ansys.aedt.core.mechanical.Mechanical.__init__", lambda x: None):
        mock_instance = MagicMock(spec=Mechanical)
        yield mock_instance


@pytest.fixture
def maxwell_3d():
    """Fixture used to mock the creation of a Maxwell instance."""
    with patch("ansys.aedt.core.maxwell.Maxwell3d.__init__", lambda x: None):
        mock_instance = MagicMock(spec=Maxwell3d)
        yield mock_instance


@patch.object(Mechanical, "design_type", "Dummy")
def test_mechanical_failure_design_type(mechanical):
    mechanical = Mechanical()

    with pytest.raises(AEDTRuntimeError):
        mechanical.create_em_target_design("Icepak")


@patch.object(Maxwell3d, "design_type", "Maxwell 3D")
def test_maxwell_failure_design(maxwell_3d):
    maxwell = Maxwell3d()

    with pytest.raises(AEDTRuntimeError):
        maxwell.create_em_target_design("Twinbuilder")


@patch.object(Maxwell3d, "nominal_adaptive", new_callable=PropertyMock)
@patch.object(Maxwell3d, "design_type", "Maxwell 3D")
def test_maxwell_failure_design_type_create_target_design(mock_nominal, maxwell_3d):
    mock_nominal.return_value = "setup_name"
    maxwell = Maxwell3d()
    maxwell._odesign = MagicMock()

    with pytest.raises(AEDTRuntimeError):
        assert maxwell.create_em_target_design("Icepak", design_setup="Invalid")


@patch.object(Maxwell3d, "nominal_adaptive", new_callable=PropertyMock)
@patch.object(Maxwell3d, "design_type", "Maxwell 3D")
def test_maxwell_create_target_design(mock_nominal, maxwell_3d):
    mock_nominal.return_value = "setup_name"
    maxwell = Maxwell3d()
    maxwell._odesign = MagicMock()

    assert maxwell.create_em_target_design("Icepak", design_setup="Forced")
