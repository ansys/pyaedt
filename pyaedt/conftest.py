import pytest
import pyaedt

@pytest.fixture(autouse=True)
def start_aedt(doctest_namespace):
    desktop = pyaedt.Desktop("2021.1", NG=True)
    doctest_namespace["desktop"] = desktop