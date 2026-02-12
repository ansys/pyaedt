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
    skip_version_manager: bool=False,
    odesktop=None,
) -> bool:
    """Add PyAEDT tabs in AEDT.

    Parameters
    ----------
    personal_lib : str
        AEDT personal library folder.
    skip_version_manager : bool, optional
        Skip the version manager tab. The default is ``False``.
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

    __add_pyaedt_tabs(personal_lib, skip_version_manager, odesktop)


def __add_pyaedt_tabs(personal_lib, skip_version_manager, odesktop=None) -> None:
    """Add PyAEDT tabs in AEDT."""
    if skip_version_manager:
        pyaedt_tabs = ["Console", "Jupyter", "Run_Script", "ExtensionManager"]
    else:
        pyaedt_tabs = ["Console", "Jupyter", "Run_Script", "ExtensionManager", "VersionManager"]
    # Name of the console utilities group in the Automation tab.
    utilities_title = "PyAEDT Utilities"
    extensions_catalog = read_toml(os.path.join(os.path.dirname(__file__), "extensions_catalog.toml"))

    project_workflows_dir = os.path.dirname(__file__)

    for extension in pyaedt_tabs:
        if extension in extensions_catalog.keys():
            extension_info = extensions_catalog[extension]
            script_path = None
            if extension_info["script"]:
                script_path = os.path.join(project_workflows_dir, extension_info["script"])

            icon_file = os.path.join(project_workflows_dir, "images", "large", extension_info["icon"])
            template_name = extension_info["template"]
            if extension == "Console":
                group_icon_file = os.path.join(project_workflows_dir, "images", "large", "gallery", "console.png")
                customize_automation_tab.add_script_to_menu(
                    extension_info["name"],
                    script_path,
                    template_name,
                    icon_file=icon_file,
                    product="Project",
                    copy_to_personal_lib=False,
                    panel="Panel_PyAEDT_Installer",
                    personal_lib=personal_lib,
                    odesktop=odesktop,
                    group_name=utilities_title,
                    group_icon=group_icon_file,
                )
                console_cli_info = extensions_catalog.get("ConsoleCLI")
                if console_cli_info:
                    console_cli_script = None
                    if console_cli_info["script"]:
                        console_cli_script = os.path.join(project_workflows_dir, console_cli_info["script"])
                    customize_automation_tab.add_script_to_menu(
                        console_cli_info["name"],
                        console_cli_script,
                        console_cli_info["template"],
                        icon_file=icon_file,
                        product="Project",
                        copy_to_personal_lib=False,
                        panel="Panel_PyAEDT_Installer",
                        personal_lib=personal_lib,
                        odesktop=odesktop,
                        group_name=utilities_title,
                        group_icon=group_icon_file,
                    )
            else:
                customize_automation_tab.add_script_to_menu(
                    extension_info["name"],
                    script_path,
                    template_name,
                    icon_file=icon_file,
                    product="Project",
                    copy_to_personal_lib=False,
                    panel="Panel_PyAEDT_Installer",
                    personal_lib=personal_lib,
                    odesktop=odesktop,
                )
