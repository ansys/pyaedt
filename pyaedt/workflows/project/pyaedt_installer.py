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

from pyaedt import is_windows
from pyaedt import pyaedt_path
from pyaedt.generic.general_methods import read_toml
from pyaedt.workflows import customize_automation_tab


def add_pyaedt_to_aedt(
    aedt_version="2024.1",
    student_version=False,
    new_desktop_session=False,
    non_graphical=False,
):
    """Add PyAEDT tabs in AEDT.

    Parameters
    ----------
    aedt_version : str, optional
        AEDT release.
    student_version : bool, optional
        Whether to use the student version of AEDT. The default
        is ``False``.
    new_desktop_session : bool, optional
        Whether to create a new AEDT session. The default
        is ``False``
    non_graphical : bool, optional
        Whether to run AEDT in non-graphical mode. The default
        is ``False``.
    """

    from pyaedt import Desktop
    from pyaedt.generic.general_methods import grpc_active_sessions
    from pyaedt.generic.settings import settings

    sessions = grpc_active_sessions(aedt_version, student_version)
    close_on_exit = True
    if not sessions:
        if not new_desktop_session:
            print("Launching a new AEDT desktop session.")
        new_desktop_session = True
    else:
        close_on_exit = False
    settings.use_grpc_api = True
    with Desktop(
        specified_version=aedt_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        student_version=student_version,
        close_on_exit=close_on_exit,
    ) as d:
        personal_lib_dir = d.odesktop.GetPersonalLibDirectory()
        pers1 = os.path.join(personal_lib_dir, "pyaedt")
        pid = d.odesktop.GetProcessID()
        # Linking pyaedt in PersonalLib for IronPython compatibility.
        if os.path.exists(pers1):
            d.logger.info("PersonalLib already mapped.")
        else:
            if is_windows:
                os.system('mklink /D "{}" "{}"'.format(pers1, pyaedt_path))
            else:
                os.system('ln -s "{}" "{}"'.format(pyaedt_path, pers1))

        __add_pyaedt_tabs(d)

    if pid and new_desktop_session:
        try:
            os.kill(pid, 9)
        except Exception:  # pragma: no cover
            return False


def __add_pyaedt_tabs(desktop_object):
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
                desktop_object,
                toolkit_info["name"],
                script_path,
                template_name,
                icon_file=icon_file,
                product="Project",
                copy_to_personal_lib=True,
                executable_interpreter=None,
            )
