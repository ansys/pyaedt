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

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import shutil
import sys
import tempfile
import time

from ansys.aedt.core.generic.settings import settings

message_levels = {"Global": 0, "Project": 1, "Design": 2}


class Msg:
    (INFO, WARNING, ERROR, FATAL) = range(4)


class MessageList:
    """
    Collects and returns messages from the AEDT message manager for a specified project name and design name.

    Parameters
    ----------
    msg_list : list
        List of messages extracted from AEDT.

    Attributes
    ----------
    info_level : list of str
        List of strings representing the info messages of the message manager.

    warning_level : list of str
        List of strings representing the warning messages of the message manager.

    error_level : list of str
        List of strings representing the error messages of the message manager.

    debug_level : list of str
        List of strings representing the debug messages of the message manager.

    unknown_level : list of str
        List of strings representing the messages with no level of the message manager.

    """

    def __init__(self, msg_list):
        self.info_level = []
        self.warning_level = []
        self.error_level = []
        self.debug_level = []
        self.unknown_level = []
        self.global_level = []
        self.project_level = []
        self.design_level = []
        global_label = "Project: *Global - Messages, "
        project_label = "Project: "
        design_label = ", Design: "
        for line in msg_list:
            # Find the first instance of '[' to get the message context
            if "[info]" in line.lower():
                self.info_level.append(line)
            elif "[warning]" in line.lower():
                self.warning_level.append(line)
            elif "[error]" in line.lower():
                self.error_level.append(line)
            elif "[debug]" in line.lower():
                self.debug_level.append(line)
            else:  # pragma: no cover
                self.unknown_level.append(line)
            if global_label in line:
                self.global_level.append(line)
            elif design_label in line:
                self.design_level.append(line)
            elif project_label in line:
                self.project_level.append(line)
            else:
                self.global_level.append(line)


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


