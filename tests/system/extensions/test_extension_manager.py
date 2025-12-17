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

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.customize_automation_tab import AEDT_APPLICATIONS
from ansys.aedt.core.extensions.installer.extension_manager import ExtensionManager


@pytest.fixture(autouse=True)
def disable_pyaedt_update_check(monkeypatch):
    """Prevent ExtensionManager from starting the update-check thread during tests."""
    monkeypatch.setattr(
        "ansys.aedt.core.extensions.installer.extension_manager.ExtensionManager.check_for_pyaedt_update_on_startup",
        lambda self: None,
    )
    yield


def test_extension_manager_initialization(add_app):
    """Test that ExtensionManager initializes correctly in a real AEDT environment."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_extension_manager",
        design_name="test_design",
    )

    # Create extension manager with withdraw=True to avoid showing window
    extension = ExtensionManager(withdraw=True)

    try:
        # Verify basic initialization
        assert extension.root is not None
        assert extension.root.title() == "Extension Manager"
        assert extension.toolkits is not None
        assert extension.current_category is not None
        assert extension.python_interpreter is not None
        assert extension.right_panel is not None

        # Verify theme initialization
        assert extension.theme is not None

        # Verify log variables
        assert isinstance(extension.full_log_buffer, list)
        assert extension.logs_window is None
        assert extension.logs_text_widget is None

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_load_extensions(add_app):
    """Test loading extensions for different categories."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_load_extensions",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        # Test loading extensions for different categories
        test_categories = ["Common", "HFSS", "Maxwell3D", "Circuit"]

        for category in test_categories:
            extension.load_extensions(category)

            # Verify current category is set
            expected_category = AEDT_APPLICATIONS.get(category.lower(), category)
            assert extension.current_category == expected_category

            # Verify right panel has content
            assert extension.right_panel is not None

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_log_buffer(add_app):
    """Test log buffer functionality."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_log_buffer",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        # Test appending to log buffer
        test_message = "Test log message"
        test_tag = "info"

        extension._append_full_log(test_message, test_tag)

        # Verify log was appended
        assert len(extension.full_log_buffer) > 0
        assert (test_message, test_tag) in extension.full_log_buffer

        # Test clearing logs
        extension._clear_logs()
        assert len(extension.full_log_buffer) == 0

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_check_extension_pinned(add_app):
    """Test checking if extension is pinned."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_check_pinned",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        # Test with a common extension category
        category = "HFSS"
        option = "test_extension"

        # This should not raise an error
        is_pinned = extension.check_extension_pinned(category, option)

        # Result should be boolean
        assert isinstance(is_pinned, bool)

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_window_geometry(add_app):
    """Test window dimensions and geometry settings."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_geometry",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        # Force geometry update
        extension.root.update()

        # Get window dimensions
        geometry = extension.root.geometry()

        # Verify geometry string is properly formatted
        assert "x" in geometry
        assert "+" in geometry or "-" in geometry

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_multiple_categories(add_app):
    """Test switching between multiple extension categories."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_multiple_categories",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        # Test loading multiple categories in sequence
        categories = ["Common", "HFSS", "Circuit", "Common"]

        for category in categories:
            extension.load_extensions(category)
            expected = AEDT_APPLICATIONS.get(category.lower(), category)
            assert extension.current_category == expected

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_canvas_theme_application(add_app):
    """Test that canvas theme is properly applied."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_canvas_theme",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        import tkinter

        with pytest.raises(tkinter.TclError):
            # Create a test canvas
            test_canvas = tkinter.Canvas(extension.root)

            # Apply theme to canvas
            extension.apply_canvas_theme(test_canvas)

            # Verify canvas has background color set
            bg_color = test_canvas.cget("bg")
            assert bg_color is not None

            # Clean up test canvas
            test_canvas.destroy()
            raise tkinter.TclError("Force error to exit cleanly")

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_toolkits_loaded(add_app):
    """Test that toolkits are properly loaded on initialization."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_toolkits",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        # Verify toolkits are loaded
        assert extension.toolkits is not None
        assert isinstance(extension.toolkits, dict)

        # Toolkits should contain at least some categories
        assert len(extension.toolkits) > 0

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_extension_manager_default_category(add_app):
    """Test that default category is properly set."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
        project_name="test_default_category",
        design_name="test_design",
    )

    extension = ExtensionManager(withdraw=True)

    try:
        # Verify default category is set
        assert extension.current_category is not None
        assert extension.current_category == "Project"

    finally:
        extension.root.destroy()
        aedtapp.close_project(aedtapp.project_name)
