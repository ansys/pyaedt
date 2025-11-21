# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""
Launches an interactive shell with an instance of HFSS.

Omitting the .py in the name of this file hides it from the Electronics Desktop Toolkit menu.
It should be hidden from this menu because the scripts in that menu are meant to be executed using IronPython
cpython_console.py should be run instead of this script.

This file can also serve as a template to modify PyAEDT scripts to take advantage of the command line arguments
provided by the launcher
"""

import atexit
from pathlib import Path
import sys
from IPython import get_ipython
import tempfile

aedt_process_id = int(sys.argv[1])
version = sys.argv[2]
print("Loading the PyAEDT Console.")

try:  # pragma: no cover
    if version <= "2023.1":
        from pyaedt import Desktop
        from pyaedt.generic.general_methods import active_sessions
        from pyaedt.generic.general_methods import is_windows
    else:
        from ansys.aedt.core import *
        import ansys.aedt.core  # noqa: F401
        from ansys.aedt.core import Desktop
        from ansys.aedt.core.generic.general_methods import active_sessions
        from ansys.aedt.core.generic.general_methods import is_windows
        from ansys.aedt.core.generic.file_utils import available_file_name

except ImportError:  # pragma: no cover
    # Debug only purpose. If the tool is added to the ribbon from a GitHub clone, then a link
    # to PyAEDT is created in the personal library.
    console_setup_dir = Path(__file__).resolve().parent
    if "PersonalLib" in console_setup_dir.parts:
        sys.path.append(str(console_setup_dir / ".." / ".." / ".."))
    if version <= "2023.1":
        from pyaedt import Desktop
        from pyaedt.generic.general_methods import active_sessions
        from pyaedt.generic.general_methods import is_windows
    else:
        from ansys.aedt.core import *  # noqa: F401
        import ansys.aedt.core  # noqa: F401
        from ansys.aedt.core import Desktop
        from ansys.aedt.core.generic.general_methods import active_sessions
        from ansys.aedt.core.generic.general_methods import is_windows
        from ansys.aedt.core.generic.file_utils import available_file_name


def release(d):  # pragma: no cover
    d.logger.info("Exiting the PyAEDT Console.")

    d.release_desktop(False, False)


session_found = False
port = 0
student_version = False


sessions = active_sessions(version=version, student_version=False)
if aedt_process_id in sessions:  # pragma: no cover
    session_found = True
    if sessions[aedt_process_id] != -1:
        port = sessions[aedt_process_id]
if not session_found:  # pragma: no cover
    sessions = active_sessions(version=version, student_version=True)
    if aedt_process_id in sessions:
        session_found = True
        student_version = True
        if sessions[aedt_process_id] != -1:
            port = sessions[aedt_process_id]

error = False
if port:  # pragma: no cover
    desktop = Desktop(
        version=version,
        port=port,
        new_desktop=False,
        non_graphical=False,
        close_on_exit=False,
        student_version=student_version,
    )
elif is_windows:  # pragma: no cover
    desktop = Desktop(
        version=version,
        aedt_process_id=aedt_process_id,
        new_desktop=False,
        non_graphical=False,
        close_on_exit=False,
        student_version=student_version,
    )
else:  # pragma: no cover
    print("Error. AEDT should be started in gRPC mode in Linux to connect to PyAEDT")
    print("use ansysedt -grpcsrv portnumber command.")
    error = True

if not error:  # pragma: no cover
    print(" ")

    print("\033[92m****************************************************************")
    print(f"*  ElectronicsDesktop {version} Process ID {aedt_process_id}")
    print(f"*  CPython {sys.version.split(' ')[0]}")
    print("*---------------------------------------------------------------")
    print("*  Example: \033[94m hfss = Hfss() \033[92m")
    print("*  Example: \033[94m m2d = Maxwell2d() \033[92m")
    print("*  Desktop object is initialized: \033[94mdesktop.logger.info('Hello world')\033[92m")
    print("*  \033[31mType exit() to close the console and release the desktop.  \033[92m ")
    print("****************************************************************\033[0m")
    print(" ")

    if is_windows:
        try:
            import win32api
            import win32con

            def handler(ctrl_type):
                if ctrl_type == win32con.CTRL_CLOSE_EVENT:
                    release(desktop)
                    return False
                return True

            win32api.SetConsoleCtrlHandler(handler, 1)
        except ImportError:
            atexit.register(release, desktop)
    else:
        try:
            import signal

            def signal_handler(sig, frame):
                release(desktop)
                sys.exit(0)

            signal.signal(signal.SIGHUP, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ImportError:
            pass
        atexit.register(release, desktop)

if version > "2023.1":  # pragma: no cover

    log_file = Path(tempfile.gettempdir()) / "pyaedt_script.py"
    log_file = available_file_name(log_file)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("# PyAEDT script recorded from PyAEDT Console:\n\n")
        f.write("import ansys.aedt.core\n")
        f.write("from ansys.aedt.core import *\n")

    def log_successful_command(result):
        """
        IPython Hook: Executes after every command (cell).
        Logs the input command only if 'result.error_in_exec' is False (no exception).
        """
        # Check for execution error
        if not result.error_in_exec:
            command = result.info.raw_cell.strip()

            # Avoid logging empty lines, comments, or the hook code itself
            if command and not command.startswith('#') and "log_successful_command" not in command:
                try:
                    # Append the successful command to the log file
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(command + "\n")
                except Exception as e:
                    # Handle potential file writing errors
                    print(f"ERROR: Failed to write to log file: {e}")


    # Register the Hook
    ip = get_ipython()
    if ip:
        # Register the function to run after every command execution
        ip.events.register('post_run_cell', log_successful_command)
        # Inform the user that logging is active
        print(f"Successful commands will be saved to: \033[94m'{log_file}'\033[92m")
        print(" ")
        print(" ")
        print(" ")
