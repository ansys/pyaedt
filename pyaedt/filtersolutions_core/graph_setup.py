from ctypes import c_char_p
from ctypes import c_int

import pyaedt


class GraphSetup:
    """Defines minimum and maximum of freuquncy and time parameters of filter responses.

    Attributes
    ----------
    _dll: CDLL
        FilterSolutions C++ API DLL.
    _dll_interface: DllInterface
        an instance of DllInterface class

    Methods
    ----------
    _define_graph_dll_functions:
        Define argument types of DLL function.
    """

    def __init__(self):
        self._dll = pyaedt.filtersolutions_core._dll_interface()._dll
        self._dll_interface = pyaedt.filtersolutions_core._dll_interface()
        self._define_graph_dll_functions()

    def _define_graph_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setPlotMinimumFrequency.argtype = c_char_p
        self._dll.setPlotMinimumFrequency.restype = c_int
        self._dll.getPlotMinimumFrequency.argtypes = [c_char_p, c_int]
        self._dll.getPlotMinimumFrequency.restype = c_int

        self._dll.setPlotMaximumFrequency.argtype = c_char_p
        self._dll.setPlotMaximumFrequency.restype = c_int
        self._dll.getPlotMaximumFrequency.argtypes = [c_char_p, c_int]
        self._dll.getPlotMaximumFrequency.restype = c_int

        self._dll.setPlotMinimumTime.argtype = c_char_p
        self._dll.setPlotMinimumTime.restype = c_int
        self._dll.getPlotMinimumTime.argtypes = [c_char_p, c_int]
        self._dll.getPlotMinimumTime.restype = c_int

        self._dll.setPlotMaximumTime.argtype = c_char_p
        self._dll.setPlotMaximumTime.restype = c_int
        self._dll.getPlotMaximumTime.argtypes = [c_char_p, c_int]
        self._dll.getPlotMaximumTime.restype = c_int

    @property
    def minimum_frequency(self) -> str:
        """Minimum frequency value for exporting frequency and S parameters responses. The default is 200 MHz.

        Returns
        -------
        str
        """
        min_freq_string = self._dll_interface.get_string(self._dll.getPlotMinimumFrequency)
        return min_freq_string

    @minimum_frequency.setter
    def minimum_frequency(self, min_freq_string):
        self._dll_interface.set_string(self._dll.setPlotMinimumFrequency, min_freq_string)

    @property
    def maximum_frequency(self) -> str:
        """Maximum frequency value for exporting frequency and S parameters responses. The default is 5 GHz.

        Returns
        -------
        str
        """
        max_freq_string = self._dll_interface.get_string(self._dll.getPlotMaximumFrequency)
        return max_freq_string

    @maximum_frequency.setter
    def maximum_frequency(self, max_freq_string):
        self._dll_interface.set_string(self._dll.setPlotMaximumFrequency, max_freq_string)

    @property
    def minimum_time(self) -> str:
        """Minimum time value for exporting time response. The default is 0 s.

        Returns
        -------
        str
        """
        min_time_string = self._dll_interface.get_string(self._dll.getPlotMinimumTime)
        return min_time_string

    @minimum_time.setter
    def minimum_time(self, min_time_string):
        self._dll_interface.set_string(self._dll.setPlotMinimumTime, min_time_string)

    @property
    def maximum_time(self) -> str:
        """Maximum time value for exporting time response. The default is 10 ns.

        Returns
        -------
        str
        """
        max_time_string = self._dll_interface.get_string(self._dll.getPlotMaximumTime)
        return max_time_string

    @maximum_time.setter
    def maximum_time(self, max_time_string):
        self._dll_interface.set_string(self._dll.setPlotMaximumTime, max_time_string)
