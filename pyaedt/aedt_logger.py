# -*- coding: utf-8 -*-
import logging
import sys

from pyaedt import log_handler
from pyaedt import settings

message_levels = {"Global": 0, "Project": 1, "Design": 2}


class Msg:
    (INFO, WARNING, ERROR, FATAL) = range(4)


class MessageList:
    """
    Collects and returns messages from the AEDT message manager for a specified project name and design name.

    Parameters
    ---------
    msg_list : list
        List of messages extracted from AEDT.
    project_name : str
        Name of the project. The default is the active project.
    design_name : str
        Name of the design within the specified project. The default is the active design.


    Attributes
    ----------
    global_level : list of str
        List of strings representing the message content at the global level of the message manager.

    project_level : list of str
        List of strings representing the message content within the specified project.

    design_level : list of str
        List of strings representing the message content for the specified design within the specified project.

    """

    def __init__(self, msg_list, project_name, design_name):
        self.global_level = []
        self.project_level = []
        self.design_level = []
        global_label = "Project: *Global - Messages, "
        project_label = "Project: {}, ".format(project_name)
        design_label = "Project: {}, Design: {} (".format(project_name, design_name)
        for line in msg_list:
            # Find the first instance of '[' to get the message context
            loc = line.find("[")
            if loc < 0:
                # Format is not clear - append to global
                self.global_level.append(line)
            else:
                line_label = line[0:loc]
                msg_txt = line[loc:].strip()
                if design_label in line_label:
                    self.design_level.append(msg_txt)
                elif project_label in line_label:
                    self.project_level.append(msg_txt)
                elif global_label in line_label:
                    self.global_level.append(msg_txt)


class AppFilter(logging.Filter):
    """Specifies the destination of the logger.

    AEDT exposes three different loggers, which are the global, project, and design loggers.

    Parameters
    ----------
    destination : str, optional
        Logger to write to. Options are ``"Global"`, ``"Project"``, and ``"Design"``.
        The default is ``"Global"``.
    extra : str, optional
        Name of the design or project. The default is ``""``.
    """

    def __init__(self, destination="Global", extra=""):
        self._destination = destination
        self._extra = extra

    def filter(self, record):
        """
        Modify the record sent to the logger.

        Parameters
        ----------
        record : class:`logging.LogRecord`
            Contains information related to the event being logged.
        """
        record.destination = self._destination

        # This will avoid the extra '::' for Global that does not have any extra info.
        if not self._extra:
            record.extra = self._extra
        else:
            record.extra = self._extra + ":"
        return True


