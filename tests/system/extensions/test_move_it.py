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

from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Q3d
from ansys.aedt.core.extensions.hfss.move_it import MoveItExtension
from ansys.aedt.core.extensions.hfss.move_it import MoveItExtensionData
from ansys.aedt.core.extensions.hfss.move_it import main
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.object_3d import PolylineSegment
from tests.system.extensions.conftest import desktop_version
from tests.system.extensions.conftest import local_path as extensions_local_path

fields_calculator = "fields_calculator_solved"
test_subfolder = "T45"

HFSS_ASSIGNMENTS = ["Polyline1"]


def test_move_it_generate_button(add_app):
    """Test the Generate button in the Move IT extension."""
    aedt_app = add_app(application=Hfss, project_name="move_it", design_name="generate")

    aedt_app["p1"] = "100mm"
    aedt_app["p2"] = "71mm"
    test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

    p2 = aedt_app.modeler.create_polyline(
        points=test_points, segment_type=PolylineSegment("Spline", num_points=4), name="spline_4pt"
    )

    DATA = MoveItExtensionData(choice=p2.name, velocity=1.4, acceleration=0.0, delay=0.0)

    extension = MoveItExtension(withdraw=True)
    extension.root.nametowidget("generate").invoke()

    assert 2 == len(aedt_app.variable_manager.variables)
    assert DATA == extension.data
    assert main(extension.data)
    assert 7 == len(aedt_app.variable_manager.variables)


def test_move_it_exceptions(add_app):
    """Test the Generate button in the Move IT extension."""
    DATA = MoveItExtensionData(choice=None)
    with pytest.raises(AEDTRuntimeError):
        main(DATA)

    DATA = MoveItExtensionData(velocity=-1.0)
    with pytest.raises(AEDTRuntimeError):
        main(DATA)

    DATA = MoveItExtensionData(delay=-1.0)
    with pytest.raises(AEDTRuntimeError):
        main(DATA)

    DATA = MoveItExtensionData(acceleration=-1.0)
    with pytest.raises(AEDTRuntimeError):
        main(DATA)

    _ = add_app(application=Q3d, project_name="move_it", design_name="wrong_design")

    DATA = MoveItExtensionData(choice="invented", velocity=1.0, acceleration=0.0, delay=0.0)

    with pytest.raises(AEDTRuntimeError):
        main(DATA)
