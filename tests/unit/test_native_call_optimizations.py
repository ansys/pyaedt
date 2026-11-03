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

"""Unit tests checking that common operations avoid redundant native API calls."""

from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.modeler.cad.primitives import GeometryModeler


@pytest.fixture
def modeler():
    with patch.object(GeometryModeler, "__init__", lambda self: None):
        mdl = GeometryModeler()
    mdl._app = MagicMock()
    mdl._solids = []
    mdl._sheets = []
    mdl._lines = []
    mdl._points = []
    mdl._unclassified = []
    mdl._planes = {}
    mdl._all_object_names = []
    oeditor = MagicMock()
    oeditor.GetObjectsInGroup.side_effect = lambda group: {
        "Solids": ["box1", "box2"],
        "Sheets": ["rect1"],
        "Lines": [],
        "Unclassified": ["bad1"],
    }[group]
    oeditor.GetPoints.return_value = ["pt1"]
    oeditor.GetChildNames.return_value = ["plane1"]
    with patch.object(GeometryModeler, "oeditor", new_callable=PropertyMock, return_value=oeditor):
        yield mdl, oeditor


def test_add_message_skips_desktop_when_desktop_logs_disabled() -> None:
    from ansys.aedt.core.aedt_logger import AedtLogger
    from ansys.aedt.core.generic.settings import settings

    logger = AedtLogger()
    desktop = PropertyMock(side_effect=AssertionError("desktop must not be queried"))
    original = settings.enable_desktop_logs
    settings.enable_desktop_logs = False
    try:
        with patch.object(AedtLogger, "_desktop", new_callable=lambda: desktop):
            logger.add_message(0, "message")
    finally:
        settings.enable_desktop_logs = original

    desktop.assert_not_called()


# Round 2 optimizations
