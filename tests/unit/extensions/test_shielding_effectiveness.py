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

import tkinter
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss.shielding_effectiveness import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import ShieldingEffectivenessExtension
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import ShieldingEffectivenessExtensionData
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_aedt_app():
    """Fixture to create a mock AEDT application."""
    mock_modeler = MagicMock()
    mock_modeler.object_names = ["test_enclosure"]

    mock_aedt_application = MagicMock()
    mock_aedt_application.modeler = mock_modeler
    mock_aedt_application.design_type = "HFSS"

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_shielding_effectiveness_extension_default(mock_desktop, mock_aedt_app):
    """Test instantiation of the Shielding Effectiveness extension."""
    mock_desktop.return_value = MagicMock()

    extension = ShieldingEffectivenessExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_shielding_effectiveness_extension_generate_button(mock_desktop, mock_aedt_app):
    """Test instantiation of the Shielding Effectiveness extension."""
    mock_desktop.return_value = MagicMock()

    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.root.nametowidget("generate").invoke()
    data: ShieldingEffectivenessExtensionData = extension.data

    assert 0.01 == data.sphere_size
    assert 0.0 == data.x_pol
    assert 0.0 == data.y_pol
    assert 1.0 == data.z_pol
    assert "Electric" == data.dipole_type
    assert "GHz" == data.frequency_units
    assert 0.1 == data.start_frequency
    assert 1.0 == data.stop_frequency
    assert 10 == data.points
    assert 4 == data.cores


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_shielding_effectiveness_extension_exceptions(mock_desktop, mock_aedt_app):
    """Test instantiation of the Shielding Effectiveness extension."""
    mock_desktop.return_value = MagicMock()

    # Test exception when no objects exist in design
    mock_aedt_app.modeler.object_names = []
    with pytest.raises(AEDTRuntimeError):
        ShieldingEffectivenessExtension(withdraw=True)

    # Test exception when multiple objects exist in design
    mock_aedt_app.modeler.object_names = ["object1", "object2"]
    with pytest.raises(AEDTRuntimeError):
        ShieldingEffectivenessExtension(withdraw=True)

    # Reset to valid state
    mock_aedt_app.modeler.object_names = ["test_enclosure"]

    # Test negative sphere size
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.sphere_size_entry.delete("1.0", tkinter.END)
    extension.sphere_size_entry.insert(tkinter.END, "-0.01")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test zero sphere size
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.sphere_size_entry.delete("1.0", tkinter.END)
    extension.sphere_size_entry.insert(tkinter.END, "0.0")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test invalid frequency range (start >= stop)
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.start_frequency_entry.delete("1.0", tkinter.END)
    extension.start_frequency_entry.insert(tkinter.END, "2.0")
    extension.stop_frequency_entry.delete("1.0", tkinter.END)
    extension.stop_frequency_entry.insert(tkinter.END, "1.0")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test different frequency units
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.start_frequency_units.set("GHz")
    extension.stop_frequency_units.set("MHz")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test negative points
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.points_entry.delete("1.0", tkinter.END)
    extension.points_entry.insert(tkinter.END, "-5")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test zero points
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.points_entry.delete("1.0", tkinter.END)
    extension.points_entry.insert(tkinter.END, "0")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test negative cores
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.cores_entry.delete("1.0", tkinter.END)
    extension.cores_entry.insert(tkinter.END, "-2")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    # Test zero cores
    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.cores_entry.delete("1.0", tkinter.END)
    extension.cores_entry.insert(tkinter.END, "0")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_shielding_effectiveness_extension_magnetic_dipole(mock_desktop, mock_aedt_app):
    """Test setting magnetic dipole type."""
    mock_desktop.return_value = MagicMock()

    extension = ShieldingEffectivenessExtension(withdraw=True)
    # Uncheck the electric dipole checkbox to set magnetic dipole
    extension.dipole_var.set(0)
    extension.root.nametowidget("generate").invoke()
    data: ShieldingEffectivenessExtensionData = extension.data

    assert "Magnetic" == data.dipole_type


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_shielding_effectiveness_extension_custom_values(mock_desktop, mock_aedt_app):
    """Test setting custom values in the extension."""
    mock_desktop.return_value = MagicMock()

    extension = ShieldingEffectivenessExtension(withdraw=True)

    # Set custom values
    extension.sphere_size_entry.delete("1.0", tkinter.END)
    extension.sphere_size_entry.insert(tkinter.END, "0.02")

    extension.x_pol_entry.delete("1.0", tkinter.END)
    extension.x_pol_entry.insert(tkinter.END, "1.0")

    extension.y_pol_entry.delete("1.0", tkinter.END)
    extension.y_pol_entry.insert(tkinter.END, "0.5")

    extension.z_pol_entry.delete("1.0", tkinter.END)
    extension.z_pol_entry.insert(tkinter.END, "0.0")

    extension.start_frequency_entry.delete("1.0", tkinter.END)
    extension.start_frequency_entry.insert(tkinter.END, "0.5")
    extension.start_frequency_units.set("MHz")

    extension.stop_frequency_entry.delete("1.0", tkinter.END)
    extension.stop_frequency_entry.insert(tkinter.END, "5.0")
    extension.stop_frequency_units.set("MHz")

    extension.points_entry.delete("1.0", tkinter.END)
    extension.points_entry.insert(tkinter.END, "20")

    extension.cores_entry.delete("1.0", tkinter.END)
    extension.cores_entry.insert(tkinter.END, "8")

    extension.root.nametowidget("generate").invoke()
    data: ShieldingEffectivenessExtensionData = extension.data

    assert 0.02 == data.sphere_size
    assert 1.0 == data.x_pol
    assert 0.5 == data.y_pol
    assert 0.0 == data.z_pol
    assert "MHz" == data.frequency_units
    assert 0.5 == data.start_frequency
    assert 5.0 == data.stop_frequency
    assert 20 == data.points
    assert 8 == data.cores
