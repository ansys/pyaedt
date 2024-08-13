from ansys.aedt.core import __version__
from ansys.aedt.core import *

__version__ = __version__

import warnings

WARNING_MESSAGE = """Module 'pyaedt' has become an alias to the new package structure.
Please update you imports to use the new architecture based on 'ansys.aedt.core'.
The old structure will be deprecated in future versions, see https://aedt.docs.pyansys.com/version/stable/release_1_0.html#restructuring-of-the-codebase
"""

def alias_deprecation_warning():
    """Warning message informing users of architecture deprecation."""
    # Store warnings showwarning
    existing_showwarning = warnings.showwarning

    # Define and use custom showwarning
    def custom_show_warning(message, category, filename, lineno, file=None, line=None):
        """Custom warning used to remove <stdin>:loc: pattern."""
        print("{}: {}".format(category.__name__, message))

    warnings.showwarning = custom_show_warning

    warnings.warn(WARNING_MESSAGE, FutureWarning)

    # Restore warnings showwarning
    warnings.showwarning = existing_showwarning


alias_deprecation_warning()
