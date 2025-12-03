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

import sys
import tkinter

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.installer.version_manager import VersionManager


@pytest.fixture(autouse=True)
def disable_pyaedt_update_check(monkeypatch):
    """Prevent update check during tests."""
    monkeypatch.setattr(
        "ansys.aedt.core.extensions.installer.version_manager.VersionManager.check_for_pyaedt_update_on_startup",
        lambda self: None,
    )
    yield


def test_version_manager_initialization(add_app):
    """Test VersionManager initialization in a real AEDT environment."""
    # Create HFSS application for testing environment
    aedtapp = add_app(
        application=Hfss,
    )

    # Get desktop instance
    desktop_aedt = aedtapp._desktop

    # Create tkinter root
    root = tkinter.Tk()

    try:
        # Create version manager
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Verify basic initialization
            assert vm.root is not None
            assert vm.desktop is not None
            assert vm.root.title() == "Version Manager"

            # Verify properties are accessible
            assert vm.venv_path is not None
            assert vm.python_exe is not None
            assert vm.python_version is not None

            # Verify theme initialization
            assert vm.theme_color == "light"
            assert vm.theme is not None
            assert vm.style is not None

            # Verify environment activation
            assert vm.activated_env is not None
            assert isinstance(vm.activated_env, dict)

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_version_manager_venv_properties(add_app):
    """Test venv-related properties."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Test venv_path points to sys.prefix
            assert vm.venv_path == sys.prefix

            # Test python_exe is a string path containing 'python'
            assert isinstance(vm.python_exe, str)
            assert "python" in vm.python_exe.lower()

            # Test python_version format
            version_parts = vm.python_version.split(".")
            assert len(version_parts) == 2
            assert all(part.isdigit() for part in version_parts)

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_version_manager_theme_toggle(add_app):
    """Test theme toggling functionality."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Verify initial theme
            assert vm.theme_color == "light"

            # Toggle to dark theme
            vm.toggle_theme()
            assert vm.theme_color == "dark"

            # Toggle back to light theme
            vm.toggle_theme()
            assert vm.theme_color == "light"

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name, save=False)


def test_version_manager_activate_venv(add_app):
    """Test venv activation."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Call activate_venv again
            vm.activate_venv()

            # Verify environment is set
            assert vm.activated_env is not None
            assert "VIRTUAL_ENV" in vm.activated_env

            # Verify VIRTUAL_ENV points to venv_path
            assert vm.activated_env["VIRTUAL_ENV"] == str(vm.venv_path)

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name, save=False)


def test_version_manager_get_installed_version(add_app):
    """Test getting installed package versions."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Test getting pyaedt version
            pyaedt_version = vm.get_installed_version("pyaedt")
            assert pyaedt_version is not None
            assert pyaedt_version != "Please restart"

            # Test getting version of non-existent package
            fake_version = vm.get_installed_version("nonexistent-package-xyz")
            assert fake_version == "Please restart"

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name, save=False)


def test_version_manager_version_properties(add_app):
    """Test version-related properties."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Test pyaedt_version
            assert vm.pyaedt_version is not None

            # Test pyedb_version
            assert vm.pyedb_version is not None

            # Test aedt_version
            assert vm.aedt_version is not None

            personal_lib = vm.personal_lib
            assert personal_lib is not None

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name, save=False)


def test_version_manager_is_git_available(add_app):
    """Test git availability check."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Test git availability
            is_available = vm.is_git_available()

            # Result should be boolean
            assert isinstance(is_available, bool)

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name)


def test_version_manager_clicked_refresh(add_app):
    """Test refresh functionality."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Call clicked_refresh without restart
            vm.clicked_refresh(need_restart=False)

            # Verify string variables are set
            venv_info = vm.venv_information.get()
            assert venv_info is not None
            assert len(venv_info) > 0

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name, save=False)


def test_version_manager_platform_detection(add_app):
    """Test platform detection."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Verify platform flags are set correctly
            assert isinstance(vm.is_linux, bool)
            assert isinstance(vm.is_windows, bool)
            assert vm.is_linux != vm.is_windows  # Should be opposite

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name, save=False)


def test_version_manager_string_vars_initialization(add_app):
    """Test StringVar initialization."""
    # Create HFSS application for testing environment
    aedtapp = add_app(application=Hfss)

    desktop_aedt = aedtapp._desktop
    root = tkinter.Tk()

    try:
        with pytest.raises(tkinter.TclError):
            vm = VersionManager(root, desktop_aedt)

            # Verify StringVar objects are initialized
            assert vm.venv_information is not None
            assert vm.pyaedt_info is not None
            assert vm.pyedb_info is not None

            # Verify branch name variables
            assert vm.pyaedt_branch_name.get() == "main"
            assert vm.pyedb_branch_name.get() == "main"

            raise tkinter.TclError("Force error to exit cleanly")
    finally:
        root.destroy()
        aedtapp.close_project(aedtapp.project_name, save=False)
