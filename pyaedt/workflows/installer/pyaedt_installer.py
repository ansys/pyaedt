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
import shutil

from pyaedt.generic.general_methods import read_toml
from pyaedt.workflows import customize_automation_tab
import pyaedt.workflows.templates


def add_pyaedt_to_aedt(
    aedt_version,
    personal_lib,
):
    """Add PyAEDT tabs in AEDT.

    Parameters
    ----------
    aedt_version : str
        AEDT release.
    personal_lib : str
        AEDT personal library folder.
    """

    logger = logging.getLogger("Global")
    if not personal_lib or not aedt_version:
        from pyaedt.generic.desktop_sessions import _desktop_sessions

        if not _desktop_sessions:
            logger.error("'personal_lib' or AEDT version is not provided. There is no available desktop session.")
            return False
        d = list(_desktop_sessions.values())[0]
        personal_lib = d.personallib
        aedt_version = d.aedt_version_id

    extensions_dir = os.path.join(personal_lib, "Toolkits")
    os.makedirs(extensions_dir, exist_ok=True)

    templates_dir = os.path.dirname(pyaedt.workflows.templates.__file__)
    script_file = os.path.join(templates_dir, "pyaedt_utils.py")
    dest_script_path = os.path.join(extensions_dir, "pyaedt_utils.py")
    shutil.copy2(script_file, dest_script_path)

    __add_pyaedt_tabs(personal_lib, aedt_version)


def __add_pyaedt_tabs(personal_lib, aedt_version):
    """Add PyAEDT tabs in AEDT."""

    pyaedt_tabs = ["Console", "Jupyter", "Run_Script", "ExtensionManager"]

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
            customize_automation_tab.add_script_to_menu(
                extension_info["name"],
                script_path,
                template_name,
                icon_file=icon_file,
                product="Project",
                copy_to_personal_lib=True,
                executable_interpreter=None,
                panel="Panel_PyAEDT_Installer",
                personal_lib=personal_lib,
                aedt_version=aedt_version,
            )
