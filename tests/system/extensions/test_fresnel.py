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

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.fresnel import FresnelExtension


@pytest.fixture()
def aedt_app(add_app):
    app = add_app(application=Hfss, solution_type="Modal")
    yield app
    app.close_project(app.project_name, save=False)


def test_fresnel_function(aedt_app) -> None:
    """Test Fresnel extension with no setup."""
    extension = FresnelExtension(withdraw=True)

    assert extension.fresnel_type.get() == "isotropic"
    assert extension.setup_names == ["No Setup"]


def test_fresnel_ui_interactions(aedt_app) -> None:
    """Test various UI interactions in the Fresnel extension."""
    # Create HFSS application for testing environment
    aedt_app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test elevation slider
    elevation_slider = extension._widgets["elevation_slider"]

    elevation_slider.set(0)  # Coarse
    extension.elevation_slider_changed(0)
    assert extension._widgets["theta_scan_max"].get() == 20.0

    elevation_slider.set(2)  # Fine
    extension.elevation_slider_changed(2)
    assert extension._widgets["theta_scan_max"].get() == 20.0

    elevation_slider.set(1)  # Regular
    extension.elevation_slider_changed(1)
    assert extension._widgets["theta_scan_max"].get() == 22.5

    # Test azimuth slider
    azimuth_slider = extension._widgets["azimuth_slider"]
    azimuth_slider.set(0)
    extension.azimuth_slider_changed(0)
    azimuth_slider.set(1)
    extension.azimuth_slider_changed(1)
    azimuth_slider.set(2)
    extension.azimuth_slider_changed(2)

    # Test theta scan max slider
    theta_scan_max_slider = extension._widgets["theta_scan_max_slider"]
    theta_scan_max_slider.set(30)
    extension.snap_theta_scan_max_slider(30)

    # Test theta scan max spin
    theta_scan_max_spin = extension._widgets["theta_scan_max_spin"]
    theta_scan_max_spin.set(45)
    extension.snap_theta_scan_max_spin()

    # Test frequency units combo
    freq_units_combo = extension._widgets["frequency_units_combo"]
    freq_units_combo.current(1)  # MHz
    freq_units_combo.current(0)  # GHz

    # Test keep mesh checkbox
    keep_mesh_checkbox = extension._widgets["keep_mesh_checkbox"]
    keep_mesh_checkbox.invoke()  # Toggle off
    keep_mesh_checkbox.invoke()  # Toggle on

    # Test tab switching
    tabs = extension._widgets["tabs"]
    tabs.select(extension._widgets["advanced_tab"])
    tabs.select(extension._widgets["settings_tab"])
    tabs.select(extension._widgets["extraction_tab"])


def test_fresnel_validation_method_lattice(aedt_app) -> None:
    """Test the validation method in the Fresnel extension."""
    # Create HFSS application for testing environment
    aedt_app.create_setup()

    box1 = aedt_app.modeler.create_box([-100, -100, -100], [200, 200, 200], name="Rad_box2")
    aedt_app.create_floquet_port(
        box1.faces[0], modes=7, deembed_distance=1, reporter_filter=[False, True, False, False, False, False, False]
    )
    aedt_app.auto_assign_lattice_pairs(box1.name)
    aedt_app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test validate button (extraction tab)
    validate_button = extension._widgets["validate_button"]
    validate_button.invoke()


def test_fresnel_validation_method_primary(aedt_app) -> None:
    """Test the validation method in the Fresnel extension."""
    # Create HFSS application for testing environment
    aedt_app.create_setup()

    box1 = aedt_app.modeler.create_box([-100, -100, -100], [200, 200, 200])

    aedt_app.create_floquet_port(
        box1.faces[0], modes=7, deembed_distance=1, reporter_filter=[False, True, False, False, False, False, False]
    )

    pr1 = aedt_app.assign_primary(box1.bottom_face_x, ["-100mm", "0mm", "-100mm"], ["-100mm", "0mm", "100mm"])
    _ = aedt_app.assign_secondary(box1.top_face_x, pr1.name, ["100mm", "0mm", "-100mm"], ["100mm", "0mm", "100mm"])

    pr2 = aedt_app.assign_primary(box1.bottom_face_y, ["0mm", "-100mm", "-100mm"], ["0mm", "-100mm", "100mm"])
    _ = aedt_app.assign_secondary(box1.top_face_y, pr2.name, ["0mm", "100mm", "-100mm"], ["0mm", "100mm", "100mm"])

    aedt_app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test validate button (extraction tab)
    validate_button = extension._widgets["validate_button"]
    validate_button.invoke()


def test_fresnel_apply_validate_method(aedt_app) -> None:
    """Test the apply and validate method in the Fresnel extension."""
    aedt_app.create_setup()

    (inner, outer, _) = aedt_app.modeler.create_coaxial([0, 0, 0], 0)
    aedt_app.lumped_port(inner, outer, create_port_sheet=True)
    aedt_app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Switch to advanced tab
    tabs = extension._widgets["tabs"]
    tabs.select(extension._widgets["advanced_tab"])

    # Set up frequency sweep values
    extension._widgets["start_frequency"].delete("1.0", tkinter.END)
    extension._widgets["start_frequency"].insert(tkinter.END, "1.0")
    extension._widgets["stop_frequency"].delete("1.0", tkinter.END)
    extension._widgets["stop_frequency"].insert(tkinter.END, "2.0")
    extension._widgets["step_frequency"].delete("1.0", tkinter.END)
    extension._widgets["step_frequency"].insert(tkinter.END, "0.1")

    # Test apply and validate button
    apply_validate_button = extension._widgets["apply_validate_button"]
    apply_validate_button.invoke()


def test_fresnel_apply_validate_method_floquet(aedt_app) -> None:
    """Test the apply and validate method in the Fresnel extension."""
    aedt_app.create_setup()

    box1 = aedt_app.modeler.create_box([-100, -100, -100], [200, 200, 200], name="Rad_box2")
    aedt_app.create_floquet_port(
        box1.faces[0], modes=7, deembed_distance=1, reporter_filter=[False, True, False, False, False, False, False]
    )

    aedt_app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Switch to advanced tab
    tabs = extension._widgets["tabs"]
    tabs.select(extension._widgets["advanced_tab"])

    # Set up frequency sweep values
    extension._widgets["start_frequency"].delete("1.0", tkinter.END)
    extension._widgets["start_frequency"].insert(tkinter.END, "1.0")
    extension._widgets["stop_frequency"].delete("1.0", tkinter.END)
    extension._widgets["stop_frequency"].insert(tkinter.END, "2.0")
    extension._widgets["step_frequency"].delete("1.0", tkinter.END)
    extension._widgets["step_frequency"].insert(tkinter.END, "0.1")

    # Test apply and validate button
    apply_validate_button = extension._widgets["apply_validate_button"]
    apply_validate_button.invoke()
