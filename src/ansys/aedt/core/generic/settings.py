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

"""This module contains the ``Settings`` and ``_InnerProjectSettings`` classes.

The first class encapsulates the settings associated with PyAEDT and AEDT including logging,
LSF, environment variables and general settings. Most of the default values used can be modified
using a YAML configuration file. An example of such file can be found in the documentation, see
`Settings YAML file <https://aedt.docs.pyansys.com/version/stable/User_guide/settings.html>`_.
The path to the configuration file should be specified with the environment variable
``PYAEDT_LOCAL_SETTINGS_PATH``. If no environment variable is set, the class will look for the
configuration file ``pyaedt_settings.yaml`` in the user's ``APPDATA`` folder for Windows and
``HOME`` folder for Linux.

The second class is intended for internal use only and shouldn't be modified by users.
"""

import logging
import os
from pathlib import Path
import time
from typing import Any
from typing import List
from typing import Optional
from typing import Union
import uuid
import warnings

from ansys.aedt.core import pyaedt_path
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.scheduler import DEFAULT_CUSTOM_SUBMISSION_STRING
from ansys.aedt.core.generic.scheduler import DEFAULT_NUM_CORES

is_linux = os.name == "posix"

# Settings allowed to be updated using a YAML configuration file.
ALLOWED_LOG_SETTINGS = [
    "enable_debug_edb_logger",
    "enable_debug_geometry_operator_logger",
    "enable_debug_grpc_api_logger",
    "enable_debug_internal_methods_logger",
    "enable_debug_logger",
    "enable_debug_methods_argument_logger",
    "enable_desktop_logs",
    "enable_file_logs",
    "enable_global_log_file",
    "enable_local_log_file",
    "enable_logger",
    "enable_screen_logs",
    "global_log_file_name",
    "global_log_file_size",
    "logger_datefmt",
    "logger_file_path",
    "logger_formatter",
    "aedt_log_file",
]
ALLOWED_LSF_SETTINGS = [
    "custom_lsf_command",
    "lsf_aedt_command",
    "lsf_num_cores",
    "lsf_osrel",
    "lsf_queue",
    "lsf_ram",
    "lsf_timeout",
    "lsf_ui",
    "use_lsf_scheduler",
]
ALLOWED_GENERAL_SETTINGS = [
    "lazy_load",
    "objects_lazy_load",
    "aedt_install_dir",
    "aedt_version",
    "desktop_launch_timeout",
    "disable_bounding_box_sat",
    "edb_dll_path",
    "enable_error_handler",
    "enable_pandas_output",
    "force_error_on_missing_project",
    "local_example_folder",
    "number_of_grpc_api_retries",
    "release_on_exception",
    "retry_n_times_time_interval",
    "use_grpc_api",
    "use_multi_desktop",
    "wait_for_license",
    "remote_api",
    "remote_rpc_service_manager_port",
    "pyaedt_server_path",
    "remote_rpc_session_temp_folder",
    "block_figure_plot",
    "skip_license_check",
    "num_cores",
    "use_local_example_data",
    "pyd_libraries_path",
    "pyd_libraries_user_path",
]

ALLOWED_AEDT_ENV_VAR_SETTINGS = [
    "ANSYSEM_FEATURE_F335896_MECHANICAL_STRUCTURAL_SOLN_TYPE_ENABLE",
    "ANSYSEM_FEATURE_F395486_RIGID_FLEX_BENDING_ENABLE",
    "ANSYSEM_FEATURE_F538630_MECH_TRANSIENT_THERMAL_ENABLE",
    "ANSYSEM_FEATURE_F545177_ECAD_INTEGRATION_WITH_APHI_ENABLE",
    "ANSYSEM_FEATURE_F650636_MECH_LAYOUT_COMPONENT_ENABLE",
    "ANSYSEM_FEATURE_S432616_LAYOUT_COMPONENT_IN_3D_ENABLE",
    "ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE",
    "ANSYSEM_FEATURE_SF222134_CABLE_MODELING_ENHANCEMENTS_ENABLE",
    "ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE",
    "ANS_MESHER_PROC_DUMP_PREPOST_BEND_SM3",
    "ANSYSEM_FEATURE_F826442_MULTI_FINITE_ARRAYS_ENABLE",
    "ANS_NODEPCHECK",
]


