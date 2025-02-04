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

from unittest.mock import MagicMock
from unittest.mock import patch

from ansys.aedt.core.generic.errors import AEDTRuntimeError
from ansys.aedt.core.maxwell import Maxwell3d
import pytest


@patch.object(Maxwell3d, "solution_type", "Transient")
@patch("ansys.aedt.core.maxwell.BoundaryObject", autospec=True)
def test_maxwell_3d_assign_resistive_sheet_failure(mock_boundary_object, maxwell_3d_setup):
    boundary_object = MagicMock()
    boundary_object.create.return_value = False
    mock_boundary_object.return_value = boundary_object
    maxwell = Maxwell3d()
    maxwell._modeler = MagicMock()
    maxwell._logger = MagicMock()

    with pytest.raises(AEDTRuntimeError, match=r"Boundary ResistiveSheet_\w+ was not created\."):
        maxwell.assign_resistive_sheet(None, None)
