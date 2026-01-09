# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""This module contains the ``Desktop`` class.

This module is used to initialize AEDT and the message manager for managing AEDT.
You can initialize this module before launching an app or
have the app automatically initialize it to the latest installed AEDT version.
"""

import atexit
import datetime
from difflib import get_close_matches
from enum import Enum
import gc
import os
from pathlib import Path
import pkgutil
import re
import shlex
import shutil
import socket
import subprocess  # nosec
import sys
import tempfile
import time
import traceback
from typing import Optional
from typing import Union
import warnings

from ansys.aedt.core import __version__
from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import available_license_feature
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import _is_version_format_valid
from ansys.aedt.core.generic.general_methods import _normalize_version_to_string
from ansys.aedt.core.generic.general_methods import active_sessions
from ansys.aedt.core.generic.general_methods import com_active_sessions
from ansys.aedt.core.generic.general_methods import deprecate_argument
from ansys.aedt.core.generic.general_methods import grpc_active_sessions
from ansys.aedt.core.generic.general_methods import inside_desktop_ironpython_console
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import Settings
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.internal.checks import min_aedt_version
from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions
from ansys.aedt.core.internal.desktop_sessions import _edb_sessions
from ansys.aedt.core.internal.errors import AEDTRuntimeError

LOOPBACK_HOSTS = ("localhost", "127.0.0.1")
"""Tuple of loopback host names."""

pathname = Path(__file__)
pyaedtversion = __version__
modules = [tup[1] for tup in pkgutil.iter_modules()]


class TransportMode(str, Enum):
    """Enum containing the different modes of connection."""

    (INSECURE, UDS, MTLS, WNUA) = ("insecure", "uds", "mtls", "wnua")


class _ServerArgs:
    """Class handling gRPC server arguments (server command line).

    This class should not be instantiated directly. Use the
    :func:`_get_grpcsrv_args<ansys.aedt.core.desktop._get_grpcsrv_args>` function instead.
    """

    def __init__(self, mode, host=None, port=None):
        """Initialize server arguments.

        Parameters
        ----------
        mode : TransportMode
            The transport mode to use.
        host : str, optional
            Host address.
        port : int, optional
            Port number.
        """
        self.__mode = mode
        self.__host = host
        self.__port = port

    @property
    def mode(self):
        """Get transport mode."""
        return self.__mode

    def __check_settings(self):
        """Validate settings to ensure they are compatible with the transport mode."""
        if settings.grpc_local and settings.grpc_listen_all:
            raise AEDTRuntimeError(
                "Invalid gRPC configuration: grpc_local and settings.grpc_listen_all cannot be both True."
            )

    def __repr__(self) -> str:
        self.__check_settings()

        if self.__mode in (TransportMode.UDS, TransportMode.WNUA):
            return f"{self.__port}" if self.__port is not None else ""
        if self.__mode not in (TransportMode.MTLS, TransportMode.INSECURE):
            raise ValueError(f"Invalid transport mode {self.__mode}.")

        host = self.__host if not settings.grpc_listen_all else "0.0.0.0"  # nosec
        mode = (
            "SecureMode"
            if self.__mode == TransportMode.MTLS and os.environ.get("ANSYS_GRPC_CERTIFICATES", None)
            else "InsecureMode"
        )
        return f"{host}:{self.__port}:{mode}" if self.__port is not None else f"{host}:{mode}"


def _get_grpcsrv_args(host: Optional[str], port: int) -> _ServerArgs:
    def check_mtls():
        """Perform checks for remote mTLS connections."""
        certs_folder = os.environ.get("ANSYS_GRPC_CERTIFICATES")
        if not certs_folder:
            raise RuntimeError(
                "Secure mode requires certificates, please set the ANSYS_GRPC_CERTIFICATES "
                "environment variable to the folder containing the certificates."
            )

        for file in ("ca.crt", "client.crt", "client.key"):
            if not (Path(certs_folder) / file).is_file():
                raise FileNotFoundError(f"Certificate file '{file}' not found in folder '{certs_folder}'.")

    if settings.grpc_secure_mode:
        if settings.grpc_local and not os.environ.get("ANSYS_GRPC_CERTIFICATES", None):
            mode = TransportMode.WNUA if os.name == "nt" else TransportMode.UDS
        else:
            mode = TransportMode.MTLS
            check_mtls()
    else:
        mode = TransportMode.INSECURE

    server_args = _ServerArgs(mode=mode, host=host, port=port)
    return server_args


@pyaedt_function_handler()
def launch_aedt(
    full_path: Union[str, Path],
    non_graphical: bool,
    port: int,
    student_version: bool,
    host: Optional[str] = None,
):  # pragma: no cover
    """Launch AEDT in gRPC mode.

    .. warning::

        Do not execute this function with untrusted function argument, environment
        variables or pyaedt global settings.
        See the :ref:`security guide<security_launch_aedt>` for details.
    """
    if settings.grpc_local and settings.grpc_listen_all:
        raise AEDTRuntimeError(
            "Invalid gRPC configuration: settings.grpc_local and settings.grpc_listen_all cannot be both True."
        )

    for k, v in settings.aedt_environment_variables.items():
        os.environ[k] = v

    full_path = Path(full_path)
    if not full_path.exists() or full_path.name.lower() not in {
        "ansysedt",
        "ansysedtsv",
        "ansysedtsv.exe",
        "ansysedt.exe",
    }:
        raise ValueError(f"The path {full_path} is not a valid executable.")
    _check_port(port)

    server_args: _ServerArgs = _get_grpcsrv_args(host, port)
    command = [str(full_path), "-grpcsrv", str(server_args)]
    # NOTE: Update command if PYAEDT_USE_PRE_GRPC_ARGS is set to allow working
    # with previous SP where grpc transport mode were not available
    # This environment variable is not necessary for UDS and WNUA modes.
    if os.environ.get("PYAEDT_USE_PRE_GRPC_ARGS", "False") == "True":
        command[-1] = str(port)
    if non_graphical:
        command.append("-ng")
    if settings.wait_for_license:
        command.append("-waitforlicense")
    if settings.aedt_log_file:
        command.extend(["-Logfile", settings.aedt_log_file])

    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if is_windows:
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS

    pyaedt_logger.info(f"Launching AEDT server with gRPC transport mode: {server_args.mode}")
    pyaedt_logger.debug(f"Launching AEDT server with command: {' '.join(command)}")
    subprocess.Popen(command, **kwargs)  # nosec

    on_ci = os.getenv("ON_CI", "False")
    if not student_version and on_ci != "True" and not settings.skip_license_check:
        available_licenses = available_license_feature()
        if available_licenses > 0:
            pyaedt_logger.info("Electronics Desktop license available.")
        elif available_licenses == 0:  # pragma: no cover
            pyaedt_logger.warning("Electronics Desktop license not found on the default license server.")

    timeout = settings.desktop_launch_timeout
    start = time.time()
    while timeout > 0:
        active_s = active_sessions(student_version=student_version)
        if port in active_s.values():
            break
        timeout -= 1
        time.sleep(1)

    if timeout == 0:
        pyaedt_logger.error(f"Failed to start on gRPC port: {port}.")
        return False, 0

    end = round(time.time() - start, 1)
    pyaedt_logger.info(f"Electronics Desktop started on gRPC port {port} after {end} seconds.")
    return True, port


@pyaedt_function_handler()
def launch_aedt_in_lsf(non_graphical, port, host=None):  # pragma: no cover
    """Launch AEDT in LSF in gRPC mode.

    .. warning::

        Do not execute this function with untrusted input parameters.
        See the :ref:`security guide<security_launch_aedt>` for details.
    """
    for k, v in settings.aedt_environment_variables.items():
        os.environ[k] = v

    _check_port(port)
    _check_settings(settings)

    server_args: _ServerArgs = _get_grpcsrv_args(host, port)
    if not settings.custom_lsf_command:  # pragma: no cover
        if hasattr(settings, "lsf_osrel") and hasattr(settings, "lsf_ui"):
            select_str = (
                f'"select[(osrel={settings.lsf_osrel}) && ui={settings.lsf_ui}] rusage[mem={str(settings.lsf_ram)}]"'
            )
        elif hasattr(settings, "lsf_ui"):
            select_str = f'"select[(ui={settings.lsf_ui}) rusage[mem={settings.lsf_ram}]]"'
        else:
            select_str = f'"-R rusage[mem={settings.lsf_ram}"'
        command = [
            "bsub",
            "-n",
            str(settings.num_cores),
            "-R",
            select_str,
            "-Is",
            settings.lsf_aedt_command,
            "-grpcsrv",
            str(server_args),
        ]
        # NOTE: Update command if PYAEDT_USE_PRE_GRPC_ARGS is set to allow working
        # with previous SP where grpc transport mode were not available
        # This environment variable is not necessary for UDS and WNUA modes.
        if os.environ.get("PYAEDT_USE_PRE_GRPC_ARGS", "False") == "True":
            command[-1] = str(port)
        if settings.lsf_queue:
            command.append(f"-q {settings.lsf_queue}")
        if non_graphical:
            command.append("-ng")
        if settings.wait_for_license:
            command.append("-waitforlicense")
        if settings.aedt_log_file:
            command.extend(["-Logfile", settings.aedt_log_file])
    else:  # pragma: no cover
        command = shlex.split(settings.custom_lsf_command)
        command.append("-grpcsrv")
        command.append(str(server_args))
        # NOTE: Update command if PYAEDT_USE_PRE_GRPC_ARGS is set to allow working
        # with previous SP where grpc transport mode were not available
        # This environment variable is not necessary for UDS and WNUA modes.
        if os.environ.get("PYAEDT_USE_PRE_GRPC_ARGS", "False") == "True":
            command[-1] = str(port)
    command_str = " ".join(str(x) for x in command)
    pyaedt_logger.info("LSF Command: '" + command_str + "'")

    def lsf_message(x):
        return x.stderr.readline().strip().decode("utf-8", "replace")

    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
    except FileNotFoundError as e:
        raise AEDTRuntimeError("Failed to start AEDT in LSF. Check the LSF configuration settings.") from e

    timeout = settings.lsf_timeout
    i = 0
    while i < timeout:
        err = lsf_message(p)  # noqa
        pyaedt_logger.info("[LSF]:" + err)
        m = re.search(r"<<Starting on (.+?)>>", err)
        if m:
            aedt_startup_timeout = 120
            k = 0
            # LSF resources are assigned. Make sure AEDT starts
            while not _is_port_occupied(port, machine_name=m.group(1)):
                if k > aedt_startup_timeout:
                    pyaedt_logger.error("LSF allocated resources, but AEDT was unable to start due to a timeout.")
                    return False, err
                time.sleep(1)
                k += 1
            return True, m.group(1)
        i += 1
        time.sleep(1)
    return False, err


def _check_port(port):
    """Check port."""
    try:
        port = int(port)
    except ValueError:
        raise ValueError(f"The port {port} is not a valid integer.")


def _check_settings(settings: Settings):
    """Check settings."""
    if not isinstance(settings.num_cores, int) or settings.num_cores <= 0:
        raise ValueError("Invalid number of cores.")
    if not isinstance(settings.lsf_ram, int) or settings.lsf_ram <= 0:
        raise ValueError("Invalid memory value.")
    if not settings.lsf_aedt_command:
        raise ValueError("Invalid LSF AEDT command.")


def _is_port_occupied(port, host=None):
    """Check if a port is occupied."""
    if host is None:
        host = "127.0.0.1"
    if not port:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def _find_free_port():
    from contextlib import closing

    host = "127.0.0.1"
    pyaedt_logger.debug(f"Looking for free port on {host}.")

    def _find(host):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind((host, 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    while True:
        new_port = _find(host)
        if new_port not in list(active_sessions().values()) and new_port not in range(50051, 50070, 1):
            pyaedt_logger.debug(f"Port selected: {new_port}")
            return new_port
        time.sleep(0.1)


def exception_to_desktop(ex_value, tb_data):  # pragma: no cover
    """Write the trace stack to AEDT when a Python error occurs.

    The message is added to the AEDT global logger and to the log file (if present).

    Parameters
    ----------
    ex_value : str
        Type of the exception.
    tb_data : str
        Traceback data.

    """
    tb_trace = traceback.format_tb(tb_data)
    tblist = tb_trace[0].split("\n")
    pyaedt_logger.error(str(ex_value))
    for el in tblist:
        pyaedt_logger.error(el)


def is_student_version(oDesktop):
    edt_root = Path(oDesktop.GetExeDir())
    if is_windows and Path(edt_root).is_dir():
        if any("ansysedtsv" in fn.lower() for fn in os.listdir(edt_root)):  # pragma no cover
            return True
    return False


class Desktop(PyAedtBase):
    """Provides the Ansys Electronics Desktop (AEDT) interface.

    Parameters
    ----------
    version : str, int, float, optional
        Version of AEDT to use. The default is ``None``, in which case the
        active setup or latest installed version is used.
        Examples of input values are ``252``, ``25.2``,``2025.2``,``"2025.2"``.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the machine.
        The default is ``True``.
    close_on_exit : bool, optional
        Whether to close AEDT on exit. The default is ``True``.
        This option is used only when Desktop is used in a context manager (``with`` statement).
        If Desktop is used outside a context manager, see the ``release_desktop`` arguments.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``.
    machine : str, optional
        Machine name to connect the oDesktop session to. This parameter works only in 2022 R2
        and later. The remote server must be up and running with the command
        ``"ansysedt.exe -grpcsrv portnum"``. If the machine is `"localhost"`, the server also
        starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on the already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 and
        later. The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop = False``.

    Examples
    --------
    Launch AEDT 2025 R1 in non-graphical mode and initialize HFSS.

    >>> import ansys.aedt.core
    >>> desktop = ansys.aedt.core.Desktop(version="2025.2", non_graphical=False)
    PyAEDT INFO: pyaedt v...
    PyAEDT INFO: Python version ...
    >>> hfss = ansys.aedt.core.Hfss(design="HFSSDesign1")
    PyAEDT INFO: Project...
    PyAEDT INFO: Added design 'HFSSDesign1' of type HFSS.

    Launch AEDT 2025 R1 in graphical mode and initialize HFSS.

    >>> desktop = Desktop(252)
    PyAEDT INFO: pyaedt v...
    PyAEDT INFO: Python version ...
    >>> hfss = ansys.aedt.core.Hfss(design="HFSSDesign1")
    PyAEDT INFO: No project is defined. Project...
    """

    # _sessions = {}
    _invoked_from_design = False

    def __new__(cls, *args, **kwargs):
        # The following commented lines will be useful when we will need to search among multiple saved desktop.
        specified_version = (
            kwargs.get("specified_version")
            or kwargs.get("version")
            or settings.aedt_version
            or (None if (not args or args[0] is None) else args[0])
        )
        if "new_desktop_session" in kwargs or "new_desktop" in kwargs:
            new_desktop = kwargs.get("new_desktop_session") or kwargs.get("new_desktop")
        else:
            new_desktop = True if (not args or len(args) < 3) else args[2]

        # student_version = kwargs.get("student_version") or False if (not args or len(args)<5) else args[4]
        # machine = kwargs.get("machine") or "" if (not args or len(args)<6) else args[5]
        specified_version = _normalize_version_to_string(specified_version)
        port = kwargs.get("port") or 0 if (not args or len(args) < 7) else args[6]
        aedt_process_id = kwargs.get("aedt_process_id") or None if (not args or len(args) < 8) else args[7]
        if not settings.remote_api:
            pyaedt_logger.info(f"Python version {sys.version}.")
        pyaedt_logger.info(f"PyAEDT version {__version__}.")
        if settings.use_multi_desktop and not inside_desktop_ironpython_console and new_desktop:
            pyaedt_logger.info("Initializing new Desktop session.")
            return object.__new__(cls)
        elif len(_desktop_sessions.keys()) > 0:
            if settings.use_multi_desktop and (port or aedt_process_id or specified_version):
                for el in list(_desktop_sessions.values()):
                    if (
                        (port != 0 and el.port == port)
                        or (aedt_process_id and el.aedt_process_id == aedt_process_id)
                        or (not port and not aedt_process_id and el.aedt_version_id == specified_version)
                    ):
                        return el
                return object.__new__(cls)
            sessions = list(_desktop_sessions.keys())
            try:
                process_id = _desktop_sessions[sessions[0]].odesktop.GetProcessID()
                pyaedt_logger.info(f"Returning found Desktop session with PID {process_id}!")
                cls._invoked_from_design = False
                return _desktop_sessions[sessions[0]]
            except Exception:
                del _desktop_sessions[sessions[0]]
                pyaedt_logger.info("Initializing new Desktop session.")
                return object.__new__(cls)
        else:
            pyaedt_logger.info("Initializing new Desktop session.")
            return object.__new__(cls)

    @pyaedt_function_handler()
    def __init__(
        self,
        version=None,
        non_graphical=False,
        new_desktop=True,
        close_on_exit=True,
        student_version=False,
        machine=None,
        port=0,
        aedt_process_id=None,
    ):
        """Initialize desktop."""
        # Check if already initialized and returning object if so.
        result = self._check_if_initialized()
        if result:
            return
        # Initialize Desktop variables.

        self.__closed = False
        self.__aedt_version_id = version
        self.__aedt_install_dir = None
        self.__aedt_process_id = (
            int(os.getenv("PYAEDT_SCRIPT_PROCESS_ID"))
            if os.getenv("PYAEDT_SCRIPT_PROCESS_ID", None)
            else aedt_process_id
        )
        self.__launched_by_pyaedt = False
        self.__non_graphical = (
            True if os.getenv("PYAEDT_NON_GRAPHICAL", "false").lower() in ("true", "1", "t") else non_graphical
        )
        self.__close_on_exit = close_on_exit
        self.__machine = machine
        self.__port = port
        self.__is_grpc_api = True
        self.__student_version = False
        self.__aedt_version_string = ""
        self.__starting_mode = "grpc"
        self.__new_desktop = (
            True if os.getenv("PYAEDT_DOC_GENERATION", "False").lower() in ("true", "1", "t") else new_desktop
        )
        self.aedt_version_id = (
            str(os.getenv("PYAEDT_SCRIPT_VERSION"))
            if os.getenv("PYAEDT_SCRIPT_VERSION", None)
            else version
            if version
            else list(_desktop_sessions.values())[-1].aedt_version_id
            if _desktop_sessions
            else None
        )
        self.__desktop = None
        self._connected_app_instances = 0
        self.__logger = None
        self.__logfile = None

        # Check version arguments and installed AEDT versions.
        self.__check_version(version, student_version)

        # Starting AEDT
        if "console" in self.__starting_mode:  # pragma no cover
            # technically not a startup mode, we have just to load oDesktop
            self.odesktop = sys.modules["__main__"].oDesktop
            self.close_on_exit = False
            try:
                self.non_graphical = self.odesktop.GetIsNonGraphical()
            except Exception:  # pragma: no cover
                self.non_graphical = non_graphical
            self.is_grpc_api = False
        else:
            settings.aedt_version = self.aedt_version_id
            if self.__starting_mode == "com":  # pragma no cover
                self.logger.info("Launching PyAEDT with CPython and PythonNET.")
                self.__init_dotnet()
            elif self.__starting_mode == "grpc":
                result = self.__init_grpc()
                if not result:
                    raise Exception("Failed to connect to AEDT via gRPC.")

        # Setup logging.
        self.__set_logger_file()
        settings.enable_desktop_logs = not self.non_graphical and self.aedt_version_id < "2024.2"
        self.__init_desktop()

        self._check_new_desktop(aedt_process_id, student_version)

        # save the current desktop session in the database
        _desktop_sessions[self.aedt_process_id] = self
        # Register the desktop closure to be called at exit unless asked not to.
        atexit.register(
            lambda: self.__release_and_close_desktop(close_projects=close_on_exit, close_aedt_app=close_on_exit)
        )

    @property
    def aedt_version_id(self) -> str:
        return self.__aedt_version_id

    @aedt_version_id.setter
    def aedt_version_id(self, value):
        if isinstance(value, int):
            value = f"20{str(value)[:2]}.{str(value)[2:3]}"
        elif isinstance(value, float):
            value = f"{value}"
        self.__aedt_version_id = value
        settings.aedt_version = value

    @property
    def aedt_process_id(self) -> int:
        return self.__aedt_process_id

    @aedt_process_id.setter
    def aedt_process_id(self, value):
        self.__aedt_process_id = value

    @pyaedt_function_handler()
    def _check_if_initialized(self) -> bool:
        if getattr(self, "_initialized", None) is not None and self._initialized:
            try:
                self.grpc_plugin.recreate_application(True)
            except Exception:
                pyaedt_logger.debug("Failed to recreate application.")
            return True
        else:
            self._initialized = True
        self._initialized_from_design = True if Desktop._invoked_from_design else False
        Desktop._invoked_from_design = False
        return False

    @property
    def launched_by_pyaedt(self) -> bool:
        """Flag to check if AEDT was launched by PyAEDT."""
        return self.__launched_by_pyaedt

    @launched_by_pyaedt.setter
    def launched_by_pyaedt(self, value):
        self.__launched_by_pyaedt = value

    @property
    def non_graphical(self) -> bool:
        """Whether AEDT is running in non-graphical mode."""
        return self.__non_graphical

    @non_graphical.setter
    def non_graphical(self, value):
        self.__non_graphical = value

    @property
    def close_on_exit(self) -> bool:
        """Whether AEDT will close on exit."""
        return self.__close_on_exit

    @close_on_exit.setter
    def close_on_exit(self, value):
        self.__close_on_exit = value

    @property
    def machine(self) -> str:
        """Machine name."""
        if self.__machine is None:
            self._check_machine()
        return self.__machine

    @machine.setter
    def machine(self, value):
        self.__machine = value

    @property
    def port(self) -> int:
        """Port number."""
        if not self.__port:
            self._validate_port()
        return self.__port

    @port.setter
    def port(self, value):
        self.__port = value

    @property
    def is_grpc_api(self) -> bool:
        """Whether the connection is through gRPC API."""
        return self.__is_grpc_api

    @is_grpc_api.setter
    def is_grpc_api(self, value):
        self.__is_grpc_api = value

    @property
    def student_version(self) -> bool:
        """Whether AEDT is the student version."""
        return self.__student_version

    @student_version.setter
    def student_version(self, value):
        self.__student_version = value

    @property
    def new_desktop(self) -> bool:
        """Whether a new session will be started or not."""
        return self.__new_desktop

    @new_desktop.setter
    def new_desktop(self, value):
        self.__new_desktop = value

    @property
    def aedt_version_string(self) -> str:
        """AEDT version string."""
        return self.__aedt_version_string

    @aedt_version_string.setter
    def aedt_version_string(self, value):
        self.__aedt_version_string = value

    @pyaedt_function_handler()
    def check_starting_mode(self):
        # start the AEDT opening decision tree
        # starting_mode can be one of these: "grpc", "com", "console_in", "console_out"
        if "oDesktop" in dir(sys.modules["__main__"]):  # pragma: no cover
            # we are inside the AEDT Ironpython console
            self.logger.info("Ironpython session with embedded oDesktop")
            self.__starting_mode = "console_in"
        elif is_linux:
            self.__starting_mode = "grpc"
        elif is_windows and "pythonnet" not in modules:
            self.__starting_mode = "grpc"
        elif settings.remote_rpc_session:
            self.__starting_mode = "grpc"
        elif self.aedt_process_id and not self.new_desktop:  # pragma: no cover
            # connecting to an existing session has the precedence over use_grpc_api user preference
            sessions = active_sessions(
                version=self.aedt_version_id, student_version=self.student_version, non_graphical=self.non_graphical
            )
            self.logger.info(sessions)
            if self.aedt_process_id in sessions:
                if sessions[self.aedt_process_id] != -1:
                    self.port = sessions[self.aedt_process_id]
                    self.__starting_mode = "grpc"
                else:
                    self.__starting_mode = "com"
            else:
                raise ValueError(
                    f"The version specified ({self.aedt_version_id}) doesn't correspond "
                    "to the pid specified ({self.aedt_process_id})"
                )
        elif float(self.aedt_version_id) < 2022.2:  # pragma no cover
            self.__starting_mode = "com"
            if self.non_graphical:
                self.logger.disable_desktop_log()
        elif float(self.aedt_version_id) == 2022.2:  # pragma no cover
            if self.non_graphical:
                self.logger.disable_desktop_log()
            if self.machine and self.port:
                self.__starting_mode = "grpc"  # if the machine and port is specified, user wants to use gRPC
            elif settings.use_grpc_api is None:
                self.__starting_mode = "com"  # default if user doesn't specify use_grpc_api
            else:
                self.__starting_mode = "grpc" if settings.use_grpc_api else "com"
        elif float(self.aedt_version_id) > 2022.2:
            if settings.use_grpc_api is None:  # pragma no cover
                self.__starting_mode = "grpc"  # default if user doesn't specify use_grpc_api
            else:
                self.__starting_mode = "grpc" if settings.use_grpc_api else "com"
        else:  # pragma: no cover
            # it should not arrive here, it means that there is a starting case not covered by the decision tree
            raise Exception("Unsupported AEDT starting mode")

    @property
    def aedt_install_dir(self):
        """AEDT installation path."""
        return self.__aedt_install_dir

    @aedt_install_dir.setter
    def aedt_install_dir(self, value):
        self.__aedt_install_dir = value

    @pyaedt_function_handler()
    def _check_new_desktop(self, aedt_process_id, student_version):
        if aedt_process_id and self.aedt_process_id != aedt_process_id:  # pragma no cover
            raise Exception(
                f"AEDT started a new session instead of connecting to the session with pid: {aedt_process_id}"
            )

        current_is_student = is_student_version(self.odesktop)
        if student_version ^ current_is_student:
            self.__logger.warning(
                f"AEDT started as {'Student' if current_is_student else 'Regular'} version, "
                f"but requested as {'Student' if student_version else 'Regular'} version."
            )
        self.student_version = current_is_student

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):  # pragma no cover
        # Write the trace stack to the log file if an exception occurred in the main script.
        if ex_type:
            self.__exception(ex_value, ex_traceback)
        if self.close_on_exit:
            self.close_desktop()
            self.__closed = True
        else:
            self.release_desktop(False, False)
            self.__closed = True

    @pyaedt_function_handler()
    def __getitem__(self, project_design_name):
        """Get the application interface object (Hfss, Icepak, Maxwell3D...) for a given project name and design name.

        Parameters
        ----------
        project_design_name : List
            Project and design name.

        Returns
        -------
        :class:Application interface
            Returns None if project and design name are not found.

        """
        from ansys.aedt.core import get_pyaedt_app

        if len(project_design_name) != 2:
            return None
        if isinstance(project_design_name[0], int) and project_design_name[0] < len(self.project_list):
            projectname = self.project_list[project_design_name[0]]
        elif isinstance(project_design_name[0], str) and project_design_name[0] in self.project_list:
            projectname = project_design_name[0]
        else:
            return None

        initial_oproject = self.active_project()
        if initial_oproject.GetName() != projectname:  # pragma no cover
            self.active_project(projectname)

        if isinstance(project_design_name[1], int) and project_design_name[1] < len(self.design_list()):
            designname = self.design_list()[project_design_name[1]]
        elif isinstance(project_design_name[1], str) and project_design_name[1] in self.design_list():
            designname = project_design_name[1]
        else:
            return None

        return get_pyaedt_app(projectname, designname, self)

    # ################################## #
    #             Properties             #
    # ################################## #

    @property
    @min_aedt_version("2023.2")
    def are_there_simulations_running(self):
        """Check if there are simulation running.

        Returns
        -------
        float

        """
        return self.odesktop.AreThereSimulationsRunning()

    @property
    def current_version(self):
        """Current AEDT version."""
        return aedt_versions.current_version

    @property
    def current_student_version(self):
        """Current AEDT student  version."""
        return aedt_versions.current_student_version

    @property
    def installed_versions(self):
        """Dictionary of AEDT versions installed on the system and their installation paths."""
        return aedt_versions.installed_versions

    @property
    def install_path(self):
        """Installation path for AEDT."""
        version_key = settings.aedt_version
        try:
            return self.installed_versions[version_key]
        except Exception:  # pragma: no cover
            return self.installed_versions[version_key + "CL"]

    @pyaedt_function_handler()
    def get_example(self, example_name, folder_name="."):
        """Retrieve the path to a built-in example project.

        Parameters
        ----------
        example_name : str
            Name of the example for which the full path is desired.
        folder_name : str, optional
            Name of the subfolder in the ``"Examples"`` folder where the example having
            ``example_name`` can be found. The default is ``"."`` which points to
            ``self.install_path / "Examples"``

        Returns
        -------
        pathlib.Path
            Return the path to the example file if found, otherwise ``None``.

        Examples
        --------
        Create a copy of a built-in example.

        >>> import shutil
        >>> from ansys.aedt.core import Desktop
        >>> from pathlib import Path
        >>> working_folder = Path("C:\") / "path" / "to" / "target_folder"  # Windows
        >>> d = Desktop(version=252)
        >>> example_path = d.get_example("5G_SIW_Aperture_Antenna")
        >>> new_project = working_folder / example_path.name
        >>> working_folder.mkdir(parents=True, exist_ok=True)
        >>> shutil.copytree(example_path, new_project)  # Copy example to new working folder.
        """
        root = Path(self.install_path) / "Examples" / folder_name

        # Gather all files
        all_files = [f for f in root.rglob("*") if f.is_file() and not f.suffix.lower() == ".pdf"]

        # Normalize names for fuzzy matching
        filenames = [f.name.lower() for f in all_files]
        name_lower = example_name.lower()

        # Get close matches
        close = get_close_matches(name_lower, filenames, n=1, cutoff=0.6)

        if close:
            match_name = close[0]
            # Find the original Path object that matches the filename (case-insensitive)
            for file in all_files:
                if file.name.lower() == match_name:
                    return file.resolve()

    @property
    def logger(self):
        """AEDT logger."""
        if self.__logger is None:
            self.__logger = pyaedt_logger
            if settings.enable_screen_logs:
                self.__logger.enable_stdout_log()
            else:
                self.__logger.disable_stdout_log()
            if settings.enable_file_logs:
                self.__logger.enable_log_on_file()
            else:
                self.__logger.disable_log_on_file()
            if settings.enable_desktop_logs:
                self.__logger.enable_desktop_log()
            else:
                self.__logger.disable_desktop_log()
        return self.__logger

    @property
    def odesktop(self):
        """AEDT instance containing all projects and designs.

        Examples
        --------
        Get the COM object representing the desktop.

        >>> from ansys.aedt.core import Desktop
        >>> d = Desktop()
        >>> d.odesktop
        """
        if settings.use_grpc_api:
            tries = 0
            while tries < 5:
                try:
                    self.__desktop = self.grpc_plugin.odesktop
                    return self.__desktop
                except Exception:
                    tries += 1
                    time.sleep(1)
        return self.__desktop

    @odesktop.setter
    def odesktop(self, val):
        self.__desktop = val

    @property
    def messenger(self):
        """Messenger manager for the AEDT logger."""
        return pyaedt_logger

    @property
    def personallib(self):
        """PersonalLib directory.

        Returns
        -------
        str
            Full absolute path for the ``PersonalLib`` directory.

        """
        return self.odesktop.GetPersonalLibDirectory()

    @property
    def src_dir(self):
        """Python source directory.

        Returns
        -------
        str
            Full absolute path for the ``python`` directory.

        """
        return Path(__file__)

    @property
    def syslib(self):
        """SysLib directory.

        Returns
        -------
        str
            Full absolute path for the ``SysLib`` directory.

        """
        return self.odesktop.GetLibraryDirectory()

    @property
    def pyaedt_dir(self):
        """PyAEDT directory.

        Returns
        -------
        str
           Full absolute path for the ``pyaedt`` directory.

        """
        return Path(__file__).parent

    @property
    def userlib(self):
        """UserLib directory.

        Returns
        -------
        str
            Full absolute path for the ``UserLib`` directory.

        """
        return self.odesktop.GetUserLibDirectory()

    @property
    def grpc_mode(self):
        server_args: _ServerArgs = _get_grpcsrv_args(self.machine, self.port)
        return server_args.mode

    # ############################################ #
    #                Public methods                #
    # ############################################ #

    @pyaedt_function_handler()
    def active_design(self, project_object=None, name=None, design_type=None):
        """Get the active design.

        Parameters
        ----------
        project_object : optional
            AEDT project object. The default is ``None``, in which case the active project is used.

        name : str, optional
            Name of the design to make active.
            The default is ``None``, in which case the active design is returned.

        design_type : str, optional
            Name of the active design to make active.
            The default is ``None``, in which case the active design is returned.

        References
        ----------
        >>> oProject.GetActiveDesign
        >>> oProject.SetActiveDesign
        """
        if not project_object:
            project_object = self.active_project()
        if not project_object:
            return None
        if not name:
            active_design = None
            try:
                active_design = project_object.GetActiveDesign()
            except Exception:
                active_design = project_object.SetActiveDesign(self.design_list(project_object.GetName())[0])
            finally:
                if not active_design and self.design_list(project_object.GetName()):
                    active_design = project_object.SetActiveDesign(self.design_list(project_object.GetName())[0])
        else:
            try:
                active_design = project_object.SetActiveDesign(name)
            except Exception:
                return None
        if is_linux and settings.aedt_version == "2024.1" and design_type == "Circuit Design":  # pragma: no cover
            time.sleep(1)
            self.close_windows()
        warning_msg = f"Active Design set to {active_design.GetName()}"
        pyaedt_logger.info(warning_msg)
        return active_design

    @pyaedt_function_handler()
    def active_project(self, name=None):
        """Get the active project.

        Parameters
        ----------
        name : str, optional
            Name of the active project to make active.
            The default is ``None``, in which case the active project is returned.

        References
        ----------
        >>> oDesktop.GetActiveProject
        >>> oDesktop.SetActiveProject
        """
        if not name:
            active_project = self.odesktop.GetActiveProject()
            if not active_project and self.project_list:
                active_project = self.odesktop.SetActiveProject(self.project_list[0])
        else:
            try:
                active_project = self.odesktop.SetActiveProject(name)
            except Exception:
                self.logger.error(f"Failed to set active project to {name}")
                self.logger.error(f"Current available projects: {self.project_list}")
                return None
        if is_linux and settings.aedt_version == "2024.1":  # pragma: no cover
            time.sleep(1)
            self.close_windows()
        return active_project

    @pyaedt_function_handler()
    def close_windows(self):
        """Close all windows.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oDesktop.CloseAllWindows
        """
        self.odesktop.CloseAllWindows()
        return True

    @property
    def project_list(self):
        """Get a list of projects.

        Returns
        -------
        List
            List of projects.

        """
        return list(self.odesktop.GetProjectList())

    @pyaedt_function_handler()
    def analyze_all(self, project=None, design=None):  # pragma: no cover
        """Analyze all setups in a project.

        Parameters
        ----------
        project : str, optional
            Project name. The default is ``None``, in which case the active project
            is used.
        design : str, optional
            Design name. The default is ``None``, in which case all designs in
            the project are analyzed.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not project:
            oproject = self.active_project()
        else:
            oproject = self.active_project(project)
        if oproject:
            if not design:
                oproject.AnalyzeAll()
            else:
                odesign = self.active_design(oproject, design)
                if odesign:
                    odesign.AnalyzeAll()
        return True

    @pyaedt_function_handler()
    def clear_messages(self):
        """Clear all AEDT messages.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.odesktop.ClearMessages("", "", 3)
        return True

    @pyaedt_function_handler()
    def save_project(self, project_name=None, project_path=None):
        """Save the project.

        Parameters
        ----------
        project_name : str, optional
            Project name. The default is ``None``, in which case the active project
            is used.
        project_path : str, Path, optional
            Full path to the project. The default is ``None``, in which case the current project is saved.
            If a path is provided, "save as" is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not project_name:
            oproject = self.odesktop.GetActiveProject()
            project_name = oproject.GetName()
        else:
            oproject = self.odesktop.SetActiveProject(project_name)
        if project_path:
            project_path = Path(project_path)
            # check if the path ends with a file (by verifying if it has an extension)
            if project_path.suffix:
                final_path = project_path
            else:
                final_path = project_path / (project_name + ".aedt")
            oproject.SaveAs(str(final_path), True)
        else:
            oproject.Save()
        return True

    @pyaedt_function_handler()
    def project_path(self, project_name=None):
        """Get the path to the project.

        Parameters
        ----------
        project_name : str, optional
            Project name. The default is ``None``, in which case the active
            project is used.

        Returns
        -------
        str
            Path to the project.

        """
        if not project_name:
            oproject = self.active_project()
        else:
            oproject = self.active_project(project_name)
        if oproject:
            return oproject.GetPath()
        return None

    @pyaedt_function_handler()
    def design_list(self, project=None):
        """Get a list of the designs.

        Parameters
        ----------
        project : str, optional
            Project name. The default is ``None``, in which case the active
            project is used.

        Returns
        -------
        List
            List of the designs.
        """
        updateddeslist = []
        if not project:
            oproject = self.active_project()
        else:
            oproject = self.active_project(project)
        if oproject:
            deslist = list(oproject.GetTopDesignList())
            for el in deslist:
                m = re.search(r"[^;]+$", el)
                updateddeslist.append(m.group(0))
        return updateddeslist

    @pyaedt_function_handler()
    def design_type(self, project_name=None, design_name=None):
        """Get the type of design.

        Parameters
        ----------
        project_name : str, optional
            Project name. The default is ``None``, in which case the active
            project is used.
        design_name : str, optional
            Design name. The default is ``None``, in which case the active
            design is used.

        Returns
        -------
        str
            Design type.
        """
        if not project_name:
            oproject = self.active_project()
        else:
            oproject = self.active_project(project_name)
        if not oproject:  # pragma: no cover
            return ""
        if not design_name:
            odesign = self.active_design(oproject)
        else:
            odesign = self.active_design(oproject, design_name)
        if odesign:
            return odesign.GetDesignType()
        else:  # pragma: no cover
            return ""

    def __exception(self, ex_value, tb_data):  # pragma: no cover
        """Write the trace stack to AEDT when a Python error occurs.

        Parameters
        ----------
        ex_value : str
            Type of the exception.
        tb_data : str
            Traceback data.

        Returns
        -------
        str
            Type of the exception.

        """
        tb_trace = traceback.format_tb(tb_data)
        tblist = tb_trace[0].split("\n")
        self.logger.error(str(ex_value))
        for el in tblist:
            if el:
                self.logger.error(el)

        return str(ex_value)

    @pyaedt_function_handler()
    def load_project(self, project_file, design_name=None):
        """Open an AEDT project based on a project and optional design.

        Parameters
        ----------
        project_file : str
            Full path and name for the project.
        design_name : str, optional
            Design name. The default is ``None``.

        Returns
        -------
        :def :`ansys.aedt.core.Hfss`
            Any of the PyAEDT App initialized.

        References
        ----------
        >>> oDesktop.OpenProject

        """
        if Path(project_file).stem in self.project_list:
            proj = self.active_project(Path(project_file).stem)
        else:
            proj = self.odesktop.OpenProject(project_file)
        if proj:
            active_design = self.active_design(proj)
            if design_name and design_name in proj.GetChildNames():  # pragma: no cover
                return self[[proj.GetName(), design_name]]
            elif active_design:
                return self[[proj.GetName(), active_design.GetName()]]
            return True
        else:  # pragma: no cover
            return False

    @pyaedt_function_handler()
    def __release_aedt_application(self, pid, is_grpc_api):
        """Release the AEDT API.

        Parameters
        ----------
        desktop_class : :class:ansys.aedt.core.desktop.Desktop
            Desktop class.
        pid : int
            Process ID of the desktop app that is being closed.
        is_grpc_api : bool
            Whether the active AEDT session is gRPC or COM.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if settings.remote_rpc_session or (settings.aedt_version >= "2022.2" and is_grpc_api):
            for k, d in _desktop_sessions.items():
                if k == pid:
                    d.grpc_plugin.recreate_application(True)
                    d.grpc_plugin.Release()
                    return True
        elif not inside_desktop_ironpython_console:  # pragma: no cover
            try:
                scopeID = 0
                while scopeID <= 5:
                    self.COMUtil.ReleaseCOMObjectScope(self.COMUtil.PInvokeProxyAPI, scopeID)
                    scopeID += 1
            except Exception:
                pyaedt_logger.warning(
                    "Something went wrong releasing AEDT. Exception in `_main.COMUtil.ReleaseCOMObjectScope`."
                )
        return True

    @pyaedt_function_handler()
    def __close_aedt_application(self, pid, is_grpc_api):
        """Close the AEDT application.

        Parameters
        ----------
        desktop_class : :class:ansys.aedt.core.desktop.Desktop
            Desktop class.
        pid : int
            Process ID of the desktop app that is being closed.
        is_grpc_api : bool
            Whether the active AEDT session is gRPC or COM.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if settings.remote_rpc_session or (settings.aedt_version >= "2022.2" and is_grpc_api):
            try:
                if settings.use_multi_desktop:  # pragma: no cover
                    os.kill(pid, 9)
                else:
                    self.odesktop.QuitApplication()
                    if self.is_grpc_api:
                        self.grpc_plugin.Release()
                    timeout = 20
                    while pid in active_sessions():
                        time.sleep(1)
                        if timeout == 0:
                            os.kill(pid, 9)
                            break
                        timeout -= 1
                    self.grpc_plugin = None
                    self.odesktop = None
                return True
            except Exception:  # pragma: no cover
                warnings.warn("Something went wrong closing AEDT. Exception in `_main.oDesktop.QuitApplication()`.")
        elif not inside_desktop_ironpython_console:  # pragma: no cover
            try:
                if settings.use_multi_desktop:
                    self.odesktop.QuitApplication()
                else:
                    os.kill(pid, 9)
            except Exception:  # pragma: no cover
                warnings.warn("Something went wrong closing AEDT. Exception in `os.kill(pid, 9)`.")
                return False
        if not settings.remote_rpc_session:  # pragma: no cover
            timeout = 10
            while pid in active_sessions():
                time.sleep(1)
                timeout -= 1
                if timeout == 0:
                    try:
                        os.kill(pid, 9)
                        return True
                    except Exception:  # pragma: no cover
                        warnings.warn(
                            "Something went wrong closing AEDT. Exception in `os.kill(pid, 9)` after timeout."
                        )
                        return False
        return True

    @pyaedt_function_handler()
    def __release_and_close_desktop(self, close_projects, close_aedt_app):
        """Internal method performing common operations when releasing or closing AEDT.

        Parameters
        ----------
        close_projects : bool, optional
            Whether to close the AEDT projects that are open in the session.
        close_aedt_app : bool, optional
            Whether to close the active AEDT session on exiting AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        # Handle case were the desktop has been released and properties have already been deleted
        if self.__closed is True:  # pragma no cover
            return True
        if self.is_grpc_api:
            self.grpc_plugin.recreate_application(True)
        self.logger._desktop_class = None
        self.logger._oproject = None
        self.logger._odesign = None
        if os.getenv("PYAEDT_DOC_GENERATION", "False").lower() in ("true", "1", "t"):  # pragma: no cover
            close_projects = True
            close_aedt_app = True

        for edb_object in _edb_sessions:
            try:
                edb_object.close()
            except Exception:  # pragma: no cover
                self.logger.warning("Failed to close Edb object.")

        if close_projects and "PYTEST_CURRENT_TEST" not in os.environ:
            projects = self.project_list
            for project in projects:
                try:
                    self.odesktop.CloseProject(project)
                except Exception:  # pragma: no cover
                    self.logger.warning(f"Failed to close Project {project}")

        if close_aedt_app:
            result = self.__close_aedt_application(self.aedt_process_id, self.is_grpc_api)
        else:
            result = self.__release_aedt_application(self.aedt_process_id, self.is_grpc_api)

        if not result:  # pragma: no cover
            self.logger.error("Error releasing desktop.")
            return False

        if close_aedt_app:
            self.logger.info("Desktop has been released and closed.")
        else:
            self.logger.info("Desktop has been released.")
        if self.aedt_process_id in _desktop_sessions:
            del _desktop_sessions[self.aedt_process_id]
        props = [a for a in dir(self) if not a.startswith("__")]
        for a in props:
            self.__dict__.pop(a, None)

        gc.collect()
        self.__closed = True
        return result

    @pyaedt_function_handler()
    @deprecate_argument(
        arg_name="close_on_exit",
        message="The ``close_on_exit`` argument will be removed in future versions. "
        "Use ``close_desktop`` method to close the desktop.",
    )
    def release_desktop(self, close_projects=True, close_on_exit=True):
        """Release AEDT.

        Parameters
        ----------
        close_projects : bool, optional
            Whether to close the AEDT projects that are open in the session.
            The default is ``True``.
        close_on_exit : bool, optional
            Whether to close the active AEDT session on exiting AEDT.
            The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import ansys.aedt.core
        >>> desktop = ansys.aedt.core.Desktop("2025.2")
        PyAEDT INFO: pyaedt v...
        PyAEDT INFO: Python version ...
        >>> desktop.release_desktop(close_projects=False)  # doctest: +SKIP

        """
        if close_on_exit:
            warnings.warn(
                "The `close_on_exit` argument will be removed in future versions. "
                "Use `close_desktop` method to close the desktop.",
                DeprecationWarning,
            )

        return self.__release_and_close_desktop(close_projects, close_on_exit)

    def close_desktop(self):
        """Close all projects and shut down AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import ansys.aedt.core
        >>> desktop = ansys.aedt.core.Desktop("2025.2")
        PyAEDT INFO: pyaedt v...
        PyAEDT INFO: Python version ...
        >>> desktop.close_desktop()  # doctest: +SKIP

        """
        return self.__release_and_close_desktop(close_projects=True, close_aedt_app=True)

    def enable_autosave(self):
        """Enable the autosave option.

        Examples
        --------
        >>> import ansys.aedt.core
        >>> desktop = ansys.aedt.core.Desktop("2025.2")
        PyAEDT INFO: pyaedt v...
        PyAEDT INFO: Python version ...
        >>> desktop.enable_autosave()

        """
        self.odesktop.EnableAutoSave(True)

    def disable_autosave(self):
        """Disable the autosave option.

        Examples
        --------
        >>> import ansys.aedt.core
        >>> desktop = ansys.aedt.core.Desktop("2025.2")
        PyAEDT INFO: pyaedt v...
        PyAEDT INFO: Python version ...
        >>> desktop.disable_autosave()

        """
        self.odesktop.EnableAutoSave(False)

    def change_license_type(self, license_type="Pool"):  # pragma: no cover
        """Change the license type.

        Parameters
        ----------
        license_type : str, optional
            Type of the license. The options are ``"Pack"`` and ``"Pool"``.
            The default is ``"Pool"``.

        Returns
        -------
        bool
           ``True``.

            .. note::
               Because of an API limitation, this method returns ``True`` even when the key is wrong.

        """
        try:
            self.odesktop.SetRegistryString("Desktop/Settings/ProjectOptions/HPCLicenseType", license_type)
            return True
        except Exception:
            return False

    def enable_optimetrics(self):  # pragma: no cover
        """Enable optimetrics.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        """
        try:
            return self.change_registry_key("Desktop/Settings/ProjectOptions/EnableLegacyOptimetricsTools", 1)
        except Exception:
            self.logger.error("Failed to enable optimetrics.")
            return False

    def disable_optimetrics(self):  # pragma: no cover
        """Disable optimetrics.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        """
        try:
            return self.change_registry_key("Desktop/Settings/ProjectOptions/EnableLegacyOptimetricsTools", 0)
        except Exception:
            self.logger.error("Failed to disable optimetrics.")
            return False

    def change_registry_key(self, key_full_name, key_value):
        """Change an AEDT registry key to a new value.

        Parameters
        ----------
        key_full_name : str
            Full name of the AEDT registry key.
        key_value : str, int
            Value for the AEDT registry key.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(key_value, str):
            try:
                self.odesktop.SetRegistryString(key_full_name, key_value)
                self.logger.info(f"Key {key_full_name} correctly changed.")
                return True
            except Exception:
                self.logger.warning(f"Error setting up Key {key_full_name}.")
                return False
        elif isinstance(key_value, int):
            try:
                self.odesktop.SetRegistryInt(key_full_name, key_value)
                self.logger.info(f"Key {key_full_name} correctly changed.")
                return True
            except Exception:
                self.logger.warning(f"Error setting up Key {key_full_name}.")
                return False
        else:
            self.logger.warning("Key value must be an integer or string.")
            return False

    def change_active_dso_config_name(self, product_name="HFSS", config_name="Local"):  # pragma: no cover
        """Change a specific registry key to a new value.

        Parameters
        ----------
        product_name : str, optional
            Name of the tool to apply the active configuration to. The default is
            ``"HFSS"``.
        config_name : str, optional
            Name of the configuration to apply. The default is ``"Local"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        try:
            self.change_registry_key(f"Desktop/ActiveDSOConfigurations/{product_name}", config_name)
            self.logger.info(f"Configuration Changed correctly to {config_name} for {product_name}.")
            return True
        except Exception:
            self.logger.warning(f"Error Setting Up Configuration {config_name} for {product_name}.")
            return False

    def change_registry_from_file(self, registry_file, make_active=True):  # pragma: no cover
        """Apply desktop registry settings from an ACF file.

        One way to get an ACF file is to export a configuration from the AEDT UI and then edit and reuse it.

        Parameters
        ----------
        registry_file : str
            Full path to the ACF file.
        make_active : bool, optional
            Whether to set the imported configuration as active. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self.odesktop.SetRegistryFromFile(registry_file)
            if make_active:
                with open_file(registry_file, "r") as f:
                    for line in f:
                        stripped_line = line.strip()
                        if "ConfigName" in stripped_line:
                            config_name = stripped_line.split("=")
                        elif "DesignType" in stripped_line:
                            design_type = stripped_line.split("=")
                            break
                    if design_type and config_name:
                        self.change_registry_key(design_type[1], config_name[1])
            return True
        except Exception:
            return False

    @staticmethod
    @pyaedt_function_handler()
    def get_available_toolkits():
        """Get toolkit ready for installation.

        Returns
        -------
        list
            List of toolkit names.
        """
        from ansys.aedt.core.extensions.customize_automation_tab import available_toolkits

        return list(available_toolkits().keys())

    @pyaedt_function_handler()
    def submit_job(
        self,
        project_file,
        clustername,
        aedt_full_exe_path=None,
        numnodes=1,
        numcores=32,
        wait_for_license=True,
        setting_file=None,
    ):  # pragma: no cover
        """Submit a job to be solved on a cluster.

        Parameters
        ----------
        project_file : str or :class:`pathlib.Path`, optional
            Full path to the project. The path should be visible from the server where the
            simulation will run.
            If the client path is used then the
            mapping between the client and server path must be specified in the `setting_file``.
        clustername : str
            Name of the cluster to submit the job to.
        aedt_full_exe_path : str, optional
            Full path to the AEDT executable file on the server. The default is ``None``, in which
            case ``"/clustername/AnsysEM/AnsysEM2x.x/Win64/ansysedt.exe"`` is used. On linux
            this path should point to the Linux executable ``"ansysedt"``.
        numnodes : int, optional
            Number of nodes. The default is ``1``.
        numcores : int, optional
            Number of cores. The default is ``32``.
        wait_for_license : bool, optional
             Whether to wait for a license to become available. The default is ``True``.
        setting_file : str, optional
            Name of the "*.areg" file to use as a template. The default value
            is ``None`` in which case a default template will be used.
            If ``setting_file`` is passed it can be located either on the client or server.
            If the "*.areg" file is on the client information from ``numcores`` and ``numnodes``
            will be added. If the "*.areg" file is on the server it
            will be applied without modifications.

        Returns
        -------
        int
            ID of the job.

        References
        ----------
        >>> oDesktop.SubmitJob
        """
        project_path = Path(project_file).parent
        project_name = Path(project_file).stem
        if project_name in self.project_list:
            self.save_project(project_name, project_path)
        if not aedt_full_exe_path:
            version = self.odesktop.GetVersion()[2:6]
            if version >= "22.2":
                version_name = "v" + version.replace(".", "")
            else:
                version_name = "AnsysEM" + version
            if Path(r"\\" + clustername + r"\AnsysEM\{}\Win64\ansysedt.exe".format(version_name)).exists():
                aedt_full_exe_path = (
                    r"\\\\\\\\" + clustername + r"\\\\AnsysEM\\\\{}\\\\Win64\\\\ansysedt.exe".format(version_name)
                )
            elif Path(r"\\" + clustername + r"\AnsysEM\{}\Linux64\ansysedt".format(version_name)).exists():
                aedt_full_exe_path = (
                    r"\\\\\\\\" + clustername + r"\\\\AnsysEM\\\\{}\\\\Linux64\\\\ansysedt".format(version_name)
                )
            else:
                self.logger.error("AEDT shared path does not exist. Provide a full path.")
                return False
        else:
            if not Path(aedt_full_exe_path).exists():
                self.logger.warning("The AEDT executable path is not visible from the client.")
            aedt_full_exe_path.replace("\\", "\\\\")
        if project_name in self.project_list:
            self.odesktop.CloseProject(project_name)
        path_file = Path(__file__)
        destination_reg = Path(project_path) / "Job_settings.areg"
        if not setting_file:
            setting_file = Path(path_file) / "misc" / "Job_Settings.areg"
        if Path(setting_file).exists():
            f1 = open_file(destination_reg, "w")
            with open_file(setting_file) as f:
                lines = f.readlines()
                for line in lines:
                    if "\\	$begin" == line[:8]:
                        lin = f"\\	$begin \\'{clustername}\\'\\\n"
                        f1.write(lin)
                    elif "\\	$end" == line[:6]:
                        lin = f"\\	$end \\'{clustername}\\'\\\n"
                        f1.write(lin)
                    elif "NumCores=" in line:
                        lin = f"\\	\\	\\	\\	NumCores={numcores}\\\n"
                        f1.write(lin)
                    elif "NumNodes=1" in line:
                        lin = f"\\	\\	\\	\\	NumNodes={numnodes}\\\n"
                        f1.write(lin)
                    elif "ProductPath" in line:
                        lin = f"\\	\\	ProductPath =\\'{aedt_full_exe_path}\\'\\\n"
                        f1.write(lin)
                    elif "WaitForLicense" in line:
                        lin = f"\\	\\	WaitForLicense={str(wait_for_license).lower()}\\\n"
                        f1.write(lin)
                    else:
                        f1.write(line)
            f1.close()
        else:
            self.logger.warning("Setting file not found on client machine. Considering it as server path.")
            destination_reg = setting_file
        job = self.odesktop.SubmitJob(str(destination_reg), str(project_file))
        self.logger.info(f"Job submitted: {str(job)}")
        return job

    @pyaedt_function_handler()
    def submit_ansys_cloud_job(
        self,
        project_file,
        config_name,
        region,
        numnodes=1,
        numcores=32,
        wait_for_license=True,
        setting_file=None,
        job_name=None,
    ):  # pragma: no cover
        """Submit a job to be solved on a cluster.

        Parameters
        ----------
        project_file : str
            Full path to the project.
        config_name : str
            Name of the Ansys Cloud machine configuration selected.
        region : str
            Name of Ansys Cloud location region.
            Available regions are: ``"westeurope"``, ``"eastus"``, ``"northcentralus"``, ``"southcentralus"``,
            ``"northeurope"``, ``"japaneast"``, ``"westus2"``, ``"centralindia"``.
        numnodes : int, optional
            Number of nodes. The default is ``1``.
        numcores : int, optional
            Number of cores. The default is ``32``.
        wait_for_license : bool, optional
             Whether to wait for the license to be validated. The default is ``True``.
        setting_file : str, optional
            Name of the file to use as a template. The default value is ``None``.

        Returns
        -------
        str, str
            Job ID, job name.

        References
        ----------
        >>> oDesktop.SubmitJob

        Examples
        --------
        >>> from ansys.aedt.core import Desktop

        >>> d = Desktop(version="2025.2", new_desktop=False)
        >>> d.select_scheduler("Ansys Cloud")
        >>> out = d.get_available_cloud_config()
        >>> job_id, job_name = d.submit_ansys_cloud_job(
        ...     "via_gsg.aedt", list(out.keys())[0], region="westeurope", job_name="MyJob"
        ... )
        >>> o1 = d.get_ansyscloud_job_info(job_id=job_id)
        >>> o2 = d.get_ansyscloud_job_info(job_name=job_name)
        >>> d.download_job_results(job_id=job_id, project_path="via_gsg.aedt", results_folder="via_gsg_results")
        >>> d.release_desktop(False, False)
        """
        project_path = Path(project_file).parent
        project_name = Path(project_file).stem
        if project_name in self.project_list:
            self.save_project(project_name, project_path)
        if not job_name:
            job_name = generate_unique_name(project_name)
        if project_name in self.project_list:
            self.odesktop.CloseProject(project_name)
        path_file = Path(__file__)
        reg_name = generate_unique_name("ansys_cloud") + ".areg"
        destination_reg = Path(project_path) / reg_name
        if not setting_file:
            setting_file = Path(path_file) / "misc" / "ansys_cloud.areg"
        shutil.copy(setting_file, destination_reg)

        f1 = open_file(destination_reg, "w")
        with open_file(setting_file) as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                line = lines[i]
                if "NumTasks" in line:
                    lin = f"\\	\\	\\	\\	NumTasks={numcores}\\\n"
                    f1.write(lin)
                elif "NumMaxTasksPerNode" in line:
                    lin = f"\\	\\	\\	\\	NumMaxTasksPerNode={numcores}\\\n"
                    f1.write(lin)
                elif "NumNodes=1" in line:
                    lin = f"\\	\\	\\	\\	NumNodes={numnodes}\\\n"
                    f1.write(lin)
                elif "Name=\\'Region\\'" in line:
                    f1.write(line)
                    lin = f"\\	\\	\\	\\	Value=\\'{region}\\'\\\n"
                    f1.write(lin)
                    i += 1
                elif "WaitForLicense" in line:
                    lin = f"\\	\\	WaitForLicense={str(wait_for_license).lower()}\\\n"
                    f1.write(lin)
                elif "	JobName" in line:
                    lin = f"\\	\\	\\	JobName=\\'{job_name}\\'\\\n"
                    f1.write(lin)
                elif "Name=\\'Config\\'" in line:
                    f1.write(line)
                    lin = f"\\	\\	\\	\\	Value=\\'{config_name}\\'\\\n"
                    f1.write(lin)
                    i += 1
                else:
                    f1.write(line)
                i += 1
        f1.close()
        try:
            id = self.odesktop.SubmitJob(destination_reg, project_file)[0]
            return id, job_name
        except Exception:
            self.logger.error("Failed to submit job. check parameters and credentials and retry")
            return "", ""

    @pyaedt_function_handler()
    def get_ansyscloud_job_info(self, job_id=None, job_name=None):  # pragma: no cover
        """Monitor a job submitted to Ansys Cloud.

        .. warning::

            Do not execute this function with untrusted function argument, environment
            variables or pyaedt global settings.
            See the :ref:`security guide<security_ansys_cloud>` for details.

        Parameters
        ----------
        job_id : str, optional
            Job Id.  The default value is ``None`` if job name is used.
        job_name : str, optional
            Job name.  The default value is ``None`` if job id is used.

        Returns
        -------
        dict

        Examples
        --------
        >>> from ansys.aedt.core import Desktop

        >>> d = Desktop(version="2025.2", new_desktop=False)
        >>> d.select_scheduler("Ansys Cloud")
        >>> out = d.get_available_cloud_config()
        >>> job_id, job_name = d.submit_ansys_cloud_job(
        ...     "via_gsg.aedt", list(out.keys())[0], region="westeurope", job_name="MyJob"
        ... )
        >>> o1 = d.get_ansyscloud_job_info(job_id=job_id)
        >>> o2 = d.get_ansyscloud_job_info(job_name=job_name)
        >>> d.download_job_results(job_id=job_id, project_path="via_gsg.aedt", results_folder="via_gsg_results")
        >>> d.release_desktop(False, False)
        """
        ansys_cloud_cli_path = Path(self.install_path) / "common" / "AnsysCloudCLI" / "AnsysCloudCli.exe"
        if not Path(ansys_cloud_cli_path).exists():
            raise FileNotFoundError("Ansys Cloud CLI not found. Check the installation path.")
        command = [ansys_cloud_cli_path]
        if job_name:
            command += ["jobinfo", "-j", job_name]
        elif job_id:
            command += ["jobinfo", "-i", job_id]
        cloud_info = Path(tempfile.gettempdir()) / generate_unique_name("job_info")

        try:
            with open_file(cloud_info, "w") as outfile:
                subprocess.run(command, stdout=outfile, check=True)  # nosec
        except subprocess.CalledProcessError as e:
            raise AEDTRuntimeError("An error occurred while monitoring a job submitted to Ansys Cloud") from e

        out = {}
        with open_file(cloud_info, "r") as infile:
            lines = infile.readlines()
            for i in lines:
                if ":" in i.strip():
                    strp = i.strip().split(":")
                    out[strp[0]] = ":".join(strp[1:])
        return out

    @pyaedt_function_handler()
    def select_scheduler(
        self, scheduler_type, address=None, username=None, force_password_entry=False
    ):  # pragma: no cover
        """Select a scheduler to submit the job.

        Parameters
        ----------
        scheduler_type : str
            Name of the scheduler.
            Options are `"RSM"``, `""Windows HPC"``, `""LSF``, `""SGE"``, `""PBS"``, `""Ansys Cloud"``.
        address : str, optional
            String specifying the IP address or hostname of the head node or for the
            remote host running the RSM service.
        username : str, optional
            Username string to use for remote RSM service (or blank to use username
            stored in current submission host user settings). If the (non-blank) username doesn't match the
            username stored in current submission host user
            settings, then the Select Scheduler dialog is displayed to allow for password entry prior to job submission.
        force_password_entry : bool, optional
            Boolean used to force display of the Select Scheduler GUI to allow for
             password entry prior to job submission.


        Returns
        -------
        str
            The selected scheduler (if selection was successful, this string should match the input option string,
            although it could differ in upper/lowercase).

        Examples
        --------
        >>> from ansys.aedt.core import Desktop

        >>> d = Desktop(version="2025.2", new_desktop=False)
        >>> d.select_scheduler("Ansys Cloud")
        >>> out = d.get_available_cloud_config()
        >>> job_id, job_name = d.submit_ansys_cloud_job(
        ...     "via_gsg.aedt", list(out.keys())[0], region="westeurope", job_name="MyJob"
        ... )
        >>> o1 = d.get_ansyscloud_job_info(job_id=job_id)
        >>> o2 = d.get_ansyscloud_job_info(job_name=job_name)
        >>> d.download_job_results(job_id=job_id, project_path="via_gsg.aedt", results_folder="via_gsg_results")
        >>> d.release_desktop(False, False)
        """
        if not address:
            return self.odesktop.SelectScheduler(scheduler_type)
        elif not username:
            return self.odesktop.SelectScheduler(scheduler_type, address)
        else:
            return self.odesktop.SelectScheduler(scheduler_type, address, username, str(force_password_entry))

    @pyaedt_function_handler()
    def get_available_cloud_config(self, region="westeurope"):  # pragma: no cover
        """Get available Ansys Cloud machines configuration.

        .. warning::

            Do not execute this function with untrusted function argument, environment
            variables or pyaedt global settings.
            See the :ref:`security guide<security_ansys_cloud>` for details.

        Parameters
        ----------
        region : str
            Name of Ansys Cloud location region.
            Available regions are: ``"westeurope"``, ``"eastus"``, ``"northcentralus"``, ``"southcentralus"``,
            ``"northeurope"``, ``"japaneast"``, ``"westus2"``, ``"centralindia"``.

        Returns
        -------
        dict
            Dictionary containing the config name and config details.

        Examples
        --------
        >>> from ansys.aedt.core import Desktop

        >>> d = Desktop(version="2025.2", new_desktop=False)
        >>> d.select_scheduler("Ansys Cloud")
        >>> out = d.get_available_cloud_config()
        >>> job_id, job_name = d.submit_ansys_cloud_job(
        ...     "via_gsg.aedt", list(out.keys())[0], region="westeurope", job_name="MyJob"
        ... )
        >>> o1 = d.get_ansyscloud_job_info(job_id=job_id)
        >>> o2 = d.get_ansyscloud_job_info(job_name=job_name)
        >>> d.download_job_results(job_id=job_id, project_path="via_gsg.aedt", results_folder="via_gsg_results")
        >>> d.release_desktop(False, False)
        """
        ansys_cloud_cli_path = Path(self.install_path) / "common" / "AnsysCloudCLI" / "AnsysCloudCli.exe"
        if not Path(ansys_cloud_cli_path).exists():
            raise FileNotFoundError("Ansys Cloud CLI not found. Check the installation path.")
        ver = self.aedt_version_id.replace(".", "R")
        command = [ansys_cloud_cli_path, "getQueues", "-p", "AEDT", "-v", ver, "--details"]
        cloud_info = Path(tempfile.gettempdir()) / generate_unique_name("cloud_info")
        try:
            with open_file(cloud_info, "w") as outfile:
                subprocess.run(command, stdout=outfile, check=True)  # nosec
        except subprocess.CalledProcessError as e:
            raise AEDTRuntimeError("An error occurred while monitoring a job submitted to Ansys Cloud") from e

        dict_out = {}
        with open_file(cloud_info, "r") as infile:
            lines = infile.readlines()
            for i in range(len(lines)):
                line = lines[i].strip()
                if line.endswith(ver):
                    split_line = line.split("_")
                    if split_line[1] == region:
                        name = f"{split_line[0]} {split_line[3]}"
                        dict_out[name] = {"Name": line}
                        for k in range(i + 1, i + 8):
                            spl = lines[k].split(":")
                            try:
                                dict_out[name][spl[0].strip()] = int(spl[1].strip())
                            except ValueError:
                                dict_out[name][spl[0].strip()] = spl[1].strip()
        os.unlink(cloud_info)
        return dict_out

    @pyaedt_function_handler()
    def download_job_results(self, job_id, project_path, results_folder, filter="*"):  # pragma: no cover
        """Download job results to a specific folder from Ansys Cloud.

        Parameters
        ----------
        job_id : str
            Job Id of solved project.
        project_path : str
            Project path to aedt file. The ".q" file will be created there to monitor download status.
        results_folder : str
            Folder where the simulation results will be downloaded.
        filter : str, optional
            A string containing filters to download. The delimiter of file types is ";". If no filter
            specified, the default filter "*" will be applied, which requests all files for download

        Returns
        -------
        bool
        """
        download_status = self.odesktop.DownloadJobResults(job_id, project_path, results_folder, filter)
        return True if download_status == 1 else False

    @pyaedt_function_handler()
    @min_aedt_version("2023.2")
    def get_monitor_data(self):  # pragma: no cover
        """Check and get monitor data of an existing analysis.

        Returns
        -------
        dict

        """
        counts = {"profile": 0, "convergence": 0, "sweptvar": 0, "progress": 0, "variations": 0, "displaytype": 0}
        if self.are_there_simulations_running:
            reqstr = " ".join([f"{t} {counts[t]} 0" for t in counts])
            data = self.odesktop.GetMonitorData(reqstr)
            all_lines = (line.strip() for line in data.split("\n"))
            for line in all_lines:
                if line.startswith("$begin"):
                    btype = line.split()[1].strip("'")
                    if btype == "MonitoringProfileMsg":
                        counts["profile"] += 1
                    elif btype == "MonConvData":
                        counts["convergence"] += 1
                    elif btype == "MonGenericVariations":
                        pass
                    elif btype == "MapMonGraphicalProgMsg":
                        pass
                    elif btype == "MonitoringSweptVariableMsg":
                        counts["sweptvar"] += 1
            return counts
        return counts

    @pyaedt_function_handler()
    @min_aedt_version("2023.2")
    def stop_simulations(self, clean_stop=True):
        """Check if there are simulation running and stops them.

        Returns
        -------
        str

        """
        return self.odesktop.StopSimulations(clean_stop)

    # ############################################# #
    #                Private methods                #
    # ############################################# #

    def __init_desktop(self):
        # run it after the settings.non_graphical is set
        self.pyaedt_version = __version__
        settings.aedt_version = self.odesktop.GetVersion()[0:6]
        self.odesktop.RestoreWindow()
        self.aedt_install_dir = self.odesktop.GetExeDir()

    def __check_version(self, specified_version, student_version):
        if self.current_version == "" and aedt_versions.latest_version == "":
            raise AEDTRuntimeError("AEDT is not installed on your system. Install AEDT version 2022 R2 or higher.")
        specified_version = _normalize_version_to_string(specified_version)
        if not specified_version:
            if student_version and self.current_student_version:
                specified_version = self.current_student_version
            elif student_version and self.current_version:
                specified_version = self.current_version
                student_version = False
                self.logger.warning("AEDT Student Version not found on the system. Using regular version.")
            else:
                if self.current_version != "":
                    specified_version = self.current_version
                else:
                    specified_version = aedt_versions.latest_version
                if "SV" in specified_version:
                    student_version = True
                    self.logger.warning("Only AEDT Student Version found on the system. Using Student Version.")
        elif student_version:
            specified_version += "SV"

        if not _is_version_format_valid(specified_version):
            raise AEDTRuntimeError(f"Internal version format is not correct: specified_version: {specified_version}")

        if float(specified_version[0:6]) < 2019:
            raise ValueError("PyAEDT supports AEDT version 2021 R1 and later. Recommended version is 2022 R2 or later.")
        elif float(specified_version[0:6]) < 2022.2:
            warnings.warn(
                """PyAEDT has limited capabilities when used with an AEDT version earlier than 2022 R2.
                Update your AEDT installation to 2022 R2 or later."""
            )
        if specified_version not in self.installed_versions and specified_version + "CL" not in self.installed_versions:
            raise ValueError(
                f"Specified version {specified_version[0:6]}{' Student Version' if student_version else ''} is not "
                f"installed on your system"
            )

        version = "Ansoft.ElectronicsDesktop." + specified_version[0:6]
        if self.aedt_install_dir is None:
            if specified_version in self.installed_versions:
                self.aedt_install_dir = self.installed_versions[specified_version]
        if settings.remote_rpc_session:
            try:
                version = "Ansoft.ElectronicsDesktop." + settings.remote_rpc_session.aedt_version[0:6]
                return settings.remote_rpc_session.student_version, settings.remote_rpc_session.aedt_version, version
            except Exception:
                return False, "", ""
        self.student_version = student_version
        self.aedt_version_id = specified_version
        self.aedt_version_string = version

    def __run_student(self):  # pragma: no cover
        executable = Path(Path(self.aedt_install_dir) / "ansysedtsv.exe").resolve(strict=True)
        if not executable.exists():
            raise FileNotFoundError(f"Student version executable {executable} not found")
        pid = subprocess.Popen([executable], creationflags=subprocess.DETACHED_PROCESS)  # nosec
        self.logger.debug(f"Running Electronic Desktop Student Version with PID {pid}.")
        time.sleep(5)

    def __dispatch_win32(self, version):  # pragma: no cover
        from ansys.aedt.core.internal.clr_module import win32_client

        o_ansoft_app = win32_client.Dispatch(version)
        self.odesktop = o_ansoft_app.GetAppDesktop()

    def __init_dotnet(
        self,
    ):  # pragma: no cover
        import pythoncom

        pythoncom.CoInitialize()

        if is_linux:
            raise Exception(
                "PyAEDT supports COM initialization in Windows only. To use in Linux, upgrade to AEDT 2022 R2 or later."
            )
        base_path = self.aedt_install_dir
        sys.path.insert(0, base_path)
        sys.path.insert(0, str(Path(base_path) / "PythonFiles" / "DesktopPlugin"))
        launch_msg = f"AEDT installation Path {base_path}."
        self.logger.info(launch_msg)
        processID = []
        if is_windows:
            processID = com_active_sessions(self.aedt_version_id, self.student_version, self.non_graphical)
        if self.student_version and not processID:  # Opens an instance if processID is an empty list
            self.__run_student()
        else:
            # Force new object if no non-graphical instance is running or if there is not an already existing process.
            self.__initialize()

        processID2 = []
        if is_windows:
            processID2 = com_active_sessions(self.aedt_version_id, self.student_version, self.non_graphical)
        proc = [i for i in processID2 if i not in processID]  # Looking for the "new" process
        if (
            not proc and (not self.new_desktop) and self.aedt_process_id
        ):  # if it isn't a new aedt session and a process ID is given
            proc = [self.aedt_process_id]
        elif not proc:
            proc = processID2
        if proc == processID2 and len(processID2) > 1:
            self.__dispatch_win32(self.aedt_version_string)
        elif self.aedt_version_id >= "2021.2":
            context = pythoncom.CreateBindCtx(0)
            running_coms = pythoncom.GetRunningObjectTable()
            monikiers = running_coms.EnumRunning()
            for monikier in monikiers:
                m = re.search(
                    self.aedt_version_string[10:] + r"\.\d:" + str(proc[0]), monikier.GetDisplayName(context, monikier)
                )
                if m:
                    obj = running_coms.GetObject(monikier)

                    from ansys.aedt.core.internal.clr_module import win32_client

                    self.odesktop = win32_client.Dispatch(obj.QueryInterface(pythoncom.IID_IDispatch))
                    if self.student_version:
                        self.logger.info(f"New AEDT {self.aedt_version_id} Student version process ID {proc[0]}.")
                    elif self.aedt_process_id:
                        self.logger.info(f"Existing AEDT session process ID {proc[0]}.")
                    else:
                        self.logger.info(f"New AEDT {self.aedt_version_id} Started process ID {proc[0]}.")
                    break
        else:
            self.logger.warning(
                "PyAEDT is not supported in AEDT versions earlier than 2021 R2. Trying to launch PyAEDT with PyWin32."
            )
            self.__dispatch_win32(self.aedt_version_string)
        # we should have a check here to see if AEDT is really started
        self.is_grpc_api = False

    def __initialize(
        self,
    ):
        if not self.is_grpc_api:  # pragma: no cover
            from ansys.aedt.core.internal.clr_module import _clr

            _clr.AddReference("Ansys.Ansoft.CoreCOMScripting")
            AnsoftCOMUtil = __import__("Ansys.Ansoft.CoreCOMScripting")
            self.COMUtil = AnsoftCOMUtil.Ansoft.CoreCOMScripting.Util.COMUtil
            StandalonePyScriptWrapper = AnsoftCOMUtil.Ansoft.CoreCOMScripting.COM.StandalonePyScriptWrapper
            if self.non_graphical or self.new_desktop:
                self.launched_by_pyaedt = True
                return StandalonePyScriptWrapper.CreateObjectNew(self.non_graphical)
            else:
                return StandalonePyScriptWrapper.CreateObject(self.aedt_version_string)
        else:
            settings.use_grpc_api = True
            self.is_grpc_api = True
            base_path = self.aedt_install_dir
            sys.path.insert(0, base_path)
            sys.path.insert(0, str(Path(base_path) / "PythonFiles" / "DesktopPlugin"))
            if is_linux:
                pyaedt_path = Path(__file__).parent
                os.environ["PATH"] = str(pyaedt_path) + os.pathsep + os.environ["PATH"]
            os.environ["DesktopPluginPyAEDT"] = str(Path(self.aedt_install_dir) / "PythonFiles" / "DesktopPlugin")
            launch_msg = f"AEDT installation Path {base_path}"
            self.logger.info(launch_msg)
            from ansys.aedt.core.internal.grpc_plugin_dll_class import AEDT

            if settings.use_multi_desktop:
                os.environ["DesktopPluginPyAEDT"] = str(
                    Path(list(self.installed_versions.values())[0]) / "PythonFiles" / "DesktopPlugin"
                )
            self.grpc_plugin = AEDT(os.environ["DesktopPluginPyAEDT"])
            server_args: _ServerArgs = _get_grpcsrv_args(self.machine, self.port)
            if str(server_args).endswith((":SecureMode", ":InsecureMode")):
                self.machine += ":" + str(server_args).split(":")[-1]
            # NOTE: When working locally, machine is updated to an empty string to work with UDS.
            # This is necessary when working with UDS and also works for WNUA.
            elif settings.grpc_local and settings.grpc_secure_mode and "ANSYS_GRPC_CERTIFICATES" not in os.environ:
                pyaedt_logger.debug("Setting machine to '' to work with UDS/WNUA connection mechanism.")
                self.machine = ""
            # NOTE: Update command if PYAEDT_USE_PRE_GRPC_ARGS is set to allow working
            # with previous SP where grpc transport mode were not available
            # This environment variable is not necessary for UDS and WNUA modes.
            if os.environ.get("PYAEDT_USE_PRE_GRPC_ARGS", "False") == "True":
                self.machine = self.machine.split(":")[0] if self.machine else self.machine

            oapp = self.grpc_plugin.CreateAedtApplication(self.machine, self.port, self.non_graphical, self.new_desktop)
            self.port = self.grpc_plugin.port
            self.aedt_process_id = self.odesktop.GetProcessID()
            return oapp

    @pyaedt_function_handler()
    def _check_machine(self):
        if settings.remote_rpc_session:  # pragma: no cover
            settings.remote_api = True
            self.logger.warning(
                "Remote AEDT connection without specified machine. "
                "Trying to use the machine name from the RPyC connection."
            )
            try:
                self.machine = settings.remote_rpc_session.server_name
            except Exception:
                self.logger.debug("Failed to retrieve server name from RPyC connection")

        self.logger.debug("No machine name provided. Defining self.machine as '127.0.0.1'.")
        self.machine = "127.0.0.1"

    @pyaedt_function_handler()
    def _validate_port(self):
        self.__port = 0
        if settings.remote_rpc_session:
            self.logger.warning(
                "Remote AEDT connection without specified port. Trying to use the port from the RPyC connection."
            )
            try:
                self.__port = settings.remote_rpc_session.port
            except Exception:
                self.logger.debug("Failed to retrieve port from RPyC connection")
                raise Exception("Failed to retrieve port from RPyC connection")

        if (
            settings.use_multi_desktop
            or "PYTEST_CURRENT_TEST" in os.environ
            or (self.new_desktop and self.aedt_version_id < "2024.2")
            or (is_linux and self.new_desktop)
        ):
            self.__port = _find_free_port()
            self.logger.info(f"New AEDT session is starting on gRPC port {self.port}.")
        elif self.new_desktop:
            self.__port = 0
        else:
            sessions = grpc_active_sessions(
                version=self.aedt_version_id, student_version=self.student_version, non_graphical=self.non_graphical
            )
            if sessions:
                self.__port = sessions[0]
                if len(sessions) == 1:
                    self.logger.info(f"Found active AEDT gRPC session on port {self.port}.")
                else:
                    self.logger.warning(
                        f"Multiple AEDT gRPC sessions are found. Setting the active session on port {self.port}."
                    )
            elif self.aedt_version_id < "2024.2" or is_linux:
                self.__port = _find_free_port()
                self.logger.info(f"New AEDT session is starting on gRPC port {self.port}.")
                self.new_desktop = True

    def __init_grpc(self):
        result = False
        if self.new_desktop and settings.use_lsf_scheduler and is_linux:  # pragma: no cover
            self.logger.info(f"Starting new AEDT gRPC session on port {self.port}.")
            out, self.machine = launch_aedt_in_lsf(self.non_graphical, self.port)
            self.new_desktop = False
            if out:
                self.launched_by_pyaedt = True
                result = self.__initialize()
            else:
                self.logger.error(f"Failed to start LSF job on machine: {self.machine}.")
                return result
        elif self.new_desktop and (
            "PYTEST_CURRENT_TEST" in os.environ
            or not settings.grpc_local
            or self.aedt_version_id < "2024.2"
            or settings.use_multi_desktop
            or is_linux
        ):  # pragma: no cover
            self.logger.info(f"Starting new AEDT gRPC session on port {self.port}.")
            installer = Path(self.aedt_install_dir) / "ansysedt"
            if self.student_version:  # pragma: no cover
                installer = Path(self.aedt_install_dir) / "ansysedtsv"
            if not is_linux:
                if self.student_version:  # pragma: no cover
                    installer = Path(self.aedt_install_dir) / "ansysedtsv.exe"
                else:
                    installer = Path(self.aedt_install_dir) / "ansysedt.exe"
            # Only provide host if user provided a machine name
            out, self.port = launch_aedt(
                installer, self.non_graphical, self.port, self.student_version, host=self.machine
            )
            self.new_desktop = False
            self.launched_by_pyaedt = True
            result = self.__initialize()
        else:
            flag_new = False
            if self.port == 0:
                self.logger.info("Starting new AEDT gRPC session.")
                flag_new = True
            else:
                self.logger.info(f"Connecting to AEDT gRPC session on port {self.port}.")
            result = self.__initialize()
            if flag_new:
                self.logger.info(f"New AEDT gRPC session session started on port {self.port}.")
        if result:
            if self.new_desktop:
                message = (
                    f"{self.aedt_version_id}{' Student' if self.student_version else ''} version started "
                    f"with process ID {self.aedt_process_id}."
                )
                self.logger.info(message)

        else:
            self.logger.error("Failed to connect to AEDT using gRPC plugin.")
            self.logger.error("Check installation, license and environment variables.")
        return result

    def __set_logger_file(self):
        # Set up the log file in the AEDT project directory
        if settings.logger_file_path:
            self.__logfile = settings.logger_file_path
        else:
            if settings.remote_api or settings.remote_rpc_session:
                project_dir = tempfile.gettempdir()
            elif self.odesktop:
                project_dir = self.odesktop.GetProjectDirectory()
            else:
                project_dir = tempfile.gettempdir()
            self.__logfile = Path(project_dir) / f"pyaedt{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger._desktop_class = self
        if self.aedt_version_id >= "2024.2":
            messages = self.odesktop.GetMessages("", "", 0)
            check_message = f" {self.port}."
            for message in messages:
                if check_message in message:
                    mes_split = message.split(".")
                    if len(mes_split) > 1 and len(mes_split[1].strip()) == 0:
                        self.logger.warning(
                            "Service Pack is not detected. PyAEDT is currently connecting in Insecure Mode."
                        )
                        self.logger.warning(
                            "Please download and install latest Service Pack to use connect to AEDT in Secure Mode."
                        )
        if settings.enable_debug_logger:
            self.logger.info("Debug logger is enabled. PyAEDT methods will be logged.")
        else:
            self.logger.info("Debug logger is disabled. PyAEDT methods will not be logged.")
        return True
