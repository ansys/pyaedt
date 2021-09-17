import datetime
import logging
import weakref
import os

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

        if to_stdout:
            self._std_out_handler = logging.StreamHandler()
            self._std_out_handler.setLevel(level)
            self._file_handler.setFormatter(formatter)

        #self._desktop = weakref.ref(desktop)
        self._desktop = desktop
        self._global = logging.getLogger('global')
        self._global.addHandler(log_handler._LogHandler(self._desktop.messenger, 'Global', level))
        self._global.setLevel(level)

        self._project = logging.getLogger(self._main.oDesktop.GetActiveProject().GetName())
        self._project.addHandler(log_handler._LogHandler(self._desktop.messenger, 'Project', level))
        self._project.setLevel(level)

        self._design = logging.getLogger(self._main.oDesktop.GetActiveProject().GetActiveDesign().GetName())
        self._design.addHandler(log_handler._LogHandler(self._desktop.messenger, 'Design', level))
        self._design.setLevel(level)

        if self._file_handler is not None:
            self._global.addHandler(self._file_handler)
            self._project.addHandler(self._file_handler)
            self._design.addHandler(self._file_handler)
        if to_stdout:
            self._global.addHandler(self._std_out_handler)
            self._project.addHandler(self._std_out_handler)
            self._design.addHandler(self._std_out_handler)

    @property
    def global_logger(self):
        """Global logger."""
        return self._global

    @property
    def project_logger(self):
        """Project logger."""
        return self._project

    @property
    def design_logger(self):
        """Design logger."""
        return self._design