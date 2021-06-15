import pytest
# Setup paths for module imports
import gc
import math
import os

# Import required modules
from .conftest import local_path, scratch_path
from pyaedt.hfss import Hfss
from pyaedt.application.MessageManager import AEDTMessageManager
from pyaedt.application.Variables import Variable
from pyaedt.generic.filesystem import Scratch

import logging

LOGGER = logging.getLogger(__name__)

class TestMessage:

    def setup_class(self):

        with Scratch(scratch_path) as self.local_scratch:

            # Test the global messenger before opening the desktop
            msg = AEDTMessageManager()
            msg.clear_messages()
            msg.add_info_message("Test desktop level - Info")
            msg.add_info_message("Test desktop level - Info", level='Design')
            msg.add_info_message("Test desktop level - Info", level='Project')
            msg.add_info_message("Test desktop level - Info", level='Global')
            #assert len(msg.messages.global_level) == 4
            #assert len(msg.messages.project_level) == 0
            #assert len(msg.messages.design_level) == 0
            msg.clear_messages(level=0)
            #assert len(msg.messages.global_level) == 0
            #assert len(msg.messages.project_level) == 0
            #assert len(msg.messages.design_level) == 0

            self.aedtapp = Hfss()

    def teardown_class(self):

        assert self.aedtapp.close_project()
        self.local_scratch.remove()
        gc.collect()

    def test_00_test_global_messenger(self, caplog):
        #TODO: close_project causes a crash ... refactor the project/desktop stuff !
        #self.aedtapp.close_project()
        #self.aedtapp = Hfss()
        pass

    @pytest.mark.skip(reason="Issue on Build machine")
    def test_01_get_messages(self, caplog):

        msg = self.aedtapp.messenger
        msg.add_info_message("Test Info design level")
        msg.add_info_message("Test Info project level", "Project")
        msg.add_info_message("Test Info", 'Global')
        assert len(msg.messages.global_level) == 1
        assert len(msg.messages.project_level) == 2
        assert len(msg.messages.design_level) == 1
        pass

    @pytest.mark.skip(reason="Issue on Build machine")
    def test_02_messaging(self, caplog):
        msg = self.aedtapp.messenger
        msg.clear_messages()
        msg.add_info_message("Test Info")
        msg.add_info_message("Test Info", "Project")
        msg.add_info_message("Test Info", 'Global')
        msg.add_warning_message("Test Warning at Design Level")
        msg.add_warning_message("Test Warning at Project Level", "Project")
        msg.add_warning_message("Test Warning at Global Level", 'Global')
        msg.add_error_message("Test Error at Design Level")
        msg.add_error_message("Test Error at Project Level", "Project")
        msg.add_error_message("Test Error at Global Level", 'Global')
        msg.add_debug_message("Test Debug")
        msg.add_debug_message("Test Debug", "Project")
        msg.add_debug_message("Test Debug", 'Global')
        assert caplog.messages[0] == "Test Warning at Design Level"
        assert caplog.messages[1] == "Test Warning at Project Level"
        assert caplog.messages[2] == "Test Warning at Global Level"
        assert len(caplog.messages) == 6
        assert len(msg.messages.global_level) == 5
        assert len(msg.messages.project_level) == 6
        assert len(msg.messages.design_level) == 4

