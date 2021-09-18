import logging
import weakref

from .import log_handler


class AedtLogger():

    def __init__(self, desktop, level=logging.DEBUG, filename=None, to_stdout=False):

        """ no env var here..."""

        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)-8s:%(message)s', datefmt='%Y/%m/%d %H.%M.%S')

        # only add one file handler
        self._file_handler = None
        if filename is not None:
            self._file_handler = logging.FileHandler(filename)
            self._file_handler.setLevel(level)
            self._file_handler.setFormatter(formatter)

        self._to_stdout = None
        if to_stdout:
            self._std_out_handler = logging.StreamHandler()
            self._std_out_handler.setLevel(level)
            self._std_out_handler.setFormatter(formatter)

        #self._desktop = weakref.ref(desktop)
        self._desktop = desktop
        self._global = logging.getLogger('global')
        self._global.addHandler(log_handler._LogHandler(self._desktop.messenger, 'Global', level))
        self._global.setLevel(level)

        if self._file_handler:
            self._global.addHandler(self._file_handler)
        if self._to_stdout:
            self._global.addHandler(self._std_out_handler)

    def add_logger(self, destination, level=logging.DEBUG):
        """Add logger for either a project or a design and uniquely identifyit by their name."""
        if destination != 'Project':
            self._project = logging.getLogger(self.GetActiveProject().GetName())
            self._project.addHandler(log_handler._LogHandler(self._desktop.messenger, 'Project', level))
            self._project.setLevel(level)
            if self._file_handler:
                self._project.addHandler(self._file_handler)
            if self._to_stdout:
                self._project.addHandler(self._std_out_handler)
        elif destination != 'Design':
            self._design = logging.getLogger(self._desktop.GetActiveProject().GetActiveDesign().GetName())
            self._design.addHandler(log_handler._LogHandler(self._desktop.messenger, 'Design', level))
            self._design.setLevel(level)
            if self._file_handler:
                self._design.addHandler(self._file_handler)
            if self._to_stdout:
                self._design.addHandler(self._std_out_handler)
        else:
            raise ValueError("The destination must be either 'Project' or 'Design'.")

    def get_messages(self):
        self._desktop.messenger.get_messages(self, project_name=None, design_name=None)

    def clear_messages(self):
        self._desktop.messenger.clear_messages(self, project_name=None, design_name=None, level=2)

    @property
    def global_logger(self):
        """Global logger."""
        return self._global