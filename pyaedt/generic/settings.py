import logging
import os
import time

is_linux = os.name == "posix"


class Settings(object):
    """Manages all PyAEDT environment variables and global settings."""

    def __init__(self):
        self._enable_logger = True
        self._enable_desktop_logs = True
        self._enable_screen_logs = True
        self._enable_file_logs = True
        self.pyaedt_server_path = ""
        self._logger_file_path = None
        self._logger_formatter = "%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s"
        self._logger_datefmt = "%Y/%m/%d %H.%M.%S"
        self._enable_debug_edb_logger = False
        self._enable_debug_grpc_api_logger = False
        self._enable_debug_methods_argument_logger = False
        self._enable_debug_geometry_operator_logger = False
        self._enable_debug_internal_methods_logger = False
        self._enable_debug_logger = False
        self._enable_error_handler = True
        # self._non_graphical = False
        self._aedt_version = None
        self.remote_api = False
        self._use_grpc_api = None
        # self.machine = ""
        # self.port = 0
        self.formatter = None
        self.remote_rpc_session = None
        self.remote_rpc_session_temp_folder = ""
        self.remote_rpc_service_manager_port = 17878
        self._project_properties = {}
        self._project_time_stamp = 0
        self._disable_bounding_box_sat = False
        self._force_error_on_missing_project = False
        self._enable_pandas_output = False
        self.time_tick = time.time()
        self._global_log_file_name = "pyaedt_{}.log".format(os.path.split(os.path.expanduser("~"))[-1])
        self._enable_global_log_file = True
        self._enable_local_log_file = False
        self._global_log_file_size = 10
        self._edb_dll_path = None
        self._lsf_num_cores = 2
        self._lsf_ram = 1000
        self._use_lsf_scheduler = False
        self._lsf_aedt_command = "ansysedt"
        self._lsf_timeout = 3600
        self._lsf_queue = None
        self._aedt_environment_variables = {
            "ANS_MESHER_PROC_DUMP_PREPOST_BEND_SM3": "1",
            "ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE": "1",
            "ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE": "1",
            "ANSYSEM_FEATURE_SF222134_CABLE_MODELING_ENHANCEMENTS_ENABLE": "1",
            "ANSYSEM_FEATURE_F395486_RIGID_FLEX_BENDING_ENABLE": "1",
            "ANSYSEM_FEATURE_S432616_LAYOUT_COMPONENT_IN_3D_ENABLE": "1",
            "ANSYSEM_FEATURE_F545177_ECAD_INTEGRATION_WITH_APHI_ENABLE": "1",
            "ANSYSEM_FEATURE_F650636_MECH_LAYOUT_COMPONENT_ENABLE": "1",
        }
        if is_linux:
            self._aedt_environment_variables["ANS_NODEPCHECK"] = "1"
        self._desktop_launch_timeout = 90
        # self._aedt_process_id = None
        # self._is_student = False
        self._number_of_grpc_api_retries = 3
        self._retry_n_times_time_interval = 0.1

    @property
    def retry_n_times_time_interval(self):
        """Time interval between the retries of the method _retry_n_times.

        Returns
        -------
        float
        """
        return self._retry_n_times_time_interval

    @retry_n_times_time_interval.setter
    def retry_n_times_time_interval(self, value):
        self._retry_n_times_time_interval = float(value)

    @property
    def number_of_grpc_api_retries(self):
        """Number of Grpc API retries. Default is 3.

        Returns
        -------
        int
        """
        return self._number_of_grpc_api_retries

    @number_of_grpc_api_retries.setter
    def number_of_grpc_api_retries(self, value):
        self._number_of_grpc_api_retries = int(value)

    # @property
    # def aedt_process_id(self):
    #     """ID of the desktop process. The default is ``None``.
    #
    #     Returns
    #     -------
    #     int
    #     """
    #     return self._aedt_process_id
    #
    # @aedt_process_id.setter
    # def aedt_process_id(self, value):
    #     self._aedt_process_id = int(value)
    #
    # @property
    # def is_student(self):
    #     """Whether the desktop process is set to the student version. The
    #     default is ``False``.
    #
    #     Returns
    #     -------
    #     bool
    #     """
    #     return self._is_student
    #
    # @is_student.setter
    # def is_student(self, value):
    #     self._is_student = value

    @property
    def desktop_launch_timeout(self):
        """Set the desktop launcher max timeout. Default is ``90`` seconds.

        Returns
        -------
        int
        """
        return self._desktop_launch_timeout

    @desktop_launch_timeout.setter
    def desktop_launch_timeout(self, value):
        self._desktop_launch_timeout = int(value)

    @property
    def aedt_environment_variables(self):
        """Set environment variables to be set before launching a new aedt session.
        This includes beta features enablemement.

        Returns
        -------
        dict
        """
        return self._aedt_environment_variables

    @aedt_environment_variables.setter
    def aedt_environment_variables(self, value):
        self._aedt_environment_variables = value

    @property
    def lsf_queue(self):
        """LSF queue name. This attribute is valid only on Linux
        systems running LSF Scheduler."""
        return self._lsf_queue

    @lsf_queue.setter
    def lsf_queue(self, value):
        self._lsf_queue = value

    @property
    def use_lsf_scheduler(self):
        """Whether to use LSF Scheduler. This attribute is valid only on Linux
        systems running LSF Scheduler."""
        return self._use_lsf_scheduler

    @use_lsf_scheduler.setter
    def use_lsf_scheduler(self, value):
        self._use_lsf_scheduler = value

    @property
    def lsf_aedt_command(self):
        """Get or set the ``ansysedt`` command to launch. The default is ``"ansysedt"``.
        This attribute is valid only on Linux systems running LSF Scheduler."""
        return self._lsf_aedt_command

    @lsf_aedt_command.setter
    def lsf_aedt_command(self, value):
        self._lsf_aedt_command = value

    @property
    def lsf_num_cores(self):
        """Get or set the number of LSF cores. This attribute is valid only
        on Linux systems running LSF Scheduler."""
        return self._lsf_num_cores

    @lsf_num_cores.setter
    def lsf_num_cores(self, value):
        self._lsf_num_cores = int(value)

    @property
    def lsf_ram(self):
        """Get or set the RAM allocated for the LSF job. This attribute is valid
        only on Linux systems running LSF Scheduler."""
        return self._lsf_ram

    @lsf_ram.setter
    def lsf_ram(self, value):
        self._lsf_ram = int(value)

    @property
    def lsf_timeout(self):
        """Get or set the timeout for starting the interactive session. The default is ``3600`` seconds."""
        return self._lsf_timeout

    @lsf_timeout.setter
    def lsf_timeout(self, value):
        self._lsf_timeout = int(value)

    @property
    def aedt_version(self):
        """Get and set the aedt version.
        It disables the sat bounding box for AEDT version > 2022.2.

        Returns
        -------
        str
            Aedt version in the form ``"2023.x"``.
        """
        return self._aedt_version

    @aedt_version.setter
    def aedt_version(self, value):
        self._aedt_version = value
        if self._aedt_version >= "2023.1":
            self.disable_bounding_box_sat = True

    @property
    def edb_dll_path(self):
        """Get/Set an optional path for Edb Dll.

        Returns
        -------
        bool
        """
        return self._edb_dll_path

    @edb_dll_path.setter
    def edb_dll_path(self, value):
        if os.path.exists(value):
            self._edb_dll_path = value

    @property
    def global_log_file_size(self):
        """Get/Set the global pyaedt log file size in Mbytes. The default value is ``10``.

        Returns
        -------
        bool
        """
        return self._global_log_file_size

    @global_log_file_size.setter
    def global_log_file_size(self, value):
        self._global_log_file_size = value

    @property
    def enable_global_log_file(self):
        """Enable/Disable the global pyaedt log file logging in global temp folder. Default is `True`.

        Returns
        -------
        bool
        """
        return self._enable_global_log_file

    @enable_global_log_file.setter
    def enable_global_log_file(self, value):
        self._enable_global_log_file = value

    @property
    def enable_local_log_file(self):
        """Enable/Disable the local pyaedt log file logging in projectname.pyaedt project folder. Default is `True`.

        Returns
        -------
        bool
        """
        return self._enable_local_log_file

    @enable_local_log_file.setter
    def enable_local_log_file(self, value):
        self._enable_local_log_file = value

    @property
    def global_log_file_name(self):
        """Get/Set the global pyaedt log file path. Default is pyaedt_username.log.

        Returns
        -------
        str
        """
        return self._global_log_file_name

    @global_log_file_name.setter
    def global_log_file_name(self, value):
        self._global_log_file_name = value

    @property
    def enable_pandas_output(self):
        """
        Set/Get a flag to use Pandas to export dict and lists. This applies to Solution data output.
        If ``True`` the property or method will return a pandas object in CPython environment.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return self._enable_pandas_output

    @enable_pandas_output.setter
    def enable_pandas_output(self, val):
        self._enable_pandas_output = val

    @property
    def enable_debug_methods_argument_logger(self):
        """
        Set/Get a flag to plot methods argument in debug logger.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return self._enable_debug_methods_argument_logger

    @enable_debug_methods_argument_logger.setter
    def enable_debug_methods_argument_logger(self, val):
        self._enable_debug_methods_argument_logger = val

    @property
    def force_error_on_missing_project(self):
        """Set/Get a flag to check project path.
        If ``True`` when passing a project path, the project has to exist otherwise it will raise an error.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return self._force_error_on_missing_project

    @force_error_on_missing_project.setter
    def force_error_on_missing_project(self, val):
        self._force_error_on_missing_project = val

    @property
    def disable_bounding_box_sat(self):
        """Set/Get Bounding Box Sat enablement.

        Returns
        -------
        bool
        """
        return self._disable_bounding_box_sat

    @disable_bounding_box_sat.setter
    def disable_bounding_box_sat(self, val):
        self._disable_bounding_box_sat = val

    @property
    def use_grpc_api(self):
        """Set/Get GRPC API usage or Legacy COM Object. This is the user setting.

        Returns
        -------
        bool
        """
        return self._use_grpc_api

    @use_grpc_api.setter
    def use_grpc_api(self, val):
        """Set/Get GRPC API usage or Legacy COM Object. This is the user setting."""
        self._use_grpc_api = val

    @property
    def logger(self):
        """Get the active logger."""
        try:
            return logging.getLogger("Global")
        except:  # pragma: no cover
            return logging.getLogger(__name__)

    # @property
    # def non_graphical(self):
    #     """Get the value for the non-graphical flag."""
    #     return self._non_graphical
    #
    # @non_graphical.setter
    # def non_graphical(self, val):
    #     self._non_graphical = val

    @property
    def enable_error_handler(self):
        """Return the content for the environment variable."""
        return self._enable_error_handler

    @enable_error_handler.setter
    def enable_error_handler(self, val):
        self._enable_error_handler = val

    @property
    def enable_desktop_logs(self):
        """Get the content for the environment variable."""
        return self._enable_desktop_logs

    @enable_desktop_logs.setter
    def enable_desktop_logs(self, val):
        self._enable_desktop_logs = val

    @property
    def enable_screen_logs(self):
        """Get the content for the environment variable."""
        return self._enable_screen_logs

    @enable_screen_logs.setter
    def enable_screen_logs(self, val):
        self._enable_screen_logs = val

    @property
    def pyaedt_server_path(self):
        """Get the content for the environment variable."""
        return os.getenv("PYAEDT_SERVER_AEDT_PATH", "")

    @pyaedt_server_path.setter
    def pyaedt_server_path(self, val):
        os.environ["PYAEDT_SERVER_AEDT_PATH"] = str(val)

    @property
    def enable_file_logs(self):
        """Get the content for the environment variable."""
        return self._enable_file_logs

    @enable_file_logs.setter
    def enable_file_logs(self, val):
        self._enable_file_logs = val

    @property
    def enable_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_logger

    @enable_logger.setter
    def enable_logger(self, val):
        self._enable_logger = val

    @property
    def logger_file_path(self):
        """Return the Environment Variable Content."""
        return self._logger_file_path

    @logger_file_path.setter
    def logger_file_path(self, val):
        self._logger_file_path = val

    @property
    def logger_formatter(self):
        """Return the Environment Variable Content."""
        return self._logger_formatter

    @logger_formatter.setter
    def logger_formatter(self, val):
        self._logger_formatter = val

    @property
    def logger_datefmt(self):
        """Return the Environment Variable Content."""
        return self._logger_datefmt

    @logger_datefmt.setter
    def logger_datefmt(self, val):
        self._logger_datefmt = val

    @property
    def enable_debug_edb_logger(self):
        """Enable or disable Logger for any EDB API method."""
        return self._enable_debug_edb_logger

    @property
    def enable_debug_grpc_api_logger(self):
        """Enable or disable Logger for any grpc API method."""
        return self._enable_debug_grpc_api_logger

    @enable_debug_grpc_api_logger.setter
    def enable_debug_grpc_api_logger(self, val):
        self._enable_debug_grpc_api_logger = val

    @enable_debug_edb_logger.setter
    def enable_debug_edb_logger(self, val):
        self._enable_debug_edb_logger = val

    @property
    def enable_debug_geometry_operator_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_debug_geometry_operator_logger

    @enable_debug_geometry_operator_logger.setter
    def enable_debug_geometry_operator_logger(self, val):
        self._enable_debug_geometry_operator_logger = val

    @property
    def enable_debug_internal_methods_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_debug_internal_methods_logger

    @enable_debug_internal_methods_logger.setter
    def enable_debug_internal_methods_logger(self, val):
        self._enable_debug_internal_methods_logger = val

    @property
    def enable_debug_logger(self):
        """Return the Environment Variable Content."""
        return self._enable_debug_logger

    @enable_debug_logger.setter
    def enable_debug_logger(self, val):
        self._enable_debug_logger = val


settings = Settings()
