import logging

from .import log_handler


FORMATTER = logging.Formatter(
        "%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s",
        datefmt='%Y/%m/%d %H.%M.%S')

class AppFilter(logging.Filter):
    """This filter will be used to specify the destination of the log
    Global, project and design.

    Parameters
    ----------
    destination : str, optional
        Desktop exposes 3 different destinations: Global, project and design.
        The default is ``Global``.
    extra : str, optional
        Name of the design or project. The default is an empty string.
    """

    def __init__(self, destination='Global', extra=''):
        self._destination = destination
        self._extra = extra

    def filter(self, record):
        record.destination = self._destination

        # This will avoid to see '::' for Global that does not have any extra info.
        if not self._extra:
            record.extra = self._extra
        else:
            record.extra = self._extra + ":"
        return True


class AedtLogger():
    """Logger used for each Aedt logger.

    This class allows you to add handler to a file or standard output.

    Parameters
    ----------
    level : int, optional
        Logging level to filter the message severity allowed in the logger.
        The default is ``logging.DEBUG``.
    filename : str, optional
        Name of the file where log messages can be written to.
        The default is ``None``.
    to_stdout : bool, optional
        Write log message into the standard output. The default is ``False``.
    """

    def __init__(self, messenger, level=logging.DEBUG, filename=None, to_stdout=False):
        self._messenger = messenger
        self._Global = logging.getLogger('Global')
        self._file_handler = None
        self._std_out_handler = None

        if not self._Global.handlers:
            self._Global.addHandler(log_handler._LogHandler(self._messenger, 'Global', logging.DEBUG))
            self._Global.setLevel(level)
            self._Global.addFilter(AppFilter())

        if filename:
            self._file_handler = logging.FileHandler(filename)
            self._file_handler.setLevel(level)
            self._file_handler.setFormatter(FORMATTER)
            self._Global.addHandler(self._file_handler)

        if to_stdout:
            self._std_out_handler = logging.StreamHandler()
            self._std_out_handler.setLevel(level)
            self._std_out_handler.setFormatter(FORMATTER)
            self._Global.addHandler(self._std_out_handler)

    def add_logger(self, destination, level=logging.DEBUG):
        """Add a logger for either an active project or an active design."""
        if destination == 'Project':
            project_name = self._messenger._project_name
            self._project = logging.getLogger(project_name)
            self._project.addHandler(log_handler._LogHandler(self._messenger, 'Project', level))
            self._project.setLevel(level)
            #self._project.setFormatter(FORMATTER)
            self._project.addFilter(AppFilter('Project', project_name))
            if self._file_handler is not None:
                self._project.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._project.addHandler(self._std_out_handler)
            return self._project
        elif destination == 'Design':
            project_name = self._messenger._project_name
            design_name = self._messenger._design_name
            self._design = logging.getLogger(project_name + ":" + design_name)
            self._design.addHandler(log_handler._LogHandler(self._messenger, 'Design', level))
            self._design.setLevel(level)
            #self._design.setFormatter(FORMATTER)
            self._design.addFilter(AppFilter('Design', design_name))
            if self._file_handler is not None:
                self._design.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._design.addHandler(self._std_out_handler)
            return self._design
        else:
            raise ValueError("The destination must be either 'Project' or 'Design'.")

    def get_messages(self):
        """Get messages for the current design of the current project."""
        return self._messenger.get_messages(self._messenger._project_name, self._messenger._design_name)

    def clear_messages(self, project_name=None, design_name=None, level=2):
        """Clear messages for a design and/or a project and/or global."""
        self._messenger.clear_messages(project_name, design_name, level)

    @property
    def glb(self):
        """Global logger."""
        return self._Global

    @property
    def project(self):
        """Project logger."""
        return self._project

    @property
    def design(self):
        """Design logger."""
        self._design = logging.getLogger(self._messenger._design_name)
        if not self._design.hasHandlers:
            self._design.addHandler(log_handler._LogHandler(self._messenger, 'Design', level))
            self._design.setLevel(level)
            if self._file_handler is not None:
                self._design.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._design.addHandler(self._std_out_handler)
        return self._design
