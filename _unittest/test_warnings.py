import sys
from unittest.mock import patch
import warnings

from pyaedt import LATEST_DEPRECATED_PYTHON_VERSION
from pyaedt import deprecation_warning


@patch.object(warnings, "warn")
def test_deprecation_warning(mock_warn):
    deprecation_warning()

    current_version = sys.version_info[:2]
    if current_version <= LATEST_DEPRECATED_PYTHON_VERSION:
        str_current_version = "{}.{}".format(*sys.version_info[:2])
        expected = (
            "Current python version ({}) is deprecated in PyAEDT. We encourage you "
            "to upgrade to the latest version to benefit from the latest features "
            "and security updates.".format(str_current_version)
        )
        mock_warn.assert_called_once_with(expected, PendingDeprecationWarning)
    else:
        mock_warn.assert_not_called()
