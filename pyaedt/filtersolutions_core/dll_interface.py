import ctypes
from enum import Enum
import os
import threading
import time
from typing import Callable


class DllInterface:
    """Interfaces with the FilterSolutions C++ API DLL."""

    def __init__(self, show_gui=True):
        self._init_dll_path()
        self._init_dll(show_gui)

    def restore_defaults(self):
        """Restore the state of the API, including all options and values, to the initial startup state."""
        status = self._dll.startApplication(self.show_gui)
        self.raise_error(status)

    def _init_dll_path(self):
        """Set DLL path and print the status of the DLL access to the screen."""
        relative_path = "../../../build_output/64Release/nuhertz/FilterSolutionsAPI.dll"
        self.dll_path = os.path.join(os.path.dirname(__file__), relative_path)
        if not os.path.isfile(self.dll_path):
            self.dll_path = os.path.join(
                os.environ["ANSYSEM_ROOT242"], "nuhertz/FilterSolutionsAPI.dll"
            )  # pragma: no cover
        print("DLL Path:", self.dll_path)
        if not os.path.isfile(self.dll_path):
            raise RuntimeError(f"The 'FilterSolution' API DLL was not found at {self.dll_path}.")  # pragma: no cover

    def _init_dll(self, show_gui):
        """Load DLL and initialize application parameters to default values."""

        self._dll = ctypes.cdll.LoadLibrary(self.dll_path)
        self._define_dll_functions()
        self.show_gui = show_gui
        if show_gui:  # pragma: no cover
            self._app_thread = threading.Thread(target=self._app_thread_task)
            self._app_thread.start()
            # TODO: Need some way to confirm that the GUI has completed initialization,
            # otherwise some subsequent API calls will fail. For now, sleep a few seconds.
            time.sleep(5)
        else:
            status = self._dll.startApplication(False)
            self.raise_error(status)

        print("DLL Loaded:", self.api_version())
        print("API Ready")
        print("")

    def _app_thread_task(self):  # pragma: no cover
        """Print the status of running application thread."""
        print("Starting Application::Run thread")
        status = self._dll.startApplication(self.show_gui)
        self.raise_error(status)

    def _define_dll_functions(self):
        """Define DLL function."""
        self._dll.getVersion.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self._dll.getVersion.restype = ctypes.c_int

    def get_string(self, dll_function: Callable, max_size=100) -> str:
        """
        Call a DLL function that returns a string.

        Parameters
        ----------
        dll_function: Callable
            DLL function to call. It must be a function that returns a string.
        max_size: int
            Maximum number of string characters to return. This value is used for the string buffer size.

        Returns
        -------
        str
            Requested string. If '`status`', an error message is returned.
        """
        text_buffer = ctypes.create_string_buffer(max_size)
        status = dll_function(text_buffer, max_size)
        self.raise_error(status)
        text = text_buffer.value.decode("utf-8")
        return text

    def set_string(self, dll_function: Callable, string: str):
        """
        Call a DLL function that sets a string.

        Parameters
        ----------
        dll_function: Callable
            DLL function to call. It must be a function that sets a string.
        string: str
            String to set.
        """
        bytes_value = bytes(string, "ascii")
        status = dll_function(bytes_value)
        self.raise_error(status)

    def string_to_enum(self, enum_type: Enum, string: str) -> Enum:
        """
        Convert string to a string defined by an enum.

        Parameters
        ----------
        enum_type: Enum
            Enum to call.
        string: str
            String to convert.

        Returns
        -------
        str
            Converted enum string.
        """
        fixed_string = string.upper().replace(" ", "_")
        return enum_type[fixed_string]

    def enum_to_string(self, enum_value: Enum) -> str:
        """
        Convert a string defined by an enum to a string.

        Parameters
        ----------
        enum_type: Enum
            Enum to call.
        string: str
            String to convert.

        Returns
        -------
        str
            String converted from the enum string.
        """
        fixed_string = str(enum_value.name).replace("_", " ").lower()
        return fixed_string

    def api_version(self) -> str:
        """
        Return the version of API.

        Returns
        -------
        str
            API version.
        """
        version = self.get_string(self._dll.getVersion)
        return version

    def raise_error(self, error_status):
        if error_status != 0:
            error_message = self.get_string(self._dll.getErrorMessage, 4096)
            raise RuntimeError(error_message)
