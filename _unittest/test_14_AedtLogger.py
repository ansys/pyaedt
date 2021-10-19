# Setup paths for module imports
import tempfile
import os
import io
import sys
import pytest

# Import required modules
from pyaedt.aedt_logger import AedtLogger


class TestClass:

    # @pytest.mark.xfail
    # def test_01_global(self, clean_desktop_messages, clean_desktop, hfss):
    #     logger = hfss.logger
    #     # The default logger level is DEBUGGING.
    #     logger.glb.debug("Global debug message for testing.")
    #     logger.glb.info("Global info message for testing.")
    #     logger.glb.warning("Global warning message for testing.")
    #     logger.glb.error("Global error message for testing.")
    #     logger.glb.info("Global critical message for testing.")
    #
    #     # Project logger
    #     logger.add_logger("Project")
    #     logger.project.debug("Project debug message for testing.")
    #     logger.project.info("Project info message for testing.")
    #     logger.project.warning("Project warning message for testing.")
    #     logger.project.error("Project error message for testing.")
    #     logger.project.info("Project critical message for testing.")
    #
    #     # Current active design logger
    #     logger.add_logger("Design")
    #     logger.design.debug("Design debug message for testing.")
    #     logger.design.info("Design info message for testing.")
    #     logger.design.warning("Design warning message for testing.")
    #     logger.design.error("Design error message for testing.")
    #     logger.design.info("Design critical message for testing.")
    #
    #     global_messages = logger.get_messages().global_level
    #     assert len(global_messages) >= 11
    #
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
    #
    #     print("#######")
    #     print("Global")
    #     print(global_messages)
    #     assert '[info] Global debug message for testing.' in global_messages
    #     assert '[info] Global info message for testing.' in global_messages
    #     assert '[warning] Global warning message for testing.' in global_messages
    #     assert '[error] Global error message for testing.' in global_messages
    #     assert '[info] Global critical message for testing.' in global_messages
    #
    #     design_messages = logger.get_messages().design_level
    #     assert len(design_messages) >= 6
    #     assert '[info] Successfully loaded project materials !' in design_messages[0]
    #     assert '[info] Design debug message for testing.' in design_messages[1]
    #     assert '[info] Design info message for testing.' in design_messages[2]
    #     assert '[warning] Design warning message for testing.' in design_messages[3]
    #     assert '[error] Design error message for testing.' in design_messages[4]
    #     assert '[info] Design critical message for testing.' in design_messages[5]
    #
    #     project_messages = logger.get_messages().project_level
    #     assert len(project_messages) >= 5
    #     assert '[info] Project debug message for testing.' in project_messages[0]
    #     assert '[info] Project info message for testing.' in project_messages[1]
    #     assert '[warning] Project warning message for testing.' in project_messages[2]
    #     assert '[error] Project error message for testing.' in project_messages[3]
    #     assert '[info] Project critical message for testing.' in project_messages[4]
    #
    #     logger.clear_messages("", "", 2)
    #     assert not logger.get_messages().global_level

    def test_02_output_file_with_app_filter(self, hfss):
        content = None
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "test.txt")
            logger = AedtLogger(hfss._messenger, filename=path)
            logger.glb.info("Info for Global")
            logger.glb.debug("Debug for Global")
            logger.glb.warning("Warning for Global")
            logger.glb.error("Error for Global")
            project_logger = logger.add_logger('Project')
            project_logger.info("Info for Project")
            project_logger.debug("Debug for Project")
            project_logger.warning("Warning for Project")
            project_logger.error("Error for Project")
            design_logger = logger.add_logger('Design')
            design_logger.info("Info for Design")
            design_logger.debug("Debug for Design")
            design_logger.warning("Warning for Design")
            design_logger.error("Error for Design")

            # Close every handlers to make sure that the
            # file handler on every logger has been released properly.
            # Otherwise, we can't read the content of the log file.
            for handler in logger.glb.handlers:
                handler.close()
            for handler in project_logger.handlers:
                handler.close()
            for handler in design_logger.handlers:
                handler.close()

            with open(path, 'r') as f:
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

        hfss.logger.glb.handlers.pop()
        hfss.logger.project.handlers.pop()
        if len(hfss.logger.design.handlers) > 0:
            hfss.logger.design.handlers.pop()

    def test_03_stdout_with_app_filter(self, hfss):
        capture = CaptureStdOut()
        with capture:
            logger = AedtLogger(hfss._messenger, to_stdout=True)
            logger.glb.info("Info for Global")
            logger.glb.debug("Debug for Global")
            logger.glb.warning("Warning for Global")
            logger.glb.error("Error for Global")
            project_logger = logger.add_logger('Project')
            project_logger.info("Info for Project")
            project_logger.debug("Debug for Project")
            project_logger.warning("Warning for Project")
            project_logger.error("Error for Project")
            design_logger = logger.add_logger('Design')
            design_logger.info("Info for Design")
            design_logger.debug("Debug for Design")
            design_logger.warning("Warning for Design")
            design_logger.error("Error for Design")

        assert "PyAEDT Info: Info for Global" in capture.content
        assert "PyAEDT Info: Debug for Global" in capture.content
        assert "PyAEDT Warning: Warning for Global" in capture.content
        assert "PyAEDT Error: Error for Global" in capture.content
        assert "PyAEDT Info: Info for Project" in capture.content
        assert "PyAEDT Info: Debug for Project" in capture.content
        assert "PyAEDT Warning: Warning for Project" in capture.content
        assert "PyAEDT Error: Error for Project" in capture.content
        assert "PyAEDT Info: Info for Design" in capture.content
        assert "PyAEDT Info: Debug for Design" in capture.content
        assert "PyAEDT Warning: Warning for Design" in capture.content
        assert "PyAEDT Error: Error for Design" in capture.content

        for handler in logger.glb.handlers:
            handler.close()
        for handler in project_logger.handlers:
            handler.close()
        for handler in design_logger.handlers:
            handler.close()


class CaptureStdOut():
    """Capture standard output with a context manager."""

    def __init__(self):
        self._stream = io.StringIO()

    def __enter__(self):
        sys.stdout = self._stream

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__

    @property
    def content(self):
        """Return the captured content."""
        return self._stream.getvalue()