def generate_log_filename():
    """Generate a log filename."""
    base = "pyaedt"
    username = Path.home().name
    unique_id = uuid.uuid4()
    return f"{base}_{username}_{unique_id}.log"


class _InnerProjectSettings:  # pragma: no cover
    """Global inner project settings.

    This class is intended for internal use only.
    """

    properties: dict = {}
    time_stamp: Union[int, float] = 0


class Settings(PyAedtBase):
    """Manages all PyAEDT environment variables and global settings."""

    def __init__(self):
        # Setup default values then load values from PersoalLib' settings_config.yaml if it exists.
        # Settings related to logging
        self.__logger: Optional[logging.Logger] = None
        self.__enable_logger: bool = True
        self.__enable_desktop_logs: bool = False
        self.__enable_screen_logs: bool = True
        self.__enable_file_logs: bool = True
        self.__logger_file_path: Optional[str] = None
        self.__logger_formatter: str = "%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s"
        self.__logger_datefmt: str = "%Y/%m/%d %H.%M.%S"
        self.__enable_debug_edb_logger: bool = False
        self.__enable_debug_grpc_api_logger: bool = False
        self.__enable_debug_methods_argument_logger: bool = False
        self.__enable_debug_geometry_operator_logger: bool = False
        self.__enable_debug_internal_methods_logger: bool = False
        self.__enable_debug_logger: bool = False
        self.__global_log_file_name: str = generate_log_filename()
        self.__enable_global_log_file: bool = True
        self.__enable_local_log_file: bool = False
        self.__global_log_file_size: int = 10
        self.__aedt_log_file: Optional[str] = None
        # Settings related to Linux systems running LSF scheduler
        self.__num_cores = DEFAULT_NUM_CORES
        self.__lsf_ram: int = 1000
        self.__use_lsf_scheduler: bool = False
        self.__lsf_osrel: Optional[str] = None
        self.__lsf_ui: Optional[int] = None
        self.__lsf_aedt_command: str = "ansysedt"
        self.__lsf_timeout: int = 3600
        self.__lsf_queue: Optional[str] = None
        self.__custom_lsf_command = DEFAULT_CUSTOM_SUBMISSION_STRING
        # Settings related to environment variables that are set before launching a new AEDT session
        # This includes those that enable the beta features!
        self.__aedt_environment_variables: dict[str, str] = {
            "ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE": "1",
            "ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE": "1",
            "ANSYSEM_FEATURE_SF222134_CABLE_MODELING_ENHANCEMENTS_ENABLE": "1",
            "ANSYSEM_FEATURE_F395486_RIGID_FLEX_BENDING_ENABLE": "1",
            "ANSYSEM_FEATURE_S432616_LAYOUT_COMPONENT_IN_3D_ENABLE": "1",
            "ANSYSEM_FEATURE_F545177_ECAD_INTEGRATION_WITH_APHI_ENABLE": "1",
            "ANSYSEM_FEATURE_F650636_MECH_LAYOUT_COMPONENT_ENABLE": "1",
            "ANSYSEM_FEATURE_F538630_MECH_TRANSIENT_THERMAL_ENABLE": "1",
            "ANSYSEM_FEATURE_F335896_MECHANICAL_STRUCTURAL_SOLN_TYPE_ENABLE": "1",
            "ANS_MESHER_PROC_DUMP_PREPOST_BEND_SM3": "1",
            "ANSYSEM_FEATURE_F826442_MULTI_FINITE_ARRAYS_ENABLE": "1",
        }
        if is_linux:
            self.__aedt_environment_variables["ANS_NODEPCHECK"] = "1"
        # General settings
        self.__enable_error_handler: bool = True
        self.__release_on_exception: bool = True
        self.__aedt_version: Optional[str] = None
        self.__aedt_install_dir: Optional[str] = None
        self.__use_multi_desktop: bool = False
        self.__use_grpc_api: Optional[bool] = None
        self.__disable_bounding_box_sat = False
        self.__force_error_on_missing_project = False
        self.__enable_pandas_output = False
        self.__edb_dll_path: Optional[str] = None
        self.__desktop_launch_timeout: int = 120
        self.__number_of_grpc_api_retries: int = 6
        self.__retry_n_times_time_interval: float = 0.1
        self.__wait_for_license: bool = False
        self.__lazy_load: bool = True
        self.__objects_lazy_load: bool = True
        self.__skip_license_check: bool = True
        # Previously 'public' attributes
        self.__formatter: Optional[logging.Formatter] = None
        self.__remote_rpc_session: Any = None
        self.__remote_rpc_session_temp_folder: str = ""
        self.__remote_rpc_service_manager_port: int = 17878
        self.__remote_api: bool = False
        self.__time_tick = time.time()
        self.__pyaedt_server_path = ""
        self.__block_figure_plot = False
        self.__local_example_folder = None
        self.__use_local_example_data = False
        self.__pyd_libraries_path: Path = Path(pyaedt_path) / "syslib"
        self.__pyd_libraries_user_path: Optional[str] = None

        # Load local settings if YAML configuration file exists.
        pyaedt_settings_path = os.environ.get("PYAEDT_LOCAL_SETTINGS_PATH", "")
        if not pyaedt_settings_path:
            if is_linux:
                pyaedt_settings_path = Path(os.environ["HOME"]) / "pyaedt_settings.yaml"
            else:
                pyaedt_settings_path = Path(os.environ["APPDATA"]) / "pyaedt_settings.yaml"
        self.load_yaml_configuration(pyaedt_settings_path)

    # ########################## Logging properties ##########################

    @property
    def logger(self):
        """Active logger."""
        return self.__logger

    @logger.setter
    def logger(self, val):
        self.__logger = val

    @property
    def block_figure_plot(self):
        """Block matplotlib figure plot during python script run until the user close it manually.

        Default is ``False``.
        """
        return self.__block_figure_plot

    @block_figure_plot.setter
    def block_figure_plot(self, val):
        self.__block_figure_plot = val

    @property
    def enable_desktop_logs(self):
        """Enable or disable the logging to the AEDT message window."""
        return self.__enable_desktop_logs

    @enable_desktop_logs.setter
    def enable_desktop_logs(self, val):
        self.__enable_desktop_logs = val

    @property
    def global_log_file_size(self):
        """Global PyAEDT log file size in MB. The default value is ``10``."""
        return self.__global_log_file_size

    @global_log_file_size.setter
    def global_log_file_size(self, value):
        self.__global_log_file_size = value

    @property
    def enable_global_log_file(self):
        """Enable or disable the global PyAEDT log file located in the global temp folder.

        The default is ``True``.
        """
        return self.__enable_global_log_file

    @enable_global_log_file.setter
    def enable_global_log_file(self, value):
        self.__enable_global_log_file = value

    @property
    def enable_local_log_file(self):
        """Enable or disable the local PyAEDT log file located in the ``projectname.pyaedt`` project folder.

        The default is ``True``.
        """
        return self.__enable_local_log_file

    @enable_local_log_file.setter
    def enable_local_log_file(self, value):
        self.__enable_local_log_file = value

    @property
    def global_log_file_name(self):
        """Global PyAEDT log file path. The default is ``pyaedt_username.log``."""
        return self.__global_log_file_name

    @global_log_file_name.setter
    def global_log_file_name(self, value):
        if value is not None:
            self.__global_log_file_name = value

    @property
    def enable_debug_methods_argument_logger(self):
        """Flag for whether to write out the method's arguments in the debug logger.

        The default is ``False``.
        """
        return self.__enable_debug_methods_argument_logger

    @enable_debug_methods_argument_logger.setter
    def enable_debug_methods_argument_logger(self, val):
        self.__enable_debug_methods_argument_logger = val

    @property
    def enable_screen_logs(self):
        """Enable or disable the logging to STDOUT."""
        return self.__enable_screen_logs

    @enable_screen_logs.setter
    def enable_screen_logs(self, val):
        self.__enable_screen_logs = val

    @property
    def enable_file_logs(self):
        """Enable or disable the logging to a file."""
        return self.__enable_file_logs

    @enable_file_logs.setter
    def enable_file_logs(self, val):
        self.__enable_file_logs = val

    @property
    def enable_logger(self):
        """Enable or disable the logging overall."""
        return self.__enable_logger

    @enable_logger.setter
    def enable_logger(self, val):
        self.__enable_logger = val

    @property
    def logger_file_path(self):
        """PyAEDT log file path."""
        return self.__logger_file_path

    @logger_file_path.setter
    def logger_file_path(self, val):
        self.__logger_file_path = val

    @property
    def logger_formatter(self):
        """Message format of the log entries.

        The default is ``'%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s'``.
        """
        return self.__logger_formatter

    @logger_formatter.setter
    def logger_formatter(self, val):
        self.__logger_formatter = val

    @property
    def logger_datefmt(self):
        """Date format of the log entries.

        The default is ``'%Y/%m/%d %H.%M.%S'``
        """
        return self.__logger_datefmt

    @logger_datefmt.setter
    def logger_datefmt(self, val):
        self.__logger_datefmt = val

    @property
    def enable_debug_edb_logger(self):
        """Enable or disable the logger for any EDB API methods."""
        return self.__enable_debug_edb_logger

    @enable_debug_edb_logger.setter
    def enable_debug_edb_logger(self, val):
        self.__enable_debug_edb_logger = val

    @property
    def enable_debug_grpc_api_logger(self):
        """Enable or disable the logging for the gRPC API calls."""
        return self.__enable_debug_grpc_api_logger

    @enable_debug_grpc_api_logger.setter
    def enable_debug_grpc_api_logger(self, val):
        self.__enable_debug_grpc_api_logger = val

    @property
    def enable_debug_geometry_operator_logger(self):
        """Enable or disable the logging for the geometry operators.

        This setting is useful for debug purposes.
        """
        return self.__enable_debug_geometry_operator_logger

    @enable_debug_geometry_operator_logger.setter
    def enable_debug_geometry_operator_logger(self, val):
        self.__enable_debug_geometry_operator_logger = val

    @property
    def enable_debug_internal_methods_logger(self):
        """Enable or disable the logging for internal methods.

        This setting is useful for debug purposes.
        """
        return self.__enable_debug_internal_methods_logger

    @enable_debug_internal_methods_logger.setter
    def enable_debug_internal_methods_logger(self, val):
        self.__enable_debug_internal_methods_logger = val

    @property
    def enable_debug_logger(self):
        """Enable or disable the debug level logger."""
        return self.__enable_debug_logger

    @enable_debug_logger.setter
    def enable_debug_logger(self, val):
        self.__enable_debug_logger = val

    @property
    def aedt_log_file(self):
        """Path to the AEDT log file.

        Used to specify that Electronics Desktop has to be launched with ``-Logfile`` option.
        """
        return self.__aedt_log_file

    @aedt_log_file.setter
    def aedt_log_file(self, value: str):
        self.__aedt_log_file = value

    # ############################# LSF properties ############################

    @property
    def lsf_queue(self):
        """LSF queue name.

        This attribute is valid only on Linux systems running LSF Scheduler.
        """
        return self.__lsf_queue

    @lsf_queue.setter
    def lsf_queue(self, value):
        self.__lsf_queue = value

    @property
    def use_lsf_scheduler(self):
        """Whether to use LSF Scheduler.

        This attribute is valid only on Linux systems running LSF Scheduler.
        """
        return self.__use_lsf_scheduler

    @use_lsf_scheduler.setter
    def use_lsf_scheduler(self, value):
        self.__use_lsf_scheduler = value

    @property
    def lsf_aedt_command(self):
        """Command to launch the task in the LSF Scheduler.

        The default is ``"ansysedt"``.
        This attribute is valid only on Linux systems running LSF Scheduler.
        """
        return self.__lsf_aedt_command

    @lsf_aedt_command.setter
    def lsf_aedt_command(self, value):
        self.__lsf_aedt_command = value

    @property
    def lsf_num_cores(self):
        """Number of LSF cores.

        This attribute is valid only on Linux systems running LSF Scheduler.
        """
        warnings.warn("Use :attr:`num_cores`.", DeprecationWarning)
        return self.__num_cores

    @lsf_num_cores.setter
    def lsf_num_cores(self, value):
        warnings.warn("Use :attr:`num_cores`.", DeprecationWarning)
        self.__num_cores = int(value)

    @property
    def num_cores(self):
        """Number cores to use with the scheduler."""
        return self.__num_cores

    @num_cores.setter
    def num_cores(self, value):
        self.__num_cores = int(value)

    @property
    def lsf_ram(self):
        """RAM allocated for the LSF job.

        This attribute is valid only on Linux systems running LSF Scheduler.
        """
        return self.__lsf_ram

    @lsf_ram.setter
    def lsf_ram(self, value):
        self.__lsf_ram = int(value)

    @property
    def lsf_ui(self):
        """Value passed in the LSF 'select' string to the ui resource."""
        return self.__lsf_ui

    @lsf_ui.setter
    def lsf_ui(self, value):
        if value is not None:
            self.__lsf_ui = int(value)

    @property
    def lsf_timeout(self):
        """Timeout in seconds for trying to start the interactive session. The default is ``3600`` seconds."""
        return self.__lsf_timeout

    @lsf_timeout.setter
    def lsf_timeout(self, value):
        self.__lsf_timeout = int(value)

    @property
    def lsf_osrel(self):
        """Operating system string.
        This attribute is valid only on Linux systems running LSF Scheduler.
        """
        return self.__lsf_osrel

    @lsf_osrel.setter
    def lsf_osrel(self, value):
        self.__lsf_osrel = value

    @property
    def custom_lsf_command(self):
        """Command to launch in the LSF Scheduler. The default is ``None``.
        This attribute is valid only on Linux systems running LSF Scheduler.
        """
        return self.__custom_lsf_command

    @custom_lsf_command.setter
    def custom_lsf_command(self, value):
        self.__custom_lsf_command = value

    # ############################## Environment variable properties ##############################

    @property
    def aedt_environment_variables(self):
        """Environment variables that are set before launching a new AEDT session,
        including those that enable the beta features.
        """
        return self.__aedt_environment_variables

    @aedt_environment_variables.setter
    def aedt_environment_variables(self, value):
        self.__aedt_environment_variables = value

    # ##################################### General properties ####################################

    @property
    def remote_api(self):
        """State whether remote API is used or not."""
        return self.__remote_api

    @remote_api.setter
    def remote_api(self, value: bool):
        self.__remote_api = value

    @property
    def formatter(self):
        """Get the formatter."""
        return self.__formatter

    @formatter.setter
    def formatter(self, value: logging.Formatter):
        self.__formatter = value

    @property
    def remote_rpc_session(self):
        """Get the RPyC connection."""
        return self.__remote_rpc_session

    @remote_rpc_session.setter
    def remote_rpc_session(self, value: Any):
        self.__remote_rpc_session = value

    @property
    def remote_rpc_session_temp_folder(self):
        """Get the remote RPyC session temp folder."""
        return self.__remote_rpc_session_temp_folder

    @remote_rpc_session_temp_folder.setter
    def remote_rpc_session_temp_folder(self, value: str):
        self.__remote_rpc_session_temp_folder = value

    @property
    def remote_rpc_service_manager_port(self):
        """Get the remote RPyC service manager port."""
        return self.__remote_rpc_service_manager_port

    @remote_rpc_service_manager_port.setter
    def remote_rpc_service_manager_port(self, value: int):
        self.__remote_rpc_service_manager_port = value

    @property
    def time_tick(self):
        """Time in seconds since the 'epoch' as a floating-point number."""
        return self.__time_tick

    @time_tick.setter
    def time_tick(self, value: float):
        self.__time_tick = value

    @property
    def release_on_exception(self):
        """Enable or disable the release of AEDT on exception."""
        return self.__release_on_exception

    @release_on_exception.setter
    def release_on_exception(self, value):
        self.__release_on_exception = value

    @property
    def objects_lazy_load(self):
        """Flag for enabling and disabling the lazy load. The default value is ``True``."""
        return self.__objects_lazy_load

    @objects_lazy_load.setter
    def objects_lazy_load(self, value):
        self.__objects_lazy_load = value

    @property
    def lazy_load(self):
        """Flag for enabling and disabling the lazy load. The default value is ``True``."""
        return self.__lazy_load

    @lazy_load.setter
    def lazy_load(self, value):
        self.__lazy_load = value

    @property
    def wait_for_license(self):
        """Enable or disable the use of the flag `-waitforlicense` when launching Electronic Desktop.

        The default value is ``False``.
        """
        return self.__wait_for_license

    @wait_for_license.setter
    def wait_for_license(self, value):
        self.__wait_for_license = value

    @property
    def retry_n_times_time_interval(self):
        """Time interval between the retries by the ``_retry_n_times`` method."""
        return self.__retry_n_times_time_interval

    @retry_n_times_time_interval.setter
    def retry_n_times_time_interval(self, value):
        self.__retry_n_times_time_interval = float(value)

    @property
    def number_of_grpc_api_retries(self):
        """Number of gRPC API retries. The default is ``3``."""
        return self.__number_of_grpc_api_retries

    @number_of_grpc_api_retries.setter
    def number_of_grpc_api_retries(self, value):
        self.__number_of_grpc_api_retries = int(value)

    @property
    def desktop_launch_timeout(self):
        """Timeout in seconds for trying to launch AEDT. The default is ``120`` seconds."""
        return self.__desktop_launch_timeout

    @desktop_launch_timeout.setter
    def desktop_launch_timeout(self, value):
        self.__desktop_launch_timeout = int(value)

    @property
    def aedt_version(self):
        """AEDT version in the form ``"2023.x"``.

        In AEDT 2022 R2 and later, evaluating a bounding box by exporting a SAT file is disabled.
        """
        return self.__aedt_version

    @aedt_version.setter
    def aedt_version(self, value):
        if value is not None:
            self.__aedt_version = value
            if self.__aedt_version >= "2023.1":
                self.disable_bounding_box_sat = True

    @property
    def aedt_install_dir(self):
        """AEDT installation path."""
        return self.__aedt_install_dir

    @aedt_install_dir.setter
    def aedt_install_dir(self, value):
        self.__aedt_install_dir = value

    @property
    def use_multi_desktop(self):
        """Flag indicating if multiple desktop sessions are enabled in the same Python script.

        Current limitations follow:
        - Release without closing the desktop is not possible,
        - The first desktop created must be the last to be closed.

        Enabling multiple desktop sessions is a beta feature.
        """
        return self.__use_multi_desktop

    @use_multi_desktop.setter
    def use_multi_desktop(self, value):
        self.__use_multi_desktop = value

    @property
    def edb_dll_path(self):
        """Optional path for the EDB DLL file."""
        if self.__edb_dll_path is not None:
            # If the optional path is set, return it
            return Path(self.__edb_dll_path)
        return None

    @edb_dll_path.setter
    def edb_dll_path(self, value):
        if value is not None:
            dll_path = Path(value)
            if dll_path.exists():
                self.__edb_dll_path = dll_path

    @property
    def enable_pandas_output(self):
        """Flag for whether Pandas is being used to export dictionaries and lists.

        This attribute applies to Solution data output.
        The default is ``False``. If ``True``, the property or method returns a Pandas object.
        This property is valid only in the CPython environment.
        """
        return self.__enable_pandas_output

    @enable_pandas_output.setter
    def enable_pandas_output(self, val):
        self.__enable_pandas_output = val

    @property
    def force_error_on_missing_project(self):
        """Flag for whether to check the project path.

        The default is ``False``.
        If ``True``, when passing a project path, the project has to exist.
        Otherwise, an error is raised.
        """
        return self.__force_error_on_missing_project

    @force_error_on_missing_project.setter
    def force_error_on_missing_project(self, val):
        self.__force_error_on_missing_project = val

    @property
    def disable_bounding_box_sat(self):
        """Flag for enabling and disabling bounding box evaluation by exporting a SAT file."""
        return self.__disable_bounding_box_sat

    @disable_bounding_box_sat.setter
    def disable_bounding_box_sat(self, val):
        self.__disable_bounding_box_sat = val

    @property
    def use_grpc_api(self):
        """Flag for whether to use the gRPC API or legacy COM object."""
        return self.__use_grpc_api

    @use_grpc_api.setter
    def use_grpc_api(self, val):
        self.__use_grpc_api = val

    @property
    def enable_error_handler(self):
        """Flag for enabling and disabling the internal PyAEDT error handling."""
        return self.__enable_error_handler

    @enable_error_handler.setter
    def enable_error_handler(self, val):
        self.__enable_error_handler = val

    @property
    def pyaedt_server_path(self):
        """Get ``PYAEDT_SERVER_AEDT_PATH`` environment variable."""
        self.__pyaedt_server_path = os.getenv("PYAEDT_SERVER_AEDT_PATH", "")
        return self.__pyaedt_server_path

    # NOTE: Convenient way to set the environment variable for RPyC
    @pyaedt_server_path.setter
    def pyaedt_server_path(self, val):
        os.environ["PYAEDT_SERVER_AEDT_PATH"] = str(val)
        self.__pyaedt_server_path = os.environ["PYAEDT_SERVER_AEDT_PATH"]

    @property
    def skip_license_check(self):
        """Flag indicating whether to check for license availability when launching the Desktop."""
        return self.__skip_license_check

    @skip_license_check.setter
    def skip_license_check(self, value):
        self.__skip_license_check = value

    @property
    def use_local_example_data(self):
        """Methods in downloads.py will use the local examples folder if this is set."""
        return self.__use_local_example_data

    @use_local_example_data.setter
    def use_local_example_data(self, value):
        self.__use_local_example_data = value

    @property
    def local_example_folder(self):
        """Methods in downloads.py will use the local examples folder if this is set."""
        return self.__local_example_folder

    @local_example_folder.setter
    def local_example_folder(self, value):
        self.__local_example_folder = value

    @property
    def pyd_libraries_path(self):
        if self.__pyd_libraries_user_path is not None:
            # If the user path is set, return it
            return Path(self.__pyd_libraries_user_path)
        return Path(self.__pyd_libraries_path)

    @property
    def pyd_libraries_user_path(self):
        # Get the user path for PyAEDT libraries.
        if self.__pyd_libraries_user_path is not None:
            return Path(self.__pyd_libraries_user_path)
        return None

    @pyd_libraries_user_path.setter
    def pyd_libraries_user_path(self, val):
        if val is None:
            # If the user path is None, set it to None
            self.__pyd_libraries_user_path = None
        else:
            lib_path = Path(str(val))
            if not lib_path.exists():
                # If the user path does not exist, return None
                raise ValueError("The user path for PyAEDT libraries does not exist. Please set a valid path.")
            else:
                # If the user path exists, set it as a Path object
                self.__pyd_libraries_user_path = lib_path

    # yaml setting file IO methods

    def load_yaml_configuration(self, path: Union[Path, str], raise_on_wrong_key: bool = False):
        """Update default settings from a YAML configuration file."""
        import yaml

        def filter_settings(settings: dict, allowed_keys: List[str]):
            """Filter the items of settings based on a list of allowed keys."""
            return filter(lambda item: item[0] in allowed_keys, settings.items())

        def filter_settings_with_raise(settings: dict, allowed_keys: List[str]):
            """Filter the items of settings based on a list of allowed keys."""
            for key, value in settings.items():
                if key not in allowed_keys:
                    raise KeyError(f"Key '{key}' is not part of the allowed keys {allowed_keys}")
                yield key, value

        configuration_file = Path(path)
        if configuration_file.exists():
            with open(configuration_file, "r") as yaml_file:
                local_settings = yaml.safe_load(yaml_file)
            pairs = [
                ("log", ALLOWED_LOG_SETTINGS),
                ("lsf", ALLOWED_LSF_SETTINGS),
                ("general", ALLOWED_GENERAL_SETTINGS),
            ]
            for setting_type, allowed_settings_key in pairs:
                settings = local_settings.get(setting_type, {})
                print(setting_type, allowed_settings_key)
                if raise_on_wrong_key:
                    for key, value in filter_settings_with_raise(settings, allowed_settings_key):
                        setattr(self, key, value)
                else:
                    for key, value in filter_settings(settings, allowed_settings_key):
                        setattr(self, key, value)
            # NOTE: Handle env var differently as they are loaded at once
            setting_type = "aedt_env_var"
            settings = local_settings.get(setting_type, {})
            if settings:
                if raise_on_wrong_key and any(key not in ALLOWED_AEDT_ENV_VAR_SETTINGS for key in settings.keys()):
                    raise KeyError("An environment variable key is not part of the allowed keys.")
                self.aedt_environment_variables = settings

    def write_yaml_configuration(self, path: Union[Path, str]):
        """Write the current settings into a YAML configuration file."""
        import yaml

        configuration_file = Path(path)

        data = {}
        data["log"] = {
            key: str(value) if isinstance(value := getattr(self, key), Path) else value for key in ALLOWED_LOG_SETTINGS
        }
        data["lsf"] = {
            key: str(value) if isinstance(value := getattr(self, key), Path) else value for key in ALLOWED_LSF_SETTINGS
        }
        data["aedt_env_var"] = getattr(self, "aedt_environment_variables")
        data["general"] = {
            key: str(value) if isinstance(value := getattr(self, key), Path) else value
            for key in ALLOWED_GENERAL_SETTINGS
        }

        with open(configuration_file, "w") as file:
            yaml.safe_dump(data, file, sort_keys=False)


settings = Settings()
inner_project_settings = _InnerProjectSettings()
