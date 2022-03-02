import os

import pytest

from pyaedt import Icepak
from pyaedt import icepak as icepak_module


@pytest.fixture(autouse=True, scope="module")
def create_icepak(request, doctest_namespace):
    """Create Icepak object to use in docstring examples.

    An Icepak object is created only once when running tests on
    icepak.py. The doctest_namespace dictionary is passed into
    the context of the doctests. Because of doctest_namespace["icepak"],
    the object ``icepak`` can be referenced inside docstring examples.

    """
    # Check test is running from icepak.py module
    if request.module != icepak_module:
        return

    # Use RadioBoardIcepak.aedt project to test
    project_path = os.path.join(doctest_namespace["projects_path"], "RadioBoardIcepak.aedt")
    doctest_namespace["icepak"] = Icepak(projectname=project_path, designname="IcepakDesign1")


@pytest.fixture(autouse=True, scope="function")
def set_active_design(request, doctest_namespace):
    """Set active design to created Icepak design.

    Set the active project and design before every test, since
    these can be overwritten by other projects or designs created
    in the examples.
    """
    # Check test is running from icepak.py module
    if request.module != icepak_module:
        return

    icepak = doctest_namespace["icepak"]
    icepak._oproject = "RadioBoardIcepak"
    icepak._odesign = "IcepakDesign1"
