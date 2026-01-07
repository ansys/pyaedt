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

import logging
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.modeler.cad.primitives import GeometryModeler


@pytest.fixture
def mock_hfss_app():
    """Fixture used to mock the creation of a Maxwell instance."""
    with patch("ansys.aedt.core.hfss.Hfss.__init__", lambda x: None):
        mock_instance = Hfss()
        mock_instance._logger = logging.getLogger(__name__)
        mock_instance._oeditor = PropertyMock(return_value=MagicMock())
        mock_instance.value_with_units = MagicMock(return_value="1mm")
        mock_instance._odesign = MagicMock()
        yield mock_instance


@patch("ansys.aedt.core.modeler.cad.primitives.GeometryModeler.unclassified_objects", new_callable=PropertyMock)
def test_project_object_failure(mock_unclassified_objects, mock_hfss_app, caplog: pytest.LogCaptureFixture):
    mock_unclassified_objects.side_effect = [[], [MagicMock()]]
    gm = GeometryModeler(mock_hfss_app)

    assert not gm.project_sheet("rect", "box", 1)
    assert any(
        "Failed to Project Sheet. Reverting to original objects." in record.getMessage() for record in caplog.records
    )
