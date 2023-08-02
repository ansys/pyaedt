# Setup paths for module imports
import logging
import os.path

# from _unittest.conftest import BasisTest
from _unittest.conftest import config
import pytest

from pyaedt import Icepak
from pyaedt import settings
from pyaedt.aedt_logger import AedtLogger

# try:
#     import pytest
# except ImportError:
#     import _unittest_ironpython.conf_unittest as pytest

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app()
    return app


# @pytest.fixture(scope="class", autouse=True)
# def messages(local_scratch):
#     msg = AedtLogger()
#     msg.clear_messages()
#     msg.add_info_message("Test desktop level - Info")
#     msg.add_info_message("Test desktop level - Info", level="Design")
#     msg.add_info_message("Test desktop level - Info", level="Project")
#     msg.add_info_message("Test desktop level - Info", level="Global")
#     msg.clear_messages(level=0)
#     msg.clear_messages(level=3)


class TestClass:
    # def setup_class(self):
    #     BasisTest.my_setup(self)
    #     # Test the global messenger before opening the desktop
    #     msg = AedtLogger()
    #     msg.clear_messages()
    #     msg.add_info_message("Test desktop level - Info")
    #     msg.add_info_message("Test desktop level - Info", level="Design")
    #     msg.add_info_message("Test desktop level - Info", level="Project")
    #     msg.add_info_message("Test desktop level - Info", level="Global")
    #     # assert len(msg.messages.global_level) == 4
    #     # assert len(msg.messages.project_level) == 0
    #     # assert len(msg.messages.design_level) == 0
    #     # assert len(msg.messages.global_level) == 0
    #     # assert len(msg.messages.project_level) == 0
    #     # assert len(msg.messages.design_level) == 0
    #     msg.clear_messages(level=0)
    #     self.aedtapp = BasisTest.add_app(self)
    #     msg.clear_messages(level=3)
    #
    # def teardown_class(self):
    #     BasisTest.my_teardown(self)

    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_00_global_messenger(self):
        msg = AedtLogger()
        msg.clear_messages()
        msg.add_info_message("Test desktop level - Info")
        msg.add_info_message("Test desktop level - Info", level="Design")
        msg.add_info_message("Test desktop level - Info", level="Project")
        msg.add_info_message("Test desktop level - Info", level="Global")
        msg.clear_messages(level=0)
        msg.clear_messages(level=3)

    @pytest.mark.skipif(config["NonGraphical"], reason="Messages not functional in non-graphical mode")
    def test_01_get_messages(self, add_app):  # pragma: no cover
        settings.enable_desktop_logs = True
        msg = self.aedtapp.logger
        msg.clear_messages(level=3)
        msg.add_info_message("Test Info design level")
        msg.add_info_message("Test Info project level", "Project")
        msg.add_info_message("Test Info", "Global")
        assert len(msg.messages.global_level) >= 1
        assert len(msg.messages.project_level) >= 1
        assert len(msg.messages.design_level) >= 1
        ipk_app = add_app(application=Icepak)
        box = ipk_app.modeler.create_box([0, 0, 0], [1, 1, 1])
        ipk_app.modeler.create_3dcomponent(os.path.join(self.local_scratch.path, "test_m.a3dcomp"))
        box.delete()
        cmp = ipk_app.modeler.insert_3d_component(os.path.join(self.local_scratch.path, "test_m.a3dcomp"))
        ipk_app_comp = cmp.edit_definition()
        msg_comp = ipk_app_comp.logger
        msg_comp.add_info_message("3dcomp, Test Info design level")
        msg_comp.add_info_message("3dcomp, Test Info project level", "Project")
        assert len(msg_comp.messages.project_level) >= 1
        assert len(msg_comp.messages.design_level) >= 1
        settings.enable_desktop_logs = False

    @pytest.mark.skipif(config["NonGraphical"], reason="Messages not functional in non-graphical mode")
    def test_02_messaging(self):  # pragma: no cover
        settings.enable_desktop_logs = True
        msg = self.aedtapp.logger
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
        settings.enable_desktop_logs = False
