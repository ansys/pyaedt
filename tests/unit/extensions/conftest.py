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

"""
Unit Extensions Test Configuration
----------------------------------

This conftest.py contains configurations specific to unit extension tests.
It provides mock fixtures for testing extensions without requiring full
AEDT applications. General configurations are inherited from top-level.
"""

from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.misc import ExtensionCommon


@pytest.fixture
def mock_icepak_app():
    """Fixture to mock Icepak application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_instance = MagicMock()
        mock_instance.design_type = "Icepak"
        mock_property.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_hfss_app():
    """Fixture to mock HFSS application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_instance = MagicMock()
        mock_instance.design_type = "HFSS"
        mock_property.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_hfss_3d_layout_app():
    """Fixture to mock HFSS 3D Layout application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_instance = MagicMock()
        mock_instance.design_type = "HFSS 3D Layout Design"
        mock_property.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_maxwell_3d_app(request):
    """Fixture to mock Maxwell 3D application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_instance = MagicMock()
        mock_instance.design_type = "Maxwell 3D"
        mock_instance._aedt_version = getattr(request, "param", "2026.1")
        mock_property.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_maxwell_2d_app(request):
    """Fixture to mock Maxwell 2D application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_instance = MagicMock()
        mock_instance.design_type = "Maxwell 2D"
        mock_instance._aedt_version = getattr(request, "param", "2026.1")
        mock_property.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_circuit_app():
    """Fixture to mock Circuit application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_instance = MagicMock()
        mock_instance.design_type = "Circuit Design"
        mock_property.return_value = mock_instance

        yield mock_instance


@pytest.fixture
def mock_emit_app():
    """Fixture to mock EMIT application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_instance = MagicMock()
        mock_instance.design_type = "EMIT"
        mock_property.return_value = mock_instance

        yield mock_instance
