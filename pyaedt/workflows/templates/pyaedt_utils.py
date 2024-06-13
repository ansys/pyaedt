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

"""
* * * This script is meant to run in IronPython within AEDT. * * *

It contains common methods for the PyAEDT panels.
"""
import os
import random
import string
import sys

from System.Windows.Forms import MessageBox
from System.Windows.Forms import MessageBoxButtons
from System.Windows.Forms import MessageBoxIcon

is_linux = os.name == "posix"


def sanitize_interpreter_path(interpreter_path, version):
    python_version = "3_10" if version > "231" else "3_7"
    if version > "231" and python_version not in interpreter_path:
        interpreter_path = interpreter_path.replace("3_7", "3_10")
    elif version <= "231" and python_version not in interpreter_path:
        interpreter_path = interpreter_path.replace("3_10", "3_7")
    return interpreter_path


def check_file(file_path, oDesktop):
    if not os.path.isfile(file_path):
        show_error(
            '"{}" does not exist. Install PyAEDT using the Python script installer from the PyAEDT '
            "documentation.".format(file_path),
            oDesktop,
        )
        return False
    return True


def get_linux_terminal():
    for terminal in ["x-terminal-emulator", "konsole", "xterm", "gnome-terminal", "lxterminal", "mlterm"]:
        term = which(terminal)
        if term:
            return term
    return None


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def show_error(msg, oDesktop):
    oDesktop.AddMessage("", "", 2, str(msg))
    MessageBox.Show(str(msg), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
    sys.exit()


def environment_variables(oDesktop):
    os.environ["PYAEDT_SCRIPT_PROCESS_ID"] = str(oDesktop.GetProcessID())
    version = str(oDesktop.GetVersion()[:6])
    os.environ["PYAEDT_SCRIPT_VERSION"] = version
    if version > "2023.1":
        os.environ["PYAEDT_SCRIPT_PORT"] = str(oDesktop.GetGrpcServerPort())
    else:
        os.environ["PYAEDT_SCRIPT_PORT"] = str(0)
    if "Ansys Student" in str(oDesktop.GetExeDir()):
        os.environ["PYAEDT_STUDENT_VERSION"] = "True"
    else:
        os.environ["PYAEDT_STUDENT_VERSION"] = "False"
    if is_linux:
        edt_root = os.path.normpath(oDesktop.GetExeDir())
        os.environ["ANSYSEM_ROOT{}".format(version)] = edt_root
        ld_library_path_dirs_to_add = [
            "{}/commonfiles/CPython/3_7/linx64/Release/python/lib".format(edt_root),
            "{}/commonfiles/CPython/3_10/linx64/Release/python/lib".format(edt_root),
            "{}/common/mono/Linux64/lib64".format(edt_root),
            "{}/Delcross".format(edt_root),
            "{}".format(edt_root),
        ]
        os.environ["LD_LIBRARY_PATH"] = ":".join(ld_library_path_dirs_to_add) + ":" + os.getenv("LD_LIBRARY_PATH", "")
        if version > "2023.1":
            os.environ["TCL_LIBRARY"] = os.path.join(
                "{}/commonfiles/CPython/3_10/linx64/Release/python/lib".format(edt_root), "tcl8.5"
            )
            os.environ["TK_LIBRARY"] = os.path.join(
                "{}/commonfiles/CPython/3_10/linx64/Release/python/lib".format(edt_root), "tk8.5"
            )
            os.environ["TKPATH"] = os.path.join(
                "{}/commonfiles/CPython/3_10/linx64/Release/python/lib".format(edt_root), "tk8.5"
            )
        else:
            os.environ["TCL_LIBRARY"] = os.path.join(
                "{}/commonfiles/CPython/3_7/linx64/Release/python/lib".format(edt_root), "tcl8.5"
            )
            os.environ["TK_LIBRARY"] = os.path.join(
                "{}/commonfiles/CPython/3_7/linx64/Release/python/lib".format(edt_root), "tk8.5"
            )
            os.environ["TKPATH"] = os.path.join(
                "{}/commonfiles/CPython/3_7/linx64/Release/python/lib".format(edt_root), "tk8.5"
            )


def generate_unique_name(root_name, suffix="", n=6):
    char_set = string.ascii_uppercase + string.digits
    unique_name = root_name + "_" + "".join(random.choice(char_set) for _ in range(n))  # nosec
    if suffix:
        unique_name += suffix
    return unique_name
