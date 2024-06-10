from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_int

import pyaedt


class LumpedNodesandLeads:
    """Defines attributes of lumped element node capacitor and lead inductor.

    This class allows you to construct all the necessary node capacitor and
    lead inductor attributes of lumped elements for the LumpedDesign class.

    Attributes
    ----------
    _dll: CDLL
        FilterSolutions C++ API DLL.
    _dll_interface: DllInterface
        Instance of the ``DllInterface`` class

    Methods
    ----------
    _define_nodes_and_leads_dll_functions:
        Define argument types of DLL functions.
    """

    def __init__(self):
        self._dll = pyaedt.filtersolutions_core._dll_interface()._dll
        self._dll_interface = pyaedt.filtersolutions_core._dll_interface()
        self._define_nodes_and_leads_dll_functions()

    def _define_nodes_and_leads_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setLumpedCNodeCapacitor.argtype = c_char_p
        self._dll.setLumpedCNodeCapacitor.restype = c_int
        self._dll.getLumpedCNodeCapacitor.argtypes = [c_char_p, c_int]
        self._dll.getLumpedCNodeCapacitor.restype = c_int

        self._dll.setLumpedCLeadInductor.argtype = c_char_p
        self._dll.setLumpedCLeadInductor.restype = c_int
        self._dll.getLumpedCLeadInductor.argtypes = [c_char_p, c_int]
        self._dll.getLumpedCLeadInductor.restype = c_int

        self._dll.setLumpedLNodeCapacitor.argtype = c_char_p
        self._dll.setLumpedLNodeCapacitor.restype = c_int
        self._dll.getLumpedLNodeCapacitor.argtypes = [c_char_p, c_int]
        self._dll.getLumpedLNodeCapacitor.restype = c_int

        self._dll.setLumpedLLeadInductor.argtype = c_char_p
        self._dll.setLumpedLLeadInductor.restype = c_int
        self._dll.getLumpedLLeadInductor.argtypes = [c_char_p, c_int]
        self._dll.getLumpedLLeadInductor.restype = c_int

        self._dll.setLumpedRNodeCapacitor.argtype = c_char_p
        self._dll.setLumpedRNodeCapacitor.restype = c_int
        self._dll.getLumpedRNodeCapacitor.argtypes = [c_char_p, c_int]
        self._dll.getLumpedRNodeCapacitor.restype = c_int

        self._dll.setLumpedRLeadInductor.argtype = c_char_p
        self._dll.setLumpedRLeadInductor.restype = c_int
        self._dll.getLumpedRLeadInductor.argtypes = [c_char_p, c_int]
        self._dll.getLumpedRLeadInductor.restype = c_int

        self._dll.setLumpedCNodeLedComensate.argtype = c_bool
        self._dll.setLumpedCNodeLedComensate.restype = c_int
        self._dll.getLumpedCNodeLedComensate.argtype = POINTER(c_bool)
        self._dll.getLumpedCNodeLedComensate.restype = c_int

        self._dll.setLumpedLNodeLedComensate.argtype = c_bool
        self._dll.setLumpedLNodeLedComensate.restype = c_int
        self._dll.getLumpedLNodeLedComensate.argtype = POINTER(c_bool)
        self._dll.getLumpedLNodeLedComensate.restype = c_int

    @property
    def c_node_capacitor(self) -> str:
        """Shunt capacitors value of non ideal capacitors nodes in synthesized circuit
        The default is ``0``.

        Returns
        -------
        str
        """
        c_node_capacitor = self._dll_interface.get_string(self._dll.getLumpedCNodeCapacitor)
        return c_node_capacitor

    @c_node_capacitor.setter
    def c_node_capacitor(self, c_node_capacitor):
        self._dll_interface.set_string(self._dll.setLumpedCNodeCapacitor, c_node_capacitor)

    @property
    def c_lead_inductor(self) -> str:
        """Series inductors value of non ideal capacitors leades in synthesized circuit
        The default is ``0``.

        Returns
        -------
        str
        """
        c_lead_inductor = self._dll_interface.get_string(self._dll.getLumpedCLeadInductor)
        return c_lead_inductor

    @c_lead_inductor.setter
    def c_lead_inductor(self, c_lead_inductor):
        self._dll_interface.set_string(self._dll.setLumpedCLeadInductor, c_lead_inductor)

    @property
    def l_node_capacitor(self) -> str:
        """Shunt capacitors value of non ideal inductors nodes in synthesized circuit
        The default is` ``0``.

        Returns
        -------
        str
        """
        l_node_capacitor = self._dll_interface.get_string(self._dll.getLumpedLNodeCapacitor)
        return l_node_capacitor

    @l_node_capacitor.setter
    def l_node_capacitor(self, l_node_capacitor):
        self._dll_interface.set_string(self._dll.setLumpedLNodeCapacitor, l_node_capacitor)

    @property
    def l_lead_inductor(self) -> str:
        """Series inductors value of non ideal inductors leades in synthesized circuit
        The default is ``0``.

        Returns
        -------
        str
        """
        l_lead_inductor = self._dll_interface.get_string(self._dll.getLumpedLLeadInductor)
        return l_lead_inductor

    @l_lead_inductor.setter
    def l_lead_inductor(self, l_lead_inductor):
        self._dll_interface.set_string(self._dll.setLumpedLLeadInductor, l_lead_inductor)

    @property
    def r_node_capacitor(self) -> str:
        """Shunt capacitors value of non ideal resistors nodes in synthesized circuit
        The default is ``0``.

        Returns
        -------
        str
        """
        r_node_capacitor = self._dll_interface.get_string(self._dll.getLumpedRNodeCapacitor)
        return r_node_capacitor

    @r_node_capacitor.setter
    def r_node_capacitor(self, r_node_capacitor):
        self._dll_interface.set_string(self._dll.setLumpedRNodeCapacitor, r_node_capacitor)

    @property
    def r_lead_inductor(self) -> str:
        """Series inductors value of non ideal resistors leades in synthesized circuit
        The default is ``0``.

        Returns
        -------
        str
        """
        r_lead_inductor = self._dll_interface.get_string(self._dll.getLumpedRLeadInductor)
        return r_lead_inductor

    @r_lead_inductor.setter
    def r_lead_inductor(self, r_lead_inductor):
        self._dll_interface.set_string(self._dll.setLumpedRLeadInductor, r_lead_inductor)

    @property
    def c_node_compensate(self) -> bool:
        """Flag indicating if the possible adjust capacitor values to compensate for node capacitance is enabled.

        Returns
        -------
        bool
        """
        c_node_compensate = c_bool()
        status = self._dll.getLumpedCNodeLedComensate(byref(c_node_compensate))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return bool(c_node_compensate.value)

    @c_node_compensate.setter
    def c_node_compensate(self, c_node_compensate: bool):
        status = self._dll.setLumpedCNodeLedComensate(c_node_compensate)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def l_node_compensate(self) -> bool:
        """Flag indicating if the possible adjust inductor values to compensate for lead inductance is enabled.

        Returns
        -------
        bool
        """
        l_node_compensate = c_bool()
        status = self._dll.getLumpedLNodeLedComensate(byref(l_node_compensate))
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
        return bool(l_node_compensate.value)

    @l_node_compensate.setter
    def l_node_compensate(self, l_node_compensate: bool):
        status = self._dll.setLumpedLNodeLedComensate(l_node_compensate)
        pyaedt.filtersolutions_core._dll_interface().raise_error(status)
