# Setup paths for module imports
import tempfile
import os
import io
import logging
import shutil
import sys

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
        self.aedtapp = Hfss()
        pass

    def teardown_class(self):
        self.aedtapp.close_project(self.aedtapp.project_name, saveproject=False)
        shutil.rmtree(os.path.join(tempfile.gettempdir(), "log_testing"))
        pass

    # @pytest.mark.xfail
    # def test_01_global(self, clean_desktop_messages, clean_desktop, hfss):
    #     logger = hfss.logger
    #     # The default logger level is DEBUGGING.
    #     logger.debug("Global debug message for testing.")
    #     logger.info("Global info message for testing.")
    #     logger.warning("Global warning message for testing.")
    #     logger.error("Global error message for testing.")
    #     logger.info("Global critical message for testing.")

    #     # Project logger
    #     logger.add_logger("Project")
    #     logger.project.debug("Project debug message for testing.")
    #     logger.project.info("Project info message for testing.")
    #     logger.project.warning("Project warning message for testing.")
    #     logger.project.error("Project error message for testing.")
    #     logger.project.info("Project critical message for testing.")

    #     # Current active design logger
    #     logger.add_logger("Design")
    #     logger.design.debug("Design debug message for testing.")
    #     logger.design.info("Design info message for testing.")
    #     logger.design.warning("Design warning message for testing.")
    #     logger.design.error("Design error message for testing.")
    #     logger.design.info("Design critical message for testing.")

    #     global_messages = logger.get_messages().global_level
    #     assert len(global_messages) >= 11

    #     pyaedt_version = False
    #     python_version = False
    #     project = False
    #     for message in global_messages:
    #         if '[info] pyaedt v' in message:
    #             pyaedt_version = True
    #             continue
    #         if '[info] Python version' in message:
    #             python_version = True
    #             continue
    #         if '[info] Project' in message:
    #             project = True

    #     print("#######")
    #     print("Global")
    #     print(global_messages)
    #     assert '[info] Global debug message for testing.' in global_messages
    #     assert '[info] Global info message for testing.' in global_messages
    #     assert '[warning] Global warning message for testing.' in global_messages
    #     assert '[error] Global error message for testing.' in global_messages
    #     assert '[info] Global critical message for testing.' in global_messages

    #     design_messages = logger.get_messages().design_level
    #     assert len(design_messages) >= 6
    #     assert '[info] Successfully loaded project materials !' in design_messages[0]
    #     assert '[info] Design debug message for testing.' in design_messages[1]
    #     assert '[info] Design info message for testing.' in design_messages[2]
    #     assert '[warning] Design warning message for testing.' in design_messages[3]
    #     assert '[error] Design error message for testing.' in design_messages[4]
    #     assert '[info] Design critical message for testing.' in design_messages[5]

    #     project_messages = logger.get_messages().project_level
    #     assert len(project_messages) >= 5
    #     assert '[info] Project debug message for testing.' in project_messages[0]
    #     assert '[info] Project info message for testing.' in project_messages[1]
    #     assert '[warning] Project warning message for testing.' in project_messages[2]
    #     assert '[error] Project error message for testing.' in project_messages[3]
    #     assert '[info] Project critical message for testing.' in project_messages[4]

    #     logger.clear_messages("", "", 2)
    #     assert not logger.get_messages().global_level

    def test_02_output_file_with_app_filter(self):
        content = None
        temp_dir = tempfile.gettempdir()
        logging_dir = os.path.join(temp_dir, "log_testing")
        if not os.path.exists(logging_dir):
            os.makedirs(logging_dir)
        path = os.path.join(logging_dir, "test02.txt")
        logger = AedtLogger(self.aedtapp._messenger, filename=path)
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

        # Close every handlers to make sure that the
        # file handler on every logger has been released properly.
        # Otherwise, we can't read the content of the log file.

        # delete the global file handler but not the log hadler because
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
        # self.aedtapp.logger.handlers.pop()
        # self.aedtapp.logger.project.handlers.pop()
        # if len(self.aedtapp.logger.design.handlers) > 0:
        #     self.aedtapp.logger.design.handlers.pop()

        os.remove(path)

    @pytest.mark.skipif(is_ironpython, reason="stdout redirection does not work in IronPython.")
    def test_03_stdout_with_app_filter(self):
        capture = CaptureStdOut()
        with capture:
            logger = AedtLogger(self.aedtapp._messenger, to_stdout=True)
            logger.info("Info for Global")
            logger.warning("Warning for Global")
            logger.error("Error for Global")

        assert "pyaedt info: Info for Global" in capture.content
        assert "pyaedt warning: Warning for Global" in capture.content
        assert "pyaedt error: Error for Global" in capture.content

    def test_04_disable_output_file_handler(self):
        content = None
        temp_dir = tempfile.gettempdir()
        logging_dir = os.path.join(temp_dir, "log_testing")
        if not os.path.exists(logging_dir):
            os.makedirs(logging_dir)
        path = os.path.join(logging_dir, "test04.txt")
        logger = AedtLogger(self.aedtapp._messenger, filename=path)
        logger.info("Info for Global before disabling the log file handler.")
        project_logger = logger.add_logger("Project")
        project_logger.info("Info for Project before disabling the log file handler.")
        design_logger = logger.add_logger("Design")
        design_logger.info("Info for Design before disabling the log file handler.")

        with open(path, "r") as f:
            content = f.readlines()

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

        os.remove(path)

    @pytest.mark.skipif(is_ironpython, reason="stdout redirection does not work in IronPython.")
    def test_05_disable_stdout(self):
        with tempfile.TemporaryFile("w+") as fp:

            stream = unittest.mock.MagicMock()
            stream.write = unittest.mock.MagicMock()

            stream.write.side_effect = fp.write
            sys.stdout = stream

            logger = AedtLogger(self.aedtapp._messenger, to_stdout=True)
            logger.info("Info for Global")
            logger.disable_stdout_log()
            logger.info("Info after disabling the stdout handler.")
            logger.enable_stdout_log()
            logger.info("Info after re-enabling the stdout handler.")

            sys.stdout = sys.__stdout__

            stream.write.assert_any_call("pyaedt info: Info for Global")
            stream.write.assert_any_call("pyaedt info: Info after re-enabling the stdout handler.")

            with pytest.raises(AssertionError) as e_info:
                stream.write.assert_any_call("pyaedt info: Info after disabling the stdout handler.")

            fp.seek(0)
            stream_content = fp.readlines()

        assert stream_content[0] == "pyaedt info: Info for Global\n"
        assert stream_content[1] == "pyaedt info: Info after re-enabling the stdout handler.\n"


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
