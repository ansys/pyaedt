import logging

from .import log_handler

FORMATTER = logging.Formatter(
        "%(asctime)s:%(name)s:%(dest):%(extra):%(levelname)-8s:%(message)s",
        datefmt='%Y/%m/%d %H.%M.%S')

# def make_formatter(destination):
#     """Create an AEDT specific formatter that include destination.
    
#     Parameters
#     ----------
#     destination : str
#     """

#     return logging.Formatter(
#         "%(asctime)s:%(name)s:" + destination + ":%(levelname)-8s:%(message)s",
#         datefmt='%Y/%m/%d %H.%M.%S')

class AppFilter(logging.Filter):

    def __init__(self, dest='global', extra=''):
        self._dest = dest
        self._extra = extra

    def filter(self, record):
        record.dest = self._dest
        record.extra = self._extra
        return True

class AedtLogger():

    def __init__(self, messenger, level=logging.DEBUG, filename=None, to_stdout=False):

        """ no env var here..."""

        self._messenger = messenger
        self._global = logging.getLogger('global')
        self._file_handler = None
        self._std_out_handler = None

        #3 app filter
        # ap filter class must redirect to the handler

        if not self._global.handlers:
            self._global.addHandler(log_handler._LogHandler(self._messenger, 'Global', level))
            self._global.setLevel(level)
            self._global.setFormatter(FORMATTER)
            self._global.addFilter(AppFilter())


            if filename:
                self._file_handler = logging.FileHandler(filename)
                self._file_handler.setLevel(level)
                self._file_handler.setFormatter(FORMATTER)
                self._global.addHandler(self._file_handler)

            if to_stdout:
                self._std_out_handler = logging.StreamHandler()
                self._std_out_handler.setLevel(level)
                self._std_out_handler.setFormatter(FORMATTER)
                self._global.addHandler(self._std_out_handler)

    def add_logger(self, destination, level=logging.DEBUG):
        """Add logger for either an active project or an active design."""
        if destination == 'Project':
            project_name = self._messenger._project_name
            self._project = logging.getLogger(project_name)
            self._project.addHandler(log_handler._LogHandler(self._messenger, 'Project', level))
            self._project.setLevel(level)
            self._project.setFormatter(FORMATTER)
            self._project.addFilter(AppFilter('Project', project_name))
            if self._file_handler is not None:
                self._project.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._project.addHandler(self._std_out_handler)
        elif destination == 'Design':
            design_name = self._messenger._design_name
            self._design = logging.getLogger(design_name)
            self._design.addHandler(log_handler._LogHandler(self._messenger, 'Design', level))
            self._design.setLevel(level)
            self._design.setFormatter(FORMATTER)
            self._design.addFilter(AppFilter('Design', design_name))
            if self._file_handler is not None:
                self._design.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._design.addHandler(self._std_out_handler)
        else:
            raise ValueError("The destination must be either 'Project' or 'Design'.")

    def get_messages(self):
        return self._messenger.get_messages(self._messenger._project_name, self._messenger._design_name)

    def clear_messages(self, project_name=None, design_name=None, level=2):
        self._messenger.clear_messages(project_name, design_name, level)

    @property
    def glb(self):
        """Global logger."""
        return self._global

    @property
    def project(self):
        """Global logger."""
        return self._project

    @property
    def design(self):
        """Global logger."""
        self._design = logging.getLogger(self._messenger._design_name)
        if not self._design.hasHandlers:
            self._design.addHandler(log_handler._LogHandler(self._messenger, 'Design', level))
            self._design.setLevel(level)
            if self._file_handler is not None:
                self._design.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._design.addHandler(self._std_out_handler)
        return self._design
