from typing import List
import pytest

def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    """Hook used to apply marker on system tests."""
    for item in items:
        item.add_marker(pytest.mark.system)