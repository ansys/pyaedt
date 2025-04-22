# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_int

import ansys.aedt.core


class LumpedNodesandLeads:
    """Defines attributes of the lumped element node capacitors and lead inductors.

    This class allows you to define and modify the node capacitors and
    lead inductors parameters of the lumped elements used in the designed filter.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
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
        """Shunt capacitance assigned to each capacitor node.
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
        """Series inductance assigned to each capacitor lead.
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
        """Shunt capacitance assigned to each inductor node.

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
        """Series inductance assigned to each inductor lead.

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
        """Shunt capacitance assigned to each resistor node.
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
        """Series inductance assigned to each resistor lead.

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
        """Flag indicating if the adjusting capacitor values to compensate for node capacitance is enabled.

        Returns
        -------
        bool
        """
        c_node_compensate = c_bool()
        status = self._dll.getLumpedCNodeLedComensate(byref(c_node_compensate))
        self._dll_interface.raise_error(status)
        return bool(c_node_compensate.value)

    @c_node_compensate.setter
    def c_node_compensate(self, c_node_compensate: bool):
        status = self._dll.setLumpedCNodeLedComensate(c_node_compensate)
        self._dll_interface.raise_error(status)

    @property
    def l_node_compensate(self) -> bool:
        """Flag indicating if the adjusting inductor values to compensate for lead inductance is enabled.

        Returns
        -------
        bool
        """
        l_node_compensate = c_bool()
        status = self._dll.getLumpedLNodeLedComensate(byref(l_node_compensate))
        self._dll_interface.raise_error(status)
        return bool(l_node_compensate.value)

    @l_node_compensate.setter
    def l_node_compensate(self, l_node_compensate: bool):
        status = self._dll.setLumpedLNodeLedComensate(l_node_compensate)
        self._dll_interface.raise_error(status)
