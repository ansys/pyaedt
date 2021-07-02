"""
Message Manager Library Module
------------------------------

Description
===========
This class contains all the functionalities to log error and messages
both in AEDT and in log file.

Examples
--------
Log the three types of messages

>>> from pyaedt.hfss import Hfss
>>> hfss = Hfss()
>>> hfss._messenger.add_info_message("This is an info Message on Design", "Design")
>>> hfss._messenger.add_warning_message("This is a global warning Message", "Global")
>>> hfss._messenger.add_error_message("This is a Project Error Message", "Project")


"""

import sys
import logging
import os
from ..generic.general_methods import aedt_exception_handler, generate_unique_name
message_levels = {'Global': 0,
                  'Project': 1,
                  'Design': 2}

class Msg():
    (INFO, WARNING, ERROR, FATAL) = range(4)


class MessageList:
    """Data structure to collect and return message information from the AEDT Message Manager for a specified
       project name and design name

    Parameters
    ---------
    msg_list : list of str
        list of messages extracted by the AEDTMessenger class from the Desktop

    project_name : str, default=active project name
        Specified project within the AEDT Desktop
    design_name : str, default=active design name
        Specified design within the specified project


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
            loc = line.find('[')
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
    """Class that manages AEDT Messaging to the logger file and to the AEDT Message UI

    Attributes
    ----------
    messages : MessageList

    Methods
    -------
    add_error message
    add_warning_message
    add_info_message
    add debug_message (deprecated)
    add message
    get_design_messages
    clear_messages

    """
    def __init__(self, parent=None, loadondesktop=True, loadonlog=True):
        self._parent = parent
        if not parent:
            self.MainModule = sys.modules['__main__']
            self._desktop = self.MainModule.oDesktop
        else:
            self._desktop = self._parent._desktop

        self.loadondesktop = loadondesktop
        if loadonlog:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None

    @property
    def messages(self):
        """Return the AEDT Message Manager Contents for the active project and design

        Returns
        -------
        MessageList
        """
        return self.get_messages(self._project_name, self._design_name)

    @aedt_exception_handler
    def get_messages(self, project_name, design_name):
        """Return the AEDT Message Manager Contents for a specified project and design

        If the design- or project names are invalid, they will be ignored

        Returns
        -------
        MessageList

        """
        global_message_data = self._desktop.GetMessages("", "", 0)
        message_data = MessageList(global_message_data, project_name, design_name)
        return message_data

    @aedt_exception_handler
    def add_error_message(self, message_text, level=None):
        """Add a type 2 "Error" message to the message manager tree.

        Add an error message to the logger if the handler is present.

        Parameters
        ----------
        message_text :
            message to show
        level : str, default="Design"
            message level. Must be "Global", "Project" or "Design"

        Examples
        --------
        Add an error message to the desktop message manager

        >>> hfss._messenger.add_error_message("Project Error Message", "Project")

        """
        self.add_message(2, message_text, level)

    @aedt_exception_handler
    def add_warning_message(self, message_text, level=None):
        """Add a type 1 "Warning" message to the message manager tree.
        Add a warning message to the logger if the handler is present

        Parameters
        ----------
        message_text :
            message to show
        level : str, default="Design"
            message level. Must be "Global", "Project" or "Design"

        Examples
        --------
        Add a warning message to the desktop message manager

        >>> hfss._messenger.add_warning_message("Project warning message")

        """
        self.add_message(1, message_text, level)

    @aedt_exception_handler
    def add_info_message(self, message_text, level=None):
        """Add a type 0 "Info" message to the active design level of the message manager tree

        Add an info message to the logger if the handler is present

        Parameters
        ----------
        message_text : str
            Message to show
        level : str, default="Design"
            message level. Must be "Global", "Project" or "Design"

        Examples
        --------
        Add a info message at the global level.

        >>> hfss._messenger.add_info_message("Global warning message", "Global")

        """
        self.add_message(0, message_text, level)

    @aedt_exception_handler
    def add_debug_message(self, message_text, level=None):
        """
        .. deprecated use add_info_message
        """
        self.add_info_message(message_text, level)

    @aedt_exception_handler
    def add_message(self, type, message_text, level=None, proj_name=None, des_name=None):
        """Pass a parameterized message to the AEDT message manager allowing specification of type and project/design level.

        Parameters
        ----------
        type : int
            Message types:

            * 0: info
            * 1: Warning
            * 2: Error

        message_text : str
            Message to show.
        level : str, default="Design"
            message level. Must be "Global", "Project" or "Design"
        proj_name : str, optional
            Project name.
        des_name : str, optional
            Design name.

        """
        if not proj_name:
            proj_name = ""

        if not des_name:
            des_name = ""

        if not level:
            level = 'Design'

        assert level in message_levels, "Message level must be 'Design', 'Project', or 'Global'"

        if self.loadondesktop:
            if not proj_name and message_levels[level] > 0:
                proj_name = self._project_name
            if not des_name and message_levels[level] > 1:
                des_name = self._design_name
            if des_name and ";" in des_name:
                des_name = des_name[des_name.find(";")+1:]
            self._desktop.AddMessage(proj_name, des_name, type, message_text)

        if len(message_text) > 250:
            message_text = message_text[:250] + "..."

        # Print to stdout and to logger
        if type == 0:
            print("pyaedt Info: {}".format(message_text))
            self.logger.info(message_text)
        elif type == 1:
            print("pyaedt Warning: {}".format(message_text))
            self.logger.warning(message_text)
        elif type == 2:
            print("pyaedt Error: {}".format(message_text))
            self.logger.error(message_text)

    @aedt_exception_handler
    def clear_messages(self, proj_name=None, des_name=None, level=2):
        """Clear messages.

        Parameters
        ----------
        proj_name : str
            Name of project.  If blank, then all projects.  Defaults
            to current project.
        des_name : str
            Name of design If blank, then all designs.  Defaults
            to current project.
        level : int, optional
            Clear message level.  Default 2.

            * ``0`` : Clear all info messages
            * ``1`` : Clear all info and warning messages
            * ``2`` : Clear all info, warning and error messages
            * ``3`` : Clear all messages included info, warning,
              error, and fatal-error.

        Examples
        --------
        Clear all messages in the current design and project

        >>> hfss.clear_messages(level=3)

        """
        proj_name = self._project_name
        des_name = self._design_name
        self._desktop.ClearMessages(proj_name, des_name, level)

    @property
    def _oproject(self):
        return self._desktop.GetActiveProject()

    @property
    def _odesign(self):
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


class EDBMessageManager(object):
    """Class that manage EDB Messaging to the logger file"""

    def __init__(self, project_dir="C:\\Temp"):
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            logging.basicConfig(
                filename=os.path.join(project_dir, "EDBTLib.log"),
                level=logging.DEBUG,
                format='%(asctime)s:%(name)s:%(levelname)-8s:%(message)s',
                datefmt='%Y/%m/%d %H.%M.%S')
            self.logger = logging.getLogger(__name__)

    def add_error_message(self, message_text):
        """Add a type 2 "Error" message to the logger

        Parameters
        ----------
        message_text :
            message to show

        Returns
        -------

        """

        self.logger.error(message_text)

    def add_warning_message(self, message_text):
        """Add a "Warning" message to the logger

        Parameters
        ----------
        message_text :
            message to show

        Returns
        -------

        """
        self.logger.warning(message_text)

    def add_info_message(self, message_text):
        """Add an "Info" message to the logger

        Parameters
        ----------
        message_text :
            message to show

        Returns
        -------

        """
        self.logger.info(message_text)
