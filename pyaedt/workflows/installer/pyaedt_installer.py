# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Methods to add PyAEDT in AEDT."""

import os

from pyaedt.generic.general_methods import read_toml
from pyaedt.workflows import customize_automation_tab


def add_pyaedt_to_aedt(
    aedt_version,
    personallib,
):
    """Add PyAEDT tabs in AEDT.

    Parameters
    ----------
    aedt_version : str
        AEDT release.
    personallib : str
        AEDT Personal Lib folder.
    """

    __add_pyaedt_tabs(personallib, aedt_version)


def __add_pyaedt_tabs(personallib, aedt_version):
    """Add PyAEDT tabs in AEDT."""

    pyaedt_tabs = ["Console", "Jupyter", "Run_Script", "ToolkitManager"]

    toolkits_catalog = read_toml(os.path.join(os.path.dirname(__file__), "toolkits_catalog.toml"))

    project_workflows_dir = os.path.dirname(__file__)

    for toolkit in pyaedt_tabs:
        if toolkit in toolkits_catalog.keys():
            toolkit_info = toolkits_catalog[toolkit]
            script_path = None
            if toolkit_info["script"]:
                script_path = os.path.join(project_workflows_dir, toolkit_info["script"])
            icon_file = os.path.join(project_workflows_dir, "images", "large", toolkit_info["icon"])
            template_name = toolkit_info["template"]
            customize_automation_tab.add_script_to_menu(
                toolkit_info["name"],
                script_path,
                template_name,
                icon_file=icon_file,
                product="Project",
                copy_to_personal_lib=True,
                executable_interpreter=None,
                panel="Panel_PyAEDT_Installer",
                personal_lib=personallib,
                aedt_version=aedt_version,
            )