class AedtLogger(object):
    """
    Specifies the logger to use for each AEDT logger.

    This class allows you to add a handler to write messages to a file and to indicate
    whether to write mnessages to the standard output (stdout).

    Parameters
    ----------
    level : int, optional
        Logging level to filter the message severity allowed in the logger.
        The default is ``logging.DEBUG``.
    filename : str, optional
        Name of the file to write messages to. The default is ``None``.
    to_stdout : bool, optional
        Whether to write log messages to stdout. The default is ``False``.
    """

    def __init__(self, level=logging.DEBUG, filename=None, to_stdout=False):
        main = sys.modules["__main__"]

        self.level = level
        self.filename = filename or settings.logger_file_path
        settings.logger_file_path = self.filename
        # if is_ironpython:
        #     logging.basicConfig()
        self._global = logging.getLogger("Global")
        self._file_handler = None
        self._std_out_handler = None
        if settings.formatter:
            self.formatter = settings.formatter
        else:
            self.formatter = logging.Formatter(settings.logger_formatter, datefmt=settings.logger_datefmt)
        if not settings.enable_logger:
            self._global.addHandler(logging.NullHandler())
            return

        if self._global.handlers:
            if "messenger" in dir(self._global.handlers[0]):
                self._global.removeHandler(self._global.handlers[0])
                if self._global.handlers:
                    self._global.removeHandler(self._global.handlers[0])
        if not self._global.handlers:
            self._global.addHandler(log_handler.LogHandler(self, "Global", logging.DEBUG))
            main._aedt_handler = self._global.handlers
            self._global.setLevel(level)
            self._global.addFilter(AppFilter())

        if self.filename:
            self._file_handler = logging.FileHandler(self.filename)
            self._file_handler.setLevel(level)
            self._file_handler.setFormatter(self.formatter)
            self._global.addHandler(self._file_handler)

        if to_stdout:
            self._std_out_handler = logging.StreamHandler()
            self._std_out_handler.setLevel(level)

            self._std_out_handler.setFormatter(self.formatter)
            self._global.addHandler(self._std_out_handler)

    @property
    def _desktop(self):
        if "oDesktop" in dir(sys.modules["__main__"]):
            MainModule = sys.modules["__main__"]
            return MainModule.oDesktop
        return None  # pragma: no cover

    @property
    def _log_on_desktop(self):
        if self._desktop and settings.enable_desktop_logs:
            return True
        else:
            return False

    @_log_on_desktop.setter
    def _log_on_desktop(self, val):
        settings.enable_desktop_logs = val

    @property
    def _log_on_file(self):
        return settings.enable_file_logs

    @_log_on_file.setter
    def _log_on_file(self, val):
        settings.enable_file_logs = val

    @property
    def _log_on_screen(self):
        return settings.enable_screen_logs

    @_log_on_screen.setter
    def _log_on_screen(self, val):
        settings.enable_screen_logs = val

    @property
    def logger(self):
        """AEDT logger object."""
        if self._log_on_file:
            return logging.getLogger(__name__)
        else:
            return None  # pragma: no cover

    @property
    def messages(self):
        """Message manager content for the active project and design.

        Returns
        -------
        list of str
           List of messages for the active project and design.

        """
        return self.get_messages(self._project_name, self._design_name)

    def get_messages(self, project_name=None, design_name=None, level=0, aedt_messages=False):
        """Get the message manager content for a specified project and design.

        If the specified project and design names are invalid, they are ignored.

        Parameters
        ----------
        project_name : str
            Name of the project to read messages from. Leave empty string to get Desktop level messages.
        design_name : str
            Name of the design to read messages from. Leave empty string to get Desktop level messages.
        level : int
            Level of messages to read. 0 – info and above, 1 – warning and above, 2 – error and fatal
        aedt_messages : bool
            Read content of message manager even if logger is disabled.


        Returns
        -------
        list of str
            List of messages for the specified project and design.

        """
        project_name = project_name or self._project_name
        design_name = design_name or self._design_name
        if self._log_on_desktop or aedt_messages:
            global_message_data = self._desktop.GetMessages("", "", level)
            return MessageList(global_message_data, project_name, design_name)
        return MessageList([], project_name, design_name)

    def add_error_message(self, message_text, level=None):
        """
        Add a type 2 "Error" message to the message manager tree.

        Also add an error message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the error message.
        level : str, optional
            Level to add the error message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default is ``None``,
            in which case the error message gets added to the ``"Design"``
            level.

        Examples
        --------
        Add an error message to the AEDT message manager.

        >>> hfss.logger.project.error("Project Error Message", "Project")

        """
        self.add_message(2, message_text, level)

    def add_warning_message(self, message_text, level=None):
        """
        Add a type 1 "Warning" message to the message manager tree.

        Also add a warning message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the warning message.
        level : str, optional
            Level to add the warning message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default is ``None``,
            in which case the warning message gets added to the ``"Design"``
            level.

        Examples
        --------
        Add a warning message to the AEDT message manager.

        >>> hfss.logger.warning("Global warning message")

        """
        self.add_message(1, message_text, level)

    def add_info_message(self, message_text, level=None):
        """Add a type 0 "Info" message to the active design level of the message manager tree.

        Also add an info message to the logger if the handler is present.

        Parameters
        ----------
        message_text : str
            Text to display as the info message.
        level : str, optional
            Level to add the info message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default is ``None``,
            in which case the info message gets added to the ``"Design"``
            level.

        Examples
        --------
        Add an info message at the global level.

        >>> hfss.logger.info("Global warning message", "Global")

        """
        self.add_message(0, message_text, level)

    def add_debug_message(self, message_type, message_text):
        """
        Parameterized message to the message manager to specify the type and project or design level.

        Parameters
        ----------
        message_type : int
            Type of the message. Options are:

            * ``0`` : Info
            * ``1`` : Warning
            * ``2`` : Error

        message_text : str
            Text to display as the message.

        """

        if len(message_text) > 250:
            message_text = message_text[:250] + "..."

        # Print to stdout and to logger
        if self._log_on_file:
            if message_type == 0 and self.logger:
                self.logger.debug(message_text)
            elif message_type == 1 and self.logger:
                self.logger.warning(message_text)
            elif message_type == 2 and self.logger:
                self.logger.error(message_text)

    def add_message(self, message_type, message_text, level=None, proj_name=None, des_name=None):
        """Add a message to the message manager to specify the type and project or design level.

        Parameters
        ----------
        message_type : int
            Type of the message. Options are:
            * ``0`` : Info
            * ``1`` : Warning
            * ``2`` : Error
        message_text : str
            Text to display as the message.
        level : str, optional
            Level to add the message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default is ``None``,
            in which case the message gets added to the
            ``"Design"`` level.
        proj_name : str, optional
            Name of the project.
        des_name : str, optional
            Name of the design.
        """
        if not proj_name:
            proj_name = ""

        if not des_name:
            des_name = ""

        if not level:
            level = "Design"

        assert level in message_levels, "Message level must be `Design', 'Project', or 'Global'."

        if self._log_on_desktop and self._desktop:
            if not proj_name and message_levels[level] > 0:
                proj_name = self._project_name
            if not des_name and message_levels[level] > 1:
                des_name = self._design_name
            if des_name and ";" in des_name:
                des_name = des_name[des_name.find(";") + 1 :]
            try:
                self._desktop.AddMessage(proj_name, des_name, message_type, message_text)
            except:
                print("pyaedt info: Failed in Adding Desktop Message")

        if len(message_text) > 250:
            message_text = message_text[:250] + "..."

        # Print to stdout and to logger
        if self._log_on_screen:
            if message_type == 0:
                print("pyaedt info: {}".format(message_text))
            elif message_type == 1:
                print("pyaedt warning: {}".format(message_text))
            elif message_type == 2:
                print("pyaedt error: {}".format(message_text))
        if self._log_on_file:
            if message_type == 0 and self.logger:
                self.logger.debug(message_text)
            elif message_type == 1 and self.logger:
                self.logger.warning(message_text)
            elif message_type == 2 and self.logger:
                self.logger.error(message_text)

    def clear_messages(self, proj_name=None, des_name=None, level=2):
        """Clear all messages.

        Parameters
        ----------
        proj_name : str, optional
            Name of project. The default is ``None``, in which case messages
            are cleared for the current project. If blank, messages are cleared
            for all projects.
        des_name : str, optional
            Name of the design within the specified project. The default
            is ``None,`` in which case the current design is used.
            If blank, all designs are used.
        level : int, optional
            Level of the messages to clear. Options are:

            * ``0`` : Clear all info messages.
            * ``1`` : Clear all info and warning messages.
            * ``2`` : Clear all info, warning, and error messages.
            * ``3`` : Clear all messages, which include info, warning,
              error, and fatal-error messages.

            The default is ``2.``

        Examples
        --------
        Clear all messages in the current design and project.

        >>> hfss.clear_messages(level=3)

        """
        if self._log_on_desktop:
            if proj_name is None:
                proj_name = self._project_name
            if des_name is None:
                des_name = self._design_name
            self._desktop.ClearMessages(proj_name, des_name, level)

    @property
    def _oproject(self):
        if self._desktop:
            return self._desktop.GetActiveProject()

    @property
    def _odesign(self):
        if self._oproject:
            return self._oproject.GetActiveDesign()

    @property
    def _design_name(self):
        try:
            return self._odesign.GetName()
        except AttributeError:
            return ""

    @property
    def _project_name(self):
        try:
            return self._oproject.GetName()
        except AttributeError:
            return ""

    def add_logger(self, destination, level=logging.DEBUG):
        """
        Add a logger for either the active project or active design.

        Parameters
        ----------
        destination : str
            Logger to write to. Options are ``"Project"`` and ``"Design"``.
        level : int, optional
            Logging level enum. The default is ``logging.DEBUG``.
        """

        if destination == "Project":
            project_name = self._project_name
            self._project = logging.getLogger(project_name)
            self._project.addHandler(log_handler.LogHandler(self, "Project", level))
            self._project.setLevel(level)
            self._project.addFilter(AppFilter("Project", project_name))
            if self._file_handler is not None:
                self._project.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._project.addHandler(self._std_out_handler)
            return self._project
        elif destination == "Design":
            project_name = self._project_name
            design_name = self._design_name
            self._design = logging.getLogger(project_name + ":" + design_name)
            self._design.addHandler(log_handler.LogHandler(self, "Design", level))
            self._design.setLevel(level)
            self._design.addFilter(AppFilter("Design", design_name))
            if self._file_handler is not None:
                self._design.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._design.addHandler(self._std_out_handler)
            return self._design
        else:
            raise ValueError("The destination must be either 'Project' or 'Design'.")

    def disable_desktop_log(self):
        """Disable the log in AEDT."""
        self._log_on_desktop = False

    def enable_desktop_log(self):
        """Enable the log in AEDT."""
        self._log_on_desktop = True

    def disable_stdout_log(self):
        """Disable printing log messages to stdout."""
        self._log_on_screen = False
        self._global.removeHandler(self._std_out_handler)

    def enable_stdout_log(self):
        """Enable printing log messages to stdout."""
        self._log_on_screen = True

    def disable_log_on_file(self):
        """Disable writing log messages to an output file."""
        self._log_on_file = False
        self._file_handler.close()
        self._global.removeHandler(self._file_handler)

    def enable_log_on_file(self):
        """Enable writing log messages to an output file."""
        self._log_on_file = True
        self._file_handler = logging.FileHandler(self.filename)
        self._file_handler.setLevel(self.level)
        self._file_handler.setFormatter(self.formatter)
        self._global.addHandler(self._file_handler)

    def info(self, msg, *args, **kwargs):
        """Write an info message to the global logger."""
        return self._global.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Write a warning message to the global logger."""
        return self._global.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Write an error message to the global logger."""
        return self._global.error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Write a debug message to the global logger."""
        return self._global.debug(msg, *args, **kwargs)

    @property
    def glb(self):
        """Global logger."""
        self._global = logging.getLogger("Global")
        return self._global

    @property
    def project(self):
        """Project logger."""
        self._project = logging.getLogger(self._project_name)
        if not self._project.handlers:
            self.add_logger("Project")
        return self._project

    @property
    def design(self):
        """Design logger."""
        self._design = logging.getLogger(self._project_name + ":" + self._design_name)
        if not self._design.handlers:
            self.add_logger("Design")
        return self._design