class AedtLogger:
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

    def __init__(self, level=logging.DEBUG, filename=None, to_stdout=False, desktop=None):
        self._desktop_class = desktop
        self._oproject = None
        self._odesign = None
        self._project_name = ""
        self._design_name = ""
        self._std_out_handler = None
        self._files_handlers = []
        self.level = level
        self._non_graphical = None
        self.filename = filename or settings.logger_file_path
        self._messages = []
        settings.logger_file_path = self.filename

        self._global = logging.getLogger("Global")
        if not settings.enable_logger:
            self._global.addHandler(logging.NullHandler())
            return

        self._projects = {}

        self._global.setLevel(level)
        self._global.addFilter(AppFilter())

        if settings.formatter:
            self.formatter = settings.formatter
        else:
            self.formatter = logging.Formatter(settings.logger_formatter, datefmt=settings.logger_datefmt)
        global_handler = False
        if settings.enable_global_log_file:
            for handler in self._global.handlers:
                if settings.global_log_file_name in str(handler):
                    global_handler = True
                    break
            log_file = Path(tempfile.gettempdir()) / settings.global_log_file_name
            my_handler = RotatingFileHandler(
                log_file,
                mode="a",
                maxBytes=float(settings.global_log_file_size) * 1024 * 1024,
                backupCount=2,
                encoding=None,
                delay=0,
            )
            my_handler.setFormatter(self.formatter)
            my_handler.setLevel(self.level)
            if not global_handler and settings.global_log_file_name:
                self._global.addHandler(my_handler)
            self._files_handlers.append(my_handler)
        if self.filename and Path(self.filename).exists():
            shutil.rmtree(self.filename, ignore_errors=True)
        if self.filename and settings.enable_local_log_file:
            self.add_file_logger(self.filename, "Global", level)

        if to_stdout:
            settings.enable_screen_logs = True
            self._std_out_handler = logging.StreamHandler(sys.stdout)
            self._std_out_handler.setLevel(level)
            _logger_stdout_formatter = logging.Formatter("PyAEDT %(levelname)s: %(message)s")

            self._std_out_handler.setFormatter(_logger_stdout_formatter)
            self._global.addHandler(self._std_out_handler)
        self._timer = time.time()
        settings.logger = self

    def add_file_logger(self, filename, project_name, level=None):
        """Add a new file to the logger handlers list."""
        _project = logging.getLogger(project_name)
        _project.setLevel(level if level else self.level)
        _project.addFilter(AppFilter("Project", project_name))
        _file_handler = logging.FileHandler(filename)
        _file_handler.setLevel(level if level else self.level)
        _file_handler.setFormatter(self.formatter)
        _project.addHandler(_file_handler)
        if self._std_out_handler is not None:
            _project.addHandler(self._std_out_handler)
        for handler in self._global.handlers:
            if settings.global_log_file_name in str(handler):
                _project.addHandler(handler)
                break
        self.info(f"New logger file {filename} added to handlers.")
        self._files_handlers.append(_file_handler)
        _project.info_timer = self.info_timer
        _project.reset_timer = self.reset_timer
        _project._timer = time.time()

        return _project

    def remove_file_logger(self, project_name):
        """Remove a file from the logger handlers list."""
        handlers = [i for i in self._global.handlers]
        for handler in self._files_handlers:
            if f"pyaedt_{project_name}.log" in str(handler):
                handler.close()
                if handler in handlers:
                    self._global.removeHandler(handler)
                self.info(f"logger file pyaedt_{project_name}.log removed from handlers.")

    def remove_all_project_file_logger(self):
        """Remove all the local files from the logger handlers list."""
        handlers = [i for i in self._global.handlers]
        for handler in handlers:
            if "pyaedt_" in str(handler):
                handler.close()
                self._global.removeHandler(handler)
        self.info("Project files removed from handlers.")

    @property
    def _desktop(self):
        if self._desktop_class:
            return self._desktop_class.odesktop
        return None  # pragma: no cover

    @property
    def _log_on_desktop(self):
        try:
            if self._desktop and settings.enable_desktop_logs:
                return True
            else:
                return False
        except Exception:  # pragma: no cover
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
            return logging.getLogger("Global")
        else:
            return None  # pragma: no cover

    @property
    def aedt_messages(self):
        """Message manager content for the active project and design.

        Returns
        -------
        list of str
           List of messages for the active project and design.

        """
        return self.get_messages(self.project_name, self.design_name, aedt_messages=True)

    @property
    def messages(self):
        """Message manager content for the active session.

        Returns
        -------
        list of str
           List of messages for the active session.

        """
        return self.get_messages(self.project_name, self.design_name)

    @property
    def aedt_info_messages(self):
        """Message manager content for the active project and design.

        Returns
        -------
        list of str
           List of info messages for the active project and design.

        """
        aa = self.get_messages(self.project_name, self.design_name, aedt_messages=True)
        return aa.info_level

    @property
    def aedt_warning_messages(self):
        """Message manager content for the active project and design.

        Returns
        -------
        list of str
           List of warning messages for the active project and design.

        """
        aa = self.get_messages(self.project_name, self.design_name, aedt_messages=True)
        return aa.warning_level

    @property
    def aedt_error_messages(self):
        """Message manager content for the active project and design.

        Returns
        -------
        list of str
           List of error messages for the active project and design.

        """
        aa = self.get_messages(self.project_name, self.design_name, aedt_messages=True)
        return aa.error_level

    @property
    def info_messages(self):
        """Message manager content for the active pyaedt session.

        Returns
        -------
        list of str
           List of info messages.

        """
        aa = self.get_messages(self.project_name, self.design_name, aedt_messages=False)
        return aa.info_level

    @property
    def warning_messages(self):
        """Message manager content for the active pyaedt session.

        Returns
        -------
        list of str
           List of warning messages.

        """
        aa = self.get_messages(self.project_name, self.design_name, aedt_messages=False)

        return aa.warning_level

    @property
    def error_messages(self):
        """Message manager content for the active pyaedt session.

        Returns
        -------
        list of str
           List of error messages.

        """
        aa = self.get_messages(self.project_name, self.design_name, aedt_messages=False)
        return aa.error_level

    def reset_timer(self, time_val=None):
        """Reset actual timer to  actual time or specified time.

        Parameters
        ----------
        time_val : float, optional
            Value time to apply.

        Returns
        -------

        """
        if time_val:
            self._timer = time_val
        else:
            self._timer = time.time()
        return self._timer

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
        if aedt_messages and self._desktop.GetVersion() > "2022.2":
            project_name = project_name or self.project_name
            design_name = design_name or self.design_name
            global_message_data = list(self._desktop.GetMessages("", "", level))
            # if a 3d component is open, GetMessages without the project name argument returns messages with
            # "(3D Component)" appended to project name
            if not any(msg in global_message_data for msg in self._desktop.GetMessages(project_name, "", 0)):
                project_name = project_name + " (3D Component)"
            global_message_data.extend(list(self._desktop.GetMessages(project_name, design_name, level)))
            global_message_data = list(set(global_message_data))
            return MessageList(global_message_data)
        message_lists = []
        levels = {0: "[info] ", 1: "[warning] ", 2: "[error] ", 3: "[debug] "}

        for message in self._messages:
            if message[0] >= level:
                if not project_name or not message[2] or project_name == message[2]:
                    if not design_name or not message[3] or design_name == message[3]:
                        message_lists.append(levels[message[0]] + message[1])
        return MessageList(message_lists)

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

        >>> hfss.logger.project_logger.error("Project Error Message", "Project")

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

    def add_debug_message(self, message_text, level=None):
        """
        Parameterized message to the message manager to specify the type and project or design level.

        Parameters
        ----------
        message_text : str
            Text to display as the message.
        level : str, optional
            Level to add the info message to. Options are ``"Global"``,
            ``"Project"``, and ``"Design"``. The default value is ``None``,
            in which case the info message gets added to the ``"Design"``
            level.
        """
        return self.add_message(3, message_text, level=level)

    def add_message(self, message_type, message_text, level=None, proj_name=None, des_name=None):
        """Add a message to the message manager to specify the type and project or design level.

        Parameters
        ----------
        message_type : int
            Type of the message. Options are:
            * ``0`` : Info
            * ``1`` : Warning
            * ``2`` : Error
            * ``3`` : Debug
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
        self._log_on_dekstop(
            message_type=message_type, message_text=message_text, level=level, proj_name=proj_name, des_name=des_name
        )

        self._log_on_handler(message_type, message_text)

    def _log_on_dekstop(self, message_type, message_text, level=None, proj_name=None, des_name=None):
        if not proj_name:
            proj_name = ""

        if not des_name:
            des_name = ""

        if not level:
            level = "Design"

        if level not in message_levels:
            raise ValueError("Message level must be 'Design', 'Project', or 'Global'.")

        if self._log_on_desktop and self._desktop:
            if not proj_name and message_levels[level] > 0:
                proj_name = self.project_name
            if not des_name and message_levels[level] > 1:
                des_name = self.design_name
            if des_name and ";" in des_name:
                des_name = des_name[des_name.find(";") + 1 :]
            try:
                self._desktop.AddMessage(proj_name, des_name, message_type, message_text)
            except Exception:  # pragma: no cover
                self._global.info("Failed to add desktop message.")

    def _log_on_handler(self, message_type, message_text, *args, **kwargs):
        message_text = str(message_text)
        if args:
            try:
                msg1 = message_text % tuple(str(i) for i in args)
            except TypeError:
                msg1 = message_text
        else:
            msg1 = message_text
        self._messages.append([message_type, msg1, self.project_name, self.design_name])
        if not (self._log_on_file or self._log_on_screen) or not self._global:
            return
        if len(message_text) > 250 and message_type < 3:
            message_text = message_text[:250] + "..."
        if message_type == 0:
            self._global.info(message_text, *args, **kwargs)
        elif message_type == 1:
            self._global.warning(message_text, *args, **kwargs)
        elif message_type == 2:
            self._global.error(message_text, *args, **kwargs)
        elif message_type == 3:
            self._global.debug(message_text, *args, **kwargs)

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

        Clear all messages.

        >>> hfss.clear_messages(proj_name="", des_name="", level=3)
        """
        if self.non_graphical:
            return
        if proj_name is None:
            proj_name = self.project_name
        if des_name is None:
            des_name = self.design_name
        try:
            self._desktop.ClearMessages(proj_name, des_name, level)
        except Exception:  # pragma: no cover
            self._global.info("Failed to clear desktop messages.")

    @property
    def non_graphical(self):
        """Check if desktop is graphical or not.

        Returns
        -------
        bool
        """
        if self._non_graphical is None and self._desktop:
            self._non_graphical = self._desktop.GetIsNonGraphical()

        return self._non_graphical

    @property
    def oproject(self):
        """Project object.

        Returns
        -------
        object
        """
        if self._oproject:
            return self._oproject
        return None  # pragma: no cover

    @property
    def odesign(self):
        """Design object.

        Returns
        -------
        object
        """
        if self._odesign:
            return self._odesign
        return None  # pragma: no cover

    @oproject.setter
    def oproject(self, val):
        self._oproject = val
        try:
            self._project_name = self._oproject.GetName()
        except AttributeError:  # pragma: no cover
            self._project_name = ""

    @odesign.setter
    def odesign(self, val):
        self._odesign = val
        try:
            self._design_name = self._odesign.GetName()
        except AttributeError:  # pragma: no cover
            self._design_name = ""

    @property
    def design_name(self):
        """Name of current logger design.

        Returns
        -------
        str
        """
        return self._design_name

    @property
    def project_name(self):
        """Name of current logger project.

        Returns
        -------
        str
        """
        return self._project_name

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
            self._project.setLevel(level)
            self._project.addFilter(AppFilter("Project", project_name))
            if self._files_handlers:
                for handler in self._files_handlers:
                    self._project.addHandler(handler)
            if self._std_out_handler is not None:
                self._project.addHandler(self._std_out_handler)
            return self._project
        elif destination == "Design":
            project_name = self.project_name
            design_name = self.design_name
            self._design = logging.getLogger(project_name + ":" + design_name)
            self._design.setLevel(level)
            self._design.addFilter(AppFilter("Design", design_name))
            if self._files_handlers:
                for handler in self._files_handlers:
                    self._design.addHandler(handler)
            if self._std_out_handler is not None:
                self._design.addHandler(self._std_out_handler)
            self._design.parent = None
            return self._design
        else:
            raise ValueError("The destination must be either 'Project' or 'Design'.")

    def disable_desktop_log(self):
        """Disable the log in AEDT."""
        self._log_on_desktop = False
        self.info("Log on AEDT is disabled.")

    def enable_desktop_log(self):
        """Enable the log in AEDT."""
        self._log_on_desktop = True
        self.info("Log on AEDT is enabled.")

    def disable_stdout_log(self):
        """Disable printing log messages to stdout."""
        self._log_on_screen = False
        self._global.removeHandler(self._std_out_handler)
        self.info("Log on console is disabled.")

    def enable_stdout_log(self):
        """Enable printing log messages to stdout."""
        self._log_on_screen = True
        if not self._std_out_handler:
            self._std_out_handler = logging.StreamHandler(sys.stdout)
            self._std_out_handler.setLevel(self.level)
            _logger_stdout_formatter = logging.Formatter("pyaedt %(levelname)s: %(message)s")

            self._std_out_handler.setFormatter(_logger_stdout_formatter)
            self._global.addHandler(self._std_out_handler)
        self._global.addHandler(self._std_out_handler)
        self.info("Log on console is enabled.")

    def disable_log_on_file(self):
        """Disable writing log messages to an output file."""
        from logging import FileHandler

        self._log_on_file = False
        for _file_handler in self._global.handlers:
            if isinstance(_file_handler, FileHandler):
                _file_handler.close()
                self._global.removeHandler(_file_handler)
        for _file_handler in self.design_logger.handlers:
            if isinstance(_file_handler, FileHandler):
                _file_handler.close()
                self.design_logger.removeHandler(_file_handler)
        for _file_handler in self.project_logger.handlers:
            if isinstance(_file_handler, FileHandler):
                _file_handler.close()
                self.project_logger.removeHandler(_file_handler)
        self.info("Log on file is disabled.")

    def enable_log_on_file(self):
        """Enable writing log messages to an output file."""
        self._log_on_file = True
        for _file_handler in self._files_handlers:
            self._global.addHandler(_file_handler)
            if "baseFilename" in dir(_file_handler):
                self.info(f"Log on file {_file_handler.baseFilename} is enabled.")

    def info(self, msg, *args, **kwargs):
        """Write an info message to the global logger."""
        if not settings.enable_logger:
            return
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        self._log_on_dekstop(0, msg1, "Global")
        return self._log_on_handler(0, msg, *args, **kwargs)

    def info_timer(self, msg, start_time=None, *args, **kwargs):
        """Write an info message to the global logger with elapsed time.
        Message will have an appendix of type Elapsed time: time.
        """
        if not settings.enable_logger:
            return
        if not start_time:
            start_time = self._timer
        td = time.time() - start_time
        m, s = divmod(td, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d > 0:
            msg += f" Elapsed time: {round(d)}days {round(h)}h {round(m)}m {round(s)}sec"
        elif h > 0:
            msg += f" Elapsed time: {round(h)}h {round(m)}m {round(s)}sec"
        else:
            msg += f" Elapsed time: {round(m)}m {round(s)}sec"
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        self._log_on_dekstop(0, msg1, "Global")
        return self._log_on_handler(0, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Write a warning message to the global logger."""
        if not settings.enable_logger:
            return
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        self._log_on_dekstop(1, msg1, "Global")
        return self._log_on_handler(1, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Write an error message to the global logger."""
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        self._log_on_dekstop(2, msg1, "Global")
        return self._log_on_handler(2, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Write a debug message to the global logger."""
        if not (settings.enable_debug_logger or settings.enable_debug_grpc_api_logger) or not settings.enable_logger:
            return
        if args:
            try:
                msg1 = msg % tuple(str(i) for i in args)
            except TypeError:
                msg1 = msg
        else:
            msg1 = msg
        if not settings.enable_debug_grpc_api_logger:
            self._log_on_dekstop(0, msg1, "Global")
        return self._log_on_handler(3, msg, *args, **kwargs)

    @property
    def glb(self):
        """Global logger."""
        self._global = logging.getLogger("Global")
        return self._global

    @property
    def project_logger(self):
        """Project logger."""
        self._project = logging.getLogger(self.project_name)
        if not self._project.handlers:
            self.add_logger("Project")
        return self._project

    @property
    def design_logger(self):
        """Design logger."""
        self._design = logging.getLogger(self.project_name + ":" + self.design_name)
        if not self._design.handlers:
            self.add_logger("Design")
        return self._design


pyaedt_logger = AedtLogger(to_stdout=settings.enable_screen_logs)
