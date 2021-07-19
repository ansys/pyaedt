import os
from pathlib import Path

import pytest

from pyaedt import Desktop
from pyaedt.doctest_fixtures import *

# Import fixtures from other files
pytest_plugins = [
    "pyaedt.doctest_fixtures.icepak_fixtures",
]


@pytest.fixture(autouse=True, scope="session")
def start_aedt():
    desktop = Desktop("2021.1", NG=True)
    desktop.disable_autosave()

    # Wait to run doctest on docstrings
    yield desktop
    desktop.force_close_desktop()

@pytest.fixture(autouse=True, scope="session")
def get_root_directory(doctest_namespace):
    """Set up paths to the root and project directories.
    
    These paths can be used in other fixtures when loading
    existing projects and designs.
    """
    root = Path(__file__).parent.parent
    doctest_namespace["root_path"] = root
    doctest_namespace["projects_path"] = os.path.join(root, "_unittest", "example_models")
