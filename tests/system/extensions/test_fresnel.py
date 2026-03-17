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

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.fresnel import FresnelExtension


def test_fresnel_function(add_app) -> None:
    """Test Fresnel extension with no setup."""
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    extension = FresnelExtension(withdraw=True)

    assert extension.fresnel_type.get() == "isotropic"
    assert extension.setup_names == ["No Setup"]

    app.close_project(save=False)


def test_fresnel_with_setups(add_app) -> None:
    """Test Fresnel extension with a setup created."""
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    setup = app.create_setup()

    extension = FresnelExtension(withdraw=True)

    assert extension.fresnel_type.get() == "isotropic"
    assert extension.setup_names[0] == setup.name

    isotropic_widget = extension._widgets.get("isotropic_button")
    if isotropic_widget:
        isotropic_widget.invoke()
        assert extension.fresnel_type.get() == "isotropic"

    app.close_project(save=False)


def test_fresnel_ui_interactions(add_app) -> None:
    """Test various UI interactions in the Fresnel extension."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test elevation slider
    elevation_slider = extension._widgets["elevation_slider"]
    elevation_slider.set(0)  # Coarse
    extension.elevation_slider_changed(0)
    elevation_slider.set(2)  # Fine
    extension.elevation_slider_changed(2)
    elevation_slider.set(1)  # Regular
    extension.elevation_slider_changed(1)

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

    app.close_project(save=False)


def test_fresnel_text_widgets(add_app) -> None:
    """Test text input widgets in the Fresnel extension."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test start frequency text widget
    start_freq = extension._widgets["start_frequency"]
    start_freq.delete("1.0", tkinter.END)
    start_freq.insert(tkinter.END, "10.0")

    # Test stop frequency text widget
    stop_freq = extension._widgets["stop_frequency"]
    stop_freq.delete("1.0", tkinter.END)
    stop_freq.insert(tkinter.END, "20.0")

    # Test step frequency text widget
    step_freq = extension._widgets["step_frequency"]
    step_freq.delete("1.0", tkinter.END)
    step_freq.insert(tkinter.END, "0.5")

    # Test HPC settings
    core_number = extension._widgets["core_number"]
    core_number.delete("1.0", tkinter.END)
    core_number.insert(tkinter.END, "8")

    tasks_number = extension._widgets["tasks_number"]
    tasks_number.delete("1.0", tkinter.END)
    tasks_number.insert(tkinter.END, "2")

    app.close_project(save=False)


def test_fresnel_combo_boxes(add_app) -> None:
    """Test combo box interactions in the Fresnel extension."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test setup combo in advanced tab
    setup_combo = extension._widgets["setup_combo"]
    assert len(setup_combo["values"]) > 0
    setup_combo.current(0)

    # Test setup sweep combo in extraction tab
    setup_sweep_combo = extension._widgets["setup_sweep_combo"]
    assert len(setup_sweep_combo["values"]) > 0
    setup_sweep_combo.current(0)

    # Test frequency units combo
    freq_units_combo = extension._widgets["frequency_units_combo"]
    assert freq_units_combo.get() == "GHz"
    freq_units_combo.current(1)  # MHz
    assert freq_units_combo.get() == "MHz"
    freq_units_combo.current(2)  # kHz
    freq_units_combo.current(3)  # Hz
    freq_units_combo.current(0)  # Back to GHz

    app.close_project(save=False)


def test_fresnel_validation_method(add_app) -> None:
    """Test the validation method in the Fresnel extension."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test validate button (extraction tab)
    # This will fail validation but we're testing the button invocation
    validate_button = extension._widgets["validate_button"]
    validate_button.invoke()

    app.close_project(save=False)


def test_fresnel_apply_validate_method(add_app) -> None:
    """Test the apply and validate method in the Fresnel extension."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

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

    app.close_project(save=False)


def test_fresnel_elevation_spin_changed(add_app) -> None:
    """Test elevation spin changed callback."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test elevation_spin_changed method
    extension._widgets["elevation_resolution"].set(5.0)
    extension.elevation_spin_changed()

    # Verify theta_scan_max constraints are updated
    theta_max = extension._widgets["theta_scan_max"].get()
    assert theta_max >= 0

    app.close_project(save=False)


