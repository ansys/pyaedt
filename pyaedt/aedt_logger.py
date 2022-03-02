import logging
import sys

from pyaedt import log_handler
from pyaedt import settings
from pyaedt.application.MessageManager import AEDTMessageManager


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

        self._messenger = AEDTMessageManager()
        self._global = logging.getLogger("Global")
        self._file_handler = None
        self._std_out_handler = None
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
            self._global.addHandler(log_handler.LogHandler(self._messenger, "Global", logging.DEBUG))
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
    def messages(self):
        """List of messages."""
        return self._messenger.messages

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
            project_name = self._messenger._project_name
            self._project = logging.getLogger(project_name)
            self._project.addHandler(log_handler.LogHandler(self._messenger, "Project", level))
            self._project.setLevel(level)
            self._project.addFilter(AppFilter("Project", project_name))
            if self._file_handler is not None:
                self._project.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._project.addHandler(self._std_out_handler)
            return self._project
        elif destination == "Design":
            project_name = self._messenger._project_name
            design_name = self._messenger._design_name
            self._design = logging.getLogger(project_name + ":" + design_name)
            self._design.addHandler(log_handler.LogHandler(self._messenger, "Design", level))
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
        self._messenger._log_on_desktop = False

    def enable_desktop_log(self):
        """Enable the log in AEDT."""
        self._messenger._log_on_desktop = True

    def disable_stdout_log(self):
        """Disable printing log messages to stdout."""
        self._messenger._log_on_screen = False
        self._global.removeHandler(self._std_out_handler)

    def enable_stdout_log(self):
        """Enable printing log messages to stdout."""
        self._messenger._log_on_screen = True

    def disable_log_on_file(self):
        """Disable writing log messages to an output file."""
        self._messenger._log_on_file = False
        self._file_handler.close()
        self._global.removeHandler(self._file_handler)

    def enable_log_on_file(self):
        """Enable writing log messages to an output file."""
        self._messenger._log_on_file = True
        self._file_handler = logging.FileHandler(self.filename)
        self._file_handler.setLevel(self.level)
        self._file_handler.setFormatter(self.formatter)
        self._global.addHandler(self._file_handler)

    def get_messages(self):
        """Get messages for the current design of the current project."""
        return self._messenger.get_messages(self._messenger._project_name, self._messenger._design_name)

    def clear_messages(self, project_name=None, design_name=None, level=2):
        """
        Clear messages in the design, project, or global logger or in any or all of these loggers.

        Parameters
        ----------
        project_name : str, optional
           Name of the project. The default is ``None``, in which case the active
           project is used.
        design_name : str, optional
           Name of the desigh. The default is ``None``, in which case the active
           design is used.
        level : int, optional
           The default is ``2.``.
        """
        self._messenger.clear_messages(project_name, design_name, level)

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
        self._project = logging.getLogger(self._messenger._project_name)
        if not self._project.handlers:
            self.add_logger("Project")
        return self._project

    @property
    def design(self):
        """Design logger."""
        self._design = logging.getLogger(self._messenger._project_name + ":" + self._messenger._design_name)
        if not self._design.handlers:
            self.add_logger("Design")
        return self._design
