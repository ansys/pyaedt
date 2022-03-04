import os

import pytest

from pyaedt import Hfss
from pyaedt import hfss as hfss_module


@pytest.fixture(autouse=True, scope="module")
def create_hfss(request, doctest_namespace):
    """Create Hfss object to use in docstring examples.

    An Hfss object is created only once when running tests on
    hfss.py. The doctest_namespace dictionary is passed into
    the context of the doctests. Because of doctest_namespace["hfss"],
    the object ``hfss`` can be referenced inside docstring examples.

    """
    # Check test is running from hfss.py module
    if request.module != hfss_module:
        return

    # Use USB_Connector.aedt project to test
    project_path = os.path.join(doctest_namespace["projects_path"], "USB_Connector.aedt")
    doctest_namespace["hfss"] = Hfss(projectname=project_path, designname="HfssDesign1")


@pytest.fixture(autouse=True, scope="function")
def set_active_design(request, doctest_namespace):
    """Set active design to created Hfss design.

    Set the active project and design before every test, since
    these can be overwritten by other projects or designs created
    in the examples.
    """
    # Check test is running from hfss.py module
    if request.module != hfss_module:
        return

    hfss = doctest_namespace["hfss"]
    hfss._oproject = "USB_Connector"
    hfss._odesign = "HfssDesign1"
