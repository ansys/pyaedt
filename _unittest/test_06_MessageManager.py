# Setup paths for module imports
import logging

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from pyaedt.application.MessageManager import AEDTMessageManager

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

LOGGER = logging.getLogger(__name__)


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        # Test the global _messenger before opening the desktop
        msg = AEDTMessageManager()
        msg.clear_messages()
        msg.add_info_message("Test desktop level - Info")
        msg.add_info_message("Test desktop level - Info", level="Design")
        msg.add_info_message("Test desktop level - Info", level="Project")
        msg.add_info_message("Test desktop level - Info", level="Global")
        # assert len(msg.messages.global_level) == 4
        # assert len(msg.messages.project_level) == 0
        # assert len(msg.messages.design_level) == 0
        # assert len(msg.messages.global_level) == 0
        # assert len(msg.messages.project_level) == 0
        # assert len(msg.messages.design_level) == 0
        msg.clear_messages(level=0)
        BasisTest.add_app(self)
        msg.clear_messages(level=3)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    @pytest.mark.skipif(config["build_machine"], reason="Issue on Build machine")
    def test_01_get_messages(self):  # pragma: no cover
        msg = self.aedtapp._messenger
        msg.clear_messages(level=3)
        msg.add_info_message("Test Info design level")
        msg.add_info_message("Test Info project level", "Project")
        msg.add_info_message("Test Info", "Global")
        assert len(msg.messages.global_level) >= 1
        assert len(msg.messages.project_level) >= 1
        assert len(msg.messages.design_level) >= 1
        pass

    @pytest.mark.skipif(config["build_machine"], reason="Issue on Build machine")
    def test_02_messaging(self):  # pragma: no cover
        msg = self.aedtapp._messenger
        msg.clear_messages(level=3)
        msg.add_info_message("Test Info")
        msg.add_info_message("Test Info", "Project")
        msg.add_info_message("Test Info", "Global")
        msg.add_warning_message("Test Warning at Design Level")
        msg.add_warning_message("Test Warning at Project Level", "Project")
        msg.add_warning_message("Test Warning at Global Level", "Global")
        msg.add_error_message("Test Error at Design Level")
        msg.add_error_message("Test Error at Project Level", "Project")
        msg.add_error_message("Test Error at Global Level", "Global")
        msg.add_info_message("Test Debug")
        msg.add_info_message("Test Debug", "Project")
        msg.add_info_message("Test Debug", "Global")
        assert len(msg.messages.global_level) >= 5
        assert len(msg.messages.project_level) >= 5
        assert len(msg.messages.design_level) >= 4
