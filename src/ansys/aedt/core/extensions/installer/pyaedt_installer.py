# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

"""Methods to add PyAEDT in AEDT."""

import logging
import os

from ansys.aedt.core.extensions import customize_automation_tab
from ansys.aedt.core.generic.file_utils import read_toml


def add_pyaedt_to_aedt(
    personal_lib,
    skip_version_manager: bool = False,
    skip_extension_manager: bool = False,
    light: bool = False,
    odesktop=None,
) -> bool:
    """Add PyAEDT tabs in AEDT.

    Parameters
    ----------
    personal_lib : str
        AEDT personal library folder.
    skip_version_manager : bool, optional
        Skip the version manager tab. The default is ``False``.
    skip_extension_manager : bool, optional
        Skip the extension manager tab. The default is ``False``.
    light : bool, optional
        Install only Console, optional Extension Manager, and optional Version Manager.
        The default is ``False``.
    odesktop : oDesktop, optional
        Desktop session. The default is ``None``.
    """
    logger = logging.getLogger("Global")
    if not personal_lib:
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if not _desktop_sessions:
            logger.error("Personallib is not provided. There is no available desktop session.")
            return False
        d = list(_desktop_sessions.values())[0]
        personal_lib = d.personallib

    extensions_dir = os.path.join(personal_lib, "Toolkits")
    os.makedirs(extensions_dir, exist_ok=True)

    pyaedt_tabs = ["Utilities", "Run_Script"]
    if not skip_extension_manager:
        pyaedt_tabs.append("ExtensionManager")
    if not skip_version_manager:
        pyaedt_tabs.append("VersionManager")
    # Name of the console utilities group in the Automation tab.
    utilities_title = "PyAEDT Utilities"
    extensions_catalog = read_toml(os.path.join(os.path.dirname(__file__), "extensions_catalog.toml"))

    project_workflows_dir = os.path.dirname(__file__)

    def _install_extension(extension_key, *, group_name=None, group_icon=None):
        extension_info = extensions_catalog.get(extension_key)
        if not extension_info:
            return
        script_path = os.path.join(project_workflows_dir, extension_info["script"]) if extension_info["script"] else None
        icon_file = os.path.join(project_workflows_dir, "images", "large", extension_info["icon"])
        menu_kwargs = {
            "icon_file": icon_file,
            "product": "Project",
            "copy_to_personal_lib": False,
            "panel": "Panel_PyAEDT_Installer",
            "personal_lib": personal_lib,
            "odesktop": odesktop,
        }
        if group_name is not None:
            menu_kwargs["group_name"] = group_name
        if group_icon is not None:
            menu_kwargs["group_icon"] = group_icon
        customize_automation_tab.add_script_to_menu(
            extension_info["name"],
            script_path,
            extension_info["template"],
            **menu_kwargs,
        )

    def _install_utilities_group(group_icon_path):
        console_info = extensions_catalog.get("Console")
        console_icon_file = None
        if console_info:
            console_icon_file = os.path.join(project_workflows_dir, "images", "large", console_info["icon"])
            _install_extension("Console", group_name=utilities_title, group_icon=group_icon_path)

        console_cli_info = extensions_catalog.get("ConsoleCLI")
        if console_cli_info:
            console_cli_script = None
            if console_cli_info["script"]:
                console_cli_script = os.path.join(project_workflows_dir, console_cli_info["script"])
            customize_automation_tab.add_script_to_menu(
                console_cli_info["name"],
                console_cli_script,
                console_cli_info["template"],
                icon_file=console_icon_file,
                product="Project",
                copy_to_personal_lib=False,
                panel="Panel_PyAEDT_Installer",
                personal_lib=personal_lib,
                odesktop=odesktop,
                group_name=utilities_title,
                group_icon=group_icon_path,
            )

        jupyter_info = extensions_catalog.get("Jupyter")
        if not jupyter_info:
            return
        jupyter_script = None
        if jupyter_info["script"]:
            jupyter_script = os.path.join(project_workflows_dir, jupyter_info["script"])
        customize_automation_tab.add_script_to_menu(
            jupyter_info["name"],
            jupyter_script,
            jupyter_info["template"],
            icon_file=console_icon_file,
            product="Project",
            copy_to_personal_lib=False,
            panel="Panel_PyAEDT_Installer",
            personal_lib=personal_lib,
            odesktop=odesktop,
            group_name=utilities_title,
            group_icon=group_icon_path,
        )

    if light:
        _install_extension("Console")
        _install_extension("Run Script")
        if not skip_extension_manager:
            _install_extension("ExtensionManager")
        if not skip_version_manager:
            _install_extension("VersionManager")
        return True

    for extension in pyaedt_tabs:
        if extension == "Utilities":
            group_icon_file = os.path.join(project_workflows_dir, "images", "large", "gallery", "console.png")
            _install_utilities_group(group_icon_file)
            continue
        _install_extension(extension)
    return True
