"""
This module contains the ``AEDTMessageManager`` class.

This module provides all functionalities for logging errors and messages
in both AEDT and the log file.
"""
import logging
import sys

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
        List of messages extracted from AEDT by the :class:`AEDTMessageManager` class.
    project_name : str
        Name of the project. The default is the active project.
    design_name : str
        Name of the design within the specified project. The default is the active design.


    Attributes
    ----------
    global_level : list of str
        List of strings representing the message content at the global level of the message manager

    project_level : list of str
        List of strings representing the message content of the specifiec project

    design_level : list of str
        List of strings representing the message content for the specified design within the specified project

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


class AEDTMessageManager(object):
    """
    Manages AEDT messaging to both the logger and the AEDT message manager.

    Parameters
    ----------
    parent :
        The default is ``None``.

    Attributes
    ----------
    messages : list
       List of messages.

    Methods
    -------
    add_error message
    add_warning_message
    add_info_message
    add debug_message (deprecated)
    add message
    get_design_messages
    clear_messages

    Examples
    --------
    Log the three types of messages.

    >>> from pyaedt.hfss import Hfss
    >>> hfss = Hfss()
    >>> hfss.logger.design.info("This is an info message on a design", "Design")
    >>> hfss.logger.warning("This is a global warning message", "Global")
    >>> hfss.logger.project.error("This is a project error message", "Project")

    """

    def __init__(self, app=None):
        self._app = app

    @property
    def _desktop(self):
        if self._app:
            return self._app._desktop  # pragma: no cover
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
        """Aedt Logger object."""
        if self._log_on_file:
            try:
                return logging.getLogger(__name__)
            except:
                return None
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

    def get_messages(self, project_name, design_name):
        """
        Retrieve the message manager content for a specified project and design.

        If the specified project and design names are invalid, they are ignored.

        Parameters
        ----------
        project_name : str
            Name of the project.
        design_name : str
            Name of the design within the specified project.

        Returns
        -------
        list of str
            List of messages for the specified project and design.

        """
        if self._log_on_desktop:
            global_message_data = self._desktop.GetMessages("", "", 0)
            message_data = MessageList(global_message_data, project_name, design_name)
            return message_data
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

    def add_debug_message(self, type, message_text):
        """
        Parameterized message to the message manager to specify the type and project or design level.

        Parameters
        ----------
        type : int
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
            if type == 0 and self.logger:
                self.logger.debug(message_text)
            elif type == 1 and self.logger:
                self.logger.warning(message_text)
            elif type == 2 and self.logger:
                self.logger.error(message_text)

    def add_message(self, type, message_text, level=None, proj_name=None, des_name=None):
        """
        Pass a parameterized message to the message manager to specify the type and project or design level.

        Parameters
        ----------
        type : int
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
                self._desktop.AddMessage(proj_name, des_name, type, message_text)
            except:
                print("pyaedt info: Failed in Adding Desktop Message")

        if len(message_text) > 250:
            message_text = message_text[:250] + "..."

        # Print to stdout and to logger
        if self._log_on_screen:
            if type == 0:
                print("pyaedt info: {}".format(message_text))
            elif type == 1:
                print("pyaedt warning: {}".format(message_text))
            elif type == 2:
                print("pyaedt error: {}".format(message_text))
        if self._log_on_file:
            if type == 0 and self.logger:
                self.logger.debug(message_text)
            elif type == 1 and self.logger:
                self.logger.warning(message_text)
            elif type == 2 and self.logger:
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
