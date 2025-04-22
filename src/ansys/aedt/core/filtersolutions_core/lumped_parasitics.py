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

from ctypes import c_char_p
from ctypes import c_int

import ansys.aedt.core


class LumpedParasitics:
    """Defines attributes of the lumped element parasitics.


    This class allows you to define and modify the parasitic
    parameters of the lumped elements used in designed filter.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_parasitics_dll_functions()

    def _define_parasitics_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setLumpedCapacitorQ.argtype = c_char_p
        self._dll.setLumpedCapacitorQ.restype = c_int
        self._dll.getLumpedCapacitorQ.argtypes = [c_char_p, c_int]
        self._dll.getLumpedCapacitorQ.restype = c_int

        self._dll.setLumpedCapacitorRs.argtype = c_char_p
        self._dll.setLumpedCapacitorRs.restype = c_int
        self._dll.getLumpedCapacitorRs.argtypes = [c_char_p, c_int]
        self._dll.getLumpedCapacitorRs.restype = c_int

        self._dll.setLumpedCapacitorRp.argtype = c_char_p
        self._dll.setLumpedCapacitorRp.restype = c_int
        self._dll.getLumpedCapacitorRp.argtypes = [c_char_p, c_int]
        self._dll.getLumpedCapacitorRp.restype = c_int

        self._dll.setLumpedCapacitorLs.argtype = c_char_p
        self._dll.setLumpedCapacitorLs.restype = c_int
        self._dll.getLumpedCapacitorLs.argtypes = [c_char_p, c_int]
        self._dll.getLumpedCapacitorLs.restype = c_int

        self._dll.setLumpedInductorQ.argtype = c_char_p
        self._dll.setLumpedInductorQ.restype = c_int
        self._dll.getLumpedInductorQ.argtypes = [c_char_p, c_int]
        self._dll.getLumpedInductorQ.restype = c_int

        self._dll.setLumpedInductorRs.argtype = c_char_p
        self._dll.setLumpedInductorRs.restype = c_int
        self._dll.getLumpedInductorRs.argtypes = [c_char_p, c_int]
        self._dll.getLumpedInductorRs.restype = c_int

        self._dll.setLumpedInductorRp.argtype = c_char_p
        self._dll.setLumpedInductorRp.restype = c_int
        self._dll.getLumpedInductorRp.argtypes = [c_char_p, c_int]
        self._dll.getLumpedInductorRp.restype = c_int

        self._dll.setLumpedInductorCp.argtype = c_char_p
        self._dll.setLumpedInductorCp.restype = c_int
        self._dll.getLumpedInductorCp.argtypes = [c_char_p, c_int]
        self._dll.getLumpedInductorCp.restype = c_int

    @property
    def capacitor_q(self) -> str:
        """Q factor value of non-ideal capacitors in the synthesized circuit.

        The default is ``infinite``.

        Returns
        -------
        str
        """
        capacitor_q_string = self._dll_interface.get_string(self._dll.getLumpedCapacitorQ)
        return capacitor_q_string

    @capacitor_q.setter
    def capacitor_q(self, capacitor_q_string):
        self._dll_interface.set_string(self._dll.setLumpedCapacitorQ, capacitor_q_string)

    @property
    def capacitor_rs(self) -> str:
        """Series resistor value of non-ideal capacitors in the synthesized circuit.

        The default is ``0``.

        Returns
        -------
        str
        """
        capacitor_rs_string = self._dll_interface.get_string(self._dll.getLumpedCapacitorRs)
        return capacitor_rs_string

    @capacitor_rs.setter
    def capacitor_rs(self, capacitor_rs_string):
        self._dll_interface.set_string(self._dll.setLumpedCapacitorRs, capacitor_rs_string)

    @property
    def capacitor_rp(self) -> str:
        """Shunt resistor value of non-ideal capacitors in the synthesized circuit.
        The default is ``infinite``.

        Returns
        -------
        str
        """
        capacitor_rp_string = self._dll_interface.get_string(self._dll.getLumpedCapacitorRp)
        return capacitor_rp_string

    @capacitor_rp.setter
    def capacitor_rp(self, capacitor_rp_string):
        self._dll_interface.set_string(self._dll.setLumpedCapacitorRp, capacitor_rp_string)

    @property
    def capacitor_ls(self) -> str:
        """Series inductance value of non-ideal capacitors in the synthesized circuit.

        The default is ``0``.

        Returns
        -------
        str
        """
        capacitor_ls_string = self._dll_interface.get_string(self._dll.getLumpedCapacitorLs)
        return capacitor_ls_string

    @capacitor_ls.setter
    def capacitor_ls(self, capacitor_ls_string):
        self._dll_interface.set_string(self._dll.setLumpedCapacitorLs, capacitor_ls_string)

    @property
    def inductor_q(self) -> str:
        """Q factor value of non-ideal inductors in the synthesized circuit.
        The default is ``infinite``.

        Returns
        -------
        str
        """
        inductor_q_string = self._dll_interface.get_string(self._dll.getLumpedInductorQ)
        return inductor_q_string

    @inductor_q.setter
    def inductor_q(self, inductor_q_string):
        self._dll_interface.set_string(self._dll.setLumpedInductorQ, inductor_q_string)

    @property
    def inductor_rs(self) -> str:
        """Series resistor value of non-ideal inductors in the synthesized circuit.

        The default is` ``0``.

        Returns
        -------
        str
        """
        inductor_rs_string = self._dll_interface.get_string(self._dll.getLumpedInductorRs)
        return inductor_rs_string

    @inductor_rs.setter
    def inductor_rs(self, inductor_rs_string):
        self._dll_interface.set_string(self._dll.setLumpedInductorRs, inductor_rs_string)

    @property
    def inductor_rp(self) -> str:
        """Shunt resistor value of non-ideal inductors in the synthesized circuit.

        The default is ``infinite``.

        Returns
        -------
        str
        """
        inductor_rp_string = self._dll_interface.get_string(self._dll.getLumpedInductorRp)
        return inductor_rp_string

    @inductor_rp.setter
    def inductor_rp(self, inductor_rp_string):
        self._dll_interface.set_string(self._dll.setLumpedInductorRp, inductor_rp_string)

    @property
    def inductor_cp(self) -> str:
        """Shunt capacitor value of non-ideal inductors in the synthesized circuit.

        The default is ``0``.

        Returns
        -------
        str
        """
        inductor_cp_string = self._dll_interface.get_string(self._dll.getLumpedInductorCp)
        return inductor_cp_string

    @inductor_cp.setter
    def inductor_cp(self, inductor_cp_string):
        self._dll_interface.set_string(self._dll.setLumpedInductorCp, inductor_cp_string)