def test_fresnel_extract_parametric_fresnel(add_app) -> None:
    """Test the extract_parametric_fresnel method."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test with no phi (isotropic case)
    rows_no_phi = [
        {"scan_T": 0.0},
        {"scan_T": 10.0},
        {"scan_T": 20.0},
        {"scan_T": 30.0},
    ]
    result = extension.extract_parametric_fresnel(rows_no_phi, theta_key="scan_T", phi_key="scan_P")
    assert result["has_phi"] is False
    assert len(result["theta"]) > 0
    assert len(result["phi"]) == 0

    # Test with phi (anisotropic case)
    rows_with_phi = [
        {"scan_T": 0.0, "scan_P": 0.0},
        {"scan_T": 10.0, "scan_P": 0.0},
        {"scan_T": 0.0, "scan_P": 10.0},
        {"scan_T": 10.0, "scan_P": 10.0},
    ]
    result = extension.extract_parametric_fresnel(rows_with_phi, theta_key="scan_T", phi_key="scan_P")
    assert result["has_phi"] is True
    assert len(result["phi"]) > 0
    assert len(result["theta_by_phi"]) > 0

    # Test with empty rows
    empty_rows = []
    result = extension.extract_parametric_fresnel(empty_rows, theta_key="scan_T", phi_key="scan_P")
    assert result["has_phi"] is False
    assert len(result["theta"]) == 0

    app.close_project(save=False)


def test_fresnel_slider_interactions(add_app) -> None:
    """Test slider interactions with various positions."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test theta scan max slider with various values
    theta_scan_max_slider = extension._widgets["theta_scan_max_slider"]
    test_positions = [0, 15, 30, 45, 60, 75, 90]

    for pos in test_positions:
        theta_scan_max_slider.set(pos)
        extension.snap_theta_scan_max_slider(pos)
        current_val = extension._widgets["theta_scan_max"].get()
        assert current_val >= 0
        assert current_val <= 90

    # Test elevation resolution changes
    elevation_spin = extension._widgets["elevation_spin"]
    test_resolutions = ["1.0", "2.5", "5.0", "7.5", "10.0", "15.0"]

    for res in test_resolutions:
        elevation_spin.set(res)
        extension.elevation_spin_changed()

    app.close_project(save=False)


def test_fresnel_checkbox_interactions(add_app) -> None:
    """Test checkbox state changes."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test keep mesh checkbox
    keep_mesh_checkbox = extension._widgets["keep_mesh_checkbox"]

    # Initially should be True
    assert extension._widgets["keep_mesh"].get() is True

    # Toggle off
    keep_mesh_checkbox.invoke()
    assert extension._widgets["keep_mesh"].get() is False

    # Toggle back on
    keep_mesh_checkbox.invoke()
    assert extension._widgets["keep_mesh"].get() is True

    # Multiple toggles
    for _ in range(5):
        keep_mesh_checkbox.invoke()

    app.close_project(save=False)


def test_fresnel_radio_button_switching(add_app) -> None:
    """Test switching between isotropic and anisotropic modes."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Get the radio button widgets
    isotropic_widget = extension._widgets.get("isotropic_button")
    anisotropic_widget = extension._widgets.get("anisotropic_button")

    # Test isotropic button (default)
    if isotropic_widget:
        isotropic_widget.invoke()
        assert extension.fresnel_type.get() == "isotropic"

    # Test anisotropic button (if available in version)
    if extension.desktop.aedt_version_id >= "2027.1" and anisotropic_widget:
        anisotropic_widget.invoke()
        assert extension.fresnel_type.get() == "anisotropic"

        # Switch back to isotropic
        if isotropic_widget:
            isotropic_widget.invoke()
            assert extension.fresnel_type.get() == "isotropic"

    app.close_project(save=False)


