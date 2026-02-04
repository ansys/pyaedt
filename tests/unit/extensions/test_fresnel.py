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

from ansys.aedt.core.extensions.hfss.fresnel import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss.fresnel import FresnelExtension
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.generic.numbers_utils import Quantity


@pytest.fixture
def mock_hfss_app_fresnel(mock_hfss_app):
    """Fixture to create a mock AEDT application (extends HFSS mock)."""
    with patch.object(ExtensionCommon, "desktop", new_callable=PropertyMock) as mock_desktop_property:
        mock_desktop_instance = MagicMock()
        mock_desktop_instance.design_list.return_value = [
            "Design1",
            "Design2",
        ]
        mock_desktop_instance.aedt_version_id = "2026.2"
        mock_desktop_property.return_value = mock_desktop_instance

        mock_hfss_app.design_setups = {}

        mock_setup = MagicMock()
        mock_setup.properties = {"Solution Freq": Quantity("1GHz")}

        mock_hfss_app.design_setups = {"Setup": mock_setup}

        yield mock_hfss_app


def test_default(mock_hfss_app_fresnel):
    """Test instantiation of the Fresnel extension."""
    mock_hfss_app_fresnel.design_setups = {}
    extension = FresnelExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_mode(mock_hfss_app_fresnel):
    """Test coefficient mode."""
    extension = FresnelExtension(withdraw=True)

    # Select advanced workflow tab
    tabs = extension._widgets["tabs"]
    tabs.select(1)

    isotropic_button = extension._widgets["isotropic_button"]
    anisotropic_button = extension._widgets["anisotropic_button"]
    isotropic_button.invoke()
    assert extension._widgets["azimuth_slider"].grid_info() != {}
    assert extension._widgets["azimuth_spin"].grid_info() != {}
    assert extension._widgets["azimuth_label"].grid_info() != {}

    anisotropic_button.invoke()
    assert extension._widgets["azimuth_slider"].grid_info() == {}
    assert extension._widgets["azimuth_spin"].grid_info() == {}
    assert extension._widgets["azimuth_label"].grid_info() == {}

    extension.root.destroy()


def test_elevation_slider_changed_updates_values(mock_hfss_app_fresnel):
    extension = FresnelExtension(withdraw=True)

    # Select advanced workflow tab
    tabs = extension._widgets["tabs"]
    tabs.select(1)
    anisotropic_button = extension._widgets["anisotropic_button"]
    anisotropic_button.invoke()

    extension._widgets["elevation_resolution"].set(-5)

    extension.root.destroy()


def test_apply_validate_no_setup(mock_hfss_app_fresnel):
    mock_hfss_app_fresnel.design_setups = {}
    extension = FresnelExtension(withdraw=True)

    # Select advanced workflow tab
    tabs = extension._widgets["tabs"]
    tabs.select(1)
    anisotropic_button = extension._widgets["anisotropic_button"]
    anisotropic_button.invoke()

    apply_button = extension._widgets["apply_validate_button"]
    apply_button.invoke()

    extension.root.destroy()


def test_apply_validate(mock_hfss_app_fresnel):
    extension = FresnelExtension(withdraw=True)

    # Select advanced workflow tab
    tabs = extension._widgets["tabs"]
    tabs.select(1)
    anisotropic_button = extension._widgets["anisotropic_button"]
    anisotropic_button.invoke()

    apply_button = extension._widgets["apply_validate_button"]
    apply_button.invoke()

    extension.root.destroy()


@pytest.mark.parametrize(
    "vals,valid,step",
    [
        ([0, 15, 30, 45, 60, 75, 90], True, 15.0),
        ([0, 10, 20, 30, 40, 50, 60, 70, 80, 90], True, 10.0),
        ([0, 7.5, 15, 22.5, 30, 37.5, 45, 52.5, 60, 67.5, 75, 82.5, 90], True, 7.5),
        ([5, 10, 15], False, None),
        ([0], False, None),
        ([0, 13, 26, 39, 52, 65, 78, 91], False, None),
    ],
)
def test_validate_even_and_divides(vals, valid, step):
    ok, s, filtered = FresnelExtension.validate_even_and_divides_90(vals)
    assert ok is valid
    assert (s == step) or (s is None and step is None)
    if ok:
        # last value must be 90 when valid
        assert abs(filtered[-1] - 90.0) < 1e-6
