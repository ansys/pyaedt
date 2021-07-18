import pytest
from pyaedt import Desktop


@pytest.fixture(autouse=True, scope="session")
def start_aedt():
    desktop = Desktop("2021.1", non_graphical=True)
    desktop.disable_autosave()

    # Wait to run doctest on docstrings
    yield desktop
    desktop.force_close_desktop()