def test_fresnel_tab_navigation(add_app) -> None:
    """Test navigating through all tabs in the extension."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    tabs = extension._widgets["tabs"]

    # Test extraction tab
    tabs.select(extension._widgets["extraction_tab"])

    # Test advanced tab
    tabs.select(extension._widgets["advanced_tab"])

    # Test settings tab
    tabs.select(extension._widgets["settings_tab"])

    # Cycle through tabs multiple times
    for _ in range(3):
        tabs.select(extension._widgets["extraction_tab"])
        tabs.select(extension._widgets["advanced_tab"])
        tabs.select(extension._widgets["settings_tab"])

    app.close_project(save=False)


def test_fresnel_frequency_input_variations(add_app) -> None:
    """Test various frequency input combinations."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test different frequency values
    test_cases = [
        ("1.0", "10.0", "0.5"),
        ("0.5", "5.0", "0.1"),
        ("10.0", "20.0", "1.0"),
        ("5.0", "5.0", "0.1"),  # Same start and stop
    ]

    for start, stop, step in test_cases:
        start_freq = extension._widgets["start_frequency"]
        stop_freq = extension._widgets["stop_frequency"]
        step_freq = extension._widgets["step_frequency"]

        start_freq.delete("1.0", tkinter.END)
        start_freq.insert(tkinter.END, start)

        stop_freq.delete("1.0", tkinter.END)
        stop_freq.insert(tkinter.END, stop)

        step_freq.delete("1.0", tkinter.END)
        step_freq.insert(tkinter.END, step)

        # Verify values are set
        assert start_freq.get("1.0", tkinter.END).strip() == start
        assert stop_freq.get("1.0", tkinter.END).strip() == stop
        assert step_freq.get("1.0", tkinter.END).strip() == step

    app.close_project(save=False)


def test_fresnel_hpc_settings(add_app) -> None:
    """Test HPC settings input variations."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test different core and task combinations
    test_cases = [
        ("1", "1"),
        ("4", "2"),
        ("8", "4"),
        ("16", "1"),
        ("32", "8"),
    ]

    for cores, tasks in test_cases:
        core_number = extension._widgets["core_number"]
        tasks_number = extension._widgets["tasks_number"]

        core_number.delete("1.0", tkinter.END)
        core_number.insert(tkinter.END, cores)

        tasks_number.delete("1.0", tkinter.END)
        tasks_number.insert(tkinter.END, tasks)

        # Verify values are set
        assert core_number.get("1.0", tkinter.END).strip() == cores
        assert tasks_number.get("1.0", tkinter.END).strip() == tasks

    app.close_project(save=False)


def test_fresnel_all_frequency_units(add_app) -> None:
    """Test cycling through all frequency units."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    freq_units_combo = extension._widgets["frequency_units_combo"]

    # Test all frequency units
    units = ["GHz", "MHz", "kHz", "Hz"]

    for i, unit in enumerate(units):
        freq_units_combo.current(i)
        assert freq_units_combo.get() == unit

    # Cycle through units multiple times
    for _ in range(3):
        for i in range(len(units)):
            freq_units_combo.current(i)

    app.close_project(save=False)


def test_fresnel_spin_box_boundaries(add_app) -> None:
    """Test spin box boundary values."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test elevation spin at boundaries
    elevation_spin = extension._widgets["elevation_spin"]
    elevation_values = extension.elevation_resolution_values

    # Set to first value
    elevation_spin.set(str(elevation_values[0]))
    extension.elevation_spin_changed()
    assert extension._widgets["elevation_resolution"].get() == elevation_values[0]

    # Set to last value
    elevation_spin.set(str(elevation_values[-1]))
    extension.elevation_spin_changed()
    assert extension._widgets["elevation_resolution"].get() == elevation_values[-1]

    # Set to middle values
    for val in elevation_values[len(elevation_values) // 2 - 2 : len(elevation_values) // 2 + 2]:
        elevation_spin.set(str(val))
        extension.elevation_spin_changed()

    app.close_project(save=False)


def test_fresnel_theta_scan_max_constraints(add_app) -> None:
    """Test theta scan max with constraint validation."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test update_theta_scan_max_constraints with various elevation resolutions
    test_resolutions = [1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 18.0, 22.5, 30.0]

    for res in test_resolutions:
        extension._widgets["elevation_resolution"].set(res)
        extension.update_theta_scan_max_constraints()

        # Verify theta max is within valid range
        theta_max = extension._widgets["theta_scan_max"].get()
        assert theta_max >= res
        assert theta_max <= 90.0

        # Verify it's a multiple of resolution (with small tolerance for floating point)
        ratio = theta_max / res
        assert abs(ratio - round(ratio)) < 1e-6

    app.close_project(save=False)


