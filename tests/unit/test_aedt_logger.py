# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
import sys
import tempfile
import unittest.mock

import pytest

from ansys.aedt.core.aedt_logger import AedtLogger
from ansys.aedt.core.generic.settings import settings

settings.enable_desktop_logs = True
settings.enable_local_log_file = True


def test_formatter(test_tmp_dir):
    settings.formatter = logging.Formatter(fmt="%(asctime)s (%(levelname)s) %(message)s", datefmt="%d.%m.%Y %H:%M:%S")
    path = test_tmp_dir / "test01.txt"
    logger = AedtLogger(filename=str(path))
    assert logger.formatter == settings.formatter
    settings.formatter = None
    logger.disable_log_on_file()
    path.unlink(missing_ok=True)


def test_output_file_with_app_filter(test_tmp_dir):
    settings.enable_debug_logger = True
    path = test_tmp_dir / "test02.txt"
    logger = AedtLogger(filename=str(path))
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
    path.unlink(missing_ok=True)


def test_stdout_with_app_filter():
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


def test_disable_output_file_handler(test_tmp_dir):
    tempfile.gettempdir()
    path = test_tmp_dir / "test04.txt"

    if path.is_file():
        path.unlink(missing_ok=True)

    logger = AedtLogger(filename=str(path))
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
    for _, line in enumerate(content):
        if "Info for Global after disabling the log file handler." in line:
            disablement_succeeded = False
    assert disablement_succeeded

    # Enable log on file.
    logger.enable_log_on_file()
    logger.info("Info for Global after re-enabling the log file handler.")

    with open(path, "r") as f:
        content = f.readlines()

    enablement_succeeded = False
    for _, line in enumerate(content):
        if "Info for Global after re-enabling the log file handler." in line:
            enablement_succeeded = True
    assert enablement_succeeded

    # Close every handlers to make sure that the
    # file handler on every logger has been released properly.
    # Otherwise, we can't read the content of the log file.
    logger.disable_log_on_file()

    path.unlink(missing_ok=True)


def test_disable_stdout(test_tmp_dir):
    temp_file = test_tmp_dir / "dummy.tmp"
    with temp_file.open("w+") as fp:
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

        with pytest.raises(AssertionError):
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

    # Close every handlers to make sure that the
    # file handler on every logger has been released properly.
    # Otherwise, we can't read the content of the log file.
    logger.disable_log_on_file()


class CaptureStdOut:
    """Capture standard output with a context manager."""

    def __init__(self):
        self._stream = io.StringIO()

    def __enter__(self):
        sys.stdout = self._stream

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.stdout = sys.__stdout__

    def release(self):
        self._stream.close()

    @property
    def content(self):
        """Return the captured content."""
        return self._stream.getvalue()
