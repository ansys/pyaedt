# Setup paths for module imports
import tempfile
import os
import io
import sys
from pyaedt.generic import ibs_reader
try:
    import pytest
    import unittest.mock
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

from pyaedt.generic.general_methods import is_ironpython
# Import required modules
from pyaedt.aedt_logger import AedtLogger
from pyaedt import Hfss

class TestClass:
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    def test_01_read_ibis_file(self):
        ibs_reader.read_project(os.path.join(os.getcwd(), "example_models", "u26a_800_modified.ibs" ))


class CaptureStdOut():
    """Capture standard output with a context manager."""

    def __init__(self):
        self._stream = io.StringIO()

    def __enter__(self):
        sys.stdout = self._stream

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__

    def release(self):
        self._stream.close()

    @property
    def content(self):
        """Return the captured content."""
        return self._stream.getvalue()
