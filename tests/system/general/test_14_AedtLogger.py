# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
import logging
import os
import shutil
import sys
import tempfile
import unittest.mock

from ansys.aedt.core.aedt_logger import AedtLogger
from ansys.aedt.core.generic.settings import settings
import pytest

from tests.system.general.conftest import config

settings.enable_desktop_logs = True

desktop_version = config["desktopVersion"]


@pytest.fixture(scope="class")
def aedtapp(add_app):
    settings.enable_local_log_file = True
    app = add_app(project_name="Test_14")
    yield app
    settings.enable_local_log_file = False


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_01_formatter(self):
        settings.formatter = logging.Formatter(
            fmt="%(asctime)s (%(levelname)s) %(message)s", datefmt="%d.%m.%Y %H:%M:%S"
        )
        path = os.path.join(self.local_scratch.path, "test01.txt")
        logger = AedtLogger(filename=path)
        assert logger.formatter == settings.formatter
        settings.formatter = None
        logger.disable_log_on_file()

        for handler in [i for i in logger._global.handlers]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger._global.removeHandler(handler)
        logger.enable_log_on_file()

    def test_02_output_file_with_app_filter(self):
        settings.enable_debug_logger = True
        content = None
        temp_dir = tempfile.gettempdir()
        path = os.path.join(self.local_scratch.path, "test02.txt")
        logger = AedtLogger(filename=path)
        logger.info("Info for Global")

        logger.debug("Debug for Global")
        logger.warning("Warning for Global")
        logger.error("Error for Global")
        project_logger = logger.add_logger("Project")
        project_logger.info("Info for Project")
        project_logger.debug("Debug for Project")
        project_logger.warning("Warning for Project")
        project_logger.error("Error for Project")
        design_logger = logger.add_logger("Design")
        design_logger.info("Info for Design")
        design_logger.debug("Debug for Design")
        design_logger.warning("Warning for Design")
        design_logger.error("Error for Design")
        logger.info_timer("Info with message")
        logger.reset_timer()
        settings.enable_debug_logger = False

        # Close every handlers to make sure that the
        # file handler on every logger has been released properly.
        # Otherwise, we can't read the content of the log file.

        # delete the global file handler but not the log handler because
        # it is used to write some info messages when closing AEDT.
        logger.disable_log_on_file()

        for handler in project_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                project_logger.removeHandler(handler)

        for handler in design_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                design_logger.removeHandler(handler)

        with open(path, "r") as f:
            content = f.readlines()
        content.remove(content[0])
        assert ":Global:INFO    :Info for Global" in content[0]
        assert ":Global:DEBUG   :Debug for Global" in content[1]
        assert ":Global:WARNING :Warning for Global" in content[2]
        assert ":Global:ERROR   :Error for Global" in content[3]
        assert ":INFO    :Info for Project" in content[4]
        assert ":DEBUG   :Debug for Project" in content[5]
        assert ":WARNING :Warning for Project" in content[6]
        assert ":ERROR   :Error for Project" in content[7]
        assert ":INFO    :Info for Design" in content[8]
        assert ":DEBUG   :Debug for Design" in content[9]
        assert ":WARNING :Warning for Design" in content[10]
        assert ":ERROR   :Error for Design" in content[11]
        assert "Elapsed time:" in content[12]

        shutil.rmtree(path, ignore_errors=True)

    def test_03_stdout_with_app_filter(self):
        capture = CaptureStdOut()
        settings.logger_file_path = ""
        with capture:
            logger = AedtLogger(to_stdout=True)
            logger.info("Info for Global")
            logger.warning("Warning for Global")
            logger.error("Error for Global")

        assert "PyAEDT INFO: Info for Global" in capture.content
        assert "PyAEDT WARNING: Warning for Global" in capture.content
        assert "PyAEDT ERROR: Error for Global" in capture.content

    def test_04_disable_output_file_handler(self):
        content = None
        temp_dir = tempfile.gettempdir()
        path = os.path.join(self.local_scratch.path, "test04.txt")
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        logger = AedtLogger(filename=path)
        logger.info("Info for Global before disabling the log file handler.")
        project_logger = logger.add_logger("Project")
        project_logger.info("Info for Project before disabling the log file handler.")
        design_logger = logger.add_logger("Design")
        design_logger.info("Info for Design before disabling the log file handler.")

        with open(path, "r") as f:
            content = f.readlines()
        content.remove(content[0])

        assert ":Global:INFO    :Info for Global" in content[0]
        assert ":INFO    :Info for Project before disabling the log file handler." in content[1]
        assert ":INFO    :Info for Design before disabling the log file handler." in content[2]

        # Disable log on file.
        logger.disable_log_on_file()
        logger.info("Info for Global after disabling the log file handler.")
        project_logger.info("Info for Project after disabling the log file handler.")
        design_logger.info("Info for Design after disabling the log file handler.")

        with open(path, "r") as f:
            content = f.readlines()

        disablement_succeeded = True
        for i in range(len(content)):
            if "Info for Global after disabling the log file handler." in content[i]:
                disablement_succeeded = False
        assert disablement_succeeded

        # Enable log on file.
        logger.enable_log_on_file()
        logger.info("Info for Global after re-enabling the log file handler.")

        with open(path, "r") as f:
            content = f.readlines()

        enablement_succeeded = False
        for i in range(len(content)):
            if "Info for Global after re-enabling the log file handler." in content[i]:
                enablement_succeeded = True
        assert enablement_succeeded

        # Close every handlers to make sure that the
        # file handler on every logger has been released properly.
        # Otherwise, we can't read the content of the log file.
        logger.disable_log_on_file()

        for handler in project_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                project_logger.removeHandler(handler)

        for handler in design_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                design_logger.removeHandler(handler)

        shutil.rmtree(path, ignore_errors=True)
        settings.logger_file_path = ""

    def test_05_disable_stdout(self):
        with tempfile.TemporaryFile("w+") as fp:
            stream = unittest.mock.MagicMock()
            stream.write = unittest.mock.MagicMock()

            stream.write.side_effect = fp.write
            sys.stdout = stream

            logger = AedtLogger(to_stdout=True)
            logger.info("Info for Global")
            logger.disable_stdout_log()
            logger.info("Info after disabling the stdout handler.")
            logger.enable_stdout_log()
            logger.info("Info after re-enabling the stdout handler.")

            sys.stdout = sys.__stdout__

            stream.write.assert_any_call("PyAEDT INFO: Info for Global\n")
            stream.write.assert_any_call("PyAEDT INFO: Info after re-enabling the stdout handler.\n")

            with pytest.raises(AssertionError) as e_info:
                stream.write.assert_any_call("PyAEDT INFO: Info after disabling the stdout handler.")
            fp.seek(0)
            stream_content = fp.readlines()
        for handler in logger._global.handlers[:]:
            if "MagicMock" in str(handler) or "StreamHandler (DEBUG)" in str(handler):
                handler.close()
                logger._global.removeHandler(handler)
        assert stream_content[0] == "PyAEDT INFO: Info for Global\n"
        assert stream_content[1] == "PyAEDT INFO: Log on console is enabled.\n"
        assert stream_content[2] == "PyAEDT INFO: Info after re-enabling the stdout handler.\n"


class TestLogMessages:
    """Class used to test log messages."""

    def test_log_when_accessing_non_existing_object(self, caplog):
        """Check that accessing a non-existent object logs an error message."""
        from ansys.aedt.core import Hfss

        app = Hfss(
            project="log_project",
            design="log_design",
            version=desktop_version,
            new_desktop=True,
        )
        with pytest.raises(AttributeError):
            app.get_object_material_properties("MS1", "conductivity")
        assert ("Global", logging.ERROR, "    assignment = MS1 ") in caplog.record_tuples


class CaptureStdOut:
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
