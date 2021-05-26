"""
Message Manager Library Class
----------------------------------------------------------------

Disclaimer
==================================================

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**


Description
==================================================

This class contains all the functionalities to log error and messages both in AEDT and in log file

:Example:

hfss = HFSS()

hfss.messenger.add_info_message("This is an info Message on Design", "Design")

hfss.messenger.add_warning_message("This is a global warning Message", "Global")

hfss.messenger.add_error_message("This is a Project Error Message", "Project")


========================================================

"""

import sys
import logging
import os
from ..generic.general_methods import aedt_exception_handler, generate_unique_name
message_levels = {'Global': 0,
                  'Project': 1,
                  'Design': 2}


class AEDTMessageManager(object):
    """Class that manage AEDT Messaging to the logger file and to the AEDT Message UI"""
    @property
    def oproject(self):
        """ """
        if not self._parent:
            return self._desktop.GetActiveProject()
        else:
            return self._parent._oproject

    @property
    def odesign(self):
        """ """
        if not self._parent:
            return self.oproject.GetActiveDesign()
        else:
            return self._parent._odesign

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

    @aedt_exception_handler
    def design_name(self, level=None):
        """

        Parameters
        ----------
        level :
             (Default value = None)

        Returns
        -------

        """
        if not level:
            level = 'Design'
        if message_levels[level] > 1:
            try:
                return self.odesign.GetName()
            except:
                return ""
        else:
            return ""

    @aedt_exception_handler
    def project_name(self, level=None):
        """

        Parameters
        ----------
        level :
             (Default value = None)

        Returns
        -------

        """
        if not level:
            level = 'Design'
        if message_levels[level] > 0:
            try:
                return self.oproject.GetName()
            except:
                return ""
        else:
            return ""

    @aedt_exception_handler
    def add_error_message(self, message_text, level='Design'):
        """Add a type 2 "Error" message to the active design level of the message manager tree
            Add an error message to the logger if the handler is present

        Parameters
        ----------
        message_text :
            message to show
        level :
            message level. Default message level is 'Design'

        Returns
        -------

        """

        self.add_message(2, message_text, level)
        if self.logger:
            self.logger.error(message_text)

    @aedt_exception_handler
    def add_warning_message(self, message_text, level='Design'):
        """Add a type 1 "Warning" message to the active design level of the message manager tree
            Add a warning message to the logger if the handler is present

        Parameters
        ----------
        message_text :
            message to show
        level :
            message level. Default message level is 'Design'

        Returns
        -------

        """
        self.add_message(1, message_text, level)
        if self.logger:
            self.logger.warning(message_text)

    @aedt_exception_handler
    def add_info_message(self, message_text, level='Design'):
        """Add a type 0 "Info" message to the active design level of the message manager tree
            Add an info message to the logger if the handler is present

        Parameters
        ----------
        message_text :
            message to show
        level :
            message level. Default message level is 'Design'

        Returns
        -------

        """
        self.add_message(0, message_text, level)
        if self.logger:
            self.logger.info(message_text)

    @aedt_exception_handler
    def add_debug_message(self, message_text, level='Design'):
        """Add a type 0 "Info" message to the active design level of the message manager tree
            Add a debug message to the logger if the handler is present

        Parameters
        ----------
        message_text :
            message to show
        level :
            message level. Default message level is 'Design'

        Returns
        -------

        """
        self.add_message(0, message_text, level)
        if self.logger:
            self.logger.debug(message_text)

    @aedt_exception_handler
    def add_message(self, type, message_text, level=None, proj_name=None, des_name=None):
        """Passes a parametrizable message to the AEDT messag manger allowing specification of type and project/design level

        Parameters
        ----------
        type :
            Types: 0: info, 1: Warning, 2: Error
        message_text :
            message to show
        level :
            message level. Default message level is 'Design'
        proj_name :
            project name (Default value = None)
        des_name :
            design name (Default value = None)

        Returns
        -------

        """
        if self.loadondesktop:
            if not proj_name:
                proj_name = self.project_name(level)
            if not des_name:
                des_name = self.design_name(level)
            if des_name and ";" in des_name:
                des_name = des_name[des_name.find(";")+1:]
            self._desktop.AddMessage(proj_name, des_name, type, message_text)
        if len(message_text) > 250:
            message_text = message_text[:250] + "..."
        if type == 0:
            print("Info: {}".format(message_text))
        if type == 1:
            print("Warning: {}".format(message_text))
        if type == 2:
            print("Error: {}".format(message_text))

    @aedt_exception_handler
    def clear_messages(self, proj_name=None, des_name=None, level=2):
        """Optional Severity Levels
        0 -- clear all info messages;
        1 -- clear all info and warning messages;
        2 -- clear all info, warning and error messages;
        3 -- clear all messages included info, warning, error, and fatal-error.

        Parameters
        ----------
        proj_name :
            name of project (or blank string for all projects) (Default value = None)
        des_name :
            name of design (or blank string for all design) (Default value = None)
        level :
            severity level (Default value = 2)

        Returns
        -------

        """
        if proj_name is None:
            proj_name = self.oproject.GetName()

        if des_name is None:
            des_name = self.odesign.GetName()

        self._desktop.ClearMessages(proj_name, des_name, level)


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

