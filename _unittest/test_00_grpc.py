from _unittest.conftest import BasisTest
from _unittest.conftest import config
from pyaedt import Desktop
from pyaedt.generic.general_methods import grpc_active_sessions

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

from pyaedt import settings
from pyaedt.generic.general_methods import is_ironpython

test_project_name = "Coax_HFSS"

if not is_ironpython and config["desktopVersion"] >= "2023.2":

    class TestClass(BasisTest, object):
        def setup_class(self):
            settings.use_grpc_api = True

        def teardown_class(self):
            settings.use_grpc_api = config["use_grpc"]
            settings.non_graphical = config["NonGraphical"]

        def test_00_destkop(self):
            d = Desktop(specified_version="2022.2", new_desktop_session=True)
            assert d.port in grpc_active_sessions()
            d.release_desktop(False, False)

        def test_01_destkop_existing(self):
            d = Desktop(specified_version="2022.2", new_desktop_session=False)
            assert d.port in grpc_active_sessions()
            d.release_desktop(False, False)

        def test_02_destkop_new(self):
            d = Desktop(specified_version="2022.2", new_desktop_session=True, non_graphical=True)
            assert d.port in grpc_active_sessions()
            d.release_desktop(False, False)

        def test_03_destkop_release(self):
            d = Desktop(specified_version="2022.2", new_desktop_session=False)
            assert d.port in grpc_active_sessions()
            d.release_desktop()
            d = Desktop(specified_version="2022.2", new_desktop_session=False)
            assert d.port in grpc_active_sessions()
            d.release_desktop()
