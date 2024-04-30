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
from pyaedt.workflows import customize_automation_tab


def add_pyaedt_to_aedt(
    aedt_version="2024.1",
    student_version=False,
    use_sys_lib=False,
    new_desktop_session=False,
    non_graphical=False,
    sys_dir="",
    pers_dir="",
):
    """Add PyAEDT tabs in AEDT.

    Parameters
    ----------
    aedt_version : str, optional
        AEDT release.
    student_version : bool, optional
        Whether to use the student version of AEDT. The default
        is ``False``.
    use_sys_lib : bool, optional
       Whether to use the ``syslib`` or ``PersonalLib`` directory. The default is ``False``.
    new_desktop_session : bool, optional
        Whether to create a new AEDT session. The default
        is ``False``
    non_graphical : bool, optional
        Whether to run AEDT in non-graphical mode. The default
        is ``False``.
    sys_dir : str, optional
        Full path of ``syslib`` directory.
    pers_dir : str, optional
        Full path of ``PersonalLib`` directory.

    """
    if not (sys_dir or pers_dir):
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
            sys_dir = d.syslib
            pers_dir = d.personallib

            toolkits = ["Project"]
            # Bug on Linux 23.1 and before where Project level toolkits don't show up. Thus copying to individual design
            # toolkits.
            if not is_windows and aedt_version <= "2023.1":
                toolkits = [
                    "2DExtractor",
                    "CircuitDesign",
                    "HFSS",
                    "HFSS-IE",
                    "HFSS3DLayoutDesign",
                    "Icepak",
                    "Maxwell2D",
                    "Maxwell3D",
                    "Q3DExtractor",
                    "Mechanical",
                ]

            for product in toolkits:
                if use_sys_lib:
                    try:
                        sys_dir = os.path.join(sys_dir, "Toolkits")
                        __add_pyaedt_tabs(d, sys_dir, product, aedt_version, student_version)
                        print("Installed toolkit for {} in sys lib.".format(product))
                    except IOError:
                        pers_dir = os.path.join(pers_dir, "Toolkits")
                        __add_pyaedt_tabs(d, pers_dir, product, aedt_version, student_version)
                        print("Installed toolkit for {} in PersonalLib.".format(product))
                else:
                    pers_dir = os.path.join(pers_dir, "Toolkits")
                    __add_pyaedt_tabs(d, pers_dir, product, aedt_version, student_version)
                    print("Installed toolkit for {} in PersonalLib.".format(product))

        if pid and new_desktop_session:
            try:
                os.kill(pid, 9)
            except Exception:
                pass


def __add_pyaedt_tabs(desktop_object, input_dir, product, aedt_version, student_version=False):
    """Add PyAEDT tabs in AEDT.

    Parameters
    ----------
    desktop_object : :class:pyaedt.desktop.Desktop
        Desktop object.
    input_dir : str
        Path to the toolkit library directory.
    product : str, optional
        Product directory to install the toolkit.
    aedt_version : str, optional
        Version of AEDT to use.
    student_version : bool, optional
        Whether to use the student version of AEDT. The default
        is ``False``.
    """
    project_workflows_dir = os.path.dirname(__file__)

    script_path = os.path.join(project_workflows_dir, "console_setup.py")
    icon_file = os.path.join(project_workflows_dir, "images", "large", "console.png")
    template_name = "PyAEDT_Console"
    customize_automation_tab.add_script_to_menu(
        desktop_object,
        "PyAEDT Console",
        script_path,
        template_name,
        icon_file=icon_file,
        product="Project",
        copy_to_personal_lib=True,
        executable_interpreter=None,
    )

    # files_to_copy = ["Console", "Run_PyAEDT_Script", "Jupyter", "Run_Toolkit_Manager"]
    # # Remove hard-coded version number from Python virtual environment path and replace it with the corresponding AEDT
    # # version's Python virtual environment.
    #
    # jupyter_executable = executable_version_agnostic.replace("python" + exe(), "jupyter" + exe())
    #
    # for file_name in files_to_copy:
    #     with open(os.path.join(current_dir, file_name + ".py_build"), "r") as build_file:
    #         file_name_dest = file_name.replace("_", " ") + ".py"
    #         with open(os.path.join(tool_dir, file_name_dest), "w") as out_file:
    #             print("Building to " + os.path.join(tool_dir, file_name_dest))
    #             build_file_data = build_file.read()
    #             build_file_data = (
    #                 build_file_data.replace("##TOOLKIT_REL_LIB_DIR##", toolkit_rel_lib_dir)
    #                 .replace("##PYTHON_EXE##", executable_version_agnostic)
    #                 .replace("##IPYTHON_EXE##", ipython_executable)
    #                 .replace("##JUPYTER_EXE##", jupyter_executable)
    #                 .replace("##TOOLKIT_MANAGER_SCRIPT##", os.path.join(lib_dir, "../workflows/toolkit_manager.py"))
    #                 .replace("##PYAEDT_STUDENT_VERSION##", str(is_student_version))
    #             )
    #             if not version_agnostic:
    #                 build_file_data = build_file_data.replace(" % version", "")
    #             out_file.write(build_file_data)
    # shutil.copyfile(os.path.join(current_dir, "console_setup.py"), os.path.join(lib_dir, "console_setup.py"))
    # shutil.copyfile(
    #     os.path.join(current_dir, "jupyter_template.ipynb"),
    #     os.path.join(lib_dir, "jupyter_template.ipynb"),
    # )
    # shutil.copyfile(
    #     os.path.join(current_dir, "../workflows/toolkit_manager.py"),
    #     os.path.join(lib_dir, "../workflows/toolkit_manager.py"),
    # )
    # if aedt_version >= "2023.2":
    #     write_tab_config(os.path.join(toolkit_dir, product), lib_dir)
