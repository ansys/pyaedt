import logging
import weakref

from .import log_handler


class AedtLogger():

    def __init__(self, messenger, level=logging.DEBUG, filename=None, to_stdout=False):

        """ no env var here..."""

        #self._desktop = weakref.ref(desktop)
        self._messenger = messenger
        self._global = logging.getLogger('global')
        self._global.addHandler(log_handler._LogHandler(self._messenger, 'Global', level))
        self._global.setLevel(level)

        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)-8s:%(message)s', datefmt='%Y/%m/%d %H.%M.%S')

        self._file_handler = None
        if filename:
            self._file_handler = logging.FileHandler(filename)
            self._file_handler.setLevel(level)
            self._file_handler.setFormatter(formatter)
            self._global.addHandler(self._file_handler)

        self._std_out_handler = None
        if to_stdout:
            self._std_out_handler = logging.StreamHandler()
            self._std_out_handler.setLevel(level)
            self._std_out_handler.setFormatter(formatter)
            self._global.addHandler(self._std_out_handler)

    def add_logger(self, destination, level=logging.DEBUG):
        """Add logger for either an active project or an active design."""
        if destination == 'Project':
            self._project = logging.getLogger(self._messenger._project_name)
            self._project.addHandler(log_handler._LogHandler(self._messenger, 'Project', level))
            self._project.setLevel(level)
            if self._file_handler is not None:
                self._project.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._project.addHandler(self._std_out_handler)
        elif destination == 'Design':
            self._design = logging.getLogger(self._messenger._design_name)
            self._design.addHandler(log_handler._LogHandler(self._messenger, 'Design', level))
            self._design.setLevel(level)
            if self._file_handler is not None:
                self._design.addHandler(self._file_handler)
            if self._std_out_handler is not None:
                self._design.addHandler(self._std_out_handler)
        else:
            raise ValueError("The destination must be either 'Project' or 'Design'.")

    def get_messages(self):
        self._messenger.get_messages(self, project_name=None, design_name=None)

    def clear_messages(self):
        self._messenger.clear_messages(self, project_name=None, design_name=None, level=2)

    @property
    def global_logger(self):
        """Global logger."""
        return self._global

    @property
    def project_logger(self):
        """Global logger."""
        return self._project

    @property
    def design_logger(self):
        """Global logger."""
        return self._design