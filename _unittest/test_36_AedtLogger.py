# Setup paths for module imports
from _unittest.conftest import scratch_path
import gc

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Hfss(new_desktop_session=True)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_global(self):
        logger = self.aedtapp.logger
        # The default logger level is DEBUGGING.
        logger.global_logger.debug("Debug message for testing.")
        logger.global_logger.info("Info message for testing.")
        logger.global_logger.warning("Warning message for testing.")
        logger.global_logger.error("Error message for testing.")
        logger.global_logger.info("Critical message for testing.")

        # Project logger
        logger.add_logger("Project")
        logger.project_logger.debug("Debug message for testing.")
        logger.project_logger.info("Info message for testing.")
        logger.project_logger.warning("Warning message for testing.")
        logger.project_logger.error("Error message for testing.")
        logger.project_logger.info("Critical message for testing.")

        # Current active design logger
        logger.add_logger("Design")
        logger.design_logger.debug("Debug message for testing.")
        logger.design_logger.info("Info message for testing.")
        logger.design_logger.warning("Warning message for testing.")
        logger.design_logger.error("Error message for testing.")
        logger.design_logger.info("Critical message for testing.")

        global_messages = logger._messenger.messages.global_level
        assert len(global_messages) == 11
        assert global_messages[0] == '[info] pyaedt v0.4.dev0'
        assert '[info] Python version 3.8.0' in global_messages[1]
        assert '[info] Project' in global_messages[2]
        assert '[info] No design is present. Inserting a new design.' in global_messages
        assert '[info] Design Loaded' in global_messages
        assert '[info] Materials Loaded' in global_messages
        assert '[info] Debug message for testing.' in global_messages
        assert '[info] Info message for testing.' in global_messages
        assert '[warning] Warning message for testing.' in global_messages
        assert '[error] Error message for testing.' in global_messages
        assert '[info] Critical message for testing.' in global_messages

        design_messages = logger._messenger.messages.design_level
        assert len(design_messages) == 6
        assert '[info] Successfully loaded project materials !' in design_messages[0]
        assert '[info] Debug message for testing.' in design_messages[1]
        assert '[info] Info message for testing.' in design_messages[2]
        assert '[warning] Warning message for testing.' in design_messages[3]
        assert '[error] Error message for testing.' in design_messages[4]
        assert '[info] Critical message for testing.' in design_messages[5]

        project_messages = logger._messenger.messages.project_level
        assert len(project_messages) == 5
        assert '[info] Debug message for testing.' in project_messages[0]
        assert '[info] Info message for testing.' in project_messages[1]
        assert '[warning] Warning message for testing.' in project_messages[2]
        assert '[error] Error message for testing.' in project_messages[3]
        assert '[info] Critical message for testing.' in project_messages[4]

        logger.clear_messages("","", 2)