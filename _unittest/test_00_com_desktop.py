from _unittest.conftest import config
from pyaedt import Desktop
from pyaedt import settings


def test_00_destkop():
    settings.use_grpc_api = False
    d = Desktop(
        config["desktopVersion"],
        non_graphical=True,
        new_desktop_session=True,
    )

    assert isinstance(d.project_list(), list)
    assert isinstance(d.design_list(), list)
    assert d.aedt_version_id == config["desktopVersion"]
    assert d.personallib
    assert d.userlib
    assert d.syslib
    assert d.clear_messages()
    d.release_desktop()
    settings.use_grpc_api = config["use_grpc"]