def test_fresnel_validate_even_and_divides_90_edge_cases(add_app) -> None:
    """Test validate_even_and_divides_90 with edge cases."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Test with 1 degree steps
    sequence_1deg = [float(i) for i in range(0, 91, 1)]
    is_valid, step, filtered = extension.validate_even_and_divides_90(sequence_1deg)
    assert is_valid is True
    assert step == 1.0

    # Test with 2 degree steps
    sequence_2deg = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
    is_valid, step, filtered = extension.validate_even_and_divides_90(sequence_2deg)
    assert is_valid is True
    assert step == 2.0

    # Test with non-uniform spacing
    non_uniform = [0.0, 5.0, 15.0, 30.0]
    is_valid, step, filtered = extension.validate_even_and_divides_90(non_uniform)
    assert is_valid is False

    # Test with step that doesn't divide 90
    bad_step = [0.0, 7.0, 14.0, 21.0]
    is_valid, step, filtered = extension.validate_even_and_divides_90(bad_step)
    assert is_valid is False

    # Test with only end point
    only_end = [90.0]
    is_valid, step, filtered = extension.validate_even_and_divides_90(only_end)
    assert is_valid is False

    # Test with two points
    two_points = [0.0, 90.0]
    is_valid, step, filtered = extension.validate_even_and_divides_90(two_points)
    assert is_valid is True
    assert step == 90.0

    app.close_project(save=False)


def test_fresnel_snap_theta_scan_max(add_app) -> None:
    """Test snapping theta scan max to valid values."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Set elevation resolution
    extension._widgets["elevation_resolution"].set(5.0)
    extension.update_theta_scan_max_constraints()

    # Test snapping with various values
    test_values = [12.3, 17.8, 23.1, 32.7, 47.5]

    for val in test_values:
        extension.snap_theta_scan_max_slider(val)
        snapped_val = extension._widgets["theta_scan_max"].get()

        # Verify snapped value is multiple of 5.0
        assert abs(snapped_val % 5.0) < 1e-6

    # Test snap_theta_scan_max_spin
    extension._widgets["theta_scan_max_slider"].set(37.3)
    extension.snap_theta_scan_max_spin()
    snapped_val = extension._widgets["theta_scan_max"].get()
    assert abs(snapped_val % 5.0) < 1e-6

    app.close_project(save=False)


def test_fresnel_multiple_slider_movements(add_app) -> None:
    """Test multiple consecutive slider movements."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    elevation_slider = extension._widgets["elevation_slider"]

    # Move slider multiple times
    positions = [0, 1, 2, 1, 0, 2, 1]
    for pos in positions:
        elevation_slider.set(pos)
        extension.elevation_slider_changed(pos)

    # Verify final resolution is correct
    final_resolution = extension._widgets["elevation_resolution"].get()
    expected = extension.elevation_resolution_slider_values[1]
    assert final_resolution == expected

    app.close_project(save=False)


def test_fresnel_widget_existence(add_app) -> None:
    """Test that all expected widgets exist in the extension."""
    # Create HFSS application for testing environment
    app = add_app(
        application=Hfss,
        project="fresnel_test",
        design="design1",
    )

    app.create_setup()

    # Create extension
    extension = FresnelExtension(withdraw=True)

    # Check all critical widgets exist
    expected_widgets = [
        "tabs",
        "extraction_tab",
        "advanced_tab",
        "settings_tab",
        "elevation_slider",
        "elevation_spin",
        "azimuth_slider",
        "azimuth_spin",
        "theta_scan_max_slider",
        "theta_scan_max_spin",
        "setup_combo",
        "setup_sweep_combo",
        "frequency_units_combo",
        "start_frequency",
        "stop_frequency",
        "step_frequency",
        "core_number",
        "tasks_number",
        "keep_mesh_checkbox",
        "validate_button",
        "apply_validate_button",
        "floquet_ports_label",
        "floquet_ports_label_extraction",
        "design_validation_label",
        "design_validation_label_extraction",
    ]

    for widget_name in expected_widgets:
        assert widget_name in extension._widgets, f"Widget {widget_name} not found"

    app.close_project(save=False)
